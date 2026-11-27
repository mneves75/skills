# Playbook: scoped refactor

1. **Freeze scope and baseline.** Require a named module or file boundary. Never let a vague
   "clean up" grow into an edit across the repository. Record the current tests, types and
   behavior as the baseline.
2. **Diagnose and plan.**
   - `untangle-codebase`. Naming it alone gives a diagnosis and plan, and it waits for approval
     to edit; an explicit refactoring request authorizes bounded edits.
   - `blast-radius` for what the change could break outside the diff.
   - Fallback: map callers, dependency direction and duplicated rules, then propose the smallest
     behavior-preserving edits.
3. **Apply and prove.**
   - Preserve public contracts and safety checks.
   - Rerun the baseline after each coherent unit.
   - Then run the review and verify steps of the build playbook.
