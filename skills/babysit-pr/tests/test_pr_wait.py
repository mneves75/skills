"""End-to-end tests for scripts/pr-wait against a fake `gh` on PATH (no network).

Needs Python 3.11+. Run: python3 skills/babysit-pr/tests/test_pr_wait.py
Set PR_WAIT=<path> to run the same cases against another copy of the script.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPT = Path(os.environ.get("PR_WAIT") or Path(__file__).resolve().parents[1] / "scripts" / "pr-wait")
HEAD = "abc1234def5678"

FAKE_GH = r'''#!/usr/bin/env python3
import json, os, sys
scenario = json.loads(open(os.environ["FAKE_GH_SCENARIO"]).read())
args = sys.argv[1:]
if args[:2] == ["pr", "view"]:
    print(json.dumps({"number": int(args[2])}))
elif args[:2] == ["pr", "checks"]:
    print(json.dumps(scenario["checks"]))
    sys.exit(scenario.get("checks_exit", 0))
elif args[:2] == ["pr", "diff"]:
    pass
elif args[:2] == ["api", "graphql"]:
    query = next(a for a in args if a.startswith("query="))
    if "statusCheckRollup" in query:
        contexts = {"nodes": scenario.get("rollup", [])}
        commit = {"oid": scenario["pr"]["headRefOid"], "statusCheckRollup": {"contexts": contexts}}
        pr = {"commits": {"nodes": [{"commit": commit}]}}
        print(json.dumps({"data": {"repository": {"pullRequest": pr}}}))
    else:
        print(json.dumps({"data": {"viewer": {"login": "me"}, "repository": {"pullRequest": scenario["pr"]}}}))
elif args[:1] == ["api"] and ("/rules/branches/" in args[1] or "/protection/" in args[1]):
    print("gh: Not Found (HTTP 404)", file=sys.stderr)
    sys.exit(1)
elif args[:1] == ["api"] and "/compare/" in args[1]:
    print("0")
else:
    print(f"fake gh: unhandled {args}", file=sys.stderr)
    sys.exit(1)
'''


def pull_request() -> dict:
    return {
        "url": "https://github.com/o/r/pull/7", "state": "OPEN", "headRefOid": HEAD,
        "baseRefName": "main", "mergeStateStatus": "CLEAN", "author": {"login": "author"},
        "baseRef": {"target": {"oid": "base0001"}},
        "comments": {"nodes": []}, "reviews": {"nodes": []}, "reviewThreads": {"nodes": []},
    }


def check(name: str, bucket: str) -> dict:
    return {"name": name, "bucket": bucket, "link": f"https://example.test/{name}", "description": ""}


def check_run(name: str, conclusion: str, *messages: str) -> dict:
    notes = [{"annotationLevel": "FAILURE", "message": m} for m in messages]
    return {"__typename": "CheckRun", "name": name, "conclusion": conclusion, "annotations": {"nodes": notes}}


LOCKED = "The job was not started because your account is locked due to a billing issue."
SPENDING = ("The job was not started because recent account payments have failed or your spending "
            "limit needs to be increased. Please check the 'Billing &amp; plans' section in your settings")


class PrWaitTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        gh = bin_dir / "gh"
        gh.write_text(FAKE_GH)
        gh.chmod(0o755)
        self.scenario = root / "scenario.json"
        self.env = {
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "HOME": str(root / "home"),
            "FAKE_GH_SCENARIO": str(self.scenario),
        }

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, checks: list[dict], rollup: list[dict] | None = None, checks_exit: int = 0) -> None:
        self.scenario.write_text(json.dumps(
            {"pr": pull_request(), "checks": checks, "rollup": rollup or [], "checks_exit": checks_exit}))

    def run_wait(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args], env=self.env, capture_output=True, text=True, timeout=60)

    def test_green_exits_zero(self) -> None:
        self.write([check("build", "pass")])
        proc = self.run_wait("7", "--repo", "o/r", "--until", "green", "--interval", "5")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn(f"green on {HEAD[:7]}", proc.stdout)

    def test_code_failure_exits_one(self) -> None:
        self.write([check("build", "fail"), check("lint", "pass")], [check_run("build", "FAILURE", "Process completed with exit code 1.")], 1)
        proc = self.run_wait("7", "--repo", "o/r", "--until", "green", "--interval", "5")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("check failed: build", proc.stdout)

    def test_billing_block_is_not_a_code_failure(self) -> None:
        for message in (LOCKED, SPENDING):
            with self.subTest(message=message[:60]):
                self.write([check("build", "fail"), check("lint", "pass")], [check_run("build", "FAILURE", message)], 1)
                proc = self.run_wait("7", "--repo", "o/r", "--until", "green", "--interval", "5")
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertIn(f"green on {HEAD[:7]}", proc.stdout)
                self.assertIn("billing-blocked (prove locally): build", proc.stdout)
                for state in Path(self.env["HOME"]).glob(".local/state/pr-wait/*.json"):
                    state.unlink()

    def test_other_unstarted_job_still_fails(self) -> None:
        message = "The job was not started because the runner group is disabled."
        self.write([check("build", "fail")], [check_run("build", "FAILURE", message)], 1)
        proc = self.run_wait("7", "--repo", "o/r", "--until", "green", "--interval", "5")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("check failed: build", proc.stdout)

    def test_second_watcher_exits_two(self) -> None:
        self.write([check("build", "pending")], checks_exit=8)
        first = subprocess.Popen(
            [sys.executable, str(SCRIPT), "7", "--repo", "o/r", "--interval", "5"],
            env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            lock = Path(self.env["HOME"]) / ".local/state/pr-wait/o__r__7.lock"
            deadline = time.monotonic() + 20
            while not (lock.exists() and lock.read_text().strip()) and time.monotonic() < deadline:
                time.sleep(0.1)
            self.assertTrue(lock.exists(), "first watcher never took the lock")
            proc = self.run_wait("7", "--repo", "o/r")
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
            self.assertIn("already watches", proc.stdout)
        finally:
            first.terminate()
            first.communicate(timeout=10)

    def test_missing_pr_number_exits_two(self) -> None:
        self.write([])
        proc = self.run_wait("")
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("missing PR number", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
