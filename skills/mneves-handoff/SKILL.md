---
name: mneves-handoff
description: Write a clipboard-ready prompt that hands a task to another agent for review and discussion. Use for "handoff <task>" or "write a handoff".
license: MIT
---

# Handoff

Write a standalone prompt that lets a fresh agent investigate, discuss, or continue a task. The
receiving agent owns its own review; the handoff gives it starting context and known constraints,
not a finished decision.

This is not a delegation brief. A brief sends a worker into your own tree with exact paths and
proof commands; a handoff goes to an agent you do not control, in a directory you do not know,
that should first decide whether the task is worth doing.

## Workflow

1. Identify the task. From a short label, infer the rest from the current repository, recent
   discussion, branch name, linked issue or PR, and nearby docs.
2. Gather enough to orient a stranger: repository and product identity, relevant issue, PR, and
   branch names, likely modules, constraints, and known symptoms. Do not do the receiving
   agent's review or settle the technical direction for it.
3. Write the prompt with the template below.
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

## Template

```text
I want to discuss and possibly work on: <short task title>

Context:
- <portable repository/product context>
- <what triggered this task>
- <known current state: branch, issue, or PR names or URLs>
- <important constraints and ownership boundaries>

Before any implementation:
- Find the right repository from the current directory, a parent, or the usual workspace.
- Read the repository's agent instructions.
- Inspect the relevant code, docs, tests, recent commits, and linked issue/PR state.
- Decide whether this task is still real, whether the proposed direction is a good idea, and
  whether a smaller or better fix exists.
- Call out stale assumptions, hidden risks, and anything that should stop the work.

Task:
- <what to investigate or implement if the review supports it>
- <expected behavior or decision criteria>
- <non-goals>

Validation:
- <focused tests, checks, or live proof expected>
- <what evidence to include>
- <what is explicitly not required>

Output:
- Start with your review findings and recommendation.
- Then give the proposed plan or patch summary.
- If you edit code, keep changes scoped and report the exact proof you ran.
- Do not push, merge, close issues/PRs, label, or post public comments unless told to.
```

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
