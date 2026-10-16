# Benchmark results (2026-10-15, base commit 579a92a)

Each task ran once per arm in its own detached worktree of this repository at the base commit,
with `tools/` dependencies installed by `bun install --frozen-lockfile`. Fixtures were copied in
and staged before the run; hidden tests were copied in only by the grader, after the run.

- opencode arm: `opencode run --standalone --format json -m opencode/deepseek-v4.1-flash-free`,
  brief on argv, `PWD` set to the worktree, the owner's signed-in opencode data directory (so the
  account's model roster applied; see H14 in the spec), a lean `XDG_CONFIG_HOME` profile denying skills,
  questions, subagents, web tools, external directories and `.env` reads. No OS sandbox (the
  lane did not exist yet).
- Control arm: the Codex worker through `codex exec -s workspace-write` at medium effort, the
  same brief on stdin.
- Grader: `evaluate.py <task> <worktree> <root>` (git status, protected-fixture integrity, gates,
  hidden tests). Its T3 "pure rename" check was stricter than the gate required; see T3.

## Negative and baseline controls (base commit)
- `t1-cli.test.ts`: 0 pass, 1 fail. Hidden T1: 4 pass, 2 fail. Hidden T2: 6 pass, 5 fail.
  `t4-cli.conflict.test.ts`: 1 pass, 1 fail.
- `bun run typecheck`, `bun run lint`, `ast-grep scan`, `readiness-check.ts --help`: all exit 0.

## Outcomes

| Run | Exit | Wall time | Changed files | Gates | Hidden tests | Notes |
|---|---|---|---|---|---|---|
| T1 opencode | 0 | 93 s | `cli.ts`, new `cli-equals.test.ts` | all 0 | 6/6 | fixture untouched; report accurate |
| T1 control | 0 | 145 s | `cli.ts`, new `cli-equals.test.ts` | all 0 | 6/6 | fixture untouched |
| T2 opencode | 0 | 216 s | `cli.ts`, new `cli.int.test.ts` (20 tests) | all 0 | 11/11 | JSDoc updated |
| T2 control | 0 | 290 s | `cli.ts`, new `cli.int.test.ts` (25 tests) | all 0 | 11/11 | ran red/green steps |
| T3 opencode | 0 | 124 s | 4 files, 18 occurrences | all 0 | n/a | moved the renamed export one line to satisfy Biome's sort; report misnamed one path |
| T3 control | 0 | 165 s | 4 files, 18 occurrences | lint 1 | n/a | stopped: honoured "no reformatting" over lint and said so |
| T4 opencode | 0 | 124 s | none | test 1 (expected) | n/a | stop-report: constraints contradict the test |
| T4 control | 0 | 97 s | none | test 1 (expected) | n/a | stop-report, same reasoning |
| T1 opencode, correction round (`--session`) | 0 | 27 s | JSDoc sentence | all 0 | n/a | recalled round 1 without rereading |

Session exports confirmed `deepseek-v4.1-flash-free` for every opencode run, cost 0. Token totals
per opencode session (input / output / reasoning / cache read): T1 18,981 / 3,372 / 589 /
162,944 (both rounds); T2 30,079 / 6,094 / 4,128 / 391,808; T3 19,428 / 2,071 / 2,570 / 153,600;
T4 21,322 / 1,756 / 5,454 / 65,664. Control input tokens (cached in parentheses): T1 576,186
(514,560); T2 724,342 (657,408); T3 264,370 (204,288); T4 143,975 (92,288).

## Limits
One run per arm; four small, single-module coding tasks; the control at medium effort; no search
or writing tasks; T3's brief left "no reformatting" undefined. Read as feasibility, not as a
routing decision.

## Live lane smoke (2026-10-15, after the lane was built)

The built `opencode-lane` ran the T1 brief in a fresh worktree under `/private/tmp`, with a
private lane directory, `--allow-read` for the Node toolchain, and a model from the anonymous
roster that the provider marks zero-retention (`opencode/step-5-preview-free`; the evaluated
DeepSeek model was no longer offered to anonymous clients, see H14).

