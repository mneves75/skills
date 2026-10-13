# Evidence and report contract

Use the user's language and requested artifact format. Return these eight sections,
with concrete file/symbol/route/policy evidence and redacted diagnostics. Keep small
reports compact without dropping sections or silently replacing missing proof with PASS.

## Finding records

Assign stable IDs. For each record capture:

- Severity: Critical, High, Medium, Low or Informational. Explain affected assets,
  plausible exploit path/preconditions and impact; do not inflate absent features.
- Confidence: High, Medium or Low, separate from severity. State what establishes
  or would falsify the finding. Unconfirmed hypotheses remain investigate items.
- Area, actual path/line and symbol/route/policy, observed behavior, relevant current
  standard/control, evidence scope and source. Do not invent an identifier or line.
- Proposed fix, owner/dependencies, implementation risk, rollback and acceptance test.
- Fix state and verification state, with exact commands/outcomes and environment.

Fix states are proposed, confirmed, fixed-and-verified, awaiting-application,
manual-action, blocked, disproved or waived. A policy file can be fixed locally while
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

## 1. Executive summary

State overall risk and confidence, assessed scope and limitations, highest risks,
verified fixes and manual actions. Give a reasoned launch-readiness assessment from
confirmed impact and unresolved evidence; do not equate “audit complete” with “safe.”
Name explicit blockers and separate observed vulnerability from unknown provider state.

## 2. Project inventory

Stack/runtime/package manager, confirmed auth/database/provider relationships, data
locations/flows and sensitive entry points. Separate facts from assumptions. Include
source/package coverage (inventoried, inspected, tested), exclusions and unread or
unavailable surfaces; list selected official baseline editions/profile and source dates.

## 3. Findings table

Required columns, extended by confidence:

| ID | Severity | Confidence | Area | Evidence | Risk | Fix status | Verification |
|---|---|---|---|---|---|---|---|

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

Evidence scope is essential: source-only or local checks cannot mark live provider
policies, billing caps, monitoring or deployed headers Yes. Preserve useful technical
progress while accurately reporting the remaining launch gate.
