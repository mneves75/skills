# Engine and model selection

Override precedence and per-engine prerequisites.

## Overrides and precedence

Use `--engine`, `--model`, and `--thinking` to override the defaults.
`--codex-speed fast` selects priority service when supported. Only Claude accepts
`--fallback-model`; one effort covers the Claude chain, so an Opus chain defaults to medium
and a chain that mixes Opus with other models needs `--thinking claude=<level>`.
Per-engine environment overrides use `AUTOREVIEW_<ENGINE>_*`.
CLI options override environment settings, which override built-in defaults.
An explicitly selected model other than the default has no automatic Codex fallback.
Check the startup engine/model/thinking lines; shell configuration may override defaults.
Reasoning levels are validated per model before preparation; an explicitly selected model
may reject some levels (`--help` lists them), and a model other than the default never falls back.

## Defaults and fallback

Codex is the default engine. The helper owns the default model and reasoning tier and
prints them at startup; run `--help` for the current values rather than assuming them.
Codex review has no automatic model fallback. Account-access failures are reported without
switching to an advisory or planning model. Explicit caller overrides remain authoritative.

## Optional engine prerequisites

| Optional engine | Prerequisites                                                                                         |
| --------------- | ----------------------------------------------------------------------------------------------------- |
| Claude          | Recent CLI; safe mode with web-only tools                                                             |
| Amp             | `AMP_API_KEY` for a plugin-free account; local POSIX execution, no custom endpoint or cloud/orb agent |
| Pi              | Recent CLI; configured model; no tools or project resources                                           |
| Kimi            | Recent CLI; configured model; Python 3.11+ or `tomli` for TOML config; `--allow-kimi-argv-prompt`     |

Kimi Code takes a one-shot prompt only as a command-line argument, and other local accounts
can read a process's arguments while it runs. `--engine kimi` therefore refuses to start,
before any Kimi process, unless the run passes `--allow-kimi-argv-prompt`. Pass it only on a
machine whose other accounts may see the review pack; otherwise choose another engine.
