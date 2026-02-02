#!/usr/bin/env python3
"""
SRS Database Manager for teach-back-srs skill.

Manages a per-project SQLite database with SM-2 spaced repetition scheduling.
Stores cards generated from teach-back sessions, tracks reviews, and schedules
future reviews based on recall quality.

Usage:
    python srs_db.py init                          # Create DB in .ai-learn/srs.db
    python srs_db.py add-card --question Q --answer A [--context path] [--tags t1,t2] [--session-id N]
    python srs_db.py add-session --topic T --summary S --gaps N --cards N
    python srs_db.py due                           # List cards due for review
    python srs_db.py review --card-id ID --quality Q  # Record review (quality 0-5)
    python srs_db.py stats                         # Show learning statistics
    python srs_db.py cards [--topic T] [--session-id N]  # List cards with filters
    python srs_db.py sessions                      # List all teach-back sessions
    python srs_db.py export [--format md|csv]      # Export cards
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DB_DIR = ".ai-learn"
DB_NAME = "srs.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    summary TEXT,
    gaps_found INTEGER DEFAULT 0,
    cards_generated INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    context TEXT,
    tags TEXT,
    difficulty TEXT CHECK(difficulty IN ('easy', 'medium', 'hard')) DEFAULT 'medium',
    session_id INTEGER REFERENCES sessions(id),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    -- SM-2 scheduling fields
    ease_factor REAL NOT NULL DEFAULT 2.5,
    interval_days INTEGER NOT NULL DEFAULT 0,
    repetitions INTEGER NOT NULL DEFAULT 0,
    next_review TEXT NOT NULL DEFAULT (datetime('now')),
    deleted_at TEXT
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL REFERENCES cards(id),
    quality INTEGER NOT NULL CHECK(quality BETWEEN 0 AND 5),
    reviewed_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_cards_next_review ON cards(next_review)
    WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_cards_session ON cards(session_id);
CREATE INDEX IF NOT EXISTS idx_reviews_card ON reviews(card_id);
"""


def _now() -> str:
    """Current UTC time as ISO string (consistent with SQLite datetime('now'))."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def get_db_path() -> Path:
    """Resolve DB path relative to current working directory."""
    return Path.cwd() / DB_DIR / DB_NAME


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    """Connect to the SRS database."""
    path = db_path or get_db_path()
    if not path.exists():
        print(f"Database not found at {path}. Run 'init' first.", file=sys.stderr)
        sys.exit(1)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> Path:
    """Create database directory and schema."""
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Add .gitignore to keep learning data out of repo
    gitignore = db_path.parent / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n!.gitignore\n")

    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA)
    conn.close()
    print(f"Initialized SRS database at {db_path}")
    return db_path


def sm2_update(
    quality: int,
    repetitions: int,
    ease_factor: float,
    interval_days: int,
) -> tuple[int, float, int]:
    """
    SM-2 algorithm: compute next repetitions, ease_factor, interval.

    Quality scale:
        0 - Complete blackout
        1 - Wrong, but recognized answer when shown
        2 - Wrong, but answer felt familiar
        3 - Correct with serious difficulty
        4 - Correct with some hesitation
        5 - Perfect, instant recall

    Returns (new_repetitions, new_ease_factor, new_interval_days).
    """
    new_ef = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ef = max(1.3, new_ef)

    if quality >= 3:
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(interval_days * new_ef)
        new_reps = repetitions + 1
    else:
        new_reps = 0
        new_interval = 1

    return new_reps, new_ef, new_interval


def add_session(topic: str, summary: str = "", gaps: int = 0, cards: int = 0) -> int:
    """Record a teach-back session. Returns session ID."""
    conn = connect()
    cur = conn.execute(
        "INSERT INTO sessions (topic, summary, gaps_found, cards_generated) VALUES (?, ?, ?, ?)",
        (topic, summary, gaps, cards),
    )
    conn.commit()
    session_id = cur.lastrowid
    conn.close()
    print(f"Session #{session_id} recorded: {topic}")
    return session_id


def add_card(
    question: str,
    answer: str,
    context: str = "",
    tags: str = "",
    difficulty: str = "medium",
    session_id: int | None = None,
) -> int:
    """Add a flashcard. Returns card ID."""
    conn = connect()
    cur = conn.execute(
        """INSERT INTO cards (question, answer, context, tags, difficulty, session_id)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (question, answer, context, tags, difficulty, session_id),
    )
    conn.commit()
    card_id = cur.lastrowid
    conn.close()
    print(f"Card #{card_id} added: {question[:60]}...")
    return card_id


