# Provenance

- Source: [janestreet/agent_skills — socratic-tutor](https://github.com/janestreet/agent_skills/tree/7c6715c29548a3b39d4a9545c698ee4fd17a7213/socratic-tutor).
- Commit: `7c6715c29548a3b39d4a9545c698ee4fd17a7213` (2026-11-03).
- Original procedure: [SKILL.md](https://github.com/janestreet/agent_skills/blob/7c6715c29548a3b39d4a9545c698ee4fd17a7213/socratic-tutor/SKILL.md).
- License: [upstream MIT License](https://github.com/janestreet/agent_skills/blob/7c6715c29548a3b39d4a9545c698ee4fd17a7213/LICENSE.md), preserved verbatim in [LICENSE](LICENSE), Copyright (c) 2026 Jane Street Group, LLC.
- Adapted on: 2026-11-09. The upstream name is `socratic-tutor`; the `mneves-` prefix is the
  owner's explicit choice.

## Adaptations

Keeps the upstream procedure, wording and order: intent guard, diagnostic before teaching,
0-5 skill map, one question per turn, strict level evidence, spaced review, final
assessment and the in-chat commands. Changes, each tied to a defect:

- Portable frontmatter: a one-line capability-and-trigger description and `license: MIT`.
  "quiz me" is no longer a trigger, because `mneves-teach-back-srs` owns stored-card review;
  the guard routes codebase teach-back and flashcards there when it is installed.
- Untested subskills render as `?`, never a guessed level or 0 (upstream's 3-5 question
  diagnostic cannot place up to 10 subskills, and trials scored the rest 0/5).
- One map format: the example now uses the block characters the text asks for, inside a
  code block, and the overall percentage has a stated formula over placed subskills (`?`
  while none is placed). A two-level tree maps the working branch and lists the others as
  not started.
- An ambiguous request gets one short question and nothing else, and the subskill
  breakdown stays private until the diagnostic ends, so the plan does not hint at answers.
- One question means one sentence, with any code it needs placed before it, for diagnostic
  questions too: trials showed a second question appended in about one message in seven, and
  snippets after the question, including the first diagnostic question.
- A wrong answer gets a narrower question without the mechanism behind the answer. The
  tutor counts misses on an idea and explains and re-tests after the third; upstream
  allowed that, but in trials no run ever explained.
- Grading checks the facts before marking a defensible answer wrong, and admits the
  tutor's own errors.
- "just tell me" answers count as told and raise no level until an unprompted re-test.
- Practical exercises with side effects run in the user's scratch location, not the
  agent's tools.
- The save block carries the target, last-checked and due-for-review data that spaced
  review needs; an incomplete or invalid resume block is reported, never guessed, and a
  missing target takes the default instead of another question.
- Teaches in the user's language and offers "save state" when the user stops early.

No executable, dependency, model pin or mandatory sibling skill is added. Trial cases and
results: [docs/specs/mneves-socratic-tutor](https://github.com/mneves75/skills/tree/main/docs/specs/mneves-socratic-tutor)
in the source repository.
