# Sources and evidence limits

Last checked: 2026-10-02. Re-fetch current guidance before acting on crawler or
provider policies; this is an evidence map, not a permanent ranking specification.

## OpenAI

- [Crawler documentation](https://developers.openai.com/api/docs/bots)
  ([Markdown](https://developers.openai.com/api/docs/bots.md)): independent search,
  training and user-initiated agents; searchbot access and approximate robots-update
  propagation. Current searchbot ranges: <https://openai.com/searchbot.json>.
- [ChatGPT search](https://help.openai.com/en/articles/9237897-chatgpt-search):
  allow searchbot and its published IPs; relevance/reliability matter; no guaranteed
  placement.
- [Publisher FAQ](https://help.openai.com/en/articles/12627856): search discovery,
  summaries/snippets, `noindex` visibility to the crawler and ChatGPT referral UTM.

These sources do not establish `llms.txt`, a particular schema type, fixed paragraph
length, training permission or keyword density as a ChatGPT ranking requirement.
An official docs site serving `llms.txt` does not prove ChatGPT Search uses it for
ranking. Search partners exist; do not describe any single partner's index as the
exclusive ChatGPT index or promise submission guarantees inclusion.

## Cloudflare, only when relevant

- [AI bot policies](https://developers.cloudflare.com/bots/additional-configurations/block-ai-bots/):
  Search, Agent and Training classifications and the changing legacy defaults.
- [Bot Management API](https://developers.cloudflare.com/api/resources/bot_management/):
  actual configuration fields, including `ai_search`, `ai_user`, `ai_training`,
  legacy `ai_bots_protection` and preference synchronization.

Read these together. `ai_search: "disabled"` describes a disabled blocking policy,
not a broken search service. A legacy AI-block switch alone does not establish that
OAI-SearchBot is blocked. Settings and actual edge outcomes are different evidence.

## Third-party article evaluated

[NoCodeLife, 2026-01-23](https://www.nocodelife.com/how-to-make-your-website-show-up-in-chatgpt-answers/).

Retain the useful recommendations for readable HTML, semantics, canonical metadata,
discovery files and clear opening explanations. Treat its `llms.txt` emphasis and
ChatGPT ranking implications as unverified. Replace blanket crawler permission with
purpose-specific policies and truthful authorship/schema decisions. Do not copy its
embedded agent prompt into standing instructions or treat it as authorization.
