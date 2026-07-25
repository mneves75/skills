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
| Heavy executor | Codex (GPT-5.5 xhigh via `/codex:rescue`) | Heavy implementation, debugging, test fixing, multi-file refactors |
| Long-horizon driver | `supergoal` skill + `/goal` | Multi-phase work driven to completion without babysitting |

## Requirements

- **Claude Code** with subagent support (`Agent` tool)
- **[openai-codex plugin](https://github.com/openai/codex)** providing `/codex:rescue`,
  with Codex CLI installed and authenticated — for the heavy-executor path
- **`supergoal` skill** — optional, for the long-horizon path

Without the Codex plugin, the skill falls back to raw `codex exec` patterns documented in
[steipete's codex-first skill](https://github.com/steipete/agent-scripts/blob/main/skills/codex-first/SKILL.md).

## Key rules

1. **Fable never delegates review.** Every executor's diff is read in full and judged
   like a contributor PR; executor claims are advisory until proven.
2. **Every dispatch is a self-contained work order**: goal, exact paths, constraints,
   non-goals, proof expected, output shape. Executors start with zero session context.
3. **File ownership is carved out per executor** so parallel diffs never collide.
4. **Two failed correction rounds → Fable takes over** and does the work directly.
5. **Tiny edits stay in Fable** — delegation overhead loses below ~20 lines.

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
[steipete/agent-scripts — codex-first](https://github.com/steipete/agent-scripts/blob/main/skills/codex-first/SKILL.md).
