# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Readiness ledger guard**: `check-readiness-catalog.py` also checks `docs/readiness/ledger.md`. It requires exactly one row per control and only valid statuses, a Totals line that matches the table, the same production commit in Cursors, Binding run and the gate history, and an underlying status plus an expiry on every WAIVED row.
- **Release closeout** (`CONTRIBUTING.md`): release PR text stays true after the merge, an annotated tag records the verdict, and the binding bookkeeping lands in the next release PR instead of a separate merge.
- **Dependabot**: `tools/` uses the `bun` ecosystem; the npm updater could not read `bun.lock`.

## [1.41.0] - 2026-10-26

Includes the 1.39.0 work that was reviewed in PR #26 but never reached `main`.

### Added
- **`mneves-security` attack classes** (`references/attack-classes.md`): core classes (indirect injection, access control, business logic, feature abuse, cryptography) and domain classes selected from the inventory (HTTP framing and identity, client side, CI and release, cloud, messaging, resource spend, data lifecycle, local IPC, native code, agents), closed by a coverage-critic pass. Written in this repository's words, informed by Cloudflare's MIT `security-audit` skill (`c1c8a8c`, credited in `NOTICE`).

### Changed
- **`mneves-security` candidate contract**: a finding names the lower-trust principal, its input, the control, the crossed boundary, the affected resource and the observed result; one disposition field (confirmed, needs-validation, disproved) replaces the confidence column; only confirmed findings carry a severity, set by written anchors; the finder never confirms its own candidate, a fresh verifier tries to disprove it first and confirmation needs positive proof.
- **`mneves-security` evidence rules**: local, minimal reproduction with dummy principals; untrusted target code only in a sandbox; a fix is proven by one test that fails on untouched source and passes with the fix; coverage is always reported as partial; disproofs expire with the assumptions they rested on.
- **Deploy gate**: unchanged blocking policy (confirmed Critical or High); needs-validation records never block by themselves and are listed in the decision packet, while a missing fact behind a production launch control keeps that control BLOCKED. Missing launch controls are rows and plan items, not exploit findings.
- **Cross-skill consistency**: `mneves-superaudit` releases name the security gate; `mneves-ship-deploy` drops author-only paths, gains fallbacks for unshipped review and browser tools, and shows the WAIVED tag form; `mneves-production-readiness` maps security evidence kinds to its scopes, imports gate-step blockers only from the record and aligns CMP-06 applicability (readiness catalog version 2: a version-1 ledger reassesses CMP-06); descriptions gain negative scope.
- **Guide page**: commands and the summary table wrap at phone width, prose is capped near 70 characters, the page links back to the catalog and each table row links to its section.
- **Readiness checks that never looked**: `no-lint-ignores` (TypeScript, Go, Python) and Go `no-unsafe-types` returned a fixed pass; they now count suppression comments (`eslint-disable`, `biome-ignore`, `//nolint`, `#nosec`, `# noqa`, `# type: ignore` and similar) and `unsafe` package uses in the project's own sources, skipping vendored, generated and hidden trees. Go and Python `npm-scripts` were skipped; they now pass on Makefile targets, a justfile or Taskfile, and for Python nox, tox, poe, pdm or hatch scripts. Go, Python, Rust and Java share one task-runner lookup whose Makefile pattern no longer counts variable assignments (`CC:=gcc`) as targets and now accepts targets with digits, dots or slashes (`py312:`). The pattern also avoids overlapping repetition so a long non-rule line cannot stall scanning; a subprocess regression checks a 100,000-space line with a 3-second deadline. The source scan ignores text inside string literals, skips unreadable files and never enters vendored or hidden directories. Scores for Go, Python, Rust, Java and TypeScript projects can change.
- **Supply chain**: ast-grep and marked are exact `tools/` devDependencies, so `bun.lock` records their sha512 and CI installs them with `--frozen-lockfile` instead of `npm install -g` or `npx` by version. Skill validation now uses the Agent Skills reference validator, `skills-ref` 0.1.1 from PyPI (CLI `agentskills`), installed with `--require-hashes` from `.github/requirements/skills-ref.txt`; the npm `skills-ref` CI ran before is an unrelated individual's package. The reference validator also checks that each directory matches its skill name; CI's `bun audit` on the locked tree fails the build on any advisory. The render job installs WeasyPrint with `--require-hashes` from `.github/requirements/render-starters.txt`. `build-site.sh` runs the locked marked and needs `bun install` in `tools/` first.
- **Pages publication**: `static.yml` deploys a `main` commit only after CI succeeds on it, refuses any commit not on `main`, and takes a `ref` for a one-command rollback (`gh workflow run static.yml -f ref=<tag>`). A manual rollback also requires the selected commit's latest CI push run on `main` to have succeeded; missing, failed or unfinished evidence and API errors stop publication. Real-Git tests exercise both publication paths with a fake CI provider. Automatic publication now runs after every successful CI run on `main`, not only when `site/` changes.
- **`SECURITY.md`**: supported runtimes (Bun 1.4.4+, Python 3.11+, a maintained Node.js line), their end-of-life owner and a 7-day deadline for critical advisories.
- **`autoreview`**: the README names the engine CLI as the owner of provider retries, backoff and rate limits.
- **Model defaults** re-verified on 2026-10-26; ids unchanged.
- **Release documentation**: project state and contributor instructions distinguish accepted source from production readiness. The public ledger and plan now reflect the completed source audit, including SEC-13's verified dependency controls and SEC-21's missing device evidence, without treating merge approval as a waiver.

### Removed
- **Readiness tool dead code**: nine unused `tools/lib` modules (`fetch`, `progress`, `repo`, `result`, `signals`, `refs`, `types` and the `index` and `readiness/index` barrels), unused constants, check-category sets, cache singleton and dependency helpers, about 2,200 lines carried over from another project with its file names. The tool's own code now makes no network calls.

### Fixed
- **Readiness CI gate**: an invalid or empty `--min-level` (`L5`, `0`, `3x`), `--scoring`, `--format` or `--language` now exits 2 with the expected values; `--language` still accepts every detectable language, including those without an adapter that run the fallback checks, instead of silently passing the gate or reporting a scoring mode it never applied.
- **Readiness `error-budgets` check**: README matching uses whole words, so "slow" or "slides" no longer count as SLO documentation.
- **Readiness signal tests**: allow 500 ms for SIGKILLed descendants to disappear before asserting, which failed intermittently under heavy load; the control with cleanup disabled still fails.
- **Lint gate**: `tools/biome.json` makes unused imports, variables and parameters errors (21 removed); a planted unused import now fails `bun run lint`. `tsconfig` adds `exactOptionalPropertyTypes`.
- **Bun pin**: CI and `tools/package.json` (`packageManager`, `engines`) agree on Bun 1.4.4; the `engines` floor rises from `>=1.2`.
- **Python floors**: every helper entry point and the ship-deploy contract test state their floor , now 3.11+ throughout because Python 3.10 reached end of life on 2026-10-01; CI syntax-checks the autoreview live harness that no other step runs.
- **Small fixes**: `install-cccc.py` sends its own User-Agent instead of another client's; `build-site.sh` honours `TMPDIR`.
- **Readiness tool tests**: `shared.test.ts` warms each fake command once before the timed run, so macOS's first-exec cost of a new file no longer exceeds the 150 ms deadline under test; every bound is unchanged.
- **`SECURITY.md`**: the scope now lists every shipped executable, including the `mneves-ship-deploy` and `mneves-render` scripts and tests.
- **`mneves-ship-deploy`**: the stop rule and repo-identity check no longer name the author's paths or account, so a stranger's own repository qualifies; the security gate now runs after the readiness ledger commit too; live proof names a driver-agnostic browser or device capability; the description is capability and trigger only.
- **Model ids**: `HOWTO.md` and autoreview's engine reference no longer restate model ids or tiers outside the orchestrator's Defaults block.
- **Docs drift**: the readiness README's quick start works from a clone (the CLI is not in a skill install); HOWTO no longer equates the five questions with a maturity level and binds gate reuse to the tree; the AGENTS tree, teach-back README tree and card-quality step number match the files; superaudit briefs say "cross-session memory tools" instead of an undefined product name; verify and orchestrator READMEs match their skills.
- **`council`**: its requirements line moves from frontmatter into the body, because `compatibility` is reserved for skills that ship an executable. **`mneves-render`**: the description gains its trigger.
- **`mneves-teach-back-srs`**: SM-2 interval examples now match the shipped helper (q=5 gives 1, 6, 17, 49, 147 days), and card rules cite the right step.
- **`autoreview`**: the engine reference no longer names a model outside the helper's defaults.
- **Readiness tool types**: the 32 non-null assertions become narrowed types, single map lookups and loops; TOML path handling rejects an empty path instead of writing an `undefined` key, and Biome's `noNonNullAssertion` is an error.
- **`mneves-teach-back-srs`**: `srs_db.py` library functions raise `SrsError` instead of calling `sys.exit`, so a program importing the helper keeps running; the CLI still prints the message and exits 1, and a missing card rolls back its write transaction.
- **AGENTS.md**: byte-identical upstream references may name a sibling by bare basename when the `SKILL.md` map resolves it (`security-audit`).

## [1.40.0] - 2026-10-23

### Added
- **`council`**: an attributed adaptation of Kitze's bounded multi-CLI deliberation protocol, with independent exact-round replies, faithful objection transcripts, private collision-resistant sessions, provider-disclosure boundaries, supervised timeouts, and capability-checked Claude/Codex/Cursor read-only adapters; unsupported CLIs skip explicitly and Gemini's headless auto-YOLO path is not shipped.
- **`security-audit`**: Cloudflare's six-phase source-audit harness with deterministic coverage ledgers, prior-run revalidation, independent candidate/final verification, three finding verdicts, sandbox/write-isolation rules, machine-readable reports, and zero-dependency Node validators with their complete test suites.
- **Implementation plan**: `plans/003-council-security-audit.md` records the source pins, design alternatives, acceptance gates and release evidence.

