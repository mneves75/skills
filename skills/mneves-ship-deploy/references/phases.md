# Release phases, tags, and staging teardown

Detailed procedures referenced from `../SKILL.md`. Preserve every authorization boundary,
gate order, and live-proof assertion.

## Phase 1 — Review gates (detail)

Run in order, except the security gate (item 2), which runs last; fix what each surfaces
before moving on:

1. **`autoreview`** — pre-commit code review when installed; otherwise the repository's
   documented independent review gate. Run automatically when its content and destination are
   already authorized; keep it bounded to one review and one rerun after accepted corrections.
   Unresolved actionable findings block the release.
2. **Security gate (mandatory in both modes)** — run `mneves-security` in deploy-gate mode
   *last*, after steps 1, 3, and 4, build gates, and Phase 2 land their changes, so it audits
   the exact final tree hash before any deploying push, merge, or tag. Any subsequent tree edit
   creates a new candidate requiring a fresh audit. One audit serves every target of the same
   tree; production runs the gate's reuse pass before promotion. Put its runtime checks into
   `scripts/verify-live.sh` (or equivalent live proof) so they pass before tagging, and record
   the verdict in each tag message (`security gate: PASS`, or `WAIVED <IDs>`). Without
   `mneves-security`, the release is blocked until it is installed
   (`npx skills@latest add mneves75/skills --skill mneves-security -g -y`) or explicitly waived
   by name by the owner; no other review substitutes for it.
3. **`improve` (deep pass)** — for feature or structural releases (skip on patch releases) when
   installed; otherwise a read-only survey in the main session. Land only in-scope items; record
   the rest as named follow-ups.
4. **`mneves-production-readiness`** — provisional readiness assessment when installed; otherwise
   the repository's documented readiness review. Fix in-scope blockers, commit ledger updates,
   and put open production blockers into the decision packet as named waivers.
5. **Oversized findings** — if Phase 1 surfaces work too large for the session, use the host's
   native task/goal workflow only when requested; otherwise report remaining work within scope.

Build, typecheck, lint, and tests must be green before Phase 2. If a gate cannot run locally
(needs a DB, device, or paid service), state which one and why — never claim it passed. Inspect
what CI actually executed rather than trusting an exit-0 summary.

## Phase 2 & 3 — Version, changelog, docs, commit, and PR merge gate

- Bump the single version source of truth (`SemVer`: breaking → major, feature → minor, fix → patch).
- Update `CHANGELOG.md` in house style (one-line bullets, no prose-length hard-wrap); give the
  released version today's date and open a fresh `Unreleased` heading only *after* verification.
- Fix stale user-visible docs (`README.md`, `AGENTS.md`/`CLAUDE.md`, status docs) before closeout.
- Inspect push-, merge-, and tag-triggered workflows *before* choosing a destination ref. If a
  push or merge would trigger production, push a non-deploying working branch and wait for the
  owner's explicit OK for the exact candidate and target.
- Commit atomically with Conventional Commits and explicit paths:
  ```bash
  git commit -m "chore(release): vX.Y.Z" -- <paths you touched>
  git push
  ```
- In PR-first repos, open the PR (`gh pr create`) leading with the problem in plain words, the
  solution, and one line on how it was proved (sanitized before/after images for UI changes).
