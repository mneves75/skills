# Applying ChatGPT Search

Invoke `mneves-chatgpt-search` from the target site's repository. A user-wide install
is reusable across repositories; it does not run against every site or publish changes.
Start a new agent session if discovery has not refreshed. If the host cannot discover
the skill, point it at the installed `SKILL.md`.

## Install and invoke

```bash
npx skills@latest add mneves75/skills --skill mneves-chatgpt-search -g -y
```

In Codex:

```text
Use $mneves-chatgpt-search on https://example.com in this repository.
Inspect the site's audience, priority pages, crawler/training preferences and
existing analytics. Fix demonstrated local gaps, run the documented gates and
report crawler access, citations and referrals separately. Do not deploy.
```

In Claude Code, use `/mneves-chatgpt-search`, or name the skill in a request.
For another agent, use its named-skill invocation or point it to `SKILL.md`.

For a public site with no source checkout:

```text
Use mneves-chatgpt-search to audit https://example.com without changes.
Return prioritized findings with observed URLs and status; mark CDN settings
and genuine crawler events blocked if authenticated access is unavailable.
```

Preserve the site's actual constraints. For an aggregator, do not claim original
reporting or invent authors; retain provenance and deliberate indexability gates.
For a product, documentation, service or commerce site, use its real content purpose.
Do not fabricate authority scores, analytics baselines or crawler history.

## Citation baseline

Choose 5–10 useful audience questions before observing results. Include discovery
and informational intents. Keep branded/direct-URL questions separate: those test
retrieval rather than unprompted discovery. For a documentation site, questions might
cover its supported workflows; for a news comparison site, how to compare coverage
or understand its methods. Tailor questions to real content rather than inventing it.

Use fresh ChatGPT conversations with Search enabled, keeping language, region,
account/settings and query wording as consistent as possible. Prefer temporary
chats or disable memory when available to reduce prior-site exposure. Run each
query three times. Save each actual answer and cited URLs/screenshots in the
site's private evidence directory. Record every run, including no citation,
errors and incomplete answers. If UI access is unavailable, report that blocker.

Suggested CSV columns:

```text
checked_at,query_id,run,surface,search_enabled,language,region,brand_mentioned,domain_cited,cited_urls,artifact,status
```

Report citation rate as cited completed answers / completed answers, with numerator,
denominator and excluded/error counts. Count a citation only when the answer cites
the intended domain, not when it mentions the brand or links to another site's
description of it. Report mentions separately. Do not count an API web-search test
as ChatGPT UI evidence; label that surface explicitly if used.

Repeat the same queries after publication and a reasonable discovery period, such
as weekly checks over four weeks. This is an experiment design, not an indexing SLA
or an automated recurring job. Record content/deployment changes; sample variation
alone does not establish that a change caused improved ranking.

## Referral baseline

Use existing privacy-preserving analytics for `utm_source=chatgpt.com`, mapped to
the site's explicit ChatGPT category. Confirm with a synthetic request only in a
local/test dataset; never manufacture live reader traffic to prove instrumentation.
Referrer data and UTM counts can both be incomplete. Historical unknown-source records
cannot safely be reclassified without evidence that was not retained.

After an authorized deployment, use the site's existing traffic report for a fixed
period, such as seven days. Follow its approved credential workflow; never print
secrets or replace the analytics vendor just for this task. Validate instrumentation
locally before claiming the deployed implementation changed.