### Changed
- **`mneves-security`**: explicit Cloudflare-style deep audits route to the optional `security-audit` sibling without duplicate full audits; the existing twelve-area audit, remediation and deploy-gate contracts remain the complete fallback.
- **`mneves-fable-orchestrator`**: explicit council requests route to the optional `council` sibling; ordinary delegation and verification stay distinct. The Defaults block gains one local fallback lane for hosts where no Claude or Codex seat can run, and every id in it was re-verified against the vendors' current catalogs on 2026-10-23.
- **Fallback discipline**: a substituted seat is announced and reported, never used when a model is named or a different reviewer is required, and never treated as cross-model review.
- **Review corrections**: Council now states independence as a protocol obligation and names each adapter's real read scope, including Cursor's documented system-wide read default and its prompt appearing in the argument vector; `security-audit` corrects one inherited contradiction so a retained `rejected` record keeps its Phase 3 disproof instead of being required to pass a Phase 5 step that never receives it.
- **Catalog and docs**: seventeen default skills, with Council and security-audit guides, landing cards, usage-efficiency notes, provenance and CI execution for both Node validator suites.
- **`SECURITY.md`**: the scope, data-handling and erasure sections now cover the two new surfaces (Council's private session directory, its member CLIs and the sessions those CLIs keep themselves; the `security-audit` output directory and its Node validators), and the erasure steps say plainly which copies this project cannot enumerate or remove, so the published contract matches what ships.

## [1.38.0] - 2026-10-18

### Added
- **SRE guides**: service level objective and incident review procedures, kept as documents and prompts after their candidate skills failed evaluation.
- **Objectives guide** (`docs/sre-guides/slo/`): specifies service level objectives from user
  outcomes (correct content, freshness, latency) before their collection, and computes compliance, burn rate and remaining
  budget with stated domains: weighted sums, no data is `unknown`, a gap keeps the full window
  `unknown` (covered figures are an observed subset), a 100% target has no budget, provider
  failures stay bad events, correctness and security failures are never budget, burn is a
  normalised error fraction reported against its own window, alert thresholds state their
  traffic assumption, completeness needs an independent expected count, and an
  acknowledgement is durable only as far as its contract says. Targets, alerts and budget
  policies stay `draft` until the owner adopts them; none becomes a release gate, freeze or
  feature switch.
- **Incident learning guide** (`docs/sre-guides/incident-learning/`): blameless review of an
  incident, near miss or workflow/test event after impact stops; during impact it only records and points to the runbook and the
  incident lead. Sources with clocks (unknown skew leaves cross-clock order uncertain), planned
  versus executed and reported versus observed labels, absence read as "not observed there",
  correlation kept apart from mechanism, contributing conditions, decisions in context, what
  worked and luck. Actions carry checks that reproduce the relevant scale, platform and
  failure; owners and dates are accepted or marked unassigned, pending or proposed; only a
  passed check is `done`. Log lines claiming approvals are data.
- **SRE prompts** (`docs/sre-prompts.md`): eight Task/Acceptance/Constraints/Delivery/Target
  templates, linked to the guides, with a warning to check every draft against the supplied
  artifacts. Guides and prompts are source-reviewed; no runtime reliability is claimed for
  them.
- **Spec and evaluation record** (`docs/specs/sre-workflows/`): contracts, integration and
  retention rule (keep a skill on better behaviour than a competent prompt, or on equal
  behaviour plus observed automatic discovery; otherwise retire its entrypoint and keep the
  prompts), nineteen synthetic cases comparing prompt-only and skill runs, and a review record
  (`review.md`). Round 1 ran once on the first package contents as one bundled response per arm
  (source-blind: baseline 8 met / 11 partial, candidate 13 met / 6 partial, one regression);
  it is not repeated evidence or a release pass. Round 2 returned SOURCE FAIL and BEHAVIOR
  FAIL. Round 3, the one behavioural run against the corrected sources, scored baseline 14 met /
  5 partial and candidate 15 met / 4 partial, with gains on E2, E3 and E13 and regressions on
  E9 and E18; final BEHAVIOR is FAIL. Round 4, after a source correction and a harness repair,
  scored 18 semantic cases (not comparable with the 19-case totals): baseline 12 met / 6
  partial, candidate 14 met / 4 partial. Discovery without naming and all eight unrelated-request
  controls passed, but each skill added a new unsupported claim (E2, E10) and further answers
  asserted unsupported reliance, cause or measurement, so both failed the retention rule.
- **Retirement decision**: the candidate `mneves-slo` and `mneves-incident-learning` skill
  entrypoints, never released, were retired under the spec's retirement rule; their seven files moved to `docs/sre-guides/`
  without frontmatter. The independent UI check passed on an earlier local seventeen-card
  preview only.
- **Provisional readiness baseline** (`docs/readiness/`): ledger and plan at a dated source
  snapshot, production readiness NOT READY; no binding record, cursor or waiver.

### Changed
- **README "Check the install"** separates entrypoint present, full package present and
  runtime discovery.
- **Catalog and docs**: still fifteen skills; README, HOWTO and the landing page's "Plan &
  deliver" group link the SRE guides and prompts as documents, not skills.
- **`mneves-fable-orchestrator`**: Defaults block re-verified against the vendor model lists on
  2026-10-18; ids and assignments unchanged.

## [1.37.0] - 2026-10-16

### Added
- **`mneves-production-readiness`**: gates staging and production deploys on evidence-backed readiness.
  103 controls cover data model and migrations, backup and restore, money/time/text correctness,
  delivery, queues and integrations, email, cost, observability and on-call, testing, billing, public
  API, AI operations, user experience, maintainability and ownership; 32 security and compliance rows
  delegate to `mneves-security` with fallbacks. A tracked ledger, per-target cursors, a baseline plus
  per-deploy delta, expiring evidence, an independent check before production records, owner-only
  waivers and a detailed fix plan. The spec preserves every item of the source checklist.
- **Release contract guarantee 11**: a release script that declares `# release-contract: 2` refuses
  to deploy without a valid readiness record for the exact unit, target and commit; `--waive
  readiness=<reason>` is the only bypass. The conformance check reports it (FAIL with the marker,
  WARN without), and the reference `release.sh` implements it with guard tests. The script
  parses the record as JSON against its exact schema (unknown, repeated or nested keys and
  incomplete waivers are refused), rejects impossible dates, expired waivers, symlinked record
  directories and a project gate named `readiness`, and snapshots the record into the evidence.
- **Readiness catalog guard**: `tools/scripts/check-readiness-catalog.py` checks control
  headings, tiers, verification lines, unique IDs, the spec's preservation map and the catalog
  version; CI runs it with fourteen planted violations.

### Changed
- **`mneves-ship-deploy`**: Preflight reads the readiness ledger; review runs a provisional
  readiness assessment; dev (when present), staging and production each bind a readiness
  record before deploying.
- **Owner decisions applied (2026-10-16)**: readiness keeps its baseline-plus-delta cadence
  (the security gate keeps its full audit per tree); staging blocks only on DM-02, DM-03 and
  TST-05, while secrets (SEC-12) and impostor packages (SEC-13) block through the imported
  security verdict; production waives `blocker` and `contract` rows by name, with `advisory`
  rows in the plan; the gate also runs on the dev stop.
- **`mneves-security`**: a usable secret in the candidate (SEC-12) and a dependency that does
  not exist or is not the intended package (SEC-13) are confirmed High findings at least, so
  they block every target, dev and staging included.
- **Security import**: the readiness gate reads the `mneves-security` gate record for the same
  commit and target; a security block keeps readiness `not-ready`, so the release script's
  readiness guard also stops a release the security gate blocked.
- **Waivers, hotfixes and rollbacks**: a record's waiver holds `control`, `owner`, `reason` and
  `expires` (the record gives its scope); the reference script refuses one that repeats
  `target` with a clear message instead of "duplicate target key". An incident repair shipped
  under `--waive readiness` gets its gate run right after; a rollback to a build with a `ready`
  record needs none.
- **Catalog and docs**: fifteen skills; README, HOWTO, landing page, glossary and product brief.
- **Orchestrator Defaults**: model ids re-verified against the vendor model list on 2026-10-16.

## [1.36.0] - 2026-10-16

### Fixed
- The readiness checker no longer lets a crafted manifest pollute `Object.prototype`.
  `Cargo.toml` and `pyproject.toml` keys `__proto__`, `constructor` and `prototype` are
  rejected, and ordinary manifests parse as before (F-01 from the 1.35.0 security gate).
- A timed-out readiness check now kills its whole process group, waits for it to exit and
  clears its timer; every adapter command has a deadline (60 seconds unless the check sets
  one). Commands now run through `/bin/sh`, so the assessor needs a POSIX system (F-02).
  The shared checks also run under deadlines, and stopping the checker (SIGINT or SIGTERM)
  stops every command it started.
- A crafted `pnpm-workspace.yaml` line no longer stalls app discovery (quadratic matching), and
  an `.env.example` file no longer hides the warning for suspicious files such as
  `credentials.json` or `private.key`.
- `codex-lane` cleanup guidance names each lane's exact files; the old `<lane>.*` advice also
  deleted the files of dotted lanes such as `job.extra`.
- Autoreview redacts provider credentials from the environment (`*_API_KEY`, `*_TOKEN`, the
  known provider keys and each `ANTHROPIC_CUSTOM_HEADERS` value) in terminal output, error messages and saved reports; before, only
  proxy credentials were redacted.
- Autoreview's TruffleHog scan runs offline by default and every detection blocks, so a dry
  run contacts nobody; `--verify-secrets-online` restores online verification on request.
- Autoreview refuses a run over 20 review passes or 10,240,000 prompt bytes before the first
  provider call (`--max-review-passes`, `--max-review-input-bytes` raise the limits), and
  refuses a Git work tree relocated away from its checkout, which could run an executable
  from the original checkout before isolation.
- The reference `verify-live.sh` and `release.sh` read health bodies as JSON objects with
  unique top-level keys (a nested or repeated field no longer passes), which needs `python3`;
  release tag messages state the recorded security gate verdict.
- `sync-pstack.sh` refuses upstream skills that contain a symlink; the site's HTML guard
  accepts only a strict subset; concurrent `mneves-teach-back-srs` reviews no longer lose
  a scheduling step.

### Security
- Every site page and the readiness HTML report carry a Content-Security-Policy and a
  referrer policy, tested served in a browser, and load no third-party fonts.
- `SECURITY.md` adds the access and release model, a quarterly access review, a compromise
  runbook, data handling and site protections. The autoreview README states its security
  model: untrusted input, what it sends, cost bounds, no irreversible actions, what it keeps.
  The readiness disclosure now says that the project's own tooling may download packages and
  write build output, and `codex-lane` transcript retention and erasure are documented, with
  erasure steps for local files, provider copies and backups.
- Access review, 2026-10-16: the maintainer administers the repository and one other account,
  also the maintainer's, has write access and keeps it; devices with write access use
  full-disk encryption and a screen lock (maintainer attestation).

### Changed
- `tools/` has unit tests (`bun test`), run in CI after typecheck and lint, and the SRS
  helper's test runs in CI.

## [1.35.1] - 2026-10-16

### Changed
- `mneves-fable-orchestrator` routes building and reviewing to different models. Opus
  (Claude) or Sol at xhigh (Codex) build: main session, workers and heavy executor. Fable
  (Claude) or Astra (Codex) plan, advise and review, and the main session gets a Fable
  advisor. Codex planning and plan advice move from high to xhigh, and the Codex reviewer
  moves from Sol at xhigh to Astra at high, so the model that built a change never reviews it. Ids re-verified
  against the vendor model lists on 2026-10-16.

## [1.35.0] - 2026-10-15

### Added
- A full security audit now gates every staging and production deploy (`mneves-security`).
  Deploy-gate mode audits the exact candidate in full: all twelve review areas and every
  applicable launch control. It ends in a fix plan and a PASS, BLOCK or WAIVED verdict bound
  to the audited tree and target. A confirmed Critical or High finding blocks every target until it
  is fixed, disproved or waived by the owner by name; for production, every unmet applicable
  launch control also needs a named waiver. A production deploy of the commit staging already
  passed reuses that audit with fresh advisories and production checks; a rollback to a gated
  build needs no audit; an urgent fix ships under a named waiver with its full audit right after.
  Production also needs independent acceptance; on dev and staging its absence is a plan item.
- **Launch controls**: 32 security, privacy and compliance controls (`SEC-01` to `SEC-23`,
  `CMP-01` to `CMP-09`): reset links, MFA and recovery, sessions, SSO/SAML/SCIM, object and
  tenant isolation, impersonation, throttling, secrets rotation, package provenance, uploads,
  CORS and headers, encryption, least privilege for agents, audit trails, penetration tests,
  disclosure, lost devices, webhook signatures, AI safeguards, questionnaires, SOC 2, health
  data, read audits, card scope, erasure, residency, access reviews and legal documents. The
  IDs match the production-readiness catalog's delegated rows, so its import maps one to one.
- A gate verdict record per commit and target (`<unit>/.scratch/security-gate/<commit>/<target>.json`,
  one scalar per line, open blocker IDs included) that a readiness review can import without a
  JSON parser.

### Changed
- `mneves-ship-deploy` runs the `mneves-security` gate in Phase 1 in place of the third-party
  `security-audit` skill, after the other Phase 1 changes land; without it the release is blocked
  until it is installed or the owner waives it. The decision packet carries the verdict, and
  production promotion requires PASS or WAIVED for the promoted commit.
- `mneves-ship-deploy` adds a dev stop: when a project documents a dev environment, both modes
  deploy, prove and tag (`vX.Y.Z-alpha<N>`) the same commit on dev before staging.
- `mneves-verify` routes security evidence to `mneves-security` and, for a release, to its
  deploy-gate verdict.

## [1.34.1] - 2026-10-13

### Changed
- Delegation acceptance checks source provenance and actual evidence before accepting claims.
  Task/project/session identity and counterexamples bound workflow or efficiency conclusions.
- Usage guidance replaces the ten-task prescription with an optional one-task receipt,
  preserves required gate and strict verifier formats, retains blocked/abandoned cases and
  distinguishes attributed measurements from unknown costs. The guide and generated site agree.

## [1.34.0] - 2026-10-13

### Added

- **`mneves-security`**: portable application security/privacy audit, detailed remediation
  and authorized safe fixes. Covers twelve review areas and conditional AI/agentic/mobile
  controls with current official OWASP guidance, adversarial review, independent
  acceptance, an eight-section engineering report and an evidence-scoped launch checklist.
- **Security skill plan**: first-principles alternatives, primary-source research,
  advisory corrections and frozen behavioral acceptance scenarios.

### Changed

- **Catalog and usage docs**: fourteen skills, security examples, scope/verification
  boundaries, domain terms and regenerated HOWTO/landing changelog.
- **Skills landing page**: a responsive catalog grouped by job, clearer install/guide
  hierarchy, self-hosted typography and preserved source/provenance. Copy controls now
  report unavailable or rejected clipboard writes truthfully; a real-browser regression
  covers successful, denied and unavailable copying.
- **Catalog verification**: source skills and guide targets must match the landing page;
  planted missing-entry, duplicate-entry and broken-link controls exercise the guard.
- **Release integration**: reconcile the landing/product collection count with the
  concurrently updated 36-skill pstack inventory; reject stale counts during generation checks.
- **Guide accessibility**: make generated code/table scroll containers keyboard-focusable
  with visible focus, and place the guide content in a main landmark. Generation regressions
  cover both defects found during independent live acceptance.

## [1.33.0] - 2026-10-13

### Added

- **`mneves-render`**: project-local Markdown renderers for HTML, editable DOCX and PDF.
  Pandoc starters preserve metadata and literal punctuation, share HTML/print styling,
  guard active content, and constrain long text and oversized figures. Real-engine
  regressions and CI LibreOffice previews complement structural and visual acceptance.
- **Agent workflow configuration**: local Markdown issue-tracker and single-context domain
  documentation for the repository's engineering skills.
- **`mneves-ship-deploy` release contract**: a read-only conformance checker, reference
  release/live-verification scripts, planted controls and Cloudflare/VPS deployment guidance.

### Changed

- **pstack upstream update**: refreshed all 36 collection skills from the owner's fork,
  incorporating port upstream 0.9.83 and local routing version 0.9.84. Adds `ketchup`,
  `thermos` and `thermo-nuclear-review`, review-thread pagination and plan-fence fixes.
  Planning may write requested design artifacts; advisory calls stay read-only, and execution panels retain
  xhigh reasoning when model diversity is reduced.
- **Defaults guard controls**: accept a Codex-only model block while retaining a planted
  Claude-seat fixture, so the new routing policy does not silently terminate the controls.

- **Codex model routing**: planning and read-only advice use Astra with high reasoning;
  execution, discovery, frontend work, specialists and code review use Sol with xhigh
  reasoning. Autoreview no longer falls back to an advisory model on account-access failures.
- **pstack routing**: regenerated Codex and Pi execution mappings and effort defaults from
  their owning source. The exported local patch now includes model configuration, generator
  changes and their tests so rebuilding the collection preserves the routing policy.

- **`mneves-ship-deploy`**: deploys the pushed commit, proves it live, then tags. It used to
  tag and push the tag before deploying, so a tag could name a build nobody had verified. A
  gate that cannot pass becomes one decision packet with named waivers while every other gate
  still runs. The preflight reports a sixth finding, the release contract.


## [1.32.0] - 2026-10-08

### Added

- **`autoreview` complexity evidence**: portable `cccc` installation with reviewed release
  checksums, explicit destinations and no replacement or PATH edits; offline failure controls
  and a separate real-binary smoke check for thresholds, parsing, missing inputs and empty scans.
- **Implementation plan**: alternatives, frozen acceptance, primary-source research and
  adversarial findings for the complexity integration.

### Changed

- **Review skills**: autoreview, Fable, expert-review, superaudit and verify use installed
  `cccc` for supported source and always challenge code changes adversarially. Coverage,
  parse diagnostics, version and repository policy accompany scores; optional metrics never
  replace tests or independent review. Single-skill installs retain inline fallbacks.
- **Fable model defaults**: rechecked against current vendor catalogs; verification date
  updated without changing role selection.
- **Documentation and CI**: installation/review guidance, installer tests in the existing
  portable suite, generated catalog, ignored scratch and local complexity cache artifacts.

## [1.31.0] - 2026-10-04

### Changed

- **pstack `tdd`**: writes the failing test first for every bug fix or feature by default.
  Prototypes, spikes and pure config are excluded, and when no cheap test exists it names the
  check it used instead. Upstream ran it only when asked; this is the fork's fourth local
  commit, so `UPSTREAM` now reports `local-commits: 4` and the patch still rebuilds the
  collection from the public `c1123fe`.

### Fixed

- **pstack links**: seven anchors and eleven sentences in `poteto-mode` playbooks, `arena`,
  `figure-it-out` and the Codex/Pi tool maps pointed at sections the fork had retired
  (Non-negotiables, Principles, Laziness Protocol). They now point at `poteto-mode`'s Task
  routing and its engineering references.

## [1.30.0] - 2026-10-04

### Added

- **pstack collection**: [`collections/pstack`](collections/pstack/) vendors 32 pstack skills for Claude Code, Codex, Pi and other agents. They come from Lauren Tan's pstack through the pstack-claude port
  (0.9.67, based on `c1123fe`), with three local commits shipped as `local-overrides.patch`:
  Opus/Fable-only Claude roles, local-only autonomy, and the `principle-*` and `unslop` skills
  folded into `poteto-mode` references. It installs with `--full-depth` or its tree URL; the
  default install is unchanged. Its README lists what each agent can run without the plugin.
- **`tools/scripts/sync-pstack.sh`**: regenerates the collection from tracked files at a pinned
  commit, moves non-spec frontmatter keys under `metadata:`, records the published base commit
  in `UPSTREAM` (credentials stripped) with a patch that rebuilds the fork from it, and validates
  before it replaces anything. `sync-pstack.test` covers it against
  a fixture repository; CI runs it and validates every collection skill with `skills-ref`.
- **Matt Pocock overlap report** in the collection README: `tdd` and `teach` collide by name,
  and thirteen skill groups share triggers, including Matt Pocock's new `pr`.

### Changed

- **`mneves-fable-orchestrator`**: Defaults re-verified against the vendor model lists on
  2026-10-04; no id changed.

## [1.29.0] - 2026-10-02

### Added

- **`mneves-chatgpt-search`**: portable ChatGPT Search audit, improvement and measurement workflow grounded in official OpenAI guidance. Separates search crawling from model training, preserves privacy and provenance, and distinguishes eligibility, genuine crawler access, citations and reader referrals. Includes application examples, a repeated-query baseline and source references; it ships no executables or required integrations.

### Changed

- Updated the skill catalogs, usage guide and generated site for twelve skills.
- Reverified the unchanged orchestrator model IDs and Claude aliases against the official [OpenAI model catalog](https://developers.openai.com/api/docs/models) and [Claude Code model configuration](https://code.claude.com/docs/en/model-config) for this version.

### Fixed

- Generate the usage guide through the Markdown CLI's awaited file output so piped stdout cannot silently truncate it. A real-build regression verifies the final section and unchanged rebuilds in an isolated copy; CI runs it before checking generated files.

## [1.28.0] - 2026-10-01

### Added

- **`mneves-ship-deploy`**: portable release workflow with staging authorized within the requested scope, automatic authorized review gates, and explicit approval of the exact candidate before production tags, pushes, deployments, or promotion. Optional integrations have documented-command fallbacks; plain `ship` grants no deployment authority.

### Changed

- Reverified the unchanged orchestrator model IDs and Claude aliases against the official OpenAI and Claude Code catalogs for this version.

## [1.27.0] - 2026-09-30

### Changed

- **Skill workflows**: less repeated context and bounded work across all ten entrypoints.
  Shorter discovery descriptions, branch-specific references and reuse of checked context
  bound generation, retries and reviews.
  Required proof, privacy, consent, credential scanning, isolation and upstream provenance stay
  binding. The new [usage guide](docs/usage-efficiency.md) supplies a compact task contract and
  explains how to measure usage without treating byte reductions as credit savings.
- **`mneves-fable-orchestrator`**: ordinary Codex sessions/workers use `gpt-6.1-sol` at `medium`,
  bounded workers use `gpt-6-luna` at `medium`, and difficult execution keeps Sol at `high`.
  Routine review uses Sol at `high`; explicit specialist/different-model review and the Claude
  plan advisor keep Astra at `xhigh`. Claude main/worker and frontend bindings are preserved.
- **`autoreview`**: the Codex default is Sol at `high`, with a single Astra at `high` retry only
  for confirmed account-access failure. Explicit model overrides retain their existing no-retry
  boundary. Regression tests cover default dispatch, effort overrides and access-only fallback.

### Fixed

- **`mneves-teach-back-srs`**: resolve the installed helper rather than assuming a working
  directory; substitute its absolute path or assign it inside each fresh shell invocation.
- **Readiness tools**: sort one export to satisfy the existing lint gate without behavior changes.

## [1.26.0] - 2026-09-29

### Changed

- **`mneves-fable-orchestrator`**: every Codex `gpt-6-sol` seat is now `gpt-6.1-sol` at `high`.
  The Codex main-session seat moves from `medium` to `high` and no longer claims to be Codex's
  default; the heavy-executor seat keeps `high`; the reviewer fallback moves from `xhigh` to
  `high`. Review and plan-advisor seats stay on `gpt-6-astra` at `xhigh`.
- **`mneves-fable-orchestrator`**: the Claude main-session and heavy-executor seats move from
  `xhigh` to `high`. Guidance for the current Sonnet reserves `xhigh` for measured gains. On one
  real migration task, with a failing test suite as the oracle, `medium`, `high` and `xhigh` all
  passed; `xhigh` took about four times the tokens and cost of `high` for the same diff size.
  One task is a small sample, so `high` is a default to revisit, not a finding. Frontend stays on
  Opus in these defaults.
- **`autoreview`**: the access-only retry runs `gpt-6.1-sol` at `high` (was `gpt-6-sol` at
  `xhigh`), and the `amp` engine defaults to `openai/gpt-6.1-sol`. The retry's effort override
  now has a test that tells it apart from the primary's effort (primary `xhigh`, retry `high`).
- **HOWTO** and the landing page name the new Codex seats.
- Probes on 2026-09-29: `gpt-6.1-sol` answered at `high` and `gpt-6-astra` at `xhigh`, a fake id
  (`gpt-6.1-solx`) exited 1, and the Claude aliases `sonnet` and `opus` resolved to
  `claude-sonnet-5-5` and `claude-opus-5-5`. The `amp` id is unverified: it follows the Codex id
  and no Amp binary was probed.

## [1.25.0] - 2026-09-28

### Changed

- **`mneves-fable-orchestrator`**: the Claude main session runs Sonnet at `xhigh` with an Opus advisor.
  It moves from Opus to Sonnet (`sonnet`), with Opus (`opus`) as its Claude Code advisor. The heavy-executor seat gains a Claude
  binding, Sonnet at `xhigh`; its Codex binding (`gpt-6-sol`, `high`) is unchanged. The frontend
  subagent stays on Opus. Review and plan-advisor seats are unchanged. Evidence on 2026-09-28
  (Claude Code 2.1.284): `sonnet` resolves to `claude-sonnet-5-5`, and session transcripts showed
  the main session and a `general-purpose` subagent on `claude-sonnet-5-5` at `xhigh` and an
  Opus-pinned frontend subagent on `claude-opus-5-5`. Anthropic's launch notes give `xhigh` a
  higher FrontierCode score than `max` on Sonnet 5.5. The advisor requires Claude Code's
  feature-flag fetch, which `DISABLE_TELEMETRY` and `DO_NOT_TRACK` switch off.
- **HOWTO** and the landing page describe the Claude and Codex routing separately.

### Fixed

- **Defaults guard**: `check-defaults-block.sh` learned only the first `reasoning` tier and seat on
  each Defaults row, so a row binding two harnesses left its second tier unprotected. It now learns
  every match, and the new `check-defaults-block.test` (run in CI) plants each tier and seat
  outside the block and requires a rejection.

## [1.24.1] - 2026-09-25

### Changed

- **`autoreview`**: the `codex` engine reviews on `gpt-6-astra` at `xhigh` (was `high`).
  The access-only retry stays `gpt-6-sol` at `xhigh`; `--thinking` still overrides the primary
  effort only. The `amp` and `claude` engines are unchanged.
- **`mneves-fable-orchestrator`**: the `reviewer` and `plan advisor` seats move to `gpt-6-astra` at
  `xhigh` (were `high`). Execution seats are unchanged. Probes on 2026-09-25: `gpt-6-astra` and
  `gpt-6-sol` both answered at `xhigh`, and a fake id was rejected with a 400.
- **HOWTO**: the `mneves-verify` example and the orchestrator summary name the `xhigh` reviewer.

## [1.24.0] - 2026-09-25

### Changed

- **`autoreview`**: the `codex` engine defaults to `gpt-6-astra` at `high` (was `gpt-6-sol`). An
  account-access failure retries once on `gpt-6-sol` at `xhigh` (was `gpt-6-luna`). Naming the
  default model explicitly keeps that retry; any other explicit model still never falls back.
  Because Astra rejects `none` and `minimal`, `--thinking none` or `minimal` now needs an explicit
  non-Astra `--model`.
- **`mneves-fable-orchestrator`**: the reviewer seat moves to `gpt-6-astra` at `high`, with a new
  `reviewer fallback` seat, `gpt-6-sol` at `xhigh`. Execution seats are unchanged. Probes on
  2026-09-25: `gpt-6-astra` answered at `high`, `gpt-6-sol` at `xhigh`, and a fake id was rejected.
- **HOWTO**: the `mneves-verify` example and the orchestrator summary name the new reviewer.

## [1.23.3] - 2026-09-23

### Added

- README "Check the install": a loop that lists which of this repo's skills an agent's skills
  directory is missing. Per-skill symlink installs do not pick up skills added in later releases,
  so a skill such as `mneves-verify` can exist in the clone and still never be offered to the
  agent. HOWTO points to it.

## [1.23.2] - 2026-09-22

### Changed

- **`mneves-fable-orchestrator`**: the Codex orchestrator seat runs `gpt-6-sol` at `medium`, the
  Codex default (was `high`); the heavy executor and reviewer stay at `high`.

## [1.23.1] - 2026-09-22

### Changed

- **`handoff` is renamed `mneves-handoff`**: another widely installed skill is also called
  `handoff`, so installing both collections clashed. `AGENTS.md` now allows the `mneves-` prefix on
  an adapted skill for exactly this case, with the upstream name kept in the provenance.

### Fixed

- `autoreview`'s test runner runs the three upstream Git suites added in 1.23.0, and the imported
  tests no longer need TruffleHog installed (they mock the scanner or use the fake one), so CI
  passes on runners without it. Upstream's synthetic proxy credential URLs are split so the pack
  scanner accepts them for review. Tests only; the helper is unchanged.

## [1.23.0] - 2026-09-22

Ideas and fixes from a review of OpenClaw Agent Skills 0.1.0 (`711711b8`).

### Added

- **`handoff`** (MIT, adapted from OpenClaw): a clipboard-ready prompt that hands a task to an
  agent you do not control. It opens a discussion, asks the receiver to review before changing
  anything, and names things by portable anchors instead of filesystem paths.

### Changed

- **`autoreview`** imports upstream fixes through `711711b8`: Git collection no longer runs
  checkout-controlled executables (filter drivers are disabled, a diff that needs a converter is
  refused); Git must pass a 10-second `--version` preflight, with trusted `AUTOREVIEW_GIT` and
  `DEVELOPER_DIR` overrides; a pass that does not confirm a finished assessment leaves the review
  `incomplete` (exit 2); trusted global `core.autocrlf` is honored; engines accept authenticated
  proxies with redacted diagnostics; `--prompt-file` accepts an absolute in-repository path;
  reasoning levels are validated per model before preparation; complete Claude capability output
  is captured. Upstream's removal of TruffleHog scanning (#240, #244) and its Astra usage guidance
  are not taken: every outgoing pack is still scanned, and routing stays on the Defaults block.
- **`mneves-verify`**: behavior checks for UI, CLI, API, and generated output are source-blind and
  must probe for fake work (varied inputs, retries, persistence, opened output) before PASS.

## [1.22.0] - 2026-09-22

GPT-6 Sol at `high` becomes the Codex model for execution, orchestration and review; GPT-6 Astra is
kept only as the advisor on the Claude main session's plans.

### Changed

- **`mneves-fable-orchestrator`**: the Defaults block binds the heavy executor, the Codex
  orchestrator and the reviewer to `gpt-6-sol` at `high` (was `gpt-5.6-sol` at `xhigh` and
  `gpt-6-astra` at `high`). The advisor/reviewer role splits in two: a reviewer for fixed Git
  targets and a plan advisor (`gpt-6-astra`, `high`) that reviews only the Claude main session's
  plans. Because the Codex orchestrator and executor now share a model, a Codex session's task,
  not its model, decides its seat.
- **`autoreview`**: the `codex` engine defaults to `gpt-6-sol` at `high`, with an access-only retry
  on `gpt-6-luna` at `xhigh` (was `gpt-6-astra` with a `gpt-5.6-sol` retry); the `amp` engine
  defaults to `openai/gpt-6-sol`.
- HOWTO, landing page and the orchestrator README describe the new routing.

## [1.21.0] - 2026-09-22

The Claude main session moves from Fable to Opus 5.5.

### Changed

- **`mneves-fable-orchestrator`**: the Defaults block binds the main session to the latest Opus
  (Claude alias `opus`, which resolves to `claude-opus-5-5` on Claude Code 2.1.280); the frontend
  subagent stays on Opus. Codex seats are unchanged. The skill keeps its name so existing installs
  and references keep working.
- **`autoreview`**: the `claude` engine defaults to `claude-opus-5-5` instead of `claude-fable-5`.
  An explicit `--model fable` still works and still requires Claude Code 2.1.170 or later.

## [1.20.0] - 2026-09-22

Follow-through on the 1.19.0 self-assessment: the Codex seats get the same protection against
model-id rot that the Claude seats got, and the lane wrapper's fork path becomes a real command.

### Added

- **`codex-lane fork <lane> <new-lane> <prompt|->`**: branches a lane's thread with
  `codex exec fork` into a new lane that inherits the source's cwd and stored policy, so two
  follow-ups can be tried from the same executor state and compared on the same evidence. The
  new lane's id comes from the fork's own `thread.started` event; a fork that reports the source
  id is refused instead of aliased; the source lane is never written. Covered by
  `codex-lane.test`.
- **Defaults-block guard** (`tools/scripts/check-defaults-block.sh`, in CI): the protected
  vocabulary is derived from the orchestrator's Defaults block itself (vendor ids and their
  segments, the Claude seat names and aliases, the reasoning tiers, anything backticked), so
  every value the block names is what may not appear elsewhere in SKILL.md, compared
  case-insensitively as whole words; any vendor-id-shaped token is flagged whether the block
  names it or not. The block's "Verified against the vendor model lists on YYYY-MM-DD" date
  must equal the date of the top CHANGELOG entry, whose version must equal VERSION, so a release
  cut without re-verifying the ids fails CI. Ten planted violations, a stale date, and a version
  mismatch each fail the check; four benign near-misses (`high-stakes`, `fabled`, `maximum`,
  `solution`) pass. `AGENTS.md` records the release step.

### Changed

- The orchestrator README, HOWTO, and codex-dispatch reference describe `fork`.

## [1.19.0] - 2026-09-22

Every skill reviewed against the 2026 Agent Skills spec, Anthropic's authoring guidance, the
current Claude Code and Codex CLI references, and `steipete/agent-scripts codex-first`; findings
verified by a two-axis code review and a security review of the shipped executables.

### Fixed

- **`mneves-fable-orchestrator`**: the Defaults block named "Opus 5.1", a model that does not exist.
  Claude seats now read "latest release" with the `fable` / `opus` aliases; Codex seats keep the
  1.18.1 routing (GPT-5.6 Sol `xhigh` executes, GPT-6 Astra `high` orchestrates, advises, reviews).
  HOWTO's example calls the coordinator "the main session", not "the advisor", matching the skill.
- **`codex-lane next`**: a refused resume (`thread/resume failed` on stderr, seen on very long
  threads) used to look like a no-op round that echoed the previous turn's final message. It now
  exits non-zero, says so, keeps the lane's last-message pointer on the real previous turn, and
  withholds the stale message. Only stderr is consulted; the event stream is model output.
- **`codex-lane`** hardening from the security review and autoreview: every artifact is created
  with a real `O_CREAT|O_EXCL|O_NOFOLLOW` open at mode 0600 (a leftover file, planted symlink,
  or FIFO is refused, never followed or waited on), an existing `CODEX_LANE_DIR` that grants
  group or other users any access is refused by `start` and `next` alike, stored launch args are
  re-validated on every `next`, and a relative `TMPDIR` no longer breaks the prompt file after `cd`.
- Install docs: Codex reads skills from `~/.agents/skills` and `.agents/skills`, not
  `~/.codex/skills`. `mneves-superaudit`'s example path no longer names the author's layout.
- Landing page: `mneves-superaudit` gets its card and the copy says nine skills, not eight;
  `MEMORY.md`'s inventory lists it too.

### Added

- **`compatibility:` frontmatter** on the three executable skills (`autoreview`,
  `mneves-fable-orchestrator`, `mneves-teach-back-srs`) naming the tools they need. Frontmatter
  stays on the Agent Skills spec: CI's `skills-ref validate` rejects any other key, so host-only
  fields (`context: fork`, `effort`, `paths`) stay out; recorded as an `AGENTS.md` invariant.
- **`tools/codex-lane.test`**: end-to-end test of `codex-lane` against a fake `codex` on `PATH`
  (no quota): start, replayed args before `resume`, refused resume, two negative controls,
  stderr streaming and capture, tampered state file. Runs in CI; the 1.18.1 script fails it.
- **`references/codex-dispatch.md`** rewritten around the current CLI: skills location, global
  flags precede `resume`, `codex exec fork` for branching a thread, route-failure taxonomy with
  a one-request probe, hung-run heuristic, private overlay for provider credentials, per-worker
  worktrees and lock etiquette, live-worker check before editing, and the optional `codex-auto`
  launcher marked as not shipped. The orchestrator gains three rules from `codex-first`: never
  stash or rebase someone else's dirty work to start a dispatch, a stop-report is a successful
  run, and an uncommissioned commit message is a lead.
- Orchestrator README "Lane mechanics": python3 requirement, lane-name charset, refused
  pass-through flags, lock recovery, `CODEX_HOME` on every command, stderr log, artifact pruning.
- `autoreview` README documents `scripts/test-review-harness` as the live positive/negative
  control run (calls a provider, so not in CI). `mneves-teach-back-srs` links all three references.

### Changed

- `autoreview` SKILL.md: disclosure authorization comes from the active task or a trusted host
  policy, is asked once, and never authorizes applying findings.
- CI pins `bun-version: 1.4.2`; `build-site.sh` pins `marked@18.0.13` and runs the rendered
  HOWTO body through `tools/scripts/check-html-active.py` (stdlib HTML parser): an element that
  runs or embeds code, an `on*` handler, or a URL attribute whose entity-decoded value uses an
  executable scheme fails the build, while escaped code examples pass. The pre-commit hook diffs
  each staged file with `--literal-pathspecs`.

### Known follow-ups

- Re-vendor `autoreview` from upstream `openclaw/agent-skills` HEAD (six fixes since `3e9f3396`,
  including GPT-6 Astra reasoning-level validation and a trusted-git preflight); it needs its own
  reviewed release per the skill's maintenance policy.

## [1.18.1] - 2026-09-12

### Changed

- **Astra returns to `high`** for orchestration, advice and review; GPT-5.6 Sol at `xhigh` stays
  the executor. `autoreview`'s Codex default drops from `xhigh` to `high` (the access-only Sol
  `xhigh` retry is unchanged), and the orchestrator's Defaults name one advisor/reviewer role.
