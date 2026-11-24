#!/usr/bin/env python3
"""Blinded zero-skill baseline-delta A/B evaluator. Python 3.11+, stdlib only.

For each case in tools/catalog-eval/baseline-delta-cases.json:
  1. Runs Control (no skill) and Treatment (full skills/<name>/SKILL.md prepended) using the
     generator model (Claude, tool-disabled, fresh single-turn).
  2. Deterministic counterbalanced A/B assignment across the frozen case list (half Treatment=A,
     half Treatment=B) to prevent position confounding.
  3. Sends (prompt, rubric, Output A, Output B) to a DIFFERENT blinded judge model (Codex,
     tool-disabled, strict JSON schema) that never sees which output used a skill.
  4. Unblinds scores, computes lift (treatment_score - control_score), and writes summary.json.

Usage:
  python3 tools/scripts/baseline-delta-eval.py check [--cases PATH] [--root PATH]
  python3 tools/scripts/baseline-delta-eval.py run --out DIR [--claude-cmd CMD] [--codex-cmd CMD]
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

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "tools/catalog-eval/baseline-delta-cases.json"
SCHEMA_ID = "baseline-delta-1"
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

GEN_MODEL, GEN_EFFORT = "claude-opus-5-5", "medium"
JUDGE_MODEL, JUDGE_EFFORT = "gpt-6.2-sol", "high"
CALL_TIMEOUT = float(os.environ.get("BASELINE_DELTA_TIMEOUT", "300"))

JUDGE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["score_a", "score_b", "winner", "margin", "reason"],
    "properties": {
        "score_a": {"type": "integer", "minimum": 0, "maximum": 5},
        "score_b": {"type": "integer", "minimum": 0, "maximum": 5},
        "winner": {"type": "string", "enum": ["A", "B", "tie"]},
        "margin": {"type": "string", "enum": ["decisive", "slight", "none"]},
        "reason": {"type": "string"},
    },
}

JUDGE_PROMPT = """You are a strict, impartial senior engineering evaluator performing a BLINDED A/B comparison.
Two assistants answered the same user request. You do NOT know how either output was generated.

Judge purely on real-world user value against the rubric below:
- Reward concrete usefulness, accuracy, honoring boundaries, clarity, and decision quality.
- Do NOT reward length, boilerplate headings, theatrical formatting, or jargon for its own sake.
- If both outputs are equally useful in practice, pick "tie" with margin "none".

User request:
{user_prompt}

Evaluation rubric:
{rubric}

<output_a>
{output_a}
</output_a>

<output_b>
{output_b}
</output_b>

