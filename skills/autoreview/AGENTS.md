# Autoreview Skill

- This portable adaptation is maintained in `mneves75/skills`, derived from `openclaw/agent-skills`.
- Maintain this directory directly; no upstream checkout is required to install, run, or test it.
- Preserve local model defaults when incorporating upstream changes.
- Validate helper changes with `python3 scripts/run-tests.py` from this directory.
- Keep the upstream MIT license and pinned provenance. Update references when importing fixes;
  inspect the diff and rerun the security tests before changing isolation or retry behavior.
