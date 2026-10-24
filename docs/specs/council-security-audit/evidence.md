# Council and security-audit: findings and dispositions

Companion to [plans/003](../../../plans/003-council-security-audit.md).

This document records what review changed and what a reader can check. It deliberately does not
report who reviewed the work, how many rounds ran, or what verdict a reviewer issued: those are
release-session facts with no artifact in this repository, and an unverifiable claim does not
belong in shipped text. What is here is the durable part — each finding, how it ended, and the
commit that carries the change — plus the commands that reproduce the release checks.

## Findings and dispositions

| Finding | Severity | Where | Disposition | Commit |
|---|---|---|---|---|
| Council described independence as though it were enforced; a session inside the project lets one member read another's reply | high | `skills/council/` | fixed: independence is a protocol obligation, and the session root must sit outside the project and every working directory | `c11aa07` |
| Cursor receives the prompt in its argument vector | medium | `skills/council/SKILL.md` | fixed as disclosure: the exposure is named and private content requires accepting it | `c11aa07` |
| The fallback trigger read as satisfied by one missing primary seat | medium | `skills/mneves-fable-orchestrator/SKILL.md` | fixed: it requires that no authorized primary seat for that role can run, and records each failure | `c11aa07`, `5499adc` |
| Inherited contradiction: a retained `rejected` record had to pass a Phase 5 step that never receives it | medium | `skills/security-audit/references/VALIDATION-AND-REPORTING.md` | fixed: the Phase 3 disproof is retained; 16 of 20 upstream files stay byte-identical | `c11aa07` |
| `claude --restricted` does not stop the reviewed repository's `CLAUDE.md`, skills or hooks loading as instructions | high | `skills/council/SKILL.md` | fixed: `--safe-mode` added, checked against installed help | `5499adc` |
| Codex loads the repository's `AGENTS.md` as instructions | medium | `skills/council/SKILL.md` | fixed: `-C` pins the directory and `-c project_doc_max_bytes=0` stops project-doc loading, checked against `codex-cli 0.164.0` | `5499adc` |
| A round where every member failed still produced a plan labelled as a council | medium | `skills/council/SKILL.md` | fixed: it stops and reports un-counciled, naming the rounds | `5499adc` |
| The adapter table is bare commands while the prose requires a supervisor | medium | `skills/council/SKILL.md` | fixed: the table is a member command run under the step 3.2 supervisor from `CONTEXT_DIR` | `5499adc` |
| Cursor's read-only boundary rests on a start mode, the same bar that excluded Gemini | medium | `skills/council/SKILL.md` | claim narrowed: non-interactive Plan Mode enforcement is stated as not established | `5499adc` |
| One sentence let "do not" govern "confine reads", contradicting the Claude row | medium | `skills/council/SKILL.md` | fixed: the caveat and the per-adapter confinement are separate statements | `7883500` |
| Orchestrator wording read as permission to use one model twice | medium | `skills/mneves-fable-orchestrator/SKILL.md` | fixed: two sessions of one model are self-review; report the gate blocked | `5499adc` |
| F-1: the security policy omitted both new stores and executable surfaces, then overclaimed erasure completeness for copies the member CLIs keep | medium | `SECURITY.md` | fixed: scope, data map and erasure now separate what this project writes from what it cannot enumerate, and say retention was not tested | `860332d`, `ea2169e` |
| The security policy implied source inspection happens inside the sandbox | low | `SECURITY.md` | fixed: source inspection is read-only, only target-controlled execution is sandboxed | `78d2be7` |
| The defaults guard covers only `SKILL.md`, so a model id in a reference file would pass CI | low | `tools/scripts/check-defaults-block.sh` | follow-up, not fixed here: it changes the orchestrator's own guard | — |
| Both validators accept an empty ledger and empty findings, so they cannot prove a run did the work | medium | `skills/security-audit/` | documented upstream gap: forking the pinned validators and their 65 tests was rejected in favour of stating the limitation | `5499adc` |
| `tools/readiness-check.test.ts:50`, the descendant-reaping assertion, failed once | low | `tools/` | disproved as caused by this change: `tools/` is byte-identical to four earlier trees whose runs passed, and a rerun of the same tree passed. No commit changes it | — |

## Checks a reader can re-run

These produce the same result from a clone; they are the release's reproducible evidence.

```sh
for d in skills/*/; do npx -y skills-ref@0.1.5 validate "$d"; done   # 17 default skills
npx -y skills@latest add . --list                                    # discovers both new packages
node skills/security-audit/validate-findings.test.cjs                # 34 tests
node skills/security-audit/validate-coverage-ledger.test.cjs        # 31 tests
bash tools/scripts/check-defaults-block.sh                          # ids only in the Defaults block
bash tools/scripts/check-defaults-block.test                       # planted controls reject them
tools/scripts/build-site.sh && bash tools/scripts/build-site.test   # 38 controls, repeatable build
ast-grep scan --config sgconfig.yml .                               # the repository's own guard
```

Version surfaces must agree: `VERSION`, the README badge, the top `CHANGELOG.md` entry, the
generated changelog row in `site/index.html`, and the orchestrator's "Verified against" date all
read `1.40.0` / `2026-10-23`. Every skill directory has exactly one card in `site/index.html`.

## Residual risk

- **Not a live test of Council.** No member CLI was invoked in any review, so the protocol and the
  adapters' behavior under inherited configuration remain unverified. The commands are checked
  against `--help`, which establishes that the flags exist, not how the tools behave at runtime.
- **Erasure is disclosed, not verified.** `SECURITY.md` says which copies this project cannot
  enumerate and that member-CLI retention was untested; it cannot prove complete erasure.
- **Runtime is proven after the deploy.** Headers and served bytes are checked against the live
  site, not before it.
- **Owner-side evidence stays owner-side.** Provider spend caps, provider retention and the
  operator access inventory are covered only by the dated waivers in
  [the readiness ledger](../../readiness/ledger.md), expiring 2026-10-25T23:59:59Z.
- **The deploy-gate verdict is release evidence.** The gate writes a record per candidate under
  `.scratch/security-gate/<commit>/`, which this repository ignores, and the release tag message
  carries the verdict for the deployed commit. Neither is restated here.
