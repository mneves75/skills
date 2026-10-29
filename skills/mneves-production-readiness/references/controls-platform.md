# Controls: delivery, integrations, email, cost and operations

Each control states its tier, the profile flags that make it apply, and the paths whose change
triggers reassessment in a delta. `Verify` says what to inspect or run; `Evidence` names the
minimum scope that can mark it PASS.

## DEL: delivery and environments

### DEL-01 Environment parity
`advisory` · triggers: deploy config, environment templates, infrastructure code
- Verify: staging runs the same build artifact, runtime versions, services and configuration
  shape as production. Differences are listed. Variables are declared per environment (names
  only) and no build bakes one environment's values into another.
- Evidence: source plus staging.

### DEL-02 Infrastructure as code
`advisory` · triggers: infrastructure code
- Verify: hosting, DNS, queues, buckets, schedules, access policies and alerts are declared in
  versioned code or a reproducible script and reviewed like code. Console changes are recorded and
  folded back; drift is checked.
- Evidence: source.

### DEL-03 Tested before deploy
`blocker` · always-on · triggers: CI, release scripts
- Verify: the deployed commit passed the repository's gates (lint, types, tests, build) from a
  clean checkout of a pushed commit, and a failing gate stops the deploy. The release contract's
  pushed-source and gate guarantees satisfy this control.
- Evidence: before the deploy, the CI run for the commit or the release script's gate list;
  after it, the release evidence (`release.json`).

### DEL-04 Rollback path
`blocker` · always-on · triggers: release scripts, migrations
- Verify: one documented command or button returns to the previous version and was exercised at
  least once. This release's migrations still work with the previous application version (DM-02).
  The release prints the exact rollback command.
- Evidence: release evidence plus an owner-attested or staging rollback exercise.

### DEL-05 Zero-downtime deploys
`blocker` · applies: `live` with stake · triggers: deploy config, health endpoints, migrations
- Verify: deploys roll out gradually or blue/green behind health checks, drain in-flight requests
  and jobs on shutdown, and keep old and new versions compatible during rollout (schema, API,
  queue messages, cached data).
- Evidence: source plus a staging observation.

### DEL-06 Feature flags
`advisory` · triggers: flag configuration
- Verify: risky or unfinished features ship behind flags with a kill switch, an owner and a
  removal date. Flag evaluation fails safe.
- Evidence: source.

### DEL-07 Capacity and scaling
`contract` (sla), otherwise `advisory` · triggers: scaling configuration
- Verify: autoscaling or documented headroom covers the expected peak (TST-04). Maximums respect
  downstream limits (DM-05, provider quotas). Queue consumers scale with depth.
- Evidence: staging load result plus production configuration.

### DEL-08 Edge delivery
`advisory` · applies: `ui` · triggers: hosting config, cache headers
- Verify: static assets are fingerprinted and served from a CDN with long immutable caching.
  HTML and private responses are not cached in shared layers. Latency is measured from the main
  customer regions.
- Evidence: staging or production headers.

### DEL-09 Domains, DNS and certificates
`blocker` · always-on (expiry) · triggers: DNS or infrastructure code
- Verify: certificates renew automatically and expiry is monitored with an alert weeks ahead.
  Public certificate lifetimes are shrinking year by year, so manual renewal is a finding.
  Domains auto-renew with a valid payment method and a registrar lock. DNS changes are versioned.
- Evidence: production (expiry dates read live) plus owner-attested registrar settings.

## ASY: async work and integrations

### ASY-01 Background work
`advisory` · triggers: request handlers that call slow or external work
- Verify: slow or external work (email, documents, imports, model calls, outbound webhooks)
  leaves the request path for a durable queue with timeouts, and the user gets a status to follow.
- Evidence: source.

### ASY-02 Retries with backoff
`blocker` · applies: `jobs`, `webhooks` or external calls · triggers: job code, API clients
- Verify: every outbound call has a timeout. Retries use capped exponential backoff with jitter,
  retry only retryable failures (timeouts, 429, 5xx), honour `Retry-After` and wrap idempotent
  handlers (DC-05).
