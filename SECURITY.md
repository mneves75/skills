# Security Policy

## Supported Versions

Security fixes land on `main` and in the latest tagged release only.

Supported runtimes for the shipped executables:

| Runtime | Supported | Used by |
|---|---|---|
| Bun | 1.4.4 or later (CI pins 1.4.4) | the readiness tool in `tools/` |
| Python | 3.11 or later | autoreview, the ship-deploy contract check, the SRS helper, render starters, site build helpers |
| Node.js | a release line upstream still maintains | security-audit validators, site build |

The maintainer (@mneves75) owns these floors: when a runtime line reaches upstream end of
life, the next release raises the floor. A critical advisory in a supported runtime, a locked
dependency or a pinned action is fixed, or the affected path disabled, within 7 days of
publication. CI's `bun audit`, which fails the build on any advisory in the locked tools, and Dependabot alerts are how such an advisory is found.

## Reporting a Vulnerability

Do not open a public issue for a suspected vulnerability. Use GitHub's
[private vulnerability reporting](https://github.com/mneves75/skills/security/advisories/new)
for this repository.

- Acknowledgement: within 3 business days.
- Triage and severity: within 7 business days.
- Fix timeline: agreed after triage, by severity. Coordinated disclosure; please allow
  time for remediation before publishing.

## Scope

Everything shipped here: skill instructions (`skills/*/SKILL.md`), the orchestrator's shell
script and its test (`skills/mneves-fable-orchestrator/tools/codex-lane`, `codex-lane.test`),
the release contract checker, reference release scripts and their tests
(`skills/mneves-ship-deploy/scripts/`, `assets/*.sh`, `tests/`), the render content-policy
filter, starters and tests (`skills/mneves-render/scripts/check_ast.py`, `assets/`, `tests/`),
the SRS helper and its test (`skills/mneves-teach-back-srs/scripts/srs_db.py`, `tests/`), the
Node validators and their tests (`skills/security-audit/validate-*.cjs`, `*.test.cjs`), the
Bun/TypeScript tool (`tools/`), the autoreview CLI and its packaged tests
(`skills/autoreview/`), the git hook (`.githooks/`), and the GitHub workflows.

Skill files are instructions executed by an AI agent with your permissions. Treat a skill
you did not read like a script you did not read.

Autoreview treats repository inputs and model output as untrusted. Its scanner, subprocess
isolation, source-integrity checks, and output-path restrictions are security boundaries;
do not disable them to obtain a clean review. Scanning is not permission to disclose private
code, and an AI review does not prove a program secure. Beta tags identify test candidates,
not a guarantee that every provider or platform has been exercised.

## Access and release model

- One maintainer administers the repository. Every other account with write access is
  checked in the quarterly access review below, and removed when it is no longer needed.
- A ruleset on `main` blocks force-pushes and branch deletion. GitHub secret scanning,
  Dependabot alerts and private vulnerability reporting are enabled.
- CI runs with `contents: read`. Only the Pages workflow gets `pages: write` and
  `id-token: write`, its `github-pages` environment deploys from `main` only, and every
  action is pinned to a full commit SHA.
- A merge to `main` publishes the skills at once and the site once CI passes on that commit
  (`static.yml` waits for the CI run). Each release first passes the
  repository's own pre-deploy security gate (the `mneves-security` deploy gate) and needs the
  maintainer's explicit approval of that commit. AI agents act only through the maintainer's
  session and hold no separate deploy credentials.
- Access review, each quarter: list collaborators, deploy keys, OAuth and GitHub App grants,
  and personal access tokens with access to the repository; remove what is not needed;
  record the date in the release notes of the next release.

## If a device or credential is compromised

Applies to any device or token with write access to this repository.

1. From a clean device, revoke GitHub sessions, personal access tokens, SSH and signing keys,
   and OAuth grants; change the password and confirm two-factor authentication.
2. Review the account security log, recent pushes, tags, releases, workflow runs and Pages
   deployments. Revert unexpected changes with a corrective release; never move a published tag.
3. Rotate every provider credential that device held for these tools (AI review engines,
   package registries). This repository stores none.
4. Inspect open branches and pull requests before the next release, and run the pre-deploy
   security gate on that candidate.
5. Record what happened, what was revoked and what changed.

Baseline for devices with write access: full-disk encryption, a screen lock, and current
operating-system updates.

## Data handling

- The site (`site/`) loads no third-party resources and sets no cookies.
- The readiness checker (`tools/`) sends nothing about the assessed repository anywhere. Some
  checks run the project's own build, lint, test and dependency tooling (for example `bunx`,
  Maven or Gradle resolution, `pip install -e .`), which can download packages from their
  registries and write build output, caches or the active Python environment. Each command
  has a deadline and stops with the checker. Assess only repositories you trust, in an
  environment where those side effects are acceptable.
