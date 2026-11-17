# Release 1.51.4 — run notes

Updated: 2026-11-17. Status: candidate prepared on `release/1.51.4` (from `main` at `9d90d4a`);
gates not yet run. The binding gate result will live in the private gate records and the
`v1.51.4` tag message.
Machine-readable results: [tests.json](tests.json).

## Scope

- `mneves-fable-orchestrator`, Delegation brief: tell a worker not to call an advisor tool where
  the host has one (open questions go in its result) and to read files with bounded reads, never a
  whole large file. Reason: the owner's 30-day cost scan (2026-11-17) found subagent advisor calls
  and whole-file shell reads among the largest delegated costs.
- Defaults block re-verified against the vendors' model lists; only the verified-on date moves.
- 1.51.3 binding run folded into `docs/readiness/ledger.md` and `plan.md`; `MEMORY.md` release state.
- VERSION, README badge, CHANGELOG 1.51.4 and the regenerated landing changelog rows.

## Observed

- `git rev-parse 9d90d4a^{tree}` and `8ff1b75^{tree}` both print `921e828…`: the merge kept the
  gated tree.
- The ledger's 136 status/tier pairs equal those of the 8ff1b75 binding assessment, which in turn
  equal the 1.51.2 assessment's.
- Defaults sources, read 2026-11-17: Anthropic models overview (`claude-opus-5-5`,
  `claude-fable-5-2` as Claude API IDs and aliases); Claude Code model configuration (`opus` uses
  the latest Opus, Opus 5.5 on the Anthropic API); Codex models cache read through `codex-auto exec`
  (`gpt-6.1-sol`, `gpt-6-astra`); `pi --list-models` (`opencode-go` `deepseek-v4.1-flash`). No id
  was missing.
- No routing-eval case anchors the Delegation brief. The orchestrator `SKILL.md` is a hashed
  routing-eval source and its Defaults date moved, so the binding gate needs a fresh live
  `routing-eval.py run` on the candidate. No case is marked `changed: true` (P19 is `clarified`),
  so no baseline run is required.

## Open decisions

- The owner's decision of 2026-11-17, reported by the main session ("Renovar até 11-28"), renews
  the same 16 conditional readiness waivers under the same condition for the 1.51.4 candidate to
  2026-11-28T23:59:59Z. By the ledger's convention a renewal is recorded in the candidate's
  private `owner-approval.json` by the gate session, not in tracked files; the fold renews none.

## Evidence limits

- The checks in tests.json ran on the branch before push; they are builder-run, not independent
  acceptance. No live routing eval, security gate or readiness gate ran here.
- The commit that moves the Defaults date precedes the CHANGELOG commit, so
  `check-defaults-block.sh` passes from the release-bump commit on, not on that one commit alone.
