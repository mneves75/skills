# Production readiness ledger

> Historical note (2026-10-18): this provisional baseline predates the retirement of the two SRE
> candidate skills into `docs/sre-guides/`; it was not re-run on the guides-only candidate.

Schema: 1 · Catalog: 2 · Unit: . · Stage: live · Visibility: public
Deploy artifact: `site/`, published to GitHub Pages by `.github/workflows/static.yml` after CI succeeds for a push to `main`, only for the `main` tip; a manual dispatch republishes an earlier commit on `main` (rollback)
Profile: ui (static HTML/CSS and minimal JavaScript, `PRODUCT.md:28`); stake: none (no `db`, `accounts`, `uploads`, `marketing-email`, `payments` or `sla`, `SECURITY.md:94`, `SECURITY.md:117-118`)
Regulated: none established. No regulated consumer-service activity is established for these scoped static developer docs; the UX-07 contract gate is inactive, and this is not a legal exemption claim.
Contracts: none
Cursors: production b95604c (2026-10-18)
Baseline: 2026-10-18 at 1f9d8fbc8b1229efb4e465f23665e42314433627 (source snapshot) · maximum age 90 days
Binding run for production: 2026-10-18 at b95604cb94e90f25abab4d44b68ec533bc0fb314 · verdict ready · 0 open blockers · record `.scratch/readiness/production.json` (valid to 2026-10-19T22:12:00Z; expired)
Owners: proposed roles only, none accepted · review proposed: maintainer · data proposed: maintainer · delivery and cost proposed: maintainer · on-call proposed: maintainer, backup unassigned · security patching proposed: maintainer · compliance proposed: maintainer · testing proposed: maintainer · scope proposed: maintainer · architecture proposed: maintainer · memory proposed: maintainer

The provisional baseline was followed by a binding production run on 2026-10-18 at
`b95604c` (tree `5471032…`), the commit deployed as v1.38.0. That run reassessed the always-on
set and the delta, imported the exact-candidate security rows, and folded in a fresh-context
independent check of every blocker row claiming PASS or NOT APPLICABLE. The check found MNT-05
and ASY-02 standing on evidence that does not hold at unit `.`; both are WAIVED, not PASS,
with the fix owed before 2026-10-25. Eleven rows carry owner waivers: SEC-13, SEC-17, SEC-20,
SEC-23, CMP-06, DEL-03, DEL-04, DEL-09, OPS-04, MNT-05 and ASY-02. Underlying FAIL and NOT
TESTED results stay visible, and an expired waiver restores each block. Readiness is a
precondition, not release authority: the deploy of that exact commit and target was approved
separately, and its live proof (served bytes matching the gated tree, links, headers profile)
was checked before the tag. A green source gate (CI) is not readiness.

Evidence is source scope, read 2026-10-18 at `1f9d8fb`, unless a row says otherwise; file and
line citations refer to that snapshot. The result closeout later edited cited files
(`CHANGELOG.md`, `site/README.md`); the final binding record assesses those deltas.
"UI run 2026-10-18" means one independent, source-blind run against a local preview of `site/` (local scope): Chrome at 1440x1000, 768x1024 and 320x800,
light and dark, keyboard, mocked Clipboard API, axe 4.12.1. It counts for the final candidate
only after its preview is confirmed to be the same `site/` bytes. Security and compliance rows
import the provisional security assessment of 2026-10-18 at `1f9d8fb`, except SEC-23, which is
assessed against the frozen seven-file skill manifest; the assessment's scope includes the
local-distribution trust boundaries (skills, scripts and tools users run) as well as the hosted
artifact. Restricted details stay out of this public file.

