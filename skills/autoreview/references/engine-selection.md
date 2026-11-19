# Engine and model selection

Override precedence and per-engine prerequisites.

## Overrides and precedence

Use `--engine`, `--model`, and `--thinking` to override the defaults.
`--codex-speed fast` selects priority service when supported. Only Claude accepts
`--fallback-model`; one effort covers the Claude chain, `--help` names its default, and a
chain that mixes models with different default efforts needs an explicit `--thinking claude=<level>`.
Per-engine environment overrides use `AUTOREVIEW_<ENGINE>_*`.
CLI options override environment settings, which override built-in defaults.
An explicitly selected model other than the default has no automatic Codex fallback.
Check the startup engine/model/thinking lines; shell configuration may override defaults.
Reasoning levels are validated per model before preparation; an explicitly selected model
may reject some levels (`--help` lists them), and a model other than the default never falls back.
For GPT-6.2 Codex routes, use `low` when migrating an explicit `none` or `minimal`
setting. Use `ultra` only with a client and route that advertise it. The OpenAI guide's
`medium` starting point applies to new API integrations. Autoreview has its own default
for its established CLI review workflow.
[OpenAI model migration guide](https://developers.openai.com/api/docs/guides/latest-model#migration-quickstart) ·
[Codex configuration reference](https://developers.openai.com/codex/config-reference/)

## Defaults and fallback

Codex is the default engine. The helper owns the default model and reasoning tier and
prints them at startup; run `--help` for the current values rather than assuming them.
Codex review has no automatic model fallback. Account-access failures are reported without
switching to an advisory or planning model. Explicit caller overrides remain authoritative,
including a caller that substitutes another reviewer under its own recorded policy.

## Optional engine prerequisites

| Optional engine | Prerequisites                                                                                         |
| --------------- | ----------------------------------------------------------------------------------------------------- |
| Claude          | Recent CLI; safe mode with web-only tools                                                             |
| Amp             | `AMP_API_KEY` for a plugin-free account; local POSIX execution, no custom endpoint or cloud/orb agent |
| Pi              | Recent CLI; configured model; no tools or project resources                                           |
| Kimi            | Recent CLI; configured model; Python 3.11+ or `tomli` for TOML config; `--allow-kimi-argv-prompt`     |
| Agy             | Antigravity CLI >= 1.5.12 (`agy` authenticated); default `gemini-4-neon-xhigh`; web search always on  |

Kimi Code takes a one-shot prompt only as a command-line argument, and other local accounts can
read a process's arguments while it runs. `--engine kimi` therefore refuses to start unless the run
passes `--allow-kimi-argv-prompt`. Pass that flag only on a machine whose other accounts may see
the review pack; otherwise choose another engine.

`--engine agy` sends the review prompt over stdin NDJSON (`--input-format stream-json
--output-format stream-json`), runs in an empty temporary workspace with an isolated `HOME`
(staging only auth material — macOS Keychains link, file OAuth token, `GEMINI_API_KEY`, or
`AGY_ADC_AUTH` / ADC credentials — so global/plugin hooks, plugins, user MCP servers, and global
rules are never discovered), passes `--disable-slash-commands`, `--sandbox`, and session-only
`--settings` enforcing `toolPermission: "strict"`, `allowNonWorkspaceAccess: false`,
`enableTerminalSandbox: true`, and explicit deny rules for `command(*)`, `write_file(*)`,
`read_file(*)`, `read_url(*)`, `mcp(*)`, and `unsandboxed(*)`, and verifies
`permission_mode == "strict"` plus tool events in the stream before accepting structured output.
Because Antigravity CLI's built-in `search_web` cannot be disabled up front, `--engine agy`
rejects `--no-tools` and `--no-web-search`.
