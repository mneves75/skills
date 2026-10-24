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

One workflow ran two independent reviewers on the same frozen tree: a safety track and a
standards/spec track. Both ran in fresh contexts on the builder's model family, so their findings
were treated as leads and re-checked with commands.

### Safety track

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

### Standards and spec track

| Finding | Severity as raised | Disposition | Fix |
|---|---|---|---|
| The adaptation described its link changes as link-only, while the files also gained the backticked-basename convention | low | fixed | the README and provenance now describe both |
| The local-change list was incomplete (it did not name every deviation) | low | partially fixed | the provenance and README lists were rewritten; a reader should still diff against the pin rather than trust a summary |
| The defaults guard covers only `SKILL.md`, so a model id placed in a reference file would pass CI | low | follow-up, not fixed here | a guard-coverage change touches the orchestrator's own tooling; recorded in the gate record |
| Product names appeared in fallback prose instead of capability roles | low | fixed | prose refers to seats and roles; ids stay in the Defaults block |
| The candidate's changelog date could be read as a release claim before release | low | disproved | the repository's own gates require the top entry's date to equal the verified-on date, so the date is a release-gate input, not a claim |

## `mneves-verify` (fresh context)

Nine frozen criteria, each re-derived with commands: catalog and spec validity, references
layout, portability, provenance (pins resolved, exactly 16 of 20 files byte-identical), version
agreement, the owner's fallback requirement quoted clause by clause, three specific shipped
claims, the site build and cards, and no overclaiming. Verdict: PASS, with two non-blocking
caveats — the browser claim had no persisted artifact at that time, and the backticked companion
basenames are navigation pointers rather than links. The browser transcript now exists at
`.scratch/evidence/browser-ea2169e.log` (ignored, outside the tracked tree).

## Deploy gate and independent acceptance

Three full deploy-gate audits completed, one per tree, each covering the whole first-party source,
all twelve areas and the 32 launch controls: `42fcbea6`, `4e32d14` and `011b22e7`. Two further
trees, `f46c7a3e` and `dae02fb`, were blocked by independent acceptance after the audit for them
was superseded mid-run, so they are acceptance rounds rather than completed audits, and the table
labels them that way. No run reused another tree's verdict.

| # | Tree | Kind | Outcome | What blocked it | Fixed by |
|---|---|---|---|---|---|
| 1 | `42fcbea6` | full audit | BLOCK | independent acceptance cannot be self-issued from the builder's seat; one Medium finding F-1 (the security policy omitted both new stores) | `860332d` |
| 2 | `f46c7a3e` | acceptance only | BLOCK | F-1 only partly closed: "no tool keeps another copy" ignored stores member CLIs write themselves | `ea2169e` |
| 3 | `dae02fb` | acceptance only | BLOCK | one sentence let "do not" govern "confine reads", contradicting the Claude row | `7883500` |
| 4 | `4e32d14` | full audit, verdict WAIVED pre-acceptance | BLOCK at acceptance | the plan asserted review and gate history with no in-tree evidence, and repeated the blanket read-scope claim | `1acf6e6` |
| 5 | `011b22e7` | full audit | BLOCK | CI `check` was red when the audit observed it, and acceptance was still pending; the failure reproduced as a flake and the rerun of the same tree passed | this commit |

This record lists the findings those seats raised and how each ended. It is not a claim to have
enumerated every observation any seat made: items raised at Info level, or reclassified during a
later acceptance round, are carried in the gate record as follow-ups instead of being presented as
resolved. In particular the defaults guard still covers only `SKILL.md` (a reference file could
carry a model id past CI), the `cccc` complexity evidence for the new Node files exists but was
not in this document when acceptance first read it, and the readiness ledger cites
`.scratch/readiness/production.*`, which is absent on this host.

The five launch controls that are not `Yes` (SEC-13, SEC-17, SEC-20, SEC-23, CMP-06) carry the
owner's dated waivers in [the readiness ledger](../../readiness/ledger.md), expiring
2026-10-25T23:59:59Z. Nothing in that list was waived by the agent.

The final verdict, the accepted commit and tree, and the residual risk belong in the release tag
message and the gate record the skill writes under `.scratch/security-gate/<commit>/`, which is
ignored by design and therefore not reproduced here. Earlier runs' records were returned as text
in the release session rather than persisted, which is why this table is the durable summary.

## Residual risk this record does not remove

- Not a live-Council test: no member CLI was invoked in any review, so the protocol and the
  adapters' behavior under inherited configuration remain unverified.
- `gitleaks` produced no report in the gate run (flag misuse), so the second secret scanner is
  NOT TESTED; TruffleHog was run and found no verified secret.
- Provider spend caps, provider retention and the operator access inventory remain owner-side
  evidence, covered only by the dated waivers above.
- Runtime headers and the served bytes are proven after the deploy, not before it.
