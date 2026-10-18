# Using skills with less repeated work

Keep one coherent outcome per session. Start with the smallest relevant skill, and read only
the references that its current branch needs. Skill descriptions are discovery pointers;
entrypoints should carry shared constraints and conditional routes rather than entire catalogs.

Use a compact task contract:

```text
Task: <specific problem or module>.
Acceptance: <observable success, failure behavior, required checks and evidence>.
Constraints: <scope, ownership, behavior to preserve, existing authority>.
Delivery: Complete the authorized work and verification; report results and precise blockers.
Target: <discussion, local patch, PR, or authorized external destination>.
```

Infer fields already established in the session. Link accessible large logs or source identities
instead of pasting transcripts. A discussion-first handoff preserves its assessment boundary;
an approved implementation continues without repeated permission for the same action.

| Skill | Avoidable repeated work removed or bounded |
|---|---|
| autoreview | Git filter/line-ending details load on the relevant collection branch; reuse the current frozen review instead of launching copies |
| imagegen-frontend-mobile | Reuse supplied screens/assets/style and generate only the requested set plus justified corrections |
| mneves-chatgpt-search | Preserve working discovery infrastructure; route audit, local fixes and measurement separately, refreshing only relevant official guidance |
| mneves-agent-readiness | Choose one requested assessment/output mode; static/manual triage does not masquerade as a runtime maturity score |
| mneves-eli5 | Retain checked facts across audience changes; use an analogy only when it helps |
| mneves-expert-review | Combine challenge perspectives in one pass; compare distinct options without open-ended generation |
| mneves-fable-orchestrator | Use ordinary or bounded workers by scope, reserve specialists for justified difficulty, and resume multi-round lanes |
| mneves-incident-learning | Load the evidence reference once before the timeline; reuse the supplied exports instead of re-collecting; the prompts in `sre-prompts.md` cover a single review without installing |
| mneves-slo | Compute from supplied counts instead of querying live systems; load adoption guidance only when proposing targets or alerts |
| mneves-handoff | Carry compact checked context, acceptance, authority and blockers; disclose the discussion template conditionally |
| mneves-security | Separate audit/fix/delivery authority; keep current standards in a source reference and retain evidence without claiming untested provider controls |
| mneves-superaudit | Delegate only substantial independent work; carry existing authority across phases while preserving requested stops |
| mneves-teach-back-srs | Load only teach-back, review, stats or export; resolve the helper once from its installed location |
| mneves-verify | Choose behavior probes from the frozen criteria; preserve independence and high-risk model requirements |

Model, effort and speed defaults belong in the active host configuration or a skill's explicit
defaults owner. Preserve caller overrides. Use a capable ordinary route for routine work,
a cheaper route for bounded tasks, and stronger specialists when requirements or observed
difficulty justify them. A prose model request does not configure a dispatched process.

Required repository gates, complete requested scope, secret scanning, isolation, consent and
privacy stay binding. Lower usage is not permission to omit proof or declare a blocked check
passed. Retry an unchanged blocker only after a relevant capability/input change or a bounded
transient retry. A smaller tool-history budget requires saving full critical output as a local
artifact, not discarding it.

## Pilot one task receipt

Start with one ordinary task and reuse its existing final report. This is an optional
measurement experiment, not an extra gate or a replacement for required verification.
Keep the receipt short:

```text
Outcome/source: <completed, blocked or abandoned; task/project and checked revision/artifact>.
Applicable gates: <check and PASS, FAIL, SKIP or BLOCKED; evidence and any skip/block reason>.
Blockers/corrections: <unresolved blockers and material corrective work, or none>.
Recording effort: <time/effort to prepare this receipt; measured, estimated or unknown>.
```

A deliberately inapplicable platform check may be SKIP. An applicable mandatory check that
cannot run remains BLOCKED or FAIL according to its existing contract; it cannot justify a
completion claim. Keep any workflow-required verifier verdict format unchanged; put this
optional receipt in the existing final report or adjacent evidence, rather than adding lines
to a strict verdict.

Add timing or usage only when the harness already provides it with reliable task attribution.
Keep input, cached input and output distinct when available, respecting the provider's counter
definitions; do not add overlapping totals. Otherwise mark the metric unknown. Session elapsed
time is not active work time, human attention, or production change lead time. Entry-point byte
reductions are context-size measurements, not demonstrated credit savings. Include corrections
and recording effort when comparing routes; do not replace missing costs with zero.

Continue only if the pilot informs a concrete decision at negligible recording cost. If useful,
observe consecutive tasks within one project, task category and harness, retaining blocked and
abandoned cases. Change one policy element at a time. Small before/after samples are case
evidence, not causal estimates or proof of unchanged defect risk. Stop collecting fields that
do not inform a decision; avoid recurring synthetic audits merely to measure an optimization.

This keeps outcome measurement contextual, as recommended by
[DORA's measurement guidance](https://dora.dev/guides/dora-metrics/). Conditional reference
loading follows the [Agent Skills specification](https://agentskills.io/specification).
