# Release contract

What a deployable repository provides so that a release proves itself. `mneves-ship-deploy`
uses these entry points when they exist and names the missing ones in its preflight report.
[`scripts/release-contract-check.py`](../scripts/release-contract-check.py) reports
conformance for one repository or a folder of them.

## Entry points

| Path and arguments | Does |
|---|---|
| `scripts/release.sh <staging\|production> [--check] [--dry-run] [--waive <gate>=<reason>]... [--yes]` | The whole release for one target |
| `scripts/verify-live.sh <staging\|production>` | Read-only live assertions; exits 0 only when every one holds |

The path and the arguments are the contract. The implementation language is the repository's
choice: a two-line shell wrapper around an existing script conforms.

## What `release.sh` guarantees

1. **Pushed source.** It releases a commit the remote default branch already has, and builds
   from a clean checkout of that commit, so local edits never ship.
2. **Promotion.** `production` releases the commit staging serves right now. Any other commit
   is refused.
3. **Runtime pin.** The runtime and package-manager versions equal the repository's declared
   pin.
4. **Gates.** The repository's local gate runs inside the release. One gate is bypassed only by
   `--waive <gate>=<reason>`; every other gate still runs.
5. **Recovery point.** Before a data migration it takes an export and a recovery point, and it
   refuses destructive statements unless their own flag is passed.
6. **Target parity.** Required secrets and bindings exist on the target, and build-time values
   are the target's own.
7. **Live proof.** After the deploy, `verify-live.sh` passes for the target. On failure it
   prints the rollback command for the version it replaced, exits non-zero and creates no tag.
8. **Tag after proof.** `vX.Y.Z-betaN` once staging passes, `vX.Y.Z` once production passes.
   A pushed tag is never moved.
9. **Evidence.** It writes `release.json`: target, tag, version, commit, deployed and previous
   version ids, waivers, URL and UTC time. A prose ledger records what that file says. The
   file itself usually sits in an ignored run directory, so a committed ledger copies its
   values.
10. **`--check`** prints the plan (target, version, commit, tag, URL) and exits. It builds,
    deploys and tags nothing. It may fetch from the remote and read the live staging page.

11. **Readiness record** (contract version 2). Before building, it reads
    `<unit>/.scratch/readiness/<target>.json` (`<unit>` is `.` for a single-unit repository; see
    the format below) and
    refuses unless the record is a regular file, `schema` is 1, `unit`, `target` and the full
    `commit` match this release, `verdict` is `ready`, `open_blockers` is 0, `created_at` is not
    in the future and `valid_until` has not passed. It copies the record into the run's evidence
    and summarizes it in `release.json`. `--waive readiness=<reason>` skips the check for an
    unavailable gate or an owner-approved incident repair; control-level gaps are waived inside
    the record, never with this flag. `--check` prints the readiness status without failing.

Guarantees 1, 2, 5, 6 and 7 are fixed: no flag turns them off. `--dry-run` runs everything up
to the deploy and publishes nothing.

## Contract version

A release script states the contract it implements with a comment line
`# release-contract: 2`. Version 2 adds guarantee 11. The conformance check reports a missing
readiness check as FAIL in a script that declares version 2 and as WARN in one that declares
nothing, so existing repositories keep passing until they adopt it.

## Readiness record

A production-readiness gate run (the separately installed `mneves-production-readiness` skill, or
an equivalent review) writes the record for one deployable unit, target and candidate commit:

```json
{
  "schema": 1,
  "unit": ".",
  "target": "staging",
  "catalog": 1,
  "commit": "<full 40-character SHA>",
  "verdict": "ready",
  "open_blockers": 0,
  "created_at": "2026-10-15T19:00:00Z",
  "valid_until": "2026-10-16T19:00:00Z",
  "waivers": []
}
```

Each scalar, and each field of each waiver object, sits on its own line; every object opens with
`{` on its own line; keys are written without escapes. A shell script therefore reads the record
without a JSON parser, and it refuses a waiver whose `expires` has passed. Timestamps
are UTC in exactly the form `YYYY-MM-DDTHH:MM:SSZ` and compare as strings. The gate that writes
the record keeps `valid_until` within 24 hours of `created_at`; the release script checks only
that `created_at` is not in the future and `valid_until` has not passed. The record proves that
the gate ran for these bytes; it does not authorize a deploy, and production still needs the
owner's approval. Readiness waivers inside the record are the owner's, with expiries.

In a public repository, host names, URLs and account ids stay out of the committed scripts:
they come from an ignored file the scripts read at run time (the reference scripts read
`scripts/release.env` when it exists).

## What `verify-live.sh` asserts

- **Served commit.** Each deployed unit reports the released commit: a page through
  `<meta name="app-commit" content="...">`, an API through a `commit` field in its health
  response.
- **Health body.** The health response carries the expected fields. A 2xx status alone proves
  that something answers.
- **Two controls.** One request that must succeed with real data, and one that must be refused.
- **Wiring.** The transport or binding the design depends on, and the schedules the platform
  reports, match the configuration.

It only reads, so the same script serves three callers: the release after a deploy, a schedule
between deploys, and an agent at the start of a session.

## A waiver

A waiver names one gate and a reason a reader can check, for example
`--waive supply-chain=GHSA-xxxx has no patched release`. `release.json` records it. An
unfixable gate is one waiver request to the owner, sent as soon as it is known, together with
the candidate, the target and the rollback plan. `readiness` is a waivable gate name even though
it is not in the gate list, so a gate list may not use it.
