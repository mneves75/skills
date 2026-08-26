# MEMORY.md — mneves-skills

Curated project memory: goal, current state, decisions that still bind, and lessons that cost
something to learn. Daily detail lives in `memory/YYYY-MM-DD.md`; the shipped record lives in
`CHANGELOG.md`; the enforceable invariants live in `AGENTS.md` (canonical) — this file does not
restate them.

## Goal

Ship production-ready, tool-agnostic skills for AI coding agents. Each skill encodes a reusable
judgment-heavy procedure (model routing, spaced-repetition teaching, independent verification),
not a pile of scripts. The `tools/` readiness checker is the one concrete tool, and it exists to
measure whether a *target* codebase is ready for agents.

## Where things stand

- **1.6.0** (2026-08-26): adds `mneves-eli5` (Feynman explainer, audience-calibrated); linked into
  the shared `~/.agents/skills` catalog and every agent farm (Codex, OpenCode, Cursor, Pi, Gemini, …).
- **1.5.0** shipped: adds `mneves-verify` (independent-verification skill) plus the
  repo's own ast-grep `as any` guard and a blocking pre-commit hook.
- Skills: `mneves-agent-readiness`, `mneves-fable-orchestrator` (ships `codex-lane`),
  `mneves-teach-back-srs`, `mneves-verify`, `mneves-eli5`.
- `tools/` is a Bun + TypeScript project with no external runtime deps; dev deps only (Biome,
  TypeScript, bun-types).

## Decisions that still bind

- **`mneves-` prefix on every skill** (1.3.0). Directory name and frontmatter `name:` must match.
- **Skills are Markdown-first.** Exactly one executable ships **inside a skill** — `codex-lane`
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

## Known gaps

- No CI for the `tools/` typecheck/lint (the `.github/workflows/static.yml` publishes the
  examples page, not the code). Typecheck/lint run locally via Bun/Biome when needed.
