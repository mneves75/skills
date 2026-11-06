# Plan 006: Preserve the original audit origin across release resumes

## Status

- Priority: P1
- Effort: S
- Risk: MED — release metadata must remain truthful without weakening admission checks
- Category: bug, recovery, tests
- Depends on: none
- Planned at: `0f3047be818069bcc1f2d91150f0e394505b55e3`, 2026-11-05
- Delivery: verified commits pushed to `fix/release-provenance`; no main merge, production deploy or tag in this task

## Why this matters

The first release invocation writes gate records for the merge commit. A later MERGED/tag resume selects those newer records, then overwrites their original audit origin with the merge commit itself. The published source remains the same, but its evidence incorrectly loses the commit at which the full audit was performed. This occurred during 1.46.0 closeout; its private records were corrected separately. Fix the writer so operators do not need that manual repair.

## Deeper task, not broader scope

A release engineer would model the record transitions and prove provenance invariants, rather than add a special-case repair for one release. Raw inputs are the actual CLI writer, its real-Git/fake-provider harness and original/reused JSON shapes. Use characterization, repeated CLI execution and an adversarial original-script control. The independent oracle is a RED regression on the baseline script, GREEN on the correction and unchanged refusal behavior.

Five-year criterion: the effective audit origin stays stable over repeated attempts and transfers between identical-tree commits. This is provenance idempotence, not byte-idempotence: the existing `created_at` field intentionally records the new reuse event.

