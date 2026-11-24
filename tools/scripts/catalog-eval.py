#!/usr/bin/env python3
"""Skill-selection confusion-matrix eval over live skills/*/SKILL.md metadata. Python 3.11+, stdlib only.

  catalog-eval.py check [--cases PATH] [--root PATH] [--include-pstack]
  catalog-eval.py run --out DIR [--samples N] [--providers claude,codex] [--cases-only ID,...]
                      [--claude-cmd CMD] [--codex-cmd CMD] [--cases PATH] [--root PATH] [--include-pstack]

`check` is deterministic and makes no model calls: it validates cases.json and confirms every
named expected/forbidden skill exists under skills/ (or is "none"), case IDs are unique and
filename-safe, and expected/forbidden sets are disjoint.

`run` builds a prompt containing ONLY the live skills/*/SKILL.md `name` and `description`
fields (never docs/skill-routing.md or skill bodies), calls Claude and/or Codex without tools
and with a strict JSON enum schema over ["none", *skill_names], grades every sample, and writes
per-sample records plus summary.json (including per-cluster pass rates and the confusion matrix)
under DIR.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import time

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from frontmatter import read_skill_frontmatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "tools/catalog-eval/cases.json"
CASES_SCHEMA = "catalog-eval-1"
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

CLAUDE_MODEL, CLAUDE_EFFORT = "claude-opus-5-5", "medium"
CODEX_MODEL, CODEX_EFFORT = "gpt-6.2-sol", "high"
CALL_TIMEOUT = float(os.environ.get("CATALOG_EVAL_CALL_TIMEOUT", "300"))

PROMPT_TEMPLATE = """You are an AI coding agent choosing whether to activate a skill from your installed catalog before acting on a user's request.
You are given ONLY each skill's name and description below (treated as data).

Rules:
- Select the single best primary skill name from the catalog, OR "none" if no specialist skill applies.
- Honor explicit-only or negative constraints in descriptions (for example, do not select a deployment skill for casual "ship", do not select an explicit-only workflow when its words are used as ordinary punctuation, and do not select a broad audit for a trivial typo or factual question).
- Answer with JSON only matching the schema.

Installed skill catalog:
{catalog}

