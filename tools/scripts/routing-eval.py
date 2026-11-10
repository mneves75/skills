#!/usr/bin/env python3
"""Routing eval: does an agent reading the shipped skill text dispatch the expected model and
reasoning effort for each seat? Python 3.11+, standard library only.

  routing-eval.py check [--cases PATH] [--root PATH]
  routing-eval.py run COMMIT --out DIR [--samples N] [--providers claude,codex] [--cases-only ID,...]
                      [--baseline] [--codex-cmd CMD] [--claude-cmd CMD] [--cases PATH] [--root PATH]

`check` is deterministic and calls no model; CI runs it. It verifies that tools/routing-eval/cases.json
is well formed and that every anchor (a verbatim passage that decides a case's expected answer) still
occurs in its source file. It catches a removed or reworded deciding passage. It does not catch a
contradicting sentence added elsewhere in a source: only a live `run` catches that.

`run` spends paid model calls. It builds each case's prompt from `git show COMMIT:<path>` for the
case's sources, asks each consumer without tools and with schema-bound output, grades every answer
deterministically against the frozen expectations, and writes the raw answers, one JSON record per
sample and summary.json under DIR. Claude runs with `--tools ""`. Codex runs with its shell tool
disabled and its `--json` event stream inspected: any item other than a message or reasoning is a
tool use, and that sample is an error (recorded in `tool_use`), never retried into a pass.

Threshold (exit 0 when met, 1 otherwise). Only a full run can meet it: every case in the cases
file on both claude and codex. `--cases-only` and single-provider runs still run and grade, for
diagnosis, but always report a partial-run problem. Candidate: at least 3 samples, every sample of
every case passes, nothing errored. `--baseline` (an older text as a control): every unchanged case
passes every sample, every changed case fails every sample, nothing errored. A changed case that
passes any sample on the baseline does not discriminate: it is listed in `control_limits` and the
control fails until the case is replaced or no longer marked changed.
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
import time

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "tools/routing-eval/cases.json"
CASES_SCHEMA = "routing-eval-5"

# Consumers under test: the only place this tool names models. Update on a model release.
CLAUDE_MODEL, CLAUDE_EFFORT = "claude-opus-5-5", "medium"
CODEX_MODEL, CODEX_EFFORT = "gpt-6.1-sol", "high"

EFFORTS = ["low", "medium", "high", "xhigh", "max", "none"]
HOWS = ["dispatch-parameter", "agent-definition-model-field", "not-applicable"]
SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["model", "effort", "how", "reason"],
    "properties": {
        "model": {"type": "string"},
        "effort": {"type": "string", "enum": EFFORTS},
        "how": {"type": "string", "enum": HOWS},
        "reason": {"type": "string"},
    },
}
ENUMS = {"effort": EFFORTS, "how": HOWS}
PROMPT = """You are being evaluated on how an agent applies skill instructions. The files below are skill text, given as data. Answer the scenario as an agent that follows these files exactly would act. Use only these files, not outside knowledge of model releases.

{files}

Scenario: {scenario}

