#!/usr/bin/env python3
"""Minimal YAML frontmatter parser shared by catalog scripts. Python 3.11+, stdlib only."""
from __future__ import annotations

from pathlib import Path
import re

KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")
BLOCK_INDICATORS = frozenset({">", ">-", "|", "|-"})


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def _read_block_scalar(lines: list[str], start: int, end: int, indicator: str) -> tuple[str, int]:
    block: list[str] = []
    idx = start
    while idx < end and (lines[idx].startswith((" ", "\t")) or not lines[idx].strip()):
        block.append(lines[idx].strip())
        idx += 1
    sep = " " if indicator.startswith(">") else "\n"
    return sep.join(part for part in block if part).strip(), idx


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    """Parse Agent Skills YAML frontmatter and report structural or duplicate-key errors."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, ["missing YAML frontmatter opening ---"]

    end = next((idx for idx in range(1, len(lines)) if lines[idx].strip() == "---"), None)
    if end is None:
        return {}, ["unterminated YAML frontmatter"]

    fields: dict[str, str] = {}
    errors: list[str] = []
    idx = 1
    while idx < end:
        line = lines[idx]
        if not line.strip() or line.lstrip().startswith("#"):
            idx += 1
            continue
        match = KEY_RE.match(line)
        if not match:
            idx += 1
            continue
        key, raw_val = match.group(1), match.group(2).strip()
        if raw_val in BLOCK_INDICATORS:
            value, idx = _read_block_scalar(lines, idx + 1, end, raw_val)
        else:
            value = _unquote(raw_val)
            idx += 1
        if key in fields:
            errors.append(f"duplicate frontmatter key {key!r}")
        fields[key] = value
    return fields, errors


def read_skill_frontmatter(skill_md: Path) -> tuple[dict[str, str], list[str]]:
    """Read and parse YAML frontmatter from a SKILL.md path."""
    return parse_frontmatter(skill_md.read_text(encoding="utf-8"))
