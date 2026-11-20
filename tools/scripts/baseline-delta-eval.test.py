#!/usr/bin/env python3
"""Tests for tools/scripts/baseline-delta-eval.py against fake claude/codex CLIs (no quota)."""
from __future__ import annotations

import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parent / "baseline-delta-eval.py"


def make_exec(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class BaselineDeltaEvalTest(unittest.TestCase):
    def test_check_and_run_unblinding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            out = Path(tmp) / "out"
            (root / "skills" / "demo-skill").mkdir(parents=True)
            (root / "skills" / "demo-skill" / "SKILL.md").write_text(
                "---\nname: demo-skill\ndescription: Demo skill.\n---\n# Demo\nSPECIAL_MARKER\n",
                encoding="utf-8",
            )
            cases = root / "cases.json"
            cases.write_text(
                json.dumps(
                    {
                        "schema": "baseline-delta-1",
                        "cases": [
                            {
                                "id": "d1",
                                "skill": "demo-skill",
                                "prompt": "Do the demo task.",
                                "rubric": "Check clarity.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            p_chk = subprocess.run(
                [sys.executable, str(SCRIPT), "check", "--root", str(root), "--cases", str(cases)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(p_chk.returncode, 0, p_chk.stdout + p_chk.stderr)

            fake_claude = Path(tmp) / "fake-claude"
            make_exec(
                fake_claude,
                "#!/usr/bin/env python3\n"
                "import json, sys\n"
                "p = sys.stdin.read()\n"
                "res = 'WITH_SKILL_OUT' if 'SPECIAL_MARKER' in p else 'NO_SKILL_OUT'\n"
                "print(json.dumps({'is_error': False, 'result': res}))\n",
            )

            fake_codex = Path(tmp) / "fake-codex"
            make_exec(
                fake_codex,
                "#!/usr/bin/env python3\n"
                "import json, sys\n"
                "p = sys.stdin.read()\n"
                "out_path = sys.argv[sys.argv.index('-o') + 1]\n"
                "a_block = p.split('<output_a>', 1)[1].split('</output_a>', 1)[0]\n"
                "if 'WITH_SKILL_OUT' in a_block:\n"
                "    ans = {'score_a': 5, 'score_b': 3, 'winner': 'A', 'margin': 'decisive', 'reason': 'A stronger'}\n"
                "else:\n"
                "    ans = {'score_a': 3, 'score_b': 5, 'winner': 'B', 'margin': 'decisive', 'reason': 'B stronger'}\n"
                "open(out_path, 'w').write(json.dumps(ans))\n"
                "print(json.dumps({'item': {'type': 'agent_message'}}))\n",
            )

            p_run = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "run",
                    "--root",
                    str(root),
                    "--cases",
                    str(cases),
                    "--out",
                    str(out),
                    "--claude-cmd",
                    str(fake_claude),
                    "--codex-cmd",
                    str(fake_codex),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(p_run.returncode, 0, p_run.stdout + p_run.stderr)
            summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
            r = summary["results"][0]
            self.assertEqual(r["winner"], "with_skill")
            self.assertEqual(r["score_with_skill"], 5)
            self.assertEqual(r["score_no_skill"], 3)
            self.assertEqual(r["delta"], 2)


if __name__ == "__main__":
    unittest.main()
