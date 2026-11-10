# Routing eval

An expected-outcome eval of the routing text: does an agent that reads the shipped skill text
dispatch the model and reasoning effort each seat is meant to run at? Cases live in
`tools/routing-eval/cases.json`; `tools/scripts/routing-eval.py` checks and runs them.

## What it covers

- The orchestrator's Defaults block: every Claude seat, the Codex main session, the crossed
  reviewer rule and the short-alias dispatch rule (cases O1 to O12).
- pstack's model and effort text on Claude Code, Pi and Codex: the Reasoning effort paragraph in
  every skill that has one, poteto-mode's per-job adjustment, the Pi alias table and panel line,
  and setup-pstack's defaults (cases P1 to P19, S1 and S2).
- Autoreview's engine defaults are not here. Its own tests and `test-review-harness.py` cover
  the command it actually builds.

## How it is used

- CI runs `routing-eval.py check`. It proves the cases are well formed and that each case's
  anchors, the passages that decide its answer, still exist in the files the case reads. A
  removed or reworded passage fails the check, which means: update the case, then run live.
- The check does not catch a contradicting sentence added elsewhere in a file. Only a live run
  does.
- A release that changes routing text runs `routing-eval.py run` on its candidate, and with
  `--baseline` on the previous release when cases are marked `changed`. Output stays with the
  release's private gate records. Live runs call paid models and are never run by CI.

## History

- **1.47.0, revisions 1 to 4 (private scratch).** Built after two independent acceptance rounds
  failed readiness AI-01 for lacking an eval of the changed model configuration.
  - Revision 1: 17 cases. A red run on the pre-fix text found Pi's panel line holding Opus at
    `xhigh`.
  - Revision 2: wording of two cases; two cases added for poteto-mode's per-job raise and lower,
    which found Opus moved to `high` or `low`. Both defects were fixed in pstack adaptation 07.
  - Revision 3: nine pstack cases now state that the job needs no per-job adjustment. A control
    on the 1.46.1 text had failed two unchanged cases that left the job open.
  - Revision 4: sixteen cases added for seats and files a third acceptance round found without a
    selecting case.
  - Result on the 1.47.0 candidate: 198 of 198 samples passed (33 cases, three samples, two
    consumers). On the 1.46.1 text, 50 of 52 changed-case samples failed as expected and 14 of 14
    unchanged-case samples passed. Case P11 passes on the 1.46.1 text too, so it does not catch
    a regression.
- **1.48.0, revision 5.** The set moved into the repository unchanged. Anchors were added
  beside the cases, outside each case's identity, and CI runs the check. The release-specific
  combiner (cross-run reuse, the 1.46.1 baseline and the red-run record) was not carried over;
  the runner applies one threshold to one run.

## Open

- P11 needs a replacement that fails on text which lowers Opus for a routine job.
- No case covers the local-fallback seat or the specialist seat.
