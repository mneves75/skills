# Controls delegated to the security review

These rows keep the ledger complete for security, privacy and compliance. When the separately
installed `mneves-security` skill is available, it owns the assessment: run it (or read its
current report or gate verdict for the same commit) and copy each result into the matching row
with its evidence scope. Do not re-audit what it already covered. Without that skill, run the
`Fallback` check, mark the row's depth as reduced in the ledger, and keep runtime and provider
claims NOT TESTED. A fallback never replaces a security audit.

`Area` names the `mneves-security` review area that owns the row.

## SEC: security

SEC-01 Reset and verification links
`blocker` · applies: `accounts` · area: authentication and session failure paths
- Fallback: reset and verification tokens are random, stored hashed, expire within the
  provider's or the product's short window, work once, and the response does not reveal whether
  the email exists.

SEC-02 Multi-factor authentication and recovery
`blocker` for privileged accounts, `contract` (mfa) for customers · applies: `accounts` · area: authentication
- Fallback: administrators and operators must use a second factor. A lost-device path exists
  (recovery codes or a verified support process) that does not let support bypass identity
  checks, and recovery revokes old factors and sessions.

SEC-03 Session lifetime and revocation
`blocker` · applies: `accounts` · area: authentication and session failure paths
- Fallback: sessions have idle and absolute timeouts, rotate on login and privilege change, and
  one action revokes every session and token for a user.

SEC-04 Enterprise single sign-on
`contract` (sso) · applies: `accounts` · area: authentication (OAuth/OIDC/SAML)
- Fallback: OIDC or SAML login validates signature, issuer, audience, expiry and replay; account
  linking cannot take over an existing account; the tenant can enforce SSO for its domain.

SEC-05 Automated deprovisioning
`contract` (scim) · applies: `accounts` · area: authentication; access control
- Fallback: SCIM (or the identity provider's equivalent) deactivates a user, ends their sessions
  and revokes their tokens as soon as IT offboards them.

SEC-06 Authorization model
`blocker` · applies: `multi-tenant` or more than one role · area: access control; OWASP risks
- Fallback: roles and permissions are explicit server-side checks per action, deny by default,
  with tests for each role on each sensitive action.

SEC-07 Object-level authorization
`blocker` · applies: `accounts` · area: access control; OWASP risks
- Fallback: every route or action that takes an object id loads the object scoped to the caller
  (owner or tenant) before reading or writing; a test uses a second user's id and is refused.

SEC-08 Tenant isolation
`blocker` · applies: `multi-tenant` · area: database and resource access control
- Fallback: every query, cache key, search index, file path and background job carries the
  tenant scope, enforced in one layer (row-level policies or a scoped repository), with a
  cross-tenant test.

SEC-09 Support impersonation
`blocker` when impersonation exists, otherwise `advisory` · applies: `accounts` · area: access control; logging
- Fallback: "log in as this user" requires an operator role and a reason, is visible to the
  operator as a banner, cannot change credentials, and writes an audit event for every use.

SEC-10 Login throttling
`blocker` · applies: `accounts` · area: authentication; rate limits
- Fallback: failed attempts are throttled per account and per source with increasing delays or a
  challenge, without a hard lockout that an attacker can trigger against a real user.

SEC-11 Server validation and injection defenses
`blocker` · area: server-side validation; OWASP risks
- Fallback: every write path validates type, length, range and ownership on the server; queries
  are parameterized; output is encoded for its context; cookie-authenticated mutations have CSRF
  protection.

SEC-12 Secrets hygiene and rotation
`blocker` · staging set · area: sensitive data and credential leaks; keys
- Fallback: no secret in tracked files, history, build output, logs or committed agent session
  files; secrets that ever appeared in a repository, chat or config are listed for rotation as an
  owner action; values are never printed.

SEC-13 Supply chain
`blocker` · staging set (new dependencies) · always-on (advisories) · area: dependencies and scanners
- Fallback: each new dependency exists in its registry, is the package the code meant (name,
  publisher, age, adoption, no near-name lookalike), and is pinned in the lockfile; the package
  manager's audit runs with its scope and exit status recorded.

SEC-14 File uploads
`blocker` · applies: `uploads` · area: server-side validation
- Fallback: uploads have size limits, content checks, generated names, storage outside the
  executable web root (or a separate domain), malware scanning where files are shared, and
  authorized access.

SEC-15 CORS and security headers
`blocker` · applies: `ui` or browser-called APIs · area: headers, cookies and caches; CORS
- Fallback: CORS allows only listed origins (never reflected or wildcard with credentials);
  responses carry HSTS, content-type protection, frame protection, a referrer policy and a content
  security policy suited to the app.

SEC-16 Encryption in transit and at rest
`blocker` · area: headers; sensitive data
- Fallback: every endpoint is HTTPS only; databases, backups and object storage are encrypted at
  rest; especially sensitive fields (tokens, government ids) have field-level encryption.

SEC-17 Least privilege
`blocker` · area: keys; AI and agentic controls
- Fallback: people, services, CI jobs and AI agents hold only the permissions their task needs,
  production credentials are scoped and short-lived where possible, and agents cannot reach
  production data or deploys without a human approval step.

SEC-18 Audit trail and log redaction
`blocker` · area: safe errors, logging and monitoring
- Fallback: security-relevant actions (login, permission change, export, impersonation, admin
  edits) record who, what, when and from where; logs never contain passwords, tokens, keys or card
  data.

SEC-19 Penetration test
`contract` (pentest) · area: none (owner action)
- Fallback: an independent test of the live product within the evidence window, with findings
  tracked to closure. Owner-attested only.

SEC-20 Vulnerability disclosure
`blocker` · applies: `live` with stake · area: none (owner action)
- Fallback: a published contact and policy (`SECURITY.md`, and `/.well-known/security.txt` per
  RFC 9116 for web products) with an owner who answers.

SEC-21 Compromised device or credential plan
`blocker` · applies: `live` with stake · area: none (owner action)
- Fallback: a written runbook revokes sessions, tokens and keys for a lost laptop or leaked
  credential; devices with production access use disk encryption and a screen lock.

SEC-22 Inbound webhook signatures
`blocker` · applies: `webhooks` · area: server-side validation
- Fallback: each webhook verifies the provider's signature on the raw body, rejects stale
  timestamps, and runs nothing before verification. Processing rules are in ASY-06.

SEC-23 AI feature safeguards
`blocker` · applies: `ai` · area: AI, agentic and cost controls
- Fallback: untrusted text cannot change tool permissions (prompt injection); customer or
  patient data reaches an external model only as the contract and agreements allow; per-customer
  spend and rate caps stop before cost runs away; irreversible actions need human approval;
  prompt and output logs keep only what retention rules allow.

## CMP: compliance

CMP-01 Security questionnaire
`contract` (enterprise) · area: privacy and compliance readiness
- Fallback: a maintained answer set where every answer cites evidence (policy, configuration,
  report). Owner-attested.

CMP-02 SOC 2
`contract` (soc2) · area: privacy and compliance readiness
- Fallback: policies, collected evidence and an auditor engagement for the agreed criteria;
  owner-attested status and report date.

CMP-03 Health data safeguards
`blocker` · applies: `phi` · area: privacy and compliance readiness
- Fallback: a business associate agreement with every vendor that touches the data, model
  providers included, plus the technical safeguards the agreement requires. Owner-attested.

CMP-04 Read-access audit trail
`blocker` with `phi`, otherwise `contract` (audit) · area: logging; access control
- Fallback: views of sensitive records (not only changes) record who viewed what and when, and
  the trail is retained and reviewable.

CMP-05 Payment card scope
`blocker` · applies: `payments` · area: sensitive data; headers and scripts
- Fallback: card numbers never reach the product's servers, logs or database (provider-hosted
  fields or pages); pages that embed payment fields control their scripts as the card scheme
  rules require.

