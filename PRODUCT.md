# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Developers who use AI coding agents and need to choose and install a relevant procedure.
The owner confirmed this context and delegated design judgment on 2026-10-13.

## Product Purpose

Publish portable Agent Skills: named Markdown procedures that an agent loads when a
task matches their description. The site helps visitors understand, choose and install
them, then reach the full usage guide and source.

## Operating Context

The source repository ships twenty-three original/adapted skills and a separately installed
collection of thirty-six pstack skills. Visitors install through the skills CLI or a
Git clone, then use the procedures in their existing coding-agent session.

## Capabilities and Constraints

Static HTML/CSS and minimal JavaScript, hosted on GitHub Pages. Keep the existing skill
descriptions, install commands, source/guide links, collection information, historical
readiness example and changelog provenance. English site copy. No new application
framework or runtime dependency. Preserve working functions and provide truthful errors.
The HOWTO and landing changelog rows are generated from repository documentation.
Production publication requires the authorized merge/release target.

## Evidence on Hand

The repository's SKILL.md files, HOWTO.md, README.md, CHANGELOG.md and VERSION are the
content authority. The FastAPI readiness report is a dated illustrative assessment,
not a current benchmark of these skills. No testimonials, customer logos or measured
productivity claims are supplied.

## Product Principles

- Make the right procedure easy to find and inspect.
- Preserve evidence, limitations and task authority.
- Keep installation and source accessible without a new account or service.
- Prefer a small, maintainable static implementation.

## Accessibility & Inclusion

Responsive layout, semantic headings/links, visible keyboard focus, readable contrast,
usable controls and reduced-motion preferences are required by the repository contract.
