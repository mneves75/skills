---
name: mneves-expert-review
description: Stress-test a high-stakes draft or decision. Use for rigorous review, alternatives, evidence, and trade-offs.
license: Apache-2.0
---

# Expert review and optimization pass

Improve the requested high-stakes draft or decision through one evidence-backed challenge.
Use ordinary direct answers for simple questions; this skill does not add a review to every
response. Scale detail to the decision's stakes, not to a fixed report length.

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

4. **Challenge it once.** Combine the relevant expert, implementer, user, and risk perspectives.
   Test factual accuracy, assumptions, missing behavior, complexity, usability, failure paths,
   maintainability, and misleading wording. Use a pre-mortem to identify the weakest dependency;
   state the strongest credible opposing case and the evidence that would change the decision.
   These are perspectives in one pass, not automatic separate agents or repeated reviews.

   Test the draft's weakest claim. Use independent verification when requested, required by
   the owning workflow, or warranted by risk. `mneves-verify` is a separately installed sibling;
   when absent, use an equivalent fresh read-only verifier. Report missing required capability
   as blocked. Fold verified findings back into the solution.

   For code, challenge the weakest assumption adversarially and use installed `cccc` on
   supported changed source as a comprehension signal. The separately installed `autoreview`
   skill owns detailed complexity guidance. Without it, preserve target config, run
   `cccc --no-cache --min 0` on focused source, record version/status/diagnostics, and reconcile
   expected files and parse errors. Missing tooling or unsupported/partial scans are reported;
   scores never establish correctness or justify a mechanical refactor.

5. **Compare meaningful alternatives.** Start with a conservative option, a minimal option,
   and one that challenges the premise. Merge equivalent options. Add another only if evidence
   exposes a materially different trade-off. Compare against the decision criteria; use a
   weighted score only when the weights and scores can be justified. Reject extra complexity
   whose benefit is not proportional.
   Pick the strongest or synthesize the best elements, and state the decisive trade-offs in
   plain sentences.

6. **Improve, then audit once, then deliver.** Rewrite the deliverable with the findings
   applied. Check accuracy, material completeness, relevance, simplicity, failure behavior,
   clarity, actionability, evidence, and explicit trade-offs. Correct material failures and
   recheck those claims without restarting an unchanged full review.

   Deliver the improved version with the decisive reasoning, sources, trade-offs, and remaining
   uncertainty. Omit intermediate drafts and empty report sections; the user's format wins.

## Boundaries

- This skill improves the answer to the question asked. It does not widen scope: alternatives
  that change the deliverable's scope are proposed, not silently built.
- Never fabricate research, sources, test results, or expert opinions to fill a step. A step
  with nothing genuine to add is stated as such in one line and skipped.
- The challenge-the-premise alternative (step 5) is reported even when rejected; it is the one
  the user cannot see for themselves.
- Language follows the user.
