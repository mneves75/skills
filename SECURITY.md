# Security Policy

## Supported Versions

Security fixes land on `main` and in the latest tagged release only.

## Reporting a Vulnerability

Do not open a public issue for a suspected vulnerability. Use GitHub's
[private vulnerability reporting](https://github.com/mneves75/skills/security/advisories/new)
for this repository.

- Acknowledgement: within 3 business days.
- Triage and severity: within 7 business days.
- Fix timeline: agreed after triage, by severity. Coordinated disclosure; please allow
  time for remediation before publishing.

## Scope

Everything shipped here: skill instructions (`skills/*/SKILL.md`), the shipped shell script
(`skills/mneves-fable-orchestrator/tools/codex-lane`), the Python helper
(`skills/mneves-teach-back-srs/scripts/srs_db.py`), the Bun/TypeScript tool (`tools/`),
the autoreview CLI and its packaged tests (`skills/autoreview/`),
the git hook (`.githooks/`), and the GitHub workflows.

Skill files are instructions executed by an AI agent with your permissions. Treat a skill
you did not read like a script you did not read.

Autoreview treats repository inputs and model output as untrusted. Its scanner, subprocess
isolation, source-integrity checks, and output-path restrictions are security boundaries;
do not disable them to obtain a clean review. Scanning is not permission to disclose private
code, and an AI review does not prove a program secure. Beta tags identify test candidates,
not a guarantee that every provider or platform has been exercised.
