# Controls: testing, billing, public API, AI operations and product experience

Format and terms as in `controls-data.md`.

## TST: testing

TST-01 Rule-based unit tests
`advisory` · triggers: business logic
- Verify: business rules (pricing, permissions, limits, state transitions) have tests whose
  expected values come from the rule's owner or written examples, not from running the code.
  Money and permission logic covers edges and boundaries.
- Evidence: source plus a test run.

TST-02 Third-party integration tests
`advisory` · applies: external APIs · triggers: API clients
- Verify: each external dependency has sandbox or contract tests for success, error, timeout and
  malformed responses, run in CI or before release.
- Evidence: a test run.

TST-03 Critical-flow end-to-end tests
`blocker` · applies: `live` with `accounts` or `payments` · triggers: the flows below
- Verify: signup, login, password reset, checkout or upgrade, and the product's core job run as
  end-to-end tests against staging before each production deploy.
- Evidence: a staging run for the candidate.

TST-04 Load test
`blocker` at launch, then on hot-path changes · applies: `live` with stake · triggers: hot paths, scaling configuration
- Verify: a load test at expected peak with headroom ran against a production-like environment
  and recorded throughput, latency percentiles, error rate and the first bottleneck. Capacity
  settings reflect the result.
- Evidence: a staging run.

TST-05 Isolated lower environments
`blocker` · staging set · triggers: seed scripts, fixtures, environment configuration, provider configuration
- Verify: lower environments use synthetic or irreversibly anonymized data and their own
  credentials. No production database address, key or customer export reaches staging,
  development or fixtures. Side effects stay contained: payment providers in test mode, email
  through a sandbox or a recipient allowlist, their own webhook endpoints, queues and schedulers,
  and no calls that reach customers' systems.
- Evidence: source plus staging configuration (variable names only).

TST-06 Regression tests
`advisory` · triggers: bug fixes
- Verify: each fixed bug adds a test that failed before the fix, and the suite runs on every
  change.
- Evidence: source (sample recent fixes).

TST-07 Supported environments
`advisory` · applies: `ui`
- Verify: a support matrix (browsers, devices, minimum hardware) exists, and the product is
  checked at its low end with CPU and network throttling against a performance budget.
- Evidence: local or staging.

## BIL: billing

BIL-01 Plan changes and proration
`blocker` · applies: `subscriptions` · triggers: billing code, plan configuration
- Verify: upgrade, downgrade, cancel, pause, trial end and seat changes follow written rules.
  Proration matches the provider's calculation. Entitlements come from one source of truth kept in
  step with the provider through webhooks and a reconciliation that also repairs duplicate,
  reordered or partly processed events.
- Evidence: local tests with provider test clocks or fixtures.

BIL-02 Failed payments and dunning
`blocker` · applies: `subscriptions` · triggers: billing code, email templates
- Verify: a failed renewal triggers provider retries, customer notices with a card-update link, a
  grace period and a defined access downgrade; recovery restores access.
- Evidence: staging run with test cards.

BIL-03 Invoice requirements
`contract` (b2b invoicing) · triggers: invoice templates, billing configuration
- Verify: invoices show legal entity details, tax ids, addresses, sequential numbering where
  required and customer fields such as a purchase-order number. Customers download past invoices.
- Evidence: a staging sample invoice.

BIL-04 Sales tax and VAT
`blocker` · applies: `payments` in a taxing jurisdiction · triggers: pricing, checkout, billing configuration
- Verify: a tax engine or the provider's tax service computes tax from customer location and
  product tax code. Registrations and thresholds per jurisdiction have an owner. Reverse charge and
  tax-id validation work where they apply. Invoices show tax correctly.
- Evidence: a staging sample plus owner-attested registrations (finance or legal).

BIL-05 Refunds and credits
`blocker` · applies: `payments` · triggers: billing code, admin tools
- Verify: full and partial refunds and account credits use one audited, idempotent flow that
  updates entitlements and accounting records.
- Evidence: local or staging test.

BIL-06 Metering accuracy
`blocker` · applies: `metered` · triggers: usage capture, billing jobs
- Verify: usage events are idempotent, timestamped and attributed to the right period; late,
  duplicate and reordered events are handled; a reconciliation matches metered totals with invoice
  lines to the cent.
- Evidence: a local reconciliation test.

BIL-07 Custom contract terms
`contract` (custom contracts), otherwise `advisory` · triggers: billing configuration
- Verify: negotiated terms (annual prepay, custom prices, payment terms, minimums) are data in the
  billing system, not code branches; manual overrides are logged.