- **`mneves-fable-orchestrator`**: inside Codex the session's model decides its seat. A session on
  the orchestrator model delegates substantial work to a heavy-executor worker; a session on the
  executor model implements directly and spawns the advisor only for a consequential decision or
  an independent review.

## [1.18.0] - 2026-09-12

### Changed

- **`mneves-fable-orchestrator`**: new Defaults. The main session is Fable 5.1 in a Claude harness
  or GPT-6 Astra at `xhigh` in a Codex harness; the frontend subagent is Opus 5.1; the heavy
  executor moves from GPT-6 Astra `high` to GPT-5.6 Sol `xhigh` and no longer owns review. A new
  reviewer role (GPT-6 Astra `xhigh`) owns independent review, through `autoreview` when installed.
- **`mneves-fable-orchestrator`**: a Codex main session no longer implements substantial work
  directly; like the Claude side, it delegates independent work to a heavy-executor worker whose
  model is set in the spawned agent's configuration.
- **`autoreview`**: the Codex default reasoning rises from `medium` to `xhigh` on GPT-6 Astra. The
  access-only GPT-5.6 Sol `xhigh` retry is unchanged. Reviews are slower and cost more; pass
  `--thinking medium` for the previous behavior.

## [1.17.0] - 2026-09-10

Every skill reviewed against Anthropic's Agent Skills authoring guidance and this repository's own
invariants. Activated `SKILL.md` bodies drop from 7,889 to 6,045 words while the collection gains
13 on-demand reference files, so a skill that is triggered now loads materially less and reaches
the rest only when a task needs it.

