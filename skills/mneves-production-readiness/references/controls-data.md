# Controls: data model, recovery and correctness

Each control states its tier, the profile flags that make it apply, and the paths whose change
triggers reassessment in a delta. `Verify` says what to inspect or run; `Evidence` names the
minimum scope that can mark it PASS. Tiers, flags and scopes are defined in `gates.md` and
`ledger.md`.

## DM: data model and database

DM-01 Designed schema
`blocker` · applies: `db` · triggers: schema, migrations, ORM models
- Verify: a reader can explain the entity model. Primary keys, foreign keys, unique, not-null and
  check constraints encode the rules the code relies on (code that assumes unique emails has a
  unique index on the normalized form). Tenant-owned rows carry the tenant key. Each fact has one
  source of truth. JSON columns hold only data that is never filtered or joined.
- Evidence: source.

DM-02 Reversible migrations
`blocker` · applies: `db` · triggers: migrations
- Verify: every migration in scope has a tested way back or forward: a down step that was run,
  or a written forward fix that names the data it cannot restore. Destructive steps (drop, narrowing type change, rewrite) ship
  apart from the release that stops using the data (expand, migrate, contract) and follow a
  recovery point. The previous application version still runs against the new schema, so an
  application rollback never needs a schema rollback.
- Evidence: source plus an up-and-down run on a local or staging copy.

DM-03 Lock-safe migrations
`blocker` · applies: `db` · triggers: migrations
- Verify: for each DDL statement, look up the lock it takes and whether it rewrites the table in
  the engine's documentation. On large or busy tables use the online form: concurrent index
  builds, constraints added unvalidated and validated later, nullable columns with batched
  backfills, renames through expand and contract. Check the engine version: on current PostgreSQL,
  adding a column with a constant default does not rewrite the table, while a volatile default or
  a type change does. Migrations set a lock timeout and a statement timeout, because a waiting
  exclusive lock queues every later query. Large backfills run as
  batched jobs outside the migration transaction.
- Evidence: source plus a staging run on production-sized data, or row counts that prove the
  table is small.

DM-04 Indexes for production volume
`blocker` · applies: `db` · triggers: queries, repositories, migrations
- Verify: every request-path query on an unbounded table has indexes for its filter, join and
  sort columns. Read the query plan on production-sized synthetic data. Find N+1 loops, missing
  limits, unbounded list queries and leading-wildcard searches. Report unused or duplicate
  indexes as advisory.
- Evidence: local or staging query plans on representative volume.

DM-05 Connection management
`blocker` · applies: `db` · triggers: database client config, scaling config
- Verify: pool size times maximum instances (serverless concurrency and workers included) stays
  below the database connection limit, with headroom for migrations and administration.
  Serverless and edge runtimes use a pooler or an HTTP driver. Pools have acquire and idle
  timeouts. Long transactions are bounded.
- Evidence: source plus the provider's limit (config or owner-attested).

DM-06 Recoverable deletes
`advisory` · applies: `db` and records that users delete · triggers: delete paths, models
- Verify: user-facing deletes of business records are soft deletes or archives with a restore
  window. Normal queries and unique constraints account for deleted rows. A purge job applies the
  retention schedule (DC-10, CMP-06).
- Evidence: source.

DM-07 Evolvable data model
`advisory` · applies: `db` · triggers: models, tenant configuration
- Verify: customer-specific behaviour lives in configuration, entitlements or flags, not in
  per-customer code paths or columns. Identifiers are opaque and never reused. A second customer's
  "small change" (a custom field, a setting) fits without a schema fork.
- Evidence: source.

## BR: backup and recovery

BR-01 Automated backups
`blocker` · applies: `db` or other state the product cannot regenerate · triggers: infrastructure config
- Verify: backups run at least daily for every persistent store, are encrypted, keep the stated
  retention, survive the loss or compromise of the primary account or project, and alert a human
  when a backup fails.
- Evidence: production configuration or owner-attested.

BR-02 Restore tested
`blocker` · applies: `db` or other state the product cannot regenerate · always-on (expiry)
- Verify: a restore from a real backup into an isolated environment finished within the evidence
  window. The record states duration (recovery time), data-loss window (recovery point), the
  steps and a data check (row counts or checksums). The procedure re-applies pending erasures
  before restored data serves users.
- Evidence: owner-attested or staging; expires (see `gates.md`).

BR-03 Point-in-time recovery
`blocker` · applies: `db` with user writes · triggers: infrastructure config
- Verify: point-in-time recovery (log archiving or provider time travel) is on, with retention
  longer than the time needed to notice a bad write. A runbook restores selected rows or tables to
  a side database and copies them back, not only a full rollback.
- Evidence: production configuration or owner-attested.

