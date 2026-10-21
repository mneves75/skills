# Evidence and report contract

Use the user's language and requested artifact format. Return these eight sections,
with concrete file/symbol/route/policy evidence and redacted diagnostics. Keep small
reports compact without dropping sections or silently replacing missing proof with PASS.

## Finding records

Assign stable IDs. For each record capture:

- Disposition: confirmed, needs-validation or disproved (SKILL.md step 3). A confirmed
  record names the six boundary elements and what would falsify it. A needs-validation
  record names the missing fact, the safe check that resolves it and its owner. A
  disproved record names the evidence that refuted it and the assumptions that evidence
  rests on (source, provider policy, identity, dependency versions, topology).
- Severity: Critical, High, Medium, Low or Informational, for confirmed records only, per
  the SKILL.md anchors; `-` otherwise.
- Area, actual path/line and symbol/route/policy, observed behavior, relevant current
  standard/control, evidence scope and source. Do not invent an identifier or line.
- Proposed fix, owner/dependencies, implementation risk, rollback and acceptance test.
- Fix state and verification state, with exact commands/outcomes and environment.

The fix state tracks remediation of a confirmed finding, separately from its disposition:
proposed, fixed-and-verified, awaiting-application, manual-action, blocked or waived. A policy file can be fixed locally while
application to its provider remains awaiting-application. Keep both scopes explicit.
A waiver names its owner, scope, reason and expiry; it does not turn a failed check
into PASS or permit an unapproved release.

## Verification status

| Status | Meaning |
|---|---|
| PASS | The named criterion was actually satisfied at the stated surface/environment. |
| FAIL | Observed behavior violates the named criterion. |
| BLOCKED | A necessary permission, independent capability, access or environment is unavailable. |
| NOT TESTED | No adequate check was run; state the missing proof. |
| NOT APPLICABLE | Source inventory supports why the control does not apply. |
| WAIVED | A named owner accepted a specific gap; the underlying result stays visible. |

Independent acceptance requires a fresh context and, for security work, a different
model from the builder. Record builder/verifier identity and scope. If unavailable,
block independent acceptance and overall assurance, not delivery of useful findings.
Keep task completion, security readiness and launch approval as separate conclusions.

## Gate verdict record

In deploy-gate mode, write the report to `<unit>/.scratch/security-gate/<commit>/<target>.md`
and this record next to it as `<target>.json`, where `<unit>` is the deployable unit's
directory (`.` for a single-unit repository) and `<commit>` the full SHA of the deployed
commit. One folder per commit keeps earlier verdicts for reuse and rollback; when another
commit with the same tree deploys (a merge or squash), copy the record to its folder with
`reused_from` set. Confirm with `git check-ignore` that the
path is ignored; if it is not, write both to the release's evidence location and say
where. Never commit them into the candidate: that would change the audited commit. Keep
them: they prove reuse and rollbacks, so no cleanup routine may delete them.

```json
{
  "schema": 1,
  "unit": ".",
  "target": "production",
  "commit": "<full 40-character SHA>",
  "tree": "<full 40-character tree hash>",
  "verdict": "waived",
  "open_blockers": 0,
  "blockers": "",
  "independent_acceptance": "pass",
  "reused_from": "",
  "created_at": "2026-10-15T19:00:00Z",
  "waivers": [
    {
      "id": "SEC-19",
      "owner": "@owner",
      "reason": "penetration test booked",
      "expires": "2026-11-30T00:00:00Z"
    }
  ]
}
```

- `target` is `dev`, `staging` or `production`; `verdict` is `pass`, `block` or `waived`.
- `open_blockers` counts blocks with no fix, disproof or waiver; `verdict` is `block`
  exactly when it is above 0, and `waived` when it is 0 but `waivers` is not empty.
- `blockers` lists the open blocks' IDs, separated by spaces, so the decision packet can
  name each one; it is empty when `open_blockers` is 0.
- `independent_acceptance` is `pass`, `fail` or `blocked`. For production only `pass` allows
  a `pass` verdict; on dev and staging a `blocked` value is a plan item, not a block.
- `tree` is the audited tree hash; `commit`'s tree must equal it.
- `reused_from` names the commit whose full audit this run reused, or stays empty.
- Each scalar and each waiver field sits on its own line, every object opens with `{` on
  its own line, keys carry no escapes, and timestamps are UTC `YYYY-MM-DDTHH:MM:SSZ`, so a
  shell script can read the record without a JSON parser. A waiver's `id` is a finding ID,
  a launch-control ID, or `gate:<part>` for a gate step (`gate:independent-acceptance`,
  `gate:audit` for an urgent fix deployed before its audit). The record's commit and
  target are the waiver's scope, so a waiver object never repeats them.

