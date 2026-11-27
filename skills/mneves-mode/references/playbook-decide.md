# Playbook: plan or high-stakes decision

1. **Separate facts from guesses.** Gather primary evidence: code, logs, official docs and specs.
   Cut any citation that does not support the exact claim.
2. **Stress-test.**
   - `mneves-expert-review` for memos, architecture and strategy.
   - `grilling` when the user wants to be questioned on the plan.
   - `interrogate` for an adversarial multi-model read.
   - `council` when the user asks for independent multi-CLI deliberation.
   - Fallback: write the strongest objection to the preferred option, compare at least two viable
     alternatives, and record reversibility and failure modes.
3. **Settle empirical forks locally.** Run a small benchmark or prototype before escalating a
   reversible technical question. Leave product and preference calls to the owner.
4. **Record terms when the domain is new.** `domain-modeling`. Fallback: a short glossary with
   one line per term.
5. **Report.** A planning or review request stays read-only.
