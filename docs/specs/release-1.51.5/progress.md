# Release 1.51.5 — run notes

Updated: 2026-11-17. Status: candidate prepared on `release/1.51.5` (from `release/1.51.4` at
`8cbfeb0`); gates not yet run. The binding gate result will live in the private gate records and
the `v1.51.5` tag message.
Machine-readable results: [tests.json](tests.json).

## Scope

- 1.51.4 is never released (owner, 2026-11-17: "Juntar no 1.51.5"): its PR closes without merge
  and this candidate carries its content. Its scope and observations are in
  [release-1.51.4](../release-1.51.4/progress.md); the CHANGELOG has no 1.51.4 entry.
- GPT-6.2 routes at high (owner, 2026-11-17): the orchestrator's Codex Sol seats run
  `gpt-6.2-sol` at high, the Codex planner and plan advisor `gpt-6.2-astra` at high; autoreview's
  Codex default is `gpt-6.2-sol` at `high`; pstack's Codex mapping names `gpt-6.2-sol` at `high`
  and says that level takes the place of the sheet's `default effort` line on Codex; the
  routing-eval Codex consumer is `gpt-6.2-sol` at high.
- ROOT-B-H01 (1.51.4 security gate): `mneves-teach-back-srs` prints stored text with control
  characters made visible.
- VERSION, README badge, CHANGELOG 1.51.5 and the regenerated landing changelog rows.

## Observed

- Defaults sources, read 2026-11-17: the OpenAI models page lists `gpt-6.2-astra` and
  `gpt-6.2-sol` and no longer lists `gpt-6-astra`; the GPT-6.2 guide; the Codex models cache
  (Codex CLI 0.169.0) lists both with efforts low through ultra, and lists no `none` or `minimal`
  for any model. The Anthropic ids are unchanged from 1.51.4's verification.
- Pi 1.5.2 `pi --list-models` lists no gpt-6.2 model under `openai-codex` or `openrouter`, so the
  Pi rows keep `gpt-6.1-sol`. No Amp CLI is installed here, so autoreview's `amp` default keeps
  `openai/gpt-6.1-sol`.
- autoreview: the updated assertions failed before the source change (21 failures) and pass
  after it.
- teach-back-srs: the new CLI test failed before the fix (ESC, BEL, CSI, CR, 0x01 and DEL reached
  stdout) and passes after it.
- pstack: `sync-pstack.sh` regenerated only `poteto-mode/references/codex-tools.md` and the
  `UPSTREAM` hashes. The tooling policy patch applies to the pinned port commit; its generator
  was not run, because it needs the adapted tree (it fails on the `unslop` row that adaptation 02
  removes).

## Codex prompt update

The prompt update on top of `ed07e22` uses the
[OpenAI migration and prompting guide](https://developers.openai.com/api/docs/guides/latest-model).
The existing Codex seats keep their selected effort. Both GPT-6.2 routes now validate
explicit effort overrides against the advertised levels in autoreview. The provider prompt,
four Codex skill launch prompts, delegated briefs, and pstack synthesis prompts also changed.
The collection was regenerated from its existing pins. The checks for this working-tree
update are recorded separately in tests.json so the earlier suite result keeps its revision.

## Routing eval

- Revision 11. Changed against the 1.51.3 baseline: O4, O8, P19 (no longer clarified) and new
  O15. 1.51.4's routing values equal 1.51.3's, so `9d90d4a` (v1.51.3) is the baseline commit.
- Run both live runs from this candidate's `tools/scripts/routing-eval.py`: it reads sources with
  `git show COMMIT:<path>` but takes cases and consumers from the running script, so the
  `--baseline` run on `9d90d4a` also uses the `gpt-6.2-sol` high consumer and stays comparable.

## Open decisions

- The 1.51.4 binding run is not folded into the readiness ledger: 1.51.4 never ships. The fold
  owed is this release's binding run, added after 1.51.5 ships.
- The 16 conditional readiness waivers the owner renewed to 2026-11-28 for the 1.51.4 candidate
  need the gate session to record whether they carry over to this candidate, in its private
  `owner-approval.json`.

## Evidence limits

- The checks in tests.json ran on the branch before push; they are builder-run, not independent
  acceptance. No live routing eval, security gate or readiness gate ran here: both Codex accounts
  are out of quota until 2026-11-19.
