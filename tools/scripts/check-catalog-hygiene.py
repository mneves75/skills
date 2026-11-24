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

INLINE_SPLIT_RE = re.compile(r"\]\(")
REF_DEF_RE = re.compile(r"^\s*\[([^\]]+)\]:\s*(\S+)(?:\s+.*)?$", re.MULTILINE)
REF_USE_FULL_RE = re.compile(r"!?\[[^\]]*\]\[([^\]]*)\]")
REF_USE_SHORT_RE = re.compile(r"!?\[([^\]]+)\](?![(\[:])")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
INDENT_CODE_RE = re.compile(r"^(?: {4}|\t)")


def _strip_inline_code(text: str) -> str:
    """Remove CommonMark inline code spans and neutralized backslash escapes."""
    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch == "\\" and i + 1 < n and text[i + 1] in "\\`[]()!":
            out.append("  ")
            i += 2
            continue
        if ch == "`":
            j = i
            while j < n and text[j] == "`":
                j += 1
            ticks = text[i:j]
            close = text.find(ticks, j)
            while close != -1 and (
                (close > 0 and text[close - 1] == "`")
                or (close + len(ticks) < n and text[close + len(ticks)] == "`")
            ):
                close = text.find(ticks, close + 1)
            if close != -1:
                i = close + len(ticks)
                continue
            out.append(ticks)
            i = j
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _strip_line_comments(line: str, in_comment: bool) -> tuple[str, bool]:
    out: list[str] = []
    pos = 0
    while pos < len(line):
        if in_comment:
            end = line.find("-->", pos)
            if end == -1:
                return "".join(out), True
            pos, in_comment = end + 3, False
        else:
            start = line.find("<!--", pos)
            if start == -1:
                out.append(line[pos:])
                break
            out.append(line[pos:start])
            pos, in_comment = start + 4, True
    return "".join(out), in_comment


def strip_fenced_code(text: str) -> str:
    out: list[str] = []
    fence_marker: str | None = None
    in_comment = False
    can_indent_code = True
    for line in text.splitlines():
        if fence_marker is not None:
            m = FENCE_RE.match(line)
            if m and m.group(1)[0] == fence_marker[0] and len(m.group(1)) >= len(fence_marker):
                fence_marker = None
            continue
        cleaned, in_comment = _strip_line_comments(line, in_comment)
        if not cleaned and in_comment:
            continue
        m = FENCE_RE.match(cleaned)
        if m:
            fence_marker = m.group(1)
            can_indent_code = False
            continue
        if can_indent_code and INDENT_CODE_RE.match(cleaned):
            continue
        out.append(cleaned)
        can_indent_code = not cleaned.strip()
    return "\n".join(out)


def _read_link_dest(prose: str, i: int) -> tuple[str, int] | None:
    n = len(prose)
    if i >= n:
        return None
    if prose[i] == "<":
        end = prose.find(">", i + 1)
        if end == -1 or "\n" in prose[i + 1 : end]:
            return None
        dest = prose[i + 1 : end].strip()
        return (dest, end + 1) if dest else None
    start, depth = i, 0
    while i < n and prose[i] not in " \t\r\n":
        if prose[i] == "(":
            depth += 1
        elif prose[i] == ")":
            if depth == 0:
                break
            depth -= 1
        i += 1
    dest = prose[start:i]
    return (dest, i) if dest else None


def _skip_link_title(prose: str, i: int) -> int | None:
    n = len(prose)
    if i >= n or prose[i] not in "\"'(":
        return i
    close = ")" if prose[i] == "(" else prose[i]
    i += 1
    while i < n and prose[i] != close:
        i += 2 if prose[i] == "\\" and i + 1 < n else 1
    return (i + 1) if i < n else None


def _parse_inline_link(prose: str, start: int) -> tuple[str, int] | None:
    """Parse destination and optional title after `](`, supporting balanced parens and escaped quotes."""
    n = len(prose)
    i = start
    while i < n and prose[i] in " \t":
        i += 1
    parsed = _read_link_dest(prose, i)
    if parsed is None:
        return None
    dest, i = parsed
    while i < n and prose[i] in " \t\r\n":
        i += 1
    after_title = _skip_link_title(prose, i)
    if after_title is None:
        return None
    i = after_title
    while i < n and prose[i] in " \t\r\n":
        i += 1
    return (dest, i + 1) if i < n and prose[i] == ")" else None


def _find_link_open(prose: str, close_idx: int, min_pos: int) -> int | None:
    depth = 0
    for i in range(close_idx - 1, min_pos - 1, -1):
        ch = prose[i]
        if ch == "\n":
            return None
        if ch == "]":
            depth += 1
        elif ch == "[":
            if depth == 0:
                return (i - 1) if i > min_pos and prose[i - 1] == "!" else i
            depth -= 1
    return None


def _scan_inline_links(prose: str) -> tuple[list[str], str]:
    links: list[str] = []
    kept: list[str] = []
    pos = 0
    for match in INLINE_SPLIT_RE.finditer(prose):
        if match.start() < pos:
            continue
        open_idx = _find_link_open(prose, match.start(), pos)
        if open_idx is None:
            continue
        parsed = _parse_inline_link(prose, match.end())
        if parsed is None:
            continue
        dest, end_pos = parsed
        kept.append(prose[pos:open_idx])
        kept.append(" ")
        pos = end_pos
        if _is_relative_target(dest):
            links.append(dest)
    kept.append(prose[pos:])
    return links, "".join(kept)


def _is_relative_target(target: str) -> bool:
    return bool(target) and not target.startswith("#") and not SCHEME_RE.match(target)


def _cited_ref_labels(body_without_defs: str) -> set[str]:
    labels: set[str] = set()
    for match in REF_USE_FULL_RE.finditer(body_without_defs):
        ref = match.group(1).strip()
        if ref:
            labels.add(ref.lower())
        else:
            # Collapsed reference `[label][]`
            full = match.group(0)
            inner = full[2 if full.startswith("!") else 1 : full.find("]")]
            if inner.strip():
                labels.add(inner.strip().lower())
    for match in REF_USE_SHORT_RE.finditer(body_without_defs):
        labels.add(match.group(1).strip().lower())
    return labels


def extract_relative_links(text: str, *, cited_only: bool = False) -> list[str]:
    clean = HTML_COMMENT_RE.sub("", strip_fenced_code(text))
    prose = _strip_inline_code(REF_DEF_RE.sub("", clean))
    links, prose_without_inline = _scan_inline_links(prose)

    defs: list[tuple[str, str]] = []
    for match in REF_DEF_RE.finditer(clean):
        label = match.group(1).strip().lower()
        target = match.group(2).strip().strip("<>")
        if _is_relative_target(target):
            defs.append((label, target))

    if not defs:
        return links
    if not cited_only:
        return links + [target for _, target in defs]

    cited = _cited_ref_labels(prose_without_inline)
    return links + [target for label, target in defs if label in cited]


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
    for link in extract_relative_links(text, cited_only=False):
        rel_path = link.split("#", 1)[0]
        if not rel_path:
            continue
        if _resolve_link(sdir, link, root) is None:
            errors.append(f"skills/{name}/SKILL.md: broken relative link {link!r}")
    for link in extract_relative_links(text, cited_only=True):
        target = _resolve_link(sdir, link, root)
        if target is not None:
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
