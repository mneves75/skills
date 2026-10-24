# Council and security-audit integration

This ExecPlan is a living document. Update `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` as evidence changes. A new contributor must be able to resume from the repository and this file.

## Purpose / Big Picture

Add two useful, portable procedures to the default Agent Skills catalog: bounded independent plan deliberation through Kitze's Council idea, and Cloudflare's deep source-security audit harness. Keep `mneves-security` as the remediation/privacy/deploy-gate owner and the orchestrator as the general delegation router. The catalog becomes seventeen skills at version 1.40.0.

The observable result is that `npx skills@latest add . --list` discovers `council` and `security-audit`; Council can produce a real or explicitly un-counciled plan without fake replies, and Cloudflare's two validator suites pass alongside all existing repository gates. No staging target exists. `site/` publishes to GitHub Pages from `main`, so a production-triggering merge requires the exact-candidate release gates and approval.

## Progress

- [x] (2026-10-23) Read both pinned upstreams, licenses, current CLI help/official docs, local guidance and existing security/orchestration contracts.
- [x] (2026-10-23) Verified `main == origin/main` at `b72fadd`, preserved unrelated untracked `docs/handoffs/`, and created `feat/council-security-audit`.
- [x] (2026-10-23) Ran upstream Cloudflare tests on Node 26.12.1: 34 findings tests and 31 coverage tests passed; both validators passed syntax checks.
- [x] (2026-10-23) Added `skills/council/` with MIT provenance, bounded independent protocol, private sessions and three capability-checked adapters.
- [x] (2026-10-23) Added `skills/security-audit/` with complete upstream companions, schema, validators, tests, MIT provenance, one-level references and the `mneves-security` route.
- [x] (2026-10-23) Complete catalog, generated site, release metadata and CI/docs alignment.
- [x] (2026-10-23) Structural gates: skill layout, `skills-ref validate` on all 17 skills, `npx skills add --list` discovery, both Cloudflare suites (34 + 31 tests), `ast-grep`, Python syntax, `build-site.sh` + `build-site.test` (38 controls), defaults guard + its planted controls, readiness catalog + its 14 planted violations, Python and Node package tests, hook, `codex-lane`, ship-deploy contract (173 tests), release guards, SRS, render AST and starters (8 + 10 tests), autoreview (345 tests), `sync-pstack.test` (39 checks).
- [x] (2026-10-23) Real-browser check of the seventeen-card site at 1440x900 and 390x844, including the copy control's three scenarios and both new guide anchors.
- [ ] Adversarial review of the frozen candidate and independent verification; fix confirmed findings.
- [ ] Commit/push the candidate, inspect CI, complete exact-candidate security/readiness and production approval, then merge/tag/deliver and clean only task-owned scratch/branches.

## Surprises & Discoveries

- The Council upstream's plain `claude -p` and prompt-only OpenCode claims are not a sufficient read-only boundary. Current Claude has restricted/tool controls; Codex has an explicit read-only sandbox; Cursor has Plan Mode plus sandbox.
- Codex 0.164.0 rejects `--ask-for-approval` after `exec` but accepts `codex --ask-for-approval never exec ...`; the active command was corrected and checked.
- Gemini's official Plan Mode documentation says non-interactive exit automatically switches to YOLO. That upstream adapter is therefore not shipped.
- A sanitized Council run initially risked pointing Cursor back at the repository. `CONTEXT_DIR` now separates the authorized/sanitized invocation workspace from project identity.
- Cloudflare's actual package is nested at `skills/security-audit/`, not the repository root. Its source includes 34 findings tests and 31 coverage tests; both passed unchanged.
- The independent plan-advisor subagent failed before advice with a provider 429 quota error. No independent advisor opinion is claimed.
- `1.39.0` was already claimed by open PR #26, an unrelated skills-review release at `6649bc9`. Two candidates cannot share a version, tag or changelog heading, so this work is numbered `1.40.0`; the branch that lands second renumbers and regenerates the site.
- `tools/` has 10 failing `bun test` cases (`bounds git/find/find/grep/ls: fast|slow`) on this macOS host. The identical 10 fail on a clean worktree at `origin/main` `b72fadd`, so they are pre-existing and not caused by this change; CI runs them on Ubuntu, where the merged 1.38.0 checks were green. They stay out of scope and are reported.
- The landing page carried two stale `Fifteen` claims (hero intro and meta description) that no gate checks. A browser render found them; both now read seventeen.
- 17 of the 20 Cloudflare files were byte-identical to the pin; the adversarial review found an inherited contradiction between the Phase 5 dispatch and the completion condition for `rejected` records, so one reference file was corrected and 16 of 20 stay byte-identical.
- The adversarial review on the Codex seat found that no Council adapter confines reads to the working directory: Cursor's documented default is system-wide read, and Codex's read-only sandbox removes writes, not reads. The skill now states independence as a protocol obligation with each adapter's real read scope, and names Cursor's argument-vector exposure.
- The same review found the fallback trigger worded so that one unavailable primary seat could read as sufficient; it now requires that no authorized primary seat for that role can run and records each failure.
- A3 (upstream gap, not fixed here): both validators accept an empty ledger and an empty `findings.json`, so they cannot prove a run did the work. Adding a strict completion mode (`--require-complete`, plus a cross-check that every `candidate` fingerprint reached `findings.json`) would fork the pinned validators and their 65 tests; the procedure states the limitation instead and the change is proposed upstream before it is adopted here. The strongest rejected alternative is a local strict wrapper script, which duplicates the validators' parsing and would drift from them.

