# Playbook: review, audit or verification

1. **Stay read-only.** Answer, review, diagnosis and audit requests inspect and report. They do
   not edit code unless the user authorizes remediation.
2. **Pick the exact audit type.**

   | Need | Skill |
   |---|---|
   | Deep source security audit with a findings ledger | `security-audit` |
   | Security fixes or the pre-deploy verdict | `mneves-security` |
   | Operational launch readiness | `mneves-production-readiness` |
   | Why coding agents struggle in a repository | `mneves-agent-readiness` |
   | ChatGPT Search crawlers and citations | `mneves-chatgpt-search` |
   | Proof against acceptance criteria | `mneves-verify` |
   | Review of a fixed Git target | `autoreview` |
   | Improvement survey with handoff plans | `improve` |

3. **Fallback.** Name the missing skill and run direct read-only checks on the exact target.
   Label every dimension you could not check `NOT TESTED` or `BLOCKED`.
