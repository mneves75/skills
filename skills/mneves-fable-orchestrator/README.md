# Fable Orchestrator

Model-routing policy for sessions that can use a main agent, Codex, and subagents.

## The idea

Delegate only when the work is independent, substantial, and objectively verifiable:

| Role | Who | What |
|------|-----|------|
| Orchestrator | Main session (Claude or Codex; model per the skill's Defaults block) | Repo understanding, architecture decisions, task decomposition, spec writing, acceptance |
| Frontend executor | Frontend subagents (model per the Defaults block) | UI components, styling, layout, visual polish |
| Heavy executor | Codex via `codex exec` / `codex-lane` (model per the Defaults block) | Execution, debugging, refactors, and other non-frontend work |
| Advisor / reviewer | `autoreview` or a read-only Codex run (model per the Defaults block) | Decision advice with real downside; independent review of a fixed Git target |
| Long-horizon driver | A lane, a checked-in plan file, or your harness's long-task mechanism | User-requested multi-phase work driven to its stopping condition |

## Continuity is the whole game

The expensive mistake in agentic delegation isn't picking the wrong model. It's throwing
away what the executor already worked out. A bare `codex exec` starts a fresh thread every
time, so round 2 of a job loses round 1's private reasoning and re-pays the full
instruction preamble uncached.

OpenAI measured the same effect on ARC-AGI-3: a harness that discarded reasoning between
actions and used rolling truncation scored 13.3% RHAE; retaining reasoning and enabling
compaction scored **38.3% with 6× fewer output tokens**
([writeup](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores/)).

So the skill's hard rule is: **one round is an exec, two rounds is a lane.**
`tools/codex-lane` is a small wrapper that names a Codex thread and resumes it, so
follow-ups continue the executor's thinking instead of restarting it.

```bash
codex-lane start api-rls /tmp/spec.md -- -s workspace-write
codex-lane next  api-rls "fix the failing gate"   # literal text, or `-` to pipe stdin
codex-lane last  api-rls          # final message | also: log / id / list / drop
codex-lane fork  api-rls api-rls-b "try the trigger-based approach instead"   # A/B from the same state
```

Long prompts must go in via stdin (`codex-lane next api-rls - < build.log`):
the prompt argument is always literal text, so a pasted build log or review
report arrives on stdin, never as an argv-sized inline string.

If a job you dispatched as a plain `codex exec` turns out to need a second round, wrap its
thread instead of re-specifying it: `codex-lane adopt api-rls <thread-id> [cwd]`.

### Lane mechanics

- `codex-lane` needs `codex`, `bash`, `python3` (lane state is JSON), `awk`, and `mktemp` on
  `PATH`; it refuses to run without `codex` or `python3` so a job can never lose its thread id.
- Lane names are filenames: `[A-Za-z0-9._-]`, no leading `-` or `.`.
- `log` and `id` print the events-file path and the thread id, not the transcript; `last` prints
  the final message. Each `next` also keeps codex's stderr as `<lane>.<stamp>.stderr.log` beside
  the events and relays it when the run ends.
- One writer per lane: a `<lane>.lock` directory in `$CODEX_LANE_DIR` serializes runs. If a run
  died holding it, the error names the directory to `rmdir`.
- After `--`, the wrapper rejects `-C`/`--cd` (a lane is bound to its workspace) and `--json`,
  `-o`/`--output-last-message`, `--ephemeral` (it owns the event stream and last-message file,
  and an ephemeral thread cannot be resumed).
- The wrapper stores launch arguments, never environment: set `CODEX_HOME` (or any other
  environment) on every `start`, `next`, and `adopt` for that lane.
- If the backend refuses to resume a long thread (`thread/resume failed` on stderr), `next` exits
  non-zero, says so on stderr, and withholds the stale previous message; start a fresh lane with
  a self-contained order. Only stderr is consulted: the event stream is the model's own output.
- The binding is flag-level: `-C` is refused, but a `-c` override given at `start` can still
  change policy, so choose start arguments deliberately. Stored args are re-validated on every
  `next`, so a hand-edited state file cannot smuggle in a refused flag.
- Artifacts are never pruned; after `drop`, delete `$CODEX_LANE_DIR/<lane>.*` yourself. A lane
  directory that grants other users any access is refused.
- `fork <lane> <new-lane> <prompt|->` branches the thread (`codex exec fork`) into a new lane with
  the same cwd and policy; the source lane is never written. Compare the two lanes' diffs on the
  same evidence, keep one, `drop` the other.

A lane is bound to one workspace **and** one execution policy. `codex exec resume` rebuilds
its config from the current invocation, not from the thread, so the wrapper stores what
`start` ran under and replays it on every `next`: the lane runs in its own directory
(recorded as the physical path, `pwd -P`, so a symlinked entry point can't move it;
`-C`/`--cd` is rejected) with the same sandbox, model, and reasoning settings. Without
that, a lane started `-s workspace-write` would resume under the machine default and
quietly lose write access. There is no per-turn override: `next` takes only
`<lane> <prompt|->` and rejects trailing args.

Everything after `--` is passed through to `codex`, so the sandbox level is your call
(`-s read-only` to investigate, `-s workspace-write` to implement). Lane state lives in
`$CODEX_LANE_DIR` (default `~/.codex/lanes`), created mode `700`; the event logs hold
the full model transcript for the job.

## Requirements

- **Claude Code** with subagent support (`Agent` tool), or any harness that can spawn a
  fresh-context worker
- **[Codex CLI](https://github.com/openai/codex)** installed and authenticated, for the
  heavy-executor path, plus `bash` and `python3` for `codex-lane`. The `/codex:rescue` command
  from the openai-codex plugin is an equivalent front-end if you have that plugin; the routing
  rules apply either way. Set the shared Codex default from the skill's Defaults block. Preserve
  deliberate per-call specialist overrides. See `references/codex-dispatch.md` for flag
  placement, failure classes, and the optional (not shipped) `codex-auto` launcher.
- **Goal workflow**: optional; use the goal mechanism exposed by the active agent runtime

Install the lane wrapper by symlinking it onto your `PATH`:

```bash
ln -s /path/to/skills/skills/mneves-fable-orchestrator/tools/codex-lane ~/bin/codex-lane
```

## Key rules

1. **The main session owns acceptance.** Executor claims remain advisory until checked.
2. **Every dispatch is a self-contained work order**: goal, exact paths, constraints,
   non-goals, proof expected, output shape. Executors start with zero session context.
3. **Multi-round work runs in a lane.** Fix-ups and review findings go to
   `codex-lane next`, never a fresh spec that restates solved reasoning.
4. **File ownership is carved out per executor** so parallel diffs never collide.
5. **Independent review is risk-based.** Use it when the task or repository requires it.
6. **Small direct edits stay in the active session.**

## Install

```bash
npx skills@latest add mneves75/skills --skill mneves-fable-orchestrator
```

That links the skill where Claude Code (`~/.claude/skills`) and Codex (`~/.agents/skills`,
also `.agents/skills` inside a repository) discover skills. Or clone the collection:

```bash
git clone https://github.com/mneves75/skills.git ~/.claude/skills/mneves-skills
```

Or symlink just this skill:

```bash
ln -s /path/to/skills/skills/mneves-fable-orchestrator ~/.claude/skills/mneves-fable-orchestrator
```

## Credits

Routing philosophy and Codex invocation patterns adapted from
[steipete/agent-scripts codex-first](https://github.com/steipete/agent-scripts/blob/main/skills/codex-first/SKILL.md).
Continuity rationale from OpenAI's
[ARC-AGI-3 harness writeup](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores/).
