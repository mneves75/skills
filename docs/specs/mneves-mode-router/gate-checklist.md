# Gate checklist (frozen before any v3 text)

Source: the owner's standing prompt, pasted at the start of long tasks. Native trials pass when
every gate that applies to the trial task runs, in the order below. The selection probe cannot
prove this; only a trial transcript can.

Each gate sits in one bin:
- **Shipped:** the v3 body names it. It uses a skill in this repository, or a rule with no
  machine dependency.
- **Sibling:** a third-party skill. It goes in `references/optional-siblings.md` with a fallback.
- **Overlay:** an owner-only rule. It goes in the private overlay, never in shipped text.

| # | Gate | Bin | Skill or rule | Applies when |
|---|---|---|---|---|
| G1 | Reconcile with origin and merge before work | Shipped | rule | always in a repository |
| G2 | Frame goal, smallest verifiable change, risk tier | Shipped | rule | always |
| G3 | Tests first for behavior changes | Sibling | `tdd` (Pocock); fallback pstack `tdd` or a failing test written first | code changes |
| G4 | Skip tests for code with cognitive complexity ≤ 5 unless it contains a regular expression | Overlay | `cccc` floor | code changes |
| G5 | Survey for improvements and fix what is in scope | Sibling | `improve` (shadcn); fallback: main-session survey | when the owner names it |
| G6 | Standards and spec review of the diff | Sibling | `code-review` (Pocock); fallback `autoreview` | code changes |
| G7 | Full source security audit and fixes | Shipped | `security-audit`, then `mneves-security` for fixes | when the owner names it |
| G8 | Trim tests that guard no behavior | Overlay | `mneves-prune-tests` (not shipped here) | after implementing and testing |
| G9 | Independent verification until it passes | Shipped | `mneves-verify` | after G8 |
| G10 | Track status in `tests.json` and progress in `progress.md`; `init.sh` if needed | Overlay | rule | long tasks |
| G11 | Version bump, changelog and docs, commit, push | Shipped | rule | release |
| G12 | Pre-deploy security verdict on the exact commit | Shipped | `mneves-security` | before a deploying push, merge or tag |
| G13 | Merge to the default branch, tag, delete branch and worktree | Shipped | rule (remote branch delete is Overlay) | release |
| G14 | Production deploy, then staging teardown | Shipped | `mneves-ship-deploy` (`ship-prod`) | when the owner names it |
| G15 | Remove scratch, worktrees and caches the task created | Shipped | rule (owner disk-cleanup tools are Overlay) | before reporting done |
| G16 | Stop before destructive, outside-repository or external actions | Shipped | rule | always |
| G17 | Private report and owner notification | Overlay | owner report and notification tools | complex or sensitive changes |

Order for a full trial: G1, G2, (G3, G4 while building), G5, G6, G7, G8, G9, G11, G12, G13, G14,
G15, then G17. G10 and G16 hold throughout.

A trial fails if a gate that applies is skipped, runs out of order, or the transcript claims it
ran without a tool call that shows it.

## Amendment (2026-11-27, before any trial ran)

The frozen text above stays as written. Two reviews found rows that contradict the skill that
owns the gate, so trials grade against these corrections instead:

- **G13** merges and deletes the branch and worktree. It tags only a release that nothing
  deploys. Otherwise the tag follows G14's live proof, as `mneves-ship-deploy` requires.
- **G12a**, new: readiness on the same commit before a staging or production deploy
  (`mneves-production-readiness`, Shipped).
- **G14** tears down staging only after a production deploy succeeds; `ship-staging` stops after
  the staging proof. A merge that deploys production runs inside G14, after the staging proof
  and the owner's approval of the exact candidate and target.

Amended order: G1, G2, (G3, G4 while building), G5, G6, G7, G8, G9, G11, G12, G12a, G13, G14
(deploy, live proof, tag, teardown), G15, then G17.
