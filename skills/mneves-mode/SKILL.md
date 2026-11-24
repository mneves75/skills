---
name: mneves-mode
description: Explicit workflow router (/mneves-mode or "use mneves mode") that picks a playbook and redirects each phase to the right sibling skill with standalone fallbacks. Explicit invocation only.
license: Apache-2.0
---

# mneves-mode

Explicit workflow entrypoint for `mneves75/skills`. Use only when the user invokes `/mneves-mode`,
`$mneves-mode`, or explicitly asks for "mneves mode" or "the mneves-mode skill". Never auto-trigger
on ordinary prompts: every standalone skill in this collection remains directly discoverable on its
own.

## 1. Frame the task

Before touching files or routing a specialist:

1. Restate the user's goal and the smallest correct, verifiable change that meets it.
2. Classify the **phase** (plan/decide, build/refactor, review/audit, PR lifecycle, release/deploy)
   and **risk tier**:
   - **Standard:** reversible in-repo work.
   - **Risky:** any release or deploy, security/privacy boundary, permissions or secrets, production
     or client data, money, legal terms, or a contested result.
3. Preserve explicit scope, format, language, and review-only boundaries. Invoking `/mneves-mode`
   grants no permissions: review-only requests stay read-only, and mandatory gates stay closed.

## 2. Check installed siblings before redirecting

Sibling skills in a full install live beside this folder at `../<name>/SKILL.md` (or in the host's
active skill catalog). A single-skill install ships only this folder.

- **Installed sibling:** read its `SKILL.md` and follow its procedure for that phase; state the
  routed skill and reason once.
- **Missing sibling:** say so once and follow the standalone fallback in
  [`references/playbooks.md`](references/playbooks.md). Never imply an unavailable skill ran.
- **Closed mandatory gates:** if a required independent review, security gate, or readiness gate
  cannot run, mark that gate `BLOCKED` and continue only non-dependent work. Never count
  self-review, passing tests, or CI as an independent verdict.

## 3. Redirect table

Pick the most specific sibling for the current phase. Reassess whenever the goal or phase changes
(for example, implementation -> review -> verification -> release). Keep the same route for small
follow-ups within the same phase.

| Situation / Phase | Sibling skill | Boundary & standalone rule |
|---|---|---|
| Stress-test a high-stakes plan, memo, or decision | `mneves-expert-review` | Not for code diffs; verify every linked source |
| Multi-CLI plan deliberation or scored second opinion | `council` | Advisory only; never substitutes for tests or verification |
| Assess why coding agents struggle in a repository | `mneves-agent-readiness` | Developer/agent DX, not production launch readiness |
| Audit ChatGPT Search discovery, crawlers, or citations | `mneves-chatgpt-search` | Separate search, training, citations, and referrals |
| Split non-trivial work across agents or lanes | `mneves-fable-orchestrator` | Owns model defaults; keep framing and acceptance in main session |
| Diagnose coupling or refactor a named code area | `untangle-codebase` | Diagnosis first; explicit authorization needed to edit; never expand scope |
| Build HTML/DOCX/PDF exports from Markdown | `mneves-render` | Project-local Pandoc/WeasyPrint starter pipeline |
| Produce or update a short product launch film | `mneves-motion-film` | Checked product facts, Remotion render, scripted QA |
| Generate mobile app UI screen/flow concepts | `imagegen-frontend-mobile` | Concept images only, never application code |
| Learn a codebase via teach-back + spaced repetition | `mneves-teach-back-srs` | Local SQLite SM-2 scheduling; skip for one-off lookups |
| Independent AI code review of a fixed Git target | `autoreview` | Include adversarial challenge and local `cccc` when available |
| Deep read-only six-phase source security audit | `security-audit` | Strictly read-only with Node validators; never a deploy gate |
| Independent PASS/FAIL/BLOCKED check before "done" | `mneves-verify` | Fresh context; separates product vs verification edits |
| Watch a PR through CI and review bots | `babysit-pr` | Fixes real findings; never merges or force-pushes |
| Rebase an aging PR and decide keep vs close | `modernize` | Assesses base-branch relevance before rebasing |
| Finish someone else's PR, branch, or thread | `takeover` | Keeps original author credit; never merges |
| Format agent-authored GitHub PR comments | `leaving-pr-comments` | Applies only when posting GitHub comments for the user |
| Unattended change to a proven, ready PR | `full-stop` | Explicit invocation by name only; never merges |
| Hand off context to another agent session | `mneves-handoff` | Portable, path-free, review-first continuation prompt |
| Security audit, safe fixes, or pre-deploy security gate | `mneves-security` | Mandatory exact-commit gate before every staging/prod deploy |
| Operational launch or deployment readiness gate | `mneves-production-readiness` | Imports security rows from `mneves-security`; never re-audits them |
| Deploy pushed commit, prove live, then tag | `mneves-ship-deploy` | Explicit `ship-staging` / `ship-prod` only; plain "ship" does not deploy |

**Optional sibling collection (`pstack`, if installed):** for deep code walkthroughs (`how`),
design rationale (`why`), interface sketching before cross-boundary code (`architect`), parallel
competing implementations (`arena`), adversarial multi-model diff interrogation (`interrogate`),
test-first bug fixes (`tdd`), vocabulary reframing (`reframe`), prompt deepening (`sharpen`), or
post-task skill reflection (`reflect`), route to those skills when present. Never require them;
fall back to direct work or the root equivalents above.

## 4. Playbooks

Match the request to one playbook in [`references/playbooks.md`](references/playbooks.md) and
execute its steps in order:

1. **Feature or bug fix** — frame -> build/test (or delegate) -> adversarial review -> fresh verification.
2. **Scoped refactor** — baseline -> diagnosis & plan -> bounded edits -> regression + review + verification.
3. **High-stakes decision or plan** — frame -> stress-test / deliberate -> prototype reversible forks -> decide.
4. **PR lifecycle** — pick `babysit-pr`, `modernize`, `takeover`, or explicit `full-stop` -> attribute comments -> stop at merge gate.
5. **Release and production deploy** — exact-commit `mneves-security` -> `mneves-production-readiness` -> `mneves-ship-deploy` -> prove live -> tag.
6. **Audit or independent verification** — read-only evidence collection -> fresh-context verdict -> prioritized findings.
7. **Specialized artifacts & learning** — route to `mneves-render`, `mneves-motion-film`, `imagegen-frontend-mobile`, or `mneves-teach-back-srs` with explicit single-skill fallbacks.

## 5. Cross-cutting rules

- **Local autonomy, hard stops:** reversible in-repo work (reading, searching, editing, tests,
  builds, linters, commits on a working branch) proceeds without asking. Always stop before:
  deleting unowned files or data; force-pushing or rewriting history; merging, tagging, releasing,
  deploying to production, or submitting to app stores; out-of-repo or cloud mutations; handling
  unnamed credentials or secrets; opening client/personal records; external messages or purchases;
  or materially expanding scope. "Run until done" never crosses this line.
- **Prototype reversible forks:** when a reversible technical choice inside scope can be settled by
  a small local test or measurement, run it and decide from observed output rather than guessing.
- **No duplicated model IDs:** keep model names and reasoning tiers out of this skill; defer
  model selection to `mneves-fable-orchestrator` (when installed) or the user's host configuration.
- **Honest closure:** lead with the outcome, state commands run with exact results, separate facts
  from assumptions and unknowns, list anything unverified or blocked, and never claim completion on
  a failing or skipped gate.
