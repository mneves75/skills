#!/usr/bin/env python3
"""Exercise the Pages workflow's real guard with Git and a fake CI provider (Python 3.11+)."""

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = (ROOT / ".github/workflows/static.yml").read_text()
GUARD = textwrap.dedent(WORKFLOW.split("        run: |\n", 1)[1].split("\n      - ", 1)[0])
REASON = "Owner skipped GitHub CI for this release"


class PagesGuardTests(unittest.TestCase):
    def test_publication_requires_successful_ci_or_an_approved_exact_commit_waiver(self):
        with tempfile.TemporaryDirectory(prefix="pages-guard-") as temporary:
            root = Path(temporary)

            def git(*args):
                return subprocess.check_output(["git", *args], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()

            def commit(message):
                git("-c", "core.hooksPath=/dev/null", "commit", "--allow-empty", "-m", message)
                return git("rev-parse", "HEAD")

            git("init", "-b", "main")
            git("config", "user.name", "Pages test")
            git("config", "user.email", "pages@example.invalid")
            earlier = commit("Earlier release")
            tip = commit("Main tip")
            git("checkout", "-b", "later")
            newer = commit("Later main tip")
            git("checkout", "-b", "unmerged", tip)
            unmerged = commit("Unmerged candidate")
            fake = root / "gh"
            fake.write_text(f"#!{sys.executable}\n" + textwrap.dedent('''\
                import os
                import sys
                open(os.environ["GH_CALLED"], "a").close()
                args = sys.argv[1:]
                assert args[:2] == ["run", "list"], args
                options = dict(zip(args[2::2], args[3::2]))
                assert options["--workflow"] == "ci.yml", options
                assert options["--commit"] == os.environ["EXPECTED_COMMIT"], options
                assert options["--branch"] == "main", options
                assert options["--event"] == "push", options
                assert options["--limit"] == "1", options
                assert options["--json"] == "conclusion", options
                assert options["--jq"] == ".[0].conclusion", options
                assert "--status" not in options, "Do not hide a newer failed or unfinished run"
                if os.environ["CI_CONCLUSION"] == "api-error":
                    sys.exit(1)
                print(os.environ["CI_CONCLUSION"])
            '''))
            fake.chmod(0o755)

            def case(label, event, head, allowed, conclusion="success", main=tip, sha="", reason="", approved=""):
                return label, event, head, allowed, conclusion, main, sha, reason, approved

            dispatch, automatic = "workflow_dispatch", "workflow_run"
            cases = [
                case("automatic tip", automatic, tip, True),
                case("automatic stale commit", automatic, earlier, False),
                case("successful rollback", dispatch, earlier, True),
                case("unmerged dispatch", dispatch, unmerged, False),
                *[case(f"dispatch CI {conclusion or 'missing'}", dispatch, earlier, False, conclusion)
                  for conclusion in ["failure", "cancelled", "", "null", "api-error"]],
                # The waiver: CI failed and is never asked, the run says it was waived.
                case("approved waiver", dispatch, tip, True, "failure", sha=tip, reason=REASON, approved=tip),
                # Every refusal below has successful CI, so falling through to normal dispatch would pass.
                case("approval alone does not waive", dispatch, tip, False, "failure", approved=tip),
                case("approval alone keeps the CI route", dispatch, tip, True, approved=tip),
                case("waiver without reason", dispatch, tip, False, sha=tip, approved=tip),
                case("waiver with blank reason", dispatch, tip, False, sha=tip, reason=" \t\n ", approved=tip),
                case("reason without waiver commit", dispatch, tip, False, reason=REASON, approved=tip),
                case("waiver without approval", dispatch, tip, False, sha=tip, reason=REASON),
                case("abbreviated commit", dispatch, tip, False, sha=tip[:12], reason=REASON, approved=tip[:12]),
                case("uppercase commit", dispatch, tip, False, sha=tip.upper(), reason=REASON, approved=tip.upper()),
                case("commit with trailing newline", dispatch, tip, False, sha=tip + "\n", reason=REASON,
                     approved=tip + "\n"),
                case("symbolic ref", dispatch, tip, False, sha="HEAD", reason=REASON, approved="HEAD"),
                case("approval with trailing space", dispatch, tip, False, sha=tip, reason=REASON, approved=tip + " "),
                case("foreign commit", dispatch, tip, False, sha="f" * 40, reason=REASON, approved="f" * 40),
                case("approval for another commit", dispatch, tip, False, sha=tip, reason=REASON, approved=earlier),
                case("checkout differs from waiver", dispatch, earlier, False, sha=tip, reason=REASON, approved=tip),
                case("stale waiver behind main", dispatch, earlier, False, sha=earlier, reason=REASON,
                     approved=earlier),
                case("unmerged waiver", dispatch, unmerged, False, sha=unmerged, reason=REASON, approved=unmerged),
                case("old approval for newer main", dispatch, newer, False, main=newer, sha=newer, reason=REASON,
                     approved=tip),
                case("old waiver after main moved", dispatch, tip, False, main=newer, sha=tip, reason=REASON,
                     approved=tip),
                case("automatic event with waiver", automatic, tip, False, sha=tip, reason=REASON, approved=tip),
                case("automatic event with reason only", automatic, tip, False, reason=REASON),
                case("automatic tip with a leftover approval", automatic, tip, True, approved=tip),
                case("automatic stale commit with a leftover approval", automatic, earlier, False, approved=earlier),
            ]
            for label, event, head, allowed, conclusion, main, sha, reason, approved in cases:
                with self.subTest(label):
                    git("update-ref", "refs/remotes/origin/main", main)
                    git("checkout", "--detach", head)
                    called, summary = root / "gh-called", root / "summary.md"
                    called.unlink(missing_ok=True)
                    summary.write_text("")
                    result = subprocess.run(
                        ["bash", "-e", "-c", GUARD], cwd=root, text=True, capture_output=True,
                        env={**os.environ, "PATH": f"{root}{os.pathsep}{os.environ['PATH']}",
                             "EVENT": event, "EXPECTED_COMMIT": head, "CI_CONCLUSION": conclusion,
                             "CI_WAIVER_SHA": sha, "CI_WAIVER_REASON": reason, "CI_WAIVER_APPROVED_SHA": approved,
                             "GH_CALLED": str(called), "GITHUB_STEP_SUMMARY": str(summary)},
                        timeout=10,
                    )
                    output = result.stdout + result.stderr
                    self.assertEqual(result.returncode == 0, allowed, output)
                    waived = summary.read_text()
                    if sha or reason:
                        self.assertFalse(called.exists(), "A waiver request must never query or fall back to CI")
                    if allowed and sha:
                        self.assertIn("CI WAIVED", waived)
                        self.assertIn(sha, waived)
                        self.assertIn(reason, waived)
                    else:
                        self.assertNotIn("WAIVED", waived + output)
                    if label in {"abbreviated commit", "uppercase commit", "commit with trailing newline", "symbolic ref"}:
                        self.assertIn("full lowercase 40-character commit id", output, "Name the malformed input")

    def test_waiver_inputs_reach_the_guard_only_as_environment_data(self):
        inputs = WORKFLOW.split("  workflow_dispatch:\n", 1)[1].split("\npermissions:", 1)[0]
        for name in ["ci_waiver_sha", "ci_waiver_reason"]:
            self.assertRegex(inputs, rf"\n      {name}:\n        description: .+\n        required: false\n"
                                     r"        type: string\n")
        self.assertNotIn("${{", GUARD, "Never interpolate expressions into the guard's shell code")
        step = WORKFLOW.split("      - name: Publish only", 1)[1].split("        run: |\n", 1)[0]
        bindings = {
            "CI_WAIVER_SHA": "inputs.ci_waiver_sha",
            "CI_WAIVER_REASON": "inputs.ci_waiver_reason",
            "CI_WAIVER_APPROVED_SHA": "vars.CI_WAIVER_APPROVED_SHA",
        }
        for variable, expression in bindings.items():
            self.assertIn(f"\n          {variable}: ${{{{ {expression} }}}}\n", step)
            self.assertEqual(WORKFLOW.count(expression), 1, f"{expression} is used only as guard data")
        self.assertEqual(re.findall(r"\$\{\{[^}]*\bvars\.", WORKFLOW), ["${{ vars."],
                         "The approval comes only from the deployment environment's variable")
        self.assertIn("    environment:\n      name: github-pages\n", WORKFLOW)


if __name__ == "__main__":
    unittest.main()