CMP-06 Erasure everywhere
`blocker` · applies: `accounts` · area: privacy and compliance readiness
- Fallback: a deletion request reaches every table, file store, search index, analytics tool,
  log and processor; backups keep erased data out of use until they expire, and restores re-apply
  erasures.

CMP-07 Data residency
`contract` (residency) · area: privacy and compliance readiness
- Fallback: every store, processor, backup and log for the covered customers stays in the
  promised region, model and email providers included.

CMP-08 Access reviews
`contract` (soc2 or access-review) · area: none (owner action)
- Fallback: on the agreed schedule, an owner reviews and signs who can access production, admin
  tools and providers, and removes what is unneeded.

CMP-09 Legal documents match the product
`blocker` · applies: `live` with `accounts` · area: privacy and compliance readiness
- Fallback: the terms and privacy policy describe the data the code actually collects, the
  processors it uses and the retention it applies; mismatches are findings for the legal owner.

## Importing a `mneves-security` report

Map its launch-checklist subjects to rows: privacy disclosure → CMP-09; data map, retention,
deletion and export → CMP-06 and DC-10; access control → SEC-06, SEC-07, SEC-08; server-side
validation → SEC-11; authentication failures and sessions → SEC-01, SEC-03, SEC-10; headers,
cookies and cache → SEC-15; OWASP risks → SEC-11; secrets and leaks → SEC-12; public and secret
keys and paid proxies → SEC-17 and SEC-23; rate limits → SEC-10 and API-03; bot controls → SEC-10;
CORS and CSRF → SEC-15 and SEC-11; safe errors and logs → SEC-18; dependencies → SEC-13; billing
caps → CST-02 and SEC-23; monitoring → OBS-02, OBS-03, OBS-04. Rows the report does not cover keep
their previous status or use the fallback.
