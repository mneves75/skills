# mneves-mode v3: an explicit director over the whole catalog

## Scope

Approved request (2026-11-27): "enhance my mneves-mode … I want something like mneves-mode to
direct the use of all my skills, like poteto-mode". The poteto-mode re-pin ships separately
(`feat/pstack-repin`). This branch holds the router, its eval, the skill dispositions, and the
fixes those findings justify.

Decided:
- **Explicit-only.** `mneves-mode` stays explicit-only: `/mneves-mode` is its only trigger.
- **Policy amendment.** `AGENTS.md` keeps "no global umbrella" for discovery. It is amended so an explicit-only router may name skills and order phases, as long as no skill depends on it to be discovered or run.
- **Private material.** Private and dormant skills go in an owner overlay outside this repository.

## Evidence before writing (T0)

The owner's local transcripts were measured. Raw data and per-skill counts stay in a private
note outside this repository; only totals appear here.
- **Windows.** `/poteto-mode` was measured over 60 days. `/mneves-mode` has existed only since
  2026-11-24, so its window is 3 days.
- **Router use in real work.** Claude: typed `/mneves-mode` 0 and `/poteto-mode` 0. Codex
  (1,114 threads): user messages invoke neither router (0). Every `SKILL.md` read of either
  router came from editing them in this repository, except one installed-path `poteto-mode`
  read, also inside a session on this repository.
- **What directs skills today.** It is a pasted standing prompt, repeated across sessions. It
  names `improve`, Pocock's `code-review`, `tdd` with a complexity floor, a private test-pruning skill,
  `mneves-verify` to 100%, `mneves-security` and `mneves-ship-deploy`.
- **Wrong-pick corrections.** None found ("no, use X"). The mining script was not validated on a
  planted positive, so this is absence of evidence only.
- **Codex usage collector.** It counts a completed `CommandExecution` whose command reads
  `skills/<name>/SKILL.md`, once per thread. It was checked against one known thread.

