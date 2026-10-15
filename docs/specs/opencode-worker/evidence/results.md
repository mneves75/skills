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