### Changed

- **`autoreview`**: body 1,702 → 635 words. The Codex config-projection contract, status-sidecar
  schema and exit codes, Git target edge cases, runtime boundaries, and engine override mechanics
  moved to five reference files, each linked one level deep from `SKILL.md`. Every flag and
  operational fact is preserved.
- **`mneves-teach-back-srs`**: body 1,197 → 775 words. Review, Stats and Export modes and the
  card-quality rules moved to references; the teach-back loop, decision tree and database setup
  stay inline. SM-2 thresholds are no longer restated in prose — the `stats` command owns them.
- **`mneves-expert-review`**: twelve steps collapse to six. The pre-mortem, five-year test and
  contrarian steelman were the same move in three costumes and are now one combined attack step;
  the duplicated second quality audit is gone; the "six or more alternatives" quota becomes
  "until they stop differing in kind". `references/checklists.md` is deleted — it restated the
  body rather than deferring anything.
- **`mneves-eli5`**, **`mneves-agent-readiness`**, **`imagegen-frontend-mobile`**: worked example,
  context-file template, and safety boilerplate the base agent already applies moved out or
  removed. Two epigraphs and an unfalsifiable "updated within 30 days" freshness rule deleted.
- **`mneves-fable-orchestrator`**: model identifiers no longer appear in six places across three
  files. Prose describes capability roles and a single Defaults block carries the ids, so a model
  release is a one-line edit. `codex-auto` is now declared a personal launcher that this repository
  does not ship, with the plain `codex exec` equivalent given.
