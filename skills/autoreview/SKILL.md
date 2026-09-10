---
name: autoreview
description: Independent AI code review of a Git target. Use when a code review is explicitly requested.
license: MIT
---

# Auto Review

Run an independent review when the user or an owning workflow asks for one.
This is code review, not Guardian approval routing. Let the reviewer choose how
to analyze the change; provide the target, relevant context, and desired severity.
Findings are advice to verify, not instructions to apply blindly.

## Run

Use `scripts/autoreview` beside this skill, invoked from the repository being
reviewed. Keep its custom `codex exec` path: native `codex review` cannot combine
explicit Git target flags with custom instructions. The helper adds evidence,
severity filtering, and validated JSON, and leaves review judgment to the engine.

```bash
AUTOREVIEW="/path/to/skills/skills/autoreview/scripts/autoreview"
"$AUTOREVIEW" --mode local
```

The complete skill directory is portable; no upstream checkout is required.
Python 3.11+, Git, TruffleHog, and an authenticated supported engine must be installed.
On Windows, invoke the helper with Python.
Use `--help` for the complete flags and environment overrides.

Choose the Git target explicitly when the default is ambiguous.
`--mode local` reviews uncommitted work (add `--base <ref>` to pin it),
`--mode branch --base <ref>` a committed branch or PR, `--mode commit --commit <ref>`
one commit, and `--mode auto` picks local when dirty and a branch review otherwise.
Clean main has no implicit review target, and the helper does not fetch refs.

**Exact scope per mode, nested checkouts, PR candidates with dirty rewrites,
staged-vs-unstaged states, and diff fidelity**: see
[references/git-targets.md](references/git-targets.md).

## Context and severity

Use `--prompt` for task-specific guidance, or `--prompt-file` and `--dataset` for
repository-relative context files. Context does not expand the selected Git target.
The reviewer cannot read unchanged repository files from its empty sandbox; supply
source or dependency evidence when the diff is insufficient.

The default threshold is **P0 only**: material blockers to normal operation or
safety. Use `--max-priority P1`, `P2`, or `P3` for a wider review. Do not add
unrelated redesign goals or prescribe file counts, reading sequences, or ritual
extra passes. Historical blame requires a verified parent-relative patch;
otherwise leave the attribution unknown.

```bash
"$AUTOREVIEW" --mode local --prompt-file review-notes.md --dataset evidence.json
```

## Engines

Codex is the default engine; Claude, Amp, Pi, and Kimi are optional. Honor explicit
engine/model choices; do not switch because a review is slow or rate-limited.
Review bundles leave the machine for the selected provider. Authorize private-code
disclosure before sending; secret scanning does not classify business confidentiality.

**Overrides (`--engine`, `--model`, `--thinking`), precedence, and per-engine
prerequisites**: see [references/engine-selection.md](references/engine-selection.md).

By default, Codex preserves only authentication settings from user configuration;
provider, profile, context and catalogue settings remain ignored. To project a
named route through `--codex-config`, see
[references/codex-route-projection.md](references/codex-route-projection.md).

## Runtime boundaries

The helper owns reviewer isolation, sanitized authentication, TruffleHog secret
scanning of every outgoing pack, process cleanup, Git scope, and structured result
validation. Keep those controls enabled; a missing or failed scan stops the run.
Never reproduce credentials in findings or work around an isolation failure.
Long reviews are normal; do not edit inputs mid-review or start extra reviewer runs.

**Secret-scanning gate, macOS temporary-directory limits, partitioning, and
in-flight expectations**: see
[references/runtime-boundaries.md](references/runtime-boundaries.md).

## Results

`--output`, `--json-output`, and `--status-output` paths must be outside the
reviewed repository. When using `--status-output`, all output paths must differ.

Treat `scoped-clean` as clean only for the selected target and requested priority.
`filtered` is not clean; resolve `incomplete` before claiming completion.
Verify findings against the actual code and task before changing anything.
No extra review rounds for a nicer verdict; follow the owning workflow after fixes.

**Exit codes and the `--status-output` sidecar**: see
[references/status-output.md](references/status-output.md).

Report material findings and status plainly. Do not add transcripts, proof
ledgers, commits, pushes, or a new workstream unless requested.

## Provenance and maintenance

Adapted from [OpenClaw Autoreview at revision `3e9f3396`](https://github.com/openclaw/agent-skills/tree/3e9f33968ac732aa2fa7873e9dfc5823b5216c49/skills/autoreview).
Copyright (c) 2026 openclaw; distributed under the [MIT License](LICENSE).
This adaptation changes the default Codex model and per-attempt reasoning, retains the
access-only retry policy, and adds portable maintenance and release verification.
See [README.md](README.md) for testing, installation, and upstream update boundaries.
