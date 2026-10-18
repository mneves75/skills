# SRE workflows: review record

Companion to [spec.md](spec.md) and [evaluation.md](evaluation.md). Two review axes, Standards
and Spec, read the frozen candidate diff at `5d39c95` independently. Their findings are listed
per axis as reported; they are not merged or reranked. The second-round corrections below were
made in response. Formal acceptance of those sources then returned SOURCE FAIL (criterion 1
pass, criteria 2 and 3 fail) and BEHAVIOR FAIL; a third, bounded correction follows under
"Third round", and "Final result" maps it to the final behavioural round. A fourth, bounded loop
then corrected the sources again and repaired the harness; both skills failed retention and
were retired into `docs/sre-guides/` ("Round 4" under "Final result"). No finding in this file
is recorded as verified fixed: a case met once in one bundled answer is an observation, not a
verified fix. Paths below that name `skills/mneves-slo/` or `skills/mneves-incident-learning/`
describe the tree at the time of each round.

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

## Third round

Findings from the formal checks of the second-round sources and from round 2 (see
[evaluation.md](evaluation.md)), and the general wording added for each. Owner files first;
`SKILL.md`, the prompts and the spec carry one-line pointers. The behaviour was rechecked once,
in Round 3 (see "Final result"); the final SOURCE recheck belongs to the frozen-candidate
records and pull request, not to this file.

| Finding | Kind | Correction |
|---|---|---|
| The example timeline cites an export history that its Sources table does not register | SOURCE | Synthetic "Log export job history" row with retrieval, clock and coverage, and completeness marked not checked; the timeline cites it by that name (incident example) |
| The record calls the bundles "two seven-file packages" | SOURCE | Seven files in total: four for `mneves-slo`, three for `mneves-incident-learning` (evaluation, Round 1) |
| A 100% correctness requirement lost its test follow-up and owner without the readiness sibling | BEHAVIOR | The report keeps the invariant's test, its effectiveness evidence and an accepted, proposed or `unassigned` owner, with no target or gate (SLO specification rule 4, `SKILL.md` step 3 and readiness fallback, prompts 1 and 2, spec contract 7) |
| Draft decision output omitted owner, adoption and review dates | BEHAVIOR | Every report gives status, owner, adoption date and review date, `pending` when absent; SLA mismatches are reported without editing either promise (adoption "Draft and adopted", `SKILL.md` step 5, prompts 1 and 5, spec contract 8) |
| The answer invented a responder's interface and rationale | BEHAVIOR | A cancelled-job record and later chat show an unnoticed cancellation, not the person's interface, knowledge or reason; missing context is `unknown` with an evidence request (incident reference "Noticed or not" and "Decisions in context", `SKILL.md` step 3, prompt 6, spec incident contract 5) |
| A near miss did not name its no-user timing as luck | BEHAVIOR | Timing with no users active is luck that limited exposure, and a safeguard or someone's reasoning only with a source (incident reference "Luck", `SKILL.md` step 3, prompt 7, spec incident contract 5) |
| An answer claimed an independent reviewer result that was never returned | BEHAVIOR | A test, lookup, review, effect or approval counts only with its observed result; planned or empty is `pending` (incident reference "The review's own checks", SLO specification "Checking someone else's numbers", both `SKILL.md` report steps and `mneves-verify` fallbacks, all eight prompts, spec Shared) |

The harness gaps (E6 SLA variant and E7 positive input missing from the paired prompts, and a
routing probe that read evaluation material) are the coordinating session's to repair; no case
criterion was edited for them.

## Final result

Round 3 in [evaluation.md](evaluation.md) is the one corrected full reverification of the
third-round sources, and the last of this loop. Final BEHAVIOR (criterion 4): FAIL. UI
(criterion 5): PASS on a local seventeen-card preview only, before the retirement; the
fifteen-card catalog is not rechecked.

| Third-round finding | Observed in Round 3 |
|---|---|
| 100% correctness requirement without the readiness sibling (E3) | Candidate met E3 |
| Draft decision output without owner and dates (E6) | Candidate met E6 |
| Invented responder interface and rationale (E8) | Candidate met E8 |
| Near-miss timing not named as luck (E9) | Not established either way: E9 stayed partial for a different failure, invented absent safeguards |
| Unreturned independent reviewer result | Not reproduced; both final explicit answers left review and recomputation `pending` |
| The two SOURCE findings | Not assessed here; the final SOURCE recheck is in the frozen-candidate records |

New failures in Round 3, none fixed in this tree:

- Absence stated as fact: the candidate's E9 answer called a lock-time check and a lock-wait
  alert absent; the Claude explicit-invocation probe inferred from unsupplied artifacts that no
  data check ran and that a chat message served as the completion signal; the candidate's E18
  answer said the missing export was never attempted. The bounded-absence rule reached the
  timeline and responder context but not contributing conditions, action history or export
  attempts.
