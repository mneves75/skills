---
name: poteto-mode
description: "Use the pstack engineering workflow playbooks when the user types /poteto-mode or asks for poteto mode."
---

# Poteto mode

When another operator mode is active (for example, mneves-mode), that mode selects the skills, gates and playbook. Use a poteto playbook only for a step that mode's playbook does not cover. When both modes set a gate, apply the stricter one.

Bundled skills live at `../<name>/SKILL.md` from this file, so put this file's absolute path in every `poteto-agent` prompt.

## Platform Adaptation

These skills use Claude Code tool names (the `Skill` tool, the `Agent` tool, `AskUserQuestion`) and the Claude model names the `Agent` tool accepts, as each Models section lists them. On Claude Code they work as written. On Codex, read [`references/codex-tools.md`](references/codex-tools.md) for the Codex equivalent of a Claude tool, model, or skill named by these workflows. On Pi, read [`references/pi-tools.md`](references/pi-tools.md) instead. On GitHub Copilot, read [`references/copilot-tools.md`](references/copilot-tools.md) instead. On Muse, read [`references/muse-tools.md`](references/muse-tools.md) instead. On MiniMax Code, read [`references/minimax-tools.md`](references/minimax-tools.md) instead. On Antigravity, read [`references/agy-tools.md`](references/agy-tools.md) instead. On OMP, read [`references/omp-tools.md`](references/omp-tools.md) instead. On Kimi Code CLI, read [`references/kimi-tools.md`](references/kimi-tools.md) instead. On Grok Build, read [`references/grok.md`](references/grok.md) instead. On OpenCode 2, read [`references/opencode-tools.md`](references/opencode-tools.md) instead. Other runtimes can discover the same Agent Skills tree, but they must use their own tool, model, and configuration equivalents. No one of these mappings is a cross-runtime map.

