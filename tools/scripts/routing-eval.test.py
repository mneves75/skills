#!/usr/bin/env python3
"""Tests for tools/scripts/routing-eval.py: real cases, planted check controls, the grader, and
`run` end to end against fake `claude` and `codex` on PATH (no network, no quota). Python 3.11+."""

import copy
import importlib.util
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools/scripts/routing-eval.py"
_spec = importlib.util.spec_from_file_location("routing_eval", TOOL)
assert _spec and _spec.loader
routing_eval = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(routing_eval)

SKILL_TEXT = "# Fake skill\n\nThe reviewer runs at `medium`.\nThe planner runs on `fable`.\n"


def base_spec():
    return {
        "schema": "routing-eval-5",
        "cases": [
            {"id": "A", "sources": ["skill.md"], "changed": True, "scenario": "Which reviewer?",
             "expected": {"model": ["opus"], "effort": ["medium"]}, "known_failure": "xhigh"},
            {"id": "B", "sources": ["skill.md"], "changed": False, "scenario": "Which planner?",
             "expected": {"model": ["fable"], "how": ["agent-definition-model-field"]}, "known_failure": ""},
        ],
        "anchors": {
            "A": [{"path": "skill.md", "text": "The reviewer runs at `medium`."}],
            "B": [{"path": "skill.md", "text": "The planner runs on `fable`."}],
        },
    }


def tool(*args, env=None):
    return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, env=env, timeout=120)


