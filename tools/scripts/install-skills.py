#!/usr/bin/env python3
"""Curated profile installer with automatic overlap exclusion for mneves75/skills. Python 3.11+, stdlib only.

Dry-run by default; pass --apply to create symlinks in --target. Never overwrites a real
directory (protecting local edits). Automatically excludes superseded skills declared in
tools/install-profiles.json (for example, skips collections/pstack/skills/babysit whenever
a usable babysit-pr with SKILL.md is selected or already present in --target).

Usage:
  python3 tools/scripts/install-skills.py --list-profiles [--root PATH]
  python3 tools/scripts/install-skills.py --profile NAME --target DIR [--exclude SKILL ...] [--apply]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from frontmatter import read_skill_frontmatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PROFILES_PATH = ROOT / "tools/install-profiles.json"
PROFILES_SCHEMA = "install-profiles-1"


def load_profiles(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != PROFILES_SCHEMA:
        raise ValueError(f"{path}: unexpected schema {data.get('schema')!r}")
    return data


def resolve_profile_entries(root: Path, spec: dict, profile_name: str) -> list[Path]:
    profiles = spec["profiles"]
    if profile_name not in profiles:
        raise ValueError(f"unknown profile {profile_name!r}; available: {', '.join(sorted(profiles))}")
    prof = profiles[profile_name]
    dirs: list[Path] = []
    seen: set[Path] = set()
    for rel in prof.get("include", []):
        p = (root / rel).resolve()
        if not (p / "SKILL.md").is_file():
            raise ValueError(f"profile {profile_name!r}: missing explicit include {rel!r} ({p / 'SKILL.md'})")
        if p not in seen:
            seen.add(p)
            dirs.append(p)
    for pattern in prof.get("globs", []):
        for p in sorted(root.glob(pattern)):
            rp = p.resolve()
            if p.is_dir() and (p / "SKILL.md").is_file() and rp not in seen:
                seen.add(rp)
                dirs.append(rp)
    return dirs


def _usable_installed_names(target: Path | None) -> set[str]:
    if target is None or not target.is_dir():
        return set()
    return {
        entry.name
        for entry in target.iterdir()
        if entry.is_dir() and (entry / "SKILL.md").is_file()
    }


def plan_install(
    root: Path,
    spec: dict,
    profile_name: str,
    target: Path | None = None,
    extra_excludes: set[str] | None = None,
) -> dict:
    root = root.resolve()
    excludes = set(extra_excludes or set())
    raw_dirs = resolve_profile_entries(root, spec, profile_name)
    candidate_names = {d.name for d in raw_dirs} | _usable_installed_names(target)
    rules = spec.get("exclude_when_present", {})

    selected: list[dict] = []
    skipped: list[dict] = []
    seen_names: set[str] = set()

    for sdir in raw_dirs:
        name = sdir.name
        rel = sdir.relative_to(root).as_posix()
        if name in excludes:
            skipped.append({"name": name, "source": rel, "reason": "explicit --exclude"})
            continue
        rule = rules.get(name)
        if rule:
            prefix = rule.get("source_prefix", "")
            superseded_by = rule["superseded_by"]
            if rel.startswith(prefix) and superseded_by in candidate_names and superseded_by not in excludes:
                skipped.append({
                    "name": name,
                    "source": rel,
                    "reason": f"superseded by {superseded_by}: {rule['reason']}",
                })
                continue
        if name in seen_names:
            skipped.append({"name": name, "source": rel, "reason": "duplicate name already selected earlier"})
            continue
        seen_names.add(name)
        fm, _ = read_skill_frontmatter(sdir / "SKILL.md")
        desc = fm.get("description", "")
        selected.append({"name": name, "source": rel, "abs_source": str(sdir), "description_chars": len(desc)})

    total_chars = sum(s["description_chars"] for s in selected)
    floor = int(spec.get("claude_listing_floor_chars", 16000))
    return {
        "profile": profile_name,
        "selected": selected,
        "skipped": skipped,
        "selected_count": len(selected),
        "description_chars": total_chars,
        "floor_pct": round((total_chars / floor) * 100, 1) if floor else 0.0,
    }


def apply_plan(plan: dict, target: Path, replace_symlinks: bool = False) -> tuple[list[str], list[str], list[str]]:
    target.mkdir(parents=True, exist_ok=True)
    linked: list[str] = []
    unchanged: list[str] = []
    conflicts: list[str] = []

    for item in plan["selected"]:
        dest = target / item["name"]
        src = Path(item["abs_source"])
        if dest.is_symlink():
            if dest.resolve() == src.resolve():
                unchanged.append(item["name"])
                continue
            if replace_symlinks:
                dest.unlink()
                dest.symlink_to(src)
                linked.append(item["name"])
            else:
                conflicts.append(
                    f"{dest}: existing symlink points to {dest.resolve()} (use --replace-symlinks to retarget)"
                )
        elif dest.exists():
            conflicts.append(f"{dest}: existing non-symlink file/directory refused (local edits protected)")
        else:
            dest.symlink_to(src)
            linked.append(item["name"])
    return linked, unchanged, conflicts


def _print_profiles(root: Path, spec: dict, as_json: bool) -> int:
    rows = []
    for pname, pmeta in spec["profiles"].items():
        pl = plan_install(root, spec, pname)
        rows.append({
            "profile": pname,
            "skills": pl["selected_count"],
            "skipped": len(pl["skipped"]),
            "description_chars": pl["description_chars"],
            "floor_pct": pl["floor_pct"],
            "description": pmeta["description"],
        })
    if as_json:
        print(json.dumps(rows, indent=2))
    else:
        for r in rows:
            print(
                f"{r['profile']:18s} {r['skills']:2d} skills  "
                f"{r['description_chars']:5d} chars ({r['floor_pct']:4.1f}% of 16K floor)  "
                f"skipped={r['skipped']}  — {r['description']}"
            )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Install curated mneves75/skills profiles with overlap exclusion.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--profiles", type=Path, default=PROFILES_PATH)
    parser.add_argument("--list-profiles", action="store_true")
    parser.add_argument("--profile", default="")
    parser.add_argument("--target", type=Path, default=None)
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--replace-symlinks", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    spec = load_profiles(args.profiles)
    if args.list_profiles:
        return _print_profiles(args.root, spec, args.as_json)

    if not args.profile:
        parser.error("provide --list-profiles or --profile NAME")

    plan = plan_install(args.root, spec, args.profile, target=args.target, extra_excludes=set(args.exclude))
    if args.apply:
        if args.target is None:
            parser.error("--apply requires --target DIR")
        linked, unchanged, conflicts = apply_plan(plan, args.target, replace_symlinks=args.replace_symlinks)
        plan["applied"] = {"linked": linked, "unchanged": unchanged, "conflicts": conflicts}
        if args.as_json:
            print(json.dumps(plan, indent=2))
        else:
            print(
                f"install-skills APPLIED profile={plan['profile']}: linked={len(linked)}, "
                f"unchanged={len(unchanged)}, skipped={len(plan['skipped'])}, conflicts={len(conflicts)}, "
                f"budget={plan['description_chars']} chars ({plan['floor_pct']}% of 16K)"
            )
            for s in plan["skipped"]:
                print(f"SKIP {s['name']}: {s['reason']}")
            for c in conflicts:
                print(f"CONFLICT: {c}")
        return 1 if conflicts else 0

    if args.as_json:
        print(json.dumps(plan, indent=2))
    else:
        print(
            f"install-skills DRY-RUN profile={plan['profile']}: {plan['selected_count']} skills, "
            f"{len(plan['skipped'])} skipped, budget={plan['description_chars']} chars ({plan['floor_pct']}% of 16K)"
        )
        for s in plan["skipped"]:
            print(f"SKIP {s['name']}: {s['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
