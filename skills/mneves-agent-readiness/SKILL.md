---
name: mneves-agent-readiness
description: Assess a codebase for AI-agent readiness. Use for repository onboarding, agent friction, or infrastructure priorities.
license: Apache-2.0
---

# Agent Readiness Evaluation

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

Run the readiness-check tool. It assesses the current directory, so `cd` into the target
project first (`SKILLS` is wherever this repo is installed):

```bash
cd /path/to/your/project
bun --bun $SKILLS/tools/readiness-check.ts

# Quick mode (skip tests/build)
bun --bun $SKILLS/tools/readiness-check.ts --skip-tests --skip-build

# HTML dashboard
bun --bun $SKILLS/tools/readiness-check.ts --format=html --output=readiness-report.html

# CI gate (fail if below level 3)
bun --bun $SKILLS/tools/readiness-check.ts --min-level=3
```

## Four Phases to Evaluate

| Phase | Question | Key Checks |
|-------|----------|------------|
| **CONTEXT** | Can the agent understand? | Context file is concise, has commands, structure is recognizable |
| **ACTION** | Can the agent change things? | No `any`, strict types, linting and formatting configured |
| **VERIFICATION** | Can the agent check work? | Tests pass, build works, lockfile committed |
| **ITERATION** | Can the agent improve? | CI, PR template, required checks, deployment documented |

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

## Reference

- **Tool**: [tools/readiness-check.ts](../../tools/readiness-check.ts) (bundled with this skill)
- **Sample report**: [site/fastapi.html](../../site/fastapi.html) (live at https://mneves75.github.io/skills/fastapi.html)
- **Inspired by**: [Factory.ai Agent Readiness](https://factory.ai/agent-readiness)

> "You can't prompt your way out of bad infrastructure. Fix the environment, not the agent."
