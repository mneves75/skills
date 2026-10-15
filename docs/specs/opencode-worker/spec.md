# Spec: opencode worker lane for the orchestrator

Status: revised after three adversarial reviews (2026-10-15). The owner asked whether the
no-cost DeepSeek V4.1 Flash on OpenCode can implement tasks as a subagent, or as an autonomous
worker for a plan written by another model, and then to build the result.

## What the reviews changed

- **An independent reviewer's hostile worker found same-user IPC open** (H20): sockets, signals,
  preferences, Apple Events. The profile now closes them. It also showed that Seatbelt cannot hide
  other processes' environments (H21), which the docs now state instead of implying isolation.
- **Live rounds through the built lane changed the outcome.** opencode reads agent configuration in
  every ancestor of the workspace (H18), so worktrees go outside the home. And the provider stopped
  offering the evaluated model to anonymous clients during the day while the signed-in account kept
  it (H14): the credential-free lane cannot run it today. Account support would put a billing
  credential where the worker can read it, so it is the owner's decision, not built. The lane checks
  the anonymous roster before every round and refuses a model it does not list.
- **Acceptance testing of the built tool found the box profile in a shape opencode ignores** and
  a Code Mode bypass of the web deny (H15, H16); both fixed and pinned by tests. Keychain and
  clipboard services are denied (H17).
- **Containment moved from Codex's sandbox to a lane-generated Seatbelt profile.** The Codex
  sandbox limits writes but not reads, and it ignored a `deny_read` requirement from a private
  Codex home (canary read in both arms). The lane's own profile denies reads of the user's home,
  mounted volumes and shared temp trees, and it was proven with canaries against the real model.
- **The worker gets a private home, private opencode stores and a minimal environment.** The
  no-cost model works with no credentials and empty stores, so nothing of the owner's (sessions,
  database, auth, skills, MCP servers) is visible or writable.
- **No unsandboxed mode, no pass-through arguments, no automatic retry, no review mode.** Each
  contradicted the safety contract or assumed a hang had no side effects.
- **Project configuration is checked up to the filesystem root**, and the sandbox, not the
  check, is the boundary (a worker can create and delete configuration within a round).
- **No role is rebound and no model is bound.** Four tasks show feasibility, not dependable
  performance; the caller names the model with `-m`, and a binding waits for the trial gate below.
- **The benchmark is auditable**: briefs, fixtures, hidden tests, grader and results are in
  `evidence/`.

## Assumptions (owner said "do it all"; no interview)

1. The deliverable lives in `mneves-fable-orchestrator`, not a new skill: routing stays in one
   place and the tool mirrors `codex-lane`.
2. macOS first. The sandbox uses `sandbox-exec`; other platforms are refused until a sandbox
   with the same self-test exists for them.
3. Only models that run without credentials are supported, so the lane never touches the
   owner's credentials. A paid model needs an account and an explicit spending decision.
4. Host changes (shell wrappers, the opencode dcg plugin, global routing, the installed skill
   copy) are outside this repository and are proposed, not made.

## Evidence (this Mac, opencode 2.0.27 updated itself to 2.0.29 during the work, 2026-10-15)

### The model and the offer
- `opencode/deepseek-v4.1-flash-free`: cost 0, context 200K, output 32K, reasoning and tool calls
  (models.dev catalog). Paid siblings exist with 1M context.
- OpenCode Zen privacy page: "Its provider follows a zero-retention policy and does not use your
  data for model training." The offer is "for a limited time"; no rate limits are published.
- Served only on an OpenAI chat-completions endpoint: it cannot back a Claude Code subagent
  directly (Anthropic Messages) and needs a harness, opencode itself.
- With empty private stores and no credential the client is anonymous. In the morning the
  anonymous roster included this model and it answered with `env -i` and private stores; by 12:50
  (UTC-3) the anonymous roster listed 11 models without it, while the signed-in roster listed 74
  with it, in the same minute.

