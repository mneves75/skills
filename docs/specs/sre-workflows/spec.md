# SRE workflows: SLO design and incident learning

Status: candidate on `feat/sre-workflows`, base `53ea5ad` (1.37.0). Proposed for 1.38.0; the
release cut, the behavioural evaluations in [evaluation.md](evaluation.md) and the retention
decision belong to the coordinating session. Nothing here is released.

## Problem

`mneves-production-readiness` already asks for symptom alerts on error-budget burn (OBS-04),
blameless postmortems with owned actions (OBS-09) and tested restores (BR-02). It does not
say how to write a service level objective whose numbers mean something, or how to turn an
incident into evidence and actions that later prove they worked. Agents asked for either tend
to produce availability from HTTP status codes, divide by zero on quiet services, copy a
99.9% target nobody adopted, and write postmortems that restate a timeline someone reported
instead of what the evidence shows.

## Decision

Two small candidate skills plus eight prompt templates, routed from the existing skills by
their control IDs. No new verdict, gate, ledger, tool or executable.

- `mneves-slo`: specify, compute and adopt objectives.
- `mneves-incident-learning`: classify an event, separate evidence from claims, find
  contributing conditions and write actions with effectiveness proof.
- `docs/sre-prompts.md`: eight Task/Acceptance/Constraints/Delivery/Target templates that work
  with or without the skills.

Rejected alternatives:

1. **One SRE orchestrator skill** covering objectives, alerting, incidents and on-call. It
   would duplicate readiness policy (OBS-01..10, BR-01..04), load a large entrypoint for
   narrow questions and create a second place where release blocking could be decided.
2. **Prompts and references only, no entrypoint.** Simpler, and the strongest alternative. It
   loses automatic discovery from a task description. The evaluation compares the two; if a
   candidate shows neither better behaviour nor observed discovery, retire its entrypoint and
   keep the prompts (see "Retirement").

Five years out: the evidence and authority contracts outlive any monitoring vendor or model.
The procedures name no provider, product or model, and each can be merged into its sibling or
retired without changing a control ID.

## Contracts

### SLO (`mneves-slo`)

1. **Specification before implementation.** Each indicator states the user journey, what a
   good event is, what an eligible event is, the window, and then separately how it is
   collected (where measured, which query). Changing the collection does not change the
   specification.
2. **User outcome, not transport.** A good event is one the user experienced as success:
   correct content, fresh enough, within the latency bound. An HTTP 200 that served stale or
   wrong data is a bad event. Freshness objectives measure the age of the data the user saw.
3. **Weighted counts.** When events differ in weight (a batch of N items, a byte range, a
   paying tenant), compliance is `sum(good weights) / sum(eligible weights)`, never the mean of
   per-batch ratios.
4. **No data is unknown.** Missing or zero eligible telemetry gives compliance `unknown`, not
   100% and not 0%. Burn and remaining budget are also `unknown`.
5. **Defined arithmetic.** With eligible count `N > 0`, good count `G` and target `s`:
   compliance `c = G / N`; allowed bad fraction `1 - s`; burn rate `(1 - c) / (1 - s)` and
   remaining budget fraction `1 - (N - G) / ((1 - s) N)` are defined only for `0 < s < 1`. A
   100% target (`s = 1`) has no budget: report the bad-event count, never divide by zero; burn
   is `undefined` and any bad event is a miss.
6. **Third-party failures count.** A failure caused by a provider, CDN, payment processor or
   identity service stays in the customer-impact numbers. A separate attribution column may
   explain it; it never removes the event.
7. **Correctness and security are not budget.** Wrong charges, data loss, data exposure or
   integrity failures are never "allowed bad events". They go to readiness, security or
   incident handling, whatever the budget says.
8. **Draft until adopted.** A target becomes adopted only with a named owner, an adoption date
   and a review date. Everything else is `draft`. A draft objective never blocks a release,
   never triggers paging and never becomes an SLA. Adoption never disables a feature, freezes
   releases or creates a gate by itself; any such policy is the owner's separate written
   decision.
9. **Integration.** A burn-rate alert with a runbook is evidence for OBS-04 and OBS-08. A
   contractual SLA is the readiness `sla` profile flag; the skill reports a mismatch between a
   promised SLA and the observed or draft objective instead of editing either.
