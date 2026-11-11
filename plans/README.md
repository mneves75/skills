# Implementation plans

| Plan | Priority | Status |
|---|---|---|
| [001: Rename and verify the renderer skill](001-render-skill-hardening.md) | P1 | Implemented — acceptance and release receipts tracked in PR/Actions |
| [002: SRE workflows](002-sre-workflows.md) | P1 | Both candidate skills retired after R4; guides and prompts released in 1.38.0 |
| [003: Council and security-audit](003-council-security-audit.md) | P1 | Released in 1.40.0 |
| [005: tstack correctness and release](005-tstack-review-release.md) | P1 | Planned at a322c9f for 1.45.0, which shipped from another branch first; its commits (15e0298..c46c77c4) merged to `main` with 1.45.1 (`a53b03cf`, published and tagged 2026-11-04) and its DEL-01 shipped as 1.45.2 (`7587b764`) |
| [Complexity integration](cccc-review-integration.md) | P1 | Released in 1.32.0 |
| [004: Release 1.45.0 closeout and the closeout script](004-release-1-45-closeout.md) | P1 | 1.45.0 closeout executed; 1.45.1 folded its binding run and fixed `deploy.sh`'s record and tag-message defects; closeout script not built |
| [006: Preserve release audit origins](006-release-audit-provenance.md) | P1 | Released in 1.46.1; exact-candidate acceptance and binding results remain in private release records |

The existing complexity-integration plan on main is preserved.
Each plan records its own scope, acceptance criteria and release boundaries.
