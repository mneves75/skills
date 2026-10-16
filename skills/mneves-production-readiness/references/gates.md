# Gates, profile and freshness

Catalog version: **1**. Read this before deciding scope or a verdict.

## Profile

Derive each flag from evidence (path, symbol, configuration or dependency) and record that
evidence in the ledger header. A flag without evidence is unset. A set flag makes its controls
applicable; one of them is NOT APPLICABLE only when the specific surface it checks is absent (a
user interface without forms gives UX-04 nothing to check), with that evidence cited.

| Flag | Typical evidence |
|---|---|
| `db` | migrations, ORM models, database client, connection variable names |
| `accounts` | auth library, sessions, user tables, login routes |
| `multi-tenant` | organization, workspace or tenant keys on shared tables |
| `payments`, `subscriptions`, `metered` | payment provider SDK or variables, checkout, plans, usage reporting |
| `email`, `marketing-email` | email provider SDK, templates, lists or campaigns |
| `jobs` | queues, workers, schedulers, cron configuration |
| `webhooks`, `public-api`, `oauth` | inbound webhook routes; documented external API or API keys; third-party OAuth clients |
| `ai` | model provider SDKs, prompts, retrieval code |
| `uploads`, `ui`, `i18n`, `multi-service` | upload handlers; a user interface; locale files; more than one deployable service |

**Regulated applicability is derived, never declared.** Health data (`phi`), card payments
(under `payments`), personal data of people in jurisdictions with privacy law, consumer
services in markets with accessibility law, and sales in taxing jurisdictions follow from the
data, activities and markets the product serves: currencies, locales, shipping or billing
countries, terms, data fields. When the evidence cannot settle a material question (which
markets, whether health data is stored), mark the affected rows BLOCKED with "needs
determination" and name who decides. Do not mark them N/A.

**Contracts are declared.** The owner lists contractual commitments in the ledger header: `sso`,
`scim`, `mfa`, `sla`, `residency`, `soc2`, `pentest`, `audit`, `retention`, `accessibility`,
`b2b-invoicing`, `custom-contracts`, `sandbox`, `enterprise`, `access-review`. A `contract`-tier
control blocks only when its contract is listed or a regulation makes it applicable.

**Stage.** `prototype` when the repository instructions or the owner state that no real users,
data or charges exist; otherwise `live`. **Launch** is the first time real users, customer data
or charges enter the system: a deploy, opening signups, switching payment keys to live mode or
importing customer data. Run the production gate in its `live` form before the launch action,
even when no code deploys.

**Stake.** A product has stake when it stores customer data (records, accounts, uploaded files
or contact lists: `db`, `accounts`, `uploads` or `marketing-email`), takes money (`payments`) or
carries a declared availability promise (`sla`). Controls that apply to "`live`
with stake" (on-call, recovery plans, paging, load tests and similar) are advisory for a live
product without stake, such as a static brochure site.

## Tiers

- `blocker`: failure loses, corrupts or exposes data or money, or leaves an outage undetected or
  unrecoverable.
- `contract`: a blocker only when a declared contract or derived regulation requires it.
- `advisory`: planned work that never blocks.

## Assessment lifecycle

1. **Baseline**: every applicable control. Required when no ledger exists, the baseline is older
   than its maximum age, the catalog version changed, the stage changes to `live`, or the delta
   cannot be computed.