### Harness hazards (each reproduced)
| # | Finding | Evidence | Consequence |
|---|---|---|---|
| H1 | `opencode run` takes the project directory from `$PWD`, not the process working directory. | A probe launched with `subprocess.run(cwd=probe)` from the main checkout ran its shell tool in the main checkout. | A spawned worker acts on the caller's tree. |
| H2 | The default profile loads every global skill (≈400 here) and MCP server (6, ≈270 tools incl. desktop GUI control), and the `build` agent allows `*`. | 52,822 input tokens for "reply OK"; `mcp connected` per server. | A quarter of the 200K window spent before work; GUI tools auto-approved. |
| H3 | The dcg OpenCode plugin does not intercept shell in v2 (tool `shell`, plugin checks `bash`). | `git reset --hard HEAD` ran; `dcg` alone returns `deny`. Upstream dcg #547, open. | No destructive-command guard in opencode sessions on this host. |
| H4 | `external_directory` rules cover file tools only. | Write tool denied, `printf > outside` succeeded. | Permission rules are not a sandbox. |
| H5 | Shell deny rules block plain and `&&` commands but not `bash -c "..."`. | Commands 1-2 denied, 3 ran. | Deny rules reduce accidents only. |
| H6 | `ask` in a headless run is rejected, not hung. | "This non-interactive run cannot ask the user for permission…" | Profiles use allow and deny only. |
| H7 | One run of 16 produced no output for 180 s and no session. | `timeout` exit 124. | A first-event watchdog is required. |
| H8 | `codex sandbox` contains writes (home write denied) but reads stay open; a `deny_read` requirement in a private Codex home was ignored. | Canary read with and without it. | Codex's sandbox cannot stop read-and-send. |
| H9 | A project `opencode.json` outranks the user profile; a project `.opencode/plugins/*.js` runs code at startup. | Planted config re-allowed outside writes and 409 skills; planted plugin wrote a marker. | Any repository can widen the profile or run code. |
| H10 | Configuration hot-reloads: a worker that writes `opencode.json` mid-round widens its own permissions in the same round. | `event.type=config.updated`, then an outside write succeeded. | Only the OS sandbox contains the model. |
| H11 | A relative `XDG_CONFIG_HOME` breaks plugin loading. | `NpmInstallFailedError … ENOTDIR`. | Absolute paths only. |
| H12 | Under a read-denying profile opencode aborts (`UnexpectedStatus: 500`) when it cannot `realPath` the real `~/.claude` or the workspace's ancestor directories. | Two failed probes, then success with a private `HOME` and literal (listing-only) read access to ancestors. | The lane gives the worker a private home and allows ancestor listings, not contents. |
| H13 | `/usr/bin/git` is an xcrun shim that reads and writes a cache under the shared per-user temp directory, ignoring `TMPDIR`. | `couldn't create cache file …/T/xcrun_db-…` inside the sandbox; the real git from `xcrun --find git` runs clean. | The lane resolves the real git before the round and puts its directory first on the worker's `PATH`; no shared-temp rule. |

