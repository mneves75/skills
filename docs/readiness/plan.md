# Production readiness plan

> Historical note (2026-10-18): this plan predates the retirement of the two SRE candidate
> skills into `docs/sre-guides/`. Where it names the seven-file skill manifest or the follow-up,
> it describes the candidate as it was then; it was not re-run on the guides-only candidate.

Source: [ledger.md](ledger.md), provisional baseline of 2026-10-18 at
1f9d8fbc8b1229efb4e465f23665e42314433627. Every entry is proposed work: none is authorized,
started or exercised by this document, and owners are proposed roles, not accepted
assignments. Production readiness stays **NOT READY** until the exact final candidate has a
binding gate run with no open blocker, including the security gate record for that commit, and
the owner gaps below are closed or waived by a named owner. A waiver is the owner's decision; no
entry here grants one.

Blockers come first, ordered by failure class (exposure, then undetected outage, then
unrecoverable change); dependencies between entries are stated inside each entry. No `contract`
row is active. Advisory entries follow.

## 1. Security and compliance rows from the security gate

- Current source assessment, 2026-10-26 at `bb3080a`: SEC-12 and SEC-13 PASS, independently
  accepted. Open IDs: SEC-17 (NOT TESTED), SEC-20 (FAIL, restricted), SEC-21 (NOT TESTED),
  SEC-23 (FAIL, restricted) and CMP-06 (NOT TESTED). SEC-20 and SEC-21 are advisory in the
  readiness profile but remain production blockers through the security verdict. These five
  IDs plus DEL-04, DEL-09, ASY-02 and OPS-04 are nine distinct open controls. The binding
  production run at `cc7285e` (2026-10-27) waived all nine for that single release only, to
  2026-10-28T03:37:58Z; they stay open here until implemented.
- Failure it prevents: publishing a candidate whose security gaps are unknown or unaccepted.
- Change:
  1. Keep restricted details out of tracked files. They belong in the ignored
     release decision packet under `.scratch/` or a private tracker.
  2. Run the secrets scan on the frozen final candidate (SEC-12).
  3. Complete the access review that `SECURITY.md:48-50` defines (collaborators, deploy keys,
     OAuth and GitHub App grants, personal access tokens) and record its date (SEC-17).
     Approving one production deploy does not complete this inventory.
  4. Resolve SEC-20, SEC-21 and SEC-23 using the evidence/actions in the private release
     decision packet, or record explicit named owner waivers with a reason and expiry.
  5. Verify provider and backup retention against `SECURITY.md:92-108`, or record a dated owner
     statement saying where that proof lives (CMP-06).
  6. Run the security deploy gate on the exact candidate and target.
- Owner type: code/scanner evidence (SEC-12, SEC-13); people or process (the five open IDs).
- Size: change.
- Dependencies: the final candidate is frozen and pushed (entry 4).
- Acceptance: a security gate record for the exact commit and production target with no open
  `block`, or each remaining block waived there by a named owner with an expiry.
- Rollout and recovery: evidence only; nothing deploys. A gate that blocks leaves the current
  production site untouched.
- Mechanical gate: Pages enforces CI success and source ancestry through `static.yml`.
  This repository's security/readiness records are operating requirements before merging;
  that workflow does not itself enforce them. The merger must check the exact-candidate
  verdicts before publishing.

## 2. Second administrator and account recovery

- ID: OPS-04 (FAIL). Evidence: "One maintainer administers the repository"
  (`SECURITY.md:37-38`).
- Failure it prevents: losing the only administrator account loses the repository, the Pages
  site and the release path, with no one able to recover them.
- Change:
  1. The owner adds a second administrator with strong authentication, or moves the repository
     to an organization that has two.
  2. The owner stores the recovery codes for each administrator in a company vault.
  3. The owner writes a dated statement naming who administers what and where the proof lives.
  4. If no second person is available, the owner records a waiver with a named owner, an expiry
     and a plan. This document does not grant one.
- Owner type: people or process.
- Size: quick fix once a second person is chosen.
- Dependencies: none.
- Acceptance: the owner's statement, at most 180 days old, covering two administrators and the
  vault location, or the owner's named waiver.
- Rollout and recovery: adding an administrator is reversible by removing the account.
- Mechanical gate: none; the statement is checked for age on each baseline.

## 3. Certificate and domain expiry

- IDs: DEL-09 (NOT TESTED); advisory OBS-03 and OBS-04 (NOT TESTED). Evidence, production,
  2026-10-18: a TLS handshake with `https://mneves75.github.io/skills/` showed TLS 1.3 and a
  certificate valid 2026-09-30 to 2026-12-29; `GET /repos/mneves75/skills/pages` reported
  `cname` null and `https_enforced` true. That proves current validity, not alerting.
