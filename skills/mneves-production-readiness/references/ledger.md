# Ledger, record, evidence and plan

## Statuses

| Status | Meaning |
|---|---|
| PASS | The control's check succeeded at or above its minimum evidence scope. |
| FAIL | Observed behaviour or configuration violates the control. |
| BLOCKED | Access, an environment, a determination or an independent check is missing. |
| NOT TESTED | No adequate check ran; say what proof is missing. |
| NOT APPLICABLE | Evidence shows the control does not apply; cite it. |
| WAIVED | A named owner accepted the gap until a date; the underlying result stays visible. |

A merged control passes only when every applicable sub-check in its `Verify` line passes; the
evidence names each one.

When the place the mechanism would live is in the repository and it is absent (no backup job in
the infrastructure code that defines the database), the row is FAIL. When the evidence would
live outside the repository (a provider console, an on-call tool), the row is NOT TESTED until an
owner attests or a read-only check reaches it.

## Evidence

Scopes, from weakest: **source** (files read), **local** (run on a developer machine or CI),
**staging**, **production**; **owner-attested** is separate (a dated statement from a named owner,
saying where the proof lives). A row cannot PASS below its control's minimum scope. Evidence
cites a `path:line`, a command with its exit status, an attestation (who, when, where stored) or
a URL. "Looks fine" is not evidence. Never paste secret values, tokens or personal records; cite
their location and type.

## Ledger

Tracked Markdown, the canonical record of control status. Default path
`docs/readiness/ledger.md`; in a repository with several deployable units, one ledger per unit
beside the unit's release scripts. Derive every other summary from it.

```markdown
# Production readiness ledger

Schema: 1 · Catalog: 3 · Unit: . · Stage: live · Visibility: private
Profile: db (prisma/schema.prisma), accounts (src/auth/), payments (stripe in package.json), email, jobs
Regulated: card payments → CMP-05; EU personal data → CMP-06; EU consumer accessibility → BLOCKED, needs determination (owner)
Contracts: none
Cursors: staging 1a2b3c4 (2026-10-15) · production 1a2b3c4 (2026-10-15)
Baseline: 2026-10-15 at 1a2b3c4 · maximum age 90 days
Owners: review @lead · data @lead · delivery and cost @ops · on-call @ops, backup @lead · security patching @lead · compliance @founder · testing @lead · scope @founder · architecture @lead · memory @lead

| ID | Status | Tier | Evidence (scope, date, commit) | Owner | Next action or waiver |
|---|---|---|---|---|---|
| DM-02 | PASS | blocker | local: up and down run for `db/migrations/0012` (2026-10-15, 1a2b3c4) | @lead | — |
| BR-02 | WAIVED | blocker | none yet | @ops | waiver @founder, production: first drill booked; expires 2026-11-14 |

## Gate history

| Date | Target | Commit | Verdict | Open blockers | Waivers |
|---|---|---|---|---|---|
```

Rules:

- One row per control in the catalog, including NOT APPLICABLE rows with their evidence.
  Retired controls stay with status "retired".
- Project-local controls added after incidents use `LOCAL-nn` with the same fields.
- One person may hold several seats. Owners are handles or roles; never contact details in a
  public repository.
- In a public repository, a security-sensitive FAIL row says "restricted" and keeps its details in
  the ignored `.scratch/readiness/` directory or a private tracker.
- Update the cursor for a target only after a binding run for that target.

## Record

The record lets a release script confirm that a binding gate run happened for this exact
candidate. It is a precondition, not an authorization: production still needs the owner's
approval. Write it only at the end of a binding run.

Path: `<unit>/.scratch/readiness/<target>.json`, where `<unit>` is the deployable unit's
directory (`.`, the repository root, for a single-unit repository); the repository ignores
`.scratch/`. JSON with exactly these keys at the top level, including the waivers array:

```json
{
  "schema": 1,
  "unit": ".",
  "target": "production",
  "catalog": 3,
  "commit": "0123456789abcdef0123456789abcdef01234567",
  "verdict": "ready",
  "open_blockers": 0,
  "created_at": "2026-10-15T19:00:00Z",
  "valid_until": "2026-10-16T19:00:00Z",
  "waivers": [
    {
      "control": "BR-02",
      "owner": "@founder",
      "reason": "first drill booked",
      "expires": "2026-11-14T00:00:00Z"
    }
  ]
}
```

- `unit` is `.` or the unit's path relative to the repository root; `target` is `dev`,
  `staging` or `production`; `commit` is the full 40-character SHA of the candidate.
- `open_blockers` counts the rows that block under the target's gate rule (for dev and
  staging, the FAIL rows in the staging set) plus every open blocker of the imported security
  gate record for the same commit and target. `verdict` is `ready` exactly when it is 0; waived
  rows are not open.
- Timestamps are UTC in exactly the form `YYYY-MM-DDTHH:MM:SSZ`, so they compare as strings.
- `valid_until` is the earliest of `created_at` plus 24 hours, any waiver expiry and any
  relied-upon evidence expiry.
- A waiver object holds exactly `control`, `owner`, `reason` and `expires`; the record's unit,
  target and commit are its scope, so it never repeats them.
- Release scripts parse the record as JSON, refuse unknown or repeated keys and incomplete
  waivers, refuse an expired waiver, and copy the record into the release evidence.

## Plan

Write one entry per change that closes gaps: every FAIL, BLOCKED or NOT TESTED row in an
applicable `blocker` or active `contract` control, then the advisory items worth doing. One
change may close several rows; list every ID it closes, and end the plan with an index that maps
each open ID to its entry. Each entry has:

- ID, title, status and evidence; the failure it prevents.
- Change: the files or resources, as ordered steps.
- Owner type: code, database, infrastructure or provider, finance or legal, people or process.
- Size: quick fix (under a day), change, or feature (a ticket in the project's tracker).
- Dependencies on other IDs.
- Acceptance: the check that turns the row PASS, at its minimum scope.
- Rollout and recovery: how to ship it safely and undo it.
- Mechanical gate: the line to add to the repository's gates when the check is automatable.

Order blockers by failure class: data loss, then exposure, then wrong money, then undetected
outage, then unrecoverable change. Put dependencies before dependents, then `contract`, then
`advisory`.
