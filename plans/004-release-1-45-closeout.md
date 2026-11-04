# Plan 004: release 1.45.0 closeout and the next closeout script

Status: executing on `release/1.45.0` (2026-11-04). Owner's brief: review and merge what is open,
bump, update every document, gate, merge to main, tag, clean up; skip waiting on GitHub CI; no
staging exists for this repository.

## Scope

1. **Merge what is open.** PR #40 (pstack 0.15.36 sync, `docs/skill-ledger.md`, bounded
   workflows) is the base of this branch; PR #39 (Biome 2.3.11 → 2.6.4) is merged into it so one
   gated tree covers both; PR #38 is closed as superseded (its `full-stop` text is byte-identical
   to #40's, its paginated review reads and read-only `why` spawns are in #40's regenerated
   collection, and its hand-edited collection conflicts with the regenerated one).
2. **Release bookkeeping** (`CONTRIBUTING.md#preparing-a-release`): `VERSION`, README badge,
   `CHANGELOG.md` 1.45.0, the orchestrator Defaults block re-verified against the vendor model
   lists on the release date, `site/` regenerated, `MEMORY.md`, and the readiness ledger with the
   1.44.0 binding run (`be1a548` → `d98853b`) and the PR #37 binding run (`5336080` → `c3dc2bb`)
   folded in, as the 1.44.0 closeout left owed.
3. **Documentation items the 1.44.0 and PR #37 gates ruled "not a finding — documentation"**:
   E-1/D-B9 (codex-lane egress names the configured Codex provider, not one vendor; the landing
   page says what Codex reads), D-B6 (crossed review sends the change to the other vendor's model),
   D-B8 (gate-candidate count in `MEMORY.md`), D-B1r/D-B2r (council members read repository
   files; HOWTO egress covers council and codex-lane; babysit-pr's exit-1 list names non-transient
   `gh` errors), D-B10 (skill count), D-B11 (executable inventory and Python floor include
   `mneves-motion-film`), D-B12 (film egress: reviewer provider, Chrome URL load), D-B13 (review
   stops after five rounds), D-B14 (`facts.py` reads local pages), D-M1 (ESLint rule is a guard,
   not proof of rendering).
4. **Hardening items the same gates ruled "not a finding — hardening"**, each with a test that
   fails before: pr-wait L-9 (a jobs-API read failure is an incomplete read, not "failed") and H-A7
   (docstring matches the StatusContext check); motion-film H-M2 (`npx --no`), H-M3 (http(s) only,
   `--` before the URL), H-M4 (bounded MP4 box walk), H-M5 (closed cue-kind names), H-M6
   (`persist-credentials: false`).

## Acceptance

- Local gate suite green on the exact tree: skill layout, `agentskills validate`, sync fixtures,
  statechart runner, shell and Python syntax, codex-lane e2e, release contract, readiness catalog,
  pr-wait and SRS suites, Defaults block, ast-grep, pre-commit test, Pages guard, site freshness,
  tools typecheck/lint/test/audit, autoreview tests, motion-film and render suites where their
  engines exist.
- `autoreview` at `--max-priority P3` on the fixed SHA with a model other than the builder's.
- Security deploy gate and production-readiness gate on the frozen tree; independent acceptance by
  a model other than the builder's; no waiver set on the owner's behalf.
- After merge: main CI green, Pages deployed, every served `site/` file byte-equal to the gated
  tree, annotated `v1.45.0` tag whose message carries the verdict lines, independent verification
  (`mneves-verify`) PASS.

## Out of scope

- Needs-validation items C-A6, C-A2, L-6, B-03 and AI-1: they need a disposable public repository
  or live provider calls, which are the owner's to authorize.
- Installing skills into agent folders on any machine (outside the repository).
- A redesign of the landing page: this is a release, not a frontend task.
- The 54 MiB of source clones under `.scratch/pstack-source-clones-20261104/`, created by another
  session; the owner removes them.

## Added on the owner's 2026-11-04 instruction

`tools/scripts/init.sh` (setup, with `init.test`) and `tools/scripts/deploy.sh` (the release
procedure's steps 2 to 5 as one script, with `deploy.test.sh`). `deploy.sh` consumes the gate
records; it does not write the ledger rows, which is the part below.

## Five years out: the closeout script

Every closeout hand-folds the same facts (cursor, binding-run line, gate-history row, WAIVED rows,
`MEMORY.md` state, the tag message) from two JSON records that already hold them. The next
improvement is `tools/scripts/closeout.py <candidate-sha>`: it reads
`.scratch/security-gate/<sha>/production.json` and `.scratch/readiness/<sha>/production.json`,
rewrites the ledger header and gate-history row and refuses when the two records disagree on tree
or verdict (`deploy.sh` already prints the tag message from them). `check-readiness-catalog.py`
checks the result, so the script only has to produce it. Not built in 1.45.0.
