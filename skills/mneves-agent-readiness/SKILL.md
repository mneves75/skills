---
name: mneves-agent-readiness
description: Assess a codebase for AI-agent readiness. Use for repository onboarding, agent friction, or infrastructure priorities.
license: Apache-2.0
---

# Agent Readiness Evaluation

## Choose the assessment

Assess the requested repository or subsystem; report findings without implementing remediation
unless asked. Inspect its instructions, documented commands, and relevant configuration once.
Use an existing current report when its source and scope still match; rerun only for changed
inputs, missing evidence, or a requested fresh assessment.

For a quick manual triage, answer:

1. Does CLAUDE.md (or .cursorrules, AGENTS.md) exist with build/test commands? (CONTEXT)
2. Is strict typing enabled with linting? (ACTION)
3. Can tests run without manual setup? (VERIFICATION)
4. Does CI provide clear pass/fail feedback? (ITERATION)
5. Is the feedback loop under 5 minutes? (AUTONOMOUS)

These five questions identify friction, not the assessor's nine-pillar maturity score. Mark
unrun build/test checks as unverified; configuration alone does not prove a passing command.

## Automated Assessment

Run the readiness-check tool. It assesses the current directory, so `cd` into the target
project first (`SKILLS` is the absolute collection root, discovered from the installed skill).
The tool ships only in a full clone; without it, use the manual assessment and label that limit.
Choose one output/mode for the requested deliverable; use `--help` for other flags.

```bash
cd /path/to/your/project
bun --bun "$SKILLS/tools/readiness-check.ts"

# Quick mode (skip tests/build)
bun --bun "$SKILLS/tools/readiness-check.ts" --skip-tests --skip-build

# HTML dashboard
bun --bun "$SKILLS/tools/readiness-check.ts" --format=html --output=readiness-report.html

# CI gate (fail if below level 3)
bun --bun "$SKILLS/tools/readiness-check.ts" --min-level=3
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

## Deliver

Report assessed scope/source, mode, evidence, blocking gaps, and ranked smallest fixes. Include
the report path and exit status when the tool ran. A static-only report is not runtime proof.
Stop when each requested assessment area has evidence or a precise blocker.

When context-file guidance is a proposed fix, read
[references/context-file-template.md](references/context-file-template.md).

## Reference

- **Tool**: `tools/readiness-check.ts`, in the collection repository — present in a full clone,
  not in a single-skill install. Without it, use the manual pass above.
- **Sample report**: https://mneves75.github.io/skills/fastapi.html
- **Inspired by**: [Factory.ai Agent Readiness](https://factory.ai/agent-readiness)