BR-04 Disaster recovery plan
`blocker` · applies: `live` with stake · always-on (expiry)
- Verify: a written plan covers provider or region outage, account lockout or compromise, data
  corruption and loss of a key person. It names recovery targets, contacts and steps, is stored
  outside the system it recovers, and was exercised (tabletop or real) within the window.
- Evidence: owner-attested; expires.

BR-05 Multi-region continuity
`contract` (sla) · triggers: infrastructure config
- Verify: when a contract promises more availability than one region delivers, data replicates
  to a second region and failover was exercised. Otherwise the contract matches the single-region
  reality.
- Evidence: production configuration plus owner-attested exercise.

## DC: data correctness

DC-01 Identifiers and text
`blocker` · applies: `accounts` or user input · triggers: auth, forms, models, templates, exports
- Verify: email addresses accept valid local parts including `+`, are normalized the same way at
  signup, login, reset and invitation, and are URL-encoded in links. Names and free text with
  apostrophes, quotes, emoji, combining accents and right-to-left scripts round-trip through form,
  API, database, email, export and PDF unchanged. Unicode normalization happens once; lengths are
  measured as the database measures them. Encoding happens at output (SEC-11), never by stripping
  valid characters on input. Test with a fixture set such as `O'Brien`, `Zoë`, `李`, `عربي`,
  `👩🏽‍💻` and `a+b@example.com`.
- Evidence: local tests with the fixture set.

DC-02 Time and time zones
`blocker` · applies: scheduling, reminders or time-based billing · triggers: timestamp models, schedulers, notifications
- Verify: instants are stored in UTC with time-zone-aware types. Future local events (a 9 a.m.
  reminder) store local time plus an IANA zone, not a precomputed instant. Tests cross
  daylight-saving transitions. Schedules state their zone; display uses the viewer's zone.
- Evidence: local tests across transitions.

DC-03 Money representation
`blocker` · applies: `payments` or stored money amounts · triggers: models, pricing, billing code
- Verify: amounts are integers in minor units or exact decimals; binary floating point never
  appears in storage, arithmetic or serialized payloads. Every amount carries its ISO 4217
  currency. Conversions to the payment provider's units are explicit and tested.
- Evidence: source plus local tests.

DC-04 Currency and rounding
`blocker` · applies: multiple currencies, tax, discounts or proration · triggers: pricing, billing, tax code
- Verify: minor-unit exponents come from currency data, not a fixed two. Each operation states its
  rounding mode, matching the provider and the invoice. Splits and allocations neither lose nor
  create a cent. Exchange rates record source and time. Test with zero-, two- and three-decimal
  currencies.
- Evidence: local tests.

DC-05 Idempotent side effects
`blocker` · applies: `payments` or external side effects · triggers: payment, order, webhook and job handlers
- Verify: operations that charge, send, ship or write to another system take an idempotency key,
  store it with the outcome and return the stored outcome on retry. Keys pass through to providers
  that accept them. No retry layer (client, gateway, queue) can repeat the side effect.
- Evidence: local test that replays the same request.

DC-06 Duplicate submissions
`blocker` with `payments`, otherwise `advisory` · triggers: forms, create endpoints
- Verify: four rapid submits, a double tap or a network retry create one record, through a
  server-side key or natural unique constraint plus a client control that disables while pending.
- Evidence: local test with concurrent identical requests.

DC-07 Pagination at depth
`advisory` · applies: lists over growing tables · triggers: list endpoints, queries
- Verify: large lists use keyset or cursor pagination with a stable unique order, the server caps
  page size, and page 400 is as fast as page 1. Exact totals are estimated or cached when costly.
- Evidence: local or staging timing on production-sized data.

DC-08 Customer data export
`advisory` · applies: `accounts` · triggers: export features
- Verify: customers export their own data in a documented open format. Exports are tenant-scoped,
  streamed or queued for size, UTF-8 and spreadsheet-compatible, and neutralize cells that start
  with `=`, `+`, `-` or `@`.
- Evidence: local.

DC-09 Robust import
`advisory` · applies: import features · triggers: import code
- Verify: imports accept UTF-8 with or without a byte-order mark, Windows-1252 and UTF-16, common
  delimiters, quoted newlines and regional date and number formats. A dry run reports row-level
  errors before commit. Size and row limits apply. Re-uploading the same file is safe.
- Evidence: local tests with malformed and legacy fixtures.

DC-10 Retention enforced
`contract` (retention) · triggers: jobs, models, storage configuration
- Verify: each retention promise (contract, policy, regulation) maps to a scheduled deletion or
  anonymization job that also covers search indexes, caches, analytics, object storage and logs,
  and has a test. Backups age out on schedule.
- Evidence: source plus a job run in staging or production.
