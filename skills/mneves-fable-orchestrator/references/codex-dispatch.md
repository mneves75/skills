# Codex dispatch reference

Read this reference only when invoking `codex-auto` or `codex-lane` from another agent or
harness. The orchestrator skill owns role selection; this file owns launcher mechanics.

## Account-aware launcher

`codex-auto` is the entry point when installed. It chooses a configured profile with available
quota, then pins the default model and effort. Typical commands:

```bash
codex-auto home
codex-auto exec -s workspace-write - < /path/to/spec.txt
codex-auto review --commit <sha>
```

Use `--opm-profile <id>` only when the caller deliberately selects an account. Automatic account
selection and an explicit profile must produce the same model policy.

Current Codex CLI releases load named profiles from `$CODEX_HOME/<name>.config.toml`; legacy
`[profiles.<name>]` tables in the base file make `--profile` fail. Keep shared provider definitions
in `config.toml` and profile-specific model settings in the overlay file. Homes that share the
base config should link the same overlays when they are meant to expose the same named profiles.

The heavy-executor model and effort come from the Defaults block in `SKILL.md`, and `review`
uses the advisor/reviewer role from the same block — this file does not restate them. The live quota probe uses that model at `low`, disables user instructions and skills, and runs
in an isolated read-only directory.

For a deliberate exception, set `CODEX_AUTO_MODEL` and `CODEX_AUTO_EFFORT`; review uses
`CODEX_AUTO_REVIEW_MODEL` and `CODEX_AUTO_REVIEW_EFFORT`. Do not pass `-c model=...` through the
wrapper: its explicit `--model` flag has higher precedence. Check the session header when model
identity matters.

Never pass credentials through `-c`, argv, a prompt, or a log. Use the approved credential tool
or a private configuration home with restrictive permissions.

## One round or a lane

A single round uses `codex-auto exec`. Two or more rounds on one objective use a named lane so
follow-ups retain thread context:

```bash
selected_codex_home="$(codex-auto home)"
CODEX_HOME="$selected_codex_home" codex-lane start <lane> /path/to/spec.txt -- -s workspace-write
CODEX_HOME="$selected_codex_home" codex-lane next <lane> 'Continue with the attached failing gate.'
CODEX_HOME="$selected_codex_home" codex-lane last <lane>
```

Keep the same selected home on every command for that lane. Lane state stores launch arguments,
not environment variables; omitting `CODEX_HOME` on `next` can resume under another account.

The `$autoreview` script does not go through the wrapper either: run it with the same explicit
`CODEX_HOME` or it lands on an exhausted account and reports only `codex engine failed (1)`.
If that account refuses the required model, report the exact error. Use another engine or model
only when the caller explicitly selects that exception.

Pass long follow-up material on stdin. Send fixes, review findings, and gate failures through
`next`; start a new lane only for a different objective. A lane records its working directory and
launch arguments. Do not try to change model, sandbox, or cwd mid-lane.

`codex-lane start` is synchronous. The caller must use a process mechanism that can outlive its
own short tool timeout, then monitor the specific lane rather than killing shared Codex
processes. Never use broad process-name termination.

If a killed start wrote a `thread.started` event but no lane state, recover the thread id from the
specific lane log and adopt it with the original cwd and launch flags. Drop only a genuinely empty
stub; restarting a recoverable thread discards context.

## Diagnose before retrying

If a run exits quickly with no expected artifact, inspect its launcher output and session or lane
log. Common classes are exhausted quota, authentication, invalid model/provider routing, an
unsupported sandbox policy, or a real zero-work response. A long run is healthy while its
specific log or CPU time continues to advance.

Codex validates the whole shared configuration before dispatch. On the current CLI, custom
providers must use `wire_api = "responses"`; a retired key or legacy profile table can break an
otherwise unrelated command. Reproduce with `--strict-config` before changing shared state, and
use a private temporary configuration home when another session is actively editing the real
one. Do not silently repair or bypass another session's in-flight configuration.

Model availability can differ by account even when the CLI and shared config are identical.
When an account rejects the configured model, record the exact API error and let the account-selection policy
choose a compatible home; do not silently substitute another default model.

Resume the same lane after an interruption. Change strategy only when the error identifies a
configuration or permission mismatch. Do not bypass the sandbox merely because a run failed;
full access requires the same authorization as any other consequential action.

## Acceptance

The caller verifies the actual diff, focused tests, and any required independent review. A model
report is not proof. Preserve unrelated working-tree changes and stop if the executor overlaps a
file another agent still owns.