- Evaluation method: E15 showed fallback under unavailability in a project-only profile, not the
  frozen physical absence from the host; E16 had no actual dashboard link. Both stay partial.

The proposed work is in [follow-up.md](follow-up.md); none of it was accepted or started when
round 3 closed. Items 1 and 2 were later executed in round 4.

### Round 4

The owner opened a new bounded corrective loop after round 3; it reclassifies nothing above.
The sources gained the bounded-absence rule for every claim (follow-up item 1) and the harness
was repaired (item 2). Full record: "Round 4 (retention decision)" in
[evaluation.md](evaluation.md).

| Round 3 failure | Observed in round 4 |
|---|---|
| E9 absent safeguards (candidate) | Candidate met E9; the Claude near-miss regression still treated a supplied duration as proof of a measurement |
| Explicit probe: no data check, chat as completion signal | Not fixed: the Claude explicit probe asserted reliance on an unverified restore and completion declared from a message |
| E18 never attempted (candidate) | Candidate met E18; both export-gap regressions met |
| E15, E16 method | Runtime controls passed: scoped "Unknown skill" on Claude (Codex N/A), 4 of 4 non-triggers per host with the dashboard actually read |

New failures in round 4: the candidate's E2 offers a producer count alone as a way to close a
gap; its E10 infers a 24-hour loss ceiling from a nightly schedule; the Claude incident probe
treats a cancelled job and a missing artifact as proof that the rollback did not end the impact;
the Claude restore-evidence regression infers risk from a restore. E7 (reversed acknowledgement order)
and E13 (thread order) are shared by both arms. Semantic totals over 18 cases: baseline 12 met
/ 6 partial, candidate 14 / 4. BEHAVIOR (criterion 4): FAIL; retention FAIL for each skill; no
pass or waiver. Both entrypoints were retired under the spec's rule.

## First-principles change

A figure, an order, a status or an owner is only as strong as the artifact behind it. The first
package let several defaults fill gaps: a missing day became a miss, a displayed gap became an
order, an acknowledgement became a commit, a reviewer's guess became an accepted owner, and a
written change became done. The corrected rules give every one of those gaps an explicit state
(`unknown`, observed subset, `uncertain`, `proposed`, `pending`,
`implemented (verification pending)`) and name the evidence that would close it.

## Alternatives

1. **Retain the two small skills** (direction after round 3). Automatic discovery was observed on two
   hosts for the first package; round 1 scored the candidate higher with one regression, and
   round 2 scored it higher with no misses but formal BEHAVIOR FAIL. Round 3 scored it
   15 met / 4 partial against the baseline's 14 / 5, with automatic invocation observed, but with
   new wrong behaviour on E9 and E18, so the retention condition in
   [evaluation.md](evaluation.md) ("adds no new wrong behaviour") is not met as observed. E16
   stays partial because no dashboard link was supplied, not because a skill loaded.
   Cost: two entrypoints to keep consistent with the prompts and the spec.
2. **Prompts and references only.** Fewer files to keep aligned, and the eight templates already
   carry the constraints that matter. It loses discovery from a plain task description.

After round 3, whether to retire or run the follow-up loop was left to the owner, who ran
round 4. After round 4 the comparison is:

1. **Patch the instructions again and run round 5.** Rejected: each correction removed the last
   finding and a new unsupported inference appeared elsewhere, so another round has no
   evidence-backed stopping point.
2. **Prompts and guides only.** Chosen, as the retirement rule prescribes: discovery is lost,
   but nothing an agent loads unasked can add a wrong claim to an unrelated session, and every
   contract and worked example survives in `docs/sre-guides/`.
3. **One larger SRE orchestrator skill.** Rejected for the reasons in the spec, and because a
   bigger entrypoint widens the surface the failures came from.

Five years out, option 2 is the cheapest to keep honest: the guides name no vendor or model,
and a future skill can be proposed from them only with a fresh evaluation. The guides and
prompts are source-reviewed; no runtime reliability is claimed for them.

## Five-year decision: one policy owner per rule

Each rule has one owner file. SLO arithmetic and indicator rules live in
`docs/sre-guides/slo/references/specification.md`; alerting and adoption in `adoption.md`;
incident evidence, actions and statuses in
`docs/sre-guides/incident-learning/references/evidence-and-learning.md`. Gates, verdicts and
control IDs stay with `mneves-production-readiness`. The prompts restate the rules so they work
alone, and the spec and changelog summarise them; when any of those disagrees with the owner
file, the owner file wins and the copy is corrected. This keeps a rule change to one edit plus
its summaries, and is what let both skills be retired into `docs/` without moving policy.
