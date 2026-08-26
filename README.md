# Skills

![Version](https://img.shields.io/badge/version-1.8.0-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-green)
![CI](https://github.com/mneves75/skills/actions/workflows/ci.yml/badge.svg)
![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-purple)

Production-ready skills for AI coding agents. Tool-agnostic by design.

## Available Skills

| Skill | Description |
|-------|-------------|
| [mneves-eli5](skills/mneves-eli5/) | Feynman-technique explainer calibrated to the listener (child, layperson, executive, junior, expert), answered in the user's language |
| [mneves-agent-readiness](skills/mneves-agent-readiness/) | Evaluate codebase readiness for AI agents (Factory.ai aligned) |
| [mneves-expert-review](skills/mneves-expert-review/) | Expert-panel review and optimization pass before finalizing: objective, first principles, research, hostile panel, 6 alternatives compared on weighted criteria, pre-mortem, five-year test, contrarian steelman, quality audit, improved deliverable |
| [mneves-fable-orchestrator](skills/mneves-fable-orchestrator/) | Model-routing policy: Fable plans and reviews, Opus subagents build frontend, Codex (GPT-5.6-sol high) executes heavy implementation in a resumable lane. Ships [`codex-lane`](skills/mneves-fable-orchestrator/tools/codex-lane) |
| [mneves-teach-back-srs](skills/mneves-teach-back-srs/) | Spaced-repetition learning through codebase teach-back sessions (SM-2 + SQLite) |
| [mneves-verify](skills/mneves-verify/) | Independent verification before done/fixed/shipped: fresh context checks the artifact against criteria, PASS/FAIL/BLOCKED |

## Install

The fastest path is the [skills CLI](https://github.com/vercel-labs/skills) (`npx skills`),
which discovers every `skills/*/SKILL.md` in this repo and links it into the agents you pick
(Claude Code, Codex, OpenCode, Cursor, Cline, Windsurf, Gemini CLI, pi and 70+ more):

```bash
# Interactive: choose skills and agents
npx skills@latest add mneves75/skills

# Everything, all detected agents, no prompts (user-wide install)
npx skills@latest add mneves75/skills --all -g -y

# One skill into one agent
npx skills@latest add mneves75/skills --skill mneves-verify -a claude-code -y

# See what's available / keep up to date / remove
npx skills@latest add mneves75/skills --list
npx skills@latest update
npx skills@latest remove mneves-verify
```

Project-scoped installs (omit `-g`) land in `./.claude/skills/`, `./.agents/skills/`, etc.,
and can be committed with the project.

### Manual (git clone)

Any tool that reads `SKILL.md` folders works with a plain clone:

| Tool | Command |
|------|---------|
| Claude Code | `git clone https://github.com/mneves75/skills.git ~/.claude/skills/mneves-skills` |
| Codex | `git clone https://github.com/mneves75/skills.git ~/.codex/skills/mneves-skills` |
| [pi](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent) | `git clone https://github.com/mneves75/skills.git ~/.pi/agent/skills/mneves-skills` |
| [OpenCode](https://opencode.ai/) | `git clone https://github.com/mneves75/skills.git ~/.config/opencode/skills/mneves-skills` |
| Cursor | `git clone https://github.com/mneves75/skills.git ~/.cursor/skills/mneves-skills` |
| Shared catalog (any tool) | `git clone https://github.com/mneves75/skills.git ~/.agents/skills/mneves-skills` |

Update a clone with `git -C <dir> pull`.

## Readiness check (tool)

`mneves-agent-readiness` ships a Bun + TypeScript assessor with no runtime dependencies.
It assesses the current directory:

```bash
git clone https://github.com/mneves75/skills.git
cd skills/tools && bun install
cd /path/to/your-project
bun --bun /path/to/skills/tools/readiness-check.ts --format=html --output=report.html
```

`--help` lists every option (`--min-level` for CI gates, `--app` for monorepos, `--skip-tests`).

## Benchmark Examples

Real assessments of popular open-source projects. **[View Live Reports →](https://mneves75.github.io/skills/)**

| Project | Language | Level | Score | Report |
|---------|----------|-------|-------|--------|
| FastAPI | Python | L4 | 65.4% | [View](https://mneves75.github.io/skills/fastapi.html) |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Security reports: [SECURITY.md](SECURITY.md).

## License

Apache-2.0

## Acknowledgments

This project is inspired by [Factory.ai](https://factory.ai)'s Code Readiness framework. Factory.ai pioneered the approach of evaluating codebases for AI agent compatibility using structured pillars and maturity levels. Their commercial tool set the standard for what "agent-ready" means.

## Related

- [Anthropic Skills](https://github.com/anthropics/skills) - Official specification
- [pi coding agent](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent) - Open-source coding agent with skills support
- [OpenCode](https://opencode.ai/) - Terminal-based AI coding assistant with skills support
- [OpenSkills](https://github.com/numman-ali/openskills) - Universal skills loader
- [skills CLI](https://github.com/vercel-labs/skills) / [skills.sh](https://skills.sh) - `npx skills` installer and registry
