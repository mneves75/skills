# Decision log, optional cleanup, and verification checklists

Detailed templates and preservation-proof rules referenced from `../SKILL.md`.

## Illustrative decision log

Connect every planned or applied fix to concrete evidence, preserved contracts, and proof.
The rows below are **illustrative**, not findings about any real repository:

| Fix / alternative | Problem and evidence | Contracts and proof | Status |
|---|---|---|---|
| Extract a shared integer tax calculation; reject a configurable pricing framework | Two checkout entrypoints copy the same rounding rule, confirmed by callers and a traced rate change | Keep both public entrypoints, per-line rounding and empty-order result; run existing entrypoint tests and rounding boundaries before/after | Planned |
| Retain the authorization wrapper and bounded transient retry | Call traces show denied requests stop before the side effect, and only transient failures retry | Exercise authorized/denied calls, exhausted retries and permanent failures | Retained |

For real findings, record exact locations, rejected alternatives and costs, baseline and
post-change evidence, and unresolved questions. Keep deferred out-of-scope discoveries separate.

## Optional cleanup (separate explicit opt-in only)

Run cleanup last, after all structural checks pass, and only for the separately opted-in
category. Cleanup opt-in never overrides host deletion or test-method approval rules.

- **Comments:** keep invariants, ordering requirements, external constraints, security rationale,
  and non-obvious workarounds. A comment resembling the implementation may still state a
  necessary precondition. Remove only demonstrated restatement or obsolete explanation, and
  record where necessary context remains. Remove a workaround's comment only after proving the
  underlying constraint is resolved.
- **Tests:** apparent duplication, internal assertions, or wiring checks are not removal
  evidence. For every proposed deletion or rewrite:
  1. Inventory each assertion, the behavior or invariant it protects, and its positive/negative
     and boundary cases.
  2. Map each assertion to a kept or replacement assertion.
  3. Execute equivalent replacement proof, including a controlled regression proving the
     replacement catches what the original caught.
  4. Protect legitimate registration, authorization, and configuration wiring assertions.
  Missing assertion-level preservation evidence or equivalent proof means keep the original.
  Never delete or weaken a failing test merely to pass.

## Final report contents

Include:

- Changed paths and starting/ending revision (when Git is available).
- Problem-to-fix decisions and rejected alternatives.
- Retained safety mechanisms and special cases with rationale.
- Actual commands and flow outcomes (baseline vs post-change, including bad inputs).
- Per-criterion `PASS` / `FAIL` / `BLOCKED` status and independent review/acceptance results
  (distinguishing local checks from deployed proof and supplied skill text from native host
  discovery).
- Unresolved, blocked, or deferred items and evidence limits.