- Evidence: source.

BIL-08 Revenue reconciliation
`advisory` · applies: `payments`
- Verify: payouts, invoices, refunds, disputes and tax reconcile with accounting each month, and
  finance can reproduce revenue reports.
- Evidence: owner-attested.

## API: public API

API-01 Versioning and deprecation
`blocker` · applies: `public-api` · triggers: API routes, schemas
- Verify: the API has an explicit version scheme and deprecation policy. CI detects breaking
  schema changes, which ship only in a new version with notice.
- Evidence: source plus CI.

API-02 Customer API keys
`blocker` · applies: `public-api` · triggers: key management code
- Verify: customers create, name, scope, rotate and revoke their keys. A key is shown once,
  stored hashed (SEC-12), shows its last use, and stops working at once when revoked.
- Evidence: local.

API-03 Integration-friendly rate limits
`blocker` · applies: `public-api` · triggers: rate-limit configuration
- Verify: limits apply per key or tenant, are documented, return limit headers and 429 with
  `Retry-After`, allow realistic bursts, and alert before a customer hits them.
- Evidence: local test.

API-04 Sandbox
`contract` (sandbox), otherwise `advisory` · applies: `public-api`
- Verify: a test mode with separate keys and data lets customers build without touching live
  data or money.
- Evidence: staging.

## AI: AI operations

AI-01 Evals
`blocker` when model output is central to the product, otherwise `advisory` · applies: `ai` · triggers: prompts, model configuration, retrieval code
- Verify: a versioned eval set with expected outcomes covers the main tasks and known failures. It
  runs on every model, prompt or retrieval change and blocks regressions beyond a threshold.
- Evidence: a local or staging eval run for the candidate.

AI-02 Provider failure handling
`blocker` when a model call sits in a critical flow, otherwise `advisory` · applies: `ai` · triggers: model clients
- Verify: model calls have timeouts and bounded retries. An outage degrades to a fallback model or
  provider, a cached answer or a clear message, and a circuit breaker stops retry storms.
- Evidence: local test with a failing fake.

AI-03 Model lifecycle
`advisory` · applies: `ai` · triggers: model configuration
- Verify: model ids are pinned in configuration, deprecation notices have an owner, and a model
  switch needs an eval run (AI-01) and a staged rollout.
- Evidence: source.

## UX: product experience

UX-01 Slow networks
`advisory` · applies: `ui` · triggers: front-end code, assets
- Verify: pages meet a performance budget on a throttled connection; heavy assets load lazily;
  requests time out and retry with feedback; flaky connections do not lose work.
- Evidence: a local throttled run.

UX-02 Empty, loading and error states
`advisory` · applies: `ui` · triggers: screens, components
- Verify: every data-driven screen has all three states.
- Evidence: local.

UX-03 Actionable errors
`advisory` · applies: `ui` · triggers: error handling, copy
- Verify: an error says what happened and what to do next and shows a reference support can
  trace. A bare "something went wrong" is a finding.
- Evidence: local.

UX-04 Form resilience
`advisory` · applies: `ui` · triggers: forms
- Verify: a failed validation keeps every entered value and moves focus to the first invalid
  field; costly drafts survive navigation.
- Evidence: local.

UX-05 Undo
`advisory` · applies: `ui` · triggers: destructive actions
- Verify: destructive actions offer undo or a restore window (DM-06), with confirmation sized to
  the impact.
- Evidence: local.

UX-06 Keyboard and screen reader
`advisory` · applies: `ui` · triggers: components
- Verify: every flow works by keyboard with visible focus; controls have accessible names;
  dynamic changes are announced.
- Evidence: a manual keyboard and screen-reader pass plus automated checks.

UX-07 Accessibility conformance
`contract` (accessibility), or required by a derived regulation for consumer services in a
market with accessibility law (`gates.md`) · applies: `ui`
- Verify: an audit against the required standard (for example WCAG 2.2 AA or EN 301 549)
  produced a conformance report or accessibility statement, and CI guards against regressions.
- Evidence: owner-attested audit report.

UX-08 Localization
`advisory` · applies: `i18n` · triggers: strings, formatting code
- Verify: strings are externalized; dates, numbers, currencies and plurals use locale-aware
  formatting; layouts tolerate text expansion and right-to-left scripts.
- Evidence: local.

UX-09 Navigation state
`advisory` · applies: `ui` · triggers: routing
- Verify: back, reload and deep links restore the expected view; URLs carry meaningful state;
  going back never resubmits a step.
- Evidence: local.
