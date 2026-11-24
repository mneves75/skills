# Skill ledger

Disposition of every skill entrypoint the repository shipped before the pstack refresh (59:
23 in `skills/`, 36 in `collections/pstack/`) and of every upstream pstack name this
collection does not carry as-is (32). Each row was decided by reading the skill against its
neighbours and its upstream source. No row rests on usage counts or measured outcomes: a skill
that is rarely used is not, for that reason, removed.

Dispositions: **changed** (edited in this refresh, controls kept), **retained** (reviewed, no
edit needed), **added**, **retired** (guidance moved elsewhere), **excluded** (not shipped).
Collection rows name the [adaptation patches](../collections/pstack/adaptations/) that touch
the skill; every collection skill is generated from the pinned sources in
[`sources.json`](../collections/pstack/sources.json) and passes the Agent Skills reference
validator inside the sync.

The current root catalog has 22 skills: the 23 recorded in the historical refresh plus
`untangle-codebase` (1.46.0) and `mneves-socratic-tutor` (1.47.0), minus the three empirically
negative-lift skills retired in 2.0.0 (`mneves-eli5`, `mneves-socratic-tutor`, `mneves-superaudit`).
The opening counts describe the historical refresh inventory.

## Root skills (22)

| Skill | Disposition | Reason and kept controls |
|---|---|---|
| `autoreview` | retained | Owns the isolated review CLI, its security tests and the `cccc` complexity guidance; `full-stop` reviews through it. 1.48.0: the Kimi engine needs `--allow-kimi-argv-prompt`, because its prompt is a process argument other local accounts can read. 1.52.0: native `--engine agy` backend. |
| `babysit-pr` | changed | Canonical PR watcher. Adds one watcher owner per PR, a finite repair bound (same failure surviving two fixes, or three rounds) that yields to a stricter host or user limit, and no force-push or auto-merge change without the user. `pr-wait` and its fake-`gh` test are unchanged; 2.0.0 moves `pr-wait` internals and rate-limit/billing details to `references/pr-wait-and-limits.md`. |
| `council` | changed | Bounded, advisory multi-CLI deliberation; states it is not verification, so it does not duplicate `autoreview` or `mneves-verify`. 2.0.0 moves CLI invocation flags and prompt templates to `references/invocations-and-prompts.md` and adds prototype-first empirical fork resolution. |
| `full-stop` | changed | Fixes from PR #38: runs only on an explicit invocation ("Full stop." as punctuation is not one), no force-push or rewrite of pushed history, the user's and project's rules on asking before a test method stay in force, and existing auto-merge or merge-queue state is reported, never changed. Never merges. |
| `imagegen-frontend-mobile` | retained | Image-only path for mobile concepts; no overlap with a code skill. |
| `leaving-pr-comments` | retained | The attribution control that `full-stop`, `babysit-pr` and `takeover` name, each with a standalone fallback line. |
| `mneves-agent-readiness` | retained | Pairs with the `tools/` assessor. |
| `mneves-chatgpt-search` | retained | Distinct audience (ChatGPT Search discovery and attribution); no overlap. |
| `mneves-expert-review` | changed | Stress-tests drafts and decisions, explicitly not code diffs, so it does not compete with `autoreview`. 2.0.0 requires verifying every linked primary source supports its claim and cutting unconfirmed citations. |
| `mneves-fable-orchestrator` | changed | Normative routing and the only model Defaults block. 2.0.0 disables DeepSeek (removing the economy fallback), adds worker-contract and prototype-first brief discipline, and keeps closed independent review gates. |
| `mneves-handoff` | retained | Writes context for another agent; pstack's `recall` rebuilds your own. Different jobs. |
| `mneves-motion-film` | retained | Distinct media pipeline with its own checks and tests; its scripts were hardened in 1.45.0 (H-M2 to H-M6), outside the pstack refresh. |
| `mneves-production-readiness` | changed | Readiness gate; imports its security rows from `mneves-security` rather than re-auditing. 2.0.0 distinguishes code rollback from persistent-state rollback, checks preview writable bindings before negative controls, and treats pending observation windows as `NOT TESTED`. |
| `mneves-render` | retained | Distinct Markdown export pipeline with Pandoc acceptance tests. |
| `mneves-security` | changed | Owns remediation, privacy/OWASP launch readiness and the exact-candidate deploy verdict; routes a requested deep source audit to `security-audit` and treats its records as candidate evidence, never as a gate. 2.0.0 slims `SKILL.md` by extracting `references/deploy-gate.md`. |
| `mneves-ship-deploy` | changed | Release sequence and contract checks; requires the security gate first. 2.0.0 extracts detailed phase checklists into `references/phases.md` and adds candidate/artifact identity, preview writable-binding, observation-window, and persistent-state rollback checks. |
| `mneves-teach-back-srs` | retained | Opt-in codebase teach-back and SQLite SM-2 spaced repetition (`srs_db.py`). |
| `mneves-verify` | changed | Independent verdict required by the security and release paths. 2.0.0 adds verification-integrity rules (separating product vs verification/operational edits, negative controls for weakened checks, real execution vs vacuous exit-0), closed independent review gates, and verified-citation checks. |
| `modernize` | retained | Rebasing an aging PR is its explicit job; it already decides whether the PR should exist first. |
| `security-audit` | retained | Owns the six-phase source methodology, the coverage and findings schemas and their Node validators; already says it never claims a deploy gate. Validators unchanged. |
| `takeover` | retained | Finishing someone else's work with credit kept; no overlap. |
| `untangle-codebase` | changed | Adapted from caldoai/skills (`442c2991`, MIT). Owns bounded structural refactoring with observed baselines, contract/safety preservation, and independent acceptance. 2.0.0 extracts checklists and decision-log templates into `references/checklists.md`. |