- Failure it prevents: a certificate or domain lapse that nobody hears about until visitors do.
- Change:
  1. The owner states, dated, that the site uses the provider's own domain (no custom domain)
     and that the provider renews its certificate and domain, citing where that is documented.
  2. Add an external check that alerts a human when the served certificate has fewer than
     21 days left. The same check can carry OBS-03 (uptime) and an OBS-04 alert route.
- Owner type: infrastructure or provider, and people or process for the statement.
- Size: change.
- Dependencies: none.
- Acceptance: production evidence of the expiry check's last green run, plus one test alert that
  reached a human, plus the owner's statement.
- Rollout and recovery: a read-only external check; remove it to undo.
- Mechanical gate: the check fails below 21 days of certificate validity.

## 4. Gates pass for the exact commit that publishes

- Closed 2026-10-26 for DEL-03: `static.yml` publishes only after CI succeeds for a push to
  `main`, and only the `main` tip (ledger row DEL-03). MNT-02 (advisory) stays open: read the
  `main` ruleset through the API and record whether it requires review and the CI checks.

## 5. Exercised rollback

- ID: DEL-04 (NOT TESTED). Evidence: the rollback command is documented
  (`gh workflow run static.yml -f ref=<tag>`, `.github/workflows/static.yml:2`) and its guard
  is controlled locally, but it has never run against the live site.
- Failure it prevents: a bad publication with no tested way back.
- Change, **not authorized until the owner approves this exact action and target**, because it
  changes the public site twice:
  1. After the release is live, roll back: `gh workflow run static.yml --repo mneves75/skills -f ref=v1.40.0`,
     and watch it with `gh run watch <run-id> --repo mneves75/skills --exit-status`.
  2. Compare each served file under `https://mneves75.github.io/skills/` with
     `git show v1.40.0:site/<path>`, allowing for CDN caching.
  3. Roll forward: `gh workflow run static.yml --repo mneves75/skills -f ref=main`, then compare
     the served files with the released tag's `site/` the same way.
  4. Record both runs and comparisons in the release evidence.
- Owner type: infrastructure or provider.
- Size: quick fix.
- Dependencies: entry 1 (security gate) for the release itself.
- Acceptance: release evidence showing the served bytes matched `v1.40.0` and then the release.
- Rollout and recovery: step 3 is the recovery; a fresh `main` push whose CI passes also
  republishes the tip.
- Mechanical gate: each release tag message prints the rollback command for the version before it.

## 6. People seats and continuity (advisory)

- IDs: OPS-05, OPS-06, OBS-07, BR-04 (all NOT TESTED, advisory without stake). Evidence: solo
  operator (`SECURITY.md:37-38`); the ledger's seats are proposed only.
- Failure it prevents: no one else able to deploy, roll back or answer for the site when the
  maintainer is unavailable.
- Change:
  1. The owner accepts or reassigns each proposed seat.
  2. The owner names an on-call backup, or records an OPS-05 waiver with an expiry and a plan.
  3. Write a short recovery plan covering loss of the hosting account, the repository or the
     maintainer, stored outside GitHub.
- Owner type: people or process.
- Size: quick fix.
- Dependencies: entry 2.
- Acceptance: dated owner statements for each row.
- Rollout and recovery: documentation only.
- Mechanical gate: none.

## 7. Handover documentation (advisory)

- ID: MNT-10 (FAIL, advisory). Evidence: publishing is documented (`site/README.md:3-4`,
  `SECURITY.md:44-47`); rollback steps and the rollback and recovery owners are not.
- Failure it prevents: an inheritor who can publish but cannot undo a publication.
- Change: after entry 5, add the exercised rollback and roll-forward steps and their owner to
  `site/README.md`, and link the owners from entry 2.
- Owner type: code.
- Size: quick fix.
- Dependencies: entries 2 and 5.
- Acceptance: source docs naming the steps and owners.
- Rollout and recovery: revert the documentation commit.
- Mechanical gate: none.

## 8. Bind the UI evidence and finish the accessibility pass (advisory)

- IDs: UX-02, UX-03, UX-06, UX-09 (NOT TESTED, advisory). Evidence: local UI run of 2026-10-18,
  described in the ledger header.
