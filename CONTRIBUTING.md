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

4. Add `README.md` with the longer documentation
5. Run `npx skills@latest add . --list` and confirm your skill appears
6. Submit a pull request

### Improving Existing Skills

1. Fork the repository
2. Make your changes
3. Test with at least one AI tool (Claude Code, Cursor, etc.)
4. Submit a pull request with clear description

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
