# SRE workflows: review record

Companion to [spec.md](spec.md) and [evaluation.md](evaluation.md). Two review axes, Standards
and Spec, read the frozen candidate diff at `5d39c95` independently. Their findings are listed
per axis as reported; they are not merged or reranked. The second-round corrections below were
made in response. They have not been re-reviewed, and no finding is recorded as verified fixed.

## Standards axis

| Finding | Severity | Correction in this round |
|---|---|---|
| Completion status: the action vocabulary allowed `done (check not run)`, so an action could read as done without a passed check | P2 | Statuses are `open`, `implemented (verification pending)`, `done (check passed)`, `dropped (reason)`, in the incident reference, `SKILL.md`, prompt 8, the spec, HOWTO and the example |
| Clock skew: unknown chat skew was treated as if a displayed gap could order events | P2 | Within-source order follows the source; with unknown skew, cross-clock order is `uncertain` whatever the gap (incident reference rule 2, `SKILL.md` step 2, prompt 6, spec contract 2, example timeline and evidence limits) |
| Public copy | P3 | Copy corrections in this round: the 1.38.0 changelog entry now opens with a complete one-line sentence for the generated release row; narration about the authoring session was removed from the source lists. The axis record does not say which copy it meant, so both are listed |

## Spec axis

| Finding | Severity | Correction in this round |
|---|---|---|
| Time and traffic: burn rate was read as time to exhaustion, and alert thresholds hid their traffic assumption | P2 | Burn is a normalised error fraction; a contained window used `burn * N_window / N_period`; `f * period / w` is labelled an approximation for even traffic or time-based indicators; forecasts need the remaining budget and a traffic assumption (SLO specification rule 6, adoption, prompts 2 and 5, example alerts, spec contract 10) |
| Partial telemetry: the example declared a 28-day miss from 27 known days | P2 | A gap keeps the full window `unknown`; covered figures are an observed subset; the example shows a counterexample (99.5228%); E2 gains a partial-period variant (SLO specification rule 2, `SKILL.md` step 3, spec contract 4) |
| Durability fixture: acknowledgements, missing deliveries and a corrupted local database were read as durable commit or permanent loss | P2 | An acknowledgement proves what its contract says; undelivered is incomplete, not lost; native server, local-only and drill results are kept apart (SLO specification, incident reference "Durability, delivery and loss", prompt 4, spec contract 12, E7 positive and negative variants, E14 with an isolated drill and a no-drill variant) |
| Clock skew | P2 | As in the Standards axis row; E13 gains an unknown-skew variant |

Corrections outside both axes, made under the same brief: the active-incident exception ("or
when the lead asks", the round 1 regression) was removed everywhere; absence in one artifact
now reads "not observed there" and the example no longer infers a staging target; correlation
is kept apart from mechanism; owners and dates not in the sources are `unassigned`, `pending`
or marked proposals; action checks reproduce the relevant scale, platform and failure; E15 and
E16 need actual runtime checks.

## First-principles change

A figure, an order, a status or an owner is only as strong as the artifact behind it. The first
package let several defaults fill gaps: a missing day became a miss, a displayed gap became an
order, an acknowledgement became a commit, a reviewer's guess became an accepted owner, and a
written change became done. The corrected rules give every one of those gaps an explicit state
(`unknown`, observed subset, `uncertain`, `proposed`, `pending`,
`implemented (verification pending)`) and name the evidence that would close it.

## Alternatives

1. **Retain the two small skills** (current direction). Automatic discovery was observed on two
   hosts for the first package, and round 1 scored the candidate higher with one regression.
   Cost: two entrypoints to keep consistent with the prompts and the spec.
2. **Prompts and references only.** Fewer files to keep aligned, and the eight templates already
   carry the constraints that matter. It loses discovery from a plain task description. The
   retention rule in the spec decides between the two after the corrected sources are
   evaluated; this round does not decide it.

## Five-year decision: one policy owner per rule

Each rule has one owner file. SLO arithmetic and indicator rules live in
`skills/mneves-slo/references/specification.md`; alerting and adoption in `adoption.md`;
incident evidence, actions and statuses in
`skills/mneves-incident-learning/references/evidence-and-learning.md`. Gates, verdicts and
control IDs stay with `mneves-production-readiness`. The prompts restate the rules so they work
alone, and the spec, HOWTO and changelog summarise them; when any of those disagrees with the
owner file, the owner file wins and the copy is corrected. This keeps a rule change to one
edit plus its summaries, and lets either skill be retired into `docs/` without moving policy.
