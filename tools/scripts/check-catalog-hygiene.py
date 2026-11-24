#!/usr/bin/env python3
"""Deterministic catalog hygiene guard for mneves75/skills. Python 3.11+, stdlib only.

Checks:
  1. Every root skill directory under skills/ has a valid SKILL.md under 500 lines, unique
     frontmatter keys, and a non-empty description (error > 350 chars; warning > 220 chars).
  2. Every root skill is listed in README.md, HOWTO.md, AGENTS.md, docs/skill-ledger.md,
     and has its own explicit Route cell (`| `<name>` |`) in docs/skill-routing.md.
  3. Relative Markdown links (inline and reference-style) inside skills/*/SKILL.md and
     skills/*/references/**/*.md resolve to existing files/directories within the repository
     (ignoring fenced code blocks and external/anchor URLs).
  4. References stay one level deep from SKILL.md: every shipped file under
     skills/<name>/references/ is linked directly from SKILL.md, and files under references/
     do not link to sibling or nested references, except bare-basename references inside
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

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from frontmatter import parse_frontmatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
MAX_SKILL_LINES = 500
WARN_DESC_CHARS = 220
MAX_DESC_CHARS = 350
UPSTREAM_BARE_BASENAME_EXEMPT = frozenset({"security-audit"})

INLINE_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
REF_DEF_RE = re.compile(r"^\s*\[([^\]]+)\]:\s*(\S+)(?:\s+.*)?$", re.MULTILINE)
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


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


def _is_relative_target(target: str) -> bool:
    return bool(target) and not target.startswith("#") and not SCHEME_RE.match(target)


def extract_relative_links(text: str) -> list[str]:
    clean = strip_fenced_code(text)
    links: list[str] = []
    for match in INLINE_LINK_RE.finditer(clean):
        target = match.group(1).strip().strip("<>")
        if _is_relative_target(target):
            links.append(target)
    for match in REF_DEF_RE.finditer(clean):
        target = match.group(2).strip().strip("<>")
        if _is_relative_target(target):
            links.append(target)
    return links


def _resolve_link(base_dir: Path, link: str, root: Path) -> Path | None:
    rel_path = link.split("#", 1)[0]
    if not rel_path:
        return None
    target = (base_dir / rel_path).resolve()
    if not target.is_relative_to(root) or not target.exists():
        return None
    return target


def _check_skill_metadata(name: str, text: str, errors: list[str], warnings: list[str]) -> dict:
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

    return {"name": name, "lines": line_count, "description_chars": desc_len}


def _check_references(
    name: str,
    sdir: Path,
    root: Path,
    linked_from_skill: set[Path],
    errors: list[str],
) -> None:
    refs_dir = sdir / "references"
    if not refs_dir.is_dir():
        return
    refs_resolved = refs_dir.resolve()
    for ref_file in sorted(refs_dir.rglob("*.md")):
        ref_resolved = ref_file.resolve()
        rel_ref = ref_file.relative_to(sdir).as_posix()
        if ref_resolved not in linked_from_skill:
            errors.append(
                f"skills/{name}/{rel_ref}: unlinked reference file "
                "(every reference must be linked directly from SKILL.md)"
            )
        ref_text = ref_file.read_text(encoding="utf-8")
        for link in extract_relative_links(ref_text):
            rel_path = link.split("#", 1)[0]
            if not rel_path:
                continue
            target = _resolve_link(ref_file.parent, link, root)
            if target is None:
                errors.append(f"skills/{name}/{rel_ref}: broken relative link {link!r}")
                continue
            if target.is_relative_to(refs_resolved) and target != ref_resolved:
                is_bare_basename = "/" not in rel_path and "\\" not in rel_path
                if name in UPSTREAM_BARE_BASENAME_EXEMPT and is_bare_basename:
                    continue
                errors.append(
                    f"skills/{name}/{rel_ref}: reference-to-reference link {link!r} "
                    "(references must be linked 1 level deep from SKILL.md only)"
                )


def _check_skill_dir(sdir: Path, root: Path, errors: list[str], warnings: list[str]) -> dict | None:
    name = sdir.name
    skill_md = sdir / "SKILL.md"
    if not skill_md.is_file():
        errors.append(f"{name}: missing SKILL.md")
        return None

    text = skill_md.read_text(encoding="utf-8")
    stat = _check_skill_metadata(name, text, errors, warnings)

    linked_targets: set[Path] = set()
    for link in extract_relative_links(text):
        rel_path = link.split("#", 1)[0]
        if not rel_path:
            continue
        target = _resolve_link(sdir, link, root)
        if target is None:
            errors.append(f"skills/{name}/SKILL.md: broken relative link {link!r}")
        else:
            linked_targets.add(target)

    _check_references(name, sdir, root, linked_targets, errors)
    return stat


def _check_index_docs(root: Path, skill_names: list[str], errors: list[str]) -> None:
    doc_files = (
        ("README.md", "plain"),
        ("HOWTO.md", "plain"),
        ("AGENTS.md", "plain"),
        ("docs/skill-ledger.md", "plain"),
        ("docs/skill-routing.md", "routing_table"),
    )
    for rel_doc, mode in doc_files:
        doc_path = root / rel_doc
        if not doc_path.is_file():
            errors.append(f"missing required index doc: {rel_doc}")
            continue
        content = doc_path.read_text(encoding="utf-8")
        for name in skill_names:
            if mode == "routing_table":
                if not re.search(rf"\|\s*`{re.escape(name)}`\s*\|", content):
                    errors.append(f"{rel_doc}: missing dedicated Route table row for `{name}`")
            elif not re.search(rf"(?<![A-Za-z0-9_-]){re.escape(name)}(?![A-Za-z0-9_-])", content):
                errors.append(f"{rel_doc}: missing root skill `{name}`")


def check_repo(root: Path) -> dict:
    root = root.resolve()
    skills_dir = root / "skills"
    errors: list[str] = []
    warnings: list[str] = []
    skill_stats: list[dict] = []

    if not skills_dir.is_dir():
        return {
            "ok": False,
            "root_skill_count": 0,
            "total_description_chars": 0,
            "total_skill_lines": 0,
            "errors": [f"missing skills directory: {skills_dir}"],
            "warnings": [],
            "skills": [],
        }

    skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir())
    if not skill_dirs:
        errors.append("no skill directories found under skills/")

    skill_names: list[str] = []
    for sdir in skill_dirs:
        skill_names.append(sdir.name)
        stat = _check_skill_dir(sdir, root, errors, warnings)
        if stat is not None:
            skill_stats.append(stat)

    _check_index_docs(root, skill_names, errors)

    return {
        "ok": not errors,
        "root_skill_count": len(skill_names),
        "total_description_chars": sum(s["description_chars"] for s in skill_stats),
        "total_skill_lines": sum(s["lines"] for s in skill_stats),
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
