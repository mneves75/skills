# Git target edge cases

Exact scope of each `--mode`, plus the details that matter once the mode is chosen.

## Scope of each mode

| Target                         | Arguments                      | Scope                                                       |
| ------------------------------ | ------------------------------ | ----------------------------------------------------------- |
| Local work                     | `--mode local`                 | HEAD → index → working tree, plus untracked files           |
| Local candidate against a base | `--mode local --base <ref>`    | Pinned base → index → working tree, plus untracked files    |
| Committed branch/PR            | `--mode branch --base <ref>`   | Merge-base → HEAD; excludes dirty work                      |
| One commit                     | `--mode commit --commit <ref>` | Raw parent → commit; a root compares against the empty tree |

`--mode auto` selects local work when dirty, otherwise a branch review using the
PR base or `origin/main`. Clean main has no implicit review target.
`--mode uncommitted` is an alias for local. The helper does not fetch refs.

## Nested checkouts

Registered nested linked checkouts from the same repository are outside the
current review scope. Their presence or edits do not make the parent dirty;
ordinary adjacent files remain included and scanned. Worktree boundaries are
revalidated without changing Git ignore rules.

## Complete PR candidate including dirty rewrites

For a complete PR candidate **including dirty rewrites**, use local mode with
its pinned merge base—not branch mode:

```bash
pr_base=$(gh pr view --json baseRefName --jq .baseRefName)
merge_base=$(git merge-base HEAD "origin/$pr_base")
"$AUTOREVIEW" --mode local --base "$merge_base"
```

## Staged and unstaged states

When a file has both staged and unstaged changes, both states are reviewed.
A defect in the index remains actionable even if the working tree fixes it;
the report labels it `INDEX-only`.

## Diff fidelity

Git display settings cannot suppress context markers or add patch colors;
repository configuration is not changed. Source paths and text retain literal
whitespace. Source identity remains mandatory.

## Line endings and executable filters

Local selection honors `core.autocrlf` from external operator Git configuration,
with repository-local values and attributes retaining precedence. Only its
validated scalar value reaches diff/status; other global and system Git
configuration stays disabled. Repository-owned or relative global-config
overrides are not imported, and reviewed source bytes are not rewritten.

Local collection disables effective Git clean/process commands and requires
conversion to succeed. Unused drivers, unchanged filtered neighbors, staged-only
changes, and deletions can still be reviewed without executing converters.
If Git needs executable conversion to assemble the diff, collection fails before
any reviewer starts. This can include an unchanged filtered file whose stat cache
needs refreshing. Use explicit branch or commit mode for committed content in
that case. Built-in line-ending normalization remains enabled; raw bytes never
stand in for a required executable conversion.

## PR-base discovery

PR-base discovery uses trusted external Git and a scoped GitHub CLI environment,
preserving external authentication/configuration and proxy settings while excluding
inherited Git routing, `GH_REPO` redirection, and checkout-owned executables.
A differently named `AUTOREVIEW_GIT` override that cannot also be selected as `git`
by the child requires an explicit `--base`; rejected GitHub configuration paths
also require one.
