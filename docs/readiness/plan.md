# Production readiness plan

> Historical note: the original 2026-10-18 plan predates the retirement of the two SRE candidate
> skills into `docs/sre-guides/`. Where it names the seven-file skill manifest or the follow-up,
> it describes the candidate as it was then; it was not re-run on the guides-only candidate.

Source: [ledger.md](ledger.md), final 1.46.1 binding assessment at
`44464be872a083c7022f22b0de9d4079fab6b2b8`, reused by production merge `b6630d8fe65c9f2f18b0eafe54574e1573a09650`;
its dispositions equal those of the 1.46.0 assessment at `24f387652c70c3507af5fc310d3eae5cd9c49896`.
The current ledger covers the whole unit, including local SQLite and AI tools. Its 26 historical
waivers leave the underlying gaps open. Sixteen were candidate-only approvals for 1.46.0 and,
conditionally, 1.46.1, and have expired; the ledger records each owner, expiry and scope. The final binding assessment, rather
than its earlier not-ready baseline draft, owns the dispositions and effective tiers used here.

Every entry is proposed work: this document authorizes no implementation or external change,
and proposed maintainer roles are not accepted assignments. Each later candidate needs its own
security/readiness gate and independent acceptance. Binding results stay in private records and
the annotated release tag, so documenting this previous run does not predict the next verdict.

Entries retain their existing numbers. Data/recovery follow-up is in entry 11; unresolved
whole-unit operating scope/evidence is in entry 12. These determinations precede operating
changes that depend on them. No contract row is active. The index includes all currently open
underlying gaps and distinguishes advisory work from effective blockers.

## 1. Security and compliance rows from the security gate

- Historical 1.46.0 final security import: SEC-11/12/13/16/18 PASS; SEC-15/17/20/21/23
  and CMP-06 WAIVED, with underlying FAIL or NOT TESTED as recorded in the ledger. The
  effective security tiers remain blockers. Private canonical security and readiness records
  preserve the exact verdict, audit origin and independent acceptance; restricted details
  are not reproduced here. These six existing waivers expire 2027-01-25T23:59:59Z and every
  later candidate still needs its own gate.
- Failure it prevents: publishing a candidate whose security gaps are unknown or unaccepted.
- Change:
  1. Keep restricted details out of tracked files. They belong in the ignored
     release decision packet under `.scratch/` or a private tracker.
  2. Run the secrets scan on the frozen final candidate (SEC-12).
  3. Complete the access review that `SECURITY.md:48-50` defines (collaborators, deploy keys,
     OAuth and GitHub App grants, personal access tokens) and record its date (SEC-17).
     Approving one production deploy does not complete this inventory.
  4. Resolve SEC-15, SEC-20, SEC-21 and SEC-23 using the evidence/actions in the private release
     decision packet, or record explicit named owner waivers with a reason and expiry.
  5. Verify provider and backup retention against `SECURITY.md:92-108`, or record a dated owner
     statement saying where that proof lives (CMP-06).
  6. Run the security deploy gate on the exact candidate and target.
- Owner type: code/scanner evidence (SEC-12, SEC-13); people or process for the six waived IDs.
- Size: change.
- Dependencies: the final candidate is frozen and pushed (entry 4).
- Acceptance: a security gate record for the exact commit and production target with no open
  `block`, or each remaining block waived there by a named owner with an expiry.
- Rollout and recovery: evidence only; nothing deploys. A gate that blocks leaves the current
  production site untouched.
- Mechanical gate: Pages enforces CI success and source ancestry through `static.yml`, except
  for an owner's CI waiver dispatch, which publishes only the exact `main` tip equal to the
  resolved approval variable; the publisher's operator gate proves before dispatch that the
  value comes from the `github-pages` environment alone (from 1.45.2). This repository's
  security/readiness records are operating requirements before merging; that workflow does not
  itself enforce them. The merger must check the exact-candidate
  verdicts before publishing.

## 2. Second administrator and account recovery

- ID: OPS-04 (historical WAIVED, underlying FAIL). Evidence: "One maintainer administers the repository"
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

- IDs: DEL-09 (historical WAIVED, underlying NOT TESTED); OBS-03 and OBS-04 (historical
  WAIVED, underlying BLOCKED; effective blockers pending the entry 12 determination). Earlier production evidence,
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
  `main`, and only the `main` tip (ledger row DEL-03). The full-unit 1.46.0 binding
  treats MNT-02 as an effective blocker: historical WAIVED, underlying BLOCKED. Determine its
  operating scope under entry 12, then read the default-branch rules through the host API or
  obtain a dated owner attestation proving independent review, required checks and blocked direct pushes.
- 2026-11-04, 1.45.2 (bound 2026-11-04T12:48:13Z at `7587b764` by that session; folded into the ledger in 1.45.3): an owner's CI waiver dispatch may publish the exact
  `main` tip without CI when it equals the resolved `vars.CI_WAIVER_APPROVED_SHA`; any other
  waiver request fails. The workflow cannot prove that value's environment-only provenance, so
  the operator gate in `CONTRIBUTING.md` proves it before dispatch. Proven locally only; the next
  binding run reassesses DEL-03 on the pushed merge commit.