2. **Provisional** (a release's review phase): assess the working tree against the target's
   cursor and write the plan; the release workflow fixes what its own authority covers and
   commits ledger changes with the release.
3. **Binding gate run**, once per target, on the exact candidate (already pushed when the
   repository has a remote): assess the delta from the target's cursor to the candidate plus the
   always-on set, then write the record. A production record always comes from its own run,
   never from renaming a staging record. In a repository that releases the default-branch tip,
   the candidate is the landed commit, so the binding run follows landing.

A production binding run with open blockers produces the decision packet, not a deployable
record. When the owner grants waivers there, or a record expires while waiting, run the binding
gate again on the same commit; it lists the waivers and writes the record.

The binding run also updates the target's cursor and gate history in the ledger. That
bookkeeping does not change the deployed bytes, so the record keeps the candidate's SHA and the
tracked change waits for the next commit. A delta that contains only ledger changes reassesses
only the always-on set.

Before writing a record, confirm that its path is ignored (`git check-ignore`). If it is not,
report that the repository must ignore `.scratch/` (the release contract requires it) and do not
write the record.

## Delta

- Each target has a cursor in the ledger header: the last commit assessed for that target.
- If the cursor is an ancestor of the candidate, the delta is the changed paths between them.
  If not (rebase, force push, shallow history), use the paths changed since the merge base and
  reassess every domain they trigger; with no merge base, run a baseline.
- Controls without triggers (most owner-attested ones) are refreshed by evidence expiry and by
  baselines, not by deltas.
- Map each path to domains through the controls' `triggers`. Read a path that no trigger
  classifies and assign it; when unsure, reassess every domain it could affect.
- Changes to manifests, lockfiles, environment templates, deploy or infrastructure files re-run
  profile detection. A newly applicable control is assessed now.
- Rows outside the delta carry forward only while their evidence is unexpired and meets the
  evidence rule (a path, a command with its exit status, a dated attestation or a URL). Reassess a row whose evidence is vague or whose cited evidence changed in the delta.

## Always-on set

Reassessed on every run where they apply: SEC-12 (secrets in the delta), SEC-13 (new dependencies and current
advisories), TST-05 (isolated lower environments), DEL-03 (tested before deploy), DEL-04
(rollback path), DEL-09 (certificate and domain expiry), BR-02 and BR-04 (evidence age), OBS-03
(external uptime), and the expiry of every waiver and every piece of time-bound evidence.

## Staging gate

Blocks only on a FAIL in the staging set: DM-02 and DM-03 (a migration in the delta with no way
back or forward, or with an unreviewed blocking lock), and TST-05 (staging can reach production
data or credentials, or can email, charge, notify or call real customers or their systems). A
secret in the delta (SEC-12) or a new dependency that does not exist or is not the intended
package (SEC-13) blocks through the imported security verdict (see the security controls
reference), not through this set. The same rule applies to the dev stop of a release chain
(target `dev`). BLOCKED and NOT TESTED rows, in the staging set or elsewhere, are reported
without blocking staging; they carry into the production gate, where they block. Staging is where
the remaining evidence is produced.

## Production gate

- **`live`**: a baseline exists within its maximum age and the current catalog version; every
  applicable `blocker` row and every active `contract` row is PASS, NOT APPLICABLE with evidence,
  or WAIVED with an unexpired waiver (FAIL, BLOCKED and NOT TESTED block); the always-on set holds
  or is waived; the independent check ran.
- **`prototype`**: the staging set as for staging, plus DEL-04 and, with `db`, BR-01, which
  block unless PASS or WAIVED. List every other blocker as launch work in the plan.

## Before and after the deploy

Some evidence exists only after a deploy: OBS-03 green, the served certificate, live DNS and
email records, the rollback command printed for this version, and the `release.json` that DEL-03
cites (before the deploy, DEL-03 rests on the CI run for the commit or the release script's gate
list). Before the deploy these rows need
configuration evidence; the live part joins the release's live proof, and a failure there fails
the release. On a first deploy there is no previous version: DEL-04 is met by a tested disable
or teardown path (maintenance switch, feature flag, DNS cutback).

## Independent check

Before writing a production record, a fresh-context verifier that did not assess the rows checks
the evidence for every `blocker` and active `contract` row that became PASS or NOT APPLICABLE
since the last production record, and every applicability change. At launch this covers every
such row. Use the
separately installed `mneves-verify` skill when present, otherwise a fresh read-only subagent
with the rows, the evidence and this rule. If no verifier is available, those rows are BLOCKED
until a verifier runs or the owner waives them. An audit or provisional assessment lists these
rows as pending; the check is required only before a production record is written.

## Waivers

Only the owner, or a person the owner named, waives. A waiver names the control, owner, reason
and expiry; the ledger row or record that holds it gives its unit and target, so a waiver in a
record never repeats them (the release script refuses one that does); the maximum is 90 days, and 72 hours for an incident waiver
covering failures the release repairs. Waivers come from the release's decision packet and are
written to the ledger and the record. An expired waiver restores the underlying status.

`scripts/release.sh --waive readiness=<reason>` skips the record check entirely. Use it only when
the gate cannot run or for an incident repair the owner approved; the release records it. After
an incident repair deployed this way, run the gate on the deployed commit right after; its
findings follow the normal rules.

Rolling back to a build that already had a `ready` record for that target (its release
evidence keeps the record) needs no new record; the rollback command bypasses the release
script. Any other build needs a gate run or the owner's waiver.
Control-level gaps are waived inside the record, never with this flag.

## Freshness defaults

The ledger header may shorten these, never lengthen them.

| Evidence | Valid for |
|---|---|
| Baseline | 90 days |
| Readiness record | 24 hours, or until the earliest waiver or evidence expiry |
| BR-02 restore drill, OPS-04 and OBS-07 attestations | 180 days |
| BR-04 recovery exercise, SEC-19 penetration test | 365 days |
| CMP-08 access review | 90 days |
| TST-04 load test | until hot paths or scaling change, at most 365 days |
| Dependency advisories | the current run only |

Read advisories fresh on every run. An unavailable advisory source makes SEC-13 BLOCKED, never
PASS. A known exploitable advisory in a runtime dependency with a fix available is FAIL.

## Catalog versioning

Control IDs are never renumbered or reused. A retired control stays listed as retired, naming its
replacement. A material change to a control's meaning, tier or evidence raises the catalog
version; a ledger on an older version reassesses the changed controls, or runs a baseline when
the change list is unknown.

## Interaction with other gates

The readiness verdict never relaxes another gate: a blocking security finding still blocks. A
release presents every gate's open items in one decision packet.

## Mechanical checks

When a control has a deterministic check (secret scan, migration linter, DNS or certificate
lookup, dependency audit, eval run), the plan proposes adding it to the repository's own gates
(the release script's gate list or CI), so it runs on every release without an agent.
