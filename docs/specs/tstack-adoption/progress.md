# Tstack review — run notes

Updated: 2026-11-04. Status: released. The branch's head `c46c77c4` merged to `main` with 1.45.1 (PR #42, `a53b03cf`, published by the automatic route and tagged `v1.45.1` at 12:36Z; 1.45.0 had released the branch at `a322c9f3`); DEL-01 shipped as 1.45.2 (`7587b764`, the owner's CI waiver dispatch, tagged `v1.45.2`).
Plan: [review and release acceptance](../../../plans/005-tstack-review-release.md).
Machine-readable results: [tests.json](tests.json).

## Observed

- Upstream HEAD remains `1085050f3baed1ac724caa4a8166145fb2ac88af`; all nine upstream
  skills already have an adaptation or an explicit decision to fold them into another procedure.
  A sync alone would not improve the installed behavior.
- Source review identified two false-readiness candidates in `pr-wait`: failed required-check
  discovery can become an empty requirement set, and the last 100 review threads do not establish
  that all threads are resolved. Regression reproduction and fixes are in an isolated worktree.
- The detailed plan passed a separate adversarial review after requiring independently recorded,
  exact-commit authorization for any CI exception, binding readiness on the merged commit, and
  a verified GitHub Release. This is plan acceptance, not implementation acceptance.
- `origin/main` was reconciled before work; the merge reported already up to date. Plan commits
  `15e0298` and `2a2ded7` were pushed on the pstack working branch with `[skip ci]` as requested.
  The isolated implementation branch starts at `15e0298`; integration must retain `2a2ded7`'s
  independently authorized CI-exception amendment from the pstack branch.

## What worked

- Comparing the raw pinned source with local adaptations prevented duplicate skills and a
  cosmetic version refresh.
- Reviewing the public CLI's readiness contract exposed concrete failure modes with observable
  pass/fail criteria. The existing fake-GitHub seam supports regression tests without live mutations.
- Isolated worktrees preserved another active release session's changes.

## What did not establish correctness

- Static inspection alone was not reproduction. Builder-run controls now reproduce false
  green/ready results on the original helper and pass on the correction; main inspected both
  logs. The full 44-test suite also passed; main reran six public-CLI regression tests,
  all passing. A fresh verifier then passed 24 independently written, source-blind CLI cases
  against an unchanged helper hash, including ten-poll persistent failure and cross-poll recovery.
  This is watcher acceptance, not live GitHub integration or release approval.
- Historical CI success on `a322c9f` does not validate subsequent changes. GitHub CI is explicitly
  skipped for this task; local and independent checks must retain their actual scope.
- Skill-use counts in conversation logs do not prove that a skill causes better outcomes.

## Rendered site review

The requested taste inspector ran against the real local page at 1440, 768 and 390 pixels.
It exited 1 with eight design-rule failures and seven warnings; retain that original result.
Viewed desktop/mobile folds and the desktop contact sheet. The correction removes redundant
hardcoded counts, fixes dark-mode inline-code contrast on highlighted cards (about 1:1), and
replaces the vague headline. Release labels and install commands/buttons now have a 13px floor,
including the mobile overrides identified in source after the inspector flagged small text.

The inspector's demands for photography, video and decorative movement are marketing-style
heuristics, not this product's acceptance criteria. A static procedure index has no supplied
photographic evidence and needs none to help a visitor choose and install a skill. Preserve the
documented wayfinding layout and category separators rather than manufacture media or erase
structure to make that generic score green. Final browser acceptance still must prove contrast,
responsive layout, links, focus and clipboard behavior after the actual fixes.

The same new browser regression failed on the original page solely at dark inline-code contrast
(1.01:1), then passed all five checks on the correction: unavailable/rejected/successful clipboard
and light/dark contrast. The same five cases also passed after the final title and typography
changes, and final desktop/mobile renders were inspected. The inspector now reports four style
failures and seven warnings; contrast, headline wrapping and small-text findings are cleared.
Photography, animation and separator requirements are rejected for this document index; its
"eyebrow" heuristic labels the existing compatibility text above the next section. These remain
recorded inspector failures, not a claim that the generic score passed.

## Open coordination

Another active release session owns `release/1.45.0`, changes the same watcher, and adds
setup/deployment tooling. This session's isolated fixes were merged into the existing pstack
working PR at `d0ac1a2`, preserving the newer plan and run notes. Its temporary branch and
worktree were then removed. The other session's worktree remains untouched. Final release
integration, versioning and publication ownership remained unresolved then (settled
2026-11-04; see the 1.45.2 paragraph below).

The other session's recorded plan still waits for main CI, whereas the current task explicitly
skips GitHub CI and staging. Reconcile that discrepancy before publication. No deployment or
release tag has been produced by this session.

Its tooling commit `18729c0` now contains `tools/scripts/init.sh` and `deploy.sh`.
Read-only inspection confirms that the deployment script waits for main CI and copies both
security and readiness records to the merge SHA. Those behaviors do not satisfy this task's
CI exception or the binding readiness requirement in plan 004. Do not run it for this release
until the publishing session reconciles those contracts. A production entrypoint must use the
existing Pages transport; `hmo` must refuse before side effects because no such target exists.

The isolated watcher unit is committed and pushed as `3cbe27c`. Both independent code-review
axes passed with zero findings. Main also validated the skill with `agentskills`, regenerated
the usage guide, and ran all `build-site.test` controls successfully. A global-cache write was
denied during setup; installing the locked tools with Bun's documented repository-local
`--cache-dir` succeeded without changing global configuration or the lockfile.

