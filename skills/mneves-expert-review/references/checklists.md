# Detailed prompts per step

Open when a step in SKILL.md feels thin. These are prompts to think with, not sections to fill.

## 1. Objective
- Actual objective (the outcome the user needs, not the artifact they named).
- Intended audience and what they already know / will do with it.
- Success criteria: how would the user know it worked?
- Binding constraints: time, budget, stack, compliance, reversibility.
- Assumptions being made — list them so they can be wrong visibly.
- Acceptable vs. genuinely excellent: what would make an expert say "that is the right call"?

## 2. First principles
- What must be true for this to work?
- Which "requirements" are inherited convention rather than necessity?
- Which constraints are real, which merely assumed?
- Designing from scratch today, without copying the standard approach, what would I do?
- The simplest solution that satisfies the core objective exceptionally well?

## 3. Research
- Prefer: primary sources, official docs/standards, academic research, professional bodies,
  recognized practitioners, recent high-quality analyses, real examples from leading teams,
  the project's own guidelines when present (`DOCS/REF_DOCS`, `DOCS/GUIDELINES-REF`).
- Verify publication dates when recency matters; note the date next to the claim.
- Search for disconfirmation explicitly ("X considered harmful", "why not X", post-mortems).
- Label claims: verified fact / expert consensus / disputed / reasonable inference / own judgment.

## 4. Panel
Perspectives: subject-matter expert · senior practitioner · skeptical reviewer · end user ·
implementation specialist · risk analyst · editor / design critic.

Defect classes: factual errors · weak assumptions · missing information · unnecessary
complexity · logical gaps · usability problems · implementation risks · edge cases ·
maintainability issues · misleading wording · simplification opportunities · "merely
conventional" spots.

## 5. Alternatives (≥ 6, genuinely different)
Mandatory slots: conservative · simple/minimal · ambitious · unconventional · long-term
quality · challenges the premise of the request.

Per alternative: expected quality · advantages · disadvantages · risks · complexity · cost or
effort · scalability · maintainability · reversibility · robustness · likely failure modes.

## 6. Comparison
- Define 3–6 criteria that matter for THIS task; weight them (e.g. 40/25/20/15).
- Score every alternative against every criterion; a small table is fine.
- Reject options whose added complexity does not buy proportional benefit.
- Select or synthesize; write the decisive trade-offs in prose.

## 7. Pre-mortem
It failed badly. Why? What was underestimated? Which assumption was wrong? Which edge case?
What would an experienced expert have warned about? Which part is most fragile? What
unintended consequence appeared?

## 8. Five-year test
What looks naive now? What do I regret not considering? Which shortcuts aged badly? Which
choices created technical / financial / strategic / operational debt? What should have been
simpler? More extensible? What emerging change invalidated the assumptions?
Revise without over-engineering for hypothetical futures.

## 9. Contrarian and advisor
What would a skeptical senior advisor criticize? What do practitioners with opposing
philosophies recommend? Where do experts disagree? What evidence would change the
recommendation? Steelman the strongest opposing position before rejecting it.

## 10. Quality audit
Accuracy · Completeness · Relevance · Simplicity · Robustness · Clarity · Actionability ·
Evidence · Trade-offs. Each is a yes/no with a one-line reason when "no".

## 12. Output skeleton
Final recommendation / deliverable → Key reasoning → Important trade-offs → Risks and
mitigations → Evidence or sources → What was improved from the initial approach → Remaining
uncertainty. Omit empty sections; requested format wins.
