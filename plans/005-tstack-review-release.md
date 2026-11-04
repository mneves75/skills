# Plan 005: close tstack readiness gaps and release the reviewed catalog

## Status

- Priority: P1. Risk: medium (a readiness verdict and a production-publication guard).
- Category: correctness, verification, documentation, release.
- Planned at: `a322c9f3adfc03fabb17bdfb95c949d5bb6ef2f3`, 2026-11-04.
- Scope: this repository. No global skill installation, unrelated dependency update, new framework or wholesale visual redesign.
- Authorization: implement, version, push, merge related work, tag, deploy production and clean task-owned artifacts. The owner explicitly skips staging and GitHub CI; local checks and security/readiness gates remain required.

## Deeper brief

A professional starts from immutable upstream source, local adaptations, real executable helpers and their failure paths, rather than importing a README's recommendations. Compare actual contracts, prove each defect with a failing control, preserve local safety rules, and independently verify the released artifact. Optimize for five-year maintenance with explicit provenance and repeatable tests, not speculative skills or trend-driven dependencies.

Rewritten task: reconcile origin; inspect all nine tstack procedures at a pinned revision; update or add only what has demonstrated value; retain a per-skill decision record; implement verified correctness fixes; run adversarial review and independent acceptance; update the version and relevant documentation; merge the related branches once, publish under the explicit CI waiver, verify production, tag and clean up.

## Current evidence and decisions

`origin/main` was fetched and merged before work: already up to date. HEAD contains the reviewed pstack refresh from PR #40. PR #38 contains overlapping workflow corrections; reconcile it into the release branch without reverting the newer generated collection. PR #39 is an unrelated dependency update and is excluded.

The current tstack upstream HEAD is `1085050f3baed1ac724caa4a8166145fb2ac88af` (2026-10-28), already the revision named in the local adaptations. There is no upstream version drift to manufacture. Record a review date without claiming a new source revision.

| Upstream procedure | Decision |
|---|---|
| full-stop | Retain the self-contained adaptation and explicit invocation/merge boundaries |
| full-send | Retain its useful procedure within full-stop; do not add a duplicate merging skill |
| sol-loop | Retain bounded independent review in autoreview, council and full-stop |
| file-pr | Retain its problem-first PR guidance in existing delivery skills |
| babysit-pr | Fix the two incomplete-read paths below; retain all existing hardening |
| takeover | Retain authorship, handoff verification and standalone fallbacks |
| modernize | Retain relevance checks, observed-head lease and authorship controls |
| leaving-pr-comments | Retain attribution and truthful evidence requirements |
| council | Retain the bounded advisory workflow and explicit missing-result handling |

### COR-01: unknown required checks can become no required checks

`skills/babysit-pr/scripts/pr-wait:311-329` logs non-404 failures from the two protection APIs and returns a partial/empty set. `poll()` caches that set and can declare green using only observed checks. Change this so failed reads cannot become successful readiness evidence. Preserve the existing documented 404 behavior and distinguish transient recovery from permanent failure through the existing `GhError` path. Never cache a partial result.

### COR-02: an old unresolved thread can fall outside the readiness read

The GraphQL query requests `reviewThreads(last: 100)` without pagination metadata. `poll()` checks only those returned nodes before declaring ready. Request `pageInfo.hasPreviousPage` and fail ready closed when coverage is truncated or unknown. The recommended bounded solution reports manual review and exits 1; it does not invent a complete read. Keep `green` about checks, not discussion threads.

Alternative considered: implement full backward pagination, cursor validation and bounded retries. This would preserve automation for very large PRs but expands maintenance without demonstrated demand. Prefer the explicit coverage limit in this release. Literal upstream replacement is rejected because it would remove local safeguards.

### DEL-01: explicit CI skip conflicts with the production guard

`.github/workflows/static.yml` currently requires successful main-push CI even for manual dispatch. Do not silently ignore the owner's skip, fake CI success or weaken the default automatic path. Add a narrow manual exception requiring an exact full commit SHA and a nonblank reason, with the checked-out SHA equal to that supplied SHA, the current main tip, and the resolved `vars.CI_WAIVER_APPROVED_SHA`, an independently authorized SHA set in the protected deployment environment. The workflow enforces only that resolved equality: a repository or organization variable of the same name could supply the value, and the default token cannot read environment scope, so before dispatch the publisher runs the operator gate in `CONTRIBUTING.md` (the environment variable equals the merge SHA, no same-name repository variable, and, for an organization-owned repository, no same-name inherited organization variable; any read error or unknown scope blocks) and keeps that evidence bound to the merge SHA. No new script, dependency or token. The authorized publisher sets that nonsecret approval value only after final acceptance and removes it after publication, whether publication succeeded or failed; dispatch inputs cannot create or update it. Missing, invalid, incomplete or mismatched approval data fails. Automatic events cannot use the exception. Ordinary dispatch/rollback continues to require successful CI. Pass inputs as environment data, never interpolate them into shell code; report CI as waived, not passed. Workflow dispatch is the existing Pages transport, not the skipped CI workflow. If the required separate approval cannot be established under the owner's authority, publication remains blocked.

