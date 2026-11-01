---
name: babysit
description: Watch an open PR — fix failing CI, handle the straightforward review comments, and drive it to a mergeable state. Claude Code analog of Cursor's built-in /babysit. Use after opening a PR when the user wants the agent to shepherd it without re-prompting.
---

# Babysit a PR

On Codex, read the [platform mapping](../poteto-mode/references/codex-tools.md), including its per-skill notes, before following this skill.

On GitHub Copilot, read the [platform mapping](../poteto-mode/references/copilot-tools.md), including its per-skill notes, before following this skill.

Claude Code analog of Cursor's built-in `/babysit`. The implementation is a loop over `gh` CLI, paced by the Claude Code `loop` skill when it is installed.

When the `babysit-pr` skill is installed, use it instead: its watcher is the authoritative one, and this skill adds nothing to it. The steps below are the complete fallback for an install that has only this skill and `gh`.

A PR has one continuation owner. Before starting a loop, check whether another watcher already owns this PR (`babysit-pr`, the poteto-mode playbook, a `loop` or scheduled re-check from earlier in this session). If one does, report its state and do not start a second.

Inside poteto-mode, the **Babysit** playbook ([`../poteto-mode/playbooks/babysit.md`](../poteto-mode/playbooks/babysit.md)) supersedes this skill: it owns mode declaration, the merge frontier, stack safety, and the `watch-pr` watcher. This skill stays the standalone `/babysit` entry point for a single PR outside a poteto-mode run.

## When to use

- There's an open PR and the user explicitly wants it kept green, and you are not already inside a poteto-mode run (the playbook owns that case).
- The user invokes `/babysit` directly.
- A subagent that opens a PR does NOT babysit — return to the parent and let the parent decide.

## Steps

1. **Fetch PR state.**

   ```bash
   gh pr view <number> --json number,title,state,mergeable,reviewDecision,statusCheckRollup,mergeStateStatus,comments,reviews
   ```

2. **Triage in priority order.**
   - Merge conflicts (`mergeStateStatus == DIRTY`): run the **fix-merge-conflicts** skill when installed; otherwise merge the base branch into the PR branch and resolve each conflict by reading both sides. Never force-push without the user's clearance (see Hard rules).
   - Failing checks (`statusCheckRollup` entries with `conclusion: FAILURE`): run the **fix-ci** skill when installed; otherwise read the failing log with `gh run view <run-id> --log-failed` and reproduce it locally. Root-cause the failure; fix the underlying code or test; commit; push.
   - Review comments: run the **get-pr-comments** skill for the summary when installed; otherwise read `gh pr view <number> --comments` and `gh api --paginate repos/{owner}/{repo}/pulls/<number>/comments`. Act only on feedback you actually agree with. When a comment has a single mechanical answer — a rename, a guard clause, a formatting nit — make the edit and quote the comment in the commit message. When it hinges on a judgement call, or you can't tell what's being asked, don't guess: leave it and put what you would have done in the report.
   - Review-bot comments (Bugbot and similar automation): classify fix/dismiss/ask before acting, per [`bugbot-triage.md`](../poteto-mode/references/bugbot-triage.md). Ask by default on security, data, and high-severity findings.

3. **Loop.** Use the Claude Code `loop` skill to pace re-checks when it is installed; otherwise re-run steps 1–2 yourself at the interval below and state the cadence in the report. Pick the interval from what you're watching:
   - Active CI run: poll `gh pr checks <number> --watch` (it blocks until checks finish, so no separate loop interval needed).
   - Awaiting reviewer: 20–30 min heartbeat.
   - Idle but want to catch new comments: hourly.

4. **When to stop.**
   - Build is green, every comment resolved, branch merges cleanly → call it ready.
   - You've run three rounds of fix → push → recheck and it still isn't fully green → stop, summarise what's still broken, and hand control back. Report the PR as blocked, not ready: the round cap is an escalation signal, never a completion.
   - The next fix would force a design choice → pause and put it to the user with `AskUserQuestion`.

5. **Report.** Summarize fixes applied, comments addressed, comments deferred (with reason), current PR status. Cite each commit by SHA.

## Hard rules

- Invoking babysit on a PR covers commits and pushes to that PR's own head branch. Posting replies or comments, resolving threads, requesting reviewers, `gh pr ready` and any other write to the PR or the forge need the user's explicit request or a standing permission for that write; otherwise put the draft in the report.

- Don't rewrite history on a branch others may have pulled. If a rebase or force-push looks necessary, clear it with the user first.
- Don't tweak a test's expected values just to get a pass. Only change an assertion when the behaviour genuinely changed and the assertion was pinned to the old behaviour.
- Never skip hooks (`--no-verify`).
- Never bypass a failing check by marking it as not required.
- `gh pr ready` only when the user asked for it, all checks are green and no unresolved review comments remain.

## Cross-refs

- Opening a PR does not start a babysit; inside poteto-mode the Babysit playbook owns the request and starts only when asked.
- Use `interrogate` before opening if the diff is contested; once open, babysit takes over.
- Use the active writing preferences on any prose you write here (PR comments, commit messages, status reports).

## Provenance

This is a Claude Code analog of Cursor's `/babysit`, not a port — Cursor's implementation is closed source. The skill is independently authored, with its own prose and structure; the workflow is informed by Cursor's public `/babysit` behavior. The only overlap with other PR tools is the `gh` CLI commands it runs, which are functional invocations rather than copied text.
