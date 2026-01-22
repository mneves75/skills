# Agent Readiness Skill

**Evaluate codebase readiness for AI coding agents using automated assessment.**

Inspired by [Factory.ai's Agent Readiness](https://factory.ai/agent-readiness) framework. Open source, local-first, multi-language.

**Works with**: Claude Code, Cursor, VS Code, Codex, Windsurf, Aider, and any tool supporting the Agent Skills specification.

## Philosophy

> "The agent is not broken. The environment is."

AI coding agents operate in a feedback loop: **gather context → take action → verify work → iterate**

This skill evaluates whether your codebase supports each phase:

| Phase | Question | What Makes It Work |
|-------|----------|-------------------|
| **Context** | Can the agent understand? | CLAUDE.md, clear architecture, <300 line context files |
| **Action** | Can the agent change things? | Strict types, linting, no `any` casts |
| **Verification** | Can the agent check work? | Tests pass, build works, CI configured |
| **Iteration** | Can the agent improve? | Fast feedback loops (<5 min), PR templates |

**You can't prompt your way out of bad infrastructure. Fix the environment, not the agent.**

## Quick Start

```bash
# Install the skill
npx skills add mneves75/skills

# Run assessment on any codebase
cd your-project
readiness-check
```

## What It Does

Analyzes your codebase across **9 pillars** with **51+ automated checks** to determine how well AI agents can work with your code.

| Pillar | What It Measures |
|--------|-----------------|
| Style & Validation | Linting, formatting, type checking |
| Build System | Build scripts, lock files, reproducibility |
| Testing | Test coverage, CI integration, isolation |
| Documentation | README, CLAUDE.md, architecture docs |
| Development Environment | Setup scripts, devcontainer, env templates |
| Debugging & Observability | Structured logging, error tracking |
| Security | CODEOWNERS, security scanning, audit trail |
| Task Discovery | Makefile, PR templates, issue templates |
| Product & Experimentation | Feature flags, CI test execution |

## Use When

- Onboarding a new repository for AI-assisted development
- Diagnosing why your AI agent is struggling with a codebase
- Evaluating a codebase before deploying AI agents
- Planning infrastructure improvements for better agent performance
- Answering "why isn't my AI working well here?"

## Features

### Multi-Language Support

Automatically detects and adapts checks for:
- TypeScript / JavaScript
- Python
- Go
- Rust
- Java

### Monorepo Aware

Discovers and scores sub-applications in:
- npm/pnpm workspaces
- Go workspaces (go.work)
- Cargo workspaces
- Maven/Gradle multi-module projects

### Multiple Output Formats

```bash
# Terminal markdown (default)
readiness-check

# HTML dashboard with executive summary
readiness-check --format=html --output=report.html

# JSON for automation
readiness-check --format=json

# CI gate (fail if below level 3)
readiness-check --min-level=3
```

### Configurable Scoring

```bash
# Weighted scoring (default) - balanced pillar weights
readiness-check --scoring=weighted

# Strict scoring - weakest pillar determines level
readiness-check --scoring=strict

# Average scoring - simple average across pillars
readiness-check --scoring=average
```

## Maturity Levels

| Level | Name | Description |
|-------|------|-------------|
| L1 | Functional | Code runs, basic files exist |
| L2 | Navigable | Agent can find things |
| L3 | Actionable | Agent can make changes safely |
| L4 | Verifiable | Agent can check its work |
| L5 | Autonomous | Agent can work independently |

**Target**: Level 3 minimum for productive AI development.

## Factory.ai Comparison

This tool is inspired by [Factory.ai's Agent Readiness](https://factory.ai/agent-readiness) assessment. Here's how they compare:

| Feature | Factory.ai | This Tool |
|---------|-----------|-----------|
| **Languages** | TS, Python, Rust, Go, Java | Same (with auto-detection) |
| **Monorepo** | Limited | Full support |
| **Output** | Web dashboard | CLI + HTML + JSON + Markdown |
| **Privacy** | Cloud analysis | Local-only (no upload) |
| **Checks** | Undisclosed | 51+ (transparent) |
| **Scoring** | Weighted (proprietary) | Configurable (3 modes) |
| **Offline** | No | Yes |
| **Open Source** | No | Yes (Apache-2.0) |
| **Cost** | Free tier + paid | Free forever |

### Why Choose This Tool?

1. **Privacy First**: Your code never leaves your machine
2. **Transparency**: All checks are documented and visible
3. **Customizable**: Override detection, skip checks, configure scoring
4. **CI/CD Ready**: Built-in exit codes and min-level gating
5. **Open Source**: Audit, fork, contribute, extend

### When to Use Factory.ai

- You want a hosted solution with no setup
- You need their specific integrations
- You're already in their ecosystem

## Installation

### Claude Code

```bash
npx skills add mneves75/skills
```

### Cursor

```bash
git clone https://github.com/mneves75/skills.git ~/.cursor/skills/mneves-skills
```

### VS Code

```bash
git clone https://github.com/mneves75/skills.git ~/.vscode/skills/mneves-skills
```

### Codex / OpenAI

```bash
npx openskills add mneves75/skills
```

### Universal (Any Tool)

```bash
git clone https://github.com/mneves75/skills.git ~/.agent/skills/mneves-skills
```

### CLI Tool (Direct)

```bash
git clone https://github.com/mneves75/skills.git
cd skills/tools
bun install
bun --bun readiness-check.ts /path/to/your/project
```

## Usage Examples

### Basic Assessment

```bash
cd my-project
readiness-check
```

Output:
```
Agent Readiness Report v1.0.0
==============================
Repository: my-project
Language: typescript
Maturity: L3 (Actionable) - 67%

Pillars:
  Style & Validation     L4  83%  ████████░░
  Build System           L3  71%  ███████░░░
  Testing                L3  62%  ██████░░░░
  Documentation          L4  75%  ███████░░░
  ...
```

### HTML Dashboard

```bash
readiness-check --format=html --output=readiness.html
open readiness.html
```

Generates a visual dashboard with:
- Executive summary (Strengths / Opportunities)
- Level progress bars (L1-L5)
- Radar chart of pillar scores
- Collapsible detailed criteria per pillar
- Blocking gaps section

### CI Integration

```yaml
# .github/workflows/readiness.yml
name: Agent Readiness Check
on: [push]
jobs:
  readiness:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - run: |
          git clone https://github.com/mneves75/skills.git /tmp/skills
          cd /tmp/skills/tools && bun install
          bun --bun readiness-check.ts --min-level=3 ${{ github.workspace }}
```

### Skip Long-Running Checks

```bash
readiness-check --skip-tests --skip-build
```

### Force Language Detection

```bash
readiness-check --language=python
```

## Common Issues & Fixes

| Symptom | Diagnosis | Fix |
|---------|-----------|-----|
| L1 score despite tests | Tests not in standard location | Move to `tests/`, `__tests__/`, or `*_test.go` |
| Missing documentation score | No CLAUDE.md | Create CLAUDE.md with build/test commands |
| Low style score | No linter config | Add `.eslintrc`, `biome.json`, or `.golangci.yml` |
| Build fails | No lock file | Commit `bun.lockb`, `package-lock.json`, or `go.sum` |

## CLAUDE.md Template

The single most impactful file for agent success:

```markdown
# CLAUDE.md

## Overview
[1-2 sentences: what this project does and WHY]

## Commands
- Build: `bun run build`
- Test: `bun test`
- Lint: `bun run lint`

## Architecture
[Brief description of key directories]

## Key Decisions
- [Decision]: [Rationale]
```

Requirements:
- **Concise**: <300 lines (ideally <60)
- **Actionable**: Commands that work
- **Current**: Updated within 30 days

## Contributing

Found a bug? Want to add a check? Contributions welcome.

1. Fork the repo
2. Create a feature branch
3. Add tests for new checks
4. Submit a PR

## License

Apache-2.0

## Related

- [Factory.ai](https://factory.ai) - Commercial inspiration
- [skills.sh](https://skills.sh) - Open skill ecosystem
- [OpenSkills](https://github.com/numman-ali/openskills) - Universal skills loader
