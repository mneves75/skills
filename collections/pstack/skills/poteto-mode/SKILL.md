---
name: poteto-mode
description: "Use the Pstack playbooks when the user requests poteto mode or its engineering workflow style."
metadata:
  menu-description: "apply the Pstack engineering playbooks when requested"
---

# Poteto mode

## Platform Adaptation

These skills use Claude Code tool names (the `Skill` tool, the `Agent` tool, `AskUserQuestion`) and the Claude model names the `Agent` tool accepts, as each Models section lists them. On Claude Code they work as written. On Codex, read [`references/codex-tools.md`](references/codex-tools.md) for the Codex equivalent of a Claude tool, model, or skill named by these workflows. On Pi, read [`references/pi-tools.md`](references/pi-tools.md) instead. Other runtimes can discover the same Agent Skills tree, but they must use their own tool, model, and configuration equivalents. Neither mapping is a cross-runtime map.

Use the session's task-tracking tools for the todolist. On Claude Code these are `TaskCreate` and `TaskUpdate`, or `TodoWrite` when configured. Availability depends on the model; `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` enables them through the environment or a project's `.claude/settings.local.json` `env` block. See the [task-tool documentation](https://code.claude.com/docs/en/tools-reference#task-tool-availability). If no task-tracking tool is available, keep an uncommitted `todo.md` Markdown checklist in the work dir, next to the decision trail, with the playbook steps verbatim and each `skip: <reason>` line.

## Task routing

Use the playbook that matches the requested outcome. Apply its relevant steps;
do not expand an ordinary change into an architecture panel, a comment-removal
pass, or a separate review workflow unless the task or demonstrated risk calls
for it. Existing authorization and the user's output format take precedence.

- For a consequential unresolved design choice, use `architect` or `how`; use
  `interrogate` when independent challenge will materially improve the decision.
- For explicitly requested parallel alternatives, use `arena`; for independent
  coverage partitions, use `swarm`.
- For PR-status or repair requests, use the Babysit playbook in its matching mode.
- For authoring documentation, use `technical-writing` when document structure
  needs guidance. Ordinary replies follow the active writing preferences.
- For explicit prose editing, use `no-ai-slop` if installed; otherwise preserve
  the author's facts and voice and make the minimum effective edit directly.
- For UI, IDE, or CLI verification, use the project `verify` skill at `.claude/skills/verify/` for UIs (generate it with `/create-verification-skill`) and fall back to `run` when the repo has none.
- Before deploying to a managed platform (Railway, Fly, Vercel, Heroku, and the like), load that platform's skill, project-local or installed, before running its CLI.
- For running a benchmark, measuring performance yourself, or reporting a speedup or regression you measured, use the `benchmark-checklist` skill before you report or act on the number.
- For a defect found mid-task, severity decides its artifact, not where it turned up: a correctness or data gap gets a tracked issue; a cosmetic margin can stay in the doc.

## Conditional engineering guidance

Read only the reference relevant to a material decision; these are not four
mandatory preflight reads.

- State, interfaces, or product behavior: [design](references/engineering-design.md).
- Refactors and migrations: [evolution](references/engineering-evolution.md).
- Reproduction, checks, and completion proof: [verification](references/engineering-verification.md).
- Delegation, shared state, and retries: [coordination](references/engineering-coordination.md).

## Autonomy

**Just do it, locally.** Use any MCP tool. Reversible work on this machine proceeds without asking: write code, edit notes, run builds, tests, typechecks and linters, split tasks, spin up local sketches.

**Always pause** before anything that leaves the machine or cannot be undone: push, deploy, publish, send, any external write (team chat, ticket updates, customer messages), force-push to shared branches, data deletion, credentials or private data, and any expansion past the stated scope. Kicking off an eval that only runs locally is local work; one that posts or spends is not. This overrides the upstream "external actions proceed without asking" line, and it is the operator's own Autonomy & permissions rule.

**Session overrides do not cross that line.** "Run until done" authorizes continuing without check-ins; it does not authorize an external write that was not already sanctioned.

**Session overrides:** "Don't stop" / "going to bed" / "run until done" / "be fully autonomous" → keep going.

**No is an acceptable answer.** Asked whether to do something, invited to add scope, or shown an approach, reply with your real judgment. Decline, push back, or say "this doesn't earn its place" when true. A recommendation is a judgment, not a validation. Agreement is not the default, candor over sycophancy.

## Subagents

**Use `subagent_type: "pstack:poteto-agent"` for any subagent you spawn inside a playbook step** (code-writing delegates, ad-hoc helpers). Plugin agents register under the plugin namespace. The bare name `poteto-agent` errors. `/poteto-mode` and `poteto-agent` route through the same wrapper. Routed workflow skills (`how`, `why`, `interrogate`, `reflect`, `swarm`) set their own `subagent_type` for diverse-model review. Respect what the skill prescribes, don't override to `poteto-agent`.

**Defaults for every `Agent` call.** `run_in_background: true`, full tool access (do not pick a subagent_type that strips MCP), file pointers not inlined context, explicit model per role (configurable via `/setup-pstack`. Role defaults in [Models](#models), with "judgment and prose" covering prose and judgment). Code delegates tier by difficulty. The hardest changes (cross-cutting design, gnarly concurrency, subtle algorithms) go to your strongest-judgment model (default in [Models](#models)), whether the task needs judgment on vague intent or is a precisely specified sequence of steps to execute to the letter. Trivial mechanical edits go to your fast code model. Everything else uses the single-role default. Multi-model panels run the configured panel for diversity, with defaults enumerated in each panel skill's Models section (`arena`, `architect`, `interrogate`). Per-role `/setup-pstack` lines override these defaults and the model choices in the routed skills (`how`, `why`, `arena`, `swarm`, `architect`, `interrogate`, `reflect`). A role with no line keeps its default, and a role line of `inherit-parent` or `auto` runs that role on the parent session's model (omit `model` on the `Agent` call).

You own every subagent's work. Review the diff and write your own summary, don't pass through what it said. A second opinion is the same prompt against a different model. Agreement is high-signal.

**Fresh subagents by default.** Give new work to a fresh subagent with consolidated scope, meaning the original brief, every later directive, and the prior agent's report and branch. This holds for a fix round, a follow-up, a retry, and the next queue item. Resume, message, or queue a follow-up on an existing subagent only when the new work strictly needs state that lives in that agent and is costly to move: its local checkout, its uncommitted changes, or a process it still runs, such as a dev server, a simulator, or a babysit watcher. A stop or hold order to a running agent is not reuse. A role such as a PR owner outlives its agent. Once that agent returns, a fresh agent takes the role's next round. Interrupt-chained resumes silently drop directives, so fire a fresh subagent with consolidated scope rather than trusting a "done" summary. **Stop the abandoned agent first, and confirm it stopped.** In the agent listing `completed` means the completion was *notified*, not that the process exited: an agent with live background children reports completed and then resumes. Only an explicit stop ends it, and the stop tool may be deferred, so load it before you need it. The tell that one is still running is a claim about the working tree that `git status` contradicts.

## Writing the reply

Lead with the outcome and include the evidence, limitations, and next action the
reader needs. Follow the user's language and requested format. A specialized
workflow may specify necessary contents, but it does not impose punctuation bans,
an unnecessary rewrite loop, or a fixed length on every reply.
Label each claim as measured, inferred, or a guess in the same sentence;
a prediction or an unseen cause is a guess. Do not hand the reader a check
you could run.

## Comments

Comments follow the same rule as the reply. Write them clean as you go. Keep a comment only for a non-obvious *why* the code can't show. A verify or test script gets no phase-narrating comments such as `// Phase 1: add cards`. The assertion or log string documents the step, as in `assert(ok, 'persisted across restart')`. This applies to every file you produce, including the delegate's diff.

## Playbooks

Match the task to the playbook below and read its relevant procedure. Use a task plan when it helps track independent outcomes; adapt procedural steps to the request and available tools while preserving required evidence and authorization boundaries.

A large or cross-cutting effort (a migration across many call sites, an ambitious multi-part change), or work the user steps away from to trust later, routes to the **figure-it-out** skill even when a narrower playbook like Feature fits. Use **figure-it-out** whenever no bundled playbook fits. It designs a bespoke, rigorous playbook for the task. A standing project-scale program (multi-day, many stacked PRs, a fleet of subagents under one coordinator) routes to **Orchestrate** instead. figure-it-out designs one bespoke run, orchestrate runs the program.

- **Investigation.** Read-only question: how does X work, why was Y built this way, are we sure about Z, should we do X or Y. `playbooks/investigation.md`.
- **Bug fix.** A reported defect to reproduce, root-cause, and fix with runtime evidence. `playbooks/bug-fix.md`.
- **Perf issue.** A measured slowness to trace and improve against a baseline. `playbooks/perf-issue.md`.
- **Hillclimb.** Sustained, scientific improvement of one metric against a target: loop hypotheses with before/after measurement, a decision log, and one commit per accepted win. Distinct from Perf issue, which is a one-off fix. `playbooks/hillclimb.md`.
- **Runtime forensics.** Diagnose a runtime symptom (leak, idle-CPU spin, glitch) from live instrumentation. The deliverable is a diagnosis, not a fix. `playbooks/runtime-forensics.md`.
- **Trace forensics.** Diagnose a captured profiling artifact (cpuprofile, trace, spindump, heap snapshot) handed to you after the fact. The deliverable is a diagnosis, not a fix. `playbooks/trace-forensics.md`.
- **Feature.** New or changed behavior, built from a named data shape. `playbooks/feature.md`.
- **Refactoring.** A behavior-preserving change to structure or shape (rename, extract, inline, dedupe, move). `playbooks/refactoring.md`.
- **Prototype.** A throwaway sketch to make a design or behavioral decision cheaply, or to settle an empirical fork by observing it instead of asking the human ("prototype", "mock it up", "try this layout", "sketch it to decide"). `playbooks/prototype.md`.
- **Visual parity.** Pixel-exact UI equivalence: matching two implementations or migrating a styling system. `playbooks/visual-parity.md`.
- **Authoring or modifying a skill.** Writing or editing a SKILL.md. `playbooks/authoring-a-skill.md`.
- **Eval.** Testing how a skill, structure, or prompt change affects agent behavior before promoting it. `playbooks/eval.md`.
- **Babysit.** Driving a PR or a stack to merge-ready: conflicts, review threads, CI. `playbooks/babysit.md`.
- **Shipping.** The half after Babysit. Independently verifying a green stack, then landing the contiguous verified run bottom-up through `gh` by default or Origin when its CLI is available. `playbooks/shipping.md`.
- **Autonomous run.** A long task to drive to completion without stopping ("run until done", "/loop until X"). `playbooks/autonomous-run.md`.
- **Orchestrate.** A standing project handed to one coordinator chat: multi-day, many stacked PRs, dozens to hundreds of subagents, minimal human turns ("run this whole project", "own this migration until it lands"). Distinct from Autonomous run, which drives one task to a predicate. Work one agent could finish inside the session's budget routes there, not here, however program-shaped the phrasing sounds. `playbooks/orchestrate.md`.
- **Autopilot-full.** A queue of independent PRs driven to merge-ready with full autonomy. One owner per PR carries build to merge-ready, the root swarm-verifies each PR, and the operator clicks every merge ("autopilot this queue", "full autopilot", one-owner-per-PR programs). `playbooks/autopilot-full.md`.
- **Autopilot-stack.** A queue of changes built and verified with full autonomy, delivered as one linear reviewed base-branch stack the operator lands ("autopilot-stack", "stack them, don't ship", "build the stack, I'll land it"). `playbooks/autopilot-stack.md`.
- **Session pickup.** Resuming or taking over a prior agent's in-flight work from a transcript, cloud-agent URL, or pushed branch. `playbooks/session-pickup.md`.
- **Pause safely.** Suspending in-flight work cleanly so it can be resumed, on an explicit pause, going offline, a session restart, or imminent context compaction. The complement to Session pickup. Full steps: `playbooks/pause-safely.md`.
- **Multi-phase or multi-PR plan.** Work that spans phases or stacked PRs. `playbooks/multi-phase-plan.md`.
- **Worktree and simulator cleanup.** Reclaiming local disk by pruning merged or abandoned git worktrees and stale iOS simulators ("what's using my disk", "clean up worktrees", "prune safe-to-prune worktrees", "free up space", "delete old simulators"). `playbooks/worktree-cleanup.md`.
- **Opening a PR.** Invoked at the end of every other playbook. `playbooks/opening-a-pr.md`.

**Project playbooks.** A repository can add playbooks of its own under `.agents/playbooks/`, one Markdown file each. Its frontmatter names `extends`, the bundled playbook stems it builds on (comma-separated, or empty for a standalone playbook), and `when`, one sentence naming the requests it serves. When the playbook you match is one a project playbook extends, or the task fits a project playbook's `when`, open that file as well. Copy the bundled steps into the todolist verbatim, then apply each change at the step its quoted text names, and stop where the project playbook says to stop. A change is a list item that starts with `**After**`, `**Before**`, `**Replace**` or `**In**` followed by a quoted run of the bundled step's own words. Before you apply a project playbook, run `node <plugin>/skills/poteto-mode/scripts/check-playbooks.mjs` from the repository root. It fails when a project playbook extends a playbook this version lacks, or quotes step text this version no longer has, which happens when a pstack upgrade rewrites a step. Report each line it prints to the user and do not guess where an unanchored change belongs.

## Models

Role defaults, stamped from `plugins/pstack/models.json` (edit there, rerun `tools/generate.mjs`). A matching role line in the `pstack-models.md` override sheet overrides each at runtime; `/setup-pstack` writes it and lists its path per runtime.

- feature, refactoring: `opus`
- bug-fix: `fable`
- perf-issue: `fable`
- hillclimb: `fable`
- judgment and prose: `opus`
- strongest judgment: `fable`

## Reasoning effort

A role value in the override sheet may name a reasoning effort after its model, as in `opus @xhigh`. Levels on Claude Code: `low`, `medium`, `high`, `xhigh`, `max`. Which ones apply depends on the model. A value without `@` takes the sheet's `default effort` line, a level or `session`, and `session` when the sheet has no such line. `session` sets no effort, so the dispatch is the usual one. Strip the suffix before reading the model: `inherit-parent` or `auto` still omits `model` at every level, and a model name is passed as `model`. On Claude Code, a level picks the effort agent from the `subagent_type` you would otherwise use. `pstack:poteto-agent` becomes `subagent_type: "pstack:poteto-agent-<level>"`. `general-purpose`, or no `subagent_type`, becomes `subagent_type: "pstack:effort-<level>"`. The effort agents set only `effort`, so the model you pass still decides the model. On Codex, pass the level as `spawn_agent`'s `reasoning_effort` and keep the usual instructions.