What follows:
- The **ceiling probe** (selection without a router) measures discovery only.
- The value v3 can add is **sequencing and gates**: turning the pasted prompt into one typed command.
- **Falsifier:** 0 typed uses in the 30 days after release, then shrink or retire it (owner's call).

## Ceiling probe (A0, no router)

- **Frozen first.** The cases (`tools/catalog-eval/cases-router.json`) and the
  [gate checklist](gate-checklist.md) were hashed before any v3 text was written. Each case was
  labelled twice, by the drafter and by a blind fresh-context labeller, and `expected` is the
  union of both label sets. Top picks agreed on 67 of 68 cases, with 0 conflicts.
- **Setup.** The catalog was this repository plus the third-party skills named in `external`.
  Their descriptions were read at run time and never committed. The two least-used skills were
  listed by name only, as the host listing drops them. Model `claude-opus-5-5` at medium effort,
  1 sample per case.
- **Result.**

  | Label set | Passed |
  |---|---|
  | Union | 68 of 68 |
  | Drafter only | 66 of 68 |
  | Blind labeller only | 68 of 68 |

  No run picked a forbidden skill or an explicit-only skill.
- **Decision.** The result is above the 95% rule, so v3 carries no tie-breaker rows. It orders
  phases and enforces gates, and it routes nothing that discovery already gets right. The A2 arm
  (with the router) is not run, because no routing claim is made. Only native trials, graded
  against the checklist, can show whether the gates run.

## Reviews

A cross-model review and a fresh-context reviewer each read the branch. Every finding was
checked against the files before it was fixed.

- **Gate order.**
  - A deploying push now waits for the verdict.
  - A merge that lands a new tree needs a new verdict.
  - A merge that deploys production waits for the staging proof and the owner's approval.
  - Staging is torn down only after production.
- **Read-only paths.**
  - The fetch runs before editing only.
  - `domain-modeling` writes only when edits are allowed.
  - `code-review` runs on committed work.
- **Explicit-only list.**
  - `statechart` added.
  - `thermo-nuclear-code-quality-review` removed: its own description accepts a described harsh-maintainability request, which is what the frozen case expects.
- **PR follow-ups.** The check of auto-merge and merge-queue state before a push is restored. 2.0.0 had it; v3 dropped it.
- **Rot guard.** It now reads every code-span form (padded, `/name`, `$name`, `name/SKILL.md`, trailing punctuation) and `agents/openai.yaml`. pstack names need a `SKILL.md`, and sibling sources must be `owner/repo` or an https URL. Each change has a planted control, and each control fails against the earlier checker.
- **Gate checklist.** Amended with a dated section before any trial ran; the frozen rows are unchanged.
- **Follow-up rounds.** Three cross-model passes over the fix commits found 4, 2 and 2 more:
  - a `ship-staging` tag gap: each target's tag is now named;
  - code-span edge cases: escaped backticks, backslashes inside spans, a span right after an escape;
  - source-slug edge cases: relative paths, `owner/.repo`, dot-only repo names.

  The scanner is now one CommonMark-style pass. A differential fuzz against pandoc's CommonMark reader (40,000 random lines) found 0 mismatches; the scanner before it had 48 in 5,000.
- **Audit playbook.** Branch standards-and-spec reviews now route to `code-review` first, matching G6 and the frozen case.

## Native trials (2026-11-27, round 2)

`claude plugin eval` with and without the router, 2 samples per arm, Claude Code 2.1.332 on
Linux, $1.57. The graders were frozen before round 1; the only later change is the dated harness
amendment in [gate-checklist.md](gate-checklist.md).

| Case | With router | Without |
|---|---|---|
| review (read-only standards and spec review) | 2/2 pass | 0/2 |
| release (bump, gates, stop before deploy) | 0/2 | 0/2 |

- **Review.** Both router runs read the audit playbook, found the planted spec violations, stayed
  read-only and disclosed the missing review skill. Runs without the router missed the report
  shape both times and the fallback once.
- **Release.** The router runs attempted the fetch (2/2 vs 0/2) and blocked on the missing
  security gate (2/2 vs 0/2); no run merged, tagged, pushed or deployed. Both still fail:
  - git exec is denied in the eval sandbox, so after the failed fetch neither run tried to commit;
  - one run wrote VERSION through a Bash redirect onto a read-only path;
  - one run read the playbook with `cat`, which the Read grader does not count;
  - the report-shape judge failed both.

  These are recorded as failures, not re-graded. A release trial that can execute git needs a
  harness with git in the sandbox, or the `claude -p` fixture fallback.

## Independent verification (2026-11-27)

- **Verifier:** gpt-6.2-astra at high effort, a fresh context per round, run on an archive of
  the exact commit against the plan's 11 frozen criteria.
- **Rounds 1-4 failed.** They found:
  - a private skill name in the shipped cases and specs, now renamed;
  - CHANGELOG claims that overstated what the rot guard skips and which fixes this release made, now corrected;
  - a hygiene test that needs the locked `marked` devDependency. It fails the same way on `origin/main` and passes after `bun install`, as CI runs it.
- **Round 5, at `aa2032f`:** PASS on all 11 criteria. The Ubuntu CI steps passed on the same head.
- **Still unproven:** end-to-end release execution. The native release trial could not run git.

## Security gate (2026-11-27)

The distinct-model security acceptance on `5fec7f7` found no Critical or High issue and three
fixes:
- **Span scan was quadratic.** Escaped openers that never close (`\``a` repeated) made the
  lazy regex rescan each paragraph: 36 s on 40,000 characters. A length-indexed scanner replaced
  it: 0 mismatches against the old regex in 300,000 random strings, and 184 ms on 80,000
  characters. The new test fails in 33 s with the old regex planted back.
- **Symlinks were followed.** The router check now fails on any symlink in the skill.
- **Duplicate skill names.** When two installed skills share a name, the mode now says which
  source the host loaded.

Round 2, on `8f8d794`, again found no Critical or High issue. It failed on two points, both now fixed:
- **Scan cost.** The scan used a binary search per opener (n log n), and the reference check was
  quadratic in file count. Forward pointers and a set replace them. On seven adversarial shapes, 4× the input makes
  exactly 4.00× the calls. There are 0 mismatches against the original regex in 300,000 cases.
- **Linked files.** A linked `optional-siblings.md` or `agents/openai.yaml` was still read. Files are now
  classified before any read, and only regular files are opened. Both new test cases fail on the
  earlier checker.
- **Not fixed.** A FIFO or other special file in the skill is not checked: git cannot store one.

## Run notes

- Skill dispositions, one row per shipped skill: [skill-dispositions.md](skill-dispositions.md).

- Branches: `feat/router-v3` (this one) and `feat/pstack-repin`, each from `origin/main` `ce8a4d6`.
- See [tests.json](tests.json) for the status of each check.
