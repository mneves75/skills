# Codex dispatch reference

Read this before the first `codex exec` or `codex-lane` command issued from another agent or
harness. The orchestrator skill owns role selection; this file owns launcher mechanics.

Contents: where Codex finds skills · one round or a lane · flags, resume, and fork · diagnose
before retrying · optional account-aware launcher (not shipped) · coding and review fallback CLI (not shipped) · acceptance.

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

Append a changed requirement or a new test result as a follow-up. Identify which earlier
assumption it supersedes. Editing prior messages or tool history can cause the API to discard
reasoning items. Resume provides continuity, not a guarantee of a cache hit.
See [OpenAI's guide to conversation history](https://developers.openai.com/api/docs/guides/keep-prefix-unchanged).

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

## Coding and review fallback CLI (not shipped)

When no Codex account can run (not installed, out of quota, not signed in, or refused by host
policy), the orchestrator's Defaults block routes coding and review after `gpt-6.2-sol` to
`gemini-4-neon-xhigh` through Antigravity CLI (`agy`, **not shipped with this skill**).
`agy-yolo` is a personal wrapper/alias for `agy --dangerously-skip-permissions` (**not shipped**;
substitute `agy --dangerously-skip-permissions` only where unattended tool execution is explicitly
authorized).

Never send a repository that declares client, personal, or regulated data, or one whose owner has
not approved that provider; host-policy or task restrictions on a provider are not a reason to
route around them, and disclosure must be authorized before dispatching. When disallowed or
unavailable for review, skip this fallback explicitly and fall through to the reviewer row's second
fallback.

### Coding fallback

Unattended coding fallback with `agy-yolo` (`agy --dangerously-skip-permissions`) must run inside
a dedicated worktree **within an enclosing external sandbox (container or VM)** that bounds the
filesystem, credentials, lifecycle hooks, plugins, and workspace MCP servers, and only when the
owner or host policy explicitly authorizes unattended execution (never widening permissions beyond
the authorized Codex seat). Why an enclosing container or VM is required:

- On hosts without OS sandbox support (such as Linux without unprivileged user namespaces),
  `--sandbox` degrades to a no-op; on personal accounts, Antigravity ignores `unsandboxed(*)` deny
  rules and defaults to Auto mode (since 1.5.7) unless forced to Default mode (`"agentMode": ""`).
- Lifecycle hooks (`PreInvocation`, `SessionStart`, etc.) and workspace MCP servers
  (`.agents/mcp_config.json`) execute outside the agent's terminal sandbox with host privileges,
  even before interactive approval prompts appear.

Without an enclosing container or VM, **report the coding fallback blocked** rather than launching
an uncontained worktree session.

Inside an authorized enclosing container/VM sandbox, pass the brief from a mode-`0600` file over
stdin `stream-json` (never argv), clean up temporary files even under `set -e` while preserving
the exit status, and verify `.result.status == "SUCCESS"` before accepting `.result.response`:

```bash
# Run ONLY inside an enclosing container/VM sandbox with explicit owner/host authorization:
run_agy_coding_fallback() {
  local brief_file="$1" settings_file="" out="" status=0
  settings_file=$(mktemp) || return $?
  chmod 600 "$settings_file" || { rm -f -- "$settings_file"; return 1; }
  printf '{"agentMode":"","allowNonWorkspaceAccess":false,"enableTerminalSandbox":true,"permissions":{"deny":["unsandboxed(*)"]}}\n' > "$settings_file" \
    || { rm -f -- "$settings_file"; return 1; }

  out=$(set -o pipefail; jq -Rsc '{event:"user",message:{content:.}}' < "$brief_file" \
    | agy-yolo --sandbox --settings "$settings_file" \
        --input-format stream-json --output-format stream-json \
        --model gemini-4-neon-xhigh --print "" --print-timeout 10m) || status=$?
  rm -f -- "$settings_file"
  [ "$status" -eq 0 ] || return "$status"
  jq -re 'select(.event == "result" and .result.status == "SUCCESS") | .result.response' <<< "$out"
}
```

### Read-only review fallback

Run the first read-only review fallback through the sibling `autoreview` skill (**not shipped with
this skill**), preserving the original review's exact Git target, priority, prompt, and restriction
flags (`--mode`, `--base`, `--commit`, `--max-priority`, `--prompt-file`, `--dataset`,
`--no-tools`, `--no-web-search`) so the fallback changes only the reviewer engine and model:

```bash
# Example: preserve every original target, priority, prompt, and restriction flag unchanged:
ORIGINAL_REVIEW_ARGS=(--mode branch --base origin/main --max-priority P3)
python3 /path/to/autoreview/scripts/autoreview \
  "${ORIGINAL_REVIEW_ARGS[@]}" \
  --engine agy --model gemini-4-neon-xhigh
```

If the original review restricted tools or web search (`--no-tools` or `--no-web-search`), pass
those flags unchanged: `autoreview --engine agy` refuses before launch because Agy's built-in
`search_web` cannot be disabled up front. Treat that refusal as a reason to skip Agy and move to
the reviewer row's second fallback while preserving `--no-tools` / `--no-web-search`.

`autoreview --engine agy` handles the full isolation boundary: TruffleHog secret scanning, isolated
auth-only `HOME`/`USERPROFILE`/`XDG_*` (preventing global/plugin hooks, plugins, and user MCP
servers from running), `AGY_CLI_DISABLE_AUTO_UPDATE=true`, environment scrubbing (preserving ADC
region/project vars while refusing unforwarded custom endpoints like `GOOGLE_GEMINI_BASE_URL`,
unverified home/gateway configurations, unpreservable ADC files, and unrequested direct
`GEMINI_API_KEY` routing), an empty non-Git launch workspace, stdin NDJSON `stream-json` (zero argv
exposure), `--disable-slash-commands --sandbox` with Default-mode strict deny-all `--settings`
(never passing `--dangerously-skip-permissions`), and strict stream verification of
`permission_mode == "strict"` and tool outcomes.

If `autoreview` is not installed on the host, do **not** run an ad-hoc unisolated `agy` command on
untrusted code: skip the first fallback explicitly (recording that `autoreview` is not installed)
and fall through to the reviewer row's second fallback (or install `autoreview` first).

## Acceptance

The caller verifies the actual diff, focused tests, and any required independent review. A model
report is not proof. Preserve unrelated working-tree changes and stop if the executor overlaps a
file another agent still owns. Before editing or committing in that repository, check for a live
worker (`pgrep -fl "codex exec"`): a run whose deliverable is already in the tree can keep looping
and overwrite your fixes mid-review, so stop it once its output is verified.