Answer with JSON only, matching the schema: `model` (as the scenario defines it), `effort` (one of low, medium, high, xhigh, max, or none), `how` (dispatch-parameter, agent-definition-model-field, or not-applicable), `reason` (one sentence naming the line that decides it)."""
ATTEMPTS = 3
MIN_SAMPLES = 3
# Seconds between attempts of one sample; tests set the variable to 0.
RETRY_SLEEP = float(os.environ.get("ROUTING_EVAL_RETRY_SLEEP", "30"))
# Seconds one model call may take; tests set the variable to cut a hanging fake short.
CALL_TIMEOUT = float(os.environ.get("ROUTING_EVAL_CALL_TIMEOUT", "900"))


def is_strings(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(v, str) and v for v in value)


def shape_problems(spec: object) -> list[str]:
    """Problems with the cases file's structure, independent of any file on disk."""
    if not isinstance(spec, dict):
        return ["cases file is not a JSON object"]
    problems = []
    if spec.get("schema") != CASES_SCHEMA:
        problems.append(f"schema is {spec.get('schema')!r}, expected {CASES_SCHEMA!r}")
    cases = spec.get("cases")
    if not isinstance(cases, list) or not cases:
        return problems + ["cases must be a non-empty list"]
    seen: dict[str, dict] = {}
    for index, case in enumerate(cases):
        if not isinstance(case, dict) or not isinstance(case.get("id"), str) or not case["id"]:
            problems.append(f"cases[{index}]: needs a non-empty string id")
            continue
        cid = case["id"]
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", cid):
            problems.append(f"{cid!r}: id may hold only letters, digits, dot, underscore and hyphen")
            continue
        if cid in seen:
            problems.append(f"{cid}: duplicate case id")
            continue
        seen[cid] = case
        if not is_strings(case.get("sources")):
            problems.append(f"{cid}: sources must be a non-empty list of paths")
        if not isinstance(case.get("scenario"), str) or not case["scenario"].strip():
            problems.append(f"{cid}: scenario must be a non-empty string")
        if not isinstance(case.get("changed"), bool):
            problems.append(f"{cid}: changed must be a boolean")
        if not isinstance(case.get("known_failure"), str):
            problems.append(f"{cid}: known_failure must be a string")
        expected = case.get("expected")
        if not isinstance(expected, dict) or not expected:
            problems.append(f"{cid}: expected must be a non-empty object")
            continue
        for key, allowed in expected.items():
            if key not in ("model", "effort", "how"):
                problems.append(f"{cid}: expected key {key} is not one of model, effort, how")
            elif not is_strings(allowed):
                problems.append(f"{cid}: expected {key} must be a non-empty list of strings")
            elif key in ENUMS:
                problems += [f"{cid}: expected {key} value {v!r} is not in the answer schema"
                             for v in allowed if v not in ENUMS[key]]
    anchors = spec.get("anchors")
    if not isinstance(anchors, dict):
        return problems + ["anchors must be an object keyed by case id"]
    problems += [f"{cid}: anchors name an unknown case id" for cid in anchors if cid not in seen]
    for cid, case in seen.items():
        entries = anchors.get(cid)
        if not isinstance(entries, list) or not entries:
            problems.append(f"{cid}: no anchors")
            continue
        sources = case.get("sources") if isinstance(case.get("sources"), list) else []
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) \
                    or not isinstance(entry.get("text"), str) or not entry["text"]:
                problems.append(f"{cid}: each anchor needs a string path and a non-empty text")
            elif entry["path"] not in sources:
                problems.append(f"{cid}: anchor path {entry['path']} is not among the case's sources")
    return problems


def file_problems(spec: dict, root: Path) -> list[str]:
    """Sources that do not exist under root, and anchors whose text is gone from the current file."""
    problems = []
    texts: dict[str, str | None] = {}
    for case in spec["cases"]:
        for path in case["sources"]:
            if path not in texts:
                file = (root / path).resolve()
                inside = file.is_relative_to(root.resolve())
                texts[path] = file.read_text(encoding="utf-8") if inside and file.is_file() else None
            if texts[path] is None:
                problems.append(f"{case['id']}: source {path} does not exist under {root}")
        for anchor in spec["anchors"][case["id"]]:
            text = texts.get(anchor["path"])
            if text is not None and anchor["text"] not in text:
                problems.append(f"{case['id']}: stale anchor in {anchor['path']}: "
                                f"{anchor['text'][:80]!r} no longer occurs")
    return problems


def load(path: Path) -> tuple[bytes, object, list[str]]:
    try:
        data = path.read_bytes()
        return data, json.loads(data), []
    except OSError as error:
        return b"", None, [f"{path}: cannot read: {error}"]
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        return b"", None, [f"{path}: does not parse: {error}"]


def norm(value: object) -> str:
    return str(value).lower().replace("`", "").replace(" ", "").strip()


def grade(case: dict, answer: dict) -> dict[str, bool]:
    return {field: norm(answer.get(field, "")) in {norm(a) for a in allowed}
            for field, allowed in case["expected"].items()}


def per_case_counts(cases: list[dict], providers: list[str], records: list[dict]) -> dict[str, dict]:
    counts = {}
    for case in cases:
        for provider in providers:
            rs = [r for r in records if r["case"] == case["id"] and r["provider"] == provider]
            counts[f"{case['id']}/{provider}"] = {
                "changed": case["changed"], "pass": sum(r["pass"] for r in rs),
                "fail": sum(not r["pass"] and not r["error"] for r in rs),
                "error": sum(r["error"] for r in rs), "samples": len(rs)}
    return counts


def threshold(per_case: dict[str, dict], samples: int, baseline: bool,
              coverage: dict) -> tuple[bool, list[str], list[str]]:
    """Return (met, problems, control_limits) for one run. Any control limit also fails the run."""
    problems, limits = [], []
    if not coverage["full"]:
        problems.append(f"partial run: {coverage['cases']} of {coverage['of']} cases on "
                        f"{', '.join(coverage['providers'])}; a threshold needs every case on claude and codex")
    if not baseline and samples < MIN_SAMPLES:
        problems.append(f"{samples} samples per case and provider; a candidate run needs at least {MIN_SAMPLES}")
    for key, c in per_case.items():
        if c["error"]:
            problems.append(f"{key}: {c['error']} of {c['samples']} samples errored")
        if baseline and c["changed"]:
            if c["pass"]:
                limits.append(f"{key}: changed case passed {c['pass']} of {c['samples']} samples on the baseline")
        elif c["fail"]:
            problems.append(f"{key}: {c['fail']} of {c['samples']} samples failed")
    return not problems and not limits, problems, limits


