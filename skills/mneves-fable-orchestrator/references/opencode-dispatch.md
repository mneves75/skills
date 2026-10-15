# opencode dispatch reference

Read this before the first `opencode-lane` command. The orchestrator skill owns role selection;
this file owns the opencode worker's mechanics, its boundary and when to escalate. The caller
names the model with `-m`; no model is bound here.

Contents: status · when to use it · the boundary · one lane · what the lane enforces · failure
classes · acceptance and escalation.

## Status

An opt-in trial. The opencode worker does not replace any role binding. In the evaluation that
introduced it, four small coding tasks with hidden tests, it matched the Codex worker. That is
evidence of feasibility only. Bind a role to it only after a frozen set of at least 20
representative bounded tasks, run three times each and paired with the configured worker, meets
thresholds declared before the runs.

## When to use it

One objectively verifiable coding task: a bug fix with a failing test, a feature with a written
specification and tests, or a mechanical change gated by a type check or a grep. It runs in a
throwaway Git worktree outside your home directory (for example under `/tmp`) whose content you
trust and may send to the model's provider. Never use
it on customer or regulated data, on secrets, or in a tree holding credentials. A provider's
retention and training terms are its own published statement; read them before routing private
code.

The lane never reads your credentials, so it can only run models the provider offers to an
anonymous client: list them with `opencode models` in a fresh store (`XDG_DATA_HOME` pointing at an
empty directory). That roster rotates, sometimes within a day, and a model offered to a signed-in
account may be missing from it. "Offered" says nothing about privacy: some no-cost models may use
your prompts for training during their free period, so read the provider's privacy terms for the
exact model before routing code to it. A no-cost offer can end without notice; the lane then
refuses the model before any call.

## The boundary

The opencode harness has no operating-system sandbox, and its permission rules are not a
boundary against the model:

- The project directory comes from `$PWD`, not from the process working directory. A worker
  spawned with another `cwd` and an inherited `PWD` acts on the caller's tree.
- The user's global configuration loads every installed skill and MCP server, and the default
  agent allows every tool.
- A project `opencode.json` outranks the user profile, and a project `.opencode/plugins/*.js`
  runs code inside the harness at startup.
- It reads `.claude`, `.agents` and `.opencode` in every ancestor of the project up to `/`, and
  aborts when one is unreadable. A worktree under your home inherits your personal agent
  configuration and instructions that way.
- A fresh store resolves the model only after the model catalog arrives; a cold start can fail
  with `Model unavailable`.
- Configuration hot-reloads: a worker that writes `opencode.json` widens its own permissions
  within the same round.
- `external_directory` rules cover the file tools only; shell deny rules miss `bash -c "..."`.
- A guard plugin keyed on a tool name can stop working when the harness renames the tool, with no
  error. Prove any guard you rely on with a command it must block.
- `ask` permissions are rejected in a headless run; use allow and deny only.
- Permission rules are an array of `{action, resource, effect}`; a block in another shape is
  ignored without an error. Denying `webfetch` alone is not enough: the `execute` tool (Code
  Mode) can fetch too.

So the lane contains the worker with the operating system. On macOS it generates a Seatbelt
profile per round and runs the worker under `sandbox-exec`:

- **Reads** of your home directory, mounted volumes and the shared temp trees are denied, except
  the workspace, the lane's private box, the Git common directory (read-only), the opencode
  install, the real git, and directories you pass with `--allow-read`. Parent directories of
  those are listable, not readable.
- **Writes** go only to the workspace and the box, plus `/dev/null`, `/dev/zero`, the process's
  own descriptors and pseudo-terminals the worker opens itself, so it can neither write into
  nor read from your other terminals.
- **Keychain and clipboard** services are unreachable.
- The worker gets a private home and private opencode stores in the box, and an environment
  holding only `PATH`, `LANG`, `TERM`, `PWD` and the box paths. Your sessions, auth, skills and
  MCP servers are invisible to it.
- **Same-user IPC** is closed where Seatbelt can close it: no signals or process information for
  other processes, no Unix-socket connections except DNS (so no ssh-agent or Docker socket), no
  preferences daemon and no Apple Events.
- The **network stays open**, because the model needs it. Whatever the worker can read, it can
  send; the read rules exist for that reason.
- **Process environments are not protected.** macOS lets any process read the initial
  environment and arguments of the same user's other non-Apple processes, and Seatbelt does not
  mediate it. The lane keeps its own processes' environments to a short allowlist, but a secret
  exported in your shell or in the coordinating agent's environment is readable by the worker.
  Keep secrets out of process environments while a lane runs, or isolate the worker under a
  separate macOS user or in a VM.
- The worker cannot touch Git metadata: writes to the workspace's `.git` entry (a clone's
  directory or a worktree's pointer file), to the Git common directory, and to a hooks directory
  that `core.hooksPath` places inside the workspace are denied, so it cannot plant or change
  hooks or redirect the repository, and it cannot stage or commit. The coordinator commits after
  acceptance. Other Git settings that point at files inside the workspace (an `fsmonitor` script,
  filter or diff drivers) are not protected: review those files in the diff before running git.