- **`mneves-verify`**: the independence rule states the principle instead of naming vendors, and
  the evidence table leads with the required capability rather than with tools that are not
  shipped here.
- **`mneves-superaudit`**: description reduced from 430 to 124 characters — it was loading a
  trigger-phrase inventory into every session, at roughly three times any sibling.
- Pinned CLI patch versions removed from `autoreview`'s prerequisites; the helper reports its own
  current defaults.

### Fixed

- `mneves-expert-review` referenced a private documentation layout (`DOCS/GUIDELINES-REF`,
  `DOCS/REF_DOCS`) that exists only on the author's machine, and `mneves-teach-back-srs`'s README
  hardcoded one harness's install path. Both violated the repository's own "must work for a
  stranger's clone" invariant.
- `mneves-agent-readiness` described the readiness assessor as "bundled with this skill"; it lives
  at the repository root and is absent from a single-skill install. The skill now says so and
  points at the manual pass as the fallback.
- `AGENTS.md` omitted `mneves-superaudit` from its project tree, and `HOWTO.md` still said "eight
  skills" with the new one missing from its quick-reference table.
- `AGENTS.md` required Python 3.11+ for shipped helpers while `srs_db.py` documents and needs only
  3.10; the invariant was wrong, not the skill.

### Added

- `AGENTS.md` invariants for the rules this pass had to apply by hand: model identifiers confined
  to one block per skill, no skill requiring anything it does not ship, `SKILL.md` bodies under
  500 lines with references one level deep, and the distinction between a tool's documented
  default path and the author's private machine layout.

