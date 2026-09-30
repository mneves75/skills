---
name: mneves-handoff
description: Write a clipboard-ready discussion or continuation prompt for another agent. Use when asked for a handoff.
license: MIT
---

# Handoff

Write a standalone prompt that lets a fresh agent investigate, discuss, or continue a task. The
receiving agent owns its own review; the handoff gives it starting context and known constraints,
not a finished decision.

A handoff starts with independent assessment; a worker brief assigns implementation with exact
paths and proof commands. Preserve the user's chosen mode and already-granted authority.

## Workflow

1. Identify the task. From a short label, infer the rest from the current repository, recent
   discussion, branch name, linked issue or PR, and nearby docs.
2. Gather enough to orient a stranger: repository and product identity, relevant issue, PR, and
   branch names, likely modules, constraints, and known symptoms. Use checked summaries and
   portable evidence anchors instead of pasting transcripts or redoing the receiving review.
3. Write Task, Acceptance, Constraints, Delivery, and Target. For the discussion-first template,
   read [references/discussion-template.md](references/discussion-template.md).
4. Copy it to the clipboard (see Clipboard).
5. Reply with a one-line confirmation naming the task. Do not paste the prompt unless asked.

## Prompt rules

- Open a discussion, not a work order: the first real instruction is to review and assess.
- Ask for an independent review before any change, including whether the task is still real,
  stale, already solved, over-scoped, or better done another way.
- Assume the agent starts in the repository, a parent directory, a workspace, or its home
  directory, and can find the repository itself.
- No filesystem paths (absolute, home-relative, checkout names, or repository-relative) unless
  the user asks for them. Use portable anchors instead: repository owner/name, product and module
  names, issue and PR URLs, branch names, package names, public symbols, commands, config keys,
  exact error text, doc titles, and search terms.
- Include constraints, non-goals, validation expectations, and the output shape wanted.
- Tell the agent to re-check live repository, issue, and CI state where it matters.
- Tell the agent not to push, merge, close or label issues and PRs, or post public comments
  unless the handoff explicitly asks for it.
- No invented facts; state as checked only what you checked. No brain dump: enough to orient.

## Clipboard

Write the prompt to a private temporary file, then copy from it; never pass prompt text through
inline shell quoting, since it may contain backticks, `$`, or quotes:

```sh
f="$(mktemp)"   # write the prompt into "$f" with your file tool, then:
pbcopy < "$f"   # macOS; elsewhere wl-copy, xclip -selection clipboard, or clip.exe
rm -f "$f"
```

Without a clipboard tool, print the prompt and say the copy was unavailable.

## Provenance

Adapted from [OpenClaw Agent Skills `handoff` at revision `711711b8`](https://github.com/openclaw/agent-skills/tree/711711b86294673feced9d1cb636b539daf3c218/skills/handoff).
Copyright (c) 2026 openclaw; distributed under the [MIT License](LICENSE). Local changes: the
`mneves-` prefix (the upstream name collides with another widely installed `handoff` skill), the
brief-versus-handoff distinction, a private temporary file for the clipboard step, and condensed
rules.