### Retired root skills (2.0.0)

Retired based on blinded zero-skill baseline-delta evaluation (`docs/specs/catalog-consolidation/plan.md`, zero executables, negative delta against modern baseline models):

| Skill | Disposition | Reason |
|---|---|---|
| `mneves-superaudit` | retired | Blinded delta `-2`; broad repo audits are served directly by `untangle-codebase`, `autoreview`, `mneves-agent-readiness`, and `mneves-verify`. |
| `mneves-socratic-tutor` | retired | Blinded delta `-2`; codebase teach-back with SQLite SM-2 stays in `mneves-teach-back-srs`. |
| `mneves-eli5` | retired | Blinded delta `-1`; modern models handle audience-calibrated plain-language explanations directly without a standalone skill. |

## pstack collection: the 36 existing skills

| Skill | Disposition | Patches | Reason and kept controls |
|---|---|---|---|
| `architect` | changed | none | 2.0.0: upstream simplified to one-file brief + route to `arena` (no separate Models section). |
| `arena` | retained | 01, 02, 07 | Parallel attempts; model routing and engineering-reference links. |
| `automate-me` | changed | 02, 05 | Asks before mining transcripts; writes or opens a PR only after approval. |
| `babysit` | changed | 04, 06 | Thin route: defers to `babysit-pr` when installed, with a complete `gh` fallback; one owner per PR, head-branch writes only, paginated comments, round cap reported as blocked and yielding to stricter limits. |
| `benchmark-checklist` | retained | 02 | Links repaired to the engineering references. |
| `blast-radius` | retained | 02 | Same. |
| `bro` | retained | none | One-paragraph restatement; nothing to consolidate. |
| `correct` | changed | 05 | Adds rules only in a requested run. |
| `create-verification-skill` | retained | none | Upstream update only. |
| `deslop` | retained | none | Cursor team-kit skill, unchanged. |
| `figure-it-out` | retained | 02 | Engineering-reference links. |
| `fix-ci` | retained | none | Unchanged. |
| `fix-merge-conflicts` | retained | none | Unchanged. |
| `get-pr-comments` | changed | 05 | Reads every page of review comments. |
| `how` | changed | 12 | 2.0.0: upstream simplified to one-file read-only explorer (no Models section); `12` tightens description against non-codebase conceptual questions. |
| `interrogate` | changed | 01, 07 | Model routing; upstream and the port now ship it as one file, so its four former references are gone. |
| `ketchup` | retained | none | Upstream update only; read-only catch-up. |
| `maintain-verification-skill` | retained | none | Upstream update only. |
| `make-pr-easy-to-review` | retained | none | Unchanged. |
| `no-comments` | retained | 01, 02, 07 | Uses the shipped `comment-sicko` brief. |
| `poteto-help` | retained | 02 | Recipes point at the engineering references. |
| `poteto-mode` | changed | 01, 02, 05, 06, 07, 08, 09, 10, 11, 12 | Local-only autonomy with stops before external writes (including `worker.md` in `12`); finite repair bound in Babysit; four engineering references; Codex substitutes exempt from Opus-medium (`08`) plus Agy fallback (`11`); DeepSeek Harness (`dsh-tools.md`) excluded (`12`). |
| `recall` | changed | 02, 05, 09 | Reads chat history only on request. |
| `reflect` | changed | 05 | 2.0.0: upstream simplified to one file with no subagents/Models; `05` keeps backlog filing gated on user approval. |
| `setup-pstack` | retained | 01, 02, 07 | Model sheet setup. |
| `show-me-your-work` | retained | 02 | Links repaired. |
| `swarm` | retained | 01, 07 | Model routing. |
| `tdd` | retained | 03 | Failing test first for every bug fix or feature; name kept by the owner's choice. |
| `teach` | retained | 02 | Explains through `how` and `why`; name kept by the owner's choice. |
| `technical-writing` | retained | 02 | Links repaired. |
| `thermo-nuclear-code-quality-review` | changed | 05 | Runs only by name, so routine reviews do not stack it on `autoreview`. |
| `thermo-nuclear-review` | changed | 05 | Same. |
| `thermos` | changed | 01, 05, 07 | Same, plus model routing. |
| `typescript-best-practices` | changed | 02, 12 | `paths` moves under `metadata:`; `12` tightens description to skip trivial copy/label edits. |
| `what-did-i-get-done` | changed | 09 | Trimmed fixed bullet-count caps. |
| `why` | changed | 04 | 2.0.0: upstream simplified to one 48-word file (no Models section); `04` keeps strict read-only + never-retry-denied-reads rule. |