- The environment the worker sees is the lane's allowlist plus the few variables opencode's own
  shell adds (such as `OPENCODE*`, `AGENT`, `SHLVL`).

Other platforms are refused until a sandbox with the same self-test exists for them. Neither
`sandbox-exec` nor the lane runs inside another sandbox, such as a sandboxed Codex session: start
the lane from an unsandboxed coordinator.

## One lane

```bash
git worktree add /tmp/wt-fix-123 -b fix/123        # a throwaway tree outside your home
cd /tmp/wt-fix-123
opencode-lane start fix-123 /path/to/spec.md -m <provider/model> \
  --allow-read ~/.bun                               # a toolchain installed under your home
opencode-lane last fix-123                          # the worker's final report
opencode-lane next fix-123 - < gate-failure.log     # a correction in the same session
opencode-lane exec fix-123 -- bun test              # run a gate inside the same sandbox
opencode-lane drop fix-123
```

`start` takes the specification from a file or stdin (`-`) and never puts it in argv. A test
command that fails inside the lane with "Operation not permitted" on a path under your home
usually means a toolchain needs `--allow-read`.

## What the lane enforces

| Behavior | Why |
|---|---|
| Records the workspace, its Git top level and common directory at `start`, and checks them again before every round; refuses a second lane on the same workspace. | The harness binds from `$PWD`; two workers would overwrite each other. |
| Refuses to run when `opencode.json`, `opencode.jsonc` or `.opencode/` exists in the workspace or any ancestor, or `.claude`, `.agents`, `AGENTS.md` or `CLAUDE.md` in any ancestor; exits 5 if the worker created project configuration. | Project configuration outranks the profile and can run code; ancestors leak instructions or abort the harness. |
| Warms the model catalog with `opencode models` before every round and refuses a model it does not list. | A cold store cannot resolve the model; an ended offer is caught before any call. |
| Generates the Seatbelt profile and runs a self-test before every round and every `exec`: a workspace write must succeed; a write into the lane's state, to the workspace's `.git` entry or to a hooks directory inside the workspace, a read of the lane canary or a home canary, and a keychain query must fail. | Containment is proven each time, not assumed. |
| Writes a lean profile into the box: no skills, MCP servers or plugins; denies questions, subagents, web tools, Code Mode, outside paths, `.env` reads and common destructive git and `rm` commands. | Fewer tokens and fewer accidents; not the boundary. |
| Runs the round in its own process group with a first-event timeout and a total timeout (exit 124, no automatic retry). | A silent run may still have had effects. |
| Replays the model with `--session <id>` on `next`; one writer per lane. | Corrections keep the worker's context. |
| Reads the session export after each round and exits 4 if another model ran. | A report is not proof of which model ran; the check is not tamper-proof. |

## Failure classes

- **Exit 2 before any model call**: a refused precondition (unsupported platform, not a Git tree,
  workspace moved, agent configuration in the tree or an ancestor, a second lane on the
  workspace, a failed self-test, a model the catalog does not offer, an empty prompt, a bad
  flag). A refused `start` releases its name, so retry directly. `busy` names a lock directory:
  remove it only when no lane run is alive. `corrupt lane state` names a state file to inspect
  and remove.
- **Exit 3** or opencode's own code with `provider error` on stderr: the provider failed or
  returned nothing. The no-cost model is intermittently unavailable; retry later, then escalate.
  `opencode-lane log <lane>` holds the events.
- **Exit 4**: another model ran. Do not accept the work.
- **Exit 5**: the worker created agent configuration, or something on the Git hooks path changed.
  Inspect it before any next round and before running git in the workspace.
- **Exit 124**: a hang or overrun. Check the workspace for partial changes before running again;
  repeated hangs mean the provider is unavailable.

## Acceptance and escalation

Accept as for any delegated work: read the diff first, then rerun the gates yourself, and
inspect test and guard edits closely. Gates execute code the worker wrote, so run them inside
the lane's sandbox with `opencode-lane exec <lane> -- <command>` until you have read that code;
run them unsandboxed only after the diff review.

Commit the worker's output with Git hooks disabled, after running the hooks' checks inside the
lane: `opencode-lane exec <lane> -- <the hook or its check command>`, then
`git -c core.hooksPath=/dev/null commit ...`. Hooks often call scripts or package tooling that
live in the workspace, which the worker could change; the lane denies writes to the hook files
themselves and exits 5 with "Git hooks changed" if anything on the hooks path changed during a
round, but it cannot vouch for everything a hook calls. Escalate to the Codex worker with the failure evidence after two failed
correction rounds, on any exit 4 or 5, or as soon as the task needs judgement the specification
did not settle. The lane's state, logs and the worker's sessions live in the lane directory;
`drop` removes them.
