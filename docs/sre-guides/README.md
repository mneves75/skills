# SRE guides

Two procedures for reliability work, kept as documents you read or hand to an agent on
request. They are not installable skills: nothing here is discovered or loaded automatically.

| Guide | Use it for |
|---|---|
| [Service level objectives](slo/README.md) | Indicators, objectives, error budgets, burn-rate alerts, checking objective arithmetic |
| [Incident learning](incident-learning/README.md) | Blameless reviews of an incident, near miss or failed operation after impact stops |

For a single task, the [SRE prompts](../sre-prompts.md) are shorter: paste one into any agent
and attach the matching guide when you want the full procedure.

## What the evaluation showed

Both procedures first shipped on this branch as candidate skills (`mneves-slo` and
`mneves-incident-learning`). Four evaluation rounds compared answers with and without them. In
the last round both were discovered without being named and stayed silent on unrelated
requests, and they improved some answers, but each also introduced a new unsupported claim (a
gap "closed" by a count without outcomes, a data-loss ceiling inferred from a backup schedule)
and some answers asserted reliance, cause or measurement that no input showed. The retention
rule allows no new wrong behaviour, so both entrypoints were retired and the procedures kept
here. The full record is in [the evaluation](../specs/sre-workflows/evaluation.md).

What this means for you: an answer drafted with these guides can be fluent and still wrong.
Check every number and every factual claim against the artifacts you supplied, and treat
anything no artifact shows as `unknown`.
