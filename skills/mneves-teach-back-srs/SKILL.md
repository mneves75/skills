---
name: mneves-teach-back-srs
description: Run codebase teach-back with Socratic questions and spaced repetition. Use when users teach, want a quiz, or review cards.
license: Apache-2.0
---

# Teach-Back SRS

Spaced-repetition learning engine that turns "explain what you know" sessions into durable knowledge. The user explains their understanding of the codebase; the agent cross-references actual code, probes gaps with follow-up questions, and generates flashcards from misconceptions and blind spots. Cards are stored per-project in SQLite with SM-2 scheduling.

## Workflow Decision Tree

Determine which mode to enter based on user intent:

- **"Let me explain..." / "I think X works by..."** → Teach-Back Session (Mode 1, below)
- **"Quiz me" / "Review cards" / "What's due?"** → Review Session (Mode 2)
- **"Show my stats" / "How am I doing?"** → Stats Dashboard (Mode 3)
- **"Export cards"** → Export (Mode 4)

Modes 2-4 are documented in `references/modes.md`. Read it when one of them is the active mode.

## Mode 1: Teach-Back Session

This is the core loop. The user teaches; the agent listens, verifies, and fills gaps.

### Step 1: Initialize Database

All commands run `scripts/srs_db.py` from this skill's own directory (the folder this
SKILL.md was loaded from); the working directory is the user's project. Before the first
session in any project, create the database:

```bash
python3 scripts/srs_db.py init
```

This creates `.ai-learn/srs.db` in the current project directory (auto-gitignored).

### Step 2: Set the Topic

Ask the user what area of the codebase they want to explain. Scope it to a meaningful unit: a module or subsystem ("the auth pipeline"), a data flow ("how a request goes from input to execution"), or an architectural decision ("why we use X pattern here").

### Step 3: Listen to the Explanation

Let the user explain without interrupting. Take mental notes on **correct understanding** (what they got right), **misconceptions** (incorrect mental models), **gaps** (things they didn't mention that matter), and **vague areas** (hand-waving or hedging language such as "I think maybe...").

### Step 4: Cross-Reference the Codebase

While the user explains, read the actual code to verify claims. Use Glob, Grep, and Read to check:

- Do the files/functions they mention actually exist?
- Does the data flow match what they described?
- Are there important modules they completely missed?
- Are there edge cases or error paths they glossed over?

### Step 5: Socratic Follow-Ups

Ask 3-5 targeted questions that probe the weakest areas, in this priority order:

1. **Misconception correction**: "You mentioned X does Y, but looking at `file.rs:42`, it actually does Z. Why do you think that distinction matters?"
2. **Gap probing**: "You covered A and B well, but didn't mention C. What happens when [scenario involving C]?"
3. **Depth testing**: "You said the system uses pattern X. Can you explain why that was chosen over pattern Y?"
4. **Edge case exploration**: "What happens if [boundary condition]? Walk me through the code path."

Important: reference specific files and line numbers when correcting. Vague corrections do not create durable memories.

### Step 6: Generate Cards

Generate flashcards from every gap and misconception discovered, then store each one with
`scripts/srs_db.py add-card`. Read `references/card-quality.md` for the question, answer,
difficulty, and tagging rules plus the full command invocation.

### Step 7: Record the Session

```bash
python3 scripts/srs_db.py add-session \
  --topic "Safety pipeline architecture" \
  --summary "User understood pattern detection but missed intent gate ordering rationale" \
  --gaps 3 \
  --cards 5
```

### Step 8: Session Summary

Present a concise summary: what they got right (reinforce confidence), what gaps were found (with file references), how many cards were generated, and when the first review will be due.

## Cross-Session Continuity

The agent's conversation context resets between sessions; the SQLite database is the persistent memory. At the start of any new conversation where the user triggers this skill:

1. Check if `.ai-learn/srs.db` exists. If it does, run `stats` and `due` to understand current state
2. Report: total cards, due count, last session topic
3. If cards are due, suggest a review before starting a new teach-back

Continuity survives even though the agent has no memory of previous conversations.

## Database Location

- Path: `<project-root>/.ai-learn/srs.db`
- Auto-gitignored on init
- WAL mode for concurrent safety
- Soft deletes on cards (`deleted_at` field)

## Resources

### scripts/

- `srs_db.py`: SQLite database manager with SM-2 algorithm. Handles: init, add-card, add-session, due, review, stats, cards, sessions, export. Python 3.10+ stdlib only, no external dependencies.

### references/

- `modes.md`: Mode 2 (review session, SM-2 rating scale), Mode 3 (stats dashboard), Mode 4 (export). Load when the user asks to be quizzed, wants stats, or wants cards exported.
- `card-quality.md`: Question, answer, difficulty, and tagging rules for generated cards. Load before Step 6.
- `sm2-algorithm.md`: Detailed SM-2 formula reference, ease factor interpretation, interval progression examples. Load when explaining scheduling decisions to the user.