## 1. Executive summary

State overall risk and the evidence behind it, assessed scope and limitations, highest risks,
verified fixes and manual actions. Give a reasoned launch-readiness assessment from
confirmed impact and unresolved evidence; do not equate “audit complete” with “safe.”
Name explicit blockers and separate observed vulnerability from unknown provider state.
In deploy-gate mode, open with the verdict, candidate (commit, version, unit), target,
whether the audit was full or reused, open blockers and the waivers requested.

## 2. Project inventory

Stack/runtime/package manager, confirmed auth/database/provider relationships, data
locations/flows and sensitive entry points. Separate facts from assumptions. Include
source/package coverage (inventoried, inspected, tested), exclusions and unread or
unavailable surfaces; list selected official baseline editions/profile and source dates.

## 3. Findings table

Required columns, extended by disposition:

| ID | Disposition | Severity | Area | Evidence | Risk | Fix status | Verification |
|---|---|---|---|---|---|---|---|

Fix status is `-` for needs-validation and disproved rows. List needs-validation records
after the confirmed ones, each with its missing fact and resolving check, and disproved candidates
last, with the evidence that refuted them.

Use one record per distinct finding. Link longer reproduction/control details below
the row when needed. If there are zero confirmed findings, say so without manufacturing
issues; unresolved hypotheses and unavailable checks remain visible.

## 4. Remediation plan

Ordered steps by risk/dependency. Each step names its finding ID, exact code/resource
scope, proposed control, owner type (code, database, cloud/provider, legal/content or
manual QA), prerequisites, acceptance command/check, implementation risk and rollback.
Split automatic safe fixes from migrations/policies awaiting application and operator
actions. Manual actions specify where/what to change and what redacted proof to return,
without assuming dashboard availability, schema, domain, region or provider settings.

## 5. Changes implemented

List actual files, purpose and affected behavior; policies/migrations/tests/config added.
State what was only drafted, executed locally, applied to staging or verified in production.
Audit-only mode says no project files changed. No edit is a “fixed” claim by itself.

## 6. Verification results

Exact commands and exit outcomes, tests added/updated, allowed/denied controls, scanner
scope/version/diagnostics and concrete manual checks. Separate pre-existing failures,
missing setup and regressions introduced by the patch. Include independent/adversarial
verdicts and corrections, standard citations and unresolved manual/runtime checks.

## 7. Residual risk

Unfixed or waived findings, unavailable schema/access/env/provider state, legal review
and runtime limits. Explicit launch blockers have owners and release conditions. Avoid
blanket clearance, certification or “100% secure”; define what evidence would reduce
the remaining uncertainty. Do not disguise an owner decision as a passing technical check.

## 8. Launch security checklist

One row per subject below. Use **Yes** only for adequate, current evidence at the required
environment; **No** for unmet applicable controls; **N/A** only with a reason. Add the
verification status, evidence/environment, owner and next action. A blocked or untested
applicable control is No with its precise status, not Yes. Do not force N/A into a false
Yes/No verdict.

| Subject | Answer | Status | Evidence / environment | Owner / action |
|---|---|---|---|---|
| Privacy policy / user-facing disclosure | | | | |
| Data map / retention / deletion / export | | | | |
| RLS / equivalent object and tenant access control | | | | |
| Server-side validation | | | | |
| Auth failure / session tests | | | | |
| Security headers / cookies / cache | | | | |
| Applicable OWASP risks and coverage | | | | |
| Secrets / sensitive-data leaks | | | | |
| Public versus secret API keys / paid proxy protection | | | | |
| Rate limits / resource bounds | | | | |
| CAPTCHA / Turnstile / appropriate bot controls | | | | |
| CORS / CSRF where applicable | | | | |
| Safe errors / redacted logs | | | | |
| Dependency / security scanner results | | | | |
| Billing caps / alerts | | | | |
| Monitoring / incident ownership | | | | |

In deploy-gate mode, or when launch readiness was asked, add one row per applicable
launch control (`SEC-01` to `SEC-23`, `CMP-01` to `CMP-09`) with the same columns, and list
the not-applicable controls once with their reasons.

Evidence scope is essential: source-only or local checks cannot mark live provider
policies, billing caps, monitoring or deployed headers Yes. In deploy-gate mode,
configuration evidence meets a `runtime` launch control only provisionally, before the
deploy; the row stays pending until the live check passes. Preserve useful technical
progress while accurately reporting the remaining launch gate.
