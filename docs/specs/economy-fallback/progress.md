# Economy seat on GLM, DeepSeek as the final fallback (1.52.1)

Branch `feat/economy-glm-deepseek-final`, worktree `.scratch/wt-economy-glm`, base `origin/main`
633a2b3 (`v1.52.0`). Owner request, 2026-11-20: "usar deepseek somente em ultimo caso, como
fallback final; antes use opencode-go/GLM-5.3-Flash; ... adapte todos os meus arquivos globais
agents.md/claude.md e skills; deploy to prod when done", then "yes to all ... deploy when done".

## Task analysis

1. Playback: the pi seat (the orchestrator's economy executor) moves from
   `opencode-go/deepseek-v4.1-flash` to `opencode-go/glm-5.3-flash`. DeepSeek stays only as the
   last link of the chain, used when the GLM model itself cannot run. Every place an agent reads
   that routing changes with it: the global contract's references (one `~/.claude/AGENTS.md`,
   symlinked into Claude, Codex, pi, opencode, omp and Gemini) and the orchestrator skill, which
   ships from this repository. Then release this repository and propagate to the store and hosts.
2. Deeper version: treat the routing text as a spec with executable checks, not prose. Start
   from the provider's own catalog and a real dispatch, not the id as typed (the owner wrote
   `GLM-5.3-Flash`; `pi --list-models` lists `glm-5.3-flash`). Prove it with the frozen routing
   eval run live on both consumers (a changed O13 and a new O19 that fail on the 1.52.0 text),
   the derived-vocabulary Defaults guard, a fresh Claude and Codex session reading the edited
   global references, and store/host parity after release.
3. Red team (six months on, it failed because):
   - Shared allowance. OpenCode Go bills every model from one allowance ("The paid models you
     use on Go share one allowance", opencode.ai/docs/go), so an exhausted allowance stops GLM
     and DeepSeek together. Trigger: quota out. Cost: a wasted fallback dispatch and a misleading
     "fallback ran" report. Falsified early by reading the provider docs (done: confirmed). The
     text says the fallback is for a model-specific failure and that an exhausted shared
     allowance is reported blocked.
   - GLM cannot act as an executor (no tool use, wrong provider). Trigger: first real ticket.
     Cost: the seat silently fails. Experiment (done): `pi -p --mode json --model
     opencode-go/glm-5.3-flash` fixed a planted bug in a scratch file; every event names provider
     `opencode-go`, model `glm-5.3-flash`. DeepSeek answered the same way.
   - The eval cannot tell the new text from the old. Trigger: O19 expects DeepSeek, which the
     1.52.0 text already names for the pi seat, so a careless scenario passes on the baseline and
     proves nothing. Cost: an unearned green gate. Experiment: the `--baseline` run on 633a2b3,
     where O13 and O19 must fail on every sample.
   Simpler route: editing only the ids would leave O13's anchor stale (CI fails) and no check of
   the new order, so no.
4. Verdict: ship; the provider-doc and dispatch experiments ran first, the baseline control runs
   with the gate.

Template conflicts left for the owner (the run template and the standing contract disagree; not
edited, because each changes run cost or a recorded owner rule):
- CI: the template waits for CI on main; the 2026-11-11 standing waiver says never wait.
- `mneves-verify`: the template runs it on every task; "Release and delivery" narrowed it to
  risky work on 2026-11-11.
- Feature interview: the template continues after its own analysis; "Feature workflow" stops for
  the owner's confirmation.
- Pi's status: the template makes pi a fallback after Codex; "Model routing" keeps it a regular
  seat (2026-11-10). This change keeps the regular seat and moves only its model.
- Gemini coding fallback: the template goes from Codex straight to pi; the 2026-11-19 rule puts
  the sandboxed Gemini seat in between. Kept.

## Plan

| # | Task | Acceptance check |
|---|---|---|
| T1 | Orchestrator: economy executor row to GLM, new economy fallback row (DeepSeek), roles table, economy prose, README row | `tools/scripts/check-defaults-block.sh` and `agentskills validate skills/mneves-fable-orchestrator` pass |
| T2 | Routing eval: O13 to GLM (changed), new O19 (changed), O8/O14/O17 unmarked, anchors, revision 12 | `routing-eval.py check` and `routing-eval.test.py` pass |
| T3 | Release files: VERSION, badge, CHANGELOG, HOWTO/site, MEMORY.md, ledger fold for the 1.52.0 binding run | `build-site.test`, `check-readiness-catalog.py`, `check-defaults-block.sh` pass |
| T4 | Global references: `engineering-workflows.md`, `agent-runtime.md` | fresh `claude -p` and `codex exec` sessions name GLM for the pi seat and DeepSeek only as the final fallback |
| T5 | Live routing eval, candidate and `--baseline 633a2b3` | both `threshold_met: true` |
| T6 | Full local suite (Commands in AGENTS.md) | every command exits 0 |
| T7 | Verification: prune-tests on the touched tests, `mneves-verify` (fresh context, up to 3 passes) | clean verdict or findings listed |
| T8 | Security and readiness gates on the exact candidate, independent acceptance, `deploy.sh`, tag `v1.52.1` | tag message records PASS/WAIVED, served bytes match |
| T9 | Propagation: commit `~/.claude`, `sync-agent-commands`, `skillctl sync --apply`, `sync-agent-skills`, `probe-model-routing.py` | no FAIL lines; store = repo |
| T10 | Cleanup: worktree, local branch, scratch this run created | `git worktree list`, `scratch report --entries` |

## Progress

- 2026-11-20: T0 experiments done (GLM coding smoke, DeepSeek liveness, provider docs). Worktree
  created from `origin/main`.
