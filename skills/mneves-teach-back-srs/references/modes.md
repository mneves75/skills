# Review, Stats, and Export Modes

Modes 2-4 of the teach-back SRS skill. Mode 1 (the teach-back session itself) stays in
SKILL.md. All commands run `scripts/srs_db.py` from the skill's own directory, with the
user's project as the working directory.

## Contents

- [Mode 2: Review Session](#mode-2-review-session) - present due cards, SM-2 rating scale, record results
- [Mode 3: Stats Dashboard](#mode-3-stats-dashboard) - read and present the stats JSON
- [Mode 4: Export](#mode-4-export) - Markdown and Anki-compatible CSV output

## Mode 2: Review Session

When the user wants to review due cards.

### Step 1: Check Due Cards

```bash
python3 scripts/srs_db.py due
```

If no cards are due, report the next scheduled review date and suggest a teach-back session
on a new topic instead.

### Step 2: Present Cards

For each due card:

1. Show the **question only**
2. Wait for the user's answer
3. Show the **correct answer**
4. Ask the user to self-rate their recall

### Step 3: Rate and Record

SM-2 quality scale (present to user as options):

| Rating | Meaning | When to use |
|--------|---------|-------------|
| 5 | Perfect, instant recall | Answered correctly without hesitation |
| 4 | Correct with some thought | Had to think but got it right |
| 3 | Correct with difficulty | Struggled but eventually recalled |
| 2 | Wrong but familiar | Recognized the answer when shown |
| 1 | Wrong, vaguely familiar | Only slight recognition |
| 0 | Complete blackout | No recall at all |

Record each review:

```bash
python3 scripts/srs_db.py review --card-id ID --quality Q
```

### Step 4: Review Summary

After all due cards are reviewed, show:

- Cards reviewed count
- Average quality score
- Cards that were reset (quality < 3)
- Next review date for earliest upcoming card

## Mode 3: Stats Dashboard

```bash
python3 scripts/srs_db.py stats
```

Present the JSON output in a readable format:

- **Total cards** / **Due now**, plus the **Mastered** and **Struggling** counts the `stats`
  command reports (it owns the thresholds behind those labels)
- **Sessions** completed
- **Reviews today** and **upcoming in 7 days**
- **Average ease factor** (health indicator: below 2.0 means material is too hard or reviews
  are too infrequent)

## Mode 4: Export

```bash
python3 scripts/srs_db.py export --format md
python3 scripts/srs_db.py export --format csv
```

CSV format is compatible with Anki import (question, answer columns).
