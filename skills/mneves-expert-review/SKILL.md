---
name: mneves-expert-review
description: Stress-test a high-stakes draft or decision. Use for rigorous review, alternatives, evidence, and trade-offs.
license: Apache-2.0
---

# Expert review and optimization pass

Purpose: never deliver the first plausible answer. Deliver the strongest one found, with the
reasoning that survived an attempt to disprove it.

Scale the pass to the stakes. A one-line factual question gets steps 1, 8 and the Final
Challenge in the head, no visible ceremony. A plan, design, recommendation, or document that
others will act on gets the full pass. Effort here means depth of challenge, not word count.

Read the draft (or the request, if no draft exists yet) fully before starting. Then work the
steps in order. Detailed prompts for each step live in `references/checklists.md`; open it when
a step feels thin.

## Procedure

1. **Clarify the objective.** State in a few lines: the actual objective, the audience, the
   success criteria, the binding constraints, the assumptions being made, and what separates
   "acceptable" from "excellent" for this task. Optimize toward that, not toward polish.

2. **Rebuild from first principles.** List what must be true for the solution to work. Split
   constraints into real vs. inherited convention. Ask what the simplest design that meets the
   core objective exceptionally well would be if built from scratch today. Reconstruct the
   solution from those fundamentals before refining the draft.

3. **Research when it changes the answer.** If external facts could materially raise accuracy or
   quality, search: primary sources, official docs and standards, recognized practitioners,
   recent high-quality analyses, and the project's own guidelines when present (e.g. `DOCS/GUIDELINES-REF/`). Check publication dates when
   recency matters. Search for evidence that contradicts the draft, not evidence that comforts
   it. Label each claim: verified fact / expert consensus / disputed / inference / own judgment.
   Do not search when the answer is already fully supported; tool calls are not rigor.

4. **Attack the draft as a panel.** Review it as, at minimum: subject-matter expert, senior
   practitioner, skeptical reviewer, end user, implementer, risk analyst, and editor or design
   critic when applicable. Hunt for factual errors, weak assumptions, missing information,
   unnecessary complexity, logical gaps, usability problems, implementation risk, edge cases,
   maintainability debt, misleading wording, and places that are merely conventional. Try to
   disprove the draft; do not defend it. For checkable outcomes (code, UI, data, citations)
   the panel is not enough; hand the artifact to an independent verifier (`mneves-verify`).

5. **Generate 6+ approaches that differ in kind.** Required: one conservative, one
   simple/minimal, one ambitious, one unconventional, one optimized for long-term quality, and
   one that challenges the premise of the request. For each: expected quality, advantages,
   disadvantages, risks, complexity, effort, scalability, maintainability, reversibility,
   robustness, likely failure mode. Variations of one idea do not count.

6. **Compare explicitly.** Name the 3–6 criteria that matter most for this task, weight them,
   score the alternatives against them. Reject any option whose extra complexity buys less than
   proportional benefit. Pick the strongest or synthesize the best elements, and state the
   decisive trade-offs in plain sentences.

7. **Pre-mortem.** Assume the chosen solution failed badly. Why? What was underestimated, which
   assumption broke, which edge case bit, what would an expert have warned about, which part is
   most fragile, what unintended consequence appeared? Fold every finding back into the solution.

8. **Five-year test.** Reviewed five years on with far more experience: what looks naive, which
   shortcut aged badly, what created technical/financial/strategic/operational debt, what should
   have been simpler, what more extensible, what emerging change invalidates the assumptions?
   Revise, without engineering for hypothetical futures.

9. **Steelman the contrarian.** Find credible expert positions against the chosen approach.
   Where do practitioners disagree, what would a skeptical senior advisor criticize, what
   evidence would flip the recommendation? Present the strongest opposing case before
   rejecting it.

10. **Quality audit.** Check accuracy (facts, numbers, dates, citations, terminology),
    completeness (all material requirements, key edge cases), relevance (every element serves
    the objective), simplicity (nothing removable without loss), robustness (works outside the
    happy path), clarity (an intelligent non-specialist follows it), actionability (what to do
    is unambiguous), evidence (important claims supported), trade-offs (downsides and
    uncertainty explicit).

11. **Improve, do not critique.** Rewrite the deliverable with the findings applied. Return a
    better solution, never a review of the old one. Iterate until remaining changes would be
    cosmetic or would add complexity.

12. **Deliver the final version only.** No intermediate drafts, no private chain-of-thought.
    Give concise reasoning, evidence, comparisons and conclusions sufficient to justify the
    result. Where it helps the reader, structure as:

    - Final recommendation / deliverable
    - Key reasoning
    - Important trade-offs
    - Risks and mitigations
    - Evidence or sources
    - What was improved from the initial approach
    - Remaining uncertainty

    Drop any section that would be empty or padding. A requested output format always wins
    over this structure.

Before sending, rerun the quality audit. Any material weakness sends the work back to step 11.

## Boundaries

- This skill improves the answer to the question asked. It does not widen scope: alternatives
  that change the deliverable's scope are proposed, not silently built.
- Never fabricate research, sources, test results, or expert opinions to fill a step. A step
  with nothing genuine to add is stated as such in one line and skipped.
- The challenge-the-premise alternative (step 5) is reported to the user even when rejected;
  it is the one they cannot see themselves.
- Language follows the user (pt-BR in → pt-BR out).
