# Production readiness ledger

Schema: 1 · Catalog: 3 · Unit: . · Stage: live · Visibility: public
Deploy artifact: `site/`, published to GitHub Pages by `.github/workflows/static.yml` after CI succeeds for a push to `main`, only for the `main` tip; a manual dispatch republishes an earlier commit on `main` whose CI push run succeeded (rollback); an owner's CI waiver dispatch publishes, without CI, only the exact `main` tip equal to the resolved `vars.CI_WAIVER_APPROVED_SHA`, after the publisher's operator gate proves that value comes from the `github-pages` environment alone (from 1.45.2; `CONTRIBUTING.md`, "Skipping GitHub CI for a release")
Profile: hosted ui (static Pages artifact); distributed db, ai, user-input, external-calls and local-persistence; unit flags ui/db/ai. Unit . includes the shipped SQLite SRS and AI tools, not only site/. Stake/customer-data applicability needs owner determination; the final 1.46.0 and 1.46.1 assessments conservatively treated affected controls as blockers. Hosted stake: false is descriptive only and does not downgrade the whole unit.
Regulated: none established; no operator-specific data, market or contract determination is invented. Local privacy copies remain applicable. The UX-07 contract gate is inactive; this is not a legal exemption claim.
Contracts: none
Cursors: production 2ecd2d05504ca832c730e30453fa41cbdcd836ec (2026-11-13 UTC; v1.51.0, original audit `7e1b7d406932e3f35e8f670da8448c0d3d7b85b9`, identical tree `957981a72c85cf60b738a03fb8fbad99f97ee85e`; previous cursor 0c1b638af6ef0a56638c2538f7bfc20196f771e0, v1.50.0)
Baseline: 2026-11-05 at 24f387652c70c3507af5fc310d3eae5cd9c49896 (full-unit source assessment; maximum age 90 days; expires 2027-02-03T23:21:54Z). Final dispositions below come from binding-assessment.json, not the earlier not-ready baseline draft.
Binding run for production: 2026-11-13T18:51:12Z at 2ecd2d05504ca832c730e30453fa41cbdcd836ec (v1.51.0; original audit `7e1b7d406932e3f35e8f670da8448c0d3d7b85b9`, identical tree `957981a72c85cf60b738a03fb8fbad99f97ee85e`) · verdict ready · 0 open blockers · independent acceptance pass · 26 WAIVED · historical record `.scratch/readiness/2ecd2d05504ca832c730e30453fa41cbdcd836ec/production.json`, valid_until 2026-11-14T18:51:12Z. Earlier binding runs remain in Gate history.
Owners: proposed roles only, none accepted · review proposed: maintainer · data proposed: maintainer · delivery and cost proposed: maintainer · on-call proposed: maintainer, backup unassigned · security patching proposed: maintainer · compliance proposed: maintainer · testing proposed: maintainer · scope proposed: maintainer · architecture proposed: maintainer · memory proposed: maintainer

## Recorded 1.51.0 binding result

