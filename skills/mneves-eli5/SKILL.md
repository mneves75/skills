---
name: mneves-eli5
description: Explain ideas in plain language for a chosen audience. Use for ELI5 or audience-specific re-explanations.
license: Apache-2.0
---

# Explain Like I'm 5 (Feynman technique)

Feynman's test: if it cannot be explained simply, it is not understood yet. Simplicity here
means the listener could repeat the idea back to someone else. It never means lying,
skipping the part that matters, or padding with cute words.

## Procedure

1. **Fix the audience before writing.** Pick one level from the table below. If the user did
   not name one, infer it from their message and state the assumption in one line
   ("Explaining for a non-technical manager"). Ask only when two levels would produce
   materially different answers and nothing in the request settles it.
2. **Find the core.** Write the idea in one sentence a listener at that level would accept.
   If the sentence needs a term the listener does not know, that term is the real subject;
   explain it first.
3. **Anchor with one analogy from the listener's world.** Choose something they already
   handle (kitchen, traffic, money, school, their own job). One analogy, carried through;
   two competing analogies confuse more than none.
4. **Show, then name.** Walk through a concrete case (a real example, small numbers, a
   mini-story) before introducing the proper term. Introduce jargon only once it names
   something the listener has already seen, and put it in parentheses after the plain phrase.
5. **Say where the analogy breaks.** Every analogy is wrong somewhere. Name the gap in one
   sentence so the simple model does not become a false one.
6. **Check the gap-finding step.** Reread the explanation as the listener: is there a
   "because…" that is actually a hand-wave? Fill it or admit "this part is
   complicated; the short version is…". Never fake precision.
7. **Close with the takeaway.** One line the listener can repeat. Offer the next level up
   ("Want the version with the actual mechanism?") only when it is real, not as a ritual.

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

- **Answer in the user's language**, with correct accents. Keep code identifiers, commands, and
  product names in the original, but gloss them the first time.
- Simple ≠ wrong. If a simplification would leave the listener believing something false
  that matters for their decision, keep the complexity and explain it instead.
- No condescension. Never "it's easy" / "obviously" / "simply". Being 5 is about vocabulary,
  not intelligence.
- Concrete beats abstract: a specific number, a named thing, a single scenario. Replace
  every "some", "various", "etc." with the actual case.
- Put the listener in the sentence as the subject ("you send…", "your phone asks…").
- Re-explain on request without re-deriving: when the user says "now for my CTO" or "more
  technical", keep the same core sentence and analogy, change the level only.

## Examples

Worked examples per level: [references/examples.md](references/examples.md).
