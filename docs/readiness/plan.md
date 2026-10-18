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

- IDs: SEC-12 (NOT TESTED), SEC-13 (FAIL, restricted), SEC-17 (NOT TESTED), SEC-20 (FAIL,
  restricted, advisory tier), SEC-23 (FAIL, restricted), CMP-06 (NOT TESTED). Evidence: the
  imported provisional security assessment of 2026-10-18 at `1f9d8fb`; SEC-23 against the frozen
  seven-file skill manifest.
- Failure it prevents: publishing a candidate whose security gaps are unknown or unaccepted.
- Change:
  1. Keep the details of SEC-13, SEC-20 and SEC-23 out of tracked files. They belong in the ignored
     release decision packet under `.scratch/` or a private tracker.
  2. Run the secrets scan on the frozen final candidate (SEC-12).
  3. Complete the access review that `SECURITY.md:48-50` defines (collaborators, deploy keys,
     OAuth and GitHub App grants, personal access tokens) and record its date (SEC-17).
     Approving one production deploy does not complete this inventory.
  4. Clear SEC-23 (details in the private release record) through the proposed follow-up in
     `docs/specs/sre-workflows/follow-up.md`, then bind a new independent acceptance to the
     frozen candidate content, or record a named owner waiver.
  5. Verify provider and backup retention against `SECURITY.md:92-108`, or record a dated owner
     statement saying where that proof lives (CMP-06).
  6. Run the security deploy gate on the exact candidate and target.
- Owner type: code (SEC-12, SEC-13, SEC-23); people or process (SEC-17, SEC-20, CMP-06).
- Size: change.
- Dependencies: the final candidate is frozen and pushed (entry 4).
- Acceptance: a security gate record for the exact commit and production target with no open
  `block`, or each remaining block waived there by a named owner with an expiry.
- Rollout and recovery: evidence only; nothing deploys. A gate that blocks leaves the current
  production site untouched.
- Mechanical gate: the release refuses to start without that security gate record (the
  repository's existing pre-deploy rule, `SECURITY.md:44-47`).

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

- IDs: DEL-03 (NOT TESTED); advisory MNT-02 (NOT TESTED). Evidence: CI runs on push, pull request
  and dispatch (`.github/workflows/ci.yml:8-12`). The Pages workflow publishes on any push to
  `main` that touches `site/**` and does not wait for CI (`.github/workflows/static.yml:8-13`).
- Failure it prevents: a commit that fails the repository's gates reaching the public site.
- Change:
  1. Freeze the final candidate, push its branch and wait for CI on that exact SHA.
  2. Read the `main` ruleset through the API and record whether it requires review and the CI
     checks before merge (MNT-02).
  3. If it does not, propose one of two options: required status checks on `main`, or a
     workflow change that publishes only after CI succeeds for the same SHA. Either is a
     separate, approved change; neither is in this diff.
  4. After the authorized merge, record the CI run for the published commit in the release
     evidence.
- Owner type: code, and infrastructure or provider for repository settings.
- Size: change.
- Dependencies: none; entries 1 and 5 depend on this one.
- Acceptance: before the deploy, a green CI run for the exact candidate SHA; after it, release
  evidence linking the deployed commit to that run.
- Rollout and recovery: a ruleset change is reverted in repository settings; a workflow change
  is reverted by commit.
- Mechanical gate: a required status check, or a `workflow_run` condition on CI success.

## 5. Exercised rollback

- ID: DEL-04 (FAIL). Evidence: no record of an exercised rollback was found; the only documented path is
  "revert the redesign commit and regenerate the site" (`docs/specs/skills-site/spec.md:88-92`).
  This is not a first deploy, so a disable path does not meet the control.
- Failure it prevents: a bad publication with no tested way back.
- Change, a proposal that has **not been exercised and is not authorized**:
  1. Re-run the last successful production deploy of the previous site:
     `gh run rerun 38949299991 --repo mneves75/skills`.
  2. Watch it to completion: `gh run watch <run-id> --repo mneves75/skills --exit-status`.
  3. Compare each served file under `https://mneves75.github.io/skills/` with
     `git show 53ea5adaf420fa03e17559d0c31cbbfb0a89eb76:site/<path>`, allowing for CDN caching
     before concluding.
  4. Roll forward by dispatching the Pages workflow on the current `main`, then compare the
     served files with that commit's `site/` in the same way.
  5. Write the exercised command, both comparisons and the roll-forward into the release
     evidence and `site/README.md`, so each release can print its rollback command.
- What the re-run does: a re-run keeps the original run's `GITHUB_SHA` and `GITHUB_REF`. The
  pinned checkout defaults to the event's SHA. The workflow uploads the tracked `site/`
  directory directly (`.github/workflows/static.yml:31-35`). The re-run therefore checks out and
  re-uploads the old source; it does not necessarily reuse a retained artifact.
- Time limit: GitHub allows a re-run only for a limited period after the original run;
  approximately until 2026-11-15T18:41:45Z for this run.
- A past successful production run is not evidence of readiness.
- Owner type: infrastructure or provider.
- Size: change.
- Dependencies: entry 1 (security gate) and entry 4 (gates pass) must both clear first. The
  owner must also approve the exact action and target, because the exercise changes the public
  site twice.
- Acceptance: release evidence, plus the owner-attested exercise above, showing the served bytes
  matched the old commit and then the current one.
- Rollout and recovery: step 4 is the recovery. If it fails, a fresh push to `main` touching
  `site/**` republishes the current tree.
- Mechanical gate: the release evidence includes the exact rollback command for the published
  version.
- Sources:
  - [Re-running workflows and jobs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs)
  - [actions/checkout README at the pinned commit](https://github.com/actions/checkout/blob/11d5960a326750d5838078e36cf38b85af677262/README.md)
  - [Run 38949299991](https://github.com/mneves75/skills/actions/runs/38949299991)

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

## Index

| Open ID | Status | Entry |
|---|---|---|
| BR-04 | NOT TESTED | 6 |
| DEL-02 | NOT TESTED | 9 |
| DEL-03 | NOT TESTED | 4 |
| DEL-04 | FAIL | 5 |
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
| SEC-12 | NOT TESTED | 1 |
| SEC-13 | FAIL (restricted) | 1 |
| SEC-17 | NOT TESTED | 1 |
| SEC-20 | FAIL (restricted) | 1 |
| SEC-23 | FAIL | 1 |
| CMP-06 | NOT TESTED | 1 |
