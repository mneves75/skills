# Playbook: build or fix

1. **Frame.** Name the entry points, the callers and the acceptance check. For a bug, reproduce
   it first, and stop to rethink after two failed fixes.
   - Hard or slow bug: `diagnosing-bugs`. Fallback: a reproduction loop that tests one
     hypothesis at a time against a measured result.
   - Unfamiliar code: `how` before editing it.
2. **Design check**, when the change crosses a module or service boundary.
   - `architect` for types and module shape, or `mneves-expert-review` for a trade-off with real
     downside.
   - Fallback: a short note of interfaces and invariants written before the edit.
3. **Test first.** `tdd`. Fallback: write the failing test, watch it fail for the right reason,
   then make it pass.
4. **Implement.**
   - One track: edit directly, in minimal scope.
   - Independent tracks: `mneves-fable-orchestrator`, one brief per track with goal, context,
     constraints and done-when.
   - Fallback: run the tracks one after another, and do not claim parallel review independence.
5. **Review.**
   - `code-review` checks standards and spec. `autoreview` is the independent adversarial pass on
     a fixed Git target.
   - Fallback: a fresh read-only reviewer on the diff.
   - On risky work with no independent reviewer, mark the gate `BLOCKED`.
6. **Verify.** `mneves-verify` in a fresh context, run again after each fix until it passes.
   Fallback: run the full checks yourself and say that independent verification did not run. On
   risky work the gate stays `BLOCKED`.