## [1.16.0] - 2026-09-10

### Added

- **`mneves-superaudit`**: a bounded, delegated audit-and-ship pass over a repository. Four selectable items — slop removal, performance wins, agent DX and verification loops, PR/issue triage — each ending on a falsifiable condition rather than a judgement that the work feels complete. Five phases with typed stop gates: findings before any edit, the diff before any commit, and an explicit release instruction naming a destination before anything leaves the machine.
- Delegation guidance sized to the documented multi-agent failure modes: a per-task-class worker budget, briefs that name the other workers' paths as *do not touch*, a distilled return contract that passes file references instead of transcripts, and the cases where delegating costs more than it saves. Discovery parallelizes because it is read-only; implementation partitions by path or serializes, since the slop and performance items touch the same files.
- Measurement rules that can return "inconclusive": a performance result inside noise, or one depending on the change's own instrumentation, is never reported as a win; negative assertions and security gates require a positive control placed where the gate actually looks, and a policy claim counts only against the served artifact.
- A per-phase progress file (`agent_planning/superaudit-<date>.md`) so a long run survives compaction, and an A/B protocol for testing changes to the skill itself against a fixed repository and commit.

### Changed

- Catalog and HOWTO now cover the new skill, including the item-selection syntax that keeps unused phases out of context.

## [1.15.0] - 2026-09-07

### Added

- **`autoreview`**: portable MIT-licensed adaptation of OpenClaw's structured review helper, maintained in this collection with its source revision, license, full tests, and no dependency on an upstream checkout. Available as the `v1.15.0-beta1` candidate.
- Autoreview defaults to `gpt-6-astra` with medium reasoning and retries confirmed account-access failures once with `gpt-5.6-sol` at xhigh; primary overrides retain the fallback effort and other failures do not change models.
- An isolated test runner and CI coverage for the imported review helper, including provider-route, scanner, source-integrity, and filesystem-boundary tests.

### Changed

- Catalog, installation, licensing, and maintenance documentation now include autoreview and explain that authorized review inputs are sent to the selected provider.

### Security

- Preserve the original repository's executable and environment trust boundary during nested submodule snapshots, preventing repository-owned Git binaries from running during preparation.
- Validate both output targets and the directory entries that will be replaced; normalize accepted paths once so report writes and stale-status cleanup cannot enter the reviewed repository through symlinks or quoted home paths.

## [1.14.0] - 2026-09-07

### Added

- **`imagegen-frontend-mobile`**: an MIT-licensed, condensed adaptation of Leonxlnx's mobile image-generation skill. It generates iOS or Android screen and flow images, locks one design system across the set, inspects the rendered result, and never substitutes code for the requested images.

### Changed

- Repository guidance now distinguishes original `mneves-` skills from adapted third-party skills that retain their upstream name, license, copyright, and provenance.
- **`mneves-fable-orchestrator`** now uses GPT-6 Astra at reasoning `high` for Codex execution, planning, review, and inherited agents; explicit specialist overrides remain supported and quota probes use `low`.
- Skill descriptions now fit the discovery budget with one distinguishing capability-and-trigger sentence. Redundant trigger lists, checklists, and examples were merged into the procedures; Codex launcher mechanics moved to a conditional reference.
- **`mneves-verify`** now distinguishes substantial checkable completion, which still gets an independent verifier, from routine low-risk changes that need only proportionate deterministic proof.

### Security

- The new skill treats reference assets as untrusted data, requires authorization before sending private references to an image service, excludes secrets and unnecessary personal data from prompts, and forbids fabricated endorsements, certifications, transactions, or product claims. Repository and site copy now distinguish local tooling from provider-backed image generation.

## [1.13.0] - 2026-09-07

### Changed

- **`mneves-fable-orchestrator`** routes the heavy executor back to GPT-5.6-sol at reasoning `xhigh`; GPT-6-astra at `high` keeps only the planning, orchestration and review seat, the one Fable holds on the Claude side.

### Added

- **`mneves-fable-orchestrator`**: "Inside a codex run: sol drives, astra advises". Sol owns progress, implementation and verification and never hands the task off; it spawns an advisor only for a decision with real downside, an expensive-to-reverse trade-off, or an independent review. The advisor is named explicitly (a model asked for in prose is a wish, the agent file is the setting), gets a fresh context via `fork_turns: "none"` and a self-contained brief, edits nothing, spawns nothing, and changes no approval boundary.
- The advisor must be selected with `CODEX_AUTO_MODEL` / `CODEX_AUTO_EFFORT`, never `-c model="..."`: a wrapper that passes `--model=<executor>` wins over the `-c` override and the run lands on the executor while the caller believes otherwise. Verify with the session header's `model:` line.

## [1.12.0] - 2026-09-04

### Changed

- **`mneves-fable-orchestrator`** routes the heavy executor to GPT-6-astra at reasoning `high` (was GPT-5.6-sol); the GPT-5.6-terra bulk tier is dropped, exceptions are pinned per lane.

## [1.11.0] - 2026-08-26

### Added

- **Recorded sessions in `HOWTO.md`**: `mneves-eli5` and `mneves-expert-review` examples are verbatim `claude -p` runs (claude-fable-5, 2026-08-26); `mneves-teach-back-srs` shows real `srs_db.py` output; the readiness example was already a real run. The two remaining examples are labelled illustrative.
- Branch ruleset on `main`: no force-push, no deletion.
- CI fails when `site/howto.html` or the landing page's changelog rows are stale (`tools/scripts/build-site.sh` regenerates both).

### Changed

- **`mneves-teach-back-srs`** no longer hardcodes `~/.claude/skills/...`; commands reference `scripts/srs_db.py` relative to the skill folder, as the Agent Skills spec recommends, so any install location works.
- **`mneves-fable-orchestrator`** keeps model ids in one Models table (role, id, effort, where it is set); the body refers to roles.
- Landing-page changelog rows are generated from `CHANGELOG.md` by `tools/scripts/changelog-rows.py` instead of copied by hand. `build-howto.sh` renamed to `build-site.sh`.

