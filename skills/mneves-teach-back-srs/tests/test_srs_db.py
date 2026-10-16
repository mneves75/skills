#!/usr/bin/env python3
"""Tests for scripts/srs_db.py; Python 3.10+, standard library only.

Run: python3 skills/mneves-teach-back-srs/tests/test_srs_db.py
Each test works in its own temporary directory, so no real .ai-learn database is touched.
"""

import contextlib
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
            except BaseException as error:  # includes SystemExit from a missing card
                errors.append(error)

        threads = [threading.Thread(target=review) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=30)
        self.assertFalse(any(thread.is_alive() for thread in threads), "a review never finished")
        self.assertEqual(errors, [])
        self.assertEqual(self.state(self.card), expected)


if __name__ == "__main__":
    unittest.main()
