# Controls: maintainability, ownership and operations

Format and terms as in `controls-data.md`. These controls keep the product operable by people
other than its first builder. Several can only be owner-attested.

## MNT: maintainability

MNT-01 Readable code
`advisory` · triggers: any source change
- Verify: names, structure and comments let a new engineer follow the main flows; formatting,
  linting and type checks run in CI; generated or copied code has an owner.
- Evidence: source.

MNT-02 Reviewed changes
`blocker` · applies: `live` with stake · triggers: repository settings, CI
- Verify: every change to the default branch is reviewed before merge by a human or an independent
  reviewer, with required checks; branch protection blocks direct pushes.
- Evidence: repository settings (read through the host's API or owner-attested).

MNT-03 Branching strategy
`advisory` · triggers: contribution docs
- Verify: a written strategy (short-lived branches, protected default branch, how releases are cut)
  lets two people work without overwriting each other.
- Evidence: source (docs).

MNT-04 Dependency cadence
`advisory` · triggers: manifests, lockfiles, bot configuration
- Verify: dependencies update on a schedule (an update bot or a monthly task) through reviewed
  pull requests, and lockfiles are committed.
- Evidence: source plus recent update history.

MNT-05 Supported runtimes and frameworks
`blocker` · triggers: manifests, runtime pins
- Verify: the runtime, framework and database versions still receive security fixes; an
  end-of-life calendar has an owner; critical advisories have a patch deadline.
- Evidence: source plus the vendors' published support dates.

MNT-06 Dead code
`advisory` · triggers: any source change
- Verify: abandoned attempts, unused files, exports, routes, flags and dependencies are removed;
  an unused-code detector runs where the stack has one.
- Evidence: source.

MNT-07 Oversized modules
`advisory` · triggers: any source change
- Verify: files and functions that grew past the project's threshold are split by responsibility;
  report the largest offenders with sizes.
- Evidence: source.

MNT-08 Decision records
`advisory` · triggers: architecture changes
- Verify: consequential decisions (data model, providers, tenancy, auth, deployment) are written
  down with context, the options and the reason.
- Evidence: source (docs).

MNT-09 Fast onboarding
`advisory` · triggers: setup scripts, README, environment templates
- Verify: following the README and an environment template, a new engineer runs the product and
  its tests locally in under an hour without asking anyone.
- Evidence: local run from a clean checkout.

MNT-10 Handover documentation
`advisory`
- Verify: an inheritor finds the architecture overview, data flows, deploy and rollback steps,
  runbooks, owners and known risks in the repository or a linked space.
- Evidence: source (docs) or owner-attested.

## OPS: ownership and operations

OPS-01 Admin panel
`advisory` · applies: `accounts` · triggers: admin code
- Verify: operators do routine account work (look up, suspend, change plan, resend email) through
  an authorized, audited tool instead of direct database edits.
- Evidence: source.

OPS-02 Support tooling
`advisory` · applies: `accounts`
- Verify: support can see a customer's account state, recent errors and relevant logs by customer
  id without asking engineering, within the access rules of SEC-06.
- Evidence: source or owner-attested.

OPS-03 Customer changelog
`advisory` · applies: `live`
- Verify: customers can read what changed and when, in their language.
- Evidence: production page or source.

OPS-04 Company-owned assets
`blocker` · applies: `live`
- Verify: domains, registrar, DNS, hosting, repositories, app-store, payment, email and monitoring
  accounts belong to the company, have at least two administrators with strong authentication,
  and their recovery codes are in the company's vault.
- Evidence: owner-attested.

OPS-05 Bus factor
`blocker` · applies: `live` with stake
- Verify: at least two people can deploy, roll back, restore and answer a page from written
  procedures. A solo operator records a waiver with an expiry and a plan.
- Evidence: owner-attested.

OPS-06 Named owners
`blocker` · applies: `live` with stake
- Verify: the ledger names a person (handle or role, never contact details in a public repository)
  for each seat, and one person may hold several: code review, data model and migrations, delivery and cost, on-call primary and
  backup, security patching, compliance, testing, scope (says no to risky features), architecture
  and decision memory. An empty on-call or data seat blocks; another empty seat is a finding.
- Evidence: owner-attested.