The site unit is `e6a9830`: both review axes pass with zero findings. Fresh independent local
acceptance passed both copy controls' three outcomes, light/dark contrast, six viewport/theme
font and overflow checks, keyboard navigation/focus, all 23 guide anchors and reduced-motion
visibility. Final source and served bytes matched; the guide's count-free opening was rechecked
after regeneration. The working-branch merge preserves the exact verified helper and site hashes.

## Documentation coverage

A separate read-only reviewer read all 37 current Markdown files under `docs/` and the new
`tests.json`; the two historical screenshot assets were excluded from that textual review.
The watcher commit fixes the stale PR #30 status; the site unit removes stale catalog counts from
the landing page, its README and the usage-guide intro. Deferred release-ledger bookkeeping still
belongs to final release integration.
Historical specs and handoffs retain their dates and
original observations. Repeated historical scratch-only setup runners support a small tracked
initialization script; that implementation must be reconciled with the active release session.

## DEL-01 CI waiver (2026-11-04)

Implemented on `release/1.45.1-ci-waiver` from candidate `63d95fe`: `static.yml` accepts an owner's
CI waiver only for a manual dispatch naming the exact `main` tip that the `github-pages`
environment's `CI_WAIVER_APPROVED_SHA` approves, with a nonblank reason, and records `CI WAIVED,
not passed`. `check-pages.test.py` runs the real guard on temporary Git with a fake `gh`: 32 cases
(27 explicit, 5 CI conclusions) plus a structure test. Before the guard change the new test failed
19 cases against the original workflow; after it, all pass, and all 10 planted mutations of the
guard fail the test. `actionlint` and `git diff --check` are clean. CONTRIBUTING documents the
manual sequence: gates on the candidate tree, `[skip ci]` merge, a fresh readiness binding run on
the pushed merge commit, environment approval, dispatch, served-byte comparison, approval deletion
even on failure, and the tag.

Not established: the live route on GitHub (environment variable scope, `[skip ci]` suppressing
the automatic run, the dispatch itself). Independent review, the binding run and publication are
pending. Publisher ownership with the concurrent release session was then unresolved.

Review, 2026-11-04: independent behavioral and Standards review passed at `74f4e6c`. The Spec
review failed with one P2: `vars.CI_WAIVER_APPROVED_SHA` also resolves a same-name repository or
organization variable, so the shell cannot prove the approval's environment-only provenance, and
the default `GITHUB_TOKEN` cannot read environments (a separate token or App was judged
disproportionate). The reviewer accepted an operator gate instead: before dispatch the publisher
reads the matching id from the `github-pages` environment variable endpoint, proves no same-name
repository variable, and rules out organization inheritance by the verified owner type; any read
error or unknown scope blocks, the evidence is bound to the merge commit, and the snapshot does not
stop a concurrent configuration change. CONTRIBUTING, plan 005, the readiness ledger and plan, the
changelog bullet and the structure test's message now say the workflow enforces only equality with
the resolved value. The guard and the behavioral assertions are unchanged. The Spec re-verification
is pending. The owner has since asked to deploy and the main session owns publication, which
settles the ownership question above; security, readiness and the live release remain pending.

Release 1.45.2, 2026-11-04: the concurrent session's 1.45.1 (PR #42) merged to `main` as `a53b03c`
without DEL-01; its main CI run's first attempt was cancelled, its second succeeded, Pages published
it at 12:35Z and `v1.45.1` was tagged at 12:36Z (the statement that it was unpublished was true at 12:25Z). This branch carries `74f4e6c`
(the guard, pushed with PR #43), `5cbdf10` (the operator gate) and `9efe4d8` (the merge of that
`main`), so the candidate is 1.45.2: 1.45.1's content plus DEL-01. The main session publishes it
through CONTRIBUTING's manual sequence, with the operator gate before dispatch. Pending: the Spec
re-verification, the security gate and the readiness binding run on the final tree, the operator
gate, publication, the served-byte check and the `v1.45.2` tag. The readiness cursor stays at the
deployed `ccd51b4b`.

## Next acceptance steps

- [x] Reproduce and fix the watcher failures; full suite and independent acceptance pass.
- [x] Complete the all-documents review; preserve historical documents as history.
- [x] Complete fresh Standards and Spec reviews of the watcher; both pass with zero findings.
- [x] Finish independent site acceptance and both review axes of its final source/documentation diff.
- [ ] Reconcile the active release session's setup/deployment scripts rather than adding duplicates.
   Setup must be repository-local; deployment must preserve exact-commit security/readiness gates
   and must not invent a staging environment for this static Pages repository.
- [x] Implement DEL-01's exact-commit CI waiver with failing-first and planted-mutation controls.
- [ ] Spec re-verification of DEL-01's operator-gate correction (behavioral and Standards passed at `74f4e6c`).
- [ ] Qualify the final integrated tree before merge to main, publication, tag and attributable cleanup.

## Cleanup and handoff

Removed this session's consumed worktree (about 243 MiB apparent size, including its local tools
and cache) and its local/remote temporary branch. Stopped both temporary HTTP servers and the
implementation CLI; browser sessions closed. Private regression, review and screenshot evidence
is retained for release acceptance. Preserved the other release worktree, historical handoffs,
prior gate records and source snapshots still needed for the release.

No merge to main, version bump, production tag or deployment was performed by this session.
The publishing session must incorporate PR #40's verified follow-up commits, reconcile its
deployment script with the explicit CI skip, then run the final exact-tree release gates.
Since then PR #42 merged those commits as 1.45.1 (`a53b03c`); 1.45.2 publishes through
CONTRIBUTING's manual CI-waiver sequence, not `deploy.sh`.
