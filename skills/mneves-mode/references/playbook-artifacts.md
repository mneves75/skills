# Playbook: specialized artifacts and learning

Use the dedicated skill when it is installed. Otherwise follow the fallback's boundary, and
report `BLOCKED` when its tools are missing.

- **Markdown to HTML, DOCX or PDF:** `mneves-render`. Fallback: a small project-local export
  with document tools already installed. Reject raw active HTML, and inspect the rendered output.
- **Product launch film:** `mneves-motion-film`. Fallback: take every on-screen claim verbatim
  from product copy, check that the media tools exist before rendering, and check the duration,
  codecs and audio sync.
- **Mobile UI concept images:** `imagegen-frontend-mobile`. Fallback: concept images only,
  following the platform's conventions. Write application code only when asked.
- **Learn a codebase:** `mneves-teach-back-srs`, or `teach` for one explanation. Fallback:
  check the user's explanation against the source, with file and line citations. Say that spaced
  repetition needs the skill.
- **Technical prose:** `technical-writing`.
