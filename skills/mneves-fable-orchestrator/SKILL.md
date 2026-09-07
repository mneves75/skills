---
name: mneves-fable-orchestrator
description: Route non-trivial work across agents. Use for delegation, parallel work, Codex dispatch, or long-running implementation.
license: Apache-2.0
---

# Fable Orchestrator

Route only when delegation saves time or adds independent evidence. The active main session owns
requirements, architecture, high-stakes judgment, integration, and final acceptance.

## Current roles

| Role | Default | Responsibility |
|---|---|---|
| Claude main session | Fable 5.1 | Framing, design decisions, decomposition, acceptance |
| Claude subagent | Opus 5 | Bounded frontend or independent work |
| Codex | `gpt-6-astra`, reasoning `high` | Execution, planning, review, and ordinary inherited agents |
| Specialist | Explicit model/agent selection | Deliberate comparison or capability-specific work |

The user's current instruction beats this routing. Preserve explicit caller overrides and
specialist selections. Astra is an executor; do not insert an advisor-only handoff before it can
perform ordinary implementation. Quota probes may use Astra at `low`; do not use unsupported
`minimal` or `none` effort.

## Route the task

Keep work in the main session when it is a small direct edit, depends on session-only tools or
credentials, changes authorization, or requires a product/architecture decision.

Delegate when the work is independent, substantial, objectively verifiable, and has disjoint
file ownership. Parallelize only independent workstreams. Do not delegate a few direct reads or
duplicate work already assigned.

When the active session is already Codex, implement and verify directly. Spawn a specialist only
for a genuinely independent workstream or a review that benefits from fresh context.

For a Codex dispatch from Claude or another harness, use `codex-auto`. Read
[references/codex-dispatch.md](references/codex-dispatch.md) before the first launcher or lane
command; it owns account selection, explicit overrides, continuity, and recovery.

For a user-requested multi-phase goal that must continue across many rounds, use the available
goal workflow. A long task alone does not authorize pushes, deployments, destructive operations,
or other external writes.

## Delegation brief

Every executor starts with zero private session context. Include:

1. Goal and falsifiable acceptance criteria.
2. Repository and exact paths.
3. Relevant behavior, evidence, and errors.
4. Constraints, non-goals, ownership, and behavior to preserve.
5. Exact proof commands and expected output.

Tell the worker it is not alone in the tree, must preserve other changes, must not spawn agents,
and must not run cross-session memory. Pair a hard prohibition with a safe stop condition: if an
honest attempt cannot satisfy a gate, report the exact result instead of gaming the constraint.

## Accept delegated work

Inspect the actual diff and merged surface. Run the focused proof yourself or verify captured
output. Review guard, budget, fixture, and test-helper edits closely because they can weaken the
check rather than fix the behavior. Check the brief's assumptions and production rules; test
existence is not a substitute for the required behavior.

Use an independent fresh-context review when risk, the repository, or the user requires it.
Routine edits need only proportionate deterministic checks. If a correction is needed, continue
the existing agent or lane so it retains context.

Delegation never widens permission. Destructive or irreversible actions, credentials, external
writes, and scope expansion keep the main session's approval boundary.
