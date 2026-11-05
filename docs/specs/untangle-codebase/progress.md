# Untangle-codebase adoption

## Confirmed scope

The owner requested review of caldoai/skills' `untangle-codebase`, approved the adapted
standalone addition, asked to follow the feature process, and confirmed the invocation
boundary on 2026-11-05. This is a single-session feature with no separate implementation
tickets. Retain this checkpoint because independent gates remain blocked.

- Invocation alone produces diagnosis and a plan, then awaits edit approval. An explicit
  refactoring request authorizes implementation within its stated scope without another ask.
- Preserve the change-together lens, dependency graph, Git evidence and decision log.
  Require a bounded target, observed baseline, preserved contracts, per-unit regression
  checks, and evidence before treating special cases as defects.
- Comment/test cleanup is separately opt-in; retain invariants and safety mechanisms.
  Test removal or rewriting requires assertion preservation and executed replacement proof.
- Ship a portable standalone Markdown skill, exact MIT notice and pinned provenance,
  catalog/guide/routing integration and aligned 1.46.0 release preparation.
- Run native behavioral trials and affected gates, then independent review and acceptance.
  Commit/push on the working branch and open a PR. Merging, tagging, publication and global
  installation were not authorized.

The strongest rejected alternative was folding the workflow into `codebase-design`:
module-design vocabulary and a refactoring lifecycle have distinct triggers and installation
needs. The dedicated skill has no mandatory sibling or new executable/dependency.

## Implementation and evidence, 2026-11-05

Base: `f0abfa0151fd97bb3491fbef02d060bd2a1dfa1e`, reconciled with `origin/main` (0/0).
Upstream: `442c29918339cc8dbf09ae27aaf17b05745465a3`; MIT license preserved byte for byte.
Trialed skill SHA-256: `d6312e3a28c81228b473dfe6668aa176aa7dc1890f38b8d1827060cb7712b2bd`.
The final skill matched this hash after the trials. Detailed private evidence is retained
under `.scratch/untangle-adoption/`; it is task evidence, not a shipped dependency.

- **PASS — packaging:** all 24 root skills passed `agentskills validate`;
  `npx --yes skills@latest add . --list` discovered 24, including the new entry.
- **PASS — tooling:** `bun run typecheck`, `bun run lint` and `bun test` from `tools/`.
  Tests: 102 pass, 0 fail, 291 assertions. Lint exited 0 with 24 informational diagnostics
  in unchanged tooling; no automatic fixes were applied.
- **PASS — site:** `build-site.sh`, `build-site.test` (including planted violations),
  `check-defaults-block.sh`, its planted controls and `git diff --check`.
  Model identifiers were rechecked against vendor lists before advancing the verification
  date; model choices were unchanged. URLs and evidence limits are in private task scratch.
- **PASS — local browser:** copy unavailable/rejected/success, landing and guide overflow at
  390px and 1440px, light/dark contrast (nine existing cases); new catalog entry, keyboard
  focus and card-to-guide navigation at both widths. Desktop/mobile screenshots inspected.
  A baseline browser assertion failed before the entry was added. The retained baseline tab
  needed an explicit reload before final checks; that stale observation is not a source defect.
  One final pointer-navigation wait timed out with the browser still on the landing page;
  the refreshed accessibility tree exposed the correct link and retry navigated successfully.
  The timeout is retained in `new-guide-flow-final.log`; no source cause was established.
- **PASS — bare invocation:** fresh supplied-file trial diagnosed duplication, retained
  retry/authorization mechanisms, and stopped for edit approval. Main checked every original
  fixture file remained byte-identical. The trial read repository `MEMORY.md` incidentally,
  contrary to its brief, and disclosed it; no memory content was used in its diagnosis.
- **PASS — authorized refactor:** fresh trial proceeded without another edit-approval ask,
  centralized the tax rule and retained both public wrappers. Main re-ran seven behavioral
  tests, checked original tests/service byte-identical, and executed 7,000 comparisons
  between original implementations and the refactored calculation.
- **PASS — invalid scope:** blank, nonexistent and contradictory scope requests produced
  clarification without widening the target. The first long-input scenario was descriptive;
  a retained follow-up exercised the actual 8,000-character payload with unchanged hashes.
- **PASS — opted-in test cleanup:** the trial retained both entrypoint assertions in a shared
  test after generating a preservation map and controlled-regression replacement proof.
  Five methods became three; assertion coverage was preserved. This is not blanket permission
  to remove apparently duplicate tests.
- **PASS — honest fallback:** trials reported independent gates BLOCKED when reviewers were
  unavailable; none represented a self-check as independent acceptance.

These trials exercised an explicitly supplied skill file in isolated fixtures. They do not
certify native catalog selection, all hosts, universal refactor safety or productivity gains.
Installer discovery and procedure behavior are separate evidence. Browser evidence is local,
not a deployed preview or production proof. Existing browser tooling reported an older Chrome;
this task did not update the host browser. `cccc 1.8.0 --no-cache --min 0` probed the changed
landing HTML, generated guide and new skill entrypoint with default configuration discovery
(no repository `cccc.toml`): zero recognized files/functions and zero parse errors.
Markdown/HTML/text changes therefore have no supported complexity evidence or score.

## Initial implementation checkpoint: open gates

The statuses below describe the implementation checkpoint before release authorization.
The owner subsequently authorized the PR's merge and production publication. That authority
does not imply a passing gate: final binding results belong to the private candidate records
and annotated release tag, so a later deployment does not rewrite this historical checkpoint.

- **BLOCKED — two-axis adversarial review:** the required crossed-model reviewer is unavailable.
- **BLOCKED — mneves-verify independent acceptance:** no compliant different-model seat ran.
  Native trials and main's self-check are not substitutes for these gates.
- The configured implementation/reviewer seat and its alternate runtime were unavailable.
  Implementation used the configured fallback through `codex-auto`. Exact runtime errors
  stay in private task evidence; no account configuration changed.
- Restore the configured reviewer, or obtain an explicit owner waiver of the named gates,
  before calling this feature independently accepted or its PR ready to merge. Then freeze
  the current candidate, run the two review axes and `mneves-verify`, and resolve findings.
- At this checkpoint, no merge, tag, production release or global skill installation had occurred.

Existing `docs/handoffs/`, `tools/node_modules` and `.scratch/skills-ref` were preserved.
Task-created browser/server processes are closed during closeout; small cited evidence stays.
