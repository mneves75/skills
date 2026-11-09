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

## Trials, written before the adaptation

[`trials.json`](trials.json) holds fifteen next-turn cases: one-off question, ambiguous
request, course start, untested subskills, wrong answer, told answer, malformed resume,
tutor error, stopping midway, save state, Portuguese, blank topic, a very long pasted input,
stored-card routing and a destructive exercise. Each case ran in a fresh headless Claude
session with no settings, no MCP servers and no tools, the skill text as the only installed
instruction. Grading was by the builder against each case's `expect` line; independent
acceptance is a separate step.

| Run | Skill | Result |
|---|---|---|
| Upstream, Sonnet | `socratic-tutor` at `7c6715c` | 13 of 15 met. C04 scored untested subskills `0/5` and folded them into the overall; C05 explained the mechanism after a wrong answer |
| Upstream, Haiku | same | C04 and C10 scored untested subskills `0/5` (C10 counted them in a 6/20 overall); C05 explained the mechanism; the rest met |
| Adapted, Sonnet | this skill | 15 of 15 met |
| Adapted, Haiku | this skill | 15 of 15 met; C05 asks a leading question rather than a smaller case, which still withholds the answer |

Both models already handled routing, destructive commands, malformed resume blocks, tutor
errors and Portuguese with the upstream text, so those adaptations are one clause each.
The trials exercise a supplied skill file, not native catalog selection, and cover single
next turns, not a whole course.

## Evidence limits

Logs, the runner and the screenshots are private task evidence under `.scratch/socratic-tutor/`.
Local browser checks ran against a static server, not the deployed site. `cccc` 1.8.0 found no
supported files in the change (Markdown, HTML and JSON only), so there is no complexity score.