The table records the full-unit assessment for audit `7e1b7d406932e3f35e8f670da8448c0d3d7b85b9`
(assessed 2026-11-13T18:26:45Z, accepted 18:50:40Z), merged to production as
`2ecd2d05504ca832c730e30453fa41cbdcd836ec` (identical tree `957981a72c85cf60b738a03fb8fbad99f97ee85e`).
Every control kept the status and effective tier of the 1.50.0 assessment (`59d08af`). AI-01 stayed
PASS on a fresh live routing-eval run (204 of 204 samples, on text equal to this candidate's) and a
baseline control on 1.50.0 that met its threshold. The security gate confirmed autoreview Git
collection findings (RSCR-H01 to H04 and H06, the High one a checkout-configured signature
program) and the candidate fixed them before this assessment. Two earlier independent acceptances
of the same commit did not pass: the first was blocked by an advisory endpoint that needs POST, the
second failed on missing Python advisory evidence (AC-03), which the gate then supplied; the third
attempt passed. Per-control evidence lives in `.scratch/readiness/7e1b7d406932e3f35e8f670da8448c0d3d7b85b9/binding-assessment.json`;
the merge record above binds the ready verdict, zero open blockers and independent acceptance.
These records are private. The source baseline is provenance for that assessment, not its final
verdict. Effective tiers, including conservative blocker treatment while stake is unresolved,
are copied from the final assessment.

The 26 waivers preserve their underlying gaps and owner `@mneves75`:
- Ten existing controls (SEC-15, SEC-17, SEC-20, SEC-21, SEC-23, CMP-06, DEL-04, DEL-09,
  ASY-02, OPS-04) expire 2027-01-25T23:59:59Z; any later reuse still needs a fresh exact-candidate gate.
- Sixteen candidate-only controls (AI-02, DM-04, BR-01, BR-02, BR-03, BR-04, DEL-05, CST-02,
  OBS-02, OBS-03, OBS-04, OBS-07, TST-04, MNT-02, OPS-05 and OPS-06) were approved for 1.46.0,
  and again, conditionally on unchanged gaps, for each release from 1.46.1 to 1.51.0
  (`.scratch/security-gate/7e1b7d406932e3f35e8f670da8448c0d3d7b85b9/owner-approval.json`), to
  2026-11-14T23:59:59Z. This bookkeeping renews none of them; a later candidate needs
  its own approval.

The 1.51.1 binding result belongs in its own private exact-candidate records and annotated release
tag; this historical ready verdict does not admit a different tree.

## Earlier assessment context

> Historical note (2026-10-18): that provisional baseline predates the retirement of the two SRE
> candidate skills into `docs/sre-guides/`; it was not re-run on the guides-only candidate.

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
The binding production run of 2026-10-27 at `cc7285e` (the PR #28 merge, whose tree equals the
audited candidate `781922a`, whose fresh full security audit the landed gate record reuses
with the same five open security IDs) granted owner waivers for these nine rows, for this single release
only, expiring 2026-10-28T03:37:58Z. Underlying results stay in each row; the controls are not implemented,
and an expired waiver restores each block for the next publication.

Binding run (draft) for candidate `26bf4b2c6db3a792e8f00c38074284b5102707cb` (tree `21a00a909ee2b3860261f2a9926a4b8cf2d238c8`, release 1.43.0, which ships 1.42.0 with it), 2026-10-28T21:38:23Z, catalog 3. Delta from the production cursor `cc7285e` (an ancestor of the candidate): 86 paths in 38 commits, covering the unbound 1.42.0 draft at `a7c52a6`, the fix/1.42-fix-all merge and the tstack adoption (five MIT skills, the `pr-wait` executable and its CI step, the ship-deploy staging-off rules and contract check, job timeouts in both workflows, the regenerated site). `ci.yml` and `static.yml` re-ran profile detection: no flag changed. The catalog moved from 2 to 3 with a known change list (CST-03 added), so CST-03 was assessed (NOT APPLICABLE: no staging) instead of a new baseline, as the catalog 1 to 2 change was handled; the baseline (2026-10-18, catalog 1) ages out on 2027-01-16, before the waivers expire. The nine 2026-10-27 waivers expired before this run; the owner's 2026-10-28 decision re-waives them to 2027-01-25T23:59:59Z, and a separate 2026-10-28 decision waives SEC-15 to the same date. Status changes against the tracked ledger: SEC-12 and SEC-13 PASS to BLOCKED (no import for this commit), SEC-15 PASS to WAIVED (underlying FAIL per the a7c52a6 gate), MNT-03 and TST-06 NOT TESTED to PASS, MNT-02 NOT TESTED to FAIL (advisory; API read). ASY-02 stays WAIVED, but `pr-wait` adds an outbound call without a timeout that the waiver's reason does not name. SEC and CMP rows are not re-audited here.

Binding run for candidate `be1a548c7a2174190c04ad9a3048e82525daee3c` (tree `87efb4ee654102af95dd2012b067ca11a0c9bd5e`, release 1.44.0), bound 2026-10-30T13:39:10Z and merged as `d98853b2a3098eb1cab786c81fda7a1e655d40e5` (PR #36, same tree), catalog 3. Delta from the production cursor `f7f3958`: 14 paths in one commit (`pr-wait` fails closed on malformed check entries and a moved head and reports a failure before the ten-poll stop, four new tests; `babysit-pr` text; the orchestrator's crossed reviewer seat; the `codex-lane` egress line in `README.md`, `SECURITY.md` and `site/index.html`; the regenerated site; the 1.44.0 bump; `MEMORY.md`; a tstack spec clarification; the 1.43.0 fold-in of this ledger). No workflow, manifest, lockfile, environment template, `tools/` or CSP change, so the profile and catalog stand and only the touched rows and the always-on set were reassessed. The delta's gates ran on a clean `git archive` of the exact commit, 12 of 12 PASS (`.scratch/readiness/be1a548c7a2174190c04ad9a3048e82525daee3c/gates-bind.summary.txt`); SEC-12 and SEC-13 were imported as Yes from the completed security gate (WAIVED, no confirmed finding, independent acceptance PASS); verdict ready, 0 open blockers, the ten owner waivers unchanged. The owner chose not to wait for PR CI; main CI run 41065045522 and Pages run 41067072837 succeeded after the merge and the seven served files matched the tree, before tag `v1.44.0`.

Binding run for candidate `5336080e6919f6f44f8abb90eb1bf9455ab1cc37` (tree `5ca06ffc2d23d2537b7a5c87bff9d4b68ceb38ff`, PR #37, `mneves-motion-film`, shipped unreleased on `main`), bound 2026-10-31T22:25:32Z and merged as `c3dc2bb529da530e07572af6046d4e7312863711` (same tree), catalog 3. The assessment of `624562e` (`.scratch/readiness/624562ec07960596c8eb847e92ba50a9e9ec3ff0/production-assessment.md`) carries over for every row; the delta of 3 paths (the C-M1 and DEL/C1 output fixes with planted cases) changes no manifest, workflow, site, catalog or profile input, so DEL-03, TST-06 and SEC-11 were re-derived and the rest carried. Offline suite bound to the candidate: 51 PASS, exit 0; PR CI run 41246384032, five jobs SUCCESS; security gate WAIVED with independent acceptance PASS by the same verifier; verdict ready, 0 open blockers, waivers unchanged. Hardening and documentation items from that gate (H-M2 to H-M6, D-M1, D-B10 to D-B15) are carried into release 1.45.0.

Binding run for candidate `edeb1315ac99892e832698f03c39394ae5b4256b` (tree `d1552692a7ea2d497992adfd462ba2f9198b624d`, release 1.45.0: PR #40 at `a322c9f3` and PR #39), bound 2026-11-04T08:05:48Z and merged as `ccd51b4bd16230dde4d9197d8c5482134202f0fa` (PR #41, same tree), catalog 3. Full security gate across the candidate chain fe0b8b2 → 33dc773 → 05245fe → 57fb1e8 → 95d71fe → 983927a → ddd05ce → edeb131 (finders A and B on Opus at fe0b8b2, delta finder C at 33dc773, eight autoreview rounds on `tools/scripts/deploy.sh` and `init.sh`, independent verification on GPT-6.1 Sol at edeb131: WAIVED, acceptance PASS, readiness step 5 PASS, no confirmed finding). Offline suite bound to the candidate: 60 PASS, exit 0 (`.scratch/readiness/edeb1315…/gates.summary.txt`); PR CI not awaited by the owner's choice, main CI run 41797070135 and Pages run 41798867245 SUCCESS after the merge, seven served files byte-equal to the tree. SEC-11, SEC-12 and SEC-13 imported Yes from that gate; verdict ready, 0 open blockers, waivers unchanged (SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04). The release adds `tools/scripts/deploy.sh` (merge-tree check before the merge, newest same-tree record authoritative, waiver and validity windows, served-byte comparison, reuse records, annotated tag) and `init.sh`, with the `pr-wait` and motion-film hardening. Defects found after binding and fixed in 1.45.1: the readiness record and its reuse copy lacked `independent_acceptance` (added to both records on 2026-11-04 citing the step-5 verdict; `deploy.sh` now refuses a readiness record without it), and the tag message repeated the security ids on the Readiness and Waivers lines (the `v1.45.0` tag was written by hand without the repetition).

Binding run for candidate `63d95fe4e7ce9e33878f1bfd3814d41412b9fe93` (tree `37155bffb9c3b085eb0ff50beeab16914e3bf784`, release 1.45.1: PR #40's tail 15e0298..c46c77c4, the 1.45.0 ledger fold and the `deploy.sh`/`changelog-rows.py` fixes), bound 2026-11-04T12:19:40Z and merged as `a53b03cfe214d24d46387d4482730b1064658ca0` (PR #42, same tree), catalog 3. Chain extension of the 1.45.0 gate over `git diff ccd51b4b 63d95fe` (28 paths): delta finder D on Opus, autoreview on GPT-6.1 Sol (no finding), independent verification on GPT-6.1 Sol (WAIVED, acceptance PASS, step 5 PASS, no confirmed finding). Offline suite bound to the candidate: 60 PASS, exit 0 (SHA-256 4030c4fcaf50c0f3d3d2e038e2a49b59a82576f36fc20857a54f5aafdf0a1c7c); main CI run 41828329349 succeeded on its second attempt after the first was cancelled, Pages run 41830567961, seven served files byte-equal; `v1.45.1` written by hand from the records after `deploy.sh` stopped on the cancelled attempt (1.45.3 gives it a resume mode). SEC-11, SEC-12 and SEC-13 imported Yes from that gate; verdict ready, 0 open blockers, waivers unchanged (SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04). Finder D's notes carried: D-1 needs-validation (an unresolved thread with no readable comment counts as resolved), D-4 hardening (shell globbing of waiver ids, fixed in 1.45.3), DOC-D1 to DOC-D5 (fixed in 1.45.2 and 1.45.3).

Binding run for candidate `64d2ac6661e0c9fb1cdb1d35892963c23cd9bccf` (tree `12be405242b152af50a0237e72b5b8f12e08ed34`, release 1.45.2: the Pages CI waiver in `static.yml`, `check-pages.test.py`, CONTRIBUTING's manual release sequence, on top of 1.45.1), run by another session; pushed to `main` as `7587b764d9d909b39a4c75a814cacf2dfee1fcd9` with `[skip ci]` and bound there at 2026-11-04T12:48:13Z (security reused from `64d2ac66`, same tree), catalog 3. Records: `.scratch/security-gate/64d2ac66…/production.md` (WAIVED, independent acceptance PASS) and `.scratch/readiness/7587b764…/` (ready, 0 open blockers, 10 waivers, valid until 2026-11-05T12:19:40Z as the record states; `ledger-update.md` there is that session's fold note). Published by the owner's CI waiver dispatch (Pages run 41832914376, CI waived, not passed) and tagged `v1.45.2`. The next binding run reassesses DEL-03 on the waiver route as `docs/readiness/plan.md` says.

Carried to candidate `0237b144c87a8b0ce97496d3c328a43a7adb893a` (tree `7c88476df09c475025a4446f781f557062bd79c5`), 2026-10-28T22:09:10Z: the security gate's 26bf4b2 finder candidates were fixed in two commits, `2bfd301` (`pr-wait`: bot ownership by GitHub App, billing excused only for a run with zero steps, linear markup stripping, control characters dropped, a 120 s timeout on each `gh` call) and `0237b14` (skill text: PR text is data, a sandbox for contributors' code, D1 deletion needs the user's authorization, the Workflow identity check). Delta `26bf4b2..0237b14`: 11 paths, no workflow, manifest, lockfile, `tools/` or ledger change, so the profile and catalog stand and only the touched rows and the always-on set were reassessed. No status changed: ASY-02 stays WAIVED with underlying FAIL, but its `pr-wait` hang is closed (jitter and `Retry-After` remain).

Carried to the final candidate `7dff4754d49cc3a2fbe9f151e35d6684e7b0c91a` (tree `1c7141315b0ba50040ac50845f63fe8260f6b73f`), 2026-10-29T01:25:16Z: the 0237b14 security gate returned WAIVED with one confirmed Medium (C-A2), and the owner chose to fix it first. Four commits: `2531e2c` and `f805c6c` (`pr-wait` excuses a billing block only for a GitHub Actions job with zero steps that the Actions API returns, and waits on a bot check with a run going), `864c38d` (skill texts closing B-01, B-03, C-A3) and `7dff475` (`babysit-pr` text). Delta `0237b14..7dff475`: 8 paths, no workflow, manifest, lockfile, `tools/`, `site/` or ledger change, so the profile and catalog stand and only the touched rows and the always-on set were reassessed. No status changed. The owner extended ASY-02's waiver reason to cover `pr-wait`'s retry policy (round 2 approval).

Carried to the final candidate `4f2e7c229e75d763ebfccfd25d1f9f710cff148d` (tree `e3b3f3eb8af5b3889fd56c241d3725561d1a108c`), 2026-10-29T06:55:41Z: the 7dff475 security gate returned WAIVED with one confirmed Medium (C-A1, the rollup read to its first 100 contexts), and the owner chose to fix it first (`.scratch/security-gate/4f2e7c229e75d763ebfccfd25d1f9f710cff148d/approval-20261029-round3.json`). Two commits: `40aa907` (`pr-wait` pages the check rollup; past 1,000 checks it excuses nothing) and `4f2e7c2` (`babysit-pr` text). Delta `7dff475..4f2e7c2`: 4 paths, no workflow, manifest, lockfile, `tools/`, `site/` or ledger change, so the profile and catalog stand and only the touched rows and the always-on set were reassessed. No status changed.

Carried to the final candidate `8a4472ce566d81d463fb9549c776e852a2bee636` (tree `1ef0b2046acbec7c653d66a43b02d4db56ce0df1`), 2026-10-29T21:42:00Z: the 4f2e7c2 security gate's finders reported that `pr-wait` counted a gating bot done during an incomplete read or when a workflow job shared its check name (C-A4, C-B1), and gaps in `SECURITY.md` (D-1) (`.scratch/security-gate/4f2e7c229e75d763ebfccfd25d1f9f710cff148d/audit-A.md`, `audit-B.md`); both were fixed before verification. Two commits: `b1e0c15` (`pr-wait`: an incomplete read or a shared name never ends a bot's wait; 4 new tests) and `8a4472c` (`SECURITY.md` names `pr-wait` in the runtime table, the scope list and the data map; `babysit-pr` wording). Delta `4f2e7c2..8a4472c`: 5 paths, no workflow, manifest, lockfile, `tools/`, `site/` or ledger change, so the profile and catalog stand and only the touched rows and the always-on set were reassessed. No status changed. Bookkeeping for the release PR: many carried rows cite `SECURITY.md` by line numbers older than the `pr-wait` entry (`:56`, `:71`, `:94`, `:107-108`, `:117-118`, `:148-156`); the claims they quote still hold at `8a4472c` (`:57`, `:90`, `:123`, `:128-129`, `:149`, `:156`), so no status depends on them, but the numbers need refreshing.

Carried to the final candidate `3937725d3158a582d8cf44309db3a62d8cb42126` (tree `63881a5f83f13e1747b0a3c34afc7bc988e5f17d`), 2026-10-29T22:30:00Z: the 8a4472c security gate's finders reported that an incomplete check read made `--until ready` wait forever (C-A5, C-B2), that a nameless CheckRun raised outside the read guard (H-A2), that check links printed unquoted (H-A5), and documentation gaps (D-1r data map, D-2 skill count, README license list and egress, D-3 exit codes) (`.scratch/security-gate/8a4472ce566d81d463fb9549c776e852a2bee636/audit-A.md`, `audit-B.md`). One commit, `3937725`, fixes them; C-A6 (needs-validation) and D-4 (an unshipped spec) are unchanged. Delta `8a4472c..3937725`: 11 paths, among them three copy lines in `site/`; no workflow, manifest, lockfile, `tools/`, CSP or ledger change, so the profile and catalog stand and only the touched rows (including the UX rows for the site copy) and the always-on set were reassessed. No status changed. The stale `SECURITY.md` line citations noted for `8a4472c` remain bookkeeping for the release PR.

## Recorded controls

Totals: 136 rows · NOT APPLICABLE 66 · PASS 20 · FAIL 4 · NOT TESTED 20 · BLOCKED 0 · WAIVED 26.

| ID | Status | Tier | Evidence (scope, date, commit) | Owner | Next action or waiver |
|---|---|---|---|---|---|
| DM-01 | PASS | blocker | 1.51.0: source, local, audit `7e1b7d4`; private `binding-assessment.json`, control `DM-01` | proposed: maintainer | — |
| DM-02 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DM-02` | proposed: maintainer | — |
| DM-03 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DM-03` | proposed: maintainer | — |
| DM-04 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DM-04` | @mneves75 | Plan entry 11; underlying FAIL; waiver @mneves75 to 2026-11-14T23:59:59Z; candidate-only: 1.46.0 to 1.50.0, then 1.51.0 by conditional owner approval |
| DM-05 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DM-05` | proposed: maintainer | — |
| DM-06 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DM-06` | proposed: maintainer | — |
| DM-07 | PASS | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DM-07` | proposed: maintainer | — |
| BR-01 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `BR-01` | @mneves75 | Plan entry 11; underlying NOT TESTED; waiver @mneves75 to 2026-11-14T23:59:59Z; candidate-only: 1.46.0 to 1.50.0, then 1.51.0 by conditional owner approval |
| BR-02 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `BR-02` | @mneves75 | Plan entry 11; underlying NOT TESTED; waiver @mneves75 to 2026-11-14T23:59:59Z; candidate-only: 1.46.0 to 1.50.0, then 1.51.0 by conditional owner approval |
| BR-03 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `BR-03` | @mneves75 | Plan entry 11; underlying NOT TESTED; waiver @mneves75 to 2026-11-14T23:59:59Z; candidate-only: 1.46.0 to 1.50.0, then 1.51.0 by conditional owner approval |
| BR-04 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `BR-04` | @mneves75 | Plan entry 6; underlying BLOCKED; waiver @mneves75 to 2026-11-14T23:59:59Z; candidate-only: 1.46.0 to 1.50.0, then 1.51.0 by conditional owner approval |
| BR-05 | NOT APPLICABLE | contract | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `BR-05` | proposed: maintainer | — |
| DC-01 | PASS | blocker | 1.51.0: source, local, audit `7e1b7d4`; private `binding-assessment.json`, control `DC-01` | proposed: maintainer | — |
| DC-02 | PASS | blocker | 1.51.0: source, local, audit `7e1b7d4`; private `binding-assessment.json`, control `DC-02` | proposed: maintainer | — |
| DC-03 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DC-03` | proposed: maintainer | — |
| DC-04 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DC-04` | proposed: maintainer | — |
| DC-05 | PASS | blocker | 1.51.0: source, local, audit `7e1b7d4`; private `binding-assessment.json`, control `DC-05` | proposed: maintainer | — |
| DC-06 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DC-06` | proposed: maintainer | — |
| DC-07 | FAIL | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DC-07` | proposed: maintainer | Plan entry 11 |
| DC-08 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DC-08` | proposed: maintainer | — |
| DC-09 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DC-09` | proposed: maintainer | — |
| DC-10 | NOT APPLICABLE | contract | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DC-10` | proposed: maintainer | — |
| DEL-01 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DEL-01` | proposed: maintainer | — |
| DEL-02 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DEL-02` | proposed: maintainer | Plan entry 9 |
| DEL-03 | PASS | blocker | 1.51.0: source, local, audit `7e1b7d4`; private `binding-assessment.json`, control `DEL-03` | proposed: maintainer | — |
| DEL-04 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DEL-04` | @mneves75 | Plan entry 5; underlying NOT TESTED; waiver @mneves75 to 2027-01-25T23:59:59Z; historical existing waiver; fresh gate required for later reuse |
| DEL-05 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DEL-05` | @mneves75 | Plan entry 12; underlying BLOCKED; waiver @mneves75 to 2026-11-14T23:59:59Z; candidate-only: 1.46.0 to 1.50.0, then 1.51.0 by conditional owner approval |
| DEL-06 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DEL-06` | proposed: maintainer | — |
| DEL-07 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DEL-07` | proposed: maintainer | Advisory, not planned |
| DEL-08 | FAIL | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DEL-08` | proposed: maintainer | Plan entry 9 |
| DEL-09 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `DEL-09` | @mneves75 | Plan entry 3; underlying NOT TESTED; waiver @mneves75 to 2027-01-25T23:59:59Z; historical existing waiver; fresh gate required for later reuse |
| ASY-01 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `ASY-01` | proposed: maintainer | — |
| ASY-02 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `ASY-02` | @mneves75 | Plan entry 10; underlying FAIL; waiver @mneves75 to 2027-01-25T23:59:59Z; historical existing waiver; fresh gate required for later reuse |
| ASY-03 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `ASY-03` | proposed: maintainer | — |
| ASY-04 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `ASY-04` | proposed: maintainer | — |
| ASY-05 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `ASY-05` | proposed: maintainer | — |
| ASY-06 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `ASY-06` | proposed: maintainer | — |
| ASY-07 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `ASY-07` | proposed: maintainer | — |
| ASY-08 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `ASY-08` | proposed: maintainer | Advisory, not planned |
| ASY-09 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `ASY-09` | proposed: maintainer | — |
| EML-01 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `EML-01` | proposed: maintainer | — |
| EML-02 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `EML-02` | proposed: maintainer | — |
| EML-03 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `EML-03` | proposed: maintainer | — |
| EML-04 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `EML-04` | proposed: maintainer | — |
| CST-01 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `CST-01` | proposed: maintainer | Advisory, not planned |
| CST-02 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `CST-02` | @mneves75 | Plan entry 12; underlying BLOCKED; waiver @mneves75 to 2026-11-14T23:59:59Z; candidate-only: 1.46.0 to 1.50.0, then 1.51.0 by conditional owner approval |
| CST-03 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `CST-03` | proposed: maintainer | — |
| OBS-01 | FAIL | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `OBS-01` | proposed: maintainer | Advisory, not planned |
| OBS-02 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `OBS-02` | @mneves75 | Plan entry 12; underlying BLOCKED; waiver @mneves75 to 2026-11-14T23:59:59Z; candidate-only: 1.46.0 to 1.50.0, then 1.51.0 by conditional owner approval |
| OBS-03 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `OBS-03` | @mneves75 | Plan entry 12; underlying BLOCKED; waiver @mneves75 to 2026-11-14T23:59:59Z; candidate-only: 1.46.0 to 1.50.0, then 1.51.0 by conditional owner approval |
| OBS-04 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `OBS-04` | @mneves75 | Plan entry 12; underlying BLOCKED; waiver @mneves75 to 2026-11-14T23:59:59Z; candidate-only: 1.46.0 to 1.50.0, then 1.51.0 by conditional owner approval |
| OBS-05 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `OBS-05` | proposed: maintainer | Advisory, not planned |
| OBS-06 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `OBS-06` | proposed: maintainer | — |
| OBS-07 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `OBS-07` | @mneves75 | Plan entry 6; underlying BLOCKED; waiver @mneves75 to 2026-11-14T23:59:59Z; candidate-only: 1.46.0 to 1.50.0, then 1.51.0 by conditional owner approval |
| OBS-08 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `OBS-08` | proposed: maintainer | Advisory, not planned |
| OBS-09 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `OBS-09` | proposed: maintainer | Advisory, not planned |
| OBS-10 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `OBS-10` | proposed: maintainer | Advisory, not planned |
| TST-01 | PASS | advisory | 1.51.0: source, local, audit `7e1b7d4`; private `binding-assessment.json`, control `TST-01` | proposed: maintainer | — |
| TST-02 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `TST-02` | proposed: maintainer | Advisory, not planned |
| TST-03 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `TST-03` | proposed: maintainer | — |
| TST-04 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `TST-04` | @mneves75 | Plan entry 12; underlying BLOCKED; waiver @mneves75 to 2026-11-14T23:59:59Z; candidate-only: 1.46.0 to 1.50.0, then 1.51.0 by conditional owner approval |
| TST-05 | PASS | blocker | 1.51.0: source, local, audit `7e1b7d4`; private `binding-assessment.json`, control `TST-05` | proposed: maintainer | — |
| TST-06 | PASS | advisory | 1.51.0: source, local, audit `7e1b7d4`; private `binding-assessment.json`, control `TST-06` | proposed: maintainer | — |
| TST-07 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `TST-07` | proposed: maintainer | Advisory, not planned |
| BIL-01 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `BIL-01` | proposed: maintainer | — |
| BIL-02 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `BIL-02` | proposed: maintainer | — |
| BIL-03 | NOT APPLICABLE | contract | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `BIL-03` | proposed: maintainer | — |
| BIL-04 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `BIL-04` | proposed: maintainer | — |
| BIL-05 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `BIL-05` | proposed: maintainer | — |
| BIL-06 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `BIL-06` | proposed: maintainer | — |
| BIL-07 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `BIL-07` | proposed: maintainer | — |
| BIL-08 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `BIL-08` | proposed: maintainer | — |
| API-01 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `API-01` | proposed: maintainer | — |
| API-02 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `API-02` | proposed: maintainer | — |
| API-03 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `API-03` | proposed: maintainer | — |
| API-04 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `API-04` | proposed: maintainer | — |
| AI-01 | PASS | blocker | 1.51.0: source, local, audit `7e1b7d4`; private `binding-assessment.json`, control `AI-01` | proposed: maintainer | — |
| AI-02 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `AI-02` | @mneves75 | Plan entry 10; underlying FAIL; waiver @mneves75 to 2026-11-14T23:59:59Z for 1.51.0 (1.50.0's ran to the same date, 1.49.0's and 1.48.0's to 2026-11-12T23:59:59Z, 1.47.0's to 2026-11-10T23:59:59Z, 1.46.1's to 2026-11-06T23:59:59Z, 1.46.0's to 2027-01-25T23:59:59Z); candidate-only |
| AI-03 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `AI-03` | proposed: maintainer | Advisory, not planned |
| UX-01 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `UX-01` | proposed: maintainer | Advisory, not planned |
| UX-02 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `UX-02` | proposed: maintainer | Plan entry 8 |
| UX-03 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `UX-03` | proposed: maintainer | Plan entry 8 |
| UX-04 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `UX-04` | proposed: maintainer | — |
| UX-05 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `UX-05` | proposed: maintainer | — |
| UX-06 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `UX-06` | proposed: maintainer | Plan entry 8 |
| UX-07 | NOT APPLICABLE | contract | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `UX-07` | proposed: maintainer | — |
| UX-08 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `UX-08` | proposed: maintainer | — |
| UX-09 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `UX-09` | proposed: maintainer | Plan entry 8 |
| MNT-01 | PASS | advisory | 1.51.0: source, local, audit `7e1b7d4`; private `binding-assessment.json`, control `MNT-01` | proposed: maintainer | — |
| MNT-02 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `MNT-02` | @mneves75 | Plan entry 4; underlying BLOCKED; waiver @mneves75 to 2026-11-14T23:59:59Z; candidate-only: 1.46.0 to 1.50.0, then 1.51.0 by conditional owner approval |
| MNT-03 | PASS | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `MNT-03` | proposed: maintainer | — |
| MNT-04 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `MNT-04` | proposed: maintainer | Advisory, not planned |
| MNT-05 | PASS | blocker | 1.51.0: source, current-vendor-source-imported, audit `7e1b7d4`; private `binding-assessment.json`, control `MNT-05` | proposed: maintainer | — |
| MNT-06 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `MNT-06` | proposed: maintainer | Advisory, not planned |
| MNT-07 | FAIL | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `MNT-07` | proposed: maintainer | Advisory, not planned |
| MNT-08 | PASS | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `MNT-08` | proposed: maintainer | — |
| MNT-09 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `MNT-09` | proposed: maintainer | Advisory, not planned |
| MNT-10 | NOT TESTED | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `MNT-10` | proposed: maintainer | Plan entry 7 |
| OPS-01 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `OPS-01` | proposed: maintainer | — |
| OPS-02 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `OPS-02` | proposed: maintainer | — |
| OPS-03 | PASS | advisory | 1.51.0: source, local, audit `7e1b7d4`; private `binding-assessment.json`, control `OPS-03` | proposed: maintainer | — |
| OPS-04 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `OPS-04` | @mneves75 | Plan entry 2; underlying FAIL; waiver @mneves75 to 2027-01-25T23:59:59Z; historical existing waiver; fresh gate required for later reuse |
| OPS-05 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `OPS-05` | @mneves75 | Plan entry 6; underlying BLOCKED; waiver @mneves75 to 2026-11-14T23:59:59Z; candidate-only: 1.46.0 to 1.50.0, then 1.51.0 by conditional owner approval |
| OPS-06 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `OPS-06` | @mneves75 | Plan entry 6; underlying BLOCKED; waiver @mneves75 to 2026-11-14T23:59:59Z; candidate-only: 1.46.0 to 1.50.0, then 1.51.0 by conditional owner approval |
| SEC-01 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-01`; imported security disposition, details restricted | proposed: maintainer | — |
| SEC-02 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-02`; imported security disposition, details restricted | proposed: maintainer | — |
| SEC-03 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-03`; imported security disposition, details restricted | proposed: maintainer | — |
| SEC-04 | NOT APPLICABLE | contract | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-04`; imported security disposition, details restricted | proposed: maintainer | — |
| SEC-05 | NOT APPLICABLE | contract | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-05`; imported security disposition, details restricted | proposed: maintainer | — |
| SEC-06 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-06`; imported security disposition, details restricted | proposed: maintainer | — |
| SEC-07 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-07`; imported security disposition, details restricted | proposed: maintainer | — |
| SEC-08 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-08`; imported security disposition, details restricted | proposed: maintainer | — |
| SEC-09 | NOT APPLICABLE | advisory | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-09`; imported security disposition, details restricted | proposed: maintainer | — |
| SEC-10 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-10`; imported security disposition, details restricted | proposed: maintainer | — |
| SEC-11 | PASS | blocker | 1.51.0: source, local, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-11`; imported security disposition, details restricted | proposed: maintainer | — |
| SEC-12 | PASS | blocker | 1.51.0: source, local, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-12`; imported security disposition, details restricted | proposed: maintainer | — |
| SEC-13 | PASS | blocker | 1.51.0: source, local, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-13`; imported security disposition, details restricted | proposed: maintainer | — |
| SEC-14 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-14`; imported security disposition, details restricted | proposed: maintainer | — |
| SEC-15 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-15`; imported security disposition, details restricted | @mneves75 | Plan entry 1; underlying FAIL; waiver @mneves75 to 2027-01-25T23:59:59Z; historical existing waiver; fresh gate required for later reuse |
| SEC-16 | PASS | blocker | 1.51.0: source, production-imported, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-16`; imported security disposition, details restricted | proposed: maintainer | — |
| SEC-17 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-17`; imported security disposition, details restricted | @mneves75 | Plan entry 1; underlying NOT TESTED; waiver @mneves75 to 2027-01-25T23:59:59Z; historical existing waiver; fresh gate required for later reuse |
| SEC-18 | PASS | blocker | 1.51.0: source, local, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-18`; imported security disposition, details restricted | proposed: maintainer | — |
| SEC-19 | NOT APPLICABLE | contract | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-19`; imported security disposition, details restricted | proposed: maintainer | — |
| SEC-20 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-20`; imported security disposition, details restricted | @mneves75 | Plan entry 1; underlying FAIL; waiver @mneves75 to 2027-01-25T23:59:59Z; historical existing waiver; fresh gate required for later reuse |
| SEC-21 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-21`; imported security disposition, details restricted | @mneves75 | Plan entry 1; underlying NOT TESTED; waiver @mneves75 to 2027-01-25T23:59:59Z; historical existing waiver; fresh gate required for later reuse |
| SEC-22 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-22`; imported security disposition, details restricted | proposed: maintainer | — |
| SEC-23 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `SEC-23`; imported security disposition, details restricted | @mneves75 | Plan entry 1; underlying NOT TESTED; waiver @mneves75 to 2027-01-25T23:59:59Z; historical existing waiver; fresh gate required for later reuse |
| CMP-01 | NOT APPLICABLE | contract | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `CMP-01`; imported security disposition, details restricted | proposed: maintainer | — |
| CMP-02 | NOT APPLICABLE | contract | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `CMP-02`; imported security disposition, details restricted | proposed: maintainer | — |
| CMP-03 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `CMP-03`; imported security disposition, details restricted | proposed: maintainer | — |
| CMP-04 | NOT APPLICABLE | contract | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `CMP-04`; imported security disposition, details restricted | proposed: maintainer | — |
| CMP-05 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `CMP-05`; imported security disposition, details restricted | proposed: maintainer | — |
| CMP-06 | WAIVED | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `CMP-06`; imported security disposition, details restricted | @mneves75 | Plan entry 1; underlying NOT TESTED; waiver @mneves75 to 2027-01-25T23:59:59Z; historical existing waiver; fresh gate required for later reuse |
| CMP-07 | NOT APPLICABLE | contract | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `CMP-07`; imported security disposition, details restricted | proposed: maintainer | — |
| CMP-08 | NOT APPLICABLE | contract | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `CMP-08`; imported security disposition, details restricted | proposed: maintainer | — |
| CMP-09 | NOT APPLICABLE | blocker | 1.51.0: source, audit `7e1b7d4`; private `binding-assessment.json`, control `CMP-09`; imported security disposition, details restricted | proposed: maintainer | — |

## Gate history

| Date | Target | Commit | Verdict | Open blockers | Waivers |
|---|---|---|---|---|---|
| 2026-10-18 | production | b95604c | ready | 0 | SEC-13 SEC-17 SEC-20 SEC-23 CMP-06 DEL-03 DEL-04 DEL-09 OPS-04 MNT-05 ASY-02 |
| 2026-10-27 | production | cc7285eb41809fb9dfc35c06adb447ab8b61310b | ready | 0 | SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 |
| 2026-10-28 | production | 26bf4b2c6db3a792e8f00c38074284b5102707cb | not-ready (draft, superseded by `0237b14` before binding) | 2 (SEC-12, SEC-13, pending import) | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 |
| 2026-10-28 | production | 0237b144c87a8b0ce97496d3c328a43a7adb893a | not-ready (draft, superseded by `7dff475` before binding) | 2 (SEC-12, SEC-13, pending import) | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 |
| 2026-10-29 | production | 7dff4754d49cc3a2fbe9f151e35d6684e7b0c91a | not-ready (draft, superseded by `4f2e7c2` before binding) | 2 (SEC-12, SEC-13, pending import) | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 |
| 2026-10-29 | production | 4f2e7c229e75d763ebfccfd25d1f9f710cff148d | not-ready (draft, superseded by `8a4472c` before binding) | 2 (SEC-12, SEC-13, pending import) | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 |
| 2026-10-29 | production | 8a4472ce566d81d463fb9549c776e852a2bee636 | not-ready (draft, superseded by `3937725` before binding) | 2 (SEC-12, SEC-13, pending import) | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 |
| 2026-10-29 | production | f7f3958ed31ecbd315789e8e1fb10705211a4b09 | ready | 0 | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 |
| 2026-10-30 | production | d98853b2a3098eb1cab786c81fda7a1e655d40e5 | ready (v1.44.0; candidate `be1a548`, same tree) | 0 | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 |
| 2026-10-31 | production | c3dc2bb529da530e07572af6046d4e7312863711 | ready (PR #37; candidate `5336080`, same tree) | 0 | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 |
| 2026-11-04 | production | ccd51b4bd16230dde4d9197d8c5482134202f0fa | ready (v1.45.0; candidate `edeb131`, same tree) | 0 | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 |
| 2026-11-04 | production | a53b03cfe214d24d46387d4482730b1064658ca0 | ready (v1.45.1; candidate `63d95fe`, same tree) | 0 | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 |
| 2026-11-04 | production | 7587b764d9d909b39a4c75a814cacf2dfee1fcd9 | ready (v1.45.2, another session's run; candidate `64d2ac66`, same tree) | 0 | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 |
| 2026-11-04 | production | f0abfa0151fd97bb3491fbef02d060bd2a1dfa1e | ready (v1.45.3; candidate `ac7c6e28`, same tree) | 0 | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 |
| 2026-11-06 | production | 0f3047be818069bcc1f2d91150f0e394505b55e3 | ready (v1.46.0; original audit `24f3876`, same tree) | 0 | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 AI-02 DM-04 BR-01 BR-02 BR-03 BR-04 DEL-05 CST-02 OBS-02 OBS-03 OBS-04 OBS-07 TST-04 MNT-02 OPS-05 OPS-06 |
| 2026-11-06 | production | b6630d8fe65c9f2f18b0eafe54574e1573a09650 | ready (v1.46.1; original audit `44464be`, same tree) | 0 | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 AI-02 DM-04 BR-01 BR-02 BR-03 BR-04 DEL-05 CST-02 OBS-02 OBS-03 OBS-04 OBS-07 TST-04 MNT-02 OPS-05 OPS-06 |
| 2026-11-10 | production | ae1e8090866a46708f41e65baa84a9ad8201e81e | ready (v1.47.0; original audit `366bd67`, same tree) | 0 | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 AI-02 DM-04 BR-01 BR-02 BR-03 BR-04 DEL-05 CST-02 OBS-02 OBS-03 OBS-04 OBS-07 TST-04 MNT-02 OPS-05 OPS-06 |
| 2026-11-11 | production | 93bf9f911a09e992fb15efac8d96741d3b9faf6c | ready (v1.48.0; original audit `dc65309`, same tree) | 0 | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 AI-02 DM-04 BR-01 BR-02 BR-03 BR-04 DEL-05 CST-02 OBS-02 OBS-03 OBS-04 OBS-07 TST-04 MNT-02 OPS-05 OPS-06 |
| 2026-11-11 | production | afcf6ded615bf71e64a474109fab3181ef807dda | ready (v1.49.0; original audit `d8038a8`, same tree) | 0 | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 AI-02 DM-04 BR-01 BR-02 BR-03 BR-04 DEL-05 CST-02 OBS-02 OBS-03 OBS-04 OBS-07 TST-04 MNT-02 OPS-05 OPS-06 |
| 2026-11-11 | production | 0c1b638af6ef0a56638c2538f7bfc20196f771e0 | ready (v1.50.0; original audit `59d08af`, same tree) | 0 | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 AI-02 DM-04 BR-01 BR-02 BR-03 BR-04 DEL-05 CST-02 OBS-02 OBS-03 OBS-04 OBS-07 TST-04 MNT-02 OPS-05 OPS-06 |
| 2026-11-13 | production | 2ecd2d05504ca832c730e30453fa41cbdcd836ec | ready (v1.51.0; original audit `7e1b7d4`, same tree) | 0 | SEC-15 SEC-17 SEC-20 SEC-21 SEC-23 CMP-06 DEL-04 DEL-09 ASY-02 OPS-04 AI-02 DM-04 BR-01 BR-02 BR-03 BR-04 DEL-05 CST-02 OBS-02 OBS-03 OBS-04 OBS-07 TST-04 MNT-02 OPS-05 OPS-06 |