## Upstream pstack names not carried as-is (32)

| Name | Disposition | Reason |
|---|---|---|
| `statechart` | added | Explicit invocation only (05). The runner installs nothing and stops naming the `mise install` command (05); it renders with Pele only when available or authorized, otherwise hands over Mermaid text, and works in an allowed scratch folder (06). Its upstream test corpus is excluded; `tools/scripts/statechart-runner.test` covers the adapted runner. |
| `create-formal-verification-skill` | added | Explicit invocation only (05); installs a verifier only where already authorized, and reads a counterexample trace directly when `statechart` is absent (06). |
| `maintain-formal-verification-skill` | added | Explicit invocation only (05). |
| `ketchup-video` | added | Explicit invocation only (05); renders in an allowed scratch folder with installed tools, and a missing tool is a failed render with a text fallback; without `ketchup` it does the catch-up itself (06). |
| `in-your-own-words` | added | One-line restatement of the user's goal; no tools, no writes. |
| `sharpen` | added | Prompt-deepening instruction; 2.0.0 sync adds upstream prototype-first recommendation line (`bf0c7cd`). |
| `reframe` | added | 2.0.0: explicit-only (`/reframe`, `12`) imported from `cursor/plugins@9e278fe` (pstack 0.15.48); teaches 8–12 verified domain terms, borrows neighboring fields, and rewrites the description. |
| `poteto-mode/references/dsh-tools.md` | excluded | DeepSeek Harness mapping excluded in `sources.json` (DeepSeek disabled across all skills; two mentions removed by `12`). |
| `unslop` | retired (02) | Always-on prose rewrite; replies follow the active writing preferences. |
| `principle-attack-the-premise`, `principle-boundary-discipline`, `principle-build-the-lever`, `principle-encode-lessons-in-structure`, `principle-exhaust-the-design-space`, `principle-experience-first`, `principle-explain-the-number`, `principle-fix-root-causes`, `principle-foundational-thinking`, `principle-guard-the-context-window`, `principle-laziness-protocol`, `principle-make-operations-idempotent`, `principle-migrate-callers-then-delete-legacy-apis`, `principle-minimize-reader-load`, `principle-model-the-domain`, `principle-never-block-on-the-human`, `principle-outcome-oriented-execution`, `principle-prove-it-works`, `principle-redesign-from-first-principles`, `principle-separate-before-serializing-shared-state`, `principle-sequence-verifiable-units`, `principle-subtract-before-you-add`, `principle-test-behavior-not-implementation`, `principle-type-system-discipline` (24) | retired (02) | Consolidated into `poteto-mode/references/engineering-{design,evolution,verification,coordination}.md`, loaded by task instead of as 24 always-available entrypoints. The sync fails if any comes back or is still named. |
| `make-bot-ui` | excluded | Targets Grok Bot webhooks; the port does not carry it and no supporting product ships here. |
