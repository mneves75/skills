# Card Quality Rules

Applies to every flashcard generated in Step 6 of a teach-back session. Bad cards are worse
than no cards: they train recall of the wrong thing or become unanswerable months later.

## Question format

- Cover one concept and avoid wording that overlaps another card
- Ask about the *why* or *how*, not just *what*
- Prefer a concrete scenario ("What does X do when Y?") over a broad prompt
- Reference specific code locations when relevant
- Frame around the misconception or gap, not the correct answer

## Answer format

- Concise but complete (2-4 sentences)
- Include the file/function reference
- Explain the "why" behind the correct answer

## Difficulty assignment

- `easy`: Simple fact the user almost had right
- `medium`: Conceptual gap requiring understanding
- `hard`: Deep misconception or architectural blind spot

## Tags

Tag with the module name plus the concept category, comma-separated
(e.g., `auth,security,middleware`).

## Storing a card

Run the script once per card, from the skill's own directory, with the user's project as the
working directory:

```bash
python3 scripts/srs_db.py add-card \
  --question "Why does the safety pipeline check intent before sanitizing input?" \
  --answer "Intent gate (safety/intent.rs) runs first because it can reject catastrophic intents without any model call, saving latency and cost. Sanitization (ai/sanitize.rs) runs after because it only matters if the query will reach the model." \
  --context "safety/intent.rs, ai/sanitize.rs" \
  --tags "safety,pipeline,architecture" \
  --difficulty medium
```