## 5. Exercised rollback

- ID: DEL-04 (historical WAIVED, underlying NOT TESTED). Evidence: the rollback command is documented
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
- 2026-11-04, 1.45.2 (bound 2026-11-04T12:48:13Z at `7587b764` by that session; folded into the ledger in 1.45.3): the rollback route is unchanged, but a release
  published under an owner's CI waiver has no successful CI run, so it cannot be a rollback
  target; roll back to a version whose CI passed.

## 6. People seats and continuity

- IDs: OPS-05, OPS-06, OBS-07 and BR-04 (historical WAIVED, underlying BLOCKED; effective
  blockers). The final full-unit assessment leaves customer-data/stake and operating evidence
  unresolved; the hosted artifact alone cannot make these advisory. The ledger seats remain
  proposed roles. Entry 12 determines the operating boundary before the corresponding proof.
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

- ID: MNT-10 (NOT TESTED, advisory in the final 1.46.0 assessment). Qualifying handover
  evidence remains unverified; existing publication/runbook documentation alone does not
  prove that another operator can recover the whole unit.
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

- IDs: DEL-02 (NOT TESTED), DEL-08 (FAIL), both advisory in the final 1.46.0 assessment. Earlier evidence: the deploy is versioned
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

## 10. Bounded provider calls and retries

- IDs: AI-02 and ASY-02 (historical WAIVED, underlying FAIL; effective blockers).
  The final private assessment distinguishes model-call failure handling from general retry
  policy. AI-02's approval applies only to 1.46.0, even though its expiry is 2027-01-25T23:59:59Z;
  it is not interchangeable with the existing ASY-02 waiver.
- Failure it prevents: an unbounded or stalled external call holding the operator indefinitely,
  and retries amplifying a provider outage.
- Change: agree explicit call/retry bounds for the actual distributed flows, implement those
  bounds and defined failure behavior, and exercise a failing/hanging fake provider. Address
  the missing retry jitter/Retry-After behavior documented under ASY-02 separately. This plan
  chooses no timeout value, spend cap, provider, fallback authority or alert destination.
- Owner type: code, with owner decisions for operating policy. Size: change.
- Dependencies: entry 12's actual operator boundary; no live provider call is authorized here.
- Acceptance: local fake-provider controls prove the applicable AI-02 and ASY-02 checks, bounded
  failure and cleanup; the next exact-candidate assessment independently accepts each ID.
- Rollout and recovery: ship only after ordinary tests/review; revert the scoped change if needed.
- Mechanical gate: existing autoreview and watcher fake-provider suites, extended only with
  behavior checks for the agreed changes. No runtime change is made by this document.

## 11. Local data query and recovery evidence

- IDs: DM-04 (historical WAIVED, underlying FAIL), BR-01/02/03 (historical WAIVED,
  underlying NOT TESTED), plus advisory DC-07 (FAIL). The local SQLite store makes these
  applicable; operator ownership identifies who supplies proof, rather than excluding them.
- Failure it prevents: unbounded data queries and loss of user-created records that cannot be
  regenerated. The waivers were candidate-only for 1.46.0, expiring 2026-11-06T23:59:59Z.
- Change: first determine actual supported data volumes and operator recovery responsibility.
  Capture representative synthetic query plans/limits for DM-04 and DC-07; separately obtain
  qualifying backup configuration, a real-backup isolated restore drill with duration/recovery
  point/data checks and pending-erasure handling, and selected-row/time recovery evidence.
  Do not present SQLite WAL as point-in-time recovery or invent a hosted database service.
- Owner type: code and data/operator. Size: change. Dependencies: entry 12's data boundary.
- Acceptance: DM-04's local/staging query-plan evidence; BR-01/03 production configuration or
  dated owner attestation; BR-02 staging or owner-attested real-backup restore evidence. Each
  must meet its catalog definition and evidence window before a later PASS.
- Rollout and recovery: read-only/synthetic query evidence first; any actual backup/restore
  action needs its exact authorized target and an isolated recovery destination.
- Mechanical gate: retain proof with the relevant private assessment; use the existing SRS tests
  for any later code change. This document neither changes storage nor authorizes a data operation.

## 12. Determine the whole-unit operating boundary and obtain its proof

- IDs: BR-04, DEL-05, CST-02, OBS-02/03/04/07, TST-04, MNT-02 and OPS-05/06 (historical
  WAIVED, underlying BLOCKED; effective blockers). These candidate-only 1.46.0 exceptions
  expire 2026-11-06T23:59:59Z and do not settle their missing determinations.
- Failure it prevents: treating local user data or paid AI tooling as out of scope merely
  because the published Pages artifact is static.
- Change: obtain a dated owner determination of supported installations, customer-data/stake,
  operator responsibilities and actual service commitments. Keep conservative blocker
  treatment until evidence permits a different disposition. For applicable boundaries, obtain
  catalog-level recovery, rollout/health, error/uptime/alert/on-call, representative load,
  reviewed-change protection and named-owner evidence. Budget/cap and spend-alert decisions
  belong to the owner; no values, destination, pager, SLA or hosted architecture are invented.