- Autoreview sends the selected review inputs, after a credential scan, to the provider you
  configure; that provider's retention terms apply. Reports go only to output paths outside
  the reviewed repository, and temporary files are removed after the run.
- `mneves-teach-back-srs` keeps sessions and cards in `.ai-learn/srs.db` inside your project;
  delete that file to erase them. Its CSV export keeps text as written, for Anki; check
  formulas before opening an export of untrusted text in a spreadsheet.
- `codex-lane` (in `mneves-fable-orchestrator`) keeps each lane's state and full model
  transcripts in `$CODEX_LANE_DIR` (default `~/.codex/lanes`, mode 700) and never prunes
  them. A lane owns `<lane>.json` and, per run, `<lane>.<UTC stamp>.<pid>.jsonl`, `.last.txt`
  and `.stderr.log`. To erase it, `drop` the lane, then delete exactly those names; never a
  `<lane>.*` glob, which also matches dotted lanes such as `job.extra`.
- `council` keeps each deliberation in a private session directory outside your project
  (conventional default `~/.council/`): the task, the plan, and every member's prompt, reply
  and log. It never prunes them, and it starts other authenticated CLIs (Claude, Codex or
  pi), each under a read-only or restricted configuration. The task and plan you approve
  leave your machine to those providers under their own retention terms, and each member CLI
  keeps its own sessions under its own configuration.
- `pr-wait` (in `babysit-pr`) keeps one small state file per watched PR in
  `~/.local/state/pr-wait/` (`<owner>__<repo>__<number>.json` and its lock): ids of reported
  events, a digest of each bot summary, the base commit and the merge state; no comment text.
  It ignores a file older than six hours; delete the file to erase it.
- `security-audit` writes its audit to a directory outside the target (conventional default
  `~/security-audit-skill/<repo-name>/run-<N>/`): the coverage ledger, findings, evidence and
  reports. It never prunes them. Source inspection stays read-only, and it runs
  target-controlled builds, tests or browsers only inside the sandbox the skill requires.
- The other skills are Markdown procedures. What your agent sends, and where, follows your
  agent's own configuration.

### Erasing what these tools leave behind

Every store is on your machine or with a provider you chose; this project runs no server and
keeps no copy. To erase:

1. **Local files the tools wrote.** Delete the readiness reports you asked for (`--output`),
   autoreview's `--output`, `--json-output` and `--status-output` files, `.ai-learn/srs.db`
   and any SRS exports, the `codex-lane` files listed above, the `pr-wait` state files, the `council` session directory
   (delete each session whole, after reading it, rather than a wildcard that could match
   another run), and the `security-audit` output directories. Each lives where you chose or
   where this file says; the tools shipped here keep no second copy of their own.
2. **Provider copies.** Review inputs sent by autoreview, and prompts your agent sends while
   following a skill, are kept under that provider's own retention terms. Delete them through
   the provider's account or data controls; no tool here can reach them.
3. **The member CLIs' own stores.** `council` starts other agents, and `security-audit` runs
   target-controlled commands, so those tools persist their own sessions, chats and logs
   wherever their configuration says — for example a CLI's own session store — and `council` cannot
   disable that for every member. This repository does not track, enumerate or erase those
   copies, and their retention was not tested here. Treat each CLI's own data controls as the
   place to erase them, and prefer a sanitized prompt-only run when that matters.
4. **Backups.** Copies in your own backups (for example Time Machine or a synced folder)
   remain until those backups expire or you remove them. Delete or exclude them there; a
   restore brings erased files back, so delete them again after restoring.
5. **Not applicable.** The site sets no cookies and collects nothing, and this repository's CI
   handles no user data.

## Site protections

GitHub Pages serves the site over HTTPS and redirects HTTP to HTTPS, but it does not let a
repository set response headers. Each page therefore carries its policy in markup: a
Content-Security-Policy that starts from `default-src 'none'` and allows only what that page
uses (the landing page: same-origin script, styles and fonts, plus inline styles and same-origin
or `data:` images; the guide and the sample report: inline styles and images only, no script),
blocks forms and base-URL changes, plus a `strict-origin-when-cross-origin` referrer policy.
HSTS, `X-Content-Type-Options` and frame protection need response headers, which this hosting
cannot send, and `github.io` is not on the browsers' HSTS preload list (checked 2026-10-28). The site holds no accounts,
cookies, forms or state-changing actions.
