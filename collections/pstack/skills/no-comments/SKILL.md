---
name: no-comments
description: "Spawn the comment-sicko subagent, fix accepted findings, and offer encodings for claimed constraints."
---

# No comments

On Codex, read the [platform mapping](../poteto-mode/references/codex-tools.md), including its per-skill notes, before following this skill.

Spawn comment-sicko. Act on accepted findings.

Defer to comment-sicko's fresh perspective.

## Scope

Use the caller's files or diff. Otherwise use the current diff against the base branch, default `main`, including the working tree.

## Steps

1. Spawn an `Agent` with `subagent_type: "pstack:comment-sicko"`. Pass the scope. Do not restate its rules.
2. Inspect its report and diff. Reject application-code edits, scope escapes, exception-protected deletions, misstated `MUST KILL` reasons, and flags that treat kept intentional code as guilty. Reshape flags on our-code surprises stay actionable. Do not restore those comments. A keep survives only with proof it is about something we cannot change. Audit missed scoped lint and TypeScript suppressions. Correctness or safety suppressions stay actionable `MUST KILL`s. Restore deletions only with exact exceptions and scoped proof. Before accepting thin `IMPORTANT` or `do not remove` kills or keeps, run `/how` or `/why` on their symbol. If a kill is ambiguous, do not restore. If a keep is refuted or still ambiguous, delete it. Revert and rerun one rejected report with the failure named. Reject a second, report it open, and fail `/no-comments`.
3. Fix trivial accepted flags directly by deleting a dead path, dropping a parameter, or using the real API. If any fix needs a shape, run `/architect` once for the accepted set and surrounding code. Stop at the sketch. Architect shapes. Step 4 implements.
4. Implement the smallest root-cause fix in scope. Remove every named workaround. If the root cause is out of scope, land the smallest in-scope fix and report the rest open. The [verification guidance](../poteto-mode/references/engineering-verification.md) and [evolution guidance](../poteto-mode/references/engineering-evolution.md) guide intent only. Neither authorizes widening the fence nor fixing instances outside it. Never bolt on symptom guards.
5. For a comment asserting a constraint, verify its purpose and owner. If an authorized in-scope type, runtime check, test, or lint can enforce the same constraint, implement and verify that replacement before deleting the comment. If the replacement needs a new decision or exceeds scope, preserve the comment and report the open constraint. Prior authorization for that exact change remains valid.
6. Report the deletion count, restored comments, reruns, architect sketch, fixes, encoding offers, encodings, unenforced constraints, and other open work.
