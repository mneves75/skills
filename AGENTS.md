# AGENTS.md

Instructions for AI coding agents working with this repository. `CLAUDE.md` imports this file;
keep every rule here only.

## Overview

Skills for AI coding agents. Each skill is a folder
under `skills/` with a `SKILL.md` (YAML frontmatter `name` + `description`, then the procedure).
Users install with `npx skills@latest add mneves75/skills` or a plain `git clone`.

## Project Structure

```
.
├── skills/
│   ├── autoreview/                # Portable AI review CLI + security tests (MIT)
│   ├── imagegen-frontend-mobile/   # Mobile screen/flow image generation (MIT)
│   ├── mneves-agent-readiness/    # Codebase readiness assessment (pairs with tools/)
│   ├── mneves-eli5/               # Feynman explainer, audience-calibrated
│   ├── mneves-expert-review/      # Expert-panel review/optimization pass (+ references/)
│   ├── mneves-fable-orchestrator/ # Model routing; Codex reference + tools/codex-lane
│   ├── mneves-teach-back-srs/     # Spaced-repetition teach-back (+ scripts/srs_db.py)
│   └── mneves-verify/             # Independent verification before done/fixed/shipped
├── tools/                    # Readiness assessor (Bun + TypeScript): readiness-check.ts + lib/
├── HOWTO.md                  # Per-skill usage guide with examples (rendered to site/howto.html)
├── site/                     # GitHub Pages: index.html (landing), howto.html, sample readiness report
├── rules/ + sgconfig.yml     # ast-grep guard: reject `as any` (TS + TSX)
├── .githooks/pre-commit      # Blocking pre-commit hook (ast-grep scan) + its test
├── .github/workflows/ci.yml  # CI: skill checks, syntax, ast-grep, hook/site/tools gates, autoreview tests
├── CHANGELOG.md · VERSION    # Keep a Changelog; VERSION is the single source of the version
├── SECURITY.md · NOTICE      # Vulnerability reporting; attributions
└── MEMORY.md · memory/ · FOR_YOU_KNOW.md   # Project memory and the plain-language "why"
```

## Commands

```bash
cd tools && bun install                 # dev deps only (Biome, TypeScript, bun-types)
bun run typecheck && bun run lint       # from tools/
ast-grep scan --config sgconfig.yml .   # from repo root
bash .githooks/pre-commit.test          # hook e2e test
bun --bun tools/readiness-check.ts --format=html --output=report.html   # assess cwd
tools/scripts/build-site.sh            # HOWTO.md -> site/howto.html + landing changelog rows (CI checks freshness)
npx skills@latest add . --list          # what the skills CLI will discover
python3 skills/autoreview/scripts/run-tests.py  # isolated unit/integration/security suite
```

## Invariants (CI enforces the checkable ones)

- Directory name == frontmatter `name:`. Original skills carry the `mneves-` prefix;
  adapted third-party skills retain their upstream name, copyright, license, and provenance.
  `description:` is one short capability-and-trigger line; keyword inventories and
  procedures belong in the body or a routed reference.
- Never add a root `SKILL.md`: the skills CLI lets a shallower `SKILL.md` shadow everything
  below it.
- Skills are Markdown-first. Shipped executables are `bash` + `set -euo pipefail`, `bash -n`
  clean when written in Bash. Python helpers use Python 3.11+ and the standard library.
  Executable skills are `autoreview`, `mneves-fable-orchestrator`, and `mneves-teach-back-srs`;
  the repository copy is canonical and each ships its relevant verification procedure.
- No `any` / `as any` in `tools/`; use `unknown` + a narrowing guard. ast-grep blocks it.
- No personal paths, machine layout, secrets or client names in shipped files; a skill must work
  for a stranger's clone.
- `VERSION`, the README badge and the top `CHANGELOG.md` entry agree.

## Adding a Skill

1. `skills/<mneves-name>/SKILL.md` with frontmatter; `README.md` only when longer docs help.
   An adapted third-party skill keeps its upstream name and ships its license and provenance.
2. Root `README.md` table, a `HOWTO.md` section, the tree above, `VERSION`, `CHANGELOG.md`, README badge; then `tools/scripts/build-site.sh` (CI fails on stale site files).
3. `npx skills@latest add . --list` shows the new skill; CI green.
