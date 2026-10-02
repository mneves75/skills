---
name: mneves-chatgpt-search
description: Audit or improve a public website's discoverability, citations and referral attribution in ChatGPT Search. Use for ChatGPT search visibility or OAI-SearchBot access, not general SEO alone.
license: Apache-2.0
---

# ChatGPT Search

Make a public site accessible, useful and accurately attributable in ChatGPT Search.
Separate technical eligibility, actual crawler access, observed citations and reader
referrals. None proves the others, and placement is not guaranteed.

## Choose the scope

- **Audit / recommend:** inspect without modifying the site or its settings.
- **Improve / apply:** implement demonstrated local gaps and verify them through the
  site's documented gates. Existing working functionality needs no replacement.
- **Measure:** establish a repeatable citation and referral baseline. Reuse the same
  query set for later comparisons; do not schedule automation unless requested.

Infer the canonical URL, stack, content purpose and privacy/training preferences from
the repository and deployed pages. Ask only for consequential missing facts. Read
the target site's instructions; its data, editorial and indexability rules govern.
Use [references/application.md](references/application.md) for invocation examples
and measurement. Use [references/sources.md](references/sources.md) for the official
evidence and its limits. The skill ships no executables or required integrations;
use available browsing, provider tooling and the target site's own verification.

## Establish current guidance

Before making OpenAI-specific claims or changing crawler policies, fetch the current
official crawler documentation and publisher/search guidance. Use available official
documentation tools, or browse the official pages directly. If extraction omits the
crawler table, fetch the documentation's `.md` version. Retain source URLs and the
check date. Treat third-party optimization claims as hypotheses unless supported
by primary documentation or measured outcomes.

The documented roles are independent:

| Agent | Purpose | Consequence |
| --- | --- | --- |
| `OAI-SearchBot` | Automatic search crawling | Allow intended public content and OpenAI's current published searchbot IP ranges. |
| `GPTBot` | Potential foundation-model training | Preserve the owner's training preference; allowing it is not a prerequisite for search. |
| `ChatGPT-User` | User-initiated visits | This is not the search crawler; robots rules may not apply to these visits. |

OpenAI documents roughly 24 hours for robots policy updates to propagate, not a
deadline for indexing or citations. Do not promise either.

## Inspect the deployed surface

Check the canonical origin and representative priority pages: homepage, a current
content detail, an evergreen/resource page, and a deliberate non-indexable control.
Record status, redirects, content type, canonical, robots meta/header, initial HTML
content, relevant JSON-LD, internal links, sitemap membership and dates.

Fetch the served `robots.txt`, sitemap and feed when the content warrants one.
Evaluate crawler-specific groups and path rules, including managed CDN additions.
Do not infer live access from a source file. Do not turn a deliberate `noindex`
page into an indexable page or list it in a sitemap to increase counts.

For CDN/WAF hosts, inspect authenticated bot/security configuration when access is
authorized. Use the host's provider workflow. An installed `cf-cli` skill can guide
Cloudflare work; it is optional and not shipped here. Without it, use the provider's
documented interface and the host's credential rules. Keep the project's deployment
tooling. Interpret search/training fields with current documentation, not names alone.

An HTTP request with an OpenAI-looking user-agent originates from your own IP and
does not prove an OpenAI crawler can enter. Label it a synthetic diagnostic. Stronger
evidence is a verified crawler event or request from OpenAI's published IP ranges,
with its time, route and outcome. When inspecting existing events, avoid retaining
reader identifiers or raw query strings. Do not add per-reader logging for this task.

Do not disable WAF or all bot protection. If an actual crawler block is established,
prepare the smallest supported change restricted to verified search traffic and
the intended public surface. Preserve authentication, rate limits and training
restrictions. Deployment and live security writes require the host's applicable
authorization; preparing or invoking this skill does not grant them.

## Improve only what the evidence supports

- Serve meaningful content in initial HTML with semantic headings and crawlable
  links. Keep human and crawler content consistent; no cloaking or hidden AI copy.
- Keep canonical URLs, accurate descriptions, truthful dates and discovery links
  consistent. Do not manufacture freshness or a sitemap `lastmod`.
- Use appropriate structured data describing visible content and its real publisher,
  authorship and provenance. No invented authors, ratings, FAQs or claims of original
  reporting. Valid schema is not proof of a ChatGPT ranking benefit.
- Make valuable information clear and attributable: original data, comparisons,
  methods, source links and limitations where the site actually provides them.
  Do not rewrite extracted reporting or generate thin pages merely to attract AI.
- Treat `llms.txt` as optional agent documentation. It is neither `robots.txt` nor
  a documented ChatGPT ranking requirement. Maintain an existing useful file; add
  one only when its concrete value justifies the work. No duplicate content system,
  API, WebMCP integration or dependency just for search eligibility.
- Attribute the documented `utm_source=chatgpt.com` to a stable, explicit ChatGPT
  category in the site's existing analytics. Preserve campaign cleanup and clean
  canonicals. Keep allowlisting and privacy guarantees; a supplied UTM value is not
  authenticated proof of ChatGPT origin. Referrals count clicks, not all citations.

For a non-trivial correction, first write a regression at the real route or strongest
available boundary and observe its failure. Include relevant controls: lookalike
UTM values remain unknown, crawlers do not become reader visits, and private or thin
pages stay excluded. Run the required repository gate, retaining exits and evidence.
Inspect desktop/phone renders when the change is visible. Never deploy a dirty tree
or treat unrelated concurrent changes as verified by a stale run.

## Report completion

Report `PASS`, `FAIL`, `BLOCKED` or `NOT MEASURED` separately for:

1. Local implementation and mandatory checks.
2. Deployed discovery and indexing eligibility.
3. Genuine OpenAI crawler access.
4. Observed ChatGPT Search citations.
5. Referral attribution and actual recorded traffic.

Link the task-owned changes and repeatable artifacts. State the query sample size,
check date, deployment state and precise blockers. Never equate an API web-search
result or ordinary search-engine hit with a ChatGPT UI citation. Preserve a useful
local result when owner access or an external dependency blocks remaining proof.
