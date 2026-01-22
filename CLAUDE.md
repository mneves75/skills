# CLAUDE.md

Instructions for AI coding agents working with this repository.

## Overview

This repository contains production-ready skills for AI coding agents. Skills are reusable knowledge modules that help agents perform specialized tasks.

## Project Structure

```
skills/
├── skills/agent-readiness/   # Codebase readiness assessment skill
│   ├── SKILL.md              # Skill definition (YAML frontmatter)
│   └── README.md             # Detailed documentation
├── tools/                    # Assessment tool (Bun + TypeScript)
│   ├── readiness-check.ts    # Main entry point
│   └── lib/                  # Shared modules
├── examples/                 # Sample reports (deployed to GitHub Pages)
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
| `VERSION` | Semantic version |

## Conventions

- **Bun runtime** - All TypeScript runs via Bun
- **No external runtime deps** - Only dev dependencies
- **Multi-language support** - TypeScript, JavaScript, Go, Python, Rust, Java

## Adding a Skill

1. Create `skills/{skill-name}/SKILL.md` with YAML frontmatter
2. Add `skills/{skill-name}/README.md` for detailed docs
3. Update root `README.md` to list the new skill
