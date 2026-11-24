# Catalog Consolidation & v2.0.0 Hardening Progress

- **Branch:** `feat/v2-consolidation` (base: `origin/main` `852261b` / `v1.52.2`)
- **Target Version:** `2.0.0`
- **Plan:** [`docs/specs/catalog-consolidation/plan.md`](plan.md)
- **Machine-readable status:** [`docs/specs/catalog-consolidation/tests.json`](tests.json)

## Session Log

### 2026-11-24 — Phase 3 Consolidation, Upstream `pstack` Refresh & V3 Hardening
- Cherry-picked Phase 1 (`28d3124`), Phase 2 (`fcfc1a8`), and DeepSeek disablement (`f610a8c`) onto `feat/v2-consolidation` off `v1.52.2` (`852261b`).
- Audited upstream `cursor/plugins/pstack/skills` (`0.15.36 -> 0.15.48`) and `pstack-claude` (`0.9.128 -> 0.9.153`); pinned `sources.json` to `pstack-claude@66181d3` (`0.9.153`) and `cursor/plugins@0b46ec3` (`0.15.46`), excluded `poteto-mode/references/dsh-tools.md` (DeepSeek disabled), rebased adaptations `01`–`11`, and added `12-upstream-reframe-and-hygiene.patch` (importing explicit-only `/reframe` from `0.15.48`, tightening `typescript-best-practices` and `how` descriptions, and aligning `poteto-mode/worker.md` with local-only autonomy).
- Retired 3 negative-lift root skills (`mneves-superaudit`, `mneves-socratic-tutor`, `mneves-eli5`: `25 -> 22` root skills) with owner approval waiving a separate deprecation window for `v2.0.0` (historical single-scenario Phase 2 baseline-delta observations pinned at `fcfc1a8`).
- Slimmed heavy `SKILL.md` bodies behind 1-level-deep `references/`: `mneves-security` (137L), `mneves-ship-deploy` (`references/phases.md`), `council` (`references/invocations-and-prompts.md`), `untangle-codebase` (`references/checklists.md`), and `babysit-pr` (`references/pr-wait-and-limits.md`).
- Integrated Hardening Protocol V3 and upstream `pstack` discipline into `mneves-verify`, `mneves-ship-deploy`, `mneves-production-readiness`, `mneves-fable-orchestrator`, and `mneves-expert-review`.

### 2026-11-24 — Parallel Codex `improve` + `code-review` (Standards & Spec), Fixes, `mneves-prune-tests`, & Live Codex Catalog Eval
- Ran 3 independent read-only Codex (`gpt-6.2-sol` high) review passes (`improve`, `code-review` Standards, `code-review` Spec) against `origin/main..3b770ce` and fixed every confirmed finding:
  - **Shared frontmatter & complexity reduction:** extracted `tools/scripts/frontmatter.py` (deduplicating 3 parsers + adding duplicate-key diagnostics) and decomposed `check_repo` (`80 -> 10`), `summarize` (`52 -> 28`), `validate_cases` (`42 -> 5`), and `command_run` (`39 -> 24`). `cccc 1.8.0 --no-cache --min 0` across all 5 Python files: max cognitive `28`, median `6`, `0` parse errors.
  - **Eval security & integrity:** enforced filename-safe IDs, output-dir path confinement, enumerated root skill resolution, disjoint `expected`/`forbidden` validation, strict judge JSON validation, non-empty run checks, counterbalanced 50/50 A/B assignment in `baseline-delta-eval.py`, and isolated Codex `cwd` + `-c project_doc_max_bytes=0`.
  - **Hygiene & installer hardening:** added reference-style/nested link + direct-reachability checks and consistent missing-`skills/` schema in `check-catalog-hygiene.py`; checked usable `SKILL.md` in `install-skills.py` and rejected missing explicit `include` paths.
  - **DeepSeek removal completed:** removed `DEEPSEEK_API_KEY` from `autoreview`'s Pi forwarding allowlist (with regression assertion), removed retired economy-fallback text from `skills/mneves-fable-orchestrator/README.md` and `HOWTO.md`, and rebuilt `site/`.
  - **Skill boundaries & docs:** restored pre-promotion staging health recheck and pre-tag proof ordering in `mneves-ship-deploy`, restored lead read-only boundary in `council`, restored `## Deploy gate` anchor in `mneves-security`, folded `v1.52.2` (`852261b`) into `docs/readiness/ledger.md`, updated `PRODUCT.md`, `AGENTS.md`, `FOR_YOU_KNOW.md`, `collections/pstack/README.md`, and `codex-dispatch.md`, and restored positive `/sharpen` in `cases-hard.json` (13 cases).
  - **`pstack` REST watcher fix (`13-watch-pr-app-identity.patch`) & CI:** preserved GitHub app/workflow identity in `watch-pr/cloud-reader.ts` deduplication with a two-app regression test, resynced all 43 `collections/pstack` skills, wired `watch-pr` typecheck + tests into `.github/workflows/ci.yml`, and verified **279/279 PASS**.
- **`mneves-prune-tests` audit:** reviewed all 15 new/modified first-party test methods; 0 pruned (15/15 guard distinct contracts/planted violations; 0 unit tests added for `cccc <= 5` non-regex functions).
- **Live Codex (`gpt-6.2-sol` high) `catalog-eval.py`:** **24/24 PASS** on 22 root skills and **13/13 PASS** on 65 combined root+pstack skills (`0` fails, `0` forbidden hits, `0` errors).

## Release Gate Provenance
- Tracked files describe the `v2.0.0` candidate tree only. Binding exact-candidate results for the live 2-consumer `tools/scripts/routing-eval.py run` (with `--baseline`), `mneves-security` deploy gate, `mneves-production-readiness` gate, and independent acceptance live in the private `.scratch/` gate records and the `v2.0.0` annotated tag message per `CONTRIBUTING.md`.