def get_due_cards(limit: int = 20) -> list[dict]:
    """Get cards due for review (next_review <= now)."""
    conn = connect()
    rows = conn.execute(
        """SELECT id, question, answer, context, tags, difficulty,
                  ease_factor, interval_days, repetitions, next_review
           FROM cards
           WHERE deleted_at IS NULL AND next_review <= datetime('now')
           ORDER BY next_review ASC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def record_review(card_id: int, quality: int) -> dict:
    """Record a review and update SM-2 scheduling. Returns updated card info."""
    conn = connect()
    card = conn.execute(
        "SELECT * FROM cards WHERE id = ? AND deleted_at IS NULL", (card_id,)
    ).fetchone()
    if not card:
        print(f"Card #{card_id} not found.", file=sys.stderr)
        conn.close()
        sys.exit(1)

    new_reps, new_ef, new_interval = sm2_update(
        quality, card["repetitions"], card["ease_factor"], card["interval_days"]
    )
    next_dt = datetime.now(timezone.utc) + timedelta(days=new_interval)
    next_review = next_dt.strftime("%Y-%m-%d %H:%M:%S")

    conn.execute(
        """UPDATE cards
           SET repetitions = ?, ease_factor = ?, interval_days = ?, next_review = ?
           WHERE id = ?""",
        (new_reps, new_ef, new_interval, next_review, card_id),
    )
    conn.execute(
        "INSERT INTO reviews (card_id, quality) VALUES (?, ?)", (card_id, quality)
    )
    conn.commit()
    conn.close()

    return {
        "card_id": card_id,
        "quality": quality,
        "new_interval_days": new_interval,
        "new_ease_factor": round(new_ef, 2),
        "next_review": next_review,
        "repetitions": new_reps,
    }


def get_stats() -> dict:
    """Get learning statistics."""
    conn = connect()

    total = conn.execute(
        "SELECT COUNT(*) FROM cards WHERE deleted_at IS NULL"
    ).fetchone()[0]
    due = conn.execute(
        "SELECT COUNT(*) FROM cards WHERE deleted_at IS NULL AND next_review <= datetime('now')"
    ).fetchone()[0]
    mastered = conn.execute(
        "SELECT COUNT(*) FROM cards WHERE deleted_at IS NULL AND repetitions >= 5 AND ease_factor >= 2.5"
    ).fetchone()[0]
    struggling = conn.execute(
        "SELECT COUNT(*) FROM cards WHERE deleted_at IS NULL AND ease_factor < 1.8"
    ).fetchone()[0]
    sessions_count = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    reviews_count = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]

    avg_ef = conn.execute(
        "SELECT AVG(ease_factor) FROM cards WHERE deleted_at IS NULL"
    ).fetchone()[0]

    today_reviews = conn.execute(
        "SELECT COUNT(*) FROM reviews WHERE date(reviewed_at) = date('now')"
    ).fetchone()[0]

    upcoming_7d = conn.execute(
        """SELECT COUNT(*) FROM cards
           WHERE deleted_at IS NULL
             AND next_review > datetime('now')
             AND next_review <= datetime('now', '+7 days')"""
    ).fetchone()[0]

    # Next scheduled review
    next_due = conn.execute(
        """SELECT next_review FROM cards
           WHERE deleted_at IS NULL AND next_review > datetime('now')
           ORDER BY next_review ASC LIMIT 1"""
    ).fetchone()

    conn.close()

    return {
        "total_cards": total,
        "due_now": due,
        "mastered": mastered,
        "struggling": struggling,
        "sessions": sessions_count,
        "total_reviews": reviews_count,
        "today_reviews": today_reviews,
        "upcoming_7d": upcoming_7d,
        "avg_ease_factor": round(avg_ef, 2) if avg_ef else None,
        "next_scheduled": next_due[0] if next_due else None,
    }


def list_cards(
    topic: str | None = None, session_id: int | None = None
) -> list[dict]:
    """List active cards, filtered by topic text or session ID."""
    conn = connect()
    if session_id is not None:
        rows = conn.execute(
            """SELECT id, question, answer, context, tags, difficulty,
                      ease_factor, interval_days, repetitions, next_review
               FROM cards
               WHERE deleted_at IS NULL AND session_id = ?
               ORDER BY created_at DESC""",
            (session_id,),
        ).fetchall()
    elif topic:
        rows = conn.execute(
            """SELECT id, question, answer, context, tags, difficulty,
                      ease_factor, interval_days, repetitions, next_review
               FROM cards
               WHERE deleted_at IS NULL
                 AND (tags LIKE ? OR context LIKE ? OR question LIKE ?)
               ORDER BY created_at DESC""",
            (f"%{topic}%", f"%{topic}%", f"%{topic}%"),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT id, question, answer, context, tags, difficulty,
                      ease_factor, interval_days, repetitions, next_review
               FROM cards WHERE deleted_at IS NULL
               ORDER BY created_at DESC"""
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_sessions() -> list[dict]:
    """List all teach-back sessions."""
    conn = connect()
    rows = conn.execute(
        "SELECT * FROM sessions ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def export_cards(fmt: str = "md") -> str:
    """Export all active cards in markdown or CSV format."""
    cards = list_cards()
    if fmt == "csv":
        lines = ["question,answer,context,tags,difficulty,ease_factor,interval_days,repetitions"]
        for c in cards:
            q = c["question"].replace('"', '""')
            a = c["answer"].replace('"', '""')
            ctx = (c["context"] or "").replace('"', '""')
            tags = (c["tags"] or "").replace('"', '""')
            lines.append(
                f'"{q}","{a}","{ctx}","{tags}",'
                f'"{c["difficulty"]}",{c["ease_factor"]},{c["interval_days"]},{c["repetitions"]}'
            )
        return "\n".join(lines)
    else:
        lines = ["# SRS Cards Export\n"]
        for c in cards:
            lines.append(f"## Card #{c['id']}")
            lines.append(f"**Q:** {c['question']}")
            lines.append(f"**A:** {c['answer']}")
            if c["context"]:
                lines.append(f"**Context:** `{c['context']}`")
            if c["tags"]:
                lines.append(f"**Tags:** {c['tags']}")
            lines.append(
                f"**Status:** EF={c['ease_factor']:.2f} | "
                f"interval={c['interval_days']}d | reps={c['repetitions']}"
            )
            lines.append("")
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="SRS Database Manager")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init", help="Initialize database")

    p_session = sub.add_parser("add-session", help="Record a teach-back session")
    p_session.add_argument("--topic", required=True)
    p_session.add_argument("--summary", default="")
    p_session.add_argument("--gaps", type=int, default=0)
    p_session.add_argument("--cards", type=int, default=0)

    p_card = sub.add_parser("add-card", help="Add a flashcard")
    p_card.add_argument("--question", required=True)
    p_card.add_argument("--answer", required=True)
    p_card.add_argument("--context", default="")
    p_card.add_argument("--tags", default="")
    p_card.add_argument("--difficulty", default="medium", choices=["easy", "medium", "hard"])
    p_card.add_argument("--session-id", type=int, default=None, dest="session_id")

    sub.add_parser("due", help="List due cards")

    p_review = sub.add_parser("review", help="Record a review")
    p_review.add_argument("--card-id", type=int, required=True, dest="card_id")
    p_review.add_argument("--quality", type=int, required=True, choices=range(6))

    sub.add_parser("stats", help="Show statistics")

    p_cards = sub.add_parser("cards", help="List cards")
    p_cards.add_argument("--topic", default=None)
    p_cards.add_argument("--session-id", type=int, default=None, dest="session_id")

    sub.add_parser("sessions", help="List sessions")

    p_export = sub.add_parser("export", help="Export cards")
    p_export.add_argument("--format", default="md", choices=["md", "csv"], dest="fmt")

    args = parser.parse_args()

    if args.command == "init":
        init_db()
    elif args.command == "add-session":
        add_session(args.topic, args.summary, args.gaps, args.cards)
    elif args.command == "add-card":
        add_card(
            args.question, args.answer, args.context,
            args.tags, args.difficulty, args.session_id,
        )
    elif args.command == "due":
        cards = get_due_cards()
        if not cards:
            print("No cards due for review.")
        else:
            print(f"{len(cards)} card(s) due:\n")
            for c in cards:
                print(f"  #{c['id']} [{c['difficulty']}] {c['question'][:80]}")
                print(f"    EF={c['ease_factor']:.2f} | interval={c['interval_days']}d | reps={c['repetitions']}")
    elif args.command == "review":
        result = record_review(args.card_id, args.quality)
        print(json.dumps(result, indent=2))
    elif args.command == "stats":
        stats = get_stats()
        print(json.dumps(stats, indent=2))
    elif args.command == "cards":
        cards = list_cards(args.topic, args.session_id)
        if not cards:
            print("No cards found.")
        else:
            for c in cards:
                print(f"  #{c['id']} [{c['difficulty']}] {c['question'][:80]}")
    elif args.command == "sessions":
        sessions = list_sessions()
        if not sessions:
            print("No sessions recorded.")
        else:
            for s in sessions:
                print(f"  #{s['id']} {s['topic']} ({s['gaps_found']} gaps, {s['cards_generated']} cards)")
    elif args.command == "export":
        print(export_cards(args.fmt))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