Provisional assessment for 1.41.0, 2026-10-26 (catalog 2, source scope unless a row says
otherwise). The eleven owner waivers of 2026-10-18 expired on 2026-10-25T23:59:59Z, so each row
shows its underlying status again. DEL-03 and MNT-05 now pass on this release's changes; DEL-04,
DEL-09, ASY-02 and OPS-04 remain open. The completed source audit and independent acceptance
at `bb3080a` pass SEC-12 and SEC-13 and leave SEC-17, SEC-20, SEC-21, SEC-23 and CMP-06 open.
These five security controls and four readiness controls form nine distinct blockers; SEC-20
and SEC-21 are advisory in this catalog profile but block production through the security gate.
No waiver is granted. These are source-candidate results, not a binding gate for a later tree;
the final production gate updates the cursor and gate history only when it actually runs.

Totals: 135 rows · NOT APPLICABLE 84 · PASS 13 · FAIL 4 · NOT TESTED 34 · BLOCKED 0 · WAIVED 0.

| ID | Status | Tier | Evidence (scope, date, commit) | Owner | Next action or waiver |
|---|---|---|---|---|---|
| DM-01 | NOT APPLICABLE | blocker | No database: static files only (`PRODUCT.md:28`); "this project runs no server and keeps no copy" (`SECURITY.md:94`) | proposed: maintainer | Reassess if a database is added |
| DM-02 | NOT APPLICABLE | blocker | No database or migrations (`PRODUCT.md:28`, `SECURITY.md:94`) | proposed: maintainer | Reassess if a database is added |
| DM-03 | NOT APPLICABLE | blocker | No database or migrations (`PRODUCT.md:28`, `SECURITY.md:94`) | proposed: maintainer | Reassess if a database is added |
| DM-04 | NOT APPLICABLE | blocker | No database queries (`PRODUCT.md:28`, `SECURITY.md:94`) | proposed: maintainer | Reassess if a database is added |
| DM-05 | NOT APPLICABLE | blocker | No database client (`PRODUCT.md:28`, `SECURITY.md:94`) | proposed: maintainer | Reassess if a database is added |
| DM-06 | NOT APPLICABLE | advisory | No stored records users delete (`SECURITY.md:117-118`) | proposed: maintainer | Reassess if a database is added |
| DM-07 | NOT APPLICABLE | advisory | No data model (`PRODUCT.md:28`, `SECURITY.md:94`) | proposed: maintainer | Reassess if a database is added |
| BR-01 | NOT APPLICABLE | blocker | No persistent state: the artifact is rebuilt from tracked source (`site/README.md:7`) and uploaded from the checkout (`.github/workflows/static.yml:33-35`) | proposed: maintainer | Reassess if state is added |
| BR-02 | NOT APPLICABLE | blocker | No database or state the product cannot regenerate (`site/README.md:7`, `.github/workflows/static.yml:33-35`) | proposed: maintainer | Reassess if state is added |
| BR-03 | NOT APPLICABLE | blocker | No database with user writes (`SECURITY.md:117-118`) | proposed: maintainer | Reassess if a database is added |
| BR-04 | NOT TESTED | advisory | No stake (header), so advisory. No disaster recovery plan for loss of the hosting account, the repository or the sole maintainer was found or attested | proposed: maintainer | Plan entry 6 |
| BR-05 | NOT APPLICABLE | contract | Contracts: none (header) | proposed: maintainer | — |
| DC-01 | NOT APPLICABLE | blocker | No accounts, forms or user input (`SECURITY.md:117-118`) | proposed: maintainer | — |
| DC-02 | NOT APPLICABLE | blocker | No scheduling, reminders or time-based billing (`PRODUCT.md:28`) | proposed: maintainer | — |
| DC-03 | NOT APPLICABLE | blocker | No payments or stored money (`SECURITY.md:117-118`) | proposed: maintainer | — |
| DC-04 | NOT APPLICABLE | blocker | No currencies, tax or proration (`SECURITY.md:117-118`) | proposed: maintainer | — |
| DC-05 | NOT APPLICABLE | blocker | No payments or external side effects: the only script writes the clipboard (`site/copy-command.js:11-14`) | proposed: maintainer | — |
| DC-06 | NOT APPLICABLE | advisory | No forms or create endpoints (`SECURITY.md:117-118`) | proposed: maintainer | — |
| DC-07 | NOT APPLICABLE | advisory | No lists over growing tables (`PRODUCT.md:28`) | proposed: maintainer | — |
| DC-08 | NOT APPLICABLE | advisory | No accounts (`SECURITY.md:117-118`) | proposed: maintainer | — |
| DC-09 | NOT APPLICABLE | advisory | No import features (`PRODUCT.md:28`) | proposed: maintainer | — |
| DC-10 | NOT APPLICABLE | contract | Contracts: none (header); the site collects nothing (`SECURITY.md:107-108`) | proposed: maintainer | — |
| DEL-01 | NOT APPLICABLE | advisory | No staging environment: one production target, `github-pages`, from `main` (`.github/workflows/static.yml:8-13`, `.github/workflows/static.yml:26-27`) | proposed: maintainer | Reassess if staging is added |
| DEL-02 | NOT TESTED | advisory | The deploy is code (`.github/workflows/static.yml:1-37`); the Pages settings (workflow source, HTTPS enforcement) live in repository settings outside the repository, and drift is not checked | proposed: maintainer | Plan entry 9 |
| DEL-03 | PASS | blocker | source + local, 2026-10-26: `.github/workflows/static.yml` accepts automatic publication only after a successful CI push run and only for the current `main` tip. Manual publication requires main ancestry and the latest CI push run for the exact selected commit on `main` to have succeeded. `python3 tools/scripts/check-pages.test.py` executes the workflow's guard with real Git commits: tip and successful rollback allowed; stale automatic commit, unmerged dispatch, failed/cancelled/missing/unfinished CI evidence and API errors rejected. The dispatch cases failed before the fix. Production execution remains untested | proposed: maintainer | — |
| DEL-04 | NOT TESTED | blocker | source, 2026-10-26: one documented command returns to an earlier version, `gh workflow run static.yml -f ref=<tag>` (`.github/workflows/static.yml:2,14-18`), and the guard lets a dispatch publish only a commit already on `main` (`static.yml:47-48`, controls under DEL-03). It has never been exercised; the exercise republishes the public site twice, so it needs the owner's approval · the 2026-10-18 owner waiver expired 2026-10-25T23:59:59Z | @mneves75 | Plan entry 5 |
| DEL-05 | NOT TESTED | advisory | No stake (header), so advisory. Pages deployment behaviour during rollout was not observed | proposed: maintainer | — (advisory, no entry) |
| DEL-06 | NOT APPLICABLE | advisory | No flag configuration; the artifact is static files (`.github/workflows/static.yml:33-35`) | proposed: maintainer | — |
| DEL-07 | NOT TESTED | advisory | No `sla` contract, so advisory. Capacity is the hosting provider's; no headroom figure was read | proposed: maintainer | — (advisory, no entry) |
| DEL-08 | NOT TESTED | advisory | Applies (`ui`). Production cache headers and asset fingerprinting were not read | proposed: maintainer | Plan entry 9 |
| DEL-09 | NOT TESTED | blocker | production, 2026-10-18: TLS 1.3 certificate for `mneves75.github.io` valid to 2026-12-29; Pages API `https_enforced` true, `cname` null. Current validity only; no certificate-expiry alert and no owner statement about the provider-managed domain · the 2026-10-18 owner waiver expired 2026-10-25T23:59:59Z | @mneves75 | Plan entry 3 |
| ASY-01 | NOT APPLICABLE | advisory | No request handlers or background work (`PRODUCT.md:28`, `SECURITY.md:94`) | proposed: maintainer | — |
| ASY-02 | NOT TESTED | blocker | source + local, 2026-10-26: first-party outbound calls have timeouts and no retries (`skills/autoreview/scripts/install-cccc.py:40` 60 s; `skills/mneves-ship-deploy/assets/verify-live.sh:101,130,135` and `release.sh:241` `--max-time 20`); autoreview's one repeat switches to a different model after a model-access failure, not a transient retry. Provider calls run inside the vendor engine CLIs, whose transport timeouts and retries are outside the repository (`skills/autoreview/README.md:49-53`), and the reviewer-process deadline `--engine-timeout-seconds` is off by default (`test_reviewer_runtime_deadline_is_disabled_by_default`) · the 2026-10-18 owner waiver expired 2026-10-25T23:59:59Z | @mneves75 | Plan entry 10 |
| ASY-03 | NOT APPLICABLE | blocker | No jobs or queues (`SECURITY.md:94`) | proposed: maintainer | — |
| ASY-04 | NOT APPLICABLE | blocker | No scheduled jobs in the product (`.github/workflows/static.yml:8-13`) | proposed: maintainer | — |
| ASY-05 | NOT APPLICABLE | advisory | No application cache (`PRODUCT.md:28`) | proposed: maintainer | — |
| ASY-06 | NOT APPLICABLE | blocker | No webhooks (`SECURITY.md:117-118`) | proposed: maintainer | — |
| ASY-07 | NOT APPLICABLE | blocker | No public API or outbound webhooks (`PRODUCT.md:28`) | proposed: maintainer | — |
| ASY-08 | NOT APPLICABLE | advisory | No external API calls (`SECURITY.md:71`) | proposed: maintainer | — |
| ASY-09 | NOT APPLICABLE | blocker | No OAuth integration (`SECURITY.md:117-118`) | proposed: maintainer | — |
| EML-01 | NOT APPLICABLE | blocker | No email is sent (`SECURITY.md:117-118`) | proposed: maintainer | — |
| EML-02 | NOT APPLICABLE | blocker | No email is sent (`SECURITY.md:117-118`) | proposed: maintainer | — |
| EML-03 | NOT APPLICABLE | advisory | No email templates (`SECURITY.md:117-118`) | proposed: maintainer | — |
| EML-04 | NOT APPLICABLE | advisory | No notifications or marketing email (`SECURITY.md:117-118`) | proposed: maintainer | — |
| CST-01 | NOT TESTED | advisory | Pages artifact and workflow-log retention settings were not read | proposed: maintainer | — (advisory, no entry) |
| CST-02 | NOT TESTED | advisory | No stake (header), so advisory. No paid provider is named in the repository; no owner statement on spend alerts | proposed: maintainer | — (advisory, no entry) |
| OBS-01 | NOT APPLICABLE | advisory | No runtime that writes logs; the artifact is static files (`PRODUCT.md:28`) | proposed: maintainer | — |
| OBS-02 | NOT TESTED | advisory | No stake (header), so advisory. No client error tracker; the site loads no third-party resources (`SECURITY.md:71`) | proposed: maintainer | — (advisory, no entry) |
| OBS-03 | NOT TESTED | advisory | No stake (header), so advisory. No external uptime check was found or attested | proposed: maintainer | Plan entry 3 |
| OBS-04 | NOT TESTED | advisory | No stake (header), so advisory. No alert list attested | proposed: maintainer | Plan entry 3 |
| OBS-05 | NOT TESTED | advisory | No dashboard attested | proposed: maintainer | — (advisory, no entry) |
| OBS-06 | NOT APPLICABLE | advisory | Single static service, not `multi-service` (`PRODUCT.md:28`) | proposed: maintainer | — |
| OBS-07 | NOT TESTED | advisory | No stake (header), so advisory. One maintainer (`SECURITY.md:37-38`); no rotation attested | proposed: maintainer | Plan entry 6 |
| OBS-08 | NOT APPLICABLE | advisory | No paging alerts exist to link runbooks from (OBS-04 row) | proposed: maintainer | Reassess when alerts are added |
| OBS-09 | NOT TESTED | advisory | No owner statement that incidents on this site get written reviews | proposed: maintainer | — (advisory, no entry) |
| OBS-10 | NOT TESTED | advisory | No `sla` contract, so advisory. No status page found | proposed: maintainer | — (advisory, no entry) |
| TST-01 | NOT APPLICABLE | advisory | No business rules: the only script copies a command to the clipboard (`site/copy-command.js:11-19`) | proposed: maintainer | — |
| TST-02 | NOT APPLICABLE | advisory | No external API dependency (`SECURITY.md:71`) | proposed: maintainer | — |
| TST-03 | NOT APPLICABLE | blocker | No accounts or payments (`SECURITY.md:117-118`) | proposed: maintainer | — |
| TST-04 | NOT TESTED | advisory | No stake (header), so advisory. No load test ran; none is claimed | proposed: maintainer | — (advisory, no entry) |
| TST-05 | NOT APPLICABLE | blocker | No lower environment exists: one target, `github-pages` (`.github/workflows/static.yml:26-27`), and no data or credentials to isolate (`SECURITY.md:107-108`). Always-on: reassess every run | proposed: maintainer | Reassess if staging is added |
| TST-06 | NOT TESTED | advisory | The suite runs on every change (`.github/workflows/ci.yml:8-12`), and one recorded fix had a failing control first (`docs/specs/skills-site/spec.md:96-99`); a sample of recent fixes was not reviewed. The UI run 2026-10-18 does not cover this row | proposed: maintainer | — (advisory, no entry) |
| TST-07 | NOT TESTED | advisory | Applies (`ui`). No support matrix and no throttled low-end run; none is claimed | proposed: maintainer | — (advisory, no entry) |
| BIL-01 | NOT APPLICABLE | blocker | No subscriptions (`SECURITY.md:117-118`) | proposed: maintainer | — |
| BIL-02 | NOT APPLICABLE | blocker | No subscriptions (`SECURITY.md:117-118`) | proposed: maintainer | — |
| BIL-03 | NOT APPLICABLE | contract | Contracts: none (header) | proposed: maintainer | — |
| BIL-04 | NOT APPLICABLE | blocker | No payments (`SECURITY.md:117-118`) | proposed: maintainer | — |
| BIL-05 | NOT APPLICABLE | blocker | No payments (`SECURITY.md:117-118`) | proposed: maintainer | — |
| BIL-06 | NOT APPLICABLE | blocker | No metered usage (`SECURITY.md:117-118`) | proposed: maintainer | — |
| BIL-07 | NOT APPLICABLE | advisory | No contracts or billing (header, `SECURITY.md:117-118`) | proposed: maintainer | — |
| BIL-08 | NOT APPLICABLE | advisory | No payments (`SECURITY.md:117-118`) | proposed: maintainer | — |
| API-01 | NOT APPLICABLE | blocker | No public API (`PRODUCT.md:28`) | proposed: maintainer | — |
| API-02 | NOT APPLICABLE | blocker | No public API (`PRODUCT.md:28`) | proposed: maintainer | — |
| API-03 | NOT APPLICABLE | blocker | No public API (`PRODUCT.md:28`) | proposed: maintainer | — |
| API-04 | NOT APPLICABLE | advisory | No public API (`PRODUCT.md:28`) | proposed: maintainer | — |
| AI-01 | NOT APPLICABLE | advisory | The hosted artifact makes no model call (`site/copy-command.js:1-24` is its only script, loaded at `site/index.html:85`); AI-facing distribution risk is in SEC-23 | proposed: maintainer | — |
| AI-02 | NOT APPLICABLE | advisory | No model call in the hosted artifact (as AI-01) | proposed: maintainer | — |
| AI-03 | NOT APPLICABLE | advisory | No model configuration in the hosted artifact (as AI-01) | proposed: maintainer | — |
| UX-01 | NOT TESTED | advisory | Applies (`ui`). No throttled-network run; none is claimed | proposed: maintainer | — (advisory, no entry) |
| UX-02 | NOT TESTED | advisory | local, UI run 2026-10-18: the copy control showed the manual-copy fallback when the clipboard was missing or rejected the write, and no false success; the pages load no data, so only this error state exists. Pending: preview identity equals the final candidate | proposed: maintainer | Plan entry 8 |
| UX-03 | NOT TESTED | advisory | local, UI run 2026-10-18: the fallback says what happened and what to do (`site/copy-command.js:18`). It shows no reference support could trace. Pending: preview identity | proposed: maintainer | Plan entry 8 |
| UX-04 | NOT APPLICABLE | advisory | No forms (`SECURITY.md:117-118`) | proposed: maintainer | — |
| UX-05 | NOT APPLICABLE | advisory | No destructive actions (`SECURITY.md:117-118`) | proposed: maintainer | — |
| UX-06 | NOT TESTED | advisory | local, UI run 2026-10-18: Tab/Enter reached and activated both new guides with a 3px focus outline; ArrowRight scrolled narrow examples; axe found 0 violations and 0 incomplete on desktop catalog and guide; on the narrow dark guide, 0 violations and one contrast rule incomplete on 19 cells scrolled horizontally offscreen. No manual screen-reader pass ran, so the row cannot PASS | proposed: maintainer | Plan entry 8 |
| UX-07 | NOT APPLICABLE | contract | Contracts: none; no regulated consumer-service activity established (header). Not a legal exemption claim | proposed: maintainer | Reassess if the site starts serving consumers in a market with accessibility law |
| UX-08 | NOT APPLICABLE | advisory | English-only copy by decision (`PRODUCT.md:30`); no `i18n` | proposed: maintainer | — |
| UX-09 | NOT TESTED | advisory | local, UI run 2026-10-18: guide links landed on the matching heading. Back, reload and pasted deep links were not exercised. Pending: preview identity | proposed: maintainer | Plan entry 8 |
| MNT-01 | PASS | advisory | The artifact's only application code is `site/copy-command.js` (24 lines, named handlers); CI syntax-checks it (`.github/workflows/ci.yml:72-73`) and type-checks and lints `tools/` (`.github/workflows/ci.yml:111-117`) | proposed: maintainer | — |
| MNT-02 | NOT TESTED | advisory | No stake (header), so advisory. A ruleset blocks force-push and deletion on `main` (`SECURITY.md:39-40`); required review and required checks were not read through the API | proposed: maintainer | Plan entry 4 |
| MNT-03 | NOT TESTED | advisory | Contributions go through pull requests (`CONTRIBUTING.md:38`); a written statement of how releases are cut was not located in this read | proposed: maintainer | — (advisory, no entry) |
| MNT-04 | NOT TESTED | advisory | An update bot is configured (`.github/dependabot.yml`); recent update history was not read | proposed: maintainer | — (advisory, no entry) |
| MNT-05 | PASS | blocker | source + vendor dates, 2026-10-26: `SECURITY.md:7-18` names the supported runtimes, their end-of-life owner (@mneves75) and a 7-day patch deadline for critical advisories. Bun 1.4.4 is the latest release (oven-sh/bun releases, 2026-10-22) and CI pins it; Python 3.11 receives security fixes to 2027-10 (devguide.python.org/versions, read 2026-10-26); the 3.10 floor, end of life 2026-10-01, was raised to 3.11 in this release; Node.js is stated as an upstream-maintained line | @mneves75 | — |
| MNT-06 | PASS | advisory | One script in the artifact, used by the landing page (`site/index.html:85`); no unused routes, flags or dependencies in `site/` | proposed: maintainer | — |
| MNT-07 | PASS | advisory | The largest application file in the artifact is `site/copy-command.js` at 24 lines | proposed: maintainer | — |
| MNT-08 | PASS | advisory | Site decisions recorded with alternatives (`docs/specs/skills-site/spec.md:23-41`), the chosen direction (`docs/specs/skills-site/spec.md:75-86`) and rollback risk (`docs/specs/skills-site/spec.md:88-92`) | proposed: maintainer | — |
| MNT-09 | NOT TESTED | advisory | No timed run from a clean checkout | proposed: maintainer | — (advisory, no entry) |
| MNT-10 | FAIL | advisory | The publish and rollback commands are written (`.github/workflows/static.yml:1-2`, `site/README.md:3-4`, `SECURITY.md`), but no rollback or recovery owner is (DEL-04, OPS-04) | proposed: maintainer | Plan entry 7 |
| OPS-01 | NOT APPLICABLE | advisory | No accounts (`SECURITY.md:117-118`) | proposed: maintainer | — |
| OPS-02 | NOT APPLICABLE | advisory | No accounts (`SECURITY.md:117-118`) | proposed: maintainer | — |
| OPS-03 | PASS | advisory | Dated public changelog (`CHANGELOG.md:10`), rendered on the landing page by the generator (`site/README.md:8`) and kept current by a CI check (`.github/workflows/ci.yml:105-109`) | proposed: maintainer | — |
| OPS-04 | FAIL | blocker | One maintainer administers the repository (`SECURITY.md`); no owner statement on recovery codes or a second administrator · the 2026-10-18 owner waiver expired 2026-10-25T23:59:59Z | @mneves75 | Plan entry 2 |
| OPS-05 | NOT TESTED | advisory | No stake (header), so advisory. Solo operator (`SECURITY.md:37-38`); no waiver and no second person attested | proposed: maintainer | Plan entry 6 |
| OPS-06 | NOT TESTED | advisory | No stake (header), so advisory. Seats are proposed in the header, none accepted; on-call backup unassigned | proposed: maintainer | Plan entry 6 |
| SEC-01 | NOT APPLICABLE | blocker | Imported: no accounts (`SECURITY.md:117-118`) | proposed: maintainer | — |
| SEC-02 | NOT APPLICABLE | blocker | Imported: no product accounts (`SECURITY.md:117-118`); maintainer account controls are covered by SEC-17 and SEC-21 | proposed: maintainer | — |
| SEC-03 | NOT APPLICABLE | blocker | Imported: no sessions (`SECURITY.md:117-118`) | proposed: maintainer | — |
| SEC-04 | NOT APPLICABLE | contract | Imported: contracts none; no accounts | proposed: maintainer | — |
| SEC-05 | NOT APPLICABLE | contract | Imported: contracts none; no accounts | proposed: maintainer | — |
| SEC-06 | NOT APPLICABLE | blocker | Imported: no tenants or roles in the product (`SECURITY.md:117-118`) | proposed: maintainer | — |
| SEC-07 | NOT APPLICABLE | blocker | Imported: no accounts or object ids (`SECURITY.md:117-118`) | proposed: maintainer | — |
| SEC-08 | NOT APPLICABLE | blocker | Imported: not multi-tenant | proposed: maintainer | — |
| SEC-09 | NOT APPLICABLE | advisory | Imported: no impersonation | proposed: maintainer | — |
| SEC-10 | NOT APPLICABLE | blocker | Imported: no login | proposed: maintainer | — |
| SEC-11 | PASS | blocker | Imported, source + local, 2026-10-18, `1f9d8fb`: the local-distribution validation boundary and its regression tests | proposed: maintainer | — |
| SEC-12 | PASS | blocker | Imported, source + local, 2026-10-26 at `bb3080a`: Gitleaks 8.30.1 scanned the candidate tree and history with clean and planted-credential controls. Detected fixtures and their dispositions are reconciled in the private, independently accepted security record. Always-on; reassess the final release tree. | imported | Plan entry 1 |
| SEC-13 | PASS | blocker | Imported, source + local + registry, 2026-10-26 at `bb3080a`: the completed audit and independent acceptance verify locked tool identities and integrity, hashed Python installs, and current advisory scans. ast-grep and marked are exact devDependencies; the reference `skills-ref` validator and render dependencies use `--require-hashes`. CI fails on any locked-tool advisory. Reassess the final release tree. | @mneves75 | Plan entry 1 |
| SEC-14 | NOT APPLICABLE | blocker | Imported: no uploads | proposed: maintainer | — |
| SEC-15 | PASS | blocker | Imported, source + production, 2026-10-18: passes for the public static risk profile, with the documented deviations kept visible: no HSTS, `X-Content-Type-Options` or frame-protection headers, which Pages cannot send; CSP and referrer policy in markup; CORS without credentials (`SECURITY.md:110-118`). Not full ASVS compliance and not an owner waiver | proposed: maintainer | — |
| SEC-16 | PASS | blocker | Imported, source + local + production, 2026-10-18: HTTPS enforced (Pages API `https_enforced` true; TLS 1.3 served) and disk encryption on the inspected release device. Scoped to that device; no fleet-wide claim | proposed: maintainer | — |
| SEC-17 | NOT TESTED | blocker | Imported from the completed source-candidate security gate, 2026-10-26 at `bb3080a`. The operator access review defined in `SECURITY.md` has no dated result; prior owner waivers expired 2026-10-25T23:59:59Z. | @mneves75 | Plan entry 1 |
| SEC-18 | PASS | blocker | Imported, source + local, 2026-10-18: redaction, isolation and action-state evidence for the local tools. No assurance about external providers' log redaction | proposed: maintainer | — |
| SEC-19 | NOT APPLICABLE | contract | Imported: contracts none | proposed: maintainer | — |
| SEC-20 | FAIL | advisory | Imported from the completed source-candidate security gate, 2026-10-26 at `bb3080a`. Restricted details remain private. Advisory in this catalog profile; the security gate makes it a production blocker. Prior owner waivers expired 2026-10-25T23:59:59Z. | @mneves75 | Plan entry 1 |
| SEC-21 | NOT TESTED | advisory | Imported from the completed source-candidate security gate, 2026-10-26 at `bb3080a`. The written incident runbook does not establish current encryption and screen-lock state on devices with production access; current owner/device evidence was not established in that audit. This status does not disprove the earlier device inspection. Advisory here; the security gate makes it a production blocker. | @mneves75 | Plan entry 1 |
| SEC-22 | NOT APPLICABLE | blocker | Imported: no inbound webhooks | proposed: maintainer | — |
| SEC-23 | FAIL | blocker | Imported from the completed source-candidate security gate, 2026-10-26 at `bb3080a`. Restricted details remain in the private gate record; prior owner waivers expired 2026-10-25T23:59:59Z. | @mneves75 | Plan entry 1 |
| CMP-01 | NOT APPLICABLE | contract | Imported: contracts none | proposed: maintainer | — |
| CMP-02 | NOT APPLICABLE | contract | Imported: contracts none | proposed: maintainer | — |
| CMP-03 | NOT APPLICABLE | blocker | Imported: no health data | proposed: maintainer | — |
| CMP-04 | NOT APPLICABLE | contract | Imported: no health data; contracts none | proposed: maintainer | — |
| CMP-05 | NOT APPLICABLE | blocker | Imported: no payments | proposed: maintainer | — |
| CMP-06 | NOT TESTED | blocker | Imported from the completed source-candidate security gate, 2026-10-26 at `bb3080a`. Catalog 2 applies to stored personal data, including the tools' local stores. The erasure procedure is written (`SECURITY.md`); provider and backup retention and an erasure run are not verified. Prior owner waivers expired 2026-10-25T23:59:59Z. | @mneves75 | Plan entry 1 |
| CMP-07 | NOT APPLICABLE | contract | Imported: contracts none | proposed: maintainer | — |
| CMP-08 | NOT APPLICABLE | contract | Imported: contracts none | proposed: maintainer | — |
| CMP-09 | NOT APPLICABLE | blocker | Imported: no accounts; the site collects nothing (`SECURITY.md:107-108`) | proposed: maintainer | — |

## Gate history

| Date | Target | Commit | Verdict | Open blockers | Waivers |
|---|---|---|---|---|---|
| 2026-10-18 | production | b95604c | ready | 0 | SEC-13 SEC-17 SEC-20 SEC-23 CMP-06 DEL-03 DEL-04 DEL-09 OPS-04 MNT-05 ASY-02 |
