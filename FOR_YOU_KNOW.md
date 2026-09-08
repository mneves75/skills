# FOR_YOU_KNOW.md: mneves-skills, explained plainly

Re-read after months away. The enforceable rules live in [`AGENTS.md`](./AGENTS.md) (canonical);
the shipped record lives in [`CHANGELOG.md`](./CHANGELOG.md); current state and lessons live in
[`MEMORY.md`](./MEMORY.md) + `memory/YYYY-MM-DD.md`. This file is the "why", not the "what".

## The one idea

This repo ships **skills**: reusable instruction modules for AI coding agents. A skill is a
folder under `skills/` with a `SKILL.md` (YAML frontmatter: `name:` + `description:`, then the
procedure). A skill may add a `README.md` when longer human-facing documentation helps. The
frontmatter `description:` is the routing signal agents use to decide whether to load the skill,
so it names the trigger conditions.

Skills are tool-agnostic by design: the same folder installs into pi, Claude Code, OpenCode,
Cursor, Codex, etc. by symlinking it into that tool's skills directory.

## The decisions that look odd and aren't

**Original skills carry the `mneves-` prefix.** A rename in 1.3.0 collapsed three near-collisions
with upstream/community skill names. An adapted third-party skill instead keeps its upstream name,
license, copyright, and provenance so its origin stays obvious. Directory name and frontmatter
`name:` always match.

**`imagegen-frontend-mobile` is an attributed adaptation.** The installed upstream procedure was
1,465 lines and repeated aesthetic rules many times. The version here keeps the useful sequence
(define screens, lock a system, generate, inspect, correct) while making platform familiarity,
truthfulness, private-reference handling, and the limits of static accessibility evidence explicit.
Its MIT license travels inside the skill directory; the rest of the repository remains Apache-2.0.

**Some skills need executables.** `mneves-fable-orchestrator/tools/codex-lane` is a bash
wrapper installed by symlink onto `PATH`; `mneves-teach-back-srs/scripts/srs_db.py` is a Python
helper run from its skill directory. The repo copies are canonical. They are distinct from the
repository's own `.githooks/pre-commit` guard. `autoreview` packages a Python review CLI and its
tests because subprocess isolation, credential scanning, and source integrity need enforcement
in code. It is an MIT-licensed adaptation with a pinned upstream revision and local maintenance,
so an installation does not depend on another checkout. Other skills are Markdown-only; the readiness
assessor lives in the root `tools/` project.

**`mneves-verify` ships no scripts at all.** It is deliberately machinery-free: the whole skill
is a procedure (independent context, evidence routes, one correction + one reverify, then
PASS/FAIL/BLOCKED). The rule "no scripts/dependencies/scaffolding" is part of its contract, not
an accident of laziness.

## The repo's own guard: ast-grep

The repository itself is guarded by two ast-grep rules: reject `as any` in TypeScript
(`rules/no-as-any.yml`) and TSX (`rules/no-as-any-tsx.yml`), both wired through `sgconfig.yml`.
A blocking pre-commit hook
(`.githooks/pre-commit`, active via `git config core.hooksPath .githooks`) **fails closed** if
ast-grep is missing. This is the repo practicing what `mneves-verify` preaches: a checkable
outcome enforced by a real tool, not a prose promise. The `tools/` TypeScript must keep passing
it; the natural replacement for `as any` is `unknown` + a narrowing guard.

## Before you touch things

- `VERSION` is the single source of the version; the README badge and `CHANGELOG.md` top entry
  must match it. (1.4.0 shipped with the badge still reading 1.2.0; that was the bug.)
- Adding a skill touches five places: its `SKILL.md` (plus `README.md` when useful), the root `README.md`
  table + badge, `AGENTS.md` (tree; `CLAUDE.md` just imports it), `VERSION`, and
  `CHANGELOG.md`.
- `tools/` is a separate Bun project (`tools/package.json`, lockfile committed). Its runtime is
  Bun; there are no external runtime deps, only dev deps (Biome, TypeScript, bun-types).
- Shipped text must work from a stranger's clone: no home paths, no machine layout. CI checks
  the skill layout the `npx skills` CLI relies on (folder name == frontmatter `name`).

## Where things live

| Need | Go to |
|------|-------|
| Enforceable rules | `AGENTS.md` (canonical; `CLAUDE.md` imports it) |
| What shipped, when | `CHANGELOG.md` |
| Current state, lessons | `MEMORY.md` + `memory/YYYY-MM-DD.md` |
| A skill's procedure | `skills/<name>/SKILL.md` |
| A skill's docs | `skills/<name>/README.md`; usage with examples in `HOWTO.md` |
| The public site | `site/` (landing `index.html` hand-written except the changelog rows; `howto.html` generated; both by `tools/scripts/build-site.sh`; sample report) |
| The repo's own lint guard | `sgconfig.yml` + `rules/no-as-any.yml` + `rules/no-as-any-tsx.yml` + `.githooks/pre-commit` |
| Assessment tool | `tools/readiness-check.ts` |
