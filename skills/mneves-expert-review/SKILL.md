---
name: mneves-expert-review
description: Stress-test a high-stakes draft or decision. Use for rigorous review, alternatives, evidence, and trade-offs.
license: Apache-2.0
---

# Expert review and optimization pass

Purpose: never deliver the first plausible answer. Deliver the strongest one found, with the
reasoning that survived an attempt to disprove it.

Scale the pass to the stakes. A one-line factual question gets steps 1 and 4 in the head, no
visible ceremony. A plan, design, recommendation, or document that others will act on gets the
full pass. Effort here means depth of challenge, not word count.

Read the draft — or the request, if no draft exists yet — fully before starting.

## Procedure

1. **Clarify the objective.** State in a few lines: the actual objective, the audience, the
   success criteria, the binding constraints, the assumptions being made, and what separates
   "acceptable" from "excellent" here. Optimize toward that, not toward polish.

2. **Rebuild from first principles.** List what must be true for the solution to work. Split
   constraints into real versus inherited convention. Ask what the simplest design that meets
   the core objective exceptionally well would be if built from scratch today, then reconstruct
   from those fundamentals before refining the draft.

3. **Research only when it changes the answer.** If external facts could materially raise
   accuracy, search: primary sources, official docs and standards, recognized practitioners,
   recent high-quality analyses, and the project's own guideline docs when present. Check
   publication dates when recency matters. Look for evidence that contradicts the draft, not
   evidence that comforts it. Label each claim — verified fact / expert consensus / disputed /
   inference / own judgment. Do not search when the answer is already fully supported; tool
   calls are not rigor.

4. **Attack it.** One combined assault, from every angle that applies:

   - **As a panel** — subject-matter expert, senior practitioner, skeptical reviewer, end user,
     implementer, risk analyst, editor or design critic. Hunt factual errors, weak assumptions,
     missing information, unnecessary complexity, logical gaps, usability problems,
     implementation risk, edge cases, maintainability debt, misleading wording, and anything
     that is merely conventional.
   - **As a pre-mortem** — assume it failed badly. What was underestimated, which assumption
     broke, which edge case bit, which part is most fragile, what unintended consequence
     appeared, what would have aged badly given a few more years of hindsight?
   - **As the opposition** — find the credible expert case *against* the chosen approach. Where
     do practitioners disagree, what would a skeptical senior advisor say, what evidence would
     flip the recommendation? State the strongest opposing case before rejecting it.

   Try to disprove the draft; do not defend it. For checkable outcomes — code, UI, data,
   citations — the attack is not enough: hand the artifact to an independent verifier
   (`mneves-verify`). Fold every surviving finding back into the solution.

5. **Generate alternatives that differ in kind, then compare.** Keep generating until new
   options stop differing in kind rather than in detail; variations of one idea do not count.
   Always include one conservative, one minimal, and one that challenges the premise of the
   request. Then name the 3-6 criteria that actually matter, weight them, and score the
   alternatives. Reject any option whose extra complexity buys less than proportional benefit.
   Pick the strongest or synthesize the best elements, and state the decisive trade-offs in
   plain sentences.

6. **Improve, then audit once, then deliver.** Rewrite the deliverable with the findings
   applied — return a better solution, never a review of the old one. Then audit the rewrite
   against these nine dimensions, and send it back for another rewrite only on a material
   failure:

   accuracy (facts, numbers, dates, citations, terminology) · completeness (material
   requirements, key edge cases) · relevance (every element serves the objective) · simplicity
   (nothing removable without loss) · robustness (works outside the happy path) · clarity (an
   intelligent non-specialist follows it) · actionability (what to do is unambiguous) ·
   evidence (important claims supported) · trade-offs (downsides and uncertainty explicit).

   Deliver the final version only — no intermediate drafts. Where it helps the reader,
   structure as: final recommendation · key reasoning · important trade-offs · risks and
   mitigations · evidence or sources · what improved from the initial approach · remaining
   uncertainty. Drop any section that would be padding. A requested output format always wins
   over this structure.

## Boundaries

- This skill improves the answer to the question asked. It does not widen scope: alternatives
  that change the deliverable's scope are proposed, not silently built.
- Never fabricate research, sources, test results, or expert opinions to fill a step. A step
  with nothing genuine to add is stated as such in one line and skipped.
- The challenge-the-premise alternative (step 5) is reported even when rejected; it is the one
  the user cannot see for themselves.
- Language follows the user.
