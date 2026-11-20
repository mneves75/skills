#!/usr/bin/env python3
"""Deterministic catalog hygiene guard for mneves75/skills. Python 3.11+, stdlib only.

Checks:
  1. Every root skill directory under skills/ has a valid SKILL.md under 500 lines and a
     non-empty description (error > 350 chars; warning > 220 chars).
  2. Every root skill is listed in README.md, HOWTO.md, AGENTS.md, docs/skill-ledger.md,
     and has its own explicit Route cell (`| `<name>` |`) in docs/skill-routing.md.
  3. Relative Markdown links inside skills/*/SKILL.md and skills/*/references/*.md resolve
     to existing files/directories within the repository (ignoring fenced code blocks and
     external/anchor URLs).
  4. References stay one level deep from SKILL.md: files in skills/<name>/references/ do
     not link to sibling references, except bare-basename references inside
     skills/security-audit/references/ (byte-identical upstream exception documented in
     AGENTS.md).

Usage:
  python3 tools/scripts/check-catalog-hygiene.py [--root PATH] [--json]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
MAX_SKILL_LINES = 500
WARN_DESC_CHARS = 220
MAX_DESC_CHARS = 350
UPSTREAM_BARE_BASENAME_EXEMPT = {"security-audit"}

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    """Minimal YAML frontmatter parser for Agent Skills metadata (name, description, license)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, ["missing YAML frontmatter opening ---"]
    end = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end = idx
            break
    if end is None:
        return {}, ["unterminated YAML frontmatter"]

    fields: dict[str, str] = {}
    i = 1
    while i < end:
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, raw_val = m.group(1), m.group(2).strip()
        if raw_val in (">", ">-", "|", "|-"):
            block: list[str] = []
            i += 1
            while i < end and (lines[i].startswith(" ") or lines[i].startswith("\t") or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            sep = " " if raw_val.startswith(">") else "\n"
            fields[key] = sep.join(part for part in block if part).strip()
            continue
        if (raw_val.startswith('"') and raw_val.endswith('"')) or (
            raw_val.startswith("'") and raw_val.endswith("'")
        ):
            raw_val = raw_val[1:-1]
        fields[key] = raw_val
        i += 1
    return fields, []


def strip_fenced_code(text: str) -> str:
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def extract_relative_links(text: str) -> list[str]:
    clean = strip_fenced_code(text)
    links: list[str] = []
    for m in LINK_RE.finditer(clean):
        target = m.group(1).strip().strip("<>")
        if not target or target.startswith("#"):
            continue
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            continue
        links.append(target)
    return links


def check_repo(root: Path) -> dict:
    root = root.resolve()
    skills_dir = root / "skills"
    errors: list[str] = []
    warnings: list[str] = []
    skill_stats: list[dict] = []

    if not skills_dir.is_dir():
        return {"ok": False, "errors": [f"missing skills directory: {skills_dir}"], "warnings": [], "skills": []}

    skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir())
    if not skill_dirs:
        errors.append("no skill directories found under skills/")

    skill_names: list[str] = []
    for sdir in skill_dirs:
        name = sdir.name
        skill_names.append(name)
        skill_md = sdir / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"{name}: missing SKILL.md")
            continue

        text = skill_md.read_text(encoding="utf-8")
        line_count = len(text.splitlines())
        fm, fm_errs = parse_frontmatter(text)
        for err in fm_errs:
            errors.append(f"skills/{name}/SKILL.md: {err}")

        if fm.get("name") != name:
            errors.append(f"skills/{name}/SKILL.md: frontmatter name {fm.get('name')!r} != directory {name!r}")

        desc = fm.get("description", "")
        desc_len = len(desc)
        if desc_len < 20:
            errors.append(f"skills/{name}/SKILL.md: description too short ({desc_len} chars)")
        elif desc_len > MAX_DESC_CHARS:
            errors.append(f"skills/{name}/SKILL.md: description exceeds {MAX_DESC_CHARS} chars ({desc_len})")
        elif desc_len > WARN_DESC_CHARS:
            warnings.append(f"skills/{name}/SKILL.md: description is {desc_len} chars (recommended <= {WARN_DESC_CHARS})")

        if line_count >= MAX_SKILL_LINES:
            errors.append(f"skills/{name}/SKILL.md: {line_count} lines (must be < {MAX_SKILL_LINES})")

        # Validate relative links in SKILL.md
        for link in extract_relative_links(text):
            rel_path = link.split("#", 1)[0]
            if not rel_path:
                continue
            target = (sdir / rel_path).resolve()
            if not target.is_relative_to(root) or not target.exists():
                errors.append(f"skills/{name}/SKILL.md: broken relative link {link!r}")

        # Validate references/ links and enforce 1-level-deep rule
        refs_dir = sdir / "references"
        if refs_dir.is_dir():
            for ref_file in sorted(refs_dir.glob("*.md")):
                ref_text = ref_file.read_text(encoding="utf-8")
                for link in extract_relative_links(ref_text):
                    rel_path = link.split("#", 1)[0]
                    if not rel_path:
                        continue
                    target = (ref_file.parent / rel_path).resolve()
                    if not target.is_relative_to(root) or not target.exists():
                        errors.append(f"skills/{name}/references/{ref_file.name}: broken relative link {link!r}")
                        continue
                    if target.is_relative_to(refs_dir.resolve()) and target != ref_file.resolve():
                        is_bare_basename = "/" not in rel_path and "\\" not in rel_path
                        if name in UPSTREAM_BARE_BASENAME_EXEMPT and is_bare_basename:
                            continue
                        errors.append(
                            f"skills/{name}/references/{ref_file.name}: reference-to-reference link {link!r} "
                            "(references must be linked 1 level deep from SKILL.md only)"
                        )

        skill_stats.append({
            "name": name,
            "lines": line_count,
            "description_chars": desc_len,
        })

    # Coverage across canonical index & routing docs
    doc_files = [
        ("README.md", "plain"),
        ("HOWTO.md", "plain"),
        ("AGENTS.md", "plain"),
        ("docs/skill-ledger.md", "plain"),
        ("docs/skill-routing.md", "routing_table"),
    ]
    for rel_doc, mode in doc_files:
        doc_path = root / rel_doc
        if not doc_path.is_file():
            errors.append(f"missing required index doc: {rel_doc}")
            continue
        content = doc_path.read_text(encoding="utf-8")
        for name in skill_names:
            if mode == "routing_table":
                route_pat = re.compile(rf"\|\s*`{re.escape(name)}`\s*\|")
                if not route_pat.search(content):
                    errors.append(f"{rel_doc}: missing dedicated Route table row for `{name}`")
            else:
                if not re.search(rf"(?<![A-Za-z0-9_-]){re.escape(name)}(?![A-Za-z0-9_-])", content):
                    errors.append(f"{rel_doc}: missing root skill `{name}`")

    total_desc_chars = sum(s["description_chars"] for s in skill_stats)
    total_lines = sum(s["lines"] for s in skill_stats)
    return {
        "ok": not errors,
        "root_skill_count": len(skill_names),
        "total_description_chars": total_desc_chars,
        "total_skill_lines": total_lines,
        "errors": errors,
        "warnings": warnings,
        "skills": skill_stats,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check catalog hygiene invariants for skills/.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    result = check_repo(args.root)
    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        status = "OK" if result["ok"] else "FAIL"
        print(
            f"catalog-hygiene {status}: {result['root_skill_count']} root skills, "
            f"{result['total_description_chars']} description chars, "
            f"{result['total_skill_lines']} SKILL.md lines, "
            f"{len(result['warnings'])} warning(s), {len(result['errors'])} error(s)"
        )
        for w in result["warnings"]:
            print(f"WARN: {w}")
        for e in result["errors"]:
            print(f"ERROR: {e}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
