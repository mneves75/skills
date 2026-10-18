# Adoption, alerting and integration

## Draft and adopted

Every objective carries one status.

| Status | Requires | Effect |
|---|---|---|
| `draft` | nothing | Informational. Never blocks a release, pages a person, freezes work or becomes a contract. |
| `adopted` | a named owner, an adoption date and a review date, recorded where the project keeps decisions | The owner commits to watching it. Still no automatic gate, release freeze or feature disable. |

Every report states, for each objective, its status, owner, adoption date and review date. A
field the sources do not supply reads `pending`; a draft lists the owner decision that would
fill it.

A number in a README, a dashboard title or a sales page is `draft` until the owner adopts it.
An agent never adopts a target, never extends an adoption past its review date, and never
treats an expired review date as still adopted: report it as `adopted (review overdue)`.

A contractual SLA is a separate commitment to customers with its own remedies. An objective
is not an SLA. When an SLA exists, report whether the adopted or draft objective is at least
as strict and whether the observed compliance would have met it; do not edit either.

## Choosing a target

- Start from observed compliance over a representative window and from what users notice. A
  target well above history is a wish; one well below it hides regressions.
- Every extra nine cuts the allowed bad weight tenfold; name what it would cost (redundancy,
  on-call, slower releases) before proposing it.
- Prefer few indicators per journey (availability with correctness, latency, freshness) over
  many.
- Correctness properties (money, data integrity, access control) are not targets; they are
  tests and controls.

## Burn-rate alerts (draft)

Alert on how fast the budget is being consumed, not on single errors. The conventional
threshold for "consume a fraction `f` of the period's budget within alert window `w`" is
`f * period / w`. For a 30-day period (720 hours), spending 2% of the budget in 1 hour is a burn
rate of `0.02 * 720 / 1 = 14.4`.

That formula is a design approximation. It holds when eligible traffic is spread evenly over
the period, or for a time-based indicator (good minutes). With uneven traffic, a window's actual
share of the budget is `burn * N_window / N_period`: at peak hours the same burn spends more,
at quiet hours less. State the assumption next to every threshold, check it against recent
history when there is any, and never read a burn rate as a time until the budget runs out.

- Pair a long window with a short one (for example one-twelfth of it) and fire only when both
  exceed the threshold, so the alert stops soon after the problem does.
- A fast, severe burn pages a human; a slow burn opens a ticket.
- Each paging alert links a runbook (meaning, confirmation, mitigation, rollback, escalation).
- Low traffic makes burn rates jumpy: require a minimum `N` in the alert window, or alert on a
  count of bad events instead.
- With `N = 0` in a window, the alert reports a collection gap, not health.

Present the rules, their thresholds and the expected pages per month on recent history as a
draft for the owner. Changing alert destinations or rotations is an owner action.

## Budget policy (owner decision)

A budget policy says what the team does when the budget runs low or out: for example,
prioritise reliability work, require an extra review for risky changes, or hold a feature
launch. It is written and signed off by the owner and the people it binds. This skill may
draft one; it never enforces one, never turns it into a release gate and never disables a
feature. A missed objective is an input to planning and to `mneves-incident-learning`, not an
automatic consequence.

## Integration with readiness

When `mneves-production-readiness` is installed, these map to existing controls; nothing here
creates a control or a verdict.

| Readiness control | What this skill can supply |
|---|---|
| OBS-04 Actionable alerting | Adopted objective, burn-rate alert rules and a test page (the page itself is owner-attested) |
| OBS-05 Service dashboards | Indicator queries and their blind spots |
| OBS-08 Runbooks | The runbook link each paging alert needs |
| DEL-07 Capacity and scaling, BR-05 Multi-region | Whether an SLA's availability promise matches observed compliance and the architecture |
| BR-02, BR-04 recovery targets | Nothing: recovery time and point are measured by restore exercises, not objectives |

An objective's evidence scope follows the readiness rules: a query in source is `source`; a
computed figure from a staging or production export is that scope; an adoption is
`owner-attested`.

## Sources

Concepts, not text, follow these public references; check the current edition when a decision
depends on wording:

- Google SRE workbook, "Alerting on SLOs": https://sre.google/workbook/alerting-on-slos/
- Google SRE workbook, "Error Budget Policy": https://sre.google/workbook/error-budget-policy/