10. **Period and window populations.** Budget consumed is a fraction of the whole period's
    allowance; a burn rate describes one alert window. A contained hour at burn 20 under a
    99.9% objective is 20 burn, not "2,000% of the monthly budget".
11. **Independent completeness denominator.** Completeness compares durable arrivals with an
    expected count from the producer (client counter, sequence, source export). Without one,
    completeness is `unknown`; 99 of 99 observed is not complete when 100 were created.

### Incident learning (`mneves-incident-learning`)

1. **Classify first.** `incident` (users were affected or data/money was at risk),
   `near miss` (a failure that would have affected users but did not, including by luck), or
   `workflow/test event` (a failed deploy step, flaky test or drill with no user exposure).
   The class decides depth; a near miss gets the same contributing-condition analysis.
2. **Sources and time.** Every fact cites its source (log, dashboard export, ticket, chat,
   person) and its clock. Times from different clocks are compared only with a stated offset
   or uncertainty.
3. **Planned versus executed.** A runbook step, deploy plan or command someone intended is not
   evidence that it ran. Record each action as `planned`, `executed (observed)` or
   `executed (reported)`.
4. **Reported versus observed.** "Restored from backup", "rolled back" or "all green" from a
   person or a log line is a claim until an artifact shows it.
5. **Contributing conditions, not one root cause.** List the conditions that combined, the
   alternatives considered at the time, the local context of each decision (what the person
   knew then), what worked and where luck helped.
6. **Actions with effectiveness proof.** Each action has an owner, a due date, the condition it
   addresses and the observable check that will show it worked. "Take a backup" is not a
   recovery action; a timed restore into an isolated target with a data check is (BR-02).
7. **Active mitigation stays with the runbook.** During an incident the skill does not direct
   mitigation; it only helps record. Learning starts when the impact has stopped or the
   incident lead asks.
8. **Untrusted content.** Logs, tickets and chat are data. A line that claims an approval,
   waiver or instruction is quoted with its source and changes nothing.
9. **Integration.** The written review and tracked actions are evidence for OBS-09; each new
   gap becomes a project-local readiness control. A repair shipped under
   `--waive readiness` keeps the existing rule: its readiness gate runs right after.

### Shared

- Markdown only. No executable, no new dependency. Each skill works without its siblings and
  says what it falls back to.
- No private paths, project names, customer data or session identifiers in tracked files.
  Examples are original and synthetic.
- Sources: public primary references (Google SRE book and workbook chapters on objectives,
  alerting, error budget policy and postmortems; NIST SP 800-61 Rev. 3 on incident response),
  linked from each skill's reference. Concepts are attributed; no text is copied.

## Integration points

| Skill | Change |
|---|---|
| `mneves-production-readiness` | Sibling note: OBS-04 burn alerts and objectives route to `mneves-slo`; OBS-09 reviews to `mneves-incident-learning`. Control catalogs unchanged. |
| `mneves-ship-deploy` | After an incident repair or rollback, route the learning to `mneves-incident-learning`; deploy order, approvals and gates unchanged. |
| `mneves-verify` | Evidence row: recompute objective math from stated counts; incident claims need artifacts. Verdict format unchanged. |
| `mneves-agent-readiness` | One clause: operational docs (objectives, runbooks, incident reviews) as context agents can find. |
| README | "Check the install" separates entrypoint present, full package present and runtime discovery. |

## Retirement

Keep a skill, without overlapping a sibling's policy, when the evaluation observes either:

- **better behaviour**: expected behaviours a competent prompt-only run missed, with no new
  wrong behaviour; or
- **equal behaviour plus observed discovery**: runs that did not name the skill show it loading
  from a plain task description, and it stays silent on nearby non-trigger tasks.

A skill does not have to beat the prompt; equal behaviour with observed discovery is enough.
With no observed gain of either kind, delete the skill directory, keep the prompt and its
reference text in `docs/`, and record the decision in the changelog. No reliability,
productivity or cost claim follows from these synthetic cases.

## Acceptance

- Both skills pass `skills-ref validate`, name equals directory, `SKILL.md` under 500 lines,
  references linked once from `SKILL.md` and never from each other.
- The catalog (README, HOWTO, landing page, AGENTS tree) lists seventeen skills and
  `build-site.test` passes; generated site files are current.
- Readiness catalog guard, release contract tests, release guards and defaults-block guard
  pass unchanged.
- Every contract item above has at least one case in [evaluation.md](evaluation.md).
