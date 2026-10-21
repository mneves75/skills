# Launch controls

Read this in deploy-gate mode and whenever a request asks whether an application is safe to put
in front of paying customers. These 32 controls are the security, privacy and compliance checks a
launch needs beyond the twelve review areas of the audit reference. Each names the audit area
that holds its depth. A separately installed production-readiness review, when present, owns
the operational, data-integrity, billing, product and people checks and imports these rows by ID;
without it, this skill still covers the security slice completely.

## How to evaluate

- **Applicability.** Decide from the source inventory and the product's real market (who
  pays, which contracts, which data). The `applies` note narrows a control. Not applicable needs
  a reason ("no login surface", "no health records and no contract asks for SOC 2"); a control
  that is hard to check is NOT TESTED, never N/A. An undetermined regulated-data question is
  BLOCKED until the owner answers it: a plan item on dev and staging, a named waiver for
  production.
- **Evidence.** `source`: source or configuration inspection settles it. `test`: a test or
  local run with synthetic data. `runtime`: the deployed target or provider state. `owner`: a
  document, contract or named person. Source-only evidence never makes a `runtime` or `owner`
  control Yes. Before a deploy, configuration evidence for that target meets a `runtime`
  control; its live check then joins the release's live proof.
- **Findings.** A failed control that is exploitable is a finding with a verdict and,
  when confirmed, a severity, recorded once and cited from the row. A missing control is also a finding: name
  what the product lacks and the smallest durable way to add it.
- **Plan.** Every applicable control that is not Yes gets a remediation step: what to build,
  fix, configure or decide, its owner type (code, database, provider, legal, manual QA) and an
  acceptance check.

## SEC — Security

- **SEC-01 Reset and verification links.** Tokens are random, stored hashed, short-lived,
  single-use, voided by a newer link or a password change; the response does not reveal whether
  the account exists. Applies: accounts. Area 3. `test`
- **SEC-02 Multi-factor authentication and recovery.** A second factor exists, required for
  administrators and operators. A lost-device path (recovery codes or a verified support
  process) is not weaker than the factor and revokes old factors and sessions. Applies:
  accounts. Area 3. `source`, `test`
- **SEC-03 Session lifetime and revocation.** Idle and absolute timeouts; rotation on login and
  privilege change; one action revokes every session and token of one user. Applies: accounts.
  Area 3. `test`
- **SEC-04 Enterprise single sign-on.** OIDC and, where enterprise identity providers require
  it, SAML 2.0: signature, issuer, audience, recipient, expiry and replay checks; account
  linking cannot take over an existing account; a tenant can enforce SSO. Applies: contracts or
  procurement that require SSO. Area 3. `source`, `test`
- **SEC-05 Automated deprovisioning.** SCIM, or the provider's equivalent, deactivates a user,
  ends sessions and revokes tokens as soon as the identity provider offboards them. Applies:
  contracts that require it. Areas 2 and 3. `test`
- **SEC-06 Authorization model.** Roles and permissions beyond "admin" and "everyone else",
  checked on the server for each action, deny by default, tested per role. Applies: more than
  one role or tenant. Areas 2 and 5. `source`
- **SEC-07 Object-level authorization.** Every route or action that takes an identifier loads
  the object scoped to the caller before reading or writing; a test with a second user's
  identifier is refused. Applies: accounts. Areas 2 and 5. `test`
- **SEC-08 Tenant isolation.** Queries, caches, search indexes, file paths and background jobs
  carry the tenant scope, enforced in one layer and proven with a two-tenant test. Applies:
  multi-tenant. Area 2. `test`
- **SEC-09 Support impersonation.** "Log in as this user" needs an operator role and a reason,
  is time-limited and visible, cannot change credentials or reach the most sensitive actions, and
  writes an audit event for every use. Applies: when impersonation exists. Areas 2 and 11.
  `source`, `test`
- **SEC-10 Login throttling.** Login, reset, MFA and signup are throttled per account
  and per source, and the limit holds across instances. Escalating delays or a challenge stop
  guessing at scale without letting an attacker lock a real user out. Applies: accounts.
  Areas 3, 9 and 10. `test`
- **SEC-11 Server validation and injection defenses.** Every input is validated on the server;
  user content is encoded or sanitized for its output context; queries are parameterized;
  cookie-authenticated mutations resist CSRF; the rest of the applicable OWASP risks are traced.
  Areas 5 and 6. `source`, `test`
- **SEC-12 Secrets hygiene and rotation.** No secret in tracked files, history, build output,
  logs, prompts, agent transcripts or committed session files. Every key that ever appeared in a
  repository, config file, prompt or chat is listed for rotation as an owner action, and the
  rotation is recorded. Values are never printed. A usable secret in the candidate's tracked
  files or build output is a confirmed High finding at least, so it blocks every target. Areas 7
  and 8. `source`, `owner`
