# Skills

![Version](https://img.shields.io/badge/version-1.42.0-blue)
![License](https://img.shields.io/badge/license-Apache--2.0%20%2B%20MIT-green)
![CI](https://github.com/mneves75/skills/actions/workflows/ci.yml/badge.svg)
![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-purple)

Skills for AI coding agents. Each installs into any tool that reads `SKILL.md` folders.

**New here?** Read [HOWTO.md](HOWTO.md) ([web version](https://mneves75.github.io/skills/howto.html)); site: [mneves75.github.io/skills](https://mneves75.github.io/skills/): what each skill does, how to trigger it, and an example for every one (those recorded from real runs and those written as illustrations are each labelled as such).

## Available Skills

For compact task prompts, bounded retries and model routing, see
[Using skills with less repeated work](docs/usage-efficiency.md). Service level objectives and
incident reviews are not installable skills: read the [SRE guides](docs/sre-guides/README.md)
or paste one of the [SRE prompts](docs/sre-prompts.md), and check each draft against your
artifacts.

| Skill | Description |
|-------|-------------|
| [autoreview](skills/autoreview/) | Structured, isolated code review of a fixed Git target; ships its helper, security tests, and its own engine defaults |
| [council](skills/council/) | Bounded independent deliberation over a plan: each available member CLI answers without seeing the others, and the lead revises for exactly the requested rounds; advisory, never verification |
| [imagegen-frontend-mobile](skills/imagegen-frontend-mobile/) | Generate coherent iOS or Android screen and flow images, with platform conventions, visual QA, and no code |
| [mneves-chatgpt-search](skills/mneves-chatgpt-search/) | Improve ChatGPT Search discovery, citations and referral attribution using official guidance, separate search/training policies and verifiable evidence |
| [mneves-eli5](skills/mneves-eli5/) | Feynman-technique explainer calibrated to the listener (child, layperson, executive, junior, expert), answered in the user's language |
| [mneves-agent-readiness](skills/mneves-agent-readiness/) | Evaluate codebase readiness for AI agents: 9 pillars, maturity levels L1–L5, local-only |
| [mneves-expert-review](skills/mneves-expert-review/) | Scoped stress test: objective, first principles, relevant research, one combined challenge, distinct alternatives, improved deliverable |
| [mneves-handoff](skills/mneves-handoff/) | Clipboard-ready, path-free prompt that hands a task to another agent for independent review and discussion first |
| [mneves-render](skills/mneves-render/) | Build project-local Markdown renderers for HTML, editable DOCX and PDF, with shared design, tested starter templates and content/visual verification |
| [mneves-security](skills/mneves-security/) | Evidence-backed security/privacy audit and vulnerability hunting (candidates must name a crossed boundary and survive a fresh disprover), ordered remediation, authorized safe fixes and the mandatory gate before every staging or production deploy, using current OWASP guidance, adversarial review and independent acceptance |
| [security-audit](skills/security-audit/) | Six-phase, coverage-led source audit with independent candidate and final verification, three finding verdicts, a schema-checked ledger and machine-readable findings; ships its Node validators and tests, and is not a deploy gate |
| [mneves-production-readiness](skills/mneves-production-readiness/) | Gate staging and production deploys on production readiness: a ledger of evidence-backed controls (data, recovery, money, operations, ownership), a verdict per target and a detailed fix plan; security rows delegate to `mneves-security` |
| [mneves-fable-orchestrator](skills/mneves-fable-orchestrator/) | Route ordinary, bounded and difficult work by capability; models live in one Defaults block, including one announced fallback lane; ships [`codex-lane`](skills/mneves-fable-orchestrator/tools/codex-lane) |
| [mneves-superaudit](skills/mneves-superaudit/) | Bounded audit-and-ship pass: slop, performance, agent DX, PR triage — falsifiable completion criteria, existing authority and requested stops |
| [mneves-ship-deploy](skills/mneves-ship-deploy/) | Deploy the pushed commit, prove it live, then tag, through dev (when present) and staging without redundant confirmation; explicit approval of the exact candidate before production; ships a release-contract check |
| [mneves-teach-back-srs](skills/mneves-teach-back-srs/) | Spaced-repetition learning through codebase teach-back sessions (SM-2 + SQLite) |
| [mneves-verify](skills/mneves-verify/) | Independent verification before done/fixed/shipped: fresh context checks the artifact against criteria, PASS/FAIL/BLOCKED |

Code-review workflows use local [cccc](https://github.com/moznion/cccc) when available
to measure supported source complexity, alongside independent adversarial review and tests.
It is optional, runs locally and never makes low scores an approval. The portable
[installation and evidence procedure](skills/autoreview/references/complexity.md) ships
with `autoreview`, including a pinned checksum-verified installer and real CLI controls.

## Collections

Third-party skill packs vendored with their upstream names and licenses. They sit outside
`skills/`, so the default install below leaves them out.

| Collection | Skills | Install |
|---|---|---|
| [pstack](collections/pstack/) | 36 engineering workflow skills from Lauren Tan's pstack, via the pstack-claude port: `poteto-mode`, `architect`, `interrogate`, `swarm`, `how`, `why` and more | `npx skills@latest add https://github.com/mneves75/skills/tree/main/collections/pstack/skills` |

Its README lists the deviations from upstream and the name collisions with Matt Pocock's
skills (`tdd`, `teach`).

## Install

The fastest path is the [skills CLI](https://github.com/vercel-labs/skills) (`npx skills`),
which discovers every `skills/*/SKILL.md` in this repo and links it into the agents you pick
(Claude Code, Codex, OpenCode, Cursor, Cline, Windsurf, Gemini CLI, pi and 70+ more):

```bash
# Interactive: choose skills and agents
npx skills@latest add mneves75/skills

# Everything, all detected agents, no prompts (user-wide install)
npx skills@latest add mneves75/skills --all -g -y

# One skill into one agent
npx skills@latest add mneves75/skills --skill mneves-verify -a claude-code -y

# See what's available / keep up to date / remove
npx skills@latest add mneves75/skills --list
npx skills@latest update
npx skills@latest remove mneves-verify
```

User-wide installs land where each agent looks: `~/.claude/skills/` for Claude Code and
`~/.agents/skills/` for Codex (which also reads `.agents/skills/` inside a repository).
Project-scoped installs (omit `-g`) land in `./.claude/skills/`, `./.agents/skills/`, etc.,
and can be committed with the project.

### Manual (git clone)

Any tool that reads `SKILL.md` folders works with a plain clone:

| Tool | Command |
|------|---------|
| Claude Code | `git clone https://github.com/mneves75/skills.git ~/.claude/skills/mneves-skills` |
| Codex | `git clone https://github.com/mneves75/skills.git ~/.agents/skills/mneves-skills` (Codex reads `~/.agents/skills` and `.agents/skills` in a repository) |
| [pi](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent) | `git clone https://github.com/mneves75/skills.git ~/.pi/agent/skills/mneves-skills` |
| [OpenCode](https://opencode.ai/) | `git clone https://github.com/mneves75/skills.git ~/.config/opencode/skills/mneves-skills` |
| Cursor | `git clone https://github.com/mneves75/skills.git ~/.cursor/skills/mneves-skills` |
| Shared catalog (any tool) | `git clone https://github.com/mneves75/skills.git ~/.agents/skills/mneves-skills` |

Update a clone with `git -C <dir> pull`.

### Check the install

If you link skills one by one instead (one symlink per skill into each agent's directory), a
skill added in a later release is not linked until you add it; the agent simply never lists it.
Rerun `npx skills@latest add mneves75/skills --all -g -y`, or check three separate things:

1. **Entrypoint present**: each skill's `SKILL.md` is in the agent's directory.
2. **Full package present**: its `references/`, `assets/` and scripts are there too. A copied
   `SKILL.md` alone loads, then fails when it opens a reference.
3. **Discovered at runtime**: start a fresh session and ask the agent which skills it can
   see. A skill on disk that the agent does not list sits in a directory that agent does not
   read, or the agent needs a restart.

```bash
# from the repo root; set DIR to the agent's skills directory. Checks 1 and 2 only.
DIR=~/.claude/skills
for s in skills/*/; do
  n=$(basename "$s")
  if [ ! -e "$DIR/$n/SKILL.md" ]; then echo "missing entrypoint: $n"; continue; fi
  git ls-files -- "$s" | while read -r f; do
    test -e "$DIR/$n/${f#skills/$n/}" || echo "incomplete: $f"
  done
done
```

## Readiness check (tool)

`mneves-agent-readiness` ships a Bun + TypeScript assessor with no runtime dependencies.
It assesses the current directory:

```bash
git clone https://github.com/mneves75/skills.git
cd skills/tools && bun install
cd /path/to/your-project
bun --bun /path/to/skills/tools/readiness-check.ts --format=html --output=report.html
```

`--help` lists every option (`--min-level` for CI gates, `--app` for monorepos, `--skip-tests`).
The skip flags skip only the test-run and build-verification checks. Lint, type, dependency
and task-listing checks still run the project's toolchain (`mvn compile`, `./gradlew`,
`cargo check`, `cargo clippy`, `bunx eslint` and similar), which can execute code the
repository controls, so assess only repositories you trust, or run the tool in a sandbox.

## Example report

Report generated by the tool on 2026-08-26 with `--skip-tests --skip-build` (test-run and build-verification checks skipped; its lint checks still ran the project's tools). **[View Live Report →](https://mneves75.github.io/skills/)**

| Project | Language | Level | Score | Report |
|---------|----------|-------|-------|--------|
| FastAPI (`9a8a13f`, 2026-08-25) | Python | L3 | 61.7% | [View](https://mneves75.github.io/skills/fastapi.html) |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Security reports: [SECURITY.md](SECURITY.md).

Publishing follows [Preparing a Release](CONTRIBUTING.md#preparing-a-release): merging to
`main` publishes the site after CI succeeds. Security and readiness gates remain separate
from CI and merge approval; their current tracked assessment is in [the readiness ledger](docs/readiness/ledger.md).

## License

Original work in this repository is Apache-2.0. The adapted
[`imagegen-frontend-mobile`](skills/imagegen-frontend-mobile/) and
[`autoreview`](skills/autoreview/) skills and the [`pstack`](collections/pstack/) collection retain
their upstream MIT licenses and copyrights; see the `LICENSE` file in each directory.

The repository's readiness tooling runs locally. Image-generation workflows may send prompts and
references to the configured image provider; autoreview sends scanned review inputs to the
selected review provider. Authorize private-content disclosure before either workflow.

## Acknowledgments

The pillar/maturity-level structure follows the shape of [Factory.ai](https://factory.ai/agent-readiness)'s commercial Agent Readiness assessment. This tool is an independent, open-source, local-only implementation with its own checks and scoring.

## Related

- [Anthropic Skills](https://github.com/anthropics/skills) - Official specification
- [pi coding agent](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent) - Open-source coding agent with skills support
- [OpenCode](https://opencode.ai/) - Terminal-based AI coding assistant with skills support
- [OpenSkills](https://github.com/numman-ali/openskills) - Universal skills loader
- [skills CLI](https://github.com/vercel-labs/skills) / [skills.sh](https://skills.sh) - `npx skills` installer and registry
