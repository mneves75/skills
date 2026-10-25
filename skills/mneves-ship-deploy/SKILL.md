---
name: mneves-ship-deploy
description: "Use for `ship-staging`, `ship-prod`, or an explicit staging/production deployment request for a project you own. Plain `ship` does not invoke this skill or authorize external writes."
license: Apache-2.0
compatibility: The procedure needs only Git. The optional contract check (`scripts/release-contract-check.py`) needs Python 3.11+. The reference release scripts in `assets/` need bash 3.2+, git, curl, sed, awk, python3 and the Wrangler version the project pins.
---

# Ship Staging / Prod

The release closeout chain for the user's own projects has two explicit modes:

- `ship-staging` runs through a verified staging deployment (after a verified dev deployment, when the project has a dev environment) and stops before production.
- `ship-prod` prepares and verifies dev (when the project has one) and staging, then waits for the user's explicit OK for the exact candidate and production target before any production action.

Plain `ship` has no special meaning and grants no release, deploy, push, or pull authority.

This is an orchestrator. Prefer the installed review and deployment skills named below. They are optional integrations, not bundled dependencies: if one is unavailable, use the repository's documented commands for that phase and preserve the same gates, authorization boundaries, and evidence. If no safe documented equivalent exists, report the missing capability and stop that phase. The security gate in Phase 1 is the exception: it has no substitute.

## Approval policy

Within the requested release scope:

- **Dev and staging are authorized:** run authorized reviews, apply verified in-scope corrections, complete required gates, and deploy to the established dev and staging targets without a separate confirmation, regardless of complexity. `ship-staging` still stops before production.
- **Production always waits for explicit OK:** before any production tag, push, deployment, or promotion, present the exact repository, commit, version, production target, staging evidence, material risks, and rollback plan. Wait for the user's explicit approval of that candidate and target. `ship-prod` alone does not grant this approval. If approval of the exact candidate and target already exists, do not ask again.

`autoreview` is a review gate, not a human approval step. Follow its existing authorization requirements for the selected content and review destination; when that authorization already exists, run it without asking again. Preserve its secret-scanning and isolation controls. This policy grants no new authorization to disclose private data.

Staging authorization does not waive required gates or authorize destructive operations, credential access, separate publication, or an unspecified deployment target. Missing required input and failed gates remain blockers.

**One decision packet.** A gate that cannot pass (an advisory with no patched release, a tool that cannot run here) becomes one request to the user, sent as soon as it is known: the candidate (repository, commit, version), the target, each failing gate as a named waiver with its reason, the security gate verdict with each block it asks the owner to waive, and the rollback plan. Keep running every other gate while you wait. An approval of the packet approves exactly the waivers it lists; record them in the release evidence.

## Do not invoke when

- The user said only "ship", "commit", "push", or "land the PR" without naming staging or production → use the normal authorization rules; do not infer either mode.
- The repo is not the user's (contributor PR, someone else's project checked out locally) → stop.
- Working tree is on someone else's branch or has unknown changes from another agent → report and stop.

## Preflight (always)

```bash
git status -sb && git log --oneline -5 && git branch --show-current
```

Then establish, without guessing:

1. **Mode** — `ship-staging` or `ship-prod`, from the explicit target in the request. An ambiguous target is not authorization.
2. **Repo identity** — remote, default branch, whether the remote belongs to the user.
3. **Version source of truth** — `VERSION`, `package.json`, `app.json`/`app.config.ts`, `Cargo.toml`, `pyproject.toml`. Pick one; never bump two out of sync.
4. **Deploy target** — detect, don't assume:
   | Signal | Deploy via |
   |---|---|
   | `vercel.json`, `.vercel/` | `deploy-to-vercel` skill, when installed, or the repository's documented Vercel deployment command |
   | `wrangler.toml` / `wrangler.jsonc` | `cloudflare-deploy` skill, when installed, or the repository's documented Cloudflare deployment command. Read [references/cloudflare.md](references/cloudflare.md) before the first deploy. |
   | `eas.json` + Expo app | `eas-app-stores` skill, when installed, or the repository's documented store workflow (staging = TestFlight / internal track) |
   | `docker-compose.yml`, deploy script, VPS host in repo docs | repo's own deploy script; use `vps-setup` for host work only when installed and authorized. Read [references/vps.md](references/vps.md) before the first deploy. |
