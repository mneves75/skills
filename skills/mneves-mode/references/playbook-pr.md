# Playbook: PR lifecycle

Match the PR's situation. Do not stack workflows that overlap.

- **Watch CI and review bots:** `babysit-pr`. Fallback: read the checks and every page of review
  comments, fix the real findings in at most three rounds, then stop at the merge gate.
- **Failing checks or conflicts only:** `fix-ci` or `fix-merge-conflicts`.
- **Aging or stale PR:** `modernize`. Fallback: read the base branch's new commits first, then
  decide to modernize, rework or close before any rebase.
- **Finish someone else's PR or thread:** `takeover`. Fallback: keep the original commits and
  author credit, and never rewrite shared history.
- **Make it easy to review:** `make-pr-easy-to-review`. It changes no code behavior.
- **Post GitHub comments:** `leaving-pr-comments`. Fallback: disclose that an agent drafted or
  posted the comment for the user.
- **Hand off to another session:** `mneves-handoff`. Fallback: a continuation prompt without
  local paths, stating the goal, the verified facts and the open questions.
- **Unattended change to a ready PR:** `full-stop`, only when the user typed it.

Every PR workflow ends at the merge gate. Before pushing a follow-up fix, check the PR's
auto-merge and merge-queue state, and stop if the push could merge it. Never merge, force-push
shared history or change auto-merge settings without the user's explicit authorization.
