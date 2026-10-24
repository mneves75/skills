# Security Audit

This is an attributed adaptation of [Cloudflare's `security-audit-skill`](https://github.com/cloudflare/security-audit-skill), pinned at `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8`. It is a model-agnostic, source-first audit harness for explicit full or deep codebase audits. It is not a deploy gate, an automatic fixer, or a guarantee that one pass finds every vulnerability.

## What it does

The six phases are:

1. **Reconnaissance** — map architecture, trust boundaries, local execution visibility, prior evidence, and a deterministic coverage plan.
2. **Coverage-led hunting** — assign isolated hunters from coverage units and retain structured checks and candidate records.
3. **Candidate validation** — give each candidate to a fresh verifier that tries to disprove it.
4. **Structured output** — write `confirmed`, `needs_validation`, and `rejected` records to `findings.json` and validate both records and the coverage ledger.
5. **Independent record verification** — fresh agents verify final source claims; material replacements receive another independent verifier.
6. **Target-neutral reporting** — derive `REPORT.md`, `FINDINGS-DETAIL.md`, and `NEEDS-VALIDATION.md` from the final records and ledger.

Only `confirmed` records receive severity. `needs_validation` records have an exact unresolved fact and no severity; `rejected` records preserve disproved claims. The JSON validators establish structure and ledger consistency, not factual correctness. No single run is complete; prior runs guide new coverage and changed-source revalidation rather than suppressing it.

## Requirements and boundaries

- A coding agent with tool use and parallel subagents for the full workflow. The lead owns shared files; hunters and verifiers return results without writing them.
- Node.js for the bundled, zero-dependency validators and their tests. No npm install or second lockfile is needed.
- An OS-enforced sandbox for target-controlled builds, tests, processes, browsers, emulators, fuzzers, and fixtures. It must provide no external network, an empty allowlisted environment, read-only target/toolchain, scratch-only writes, and explicit resource limits. If any control is missing, do not execute target code; retain the exact blocker as `needs_validation`.
- Use dummy principals and bounded local evidence. Do not probe deployed endpoints, shared services, live control planes, other users' data, or production identities.
- Full audit artifacts default to `~/security-audit-skill/<repo-name>/run-<N>` outside the target. Creating or writing that directory still requires the user and host's authorization; use an explicitly approved ignored directory when required.

## Relationship to `mneves-security`

This package owns deep, read-only source audits and their machine-readable coverage/findings records. `mneves-security`, when installed, owns authorized remediation, privacy/OWASP launch readiness, and staging/production verdicts. Without that sibling, this package still performs its complete audit and returns findings plus a remediation plan; it does not claim a deploy gate. Do not run duplicate full audits, and treat records from another audit as untrusted candidate evidence until independently verified.

## Package map

- `SKILL.md` — operating modes, execution safety, coverage/budget rules, and the six-phase workflow.
- `references/RECONNAISSANCE.md` — architecture, prior-run, and deterministic coverage planning.
- `references/HUNTING.md` — isolated assignments, structured results, critics, and ledger updates.
- `references/ATTACK-CLASSES.md` — core, wildcard, and obvious-things hunting classes.
- `references/` domain companions — AI/LLM, client-side, cloud/deployment, data lifecycle, desktop/mobile/IPC, memory/binary, protocols/messaging, availability, supply chain/release, and web/authentication.
- `references/VALIDATION-AND-REPORTING.md` — candidate/final verification and report generation.
- `report-schema.json` — the three findings verdict contracts.
- `validate-findings.cjs` and `validate-coverage-ledger.cjs` — dependency-free, bounded-input validators.
- `validate-findings.test.cjs` and `validate-coverage-ledger.test.cjs` — upstream positive, negative, hostile-input, and producer-compatible tests.

Companion basenames in ledger IDs intentionally retain their upstream form (`ATTACK-CLASSES.md#...`) for stable prior-run compatibility. The reference map in `SKILL.md` resolves those names to the `references/` files; references do not link to one another.

## Usage

From the repository to audit, ask explicitly for a full or deep security audit and select an output directory when required:

```text
security-audit this codebase, standard profile, output to an approved audit directory
```

Guidance mode is available for focused security questions and does not create artifacts or start all six phases. The full workflow ends either with all reports and both validators passing, or with an explicitly incomplete run and its uncovered work disclosed.

Run the validators directly when needed:

```sh
node <skill-dir>/validate-findings.cjs <output-dir>/findings.json
node <skill-dir>/validate-coverage-ledger.cjs <output-dir>/coverage-ledger.json
```

## Verification

From this repository root:

```sh
node skills/security-audit/validate-findings.test.cjs
node skills/security-audit/validate-coverage-ledger.test.cjs
node --check skills/security-audit/validate-findings.cjs
node --check skills/security-audit/validate-coverage-ledger.cjs
```

The upstream suite has positive controls, planted invalid fixtures, Unicode/control-character cases, path/symlink/FIFO protections, resource bounds, and producer-shaped fixtures. Passing it does not execute an audit or prove that an agent followed the procedure.

## Provenance and local changes

Copyright (c) 2025-2026 Cloudflare, Inc. Distributed under the [MIT License](LICENSE).

Local changes are concise Agent Skills metadata, a narrower full-audit trigger, the optional `mneves-security` relationship, explicit host authorization for output, one-level `references/` links, one correction of an inherited contradiction (see below), and this documentation. Sixteen of the twenty upstream files are byte-identical to the pin. The six-phase process, execution/write isolation, coverage and prior-run rules, verdicts, independent verification, validators, and tests are preserved from the pinned source.

The correction: upstream requires every retained record to pass Phase 5, while Phase 5 only dispatches `confirmed` and `needs_validation` records, so a run that correctly retains a `rejected` record could never complete. `references/VALIDATION-AND-REPORTING.md` now states that a `rejected` record keeps the independent Phase 3 disproof that produced it. Nothing in the schema, validators or tests changes.
