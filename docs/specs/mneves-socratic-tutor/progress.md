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
failed attempt) are the independent reviewer's failing cases. Each case ran once per model in
a fresh headless Claude session with no settings, no MCP servers and no tools, the skill text
as the only installed instruction. The builder graded every run against the case's `expect`
line and the `grading_rules` in the same file; independent acceptance is a separate step.

| Run | Skill text | Cases | Samples | Met per sample | Partial | Failed |
|---|---|---|---|---|---|---|
| Upstream, Sonnet | `socratic-tutor` at `7c6715c` | 15 | 1 | 10 | C03, C11 | C04, C05, C10 |
| Upstream, Haiku | same | 15 | 1 | 10 | C03, C11 | C04, C05, C10 |
| First adaptation, Sonnet | v1 | 15 | 1 | 12 | C02, C03, C11 | none |
| First adaptation, Haiku | v1 | 15 | 1 | 12 | C03, C11 | C08 |
| Review fixes, Sonnet | v2 | 16 | 1 | 14 | C08, C11 | none |
| Review fixes, Haiku | v2 | 16 | 1 | 15 | C15 | none |
| Reviewer fixes, Sonnet | v3 | 18 | 1 | 17 | C17 | none |
| Reviewer fixes, Haiku | v3 | 18 | 1 | 16 | C07, C17 | none |
| Shipped, Sonnet | this skill (v4) | 18 | 3 | 16, 17, 16 | C17 (3), C06 (2) | none |
| Shipped, Haiku | this skill (v4) | 18 | 3 | 17, 16, 17 | C17 (3), C07 (1) | none |

Two more samples of v3 showed the one-question rule drifting: eight of 54 one-question checks
across three samples per model had a second question, usually an added "why?". v4 adds one
clause (one question is one sentence, with the "why" folded in) and its three samples per model
miss one of 54. Every map in the v3 and v4 samples has correct arithmetic: placed count, mean
level, two cells per level and one overall cell per 10%. v4 was graded by mechanical checks on
all 108 outputs; the builder read every flagged output and, in every sample, C01, C05, C06, C09
and C17. The checks reproduce the earlier manual grades of the upstream and v3 runs.

Upstream failures: untested subskills scored `0/5` and counted in the overall (C04, C10) and
the mechanism explained after a wrong answer (C05). Partials are a subskill list shown before
the diagnostic (C03, C11), a course description after the clarifying question (C02), two
questions in one message (v2 C08 and C11, shipped Haiku C07) and no safe way to test a
deleting command (v2 Haiku C15). Two v4 Sonnet C06 replies re-test from a new angle without
saying the told answer earns no level. v4 Haiku C06 calls the transcript's unplaced `2/5` a
guess, as the untested rule allows, and still raises nothing. v1 Haiku C08 restarted the diagnostic because the transcript
did not say it was done; v2 marks it. In C17 both models drew the correct map and listed the
other branches, then re-asked the pending diagnostic question instead of proposing a start; the
skill's step order supports that, so the oracle may be stricter than the skill.

**Correction.** The first record of these trials (commit `a88fdc9`) reported upstream Sonnet 13
of 15 and the adaptation 15 of 15 on both models. Review showed that was overstated: upstream
Sonnet C10 also counted the untested subskill as 0, the original C07 expectation contradicted
the skill (it called `borrowing ?` a missing level; the original wording is kept in
`expect_original`), and the builder had applied no consistent rule for one question or for a
breakdown shown early. The table regrades every run under the rules now in `trials.json`.

**Independent review** (fresh context, 14 cases, 27 runs, three single-clause mutants as
controls): PASS, with findings the adaptation had inherited from upstream. A learner who failed
three times was never given the explanation (0 of 4 runs), a two-level tree's map dropped the
other branches, and the overall bar's rounding was unstated; the shipped text fixes all three
(C17, C18). One of two Haiku runs did not lower a level after a failed spaced review, with the
text unchanged and Sonnet passing, so Haiku is a noisier check than one run per case suggests.
`mneves-teach-back-srs` still mentions quizzes in its description, so a host could route
"quiz me on <topic>" there; that skill is outside this change and host selection was not tested.

The trials exercise a supplied skill file, not native catalog selection, and cover single
next turns, not a whole course. With the breakdown kept private, C13's "derives subskills" is
visible only through the diagnostic question, not as a list.

## Evidence limits

Logs, the runner and the screenshots are private task evidence under `.scratch/socratic-tutor/`.
Local browser checks ran against a static server, not the deployed site. `cccc` 1.8.0 found no
supported files in the change (Markdown, HTML and JSON only), so there is no complexity score.
