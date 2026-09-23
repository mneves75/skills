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

- **1.23.3** (2026-09-23): README "Check the install" loop. Host fix: `mneves-verify`,
  `mneves-handoff` and `mneves-agent-readiness` had never been linked on this Mac; now linked in
  `~/.agents/skills` and all 13 agent skill dirs. A new skill needs this step on every agent.
- **1.23.2** (2026-09-22): Codex orchestrator seat `gpt-6-sol` `medium` (the Codex default, per the
  user); executor and reviewer stay `high`.
- **1.23.1** (2026-09-22): `handoff` renamed `mneves-handoff` (clash with mattpocock/skills
  `handoff`); AGENTS.md allows the prefix for a colliding adapted name. Autoreview test fixes that
  made CI green (`4b5c183`); `v1.23.0` was moved from `9dcc074` (CI red, test-only) to `4b5c183`.
- **1.23.0** (2026-09-22): reviewed OpenClaw agent-skills 0.1.0. Added `handoff` (MIT adaptation);
  autoreview imports upstream through `711711b8` minus the TruffleHog removal (#240, #244) and
  the Astra usage guidance; `mneves-verify` gains source-blind behavior checks and fake-work
  probes. Skipped: readme-standard, crabbox, beam, session-viewer, agent-transcript (tied to
  OpenClaw repos or services).
- **1.22.0** (2026-09-22): Codex execution, orchestration and review on `gpt-6-sol` `high`;
  `gpt-6-astra` `high` only as plan advisor for the Claude (Opus) main session. autoreview Codex
  default `gpt-6-sol`, access-only retry `gpt-6-luna` `xhigh`. Probes: `gpt-6-sol` answered at `high`
  and `xhigh`, `gpt-6-luna` at `xhigh`; a fake id is rejected (400). Host aligned (codex config, agent TOMLs, codex-auto, zshrc,
  agent-runtime.md, delegate-wave).
- **1.21.0** (2026-09-22, tag `v1.21.0`): Claude main seat moves from Fable to Opus (`opus`, which
  resolves to `claude-opus-5-5` on Claude Code 2.1.280); autoreview's `claude` engine defaults to
  `claude-opus-5-5`. The skill keeps the name `mneves-fable-orchestrator` so installs and references
  keep working. Host `agent-runtime.md` row updated; `~/.agents/skills/autoreview` (a copy, not a
  link, shared by the Claude and Codex skill links) re-synced from this repo.
- **1.20.0** (2026-09-22): `codex-lane fork` (A/B from one executor state) and the CI guard that
  keeps model ids inside the orchestrator's Defaults block with a verified-on date. Host config
  (`~/bin/codex-auto`, `~/.codex/agents` review roles, `agent-runtime.md`) aligned to Astra
  high for advice/review. Tags `v1.19.0` and `v1.20.0` pushed; `v1.10.0`–`v1.18.1` were never
  tagged on the remote although the changelog links them.
- **1.19.0** (2026-09-22): review against 2026 guidance. Claude seats in the orchestrator Defaults
  read "latest release" (`fable`, `opus` aliases) because "Opus 5.1" never existed; Codex seats
  keep 1.18.1 routing (Sol xhigh executes, Astra high orchestrates/advises/reviews). Frontmatter
  is spec-only (`skills-ref` rejects unknown keys) and executable skills carry `compatibility`.
  `codex-lane next` reports a refused resume; `codex-lane.test` runs against a fake `codex` in CI.
  Codex reads skills from `.agents/skills`, not `~/.codex/skills`.
- **1.18.1** (2026-09-12): Astra back to `high` for orchestration, advice and review (autoreview default high); Sol `xhigh` executes; a Codex session's model decides whether it orchestrates or executes.
- **1.18.0** (2026-09-12): orchestrator routes main = Fable 5.1 | Astra xhigh, frontend = Opus 5.1, heavy executor = Sol xhigh, reviewer = Astra xhigh; autoreview Codex default rises to Astra xhigh.
- **1.15.0 beta candidate** (2026-09-07): adds portable MIT-licensed `autoreview`, with Astra medium and access-only Sol xhigh fallback. The complete helper and tests are maintained here; installation needs no external upstream checkout.
- **1.14.0** (2026-09-07): added the MIT-licensed `imagegen-frontend-mobile` adaptation; Codex routing defaults to GPT-6 Astra at `high` for execution, planning, review, and inherited agents; skill descriptions are concise and launcher mechanics live in a conditional reference.
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
- Skills: `autoreview`, `imagegen-frontend-mobile`, `mneves-agent-readiness`, `mneves-eli5`, `mneves-expert-review`,
  `mneves-fable-orchestrator` (ships `codex-lane` + `codex-lane.test`), `mneves-superaudit`,
  `mneves-teach-back-srs`, `mneves-verify`.
- `tools/` is a Bun + TypeScript project with no external runtime deps; dev deps only (Biome,
  TypeScript, bun-types).

## Decisions that still bind

- **Naming and provenance.** Original skills use the `mneves-` prefix. Adapted third-party skills
  retain their upstream name, compatible license, copyright, and source. Directory name and
  frontmatter `name:` must match.
- **Skills are Markdown-first.** `autoreview` ships an isolated review CLI and its tests;
  `mneves-teach-back-srs` ships `srs_db.py`; `mneves-fable-orchestrator` ships `codex-lane`.
  These are distinct from the repository's `.githooks/pre-commit` guard. New skills should
  stay machinery-free unless a real executable is the point.
- **`VERSION`, the README badge, and the top `CHANGELOG.md` entry must agree.** Single source is
  `VERSION`.
- **The repo guards itself with ast-grep.** `rules/no-as-any.yml` rejects `as any` in TypeScript
  and `rules/no-as-any-tsx.yml` rejects it in TSX; `.githooks/pre-commit` enforces both and
  fails closed when ast-grep is absent. `unknown` + a narrowing guard is the sanctioned
  replacement.

- **Frontmatter stays on the Agent Skills spec.** CI runs `skills-ref validate`, which errors on
  any key outside `name`/`description`/`license`/`compatibility`/`metadata`/`allowed-tools`.
  Host-only fields (`context: fork`, `effort`, `paths`) are attractive but break the gate; the
  independence `mneves-verify` needs is stated in prose, not frontmatter.
- **A superseded in-flight routing change lives in `git stash` (2026-09-22)**, not in history:
  "Sol everywhere" was tried, then rejected in favour of Sol-executes / Astra-reviews.

## Lessons paid for

- **A model version in prose can be fiction.** 1.17.0–1.18.1 shipped "Opus 5.1" in the Defaults
  block and HOWTO; no such model existed. Name Claude seats by alias ("latest release") and
  check vendor model lists on every release.

- **README badge drift.** 1.4.0 shipped with the badge still pinned at 1.2.0 while `VERSION`
  read 1.3.0. Any version bump is three places, not one.
- **A skill is its description.** The frontmatter `description:` is the routing trigger agents
  read before loading anything; a description that doesn't name when-to-use makes the skill
  undiscoverable.

- **Shipped text must work from a stranger's clone.** 1.7.0 baked `~/dev/GUIDELINES-REF` into a
  skill's frontmatter `description:`; every installing agent was told to read a directory only
  the maintainer has. The public-repo scan is: no home paths, no machine layout, no client names.

## Known gaps

- Changelog links for 1.1–1.5 and 1.10–1.18.1 point at tags that do not exist on the remote
  (only v1.6.0–v1.9.0, v1.19.0, and v1.20.0 are tagged, checked 2026-09-22 with `git ls-remote`).
- `mneves75.github.io` (user site) does not exist as a repo; linking this project from it needs
  that repo to be created first.
