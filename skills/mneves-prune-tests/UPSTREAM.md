# Provenance

- Source: [caldoai/skills — prune-tests](https://github.com/caldoai/skills/tree/bd73b2ea5eb854ab8f0553fb41f77c8786f28f82/skills/prune-tests).
- Commit: `bd73b2ea5eb854ab8f0553fb41f77c8786f28f82`.
- Original procedure: [SKILL.md](https://github.com/caldoai/skills/blob/bd73b2ea5eb854ab8f0553fb41f77c8786f28f82/skills/prune-tests/SKILL.md).
- License: [upstream MIT License](https://github.com/caldoai/skills/blob/bd73b2ea5eb854ab8f0553fb41f77c8786f28f82/LICENSE), preserved verbatim in [LICENSE](LICENSE), Copyright (c) 2026 Maze.
- Adapted on: 2026-11-17. The upstream name is `prune-tests`; the `mneves-` prefix is the
  owner's choice.

## Adaptations

Keeps the upstream procedure, its three categories (the past, nothing, the implementation)
and its example; the done criteria gain a baseline line and the standing-guard exception.
Replaces the host-specific `argument-hint` key with portable Agent Skills frontmatter, a
trigger line in `description` and a title.

Adds a scope rule (no named path lists candidates and waits for the user's confirmation), a
trust rule before any suite, setup or discovery run (a trusted repository or an isolated
environment; otherwise a static candidate list and no pruning; nothing runs before an unnamed
scope is confirmed), all edits and runs in a disposable, hook-free copy discarded on interruption, a
patch checked against the approved paths before it is applied back, runs that count only when
they executed the tests in question, a recorded baseline run, and excludes failing or known-flaky tests from pruning. Keeps standing
absence guards (security regressions, invariant guards, planted-violation controls), which the
"assert it's gone" example could otherwise remove, and says how to recognize one. Requires a
planted regression for each rewrite and proof that a kept duplicate catches what the pruned
copy did (the duplicate shortcut needs the same inputs, setup, layer and assertion; a copy at
another layer is kept unless a plant in that boundary itself, not a shared helper, makes the
survivor fail), planted edits that stay inside the scope, one at a time, and are reverted before
the next step or after an interruption, a kept test whenever its proof cannot be run, one plant per case and setup a pruned copy covers with
the survivor kept and seen running, any test that may be the only guard of a required rule kept
unless a proven replacement exists or the user confirms the rule is obsolete, production code deleted
only inside the scope or, outside it, item by item after the user confirms, a caller search that counts dynamic use before deleting production code, no removal
of a public interface without the user, a full-suite re-run when production code is deleted,
and a per-test report with before and after suite results. No executables, dependencies or
sibling skills are introduced.
