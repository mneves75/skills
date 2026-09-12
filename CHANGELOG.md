# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.18.0] - 2026-09-12

### Changed

- **`mneves-fable-orchestrator`**: new Defaults. The main session is Fable 5.1 in a Claude harness
  or GPT-6 Astra at `xhigh` in a Codex harness; the frontend subagent is Opus 5.1; the heavy
  executor moves from GPT-6 Astra `high` to GPT-5.6 Sol `xhigh` and no longer owns review. A new
  reviewer role (GPT-6 Astra `xhigh`) owns independent review, through `autoreview` when installed.
- **`mneves-fable-orchestrator`**: a Codex main session no longer implements substantial work
  directly; like the Claude side, it delegates independent work to a heavy-executor worker whose
  model is set in the spawned agent's configuration.
- **`autoreview`**: the Codex default reasoning rises from `medium` to `xhigh` on GPT-6 Astra. The
  access-only GPT-5.6 Sol `xhigh` retry is unchanged. Reviews are slower and cost more; pass
  `--thinking medium` for the previous behavior.

## [1.17.0] - 2026-09-10

Every skill reviewed against Anthropic's Agent Skills authoring guidance and this repository's own
invariants. Activated `SKILL.md` bodies drop from 7,889 to 6,045 words while the collection gains
13 on-demand reference files, so a skill that is triggered now loads materially less and reaches
the rest only when a task needs it.

### Changed

- **`autoreview`**: body 1,702 → 635 words. The Codex config-projection contract, status-sidecar
  schema and exit codes, Git target edge cases, runtime boundaries, and engine override mechanics
  moved to five reference files, each linked one level deep from `SKILL.md`. Every flag and
  operational fact is preserved.
- **`mneves-teach-back-srs`**: body 1,197 → 775 words. Review, Stats and Export modes and the
  card-quality rules moved to references; the teach-back loop, decision tree and database setup
  stay inline. SM-2 thresholds are no longer restated in prose — the `stats` command owns them.
- **`mneves-expert-review`**: twelve steps collapse to six. The pre-mortem, five-year test and
  contrarian steelman were the same move in three costumes and are now one combined attack step;
  the duplicated second quality audit is gone; the "six or more alternatives" quota becomes
  "until they stop differing in kind". `references/checklists.md` is deleted — it restated the
  body rather than deferring anything.
- **`mneves-eli5`**, **`mneves-agent-readiness`**, **`imagegen-frontend-mobile`**: worked example,
  context-file template, and safety boilerplate the base agent already applies moved out or
  removed. Two epigraphs and an unfalsifiable "updated within 30 days" freshness rule deleted.
- **`mneves-fable-orchestrator`**: model identifiers no longer appear in six places across three
  files. Prose describes capability roles and a single Defaults block carries the ids, so a model
  release is a one-line edit. `codex-auto` is now declared a personal launcher that this repository
  does not ship, with the plain `codex exec` equivalent given.
- **`mneves-verify`**: the independence rule states the principle instead of naming vendors, and
  the evidence table leads with the required capability rather than with tools that are not
  shipped here.
- **`mneves-superaudit`**: description reduced from 430 to 124 characters — it was loading a
  trigger-phrase inventory into every session, at roughly three times any sibling.
- Pinned CLI patch versions removed from `autoreview`'s prerequisites; the helper reports its own
  current defaults.

### Fixed

- `mneves-expert-review` referenced a private documentation layout (`DOCS/GUIDELINES-REF`,
  `DOCS/REF_DOCS`) that exists only on the author's machine, and `mneves-teach-back-srs`'s README
  hardcoded one harness's install path. Both violated the repository's own "must work for a
  stranger's clone" invariant.
- `mneves-agent-readiness` described the readiness assessor as "bundled with this skill"; it lives
  at the repository root and is absent from a single-skill install. The skill now says so and
  points at the manual pass as the fallback.
- `AGENTS.md` omitted `mneves-superaudit` from its project tree, and `HOWTO.md` still said "eight
  skills" with the new one missing from its quick-reference table.
- `AGENTS.md` required Python 3.11+ for shipped helpers while `srs_db.py` documents and needs only
  3.10; the invariant was wrong, not the skill.

### Added