5. **Staging environment** — required for both modes. If none exists, say so and ask whether to run beta-tag-only for `ship-staging`; never skip staging and never invent a staging URL. A dev environment is optional: when the repository documents one (deploy command, URL, health check), it becomes the first stop (see Dev stop); never invent one.
6. **Release contract** — `scripts/release.sh` and `scripts/verify-live.sh`, when the repository has them, are the entry points for Phases 4 and 5: start with `scripts/release.sh <target> --check`, which prints the plan and builds, deploys and tags nothing. The checker ships in this skill's own folder, next to this file: run `python3 <skill folder>/scripts/release-contract-check.py <repo>` when Python 3.11+ is available and report each `FAIL`. Read [references/release-contract.md](references/release-contract.md) when an entry point is missing or a check fails.
7. **Readiness ledger** — the production-readiness ledger (`docs/readiness/ledger.md`, or where the repository docs say), its stage, baseline age and each target's last assessed commit. Without a ledger, the first readiness gate runs a baseline.

Report the seven findings in one short paragraph before doing anything mutating.

## Phase 1 — Review gates

Run in order, fixing what each surfaces before moving on:

1. `autoreview` — pre-commit code review, when installed; otherwise use the repository's documented independent review gate. Run automatically when its content and destination are already authorized; do not pause for redundant confirmation. Keep the review bounded: one review and one rerun after accepted corrections. Verify findings and apply in-scope corrections automatically. Unresolved actionable findings block the release; report them rather than repeating the same review indefinitely.
2. **Security gate** (mandatory in both modes) — the separately installed `mneves-security` skill in deploy-gate mode: a full security, privacy and compliance audit with a fix plan and a PASS, BLOCK or WAIVED verdict for the exact commit and each target. Run it last, after steps 1, 3 and 4, the build gates and Phase 2 have landed their changes, so it audits the final release content; it binds by tree hash to the release commit before any push, merge or tag that deploys it, and any later change to the tree is a new candidate with a new audit. Its verdict rules decide what blocks; a block clears only by a fix, disproof, or the owner's named waiver in the decision packet. One audit serves every target of the same tree; production runs the gate's reuse pass before promotion. Its runtime checks belong in `scripts/verify-live.sh` (or the live proof a project uses), so they pass before any tag, and each tag message records the verdict (`security gate: PASS`, or `WAIVED` with the waived IDs). Without the skill, the release is blocked until it is installed (`npx skills@latest add mneves75/skills --skill mneves-security -g -y`) or the owner waives the gate by name; no other review substitutes for it.
3. `improve` (deep pass) — read-only survey producing prioritized plans. Land only what is in scope for this release; everything else becomes a named follow-up, not silent work.
4. `mneves-production-readiness` — the provisional readiness assessment, when installed; otherwise the repository's documented readiness review. Fix the in-scope blockers it finds, commit ledger changes with the release, and carry the rest of its plan as named follow-ups. It never relaxes another gate; its open production blockers join the decision packet as named waivers.
5. If Phase 1 uncovers work too large for this session, use the host's native task/goal facility only when the user requests that workflow; otherwise report the remaining work. Keep it within the authorized release scope.

Gates that must be green before Phase 2: build, typecheck, lint, tests. If a gate cannot run here (needs a DB, a device, a paid service), state which one and why, and do not claim it passed. One failing gate is one named waiver in the decision packet; the release still runs every other gate.

## Phase 2 — Version, changelog, docs

- Bump the single version source of truth. SemVer: breaking → major, feature → minor, fix → patch.
- CHANGELOG: house style, one-line bullets, no prose-length hard-wrap. The released version gets today's date; open a fresh `Unreleased` heading only after the release is verified (after verification).
- Docs that describe user-visible behavior: `README.md`, `AGENTS.md`/`CLAUDE.md`, `PROJECT_STATUS.md`, `FOR_YOU_KNOW.md`. Stale docs block the release — fix before closeout.

## Phase 3 — Commit and push

Conventional Commits, atomic, explicit paths only:

Inspect push-, merge-, and tag-triggered workflows before choosing the destination ref.
If a push or merge would trigger production, push a working branch that does not trigger
production and defer the production-triggering action until the user's explicit OK for
the exact candidate and target. This boundary applies even before Phase 5.

```bash
git commit -m "chore(release): vX.Y.Z" -- <paths you touched>
git push
```

If the repo works PR-first, open the PR (`gh pr create`) and land it rather than pushing straight to the default branch. UI changes need before/after images in the PR body — sanitized.

Land the PR only when authorized and when its merge does not bypass the production approval boundary.

## Dev stop (projects with a dev environment)

When preflight found a dev environment, it is the first stop of both modes, before Phase 4. The
order is the same as staging: bind the readiness gate for `dev` on the pushed commit under the
staging rule (`mneves-production-readiness` when installed, with the same fallback as Phase 4),
deploy it, prove it live with the Phase 4 step 2 assertions and the security gate's runtime
checks, then tag it.

```bash
git tag -a vX.Y.Z-alpha<N> <commit> -m "vX.Y.Z-alpha<N> — dev; security gate: PASS" && git push origin vX.Y.Z-alpha<N>
```

