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
`triggers`, and every binding and variable it reads. `scripts/release-contract-check.py`
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

**Schedules match the configuration.**
Done when the cron list the platform reports for the deployed Worker equals `triggers.crons`
for that environment. Documentation that says a schedule changed is a claim; the platform's
list is the fact.

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