## [1.10.0] - 2026-08-26

### Changed

- **`mneves-fable-orchestrator`** adopts five rules from steipete's `codex-first` (2026-08-20 revision): every hard prohibition in a spec carries an escape hatch (the minification incident), check for a live worker with `pgrep -fl "codex exec"` before editing, verify beyond the diff (merged surface, uncommissioned commit messages, guard files, test-helper edits), a diagnosis list for executors that die instantly or go quiet (with lane resume), and never passing credentials via `-c` (use a `CODEX_HOME` overlay). Read-heavy exploration may go to Codex; a new work order always gets a fresh thread. Not adopted: routing git rebase/merge/landing to Codex.
- Every `SKILL.md` declares `license: Apache-2.0` (Agent Skills spec optional field); all six validate with `skills-ref`.
- Prose pass over skills and repo docs: list-item em dashes replaced with colons, sentence-level ones with punctuation, "production-ready"/"genuinely" dropped. The verdict format in `mneves-verify` is unchanged (it is a contract).

## [1.9.0] - 2026-08-26

### Added

- **Landing page** at https://mneves75.github.io/skills/ (`site/index.html`): install commands with copy buttons, one card per skill linking into the how-to, how it works, the readiness tool with the sample score, start-here links, recent changelog. Self-contained HTML, light/dark, keyboard-operable.

### Changed

- Pages source directory renamed `examples/` → `site/` (landing, how-to, sample report); the workflow uploads it as-is instead of generating an index from a heredoc.
- `tools/scripts/build-howto.sh` adds heading ids so the landing page can link to each skill's section.
- Dependabot PRs #1–#5 closed and their branches deleted; `main` is the only branch. The four green action bumps can be re-requested with `@dependabot recreate`.

## [1.8.2] - 2026-08-26

### Added