Alternative considered: permanently relax all manual deployment checks. Rejected because it would silently widen publication authority. The selected exception is explicit and commit-bound; its use still requires the user's authorization and private exact-candidate gates.

Progress, 2026-11-04: implemented on `release/1.45.1-ci-waiver` from `63d95fe` and proven locally (the extended `check-pages.test.py` failed 19 cases against the original guard, then passed 32 guard cases plus the structure test; 10 of 10 planted mutations killed; `actionlint` clean). The manual release sequence is in `CONTRIBUTING.md`. Independent review, the binding readiness run on the merge commit and publication are pending; the live GitHub route is untested. Revised 2026-11-04 after the independent Spec review (FAIL, P2: the shell cannot prove the approval's environment-only provenance): the approval's scope is now an operator gate before dispatch, documented in `CONTRIBUTING.md`; the guard is unchanged. Standards and behavioral review passed at `74f4e6c`; the Spec re-verification is pending. The main session owns publication. The waiver ships in 1.45.2: 1.45.1 (PR #42) merged to `main` as `a53b03c` without it and was not published, and this branch carries `74f4e6c` (the guard, pushed with PR #43), `5cbdf10` (the operator gate) and `9efe4d8` (the merge of that `main`).

## Implementation ownership and order

Use one isolated release worktree and an authorized implementation model. Other work may exist: preserve the main checkout's untracked `docs/handoffs/`, old gate evidence, and unrelated branches. A concurrent `release/1.45.0` worktree appeared after recon; this task uses a separate uniquely named branch and must resolve publisher ownership before versioning, integration or deployment (resolved 2026-11-04: the owner asked to deploy and the main session publishes). Independent watcher fixes can continue. Never force-push. Use small commits with `[skip ci]` for this task's new commits, including the eventual merge commit, so the owner's CI skip is honored.

1. **Reconcile related history.** Inspect PR #38's complete diff and merge its branch into the release branch. Preserve its intended behavior already present in PR #40; keep the latest generated pstack output. Do not hand-edit generated collection files. Record any conflict resolution and prove no earlier control was lost. Do not merge to main yet.
2. **Reproduce and fix COR-01/COR-02.** Search for every copy of the same failure pattern in shipped helpers. Extend the existing fake-gh behavioral suite first and retain the failing output on the original helper. Then implement the smallest correction and rerun the original controls and full watcher suite. Update the skill's exit/coverage contract.
3. **Implement DEL-01 with planted controls.** Extend `tools/scripts/check-pages.test.py`, which executes the actual workflow guard against real temporary Git history and a fake CI provider. Prove the new positive exception and all refusal cases before changing the guard. Preserve default CI and rollback behavior.
4. **Document the tstack review and release.** Correct the stale PR #30 status in `docs/specs/tstack-adoption/map.md`; add the all-nine disposition/provenance record there or in the existing spec area. Update relevant README/HOWTO/AGENTS/CONTRIBUTING content. Keep CLAUDE.md as the pointer it is. Fold the prior released gate bookkeeping into the readiness ledger according to CONTRIBUTING; do not publish private findings or waiver records.
5. **Review the public surface.** Use Impeccable and the installed tasteskill implementation (`design-taste-frontend`) for a bounded review of the existing design. Preserve PRODUCT.md/DESIGN.md and existing user flows. Correct factual drift (the landing page still says twenty-two while the root catalog contains twenty-three), broken links or demonstrated accessibility defects. Do not replace the visual identity solely to follow a trend. Inspect desktop, tablet and narrow mobile, keyboard focus, themes, reduced motion and clipboard failure recovery.
6. **Version and freeze.** Release version 1.45.0 (superseded: 1.45.0 and 1.45.1 landed from other branches first, so this candidate is 1.45.2), align VERSION/README badge/top changelog and generated site. Reverify the orchestrator's model Defaults against current vendor evidence before changing its verification date. Run local gates, commit the finished candidate, and stop source edits while independent review and the full exact-tree release audits run.
7. **Accept, publish and close.** Fresh Standards and Spec reviews, mneves-verify behavior acceptance, full mneves-security gate, and provisional production readiness must complete before landing. Existing owner waivers may be reused only after proving identity/scope/expiry; never invent a waiver or convert an unknown into PASS. Re-fetch and verify the base immediately before integration; any changed integration tree requires requalification. Merge the related history once and prove tree equality. Security may reuse its opinion for an identical tree; readiness must perform its own binding run on the actual pushed merge SHA, reusing only eligible evidence, rather than relabeling an old record. Establish the separately authorized exact-SHA deployment approval, pass the operator gate on its provenance with evidence bound to the merge SHA, dispatch Pages with the explicit CI waiver, compare served bytes and run production smoke checks, then remove the temporary deployment approval, also when any of these steps fails. Create and push the annotated production tag and publish a GitHub Release with sanitized notes; verify release, tag and production identity. No staging environment or beta suffix is applicable. Delete only merged task branches/worktrees and attributable unnecessary scratch; retain release evidence.

## Test contract

- Required-check API permanent failure and partial-source failure: nonzero exit; no green/ready line.
- Transient required-check failure followed by recovery: complete requirements are applied; a missing required check remains pending. Legitimate no-protection behavior remains unchanged.
- Exactly 100 resolved threads with complete pagination metadata: ready is allowed when other gates pass.
- Omitted older threads, missing/null/malformed pagination metadata: never ready; explicit incomplete-coverage failure.
- Visible unresolved thread: existing blocked behavior survives. `green` keeps its checks-only meaning.
- Deployment exception: exact current main SHA + reason + matching separately authorized deployment-environment SHA on manual dispatch succeeds without querying CI; stale/foreign/malformed/mismatched SHA, missing approval, missing/blank reason and automatic-event attempts refuse. A different future main SHA with a valid reason cannot reuse the approval. Default failed/missing CI, unmerged refs and stale automatic runs still refuse; successful historical rollback remains permitted by the original route.
- Public surface: actual rendered counts/links match the catalog, no narrow-width overflow, keyboard-visible controls, and copy success/denied/unavailable cases pass.

## Verification commands

| Command | Expected result |
|---|---|
| `python3 skills/babysit-pr/tests/test_pr_wait.py` | All old and new behavioral controls pass |
| `python3 tools/scripts/check-pages.test.py` | Actual workflow guard accepts only intended cases |
| `.scratch/skills-ref/bin/agentskills validate skills/babysit-pr` | Valid skill |
| `tools/scripts/check-defaults-block.sh` | Release/date/defaults agree |
| `python3 tools/scripts/check-readiness-catalog.py` | Catalog and ledger consistent |
| `tools/scripts/build-site.sh` and `bash tools/scripts/build-site.test` | Generated site current and controls pass |
| `bash tools/scripts/check-site-copy.sh <preview-url>` | Three clipboard cases and two contrast cases pass in a real browser |
| `cccc --no-cache --min 0 <changed-supported-source>` | Record actual coverage and diagnostics; no invented threshold |
| Existing local CI-equivalent checks appropriate to the changed tree | Passing results, with reused unchanged evidence and untested platforms explicit |

GitHub CI and staging are explicitly skipped for this release. Their absence is not a test pass. Use the deployment workflow only as the authorized production transport.

## Frozen acceptance and stopping conditions

All nine tstack decisions have source evidence; both readiness defects have fail-before/pass-after proof; prior tests and authority controls survive; the deployment exception is exact-commit, manual and explicit, and its approval's environment-only provenance is proved by the operator gate before dispatch; docs and version agree; independent reviews have no unresolved blocking findings; security/readiness verdicts are valid for the final tree; production matches that tree; the tag records the real CI waiver and gate outcomes. No raw conversation histories, secrets or personal machine paths enter shipped files.

Stop for an actual missing permission or protected operation, a confirmed blocker requiring owner evidence, or the same bug surviving two corrections. A failed local test must be investigated, not relabeled or weakened. A source change after candidate freeze requires refreshed review/audit for the changed tree. If a tool safety hook refuses cleanup, retain the exact paths and explain the block rather than bypassing it.

## Primary references

- https://github.com/t3dotgg/tstack/tree/1085050f3baed1ac724caa4a8166145fb2ac88af
- https://agentskills.io/specification
- https://agentskills.io/skill-creation/evaluating-skills
- https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs
- https://www.w3.org/TR/WCAG22/
