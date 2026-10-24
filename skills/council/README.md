# Council

Council is an attributed adaptation of [Kitze's Council](https://github.com/kitze/council), pinned at `1a3c7c303fd4ee671d7c4e2fabfd43d213aba115` (the upstream SKILL content is from `7b6976c1c09b4c10ea53aadf22150f2abaf7118d`). It keeps the useful lead → independent replies → revision protocol while tightening the execution and evidence boundaries.

## What it does

Ask for `council`, `second opinion`, or `N turns of deliberation` before a plan. The lead writes an honest plan, invokes each supported available member once per round, and revises for exactly the requested number of rounds (default one, maximum ten). Members never see each other's replies; after round one they see only the lead's changes and their own previous reply. The final response contains the conversation summary, objections and failures, and the final plan.

Council is advisory. It is not an accuracy guarantee, a test suite, an independent verifier, or a security/deploy gate. `mneves-expert-review` provides one combined challenge; `mneves-fable-orchestrator` routes ordinary delegation; neither is required for Council to work.

## Requirements and safety

- Bash and at least one authenticated supported CLI: Claude, Codex, or Cursor. Each binary and every required flag is checked at runtime. Other CLIs are skipped and reported; no sibling skill is required.
- Provider and repository-content disclosure must be authorized. Never put secrets, credentials, hidden context, or sensitive records in a council prompt or transcript. Use a sanitized prompt-only brief or stop.
- Session artifacts go in a private, user-approved location, conventionally `~/.council/`, with owner-only permissions. Outside-repository writes follow the host's approval rules.
- The active adapters use Claude restricted read/search tools, Codex's read-only sandbox with approvals disabled and ephemeral output, and Cursor's sandboxed Plan Mode without trust bypass or force flags. Gemini is not an active adapter because its official headless Plan Mode documentation says exiting the mode switches to YOLO. Grok and OpenCode are not enabled without a separately verified read-only configuration.
- Prompt size, rounds, and per-member runtime are bounded. A process supervisor must clean up each member's whole process group on timeout; missing supervision is a recorded unavailable member, not a reason to leave jobs running.

The upstream README's broad “all members are read-only” statement is deliberately not repeated. Current official references used for the adaptation include [Claude headless mode](https://code.claude.com/docs/en/headless), [Claude permissions](https://code.claude.com/docs/en/permissions), [Codex CLI reference](https://developers.openai.com/codex/cli/reference), [Cursor CLI help](https://cursor.com/docs/cli), and [Gemini Plan Mode](https://geminicli.com/docs/cli/plan-mode/).

## Example

```text
council, 2 turns: should we migrate this app from Express to Hono?
Do not implement; return the objections and the final plan.
```

If no supported member is available, Council returns a clearly marked solo, un-counciled plan. It never fabricates a council or converts a timeout into approval.

## Provenance and local changes

Copyright (c) 2026 Kitze. Distributed under the [MIT License](LICENSE).

Local changes are the concise metadata, privacy and host-authorization rules, private collision-resistant sessions, bounded prompts/rounds and supervised cleanup, capability-checked Claude/Codex/Cursor adapters, explicit unsupported-member behavior, and non-verification language. The independent-round and faithful-objection protocol remains the upstream idea.

## Verification

The package is Markdown-only. Validate its Agent Skills metadata and discovery with the repository's normal checks. Exercise the protocol with fake CLIs for parallel replies, own-history isolation, failure handling, and solo fallback; inspect real CLI `--help` for active flags. These checks do not prove provider behavior, independence of model weights, or safety of arbitrary repository content.
