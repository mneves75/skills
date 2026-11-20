#!/usr/bin/env python3
"""Tests for tools/scripts/catalog-eval.py against fake claude/codex CLIs (no network/quota)."""
from __future__ import annotations

import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parent / "catalog-eval.py"


def make_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def make_repo(root: Path) -> Path:
    for name, desc in [
        ("alpha-sec", "Security deploy gate and vulnerability fixes."),
        ("beta-audit", "Strictly read-only deep source audit."),
    ]:
        d = root / "skills" / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {desc}\n---\n# {name}\n", encoding="utf-8")
    cases_path = root / "cases.json"
    cases_path.write_text(
        json.dumps(
            {
                "schema": "catalog-eval-1",
                "cases": [
                    {
                        "id": "c1",
                        "cluster": "sec",
                        "prompt": "Run the deploy gate.",
                        "expected": ["alpha-sec"],
                        "forbidden": ["beta-audit"],
                    },
                    {
                        "id": "c2",
                        "cluster": "neg",
                        "prompt": "Fix a typo.",
                        "expected": ["none"],
                        "forbidden": ["alpha-sec"],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return cases_path


class CatalogEvalTest(unittest.TestCase):
    def test_check_valid_and_invalid_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = make_repo(root)
            p = subprocess.run(
                [sys.executable, str(SCRIPT), "check", "--root", str(root), "--cases", str(cases)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            bad = root / "bad.json"
            bad.write_text(
                json.dumps(
                    {
                        "schema": "catalog-eval-1",
                        "cases": [
                            {
                                "id": "b1",
                                "cluster": "sec",
                                "prompt": "x",
                                "expected": ["nonexistent-skill"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            p2 = subprocess.run(
                [sys.executable, str(SCRIPT), "check", "--root", str(root), "--cases", str(bad)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(p2.returncode, 1)
            self.assertIn("nonexistent-skill", p2.stdout)

    def test_run_with_fake_providers_and_confusion_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            out = Path(tmp) / "out"
            cases = make_repo(root)

            fake_claude = Path(tmp) / "fake-claude"
            make_executable(
                fake_claude,
                "#!/usr/bin/env python3\n"
                "import json, sys\n"
                "prompt = sys.stdin.read()\n"
                "req = prompt.split('User request:', 1)[-1]\n"
                "sel = 'alpha-sec' if 'deploy gate' in req else 'none'\n"
                "print(json.dumps({'is_error': False, 'structured_output': {'selected': sel, 'reason': 'ok'}}))\n",
            )

            fake_codex = Path(tmp) / "fake-codex"
            make_executable(
                fake_codex,
                "#!/usr/bin/env python3\n"
                "import json, sys\n"
                "prompt = sys.stdin.read()\n"
                "req = prompt.split('User request:', 1)[-1]\n"
                "out_path = sys.argv[sys.argv.index('-o') + 1]\n"
                "# Deliberately confuse c1 -> beta-audit to test forbidden/confusion matrix\n"
                "sel = 'beta-audit' if 'deploy gate' in req else 'none'\n"
                "open(out_path, 'w').write(json.dumps({'selected': sel, 'reason': 'fake'}))\n"
                "print(json.dumps({'item': {'type': 'agent_message'}}))\n",
            )

            p = subprocess.run(
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
                    "--samples",
                    "1",
                    "--claude-cmd",
                    str(fake_claude),
                    "--codex-cmd",
                    str(fake_codex),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["by_provider"]["claude"]["pass"], 2)
            self.assertEqual(summary["by_provider"]["codex"]["pass"], 1)
            self.assertEqual(summary["by_provider"]["codex"]["forbidden"], 1)
            self.assertEqual(summary["confusion_matrix"]["alpha-sec"]["beta-audit"], 1)
            self.assertEqual(len(summary["misses"]), 1)


if __name__ == "__main__":
    unittest.main()