- `AGENTS.md` invariants for the rules this pass had to apply by hand: model identifiers confined
  to one block per skill, no skill requiring anything it does not ship, `SKILL.md` bodies under
  500 lines with references one level deep, and the distinction between a tool's documented
  default path and the author's private machine layout.

## [1.16.0] - 2026-09-10

### Added

- **`mneves-superaudit`**: a bounded, delegated audit-and-ship pass over a repository. Four selectable items — slop removal, performance wins, agent DX and verification loops, PR/issue triage — each ending on a falsifiable condition rather than a judgement that the work feels complete. Five phases with typed stop gates: findings before any edit, the diff before any commit, and an explicit release instruction naming a destination before anything leaves the machine.
- Delegation guidance sized to the documented multi-agent failure modes: a per-task-class worker budget, briefs that name the other workers' paths as *do not touch*, a distilled return contract that passes file references instead of transcripts, and the cases where delegating costs more than it saves. Discovery parallelizes because it is read-only; implementation partitions by path or serializes, since the slop and performance items touch the same files.
- Measurement rules that can return "inconclusive": a performance result inside noise, or one depending on the change's own instrumentation, is never reported as a win; negative assertions and security gates require a positive control placed where the gate actually looks, and a policy claim counts only against the served artifact.
- A per-phase progress file (`agent_planning/superaudit-<date>.md`) so a long run survives compaction, and an A/B protocol for testing changes to the skill itself against a fixed repository and commit.

### Changed

- Catalog and HOWTO now cover the new skill, including the item-selection syntax that keeps unused phases out of context.

## [1.15.0] - 2026-09-07

### Added

- **`autoreview`**: portable MIT-licensed adaptation of OpenClaw's structured review helper, maintained in this collection with its source revision, license, full tests, and no dependency on an upstream checkout. Available as the `v1.15.0-beta1` candidate.
- Autoreview defaults to `gpt-6-astra` with medium reasoning and retries confirmed account-access failures once with `gpt-5.6-sol` at xhigh; primary overrides retain the fallback effort and other failures do not change models.
- An isolated test runner and CI coverage for the imported review helper, including provider-route, scanner, source-integrity, and filesystem-boundary tests.

### Changed

- Catalog, installation, licensing, and maintenance documentation now include autoreview and explain that authorized review inputs are sent to the selected provider.

### Security

- Preserve the original repository's executable and environment trust boundary during nested submodule snapshots, preventing repository-owned Git binaries from running during preparation.
- Validate both output targets and the directory entries that will be replaced; normalize accepted paths once so report writes and stale-status cleanup cannot enter the reviewed repository through symlinks or quoted home paths.

## [1.14.0] - 2026-09-07

### Added

- **`imagegen-frontend-mobile`**: an MIT-licensed, condensed adaptation of Leonxlnx's mobile image-generation skill. It generates iOS or Android screen and flow images, locks one design system across the set, inspects the rendered result, and never substitutes code for the requested images.

### Changed

- Repository guidance now distinguishes original `mneves-` skills from adapted third-party skills that retain their upstream name, license, copyright, and provenance.
- **`mneves-fable-orchestrator`** now uses GPT-6 Astra at reasoning `high` for Codex execution, planning, review, and inherited agents; explicit specialist overrides remain supported and quota probes use `low`.
- Skill descriptions now fit the discovery budget with one distinguishing capability-and-trigger sentence. Redundant trigger lists, checklists, and examples were merged into the procedures; Codex launcher mechanics moved to a conditional reference.
- **`mneves-verify`** now distinguishes substantial checkable completion, which still gets an independent verifier, from routine low-risk changes that need only proportionate deterministic proof.

### Security

- The new skill treats reference assets as untrusted data, requires authorization before sending private references to an image service, excludes secrets and unnecessary personal data from prompts, and forbids fabricated endorsements, certifications, transactions, or product claims. Repository and site copy now distinguish local tooling from provider-backed image generation.

## [1.13.0] - 2026-09-07

### Changed

- **`mneves-fable-orchestrator`** routes the heavy executor back to GPT-5.6-sol at reasoning `xhigh`; GPT-6-astra at `high` keeps only the planning, orchestration and review seat, the one Fable holds on the Claude side.

### Added

