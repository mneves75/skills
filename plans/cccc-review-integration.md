# cccc integration plan

## What the review changed

Use the upstream release binary, with reviewed SHA-256 pins, rather than a moving
source build. Preserve repository complexity policy. A successful exit alone is
insufficient: parse recovery and empty scans can produce misleading evidence.
The adversarial advisor found that `table = true` cannot be overridden with a
JSON CLI flag; retain table evidence and report that structured comparison is
unavailable instead of silently disabling the repository configuration.
Reconcile every expected supported file: unreadable files can be omitted while
the command succeeds. Correspondence between functions is manual and diff-based,
because names and lines are not stable identifiers. Installer publication uses
an exclusive hard link from a verified temporary binary, preserving a concurrent
winner and dangling symlinks. Real controls confirmed parse recovery and empty
scans return 0; a nonexistent input returns 2 with no JSON in this release.
The improve deep pass exposed optimized-Python false PASS and an unchecked
threshold report. Operational checks now raise explicit failures, and regression
controls include a real partial write before simulated disk exhaustion.

## Objective and frozen acceptance

Install moznion/cccc for local review and integrate its use into the relevant
portable review skills without replacing human/model review or changing existing
authorization. Prepare everything in this repository before requesting the exact
host installation authorization required by the owner's explicit boundary.

1. A pinned, checksum-verified upstream binary runs on this Mac, with a positive
   complexity control, a threshold failure, malformed input, and an empty scan.
2. A portable installer accepts an explicit destination, refuses replacement,
   rejects digest/archive/platform/version failures, and preserves other files.
3. Review, orchestration, audit, expert challenge and independent verification
   route supported source changes through cccc when available. Missing tooling,
   unsupported code and incomplete scans are reported, never passed as evidence.
4. Existing tests, security isolation and disclosure rules remain intact. No
   arbitrary score limit, automatic refactor or metric-driven acceptance is added.
5. Docs, version, changelog, generated site and required gates agree. Fresh
   different-model adversarial acceptance checks the final artifact.
6. Commit and push only this work. Merge/tag/catalog publication are authorized
   by the original request after CI, but host installation and copied host skills
   remain pending explicit approval immediately before their outside-repo writes.

## Scope and alternatives

Chosen: optional local analyzer with reproducible prebuilt installation, one
canonical reference in autoreview, and compact sibling fallbacks. This retains
Kotlin support and avoids compiling Rust dependencies for a small review tool.
Conservative alternative: build a pinned source revision; stronger source-level
control, but more disk/toolchain maintenance and crates.io omits Kotlin.
Premise challenge: skip the analyzer and rely on tests, focused diffs and expert
review. That avoids metric gaming, but loses a useful deterministic navigation
signal explicitly requested by the owner. Scores remain advisory for that reason.

## Implementation sequence

1. Isolate work from origin/main; preserve the existing dirty release branch.
2. Write installer regression tests first and observe failure without the helper.
   Failure modes: unknown platform, download failure, checksum mismatch, missing,
   duplicate, linked or oversized binary member, existing/dangling destination,
   invalid version and interrupted write. Never extract an archive wholesale.
3. Ship a Python standard-library installer and single release manifest inside
   autoreview, so a single-skill install contains its own installation procedure.
   Require an existing destination directory; create only the new binary.
4. Write a shared cccc review reference: exact target, config, version, commands,
   stdout/stderr/status, coverage and limitations. Analyze focused supported source
   with `--no-cache --min 0`; use JSON unless target config requires table output.
   Compare matched functions in base/target with the same binary and policy, only
   when useful; resolve deletions/renames from the diff. Do not execute target code.
5. Add routing to autoreview, Fable, superaudit, expert-review and verify. Keep
   absent-sibling fallbacks inline and respect outgoing review bundle scanning.
   Complexity cannot suppress standards, spec, tests or adversarial findings.
6. Update README/HOWTO/AGENTS/autoreview docs, VERSION and CHANGELOG to 1.32.0;
   refresh vendor default verification date from current primary model lists;
   regenerate site and add deterministic installer controls to CI's existing suite.
7. Run real binary controls in isolated temporary fixtures, repository typecheck,
   lint, ast-grep, skill spec, hook, site, defaults, lane and autoreview gates.
8. Run requested improve deep as a separate read-only advisory phase; use the
   installed Matt Pocock two-axis standards/spec method against this request and
   pinned base. Its missing issue-tracker setup does not justify host edits.
9. Fix confirmed in-scope problems, run fresh mneves-verify, commit/push and follow CI.
   This is a portable CLI skill and static catalog, not a native app. Stage the
   immutable source distribution as `v1.32.0-beta1` with a GitHub prerelease, then
   merge only the verified candidate to main. Verify the production GitHub Pages
   catalog contains the new guidance before tagging/releasing `v1.32.0`. No native
   store submission, server runtime or fabricated separate staging site applies.
10. Present exact global binary and host-skill copy targets for approval. Clean
    only task-created unused temporary evidence/worktree after delivery; preserve
    the pre-existing branch and worktree. Never delete their changes.

## Validation and maintenance

Installer controls use mocked downloads and temporary directories, never a
provider or root privileges. Real smoke checks exercise the pinned binary and
inspect JSON `summary.file_count` and `summary.parse_error_count` regardless of
exit status. Existing autoreview test runner owns deterministic tests; real CLI
smoke uses an explicitly supplied binary path and runs locally.

Five-year pass: do not maintain a second complexity engine or general wrapper.
Keep CLI pins in one manifest, update checksums only after checking upstream
release assets, preserve a positive and failure control on upgrades, and treat
language/parser changes as measurement changes. Re-baseline deliberately; never
silently compare scores from different versions. SHA-256 pins prove consistency
with reviewed release bytes, not independent upstream provenance or safety.

## Primary evidence

- [cccc release and installation](https://github.com/moznion/cccc/releases/tag/v1.8.0)
- [Pinned CLI and config source](https://github.com/moznion/cccc/tree/9008fbfb747bdbd7651e3e6311307005659f003b/crates/cccc-cli/src)
- [Google review guidance](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
- [SonarSource cognitive complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf)
- [OpenAI model catalog](https://developers.openai.com/api/docs/models)
- [Claude model catalog](https://platform.claude.com/docs/en/models/overview)
