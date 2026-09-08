# Autoreview beta review and release

Scope: import and harden the portable autoreview skill. Baseline collection commit:
`fabfb7463429c0943220f3312152c63945f5e506`. Upstream source:
`openclaw/agent-skills@3e9f33968ac732aa2fa7873e9dfc5823b5216c49`.
The user's specification requires Astra medium, an account-access Sol xhigh fallback,
independence from the borrowed checkout, security review, independent reviews, and a beta release.

## Acceptance

- The installed skill and a clean tagged archive resolve Astra medium and Sol xhigh; explicit
  primary model/effort overrides retain their documented precedence.
- Access errors retry once; rate limits, capacity, scanner failures, malformed reports, and
  source mutation retain fail-closed behavior. Every outgoing retry is scanned.
- The package includes the MIT copyright/license, source revision, complete helper and tests,
  portable paths, and one authoritative maintenance contract.
- Submodule reads retain the outer executable trust boundary. Output validation protects both
  the target and the directory entry actually replaced, including home expansion.
- The complete test suite, skill validators, existing collection gates, independent standards
  and spec reviews, and P3 autoreview must be assessed before release.
- Release an immutable beta tag and verify its downloadable skill; record hosted CI and
  documentation deployment separately from local evidence. No stable production tag is implied.

## Research and ten alternatives

This assessment uses published guidance, not endorsements or personal consultations.
[Martin Fowler's YAGNI](https://martinfowler.com/bliki/Yagni.html) supports avoiding unused
extension points while retaining tests and maintainability. [OWASP's prompt-injection guidance](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)
supports enforcing permissions outside the model and treating retrieved content as untrusted.
[SLSA provenance](https://slsa.dev/spec/v1.2/provenance) supports tracing an artifact to its source;
this release records provenance but does not claim a SLSA level. The
[Matt Pocock code-review workflow](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md)
separates standards compliance from specification compliance.

Compared with the original unversioned local copy, ten alternatives were considered.
Scores are engineering judgments on a 1–5 scale, weighted by security preservation (40%),
installation independence (25%), maintenance (20%), and simplicity (15%). A score does not
override a failed requirement.

| Alternative | Security | Independence | Maintenance | Simplicity | Decision |
|---|---:|---:|---:|---:|---|
| Environment variables only | 4 | 1 | 3 | 5 | Cannot independently select retry effort or remove checkout dependency |
| Shell alias with CLI flags | 4 | 1 | 2 | 5 | Same gaps; shell-specific behavior |
| User Codex profile | 4 | 1 | 3 | 4 | Helper intentionally isolates most user configuration |
| Keep the upstream symlink | 4 | 1 | 4 | 5 | Violates installation independence |
| Git submodule | 4 | 2 | 3 | 3 | Requires recursive checkout support in installers |
| Wrapper that downloads upstream | 2 | 3 | 2 | 3 | Adds runtime network and moving-source trust |
| Owned portable adaptation with pinned provenance | 5 | 5 | 4 | 4 | Selected: 93/100; preserves tested boundaries with a small local delta |
| Rewrite a Codex-only helper | 2 | 5 | 3 | 2 | Discards tested multi-engine behavior and isolation code |
| Publish a separate Python package | 4 | 5 | 3 | 2 | Adds a release/dependency channel without a current need |
| Containerized review service | 4 | 4 | 2 | 1 | Adds credential handling, deployment, and operational ownership |

The strongest contrary argument is that an upstream wrapper is smaller and easier to update.
It loses here because the required fallback effort is not exposed as a Codex CLI option and
runtime dependence is explicitly unwanted. Reconsider packaging only if distribution needs
change; do not build a generic policy framework for two model attempts.

## Findings and five-year assessment

The initial implementation met the model request but should have entered version control with
its license and reproducible test environment immediately. A default-only change cannot establish
the safety of inherited code. Independent review found two pre-existing defects: nested
snapshots could trust a parent-controlled executable, and output validation could approve a
different location from the one subsequently mutated. Both have failing-before/passing-after
regressions and safe positive controls.

Five years from now, model names and CLI capabilities will likely have changed. The durable
parts should be ownership, explicit configuration precedence, immutable release identity, and
tests of actual subprocess arguments and trust boundaries. Keep model policy at the retry
owner; update pinned upstream provenance with reviewed imports. Avoid parallel installed copies
with silent drift or a broad rewrite justified only by file size.

## Evidence status

- Local suite: 290 tests, 289 passed and one platform-specific skip. The macOS sandbox checks
  ran with the installed Codex CLI. All three security regressions failed before the fixes
  and passed afterward; a separate reviewer repeated the focused regressions successfully.
- Standards review: no confirmed standards violations or actionable smell findings.
- Spec review: no findings against the requested defaults, fallback, portability, licensing,
  test coverage, and collection integration. Both reviews used independent contexts under
  Matt Pocock's two-axis workflow; neither substitutes for a live provider run.
- All eight skills passed `skills-ref@0.1.5` validation and appeared in installer discovery.
  Skill validation, Python/Bash syntax, ast-grep, the pre-commit hook test, tools typecheck,
  and tools lint passed. The existing lint gate reports 53 warnings and 21 informational
  diagnostics, with zero errors; these are unrelated pre-existing debt.
- Gitleaks found no secrets in the packaged skill. A temporary nonfunctional token-shaped
  positive control inside the scanned scope was detected and removed. `bun audit` reported
  no vulnerabilities in the 13 checked tooling packages.
- The local catalog and usage section rendered in desktop and mobile browser viewports;
  the mobile page had no horizontal overflow at 390 pixels. The isolated browser was closed.
- The local-only autoreview dry run passed complete bundle scanning, source verification,
  and Codex isolation preflight with Astra medium and the Sol fallback selected. The first
  scan correctly refused a synthetic credentialed-proxy URI; constructing that nonfunctional
  `.invalid` fixture at runtime preserved both passing rejection tests without disabling scans.
- Candidate `217197c57a80e8bd4855e01f08741462724e592b` was committed and pushed. Its Linux
  autoreview suite and collection CI checks passed. GitHub Pages deployment
  [34180352699](https://github.com/mneves75/skills/actions/runs/34180352699) succeeded;
  both hosted pages returned HTTP 200 and matched the committed generated files byte-for-byte.
- Live P3 autoreview, hosted CI, beta publication, archive verification, and installed-copy
  synchronization remain release gates. No claim is made that every provider account or
  runtime has been live-tested.
