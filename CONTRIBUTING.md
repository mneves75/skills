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