- Evidence: source plus local tests against a failing fake.

### ASY-03 Dead-letter handling
`blocker` · applies: `jobs` · triggers: queue configuration
- Verify: work that exhausts its retries lands in a dead-letter queue or failed-jobs table with
  its error, alerts a human, and can be inspected and replayed safely.
- Evidence: source plus a staging run.

### ASY-04 Single-run schedules
`blocker` · applies: scheduled jobs with more than one instance · triggers: schedule configuration
- Verify: each scheduled job runs once per period across replicas (managed scheduler, leader
  election or database lock). Overlapping runs are prevented, missed runs have defined catch-up,
  and each run logs duration and outcome.
- Evidence: source plus a two-instance staging run, or the platform guarantee cited.

### ASY-05 Cache correctness
`advisory` · applies: caching · triggers: cache code
- Verify: every cache has an owner, a key that includes tenant and user for private data (SEC-08),
  a TTL, and invalidation on the writes that change it. Stale reads happen only where the product
  accepts them. A cache outage degrades service instead of failing it.
- Evidence: source plus a local write-then-read test.

### ASY-06 Inbound webhook processing
`blocker` · applies: `webhooks` · triggers: webhook routes
- Verify: beyond the signature check (SEC-22), events are deduplicated by provider event id,
  acknowledged fast and processed asynchronously, tolerate replay and out-of-order delivery (fetch
  current state when order matters), and are reconciled against the provider for missed events.
- Evidence: local tests that replay duplicate and out-of-order events.

### ASY-07 Outbound webhooks
`blocker` · applies: `public-api` with webhooks · triggers: webhook sender
- Verify: deliveries are signed with a rotatable secret and timestamp, retried with backoff,
  logged per attempt in a log customers can see, replayable, and disabled with notice after
  sustained failure.
- Evidence: source plus local.

### ASY-08 Third-party failure and drift
`advisory` · applies: external APIs · triggers: API clients
- Verify: each critical dependency's outage has a defined degraded behaviour (queue and retry
  later, read-only mode, a clear message), tested with a failing fake. Responses are validated at
  the boundary; unknown fields are tolerated; unexpected
  shapes fail loudly and alert instead of writing bad data. API versions are pinned where possible
  and provider changelogs have an owner.
- Evidence: source plus contract tests (TST-02).

### ASY-09 OAuth token lifecycle
`blocker` · applies: `oauth` · triggers: integration clients
- Verify: access tokens refresh before expiry under a lock so concurrent refreshes do not
  invalidate each other; rotated refresh tokens persist atomically; a revoked grant prompts the
  user to reconnect and stops retries. Tokens are stored encrypted (SEC-16).
- Evidence: local tests with an expiring fake.

## EML: email and notifications

### EML-01 Sender authentication
`blocker` · applies: `email` · triggers: DNS, email provider configuration
- Verify: every sending domain publishes SPF and DKIM and a DMARC policy aligned with the From
  domain, with reporting. Transactional mail is separated from marketing (subdomain or stream).
- Evidence: production (DNS records read live).

### EML-02 Bounces and complaints
`blocker` · applies: `email` · triggers: provider webhooks
- Verify: bounce and complaint events are processed; hard bounces and complaints suppress
  sending; support can see an undeliverable address; the complaint rate is monitored.
- Evidence: source plus provider configuration.

### EML-03 Rendering
`advisory` · applies: `email` · triggers: templates
- Verify: templates render in the clients customers use (dark mode and mobile included), carry a
  plain-text part, and are previewed before changes ship.
- Evidence: local or provider preview.

### EML-04 Notification preferences
`blocker` with `marketing-email`, otherwise `advisory` · triggers: notification code
- Verify: users can turn off each non-essential category. Marketing mail carries one-click
  unsubscribe (`List-Unsubscribe` per RFC 8058) and honours opt-outs within the mailbox
  providers' window.