- **Merge gate (latest head):** every PR merge requires explicit merge authorization (and when a
  merge triggers production, explicit owner approval of the exact candidate and target); proof
  covers every diff change; required checks pass on the actual candidate/merged commit; review bots finished and each finding is fixed or answered
  with a reason; no review requests changes; GitHub reports mergeable (not `BEHIND`/`DIRTY`)
  with no base commits touching PR files after the last green run. Never use `--admin` or any
  bypass. For GitHub billing-blocked checks (zero steps + annotation starting "The job was not
  started because" naming billing/spending limits), run the equivalent checks locally, record
  output as gate evidence, and state plainly why CI was skipped.

## Dev stop (optional, when documented)

When preflight finds a documented dev environment, run it before Phase 4 in the same order:
bind the `dev` readiness gate on the pushed commit under the staging rule, deploy, prove live
with Phase 4 step 3 assertions plus the security gate's runtime checks, then tag:

```bash
git tag -a vX.Y.Z-alpha<N> <commit> -m "vX.Y.Z-alpha<N> — dev; security gate: PASS" && git push origin vX.Y.Z-alpha<N>
```

Use `scripts/release.sh dev` only when supported; otherwise use the documented dev command.
Staging then deploys the same commit. Dev needs no separate confirmation.

## Phase 4 — Staging (`vX.Y.Z-beta<N>`)

Order: bind readiness → deploy pushed commit → prove live → tag. A tag names served, checked bytes.

1. **Bind readiness** for `staging` on the exact pushed commit, writing
   `.scratch/readiness/<commit>/staging.json` (release contract guarantee 11). A `not-ready`
   verdict stops the deploy: fix, push, and re-run the gate.
2. **Deploy** a commit the remote already has (`scripts/release.sh staging` when present and its
   built-in `verify-live.sh` covers every required check, or the detected skill/documented deploy
   command). When additional proof beyond `verify-live.sh` is required (writable-binding checks,
   independent browser/device flows, or a post-deploy observation window), complete that proof
   before creating or pushing the release tag — wire the extra checks into `verify-live.sh` or
   defer tagging until every required check finishes.
3. **Prove live** (`scripts/verify-live.sh staging` when present). Verify:
   - served commit/version and deployed artifact identity match the candidate commit;
   - health response body carries expected fields;
   - one known-good request succeeds and one invalid/unauthorized request is refused;
   - before running any negative/write test on a preview or staging target, confirm its writable
     resource bindings point strictly to staging/preview (never production);
   - exercise changed UI/device flows with an independent browser/device driver (`agent-browser`,
     Playwright, Argent, or equivalent; desktop and mobile separately; signed-in when touched) and
     inspect logs for new errors. Without a driver, mark the flow `NOT TESTED`.
   - treat an active post-deploy observation window as pending/incomplete rather than failed; live
     proof is incomplete and no tag is pushed until a required observation window finishes.
4. **Tag** the verified commit (`<N>` starts at 1 per version; failed or incomplete proofs get no tag):
   ```bash
   git tag -a vX.Y.Z-beta<N> <commit> -m "vX.Y.Z-beta<N> — staging; security gate: PASS" && git push origin vX.Y.Z-beta<N>
   ```
   Waived security gates record their IDs instead: `security gate: WAIVED SEC-19 gate:audit`.
5. **Zero staging schedules:** staging config must declare every schedule/cron empty (never
   inherited); exercise scheduled jobs manually on staging once.
6. **For `ship-prod`:** bind the `production` readiness gate on the same commit, writing
   `.scratch/readiness/<commit>/production.json` with `independent_acceptance: "pass"` (never
   reuse the staging record). Note persistent-state rollback limits explicitly: rolling back
   code or Worker versions does not revert D1/KV/R2/Durable Object state or destructive schema
   migrations.

## Phase 5 — Production (`vX.Y.Z`) & staging teardown

Enter only after explicit owner OK for the exact candidate and production target (any mismatch
invalidates approval). Immediately before promoting (especially after resuming from an earlier
`ship-staging` or waiting for approval), re-confirm the exact commit staging serves, verify
staging is still healthy (reusing an unchanged healthy staging deployment rather than redeploying
it), and confirm a valid, non-expired production security verdict and production readiness record
(re-run the gate if waivers were granted or the record expired). Deploy that exact commit to
production, complete every required live proof — applying the full Phase 4 step 3 assertions to
production (served commit/version and deployed artifact identity matching the candidate commit,
health-body check, positive and negative requests, changed-flow checks, log/error checks, and
`mneves-security` runtime checks, plus any required observation window) — then tag:

```bash
git tag -a vX.Y.Z <commit> -m "vX.Y.Z; security gate: PASS" && git push origin vX.Y.Z
```

Then finish closeout:

- Confirm the tag points at the commit production actually serves.
- **Turn staging off** as a separate, reversible operation in the same task: disable scheduled
  work, queue consumers, workflows (deleting a staging workflow requires the same authorization
  as deleting a staging database), Durable Object alarms, and external schedulers acting on
  staging. An idle request-only staging service may stay so secrets survive. For a staging
  database: confirm it holds nothing production lacks, confirm no release is currently using
  staging, verify its name and id belong to staging
  (not production), export first, and delete only with owner authorization (standing rule or
  explicit line in the production approval packet); otherwise export and hand off the export
  path. Production is done only once staging shows zero scheduled runs and zero writes, each
  with the check that proved it, and anything `NOT TESTED` named.
- Separate publication (GitHub Release, npm, app stores) requires its own explicit `release` /
  `publish` ask (`npm view <pkg>@<version>` proves npm; GitHub Release links npm page, tarball,
  integrity, and CI proof).
- Open the next patch `Unreleased` heading in `CHANGELOG.md`, commit, restore the expected
  branch with `git status -sb` clean of task leftovers, and close with a concise narrative recap.
