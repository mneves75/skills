# Evidence and completion

Read this when choosing proof for a bug fix, multi-step change, or generated check.

Start with the smallest check that could falsify the claimed outcome. For a bug,
prefer a failing reproduction and a regression test at an existing test seam.
Minimize the reproduction when that materially separates causes. When the runtime
is unavailable, continue useful static analysis, label hypotheses, and state the
missing runtime evidence instead of fabricating a pass or abandoning all work.

Choose checks for user-observable behavior or important invariants, not a mirror
of the implementation. A build proves compilation; it does not alone prove the
feature. A negative assertion needs a positive control when an empty scan could
pass. Put the control inside the same path and selector scope as the gate.

Before keeping a test, name a relevant defect and confirm the whole arrangement,
setup included, detects it; introduce the defect temporarily where practical.
Assert the required result or effect through the public interface, including
absence and fixed values when the contract requires them. An expectation computed
through the same faulty path confirms itself.

Verify the process as well as the outcome. For each fact you relied on, name the
record it came from and confirm it is the one the project's rules point at; a
correct result can rest on a paste or a file never read.

Red is a colour, not a measurement. A failing check proves the instrument only
when the failure content is the disagreement you predicted, so quote the
assertion's diff, never the assertion.

When two fixes sharing an assumption fail the same gate, write the assumption
down and choose an observation that can challenge it before a third fix depends
on it. For uneven allocation, count the work per actor before recommending a
reassignment.

Before you trust, report, or act on a number you measured (a speedup, a
regression, a throughput, a latency, or an eval result), ask why it is not twice
as good. Name the limiter from a profile or system counters taken during a run,
not from reading the code. Rule out each other thing the number could be
measuring: failed requests, skipped or cached work, code that never ran, an
untuned side, noise, and a changed piece too small to matter end to end. Keep the
run count, the spread, and the limiter with the number. For a performance number,
run the `benchmark-checklist` skill. For an eval result, ask whether every trial
did the task and whether the gap holds across trials and models.

For repetitive edits or checks, build a small reusable script when it is cheaper,
more reliable, or easier to review than manual repetition. Do not create tooling
for a one-off task already handled clearly by an existing command.

Split large work at boundaries that can be verified independently. Verify each
required unit and its integration before claiming completion. Run documented
repository gates without masking their exit status. Re-run only after a relevant
change, failure, or unresolved concern; stop polishing once the acceptance criteria
and required checks pass.

Encode a recurring, concrete failure in a type, test, or lint rule when that
prevents it reliably. Demonstrate the gate catches the actual violation before
adding it. Otherwise retain a short conditional explanation at the owning code.
