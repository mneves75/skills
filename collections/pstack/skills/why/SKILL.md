---
name: why
description: "Use for 'why does X work this way', 'why we picked Y', design rationale, regressions, postmortems, or data-backed thresholds. Starts from source control and adds the available evidence categories (issue tracker, long-form docs, real-time chat, infrastructure observability, error tracking, product analytics warehouse) that bear on the question, read-only and in parallel, then returns a cited read on decisions and tradeoffs with explicit unknowns. Use how for runtime behavior."
---

# Why

On Codex, read the [platform mapping](../poteto-mode/references/codex-tools.md), including its per-skill notes, before following this skill.

On GitHub Copilot, read the [platform mapping](../poteto-mode/references/copilot-tools.md), including its per-skill notes, before following this skill.

Investigate the motivation and intent behind code. The companion `how` skill answers what the code does and how it works. `why` answers what forces led to its shape.

Each spawn below names a role line in `pstack-models.md` and a default in [Models](#models). Set `model` to that line's value, or to the default if the sheet or the line is missing. Leave `model` unset when the value is `auto` or `inherit-parent`. If the `Agent` tool rejects a slug, use the default and say so. If it rejects the default, use the closest valid slug of the same family from its error message.

Every spawn is `general-purpose` with `readonly: true`. Investigators and the synthesizer only search and read: they never write files, post, comment, or change tickets, documents, dashboards or settings. If the host's read-only mode leaves a category's MCP unreachable, do not widen the spawn to get it: query that MCP from this session with read and search calls only, or record the category as not searched in read-only mode. A read that a host, a tool or a permission prompt denied stays denied. Record it in Sources Consulted; never retry it through a broader mode, another agent or changed permissions.

On GitHub Copilot, the platform mapping's fallback that runs a read-only role needing MCP as `general-purpose` does not apply to these spawns: keep each investigator read-only, use only the main session's permitted reads, or report the category as a coverage gap.

## Operating Posture

Operate as a **careful, cautious, and precise investigator**. Be honest about what you know vs what you're inferring. Read `references/epistemics.md` for the full confidence framework and phrasing guide. The synthesizer must follow it.

## Step 1. Understand the Target and the Question

The **target** is usually a chunk of code, a pattern, a feature, or a named design decision. The **question** is usually a design rationale, a tradeoff, a motivating edge case, an external constraint, dead code, or a broad history sweep.

If the target is vague ("why do we do it this way?" with no clear referent), make your best guess from conversation context (open files, recent edits, cursor location, what was just discussed). State your interpretation briefly so the user can redirect if you're off, then proceed.

## Step 2. Establish the Code Anchor

Before spawning investigators, build the seed context inline: file paths and line ranges, key symbols (functions, classes, constants), the last few commits touching the target, PR numbers from merge commits (pattern `(#1234)` in the subject line), and any linked ticket IDs. Run `git blame -L <start>,<end> <file>` for last-touch commits, `git log --follow -p -- <file>` for full history with patches through renames, `git log --oneline -20 -- <file>` for recent commits with PR numbers visible, and `git log -1 --format=%B <commit>` to extract PR numbers. Then pull the PR bodies and discussion for any substantive commit: `gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews`. This anchor goes to every investigator and to the synthesizer.

## Step 3. Spawn Parallel Investigators

**Size the investigation to the question.** Source control is always searched. Add a category when its evidence can bear on this question (the roster below says what each one is best at), and search a selected category fully: document the null, don't skip the search. Unselected categories are explicit unknowns, not nulls.

For a simple question, such as one commit whose PR or linked ticket states the reason, answer inline from the code anchor and skip the rest of Step 3 and Step 4: no investigators, no synthesizer. Keep the confidence language from `references/epistemics.md` and the [Output Format](#output-format), and list the categories you did not search.

### Discovery

Before spawning investigators, list the available MCPs in the Claude Code environment, to know which selected categories can be searched. Use the tool list at the top of the system prompt (every MCP appears as a tool with prefix `mcp__<server>__<name>`). Otherwise read `.mcp.json` in the plugin/project, or run `claude mcp list`.

Map each available MCP to one evidence category:

1. Source control history
2. Issue / ticket tracker
3. Long-form documents
4. Real-time team chat
5. Infrastructure observability
6. Error / exception tracking
7. Product analytics warehouse

Source control is always available through git and `gh`. For the other six, classify using the MCP name, server instructions, tool names, and resource descriptors. If an MCP could fit more than one category, choose the one matching its primary evidence. Record ambiguous cases in the coverage map.

Spawn one investigator per selected category that has a matching MCP, all in a single message so they run concurrently, each owning exactly one tool or MCP. Don't ask one agent to cover multiple MCPs. `model`: the `why investigators` line, default in [Models](#models).

Each investigator's prompt is `references/investigator-prompt.md` filled in, plus:
- the category playbook `references/sources/<source>.md` for the selected MCP, adapted from the examples in `references/source-playbook.md`
- `references/sources/incident-postmortem.md` **if the target code looks defensive** (null checks, retry logic, timeout handling, rate limiting, feature flags, egress guards, OOM handlers)
- the code anchor and the user's original question

### Investigator roster, one per selected evidence category

Each category below is uniquely positioned to surface one shape of "why", shown after "Best at". Use it to choose the categories that bear on the question, to know what to expect back, and to name a gap when a category returns empty.

1. **Source control** (git history, `gh` for PRs, code comments, tests). Always searched, the only guaranteed source. Best at *implementation-time rationale captured during review*.
2. **Issue / ticket tracker** (e.g. Linear, Jira, GitHub Issues, Plane, Shortcut MCP). Best at *the product or business forcing function*. Strongest when the why is external to engineering.
3. **Long-form documents** (e.g. Notion, Confluence, Google Docs, Coda MCP). Best at *long-form design rationale*, written out before it becomes code.
4. **Real-time team chat** (e.g. Slack, Discord, Microsoft Teams, Mattermost MCP). Best at *real-time deliberation that never reached a doc*. Especially important when the source control, ticket, and doc paper trail is thin.
5. **Infrastructure observability** (e.g. Datadog, New Relic, Honeycomb, Grafana, Splunk MCP). Best at *infrastructure and runtime reality that motivated the code*. Strongest when the target reacts to an infra signal (timeouts, retries, rate limits, circuit breakers).
6. **Error / exception tracking** (e.g. Sentry, Rollbar, Bugsnag, Airbrake MCP). Best at *the specific exceptions and error trajectories that motivated defensive or corrective code*. Strongest for catch blocks, null guards, type checks, retries, and other defenses.
7. **Product analytics warehouse** (e.g. Databricks, Snowflake, BigQuery, ClickHouse, dbt, Redshift MCP). Best at *product and data reality that shaped the code*. Strongest for flag-gated code, experiment-driven ships, data migrations, and "where did this number come from" questions.

### Categories you do not search

Every category gets one line in the final Sources Consulted, with its reason:

- **Not available.** No MCP for it in this environment. A gap, not a choice: "Real-time team chat not searched. No matching MCP available, so the conversational record was not searchable."
- **Not selected.** Its evidence does not bear on this question: "Error / exception tracking not searched. Target is a build-time script with no runtime code path."
- **Not reachable read-only, or a read was denied.** Name the denial; do not route around it.

What an unsearched category might hold stays in What We Don't Know. If the evidence you have leaves the question open, widen the search to the next most relevant category before concluding.

## Step 4. Synthesize

When you spawned investigators, spawn one synthesizer (an inline answer has none). `model`: the `why synthesizer` line, default in [Models](#models). It gets:
1. The investigator findings, including any null results, and each category not searched with its reason
2. The code anchor
3. The user's original question
4. The epistemics framework from `references/epistemics.md`
5. The synthesizer prompt template from `references/synthesizer-prompt.md`

## Step 5. Present

Present the synthesizer's output to the user. You may lightly edit for clarity or add context from the conversation, but **do not rewrite the confidence language**.

## Output Format

The structure is the one in `references/synthesizer-prompt.md`: The Question, The Code in Question, What We Found, What We Can Reasonably Infer, Competing Hypotheses, What We Don't Know, Sources Consulted, Confidence Summary. Adapt as needed, but keep the confidence separation intact, and keep Sources Consulted as one line per evidence category: searched (including the ones that returned nothing), not available, not selected, or not reachable read-only, with the reason.

After Sources Consulted, if the user's `why` question is a precursor to changing this code, convert the lineage findings into a Preserve / Change / Avoid / Risk constraint set for planning the change.

## Common Failure Modes to Avoid

- **Recency bias**. Assuming the most recent commit is authoritative. The current shape is often the accretion of many earlier decisions. Trace back.

## Models

Role defaults, stamped from `plugins/pstack/models.json` (edit there, rerun `tools/generate.mjs`). A matching role line in the `pstack-models.md` override sheet overrides each at runtime; `/setup-pstack` writes it and lists its path per runtime.

- why investigators: `opus`
- why synthesizer: `opus`

## Reasoning effort

A role value in the override sheet may name a reasoning effort after its model, as in `opus @xhigh`. Levels on Claude Code: `low`, `medium`, `high`, `xhigh`, `max`. Which ones apply depends on the model. A value without `@` takes the sheet's `default effort` line, a level or `session`, and `xhigh` when the sheet has no such line. `session` sets no effort, so the dispatch is the usual one. Strip the suffix before reading the model: `inherit-parent` or `auto` still omits `model` at every level, and a model name is passed as `model`. On Claude Code, a level picks the effort agent from the `subagent_type` you would otherwise use. `pstack:poteto-agent` becomes `subagent_type: "pstack:poteto-agent-<level>"`. `general-purpose`, or no `subagent_type`, becomes `subagent_type: "pstack:effort-<level>"`. The effort agents set only `effort`, so the model you pass still decides the model. On Codex, pass the level as `spawn_agent`'s `reasoning_effort` and keep the usual instructions.
