# Superaudit

A bounded, delegated audit-and-ship pass over a repository. Four items — slop removal, performance
wins, agent DX and verification loops, PR/issue triage — each with a falsifiable done-condition, run
through five phases with typed stop gates before every external write.

It exists because the ad-hoc version of this request ("audit everything, find a ton of wins, fix it
all, don't stop until you're certain, then deploy") has no acceptance criteria, no retry bound, and
no stopping condition. That prompt shape runs for hours and lands a diff nobody reviewed.

## What it does differently

**Grants nothing.** Local edits only. Commit, push, tag, release, deploy, and PR merge each need the
user's explicit word for that action and target. Release is a phase that exists to be refused.

**Bounded, not exhaustive.** Every item ends on a stated condition, not on a feeling of
completeness. Reviews get one round plus one rerun if accepted findings changed the artifact. If a
second round opens another hole in the same design, the answer is to simplify the invariant, not to
add guards indefinitely.

**Delegation with a budget.** Vague worker briefs are the classic multi-agent failure: workers
duplicate each other and leave the same gap uncovered. Every brief here carries owned paths, the
other workers' paths named as *do not touch*, a required return format, and a stop condition.
Discovery parallelizes because it is read-only; implementation partitions by path or serializes.
Items 1 and 2 touch the same files, so running them as concurrent writers is the degenerate case.

**Measurement that can fail.** A performance result outside noise, or one that depends on the
change's own instrumentation, is reported inconclusive — never as a win. Security and negative
assertions need a positive control placed where the gate actually looks; a control outside the
rule's path proves nothing, and a policy claim only counts against the *served* artifact.

**Survives compaction.** Phase 0 opens `agent_planning/superaudit-<date>.md` and updates it at every
phase boundary. A long run will be compacted; that file is what survives it, and it doubles as the
deliverable for item 3.

## Phases

```
0 recon        →  1 findings report     [STOP — user picks what to cut]
2 implement    →  3 verify + review     [STOP — user reads the diff]
4 release                               [STOP — needs an explicit release instruction]
```

## Layout

| File | Loaded |
|------|--------|
| `SKILL.md` | Always — brief, authority, items, delegation summary, phase map |
| `references/delegation.md` | Before the first dispatch — worker budget, brief template, return contract, when delegating loses |
| `references/phases.md` | On entering phase 0 — entry/exit criteria, performance protocol, security and review requirements, progress file, A/B protocol |

Detail is held behind references so a run that only does item 1 never loads the release phase.

## Pairs with

- [`mneves-fable-orchestrator`](../mneves-fable-orchestrator/) — routing, loaded before the first dispatch
- [`mneves-agent-readiness`](../mneves-agent-readiness/) — gives item 3 a scored baseline instead of an opinion
- [`autoreview`](../autoreview/) — structured isolated review in phase 3
- [`mneves-verify`](../mneves-verify/) — independent PASS/FAIL before anything is called done

Stack-specific profilers and repo-wide over-engineering audits sharpen items 1 and 2 when installed.
Skip an absent one rather than substituting a weaker check.

## Deliberately left out

- **A copy of your agent's global contract.** It is already loaded. Two copies drift, and
  contradictory rules cost the model tokens to reconcile.
- **Platform-specific guidance** (Apple/Xcode, a given framework). That belongs in the individual
  project's `AGENTS.md` or `CLAUDE.md`, once.
- **Model names and reasoning effort.** Routing belongs in your agent's configuration, not in a
  skill meant to outlive any particular model.

## Maintenance

This skill is a hypothesis until measured. `references/phases.md` carries an A/B protocol: same repo,
same starting commit, same item list, old version versus new, compared on wall-clock, tokens,
findings that survived verification, findings that were wrong, and gate violations.

Amend it from observed failures only — one line per real failure. An instruction never traced to a
failure is superstition and costs context on every run.