- **`mneves-fable-orchestrator`**: "Inside a codex run: sol drives, astra advises". Sol owns progress, implementation and verification and never hands the task off; it spawns an advisor only for a decision with real downside, an expensive-to-reverse trade-off, or an independent review. The advisor is named explicitly (a model asked for in prose is a wish, the agent file is the setting), gets a fresh context via `fork_turns: "none"` and a self-contained brief, edits nothing, spawns nothing, and changes no approval boundary.
- The advisor must be selected with `CODEX_AUTO_MODEL` / `CODEX_AUTO_EFFORT`, never `-c model="..."`: a wrapper that passes `--model=<executor>` wins over the `-c` override and the run lands on the executor while the caller believes otherwise. Verify with the session header's `model:` line.

## [1.12.0] - 2026-09-04

### Changed

- **`mneves-fable-orchestrator`** routes the heavy executor to GPT-6-astra at reasoning `high` (was GPT-5.6-sol); the GPT-5.6-terra bulk tier is dropped, exceptions are pinned per lane.

## [1.11.0] - 2026-08-26

### Added

- **Recorded sessions in `HOWTO.md`**: `mneves-eli5` and `mneves-expert-review` examples are verbatim `claude -p` runs (claude-fable-5, 2026-08-26); `mneves-teach-back-srs` shows real `srs_db.py` output; the readiness example was already a real run. The two remaining examples are labelled illustrative.
- Branch ruleset on `main`: no force-push, no deletion.
- CI fails when `site/howto.html` or the landing page's changelog rows are stale (`tools/scripts/build-site.sh` regenerates both).

### Changed

- **`mneves-teach-back-srs`** no longer hardcodes `~/.claude/skills/...`; commands reference `scripts/srs_db.py` relative to the skill folder, as the Agent Skills spec recommends, so any install location works.
- **`mneves-fable-orchestrator`** keeps model ids in one Models table (role, id, effort, where it is set); the body refers to roles.
- Landing-page changelog rows are generated from `CHANGELOG.md` by `tools/scripts/changelog-rows.py` instead of copied by hand. `build-howto.sh` renamed to `build-site.sh`.

## [1.10.0] - 2026-08-26

### Changed

- **`mneves-fable-orchestrator`** adopts five rules from steipete's `codex-first` (2026-08-20 revision): every hard prohibition in a spec carries an escape hatch (the minification incident), check for a live worker with `pgrep -fl "codex exec"` before editing, verify beyond the diff (merged surface, uncommissioned commit messages, guard files, test-helper edits), a diagnosis list for executors that die instantly or go quiet (with lane resume), and never passing credentials via `-c` (use a `CODEX_HOME` overlay). Read-heavy exploration may go to Codex; a new work order always gets a fresh thread. Not adopted: routing git rebase/merge/landing to Codex.
- Every `SKILL.md` declares `license: Apache-2.0` (Agent Skills spec optional field); all six validate with `skills-ref`.
- Prose pass over skills and repo docs: list-item em dashes replaced with colons, sentence-level ones with punctuation, "production-ready"/"genuinely" dropped. The verdict format in `mneves-verify` is unchanged (it is a contract).

## [1.9.0] - 2026-08-26

### Added

- **Landing page** at https://mneves75.github.io/skills/ (`site/index.html`): install commands with copy buttons, one card per skill linking into the how-to, how it works, the readiness tool with the sample score, start-here links, recent changelog. Self-contained HTML, light/dark, keyboard-operable.

### Changed

- Pages source directory renamed `examples/` → `site/` (landing, how-to, sample report); the workflow uploads it as-is instead of generating an index from a heredoc.
- `tools/scripts/build-howto.sh` adds heading ids so the landing page can link to each skill's section.
- Dependabot PRs #1–#5 closed and their branches deleted; `main` is the only branch. The four green action bumps can be re-requested with `@dependabot recreate`.

## [1.8.2] - 2026-08-26

### Added

