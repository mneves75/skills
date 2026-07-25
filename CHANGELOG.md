# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-07-24

### Changed

- **BREAKING** — all skills now carry the `mneves-` prefix: `agent-readiness` → `mneves-agent-readiness`, `fable-orchestrator` → `mneves-fable-orchestrator`, `teach-back-srs` → `mneves-teach-back-srs`. Directory name and frontmatter `name:` match. Re-link installs: `ln -s <repo>/skills/mneves-<skill> ~/.claude/skills/mneves-<skill>`.
- Fable Orchestrator routes heavy implementation to GPT-5.6-sol at reasoning `high` (was GPT-5.5 at `xhigh`).

## [1.2.0] - 2026-07-08

### Added

- **Fable Orchestrator Skill** - Model-routing policy for multi-agent Claude Code sessions
  - Fable (main session) as advisor: repo understanding, architecture decisions, task decomposition, spec writing, final review
  - Opus subagents as frontend executors (components, styling, layout)
  - Codex (GPT-5.5 xhigh via `/codex:rescue`) as heavy executor (implementation, debugging, test fixing, multi-file refactors)
  - `supergoal` + `/goal` for long-horizon, multi-phase work
  - Delegation contract (goal, paths, constraints, proof, output shape) and mandatory Fable-side verification of all delegated output
  - Codex invocation patterns adapted from [steipete/agent-scripts — codex-first](https://github.com/steipete/agent-scripts/blob/main/skills/codex-first/SKILL.md)

## [1.1.0] - 2026-02-01

### Added

- **Teach-Back SRS Skill** - Spaced-repetition learning through codebase teach-back sessions
  - Teach-back mode: explain your understanding, Claude cross-references code and probes gaps
  - Socratic follow-ups with specific file:line references for misconception correction
  - SM-2 algorithm (SuperMemo 2) for optimal review scheduling
  - Per-project SQLite database (`.ai-learn/srs.db`, auto-gitignored)
  - Review mode with self-rated recall (quality 0-5)
  - Stats dashboard: mastered, struggling, due, upcoming cards
  - Export to Markdown or Anki-compatible CSV
  - Cross-session continuity via persistent SQLite state
  - Card generation guidelines: one concept per card, why > what, context-anchored
  - Python 3.10+ stdlib only, no external dependencies

## [1.0.0] - 2026-01-22

### Added

- **Agent Readiness Skill** - Evaluate codebase readiness for AI agents
  - 9 technical pillars (Context, Typing, Testing, Build, Lint, CI/CD, Documentation, Observability, Security)
  - 5 maturity levels (L1 Runnable → L5 Autonomous)
  - Multi-language support (TypeScript, JavaScript, Go, Python, Rust, Java)
  - Monorepo application discovery
  - Multiple scoring modes (weighted, strict, average)
  - HTML, JSON, and Markdown output formats

- **Benchmark Reports** - Real assessments of popular open-source projects
  - FastAPI (Python) - L4, 65.4%

- **GitHub Pages** - Live HTML reports at https://mneves75.github.io/skills/

- **Tool Installation** - Support for pi, OpenCode, Claude Code, Cursor, VS Code, Codex, Windsurf, and Aider

### Notes

This project is inspired by [Factory.ai](https://factory.ai)'s Code Readiness framework.

[1.2.0]: https://github.com/mneves75/skills/releases/tag/v1.2.0
[1.1.0]: https://github.com/mneves75/skills/releases/tag/v1.1.0
[1.0.0]: https://github.com/mneves75/skills/releases/tag/v1.0.0
