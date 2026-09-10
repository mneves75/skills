# Autoreview

A portable AI code-review helper. It freezes a Git target, scans outgoing inputs for
credentials, invokes an isolated reviewer, validates its JSON report, and detects source
changes before accepting the result. It does not apply fixes or publish code.

## Install and run

```sh
npx skills@latest add mneves75/skills --skill autoreview
```

Install Python 3.11+, Git, [TruffleHog](https://github.com/trufflesecurity/trufflehog),
and an engine supported by [SKILL.md](SKILL.md). Authenticate the engine separately.
The Python helper uses the standard library. Keep this entire directory together.
Run the helper from the repository you want reviewed:

```sh
python3 /path/to/autoreview/scripts/autoreview --mode local --max-priority P3
```

The helper owns the default model and reasoning tier and prints them at startup; `--help`
reports the current values. A confirmed account-access failure retries once on the fallback. Rate limits, capacity failures, scanner refusals,
and invalid reports do not trigger that fallback. A custom primary model disables it.
`--model` and `--thinking` override environment settings; environment settings override
the defaults. The fallback effort remains `xhigh` when primary effort is overridden.
The built-in severity threshold remains P0; pass P3 for a review including lower priorities.

Inputs are sent to the selected provider. Scanning credentials does not make private business
data public; review only code you are authorized to send. An AI verdict is evidence to inspect,
not a security guarantee. `--dry-run` checks preparation without contacting a reviewer.

## Test

```sh
python3 scripts/run-tests.py
```

The runner isolates operator home and Git configuration so global ignore rules cannot hide
synthetic credential fixtures. Tests use fake engines and scanners; the macOS sandbox test
uses the installed Codex CLI to execute a local shell with positive and negative controls.
It needs ordinary OS permission to create temporary fixtures and launch a nested sandbox.
Unsupported platform/tool checks are reported as skipped, not as passed.

## Beta installation

A beta is an immutable `vX.Y.Z-betaN` Git tag and GitHub prerelease. Download its source
archive, keep `skills/autoreview` together, and run the tests before linking or copying it
into your agent's skill directory. Use the release's tag or commit when comparing updates.
The documentation site is a catalog, not a hosted review service. No server deployment or
TestFlight submission is needed to use this CLI skill.

## Upstream and maintenance

Source: [openclaw/agent-skills at `3e9f33968ac732aa2fa7873e9dfc5823b5216c49`](https://github.com/openclaw/agent-skills/tree/3e9f33968ac732aa2fa7873e9dfc5823b5216c49/skills/autoreview).
Copyright (c) 2026 openclaw. The [MIT License](LICENSE) covers the upstream work and
this adaptation. Changes are recorded in the collection's
[changelog](https://github.com/mneves75/skills/blob/main/CHANGELOG.md).

Keep upstream isolation, credential scanning, report validation, and complete-input checks
when importing fixes. Compare against the pinned revision, preserve the local model policy,
and run the complete suite. Updates require a reviewed release; installation never fetches
or executes a moving upstream checkout.
