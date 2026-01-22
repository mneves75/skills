---
name: agent-readiness
description: Evaluate codebase readiness for AI coding agents using automated assessment. Use when onboarding repos, diagnosing agent struggles, or planning infrastructure improvements.
---

# Agent Readiness Evaluation

## When to Use This Skill

- Onboarding a new repository for AI-assisted development
- Diagnosing why your AI agent is struggling with a codebase
- Evaluating a codebase before AI agent deployment
- User asks "why isn't my AI working well here?"
- User asks about "agent readiness" or "codebase evaluation"
- Planning infrastructure improvements for agent performance

## Core Insight

> "The agent is not broken. The environment is."

AI coding agents operate in a feedback loop: **gather context -> take action -> verify work -> iterate**

This skill evaluates whether your codebase supports each phase of that loop.

## Quick Assessment (5 Questions)

Answer these for an instant maturity estimate:

1. Does CLAUDE.md (or .cursorrules, AGENTS.md) exist with build/test commands? (CONTEXT)
2. Is strict typing enabled with linting? (ACTION)
3. Can tests run without manual setup? (VERIFICATION)
4. Does CI provide clear pass/fail feedback? (ITERATION)
5. Is the feedback loop under 5 minutes? (AUTONOMOUS)

**Score**: 5/5 = L5, 4/5 = L4, 3/5 = L3, 2/5 = L2, 1/5 = L1

## Automated Assessment

Run the readiness-check tool (v1.0.0):

```bash
# From the skills repository
cd ~/.claude/skills/mneves-skills
bun --bun tools/readiness-check.ts /path/to/your/project

# Quick mode (skip tests/build)
bun --bun tools/readiness-check.ts --skip-tests --skip-build

# HTML dashboard
bun --bun tools/readiness-check.ts --format=html --output=readiness-report.html

# CI gate (fail if below level 3)
bun --bun tools/readiness-check.ts --min-level=3
```

## Four Phases to Evaluate

| Phase | Question | Key Checks |
|-------|----------|------------|
| **CONTEXT** | Can the agent understand? | CLAUDE.md exists, <300 lines, has commands |
| **ACTION** | Can the agent change things? | No `any`, strict types, linting configured |
| **VERIFICATION** | Can the agent check work? | Tests pass, build works, lockfile committed |
| **ITERATION** | Can the agent improve? | CI configured, PR template, required checks |

## Maturity Levels

| Level | Name | Description |
|-------|------|-------------|
| **L1** | Functional | Code runs, basic files exist |
| **L2** | Navigable | Agent can find things |
| **L3** | Actionable | Agent can make changes safely |
| **L4** | Verifiable | Agent can check its work |
| **L5** | Autonomous | Agent can work independently |

**Target**: Level 3 minimum for productive AI development.

## Remediation Paths

| Gap | Action |
|-----|--------|
| Missing context file | Create CLAUDE.md/.cursorrules with build/test commands |
| No typing/linting | Add ESLint/Biome + strict TypeScript |
| Tests require setup | Use containers or in-memory alternatives |
| No CI pipeline | Add GitHub Actions workflow |
| No observability | Add structured logging |

## Context File Template

Works as CLAUDE.md, .cursorrules, or AGENTS.md:

```markdown
# Project Context

## Overview
[1-2 sentences: what this does and WHY]

## Commands
- Build: `bun run build`
- Test: `bun test`
- Lint: `bun run lint`

## Architecture
[Brief description of key directories]

## Key Decisions
- [Decision]: [Why]
```

**Requirements**: Concise (<300 lines), Actionable (commands work), Current (updated within 30 days)

## Compliance Checklist

### CONTEXT Phase
- [ ] Context file exists at repository root (CLAUDE.md, .cursorrules, AGENTS.md)
- [ ] Context file includes build/test commands
- [ ] Context file is under 300 lines
- [ ] File structure is recognizable (src/, app/, lib/)

### ACTION Phase
- [ ] No `any` type casts in codebase (if TypeScript)
- [ ] Strict mode enabled
- [ ] Linter configured (ESLint, Biome, golangci-lint, ruff)
- [ ] Formatter configured

### VERIFICATION Phase
- [ ] Tests exist and pass
- [ ] Build succeeds without manual intervention
- [ ] Lock file is committed

### ITERATION Phase
- [ ] CI pipeline configured
- [ ] PR template exists
- [ ] Deployment process documented

## Common Mistakes

- Blaming the agent when infrastructure is broken (fix the environment!)
- Missing context file (single most impactful file for agent success)
- Liberal use of `any` to silence TypeScript (use `unknown` + type guards)
- Tests that require manual setup (use containers or in-memory DBs)
- Outdated documentation (keep context files current)

## Reference

- **Tool**: [tools/readiness-check.ts](../../tools/readiness-check.ts) (bundled with this skill)
- **Examples**: [examples/](../../examples/) (sample reports)
- **Inspired by**: [Factory.ai Agent Readiness](https://factory.ai/agent-readiness)

> "You can't prompt your way out of bad infrastructure. Fix the environment, not the agent."
