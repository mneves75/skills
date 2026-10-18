# Example: report freshness for a cached Worker

Original synthetic example. The service, numbers and events are invented to show the
procedure; they describe no real system.

## Context

An edge Worker serves a signed-in "weekly report" page. It renders from a cache that a
scheduled job refreshes from an upstream database every 5 minutes. The README says "99.9%
uptime"; nobody owns that number. No customer contract exists.

## Indicator specification

| Field | Content |
|---|---|
| Journey | A signed-in user opens their weekly report |
| Good event | The page rendered within 2 seconds, with data at most 15 minutes old when shown |
| Eligible event | Report page views by signed-in users; excludes requests for report IDs that do not exist (correct 404) |
| Weight | 1 per view |
| Window | Rolling 28 days |
| Collection | The Worker logs, per view, the data timestamp it rendered and the render time; the daily export sums good and eligible views. Blind spot: views that failed before the Worker ran (DNS, client network) are not counted |

The status code is not the indicator: during an upstream stall the Worker keeps returning HTTP
200 from an old cache.

## Supplied export (synthetic)

| Days | Eligible `N` | Good `G` | Note |
|---|---|---|---|
| 1–10 | 170,000 | 169,830 | |
| 11–12 | 34,000 | 31,280 | Upstream stall: every response was 200; 2,720 views showed data up to 3 hours old |
| 13 | none | none | Log export job failed; no data |
| 14–28 | 255,000 | 254,745 | 120 of the 255 bad views were identity-provider timeouts |

## Computation

Draft target `s = 0.995` (99.5%, from the previous quarter's observed compliance, not the
README's 99.9%).

**28-day window: `unknown`.** Day 13 has no data, so the window's compliance, remaining budget
and verdict are unknown. The export failure is its own finding.

**Observed subset (days 1–12 and 14–28, 27 of 28 days)**, shown for diagnosis only:
`N = 170,000 + 34,000 + 255,000 = 459,000`; `G = 169,830 + 31,280 + 254,745 = 455,855`; bad
weight `3,145`.

- Subset compliance `c = 455,855 / 459,000 = 0.99315` (99.31%).
- Subset burn rate `(1 - 0.99315) / 0.005 = 1.37`; the subset's bad weight exceeds its own
  allowance (`0.005 * 459,000 = 2,295`).
- This is not a 28-day miss. If day 13 had 200,000 eligible views, all good, the window would
  be `655,855 / 659,000 = 99.5228%`, above the target; a day 13 with many stale views would
  make it a miss. The missing day's traffic decides, so the verdict stays `unknown` until the
  day is re-exported.
- Days 11–12 alone are well outside the target: `31,280 / 34,000 = 92.0%`, burn 16. That is a
  finding whatever day 13 holds.
- The 120 identity-provider timeouts stay bad events; the attribution column says so.

Counted by status code alone, the stale views would look good: subset bad weight 425,
compliance 99.91%. The freshness specification is what exposes the stall.

## Draft alerts

Period 28 days (672 hours). A page when 2% of the budget burns within 1 hour, confirmed over 5
minutes: threshold `0.02 * 672 / 1 = 13.44`. A ticket when 10% burns within 3 days:
`0.10 * 672 / 72 = 0.93`. Both require at least 200 eligible views in the long window; with no
views, the rule reports a collection gap. Each page links the runbook "Report data stale".

These thresholds assume report views are spread evenly over the 28 days. Weekly reports are
likely to cluster on some days, which this export does not show; at a peak hour a burn of 13.44
spends more than 2% of the budget, at night less. The owner checks the hourly shape on recent
history before adopting the rules.

## Report

1. Owner decisions: re-export day 13, so the 28-day result can be computed; adopt or change the
   99.5% freshness target (name an owner, a date and a review date); decide whether "99.9%
   uptime" stays in the README, since it is neither measured nor adopted; approve the draft
   alerts after checking the traffic assumption.
2. Status: `draft`. It blocks nothing and pages no one until adopted.
3. Evidence limits: computed from the supplied export only; the 28-day result is unknown
   because day 13 is missing, and the 99.31% figure covers the other 27 days only; views that
   failed before the Worker ran are not counted; no live system was observed.
4. Follow-up: the upstream stall and the silent export failure are worth a review with
   `mneves-incident-learning`.