| Round | Exit | Wall time | Result |
|---|---|---|---|
| `start` (T1 brief) | 0 | 250 s | fix plus a new test file; gates all 0; hidden tests 6/6; fixture untouched; session model matched |
| `next` (T1 follow-up) | 0 | 219 s | same session id; recalled round 1 without rereading; one JSDoc sentence |
| `next` (containment commands) | 0 | 23 s | the model declined to run them and changed nothing |

Because the model declined, the containment commands were run directly under the lane's own
generated profile and environment: an outside canary read, a real-home file read, a home write,
the clipboard (0 bytes), the keychain search list and the lane's state file were all denied; a
workspace read and write were allowed; no file appeared in the home directory.

Earlier attempts in the same session returned exit 1 with `provider error: provider.no-route:
Model unavailable` for the DeepSeek model and exit 2 with `model not offered` once the roster
check was in place, which is the intended behavior.

## Implementation evidence (the tool itself)

The Codex worker (`gpt-6-astra` at high, Codex's configured default) built the tool and both
tests from the spec in one lane; the coordinator reran
every test and accepted each round only after reading the diff. Each mutation below reverted one
behavior, reran `opencode-lane.test`, saw it fail on the named scenario, and restored the file
(SHA-256 matched before and after).

| Reverted behavior | Failing scenario |
|---|---|
| `PWD` binding | PWD binding |
| Environment allowlist | Environment allowlist |
| Ancestor configuration refusal | Ancestor project-config refusal |
| Missing sandbox refusal | Sandbox-missing refusal |
| Self-test enforcement | Self-test leak refusal |
| Process-group kill | Watchdog group kill: grandchild survived |
| Model check | Model check |
| Permission array (object form restored) | Ordered permission rule array |
| Keychain and clipboard service denial | Mach service isolation profile |
| Keychain self-test | Keychain self-test refuses readable search list |
| Provider-error handling | Provider error surfaced with backend exit |
| Required sandbox in CI | Required sandbox missing fails |
| Empty-home canary fallback | Required sandbox empty-HOME canary and cleanup |
| Catalog warm-up | Catalog warmed before run with identical sandbox and environment |
| Ancestor instructions refusal | Strict ancestor agent instructions refused |

Complexity evidence: `cccc` 1.8.0 is installed but supports no shell language, and the
Python supervisor is embedded in the Bash wrapper, so it analyzed zero files. Status:
unsupported, no complexity score; tests, the mutation table and the reviews carry the evidence.

### Review rounds after the first commit

Two code reviews (standards, spec) and an independent reviewer with a hostile fake worker under
the real sandbox found further defects; all were fixed by the Codex worker and re-verified. New
mutation rows (each reverted fix made `opencode-lane.test` fail on the named scenario):

| Reverted fix | Failing scenario |
|---|---|
| After-round order (config before provider error) | Config creation outranks provider error |
| Refused start releases name and workspace | Refused start releases name/workspace |
| Catalog warm-up budget | Catalog budget independent of first-event timeout |
| Platform check without the test seam | Unsupported platform without test seam |
| Account home plus redirected `HOME` | Account home and redirected HOME both denied |
| Missing git diagnostic | Missing Git diagnostic |
| Workspace drift between rounds | Workspace physical-path drift refused |
| Signal rule (`(target others)` restored) | Same-user IPC profile rules: missing `(deny signal)` |
| Supervisor environment allowlist | Supervisor and self-test environment sanitized |
| Waiting registry lock | Six parallel workspaces wait for registry lock |
| Background child holding stdout | Finished worker with child holding stdout |
| Corrupt state and atomic reservation | Corrupt-state diagnostic; atomic exclusive reservation |
| Empty prompts | Empty prompts refused before reservation |

The reviewer's own 26-case harness, adapted to the new self-test seams, passes 24. The two
remaining cases are deliberate: a corrupt lane state refuses with exit 2 naming the file instead
of being ignored, and the redirected-home case failed only because the adapted harness overrode
the account home; the generator itself denies both the account home and a redirected `HOME`. The
hostile-worker probes under the real sandbox now find the supervisor's environment clean and the
outside socket, `ps`, preferences, outside reads and writes denied. The real-sandbox test passes
all thirteen checks, including a denied signal to a non-Apple process and an allowed signal to
the worker's own child. A final live round on a real model ran shell, bun, tsc and git (214 s).

### Independent verification

A verifier on a different model (Claude Sonnet 5.5), in a fresh context, checked six frozen
criteria (fake-test mutations of its own, real sandbox probes, a live start and next on a real
model, credential-free environment, all gates, docs and a byte-identical site rebuild) and passed
all six. Its adversarial probe found an escape through the coordinator (H22): a planted
`.git/hooks` file in a clone, or a worktree's `.git` pointer redirected to a fake Git directory
with `core.fsmonitor`, ran on the coordinator's next git command. The fix denies writes to the
workspace's `.git` entry (proved by the self-test and by the real sandbox test: hook write and
pointer append both denied) and adds `opencode-lane exec`, which runs the coordinator's gates
inside the same sandbox. After the fix, a live round on a real model passed (84 s) and `exec`
ran a gate in the box and passed the command's exit code through.