Use the session's task-tracking tools for the todolist. On Claude Code these are `TaskCreate` and `TaskUpdate`, or `TodoWrite` when configured. Availability depends on the model; `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` enables them through the environment or a project's `.claude/settings.local.json` `env` block. See the [task-tool documentation](https://code.claude.com/docs/en/tools-reference#task-tool-availability). If no task-tracking tool is available, keep an uncommitted `todo.md` Markdown checklist in the work dir, next to the decision trail, with the playbook steps verbatim and each `skip: <reason>` line. When several sessions share the checkout, name it `.audit/<task-slug>.todo.md`, beside that session's `.audit/<task-slug>.tsv` trail, so they never write one file. In the Claude desktop app, `mcp__ccd_turn__update_plan` asks for items of about seven words. Give it that short plan, and keep this checklist as well, with the playbook steps verbatim and each `skip: <reason>` line.

## Task routing

Use the playbook that matches the requested outcome. Apply its relevant steps;
do not expand an ordinary change into an architecture panel, a comment-removal
pass, or a separate review workflow unless the task or demonstrated risk calls
for it. Existing authorization and the user's output format take precedence.

- First message → restate the user's goal and the smallest change that meets it, then proceed. Open each subagent brief, PR `## Why`, and final report with the goal.
- Starting any agent, whether an `Agent` subagent or a background worker → the first line of its kickoff is `Read <path>/worker.md before anything else.`, with `<path>` the absolute path of this skill's folder. The operator's rules live in skills that only load from a slash command, so they reach another agent no other way. Keep the rest of the kickoff to the goal and the task, plus this file's absolute path for a `poteto-agent`.
- A fork you could settle by running something → prototype it per `playbooks/prototype.md` instead of asking.
- For a consequential unresolved design choice across a function boundary → **architect** (for Bug fix only, check the [focused-fix exception](playbooks/bug-fix.md#focused-fix-exception) first); for explicitly requested parallel alternatives → **arena**; for independent coverage partitions → **swarm**; when independent challenge will materially improve a contested decision → **interrogate**.
- For authoring documentation, PR descriptions, or commit messages → **technical-writing** when document structure needs guidance. Ordinary replies follow the active writing preferences.
- For explicit prose editing → preserve the author's facts and voice and make the minimum effective edit directly.
- Before commit → `/deslop` when appropriate. Before review → **no-comments** when requested or warranted.
- For UI, IDE, or CLI verification → the driver skill. `run` ships with Claude Code and the model can invoke it for CLIs, TUIs, servers, and browser or Electron apps. For UIs use the project `verify` skill at `.claude/skills/verify/` (generate it with `/create-verification-skill`) and fall back to `run` when the repo has none.
- A number you measured → **benchmark-checklist** before reporting or acting on it.
- PR status → the **Babysit** playbook, not the bundled **babysit** skill. Landing a green stack → the **Shipping** playbook.
- Bot review comments → judge each on its merits, per [`bugbot-triage.md`](references/bugbot-triage.md).
- Deploying to a managed platform (Railway, Fly, Vercel, Heroku, and the like) → load that platform's skill, project-local or installed, before running its CLI, the same way Shipping step 1 resolves the forge before the first PR operation.
- A defect found mid-task → severity decides its artifact, not where it turned up. A correctness or data gap gets a tracked issue even when it surfaces while writing a closure doc; a cosmetic margin can stay in the doc.
- Long or unattended work → **show-me-your-work**.

## Conditional engineering guidance

Read only the reference relevant to a material decision; these are not four
mandatory preflight reads.

- State, interfaces, or product behavior: [design](references/engineering-design.md).
- Refactors and migrations: [evolution](references/engineering-evolution.md).
- Reproduction, checks, and completion proof: [verification](references/engineering-verification.md).
- Delegation, shared state, and retries: [coordination](references/engineering-coordination.md).

## Autonomy

**Just do it, locally.** Use any MCP tool. Reversible work on this machine proceeds without asking: write code, edit notes, run builds, tests, typechecks and linters, split tasks, spin up local sketches.

**Always pause** before anything that leaves the machine or cannot be undone: push, deploy, publish, send, any external write (team chat, ticket updates, customer messages), force-push to shared branches, data deletion, credentials or private data, and any expansion past the stated scope. Kicking off an eval that only runs locally is local work; one that posts or spends is not. This is the operator's own Autonomy & permissions rule, and it wins over any pstack text that lets external actions proceed without asking.

**Session overrides do not cross that line.** "Run until done" authorizes continuing without check-ins; it does not authorize an external write that was not already sanctioned.

**Session overrides:** "Don't stop" / "going to bed" / "run until done" / "be fully autonomous" → keep going.

**No is an acceptable answer.** Asked whether to do something, invited to add scope, or shown an approach, reply with your real judgment. Decline, push back, or say "this doesn't earn its place" when true. A recommendation is a judgment, not a validation. Agreement is not the default, candor over sycophancy.

## Subagents

**Use `subagent_type: "pstack:poteto-agent"` for any subagent you spawn directly inside a playbook step.** Plugin agents register under the plugin namespace. The bare name `poteto-agent` errors. A skills-only install has no `pstack:*` agent types: use `general-purpose` and tell the subagent to read this skill in full first. The chat that receives `/poteto-mode` runs the playbook itself. Routed workflow skills (`interrogate`, `swarm`) set their own `subagent_type`. Respect it.

**Defaults for every `Agent` call.** `run_in_background: true`, full tool access (do not pick a subagent_type that strips MCP), file pointers not inlined context, and an explicit model per role, background workers included. `/setup-pstack` writes `pstack-models.md`, whose per-role lines override the defaults below and the role models in the routed skills (`arena`, `swarm`, `interrogate`). A role with no line keeps its default. A line of `inherit-parent` or `auto` runs the role on the parent model, so omit `model` on the `Agent` call. `poteto-agent` sets no model of its own, so it then runs on the parent model. Each code playbook reads its own line (`feature, refactoring`, `bug-fix`, `perf-issue`, or `hillclimb`), prose and judgment read `judgment and prose`, and trivial mechanical edits read `swarm workers`.

Role defaults for code, prose, judgment, trivial mechanical edits, and the diverse review and design panels are in [Models](#models).

**The `strongest judgment` model is an exception.** It runs outside a panel only when the user named it for this task or two xhigh runs of the same brief on the task's own role model failed their check. Say which. Difficulty alone never qualifies.

**Match the model to the job.** Start from the role's line or default, keep its family, and set the level the job needs. The role's `@level`, or the sheet's `default effort` line, sets its starting level, and `session` starts from the session's level. A value without `@` that resolves to an Opus model runs at `medium` and is never raised or lowered for the job. Panel seats keep their listed level. Raise any other role one step, up to xhigh, for the hardest or subtlest work, lower it one step for judgment, and two or more steps for routine work. No role runs above xhigh unless the sheet sets a higher level on the role's line or the `default effort` line. Verification always runs on the `swarm workers` model (default in the **swarm** skill's Models section). If the `Agent` tool rejects a slug, never pass it again. Fall back to the role's line or default, then the calling skill's fallback, then the closest valid slug of the same family, then omit `model`. Say so.

You own every subagent's work. Review the diff and write your own summary. A second opinion is the same prompt on a model from another family.

**Fresh subagents by default.** Give a fix round, a follow-up, a retry, or the next queue item to a fresh subagent with the original brief, every later directive, and the prior agent's report and branch. Resume an existing subagent only when the work needs state that lives in it and is costly to move: its checkout, its uncommitted changes, or a process it still runs. **Stop the abandoned agent first, and confirm it stopped.** In the agent listing `completed` means the completion was *notified*, not that the process exited: an agent with live background children reports completed and then resumes. Only an explicit stop ends it, and the stop tool may be deferred, so load it before you need it. The tell that one is still running is a claim about the working tree that `git status` contradicts.

**A review gate stays closed when no independent reviewer can run.** An agent limit, subagent dispatch turned off, or a skills-only install can leave a required review with no reviewer. Keep the results of reviewers already dispatched. As the one exception to fresh subagents, reuse a finished reviewer only through the runtime's own follow-up action, only if it did not write the change, and only with the full current brief and head revision. A reused reviewer counts once. Never count your own review, passing tests, or CI as the independent verdict. Record `BLOCKED: independent review` in the todolist, keep merge-ready and shipping closed, and report which reviewers ran and which are missing. Work that doesn't depend on the review continues. A fan-out skill run only to explore may fall back to one labelled sequential pass.

## Writing the reply

Lead with the outcome and include the evidence, limitations, and next action the
reader needs. Follow the user's language and requested format. A specialized
workflow may specify necessary contents, but it does not impose punctuation bans,
an unnecessary rewrite loop, or a fixed length on every reply.
Label each claim as measured, inferred, or a guess in the same sentence;
a prediction or an unseen cause is a guess. Do not hand the reader a check
you could run.

## Playbooks

Match the task to a playbook and open its steps at `playbooks/<title>.md`, with the title in kebab case. Copy its steps into the todolist tool first. A step you choose not to do stays in the list with a one-line `skip: <reason>`. Large, cross-cutting, or unattended work, or a task no playbook fits, routes to the **figure-it-out** skill.

Investigation, Bug fix, Perf issue, Hillclimb, Runtime forensics, Trace forensics, Feature, Refactoring, Prototype, Visual parity, Authoring a skill, Eval, Babysit, Shipping, Autonomous run, Autopilot-full, Autopilot-stack, Session pickup, Pause safely, Multi-phase plan, Worktree cleanup, Opening a PR.

**Project playbooks.** A repository can add playbooks of its own under `.agents/playbooks/`, one Markdown file each. Playbooks under `~/.agents/playbooks/` take the same form and apply in every repository; when playbooks from both folders fit, apply the home folder's changes first. Each file's frontmatter names `extends`, the bundled playbook stems it builds on (comma-separated, or empty for a standalone playbook), and `when`, one sentence naming the requests it serves. When the playbook you match is one a project playbook extends, or the task fits a project playbook's `when`, open that file as well. Copy the bundled steps into the todolist verbatim, then apply each change at the step its quoted text names, and stop where the project playbook says to stop. A change is a list item that starts with `**After**`, `**Before**`, `**Replace**` or `**In**` followed by a quoted run of the bundled step's own words. In a playbook with no numbered steps, each paragraph and each list item is a step. Before you apply a project playbook, run `node <plugin>/skills/poteto-mode/scripts/check-playbooks.mjs` from the repository root. It checks both folders and fails when a project playbook extends a playbook this version lacks, or quotes step text this version no longer has, which happens when a pstack upgrade rewrites a step. Report each line it prints to the user and do not guess where an unanchored change belongs.

## Models

Role defaults, stamped from `plugins/pstack/models.json` (edit there, rerun `tools/generate.mjs`). A matching role line in the `pstack-models.md` override sheet overrides each at runtime; `/setup-pstack` writes it and lists its path per runtime.

- feature, refactoring: `opus`
- bug-fix: `opus`
- perf-issue: `opus`
- hillclimb: `opus`
- judgment and prose: `opus`
- strongest judgment: `fable`

## Reasoning effort

A role value in the override sheet may name a reasoning effort after its model, as in `opus @xhigh`. Levels on Claude Code: `low`, `medium`, `high`, `xhigh`, `max`. Which ones apply depends on the model. A value without `@` takes the sheet's `default effort` line, a level or `session`, and `xhigh` when the sheet has no such line. A value without `@` that resolves to an Opus model runs at `medium`, whatever that line or a platform mapping says. On Claude Code, `session` sets no effort. On other runtimes, follow the platform mapping for `session`. Strip the suffix before reading the model: `inherit-parent` or `auto` still omits `model` at every level, and a model name is passed as `model`. Pass the level as the dispatch's effort field and keep the `subagent_type` you would otherwise use. That is `effort` on the Claude Code `Agent` call and `reasoning_effort` on Codex's `spawn_agent`. On Codex, pass `model` and `reasoning_effort` only as the platform mapping's schema check allows. On Muse it is `effort` on a Workflow child; a `subagent_spawn` dispatch keeps the session's effort.
