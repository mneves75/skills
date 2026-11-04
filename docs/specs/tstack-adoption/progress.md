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
  `15e0298` and `2a2ded7` were pushed with `[skip ci]` as requested.

## What worked

- Comparing the raw pinned source with local adaptations prevented duplicate skills and a
  cosmetic version refresh.
- Reviewing the public CLI's readiness contract exposed concrete failure modes with observable
  pass/fail criteria. The existing fake-GitHub seam supports regression tests without live mutations.
- Isolated worktrees preserved another active release session's changes.

## What did not establish correctness

- Static inspection alone was not reproduction. Builder-run controls now reproduce false
  green/ready results on the original helper and pass on the correction; main inspected both
  logs. The full suite and fresh independent acceptance remain separate requirements.
- Historical CI success on `a322c9f` does not validate subsequent changes. GitHub CI is explicitly
  skipped for this task; local and independent checks must retain their actual scope.
- Skill-use counts in conversation logs do not prove that a skill causes better outcomes.

## Rendered site review

The requested taste inspector ran against the real local page at 1440, 768 and 390 pixels.
It exited 1 with eight design-rule failures and seven warnings; retain that original result.
Viewed desktop/mobile folds and the desktop contact sheet. Three useful corrections are selected:
the stale 22-skill count, dark-mode inline-code contrast on highlighted cards (about 1:1), and
the vague headline. Small readable copy also needs checking against the measured selectors.

The inspector's demands for photography, video and decorative movement are marketing-style
heuristics, not this product's acceptance criteria. A static procedure index has no supplied
photographic evidence and needs none to help a visitor choose and install a skill. Preserve the
documented wayfinding layout and category separators rather than manufacture media or erase
structure to make that generic score green. Final browser acceptance still must prove contrast,
responsive layout, links, focus and clipboard behavior after the actual fixes.

## Open coordination

Another active release session owns `release/1.45.0`, is changing the same watcher, and is adding
setup/deployment tooling. This session owns `release/1.45.0-tstack-20261104`. Neither worktree
may overwrite the other. Final integration, versioning and publication ownership remain unresolved;
finish independent regression evidence before asking for a final handoff decision.

The other session's recorded plan still waits for main CI, whereas the current task explicitly
skips GitHub CI and staging. Reconcile that discrepancy before publication. No deployment or
release tag has been produced by this session.

## Documentation coverage

A separate read-only reviewer read all 37 current Markdown files under `docs/` and the new
`tests.json`; the two historical screenshot assets were excluded from that textual review.
Current corrections are the stale PR #30 status, deferred release-ledger bookkeeping and the
public site's stale catalog counts. Historical specs and handoffs retain their dates and
original observations. Repeated historical scratch-only setup runners support a small tracked
initialization script; that implementation must be reconciled with the active release session.

## Next acceptance steps

1. Finish the fail-before/pass-after watcher controls and review the complete bounded diff.
2. Complete the all-documents review and record actionable current contradictions, preserving
   historical documents as history.
3. Run fresh independent code review and `mneves-verify` on the fixed artifact.
4. Reconcile the active release session's setup/deployment scripts rather than adding duplicates.
   Setup must be repository-local; deployment must preserve exact-commit security/readiness gates
   and must not invent a staging environment for this static Pages repository.
5. Qualify the final integrated tree before merge, publication, tag and attributable cleanup.