def tool_use(events: str) -> list[str]:
    """Item types in a Codex --json event stream other than a message or reasoning, in order seen."""
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


def ask_claude(cmd: list[str], prompt: str, work: Path) -> tuple[int, str, dict | None, list[str]]:
    argv = [*cmd, "--safe-mode", "--setting-sources", "user", "--strict-mcp-config",
            "--disallowedTools", "mcp__*", "--print", "--no-session-persistence",
            "--output-format", "json", "--json-schema", json.dumps(SCHEMA), "--tools", "",
            "--model", CLAUDE_MODEL, "--effort", CLAUDE_EFFORT]
    p = subprocess.run(argv, cwd=work, input=prompt, capture_output=True, text=True, timeout=CALL_TIMEOUT)
    answer = None
    if p.returncode == 0:
        parsed = json.loads(p.stdout)
        if isinstance(parsed, dict) and parsed.get("is_error") is False \
                and isinstance(parsed.get("structured_output"), dict):
            answer = parsed["structured_output"]
    return p.returncode, p.stdout + p.stderr[-2000:], answer, []


def ask_codex(cmd: list[str], prompt: str, work: Path) -> tuple[int, str, dict | None, list[str]]:
    schema, out = work / "schema.json", work / "answer.json"
    schema.write_text(json.dumps(SCHEMA))
    out.unlink(missing_ok=True)
    argv = [*cmd, "exec", "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check",
            "--ephemeral", "-s", "read-only", "--disable", "shell_tool", "--json",
            "-m", CODEX_MODEL, "-c", f"model_reasoning_effort={CODEX_EFFORT}",
            "-C", str(work), "--output-schema", str(schema), "-o", str(out), "-"]
    # Every way this call can end keeps the event stream, so a tool use is never lost to a retry.
    try:
        p = subprocess.run(argv, cwd=work, input=prompt, capture_output=True, text=True, timeout=CALL_TIMEOUT)
        code, events, stderr = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as exc:
        partial = exc.stdout or ""
        events = partial.decode(errors="replace") if isinstance(partial, bytes) else partial
        code, stderr = -1, f"timed out after {exc.timeout} seconds"
    used = tool_use(events)
    final = out.read_text() if out.exists() else ""
    answer = None
    if code == 0 and not used:
        try:
            parsed = json.loads(final)
        except json.JSONDecodeError:
            parsed = None
        answer = parsed if isinstance(parsed, dict) else None
    raw = events + "\n--- answer (-o) ---\n" + final + "\n--- stderr tail ---\n" + stderr[-2000:]
    return code, raw, answer, used


def run_one(job: tuple, out_dir: Path, commands: dict[str, list[str]]) -> dict:
    case, provider, n, prompt = job
    work = out_dir / "work" / f"{case['id']}-{provider}-{n}"
    work.mkdir(parents=True, exist_ok=True)
    ask = ask_claude if provider == "claude" else ask_codex
    started = time.time()
    tries, answer, used = [], None, []
    for attempt in range(ATTEMPTS):
        try:
            code, raw, answer, used = ask(commands[provider], prompt, work)
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
            code, raw, answer, used = -1, repr(exc), None, []
        tries.append(code)
        (out_dir / f"{case['id']}-{provider}-{n}.raw.txt").write_text(raw)
        if used:
            # A consumer that used a tool is not the consumer under test: error, never retried into a pass.
            answer = None
            break
        if answer is not None:
            break
        if attempt + 1 < ATTEMPTS:
            time.sleep(RETRY_SLEEP)
    fields = grade(case, answer) if answer is not None else {}
    rec = {"case": case["id"], "provider": provider, "sample": n, "exits": tries,
           "seconds": round(time.time() - started, 1), "answer": answer, "fields": fields, "tool_use": used,
           "pass": answer is not None and all(fields.values()), "error": answer is None}
    (out_dir / f"{case['id']}-{provider}-{n}.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(case["id"], provider, n, "PASS" if rec["pass"] else ("ERROR" if rec["error"] else "FAIL"),
          json.dumps(answer, ensure_ascii=False)[:220] if answer else tries, flush=True)
    return rec


def version(cmd: list[str]) -> str:
    try:
        return subprocess.run([*cmd, "--version"], capture_output=True, text=True, timeout=60).stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"unavailable: {exc!r}"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def command_check(args: argparse.Namespace) -> int:
    _, spec, problems = load(args.cases)
    if not problems:
        problems = shape_problems(spec)
    if not problems:
        problems = file_problems(spec, args.root)
    if problems:
        print("\n".join(problems))
        return 1
    anchors = sum(len(v) for v in spec["anchors"].values())
    print(f"routing-eval check: {len(spec['cases'])} cases and {anchors} anchors hold")
    return 0