| H14 | What the provider offers an anonymous client changes during the day: the model answered anonymous runs in the morning, then failed intermittently with `provider.no-route: Model unavailable`, and by 12:50 was missing from the anonymous roster (11 models) while the signed-in roster (74) still listed it. | Same-minute `opencode models --standalone` with a fresh store versus the signed-in store; the public model endpoint still listed the id. | The lane prints provider errors, checks the roster before every round, and cannot run a model offered only to accounts. |
| H15 | With `webfetch` denied, the model fetched the URL through the `execute` tool (Code Mode). | Status 200 from `execute`. | The lean profile also denies `execute`. |
| H16 | A permission block in the object form (`{"skill": {"*": "deny"}}`) is silently ignored; v2 expects an array of `{action, resource, effect}`. | Object form: `webfetch` and `git push` both ran; array form: `git push` denied. | Tests assert the array shape; only behavior proves a rule. |
| H17 | Seatbelt's `allow default` leaves keychain and clipboard services reachable without touching files. | `pbpaste` read 53 bytes outside, 0 under a `mach-lookup` deny; `security list-keychains` failed under it; opencode unaffected. | The profile denies those services and the self-test checks the keychain. |
| H18 | opencode walks `.claude`, `.agents` and `.opencode` in every ancestor up to `/`, above the repository root, and aborts with `UnexpectedStatus: 500` when a sandbox denies one; unsandboxed it would load their instructions. | `FileSystem.realPath (<home>/dev/.claude)`; the standard install directory `~/.opencode` sits in the home ancestor. | The lane refuses agent configuration or instructions in any strict ancestor; worktrees go outside the home, e.g. under `/tmp`. |
| H19 | Hypothesis: a cold store may also lose a startup race for the model catalog. | Lane rounds failed in about one second with an empty `kv` table; after `opencode models --standalone` filled `models-dev:catalog` one round answered. This overlapped with H14 and the two effects were not separated. | The warm-up is cheap and doubles as the roster check, so the lane keeps it. |
| H20 | Seatbelt's `allow default` leaves same-user IPC open: Unix sockets (ssh-agent, Docker), signals to other processes (including the lane supervisor, which defeats the watchdog), process listing, preferences through `cfprefsd`, and Apple Events. | An independent reviewer's hostile fake worker under the real sandbox connected to a socket, killed the supervisor and read 62 KB of Finder preferences. | The profile denies process info for others, Unix-socket connects except DNS, `cfprefsd` and Apple Events, and every signal except to processes in the same sandbox: `(deny signal (target others))` had no effect on a non-Apple victim, and earlier "denied" results came only from Apple binaries, which macOS protects anyway. A live round still ran shell, bun, tsc and git. |
| H21 | Seatbelt does not mediate `sysctl(KERN_PROCARGS2)`: the initial environment and arguments of any same-user non-Apple process are readable from inside, even with `(deny sysctl-read)`. | A sandboxed child read a planted secret from an unrelated Homebrew Python's environment. | The lane's own processes run with an allowlisted environment; secrets exported in other processes (the user's shell, the coordinator) stay readable. Real isolation needs a separate macOS user or a VM. |

The sandboxed probe with the real model (private home and stores, `env -i`): a write inside the
workspace succeeded; a write outside, a read of a canary outside, and a read of the real home all
failed with "Operation not permitted"; the environment held only the allowlisted variables.

### Capability benchmark (n=1 per arm, base `579a92a`, artifacts in `evidence/`)
Hidden tests were written before the runs and fail on the base commit (negative control); base
gates were green. Both arms ran without the lane's sandbox (it did not exist yet), the opencode
arm on the lean profile.

| Task | DeepSeek V4.1 Flash, no-cost | Codex worker, medium (control) |
|---|---|---|
| T1 bug fix, failing test given | pass, hidden 6/6, 93 s | pass, hidden 6/6, 145 s |
| T2 feature from a spec, own tests | pass, hidden 11/11, 216 s | pass, hidden 11/11, 290 s |
| T3 rename across 4 files | gates green; reordered the renamed export, which lint requires | stopped: lint needs that reorder and the brief said "no reformatting" |
| T4 contradictory oracle | honest stop, correct reasoning, no edits | honest stop, no edits |
| Correction round in the same session | kept context, 27 s | not run |

T3 had no predeclared reading of "no reformatting", so it shows two defensible behaviors, not a
ranking. Both arms reported exit codes truthfully; the opencode arm misnamed one path. The control
ran at medium effort, below the configured bounded-worker effort. The tasks are small and
single-module, and the role also covers search and writing, which were not tested.

## Decision

Ship `tools/opencode-lane` as an **opt-in trial** of the opencode worker for bounded, verifiable
coding tasks. Do not rebind any role yet.

### Alternatives considered
1. **Documentation only.** Cheapest, but nothing would enforce `PWD`, isolation, timeouts or the
   sandbox. Prior-art skills reviewed by their READMEs (delegate-to-opencode, opencode-delegate)
   run with `--auto` on the default profile; none isolates configuration or the filesystem.
2. **Adopt a third-party delegation skill.** Same gaps, plus an unshipped dependency.
3. **Run the model through Codex or Claude Code via a translating proxy.** Reuses Codex lanes,
   but Codex's sandbox leaves reads open (H8), the key would leave opencode, and it adds a moving
   dependency.
4. **Premise challenge: no no-cost worker.** Offers end, and cheap workers cost review time. Kept
   as the default: the trial is opt-in and changes no binding.

Chosen: the lane, as an opt-in trial (strongest rejected alternative: documentation only).

## Design: `opencode-lane`

```
opencode-lane start <lane> <spec-file|-> -m <provider/model> [--allow-read DIR]... [--timeout S] [--first-event-timeout S]
opencode-lane next  <lane> <prompt|->
opencode-lane last  <lane>
opencode-lane id    <lane>
opencode-lane log   <lane>
opencode-lane list
opencode-lane drop  <lane>
```

Threat model: the worker model and the repository content are untrusted (prompt injection,
planted configuration). The coordinator, the lane's own state and the owner's files are
protected. Network access is required for the model and stays open, so whatever the worker can
read can leave the machine; the design therefore limits what it can read.

### Layout
- `$OPENCODE_LANE_DIR` (default `~/.local/state/opencode-lane`, mode 700) holds, per lane, the
  state JSON, round logs, the generated profile and a canary, none of which the worker can read
  or write.
- `<lane>.box/` inside it is the worker's private world: `home`, `config/opencode/opencode.json`,
  `data`, `state`, `cache`, `tmp`. It is the only lane path the worker can read and write.

### Every round
1. **Preconditions** (exit 2 on failure, no model call): macOS (`Darwin`) with
   `/usr/bin/sandbox-exec` and `/usr/bin/security`; workspace still at its recorded physical path,
   still the same Git top level and common directory; no `opencode.json`, `opencode.jsonc` or
   `.opencode/` in the workspace or any ancestor up to `/`, and none of `.claude`, `.agents`,
   `AGENTS.md`, `CLAUDE.md` in any strict ancestor; no other live lane bound to the same
   workspace; the lane directory and the workspace do not contain each other. The home directory
   is the account's (`pwd`), not only `$HOME`.
2. **Profile** (generated each round from recorded paths):
   - reads: deny the account's home (and `$HOME` when it differs), `/Volumes`, `/private/tmp`,
     `/private/var/folders`; allow the workspace, the box, the Git common directory, the opencode
     install root, the real git, every `--allow-read` directory, and directory listings
     (`literal`) of each ancestor of those;
   - writes: deny everything except the workspace, the box and `/dev`;
   - services: deny `mach-lookup` of the keychain and pasteboard services;
   - network and process execution stay allowed.
3. **Self-test** under the same profile: a write in the workspace must succeed; a write into the
   lane state directory, a read of the lane canary, a read of a home canary kept under the
   account's home, and a keychain search-list query must fail. Any other outcome exits 2.
4. **Lean configuration** in the box, an ordered array of deny rules: `skill`, `question`,
   `subagent`, `webfetch`, `websearch`, `execute`, `external_directory`; `read` of `*.env` and
   `*.env.*`; `shell` for destructive git commands (hard reset, clean, push, checkout of paths)
   and recursive forced removal.
5. **Catalog warm-up**: `opencode models --standalone` under the same environment and sandbox,
   with its own 120-second cap; the requested model must be listed, else exit 2.
6. **Run** `sandbox-exec -f <profile> opencode run --standalone --format json -m <model>
   --title <lane>` with the prompt on stdin, `cd` into the workspace, and `env -i` with only
   `PATH`, `LANG`, `TERM=dumb`, `PWD`, `HOME`/`XDG_*`/`TMPDIR` pointing into the box. `PATH` is
   the caller's, with the directory of the real git (`xcrun --find git`, resolved outside the
   sandbox) first. `next` adds `--session <id>`. A python3 (stdlib, 3.10+) supervisor runs it in
   its own process group; no event within `--first-event-timeout` (default 120 s) or a round
   past `--timeout` (default 1800 s) kills the group and exits 124. No automatic retry: an
   interrupted round may have had effects, so the coordinator decides.
