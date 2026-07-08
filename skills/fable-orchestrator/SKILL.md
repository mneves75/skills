---
name: fable-orchestrator
description: Model-routing policy — Fable advises, plans, decomposes, and reviews; Opus subagents execute frontend tasks; Codex (GPT-5.5 xhigh via /codex:rescue) executes heavy implementation; skill + /goal drives long-horizon work. Use when starting any non-trivial task, deciding who should execute work, delegating implementation, or when the user says "delegate", "orchestrate", "use codex", "heavy task", or "long-running task".
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
| Heavy executor | **Codex via `/codex:rescue`** | Heavy implementation, debugging, test fixing, refactoring, multi-file edits |
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

**Codex gets** (via `/codex:rescue`): implementation from a frozen spec, bug fixes with
known repro, test writing/fixing, mechanical migrations, multi-file refactors, CI fixes.
- Prefer **GPT-5.5 at xhigh**: pass `--model gpt-5.5 --effort xhigh` (this skill counts as
  the explicit user request the rescue agent waits for).
- Keep each Codex task **focused and specific** — one goal per dispatch, not a grab-bag.
- Use `--background` for open-ended/long runs; `--resume` for follow-up fixes (cheaper
  than fresh runs, keeps Codex context).
- Codex subagents (`codex:codex-rescue` agent type) may be used when the plugin routes
  through them; the skill's routing rules still apply.

**Long-horizon** (multi-phase, "don't stop until done"): invoke the `supergoal` skill —
it plans phases and emits a single `/goal` command with retry + verification built in.
Goals beat ad-hoc loops for anything spanning many phases or hours.

## Delegation contract (every dispatch)

Executors start with zero session context. Every prompt must carry:
1. Goal (one sentence) + acceptance criteria
2. Exact repo + key file paths
3. Constraints ("don't touch X") and non-goals
4. Proof expected (exact test/build command)
5. Output shape ("report files changed + test output")

Carve out file ownership so parallel diffs never collide (e.g. Codex owns backend,
Opus subagent owns frontend, Fable owns specs).

## Verify (Fable, always)

After ANY executor finishes — **inspect before accepting. Never blindly trust output.**
1. `git status -sb` + read the full diff; judge it like a contributor PR
2. Run the focused tests/build yourself, or demand proof output — executor claims are advisory
3. Wrong result → iterate via `--resume` (Codex) or `SendMessage` (subagent) with a
   corrective spec; after 2 failed rounds, Fable takes over and does it directly
4. Normal closeout still applies (autoreview/verify before ship)

## Economics

Win = generation + exploration tokens moved off Fable; Fable spends only on spec + diff
review. Don't ping-pong trivia through delegation; don't re-read what an executor already
summarized correctly (spot-check instead).

## Reference

Deeper Codex invocation patterns (raw `codex exec`, temp-file prompts, resume mechanics):
[codex-first SKILL.md](https://github.com/steipete/agent-scripts/blob/main/skills/codex-first/SKILL.md)
(local: `~/dev/steipete/agent-scripts/skills/codex-first/SKILL.md`). Use raw `codex exec`
only when `/codex:rescue` is unavailable.
