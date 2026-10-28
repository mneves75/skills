# Cloudflare release checks

Checks for a Workers or Pages release that a green deploy command does not make. Each one ends
on a condition you can observe. Run the ones that apply before the first deploy to a target,
and the live ones after every deploy. The repository's own release script owns the commands;
this file says what must be true.

## Configuration, before the deploy

**Environments inherit less, and more, than expected.** A Wrangler environment inherits
`route`, `routes`, `triggers` and `workers_dev` from the top level. It does not inherit `vars`
or bindings (KV, R2, Durable Objects, services, queues, workflows). A staging environment
without its own `routes` therefore deploys onto production's routes, and one without its own
bindings deploys with none.
Done when every environment sets its own `routes` (an empty list when it has none), its own
`triggers` (staging's with an empty `crons` list: see [Staging off](#staging-off-after-production)),
and every binding and variable it reads. `scripts/release-contract-check.py`
reports this as `cf.env-routes`, `cf.env-triggers` and `cf.env-bindings`.

**Build-time values belong to the target.** A frontend that bakes a public key or an API
origin into its bundle is built once per target.
Done when the release asserts that the built bundle contains the target's value, and the live
page serves that value.

**Secrets exist on the target.**
Done when the secret names listed for the target (`wrangler secret list`) include every secret
the Worker reads. Compare names only; never print a value.

**A same-origin API proxy reaches the Worker through a service binding.** A proxy that fetches
a public `workers.dev` URL breaks when the account subdomain changes and hands the Worker the
proxy's address as the client IP, which turns a per-client rate limit into a global one.
Done when a request through the public domain proves the binding path, for example a response
header the Worker sets only for binding traffic.

**The Worker's tests run on the Workers runtime.** The runtime rejects some options Node
accepts, and a mocked store proves nothing about D1 or KV.
Done when the changed behavior has a test that runs under `wrangler dev` or the Workers test
pool against the real local store.

## Data, before a migration

Done when all three hold: a dated export of the database exists outside the database; a
recovery point is recorded (for D1, a Time Travel bookmark); pending migrations were scanned
for destructive statements, and any found has its own explicit approval. A rollback reverts
code. It does not revert data, secrets or bindings.

## Live, after every deploy

**The right deployment is serving.** A Pages deploy to a branch other than the project's
production branch creates a preview while the canonical host keeps serving the old build.
Done when the canonical host serves the released commit (see the release contract), not when
the deploy command prints a URL.

**The first read can be stale.** An edge location may still answer with the previous version,
and a zone rule may cache HTML. A first deploy to a custom domain also waits for its DNS
record and certificate.
Done when the served commit matches on repeated reads over a short backoff. When a zone rule
caches HTML, purge it and read again.

**A static site with a single-page fallback answers 200 to everything.** With
`not_found_handling` set to `single-page-application`, every GET returns the HTML shell,
including a missing asset and a path that should not exist.
Done when the live proof checks that the entry script comes back as JavaScript, and its
negative control is a method the site refuses (for example `OPTIONS /` answering 405), not a
missing path.

**Schedules match the configuration.**
Done when the cron list the platform reports for the deployed Worker equals `triggers.crons`
for that environment. Documentation that says a schedule changed is a claim; the platform's
list is the fact.

## Staging off, after production

Once production is deployed and proven live, staging must run and bill nothing while no
release is in it. An idle Worker that only answers requests may stay, so its secrets survive.
Everything that runs without a request goes. Staging's Worker is named
`<name>-<environment>` (for example `demo-worker-staging`); every command below uses that name.

**Crons.** `env.staging` declares `"triggers": {"crons": []}`, never inherits the top-level
list, and a deploy of that configuration removes every cron. Changes take up to 15 minutes to
propagate. A scheduled job is exercised on staging only with a one-off manual trigger.
`scripts/release-contract-check.py` reports a staging environment that inherits or declares a
cron as a `cf.env-triggers` FAIL.
Done when `GET /accounts/{account_id}/workers/scripts/<staging-worker>/schedules` returns an
empty `schedules` list after the propagation window.

**Queue consumers.** A deploy does not detach a consumer the configuration no longer lists.
Run `wrangler queues consumer remove <queue> <staging-worker>`. Pausing delivery
(`wrangler queues pause-delivery <queue>`) pauses the whole queue, so use it only on a queue
staging owns alone.
Done when `wrangler queues consumer list <queue> --json` prints `[]` for each staging queue.

**Workflows.** A staging Workflow needs its own name, because Workflow names are account-wide.
A Workflow can carry its own `schedules`, and removing them from the configuration may not
clear them: delete the staging Workflow with `wrangler workflows delete <name>`, which also
deletes its instances. Take `<name>` from the staging environment's `workflows` entry and
compare it with every other environment's and the top level's: a name that appears outside
staging is shared with production, so stop and report it instead of deleting.
Done when `wrangler workflows instances list <name> --status running --json` and the same with
`--status queued` print nothing, or the Workflow no longer exists.

**Durable Object alarms.** Nothing outside the object can list or cancel an alarm: only the
object's code (`deleteAlarm()`, or `deleteAll()` on a compatibility date of 2026-02-24 or
later) turns one off. Without such a code path the alarm row is NOT TESTED; say so.

