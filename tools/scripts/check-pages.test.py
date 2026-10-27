#!/usr/bin/env python3
"""Exercise the Pages workflow's real guard with Git and a fake CI provider (Python 3.11+)."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = (ROOT / ".github/workflows/static.yml").read_text()
GUARD = textwrap.dedent(WORKFLOW.split("        run: |\n", 1)[1].split("\n      - ", 1)[0])


class PagesGuardTests(unittest.TestCase):
    def test_publication_requires_successful_ci_on_the_selected_main_commit(self):
        with tempfile.TemporaryDirectory(prefix="pages-guard-") as temporary:
            root = Path(temporary)

            def git(*args):
                return subprocess.check_output(["git", *args], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()

            git("init", "-b", "main")
            git("config", "user.name", "Pages test")
            git("config", "user.email", "pages@example.invalid")
            git("-c", "core.hooksPath=/dev/null", "commit", "--allow-empty", "-m", "Earlier release")
            earlier = git("rev-parse", "HEAD")
            git("-c", "core.hooksPath=/dev/null", "commit", "--allow-empty", "-m", "Main tip")
            tip = git("rev-parse", "HEAD")
            git("update-ref", "refs/remotes/origin/main", tip)
            git("checkout", "-b", "unmerged")
            git("-c", "core.hooksPath=/dev/null", "commit", "--allow-empty", "-m", "Unmerged candidate")
            unmerged = git("rev-parse", "HEAD")
            fake = root / "gh"
            fake.write_text(f"#!{sys.executable}\n" + textwrap.dedent('''\
                import os
                import sys
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
            cases = [
                ("automatic tip", "workflow_run", tip, "success", True),
                ("automatic stale commit", "workflow_run", earlier, "success", False),
                ("successful rollback", "workflow_dispatch", earlier, "success", True),
                ("unmerged dispatch", "workflow_dispatch", unmerged, "success", False),
                *[(f"dispatch CI {conclusion or 'missing'}", "workflow_dispatch", earlier, conclusion, False)
                  for conclusion in ["failure", "cancelled", "", "null", "api-error"]],
            ]
            for label, event, commit, conclusion, allowed in cases:
                with self.subTest(label):
                    git("checkout", "--detach", commit)
                    result = subprocess.run(
                        ["bash", "-e", "-c", GUARD], cwd=root, text=True, capture_output=True,
                        env={**os.environ, "PATH": f"{root}{os.pathsep}{os.environ['PATH']}",
                             "EVENT": event, "EXPECTED_COMMIT": commit, "CI_CONCLUSION": conclusion},
                        timeout=10,
                    )
                    self.assertEqual(result.returncode == 0, allowed, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
