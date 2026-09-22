# Codex dispatch reference

Read this before the first `codex exec` or `codex-lane` command issued from another agent or
harness. The orchestrator skill owns role selection; this file owns launcher mechanics.

Contents: where Codex finds skills · one round or a lane · flags, resume, and fork · diagnose
before retrying · optional account-aware launcher (not shipped) · acceptance.

## Where Codex finds skills

Codex reads skills from `.agents/skills` (from the working directory up to the repository root)
and `$HOME/.agents/skills`; Claude Code reads `~/.claude/skills`. `npx skills@latest add
mneves75/skills` links the skill into both. A Codex session that cannot see this skill is
reading a different directory, not a broken install.

## One round or a lane

A single round is a plain `codex exec`. Two or more rounds on one objective use a named lane so
follow-ups retain thread context:

```bash
codex-lane start <lane> /path/to/spec.txt -- -s workspace-write
codex-lane next <lane> 'Continue with the attached failing gate.'
codex-lane last <lane>
```

Pass long follow-up material on stdin (`codex-lane next <lane> - < build.log`). Send fixes,
review findings, and gate failures through `next`. A lane records its working directory and
launch arguments; do not try to change model, sandbox, or cwd mid-lane.

A new objective is a new thread. A thread saturated by a long job misreads a fresh work order as
configuration and no-ops ("Understood…"); start a new `codex exec` or lane for it instead of
resuming the old one. A worker that stopped under its spec's escape hatch is not saturated:
resume it with the coordinator's decision, which is cheaper than a fresh order.

`codex-lane start` is synchronous. Give each worker its own harness-tracked background command
that outlives a short tool timeout, then monitor that specific lane. Never `&`-fork workers from
a shared launcher (its tracking ends at fork time and the workers run unsupervised), and never
use broad process-name termination.

If a killed start wrote a `thread.started` event but no lane state, recover the thread id from the
specific lane log and adopt it with the original cwd and launch flags. Drop only a genuinely empty
stub; restarting a recoverable thread discards context. After any resume outside the wrapper,
check the log tail for `Usage: codex exec resume`: a flag the subcommand rejects prints usage,
runs nothing, and a harness may still report success.

Parallel workers in one repository get one worktree and one distinctive branch each, fresh from
the default branch, with a shared spec body and a per-target header. Landing serializes on the
repository's own lock: a held lock belongs to a sibling, so back off and retry from the failed
step; never recover a lock you did not create.

## Flags, resume, and fork

- Global flags (`-s`, `-p/--profile`, `-m`, `-c`, `--json`, `-o`) must precede `resume`:
  `codex exec resume -s read-only` is a parse error. `codex-lane` orders them correctly and
  replays the stored set on every `next`; `codex exec resume` takes its sandbox and model from the
  current invocation, not from the thread.
- `codex exec fork <thread-id> [prompt]` branches a thread into a new session. Use it to try two
  follow-ups from the same state (an A/B on one executor); `codex-lane fork <lane> <new-lane>
  <prompt>` does this and records the branch as its own lane.
- Named profiles live in `$CODEX_HOME/<name>.config.toml` and load with `--profile <name>`;
  legacy `[profiles.<name>]` tables in the base file make `--profile` fail. Homes that share the
  base config should link the same overlays when they expose the same named profiles.
- Never pass credentials through `-c`, argv, a prompt, or a log. When a run needs different
  provider settings, write a private overlay (a mode-0700 directory holding a mode-0600
  `config.toml`, plus `auth.json` if the provider needs it) and point `CODEX_HOME` at it.

## Diagnose before retrying

If a run exits quickly with no expected artifact, inspect its launcher output and the session or
lane log. Common classes:

- **Exhausted quota or authentication**: the log names the account; switch homes deliberately.
  `401 Invalid API key` means the configured bearer is not valid at that endpoint.
- **Invalid model or provider routing**: model availability differs by account even when the CLI
  and shared config are identical. `502 / All target providers failed` with a `target_providers`
  list means the model id did not match the router's catalogue; `stream disconnected` against a
  loopback URL means nothing is listening there. One request settles it, cheaper than a rerun:
  `curl -s -o /dev/null -w '%{http_code}\n' -m 8 <base_url>/models`. Record the exact error; do
  not silently substitute a model.
- **Resume refused**: `thread/resume failed: list_turns is not supported` means the backend cannot
  rehydrate a long thread. Codex exits non-zero after printing the *previous* final message;
  `codex-lane next` reports the refusal on stderr and withholds that stale message. Relaunch a
  fresh `codex exec` with a self-contained order that restates branch, worktree, and PR.
- **Unsupported sandbox policy**: retry once with the CLI's documented safer alternative. Never
  bypass the sandbox because a run failed; full access needs the same authorization as any other
  consequential action.
- **Real zero-work response**: the spec was already satisfied or misread; fix the brief.

A long run is healthy while its specific log or CPU time continues to advance. A live process
whose log has not grown for about five minutes is hung, not thinking: stop only that PID, then
resume the same lane so no context is lost.

Codex validates the whole shared configuration before dispatch: a retired key or legacy profile
table can break an otherwise unrelated command. Reproduce with `--strict-config` before changing
shared state, and use a private temporary configuration home when another session is actively
editing the real one. Do not silently repair or bypass another session's in-flight configuration.

Resume the same lane after an interruption. Change strategy only when the error identifies a
configuration or permission mismatch.

## Optional account-aware launcher (not shipped)

`codex-auto` is a personal launcher that picks a configured Codex home with available quota and
pins the model and effort from the Defaults block; plain `codex exec` is the substitute. If you
have one, keep every command for a lane, and any `autoreview` run, on the same selected home:

```bash
selected_codex_home="$(codex-auto home)"
CODEX_HOME="$selected_codex_home" codex-lane start <lane> /path/to/spec.txt -- -s workspace-write
CODEX_HOME="$selected_codex_home" codex-lane next <lane> 'Continue with the attached failing gate.'
```

Lane state stores launch arguments, not environment variables, so omitting `CODEX_HOME` on `next`
can resume under another account. Its live quota probe runs the executor model at low effort in
an isolated read-only directory with user instructions and skills disabled. Automatic account
selection and an explicit profile must produce the same model policy; environment overrides such
as `CODEX_AUTO_MODEL` are deliberate exceptions, checked in the session header.

## Acceptance

The caller verifies the actual diff, focused tests, and any required independent review. A model
report is not proof. Preserve unrelated working-tree changes and stop if the executor overlaps a
file another agent still owns. Before editing or committing in that repository, check for a live
worker (`pgrep -fl "codex exec"`): a run whose deliverable is already in the tree can keep looping
and overwrite your fixes mid-review, so stop it once its output is verified.
