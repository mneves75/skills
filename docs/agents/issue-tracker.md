# Issue tracker: Local Markdown

Specs and tickets live in `docs/specs/<feature>/` when work needs more than one session.
Single-session work can use the confirmed request without a separate spec.

- Keep the spec at `docs/specs/<feature>/spec.md`.
- Use one ticket per `issues/<NN>-<slug>.md`, with a `Status:` line and acceptance criteria.
- Append discussion under `## Comments`.
- When a skill says to publish or fetch a ticket, write or read these local files.
- Keep specs; remove completed ticket files in the finishing commit.
- For wayfinding, use `map.md` and numbered child tickets in the same feature directory;
  record `Type:`, `Status:` and `Blocked by:` and resolve prerequisites before dependents.

GitHub issues are not enabled by this convention. PRs deliver code for review, not tickets.
