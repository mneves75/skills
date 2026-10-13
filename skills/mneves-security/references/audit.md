# Audit coverage

Inspect these twelve areas in every requested project review. Record applicability,
files/surfaces inspected, tests attempted and evidence limits for each. Absence of
evidence is NOT TESTED or BLOCKED; justified absence of a feature is NOT APPLICABLE.
Select controls from the current official baseline and the project's real threat model.

## 1. Privacy and compliance readiness

Map collected/stored/logged/transmitted/shared data, purpose, access, retention and
deletion/export behavior. Trace databases, object storage, backups, telemetry, logs,
analytics, email/SMS, payments and AI providers. Identify region/config only when
source or authorized runtime evidence supports it; SDK presence does not prove region,
training use, retention or contractual terms.

Check an actual user-facing privacy disclosure against observed processing. Flag gaps
in relevant consent/choice, third-party disclosure, retention, export/deletion and
backup handling. Distinguish implemented flows from policy promises. Assess GDPR,
CCPA/LGPD and platform terms as engineering readiness where relevant; do not infer
jurisdiction, prescribe legal bases or claim legal compliance. Legal/content owners
resolve those decisions. Avoid collecting real user records to construct the data map.

## 2. Database and resource access control

For Supabase/Postgres, inspect migrations/schema, grants, RLS enablement and policies
for SELECT/INSERT/UPDATE/DELETE, including USING and WITH CHECK, ownership/tenant
mutation, role escalation and permissive policy combinations. Check exposed schemas,
views/functions (including definer privileges and search paths), RPCs, storage buckets,
object policies and signed URLs. Enabled RLS alone is not a sufficient control.

Privileged/service-role clients bypass ordinary enforcement; trace server authorization
before every privileged read/write. For other stores, inspect the equivalent resource
authorization layer. Authentication is not object authorization. Test anonymous,
owner, other user/tenant and relevant roles for every applicable operation using ordinary
identities and synthetic data. Never use a bypass identity as the negative control.
Distinguish local policy files, local execution and verified deployed policy state.

## 3. Authentication and session failure paths

Check repeated wrong passwords, unknown-email reset, expired/repeated verification
links and signup with an existing email. Compare messages, status codes, redirects,
response shape and observable timing for enumeration. Test malformed/replayed tokens,
logout/revocation, session rotation/expiry and relevant role/MFA changes. Trace provider
errors through the app, not just provider documentation or a mocked happy path.

Inspect OAuth/OIDC callbacks, state/nonce/PKCE and redirect allowlists when used;
server-side token verification must constrain signature algorithm, issuer, audience
and expiry as applicable. Keep reset/verification tokens short-lived and one-use where
the provider contract supports it. Use current provider/password-storage guidance.
Throttling/lockouts must account for distributed attempts and denial of service against
victims. Provider rate limits/anti-enumeration settings require runtime or operator proof.

## 4. Security headers, cookies and caches

Inspect the effective serving layer for CSP, HSTS, MIME-sniffing protection,
Referrer-Policy, Permissions-Policy, frame protection and sensitive-response caching.
Apply headers to appropriate response types; do not blanket-require HTML controls for
non-browser binaries. Verify success/error/redirect routes and static/deployed paths
where authorized. Use no-store/private behavior appropriate to sensitive content.

For session cookies check HttpOnly, Secure in HTTPS deployments, appropriate SameSite,
domain/path scope, lifetime and deletion behavior. Test legitimate auth/payment/embed
flows before enforcement changes. Establish HTTPS/subdomain readiness before HSTS
includeSubDomains/preload; they have operational rollback consequences. CSP changes
need runtime validation of scripts/styles/frames/connect sources. A report-only policy
is observation, not enforced protection. A restrictive header file is not live evidence.

## 5. OWASP application risks

Work through every category of the applicable current web/API lists. Trace reachable
SQL/NoSQL/OS/template injection, reflected/stored/DOM XSS, CSRF, SSRF, IDOR and tenant/
role isolation, deserialization, path traversal, unsafe redirects, weak cryptography,
session handling, mass assignment, supply-chain/integrity gaps and exceptional failures.
Include business-logic abuse, race conditions and fail-open paths when relevant.

Use parameterized queries, contextual output encoding, origin/CSRF checks for applicable
cookie-authenticated mutations and explicit object/property authorization. CORS is not
CSRF protection or authorization. SSRF checks cover redirect chains, URL parsing,
internal/link-local destinations and DNS behavior, using controlled targets rather than
probing real internal services. Review downstream API trust and response validation.
Relevance, reachability and actual impact determine findings; risk labels alone do not.

## 6. Server-side validation and unsafe inputs

Enumerate public forms, APIs/server actions, webhooks, jobs, imports, uploads and all
database writes. Verify type/length/format/range, payload size, ownership, authorization
and business invariants at the server boundary; reject unexpected writable fields.
Client validation does not protect an endpoint. Reuse existing validation patterns.

For webhooks verify signatures on the provider-required raw payload, timestamp/replay
rules and idempotent processing. Queued jobs need trusted provenance and authorization,
not just a validated JSON shape. For uploads check content/signature, size/decompression
limits, filenames/paths, execution isolation, serving content type and access control.
Encode output for its destination; do not globally strip or mutate valid user text.

