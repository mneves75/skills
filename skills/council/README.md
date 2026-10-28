# Council

Council is an attributed adaptation of [Kitze's Council](https://github.com/kitze/council), pinned at `1a3c7c303fd4ee671d7c4e2fabfd43d213aba115` (the upstream SKILL content is from `7b6976c1c09b4c10ea53aadf22150f2abaf7118d`). It keeps the useful lead → independent replies → revision protocol while tightening the execution and evidence boundaries.

## What it does

Ask for `council`, `second opinion`, or `N turns of deliberation` before a plan. The lead writes an honest plan, invokes each supported available member once per round, and revises for exactly the requested number of rounds (default one, maximum ten). Members are never shown another member's reply; after round one they see only the lead's changes and their own previous reply. The final response contains the conversation summary, objections and failures, and the final plan.

Ask the council to *review* a change (a diff, a branch or a PR) and it runs review mode instead: members review the current implementation independently and score it out of 10 each round, the lead fixes what it agrees with between rounds, and the run stops when every member answers SHIP IT or the round cap (default three, maximum ten) ends. The score table goes into the PR description, or the final reply without a PR. Reaching the cap is not approval.

Council is advisory. It is not an accuracy guarantee, a test suite, an independent verifier, or a security/deploy gate. `mneves-expert-review` provides one combined challenge; `mneves-fable-orchestrator` routes ordinary delegation; neither is required for Council to work.

## Requirements and safety

- Bash and at least one authenticated supported CLI: Claude, Codex, or pi. Each binary and every required flag is checked at runtime. Other CLIs are skipped and reported; no sibling skill is required.
- Provider and repository-content disclosure must be authorized. Never put secrets, credentials, hidden context, or sensitive records in a council prompt or transcript. Use a sanitized prompt-only brief or stop.
- Session artifacts go in a private, user-approved location, conventionally `~/.council/`, outside the project and every member working directory, with owner-only permissions. Outside-repository writes follow the host's approval rules.
- Independence is a protocol obligation, not an operating-system boundary. Claude's restricted mode confines its file tools to the working directories; Codex's read-only sandbox and pi's read-only tool allowlist scope writes, not reads, so those two can open anything the running user can. What the run controls is what members are given — never another member's reply and never the session path — so a member that goes looking for one breaks the protocol in a way these flags cannot prevent.
- The active adapters use Claude restricted read/search tools, Codex's read-only sandbox with approvals disabled and ephemeral output, and pi in print mode with only its read, grep, find and ls tools, no context files, extensions, skills, MCP or project-local resources, and no saved session. pi can run a provider the other two do not, which is how a council reaches three providers. Cursor was the third adapter until 1.43.0: its read-only Plan Mode is only the mode a run starts in, it loads the workspace's rules with no flag to stop that, and its prompt travelled in the argument vector. Gemini is not an active adapter because its official headless Plan Mode documentation says exiting the mode switches to YOLO. Grok and OpenCode are not enabled without a separately verified read-only configuration.
- Prompt size, rounds, and per-member runtime are bounded. A process supervisor must clean up each member's whole process group on timeout; missing supervision is a recorded unavailable member, not a reason to leave jobs running.

The upstream README's broad “all members are read-only” statement is deliberately not repeated: read-only means no writes, not a read boundary. Current official references used for the adaptation include [Claude headless mode](https://code.claude.com/docs/en/headless), [Claude permissions](https://code.claude.com/docs/en/permissions), [Codex CLI reference](https://developers.openai.com/codex/cli/reference), the pi CLI's own `--help` (version 1.4.0, where a headless run with the read-only allowlist answered from its prompt and could not create a file, while the same prompt without the allowlist did), and [Gemini Plan Mode](https://geminicli.com/docs/cli/plan-mode/).

## Example

```text
council, 2 turns: should we migrate this app from Express to Hono?
Do not implement; return the objections and the final plan.
```

If no supported member is available, Council returns a clearly marked solo, un-counciled plan. It never fabricates a council or converts a timeout into approval.

## Provenance and local changes

Copyright (c) 2026 Kitze. Distributed under the [MIT License](LICENSE).

Local changes are the concise metadata, privacy and host-authorization rules, private collision-resistant sessions, bounded prompts/rounds and supervised cleanup, capability-checked Claude/Codex/pi adapters (including the flags that keep a reviewed repository's own instructions from loading), explicit unsupported-member behavior, per-adapter read-scope wording instead of an isolation claim, and non-verification language. The independent-round and faithful-objection protocol remains the upstream idea. Review mode with per-round scores is adapted from [tstack's `council`](https://github.com/t3dotgg/tstack/tree/1085050f3baed1ac724caa4a8166145fb2ac88af/skills/council) at revision `1085050f`, Copyright (c) 2026 Theo Browne, MIT; it is bounded by the round cap instead of looping until every member is satisfied.

## Verification

The package is Markdown-only. Validate its Agent Skills metadata and discovery with the repository's normal checks. Exercise the protocol with fake CLIs for parallel replies, own-history isolation, failure handling, and solo fallback; inspect real CLI `--help` for active flags. These checks do not prove provider behavior, independence of model weights, or safety of arbitrary repository content.