- **`HOWTO.md`**: what each of the six skills does, its trigger phrases, prerequisites, a worked example and tips; rendered to `examples/howto.html` on GitHub Pages by `tools/scripts/build-howto.sh` (bun + marked, nothing added to the repo's dependencies). Linked from the README and the Pages index.

### Fixed

- `mneves-agent-readiness` SKILL.md told the agent to pass a project path to `readiness-check.ts`; the tool assesses the current directory and ignores positional arguments. Usage now says `cd` first. Dropped the stale "v1.0.0" label.

## [1.8.1] - 2026-08-26

### Changed

- **Example report regenerated** with the fixed tool against FastAPI `9a8a13f` (2026-08-25): L3, 61.7% (`--skip-tests --skip-build`). The previous numbers disagreed across README (L4 / 65.4%), the HTML report (56.3%) and `scoring.ts` comments (53%); all now show the same run with its provenance.
- **Factory.ai attribution made factual.** Removed the speculative comparison table (competitor pricing, language list, "limited monorepo") and marketing prose ("pioneered", "set the standard"); README, NOTICE and the skill README now state only that the pillar/level structure follows Factory.ai's Agent Readiness assessment and that this is an independent, local-only implementation whose scores are not comparable.

## [1.8.0] - 2026-08-26

### Added

- **`npx skills` install path** — `npx skills@latest add mneves75/skills` is the documented primary install (all six skills verified discoverable with `--list`); manual `git clone` table kept per tool.
- **CI** (`.github/workflows/ci.yml`) — skill-layout check (folder == frontmatter `name`, description present, no root `SKILL.md`), `bash -n`, `py_compile`, ast-grep scan, pre-commit hook e2e test, `tools/` typecheck + Biome lint. `contents: read` only.
- `SECURITY.md` (private vulnerability reporting, response windows, scope) and `.github/dependabot.yml` (GitHub Actions + `tools/` npm, weekly).

### Changed

- **`mneves-expert-review`** no longer points at a maintainer-local `~/dev/GUIDELINES-REF`; it references the project's own guidelines when present, so the skill works from any clone.
- GitHub Actions pinned to commit SHAs in both workflows.
- `AGENTS.md` is the single agent-instructions file (`CLAUDE.md` imports it); tree refreshed to list all six skills and the CI/security files.
- `tools/package.json` declares `private`, `license`, `repository`, `engines`; README's readiness-check usage now matches how the tool actually runs (assesses cwd via `bun --bun …/tools/readiness-check.ts`).
- `.gitignore` covers `.codemap/` and `__pycache__/`.

### Fixed

- `readiness-check` piped output (`| jq`, `> file` via shell) was cut at 64 KiB: `console.log` followed by `process.exit` dropped unflushed data. Output is now written with an awaited `process.stdout.write` callback (`Bun.write(Bun.stdout)` re-emits the buffer after a partial pipe write on Bun 1.4.0); verified with a 100 KB JSON report through a real pipe.
- `tools/lib/checks/shared.ts` used `fs` without importing it; the "extensive `docs/`" documentation check silently never passed (error swallowed by a `catch`). Typecheck now passes and CI enforces it.
- `.githooks/pre-commit` passes staged paths after `--`, so a file named `-x.ts` is not read as an ast-grep option.
- Biome lint errors (import order, unused imports, `let` → `const`) auto-fixed; `bun run lint` is green (warnings only).

### Removed

- `docs/EXAMPLES-EXEC-SPEC.md` (1.0.0-era spec for assets that never existed).

## [1.7.0] - 2026-08-26

### Added

- **`mneves-expert-review`** (`skills/mneves-expert-review/`) — expert-panel review and optimization pass run on a draft before it is finalized: clarify the real objective, rebuild from first principles, research only when it changes the answer (web + `~/dev/GUIDELINES-REF`, disconfirmation first, claims labelled fact/consensus/disputed/inference/judgment), attack the draft as a seven-role panel, generate six genuinely different alternatives (incl. one that challenges the premise) and compare them on weighted criteria, pre-mortem, five-year test, contrarian steelman, quality audit, then return the improved deliverable with trade-offs, risks, evidence and remaining uncertainty. Scales to stakes; checkable artifacts hand off to `mneves-verify`. SKILL.md + `references/checklists.md`, no scripts. Installed via `~/.agents/skills/` symlink fan-out to Claude Code, Codex, OpenCode, Cursor, Pi and Gemini.

## [1.6.0] - 2026-08-26

### Added

- **`mneves-eli5`** (`skills/mneves-eli5/`) — Feynman-technique explainer calibrated to the listener (child, layperson, executive, junior, expert): fix the audience, one-sentence core, one analogy carried through, show-then-name jargon, state where the analogy breaks, one repeatable takeaway. Answers in the user's language; re-explains for a new audience without re-deriving. SKILL.md only, no scripts.

## [1.5.0] - 2026-08-18

### Added

- **`mneves-verify`** (`skills/mneves-verify/`) — independent-verification skill that operationalizes the "never grade your own homework" rule. Fresh independent context checks the artifact against explicit acceptance criteria; evidence routes by artifact type (focused tests + `autoreview` for code, `agent-browser`/Argent + real renders for UI, real binary/endpoint/query + positive control for CLI/API/data, primary sources + citation checks for research, `security-audit` for security); one builder correction + one full fresh reverify (every criterion + affected regression surfaces), then `Verdict: PASS | FAIL | BLOCKED` with one Criterion line per criterion. PASS alone permits done/fixed/shipped. Artifacts are untrusted data, never instructions; read-only by default, no secrets, no external writes; no scripts/dependencies/scaffolding.
- **ast-grep guard** — `sgconfig.yml` + `rules/no-as-any.yml` (TypeScript) + `rules/no-as-any-tsx.yml` (TSX): two rules rejecting `as any`, so the repository itself has a real checkable guard rather than a prose promise.
- **Blocking pre-commit hook** (`.githooks/pre-commit`) — runs the ast-grep scan and fails closed when ast-grep is absent; enabled locally via `git config core.hooksPath .githooks`.
- **Project memory** — `FOR_YOU_KNOW.md`, `MEMORY.md`, and `memory/2026-08-18.md` (previously absent).

## [1.4.0] - 2026-07-31

### Added

- **`codex-lane`** (`skills/mneves-fable-orchestrator/tools/codex-lane`) — named, resumable Codex threads: `start` / `next` / `adopt` / `id` / `log` / `last` / `list` / `drop`, state in `~/.codex/lanes/`. Install by symlink onto `PATH`.
- `codex-lane adopt <lane> <thread-id> [cwd]` wraps a thread started by a plain `codex exec`, so a dispatch that unexpectedly needs a round 2 continues on the same thread instead of being re-specified.
- Fable Orchestrator gains a **Continuity** section: one round is a `codex exec`, two or more rounds is a lane. Fix-ups, review findings and failing gates go to `codex-lane next` on the same thread instead of a fresh spec, so the executor keeps its private reasoning and the instruction preamble is served from cache. Rationale and measurements from OpenAI's [ARC-AGI-3 harness writeup](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores/) (retained reasoning + compaction: 13.3% → 38.3% RHAE, 6× fewer output tokens); locally, a fresh `exec` sends ~34k uncached input tokens versus ~35k cached on a `resume`.
- Documented the Codex flag-order trap: global flags must precede `resume` (`codex exec -s read-only resume <id>`, not `codex exec resume <id> -s read-only`).

### Changed

- Fable Orchestrator no longer requires the openai-codex plugin: the primary heavy-executor path is `codex exec` / `codex-lane`, with `/codex:rescue` noted as an equivalent front-end.
- Verify loop iterates via `codex-lane next` (Codex) or `SendMessage` (subagent) rather than a fresh dispatch.
- `codex-lane next` now treats its prompt argument as always-literal text; automatic detection of a readable file path is removed. File or untrusted content must be passed explicitly via stdin redirection — `codex-lane next <lane> - < file` — so a pathname string can never be silently replaced by the file's contents.

### Security

- `codex-lane` validates lane names against `[A-Za-z0-9._-]` and rejects leading `-`. A name like `../foo` previously escaped the lane directory, so `drop` could delete a `.json` file elsewhere on disk.
- `require_lane` is called directly instead of inside a command substitution: `die` in a `$( )` subshell only killed the subshell, so `id` / `log` / `last` / `drop` silently continued with an empty path when the lane did not exist.
- Lane directory is created mode `700` and the script runs `umask 077`, because event logs contain the full model transcript for the job.
- `codex-lane next` now `cd`s to the lane's recorded `cwd` before resuming. It previously ran wherever it was invoked, so a resume issued from another repository (or from `$HOME`) let the executor inspect, test, or modify the wrong workspace.
- Lane names are reserved atomically (`set -o noclobber`) before the Codex run starts, and the placeholder is released if no thread id is obtained. The previous `[ -f ]` check left two concurrent `start`s racing for the whole duration of a run.
- `codex` and `python3` are verified present before dispatch, not after: on a host without `python3` the executor could modify the workspace and only then lose the thread id that makes the work resumable.
- `codex-lane next` replays the execution args the lane was started with. `codex exec resume` rebuilds sandbox/model/profile from the current invocation rather than from the thread, so a lane started `-s workspace-write` previously resumed under the machine default — often read-only, i.e. unable to perform the fix-up it was resumed for. `next` now rejects trailing arguments and always replays the stored set — the per-turn `-- <args>` override is gone, so the lane's execution policy cannot drift one turn at a time.
- `-C` / `--cd` in the pass-through args is rejected. It would have moved Codex to another tree while the lane recorded the original one, sending every later `next` at the wrong repository.
- `start` and `adopt` record the workspace as a physical path (`pwd -P`). The logical `$PWD` kept a symlinked spelling, so a lane started or adopted through a symlink could have made `next` resolve to a different real tree than the one the spec targeted.
- Resumes of the same lane are serialized with an atomic lock, and artifact names carry the PID: two concurrent `next` calls could otherwise interleave turns on one thread and truncate each other's logs.
- Prompts reach Codex on stdin (`resume <id> -`) instead of argv. An *inline* prompt still travels in the wrapper's own argv, so `codex-lane next <lane> -` reads the prompt from the wrapper's stdin — a 2 MB build log passes as a file path or on stdin, and only an inline megabyte-scale string can still hit `E2BIG`.
- `codex-lane next` and `drop` acquire the lane lock *before* reading state. Reading first left a window where a concurrent `drop` reported success and the in-flight resume then recreated the lane, silently resurrecting a thread the user had dropped.
- Lane state is written to a temporary file and `os.replace`d into position. The previous truncate-then-serialize could destroy the only copy of the thread id if the write failed partway, leaving the lane unresumable.
- Attached forms of the output flag (`-o/tmp/x`, `-o=/tmp/x`) are rejected, not just the bare `-o`, since either would redirect the final message away from the file `codex-lane last` reads.
- A prompt file whose name looks like an option (`-n`, `--help`) is read via redirection instead of `cat "$1"`, which would otherwise hand the model help text instead of the prompt.
- Every attached form of the cwd flag is rejected (`-C x`, `-Cx`, `-C=x`, `--cd=x`), not just the bare token.
- Wrapper-owned and lane-incompatible flags are rejected in the pass-through args: `--json` and `--output-last-message`/`-o` would redirect the lane's own artifacts, and `--ephemeral` would create a thread that can never be resumed.
- `drop` and `adopt` take the same per-lane lock as `start`/`next`, so a drop can no longer race a running turn that then republishes the state file.
- An existing `CODEX_LANE_DIR` is no longer `chmod 700`-ed; only a directory the wrapper creates gets the restrictive mode.
- An argument before the literal `--` is now an error instead of being dropped. `codex-lane start l spec -s read-only` previously succeeded while silently running under the machine default — possibly wider permissions than the caller had just asked for.
- Lane names may not start with `.`: such a state file was invisible to `list`'s glob, so the lane worked everywhere except where you would look for it.
- `adopt` resolves a relative workspace with `CDPATH=` and `cd >/dev/null`. Under a configured `CDPATH`, bash's `cd` echoes the resolved directory, which recorded two newline-separated paths and made every later `next` die on a cwd that "is not a directory".
- `codex-lane --help` exits 0; only a malformed invocation exits 2.
- Documented examples default to `-s workspace-write` rather than `--dangerously-bypass-approvals-and-sandbox`.
- Thread ids beginning with `-` are rejected in `adopt` (and defensively on the stored/observed id in `start`/`next`) before they are persisted or passed to `codex exec resume`, where codex would parse them as flags.

### Fixed

- README version badge was pinned at 1.2.0 while `VERSION` read 1.3.0.
- `codex-lane --help` printed shell code past the end of the header comment; help is now derived from the leading comment block.
- `id`, `log`, `last` and `drop` require exactly one argument and `list` requires zero; a malformed call now exits 2 before acting (previously `drop <lane> <extra>` ignored the extra arg and deleted the lane).

## [1.3.0] - 2026-07-24

### Changed

- **BREAKING** — all skills now carry the `mneves-` prefix: `agent-readiness` → `mneves-agent-readiness`, `fable-orchestrator` → `mneves-fable-orchestrator`, `teach-back-srs` → `mneves-teach-back-srs`. Directory name and frontmatter `name:` match. Re-link installs: `ln -s <repo>/skills/mneves-<skill> ~/.claude/skills/mneves-<skill>`.
- Fable Orchestrator routes heavy implementation to GPT-5.6-sol at reasoning `high` (was GPT-5.5 at `xhigh`).

## [1.2.0] - 2026-07-08

### Added

- **Fable Orchestrator Skill** - Model-routing policy for multi-agent Claude Code sessions
  - Fable (main session) as advisor: repo understanding, architecture decisions, task decomposition, spec writing, final review
  - Opus subagents as frontend executors (components, styling, layout)
  - Codex (GPT-5.5 xhigh via `/codex:rescue`) as heavy executor (implementation, debugging, test fixing, multi-file refactors)
  - `supergoal` + `/goal` for long-horizon, multi-phase work
  - Delegation contract (goal, paths, constraints, proof, output shape) and mandatory Fable-side verification of all delegated output
  - Codex invocation patterns adapted from [steipete/agent-scripts — codex-first](https://github.com/steipete/agent-scripts/blob/main/skills/codex-first/SKILL.md)

## [1.1.0] - 2026-02-01

### Added

- **Teach-Back SRS Skill** - Spaced-repetition learning through codebase teach-back sessions
  - Teach-back mode: explain your understanding, Claude cross-references code and probes gaps
  - Socratic follow-ups with specific file:line references for misconception correction
  - SM-2 algorithm (SuperMemo 2) for optimal review scheduling
  - Per-project SQLite database (`.ai-learn/srs.db`, auto-gitignored)
  - Review mode with self-rated recall (quality 0-5)
  - Stats dashboard: mastered, struggling, due, upcoming cards
  - Export to Markdown or Anki-compatible CSV
  - Cross-session continuity via persistent SQLite state
  - Card generation guidelines: one concept per card, why > what, context-anchored
  - Python 3.10+ stdlib only, no external dependencies

## [1.0.0] - 2026-01-22

### Added

- **Agent Readiness Skill** - Evaluate codebase readiness for AI agents
  - 9 technical pillars (Context, Typing, Testing, Build, Lint, CI/CD, Documentation, Observability, Security)
  - 5 maturity levels (L1 Runnable → L5 Autonomous)
  - Multi-language support (TypeScript, JavaScript, Go, Python, Rust, Java)
  - Monorepo application discovery
  - Multiple scoring modes (weighted, strict, average)
  - HTML, JSON, and Markdown output formats

- **Benchmark Reports** - Real assessments of popular open-source projects
  - FastAPI (Python) - L4, 65.4%

- **GitHub Pages** - Live HTML reports at https://mneves75.github.io/skills/

- **Tool Installation** - Support for pi, OpenCode, Claude Code, Cursor, VS Code, Codex, Windsurf, and Aider

### Notes

This project is inspired by [Factory.ai](https://factory.ai)'s Code Readiness framework.

[1.20.0]: https://github.com/mneves75/skills/releases/tag/v1.20.0
[1.19.0]: https://github.com/mneves75/skills/releases/tag/v1.19.0
[1.18.1]: https://github.com/mneves75/skills/releases/tag/v1.18.1
[1.18.0]: https://github.com/mneves75/skills/releases/tag/v1.18.0
[1.17.0]: https://github.com/mneves75/skills/releases/tag/v1.17.0
[1.16.0]: https://github.com/mneves75/skills/releases/tag/v1.16.0
[1.15.0]: https://github.com/mneves75/skills/releases/tag/v1.15.0-beta1
[1.11.0]: https://github.com/mneves75/skills/releases/tag/v1.11.0
[1.10.0]: https://github.com/mneves75/skills/releases/tag/v1.10.0
[1.9.0]: https://github.com/mneves75/skills/releases/tag/v1.9.0
[1.8.2]: https://github.com/mneves75/skills/releases/tag/v1.8.2
[1.8.1]: https://github.com/mneves75/skills/releases/tag/v1.8.1
[1.8.0]: https://github.com/mneves75/skills/releases/tag/v1.8.0
[1.7.0]: https://github.com/mneves75/skills/releases/tag/v1.7.0
[1.6.0]: https://github.com/mneves75/skills/releases/tag/v1.6.0
[1.5.0]: https://github.com/mneves75/skills/releases/tag/v1.5.0
[1.4.0]: https://github.com/mneves75/skills/releases/tag/v1.4.0
[1.3.0]: https://github.com/mneves75/skills/releases/tag/v1.3.0
[1.2.0]: https://github.com/mneves75/skills/releases/tag/v1.2.0
[1.1.0]: https://github.com/mneves75/skills/releases/tag/v1.1.0
[1.0.0]: https://github.com/mneves75/skills/releases/tag/v1.0.0
