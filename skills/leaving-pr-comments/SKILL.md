---
name: leaving-pr-comments
description: Format and attribute GitHub comments an agent posts for the user. Use whenever leaving comments on GitHub.
license: MIT
---

# Leaving PR Comments

Prefix every agent-authored comment left on the user's behalf with this GitHub
note callout:

```md
> [!NOTE]
> 🤖 **<model> responding on behalf of <user>**

Actual comment starts here.
```

Use the verified public name of the model that wrote the comment, and the
user's name or GitHub login.

If the harness does not expose a model name, use the harness name. Do not guess.

Before posting, check the entire comment, including quoted text and
attachments, for secrets and private details.

Keep the attribution inside the note and the actual reply outside it. The
context line must start with the robot emoji. Do not add a horizontal rule,
Setext underline, heading, signature footer, or a second attribution.

Apply this format to top-level PR comments, inline review comments, replies to
bots or reviewers, and written explanations used before resolving or
dismissing feedback. Do not add it to PR descriptions, commit messages, or text
the user explicitly asked to post verbatim without attribution.

Write the comment itself in a direct style:

- Lead with the conclusion.
- Cite the relevant code, behavior, check, or reproduction.
- Keep it concise and avoid filler, canned thanks, or status narration.
- Distinguish verified facts from judgment.
- Claim only checks and proof you observed in this session; name what you did not run.

Preview the final Markdown before posting so quoting and blank lines render as
shown. After posting, verify that GitHub returned the comment or review URL.
Resolve a review thread only after its response was posted successfully.

## Provenance

Adapted from [tstack `leaving-pr-comments` at revision `1085050f`](https://github.com/t3dotgg/tstack/tree/1085050f3baed1ac724caa4a8166145fb2ac88af/skills/leaving-pr-comments).
Copyright (c) 2026 Theo Browne; distributed under the [MIT License](LICENSE). Local changes: Agent Skills metadata, and the rule that a comment never claims a check or proof the agent did not observe.
