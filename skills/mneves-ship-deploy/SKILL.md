---
name: mneves-ship-deploy
description: "Use for `ship-staging`, `ship-prod`, or an explicit staging/production deployment request for a project you own. Plain `ship` does not invoke this skill or authorize external writes."
license: Apache-2.0
compatibility: The procedure needs only Git. The optional contract check (`scripts/release-contract-check.py`) needs Python 3.11+. The reference release scripts in `assets/` need bash 3.2+, git, curl, sed, awk, python3 and the Wrangler version the project pins.
---

# Ship Staging / Prod

The release closeout chain for projects the user owns has two explicit modes:

- **`ship-staging`**: runs through a verified staging deploy (after a verified dev deploy when the project has one) and stops before production.
- **`ship-prod`**: prepares and verifies dev (when present) and staging, then waits for explicit owner OK on the exact candidate and production target before any production action.

Plain `ship` has no special meaning and grants no release, deploy, push, or pull authority.

Prefer the installed review and deployment skills named below. They are optional integrations: if one is unavailable, use the repository's documented equivalent while preserving gates, authority boundaries, and evidence; if none exists, report the missing capability and stop that phase. The Phase 1 security gate (`mneves-security`) is the exception — it has no substitute.

## Approval policy

- **Dev and staging are authorized:** run authorized reviews, apply verified in-scope fixes, complete required gates, and deploy to established dev/staging targets without redundant confirmation. `ship-staging` still stops before production.
- **Production always waits for explicit OK:** before any production tag, deploying merge/push, or promotion, present the exact repository, commit, version, production target, staging evidence, material risks, persistent-state rollback limits, and rollback plan. Wait for explicit approval of that exact candidate and target (`ship-prod` alone does not grant it; do not re-ask if already approved for the exact candidate and target).
- **`autoreview`** is a review gate, not human approval: follow its disclosure/secret-scanning/isolation controls without redundant prompts once authorized.
- Staging authorization never waives required gates or authorizes destructive operations, credential access (reading, printing, copying, or reusing any secret, including credentials in configured deploy bindings), separate publication (npm/store/GitHub Release), or an unspecified target.
- **One decision packet:** turn any failing or unrunnable gate into one request sent as soon as known (candidate identity, target, each failing gate as a named waiver with reason, security gate verdict, and rollback plan) while continuing all other gates. Approval covers only the waivers it lists.

## Do not invoke when

- The user only said "ship", "commit", "push", or "land the PR" without naming staging/production.
- The repo is not owned by the user, or the working tree is on another branch or holds unknown foreign edits → report and stop.

## Preflight (always)

```bash
git status -sb && git log --oneline -5 && git branch --show-current
```

Establish and report these seven findings in one short paragraph before any mutating step:

1. **Mode** — `ship-staging` or `ship-prod` from the explicit target in the request.
2. **Repo identity** — remote, default branch, owner confirmation, and push/merge/tag deploy triggers.
3. **Version source of truth** — pick one (`VERSION`, `package.json`, `app.json`/`app.config.ts`, `Cargo.toml`, `pyproject.toml`); never drift two.
4. **Deploy target** — detect from repo config:
   | Signal | Deploy via |
   |---|---|
   | `vercel.json`, `.vercel/` | `deploy-to-vercel` or repo's documented Vercel command |
   | `wrangler.toml` / `wrangler.jsonc` | `cloudflare-deploy` or documented Cloudflare command; read [references/cloudflare.md](references/cloudflare.md) first |
   | `eas.json` + Expo app | `eas-app-stores` or documented store workflow (staging = TestFlight / internal track) |
   | `docker-compose.yml`, deploy script, VPS host | repo's deploy script (`vps-setup` only when authorized); read [references/vps.md](references/vps.md) first |
5. **Staging (and optional dev) environment** — staging is required for both modes; if none exists, ask whether `ship-staging` should run beta-tag-only (never skip or invent a URL). Use dev first only when documented.
6. **Release contract** — if `scripts/release.sh` and `scripts/verify-live.sh` exist, start with `scripts/release.sh <target> --check`. Run `python3 <skill folder>/scripts/release-contract-check.py <repo>` when Python 3.11+ is available and report each `FAIL`. Read [references/release-contract.md](references/release-contract.md) if missing or failing.
7. **Readiness ledger** — inspect `docs/readiness/ledger.md` (or repo's documented path): stage, baseline age, and last assessed commit per target.

## Release phases

Read [references/phases.md](references/phases.md) for the exact step checklists, tag formats, live-proof assertions, and staging teardown rules. Summary of the mandatory order:

1. **Phase 1 — Review gates:** `autoreview` (bounded: 1 review + 1 rerun) → `improve` deep pass on feature/structural releases → provisional `mneves-production-readiness` → green build/typecheck/lint/tests → **final `mneves-security` deploy gate** bound by exact tree hash after all code/doc/version changes land.
2. **Phase 2 & 3 — Version, changelog, docs, commit & push:** bump single version, update `CHANGELOG.md` and user-visible docs, inspect merge/push deploy triggers first (use a non-deploying branch if pushing/merging triggers production), commit atomically with explicit paths, and satisfy the latest-head PR merge gate without bypass flags.
3. **Dev stop (when documented):** bind `dev` readiness → deploy → prove live → tag `vX.Y.Z-alpha<N>`.
4. **Phase 4 — Staging (`vX.Y.Z-beta<N>`):** bind `staging` readiness (`.scratch/readiness/<commit>/staging.json`) → deploy pushed commit → prove live (served commit/artifact identity, health fields, positive + negative request after confirming preview/staging writable bindings, independent browser/device driver on changed flows, clean logs; active observation windows stay pending, not failed) → tag `vX.Y.Z-beta<N>` with security verdict. Verify zero staging cron schedules.
   - **`ship-staging` stops here:** report changes, tags, staging evidence, and anything unverified; do not ask a trailing production question.
   - **`ship-prod` continues preparation:** bind `production` readiness (`.scratch/readiness/<commit>/production.json` with `independent_acceptance: "pass"`), verify persistent-state rollback limits (DB/KV/R2/DO migrations vs code rollback), and present the production candidate for explicit OK.
5. **Phase 5 — Production (`vX.Y.Z`):** enter only after explicit OK for the exact candidate and target (any mismatch invalidates approval). Immediately before promoting, re-confirm the exact commit staging serves, verify staging is still healthy (reusing an unchanged healthy staging deploy), and confirm valid production security/readiness verdicts. Deploy that exact commit to production, prove live (completing any required observation window before tagging), tag `vX.Y.Z`, confirm tag matches served bytes, **turn staging off** cleanly as a separate reversible step (zero scheduled runs, zero writes; export staging DB before authorized delete; see [references/cloudflare.md](references/cloudflare.md#staging-off-after-production) on Cloudflare), open next `Unreleased` heading, restore expected branch, and deliver a concise narrative recap. Separate publication (GitHub Release, npm, stores) requires its own explicit request.

## Hard rules

- Production and VPS: never drop a DB, delete records, or run destructive commands; soft-delete only. The unused staging database and staging workflows in Phase 5 are the only deletions this skill performs, and only after explicit authorization and identity verification (database export-first).
- Secrets never appear in tag messages, changelogs, PR bodies, or deploy logs.
- Never claim a deploy, gate, or verification passed unless observed; on a partial run, state exactly where it stopped.
- Abort immediately on unexpected repo state (foreign dirty tree, wrong branch) and report rather than forcing through.
