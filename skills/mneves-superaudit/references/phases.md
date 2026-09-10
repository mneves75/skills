# Phases

Read on entering phase 0.

## Progress file

Create `agent_planning/superaudit-<YYYY-MM-DD>.md` at the start of phase 0 and update it at every
phase boundary: current phase, findings accepted and rejected, paths owned by each worker, evidence
gathered, open questions. A long run will be compacted; this file is what survives it. It is also
the raw material for item 3.

## 0 — Recon

Read the repo's `AGENTS.md` chain root-to-target, `CLAUDE.md`, `README`, `PROJECT_STATUS.md`, and
any `MEMORY.md`. Establish the stack, the test/build/lint invocations, and the documented gate list
— gates are what the repo says they are, not a remembered subset.

Record `git status -sb` before touching anything. Unknown changes belong to the user or another
agent; preserve them.

Exit: the brief's blank fields are filled or explicitly assumed, and the item list is final.

## 1 — Findings

Produce a ranked report per item in scope. Each finding carries: what, where (`path:line`), why it
is wrong, the proposed change, the risk, and the check that would prove the change safe.

Search the web only when correctness depends on current, version-specific, or external facts. Cite
primary sources. Stop when the evidence is sufficient, not when it is exhausted.

**STOP.** Present the report. The user selects what to cut. Do not begin implementing.

## 2 — Implement

Only the selections from the gate. Preserve unrelated behavior and other agents' changes.

For a bug: reproduce the failure first, then fix the root cause where all callers route through —
not the one path the report named.

## 3 — Verify and review

Run the smallest check that could falsify the change first, then broaden by risk to the repo's
documented gate list. Order the commands so a later formatter or filter cannot mask an exit code.
Only claim checks that actually ran in this session.

**Performance (item 2).** Record hardware, system load, branch, commit, and warmup for both baseline
and candidate; vary one thing. Never measure during concurrent writes. A benchmark whose result
depends on the change's own instrumentation is circular — discard it. A measurement inside noise is
inconclusive and is reported as such.

**Security.** Audit the changed surface before any production gate, and say plainly whether the audit
covered the diff or the whole application. Every negative assertion and security gate needs a
positive control placed where the gate actually looks — a control outside the rule's path or selector
scope proves nothing. A header, CSP, or policy claim only counts when tested against the *served*
artifact, not the source that was meant to produce it.

**Review.** Review on two independent axes: Standards (correctness, safety, maintainability, this
repo's documented rules, evidence quality) and Spec (every requested behavior, boundary, non-goal,
and acceptance criterion against the changed artifact). The `autoreview` skill in this collection
runs a structured, isolated review when the risk or a repository gate calls for one, and
`mneves-verify` supplies an independent fresh-context PASS/FAIL check before you call anything done.
Routine and prose-only changes need no model review.

Bound: one review round, plus one rerun only if accepted findings changed the artifact. Findings are
hypotheses — verify each against the real artifact before fixing it. If a second round opens another
hole in the same design, simplify the ownership or invariant and report what remains. Do not add
guards indefinitely.

**STOP.** Present the diff and the evidence. The user reads it.

## 4 — Release

Runs only on an explicit release instruction from the user that names the destination. Nothing in
this skill authorizes it.

Sequence: version bump → changelog and affected docs → commit task-owned paths only → push the
authorized branch → tag (use a prerelease suffix such as `beta<N>` for staging) → deploy → verify the
destination and artifact directly, not the deploy tool's exit code. Never move a pushed tag. Return
to the expected branch and check `git status -sb`.

A tag identifies deployed bytes, not an assumed source diff. If the exact immutable build is already
live at the requested destination, verify it rather than redeploying.

Before deploying anything that introduces a required secret, binding, or variable, confirm it exists
in every environment that reads it.

## A/B protocol — testing this skill

This skill is a hypothesis until measured. To test a change to it: same repo, same starting commit,
same item list, old version vs new. Compare wall-clock, tokens, findings that survived verification,
findings that were wrong, and gate violations. Two runs is enough to catch a regression; it will not
resolve a small difference, and should not be reported as if it did.

Amend the skill from observed failures only. An instruction never traced to a real failure is
superstition and costs context on every run.
