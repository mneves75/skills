---
name: mneves-fable-orchestrator
description: Model-routing policy — Fable advises, plans, decomposes, and reviews; Opus subagents execute frontend tasks; Codex (GPT-5.6-sol, reasoning high) executes heavy implementation in a resumable lane; skill + /goal drives long-horizon work. Use when starting any non-trivial task, deciding who should execute work, delegating implementation, following up on a delegation, or when the user says "delegate", "orchestrate", "use codex", "heavy task", or "long-running task".
---

# Fable Orchestrator

Division of labor: **Fable thinks, others type.** Fable (this session) is the senior
advisor — expensive, high-judgment. Spend its tokens on understanding, decisions, and
review; move generation and grind to cheaper/flat-rate executors.

## Roles

| Role | Who | What |
|------|-----|------|
| Advisor | **Fable (main session)** | Repo understanding, architecture decisions, task decomposition, spec writing, final review |
| Frontend executor | **Opus subagents** (`Agent` tool, `model: "opus"`) | UI components, styling, layout, visual polish, frontend refactors |
| Heavy executor | **Codex** (`codex exec` / `codex-lane`, GPT-5.6-sol at `high`) | Heavy implementation, debugging, test fixing, refactoring, multi-file edits |
| Long-horizon driver | **`supergoal` skill + `/goal`** | Multi-phase work driven to completion without babysitting |

## Routing

**Fable keeps** (never delegated):
- Design, API/architecture decisions, naming, task decomposition
- Tasks where writing the spec IS the work (ambiguity = design work)
- Tiny edits (<~20 lines, single obvious change) — delegation overhead loses
- Anything needing session tools (MCP, secrets); destructive/irreversible ops, releases, pushes
- **Review of all delegated output — never delegated, never skipped**

**Opus subagents get**: frontend tasks — components, pages, styling, animations, visual
fixes. Spawn via `Agent` with `model: "opus"` and a self-contained brief (files, design
intent, constraints). Parallelize independent frontend tasks in one message.

**Codex gets**: implementation from a frozen spec, bug fixes with known repro, test
writing/fixing, mechanical migrations, multi-file refactors, CI fixes. One goal per
dispatch, not a grab-bag. Default `gpt-5.6-sol` at reasoning `high`; bulk/mechanical
runs (data analysis, migrations) go to `gpt-5.6-terra` at `xhigh`.

The wrapper does not inject a model — it inherits whatever the Codex CLI resolves. Make
that policy real once, in `~/.codex/config.toml`:

```toml
model = "gpt-5.6-sol"
model_reasoning_effort = "high"
```

Then pin the exception per dispatch: `-- -c model="gpt-5.6-terra" -c model_reasoning_effort="xhigh"`.
A pin given to `start` sticks for the whole lane.

**Long-horizon** (multi-phase, "don't stop until done"): invoke the `supergoal` skill —
it plans phases and emits a single `/goal` command with retry + verification built in.
Goals beat ad-hoc loops for anything spanning many phases or hours.

## Continuity: one round is an exec, two rounds is a lane

**A delegation that will take more than one round is a LANE.** A bare `codex exec` opens
a brand-new thread every time. Round 2 therefore loses every private reasoning item from
round 1 and re-pays the whole instruction preamble uncached, so the executor re-derives
the problem from its own diff instead of continuing the plan it already made.

This is the failure mode OpenAI documented on ARC-AGI-3: a harness that discarded
reasoning between actions and used rolling truncation scored 13.3% RHAE, while retaining
reasoning and enabling compaction scored 38.3% with 6× fewer output tokens
([writeup](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores/)).
Measured with codex-cli 0.146.0 / gpt-5.6-sol: a fresh `exec` sends ~34k input tokens
with 0 cached; a `resume` on the same thread serves the preamble from cache (~35k
cached) and replays the stored reasoning items.

Single round — plain exec:

```bash
codex exec -s workspace-write \
  --output-last-message /tmp/codex-result.txt \
  - < /tmp/spec.md > /tmp/codex.log 2>&1
```

Two or more rounds — a named lane (`tools/codex-lane`, state in `~/.codex/lanes/`):

```bash
codex-lane start api-rls /tmp/spec.md -- -s workspace-write
codex-lane next  api-rls "fix the failing gate"   # literal text, or `-` to pipe stdin
codex-lane last  api-rls        # final message  |  also: log / id / list / drop
```