class CheckTests(unittest.TestCase):
    def test_real_cases_hold_against_the_repository(self):
        result = tool("check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(len(result.stdout.strip().splitlines()), 1, result.stdout)

    def run_check(self, spec, text=SKILL_TEXT):
        with tempfile.TemporaryDirectory(prefix="routing-eval-check-") as temporary:
            root = Path(temporary)
            (root / "skill.md").write_text(text)
            cases = root / "cases.json"
            cases.write_text(json.dumps(spec))
            return tool("check", "--cases", str(cases), "--root", str(root))

    def assert_single_problem(self, spec, needle, text=SKILL_TEXT):
        result = self.run_check(spec, text)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        lines = result.stdout.strip().splitlines()
        self.assertEqual(len(lines), 1, lines)
        self.assertIn(needle, lines[0])

    def test_unmodified_set_passes(self):
        result = self.run_check(base_spec())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_removed_passage_is_stale(self):
        self.assert_single_problem(base_spec(), "A: stale anchor in skill.md",
                                   SKILL_TEXT.replace("runs at `medium`", "runs at `high`"))

    def test_anchor_path_outside_sources(self):
        spec = base_spec()
        spec["anchors"]["A"][0]["path"] = "other.md"
        self.assert_single_problem(spec, "A: anchor path other.md is not among the case's sources")

    def test_case_without_anchors(self):
        spec = base_spec()
        del spec["anchors"]["A"]
        self.assert_single_problem(spec, "A: no anchors")
        spec = base_spec()
        spec["anchors"]["A"] = []
        self.assert_single_problem(spec, "A: no anchors")

    def test_anchor_for_unknown_case(self):
        spec = base_spec()
        spec["anchors"]["Z"] = [{"path": "skill.md", "text": "The planner runs on `fable`."}]
        self.assert_single_problem(spec, "Z: anchors name an unknown case id")

    def test_duplicate_case_id(self):
        spec = base_spec()
        spec["cases"].append(copy.deepcopy(spec["cases"][0]))
        self.assert_single_problem(spec, "A: duplicate case id")

    def test_case_id_that_could_leave_the_output_directory(self):
        # `run` names files after the case id, so an id is a file-name fragment, never a path.
        spec = base_spec()
        spec["cases"][0]["id"] = "../A"
        spec["anchors"]["../A"] = spec["anchors"].pop("A")
        result = self.run_check(spec)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("'../A': id may hold only letters, digits, dot, underscore and hyphen", result.stdout)

    def test_missing_source_file(self):
        spec = base_spec()
        spec["cases"][1]["sources"].append("missing.md")
        self.assert_single_problem(spec, "B: source missing.md does not exist")

    def test_expected_key_outside_schema(self):
        spec = base_spec()
        spec["cases"][0]["expected"]["reason"] = ["anything"]
        self.assert_single_problem(spec, "A: expected key reason is not one of model, effort, how")

    def test_effort_outside_enum(self):
        spec = base_spec()
        spec["cases"][0]["expected"]["effort"] = ["ultra"]
        self.assert_single_problem(spec, "A: expected effort value 'ultra' is not in the answer schema")

    def test_empty_expected_list(self):
        spec = base_spec()
        spec["cases"][0]["expected"]["model"] = []
        self.assert_single_problem(spec, "A: expected model must be a non-empty list of strings")

    def test_wrong_schema(self):
        spec = base_spec()
        spec["schema"] = "routing-eval-4"
        self.assert_single_problem(spec, "schema is 'routing-eval-4', expected 'routing-eval-5'")

    def test_unparseable_file(self):
        with tempfile.TemporaryDirectory(prefix="routing-eval-check-") as temporary:
            cases = Path(temporary) / "cases.json"
            cases.write_text("{not json")
            result = tool("check", "--cases", str(cases), "--root", temporary)
        self.assertEqual(result.returncode, 1)
        self.assertIn("does not parse", result.stdout)


class GradeTests(unittest.TestCase):
    case = {"expected": {"model": ["claude-opus-5-5", "opus"], "effort": ["medium"]}}

    def test_normalised_match_passes(self):
        fields = routing_eval.grade(self.case, {"model": " `Claude-Opus-5-5` ", "effort": "MEDIUM", "how": "x"})
        self.assertEqual(fields, {"model": True, "effort": True})

    def test_wrong_effort_fails(self):
        self.assertFalse(routing_eval.grade(self.case, {"model": "opus", "effort": "high"})["effort"])

    def test_missing_graded_field_fails(self):
        self.assertFalse(routing_eval.grade(self.case, {"model": "opus"})["effort"])

    def test_ungraded_field_ignored(self):
        fields = routing_eval.grade(self.case, {"model": "opus", "effort": "medium", "how": "not-applicable", "reason": "r"})
        self.assertEqual(set(fields), {"model", "effort"})
        self.assertTrue(all(fields.values()))


FAKE_CLAUDE = """\
import json, os, sys, uuid
if sys.argv[1:] == ["--version"]:
    print("fake-claude 1.0"); sys.exit(0)
prompt = sys.stdin.read()
open(os.path.join(os.environ["FAKE_LOG"], "claude-" + uuid.uuid4().hex), "w").write(prompt)
assert "--json-schema" in sys.argv and sys.argv[sys.argv.index("--tools") + 1] == ""
answers = json.loads(os.environ["FAKE_ANSWERS"])
if answers.get("claude") == "error":
    print("boom", file=sys.stderr); sys.exit(1)
marker, answer = next((m, a) for m, a in answers["cases"].items() if m in prompt)
if answers.get("fail_first"):
    try:
        os.open(os.path.join(os.environ["FAKE_LOG"], "first-claude-" + marker), os.O_CREAT | os.O_EXCL)
        print("boom once", file=sys.stderr); sys.exit(1)
    except FileExistsError:
        pass
print(json.dumps({"is_error": False, "structured_output": answer}))
"""

FAKE_CODEX = """\
import json, os, sys, uuid
if sys.argv[1:] == ["--version"]:
    print("fake-codex 1.0"); sys.exit(0)
argv = sys.argv[1:]
if argv[0] != "exec" or argv[-1] != "-" or "--json" not in argv \\
        or not any(argv[i:i + 2] == ["--disable", "shell_tool"] for i in range(len(argv))):
    print("fake codex: expected exec --json --disable shell_tool ... -", file=sys.stderr); sys.exit(3)
prompt = sys.stdin.read()
open(os.path.join(os.environ["FAKE_LOG"], "codex-" + uuid.uuid4().hex), "w").write(prompt)
answers = json.loads(os.environ["FAKE_ANSWERS"])
if answers.get("codex") == "error":
    print("boom", file=sys.stderr); sys.exit(1)
marker, answer = next((m, a) for m, a in answers["cases"].items() if m in prompt)
if answers.get("fail_first"):
    try:
        os.open(os.path.join(os.environ["FAKE_LOG"], "first-codex-" + marker), os.O_CREAT | os.O_EXCL)
        print("boom once", file=sys.stderr); sys.exit(1)
    except FileExistsError:
        pass
print(json.dumps({"type": "thread.started", "thread_id": "t"}))
for n, kind in enumerate(answers.get("codex_items", ["reasoning", "agent_message"])):
    for event in ("item.started", "item.completed"):
        print(json.dumps({"type": event, "item": {"id": f"item_{n}", "type": kind}}))
out = sys.argv[sys.argv.index("-o") + 1]
ending = answers.get("codex_ending", "clean")
if ending == "hang":
    sys.stdout.flush()
    import time
    time.sleep(60)
print(json.dumps({"type": "turn.completed", "usage": {}}))
if ending == "bad_json":
    open(out, "w").write("{not json")
elif ending == "bad_utf8":
    open(out, "wb").write(bytes([255, 254, 123]))
elif ending == "answer_is_a_directory":
    os.mkdir(out)
elif ending == "exit_1":
    open(out, "w").write(json.dumps(answer)); sys.exit(1)
elif ending != "no_answer":
    open(out, "w").write(json.dumps(answer))
"""

RIGHT = {"CASE-ONE": {"model": "opus", "effort": "medium", "how": "not-applicable", "reason": "r"},
         "CASE-TWO": {"model": "fable", "effort": "none", "how": "agent-definition-model-field", "reason": "r"}}


class RunTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="routing-eval-run-")
        base = Path(self.temporary.name)
        self.repo = base / "repo"
        self.repo.mkdir()
        self.bin = base / "bin"
        self.bin.mkdir()
        self.log = base / "log"
        self.log.mkdir()
        self.out = base / "out"
        for name, body in (("claude", FAKE_CLAUDE), ("codex", FAKE_CODEX)):
            fake = self.bin / name
            fake.write_text(f"#!{sys.executable}\n" + textwrap.dedent(body))
            fake.chmod(0o755)

        def git(*args):
            subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True)

        git("init", "-b", "main")
        git("config", "user.name", "Routing eval test")
        git("config", "user.email", "routing-eval@example.invalid")
        (self.repo / "skill.md").write_text("COMMITTED-TEXT: reviewer at medium, planner on fable.\n")
        git("add", "skill.md")
        git("-c", "core.hooksPath=/dev/null", "commit", "-m", "skill")
        (self.repo / "skill.md").write_text("WORKTREE-TEXT: reviewer at max.\n")
        self.cases = base / "cases.json"
        self.write_cases(changed_two=False)

    def tearDown(self):
        self.temporary.cleanup()

    def write_cases(self, changed_two):
        self.cases.write_text(json.dumps({
            "schema": "routing-eval-5",
            "cases": [
                {"id": "C1", "sources": ["skill.md"], "changed": False, "scenario": "CASE-ONE reviewer?",
                 "expected": {"model": ["opus"], "effort": ["medium"]}, "known_failure": ""},
                {"id": "C2", "sources": ["skill.md"], "changed": changed_two, "scenario": "CASE-TWO planner?",
                 "expected": {"model": ["fable"], "how": ["agent-definition-model-field"]}, "known_failure": ""},
            ],
            "anchors": {"C1": [{"path": "skill.md", "text": "reviewer at medium"}],
                        "C2": [{"path": "skill.md", "text": "planner on fable"}]},
        }))

    def run_tool(self, answers, *extra, out=None, env=None):
        env = dict(os.environ, PATH=f"{self.bin}{os.pathsep}{os.environ['PATH']}", FAKE_LOG=str(self.log),
                   FAKE_ANSWERS=json.dumps(answers), **(env or {}))
        return tool("run", "HEAD", "--out", str(out or self.out), "--cases", str(self.cases), "--root", str(self.repo),
                    "--claude-cmd", str(self.bin / "claude"), "--codex-cmd", str(self.bin / "codex"), *extra, env=env)

    def summary(self):
        return json.loads((self.out / "summary.json").read_text())

    def test_correct_answers_meet_the_threshold_from_committed_text(self):
        result = self.run_tool({"cases": RIGHT})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        summary = self.summary()
        self.assertTrue(summary["threshold_met"])
        self.assertEqual(summary["problems"], [])
        self.assertEqual(summary["totals"], {"pass": 12, "fail": 0, "error": 0, "samples": 12})
        self.assertEqual(summary["per_case"]["C1/codex"]["pass"], 3)
        self.assertEqual(len(list(self.out.glob("*.raw.txt"))), 12)
        self.assertTrue((self.out / "C2-claude-3.json").exists())
        self.assertEqual(summary["cases_schema"], "routing-eval-5")
        self.assertIn("skill.md", summary["sources_sha256"])
        prompts = [path.read_text() for path in self.log.iterdir()]
        self.assertEqual(len(prompts), 12)
        for prompt in prompts:
            self.assertIn("COMMITTED-TEXT", prompt)
            self.assertNotIn("WORKTREE-TEXT", prompt)

    def test_wrong_answer_names_the_case(self):
        answers = {"cases": dict(RIGHT, **{"CASE-TWO": dict(RIGHT["CASE-TWO"], model="opus")})}
        result = self.run_tool(answers)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        summary = self.summary()
        self.assertFalse(summary["threshold_met"])
        self.assertTrue(any("C2" in problem for problem in summary["problems"]))
        self.assertFalse(any("C1" in problem for problem in summary["problems"]))

    def test_fewer_than_three_samples_is_a_problem(self):
        result = self.run_tool({"cases": RIGHT}, "--samples", "2")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(any("samples" in problem for problem in self.summary()["problems"]))

    def test_baseline_changed_case_that_fails_everywhere_is_a_good_control(self):
        self.write_cases(changed_two=True)
        answers = {"cases": dict(RIGHT, **{"CASE-TWO": dict(RIGHT["CASE-TWO"], how="dispatch-parameter")})}
        result = self.run_tool(answers, "--baseline")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        summary = self.summary()
        self.assertTrue(summary["threshold_met"])
        self.assertEqual(summary["control_limits"], [])

    def test_baseline_changed_case_that_passes_fails_the_control(self):
        self.write_cases(changed_two=True)
        result = self.run_tool({"cases": RIGHT}, "--baseline")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        summary = self.summary()
        self.assertFalse(summary["threshold_met"])
        self.assertTrue(summary["control_limits"])
        self.assertTrue(all("C2" in limit for limit in summary["control_limits"]))

    def test_erroring_consumer_fails_with_errors_counted(self):
        result = self.run_tool({"cases": RIGHT, "codex": "error"})
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        summary = self.summary()
        self.assertEqual(summary["totals"]["error"], 6)
        self.assertEqual(summary["per_case"]["C1/codex"]["error"], 3)
        self.assertEqual(summary["per_case"]["C1/claude"]["pass"], 3)
        self.assertFalse(summary["threshold_met"])

    def test_codex_tool_use_is_an_error_not_a_pass(self):
        result = self.run_tool({"cases": RIGHT, "codex_items": ["reasoning", "command_execution", "agent_message"]})
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        summary = self.summary()
        self.assertFalse(summary["threshold_met"])
        self.assertEqual(summary["per_case"]["C1/codex"]["error"], 3)
        self.assertEqual(summary["per_case"]["C1/codex"]["pass"], 0)
        self.assertTrue(any(p.startswith("C1/codex") for p in summary["problems"]))
        self.assertTrue(any(p.startswith("C2/codex") for p in summary["problems"]))
        record = json.loads((self.out / "C1-codex-1.json").read_text())
        self.assertEqual(record["tool_use"], ["command_execution"])
        self.assertTrue(record["error"])
        self.assertFalse(record["pass"])
        self.assertIn("command_execution", (self.out / "C1-codex-1.raw.txt").read_text())
        self.assertEqual(json.loads((self.out / "C1-claude-1.json").read_text())["tool_use"], [])

    def calls(self, provider):
        return len(list(self.log.glob(f"{provider}-*")))

    def test_a_sample_is_asked_once_so_a_failed_call_is_an_error(self):
        # Each consumer fails its first call per case and would answer correctly if asked again.
        result = self.run_tool({"cases": RIGHT, "fail_first": True})
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        summary = self.summary()
        self.assertFalse(summary["threshold_met"])
        self.assertEqual(summary["totals"], {"pass": 8, "fail": 0, "error": 4, "samples": 12})
        for key in ("C1/claude", "C2/claude", "C1/codex", "C2/codex"):
            self.assertEqual(summary["per_case"][key]["error"], 1, key)
        self.assertEqual((self.calls("claude"), self.calls("codex")), (6, 6), "one call per sample, no second try")

    def test_codex_tool_use_then_any_bad_ending_is_an_error(self):
        # After a tool event, nothing the call does next can turn the sample into a pass.
        for ending in ("clean", "hang", "bad_json", "bad_utf8", "answer_is_a_directory", "exit_1", "no_answer"):
            with self.subTest(ending=ending):
                for old in self.log.glob("codex-*"):
                    old.unlink()
                shutil.rmtree(self.out, ignore_errors=True)  # an earlier ending left a directory as the answer
                result = self.run_tool({"cases": RIGHT, "codex_items": ["command_execution"], "codex_ending": ending},
                                       env={"ROUTING_EVAL_CALL_TIMEOUT": "2"})
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                summary = self.summary()
                self.assertFalse(summary["threshold_met"])
                self.assertEqual(summary["per_case"]["C1/codex"], {"changed": False, "pass": 0, "fail": 0, "error": 3, "samples": 3})
                self.assertEqual(summary["per_case"]["C2/codex"]["error"], 3)
                self.assertEqual(self.calls("codex"), 6, "one call per sample, no second try")
                record = json.loads((self.out / "C1-codex-1.json").read_text())
                self.assertTrue(record["error"])
                self.assertFalse(record["pass"])

    def test_codex_bad_ending_without_tool_use_is_an_error(self):
        for ending in ("bad_json", "bad_utf8", "answer_is_a_directory", "exit_1", "no_answer"):
            with self.subTest(ending=ending):
                result = self.run_tool({"cases": RIGHT, "codex_ending": ending})
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(self.summary()["per_case"]["C1/codex"]["error"], 3)
                self.assertEqual(self.summary()["per_case"]["C1/claude"]["pass"], 3)

    def test_codex_with_only_message_and_reasoning_items_passes(self):
        result = self.run_tool({"cases": RIGHT, "codex_items": ["reasoning", "agent_message", "reasoning"]})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.summary()["per_case"]["C2/codex"]["pass"], 3)

    def test_case_subset_is_a_partial_run(self):
        result = self.run_tool({"cases": RIGHT}, "--cases-only", "C1")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        summary = self.summary()
        self.assertFalse(summary["threshold_met"])
        self.assertEqual(summary["problems"], ["partial run: 1 of 2 cases on claude, codex; "
                                               "a threshold needs every case on claude and codex"])
        self.assertEqual(summary["coverage"], {"cases": 1, "of": 2, "providers": ["claude", "codex"], "full": False})
        self.assertEqual(summary["selected"], ["C1"])
        self.assertEqual(summary["per_case"]["C1/claude"]["pass"], 3)
        self.assertEqual(summary["per_case"]["C1/codex"]["pass"], 3)

    def test_single_provider_is_a_partial_run(self):
        result = self.run_tool({"cases": RIGHT}, "--providers", "claude")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        summary = self.summary()
        self.assertFalse(summary["threshold_met"])
        self.assertEqual(summary["problems"], ["partial run: 2 of 2 cases on claude; "
                                               "a threshold needs every case on claude and codex"])
        self.assertEqual(summary["coverage"], {"cases": 2, "of": 2, "providers": ["claude"], "full": False})
        self.assertEqual(summary["per_case"]["C2/claude"]["pass"], 3)

    def test_full_run_records_full_coverage(self):
        result = self.run_tool({"cases": RIGHT})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.summary()["coverage"], {"cases": 2, "of": 2, "providers": ["claude", "codex"], "full": True})

    def test_output_inside_the_repository_is_refused(self):
        result = self.run_tool({"cases": RIGHT}, out=self.repo / "results")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside the repository or under .scratch/", result.stderr)
        self.assertFalse((self.repo / "results").exists())
        self.assertEqual(list(self.log.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
