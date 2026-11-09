# mneves-socratic-tutor adoption

## Confirmed scope

On 2026-11-09 the owner asked to review, optimize and add janestreet/agent_skills to this
collection with the `mneves-` prefix, then confirmed every recommendation of the interview
("yes to all"), added "and deployed to prod", and re-granted the sixteen conditional
candidate-only readiness waivers for this candidate only. Upstream holds one skill,
`socratic-tutor`, at `7c6715c29548a3b39d4a9545c698ee4fd17a7213` (MIT, Jane Street Group, LLC).
This is a single-session feature with no separate tickets.

- **Q1** Ship a separate skill, `skills/mneves-socratic-tutor/`. Rejected alternative: a mode
  inside `mneves-teach-back-srs`, which is codebase-only and carries an SQLite helper this
  any-topic, stateless tutor does not need.
- **Q2** Keep upstream's paste-able `save state` / `resume from:` block and complete it with
  target, last-checked and due-for-review data; an incomplete or invalid block is reported,
  never guessed. No executable or file writes; `mneves-teach-back-srs` is named only as an
  optional sibling with a fallback.
- **Q3** "quiz me" stops being a trigger (`mneves-teach-back-srs` owns it); the routing guide
  separates one explanation (`mneves-eli5`), stored-card review and codebase teach-back
  (`mneves-teach-back-srs`) and a course to mastery (this skill).
- **Q4** Adapt, do not rewrite: keep upstream structure and voice, fix the defects, one file of
  about 150 lines at most.
- **Q5** The naming invariant gains "or one the owner chooses to prefix"; the upstream name is
  recorded in `UPSTREAM.md`, `NOTICE` and the skill ledger.
- **Q6** Release 1.47.0 with the full catalog surface, the owed 1.46.1 ledger fold and the
  re-verified model ids; then the security and readiness gates, merge, publication and the
  annotated `v1.47.0` tag, as the owner authorized.

## Trials

[`trials.json`](trials.json) holds eighteen next-turn cases. C01-C15 were written before the
adaptation: one-off question, ambiguous request, course start, untested subskills, wrong
answer, told answer, malformed resume, tutor error, stopping midway, save state, Portuguese,
blank topic, a very long pasted input, stored-card routing and a destructive exercise. C16
(progress map before any placement) came from review; C17 (two-level tree map) and C18 (third
failed attempt) are the independent reviewer's failing cases. Each case runs in a fresh
headless Claude session with no settings, no MCP servers and no tools, the skill text as the
only installed instruction. Every run is graded against the case's `expect` line and the
`grading_rules` in the same file; independent acceptance is a separate step.

| Run | Skill text | Cases | Samples | Met per sample | Partial | Failed |
|---|---|---|---|---|---|---|
| Upstream, Sonnet | `socratic-tutor` at `7c6715c` | 15 | 1 | 9 | C03, C07, C11 | C04, C05, C10 |
| Upstream, Haiku | same | 15 | 1 | 9 | C03, C07, C11 | C04, C05, C10 |
| First adaptation, Sonnet | v1 | 15 | 1 | 12 | C02, C03, C11 | none |
| First adaptation, Haiku | v1 | 15 | 1 | 12 | C03, C11 | C08 |
| Review fixes, Sonnet | v2 | 16 | 1 | 14 | C08, C11 | none |
| Review fixes, Haiku | v2 | 16 | 1 | 15 | C15 | none |
| Reviewer fixes, Sonnet | v3 | 18 | 1 | 17 | C17 | none |
| Reviewer fixes, Haiku | v3 | 18 | 1 | 16 | C07, C17 | none |
| One-sentence question, Sonnet | v4 | 18 | 3 | 16, 17, 16 | C18 (3), C06 (2) | none |
| One-sentence question, Haiku | v4 | 18 | 3 | 17, 15, 16 | C05, C07 | C06 (3), C18 (1) |
| Counted misses, Sonnet | v5 | 18 | 3 | 17, 16, 17 | C07 (3), C06 (1) | none |
| Counted misses, Haiku | v5 | 18 | 3 | 18, 17, 18 | C07 (1) | none |
| Default target, Sonnet | v6 | 18 | 3 | 16, 17, 16 | C03 (2), C04, C10, C17 | none |
| Default target, Haiku | v6 | 18 | 3 | 16, 18, 18 | C07, C15 | none |
| Shipped, Sonnet | this skill (v7) | 18 | 3 | 16, 15, 17 | C04 (2), C17 (2), C10, C12 | none |
| Shipped, Haiku | this skill (v7) | 18 | 3 | 17, 15, 18 | C05, C07, C08, C15 | none |

