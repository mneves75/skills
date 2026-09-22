---
name: autoreview
description: Independent AI code review of a Git target. Use when a code review is explicitly requested.
license: MIT
compatibility: Needs Python 3.11+, Git, TruffleHog, and an authenticated review engine (Codex by default; Claude, Amp, Pi, or Kimi optional) on the machine that runs `scripts/autoreview`.
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

Local selection honors `core.autocrlf` from external operator Git configuration,
with repository-local values and attributes retaining precedence. Only its
validated scalar value reaches diff/status; other global and system Git
configuration stays disabled. Repository-owned or relative global-config
overrides are not imported, and reviewed source bytes are not rewritten.

Local collection disables effective Git clean/process commands and requires
conversion to succeed. Unused drivers, unchanged filtered neighbors, staged-only
changes, and deletions can still be reviewed without executing converters.
If Git needs executable conversion to assemble the diff, collection fails before
any reviewer starts. This can include an unchanged filtered file whose stat cache
needs refreshing. Use explicit branch or commit mode for committed content in
that case. Built-in line-ending normalization remains enabled; raw bytes never
stand in for a required executable conversion.
PR-base discovery uses trusted external Git and a scoped GitHub CLI environment,
preserving external authentication/configuration and proxy settings while excluding
inherited Git routing, `GH_REPO` redirection, and checkout-owned executables.
A differently named `AUTOREVIEW_GIT` override that cannot also be selected as `git`
by the child requires an explicit `--base`; rejected GitHub configuration paths
also require one.

## Context and severity

Use `--prompt` for task-specific guidance, or `--prompt-file` and `--dataset` for
repository-relative context files. Context does not expand the selected Git target.
The reviewer cannot read unchanged repository files from its empty sandbox; supply
source or dependency evidence when the diff is insufficient.
`--prompt-file` also accepts an absolute path inside the repository; the same
sensitive-path, symlink, and mutation checks apply. `--dataset` stays repo-relative.

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
Review bundles leave the machine for the selected provider. Require authorization from the
active task or a trusted host policy before sending the selected diff, files, and context;
the portable skill does not grant that disclosure by itself. Once authorized, do not ask
again. Authorization to review does not authorize applying findings or any other mutation.
Secret scanning still gates every pack; it does not classify business confidentiality.

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
reviewed repository. When using `--status-output`, all output paths must differ;
case-only and Unicode normalization aliases are refused on every platform.

Treat `scoped-clean` as clean only for the selected target and requested priority.
`filtered` is not clean; resolve `incomplete` before claiming completion.
Verify findings against the actual code and task before changing anything.
No extra review rounds for a nicer verdict; follow the owning workflow after fixes.

**Exit codes and the `--status-output` sidecar**: see
[references/status-output.md](references/status-output.md).

Report material findings and status plainly. Do not add transcripts, proof
ledgers, commits, pushes, or a new workstream unless requested.

## Provenance and maintenance

Adapted from [OpenClaw Autoreview at revision `711711b8`](https://github.com/openclaw/agent-skills/tree/711711b86294673feced9d1cb636b539daf3c218/skills/autoreview), except the
scanner removal (upstream #240, #244): this adaptation keeps TruffleHog scanning of every outgoing pack.
Copyright (c) 2026 openclaw; distributed under the [MIT License](LICENSE).
This adaptation changes the default Codex model and per-attempt reasoning, retains the
access-only retry policy, and adds portable maintenance and release verification.
See [README.md](README.md) for testing, installation, and upstream update boundaries.
