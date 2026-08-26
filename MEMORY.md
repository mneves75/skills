# MEMORY.md: mneves-skills

Curated project memory: goal, current state, decisions that still bind, and lessons that cost
something to learn. Daily detail lives in `memory/YYYY-MM-DD.md`; the shipped record lives in
`CHANGELOG.md`; the enforceable invariants live in `AGENTS.md` (canonical); this file does not
restate them.

## Goal

Ship tool-agnostic skills for AI coding agents. Each skill encodes a reusable
judgment-heavy procedure (model routing, spaced-repetition teaching, independent verification),
not a pile of scripts. The `tools/` readiness checker is the one concrete tool, and it exists to
measure whether a *target* codebase is ready for agents.

## Where things stand

- **1.11.0** (2026-08-26): recorded sessions in HOWTO, ruleset on `main`, teach-back script path relative,
  model table in orchestrator, landing changelog generated (`build-site.sh`).
- **1.10.0** (2026-08-26): orchestrator adopts codex-first lessons (escape hatches, live-worker check,
  verify beyond the diff, death diagnosis); `license:` in every skill; prose pass.
- **1.9.0** (2026-08-26): landing page (`site/index.html`), Pages source `examples/` → `site/`, only `main` remains.
- **1.8.2** (2026-08-26): `HOWTO.md` + rendered `site/howto.html` (per-skill usage with examples).
- **1.8.1** (2026-08-26): example report regenerated (FastAPI L3 61.7%, with provenance); Factory.ai
  attribution reduced to verifiable facts.
- **1.8.0** (2026-08-26): public-repo hardening: CI workflow, SECURITY.md, Dependabot, SHA-pinned
  actions, `npx skills add mneves75/skills` documented as primary install, maintainer-local path
  removed from `mneves-expert-review`.
- **1.7.0 / 1.6.0** (2026-08-26): `mneves-expert-review`, `mneves-eli5`.
- **1.5.0** shipped: adds `mneves-verify` (independent-verification skill) plus the
  repo's own ast-grep `as any` guard and a blocking pre-commit hook.
- Skills: `mneves-agent-readiness`, `mneves-eli5`, `mneves-expert-review`,
  `mneves-fable-orchestrator` (ships `codex-lane`), `mneves-teach-back-srs`, `mneves-verify`.
- `tools/` is a Bun + TypeScript project with no external runtime deps; dev deps only (Biome,
  TypeScript, bun-types).

## Decisions that still bind

- **`mneves-` prefix on every skill** (1.3.0). Directory name and frontmatter `name:` must match.
- **Skills are Markdown-first.** Two executables ship inside skills, `srs_db.py` (helper) and `codex-lane`
  (`skills/mneves-fable-orchestrator/tools/codex-lane`). It is distinct from the repo's own
  `.githooks/pre-commit` guard (a repository-level hook, not a skill). It is `bash` +
  `set -euo pipefail`, `bash -n` clean, and installed by symlink onto `PATH` (repo copy is
  canonical). New skills should stay machinery-free unless a real executable is the point.
- **`VERSION`, the README badge, and the top `CHANGELOG.md` entry must agree.** Single source is
  `VERSION`.
- **The repo guards itself with ast-grep.** `rules/no-as-any.yml` rejects `as any` in TypeScript
  and `rules/no-as-any-tsx.yml` rejects it in TSX; `.githooks/pre-commit` enforces both and
  fails closed when ast-grep is absent. `unknown` + a narrowing guard is the sanctioned
  replacement.

## Lessons paid for

- **README badge drift.** 1.4.0 shipped with the badge still pinned at 1.2.0 while `VERSION`
  read 1.3.0. Any version bump is three places, not one.
- **A skill is its description.** The frontmatter `description:` is the routing trigger agents
  read before loading anything; a description that doesn't name when-to-use makes the skill
  undiscoverable.

- **Shipped text must work from a stranger's clone.** 1.7.0 baked `~/dev/GUIDELINES-REF` into a
  skill's frontmatter `description:`; every installing agent was told to read a directory only
  the maintainer has. The public-repo scan is: no home paths, no machine layout, no client names.

## Known gaps

- 1.1–1.5 changelog links point at tags that do not exist (every release since 1.6.0 is tagged).
- `mneves75.github.io` (user site) does not exist as a repo; linking this project from it needs
  that repo to be created first.
