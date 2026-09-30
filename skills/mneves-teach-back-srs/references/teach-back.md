# Mode 1: teach-back session

Use the helper path resolved in SKILL.md with the user's project as working directory.
Initialize the database before its first session. Read the card-quality guide named by SKILL.md
before generating cards; the other modes and algorithm details remain conditional.

1. Establish one meaningful topic from the request: a module, subsystem, data flow, or design
   decision. Ask only if the topic is missing or materially ambiguous.
2. Let the user explain without interrupting. Track correct understanding, misconceptions,
   missing behavior, and vague claims.
3. Inspect actual files/functions, callers, and relevant failure paths to check those claims.
   Start with the named unit; expand only when a claim depends on another module. Do not turn
   a learning session into a repository-wide audit.
4. Probe the weakest areas with targeted Socratic questions: misconception correction, missed
   behavior, design rationale, then edge cases. Usually three to five suffice; ask fewer if
   the user supplied less material. Cite checked file/function locations and let the user
   answer before adding a new round.
5. Generate cards covering every verified gap and misconception, avoiding duplicates and
   unsupported assertions. Store each with `python3 "$SRS_SCRIPT" add-card` using the
   card-quality rules.
6. Record actual counts and a concise checked summary:

   ```bash
   python3 "$SRS_SCRIPT" add-session \
     --topic "Request authorization" \
     --summary "Explained the normal path; corrected the ordering of denial checks" \
     --gaps 3 \
     --cards 3
   ```

7. Summarize what was correct, checked gaps with code references, stored card count, and the
   next scheduled review. Distinguish a storage error from a successfully recorded session.

Continue only while the user is participating in the selected learning topic; avoid generating
speculative cards or unrelated follow-up sessions to fill a fixed quota.
