# Council and security-audit: review, verification and gate evidence

Companion to [plans/003](../../../plans/003-council-security-audit.md). It records what the
release was checked by, what each check found, and how every finding ended.

The raw reviewer and verifier transcripts were session artifacts and are not shipped. What is
shipped is this record: the seat and model family, the findings, the disposition, and the commit
that carries each fix. The commits and the checks they ran are the traceable output; a summary
nobody can reproduce would be worse than no summary.

## Seats

| Role | Seat | Model family | Independence |
|---|---|---|---|
| Builder | main session | local fallback seat (pi, provider roll) | — |
| Adversarial review A | Codex CLI, read-only sandbox | vendor review seat, high effort | different model from the builder |
| Adversarial review B | fresh context, pi | local fallback family | fresh context, same family as the builder |
| `mneves-verify` | fresh context, pi | local fallback family | fresh context, same family as the builder |
| Deploy gate (×4) | fresh context each run | local fallback family | fresh context, same family |
| Independent acceptance (×3) | Codex CLI, read-only / temp-only sandbox | vendor review seat, high effort | different model from the builder |

Review B and the verifier share the builder's model family. That is a real limitation of this
record: their findings were treated as leads and re-checked with commands, not as independent
assurance. The different-model rows are the only ones that satisfy the cross-model requirement,
and the deploy gate refused to accept anything less.

## Adversarial review A (different model)

| Finding | Severity as raised | Disposition | Fix |
|---|---|---|---|
| Council claimed isolation it cannot enforce; a session inside the project lets one member read another's reply | high | fixed | `c11aa07` — independence stated as a protocol obligation, session root outside the project and every working directory |
| Cursor's prompt travels in the argument vector | medium | fixed as disclosure | `c11aa07` — the exposure is named and private content requires accepting it |
| Fallback trigger could be read as satisfied by one missing primary seat | medium | fixed | `c11aa07`, `5499adc` |
| Inherited contradiction: a retained `rejected` record had to pass a Phase 5 step that never receives it | medium | fixed | `c11aa07` — Phase 3 disproof retained; 16 of 20 upstream files stay byte-identical |

Its preservation check reproduced independently: 17 of 20 upstream files were byte-identical at
the time, and the three differences were the documented adaptation.

## Adversarial review B (fresh context)

| Finding | Severity as raised | Disposition | Fix |
|---|---|---|---|
| `claude --restricted` does not stop the reviewed repository's `CLAUDE.md`, skills or hooks loading as instructions | high | fixed | `5499adc` — `--safe-mode` added, verified in installed help |
| Codex loads the repository's `AGENTS.md` as instructions | medium | fixed | `5499adc` — `-C` and `-c project_doc_max_bytes=0`, verified against `codex-cli 0.164.0` |
| A round where every member failed still produced a plan labelled as a council | medium | fixed | `5499adc` — stops and reports un-counciled, naming the rounds |
| The adapter table is bare commands, while the prose requires a supervisor | medium | fixed | `5499adc` — the table is stated as a member command run under the step 3.2 supervisor from `CONTEXT_DIR` |
| Cursor's read-only boundary rests on a start mode, the bar that excluded Gemini | medium | downgraded honestly | `5499adc` — Plan Mode enforcement in a non-interactive run is stated as not established; the member stays but the claim shrinks |
| Both validators accept an empty ledger and empty findings, so they cannot prove the run did the work | medium | documented, not fixed | recorded as an upstream gap in the plan; forking the pinned validators and their 65 tests was rejected |
| Orchestrator wording read as permission to use one model twice | medium | fixed | `5499adc` — two sessions of one model are self-review; report the gate blocked |
| Session inside `PROJECT` (same root cause as review A's first finding) | medium | already fixed | `c11aa07` |

## `mneves-verify` (fresh context)

Nine frozen criteria, each re-derived with commands: catalog and spec validity, references
layout, portability, provenance (pins resolved, exactly 16 of 20 files byte-identical), version
agreement, the owner's fallback requirement quoted clause by clause, three specific shipped
claims, the site build and cards, and no overclaiming. Verdict: PASS, with two non-blocking
caveats — the browser claim had no persisted artifact at that time, and the backticked companion
basenames are navigation pointers rather than links. The browser transcript now exists at
`.scratch/evidence/browser-ea2169e.log` (ignored, outside the tracked tree).

## Deploy gate and independent acceptance

Every gate run audited the whole first-party source, all twelve areas and the 32 launch
controls, and none reused another tree's verdict.

| Run | Tree | Outcome | What blocked it | Fixed by |
|---|---|---|---|---|
| 1 | `42fcbea6` | BLOCK | independent acceptance could not be self-issued from the builder's seat; one Medium finding F-1 (the security policy omitted both new stores) | `860332d` |
| 2 | (acceptance on `f46c7a3e`) | BLOCK | F-1 only partly closed: "no tool keeps another copy" ignored stores member CLIs write themselves | `ea2169e` |
| 3 | (acceptance on `dae02fb`) | BLOCK | one sentence let "do not" govern "confine reads", contradicting the Claude row | `7883500` |
| 4 | (acceptance on `4e32d14`) | BLOCK | this plan asserted review and gate history with no in-tree evidence, and repeated the blanket read-scope claim | this commit |

The five launch controls that are not `Yes` (SEC-13, SEC-17, SEC-20, SEC-23, CMP-06) carry the
owner's dated waivers in [the readiness ledger](../../readiness/ledger.md), expiring
2026-10-25T23:59:59Z. Nothing in that list was waived by the agent.

The final verdict, the accepted commit and tree, and the residual risk belong in the release tag
message and the gate record the skill writes under `.scratch/security-gate/<commit>/`, which is
ignored by design and therefore not reproduced here.

## Residual risk this record does not remove

- No live member invocation was executed in any review: Council's protocol and adapter behavior
  under inherited configuration are unverified.
- `gitleaks` produced no report in the gate run (flag misuse), so the second secret scanner is
  NOT TESTED; TruffleHog was run and found no verified secret.
- Provider spend caps, provider retention and the operator access inventory remain owner-side
  evidence, covered only by the dated waivers above.
- Runtime headers and the served bytes are proven after the deploy, not before it.
