#!/usr/bin/env python3
"""Tests for scripts/srs_db.py; Python 3.10+, standard library only.

Run: python3 skills/mneves-teach-back-srs/tests/test_srs_db.py
Each test works in its own temporary directory, so no real .ai-learn database is touched.
"""

import contextlib
import subprocess
import sys
import importlib.util
import io
import os
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "srs_db.py"


def load_srs():
    spec = importlib.util.spec_from_file_location("srs_db", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ConcurrentReviews(unittest.TestCase):
    def setUp(self):
        self.srs = load_srs()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(tmp.name)  # srs_db.py keeps its database under the working directory
        with contextlib.redirect_stdout(io.StringIO()):
            self.srs.init_db()
            self.card = self.srs.add_card("Overlapping question?", "Answer.")
            self.control = self.srs.add_card("Sequential question?", "Answer.")

    def state(self, card_id):
        conn = sqlite3.connect(str(self.srs.get_db_path()))
        try:
            card = conn.execute(
                "SELECT repetitions, interval_days, ease_factor FROM cards WHERE id = ?", (card_id,)
            ).fetchone()
            reviews = conn.execute("SELECT COUNT(*) FROM reviews WHERE card_id = ?", (card_id,)).fetchone()[0]
        finally:
            conn.close()
        return card, reviews

    def test_two_overlapping_reviews_advance_like_two_in_a_row(self):
        self.srs.record_review(self.control, 4)
        self.srs.record_review(self.control, 4)
        expected = self.state(self.control)

        # Each review, once it has read the card, waits up to 1 s for the other to read it too. A
        # review that reads before it holds the write lock then computes from a state the other
        # review replaces; one that locks first makes the other wait, and the barrier times out.
        both_read = threading.Barrier(2, timeout=1)
        sm2_update = self.srs.sm2_update

        def paced(*args):
            with contextlib.suppress(threading.BrokenBarrierError):
                both_read.wait()
            return sm2_update(*args)

        self.srs.sm2_update = paced
        errors = []

        def review():
            try:
                self.srs.record_review(self.card, 4)
            except Exception as error:
                errors.append(error)

        threads = [threading.Thread(target=review) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=30)
        self.assertFalse(any(thread.is_alive() for thread in threads), "a review never finished")
        self.assertEqual(errors, [])
        self.assertEqual(self.state(self.card), expected)


class ErrorsAreExceptions(unittest.TestCase):
    """Library calls raise SrsError; only the CLI turns it into a message and exit status 1."""

    def setUp(self):
        self.srs = load_srs()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(tmp.name)
        self.tmp = tmp.name

    def test_missing_database_raises(self):
        with self.assertRaisesRegex(self.srs.SrsError, "Run 'init' first"):
            self.srs.connect()

    def test_missing_card_raises_and_keeps_the_database_usable(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.srs.init_db()
        with self.assertRaisesRegex(self.srs.SrsError, "Card #999 not found"):
            self.srs.record_review(999, 4)
        with contextlib.redirect_stdout(io.StringIO()):
            card = self.srs.add_card("Still writable?", "Yes.")
        self.assertEqual(self.srs.record_review(card, 4)["repetitions"], 1)

    def test_cli_reports_errors_with_exit_status_1(self):
        for argv, message in ((["stats"], "Run 'init' first"), (["review", "--card-id", "999", "--quality", "4"], "Card #999 not found")):
            if argv[0] == "review":
                subprocess.run([sys.executable, str(SCRIPT), "init"], cwd=self.tmp, check=True, capture_output=True)
            done = subprocess.run([sys.executable, str(SCRIPT), *argv], cwd=self.tmp, capture_output=True, text=True)
            self.assertEqual(done.returncode, 1, done.stderr)
            self.assertIn(message, done.stderr)
            self.assertNotIn("Traceback", done.stderr)


if __name__ == "__main__":
    unittest.main()