Return JSON only matching the schema: integer scores 0-5 for score_a and score_b, winner ("A", "B", or "tie"), margin ("decisive", "slight", or "none"), and a concise 1-2 sentence reason."""


def _is_safe_id(value: str) -> bool:
    return bool(SAFE_ID_RE.fullmatch(value)) and ".." not in value


def _safe_child(base: Path, *parts: str) -> Path:
    base_resolved = base.resolve()
    candidate = base_resolved.joinpath(*parts).resolve()
    if not candidate.is_relative_to(base_resolved) or candidate == base_resolved:
        raise ValueError(f"path escapes output directory: {candidate}")
    return candidate


def enumerate_root_skills(root: Path) -> dict[str, Path]:
    skills_dir = root.resolve() / "skills"
    if not skills_dir.is_dir():
        return {}
    found: dict[str, Path] = {}
    for sdir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        sfile = sdir / "SKILL.md"
        if sfile.is_file():
            found[sdir.name] = sfile.resolve()
    return found


def validate_cases(spec: object, available_skills: dict[str, Path]) -> list[str]:
    if not isinstance(spec, dict):
        return ["cases file is not a JSON object"]
    problems: list[str] = []
    if spec.get("schema") != SCHEMA_ID:
        problems.append(f"bad schema: {spec.get('schema')!r}")
    cases = spec.get("cases")
    if not isinstance(cases, list) or not cases:
        return problems + ["cases must be a non-empty list"]
    seen: set[str] = set()
    for idx, case in enumerate(cases):
        if not isinstance(case, dict) or not isinstance(case.get("id"), str) or not case["id"]:
            problems.append(f"cases[{idx}]: missing string id")
            continue
        cid = case["id"]
        if not _is_safe_id(cid):
            problems.append(f"{cid!r}: id must match [A-Za-z0-9][A-Za-z0-9._-]* without '..'")
        if cid in seen:
            problems.append(f"{cid}: duplicate case id")
        seen.add(cid)
        skill = case.get("skill")
        if not isinstance(skill, str) or skill not in available_skills:
            problems.append(f"{cid}: unknown root skill {skill!r}")
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            problems.append(f"{cid}: missing prompt")
        if not isinstance(case.get("rubric"), str) or not case["rubric"].strip():
            problems.append(f"{cid}: missing rubric")
    return problems


def assign_positions(cases: list[dict]) -> dict[str, bool]:
    """Deterministically assign half of cases to treatment=A and half to treatment=B."""
    ordered = sorted(
        (hashlib.sha256(c["id"].encode("utf-8")).hexdigest(), c["id"])
        for c in cases
    )
    a_count = len(ordered) // 2
    if len(ordered) % 2 == 1:
        # Deterministically decide whether the odd case goes to A or B from the suite digest.
        a_count += int(ordered[0][0], 16) % 2
    return {cid: idx < a_count for idx, (_, cid) in enumerate(ordered)}


def _is_valid_score(val: object) -> bool:
    return isinstance(val, int) and not isinstance(val, bool) and 0 <= val <= 5


def validate_judge_answer(ans: object) -> dict | None:
    if not isinstance(ans, dict):
        return None
    if not (_is_valid_score(ans.get("score_a")) and _is_valid_score(ans.get("score_b"))):
        return None
    if ans.get("winner") not in ("A", "B", "tie"):
        return None
    if ans.get("margin") not in ("decisive", "slight", "none"):
        return None
    if not isinstance(ans.get("reason"), str):
        return None
    return ans


def generate_claude(cmd: list[str], prompt: str, work: Path) -> tuple[int, str]:
    argv = [
        *cmd, "--safe-mode", "--setting-sources", "user", "--strict-mcp-config",
        "--disallowedTools", "mcp__*", "--print", "--no-session-persistence",
        "--output-format", "json", "--tools", "",
        "--model", GEN_MODEL, "--effort", GEN_EFFORT,
    ]
    try:
        p = subprocess.run(argv, cwd=work, input=prompt, capture_output=True, text=True, timeout=CALL_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return -1, f"ERROR: {exc!r}"
    if p.returncode != 0:
        return p.returncode, f"ERROR rc={p.returncode}: {p.stderr[-1000:]}"
    try:
        parsed = json.loads(p.stdout)
    except ValueError as exc:
        return -1, f"UNPARSEABLE ({exc!r}): {p.stdout[:1000]}"
    if isinstance(parsed, dict) and parsed.get("is_error") is False and isinstance(parsed.get("result"), str):
        return 0, parsed["result"]
    return -1, f"UNPARSEABLE: {p.stdout[:1000]}"


def judge_codex(cmd: list[str], prompt: str, work: Path) -> tuple[int, dict | None, str]:
    schema_path, out_path = work / "judge_schema.json", work / "judge_answer.json"
    schema_path.write_text(json.dumps(JUDGE_SCHEMA), encoding="utf-8")
    out_path.unlink(missing_ok=True)
    argv = [
        *cmd, "exec", "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check",
        "--ephemeral", "-s", "read-only", "--disable", "shell_tool", "--json",
        "-m", JUDGE_MODEL, "-c", f"model_reasoning_effort={JUDGE_EFFORT}",
        "-c", "project_doc_max_bytes=0",
        "-C", str(work), "--output-schema", str(schema_path), "-o", str(out_path), "-",
    ]
    try:
        p = subprocess.run(argv, cwd=work, input=prompt, capture_output=True, text=True, timeout=CALL_TIMEOUT)
        rc, stdout, stderr = p.returncode, p.stdout, p.stderr
    except (OSError, subprocess.TimeoutExpired) as exc:
        return -1, None, f"judge execution error: {exc!r}"
    try:
        raw_ans = json.loads(out_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return rc, None, f"unreadable judge output: {exc!r}\n{stderr[-1000:]}"
    valid = validate_judge_answer(raw_ans) if rc == 0 else None
    return rc, valid, stdout + "\n" + stderr[-1000:]


def run_case(
    case: dict,
    skill_md: Path,
    treatment_is_a: bool,
    out_dir: Path,
    claude_cmd: list[str],
    codex_cmd: list[str],
) -> dict:
    cid = case["id"]
    skill = case["skill"]
    skill_text = skill_md.read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="baseline-delta-") as tmp:
        work_root = Path(tmp)
        work_ctrl = work_root / "control"
        work_trt = work_root / "treatment"
        work_judge = work_root / "judge"
        for w in (work_ctrl, work_trt, work_judge):
            w.mkdir(parents=True, exist_ok=True)

        control_prompt = case["prompt"]
        treatment_prompt = (
            f"You have activated the following skill instructions for this task. Follow them carefully.\n\n"
            f"<skill name=\"{skill}\">\n{skill_text}\n</skill>\n\n"
            f"User request:\n{case['prompt']}"
        )

        with cf.ThreadPoolExecutor(max_workers=2) as pool:
            f_ctrl = pool.submit(generate_claude, claude_cmd, control_prompt, work_ctrl)
            f_trt = pool.submit(generate_claude, claude_cmd, treatment_prompt, work_trt)
            rc_ctrl, out_ctrl = f_ctrl.result()
            rc_trt, out_trt = f_trt.result()

        _safe_child(out_dir, f"{cid}-control.md").write_text(out_ctrl, encoding="utf-8")
        _safe_child(out_dir, f"{cid}-treatment.md").write_text(out_trt, encoding="utf-8")

        if rc_ctrl != 0 or rc_trt != 0:
            rec = {
                "id": cid, "skill": skill, "skill_bytes": len(skill_text.encode()),
                "error": f"generation failed: ctrl={rc_ctrl}, trt={rc_trt}",
            }
            print(f"{cid} ({skill}) ERROR {rec['error']}", flush=True)
            return rec

        out_a, out_b = (out_trt, out_ctrl) if treatment_is_a else (out_ctrl, out_trt)
        jprompt = JUDGE_PROMPT.format(
            user_prompt=case["prompt"], rubric=case["rubric"], output_a=out_a, output_b=out_b
        )
        rc_j, jans, jraw = judge_codex(codex_cmd, jprompt, work_judge)
    _safe_child(out_dir, f"{cid}-judge.raw.txt").write_text(jraw, encoding="utf-8")
    if rc_j != 0 or jans is None:
        rec = {
            "id": cid, "skill": skill, "skill_bytes": len(skill_text.encode()),
            "error": f"judge failed rc={rc_j}",
        }
        print(f"{cid} ({skill}) JUDGE_ERROR rc={rc_j}", flush=True)
        return rec

    score_trt = jans["score_a"] if treatment_is_a else jans["score_b"]
    score_ctrl = jans["score_b"] if treatment_is_a else jans["score_a"]
    raw_winner = jans["winner"]
    if raw_winner == "tie":
        winner = "tie"
    elif (raw_winner == "A" and treatment_is_a) or (raw_winner == "B" and not treatment_is_a):
        winner = "with_skill"
    else:
        winner = "no_skill"

    rec = {
        "id": cid,
        "skill": skill,
        "skill_bytes": len(skill_text.encode()),
        "skill_lines": len(skill_text.splitlines()),
        "treatment_position": "A" if treatment_is_a else "B",
        "score_no_skill": score_ctrl,
        "score_with_skill": score_trt,
        "delta": score_trt - score_ctrl,
        "winner": winner,
        "margin": jans["margin"],
        "reason": jans["reason"],
        "error": None,
    }
    _safe_child(out_dir, f"{cid}.json").write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(
        f"{cid} ({skill}): with_skill={score_trt} vs no_skill={score_ctrl} "
        f"(delta={score_trt - score_ctrl:+d}, winner={winner}/{jans['margin']})",
        flush=True,
    )
    return rec


def _load_and_validate(root: Path, cases_path: Path) -> tuple[list[dict], dict[str, Path], list[str]]:
    available = enumerate_root_skills(root)
    if not available:
        return [], available, [f"no skills found under {root / 'skills'}"]
    try:
        spec = json.loads(cases_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], available, [f"{cases_path}: {exc}"]
    problems = validate_cases(spec, available)
    if problems:
        return [], available, problems
    return spec["cases"], available, []


def command_check(args: argparse.Namespace) -> int:
    cases, _, problems = _load_and_validate(args.root, args.cases)
    if problems:
        print("\n".join(problems))
        return 1
    print(f"baseline-delta check: {len(cases)} cases valid")
    return 0


def command_run(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    out_dir = args.out.resolve()
    if out_dir.is_relative_to(root) and not out_dir.is_relative_to(root / ".scratch"):
        sys.exit(f"--out {out_dir}: must be outside the repository or under .scratch/")

    cases, available, problems = _load_and_validate(root, args.cases)
    if problems:
        sys.exit("\n".join(problems))

    positions = assign_positions(cases)
    claude_cmd = shlex.split(args.claude_cmd)
    codex_cmd = shlex.split(args.codex_cmd)

    out_dir.mkdir(parents=True, exist_ok=True)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with cf.ThreadPoolExecutor(max_workers=3) as pool:
        futs = [
            pool.submit(run_case, c, available[c["skill"]], positions[c["id"]], out_dir, claude_cmd, codex_cmd)
            for c in cases
        ]
        records = [f.result() for f in futs]

    summary = {
        "schema": "baseline-delta-run-1",
        "generator": {"model": GEN_MODEL, "effort": GEN_EFFORT},
        "judge": {"model": JUDGE_MODEL, "effort": JUDGE_EFFORT},
        "position_balance": {
            "A": sum(1 for v in positions.values() if v),
            "B": sum(1 for v in positions.values() if not v),
        },
        "started_at": started,
        "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": records,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0 if all(r.get("error") is None for r in records) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Blinded zero-skill baseline-delta evaluator.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "run"):
        p = sub.add_parser(name)
        p.add_argument("--cases", type=Path, default=CASES)
        p.add_argument("--root", type=Path, default=ROOT)
        if name == "run":
            p.add_argument("--out", type=Path, required=True)
            p.add_argument("--claude-cmd", default="claude")
            p.add_argument("--codex-cmd", default="codex")
    args = parser.parse_args()
    return command_check(args) if args.command == "check" else command_run(args)


if __name__ == "__main__":
    sys.exit(main())
