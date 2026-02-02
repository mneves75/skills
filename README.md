# Skills

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-green)
![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-purple)

Production-ready skills for AI coding agents. Tool-agnostic by design.

## Available Skills

| Skill | Description |
|-------|-------------|
| [agent-readiness](skills/agent-readiness/) | Evaluate codebase readiness for AI agents (Factory.ai aligned) |
| [teach-back-srs](skills/teach-back-srs/) | Spaced-repetition learning through codebase teach-back sessions (SM-2 + SQLite) |

## Quick Start

```bash
# Install skill
git clone https://github.com/mneves75/skills.git ~/.claude/skills/mneves-skills

# Run assessment
cd your-project
readiness-check
```

## Installation

### [pi](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent)

```bash
git clone https://github.com/mneves75/skills.git ~/.pi/agent/skills/mneves-skills
```

### [OpenCode](https://opencode.ai/)

```bash
git clone https://github.com/mneves75/skills.git ~/.config/opencode/skills/mneves-skills
```

### Claude Code

```bash
git clone https://github.com/mneves75/skills.git ~/.claude/skills/mneves-skills
```

### Cursor

```bash
git clone https://github.com/mneves75/skills.git ~/.cursor/skills/mneves-skills
```

### VS Code (with AI extensions)

```bash
git clone https://github.com/mneves75/skills.git ~/.vscode/skills/mneves-skills
```

### Codex / OpenAI

```bash
# Via OpenSkills
npx openskills add mneves75/skills

# Manual
git clone https://github.com/mneves75/skills.git ~/.agent/skills/mneves-skills
```

### Windsurf / Aider / Other Tools

```bash
git clone https://github.com/mneves75/skills.git ~/.agent/skills/mneves-skills
```

## Benchmark Examples

Real assessments of popular open-source projects. **[View Live Reports →](https://mneves75.github.io/skills/)**

| Project | Language | Level | Score | Report |
|---------|----------|-------|-------|--------|
| FastAPI | Python | L4 | 65.4% | [View](https://mneves75.github.io/skills/fastapi.html) |

See [examples/](https://mneves75.github.io/skills/) for live reports.

## Skill Locations

Skills are discovered in these locations (priority order):

| Location | Scope | Tool |
|----------|-------|------|
| `./.agent/skills/` | Project | Universal |
| `~/.agent/skills/` | Global | Universal |
| `./.pi/skills/` | Project | pi |
| `~/.pi/agent/skills/` | Global | pi |
| `./.opencode/skills/` | Project | OpenCode |
| `~/.config/opencode/skills/` | Global | OpenCode |
| `./.claude/skills/` | Project | Claude Code |
| `~/.claude/skills/` | Global | Claude Code |
| `~/.cursor/skills/` | Global | Cursor |
| `~/.vscode/skills/` | Global | VS Code |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache-2.0

## Acknowledgments

This project is inspired by [Factory.ai](https://factory.ai)'s Code Readiness framework. Factory.ai pioneered the approach of evaluating codebases for AI agent compatibility using structured pillars and maturity levels. Their commercial tool set the standard for what "agent-ready" means.

## Related

- [Anthropic Skills](https://github.com/anthropics/skills) - Official specification
- [pi coding agent](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent) - Open-source coding agent with skills support
- [OpenCode](https://opencode.ai/) - Terminal-based AI coding assistant with skills support
- [OpenSkills](https://github.com/numman-ali/openskills) - Universal skills loader
- [skills.sh](https://skills.sh) - Skill registry
