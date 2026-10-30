# Adopt what tstack is worth (release 1.43.0)

Status: decided 2026-10-28 in a three-round interview, built on `feat/tstack-adoption`. Map:
[map.md](map.md).

## Problem

[tstack](https://github.com/t3dotgg/tstack) (nine skills, MIT, revision `1085050f`) covers the
stretch from a finished change to a merged PR better than this repository did: proof as observed
evidence, a merge gate, bounded review loops that fight scope, PR watching, takeovers and stale
PR triage. This repository's skills were stronger on verification, security and release gates
and silent on most of that stretch. Two owner rules also lacked a home in the skills: proof in
tstack's sense, and turning Cloudflare staging off once production is live so it costs nothing.

## Decisions

1. **Planning first, then built.** The owner confirmed the destination and then said
   "implement all", so execution is carried into the map.
2. **Adopted into `skills/`, upstream names kept** (no collision found): `full-stop`,
   `takeover`, `modernize`, `leaving-pr-comments`, `babysit-pr` with `pr-wait`. Each keeps
   MIT, Theo Browne's copyright line, and a provenance note pinned to `1085050f`. Each names its
   siblings with a fallback, so a single-skill install works.
3. **Not adopted as skills:** `full-send` (it merges; merging stays the owner's), `sol-loop`
   (one named model; its loop rules are folded into `full-stop`, `council` and `autoreview`),
   `file-pr` (folded into `full-stop`, `takeover` and `mneves-ship-deploy`).
4. **`full-stop` is self-contained:** full-send's proof, merge gate and asking rules inline;
   review by any reviewer that did not build the change; never merges.
5. **"Theo → user":** tstack's skill text already says "the user"; Theo appears only in the
   copyright line, which MIT requires to stay. Shipped text says "the user"; nothing personal.
6. **T3 Code paths kept** (`watch_pull_request`, `delegate_task`) beside the Claude Code and
   Codex paths.
7. **`council` gets review mode with scores** (owner's choice over keeping it plan-only): at
   most `X` rounds (default 3, cap 10), early stop when every member answers SHIP IT, a score
   out of 10 per member per round (`no score`, never invented), the table in the PR description.
   Reaching the cap is not approval. **pi replaces Cursor** as the third adapter.
8. **Proof** (glossary term) goes into every skill that claims done, fixed or shipped, adapted to
   each skill; PRs carry one line on how the change was proved.
9. **`modernize` says "recommendation"**, because the glossary reserves "disposition" for
   security findings. **Merge gate** is a glossary term.
10. **One release, 1.43.0**, one branch with a commit per unit, stacked on PR #29 (1.42.0).

## GitHub billing failures

Owner rule: when GitHub's billing blocks CI, ignore CI and prove the change locally. Evidence
(read-only API calls on public repositories, 2026-10-28; GitHub documents neither string):

- A billing-blocked job is a check run with `conclusion: FAILURE`, no steps, `runner_id: 0`, and
  a failure-level annotation: "The job was not started because your account is locked due to a
  billing issue." or "The job was not started because recent account payments have failed or
  your spending limit needs to be increased. …".
- `gh pr checks` shows it as an ordinary failure (`bucket: fail`, empty description).

Built as: `pr-wait` reads the head commit's check-run annotations when a gating check fails and
reports a check whose failure annotation starts "The job was not started because" and names
billing, failed payments or the spending limit as billing-blocked, not failed. The skills that
gate on CI (`full-stop`, `babysit-pr`, `modernize`, `mneves-ship-deploy`) skip such a check, run
the same checks locally, and say that CI was skipped and why. Unverified: organization-level
wording, and whether every billing block carries the annotation.

## Staging off after production

Owner rule: staging must cost nothing while no release is in it. Evidence from Cloudflare's
documentation (2026-10-28):

- An environment without its own `triggers` inherits the top-level crons; `"crons": []` in
  `env.staging` plus a deploy removes them (propagation up to 15 minutes); the schedules API
  (`GET /accounts/{account_id}/workers/scripts/{script}/schedules`) reads them back.
- A deploy does not detach a queue consumer: `wrangler queues consumer remove <queue> <script>`
  does, and `wrangler queues consumer list <queue>` proves it.
- Workflows: `wrangler workflows instances list <name> --status running`; a scheduled
  Workflow is removed with `wrangler workflows delete <name>`.
- Durable Object alarms cannot be listed or cancelled from outside the object: only code
  (`deleteAlarm()`) turns them off, so an external check is NOT TESTED.
- D1: `wrangler d1 info <name> --json` (uuid, `write_queries_24h`, `rows_written_24h`),
  `wrangler d1 export <name> --remote --output=<file>`, `wrangler d1 delete <name>`.
  `d1AnalyticsAdaptiveGroups` (`sum { writeQueries rowsWritten }` by `databaseId`) proves zero
  writes; no documented dataset isolates cron runs.

Built as: the general rule in `mneves-ship-deploy`, the Cloudflare procedure in its
`references/cloudflare.md`, `cf.env-triggers` raised from WARN to FAIL when a staging
environment inherits or declares crons, and an advisory CST control in
`mneves-production-readiness`. The staging D1 database is exported and deleted by the agent,
under the user's standing or explicit authorization for that deletion (`mneves-ship-deploy`
requires it), when it is unused: it holds nothing production lacks, no release is in staging, and its name and
uuid are confirmed as staging's. Otherwise it is reported for the owner. The next release
recreates it before its staging stop.

## Out of scope

`collections/pstack`, third-party skills installed on the owner's hosts, installing the new
skills into agent folders (outside the repository), and skills no tstack lesson touches.
