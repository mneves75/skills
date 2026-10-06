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
   version ids, waivers, URL and UTC time. Prose ledgers link to that file.
10. **`--check`** prints the plan (target, version, commit, tag, URL) and exits before any
    build or deploy. It may read the remote and the live staging page; it writes nothing.

Guarantees 1, 2, 5, 6 and 7 are fixed: no flag turns them off. `--dry-run` runs everything up
to the deploy and publishes nothing.

In a public repository, host names, URLs and account ids come from an ignored environment
file or private configuration that the scripts read at run time, never from constants
committed in the scripts.

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
the candidate, the target and the rollback plan.
