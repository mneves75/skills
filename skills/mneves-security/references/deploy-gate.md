# Deploy gate and reproduction rules

## Deploy gate protocol

Run this mode before every deployment of an application, service, site or app build to a
dev stop, staging or production, whatever starts it: a release command or script, a CI
job, a push, merge or tag that deploys, a TestFlight or internal-track upload, an
over-the-air update, or a store submission. Staging is any shared pre-production
environment; a per-branch preview counts when the project uses it as staging or it can
reach shared data or real users. A dev stop is the first target of a release chain that
goes dev, staging, production. No deploy receives a pass without a verdict for its exact
commit and target.

1. **Freeze the candidate.** Run the gate after every other release change, version and
   documentation included, has landed, so it audits the final content. Record the
   repository, version, unit, target and the audited tree hash (`git rev-parse
   HEAD^{tree}` for committed content, `git write-tree` for staged content). The verdict
   binds to every commit whose tree equals that hash, so a merge or squash that keeps the
   tree keeps the verdict; record each deployed commit before any push, merge or tag that
   deploys it. Any change to the tree, this gate's own fixes included, makes a new
   candidate with a new full audit.
2. **Audit in full.** Run Execution steps 1 to 4 over the candidate's entire first-party
   source: all twelve audit areas and every applicable launch control (`SEC-01`–`SEC-23`,
   `CMP-01`–`CMP-09`). Mark each finding as introduced since the last gated release or
   pre-existing. Apply only the fixes the release task authorizes (Execution step 5); the
   rest goes into the plan.
3. **Review independently** as in Execution step 6. Production needs independent
   acceptance from a fresh context using a different model from the builder. On dev and
   staging, an unavailable reviewer is recorded as `gate:independent-acceptance` in the
   plan and does not block.
4. **Decide.**
   - **Every target blocks** while a confirmed Critical or High finding is open, or an
     area's source could not be inspected.
   - **Production also blocks** while an applicable launch control is not `Yes` or
     independent acceptance has not passed.
   - Before a deploy, configuration evidence meets a `runtime` control provisionally (for
     production, so does the same tree's runtime evidence from an earlier target); the
     live check after the deploy decides it.
   - A fix, disproving evidence, or the owner's named waiver (owner, reason, expiry) in
     the release decision packet clears a block. Waivers make the verdict `WAIVED`; no
     block makes it `PASS`.
   - Medium and lower findings, and launch-control gaps on dev and staging, go into the
     plan.
   - `needs-validation` records never block by themselves; the decision packet lists each
     with its missing fact and resolving check. A fact that an applicable production
     launch control or independent acceptance depends on leaves that prerequisite
     `BLOCKED` or `NOT TESTED`, never `Yes`, so production still blocks through it.
5. **Record.** Write the verdict record (`<target>.json`) and report (`<target>.md`)
   outside the tracked tree per the report contract. Runtime checks (headers, cookies,
   CORS, TLS) belong in the project's live proof (`scripts/verify-live.sh` when present),
   so they run after each deploy and before any tag. A failure there fails the release:
   no tag, then fix forward or roll back by the release procedure. Each release tag's
   message records the verdict (`security gate: PASS`, or `WAIVED` with the waived IDs).

## Reuse, rollbacks and urgent fixes

- **One full audit per tree.** A later target for the same tree (dev -> staging ->
  production) reuses it: re-read advisories, assess the launch controls whose evidence
  depends on that target's environment, and run its runtime checks.
- **Rollbacks** need no new audit when the build passed the gate for that target: its
  release tag message records a `PASS` or `WAIVED` verdict, or a gate record names its
  commit. A tag whose message lacks the verdict proves nothing. Any other build,
  including one released before the gate existed, needs the owner's named waiver.
- **Urgent fixes** may deploy under the owner's named waiver (`gate:audit`). Its full
  audit runs right after the deploy. A Critical or High finding there is the next fix, or
  the owner decides to roll back.
- **Privacy:** Reports and verdict records stay private. Public PRs, issues, tags,
  changelogs or release notes cite only the verdict and finding IDs, never open
  vulnerability details.

## Reproduction, sandboxing and scanner hygiene

- **Local minimal reproduction:** Use the project's own test, build and dev commands with
  dummy principals and fixtures; stop at the first observable boundary result (wrong
  response, unauthorized dummy record, sanitizer report). Never probe deployed, shared or
  third-party systems beyond authorized live release checks, and never attempt
  availability attacks, persistence or real user data.
- **Untrusted target code:** Run third-party or otherwise untrusted code only in a
  sandbox with no external network, an allowlisted environment, writes confined to a
  scratch directory, resource limits and no dependency installs or fetches during the
  build; without one, keep the candidate `needs-validation` and provide the safe check.
- **Scanners and leak reports:** Run applicable dependency/secret/security scanners
  within permitted scope and review their version, config, coverage, diagnostics and
  exit status; empty or partial scans cannot `PASS`. Never print raw secret values; emit
  path/line and credential type only. A frontend env prefix alone does not prove a secret
  leak, and rotation remains an authorized operator action.
- **Optional complexity evidence (`cccc`):** For supported changed source, installed
  `cccc` is optional complexity evidence: preserve owning config/exclusions, run
  `cccc --no-cache --min 0` on focused files, and report version, expected/analyzed
  files, diagnostics and exit status. Unsupported or missing metrics never imply
  correctness.