`alpha` keeps SemVer order: dev before staging (`beta`) before production. `<N>` counts verified
dev builds of the target version; a failed proof gets no tag. Use `scripts/release.sh dev` only
when the repository's script supports that target; otherwise use its documented dev command.
Staging then deploys the same commit. Dev needs no separate confirmation, like staging.

## Phase 4 — Staging (`vX.Y.Z-beta<N>`)

Order: deploy the pushed commit, prove it live, then tag. A tag names bytes that were served and checked.

First bind readiness: run the readiness gate for `staging` on the exact pushed commit you will deploy (`mneves-production-readiness` when installed, otherwise the repository's documented readiness review; with neither, report the missing gate in the decision packet, where only the owner can approve `--waive readiness=<reason>`). It writes `.scratch/readiness/staging.json` in the deployable unit's directory, which `scripts/release.sh` requires (release contract guarantee 11). A `not-ready` staging verdict stops the deploy: fix, push and run the gate again.

1. **Deploy** a commit the remote already has. Use `scripts/release.sh staging` when the repository has it (it performs steps 2 and 3 itself, and may require the commit to be the tip of the default branch); otherwise the detected skill or documented command.
2. **Prove it live.** Run `scripts/verify-live.sh staging` when it exists. Otherwise assert what that script would: the served commit or version equals the candidate; the health response body has its expected fields; one request that must succeed does, and one that must be refused is. Then exercise the flow that changed with an independent browser or device driver (agent-browser, Playwright, Argent or equivalent), signed in when the change touches signed-in behavior, and read the logs for new errors. Desktop and mobile are separate targets. A green deploy command is not verification.
3. **Tag** the verified commit:

```bash
git tag -a vX.Y.Z-beta<N> <commit> -m "vX.Y.Z-beta<N> — staging; security gate: PASS" && git push origin vX.Y.Z-beta<N>
```

For `ship-prod`, then run the readiness gate for `production` on the same commit, with the same fallback. A production record never reuses the staging one; its verdict and open blockers go into the candidate presented for approval.

`<N>` starts at 1 and increments for each verified staging build of the same target version — `v2.4.0-beta1`, `-beta2`, … A staging attempt that fails its live proof gets no tag: fix, deploy again, prove again. The clean tag `vX.Y.Z` is reserved for production. Never promote an unverified build.

## Mode stop — `ship-staging`

After staging is verified, present what changed, the alpha tag (with a dev stop) and the beta tag, the dev and staging targets and evidence, and anything unverified. Then stop. Do not promote or ask a trailing production question.

## Production authorization — `ship-prod`

`ship-prod` requests preparation for production; it does not by itself authorize Phase 5. Finish Phases 1–4 (with the dev stop when the project has one), present the candidate under the Approval policy, and wait for the user's explicit OK before any production action. Do not request that approval again if it already covers the exact candidate and target. Before promotion, prove that staging is healthy and serves the exact commit being tagged for production, and that the security gate verdict for that commit and the production target is PASS or WAIVED. If `ship-prod` starts from scratch, run Phases 1–4 first. If it follows a prior `ship-staging`, re-check the deployed commit and staging health without redeploying an unchanged healthy build.

Any repository, commit, version, environment, or target mismatch invalidates the authorization: stop and present the mismatch before mutating production.

## Phase 5 — Production (`vX.Y.Z`)

Enter this phase only after the user's explicit OK for the exact candidate and production target. The production tag and its push are part of this approval boundary.

Same order as staging: deploy the commit staging serves, prove it live with the same assertions, then tag. Deploy only with a valid production readiness record for that commit. After the owner grants readiness waivers, or if the record expired while you waited, run the production gate again on the same commit so the record lists the waivers, and present any change.

```bash
git tag -a vX.Y.Z <commit> -m "vX.Y.Z; security gate: PASS" && git push origin vX.Y.Z
```

Then:

- Confirm the tag points at the commit production serves.
- Publication (GitHub Release, npm, app stores) needs its own explicit `release`/`publish` ask — a tag and a deploy are not a release. When asked: `npm view <pkg>@<version>` proves the npm side; the GitHub Release body links the npm version page, tarball, integrity, and CI proof.
- Bump the changelog to the next patch `Unreleased` and commit.
- End on the repository's expected branch, preserving unrelated changes. Switch branches only when authorized; update with a fast-forward and verify `git status -sb`.
- Close with a real narrative recap (2–5 paragraphs): what shipped and why, what the review gates caught, staging evidence, the exact tags and deploy URLs, what stayed unverified, follow-ups.

## Hard rules

- Production and VPS: never drop a DB, delete records, or run destructive commands. Verify hostname, path, and backups first. Soft-delete only.
- Secrets never appear in a tag message, changelog, PR body, or deploy log.
- Never claim a deploy, gate, or verification succeeded unless you observed it. Partial run: say exactly where it stopped.
- Abort at any phase on an unexpected repo state (dirty tree you did not create, wrong branch, foreign changes) and report rather than force through.