A long prompt (a full build log, a review report) must go in via stdin — the
prompt argument is always literal text, and an inline string still has to fit
the wrapper's own argv:

```bash
codex-lane next api-rls - < /tmp/gate3-failure.log
```

A one-round `codex exec` that turns out to need a round 2 is not a lost cause — wrap its
thread instead of writing a second spec. Restate the flags that exec ran under, since they
can't be recovered from the thread:

```bash
codex-lane adopt api-rls <thread-id> [cwd] -- -s workspace-write
```

A lane is bound to one workspace and one execution policy, because `codex exec resume`
rebuilds its config from the *current* invocation rather than from the thread:

- `next` runs in the directory the lane was started (or adopted) in — recorded as the
  physical path (`pwd -P`), so a symlinked entry point can't make `next` resolve elsewhere.
  Resuming from another repo (or from `$HOME`) therefore can't point the executor at the
  wrong tree. `-C` / `--cd` is rejected.
- the args given to `start` (sandbox, model, reasoning, profile) are stored and replayed on
  every `next` — otherwise a lane started `-s workspace-write` would quietly resume under
  the machine default and be unable to edit. There is no per-turn override: `next` takes
  only `<lane> <prompt|->` and rejects trailing args.
- the model is whatever `~/.codex/config.toml` selects unless pinned at `start`
  (`-- -c model="gpt-5.6-terra"`); the pin then sticks for the whole lane.

Pick the sandbox level deliberately: `-s read-only` for investigation, `-s workspace-write`
for implementation. Reach for `--dangerously-bypass-approvals-and-sandbox` only when the
executor genuinely must run migrations or system commands, and only in a repo you own.

Rules:
- Fix-ups, review findings, failing gates and follow-up questions **all go through
  `next`** on the same thread. Never re-spec what the executor already reasoned through.
- Start a new lane only for a genuinely different job.
- Global flags must precede `resume`: `codex exec resume <id> -s read-only` is a parse
  error; `codex exec -s read-only resume <id>` is correct. `codex-lane` handles the
  ordering — pass extras after a literal `--` to `start` (or `adopt`).
- Don't hand-roll history trimming. Codex compacts rather than truncates
  (`codex features list` → `remote_compaction_v2`); manual trimming on top of it
  reintroduces exactly the loss compaction exists to avoid.

The same principle governs subagents: continue an existing agent with `SendMessage`
rather than spawning a fresh one that re-explores from zero.

## Delegation contract (every dispatch)

Executors start with zero session context. Every prompt must carry:
1. Goal (one sentence) + acceptance criteria
2. Exact repo + key file paths
3. Constraints ("don't touch X") and non-goals
4. Proof expected (exact test/build command)
5. Output shape ("report files changed + test output")

Carve out file ownership so parallel diffs never collide (e.g. Codex owns backend,
Opus subagent owns frontend, Fable owns specs).

If delegation is unavailable, say so — never imply a dispatch happened. Either continue
locally and state that, or hand back the ready-to-run brief.

## Verify (Fable, always)

After ANY executor finishes — **inspect before accepting. Never blindly trust output.**
1. `git status -sb` + read the full diff; judge it like a contributor PR
2. Run the focused tests/build yourself, or demand proof output — executor claims are advisory
3. Wrong result → iterate via `codex-lane next` (Codex) or `SendMessage` (subagent) with a
   corrective prompt; after 2 failed rounds, Fable takes over and does it directly.
   If the job ran as a plain `codex exec` and now needs a round 2, do **not** re-spec it:
   take the thread id from the run's output (or its rollout under `~/.codex/sessions/`) and
   `codex-lane adopt <lane> <thread-id> [cwd]`, then continue with `next`.
4. Normal closeout still applies (autoreview/verify before ship)

## Economics

Win = generation + exploration tokens moved off Fable; Fable spends only on spec + diff
review. Don't ping-pong trivia through delegation; don't re-read what an executor already
summarized correctly (spot-check instead). Lanes compound the win: the preamble is paid
once per job instead of once per round.

## Reference

Deeper Codex invocation patterns (temp-file prompts, background runs, resume mechanics):
[codex-first SKILL.md](https://github.com/steipete/agent-scripts/blob/main/skills/codex-first/SKILL.md).
The `/codex:rescue` command from the openai-codex plugin is an equivalent front-end when
that plugin is installed; the routing and continuity rules above apply either way.
