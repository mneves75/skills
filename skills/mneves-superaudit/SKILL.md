---
name: mneves-superaudit
description: Bounded delegated audit-and-ship pass over a repo — slop, performance, agent DX, PR triage. Use for a repo-wide cleanup pass.
license: Apache-2.0
---

# Superaudit

A long-horizon repository pass. Fill the brief, pick the items, work the phases. Detail loads
just-in-time: read a reference only when you reach the phase that needs it.

Your agent's own global instructions and the repository's `AGENTS.md` / `CLAUDE.md` remain in force.
This skill does not restate them and never overrides them.

## 1. Brief

Invoke with a repo and the items you want, e.g. `superaudit ~/dev/myapp — items 1,2`. Fill this in
before anything else.

```
Repo / branch:
Outcome (one line):
Items in scope:            1 slop · 2 perf · 3 agent DX · 4 PR triage   (pick explicitly)
Out of scope:
Acceptance scenario:
Required evidence:
Retry / wait bounds:
Authorization granted:     none beyond local edits  ← change only if the user said otherwise
```

If a field is blank and its answer would change the work, ask. Otherwise state the assumption and
continue.

## 2. Authority

**This skill grants nothing.** Local edits only. Commit, push, tag, release, deploy, and PR merge
each need the user's explicit word for that action and target. Changing files locally does not imply
commit authority; commit authority does not imply push, tag, release, or deploy authority. Phase 4
runs only when the user types a release instruction naming the destination.

## 3. Items

Do only the ones the brief names. Each ends on a falsifiable condition, not a feeling of
completeness.

| # | Item | Done when |
|---|---|---|
| 1 | Slop audit | Ranked delete/simplify list, applied; every deletion leaves a check that fails if behavior regressed |
| 2 | Performance | Baseline and candidate measured under recorded identical conditions; a noisy or circular measurement is inconclusive, never a win |
| 3 | Agent DX & verification loops | Named gaps and fixes for setup, worktree isolation, debug access, and end-to-end QA — concretely, what the agent needs to prove its own work |
| 4 | PR / issue triage | Ranked easy-win list; nothing merged without per-PR authorization |

Item 3 pairs well with `mneves-agent-readiness`, which scores a repository against nine agent-
readiness pillars and gives item 3 a baseline instead of an opinion.

Docs — `README`, `AGENTS.md`, `CLAUDE.md`, changelog — are updated inside the item that changed the
behavior. There is no separate documentation pass.

Optional installed skills sharpen individual items when present; skip any that are absent rather
than substituting a weaker check. A repo-wide over-engineering audit helps item 1, a stack-specific
profiler helps item 2, and a saved end-to-end QA flow helps item 3.

## 4. Delegation

Load `mneves-fable-orchestrator` before the first dispatch. The main session keeps requirements,
architecture, integration, and acceptance, and never takes a worker's summary in place of the diff.

| Work | Send to |
|---|---|
| Read-only discovery across a repo | Search/explore subagents — up to 3 in parallel, disjoint path sets |
| Design / decomposition | A planning subagent |
| Heavy implementation, debugging, multi-file refactor | Your configured execution agent, one lane per path set |
| Deliberate model comparison | Two agents on the same brief, compared on the same evidence |

Read [references/delegation.md](references/delegation.md) before the first dispatch — worker budget,
brief template with explicit negative boundaries, return contract, and when delegating is a net loss.

## 5. Phases

```
0 recon        →  1 findings report     [STOP — user picks what to cut]
2 implement    →  3 verify + review     [STOP — user reads the diff]
4 release                               [STOP — needs an explicit release instruction from the user]
```

A stop gate is a real stop. Report and wait. Approval of one phase is not approval of the next.

Read [references/phases.md](references/phases.md) on entering phase 0 — entry/exit criteria, the
performance measurement protocol, security and review requirements, the progress file that keeps a
long run alive across compaction, and the A/B protocol for testing this skill itself.

## 6. Do not pad this run

Skip the rituals: "think of 10 other solutions", "imagine you are 5 years from now", "are you
satisfied", a second full review pass over unchanged work. None substitutes for a configured
reasoning effort, and none was traced to a real failure.

When this skill misfires, add one line describing that failure. Nothing else. The README explains
what else was deliberately left out and why.