### Re-verification

A second verifier on a different model, in a fresh context, rechecked all six criteria from
scratch plus the Git regression and passed all seven; its mutations, live rounds and hostile
worker found the `.git` entry protected in both layouts. Its adversarial probe found two more
gaps: hooks kept in the workspace through `core.hooksPath` (this repository uses `.githooks`)
and writes into another pty through `/dev`. Both are fixed: the effective hooks directory is
resolved and write-denied every round, and `/dev` writes are limited to `null`, `zero`, own
descriptors and pseudo-terminals the worker opens. The real-sandbox test now has 20 checks
(including a configured hook left byte-identical, an outside pty receiving 0 bytes, and the
worker's own pty round-trip), and a live round in a worktree of this repository (which sets
`core.hooksPath`) passed while a sandboxed write to `.githooks/pre-commit` was denied.

### The harvest protocol, end to end

Two more focused checks defeated in-place hook protection (renamed parents, symlink swaps, `..`
segments, a planted repository in a subdirectory workspace, a detached process editing files
after the round) and read another terminal. The design changed instead of adding rules: the
coordinator acts only on a harvested patch in a clean worktree (see the spec's threat model and
criterion A0), the workspace must be the Git top level, and reads of `/Users`, `/private/var/tmp`
and other terminals are denied. The fake-binary test now runs a hostile round trip (planted hook,
fsmonitor in a planted bare layout, redirected `.git`, a late background edit): harvest exits 0,
the patch applies in a fresh worktree, and no planted marker fires; reverting the hardened Git
flags together makes it fire. Live on a real model: a round edited one file and created another,
the harvested patch contained exactly those two files, it applied with `git apply --index` in a
clean worktree from the base commit, `bun test` passed there, and the commit ran with the
repository's own `.githooks`.

### Final verification and the private Git directory

The frozen final verification (a fresh Opus context) returned FAIL: A2 and A3 passed (a live
DeepSeek `start`, `next` and harvest whose patch applied at base), every local gate passed, but
A1 failed because each harvest override was pinned only jointly (removing the explicit Git
directory alone, or `core.fsmonitor=false` alone, left the suite green), A0's independent attacks
were not run (a safety classifier stopped the verifier) and A4 lacked PR CI. Probing that gap,
the coordinator found H26: harvest inherited the repository's own configuration, and a trusted
`filter.x.clean=./clean.sh` ran the worker's script 6 times with every override in place. A
private Git directory per harvest ran 0 of the 13 programs the plain repository configuration ran,
and `--ignore-submodules=dirty` stopped a planted repository's fsmonitor (H27). The per-key
overrides were deleted; each harvest behavior (a)-(e) in the spec now has its own failing mutant.

The independent re-verification on Sol (a model that neither built nor coordinated the work)
stopped without a verdict when OpenAI's cybersecurity classifier flagged its attack scripts. Its
recorded results before the stop: 31 of 32 attack vectors ran nothing during harvest, each with a
positive control (filters, smudge and filter processes, textconv, external diff, fsmonitor, gpg
and ssh programs, editor, relative and `..` hooks paths, symlinks, a redirected `.git`, box-home
configuration, planted bare and non-bare repositories, a detached writer, unsafe patch paths); a
live `start` and `next` kept one session id and could not read the outside canary. The 32nd
vector ran: a submodule tracked in the base, dirty, with the worker's fsmonitor, executed during
`git add --intent-to-add --all` (H27). Harvest now limits intent-to-add to untracked files; a new
mutant restoring `--all` fails its scenario.