## Decision Log

- Decision: add two attributed packages instead of folding both into existing skills.
  Rationale: Council and Cloudflare have distinct procedures and tested assets. Folding them into `mneves-fable-orchestrator`/`mneves-security` would create a large hard fork and obscure MIT provenance. The strongest rejected alternative is a single integrated security/orchestration procedure; it has fewer entrypoints but more coupling and maintenance risk.
  Date/Author: 2026-10-23 / main session.
- Decision: enable only Claude, Codex and Cursor Council adapters; skip Gemini, Grok and OpenCode unless a safe current configuration is proven.
  Rationale: supported read-only behavior must be real, not prompt-only. Gemini's headless transition is explicitly unsafe for this use. The rejected all-six copy preserves more upstream surface but violates the stronger safety requirement.
  Date/Author: 2026-10-23 / main session.
- Decision: move Cloudflare Markdown companions to `references/` while preserving upstream ledger basenames.
  Rationale: the repository requires one-level reference links and no reference-to-reference chain. Stable basenames avoid invalidating prior-run coverage IDs; validators and tests need no semantic rewrite.
  Date/Author: 2026-10-23 / main session.
- Decision: keep `mneves-security` remediation and deploy verdicts separate from Cloudflare's read-only full audit.
  Rationale: the two workflows are complementary. Optional routing gives single-skill installs a complete fallback without duplicate audits or a new required dependency.
  Date/Author: 2026-10-23 / main session.
- Decision: release as 1.40.0 without changing model assignments.
  Rationale: two new skills are a minor feature. Official Claude and OpenAI model catalogs were checked on 2026-10-23; only the orchestrator's verified-on date advances.
  Date/Author: 2026-10-23 / main session.
- Decision: number this release 1.40.0 and leave 1.39.0 to open PR #26.
  Rationale: the two candidates are unrelated and one already owns the version, its changelog heading and its tag plan; shipping a second 1.39.0 would make the tag ambiguous. The strongest rejected alternative is rebasing this work onto PR #26 for a single combined release: fewer merges, but it makes a new feature hostage to owner-only waivers on a different change and mixes two evidence trails.
  Date/Author: 2026-10-23 / main session.
- Decision: add one local fallback lane to the orchestrator Defaults block instead of leaving the host to substitute silently.
  Rationale: work must continue when no primary seat can run, but an unreported substitution destroys the link between evidence and model. The rejected alternative is prose-only advice with no id in the block, which contradicts the invariant that ids live in exactly one place.
  Date/Author: 2026-10-23 / main session.

## Context and Orientation

`skills/<name>/SKILL.md` is each installable entrypoint. `README.md` and `NOTICE` carry attribution. `HOWTO.md` generates `site/howto.html`; `site/index.html` is hand-written except generated changelog rows. `VERSION`, the README badge and the top `CHANGELOG.md` entry must agree. The orchestrator's model IDs/tiers live only in its Defaults block and its verification date must match the release date.

Upstream source pins:

- Council: https://github.com/kitze/council at `1a3c7c303fd4ee671d7c4e2fabfd43d213aba115`; SKILL content from `7b6976c1c09b4c10ea53aadf22150f2abaf7118d`; MIT.
- Cloudflare: https://github.com/cloudflare/security-audit-skill at `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8`; actual package `skills/security-audit/`; MIT.

Public upstream clones used for inspection live only in ignored `.scratch/upstream/` and are task-owned cleanup material. Existing untracked `docs/handoffs/` is unrelated and must not be staged.

## Plan of Work