## 7. Sensitive data and credential leaks

Inspect source, bundles/build config, logs, fixtures, examples/comments, response DTOs,
analytics events and client-visible env conventions without printing matching values.
Where authorized, use an existing redacted secret scanner; establish whether history
was included rather than silently claiming historical coverage. Check passwords,
tokens, authorization headers, PII, prompts/completions, payment details and DB errors.

Allowlist response fields and redact diagnostics at the emitting boundary. Report a
potential leak by path/line and credential type, with exposure confidence and required
rotation/incident action. Do not test a found key against a live provider, fetch real
records, rewrite history or rotate secrets without exact authorization.

## 8. Public keys, secret keys and paid proxies

Classify keys by the actual provider contract, independent of variable names. Public/
publishable keys may ship to clients only when allowed, with the required authorization
controls. Browser/mobile/desktop bundles cannot keep a shared secret confidential.
Secret/admin/service-role keys, database credentials, paid AI keys and webhook signing
secrets remain in controlled server environments.

Trace API responses, browser calls, source maps and generated env substitution. Moving
a paid call server-side also requires caller/object authorization, input/destination
allowlists, limits and safe errors. Preserve valid public-key usage; an anonymous public
key is not proof of a vulnerability or proof of safe resource policies.

## 9. Rate limits, availability and cost protection

Inventory paid AI/API calls, expensive queries, auth/reset/signup, email/SMS, uploads,
payment operations and public submissions. Use existing edge/store/provider mechanisms
with appropriate identity/tenant/IP keys, atomic enforcement, burst/sustained limits,
timeouts, bounded retries/concurrency/payloads and deliberate failure behavior.

In-memory limits on one replica are not global enforcement. Trust forwarded identity/IP
only through the deployment's verified proxy model. Test bypasses, concurrency, rejected
work and legitimate requests; rejection must precede paid work. Bound output tokens,
agent steps/retries and tenant spend where applicable. Distinguish hard caps from alerts
and provider rate limits; list daily/monthly caps, billing alerts and monitoring as manual
actions when code cannot enforce them. Document chosen defaults and assumptions.

## 10. Bot protection and CORS

Inventory signup/login/reset, contact/waitlist/newsletter, comments/feedback and uploads.
Choose anti-abuse controls by risk; CAPTCHA/Turnstile is not automatically appropriate
for every API or static site. If present, verify its token on the server, validate
provider-prescribed context (such as hostname/action), expiry/replay and failure handling.
A frontend widget alone offers no server enforcement. Keep accessibility/privacy and
legitimate-user failure behavior explicit. It supplements authentication and limits.

Inspect preflights and actual/error responses; compare normalized origins to exact
configured trusted production/development origins where cross-origin access is needed.
Do not use wildcard credentials, loose substring matches or reflect arbitrary origins.
Where appropriate set Vary: Origin and constrain methods/headers. CORS limits browser
response access; it does not stop direct requests. Do not invent deployment domains.

## 11. Safe errors, logging and monitoring

Return useful generic user errors without SQL, stack traces, schema names, provider
internals or sensitive identifiers. Preserve safe actionable validation/auth UX and
protocol status codes. Log redacted diagnostic context server-side with correlation
identifiers, authorization-denial/audit events, retention/access limits and alert owners.

Check auth headers, credentials, request bodies, PII and AI content at every logger/error
boundary. Log injection and diagnostic tools are data-exposure paths too. Security
errors must not fail open, exhaust resources or suppress the audit trail. A normalization
layer is useful only when it fits existing patterns. Source logging calls do not prove
production collection, redaction, alert delivery or incident response readiness.

## 12. Dependencies and scanner results

Use the actual package manager/lockfile and existing scanners. Record exact command,
tool/advisory version, graph coverage, exit status and diagnostics. Confirm affected
version and reachability; distinguish runtime/dev/build supply-chain exposure. Audit
network requests can disclose a private dependency graph: follow host disclosure rules.

Prefer safe minimal upgrades with focused regressions and reproducible frozen installs.
Do not force major upgrades, blindly run an audit autofix, remove safeguards or change
tests to silence an alert. Breaking upgrades become risk-assessed follow-up items.
Check pipeline permissions, dependency/download integrity and artifact provenance when
relevant. A zero count or unavailable advisory database does not prove no vulnerabilities.

## Conditional AI, agentic and mobile surfaces

For AI/RAG/agents apply every category of current LLM/agentic guidance. Trace untrusted
prompts/retrieved content/tool output, output encoding/execution, sensitive or hidden
context exposure, data/model poisoning, supplier/model integrity, vector retrieval tenant
isolation, unsupported output, tool privileges and unbounded consumption. Prompts are
not a security boundary. Authorize tool actions server-side, constrain agency/egress,
isolate memory/context and require the product's human approval for consequential work.
Probe with synthetic adversarial content and bounded tool/cost budgets.

For mobile clients use current MASVS/MASTG guidance: local sensitive storage/backups,
transport/platform trust, exported components/deep links, permissions, privacy/telemetry,
auth redirects and shipped credentials. Server authorization remains required. Prefer
the host's available device/build workflow; report unavailable runtime testing rather
than claiming a source inspection proves installed-device security.
