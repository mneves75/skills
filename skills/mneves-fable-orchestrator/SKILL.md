---
name: mneves-fable-orchestrator
description: Route non-trivial work across agents. Use for delegation, parallel work, Codex dispatch, or long-running implementation.
license: Apache-2.0
---

# Fable Orchestrator

Route only when delegation saves time or adds independent evidence. The active main session owns
requirements, architecture, high-stakes judgment, integration, and final acceptance.

## Roles

Roles are capabilities, not product names. Bind them to concrete models in the Defaults block
below, or in your own agent configuration — a model release should change one block, not the
whole skill.

| Role | Responsibility |
|---|---|
| Main session | Orchestration: framing, design decisions, decomposition, acceptance |
| Frontend subagent | Bounded UI work: components, styling, layout, visual polish |
| Heavy executor | Execution, debugging, refactors, other non-frontend work, and ordinary inherited agents |
| Reviewer | Independent review of a fixed Git target (`autoreview` when installed) |
| Specialist | Deliberate comparison or capability-specific work |

The user's current instruction beats this routing. Preserve explicit caller overrides and
specialist selections. The heavy executor is an executor: do not insert an advisor-only handoff
before it can perform ordinary implementation.

### Defaults

The only place this skill names models. Edit this block on a model release; nothing else.

```
main session      = Fable 5.1 (Claude harness) | gpt-6-astra, reasoning xhigh (Codex harness)
frontend subagent = Opus 5.1
heavy executor    = gpt-5.6-sol, reasoning xhigh   (quota probes: low)
reviewer          = gpt-6-astra, reasoning xhigh   (autoreview's Codex default)
```

Reasoning-effort names are vendor enums and change; if one is rejected, read the CLI's `--help`
rather than guessing a neighbouring value.

## Route the task

Keep work in the main session when it is a small direct edit, depends on session-only tools or
credentials, changes authorization, or requires a product/architecture decision.

Delegate when the work is independent, substantial, objectively verifiable, and has disjoint
file ownership. Parallelize only independent workstreams. Do not delegate a few direct reads or
duplicate work already assigned.

The same split applies when the main session runs inside Codex: substantial independent work goes
to a heavy-executor worker with its model and effort set in the spawned agent's configuration (a
model requested in prose is a wish), a fresh context, and a self-contained brief. Small direct
edits stay in the main session.

For a Codex dispatch from another harness, one round is `codex exec`, and `tools/codex-lane`
(shipped here) keeps a thread alive across rounds. `codex-auto` appears in the reference as a
personal profile-selecting launcher; it is **not shipped with this skill** — substitute plain
`codex exec` if you do not have it. Read
[references/codex-dispatch.md](references/codex-dispatch.md) before the first launcher or lane
command; it owns account selection, explicit overrides, continuity, and recovery.

A multi-phase goal that must continue across many rounds needs a driver that survives context
loss — a lane, a checked-in plan file, or your harness's own long-task mechanism. A long task
alone does not authorize pushes, deployments, destructive operations, or other external writes.

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

Use an independent fresh-context review when risk, the repository, or the user requires it; it
runs on the reviewer role. `autoreview` is a sibling skill in this repository, not shipped with
this one; without it, run the reviewer model read-only on the diff with a self-contained brief.
Routine edits need only proportionate deterministic checks. If a correction is needed, continue
the existing agent or lane so it retains context.

Delegation never widens permission. Destructive or irreversible actions, credentials, external
writes, and scope expansion keep the main session's approval boundary.