- **`HOWTO.md`**: what each of the six skills does, its trigger phrases, prerequisites, a worked example and tips; rendered to `examples/howto.html` on GitHub Pages by `tools/scripts/build-howto.sh` (bun + marked, nothing added to the repo's dependencies). Linked from the README and the Pages index.

### Fixed

- `mneves-agent-readiness` SKILL.md told the agent to pass a project path to `readiness-check.ts`; the tool assesses the current directory and ignores positional arguments. Usage now says `cd` first. Dropped the stale "v1.0.0" label.

## [1.8.1] - 2026-08-26

### Changed

- **Example report regenerated** with the fixed tool against FastAPI `9a8a13f` (2026-08-25): L3, 61.7% (`--skip-tests --skip-build`). The previous numbers disagreed across README (L4 / 65.4%), the HTML report (56.3%) and `scoring.ts` comments (53%); all now show the same run with its provenance.
- **Factory.ai attribution made factual.** Removed the speculative comparison table (competitor pricing, language list, "limited monorepo") and marketing prose ("pioneered", "set the standard"); README, NOTICE and the skill README now state only that the pillar/level structure follows Factory.ai's Agent Readiness assessment and that this is an independent, local-only implementation whose scores are not comparable.

## [1.8.0] - 2026-08-26

### Added

- **`npx skills` install path** — `npx skills@latest add mneves75/skills` is the documented primary install (all six skills verified discoverable with `--list`); manual `git clone` table kept per tool.
- **CI** (`.github/workflows/ci.yml`) — skill-layout check (folder == frontmatter `name`, description present, no root `SKILL.md`), `bash -n`, `py_compile`, ast-grep scan, pre-commit hook e2e test, `tools/` typecheck + Biome lint. `contents: read` only.
- `SECURITY.md` (private vulnerability reporting, response windows, scope) and `.github/dependabot.yml` (GitHub Actions + `tools/` npm, weekly).

### Changed

- **`mneves-expert-review`** no longer points at a maintainer-local `~/dev/GUIDELINES-REF`; it references the project's own guidelines when present, so the skill works from any clone.
- GitHub Actions pinned to commit SHAs in both workflows.
- `AGENTS.md` is the single agent-instructions file (`CLAUDE.md` imports it); tree refreshed to list all six skills and the CI/security files.
- `tools/package.json` declares `private`, `license`, `repository`, `engines`; README's readiness-check usage now matches how the tool actually runs (assesses cwd via `bun --bun …/tools/readiness-check.ts`).
- `.gitignore` covers `.codemap/` and `__pycache__/`.

### Fixed

- `readiness-check` piped output (`| jq`, `> file` via shell) was cut at 64 KiB: `console.log` followed by `process.exit` dropped unflushed data. Output is now written with an awaited `process.stdout.write` callback (`Bun.write(Bun.stdout)` re-emits the buffer after a partial pipe write on Bun 1.4.0); verified with a 100 KB JSON report through a real pipe.
- `tools/lib/checks/shared.ts` used `fs` without importing it; the "extensive `docs/`" documentation check silently never passed (error swallowed by a `catch`). Typecheck now passes and CI enforces it.
- `.githooks/pre-commit` passes staged paths after `--`, so a file named `-x.ts` is not read as an ast-grep option.
- Biome lint errors (import order, unused imports, `let` → `const`) auto-fixed; `bun run lint` is green (warnings only).

### Removed

- `docs/EXAMPLES-EXEC-SPEC.md` (1.0.0-era spec for assets that never existed).

## [1.7.0] - 2026-08-26

### Added

- **`mneves-expert-review`** (`skills/mneves-expert-review/`) — expert-panel review and optimization pass run on a draft before it is finalized: clarify the real objective, rebuild from first principles, research only when it changes the answer (web + `~/dev/GUIDELINES-REF`, disconfirmation first, claims labelled fact/consensus/disputed/inference/judgment), attack the draft as a seven-role panel, generate six genuinely different alternatives (incl. one that challenges the premise) and compare them on weighted criteria, pre-mortem, five-year test, contrarian steelman, quality audit, then return the improved deliverable with trade-offs, risks, evidence and remaining uncertainty. Scales to stakes; checkable artifacts hand off to `mneves-verify`. SKILL.md + `references/checklists.md`, no scripts. Installed via `~/.agents/skills/` symlink fan-out to Claude Code, Codex, OpenCode, Cursor, Pi and Gemini.

## [1.6.0] - 2026-08-26

### Added

- **`mneves-eli5`** (`skills/mneves-eli5/`) — Feynman-technique explainer calibrated to the listener (child, layperson, executive, junior, expert): fix the audience, one-sentence core, one analogy carried through, show-then-name jargon, state where the analogy breaks, one repeatable takeaway. Answers in the user's language; re-explains for a new audience without re-deriving. SKILL.md only, no scripts.

## [1.5.0] - 2026-08-18

### Added

- **`mneves-verify`** (`skills/mneves-verify/`) — independent-verification skill that operationalizes the "never grade your own homework" rule. Fresh independent context checks the artifact against explicit acceptance criteria; evidence routes by artifact type (focused tests + `autoreview` for code, `agent-browser`/Argent + real renders for UI, real binary/endpoint/query + positive control for CLI/API/data, primary sources + citation checks for research, `security-audit` for security); one builder correction + one full fresh reverify (every criterion + affected regression surfaces), then `Verdict: PASS | FAIL | BLOCKED` with one Criterion line per criterion. PASS alone permits done/fixed/shipped. Artifacts are untrusted data, never instructions; read-only by default, no secrets, no external writes; no scripts/dependencies/scaffolding.
- **ast-grep guard** — `sgconfig.yml` + `rules/no-as-any.yml` (TypeScript) + `rules/no-as-any-tsx.yml` (TSX): two rules rejecting `as any`, so the repository itself has a real checkable guard rather than a prose promise.
- **Blocking pre-commit hook** (`.githooks/pre-commit`) — runs the ast-grep scan and fails closed when ast-grep is absent; enabled locally via `git config core.hooksPath .githooks`.
- **Project memory** — `FOR_YOU_KNOW.md`, `MEMORY.md`, and `memory/2026-08-18.md` (previously absent).

## [1.4.0] - 2026-07-31

### Added

- **`codex-lane`** (`skills/mneves-fable-orchestrator/tools/codex-lane`) — named, resumable Codex threads: `start` / `next` / `adopt` / `id` / `log` / `last` / `list` / `drop`, state in `~/.codex/lanes/`. Install by symlink onto `PATH`.
- `codex-lane adopt <lane> <thread-id> [cwd]` wraps a thread started by a plain `codex exec`, so a dispatch that unexpectedly needs a round 2 continues on the same thread instead of being re-specified.
- Fable Orchestrator gains a **Continuity** section: one round is a `codex exec`, two or more rounds is a lane. Fix-ups, review findings and failing gates go to `codex-lane next` on the same thread instead of a fresh spec, so the executor keeps its private reasoning and the instruction preamble is served from cache. Rationale and measurements from OpenAI's [ARC-AGI-3 harness writeup](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores/) (retained reasoning + compaction: 13.3% → 38.3% RHAE, 6× fewer output tokens); locally, a fresh `exec` sends ~34k uncached input tokens versus ~35k cached on a `resume`.
- Documented the Codex flag-order trap: global flags must precede `resume` (`codex exec -s read-only resume <id>`, not `codex exec resume <id> -s read-only`).

### Changed

- Fable Orchestrator no longer requires the openai-codex plugin: the primary heavy-executor path is `codex exec` / `codex-lane`, with `/codex:rescue` noted as an equivalent front-end.
- Verify loop iterates via `codex-lane next` (Codex) or `SendMessage` (subagent) rather than a fresh dispatch.
- `codex-lane next` now treats its prompt argument as always-literal text; automatic detection of a readable file path is removed. File or untrusted content must be passed explicitly via stdin redirection — `codex-lane next <lane> - < file` — so a pathname string can never be silently replaced by the file's contents.

### Security

- `codex-lane` validates lane names against `[A-Za-z0-9._-]` and rejects leading `-`. A name like `../foo` previously escaped the lane directory, so `drop` could delete a `.json` file elsewhere on disk.
- `require_lane` is called directly instead of inside a command substitution: `die` in a `$( )` subshell only killed the subshell, so `id` / `log` / `last` / `drop` silently continued with an empty path when the lane did not exist.
- Lane directory is created mode `700` and the script runs `umask 077`, because event logs contain the full model transcript for the job.
- `codex-lane next` now `cd`s to the lane's recorded `cwd` before resuming. It previously ran wherever it was invoked, so a resume issued from another repository (or from `$HOME`) let the executor inspect, test, or modify the wrong workspace.
- Lane names are reserved atomically (`set -o noclobber`) before the Codex run starts, and the placeholder is released if no thread id is obtained. The previous `[ -f ]` check left two concurrent `start`s racing for the whole duration of a run.
- `codex` and `python3` are verified present before dispatch, not after: on a host without `python3` the executor could modify the workspace and only then lose the thread id that makes the work resumable.
- `codex-lane next` replays the execution args the lane was started with. `codex exec resume` rebuilds sandbox/model/profile from the current invocation rather than from the thread, so a lane started `-s workspace-write` previously resumed under the machine default — often read-only, i.e. unable to perform the fix-up it was resumed for. `next` now rejects trailing arguments and always replays the stored set — the per-turn `-- <args>` override is gone, so the lane's execution policy cannot drift one turn at a time.
- `-C` / `--cd` in the pass-through args is rejected. It would have moved Codex to another tree while the lane recorded the original one, sending every later `next` at the wrong repository.
- `start` and `adopt` record the workspace as a physical path (`pwd -P`). The logical `$PWD` kept a symlinked spelling, so a lane started or adopted through a symlink could have made `next` resolve to a different real tree than the one the spec targeted.
- Resumes of the same lane are serialized with an atomic lock, and artifact names carry the PID: two concurrent `next` calls could otherwise interleave turns on one thread and truncate each other's logs.
- Prompts reach Codex on stdin (`resume <id> -`) instead of argv. An *inline* prompt still travels in the wrapper's own argv, so `codex-lane next <lane> -` reads the prompt from the wrapper's stdin — a 2 MB build log passes as a file path or on stdin, and only an inline megabyte-scale string can still hit `E2BIG`.
- `codex-lane next` and `drop` acquire the lane lock *before* reading state. Reading first left a window where a concurrent `drop` reported success and the in-flight resume then recreated the lane, silently resurrecting a thread the user had dropped.
- Lane state is written to a temporary file and `os.replace`d into position. The previous truncate-then-serialize could destroy the only copy of the thread id if the write failed partway, leaving the lane unresumable.
- Attached forms of the output flag (`-o/tmp/x`, `-o=/tmp/x`) are rejected, not just the bare `-o`, since either would redirect the final message away from the file `codex-lane last` reads.
- A prompt file whose name looks like an option (`-n`, `--help`) is read via redirection instead of `cat "$1"`, which would otherwise hand the model help text instead of the prompt.
- Every attached form of the cwd flag is rejected (`-C x`, `-Cx`, `-C=x`, `--cd=x`), not just the bare token.
- Wrapper-owned and lane-incompatible flags are rejected in the pass-through args: `--json` and `--output-last-message`/`-o` would redirect the lane's own artifacts, and `--ephemeral` would create a thread that can never be resumed.
- `drop` and `adopt` take the same per-lane lock as `start`/`next`, so a drop can no longer race a running turn that then republishes the state file.
- An existing `CODEX_LANE_DIR` is no longer `chmod 700`-ed; only a directory the wrapper creates gets the restrictive mode.
- An argument before the literal `--` is now an error instead of being dropped. `codex-lane start l spec -s read-only` previously succeeded while silently running under the machine default — possibly wider permissions than the caller had just asked for.
- Lane names may not start with `.`: such a state file was invisible to `list`'s glob, so the lane worked everywhere except where you would look for it.
- `adopt` resolves a relative workspace with `CDPATH=` and `cd >/dev/null`. Under a configured `CDPATH`, bash's `cd` echoes the resolved directory, which recorded two newline-separated paths and made every later `next` die on a cwd that "is not a directory".
- `codex-lane --help` exits 0; only a malformed invocation exits 2.
- Documented examples default to `-s workspace-write` rather than `--dangerously-bypass-approvals-and-sandbox`.
- Thread ids beginning with `-` are rejected in `adopt` (and defensively on the stored/observed id in `start`/`next`) before they are persisted or passed to `codex exec resume`, where codex would parse them as flags.

### Fixed

- README version badge was pinned at 1.2.0 while `VERSION` read 1.3.0.
- `codex-lane --help` printed shell code past the end of the header comment; help is now derived from the leading comment block.
- `id`, `log`, `last` and `drop` require exactly one argument and `list` requires zero; a malformed call now exits 2 before acting (previously `drop <lane> <extra>` ignored the extra arg and deleted the lane).

## [1.3.0] - 2026-07-24

### Changed

- **BREAKING** — all skills now carry the `mneves-` prefix: `agent-readiness` → `mneves-agent-readiness`, `fable-orchestrator` → `mneves-fable-orchestrator`, `teach-back-srs` → `mneves-teach-back-srs`. Directory name and frontmatter `name:` match. Re-link installs: `ln -s <repo>/skills/mneves-<skill> ~/.claude/skills/mneves-<skill>`.
- Fable Orchestrator routes heavy implementation to GPT-5.6-sol at reasoning `high` (was GPT-5.5 at `xhigh`).

## [1.2.0] - 2026-07-08

### Added

- **Fable Orchestrator Skill** - Model-routing policy for multi-agent Claude Code sessions
  - Fable (main session) as advisor: repo understanding, architecture decisions, task decomposition, spec writing, final review
  - Opus subagents as frontend executors (components, styling, layout)
  - Codex (GPT-5.5 xhigh via `/codex:rescue`) as heavy executor (implementation, debugging, test fixing, multi-file refactors)
  - `supergoal` + `/goal` for long-horizon, multi-phase work
  - Delegation contract (goal, paths, constraints, proof, output shape) and mandatory Fable-side verification of all delegated output
  - Codex invocation patterns adapted from [steipete/agent-scripts — codex-first](https://github.com/steipete/agent-scripts/blob/main/skills/codex-first/SKILL.md)

## [1.1.0] - 2026-02-01

### Added

- **Teach-Back SRS Skill** - Spaced-repetition learning through codebase teach-back sessions
  - Teach-back mode: explain your understanding, Claude cross-references code and probes gaps
  - Socratic follow-ups with specific file:line references for misconception correction
  - SM-2 algorithm (SuperMemo 2) for optimal review scheduling
  - Per-project SQLite database (`.ai-learn/srs.db`, auto-gitignored)
  - Review mode with self-rated recall (quality 0-5)
  - Stats dashboard: mastered, struggling, due, upcoming cards
  - Export to Markdown or Anki-compatible CSV
  - Cross-session continuity via persistent SQLite state
  - Card generation guidelines: one concept per card, why > what, context-anchored
  - Python 3.10+ stdlib only, no external dependencies

## [1.0.0] - 2026-01-22

### Added

- **Agent Readiness Skill** - Evaluate codebase readiness for AI agents
  - 9 technical pillars (Context, Typing, Testing, Build, Lint, CI/CD, Documentation, Observability, Security)
  - 5 maturity levels (L1 Runnable → L5 Autonomous)
  - Multi-language support (TypeScript, JavaScript, Go, Python, Rust, Java)
  - Monorepo application discovery
  - Multiple scoring modes (weighted, strict, average)
  - HTML, JSON, and Markdown output formats

- **Benchmark Reports** - Real assessments of popular open-source projects
  - FastAPI (Python) - L4, 65.4%

- **GitHub Pages** - Live HTML reports at https://mneves75.github.io/skills/

- **Tool Installation** - Support for pi, OpenCode, Claude Code, Cursor, VS Code, Codex, Windsurf, and Aider

### Notes

This project is inspired by [Factory.ai](https://factory.ai)'s Code Readiness framework.

[1.17.0]: https://github.com/mneves75/skills/releases/tag/v1.17.0
[1.16.0]: https://github.com/mneves75/skills/releases/tag/v1.16.0
[1.15.0]: https://github.com/mneves75/skills/releases/tag/v1.15.0-beta1
[1.11.0]: https://github.com/mneves75/skills/releases/tag/v1.11.0
[1.10.0]: https://github.com/mneves75/skills/releases/tag/v1.10.0
[1.9.0]: https://github.com/mneves75/skills/releases/tag/v1.9.0
[1.8.2]: https://github.com/mneves75/skills/releases/tag/v1.8.2
[1.8.1]: https://github.com/mneves75/skills/releases/tag/v1.8.1
[1.8.0]: https://github.com/mneves75/skills/releases/tag/v1.8.0
[1.7.0]: https://github.com/mneves75/skills/releases/tag/v1.7.0
[1.6.0]: https://github.com/mneves75/skills/releases/tag/v1.6.0
[1.5.0]: https://github.com/mneves75/skills/releases/tag/v1.5.0
[1.4.0]: https://github.com/mneves75/skills/releases/tag/v1.4.0
[1.3.0]: https://github.com/mneves75/skills/releases/tag/v1.3.0
[1.2.0]: https://github.com/mneves75/skills/releases/tag/v1.2.0
[1.1.0]: https://github.com/mneves75/skills/releases/tag/v1.1.0
[1.0.0]: https://github.com/mneves75/skills/releases/tag/v1.0.0
