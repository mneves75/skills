# AGENTS.md

Instructions for AI coding agents working with this repository.

## Overview

Production-ready skills for AI coding agents. Tool-agnostic by design.

## Project Structure

```
skills/
├── skills/mneves-agent-readiness/     # Codebase readiness assessment skill
│   ├── SKILL.md                      # Skill definition (YAML frontmatter)
│   └── README.md                     # Detailed documentation
├── skills/mneves-fable-orchestrator/ # Model-routing policy (Fable plans, executors type)
│   ├── SKILL.md
│   ├── README.md
│   └── tools/codex-lane              # Resumable Codex thread wrapper (bash)
├── skills/mneves-teach-back-srs/     # Spaced-repetition learning via teach-back sessions
├── tools/                    # Assessment tool (Bun + TypeScript)
│   ├── readiness-check.ts    # Main entry point
│   └── lib/                  # Shared modules
├── examples/                 # Sample reports (GitHub Pages)
├── CHANGELOG.md              # Version history
└── NOTICE                    # Attribution notices
```

## Commands

```bash
# Install dependencies
cd tools && bun install

# Run readiness assessment
bun --bun tools/readiness-check.ts

# Generate HTML report
bun --bun tools/readiness-check.ts --format=html --output=report.html

# Skip long-running checks
bun --bun tools/readiness-check.ts --skip-tests --skip-build
```

## Key Files

| File | Purpose |
|------|---------|
| `skills/*/SKILL.md` | Skill definition with YAML metadata |
| `tools/readiness-check.ts` | Assessment tool (9 pillars, 51+ checks) |
| `skills/mneves-fable-orchestrator/tools/codex-lane` | Named, resumable Codex threads (`start`/`next`/`adopt`/`last`) |
| `VERSION` | Semantic version |

## Conventions

- **Bun runtime** - All TypeScript runs via Bun
- **No external runtime deps** - Only dev dependencies
- **Multi-language support** - TypeScript, JavaScript, Go, Python, Rust, Java
- **Shipped shell scripts** - `bash` with `set -euo pipefail`; must pass `bash -n`; users
  install them by symlink onto `PATH`, so the repo copy is canonical (never a copy-out)

## Adding a Skill

1. Create `skills/{skill-name}/SKILL.md` with YAML frontmatter
2. Add `skills/{skill-name}/README.md` for detailed docs
3. Update root `README.md` to list the new skill
4. Bump `VERSION`, add a `CHANGELOG.md` entry, and update the README version badge
