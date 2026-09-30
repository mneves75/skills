---
name: mneves-eli5
description: Explain ideas in plain language for a chosen audience. Use for ELI5 or audience-specific re-explanations.
license: Apache-2.0
---

# Explain Like I'm 5 (Feynman technique)

Explain the mechanism accurately enough for the audience to repeat it. Simplicity preserves
the facts and consequential limitations.

## Procedure

1. Choose the audience from the request or table. State a consequential assumption; ask only
   when unresolved audience choices would materially change the answer.
2. State the core idea in one audience-appropriate sentence. Explain an unfamiliar term before
   relying on it.
3. Show a concrete case before naming the technical term. Use one familiar analogy only when
   it clarifies the mechanism; name where it breaks. Experts often need no analogy.
4. Check the causal explanation for unsupported leaps. Explain the missing step or state the
   uncertainty; preserve complexity when simplification would mislead a decision.
5. End with a repeatable takeaway when useful. Offer more depth only if it helps the user.

## Audience levels

| Level | Who | Vocabulary | Depth | Length |
|---|---|---|---|---|
| child | literally 5–10 | everyday words only, no numbers beyond counting | one cause, one effect | 3–6 short sentences |
| layperson | adult, no domain background | plain words; jargon named once in parentheses | mechanism at the level of "what happens, then what" | 1–3 short paragraphs |
| executive | decision-maker, time-poor | business terms fine; no implementation terms | what it is, why it matters, the risk/cost/decision | conclusion first, ≤ 1 paragraph + 3 bullets max |
| junior | technical, new to this area | technical terms of the base field; new terms defined | how it works and the one pitfall to remember | as long as needed, with one code/config example if it helps |
| expert | knows the field, new to this detail | full jargon | the delta from what they already know, the tradeoff, edge cases | dense, no analogy needed unless the idea is counter-intuitive |

Mixed audience: write for the lowest level present, then add a clearly marked "for the
engineers" block underneath. Do not average the levels into something that serves none.

## Rules

- Use the user's language and correct accents; retain identifiers, commands and product names,
  explaining unfamiliar names once.
- Respect the listener's intelligence. Use concrete actors, numbers and scenarios, with the
  listener as subject where natural.
- For a new audience, retain checked core facts and change depth. Reread or research only
  claims the new depth makes uncertain. Finish when the mechanism and consequential limitation
  are clear at the requested level.

## Examples

Read [references/examples.md](references/examples.md) only when a worked audience example helps.
