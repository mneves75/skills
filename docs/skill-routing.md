# Choose skills by situation

Choose from the skills the active agent actually exposes, using the task's goal and current
phase. Installing a folder, exposing its description, selecting it, reading it and following
its procedure are separate steps. Diagnose the failing step before changing the catalog.

## Adopt the policy

The canonical, copyable policy is the
[Situation routing section of AGENTS.md](../AGENTS.md#situation-routing); `CLAUDE.md` imports
that file. For another project, copy that section into its canonical agent instructions once,
replacing the repository-specific guide link with your own reference if needed. This guide
links the policy instead of maintaining another copy that could drift. A skill installation
does not install the policy. Changing a machine-wide contract requires its owner's approval.

Repository and host rules determine which gates are mandatory. This policy does not make
every audit mandatory or authorize review-only requests to become edits, deployments or
posted messages. Explicitly naming a skill selects its procedure, not permission for every
action described inside it.

## Distinguish similar situations

| Situation | Route in this collection | Boundary |
|---|---|---|
| Explain a concept to a different audience | `mneves-eli5` | A smaller wording follow-up keeps the route |
| Learn a topic to mastery through questioning | `mneves-socratic-tutor` | A one-off question gets a normal answer; explaining a codebase back or reviewing stored cards belongs to `mneves-teach-back-srs` |
| Stress-test a decision | `mneves-expert-review` | Code-diff review belongs to a code-review skill |
| Review a fixed Git target | `autoreview` | Review is not independent outcome verification |
| Diagnose structural coupling or refactor an explicitly scoped code area | `untangle-codebase` | Naming it alone yields diagnosis and a plan awaiting edit approval; explicit refactoring authorizes in-scope implementation. Missing or invalid scope never expands to the whole repo; comment/test cleanup needs separate opt-in |
| Prove a completed change works | `mneves-verify` | Fresh evidence and its independence rules still apply |
| Review application security and privacy, apply authorized fixes, or gate a deployment | `mneves-security` | Its exact-candidate verdict owns the security gate |
| Run a full read-only source security audit | `security-audit` | Use when the deep audit or coverage ledger and structured findings are requested |
| Audit several selected areas of a repository | `mneves-superaudit` | Define the tracks first. A fixed-diff review or a security-only audit uses its own specialist |
| Deploy to an explicitly authorized environment | `mneves-ship-deploy` | Security and readiness gates apply before deployment |
| Assess operational launch or deployment readiness | `mneves-production-readiness` | A general critique of a plan may use `mneves-expert-review`; choose by the requested evidence |
| Assess why agents struggle in a repository | `mneves-agent-readiness` | Different from production launch readiness |
| Watch a PR | `babysit-pr` | Does not authorize merging |
| Ordinary typo or unrelated question | No specialist unless a local rule requires one | Do not invoke a broad audit merely because it is installed |

Examples are conditional on availability, not a second mandatory catalog. Use the installed
description and procedure for the final decision. `full-stop` remains explicit-only; the
words “full stop” used for emphasis do not invoke it. Plain “ship” is not a deployment request under
[this collection's deployment skill](../skills/mneves-ship-deploy/SKILL.md).

For example (**illustrative**), “diagnose coupling in `src/checkout/`” selects
`untangle-codebase` for a read-only plan; “refactor duplicated tax logic in
`src/checkout/`, preserving public entrypoints” authorizes its bounded implementation.
A generic “clean up” request does not establish that target or authorize test deletion.
The skill uses normal description-based discovery, without an umbrella or a broad
automatic cleanup trigger. Its standalone procedure includes baseline, regression,
adversarial review and independent acceptance steps; no sibling install is required.

## Keep discovery inexpensive

Independent skills retain short capability-and-trigger descriptions and standalone installation.
Related modes can share an entrypoint and load their own references when needed. Do not add a
root `SKILL.md` here: it would shadow nested skills during installer discovery.

The [Agent Skills specification](https://agentskills.io/specification) distinguishes metadata,
activated instructions and on-demand resources. Separate skills already defer their bodies.
[Claude Code's skills documentation](https://code.claude.com/docs/en/skills) describes discovery
and troubleshooting. An umbrella can reduce catalog metadata, but its routing table must still
be loaded and followed; neither arrangement guarantees successful selection.

Before combining skills, inspect the active host's catalog for omissions, duplicate installs,
disabled implicit invocation and overlapping descriptions. Repair only the demonstrated cause.
Do not overwrite upstream skills or accepted local patches to inject this policy.

### Choose a smaller install

Install the entrypoints whose deliverables you use. For example, a team that needs
security review, fixed-diff review and independent acceptance can select:

```bash
npx skills@latest add mneves75/skills --skill mneves-security autoreview mneves-verify
```

Add `security-audit` when you need a coverage ledger and machine-readable security
findings. Add `mneves-production-readiness` and `mneves-ship-deploy` for the full release
workflow. These skills still work as separate installs. See the
[pstack install guide](../collections/pstack/README.md#install) for specialist entrypoints.

For model-facing instructions, state the outcome, authority and evidence up front. Keep
tool-specific details in references. Scale deliberation and proof to the actual decision,
and use a second context when independence is required. See
[OpenAI's guide to lean skills](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
and [Anthropic's Opus 5.5 prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5).

## Evaluate selection and behavior separately

Start from actual missed or incorrect invocations in authorized session logs. Keep private logs
private; extract only the minimal task context needed and label synthetic cases. Include tasks
that need no specialist, explicit requests, unavailable skills, ambiguous matches, small
follow-ups, phase changes and goal changes. Freeze expected acceptable routes before testing.

Compare baseline and candidate in fresh sessions of each target harness, with identical skill
availability, model settings and task inputs. A supplied-catalog routing probe tests selection
only: it does not test native discovery, file loading or procedure compliance. Record which kind
ran. A prompt without tools must not claim it actually read or used a skill.

For native behavioral trials, inspect whether the intended procedure was read before dependent
actions, relevant instructions were followed, and mandatory gates and permission boundaries
survived phase changes. Do not execute production actions merely to test routing; use a contained
fixture and stop at the authorization boundary. Keep expected answers outside the test context.

Record correct acceptable selection, unnecessary activation, missed required gates and observed
compliance separately. Compare token/tool cost only when the harness supplies reliable counters;
mark missing measures unknown. Retain failures, model identities and raw outputs. Small probes
are regression examples, not proof of universal reliability or measured savings.

The initial implementation and evidence limits live in
[the routing work record](specs/skill-routing/progress.md).
