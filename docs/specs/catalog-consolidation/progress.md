# Catalog Consolidation & v2.0.0 Hardening Progress

- **Branch:** `feat/v2-consolidation` (base: `origin/main` `852261b` / `v1.52.2`)
- **Target Version:** `2.0.0`
- **Plan:** [`docs/specs/catalog-consolidation/plan.md`](plan.md)
- **Machine-readable status:** [`docs/specs/catalog-consolidation/tests.json`](tests.json)

## Session Log

### 2026-11-24 — Phase 3 Consolidation, Upstream `pstack` Refresh & V3 Hardening
- Cherry-picked Phase 1 (`28d3124`), Phase 2 (`fcfc1a8`), and DeepSeek disablement (`f610a8c`) onto `feat/v2-consolidation` off `v1.52.2` (`852261b`).
- Audited upstream `cursor/plugins/pstack/skills` (`0.15.36 -> 0.15.48`) and `pstack-claude` (`0.9.128 -> 0.9.153`); pinned `sources.json` to `pstack-claude@66181d3` (`0.9.153`) and `cursor/plugins@0b46ec3` (`0.15.46`), excluded `poteto-mode/references/dsh-tools.md` (DeepSeek disabled), rebased adaptations `01`–`11`, and added `12-upstream-reframe-and-hygiene.patch` (importing explicit-only `/reframe` from `0.15.48`, fixing Phase 2 cross-catalog false-fire descriptions in `typescript-best-practices` and `how`, and aligning `poteto-mode/worker.md` with local-only autonomy). Synced 43 `collections/pstack` skills cleanly (`agentskills validate` 43/43, `sync-pstack.test` 64/64, `statechart-runner.test` 10/10).
- Retired 3 negative-lift root skills (`mneves-superaudit`, `mneves-socratic-tutor`, `mneves-eli5`: `25 -> 22` root skills).
- Slimmed heavy `SKILL.md` bodies behind 1-level-deep `references/`: `mneves-security` (137L), `mneves-ship-deploy` (`references/phases.md`), `council` (`references/invocations-and-prompts.md`), `untangle-codebase` (`references/checklists.md`), and `babysit-pr` (`references/pr-wait-and-limits.md`).
- Integrated Hardening Protocol V3 and upstream `pstack` discipline into `mneves-verify`, `mneves-ship-deploy`, `mneves-production-readiness`, `mneves-fable-orchestrator`, and `mneves-expert-review`.
- Updated `VERSION` (`2.0.0`), `CHANGELOG.md`, `README.md`, `AGENTS.md`, `HOWTO.md`, `NOTICE`, `FOR_YOU_KNOW.md`, `MEMORY.md`, `docs/skill-ledger.md`, `docs/skill-routing.md`, `docs/usage-efficiency.md`, `collections/pstack/README.md`, `tools/install-profiles.json`, `tools/catalog-eval/*.json`, `tools/routing-eval/cases.json` (rev 13: 36 cases, 94 anchors), and rebuilt `site/`.
- Fixed `.githooks/pre-commit.test` cleanup trap (`chmod -R u+w` before `rm -rf`) to prevent interactive prompt hangs on read-only `.git/objects/` files when stdin is a tty.
- Ran `cccc 1.8.0 --no-cache --min 0` across all 10 changed Python/TS source files (`0` parse errors). Flagged duplicated `parse_frontmatter` / `parse_description` across 3 Python scripts and high cognitive complexity in `check_repo` (`80`), `summarize` (`52`), `validate_cases` (`42`), `command_run` (`39`) for the `improve` + `code-review` pass.

## Pending Steps
1. Record final deterministic test results from running suite (`task-935`) and Astra re-check (`task-937`).
2. Checkpoint commit on `feat/v2-consolidation` so `git diff origin/main...HEAD` covers the full `v2.0.0` change.
3. Run `improve` (branch scope) + Matt Pocock `code-review` (parallel Standards + Spec axes) using Codex (`gpt-6.2-sol` high) and fix every genuine issue (respecting `cccc <= 5` no-new-unit-test rule unless regex).
4. Run `mneves-prune-tests` on changed/added test suites.
5. Run Codex-side live `catalog-eval.py run` (24 root + 12 hard 65-skill) and `routing-eval.py run` (36 cases + baseline `852261b`).
6. Run independent fresh-context `mneves-verify` via Codex (`gpt-6.2-sol` high) until 100% PASS.
7. Push PR, verify all 4 GitHub Actions CI jobs green, run exact-candidate `mneves-security` + `mneves-production-readiness` deploy gate assessments, and check Claude consumer quota before any production merge/tag via `tools/scripts/deploy.sh`.

## Evidence Limits & Active External Blockers
- **Claude consumer quota:** All 4 logged-in Claude accounts in `claude-auto --status` are at 100% 7-day limit (`berlin` resets Tue 24 Nov 22:00). Until Claude quota resets (or the owner explicitly waives the Claude half in writing), the live 2-consumer `routing-eval.py run` required by `CONTRIBUTING.md` can only execute the Codex consumer half; production merge/tag remains strictly gated and must not be bypassed.
