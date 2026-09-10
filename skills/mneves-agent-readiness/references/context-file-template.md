# Context file template

Open when the assessment finds the context-file pillar weak. Works as `CLAUDE.md`,
`AGENTS.md`, or `.cursorrules`.

```markdown
# Project Context

## Overview
[1-2 sentences: what this does and WHY]

## Commands
- Build: `bun run build`
- Test: `bun test`
- Lint: `bun run lint`

## Architecture
[Brief description of key directories]

## Key Decisions
- [Decision]: [Why]
```

**Requirements**: concise (under 300 lines), and every command in it still runs. The commands
are the part that decays — a context file whose build command no longer works is worse than no
context file, because the agent trusts it.

Scope note: put a rule in exactly one file. A rule copied into the global, workspace, and
repository context files will drift, and the agent cannot tell which copy is current.
