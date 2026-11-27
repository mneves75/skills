# Optional siblings

Skills outside this repository that the playbooks name. Each is optional. When one is not
installed, say so once and use its fallback.

| Skill | Public source | Used for | Fallback |
|---|---|---|---|
| `tdd` | `mattpocock/skills`; `pstack` ships one too | Test first | Write the failing test, watch it fail, then fix |
| `code-review` | `mattpocock/skills` | Standards and spec review | `autoreview` on the same target |
| `diagnosing-bugs` | `mattpocock/skills` | Hard or slow bugs | One-hypothesis reproduction loop |
| `grilling` | `mattpocock/skills` | Question the user on a plan | `mneves-expert-review` |
| `domain-modeling` | `mattpocock/skills` | Glossary and decision records | A short glossary note |
| `improve` | `shadcn/improve` | Read-only improvement survey | A ranked read-only survey in the session |

Two installed skills can share a name, as `tdd` does. Use whichever one the host lists. Both are
test-first.

The `pstack` skills (`how`, `architect`, `interrogate`, `blast-radius`, `fix-ci`,
`fix-merge-conflicts`, `make-pr-easy-to-review`, `teach`, `technical-writing`, `poteto-mode`)
ship in this repository's `collections/pstack`. A root-only install may lack them. When one is
missing and its step states no fallback, do the step directly with ordinary tools, and say that
the skill was not used.
