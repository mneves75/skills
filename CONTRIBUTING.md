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

4. Add `README.md` with comprehensive documentation
5. Submit a pull request

### Improving Existing Skills

1. Fork the repository
2. Make your changes
3. Test with at least one AI tool (Claude Code, Cursor, etc.)
4. Submit a pull request with clear description

## Skill Requirements

- **SKILL.md**: Required. Must have valid YAML frontmatter with `name` and `description`.
- **README.md**: Recommended. Detailed documentation for the skill.
- **scripts/**: Optional. Helper scripts or tools.
- **references/**: Optional. Supporting documentation.

## Code of Conduct

Be respectful. Be helpful. Be kind.

## License

By contributing, you agree that your contributions will be licensed under Apache-2.0.
