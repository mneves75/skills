#!/usr/bin/env python3
"""Run the release-contract suite with an isolated environment and no network.

Python 3.11+ (the checker reads wrangler.toml with tomllib). Standard library only.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="release-contract-home.") as home:
        env = {key: os.environ[key] for key in (
            "PATH", "LANG", "LC_ALL", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "TMP", "TEMP", "TMPDIR",
        ) if key in os.environ}
        env.update({
            "HOME": home, "USERPROFILE": home,
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
            "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1",
        })
        return subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=root, env=env,
        ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
