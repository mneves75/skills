# Contributing

Thank you for your interest in contributing to this skills collection.

## How to Contribute

### Reporting Issues

1. Check existing issues first
2. Include reproduction steps
3. Specify which AI tool you're using (Claude Code, Cursor, etc.)

### Adding a New Skill

1. Fork the repository
2. Create a new directory under `skills/`
3. Add `SKILL.md` with YAML frontmatter:

```yaml
---
name: your-skill-name
description: Clear description of what this skill does and when to use it.
---
```

4. Add longer documentation or linked references when they help; keep all examples portable.
5. Update the README catalog, HOWTO, AGENTS tree, VERSION, changelog and README badge;
   regenerate the site with `tools/scripts/build-site.sh` (after `bun install` in `tools/`).
6. Run `npx skills@latest add . --list`, the Agent Skills validator and the repository gates.
7. Submit a pull request. The `mneves-chatgpt-search` entry illustrates a Markdown-only
   skill with optional reference branches and explicit evidence limits.

### Improving Existing Skills

1. Fork the repository
2. Make your changes
3. Test with at least one AI tool (Claude Code, Cursor, etc.)
4. Submit a pull request with clear description

### Changing the Website

Keep product facts aligned with the skill source, README and HOWTO. `PRODUCT.md`
records the audience and constraints; `DESIGN.md` records the landing page's actual
visual system, with extensions in `.impeccable/design.json`. Surface briefs are
development documentation and stay outside the published `site/` directory.

Preserve the landing changelog markers and, after `bun install` in `tools/`, run `tools/scripts/build-site.sh` followed
by `bash tools/scripts/build-site.test`. Inspect desktop, tablet and narrow mobile
renders, keyboard navigation, light/dark contrast and reduced motion. When
`agent-browser` is available, run `bash tools/scripts/check-site-copy.sh <site-url>`
through your host's approved browser route to exercise successful and denied copies.
New local fonts/assets require their license and provenance in `NOTICE`.

### Preparing a Release

Keep `VERSION`, the README badge and the latest changelog entry aligned, then regenerate
the site. Update the readiness ledger and plan from the actual assessment; a source
check or an expired waiver does not make a launch control pass.

Merging to `main` publishes the site after CI succeeds. Before that merge, complete
the [security deploy gate](skills/mneves-security/SKILL.md#deploy-gate) and
[production-readiness gate](skills/mneves-production-readiness/SKILL.md) for the final
candidate. Keep detailed reports and owner waivers private. Merge approval alone does
not waive an open control.

`main` is also what `npx skills add` installs, so every merge is a release that needs its
own gate. Close a release without a second one:

1. Tracked files in the release PR describe the candidate tree. Say that the binding result
   lives in the private gate records and the `vX.Y.Z` tag message. Do not write claims that
   the merge makes false, such as "not deployed" or "BLOCK".
2. After CI and Pages succeed and the served files match the gated tree, create an annotated
   `vX.Y.Z` tag on the merge commit (owner approval required). `tools/scripts/deploy.sh <pr>`
   does this sequence: it refuses without a production security-gate record and a readiness record
   for the head's tree, merges with `--match-head-commit`, requires the merge tree to equal the gated
   tree, waits for the CI and Pages runs, compares every served `site/` file with the tree, writes
   the reuse records for the merge commit and prints (or with `--tag` creates and pushes) the tag;
   `--dry-run` prints the plan. Its guards are proved by `tools/scripts/deploy.test.sh`. Its message carries these
   lines: `Security gate:` (with the waived IDs), `Readiness gate:`, `Waivers:` (owner and
   expiry), `Independent acceptance:` (when one ran), `Gated tree:`, `Gated commit:`, `CI:`
   and `Deployed:`. A rollback to a tag skips
   a new audit only when the tag message records the verdict.
3. Fold the binding run's ledger bookkeeping (cursor, gate-history row, WAIVED rows) and the
   `MEMORY.md` release state into the next release PR, never a standalone merge
   ([gates.md](skills/mneves-production-readiness/references/gates.md)).
   `tools/scripts/check-readiness-catalog.py` checks that the ledger stays consistent.

#### Skipping GitHub CI for a release

Only the owner can skip GitHub CI, explicitly and for one exact commit. GitHub CI is then waived, not
passed, and the security and readiness gates still apply. `tools/scripts/deploy.sh` remains the
release path whenever CI runs; it waits for a CI run that a skipped release never has. With the
owner's skip, release by hand:

1. Complete the security and readiness gates on the exact candidate tree.
2. Merge with `[skip ci]` in the merge commit message and `--match-head-commit`, and check that the
   merge commit's tree equals the gated tree. Without a CI run, Pages does not publish on its own.
3. Before any Pages dispatch, run a fresh production-readiness binding run on the pushed merge
   commit's full id. The security verdict may be reused only because the tree is identical.
4. After acceptance, a repository administrator sets the merge commit's full id as the
   `CI_WAIVER_APPROVED_SHA` variable of the `github-pages` environment:
   `gh variable set CI_WAIVER_APPROVED_SHA --env github-pages --body <sha>`. It is not a secret,
   and a dispatch cannot set it. Do not create a repository variable with that name: it would also
   reach the deploy job.
5. Dispatch Pages with the same id and the owner's reason:
   `gh workflow run static.yml --ref main -f ref=<sha> -f ci_waiver_sha=<sha> -f ci_waiver_reason='<reason>'`.
   The guard refuses, without querying CI, unless the id is a full lowercase commit id equal to the
   checked-out commit, the current `main` tip and the approved value, and the reason is not blank.
   If `main` has moved, approve and gate the new tip instead.
6. The run summary reads `CI WAIVED, not passed`. Compare every served `site/` file with the tree,
   as `deploy.sh` does.
7. Delete the approval whether the dispatch and verification succeeded or failed:
   `gh variable delete CI_WAIVER_APPROVED_SHA --env github-pages`. A retry sets it again.
8. Create the annotated tag as above, with a `CI:` line that says the owner waived CI and why,
   in place of a run.

A waived commit has no successful CI run, so the ordinary rollback dispatch cannot republish it later.

Waiver expiry is the owner's choice, up to the readiness skill's 90-day cap; never set one on the
owner's behalf. Security acceptance needs a model other than the builder's, and finders and their
verifier run in separate contexts. When no such model can run (for example, both Codex accounts
are out of quota), report the acceptance gate as blocked instead of reviewing with the same model.

## Skill Requirements

Skills must stay discoverable by `npx skills@latest add mneves75/skills`: one folder per
skill under `skills/`, folder name equal to the frontmatter `name`, no `SKILL.md` at the
repo root (it would shadow the rest), no absolute or home-directory paths in the text.
Verify with `npx skills@latest add . --list` before opening a PR. CI runs the same check.
Original skills use the `mneves-` prefix. An adapted third-party skill may retain its upstream
name only when its copyright, compatible license, source, and material modifications are recorded.

- **SKILL.md**: Required. Must have valid YAML frontmatter with `name` and `description`.
- **README.md**: Recommended. Detailed documentation for the skill.
- **scripts/**: Optional. Helper scripts or tools.
- **references/**: Optional. Supporting documentation.

## Code of Conduct

Be respectful. Be helpful. Be kind.

## License

By contributing original work, you agree that it will be licensed under Apache-2.0. Adapted
third-party work retains its compatible upstream license as identified in that skill's directory.
