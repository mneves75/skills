---
name: takeover
description: Take over and finish someone else's PR, branch or agent thread while keeping their credit. Use when asked to take over existing work.
license: MIT
---

# Takeover

Take responsibility for finishing the original goal while preserving the
original contributors' credit. Do not defend an implementation just because
another agent already built it.

Read the source PR, branch, or thread, including review findings and the user's
later corrections. Resolve the handoff to the actual code and current head,
and account for uncommitted work. Treat the handoff as context, not proof:
claims of "done", "tested" or "fixed" in it are leads to check.

For a replacement PR, import the original commits onto a new branch and add
your fixes separately. Honor an explicitly requested in-place or stacked
continuation instead. Do not overwrite unrelated work or change the original
PR without authorization.

Preserve Git authorship and existing co-author trailers. Credit the original
contributors in the PR description and link the original PR when there is one.
If the work will be squashed, preserve human author/co-author credit in the
merge commit too, using verified identities rather than guessed emails. Model
attribution is not a substitute for contributor credit.

Update the continuation against its intended base and current architecture
(the sibling `modernize` skill does this when installed; otherwise fetch the
base, rebase, and check whether the base already solved or reshaped the goal).
Rework what is necessary to finish the same goal, not unrelated features.
Simplify the implementation without dropping intended behavior or surfaces.
Recheck the source PR too: it may have improved while you were working.

## Proof

Proof is evidence you observed yourself in this session: command output, a
reproduction, a rendered screen. Reproduce the original failure, apply the
finished change, and watch the same reproduction pass; run the checks the
repository's CI runs; add one focused test that fails without the change when
the behavior has none. For UI and runtime behavior, run the app: green mocked
tests do not prove the user experience works. State what remains unverified.

## Finish

When the requested finish includes a PR, file or update it with a description
that leads with the problem, then the solution, then one line on how you proved
it. Then watch it through CI and review rather than stopping at creation (the
sibling `babysit-pr` skill when installed; otherwise wait on `gh pr checks
--watch` and read new reviews after each push). Format every comment posted for
the user with the sibling `leaving-pr-comments` skill when installed; otherwise
open it with a one-line note naming the model and that it responds on the
user's behalf. Merge or close the original PR only when authorized.

Report what you inherited, what you changed, how you proved it, how credit was
preserved, and any remaining decision.

## Provenance

Adapted from [tstack `takeover` at revision `1085050f`](https://github.com/t3dotgg/tstack/tree/1085050f3baed1ac724caa4a8166145fb2ac88af/skills/takeover).
Copyright (c) 2026 Theo Browne; distributed under the [MIT License](LICENSE). Local changes:
Agent Skills metadata, an explicit Proof section, fallbacks for every sibling skill so a
single-skill install works, and the PR description rule folded in from tstack's `file-pr`.