- Evidence: source plus local.

## CST: cost

### CST-01 Storage lifecycle
`advisory` · triggers: storage configuration
- Verify: temporary uploads, exports, build artifacts and logs expire by rule; orphaned objects
  are cleaned; storage growth is visible.
- Evidence: production configuration or owner-attested.

### CST-02 Spend alerts
`blocker` · applies: `live` with stake · triggers: provider configuration
- Verify: each paid provider (hosting, database, model, messaging, monitoring) has a budget alert
  or hard cap that reaches a human the same day, and anomaly alerts catch sudden spikes such as a
  runaway agent loop.
- Evidence: owner-attested or provider configuration.

### CST-03 Staging idle between releases
`advisory` · applies: a staging environment · triggers: deploy configuration, schedule configuration, release scripts
- Verify: once production is deployed and proven live, staging runs nothing without a request:
  its configuration declares every trigger empty instead of inheriting production's; queue
  consumers, workflows, alarms and external schedulers aimed at it are off; and a staging
  database that holds nothing production lacks is exported and deleted, then recreated by the
  next release. The release shows zero scheduled runs and zero writes on staging.
- Evidence: deploy configuration plus the provider's schedule, consumer and analytics reads,
  or owner-attested.

## OBS: observability and incidents

### OBS-01 Structured logs
`advisory` · triggers: logger configuration
- Verify: logs are structured with level, time, request or trace id and safe tenant and user
  ids, searchable, and retained long enough for investigations. Redaction belongs to SEC-18.
- Evidence: source plus a redacted production sample.

### OBS-02 Error tracking
`blocker` · applies: `live` with stake · triggers: error tracker configuration
- Verify: server and client errors reach a tracker that groups duplicates, tags release and
  environment, and alerts on new or regressed issues rather than each occurrence.
- Evidence: source plus a test error seen in the tracker from staging.

### OBS-03 External uptime checks
`blocker` · applies: `live` with stake · always-on
- Verify: checks from outside the hosting network hit the health endpoint and one critical user
  flow on a schedule, alert a human, and are green now.
- Evidence: production (current check status) or owner-attested.

### OBS-04 Actionable alerting
`blocker` · applies: `live` with stake · triggers: alert configuration
- Verify: alerts on symptoms customers feel (error rate, latency, error-budget burn, queue age,
  failed payments) page a human through a channel that wakes someone. Each links a runbook. Noisy
  alerts are tuned or removed on a schedule.
- Evidence: owner-attested alert list plus a test page.

### OBS-05 Service dashboards
`advisory` · triggers: monitoring configuration
- Verify: per-service views show traffic, errors, latency percentiles and saturation, plus the
  business signals that matter (signups, payments).
- Evidence: owner-attested.

### OBS-06 Distributed tracing
`advisory` · applies: `multi-service` · triggers: tracing configuration
- Verify: a trace id propagates across services, queues and external calls, so one slow request
  can be followed end to end.
- Evidence: a staging trace.

### OBS-07 On-call
`blocker` · applies: `live` with stake
- Verify: a named primary and backup can be reached during the hours the product promises, with
  an escalation path and production access. The rotation is written down.
- Evidence: owner-attested.

### OBS-08 Runbooks
`advisory` · triggers: alert configuration
- Verify: each paging alert links a runbook: meaning, confirmation, mitigation, rollback and
  escalation.
- Evidence: source (docs).

### OBS-09 Postmortems
`advisory` · applies: `live`
- Verify: incidents get a blameless written review with owned, dated actions tracked to done.
  Each gap it finds becomes a project-local control in the ledger.
- Evidence: owner-attested.

### OBS-10 Status page
`contract` (sla), otherwise `advisory` · applies: `live`
- Verify: a status page hosted apart from the product shows current status and history and is
  updated during incidents.
- Evidence: production.
