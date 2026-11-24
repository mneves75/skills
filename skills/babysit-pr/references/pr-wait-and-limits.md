# `pr-wait` internals, rate limits, and billing failures

Detailed watcher behavior and GitHub API fallback rules referenced from `../SKILL.md`.

## `pr-wait` invocation and exit codes

Invoke `scripts/pr-wait` by its absolute path from the `babysit-pr` skill directory
(`tests/test_pr_wait.py` verifies it against a fake `gh` with no network):

```bash
pr-wait <pr> [--repo owner/name] [--until ready|green|any-change]
```

- **State directory:** `~/.local/state/pr-wait/` (remembers already-reported events across
  restarts so nothing arriving between runs is lost).
- **Exit `0`:** `--until` condition met or PR merged.
- **Exit `1`:** action required — required check failed, merge conflicts, `BEHIND` branch,
  unresolved review threads, PR closed, GitHub unreachable, required checks unreadable, `ready`
  unable to read every check for 10 consecutive polls, or `ready` unable to read every review
  thread.
- **Exit `2`:** bad input.

Modes:

- `ready` (default): required checks green, Greptile or Macroscope reviewed the head, and zero
  unresolved threads. Use `green` instead on repos without Greptile/Macroscope (otherwise
  `ready` waits indefinitely for a bot review that never arrives).
- `green`: required checks only, never threads.
- `any-change`: exit on the first new event.

In Claude Code, run with the Monitor tool (`timeout_ms: 3600000`) so each event line wakes you;
elsewhere run as one long command. Restart after pushing, after handling exit `1`, and after a
resume — except after "could not read every check", "could not read every review thread", or a
refused required-checks read (inspect those manually). If `pr-wait` reports another pid already
watches the PR, do not start a second; stop the old one only if its events cannot reach you.

## Required checks, App identity, and thread-list guards

- `pr-wait` reads required checks from the base branch's rulesets and classic branch protection
  before polling. A `404` from both means every CI check gates. A `403` refusal exits `1`;
  network unreachability counts as a failed poll and retries. Non-admin users may receive a
  plain `404` on classic branch protection, so a classic-only check that has not started may
  not be waited for.
- A required check bound to a GitHub App counts only results from that app (a random commit
  status with the same name never turns it green; bot statuses count only after resolving the
  app's id from its slug).
- `pr-wait` reads the last 100 review threads. When GitHub indicates older threads exist (or
  does not confirm none exist), `ready` never passes and exits `1` ("could not read every
  review thread") so older unresolved threads cannot be missed. Visible unresolved threads are
  reported first, and the summary notes "not every thread read".

## GitHub rate limits

- `gh pr create`, `gh pr view`, and `gh pr checks` spend GraphQL quota. When GraphQL is
  exhausted, REST usually still has quota:
  - Read PR: `gh api repos/<owner>/<repo>/pulls/<n>`
  - Read checks: `gh api repos/<owner>/<repo>/commits/<sha>/check-runs`
- In T3 Code, `"Stopped watching, could not read it"` usually means GraphQL quota is spent.
  Check `gh api rate_limit --jq .resources.graphql`; if `remaining` is near `0`, wait for
  `reset` with one background command before watching again — never loop tightly.

## GitHub billing failures

A check GitHub refused to start due to billing or spending limits is an infrastructure block,
not a code failure. GitHub reports it as a failed check run with zero steps and an annotation
starting `"The job was not started because"` naming billing, failed payments, or the spending
limit (`gh pr checks` cannot distinguish it).

`pr-wait` verifies annotations, step count, reporting app, and the Actions API job record
before reporting a check as `billing-blocked`. Any job that ran a step, any run from another
app, or any workflow-created Checks API run (such as a test reporter whose text can come from
the PR) remains a real failure. If GitHub cannot confirm all checks (>1,000 or page error),
`pr-wait` excuses none and waits; after 10 failed polls or a permanent `gh` error (auth,
permissions, unknown PR/repo), it exits `1`.

Never wait on or re-run a billing-blocked check: run the equivalent checks locally, record the
output as proof, and state plainly that CI was skipped and why. Without `pr-wait`, inspect
annotations with `gh api repos/<owner>/<repo>/check-runs/<id>/annotations`.
