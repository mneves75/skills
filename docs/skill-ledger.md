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

The current root catalog has 25 skills: the 23 recorded in the refresh plus the
`untangle-codebase` adoption in 1.46.0 and the `mneves-socratic-tutor` adoption in 1.47.0 below. The opening counts describe the historical
refresh inventory.

## Root skills (25)

| Skill | Disposition | Reason and kept controls |
|---|---|---|
| `autoreview` | retained | Owns the isolated review CLI, its security tests and the `cccc` complexity guidance; `full-stop` reviews through it and `mneves-superaudit` defers to its guidance. |
| `babysit-pr` | changed | Canonical PR watcher. Adds one watcher owner per PR, a finite repair bound (same failure surviving two fixes, or three rounds) that yields to a stricter host or user limit, and no force-push or auto-merge change without the user. `pr-wait` and its fake-`gh` test are unchanged by the pstack refresh; 1.45.0 hardened them (L-9, H-A7: a non-404 answer from a check-run read is an error, a status context without a name is rejected). Follow-up, 2026-11-04 (tstack review, included in the 1.45.1 candidate): `pr-wait` no longer reads a failed required-checks read as "none required", and `ready` stops with exit 1 when it cannot read every review thread; eight fake-`gh` cases added. |
| `council` | retained | Bounded, advisory multi-CLI deliberation; states it is not verification, so it does not duplicate `autoreview` or `mneves-verify`. |
| `full-stop` | changed | Fixes from PR #38: runs only on an explicit invocation ("Full stop." as punctuation is not one), no force-push or rewrite of pushed history, the user's and project's rules on asking before a test method stay in force, and existing auto-merge or merge-queue state is reported, never changed. Never merges. |
| `imagegen-frontend-mobile` | retained | Image-only path for mobile concepts; no overlap with a code skill. |
| `leaving-pr-comments` | retained | The attribution control that `full-stop`, `babysit-pr` and `takeover` name, each with a standalone fallback line. |
| `mneves-agent-readiness` | retained | Pairs with the `tools/` assessor; `mneves-superaudit` item 3 composes it and falls back when it is absent. |
| `mneves-chatgpt-search` | retained | Distinct audience (ChatGPT Search discovery and attribution); no overlap. |
| `mneves-eli5` | retained | Keeps the ELI5 name as the plain-language shortcut. pstack's `bro` restates the last message and `teach` explains a codebase through `how` and `why`; neither replaces an audience-calibrated re-explanation. |
| `mneves-expert-review` | retained | Stress-tests drafts and decisions, explicitly not code diffs, so it does not compete with `autoreview`. |
| `mneves-fable-orchestrator` | retained | Normative routing and the only model Defaults block; the pstack refresh leaves it alone. 1.45.0 re-verified the block's ids and date and added one sentence on what crossing the reviewer columns discloses (`SKILL.md`, "Crossing means"); no model default moves. |
| `mneves-handoff` | retained | Writes context for another agent; pstack's `recall` rebuilds your own. Different jobs. |
| `mneves-motion-film` | retained | Distinct media pipeline with its own checks and tests; its scripts were hardened in 1.45.0 (H-M2 to H-M6), outside the pstack refresh. |
| `mneves-production-readiness` | retained | Readiness gate; imports its security rows from `mneves-security` rather than re-auditing. |
| `mneves-render` | retained | Distinct Markdown export pipeline with Pandoc acceptance tests. |
| `mneves-security` | retained | Owns remediation, privacy/OWASP launch readiness and the exact-candidate deploy verdict; routes a requested deep source audit to `security-audit` and treats its records as candidate evidence, never as a gate. |
| `mneves-ship-deploy` | retained | Release sequence and contract checks; requires the security gate first. |
| `mneves-superaudit` | changed | Names the specialists it sequences (`autoreview`, `mneves-verify`, `mneves-security` or `security-audit`, `mneves-ship-deploy`, `mneves-production-readiness`) instead of restating them, with a direct fallback when one is absent. A source audit is never reported as a deploy gate. |
| `mneves-socratic-tutor` | added | 1.47.0: adapted from janestreet/agent_skills `socratic-tutor` at `7c6715c29548a3b39d4a9545c698ee4fd17a7213`, MIT, Copyright (c) 2026 Jane Street Group, LLC; the `mneves-` prefix is the owner's explicit choice. Owns any-topic tutoring to mastery: diagnostic first, a 0-5 map with untested subskills marked `?`, one question per turn, levels earned on two checks including unprompted recall, spaced review, final assessment and a paste-able save state. Distinct from `mneves-teach-back-srs` (codebase teach-back and stored cards, which keeps "quiz me"), `mneves-eli5` (one explanation) and pstack `teach` (explains a codebase, no quizzes). Markdown only; no executable or mandatory sibling. |
| `mneves-teach-back-srs` | retained | Opt-in quiz and spaced repetition; its SRS helper is unchanged. |
| `mneves-verify` | retained | Independent verdict required by the security and release paths. |
| `modernize` | retained | Rebasing an aging PR is its explicit job; it already decides whether the PR should exist first. |
| `security-audit` | retained | Owns the six-phase source methodology, the coverage and findings schemas and their Node validators; already says it never claims a deploy gate. Validators unchanged. |
| `takeover` | retained | Finishing someone else's work with credit kept; no overlap. |
| `untangle-codebase` | added | 1.46.0: adapted from caldoai/skills at `442c29918339cc8dbf09ae27aaf17b05745465a3`, MIT, Copyright (c) 2026 Maze. Owns bounded structural refactoring using change-together evidence, a dependency graph, Git history and a problem-to-fix log. Bare invocation diagnoses and plans; explicit refactoring requests authorize scoped edits. Protects contracts and safety mechanisms, requires observed baseline and regression proof, makes comment/test cleanup separate opt-ins with assertion preservation, and marks unavailable independent review/acceptance BLOCKED. Distinct from fixed-diff review and broad audit; no mandatory sibling or new executable. |

