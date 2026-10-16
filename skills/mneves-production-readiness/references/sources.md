# Sources

The controls state durable outcomes. Dated facts live here. On each baseline, recheck any source
whose fact a verdict depends on (a standard's edition, a provider limit, a legal date); if the
check is impossible, say so and treat a currentness claim as NOT TESTED. Provider documentation
for the target's actual stack outranks these general sources. Last checked: 2026-10-15.

## Readiness practice

- [AWS Operational Readiness Reviews](https://docs.aws.amazon.com/wellarchitected/latest/operational-readiness-reviews/wa-operational-readiness-reviews.html):
  checklists distilled from incidents, run before launch and at least yearly, with different
  checklists per occasion; findings without a mitigation are fixed before launch. Basis for the
  baseline, the delta and project-local controls.
- [Google SRE launch coordination checklist](https://sre.google/sre-book/launch-checklist/):
  architecture, capacity and load tests, failover and backups, monitoring, security, automation
  and staged rollout, growth, external dependencies, schedule.
- [SRE workbook: alerting on SLOs](https://sre.google/workbook/alerting-on-slos/): page on
  error-budget burn with multiwindow, multi-burn-rate alerts (OBS-04).

## Data and delivery

- [PostgreSQL explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html),
  [ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html) and
  [`lock_timeout`](https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-LOCK-TIMEOUT):
  lock levels per statement, online index builds, rewrite rules (DM-03).
- [CA/Browser Forum ballot SC-081v3](https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/):
  public TLS certificate validity falls from 398 days to 47 days in steps from March 2026 to
  March 2029; secondary summaries give 200 days from 2026-03-15 and 100 days from 2027-03-15
  (DEL-09).
- [IETF Idempotency-Key header draft](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/):
  still an Internet-Draft; cite it as a pattern, not a standard (DC-05).

## Email

- [Gmail email sender guidelines](https://support.google.com/a/answer/81126): SPF or DKIM for
  every sender; SPF, DKIM, aligned DMARC and one-click unsubscribe for bulk senders; complaint-rate
  limits (EML-01, EML-02, EML-04).
- [RFC 8058](https://www.rfc-editor.org/rfc/rfc8058): one-click unsubscribe (EML-04).

## Security and identity (owned by the security review)

- [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html), final July 2025: at most
  100 consecutive failed attempts per authenticator with throttling options; timeouts by assurance
  level (SEC-03, SEC-10).
- [Package hallucinations, Spracklen et al., USENIX Security 2025](https://arxiv.org/abs/2406.10279):
  code models suggest packages that do not exist, repeatably; attackers register them (SEC-13).
- [RFC 9116 security.txt](https://www.rfc-editor.org/info/rfc9116): machine-readable disclosure
  contact (SEC-20).

## Privacy, compliance and accessibility

- [ICO right to erasure](https://ico.org.uk/for-organisations/guide-to-dp/guide-to-the-uk-gdpr/individual-rights/right-to-erasure):
  erased data may stay in backups only "beyond use" until overwritten (BR-02, CMP-06).
- [HHS HIPAA and cloud computing](https://www.hhs.gov/hipaa/for-professionals/special-topics/cloud-computing):
  a provider that stores or processes ePHI is a business associate even without the key (CMP-03).
- [PCI Security Standards Council](https://www.pcisecuritystandards.org/): PCI DSS v4.0.1 and its
  SAQ A eligibility for pages that embed payment fields (CMP-05). Read the current SAQ and FAQs.
- [European Accessibility Act, Directive (EU) 2019/882](https://eur-lex.europa.eu/eli/dir/2019/882/oj):
  applies to covered services, including consumer e-commerce, since 2025-06-28. Presumption of
  conformity comes only from harmonised standards cited in the Official Journal; EN 301 549 is
  under revision, so check what is cited before claiming conformity (UX-07).

## Model providers

- The provider's own model deprecation page (for example Anthropic's and OpenAI's): notice
  windows and retirement dates for pinned model ids (AI-03).
