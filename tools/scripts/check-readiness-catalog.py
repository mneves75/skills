#!/usr/bin/env python3
"""Read-only readiness catalog and preservation-map guard. Python 3.10+, standard library.

Usage: python3 tools/scripts/check-readiness-catalog.py [repository]
Exit 0 when all checks pass, 1 on any violation (reported as file:line).
"""
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

CONTROL_ID = r"[A-Z]{2,3}-[0-9]{2}"
HEADING = re.compile(rf"^### ({CONTROL_ID}) (\S.*)$")
CATALOGS = ("data", "platform", "product", "security", "stewardship")
SKILL = Path("skills/mneves-production-readiness")
SPEC = Path("docs/specs/production-readiness/spec.md")


class Audit:
    def __init__(self, root: Path):
        self.root = root
        self.errors: list[str] = []

    def error(self, file: Path, line: int, message: str) -> None:
        self.errors.append(f"{file.as_posix()}:{line}: {message}")

    def lines(self, file: Path) -> list[str]:
        try:
            return (self.root / file).read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as error:
            self.error(file, 1, f"cannot read: {error}")
            return []


def check_catalogs(audit: Audit) -> dict[str, tuple[Path, int]]:
    controls: dict[str, tuple[Path, int]] = {}
    for catalog in CATALOGS:
        file = SKILL / "references" / f"controls-{catalog}.md"
        lines = audit.lines(file)
        boundaries = [i for i, line in enumerate(lines) if line.startswith(("## ", "### "))] + [len(lines)]
        for index, line in enumerate(lines):
            if re.match(rf"^{CONTROL_ID}\b", line):
                audit.error(file, index + 1, "missing ### heading marker")
            if not line.startswith("###"):
                continue
            match = HEADING.fullmatch(line)
            if not match:
                audit.error(file, index + 1, "invalid control heading; expected ### <ID> <title>")
                continue
            control = match.group(1)
            if control in controls:
                audit.error(file, index + 1, f"duplicate control ID {control}")
            else:
                controls[control] = (file, index + 1)
            tier = lines[index + 1] if index + 1 < len(lines) else ""
            if not re.match(r"^`(blocker|contract|advisory)`(?:\s|$)", tier):
                audit.error(file, index + 2, f"{control}: missing or invalid tier line")
            end = next(boundary for boundary in boundaries if boundary > index)
            body = lines[index + 1:end]
            fields = ("Fallback",) if catalog == "security" else ("Verify", "Evidence")
            for field in fields:
                if not any(text.startswith(f"- {field}:") for text in body):
                    audit.error(file, index + 1, f"{control}: missing {field} line")
    return controls


def check_map(audit: Audit, controls: dict[str, tuple[Path, int]]) -> None:
    lines = audit.lines(SPEC)
    expected = {f"B{i}" for i in range(1, 148)} | {f"R{i}" for i in range(1, 14)}
    counts: Counter[str] = Counter()
    mapped: set[str] = set()
    active = False
    heading = 1
    for number, line in enumerate(lines, 1):
        if line.startswith("## "):
            active = line == "## Preservation map"
            if active:
                heading = number
        if not active or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells[0] == "Item" or re.fullmatch(r"[-: ]+", cells[0]):
            continue
        if len(cells) != 4 or cells[0] not in expected:
            audit.error(SPEC, number, "invalid Preservation map row")
            continue
        counts[cells[0]] += 1
        for column in cells[2:4]:
            for control in re.findall(rf"\b{CONTROL_ID}\b", column):
                if control not in controls:
                    audit.error(SPEC, number, f"undefined control ID {control}")
                mapped.add(control)
    for item in sorted(expected):
        if counts[item] != 1:
            audit.error(SPEC, heading, f"{item} must appear exactly once (found {counts[item]})")
    for control in sorted(controls.keys() - mapped):
        audit.error(SPEC, heading, f"control {control} is missing from Preservation map")


def check_references(audit: Audit) -> None:
    gates = SKILL / "references/gates.md"
    if not any(re.match(r"^Catalog version: \*\*[0-9]+\*\*", line) for line in audit.lines(gates)):
        audit.error(gates, 1, "missing Catalog version: **<n>** line")
    skill = SKILL / "SKILL.md"
    links = set(re.findall(r"\]\((?:\./)?references/([^\s)#]+)(?:#[^\s)]*)?\)", "\n".join(audit.lines(skill))))
    references = audit.root / SKILL / "references"
    for file in sorted(references.rglob("*")):
        if file.is_file() and file.relative_to(references).as_posix() not in links:
            audit.error(skill, 1, f"unlinked reference {file.relative_to(references).as_posix()}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", nargs="?", type=Path, default=Path(__file__).resolve().parents[2])
    audit = Audit(parser.parse_args().repository)
    controls = check_catalogs(audit)
    check_map(audit, controls)
    check_references(audit)
    if audit.errors:
        print("\n".join(audit.errors))
        print(f"readiness catalog: FAILED ({len(audit.errors)} violations)")
        return 1
    print(f"readiness catalog: OK ({len(controls)} controls, 160 preserved items)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
