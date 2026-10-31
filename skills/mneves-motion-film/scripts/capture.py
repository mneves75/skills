#!/usr/bin/env python3
"""Capture the product's site as reference stills for the film: hero, full page, phone.

usage: capture.py <url> <out-dir> [--chrome PATH] [--full-height 8000]

Runs headless Chrome three times with a throwaway profile, at device scale 2:
  site-hero@2x.png    1440x900 viewport (the first screen a visitor sees)
  site-full@2x.png    1440 wide, --full-height tall (headless Chrome's
                      --screenshot captures the window, so the window is made
                      tall enough to hold the page; lower it for short pages)
  site-mobile@2x.png  390x844 viewport
These are references for brand, hierarchy and copy, never footage: the film
rebuilds every screen as real, animated UI. Exits 1 when Chrome fails or a
screenshot is missing.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome",
    "chromium",
)
SHOTS = (("site-hero@2x.png", 1440, 900), ("site-full@2x.png", 1440, None), ("site-mobile@2x.png", 390, 844))


def find_chrome(explicit: str | None) -> str:
    for candidate in ([explicit] if explicit else CHROME_CANDIDATES):
        found = shutil.which(candidate) or (candidate if Path(candidate).is_file() else None)
        if found:
            return found
    raise SystemExit("capture.py: no Chrome found; pass --chrome PATH")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("out_dir")
    parser.add_argument("--chrome")
    parser.add_argument("--full-height", type=int, default=8000)
    options = parser.parse_args()
    chrome = find_chrome(options.chrome)
    out = Path(options.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    failures = 0
    with tempfile.TemporaryDirectory(prefix="capture-profile-") as profile:
        for name, width, height in SHOTS:
            target = out / name
            target.unlink(missing_ok=True)
            args = [
                chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                "--no-default-browser-check", f"--user-data-dir={profile}", "--force-device-scale-factor=2",
                f"--window-size={width},{height or options.full_height}", f"--screenshot={target.resolve()}",
                "--virtual-time-budget=4000", options.url,
            ]
            result = subprocess.run(args, capture_output=True, text=True, timeout=120)
            # A tall window can trip Chrome's teardown watchdog after the file is written, so
            # success is Chrome's own "written" line plus a non-empty file, whatever the exit code.
            written = "bytes written to file" in result.stderr and target.is_file() and target.stat().st_size > 0
            if not written:
                print(f"FAIL {name}: exit {result.returncode}: {result.stderr.strip()[-400:]!r}", file=sys.stderr)
                failures += 1
            else:
                note = f", Chrome exited {result.returncode} after writing it" if result.returncode else ""
                print(f"capture.py: {target} ({target.stat().st_size} bytes{note})")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