- **SEC-13 Supply chain.** Every dependency exists on its intended registry and is the package
  the code meant (publisher, age, adoption, no near-name lookalike or invented name), and it is
  locked to a version. Advisory scanning runs with its scope and exit status recorded; advisories
  are read fresh on every gate run. A dependency that does not exist on its registry or is not
  the intended package is a confirmed High finding at least, so it blocks every target. Area 12.
  `source`
- **SEC-14 File uploads.** Size limits, content checks, generated names, storage where files
  cannot execute (or a separate domain), malware scanning where files are shared, authorized
  access and safe serving types. Applies: uploads. Area 6. `source`, `test`
- **SEC-15 CORS and security headers.** CORS allows only listed origins, never a reflected
  origin or a wildcard with credentials; every response type carries the headers it needs.
  Applies: browser surfaces and browser-called APIs. Areas 4 and 10. `source`, `runtime`
- **SEC-16 Encryption in transit and at rest.** HTTPS only, internal hops included where
  feasible; databases, backups and object storage encrypted at rest; field-level encryption for
  especially sensitive values. Areas 4 and 7. `runtime`
- **SEC-17 Least privilege.** People, services, CI jobs and AI agents hold only what their task
  needs. Production credentials are scoped and short-lived where possible, and no agent reaches
  production data or deploys without a human approval step. Areas 8 and AI. `source`, `owner`
- **SEC-18 Audit trail and log redaction.** Security-relevant actions (login, permission change,
  export, impersonation, admin edits) record who, what, when and from where; no log holds
  passwords, tokens, keys or card data. Area 11. `source`, `test`
- **SEC-19 Penetration test.** An independent test of the live product ran before the first
  enterprise customer's own, with findings tracked to closure. Applies: enterprise sales. `owner`
- **SEC-20 Vulnerability disclosure.** A published contact and policy (`SECURITY.md`, and
  `/.well-known/security.txt` per RFC 9116 for web products) with an owner who answers.
  Applies: live products. `source`, `owner`
- **SEC-21 Compromised device or credential plan.** A written runbook for a lost laptop or a
  leaked credential: revoke sessions, tokens and keys, then review access logs. Devices with
  production access use disk encryption and a screen lock. Applies: live products. `owner`
- **SEC-22 Inbound webhook signatures.** Each webhook verifies the provider's signature on the
  raw body, rejects stale or replayed deliveries, and runs nothing before verification. Applies:
  inbound webhooks. Area 6. `test`
- **SEC-23 AI feature safeguards.** Applies: the product calls a model or runs an agent; see the
  conditional AI section of the audit reference.
  - Every untrusted field that reaches the model is treated as possible prompt injection, and
    it cannot widen tool permissions. `test`
  - Customer and patient data reach an external model only as the contract and data agreements
    allow. `source`, `owner`
  - A per-customer spend and rate cap stops before the paid call. `source`, `test`
  - Anything the AI does that cannot be undone waits for human approval. `source`, `test`
  - Prompt and output logs keep only what retention rules allow. `source`

## CMP — Compliance

- **CMP-01 Security questionnaire.** A maintained answer set for the questionnaire enterprise
  buyers send, each answer citing evidence. Applies: enterprise sales. Area 1. `owner`
- **CMP-02 SOC 2.** Policies, collected evidence and an auditor engagement for the agreed
  criteria. Applies: customers who require it. Area 1. `owner`
- **CMP-03 Health data safeguards.** HIPAA safeguards from the first patient record, and a
  business associate agreement with every vendor that touches the data, model providers
  included. Applies: any health record. Area 1. `source`, `owner`
- **CMP-04 Read-access audit trail.** Views of sensitive records, not only changes, record who
  viewed what and when; the trail is retained and reviewable. Applies: health data, or contracts
  that ask for it. Areas 2 and 11. `source`
- **CMP-05 Payment card scope.** Card numbers never reach the product's servers, logs or
  database (provider-hosted fields or pages); pages that embed payment fields control their
  scripts. Applies: payments. Areas 4 and 7. `source`
- **CMP-06 Erasure everywhere.** A deletion request reaches every table, file store, search
  index, analytics tool, log and processor; backups keep erased data out of use until they
  expire, and restores re-apply erasures. Applies: personal data. Area 1. `source`, `owner`
- **CMP-07 Data residency.** Every store, processor, backup and log for the covered customers
  stays in the promised region, model and email providers included. Applies: contracts that
  restrict the region. Area 1. `runtime`, `owner`
- **CMP-08 Access reviews.** On the agreed schedule (quarterly where required), an owner reviews
  and signs who can reach production, admin tools and providers, and removes what is unneeded.
  Applies: SOC 2 or contracts that ask for it. `owner`
- **CMP-09 Legal documents match the product.** The terms and privacy policy describe the data
  the code collects, the processors it uses and the retention it applies; a mismatch is a
  finding for the legal owner. Applies: live products with accounts. Area 1. `source`, `owner`