- Failure it prevents: accessibility and copy-feedback regressions reaching visitors unnoticed.
- Change:
  1. Confirm that the previewed `site/` bytes are the final candidate's. If any file in `site/`
     changed afterwards, including `howto.html` regenerated from `HOWTO.md`, repeat the run.
  2. UX-03: decide whether the copy fallback needs a support reference. The site has no support
     channel, so the decision may be to record why none applies.
  3. UX-09: exercise back, reload and pasted deep links to a guide heading.
  4. UX-06: run a manual screen-reader pass of the catalog, one guide and the copy control,
     and examine the 19 horizontally offscreen cells that axe left incomplete on the narrow
     dark guide.
- Owner type: code.
- Size: quick fix.
- Dependencies: the final candidate is frozen (entry 4).
- Acceptance: local evidence bound to the candidate's `site/` bytes, for each row's own check.
- Rollout and recovery: evidence only.
- Mechanical gate: `bash tools/scripts/build-site.test` and
  `bash tools/scripts/check-site-copy.sh <site-url>` already exist (`CONTRIBUTING.md:47-51`).

## 9. Hosting settings and edge headers (advisory)

- IDs: DEL-02, DEL-08 (NOT TESTED, advisory). Evidence: the deploy is versioned
  (`.github/workflows/static.yml`); Pages settings and served cache headers were not read.
- Failure it prevents: unnoticed drift in settings that live only in the repository's
  configuration, and stale assets served after a release.
- Change: record the Pages settings (source, HTTPS enforcement) read through the API, and read
  production response headers for HTML and assets.
- Owner type: infrastructure or provider.
- Size: quick fix.
- Dependencies: none.
- Acceptance: a dated API read and a production header capture.
- Rollout and recovery: read-only.
- Mechanical gate: none proposed.

## 10. Bounded provider calls in autoreview

- ID: ASY-02 (NOT TESTED). Evidence: ledger row ASY-02; the reviewer-process deadline is opt-in.
- Failure it prevents: a stalled provider call holding a review, and an agent waiting on it, forever.
- Change: give `--engine-timeout-seconds` a default (for example 3600 s) with an explicit way to
  disable it, test it against a fake engine that never exits, and document the default.
- Owner type: code. Size: quick fix. Dependencies: none.
- Acceptance: a test where a fake engine sleeps past the default fails the run with a timeout.
- Rollout and recovery: revert the default; long reviews can pass a larger value meanwhile.
- Mechanical gate: the test above in `skills/autoreview/scripts/run-tests.py`.

## Index

| Open ID | Status | Entry |
|---|---|---|
| ASY-02 | NOT TESTED | 10 |
| BR-04 | NOT TESTED | 6 |
| DEL-02 | NOT TESTED | 9 |
| DEL-04 | NOT TESTED | 5 |
| DEL-05 | NOT TESTED | — (advisory, not planned) |
| DEL-07 | NOT TESTED | — (advisory, not planned) |
| DEL-08 | NOT TESTED | 9 |
| DEL-09 | NOT TESTED | 3 |
| CST-01 | NOT TESTED | — (advisory, not planned) |
| CST-02 | NOT TESTED | — (advisory, not planned) |
| OBS-02 | NOT TESTED | — (advisory, not planned) |
| OBS-03 | NOT TESTED | 3 |
| OBS-04 | NOT TESTED | 3 |
| OBS-05 | NOT TESTED | — (advisory, not planned) |
| OBS-07 | NOT TESTED | 6 |
| OBS-09 | NOT TESTED | — (advisory, not planned) |
| OBS-10 | NOT TESTED | — (advisory, not planned) |
| TST-04 | NOT TESTED | — (advisory, not planned) |
| TST-06 | NOT TESTED | — (advisory, not planned) |
| TST-07 | NOT TESTED | — (advisory, not planned) |
| UX-01 | NOT TESTED | — (advisory, not planned) |
| UX-02 | NOT TESTED | 8 |
| UX-03 | NOT TESTED | 8 |
| UX-06 | NOT TESTED | 8 |
| UX-09 | NOT TESTED | 8 |
| MNT-02 | NOT TESTED | 4 |
| MNT-03 | NOT TESTED | — (advisory, not planned) |
| MNT-04 | NOT TESTED | — (advisory, not planned) |
| MNT-09 | NOT TESTED | — (advisory, not planned) |
| MNT-10 | FAIL | 7 |
| OPS-04 | FAIL | 2 |
| OPS-05 | NOT TESTED | 6 |
| OPS-06 | NOT TESTED | 6 |
| SEC-17 | NOT TESTED | 1 |
| SEC-20 | FAIL (restricted) | 1 |
| SEC-21 | NOT TESTED | 1 |
| SEC-23 | FAIL | 1 |
| CMP-06 | NOT TESTED | 1 |