## pstack collection: the 36 existing skills

| Skill | Disposition | Patches | Reason and kept controls |
|---|---|---|---|
| `architect` | retained | 01, 02, 07 | Planning panel; model routing and engineering-reference links. |
| `arena` | retained | 01, 02, 07 | Parallel attempts; same adaptations. |
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
| `how` | retained | 01, 07 | Model routing. |
| `interrogate` | changed | 01, 07 | Model routing; upstream and the port now ship it as one file, so its four former references are gone. |
| `ketchup` | retained | none | Upstream update only; read-only catch-up. |
| `maintain-verification-skill` | retained | none | Upstream update only. |
| `make-pr-easy-to-review` | retained | none | Unchanged. |
| `no-comments` | retained | 01, 02, 07 | Uses the shipped `comment-sicko` brief. |
| `poteto-help` | retained | 02 | Recipes point at the engineering references. |
| `poteto-mode` | changed | 01, 02, 05, 06, 07 | Local-only autonomy with stops before external writes; its Babysit playbook stops as blocked at a finite repair bound that yields to stricter limits; routes to the four engineering references instead of mandatory principle panels. `scripts/orch/` is no longer in upstream or the port, so it is not shipped. |
| `recall` | changed | 02, 05 | Reads chat history only on request. |
| `reflect` | changed | 01, 02, 05, 07 | Files backlog only with authorization. |
| `setup-pstack` | retained | 01, 02, 07 | Model sheet setup. |
| `show-me-your-work` | retained | 02 | Links repaired. |
| `swarm` | retained | 01, 07 | Model routing. |
| `tdd` | retained | 03 | Failing test first for every bug fix or feature; name kept by the owner's choice. |
| `teach` | retained | 02 | Explains through `how` and `why`; name kept by the owner's choice. |
| `technical-writing` | retained | 02 | Links repaired. |
| `thermo-nuclear-code-quality-review` | changed | 05 | Runs only by name, so routine reviews do not stack it on `autoreview`. |
| `thermo-nuclear-review` | changed | 05 | Same. |
| `thermos` | changed | 01, 05, 07 | Same, plus model routing. |
| `typescript-best-practices` | retained | 02 | `paths` moves under `metadata:`; description still names `.ts` and `.tsx`. |
| `what-did-i-get-done` | retained | none | Unchanged. |
| `why` | changed | 01, 04, 07 | Investigators and synthesizer stay read-only; a denied read is never retried with broader access. |

## Upstream pstack names not carried as-is (32)

| Name | Disposition | Reason |
|---|---|---|
| `statechart` | added | Explicit invocation only (05). The runner installs nothing and stops naming the `mise install` command (05); it renders with Pele only when available or authorized, otherwise hands over Mermaid text, and works in an allowed scratch folder (06). Its upstream test corpus is excluded; `tools/scripts/statechart-runner.test` covers the adapted runner. |
| `create-formal-verification-skill` | added | Explicit invocation only (05); installs a verifier only where already authorized, and reads a counterexample trace directly when `statechart` is absent (06). |
| `maintain-formal-verification-skill` | added | Explicit invocation only (05). |
| `ketchup-video` | added | Explicit invocation only (05); renders in an allowed scratch folder with installed tools, and a missing tool is a failed render with a text fallback; without `ketchup` it does the catch-up itself (06). |
| `in-your-own-words` | added | One-line restatement of the user's goal; no tools, no writes. |
| `sharpen` | added | Prompt-deepening instruction; no tools, no writes. |
| `unslop` | retired (02) | Always-on prose rewrite; replies follow the active writing preferences. |
| `principle-attack-the-premise`, `principle-boundary-discipline`, `principle-build-the-lever`, `principle-encode-lessons-in-structure`, `principle-exhaust-the-design-space`, `principle-experience-first`, `principle-explain-the-number`, `principle-fix-root-causes`, `principle-foundational-thinking`, `principle-guard-the-context-window`, `principle-laziness-protocol`, `principle-make-operations-idempotent`, `principle-migrate-callers-then-delete-legacy-apis`, `principle-minimize-reader-load`, `principle-model-the-domain`, `principle-never-block-on-the-human`, `principle-outcome-oriented-execution`, `principle-prove-it-works`, `principle-redesign-from-first-principles`, `principle-separate-before-serializing-shared-state`, `principle-sequence-verifiable-units`, `principle-subtract-before-you-add`, `principle-test-behavior-not-implementation`, `principle-type-system-discipline` (24) | retired (02) | Consolidated into `poteto-mode/references/engineering-{design,evolution,verification,coordination}.md`, loaded by task instead of as 24 always-available entrypoints. The sync fails if any comes back or is still named. |
| `make-bot-ui` | excluded | Targets Grok Bot webhooks; the port does not carry it and no supporting product ships here. |
