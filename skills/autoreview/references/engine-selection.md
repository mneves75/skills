# Engine and model selection

Override precedence and per-engine prerequisites.

## Overrides and precedence

Use `--engine`, `--model`, and `--thinking` to override the defaults.
`--codex-speed fast` selects priority service when supported. Only Claude accepts
`--fallback-model`. Per-engine environment overrides use `AUTOREVIEW_<ENGINE>_*`.
CLI options override environment settings, which override built-in defaults.
An explicitly selected model other than the default has no automatic Codex fallback.
Check the startup engine/model/thinking lines; shell configuration may override defaults.

## Defaults and fallback

Codex is the default engine. The helper owns the default model and reasoning tier and
prints them at startup; run `--help` for the current values rather than assuming them.
An account-access failure retries once on the configured fallback; a primary reasoning
override leaves that fallback untouched.

## Optional engine prerequisites

| Optional engine | Prerequisites                                                                                         |
| --------------- | ----------------------------------------------------------------------------------------------------- |
| Claude          | Recent CLI; safe mode with web-only tools                                                             |
| Amp             | `AMP_API_KEY` for a plugin-free account; local POSIX execution, no custom endpoint or cloud/orb agent |
| Pi              | Recent CLI; configured model; no tools or project resources                                           |
| Kimi            | Recent CLI; configured model; Python 3.11+ or `tomli` for TOML config                                 |
