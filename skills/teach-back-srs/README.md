# Teach-Back SRS Skill

**Learn any codebase deeply through spaced-repetition teach-back sessions.**

You explain what you know. Claude cross-references the actual code, finds gaps in your mental model, asks Socratic follow-ups, and generates flashcards. Cards are scheduled using the SM-2 algorithm (same as Anki) in a per-project SQLite database.

**Works with**: Claude Code, Cursor, VS Code, Codex, Windsurf, Aider, and any tool supporting the Agent Skills specification.

## How It Works

```
You explain → Claude verifies against code → Socratic follow-ups → Cards from gaps → SM-2 scheduling
```

1. **Teach-back session** — You explain a module, data flow, or architectural decision
2. **Gap analysis** — Claude reads the actual code and identifies misconceptions, blind spots, and vague areas
3. **Socratic probing** — 3-5 targeted follow-up questions with specific file:line references
4. **Card generation** — Flashcards created from every gap found, stored in SQLite
5. **Spaced review** — SM-2 algorithm schedules reviews at optimal intervals for retention

## Quick Start

```bash
# In any project directory, tell Claude:
"Let me explain how the auth system works"

# Claude will:
# 1. Initialize .ai-learn/srs.db (auto-gitignored)
# 2. Listen to your explanation
# 3. Cross-reference the actual code
# 4. Ask follow-up questions
# 5. Generate flashcards from gaps
# 6. Schedule reviews

# Later, review due cards:
"Quiz me" or "What cards are due?"

# Check progress:
"Show my stats"
```

## Trigger Phrases

| Say this | Mode |
|----------|------|
| "Let me explain..." / "I think X works by..." | Teach-back session |
| "Quiz me" / "Review cards" / "What's due?" | Review session |
| "Show my stats" / "How am I doing?" | Stats dashboard |
| "Export cards" | Export (Markdown or Anki CSV) |

## Database

- **Location**: `<project-root>/.ai-learn/srs.db`
- **Auto-gitignored** on first init
- **WAL mode** for concurrent safety
- **Soft deletes** — cards are never hard-deleted
- **No external dependencies** — Python 3.10+ stdlib only

## SM-2 Algorithm

The same spaced-repetition algorithm used by Anki:

- Quality ratings 0-5 (0 = blackout, 5 = instant recall)
- Ease factor starts at 2.5, adjusts per card based on performance
- Failed cards (quality < 3) reset to day 1
- Successful cards grow intervals exponentially: 1d → 6d → 16d → 45d → 130d...
- Cards with ease factor < 1.8 are flagged as "struggling"
- Cards with 5+ reps and ease factor >= 2.5 are "mastered"

## CLI Reference

The skill includes `scripts/srs_db.py` for direct database operations:

```bash
SCRIPT=~/.claude/skills/teach-back-srs/scripts/srs_db.py

python3 $SCRIPT init                              # Create database
python3 $SCRIPT add-card --question Q --answer A  # Add flashcard
python3 $SCRIPT add-session --topic T             # Record session
python3 $SCRIPT due                               # List due cards
python3 $SCRIPT review --card-id 1 --quality 4    # Record review
python3 $SCRIPT stats                             # Learning statistics
python3 $SCRIPT cards --topic "auth"              # Filter cards
python3 $SCRIPT cards --session-id 3              # Cards from session
python3 $SCRIPT sessions                          # List sessions
python3 $SCRIPT export --format csv               # Anki-compatible export
```

## Card Quality

Cards follow these principles:

- **One concept per card** — never bundle multiple ideas
- **Why > What** — "Why does X use pattern Y?" over "What pattern does X use?"
- **Context anchored** — tied to specific files, functions, or architectural decisions
- **Interference-resistant** — distinct enough to not confuse with other cards

## File Structure

```
teach-back-srs/
├── SKILL.md                    # Session flow, card generation rules, review protocol
├── README.md                   # This file
├── scripts/
│   └── srs_db.py               # SQLite DB manager + SM-2 engine (stdlib only)
└── references/
    └── sm2-algorithm.md        # Algorithm deep-dive, interval progression examples
```

## Requirements

- Python 3.10+ (for `X | None` union syntax)
- No external packages — stdlib sqlite3, argparse, json only

## License

Apache-2.0
