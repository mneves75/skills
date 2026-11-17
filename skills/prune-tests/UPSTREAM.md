# Provenance

- Source: [caldoai/skills — prune-tests](https://github.com/caldoai/skills/tree/bd73b2ea5eb854ab8f0553fb41f77c8786f28f82/skills/prune-tests).
- Commit: `bd73b2ea5eb854ab8f0553fb41f77c8786f28f82`.
- Original procedure: [SKILL.md](https://github.com/caldoai/skills/blob/bd73b2ea5eb854ab8f0553fb41f77c8786f28f82/skills/prune-tests/SKILL.md).
- License: [upstream MIT License](https://github.com/caldoai/skills/blob/bd73b2ea5eb854ab8f0553fb41f77c8786f28f82/LICENSE), preserved verbatim in [LICENSE](LICENSE), Copyright (c) 2026 Maze.
- Adapted on: 2026-11-17. The upstream skill name is retained.

## Adaptations

Keeps the upstream procedure, its three categories (the past, nothing, the implementation),
its done criteria and its example unchanged. Replaces the host-specific `argument-hint` key
with portable Agent Skills frontmatter and a trigger line in `description`.

Adds a scope rule (no named path lists candidates and waits for the user's confirmation), a
recorded baseline run, and excludes failing, skipped or flaky tests from pruning. Keeps
standing absence guards (security regressions, invariant guards, planted-violation controls),
which the "assert it's gone" example could otherwise remove. Requires each rewrite to fail
on a deliberately planted regression, a caller search before deleting production code, no
removal of an exported or documented interface without the user, and a per-test report with
before and after suite results. No executables, dependencies or sibling skills are introduced.
