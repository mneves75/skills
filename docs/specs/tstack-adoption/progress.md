# Tstack review — run notes

Updated: 2026-11-04. Status: implementation and independent verification in progress.
Plan: [review and release acceptance](../../../plans/004-tstack-review-release.md).
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

Another active release session owns `release/1.45.0`, is changing the same watcher, and is adding
setup/deployment tooling. This session owns `release/1.45.0-tstack-20261104`. Neither worktree
may overwrite the other. Final integration, versioning and publication ownership remain unresolved;
finish independent regression evidence before asking for a final handoff decision.

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

## Documentation coverage

A separate read-only reviewer read all 37 current Markdown files under `docs/` and the new
`tests.json`; the two historical screenshot assets were excluded from that textual review.
The watcher commit fixes the stale PR #30 status. Remaining documentation integration includes
deferred release-ledger bookkeeping and stale catalog counts in the site and usage-guide intro.
Historical specs and handoffs retain their dates and
original observations. Repeated historical scratch-only setup runners support a small tracked
initialization script; that implementation must be reconciled with the active release session.

## Next acceptance steps

- [x] Reproduce and fix the watcher failures; full suite and independent acceptance pass.
- [x] Complete the all-documents review; preserve historical documents as history.
- [x] Complete fresh Standards and Spec reviews of the watcher; both pass with zero findings.
- [ ] Finish independent site acceptance and review of its final source/documentation diff.
- [ ] Reconcile the active release session's setup/deployment scripts rather than adding duplicates.
   Setup must be repository-local; deployment must preserve exact-commit security/readiness gates
   and must not invent a staging environment for this static Pages repository.
- [ ] Qualify the final integrated tree before merge to main, publication, tag and attributable cleanup.