Upstream to v3 ran once per model and were graded under the rules of their round; upstream
C07 now counts as partial because it calls the valid untested `borrowing ?` a missing level.
v4 onward ran three samples per model under the final cases and rules. The builder graded v4
and v5. v6 and v7 were graded by a fresh-context grader: the builder's model family, without its
context or grades. It read every line of all 216 outputs under one standard. That grader is
stricter than the builder: a map row merging a probed and an unprobed idea under one level
(C04, C17), a second code block after the save block (C10) and a missing credit (C08) are
partial. So the v6 and v7 rows compare with each other, not with the rows above.

What each round changed, and the evidence for it:

- **v4**: one question is one sentence. Two more samples of v3 had a second question in eight
  of 54 one-question checks; v4 had it in one.
- **v5**: count the misses on an idea, explain after the third, and put any code before the
  question. v4 Haiku C18 narrowed again instead of explaining in one of three samples (v3
  Haiku the same, one of three), and v4 Sonnet put the snippet after its question in C18.
- **v6**: an invalid resume block with no target takes the default target without asking.
  v5 C07 added a second question about the target in four of six samples; v6 in none. One
  v6 Haiku sample still asked about the out-of-range level inline (`4? 5? a typo?`) before its
  closing question, which the one-question rule counts as partial.
- **v7**: diagnostic questions take the same form as every other question. The rule had sat
  only in the teaching loop. v6 Sonnet put the queries after the first diagnostic question in
  two of three samples (C03); v7 did so in none. The other v6-to-v7 differences are single-run
  partials on cases the change does not touch (C04, C05, C08, C12, C17): 101 met and 7
  partial on v6, 98 met and 10 partial on v7, no failures on either.

Every rendered map in the v3 to v7 samples has correct arithmetic: placed count, mean level,
two cells per level and one overall cell per 10%. For v5 and the first v6 record the builder
read C05, C06, C07, C16, C17 and C18 of every sample in full and only the opening and closing
lines of the rest; that skim missed the v6 C03 partials. Mechanical checks (question count, content
after the closing question, map arithmetic, safe-path and routing markers) only flag outputs for
reading.

Residual partials on the shipped text, none a failure: Sonnet merges a probed and an unprobed
idea into one placed row (four of its six C04 and C17 outputs); one Haiku run asks about an
out-of-range level inline (C07); and single runs leak a planning line (C12), hint at the
mechanism in the narrower question (C05), confirm without crediting (C08), move a destructive
run to a scratch folder without a `-print` check (C15), or add the map after the save block
(C10).

**Corrections.** The first record of these trials (commit `a88fdc9`) reported upstream Sonnet
13 of 15 and the adaptation 15 of 15 on both models; review showed upstream Sonnet C10 also
counted the untested subskill as 0, the C07 expectation contradicted the skill, and no
consistent rule was applied for one question or an early breakdown. The v4 record (commit
`2843773`) then claimed no failures in 108 runs: the final cross-model review found v4 Haiku
C18 narrowing instead of explaining, which a mechanical check had passed, and v4 Haiku C06
retracting the transcript's `2/5` in all three samples. Oracle changes keep the earlier wording
in `expect_original` and give the reason in `oracle_note`: C07 accepts `borrowing ?` as valid
and treats calling it an error as partial; C08 and C06 mark the diagnostic as done in the
transcript; C17 accepts re-asking a pending diagnostic question instead of proposing a start,
as steps 3-4 order. The v4 failures above are graded against the unmarked C06 transcript.
The v6 record (commit `dadb016`) then claimed Sonnet 18 of 18 in every sample. The independent
verifier found the C03 partials in two Sonnet samples, and found that `tests.json` gave the
upstream baseline as 10 of 15 where this table says 9. The full regrade above replaces those
v6 counts.

**Independent review** (fresh context, 14 cases, 27 runs, three single-clause mutants as
controls): PASS, with findings the adaptation had inherited from upstream. A learner who failed
three times was never given the explanation (0 of 4 runs, upstream text included), a two-level
tree's map dropped the other branches, and the overall bar's rounding was unstated; the shipped
text fixes all three (C17, C18). One of two Haiku runs did not lower a level after a failed
spaced review, with the text unchanged and Sonnet passing. `mneves-teach-back-srs` still
mentions quizzes in its description, so a host could route "quiz me on <topic>" there; that
skill is outside this change and host selection was not tested.

The trials exercise a supplied skill file, not native catalog selection, and cover single
next turns, not a whole course. With the breakdown kept private, C13's "derives subskills" is
visible only through the diagnostic question, not as a list.

## Evidence limits

Logs, the runner and the screenshots are private task evidence under `.scratch/socratic-tutor/`.
Local browser checks ran against a static server, not the deployed site. `cccc` 1.8.0 found no
supported files in the change (Markdown, HTML and JSON only), so there is no complexity score.
