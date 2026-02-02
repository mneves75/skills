---
name: teach-back-srs
description: "Spaced-repetition learning through teach-back sessions. This skill should be used when the user wants to explain their understanding of a project or codebase so Claude can identify knowledge gaps, ask Socratic follow-ups, and generate flashcards stored in a per-project SQLite database with SM-2 scheduling. Triggers on phrases like 'let me explain', 'teach back', 'quiz me', 'review cards', 'what do I know about', or 'test my understanding'."
---

# Teach-Back SRS

Spaced-repetition learning engine that turns "explain what you know" sessions into durable knowledge. The user explains their understanding of the codebase; Claude cross-references actual code, probes gaps with follow-up questions, and generates flashcards from misconceptions and blind spots. Cards are stored per-project in SQLite with SM-2 scheduling.

## Workflow Decision Tree

Determine which mode to enter based on user intent:

- **"Let me explain..." / "I think X works by..."** → Teach-Back Session
- **"Quiz me" / "Review cards" / "What's due?"** → Review Session
- **"Show my stats" / "How am I doing?"** → Stats Dashboard
- **"Export cards"** → Export

## Mode 1: Teach-Back Session

This is the core loop. The user teaches; Claude listens, verifies, and fills gaps.

### Step 1: Initialize Database

Before the first session in any project, ensure the database exists:

```bash
python3 ~/.claude/skills/teach-back-srs/scripts/srs_db.py init
```

This creates `.ai-learn/srs.db` in the current project directory (auto-gitignored).

### Step 2: Set the Topic

Ask the user what area of the codebase they want to explain. Scope it to a meaningful unit:
- A module or subsystem (e.g., "the auth pipeline")
- A data flow (e.g., "how a request goes from input to execution")
- An architectural decision (e.g., "why we use X pattern here")

### Step 3: Listen to the Explanation

Let the user explain without interrupting. Take mental notes on:
- **Correct understanding** — what they got right
- **Misconceptions** — incorrect mental models
- **Gaps** — things they didn't mention that matter
- **Vague areas** — hand-waving or hedging language ("I think maybe...")

### Step 4: Cross-Reference the Codebase

While the user explains, read the actual code to verify claims. Use Glob, Grep, and Read tools to check:
- Do the files/functions they mention actually exist?
- Does the data flow match what they described?
- Are there important modules they completely missed?
- Are there edge cases or error paths they glossed over?

### Step 5: Socratic Follow-Ups

Ask 3-5 targeted questions that probe the weakest areas. Follow-up question types, ordered by priority:

1. **Misconception correction** — "You mentioned X does Y, but looking at `file.rs:42`, it actually does Z. Why do you think that distinction matters?"
2. **Gap probing** — "You covered A and B well, but didn't mention C. What happens when [scenario involving C]?"
3. **Depth testing** — "You said the system uses pattern X. Can you explain why that was chosen over pattern Y?"
4. **Edge case exploration** — "What happens if [boundary condition]? Walk me through the code path."

Important: Reference specific files and line numbers when correcting. Vague corrections do not create durable memories.

### Step 6: Generate Cards

After the follow-up discussion, generate flashcards from every gap and misconception discovered. Card quality rules:

**Question format:**
- Ask about the *why* or *how*, not just *what*
- Reference specific code locations when relevant
- Frame around the misconception or gap, not the correct answer

**Answer format:**
- Concise but complete (2-4 sentences)
- Include the file/function reference
- Explain the "why" behind the correct answer

**Difficulty assignment:**
- `easy` — Simple fact the user almost had right
- `medium` — Conceptual gap requiring understanding
- `hard` — Deep misconception or architectural blind spot

**Tag with:** module name, concept category (e.g., "auth,security,middleware")

To store cards, run the script for each card:

```bash
python3 ~/.claude/skills/teach-back-srs/scripts/srs_db.py add-card \
  --question "Why does the safety pipeline check intent before sanitizing input?" \
  --answer "Intent gate (safety/intent.rs) runs first because it can reject catastrophic intents without any model call, saving latency and cost. Sanitization (ai/sanitize.rs) runs after because it only matters if the query will reach the model." \
  --context "safety/intent.rs, ai/sanitize.rs" \
  --tags "safety,pipeline,architecture" \
  --difficulty medium
```

