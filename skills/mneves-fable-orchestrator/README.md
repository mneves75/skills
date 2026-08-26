# Fable Orchestrator

Model-routing policy for multi-agent Claude Code sessions: the expensive, high-judgment
model (Fable) advises, plans, and reviews; cheaper or flat-rate executors do the typing.

## The idea

Frontier-model tokens are metered and expensive, and the top model's edge is judgment,
not typing speed. This skill encodes a standing division of labor:

| Role | Who | What |
|------|-----|------|
| Advisor | Fable (main session) | Repo understanding, architecture decisions, task decomposition, spec writing, final review |
| Frontend executor | Opus subagents | UI components, styling, layout, visual polish |
| Heavy executor | Codex (GPT-5.6-sol at `high`, via `codex exec` / `codex-lane`) | Heavy implementation, debugging, test fixing, multi-file refactors |
| Long-horizon driver | `supergoal` skill + `/goal` | Multi-phase work driven to completion without babysitting |

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
```

Long prompts must go in via stdin (`codex-lane next api-rls - < build.log`):
the prompt argument is always literal text, so a pasted build log or review
report arrives on stdin, never as an argv-sized inline string.

If a job you dispatched as a plain `codex exec` turns out to need a second round, wrap its
thread instead of re-specifying it: `codex-lane adopt api-rls <thread-id> [cwd]`.

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

Measured locally (codex-cli 0.146.0, gpt-5.6-sol): fresh exec ≈ 34k input tokens, 0
cached; resume on the same thread ≈ 35k cached with prior reasoning items replayed.

## Requirements

- **Claude Code** with subagent support (`Agent` tool)
- **[Codex CLI](https://github.com/openai/codex)** installed and authenticated, for the
  heavy-executor path. The `/codex:rescue` command from the openai-codex plugin is an
  equivalent front-end if you have that plugin; the routing rules apply either way.
  The wrapper never injects a model, so set the routing default once in
  `~/.codex/config.toml` (`model = "gpt-5.6-sol"`, `model_reasoning_effort = "high"`) and
  pin exceptions per lane with `-- -c model="..."`.
- **`supergoal` skill**: optional, for the long-horizon path

Install the lane wrapper by symlinking it onto your `PATH`:

```bash
ln -s /path/to/skills/skills/mneves-fable-orchestrator/tools/codex-lane ~/bin/codex-lane
```

## Key rules

1. **Fable never delegates review.** Every executor's diff is read in full and judged
   like a contributor PR; executor claims are advisory until proven.
2. **Every dispatch is a self-contained work order**: goal, exact paths, constraints,
   non-goals, proof expected, output shape. Executors start with zero session context.
3. **Multi-round work runs in a lane.** Fix-ups and review findings go to
   `codex-lane next`, never a fresh spec that restates solved reasoning.
4. **File ownership is carved out per executor** so parallel diffs never collide.
5. **Two failed correction rounds → Fable takes over** and does the work directly.
6. **Tiny edits stay in Fable**: delegation overhead loses below ~20 lines.

## Install

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
