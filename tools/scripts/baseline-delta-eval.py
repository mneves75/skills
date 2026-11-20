#!/usr/bin/env python3
"""Blinded zero-skill baseline-delta A/B evaluator. Python 3.11+, stdlib only.

For each case in tools/catalog-eval/baseline-delta-cases.json:
  1. Runs Control (no skill) and Treatment (full skills/<name>/SKILL.md prepended) using the
     generator model (Claude, tool-disabled, fresh single-turn).
  2. Deterministic pseudo-random A/B assignment balances position bias (half Treatment=A, half B).
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
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "tools/catalog-eval/baseline-delta-cases.json"
SCHEMA_ID = "baseline-delta-1"

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


def generate_claude(cmd: list[str], prompt: str, work: Path) -> tuple[int, str]:
    argv = [
        *cmd, "--safe-mode", "--setting-sources", "user", "--strict-mcp-config",
        "--disallowedTools", "mcp__*", "--print", "--no-session-persistence",
        "--output-format", "json", "--tools", "",
        "--model", GEN_MODEL, "--effort", GEN_EFFORT,
    ]
    p = subprocess.run(argv, cwd=work, input=prompt, capture_output=True, text=True, timeout=CALL_TIMEOUT)
    if p.returncode != 0:
        return p.returncode, f"ERROR rc={p.returncode}: {p.stderr[-1000:]}"
    parsed = json.loads(p.stdout)
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
        "-C", str(work), "--output-schema", str(schema_path), "-o", str(out_path), "-",
    ]
    p = subprocess.run(argv, cwd=work, input=prompt, capture_output=True, text=True, timeout=CALL_TIMEOUT)
    try:
        ans = json.loads(out_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        ans = None
        return p.returncode, None, f"unreadable judge output: {exc!r}\n{p.stderr[-1000:]}"
    return p.returncode, ans if p.returncode == 0 and isinstance(ans, dict) else None, p.stdout + "\n" + p.stderr[-1000:]


def run_case(case: dict, root: Path, out_dir: Path, claude_cmd: list[str], codex_cmd: list[str]) -> dict:
    cid = case["id"]
    skill = case["skill"]
    skill_md = root / "skills" / skill / "SKILL.md"
    skill_text = skill_md.read_text(encoding="utf-8")

    work_ctrl = out_dir / "work" / f"{cid}-control"
    work_trt = out_dir / "work" / f"{cid}-treatment"
    work_judge = out_dir / "work" / f"{cid}-judge"
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

    (out_dir / f"{cid}-control.md").write_text(out_ctrl, encoding="utf-8")
    (out_dir / f"{cid}-treatment.md").write_text(out_trt, encoding="utf-8")

    if rc_ctrl != 0 or rc_trt != 0:
        rec = {
            "id": cid, "skill": skill, "skill_bytes": len(skill_text.encode()),
            "error": f"generation failed: ctrl={rc_ctrl}, trt={rc_trt}",
        }
        print(f"{cid} ({skill}) ERROR {rec['error']}", flush=True)
        return rec

    # Deterministic 50/50 position flip keyed by hash of case id
    treatment_is_a = (hashlib.sha256(cid.encode()).digest()[0] % 2) == 0
    out_a, out_b = (out_trt, out_ctrl) if treatment_is_a else (out_ctrl, out_trt)
    jprompt = JUDGE_PROMPT.format(
        user_prompt=case["prompt"], rubric=case["rubric"], output_a=out_a, output_b=out_b
    )
    rc_j, jans, jraw = judge_codex(codex_cmd, jprompt, work_judge)
    (out_dir / f"{cid}-judge.raw.txt").write_text(jraw, encoding="utf-8")
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
    (out_dir / f"{cid}.json").write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(
        f"{cid} ({skill}): with_skill={score_trt} vs no_skill={score_ctrl} "
        f"(delta={score_trt - score_ctrl:+d}, winner={winner}/{jans['margin']})",
        flush=True,
    )
    return rec


def command_check(args: argparse.Namespace) -> int:
    spec = json.loads(args.cases.read_text(encoding="utf-8"))
    if spec.get("schema") != SCHEMA_ID:
        print(f"bad schema: {spec.get('schema')!r}")
        return 1
    problems = []
    for c in spec.get("cases", []):
        sfile = args.root / "skills" / c["skill"] / "SKILL.md"
        if not sfile.is_file():
            problems.append(f"{c['id']}: missing {sfile}")
    if problems:
        print("\n".join(problems))
        return 1
    print(f"baseline-delta check: {len(spec['cases'])} cases valid")
    return 0


def command_run(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    out_dir = args.out.resolve()
    if out_dir.is_relative_to(root) and not out_dir.is_relative_to(root / ".scratch"):
        sys.exit(f"--out {out_dir}: must be outside the repository or under .scratch/")
    spec = json.loads(args.cases.read_text(encoding="utf-8"))
    cases = spec["cases"]
    claude_cmd = shlex.split(args.claude_cmd)
    codex_cmd = shlex.split(args.codex_cmd)

    out_dir.mkdir(parents=True, exist_ok=True)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with cf.ThreadPoolExecutor(max_workers=3) as pool:
        futs = [pool.submit(run_case, c, root, out_dir, claude_cmd, codex_cmd) for c in cases]
        records = [f.result() for f in futs]

    summary = {
        "schema": "baseline-delta-run-1",
        "generator": {"model": GEN_MODEL, "effort": GEN_EFFORT},
        "judge": {"model": JUDGE_MODEL, "effort": JUDGE_EFFORT},
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
