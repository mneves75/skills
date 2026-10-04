---
name: tdd
description: "Use when changing behavior: a bug fix or a feature. Write the failing test first, watch it fail for the intended reason, then make it pass. Skip for prototypes, spikes, and pure config or wiring; when no cheap test path exists, say why and use the closest executable check."
---

# TDD

Before changing production code, make the intended behavior executable. For a bug, that is a focused regression test that fails before the fix and passes after it. For a feature, it is one test per agreed behavior, written and seen failing before the code that satisfies it.

Test-first is the default for behavior changes. It is not a ritual for work whose point is speed or that has no behavior of its own: prototypes and spikes (the Prototype playbook inverts the verification bar), pure config, wiring, and glue. Do not force a test when it would be impractical. If the available test would require broad harness setup, brittle mocks, slow end-to-end infrastructure, production-only state, vague reproduction steps, or large unrelated fixture churn, use the closest useful verification instead and say why.

## Workflow

1. **Understand the change.** Identify the intended behavior, the current behavior, the affected path, and the smallest observable reproduction (for a bug) or the first observable slice (for a feature).
2. **Choose the narrowest executable check.** Prefer the closest unit, component, integration, or regression test already used for that codepath. If no practical test path is obvious, do not create one from scratch just to satisfy the workflow: name why, and pick the closest executable check.
3. **Write the failing test first.** Add the smallest focused test that would catch the bug or prove the slice. The test should encode intended behavior, not mirror the current implementation.
4. **Run the new test before changing code.** Confirm it fails for the intended reason. Quote the failure content, not the assertion line: an exception, an empty result against a literal, and the predicted mismatch all print red, and only the last one proves the test measures the behavior. If it passes or fails for an unrelated reason, correct the test or reproduction before editing the implementation.
5. **Make it pass.** Make the smallest production change that satisfies the intended behavior while preserving nearby contracts.
6. **Rerun the test.** Confirm it now passes. For a feature, repeat steps 3–6 for the next slice.

## If a Failing Test Is Impractical

Use the closest executable regression check instead: a targeted script, manual reproduction command, browser automation, snapshot comparison, log assertion, or focused integration check.

Prefer no new test over a bad test. A bad test is one that mostly tests mocks, encodes current implementation details, depends on timing or unrelated global state, needs expensive infrastructure for a small fix, or would be deleted immediately after proving the fix.

## Guardrails

- Do not change tests merely to match a wrong implementation.
- Do not weaken existing assertions unless the expected behavior has genuinely changed and the reason is clear.
- Keep each test focused on one behavior. Avoid broad fixture churn or unrelated coverage expansion.
- If the bug is flaky, make the test deterministic where possible and document the signal being locked down.
- If the bug exposes a broader class of failures, first land the focused regression path, then consider additional sibling coverage.

## Final Response

Report the evidence, not just the outcome:

- Name the failing-before test or executable check and quote the failure it produced, trimmed to the diff.
- Name the passing-after test run and any nearby validation performed.
- If failing-before evidence could not be demonstrated, state why and describe the closest regression check used instead.
