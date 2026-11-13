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
  `--baseline` on the previous release when cases are marked `changed`. Only a full run, every
  case on both claude and codex, can meet a threshold; `--cases-only` and single-provider runs
  are for diagnosis. The baseline control passes only when every unchanged case passes and every
  changed case fails every sample: a changed case that passes on the baseline does not
  discriminate, and the control fails until the case is replaced or no longer marked changed.
  A case marked `"changed": "clarified"` had its source reworded to remove an ambiguity without
  changing its expected answer: the candidate run judges it, and the baseline run records its
  counts in `clarified_on_baseline` and fails only on an errored sample.
  Output stays with the release's private gate records. Live runs call paid models and are
  never run by CI.

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
  - A cross-model review of the tracked runner found three defects, fixed before release. The
    Codex consumer could run commands: `-s read-only` limits what a command may do, it does not
    remove the shell tool (a probe ran `id -u` and answered with the user id; with
    `--disable shell_tool` it answered that it had no tool). The 1.47.0 runs therefore had a
    Codex consumer that could have used a tool; their answers were schema-bound and graded the
    same way, but "without tools" was true only of the Claude consumer. The runner now disables
    the shell tool and fails any sample whose event stream shows a tool.
  - The other two: a subset run could report the threshold met, and a baseline on which a
    changed case passed still exited 0. Both now fail.
  - Two more rounds found the same guarantee still open: a tool-using Codex attempt could be
    retried into a pass when the call timed out or answered badly, and then when reading its
    answer file failed (independent acceptance, ACC-R01). Patching each path had failed twice, so
    the retry loop was removed: each sample is asked once, and any failure is an error. No live
    sample had needed a retry (0 of 198). A provider hiccup now fails the run, which is rerun.
- **1.51.0, revision 8.** O1 expects the Claude main session on Opus at reasoning medium and
  stays changed. On text equal to the 1.51.0 candidate's, 204 of 204 samples passed; the baseline
  on 1.50.0 met its control (198 of 204, every O1 sample failing as expected). Private records:
  the 1.51.0 gate's `routing-eval/` and `routing-eval-baseline/`.
- **1.51.1, revision 9.** New O14 expects the reviewer fallback (Fable at reasoning high) when no
  Codex account can run, marked changed; O3 and O4 follow the edited reviewer row with unchanged
  expectations.

## Open

- P11 needs a replacement that fails on text which lowers Opus for a routine job.
- No case covers the local-fallback seat or the specialist seat.
