# Specification and arithmetic

## The specification

Write these fields for every indicator, in this order. The first five are the specification;
the last is the implementation. Changing how an indicator is collected never changes what it
means.

| Field | Content |
|---|---|
| Journey | The user action it protects ("open the weekly report", "sync an offline edit") |
| Good event | What the user experienced as success: correct content, fresh enough, within the latency bound |
| Eligible event | Which attempts count: real user attempts, excluding only those the user caused (malformed input the product correctly rejected) or explicitly out of scope |
| Weight | 1 per event, or the unit of user value (items in a batch, bytes, seats) when events differ |
| Window | Rolling or calendar, and its length |
| Collection | Where it is measured (client, edge, service, data store), the query, and its known blind spots |

Measure as close to the user as practical. A server-side success rate misses requests that
never arrived; a client-side measure may miss users who gave up before loading it. Name the
blind spot instead of hiding it.

### Outcome, not transport

- A response is good only if its content is what the user needed. Status codes, health
  checks and "process is up" are collection shortcuts and must be justified against the good
  event.
- **Freshness**: the age of the data the user saw at the moment it was shown. A cached page
  served with HTTP 200 from data older than the bound is a bad event.
- **Completeness and durability**: for offline or queued work, a good event is an item that
  reached durable storage within the window, counted from the client or the queue, not from
  the endpoint that accepted it. An acknowledgement proves only what its contract guarantees
  (received, queued or durably committed); state which, from code or documentation, before
  counting it as durable. A missing acknowledgement can follow a successful write, and an
  undelivered item is incomplete delivery, not proven loss; permanent loss needs its own
  evidence (the source no longer holds it and no copy or retry remains).
- **Latency**: a threshold on the user-visible time, counted as good or bad per event.
  Averages hide the tail and are not indicators.

### What counts as bad, whatever the cause

- Failures caused by a provider, CDN, payment processor, identity service or the network stay
  bad events. A separate column may attribute them; they are never removed from compliance.
- Planned maintenance counts unless the user was told in advance and the owner's adopted
  objective explicitly excludes announced windows.
- Correctness, data loss, data exposure and integrity failures are not budget. Report them as
  bad events and also route them to the readiness or security review; no budget makes them
  acceptable.

## Arithmetic

Inputs for one indicator and window: eligible weight `N`, good weight `G` (`0 <= G <= N`), and
target `s` written as a fraction (99.5% is 0.995).

| Quantity | Formula | Defined when |
|---|---|---|
| Compliance `c` | `G / N` | `N > 0` |
| Bad fraction | `(N - G) / N` | `N > 0` |
| Allowed bad weight | `(1 - s) * N` | `N > 0` and `0 < s < 1` |
| Burn rate | `(1 - c) / (1 - s)` | `N > 0` and `0 < s < 1` |
| Remaining budget fraction | `1 - (N - G) / ((1 - s) * N)` | `N > 0` and `0 < s < 1` |

Rules:

1. **No data is unknown.** `N = 0`, a missing export or a collector outage gives `unknown` for
   every quantity. Never substitute 100% (nothing failed) or 0% (nothing succeeded). Report the
   collection gap as its own finding.
2. **Partial coverage keeps the full window unknown.** When part of the window has no data,
   the full window's compliance, budget and verdict are `unknown`. Figures for the covered part
   may be shown, labelled "observed subset" with the covered span, and never stated as the
   window's result or turned into a miss or a pass: the missing part's traffic can move the
   total either way. Only when the missing part's eligible weight is known or bounded, report
   the best and worst case; if they fall on both sides of the target, the verdict stays
   `unknown`. Name what would close the gap (re-export, backfill, the producer's count).
3. **Weighted sums, not averages of ratios.** With batches of different size, sum good and
   eligible weights across all batches, then divide once. The mean of per-batch ratios lets
   one tiny batch outweigh a large one.
4. **100% targets.** With `s = 1` there is no budget: allowed bad weight is 0 and burn is
   `undefined`. Report the count of bad events; any bad event is a miss. Most 100% wishes are
   correctness properties ("every payment recorded exactly once") that need a test and an
   owner, not an objective.
5. **`s = 0` or `s` outside (0, 1]** is not an objective; ask what was meant.
6. **Burn rate is a normalised error fraction.** It compares one window's bad fraction with the
   allowed fraction; it says nothing about traffic volume or time left. For an event-based
   objective, a window contained in the period used `burn_window * N_window / N_period` of the
   period's budget, when both populations are known. A forecast of when the budget runs out
   needs the remaining budget and a stated assumption about remaining traffic; never infer it
   from burn alone. A negative remaining budget over the whole period, with full coverage,
   means the objective was missed.
7. **Low traffic.** With few events, one failure swings compliance widely. State `N` next to
   every figure. Prefer longer windows, synthetic probes clearly labelled as such, or a count
   target ("no more than 2 failed checkouts per week") over a percentage that two events can
   break. Never pad `N` with synthetic traffic in the user indicator.
8. **Rounding.** Keep full precision through the calculation; round only the reported figure,
   and never round a miss into a pass (98.96% against 99% is a miss).
9. **Period budget and burn window are different populations.** Budget consumed is measured
   against the whole period's eligible weight; a burn rate describes one alert window. With a
   99.9% objective and 1,000,000 eligible events in the period, 100 failures consume 10% of the
   period budget (allowed 1,000). One contained hour with 1,000 events and 20 failures has a
   burn rate of `(20 / 1000) / 0.001 = 20`; it used `20 * 1,000 / 1,000,000 = 2%` of the
   period budget (20 of the 1,000 allowed failures). Never report that hour as "2,000% of the
   budget": the hour's own allowance (1 failure) is not the period budget.
10. **Completeness needs an expected count from an independent source.** "Every item arrived"
   compares what reached durable storage with what the producer created, counted by the
   producer (a client-side counter, a sequence number, the source system's export). 99 of 99
   observed items is not complete when 100 were created. When nothing independent records the
   expected count, completeness is `unknown`; name the counter that would close the gap.

## Checking someone else's numbers

Recompute from the stated `N`, `G` and `s`. Check that the eligible set matches the
specification, that provider failures were not dropped, that no-data periods are `unknown`
rather than perfect, that a window with a gap is not reported as a full-window result, and
that weights were summed, not averaged. A figure without its inputs is a claim, not evidence.

## Sources

Concepts, not text, follow these public references; check the current edition when a decision
depends on wording:

- Google SRE book, "Service Level Objectives": https://sre.google/sre-book/service-level-objectives/
- Google SRE workbook, "Implementing SLOs": https://sre.google/workbook/implementing-slos/
