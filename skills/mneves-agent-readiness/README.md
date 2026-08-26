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

## Relationship to Factory.ai

The pillar and maturity-level structure follows the shape of [Factory.ai's Agent Readiness](https://factory.ai/agent-readiness) (a commercial, hosted assessment). This tool is independent: open source (Apache-2.0), runs locally with no upload, every check is visible in `tools/lib/`, and the scoring modes are configurable. Scores are not comparable with Factory.ai's — the checks and weights are this tool's own.

## License

Apache-2.0

## Related

- [Factory.ai Agent Readiness](https://factory.ai/agent-readiness) - the commercial assessment whose structure this tool follows
- [skills.sh](https://skills.sh) - Open skill ecosystem
- [OpenSkills](https://github.com/numman-ali/openskills) - Universal skills loader