Preserve Council's exact-round independent replies, own-history-only continuation, faithful objections and final plan. Add provider/privacy/host boundaries, private unique sessions, bounded rounds/prompts/runtime, supervised process cleanup, explicit failures and solo fallback. Active commands are limited to capability-checked Claude restricted read/search tools, Codex read-only sandbox with global approval disabled and ephemeral output, and Cursor sandboxed Plan Mode without trust/force/auto flags. Other CLIs skip explicitly; no Gemini auto-YOLO command is shipped.

Preserve Cloudflare's six phases, coverage/prior-run/budget contracts, three verdicts, independent candidate/final verification, sandbox/write isolation, schema and both validators/tests. Add spec metadata, direct reference map, output authorization, and the optional relationship with `mneves-security`. Do not weaken a validator or test to make the package fit.

Update the orchestrator route, catalog/counts/cards/HOWTO/usage-efficiency, CI, AGENTS, NOTICE, PRODUCT, FOR_YOU_KNOW, MEMORY, VERSION, badge and changelog. Regenerate site outputs. Keep the visual design unchanged.

## Concrete Steps

From the repository root:

    node skills/security-audit/validate-findings.test.cjs
    node skills/security-audit/validate-coverage-ledger.test.cjs
    node --check skills/security-audit/validate-findings.cjs
    node --check skills/security-audit/validate-coverage-ledger.cjs
    npx -y skills-ref@0.1.5 validate skills/council
    npx -y skills-ref@0.1.5 validate skills/security-audit
    npx skills@latest add . --list
    tools/scripts/build-site.sh
    bash tools/scripts/build-site.test
    bash tools/scripts/check-defaults-block.sh
    bash tools/scripts/check-defaults-block.test

Then run every applicable command in root `AGENTS.md`, including tools typecheck/lint/tests, shell and hook tests, codex-lane fake e2e, release/readiness/SRS/defaults/catalog gates, ast-grep, autoreview tests, and render checks where installed. Use fake CLIs for Council protocol tests without provider calls. Inspect local site renders at desktop, tablet and mobile widths with keyboard and reduced-motion checks.

## Validation and Acceptance

Accept only when both packages are spec-valid/discoverable, correctly licensed and self-contained with fallbacks; Council cannot emit fake success or unsafe active flags; Cloudflare's suites and planted invalid cases pass/fail as designed; the existing security/deploy contracts remain intact; all catalog/site/version surfaces agree; and documented repository checks pass.

Run `cccc` on supported changed source when installed and record version/config/coverage/diagnostics/status. Run independent adversarial review, the requested improve deep pass and Matt Pocock code-review standards/spec axes on a frozen diff. Verify findings before fixing. Run `mneves-verify` in a fresh independent context against these criteria; a required unavailable independent/different-model verifier is BLOCKED, never a self-issued PASS.

Before production, run exact-candidate security/readiness gates and inspect CI. Present repository, commit, version, GitHub Pages target, risks and rollback for the exact approval required by `mneves-ship-deploy`. No beta/staging deployment is claimed because none exists.

## Idempotence and Recovery

Local edits and the feature branch are reversible. Upstream scratch clones can be removed and recreated from their public pins. Never overwrite the unrelated handoffs, force-push, rewrite history, move an existing tag, or delete another agent's scratch/worktree. If a gate fails, fix the in-scope cause and rerun the focused check before the full suite. If production approval or an external gate is unavailable, stop at the verified candidate and report the exact blocker.

## Artifacts and Notes

Upstream baseline on 2026-10-23, Node 26.12.1:

    validate-findings.test.cjs: 34 tests, 34 pass, 0 fail
    validate-coverage-ledger.test.cjs: 31 tests, 31 pass, 0 fail
    node --check on both validators: pass

Current CLI flag checks:

    codex --ask-for-approval never exec --help: accepted
    claude --restricted --strict-mcp-config --tools Read,Grep,Glob \
      --permission-mode dontAsk --permission-prompts none \
      --no-session-persistence --help: accepted
    cursor-agent --mode plan --sandbox enabled --help: accepted

The plan-advisor subagent returned a provider 429 before producing advice. This is an explicit independent-evidence gap, not a successful review.

## Interfaces and Dependencies

No npm dependency, package lock, application framework, model pin, or staging provider is added. Council needs Bash and at least one authenticated supported CLI. Cloudflare full audits need parallel subagents, Node.js for validators and an OS-enforced sandbox for target-controlled execution; missing execution capability becomes `needs_validation`. Optional siblings never become silent requirements.

## Outcomes & Retrospective

Implementation is in progress. The final entry must name actual checks, independent verdicts, commit/CI/live evidence and any remaining blocker; no completion or production claim is made yet.
