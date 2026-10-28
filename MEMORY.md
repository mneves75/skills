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

- **1.42.0** (2026-10-28, PR #29): ledger consistency guard, release closeout procedure
  (`docs/specs/release-closeout/spec.md`), honest readiness-check docs (RC-A-01, Medium,
  pre-existing), three skill-text hardenings and the Dependabot `bun` fix. The owner chose a
  fresh full security audit before merge, and waivers for the nine open controls to
  2027-01-25T23:59:59Z. The binding result lives in the private gate records and the `v1.42.0`
  tag message, and its ledger bookkeeping goes into the next release PR.
- **1.41.0** (2026-10-26, released and live): includes the unmerged 1.39.0 work,
  guideline corrections, readiness source checks and dead-code removal, hash-locked CI
  dependencies, the reference Agent Skills validator and CI-bound Pages publication.
  PR #28 merged on 2026-10-27 as `cc7285e`, whose tree equals the audited candidate `781922a`;
  main CI passed all four jobs, Pages published it, and all eight served URLs match the
  tracked bytes. The security gate is WAIVED (SEC-17, SEC-20, SEC-21, SEC-23, CMP-06) and
  readiness is `ready` under nine owner waivers (those five plus DEL-04, DEL-09, ASY-02,
  OPS-04) for this single release, expiring 2026-10-28T03:37:58Z; the controls stay open in
  `docs/readiness/plan.md`. On 2026-10-27 it had no tag yet (owner approval pending), so the
  documented rollback pointed at `v1.40.0`; the binding result belongs in that tag's message.
- **1.40.0** (2026-10-23; PR #27 merged as `b62072e` on 2026-10-24, published to Pages and
  tagged `v1.40.0`): adds the attributed `council` and
  `security-audit` packages, bringing the default catalog to seventeen skills. Council keeps
  exact-round independent deliberation but enables only capability-checked Claude/Codex/Cursor
  adapters and records unsupported members; Cloudflare's six-phase audit preserves its complete
  validators and tests. `mneves-security` retains remediation/privacy/deploy ownership and routes
  only explicit Cloudflare-style deep audits to the new sibling. The orchestrator routes explicit
  council requests and gains one local fallback lane that may be used only when no Claude or
  Codex seat can run. PR #26's 1.39.0 work never reached `main` on its own and shipped inside
  1.41.0. This file does not record the 1.40.0 gate or independent-verification results.
- **1.38.0** (2026-10-18, released and live): still fifteen default skills. The SLO and
  incident-learning procedures ship as guides in `docs/sre-guides/` plus eight prompts in
  `docs/sre-prompts.md`; the candidate skills `mneves-slo` and `mneves-incident-learning` were
  retired. Under `docs/specs/sre-workflows/spec.md`, a skill stays if it shows better
  behaviour than a competent prompt with no new wrong behaviour, or equal behaviour plus
  observed automatic discovery; with neither, its entrypoint is retired. Round 1 (first package contents, one bundled response per
  arm, source-blind scoring): baseline 8 met / 11 partial, candidate 13 met / 6 partial, one
  regression (an active-incident exception). Unnamed requests loaded the skills on Claude Code
  and Codex; standalone dashboard reads loaded neither. Round 2 failed SOURCE and BEHAVIOR;
  round 3, the one behavioural run against the corrected sources, scored baseline 14 met /
  5 partial and candidate 15 met / 4 partial (gains E2, E3, E13; regressions E9, E18, which
  stated absences as fact), so BEHAVIOR was FAIL. Round 4, after a source correction and a
  harness repair, scored 18 semantic cases: baseline 12 met / 6 partial, candidate 14 / 4;
  discovery and all eight non-trigger controls passed, but E2 and E10 added new unsupported
  claims and further answers asserted reliance, cause or measurement, so both skills failed
  retention and were retired. UI passed on a local preview whose seven site hashes equal the
  shipped bytes. Merged as `1f93ab1`, deployed to GitHub Pages with served bytes matching the
  gated tree, tagged `v1.38.0` and released; CI green before and after the merge. The security
  gate for `b95604c` is WAIVED (SEC-13, SEC-17, SEC-20, SEC-23, CMP-06) and readiness is `ready`
  under eleven owner waivers expiring 2026-10-25T23:59:59Z, recorded in
  `docs/readiness/ledger.md` and `.scratch/readiness/production.json`.
- **1.37.0** (2026-10-16): fifteen default skills, adding `mneves-production-readiness`, a deploy
  gate for data, recovery, money, operations, UX and maintainability (103 controls plus 32
  security and compliance rows imported from the `mneves-security` gate record). Release
  contract version 2 adds the readiness record (guarantee 11). Owner decisions: delta cadence,
  staging blocks on DM-02/DM-03/TST-05 only, production waives blocker and contract rows by
  name, readiness also runs on the dev stop.
- **1.36.0** (2026-10-16): closes the 1.35.0 gate waivers. F-01 (TOML prototype pollution)
  and F-02 (timeouts that left commands running) are fixed test-first and `tools/` gains
  `bun test` in CI; pages and the readiness report carry a meta CSP and load no third-party
  fonts; `SECURITY.md` documents access, a compromise runbook and data handling.
- **1.35.0** (2026-10-15): `mneves-security` gains a mandatory deploy gate (full audit of the
  exact candidate, PASS/BLOCK/WAIVED verdict record) and 32 launch controls whose IDs match
  the production-readiness catalog; `mneves-ship-deploy` and `mneves-verify` route to it.
  `mneves-ship-deploy` gains a dev stop (dev -> staging -> prod, `-alpha<N>` tags).
  Owner decisions: Critical/High blocks both targets, production waives every open launch
  control by name, full audit per new commit, gated rollbacks exempt, hotfix by waiver.
- **1.34.0** (2026-10-13): fourteen default skills, adding `mneves-security` with
  evidence-backed audit, authorized remediation and independent acceptance. The redesigned
  static catalog groups procedures by job, self-hosts typography and reports clipboard
  failures truthfully. The separate pstack collection has 36 skills; generation tests
  compare the catalog with source inventories and check guide landmarks/keyboard focus.
  Release and public verification evidence is tracked in PRs #13, #14 and #15.
- **1.31.0** (2026-10-04): pstack `tdd` is test-first by default (fourth local commit in the
  pstack-claude fork; `LOCAL-OVERRIDES.md` §6 there), and links to the fork's retired
  sections were repaired. The fork guards both with `tests/local-overrides.test.mjs`.
- **1.30.0** (2026-10-04): `collections/pstack` vendors 32 pstack skills from a local
  pstack-claude fork (`UPSTREAM` pins it; `tools/scripts/sync-pstack.sh` regenerates it). The
  default install still covers `skills/` only. pstack's `tdd` and `teach` keep their names by
  the owner's choice, colliding with Matt Pocock's.
- **1.29.0** (2026-10-02): twelve skills. `mneves-chatgpt-search` adds a portable
  official-guidance workflow for discovery, crawler access, citations and referral
  attribution, with training preferences and privacy preserved. Catalogs and HOWTO
  document the read-only, local-improvement and measurement modes. No ranking promise
  or new analytics dependency; repeated ChatGPT answers remain separate from API results.

- **1.27.0** (2026-09-30): ten skill entrypoints use conditional detail and bounded work.
  Portable Codex routing separates ordinary Sol/medium, bounded Luna/medium, difficult Sol/high,
  routine Sol/high review and explicit Astra/xhigh specialists. Autoreview's access-only retry
  is Astra/high; caller overrides and security controls survive. Fresh-shell SRS commands use
  the discovered absolute helper path. Documentation byte reductions are not measured usage savings.

- **1.26.0** (2026-09-29): every Codex `gpt-6-sol` seat is `gpt-6.1-sol` `high` (orchestrator main
  session, heavy executor, reviewer fallback, autoreview access-only retry, `amp` default).
  Review and plan-advisor seats stay `gpt-6-astra` `xhigh`. Host aligned: `~/.zshrc` `codex-advise`,
  `codex-auto` `exec_model` default (and `codex-auto-test`), `default_subagent_model` in
  `~/.codex/config.toml`, and the 20 `~/.codex/agents/*.toml` roles (id only; all already `high`).
  Not aligned: the `[notice.model_migrations]` record, which is Codex's own acknowledgment log.
  The Claude main-session and heavy-executor seats also move from `xhigh` to `high` (a trial;
  frontend stays on Opus in the skill defaults). Host aligned: `~/.claude/settings.json`
  `modelSettings`, agent-runtime.md and its routing probe.
- **1.25.0** (2026-09-28): the Claude main session and ordinary Claude subagents run Sonnet
  (`claude-sonnet-5-5`) at `xhigh`, with an Opus advisor; frontend stays on Opus. Codex seats
  are unchanged. Host aligned: `~/.claude/settings.json` (model, modelSettings, advisorModel,
  allowlist, subagent env), `frontend-engineer` agent, `impeccable-*` agents pinned to Opus,
  agent-runtime.md. The advisor stays inactive while `DISABLE_TELEMETRY`/`DO_NOT_TRACK` are set.
- **1.24.1** (2026-09-25): every review seat runs `gpt-6-astra` `xhigh` (autoreview Codex default,
  orchestrator reviewer and plan advisor); the `gpt-6-sol` `xhigh` retry is unchanged. Host aligned:
  `~/.zshrc` `AUTOREVIEW_CODEX_THINKING`, codex-auto review default, six Astra agent TOMLs.
- **1.24.0** (2026-09-25): review runs on `gpt-6-astra` `high`, with an access-only retry on `gpt-6-sol`
  `xhigh` (autoreview Codex default and orchestrator reviewer seat). Host aligned: codex-auto
  review default, reviewer/verifier/critic agent TOMLs, agent-runtime.md.
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

## Project Environment

From a read-only environment inspection on 2026-10-18 (an environment-inspector agent's
workspace-data scan plus source reading):

- Static GitHub Pages site in `site/`. No React Native, Expo, iOS or Android app, and no bundler.
- Build: `bash tools/scripts/build-site.sh` (generates `site/howto.html` and the landing
  changelog rows). Optional local preview:
  `python3 -m http.server 8000 --bind 127.0.0.1 --directory site`.
- `tools/` is the Bun workspace (readiness checker); see `AGENTS.md` Commands.
- Browser QA runs in an isolated browser, not a personal profile. There is no staging target;
  `.github/workflows/static.yml` publishes from `main` after CI passes on that commit; roll back
  with `gh workflow run static.yml -f ref=<earlier tag>`.

## Decisions that still bind

- **Collections are vendored, not ported.** A third-party pack that breaks the `skills/`
  invariants (TypeScript scripts, nested references, model ids) lives under `collections/` as a
  generated copy with its own license and pin. Rewriting it to the `skills/` rules would be a
  hard fork with manual syncs; regenerate from the source instead.
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

- **Frontmatter stays on the Agent Skills spec.** CI runs `agentskills validate` (the reference `skills-ref` from PyPI since 1.41.0; the npm package
  of that name is an unrelated demo), which errors on
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
- The previous release waivers expired on 2026-10-25T23:59:59Z. DEL-03, MNT-05 and SEC-13
  now have verified source evidence. The nine current production gaps are SEC-17, SEC-20,
  SEC-21, SEC-23, CMP-06, DEL-04, DEL-09, ASY-02 and OPS-04; the private exact-candidate
  decision packet holds their evidence requirements. Merge approval alone supplies no
  waiver reason or expiry. The reviewer-process deadline remains opt-in; provider retry
  ownership and a bounded process lifetime are separate claims.
