#!/usr/bin/env python3
"""Run the portable suite with isolated operator configuration and no provider calls."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="autoreview-test-home.") as test_home:
        env = {key: os.environ[key] for key in (
            "PATH", "LANG", "LC_ALL", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT",
            "TMP", "TEMP", "TMPDIR",
        ) if key in os.environ}
        env.update({
            "HOME": test_home, "USERPROFILE": test_home,
            "XDG_CONFIG_HOME": str(Path(test_home) / "config"),
            "XDG_CACHE_HOME": str(Path(test_home) / "cache"),
            "XDG_DATA_HOME": str(Path(test_home) / "data"),
            "XDG_STATE_HOME": str(Path(test_home) / "state"),
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONUTF8": "1",
        })
        for args in (
            ["scripts/autoreview_test.py"],
            ["-m", "unittest", "tests.test_autoreview_hardening",
             "tests.test_codex_inference_route", "tests.test_codex_sandbox"],
        ):
            result = subprocess.run([sys.executable, "-B", *args], cwd=root, env=env)
            if result.returncode:
                return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
