---
name: mneves-fable-orchestrator
description: Route non-trivial work across agents. Use for delegation, parallel work, Codex dispatch, or long-running implementation.
license: Apache-2.0
compatibility: Codex dispatch needs the Codex CLI (`codex`) logged in, bash, and python3 on PATH; put `tools/codex-lane` on PATH (symlink or alias) for lane commands. Without Codex the routing rules still apply to your harness's own subagents.
---

# Fable Orchestrator

The main session plans, advises and reviews. Its tokens go where judgment matters: requirements,
architecture, the spec, integration, reading what comes back, and final acceptance. Implementation
goes to an executor with a written spec when it is substantial, independent and checkable; the main session does the rest and may keep the hardest part.

## Roles

Roles are capabilities, not product names. Bind them to concrete models in the Defaults block
below, or in your own agent configuration — a model release should change one block, not the
whole skill.

| Role | Responsibility |
|---|---|
| Main session | Planning, advice and review: framing, design decisions, the spec, decomposition, acceptance |
| Frontend subagent | Bounded UI work: components, styling, layout, visual polish |
| Ordinary worker | Scoped implementation and routine inherited agents |
| Bounded worker | Search, summaries, writing, and mechanically checkable tasks |
| Heavy executor | Difficult debugging, architecture, or refactors needing stronger execution |
| Planner | Develop the plan before implementation; does not execute the changes |
| Plan advisor | Read-only review of a plan before a decision with real downside; nothing else |
| Reviewer | Independent review of a fixed Git target (`autoreview` when installed) |
| Specialist | Deliberate comparison or capability-specific work |
| Economy executor | Bounded, test-first tickets on a low-cost model |

The user's current instruction beats this routing. Preserve explicit caller overrides and
specialist selections. The heavy executor is an executor: do not insert an advisor-only handoff
before it can perform ordinary implementation.

### Defaults

The only place this skill names models. Edit this block on a model release; nothing else.

```
main session      = Opus, latest release (Claude alias `claude-opus-5-5`), reasoning medium | gpt-6.1-sol, reasoning high (Codex orchestrator)
frontend subagent = Opus, latest release (Claude subagent alias `opus`), reasoning medium | gpt-6.1-sol, reasoning high (Codex worker)
ordinary worker   = Opus, latest release (Claude subagent alias `opus`), reasoning medium | gpt-6.1-sol, reasoning high (Codex worker)
bounded worker    = Opus, latest release (Claude subagent alias `opus`), reasoning medium | gpt-6.1-sol, reasoning high (bounded Codex task)
heavy executor    = Opus, latest release (Claude subagent alias `opus`), reasoning medium | gpt-6.1-sol, reasoning high (Codex worker)
reviewer          = Opus, latest release (Claude subagent alias `opus`), reasoning medium | gpt-6.1-sol, reasoning high (autoreview `--model gpt-6.1-sol --thinking high`); when no Codex account can run: Fable, latest release (Claude subagent alias `claude-fable-5-2`), reasoning high
planner           = Fable, latest release (Claude subagent alias `claude-fable-5-2`) | gpt-6-astra, reasoning xhigh (planning)
plan advisor      = Fable, latest release (Claude `advisorModel` alias `claude-fable-5-2`) | gpt-6-astra, reasoning xhigh (advice and plan review)
specialist        = gpt-6.1-sol, reasoning high (specialist execution; a specialist review takes the reviewer seat)
economy executor  = opencode-go/deepseek-v4.1-flash, reasoning high (pi on any host; the only substitute when no Claude or Codex seat for that role can run)
```