- Owner type: people/process, repository settings, provider and finance as applicable. Size: change.
- Dependencies: none for the determination; entries 2/3/4/6/11 consume it for their own evidence.
- Acceptance: a supported applicability determination plus each applicable control's minimum
  evidence: dated operating/owner proof, repository settings, qualifying load run or provider
  configuration as its catalog requires. A new named waiver requires an explicit owner decision.
- Rollout and recovery: documentation/read-only checks first; consequential provider and data
  changes stay separately authorized. Private details remain in ignored evidence.
- Mechanical gate: reconcile every ID/status/tier with the next exact-candidate ledger; the
  catalog guard checks structural consistency, not the truth of operating evidence.

## Index

The statuses below are the recorded 1.46.1 dispositions, unchanged from 1.46.0. WAIVED preserves an
underlying gap; candidate-only approval never carries over to another candidate. Expiry/scope is in the ledger.

| Open ID | Recorded status | Effective tier | Entry |
|---|---|---|---|
| DM-04 | WAIVED (underlying FAIL) | blocker | 11 |
| BR-01 | WAIVED (underlying NOT TESTED) | blocker | 11 |
| BR-02 | WAIVED (underlying NOT TESTED) | blocker | 11 |
| BR-03 | WAIVED (underlying NOT TESTED) | blocker | 11 |
| BR-04 | WAIVED (underlying BLOCKED) | blocker | 6 |
| DC-07 | FAIL | advisory | 11 |
| DEL-02 | NOT TESTED | advisory | 9 |
| DEL-04 | WAIVED (underlying NOT TESTED) | blocker | 5 |
| DEL-05 | WAIVED (underlying BLOCKED) | blocker | 12 |
| DEL-07 | NOT TESTED | advisory | — (advisory, not planned) |
| DEL-08 | FAIL | advisory | 9 |
| DEL-09 | WAIVED (underlying NOT TESTED) | blocker | 3 |
| ASY-02 | WAIVED (underlying FAIL) | blocker | 10 |
| ASY-08 | NOT TESTED | advisory | — (advisory, not planned) |
| CST-01 | NOT TESTED | advisory | — (advisory, not planned) |
| CST-02 | WAIVED (underlying BLOCKED) | blocker | 12 |
| OBS-01 | FAIL | advisory | — (advisory, not planned) |
| OBS-02 | WAIVED (underlying BLOCKED) | blocker | 12 |
| OBS-03 | WAIVED (underlying BLOCKED) | blocker | 12 |
| OBS-04 | WAIVED (underlying BLOCKED) | blocker | 12 |
| OBS-05 | NOT TESTED | advisory | — (advisory, not planned) |
| OBS-07 | WAIVED (underlying BLOCKED) | blocker | 6 |
| OBS-08 | NOT TESTED | advisory | — (advisory, not planned) |
| OBS-09 | NOT TESTED | advisory | — (advisory, not planned) |
| OBS-10 | NOT TESTED | advisory | — (advisory, not planned) |
| TST-02 | NOT TESTED | advisory | — (advisory, not planned) |
| TST-04 | WAIVED (underlying BLOCKED) | blocker | 12 |
| TST-07 | NOT TESTED | advisory | — (advisory, not planned) |
| AI-02 | WAIVED (underlying FAIL) | blocker | 10 |
| AI-03 | NOT TESTED | advisory | — (advisory, not planned) |
| UX-01 | NOT TESTED | advisory | — (advisory, not planned) |
| UX-02 | NOT TESTED | advisory | 8 |
| UX-03 | NOT TESTED | advisory | 8 |
| UX-06 | NOT TESTED | advisory | 8 |
| UX-09 | NOT TESTED | advisory | 8 |
| MNT-02 | WAIVED (underlying BLOCKED) | blocker | 4 |
| MNT-04 | NOT TESTED | advisory | — (advisory, not planned) |
| MNT-06 | NOT TESTED | advisory | — (advisory, not planned) |
| MNT-07 | FAIL | advisory | — (advisory, not planned) |
| MNT-09 | NOT TESTED | advisory | — (advisory, not planned) |
| MNT-10 | NOT TESTED | advisory | 7 |
| OPS-04 | WAIVED (underlying FAIL) | blocker | 2 |
| OPS-05 | WAIVED (underlying BLOCKED) | blocker | 6 |
| OPS-06 | WAIVED (underlying BLOCKED) | blocker | 6 |
| SEC-15 | WAIVED (underlying FAIL) | blocker | 1 |
| SEC-17 | WAIVED (underlying NOT TESTED) | blocker | 1 |
| SEC-20 | WAIVED (underlying FAIL) | blocker | 1 |
| SEC-21 | WAIVED (underlying NOT TESTED) | blocker | 1 |
| SEC-23 | WAIVED (underlying NOT TESTED) | blocker | 1 |
| CMP-06 | WAIVED (underlying NOT TESTED) | blocker | 1 |