### Step 7: Record the Session

```bash
python3 ~/.claude/skills/teach-back-srs/scripts/srs_db.py add-session \
  --topic "Safety pipeline architecture" \
  --summary "User understood pattern detection but missed intent gate ordering rationale" \
  --gaps 3 \
  --cards 5
```

### Step 8: Session Summary

Present a concise summary:
- What they got right (reinforce confidence)
- What gaps were found (with file references)
- How many cards were generated
- When the first review will be due

## Mode 2: Review Session

When the user wants to review due cards.

### Step 1: Check Due Cards

```bash
python3 ~/.claude/skills/teach-back-srs/scripts/srs_db.py due
```

If no cards are due, report the next scheduled review date and suggest a teach-back session on a new topic instead.

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
python3 ~/.claude/skills/teach-back-srs/scripts/srs_db.py review --card-id ID --quality Q
```

### Step 4: Review Summary

After all due cards are reviewed, show:
- Cards reviewed count
- Average quality score
- Cards that were reset (quality < 3)
- Next review date for earliest upcoming card

## Mode 3: Stats Dashboard

```bash
python3 ~/.claude/skills/teach-back-srs/scripts/srs_db.py stats
```

Present the JSON output in a readable format:
- **Total cards** / **Due now** / **Mastered** (5+ reps, EF >= 2.5) / **Struggling** (EF < 1.8)
- **Sessions** completed
- **Reviews today** and **upcoming in 7 days**
- **Average ease factor** (health indicator: below 2.0 means material is too hard or reviews are too infrequent)

## Mode 4: Export

```bash
python3 ~/.claude/skills/teach-back-srs/scripts/srs_db.py export --format md
python3 ~/.claude/skills/teach-back-srs/scripts/srs_db.py export --format csv
```

CSV format is compatible with Anki import (question, answer columns).

## Card Generation Guidelines

High-quality cards follow these principles:

1. **One concept per card** — Never bundle multiple ideas
2. **Cloze-friendly questions** — "What does X do when Y?" not "Describe X"
3. **Context anchored** — Always tie back to a specific file, function, or architectural decision
4. **Interference-resistant** — Avoid cards that could be confused with each other
5. **Why > What** — "Why does the system use SM-2 instead of Leitner?" over "What algorithm does the SRS use?"

## Cross-Session Continuity

Claude's conversation context resets between sessions. The SQLite database is the persistent memory. At the start of any new conversation where the user triggers this skill:

1. Check if `.ai-learn/srs.db` exists — if yes, run `stats` and `due` to understand current state
2. Report: total cards, due count, last session topic
3. If cards are due, suggest a review before starting a new teach-back

This ensures continuity even though Claude has no memory of previous conversations.

## Example Dialogue

**User:** "Let me explain how the safety system works in ai-shell"

**Claude:** *reads safety/ directory, cross-references*

**Claude:** "Go ahead — explain the safety pipeline from user input to command execution."

**User:** "So there's a pattern matcher that checks for dangerous commands like rm -rf, and a scoring system that rates commands 1-10. If the score is too high it blocks the command."

**Claude:** "You've got the pattern detection and scoring right. A few follow-ups:

1. You described two layers, but looking at `safety/intent.rs`, there's actually a third layer that runs *before* pattern detection. What do you think it does and why would it run first?

2. You mentioned the scorer blocks at high scores. Looking at `safety/scorer.rs:47`, what actually happens at score 7+ vs score 9+? They're handled differently.

3. The pattern matcher in `safety/patterns.rs` uses `RegexSet` instead of checking patterns one by one. Why would that matter for 56 patterns?"

*After user responds, cards generated from gaps found*

## Database Location

- Path: `<project-root>/.ai-learn/srs.db`
- Auto-gitignored on init
- WAL mode for concurrent safety
- Soft deletes on cards (`deleted_at` field)

## Resources

### scripts/

- `srs_db.py` — SQLite database manager with SM-2 algorithm. Handles: init, add-card, add-session, due, review, stats, cards, sessions, export. Python 3.10+ stdlib only, no external dependencies.

### references/

- `sm2-algorithm.md` — Detailed SM-2 formula reference, ease factor interpretation, interval progression examples. Load when explaining scheduling decisions to the user.
