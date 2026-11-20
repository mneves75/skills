#!/usr/bin/env python3
"""Tests for tools/scripts/install-skills.py (dry-run, babysit overlap exclusion, local-edit guard)."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve().parent / "install-skills.py"


class InstallSkillsTest(unittest.TestCase):
    def test_list_profiles_on_real_repo(self) -> None:
        p = subprocess.run(
            [sys.executable, str(SCRIPT), "--list-profiles", "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        rows = {r["profile"]: r for r in json.loads(p.stdout)}
        self.assertEqual(rows["root-all"]["skills"], 25)
        self.assertEqual(rows["full-deduped"]["skills"], 66)
        self.assertEqual(rows["full-deduped"]["skipped"], 1)

    def test_pstack_compatible_skips_babysit_only_when_babysit_pr_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            target.mkdir()

            # Without babysit-pr in target, pstack/babysit is included (42 skills)
            p1 = subprocess.run(
                [sys.executable, str(SCRIPT), "--profile", "pstack-compatible", "--target", str(target), "--json"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(p1.returncode, 0, p1.stdout + p1.stderr)
            d1 = json.loads(p1.stdout)
            self.assertEqual(d1["selected_count"], 42)
            self.assertTrue(any(s["name"] == "babysit" for s in d1["selected"]))

            # Once babysit-pr exists in target, pstack/babysit is automatically skipped (41 skills)
            (target / "babysit-pr").mkdir()
            p2 = subprocess.run(
                [sys.executable, str(SCRIPT), "--profile", "pstack-compatible", "--target", str(target), "--json"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(p2.returncode, 0, p2.stdout + p2.stderr)
            d2 = json.loads(p2.stdout)
            self.assertEqual(d2["selected_count"], 41)
            self.assertFalse(any(s["name"] == "babysit" for s in d2["selected"]))
            self.assertTrue(any(s["name"] == "babysit" for s in d2["skipped"]))

    def test_dry_run_and_apply_and_local_dir_protection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out"
            # Dry-run creates nothing
            p_dry = subprocess.run(
                [sys.executable, str(SCRIPT), "--profile", "pr-ops", "--target", str(target)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(p_dry.returncode, 0, p_dry.stdout + p_dry.stderr)
            self.assertFalse(target.exists())

            # Apply creates symlinks cleanly
            p_apply = subprocess.run(
                [sys.executable, str(SCRIPT), "--profile", "pr-ops", "--target", str(target), "--apply"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(p_apply.returncode, 0, p_apply.stdout + p_apply.stderr)
            self.assertTrue((target / "babysit-pr").is_symlink())
            self.assertEqual((target / "babysit-pr").resolve(), (ROOT / "skills/babysit-pr").resolve())

            # Existing real directory is never overwritten
            (target / "babysit-pr").unlink()
            (target / "babysit-pr").mkdir()
            (target / "babysit-pr" / "local.txt").write_text("keep me", encoding="utf-8")
            p_conflict = subprocess.run(
                [sys.executable, str(SCRIPT), "--profile", "pr-ops", "--target", str(target), "--apply"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(p_conflict.returncode, 1)
            self.assertIn("CONFLICT", p_conflict.stdout)
            self.assertEqual((target / "babysit-pr" / "local.txt").read_text(encoding="utf-8"), "keep me")


if __name__ == "__main__":
    unittest.main()