**External schedulers.** A CI cron, launchd job or other host scheduler that calls staging is
turned off where it lives. A GitHub Actions run that GitHub refused to start over billing is
already not running; record it as such and do not count it as a scheduler that was stopped.

**The staging D1 database.** Delete it when it is unused: it holds nothing production lacks,
and no release is in staging. In order, stopping and reporting at the first step that fails:

1. Read its identity: `wrangler d1 info <name> --json` (uuid, `write_queries_24h`,
   `rows_written_24h`), with `<name>` taken from the staging environment's `d1_databases` and
   nowhere else. Compare the uuid with every `database_id` and the name with every
   `database_name` in the Wrangler configuration: both must equal the staging environment's
   entry and differ from the top level's and every other environment's. Quote the compared
   values in the report. Any match outside staging, a missing staging entry or an id that
   cannot be read stops the deletion.
2. Confirm it holds nothing production lacks. A staging database that served as the only copy
   of anything (an import, a hand-entered record, a test the owner relies on) is reported for
   the owner, not deleted.
3. Export it: `wrangler d1 export <name> --remote --output=<file>.sql`, to the release's
   private evidence location, and check the file is non-empty.
4. Delete it: `wrangler d1 delete <name> --skip-confirmation`. Report the name, uuid and
   export path.

The next release recreates it before its staging stop: the database, its id in staging's
configuration, and the migrations.

**Proof that staging is idle.** The release is done when each item above has its Done check,
and staging shows zero writes: the `d1AnalyticsAdaptiveGroups` dataset (GraphQL Analytics,
`sum { writeQueries rowsWritten }` filtered by `databaseId` and date) reads zero for a staging
database that stays, and `workflowsAdaptiveGroups` counts no `WORKFLOW_START` events for
staging's Workflows. No documented dataset isolates cron invocations: the empty schedules list
is that evidence, and Workers Logs (seven days, when staging has observability on) is the
event-level confirmation. Report each check that could not run as NOT TESTED.

## Review check: no shared cache in front of identity

A response that depends on a cookie or an `Authorization` header never passes through a shared
cache whose key ignores that identity. Four caches qualify:

- **Workers Cache**, switched on by `cache.enabled` in the Wrangler configuration, for the
  whole Worker or for one entrypoint under `exports`. Its key does not include `Cookie`.
  Cloudflare bypasses it in three cases: the response sets a cookie; the response says
  `private` or `no-store`; the request carries `Authorization` and the response is not
  marked `public`, `must-revalidate` or `s-maxage`. A request that only carries a session
  cookie gets none of these. Its response is stored, for two hours when it sets no
  `Cache-Control`, and the next signed-in user on that path receives it. Callers that
  arrive through a service binding are kept apart by `ctx.props`.
  `scripts/release-contract-check.py` reports the setting as `cf.worker-cache`.
- The **Cache API** in code (`caches.default`, `caches.open`).
- `cacheEverything` on a subrequest.
- A **zone cache rule** that covers the path.

Done when all three hold: each cache that is on is listed with the reason its responses are
identical for every user; every response that depends on identity is sent `private, no-store`;
and the proof exercises two signed-in users. A proof that covers only the signed-out path
proves the wrong thing.