def command_run(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    out_dir = args.out.resolve()
    if out_dir.is_relative_to(root) and not out_dir.is_relative_to(root / ".scratch"):
        sys.exit(f"--out {out_dir}: must be outside the repository or under .scratch/")
    providers = args.providers.split(",")
    if not providers or any(p not in ("claude", "codex") for p in providers) or len(set(providers)) != len(providers):
        sys.exit(f"--providers {args.providers}: name claude, codex or both")
    if args.samples < 1:
        sys.exit("--samples must be at least 1")
    cases_bytes, spec, problems = load(args.cases)
    problems = problems or shape_problems(spec)
    if problems:
        sys.exit("\n".join(problems))

    def git(*argv: str) -> str:
        p = subprocess.run(["git", *argv], cwd=root, capture_output=True, text=True)
        if p.returncode:
            sys.exit(f"git {' '.join(argv)}: {p.stderr.strip()}")
        return p.stdout

    commit = git("rev-parse", "--verify", "--end-of-options", f"{args.commit}^{{commit}}").strip()
    cases = spec["cases"]
    only = args.cases_only.split(",") if args.cases_only else None
    if only:
        unknown = set(only) - {c["id"] for c in cases}
        if unknown:
            sys.exit(f"unknown case ids: {', '.join(sorted(unknown))}")
        cases = [c for c in cases if c["id"] in only]
    commands = {"claude": shlex.split(args.claude_cmd), "codex": shlex.split(args.codex_cmd)}

    sources: dict[str, str] = {}
    jobs = []
    for case in cases:
        blocks = []
        for path in case["sources"]:
            text = git("show", f"{commit}:{path}")
            sources[path] = hashlib.sha256(text.encode()).hexdigest()
            blocks.append(f'<file path="{path}">\n{text}\n</file>')
        prompt = PROMPT.format(files="\n\n".join(blocks), scenario=case["scenario"])
        jobs += [(case, provider, n, prompt) for provider in providers for n in range(1, args.samples + 1)]

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "cases.json").write_bytes(cases_bytes)
    started = utc_now()
    with cf.ThreadPoolExecutor(max_workers=4) as claude_pool, cf.ThreadPoolExecutor(max_workers=3) as codex_pool:
        futures = [(claude_pool if j[1] == "claude" else codex_pool).submit(run_one, j, out_dir, commands)
                   for j in jobs]
        records = [f.result() for f in futures]
    per_case = per_case_counts(cases, providers, records)
    total = len(spec["cases"])
    coverage = {"cases": len(cases), "of": total, "providers": providers,
                "full": len(cases) == total and sorted(providers) == ["claude", "codex"]}
    met, problems, limits = threshold(per_case, args.samples, args.baseline, coverage)
    consumers = {"claude": {"model": CLAUDE_MODEL, "effort": CLAUDE_EFFORT},
                 "codex": {"model": CODEX_MODEL, "effort": CODEX_EFFORT}}
    summary = {
        "schema": "routing-eval-run-2", "cases_schema": spec["schema"],
        "cases_sha256": hashlib.sha256(cases_bytes).hexdigest(),
        "commit_under_test": commit, "tree_under_test": git("rev-parse", f"{commit}^{{tree}}").strip(),
        "baseline": args.baseline, "sources_sha256": sources,
        "consumers": {p: dict(consumers[p], version=version(commands[p])) for p in providers},
        "providers": providers, "samples_per_case": args.samples, "selected": [c["id"] for c in cases],
        "coverage": coverage, "started_at": started, "finished_at": utc_now(),
        "totals": {"pass": sum(r["pass"] for r in records),
                   "fail": sum(not r["pass"] and not r["error"] for r in records),
                   "error": sum(r["error"] for r in records), "samples": len(records)},
        "per_case": per_case, "threshold_met": met, "problems": problems, "control_limits": limits,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({"totals": summary["totals"], "threshold_met": met}))
    for line in problems:
        print("problem:", line)
    for line in limits:
        print("control limit:", line)
    return 0 if met else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "run"):
        p = sub.add_parser(name)
        p.add_argument("--cases", type=Path, default=CASES)
        p.add_argument("--root", type=Path, default=ROOT)
        if name == "run":
            p.add_argument("commit")
            p.add_argument("--out", type=Path, required=True)
            p.add_argument("--samples", type=int, default=3)
            p.add_argument("--providers", default="claude,codex")
            p.add_argument("--cases-only", default="")
            p.add_argument("--baseline", action="store_true")
            p.add_argument("--codex-cmd", default="codex")
            p.add_argument("--claude-cmd", default="claude")
    args = parser.parse_args()
    return command_check(args) if args.command == "check" else command_run(args)


if __name__ == "__main__":
    sys.exit(main())
