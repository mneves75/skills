---
name: mneves-agent-readiness
description: Assess a codebase for AI-agent readiness. Use for repository onboarding, agent friction, or infrastructure priorities.
license: Apache-2.0
---

# Agent Readiness Evaluation

## Core Insight

Agent failure is usually an environment problem, not a model problem. AI coding agents operate in a feedback loop: **gather context -> take action -> verify work -> iterate**

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

See [references/context-file-template.md](references/context-file-template.md).

## Reference

- **Tool**: `tools/readiness-check.ts`, in the collection repository — present in a full clone,
  not in a single-skill install. Without it, use the manual pass above.
- **Sample report**: https://mneves75.github.io/skills/fastapi.html
- **Inspired by**: [Factory.ai Agent Readiness](https://factory.ai/agent-readiness)
