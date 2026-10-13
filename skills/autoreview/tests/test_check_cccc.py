"""The real-binary gate must reject wrong evidence even under optimized Python."""
from pathlib import Path
import importlib.util
import io
import json
import subprocess
import sys
import unittest
from unittest import mock


class ControlTests(unittest.TestCase):
    def test_threshold_requires_complete_known_report(self):
        script = Path(__file__).resolve().parents[1] / "scripts/check-cccc.py"
        spec = importlib.util.spec_from_file_location("check_cccc", script)
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        pin = json.loads(script.with_name("cccc-release.json").read_text())
        valid = {"summary": {"file_count": 1, "function_count": 1, "parse_error_count": 0},
                 "files": [{"functions": [{"cognitive": 1, "cyclomatic": 2}]}]}
        for invalid in (None, {**valid, "summary": {"file_count": 0,
                         "function_count": 0, "parse_error_count": 0}}):
            replies = [subprocess.CompletedProcess([], 0, f"cccc {pin['version']}", ""),
                       subprocess.CompletedProcess([], 0, json.dumps(valid), ""),
                       subprocess.CompletedProcess([], 1, "" if invalid is None else
                                                   json.dumps(invalid), "")]
            with self.subTest(invalid=invalid), \
                 mock.patch.object(sys, "argv", [str(script), str(script)]), \
                 mock.patch.object(helper.subprocess, "run", side_effect=replies), \
                 mock.patch.object(sys, "stdout", new_callable=io.StringIO) as output:
                with self.assertRaises(RuntimeError):
                    helper.main()
                self.assertNotIn("PASS: existing threshold", output.getvalue())

    def test_optimized_python_still_rejects_wrong_version(self):
        script = Path(__file__).resolve().parents[1] / "scripts/check-cccc.py"
        probe = r'''
import importlib.util, json, subprocess, sys
from unittest import mock
spec = importlib.util.spec_from_file_location("control", sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
sys.argv = [sys.argv[1], sys.argv[1]]
document = {"summary": {"file_count": 0, "function_count": 0, "parse_error_count": 1},
            "files": [{"functions": [{"cognitive": 999, "cyclomatic": 999}]}]}
def fake_run(args, **kwargs):
    output = "wrong version" if "--version" in args else json.dumps(document)
    if "simple.ts" in args[-1] and "--no-config" not in args:
        output = "choose"
    return subprocess.CompletedProcess(args, 99, output, "")
with mock.patch.object(module.subprocess, "run", side_effect=fake_run):
    module.main()
'''
        result = subprocess.run([sys.executable, "-OO", "-B", "-c", probe, str(script)],
                                text=True, capture_output=True, timeout=30)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("PASS:", result.stdout)


if __name__ == "__main__":
    unittest.main()