When review runs, a seat never reviews what it built. That covers the workers, the heavy executor, the economy
executor, and the main session when it kept the hardest part: a change is
reviewed by the reviewer value in the other column from the seat that built it, and an economy
executor's change by either reviewer value. When no reviewer value allowed for a change can run
except the Codex one, and no Codex account can run (Codex not installed, out of quota, not signed
in, or refused by host policy; a slow or failing run does not count), the reviewer row's
fallback reviews in its place, in a fresh context, gates and security acceptance included.
Record the substitution and the error each Codex account returned. The fallback never reviews a
change its own model built; when it is excluded and no other model can review, report the gate
blocked, and the economy executor does not take that review. Planning and
plan advice run only on their own seats. Crossing means the change leaves for the other column's
provider: authorize that disclosure as you would for any review provider before dispatching it.

Verified against the vendor model lists on 2026-11-13; a release re-verifies every id above and
updates this date (CI requires it to match the release date, and that the values named above
appear nowhere else in this file). A seat that names a versioned alias stays on that release
when the host's short alias moves; check what each short alias resolves to on every release.
A dispatch tool that accepts only short aliases cannot take a versioned id: set it in the
agent definition's model field instead.

### The economy executor

The economy executor row is a regular implementation seat for bounded tickets whose proof is a
test written first. Dispatching to it sends the code to that row's provider, so:

- Never send it a repository that declares client, personal or regulated data, or one whose
  owner has not approved that provider. Host-policy or task restrictions on a provider are not a
  reason to route around them.
- Say which seat built the change in the first status line and in the final report. A silent
  choice hides which model produced the evidence.
- Never take it when the caller, the repository, or a gate names a model. Report that gate as
  blocked instead.
- It cannot satisfy cross-model review of its own output: it reviewing its own output is
  self-review, and two sessions of the same model are still self-review. If no other model can
  review, report the review gate blocked instead of running it.
- Nothing else relaxes. Effort selection, evidence, acceptance and permission rules are the
  same, and this seat gains no authority another seat lacked.

It is also the only substitute, apart from the reviewer row's named fallback, when no authorized
primary seat for a role can run: not installed, not signed in, out of quota, or refused by host
policy. Record why each applicable primary
failed, and announce the substitution the same way.

Reasoning-effort names are vendor enums and change; if one is rejected, read the CLI's `--help`
rather than guessing a neighbouring value.

## Route the task

For explicit `council`, `convene the council`, or independent multi-CLI deliberation requests, use
`council` when installed; it owns bounded independent deliberation, member safety and the
transcript. Without it, say it is unavailable and use the main session's solo plan marked
un-counciled. Do not turn ordinary delegation, expert review or verification into a council
implicitly; provider disclosure and the requested round/cost bounds remain binding.

Before writing a non-trivial plan, red-team it. Play the request back in full. Assume it failed
six months on and name the three likeliest causes: an assumption nobody checked, a failure case
nobody considered, optimism that saved effort. Give each its trigger, its cost and the cheapest
experiment that would show it early. Say whether a simpler route reaches the same goal. End with
one verdict: ship, run this experiment first, or stop.

Keep work in the main session when it is a trivial edit, depends on session-only tools or
credentials, changes authorization, or requires a product/architecture decision. The main session
may also keep the hardest part of a task, where writing the spec would cost more than the work.

Dispatch implementation only when it is substantial, independent and objectively verifiable, with
disjoint file ownership: write the spec first, then send it to an executor; otherwise the main
session does it. Parallelize only independent workstreams. Do not delegate a few direct reads or
duplicate work already assigned. Never stash, switch, rebase, or reset someone else's dirty work
merely to begin a dispatch; give parallel workers their own worktrees instead.

Select the cheapest configured role that can satisfy the task and its proof; escalate on
requirements or demonstrated difficulty. Host routing and explicit caller choices override
these portable defaults. Configure the spawned model/effort in the actual dispatch, not prose.
Use fresh context and a self-contained brief for an independent worker; continue the same
worker for corrections to its task.

Use the reviewer only when the user, repository, or risk requires independent review. A
different-model requirement needs an explicitly selected reviewer allowed by the host policy;
ordinary review defaults do not satisfy it automatically. The reviewer row's fallback, under the
conditions above, is such a selection. If none is available, report the gate as blocked. The
planner and plan advisor serve planning and advice only and never execute implementations; their
model reviews only as the reviewer row's fallback.

