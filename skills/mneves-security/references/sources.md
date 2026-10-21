# Primary-source lookup

These are lookup starting points, not a permanently current checklist. Recheck official
project pages/releases and applicable provider docs at execution time. Record edition,
URL, access date, chosen requirements/profile and unavailable sources. Prefer stable
versioned requirements; separate a draft/bleeding-edge document from a released standard.
Use version-qualified control IDs only after reading the actual requirement.

## OWASP snapshot

Checked 2026-10-13. The snapshot establishes the initial baseline, not future freshness:

| Surface / purpose | Official starting point | Edition checked |
|---|---|---|
| Web/API control requirements | [ASVS](https://owasp.org/projects/asvs), [stable releases](https://github.com/OWASP/ASVS/releases) | 5.0.0 |
| Web risk coverage | [Web Top 10](https://top10.owasp.org/2025/) | 2025 |
| API risk coverage | [API Top 10](https://api-security.owasp.org/editions/2023/en/0x00-header/) | 2023 |
| Web test methods | [WSTG versioned testing guide](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/) | 4.2 |
| LLM applications | [GenAI LLM Top 10](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) | 2026 |
| Agents / autonomous tool use | [Agentic Applications Top 10](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | 2026 |
| Mobile clients | [MASVS](https://mas.owasp.org/MASVS/), [MASTG](https://mas.owasp.org/MASTG/) | Select current applicable releases at audit time |

Read all categories of the lists applicable to the discovered surfaces, then map risks
to controls and allowed/denied tests. Top 10 lists raise awareness; they are not complete
verification standards. Review all selected ASVS requirements, documenting applicability
and exclusions. “All OWASP” is not a finite certification profile: state which projects,
versions, controls and surfaces were actually covered.

## Focused implementation guidance

Use the [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/) for actual fixes:

- [Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html),
  [password reset](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html),
  [authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
  and [session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html).
- [HTTP headers](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html),
  [CSP](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html),
  [CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
  and [SSRF](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html).
- [Input validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html),
  [uploads](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html),
  [logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) and
  [AI prompt injection](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html).

Consult the actual framework, runtime, deployment, auth/storage/payment/AI provider
documentation for its current semantics; do not transpose one vendor's security contract
to another. For a discovered Supabase project, start with official
[RLS](https://supabase.com/docs/guides/database/postgres/row-level-security),
[API keys](https://supabase.com/docs/guides/getting-started/api-keys) and
[storage access](https://supabase.com/docs/guides/storage/security/access-control).
These links do not make Supabase a required dependency or prove deployed policies.

For a deeper multi-agent hunt with a coverage ledger and schema-validated findings, use
Cloudflare's separately installed
[security-audit](https://github.com/cloudflare/security-audit-skill) skill when present.
It is not shipped here; without it, this skill's attack classes and coverage critic apply.
Its [harness write-up](https://blog.cloudflare.com/build-your-own-vulnerability-harness)
is the evidence for the disproof step and partial-coverage rule: one run found about half
of what repeated runs found, and unsupported candidates were rejected by a validator that
could not file findings of its own and by requiring a proof that runs on unmodified source.

Legal readiness uses relevant official regulatory guidance only when jurisdiction and
processing are known. Request legal/content ownership for unresolved interpretations.
Do not send source, records or private dependency metadata to search services. Retrieval
failure is a disclosed limitation; it never becomes a fabricated citation or currentness claim.