7. **After the round**, in this order: exit 5 if the worker created `opencode.json`,
   `opencode.jsonc`, `.opencode/`, `.claude/` or `.agents/` in the workspace; `opencode session
   export --standalone <id>` under the same environment, exit 4 if the model differs; provider
   `error` events printed to stderr (opencode's non-zero code, else 3); exit 3 if there is no
   final text.

A `start` refused before the model runs (steps 1-5) releases the lane name and the workspace
claim, so a retry with another model works without `drop`. A lock left by a killed run is named in
the error together with the directory to remove.

Exit codes: 0, 2 (usage or refused precondition), 3, 4, 5, 124, otherwise opencode's own code.
Lane names `[A-Za-z0-9._-]`, no leading `-` or `.`; one writer per lane. `drop` deletes the lane's
state and box (the worker's sessions and snapshots live in the box, so they go with it).

What this does not do: it does not restrict network destinations, cap disk use inside the
workspace and box, or prove which endpoint served the model; the session-export check detects
routing mistakes and is not tamper-proof, since the worker can write its own store. It does not
hide the environment and arguments of the user's other processes (H21), and a worker process
that starts its own session can outlive the round's process-group kill (it stays sandboxed). The
worker cannot stage or commit (the Git common directory is read-only); the coordinator commits.

## Trial gate before any role binding
Bind the bounded-worker role only after a frozen, stratified set of at least 20 representative
bounded tasks (coding, search, writing), three runs each across different days, paired with the
configured bounded worker, with thresholds declared before the runs: first-pass acceptance,
constraint violations, correction rounds, escalations, wall time and coordinator effort.

## Five years out
What breaks first: the no-cost offer, then the harness surface (v1 to v2 renamed the shell tool
and silently disabled a guard; the binary updated itself during this work), then the model id.
The lane absorbs drift by failing closed: the self-test proves containment before every round,
the roster and model checks run around every round, and the lane binds no model. With hindsight,
the decisive choice is already made: contain the model with the operating system, not with the
model's own permission rules, and route on evidence, not on price.

## Implementation plan
1. Branch `feat/opencode-lane` (worktree `.scratch/wt-opencode-lane`).
2. Tests first, then the tool, built by the Codex worker per the owner's routing rule:
   - `tools/opencode-lane.test`: fakes for `opencode` and `sandbox-exec` on an override path;
     every behavior above, each shown to fail without its implementation (mutation table).
   - `tools/opencode-lane.sandbox.test`: the real `sandbox-exec` with canaries and no model
     call; prints SKIP and exits 0 off macOS. Run by the coordinator (a sandboxed Codex worker
     cannot nest `sandbox-exec`).
3. Docs: `references/opencode-dispatch.md`, SKILL.md paragraph and compatibility, skill README, HOWTO, root README, AGENTS.md, GLOSSARY, CI, CHANGELOG 1.35.0,
   VERSION, badge, `build-site.sh`.
4. Verification: both lane tests, `codex-lane.test`, the Defaults guard and its test,
   `build-site.test`, hook test, ast-grep; one live lane round plus a `next` round on the real
   model in a throwaway worktree; live re-verification of every Defaults id with a fake-id
   negative control.
5. Reviews: `code-review`, the `reviewer` agent, `mneves-verify`; fix confirmed findings.
6. Commit, push, PR, CI green, merge to `main` (authorized by the owner's request), delete the
   branch and worktrees.

## Acceptance criteria
- A1 `opencode-lane.test` passes and each listed safety behavior has a scenario that fails when
  that behavior is removed.
- A2 `opencode-lane.sandbox.test` passes on macOS: workspace write allowed; outside write,
  outside canary read and real-home read denied; ancestor listing allowed.
- A3 A live lane completes `start` and `next` on the real model in a throwaway worktree; the
  session export names the requested model; the worker cannot read a canary outside the
  workspace.
- A4 Every AGENTS.md command gate passes; CI green on the PR; docs agree with the tool.

## Out of scope (proposals for the owner)
- Fix the local dcg OpenCode plugin or wait for dcg #547; until then interactive opencode
  sessions on this host have no destructive-command guard.
- A shell wrapper and `~/bin` link for `opencode-lane`, synced to omarchy.
- Refresh `~/.agents/skills/mneves-fable-orchestrator`, a stale copy rather than a symlink.
- Global routing (`agent-runtime.md`, "Claude orchestrates Codex") after the trial gate.
- `~/.config/opencode/agents/references/*.md` load as primary agents.
- Linux support (bubblewrap or Landlock) with the same self-test.