For a Codex dispatch from another harness, one round is `codex exec`, and `tools/codex-lane`
(shipped here) keeps a thread alive across rounds. `codex-auto` appears in the reference as a
personal profile-selecting launcher; it is **not shipped with this skill** — substitute plain
`codex exec` if you do not have it. Read
[references/codex-dispatch.md](references/codex-dispatch.md) before the first `codex exec` or
lane command; it owns flag placement, continuity, failure classes, and the optional launcher.

A multi-phase goal that must continue across many rounds needs a driver that survives context
loss — a lane, a checked-in plan file, or your harness's own long-task mechanism. A long task
alone does not authorize pushes, deployments, destructive operations, or other external writes.
When nobody is watching the run, a question in an ordinary message goes unseen: ask through the
harness's question tool with the full context and a recommended option, and if it returns no
answer, take the safe path (leave the work unmerged and undeployed) and lead the final report
with the question.

## Delegation brief

Every executor starts with zero private session context. Include:

1. Goal and falsifiable acceptance criteria.
2. Repository and exact paths.
3. Relevant behavior, evidence, and errors.
4. Constraints, non-goals, ownership, and behavior to preserve.
5. Exact proof commands and expected output.

Tell the worker it is not alone in the tree, must preserve other changes, must not spawn agents,
and must not run cross-session memory. Only the session that owns a pull request watches it: a
delegated worker or reviewer never starts a PR watcher. Pair a hard prohibition with a safe stop condition: if an
honest attempt cannot satisfy a gate, report the exact result instead of gaming the constraint.
A cornered worker satisfies the letter of a rule (told never to raise a size budget, one
hand-minified identifiers and passed every gate); treat a stop-report as a successful run, the
coordinator's decision point.

## Accept delegated work

Inspect the actual diff and merged surface. Run the focused proof yourself or verify captured
output. A worker's "tests pass" is a claim; proof is what you observed in this session, and
green mocked tests do not prove user-visible behavior. Review guard, budget, fixture, and test-helper edits closely because they can weaken the
check rather than fix the behavior; a commit message you did not commission is a lead. Check the brief's assumptions and production rules; test
existence is not a substitute for the required behavior.

Read the diff for shape as well as behavior: fewer, deeper modules with smaller interfaces; input
checked once where it enters and trusted after; one-off logic written where it is used, not split
into a function ahead of a second caller.

Bind each claim to the right task, project/session and source revision before accepting it.
Inspect the cited artifact and reconcile the strongest counterexample; a missing record or
an unused instruction is not proof of a workflow defect. Check the format and coverage of a
collector before making absence claims. Label measured facts, estimates and unknowns; do not
infer savings from instruction size or attribute total session usage to one task without proof.
Retrieve bounded relevant excerpts, keeping full critical output locally when needed.

Use an independent fresh-context review when risk, the repository, or the user requires it; it
runs on the reviewer role. `autoreview` is a sibling skill in this repository, not shipped with
this one; without it, run the reviewer model read-only on the diff with a self-contained brief.

For code review, always include an adversarial challenge to the weakest plausible assumption.
When `cccc` is installed, collect complexity evidence for supported changed source before
dispatch and supply the version, target/config identity, file coverage, diagnostics and status.
The separate `autoreview` skill owns its detailed complexity reference; single-skill installs
may lack it. Then run `cccc --no-cache --min 0` on focused source with the owning config,
reconcile expected files and parsing errors, report missing/unsupported/incomplete evidence,
and continue independent review. Scores never replace tests or standards/spec judgment.
Routine edits need only proportionate deterministic checks. If a correction is needed, continue
the existing agent or lane so it retains context.

Delegation never widens permission. Destructive or irreversible actions, credentials (reading, printing, rotating or using a secret),
external writes (remote services, publishing, messages outside the session), and scope expansion
keep the main session's approval boundary.