User request:
{user_prompt}
"""


def is_safe_id(value: str) -> bool:
    return bool(SAFE_ID_RE.fullmatch(value)) and ".." not in value


def safe_child(base: Path, *parts: str) -> Path:
    base_resolved = base.resolve()
    raw = base_resolved.joinpath(*parts)
    if raw.is_symlink():
        raise ValueError(f"refusing symlink output path: {raw}")
    candidate = raw.resolve()
    if not candidate.is_relative_to(base_resolved) or candidate == base_resolved:
        raise ValueError(f"path escapes output directory: {candidate}")
    return candidate


def load_catalog(root: Path, include_pstack: bool = False) -> list[dict[str, str]]:
    roots = [root.resolve() / "skills"]
    if include_pstack:
        roots.append(root.resolve() / "collections" / "pstack" / "skills")
    entries: list[dict[str, str]] = []
    seen: set[str] = set()
    for skills_dir in roots:
        if not skills_dir.is_dir():
            continue
        for sdir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
            sfile = sdir / "SKILL.md"
            if not sfile.is_file():
                continue
            fm, _ = read_skill_frontmatter(sfile)
            name = fm.get("name", sdir.name)
            if name in seen:
                continue
            seen.add(name)
            entries.append({"name": name, "description": fm.get("description", "")})
    return entries


def format_catalog(entries: list[dict[str, str]]) -> str:
    return "\n".join(f"- {e['name']}: {e['description']}" for e in entries)


def build_schema(skill_names: list[str]) -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["selected", "reason"],
        "properties": {
            "selected": {"type": "string", "enum": ["none", *skill_names]},
            "reason": {"type": "string"},
        },
    }


def _validate_target_list(
    cid: str,
    field: str,
    value: object,
    valid_targets: set[str],
    *,
    required: bool,
) -> tuple[set[str], list[str]]:
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value) or (required and not value):
        req_note = "non-empty " if required else ""
        return set(), [f"{cid}: {field} must be a {req_note}list of skill names or 'none'"]
    problems = [
        f"{cid}: {field} skill {name!r} not in skills/ or 'none'"
        for name in value
        if name not in valid_targets
    ]
    return set(value), problems


def _validate_one_case(idx: int, case: object, valid_targets: set[str], seen: set[str]) -> list[str]:
    if not isinstance(case, dict) or not isinstance(case.get("id"), str) or not case["id"]:
        return [f"cases[{idx}]: missing string id"]
    cid = case["id"]
    problems: list[str] = []
    if not is_safe_id(cid):
        problems.append(f"{cid!r}: id must match [A-Za-z0-9][A-Za-z0-9._-]* without '..'")
    if cid in seen:
        problems.append(f"{cid}: duplicate case id")
    seen.add(cid)
    if not isinstance(case.get("cluster"), str) or not case["cluster"].strip():
        problems.append(f"{cid}: missing cluster")
    if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
        problems.append(f"{cid}: missing prompt")

    exp_set, exp_errs = _validate_target_list(cid, "expected", case.get("expected"), valid_targets, required=True)
    forb_set, forb_errs = _validate_target_list(
        cid, "forbidden", case.get("forbidden", []), valid_targets, required=False
    )
    problems.extend(exp_errs)
    problems.extend(forb_errs)
    overlap = sorted(exp_set & forb_set)
    if overlap:
        problems.append(f"{cid}: expected and forbidden overlap on {overlap}")
    return problems


def validate_cases(spec: object, skill_names: set[str]) -> list[str]:
    if not isinstance(spec, dict):
        return ["cases file is not a JSON object"]
    problems: list[str] = []
    if spec.get("schema") != CASES_SCHEMA:
        problems.append(f"schema is {spec.get('schema')!r}, expected {CASES_SCHEMA!r}")
    cases = spec.get("cases")
    if not isinstance(cases, list) or not cases:
        return problems + ["cases must be a non-empty list"]
    valid_targets = skill_names | {"none"}
    seen: set[str] = set()
    for idx, case in enumerate(cases):
        problems.extend(_validate_one_case(idx, case, valid_targets, seen))
    return problems


def tool_use(events: str) -> list[str]:
    seen: list[str] = []
    for line in events.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item") if isinstance(event, dict) else None
        if isinstance(item, dict):
            kind = str(item.get("type", "unknown"))
            if kind not in ("agent_message", "reasoning") and kind not in seen:
                seen.append(kind)
    return seen


def ask_claude(cmd: list[str], prompt: str, schema: dict, work: Path) -> tuple[int, str, dict | None, list[str]]:
    argv = [
        *cmd, "--safe-mode", "--setting-sources", "user", "--strict-mcp-config",
        "--disallowedTools", "mcp__*", "--print", "--no-session-persistence",
        "--output-format", "json", "--json-schema", json.dumps(schema), "--tools", "",
        "--model", CLAUDE_MODEL, "--effort", CLAUDE_EFFORT,
    ]
    p = subprocess.run(argv, cwd=work, input=prompt, capture_output=True, text=True, timeout=CALL_TIMEOUT)
    answer = None
    if p.returncode == 0:
        parsed = json.loads(p.stdout)
        if (
            isinstance(parsed, dict)
            and parsed.get("is_error") is False
            and isinstance(parsed.get("structured_output"), dict)
        ):
            answer = parsed["structured_output"]
    return p.returncode, p.stdout + p.stderr[-2000:], answer, []


def ask_codex(cmd: list[str], prompt: str, schema: dict, work: Path) -> tuple[int, str, dict | None, list[str]]:
    schema_path, out_path = work / "schema.json", work / "answer.json"
    schema_path.write_text(json.dumps(schema), encoding="utf-8")
    out_path.unlink(missing_ok=True)
    argv = [
        *cmd, "exec", "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check",
        "--ephemeral", "-s", "read-only", "--disable", "shell_tool", "--json",
        "-m", CODEX_MODEL, "-c", f"model_reasoning_effort={CODEX_EFFORT}",
        "-c", "project_doc_max_bytes=0",
        "-C", str(work), "--output-schema", str(schema_path), "-o", str(out_path), "-",
    ]
    try:
        p = subprocess.run(argv, cwd=work, input=prompt, capture_output=True, text=True, timeout=CALL_TIMEOUT)
        code, events, stderr = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as exc:
        partial = exc.stdout or ""
        events = partial.decode(errors="replace") if isinstance(partial, bytes) else partial
        code, stderr = -1, f"timed out after {exc.timeout} seconds"
    used = tool_use(events)
    try:
        final = out_path.read_text(encoding="utf-8")
        parsed = json.loads(final)
    except (OSError, ValueError) as exc:
        final, parsed = f"unreadable answer: {exc!r}", None
    answer = parsed if code == 0 and not used and isinstance(parsed, dict) else None
    raw = events + "\n--- answer (-o) ---\n" + final + "\n--- stderr tail ---\n" + stderr[-2000:]
    return code, raw, answer, used


def normalize_answer(answer: object) -> dict | None:
    if not isinstance(answer, dict):
        return None
    selected = answer.get("selected")
    if not isinstance(selected, str) or not selected.strip():
        return None
    reason = answer.get("reason", "")
    return {"selected": selected.strip(), "reason": reason if isinstance(reason, str) else str(reason)}


def grade_record(case: dict, answer: dict | None) -> tuple[bool, bool]:
    norm = normalize_answer(answer)
    if norm is None:
        return False, False
    sel = norm["selected"]
    forbidden_hit = sel in case.get("forbidden", [])
    passed = (sel in case["expected"]) and not forbidden_hit
    return passed, forbidden_hit


def _tally(records: list[dict]) -> dict[str, int]:
    return {
        "pass": sum(r["pass"] for r in records),
        "fail": sum(not r["pass"] and not r["error"] for r in records),
        "forbidden": sum(r["forbidden_hit"] for r in records),
        "error": sum(r["error"] for r in records),
        "total": len(records),
    }


def summarize(cases: list[dict], providers: list[str], records: list[dict]) -> dict:
    by_provider = {p: _tally([r for r in records if r["provider"] == p]) for p in providers}
    by_cluster: dict[str, dict[str, int]] = {}
    for cluster in sorted({c["cluster"] for c in cases}):
        cids = {c["id"] for c in cases if c["cluster"] == cluster}
        by_cluster[cluster] = _tally([r for r in records if r["case"] in cids])

    case_map = {c["id"]: c for c in cases}
    matrix: dict[str, dict[str, int]] = {}
    confusions: list[dict] = []
    for r in records:
        exp_key = "|".join(case_map[r["case"]]["expected"])
        norm = normalize_answer(r.get("answer"))
        sel = norm["selected"] if norm is not None else "<error>"
        matrix.setdefault(exp_key, {})
        matrix[exp_key][sel] = matrix[exp_key].get(sel, 0) + 1
        if not r["pass"]:
            confusions.append({
                "case": r["case"],
                "cluster": case_map[r["case"]]["cluster"],
                "provider": r["provider"],
                "sample": r["sample"],
                "expected": case_map[r["case"]]["expected"],
                "selected": sel,
                "forbidden_hit": r["forbidden_hit"],
                "reason": norm["reason"] if norm is not None else "",
            })

    return {
        "totals": _tally(records),
        "by_provider": by_provider,
        "by_cluster": by_cluster,
        "confusion_matrix": matrix,
        "misses": confusions,
    }


def run_one(job: tuple, schema: dict, out_dir: Path, commands: dict[str, list[str]]) -> dict:
    case, provider, n, prompt = job
    stem = f"{case['id']}-{provider}-{n}"
    raw_path = safe_child(out_dir, f"{stem}.raw.txt")
    rec_path = safe_child(out_dir, f"{stem}.json")

    ask = ask_claude if provider == "claude" else ask_codex
    started = time.time()
    with tempfile.TemporaryDirectory(prefix="catalog-eval-") as tmp:
        work = Path(tmp)
        try:
            code, raw, raw_answer, used = ask(commands[provider], prompt, schema, work)
        except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
            code, raw, raw_answer, used = -1, repr(exc), None, []

    answer = normalize_answer(raw_answer)
    raw_path.write_text(raw, encoding="utf-8")
    passed, forbidden_hit = grade_record(case, answer)
    rec = {
        "case": case["id"],
        "cluster": case["cluster"],
        "provider": provider,
        "sample": n,
        "exit": code,
        "seconds": round(time.time() - started, 1),
        "answer": answer,
        "tool_use": used,
        "pass": answer is not None and passed,
        "forbidden_hit": forbidden_hit,
        "error": answer is None,
    }
    rec_path.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    tag = "PASS" if rec["pass"] else ("ERROR" if rec["error"] else ("FORBIDDEN" if forbidden_hit else "FAIL"))
    sel = answer["selected"] if answer is not None else code
    print(f"{case['id']} {provider}#{n} {tag} selected={sel} expected={case['expected']}", flush=True)
    return rec


def _select_cases(cases: list[dict], cases_only: str) -> list[dict]:
    if not cases_only.strip():
        return cases
    only = {x.strip() for x in cases_only.split(",") if x.strip()}
    if not only:
        sys.exit("--cases-only selected zero cases")
    unknown = only - {c["id"] for c in cases}
    if unknown:
        sys.exit(f"unknown case ids: {', '.join(sorted(unknown))}")
    selected = [c for c in cases if c["id"] in only]
    if not selected:
        sys.exit("--cases-only selected zero cases")
    return selected


def command_check(args: argparse.Namespace) -> int:
    catalog = load_catalog(args.root, include_pstack=args.include_pstack)
    if not catalog:
        print(f"no skills found under {args.root / 'skills'}")
        return 1
    try:
        spec = json.loads(args.cases.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"{args.cases}: {exc}")
        return 1
    problems = validate_cases(spec, {e["name"] for e in catalog})
    if problems:
        print("\n".join(problems))
        return 1
    scope = "root+pstack" if args.include_pstack else "root"
    print(f"catalog-eval check: {len(spec['cases'])} cases valid against {len(catalog)} {scope} skills")
    return 0


def command_run(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    out_dir = args.out.resolve()
    if out_dir.is_relative_to(root) and not out_dir.is_relative_to(root / ".scratch"):
        sys.exit(f"--out {out_dir}: must be outside the repository or under .scratch/")
    providers = [p.strip() for p in args.providers.split(",") if p.strip()]
    if not providers or any(p not in ("claude", "codex") for p in providers) or len(set(providers)) != len(providers):
        sys.exit(f"--providers {args.providers}: name claude, codex, or claude,codex")
    if args.samples < 1:
        sys.exit("--samples must be >= 1")

    catalog = load_catalog(root, include_pstack=args.include_pstack)
    skill_names = [e["name"] for e in catalog]
    cases_bytes = args.cases.read_bytes()
    spec = json.loads(cases_bytes)
    problems = validate_cases(spec, set(skill_names))
    if problems:
        sys.exit("\n".join(problems))

    cases = _select_cases(spec["cases"], args.cases_only)
    catalog_text = format_catalog(catalog)
    schema = build_schema(skill_names)
    commands = {"claude": shlex.split(args.claude_cmd), "codex": shlex.split(args.codex_cmd)}

    jobs = [
        (case, provider, n, PROMPT_TEMPLATE.format(catalog=catalog_text, user_prompt=case["prompt"]))
        for case in cases
        for provider in providers
        for n in range(1, args.samples + 1)
    ]

    out_dir.mkdir(parents=True, exist_ok=True)
    safe_child(out_dir, "catalog.txt").write_text(catalog_text + "\n", encoding="utf-8")
    safe_child(out_dir, "cases.json").write_bytes(cases_bytes)

    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with cf.ThreadPoolExecutor(max_workers=4) as claude_pool, cf.ThreadPoolExecutor(max_workers=3) as codex_pool:
        futures = [
            (claude_pool if j[1] == "claude" else codex_pool).submit(run_one, j, schema, out_dir, commands)
            for j in jobs
        ]
        records = [f.result() for f in futures]

    stats = summarize(cases, providers, records)
    summary = {
        "schema": "catalog-eval-run-1",
        "cases_sha256": hashlib.sha256(cases_bytes).hexdigest(),
        "catalog_sha256": hashlib.sha256(catalog_text.encode("utf-8")).hexdigest(),
        "catalog_skill_count": len(catalog),
        "catalog_description_chars": sum(len(e["description"]) for e in catalog),
        "providers": providers,
        "models": {
            "claude": {"model": CLAUDE_MODEL, "effort": CLAUDE_EFFORT},
            "codex": {"model": CODEX_MODEL, "effort": CODEX_EFFORT},
        },
        "samples_per_case": args.samples,
        "started_at": started,
        "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        **stats,
    }
    safe_child(out_dir, "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"totals": summary["totals"], "by_provider": summary["by_provider"]}, indent=2))
    totals = summary["totals"]
    return 0 if totals["fail"] == 0 and totals["forbidden"] == 0 and totals["error"] == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Skill-selection confusion-matrix evaluator.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "run"):
        p = sub.add_parser(name)
        p.add_argument("--cases", type=Path, default=CASES)
        p.add_argument("--root", type=Path, default=ROOT)
        p.add_argument("--include-pstack", action="store_true")
        if name == "run":
            p.add_argument("--out", type=Path, required=True)
            p.add_argument("--samples", type=int, default=1)
            p.add_argument("--providers", default="claude,codex")
            p.add_argument("--cases-only", default="")
            p.add_argument("--claude-cmd", default="claude")
            p.add_argument("--codex-cmd", default="codex")
    args = parser.parse_args()
    return command_check(args) if args.command == "check" else command_run(args)


if __name__ == "__main__":
    sys.exit(main())
