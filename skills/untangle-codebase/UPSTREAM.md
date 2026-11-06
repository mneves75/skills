# Provenance

- Source: [caldoai/skills — untangle-codebase](https://github.com/caldoai/skills/tree/442c29918339cc8dbf09ae27aaf17b05745465a3/skills/untangle-codebase).
- Commit: `442c29918339cc8dbf09ae27aaf17b05745465a3`.
- Original procedure: [SKILL.md](https://github.com/caldoai/skills/blob/442c29918339cc8dbf09ae27aaf17b05745465a3/skills/untangle-codebase/SKILL.md).
- License: [upstream MIT License](https://github.com/caldoai/skills/blob/442c29918339cc8dbf09ae27aaf17b05745465a3/LICENSE), preserved verbatim in [LICENSE](LICENSE), Copyright (c) 2026 Maze.
- Adapted on: 2026-11-05. The upstream skill name is retained.

## Adaptations

Preserves the change-together question, hidden links / needless links / surplus analysis,
dependency graph, Git evidence and problem-to-fix decision log. Replaces the whole-codebase
mandate and open-ended search with explicit scope, frozen criteria and bounded completion.
Invocation alone diagnoses and plans; an explicit refactoring request authorizes in-scope
implementation, while review-only requests stay read-only. Missing or invalid scope never
selects the whole repository implicitly.

Uses portable Agent Skills frontmatter, removing host-specific invocation and argument keys.
Adds observed baselines, concrete caller/behavior evidence, design alternatives and costs,
verification per unit and final regression. Retries, wrappers and special cases are examined
as potentially necessary behavior; public contracts and safety mechanisms remain protected.
Incidental bug fixes need their own authorization and proof.

Makes comment and test cleanup separate opt-ins, retaining invariants and requiring
assertion-level preservation plus equivalent replacement proof before test removal or
rewriting. Requires fresh adversarial review and independent acceptance, with explicit
BLOCKED gates and a focused self-check when independence is unavailable. No model pins,
executables, dependencies or mandatory sibling skills are introduced. Examples are
illustrative; upstream claims about productivity are not presented as measured results.