Sources: [Git revision/object semantics](https://git-scm.com/docs/gitrevisions) distinguish commits and trees. [AWS retry guidance](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) motivates semantic equivalence over retries. This plan does not claim SLSA compliance or introduce an attestation framework.

## Current state and vocabulary

- `tools/scripts/deploy.sh:505-517` contains the only production writer with this assignment:

```python
record = json.load(open(sys.argv[1], encoding="utf-8"))
record["reused_from"] = record.get("commit")
record["commit"] = sys.argv[3]
record["created_at"] = sys.argv[4]
```

- Both security/readiness records call that writer. The selector already validates schema, candidate tree, verdict, independent acceptance, expiry and readiness validity before publication. Preserve those rules.
- Effective audit origin means the existing nonempty `reused_from`, otherwise the source record's `commit`.
- `tools/scripts/deploy.test.sh` runs the real CLI in disposable Git repositories, with fake `gh`/`curl`, a local bare origin and synthetic records. `run_deploy` supplies `DEPLOY_REPO=test/skills`, an example-domain site and bounded test polling. `DEPLOY_SH` selects another script for regression controls.
- Security fresh records permit an empty origin; readiness permits the optional field to be absent. Existing fixtures can explicitly name their freshly audited commit. Do not invent a rule that every self-valued string is necessarily false: truth depends on the actual audit origin.
- The deployed commit is not necessarily the audited commit; equality of their Git trees permits documented reuse. Preserve the actual root across further transfers.
- `CONTRIBUTING.md` owns operator release instructions. `CLAUDE.md` imports `AGENTS.md`, so keep any new rule only in AGENTS. VERSION is canonical; README badge/top changelog/generated site must agree.

## Options and choice

1. **Chosen:** preserve the existing effective audit origin when copying to another commit, and preserve the provenance field's existing form for same-commit rewrites. Local change inside the current writer, no schema change.
2. Reconstruct a chain by opening historical records: rejected because it adds I/O, missing-history/cycle behavior and cannot recover an origin already lost without evidence.
3. Add an `audited_commit` field/schema migration: rejected because the current optional `reused_from` contract already expresses the necessary distinction.

Load-bearing target shape, subject to verified equivalent implementation:

```python
if record["commit"] != sys.argv[3]:
    record["reused_from"] = record.get("reused_from") or record["commit"]
```

Do not guess a historical origin, rewrite old private records, globally reject previously supported valid shapes, change timestamps/validity semantics or implement a chain walker.

## Scope

Only these paths may change:

- `tools/scripts/deploy.sh`
- `tools/scripts/deploy.test.sh`
- `CONTRIBUTING.md`
- `AGENTS.md` — one relevant release-provenance rule/pointer if useful
- `VERSION`, `README.md`, `CHANGELOG.md`
- `site/index.html`, `site/howto.html` — generator output only
- `skills/mneves-fable-orchestrator/SKILL.md` — verification-date line only if the new changelog date requires it, with fresh vendor checks
- `plans/006-release-audit-provenance.md` and `plans/README.md`

Do not edit other skills, collections, installed agent configuration, current production gate/waiver records, user handoffs, lockfiles, UI styling/layout or provider settings. This is a CLI correction, so no site redesign is requested; a generated changelog row does not justify new product scope.

## Git and isolation

Work on `fix/release-provenance` in the assigned disposable worktree. Confirm base SHA and `origin/main` before edits. Preserve other agents' changes. Use explicit paths for staging; no `git add -A`, amend, force push or default-branch push. User authorized commits and pushes to this working branch. Push with an explicit destination and set its upstream to that feature branch, not origin/main.

Suggested units: `fix(release): preserve audit origins across resumed publication`, then `docs(release): prepare 1.46.1 provenance correction`. Each commit describes actual proof. The advisor maintains the plan index; coordinate its final status before the closing commit.

## Step 1 — Establish the baseline and write regressions first

1. Read the complete helper and harness, applicable instructions and operator docs.
2. Run existing `bash tools/scripts/deploy.test.sh` with a task-owned ignored TMPDIR; record actual exit/count.
3. Extend the existing harness, not a second test framework. Start with the lost-origin resume regression, observe RED, then make its smallest correction in Step 2. Continue one vertical case at a time rather than writing a bulk imagined suite. Cover these meaningful end-to-end cases:
   - OPEN first publication establishes the candidate audit origin for both record kinds.
   - A no-tag publication followed by MERGED `--tag` resume keeps that origin, performs no second merge and tags the same merge.
   - Repeated MERGED attempts preserve the root, not the immediately preceding record commit.
   - An already-reused source transferred to another real identical-tree commit preserves the original root.
   - A fresh same-commit rewrite preserves security's empty origin and readiness's absent optional field.
4. Compare full record objects, allowing only the existing documented commit/creation/provenance changes. Explicitly check waiver arrays, verdicts, tree, independent acceptance, evidence and `valid_until`; retries must not extend validity.
5. Run new tests against the unchanged baseline script via `DEPLOY_SH`. Capture RED assertions showing the specific lost-origin/same-commit problem. A tool/fixture error is not acceptable RED evidence.

Never call real GitHub or Pages. All merges/tags/pushes in these tests belong only to the harness's local synthetic repositories. Keep existing negative guard cases intact.

## Step 2 — Make the smallest writer correction

Apply the chosen local provenance rule. Keep normal fresh transfers, record schemas, source snapshot order, Git/tree matching, gate selection, HTTP verification and tag boundaries unchanged. Do not extract unrelated helpers or alter retry budgets.

Run `bash -n tools/scripts/deploy.sh tools/scripts/deploy.test.sh` and the complete deploy harness. All cases must pass. Re-run the same new tests with the exported baseline script to prove they still detect the old behavior. If the same bug survives two fixes, stop and report per owner rule.

## Step 3 — Documentation and patch preparation

Document stable audit-root semantics and same-commit optional-field preservation in CONTRIBUTING and the helper's existing header; add a concise AGENTS pointer rather than duplicating the procedure. CLAUDE remains its existing import unless its actual content requires a change.

Bump 1.46.0 to 1.46.1, update the README badge and top changelog. Use the owner's current project date consistently. Re-verify orchestrator model IDs against official vendor lists, retaining evidence; date must equal the top changelog entry. No model/effort policy change.

Regenerate site using its existing locked tools. A fresh worktree needs its own locked `tools/node_modules`; read dependency guidance before installing, use `bun install --frozen-lockfile`, never share/copy/link mutable dependencies with the main checkout. Lockfiles must remain unchanged.

## Step 4 — Verify, review and deliver

- `bash tools/scripts/deploy.test.sh` — all old/new cases PASS, real CLI with fake providers.
- `python3 tools/scripts/check-pages.test.py` — actual Pages guards PASS.
- `tools/scripts/check-defaults-block.sh` and its existing test — PASS.
- `tools/scripts/build-site.sh` then `bash tools/scripts/build-site.test` — consistent/repeatable generated site, all controls PASS.
- `python3 tools/scripts/check-readiness-catalog.py` — existing catalog consistent; no unauthorized binding/waiver update.
- `git diff --check` and scope check — clean and only allowed paths.
- Collect installed cccc evidence for supported changed source; explicitly report unsupported Bash/embedded-Python coverage, never a fake score. Skip crapper/dryer/mutator if not installed.
- Fresh Standards and Spec axes plus adversarial challenge to provenance, same-file read/write, selector precedence and validity preservation. Review only this diff.
- Fresh different-model `mneves-verify` checks the frozen done criteria. Keep unavailable review BLOCKED; do not self-certify or extend the previous release's routing/waivers.
- Commit/push all task-owned verified changes. Verify origin branch equals local HEAD. No production invocation; a future merge needs its own exact-candidate gates/authorization.

## Done criteria

1. Actual baseline script fails the new regression cases for lost origin; corrected script passes all cases.
2. Both kinds preserve audit roots through first write, repeated resume and a further identical-tree transfer; same-commit fresh forms remain intact.
3. Waivers, verdicts, tree, evidence, acceptance and validity are preserved; existing refusal controls still PASS.
4. Version/badge/changelog/date/generated site agree; relevant operator docs explain the rule.
5. Independent reviews and mneves-verify have no unresolved in-scope finding.
6. Verified commits are pushed to the explicit feature branch; main/production/tag/history are unchanged.
7. Remove only task-owned disposable worktrees, dependencies/processes and uncited scratch after evidence has been summarized; run the owner's leftovers/worktree/scratch scans. Preserve the delivered unmerged branch until the owner controls its merge; report its exact later cleanup commands rather than discard published work.

## STOP conditions

- In-scope source has drifted from planned SHA/excerpts: reconcile instead of resetting other work.
- A correct fix needs schema changes, historical-root guessing, provider settings, out-of-repo changes or unrelated source edits.
- Regression output is an infrastructure error rather than the expected incorrect provenance.
- Same bug survives two fixes or mandatory independent review is unavailable.
- Any production/GitHub action is attempted from the synthetic harness: stop immediately.

## Maintenance and execution record

Keep the single writer responsible for both record kinds. Test semantic roots rather than freezing timestamps or private installation paths. Later schema work must preserve the distinction between content tree, deployed commit and original audit origin.

### Observed execution, 2026-11-05

- Origin was fetched and the visible main checkout fast-forward checked at the planned base; no incoming changes. Unrelated untracked handoffs were preserved. Implementation is isolated on `fix/release-provenance`.
- Before the production edit, the existing real-CLI harness passed 69/69 cases. The added no-tag publication/tag-resume regression then failed because both records replaced the original audit commit with the merge commit, despite CLI exit 0.
- The focused six-case control against the original script returned 1 PASS / 5 FAIL. The same six cases passed after the minimal conditional writer change. Failures were actual JSON provenance mismatches, including empty/absent same-commit forms, rather than provider or fixture errors.
- Main-session inspection covered every current source/test/documentation hunk. Full-object assertions preserve waivers, evidence, verdicts, tree, independent acceptance and validity while allowing the documented timestamp/commit changes. This integration check is not the required independent review.
- `cccc` 1.8.0 reported zero supported files and zero parse errors for the changed Bash/embedded-Python source; complexity coverage is unsupported, not a passing score. Optional crapper/dryer/mutator tools were absent.
- Vendor IDs were rechecked against the official [OpenAI model list](https://developers.openai.com/api/docs/models), [Anthropic model list](https://platform.claude.com/docs/en/models/overview) and [OpenCode Go list](https://docs.opencode.ai/docs/go/). The existing verification date already matches this patch's date; model policy and IDs remain unchanged.
- Independent review is currently **BLOCKED**: the required cross-model reviewer returned HTTP 403. A task-specific request to use the advice model for Standards, Spec and final verification remains unanswered. The prior release's exception does not extend to this changed candidate. No independent PASS is claimed.

### Frozen regression and integration results

Both executor and main-session advisor separately ran the following commands against the frozen source; their results agreed. Source SHA-256: `deploy.sh` = `8dd122c979d6cc6f9e3a45dcf6062b076c951b9a0eba6a44fe77075dbb23c1e9`; `deploy.test.sh` = `5d148c1e30ef8a6f0471c99120e57c2b291769d7048b480f28e36c3032c97065`. The baseline control was exported directly from the planned Git object, not reconstructed.

| Command or flow | Observed result |
|---|---|
| `bash -n tools/scripts/deploy.sh tools/scripts/deploy.test.sh` | PASS, exit 0 |
| `bash tools/scripts/deploy.test.sh` | PASS, 75 passed / 0 failed |
| Same harness with `DEPLOY_SH` pointing at the unchanged baseline | Expected RED, exit 1: 70 passed / 5 provenance failures; original 69 refusal/positive cases remain passing |
| First OPEN publication | PASS, both audit roots established and complete protected fields retained |
| Repeated MERGED resumes, two attempts | PASS, both roots retained and no second merge |
| MERGED `--tag` resume | PASS, both roots retained, no second merge, annotated tag peels to the same synthetic merge |
| Further identical-tree transfer of an already-reused record | PASS, original audit roots retained for both kinds |
| Fresh same-commit rewrite | PASS, security's empty origin and readiness's absent origin retained |
| `python3 tools/scripts/check-pages.test.py` | PASS, 2 tests |
| `bash tools/scripts/check-defaults-block.sh` and its `.test` | PASS, 1.46.1/date agreement and 5 planted controls |
| `bash tools/scripts/build-site.sh` and its `.test` | PASS, 42 controls; HOWTO output byte-identical, landing changelog rows regenerated |
| `python3 tools/scripts/check-readiness-catalog.py` | PASS, 136 controls / 160 preserved items, ledger consistent |
| `git diff --check`, version/badge/changelog/generated-row and allowed-path checks | PASS; lockfiles and unrelated files unchanged |

Only disposable synthetic repositories were merged/tagged/pushed by the CLI tests; fake providers handled all network-facing behavior. No real release command or production mutation was used. These are deterministic CLI proofs, not a production publication or a substitute for cross-model acceptance.

### Remaining acceptance and delivery boundary

- Standards axis: **BLOCKED**, required reviewer unavailable; no findings or PASS are invented.
- Spec axis: **BLOCKED**, same model-routing dependency.
- `mneves-verify`: **BLOCKED**, a fresh different-model verifier has not run. Done criterion 5 is not satisfied.
- Git delivery targets only the working branch and a draft PR for CI. Main, production, existing tags and published history remain outside this correction's delivery scope.
- Own task worktree, dependencies and temporary logs are removed after their evidence is summarized and the branch is pushed. Pre-existing handoffs, scratch and protected gate records are preserved. An unmerged remote PR branch remains the owner-controlled deliverable; delete it only after merge, with `git push origin --delete fix/release-provenance` if the merge did not already delete it.
- The requested `codemap --importers` check for this plan returned **not indexed** because the worktree is under an excluded folder. Importer coverage is unknown, not zero. The repository leftovers scan ran read-only, but some system-wide categories were unavailable under the sandbox; worktree and scratch inventories were obtained separately. No cache, simulator or unrelated data cleanup was performed.
