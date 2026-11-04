# Situation-based skill routing

## Scope and decision

Approved request: implement the preceding routing recommendation. Apply a compact policy in
this repository and publish reusable adoption guidance; preserve independent skills, upstream
sources and standalone installs. Machine-wide configuration is outside this repository and
requires separate owner approval; the repository change contains no host configuration. No new dispatcher, dependency or umbrella skill is needed.

Compared alternatives: a global umbrella reduces metadata entries but hides unrelated capabilities
behind another selection step; domain-specific grouping is useful only where modes already share
a purpose. Chosen: precise independent descriptions plus a phase-aware policy. Over a five-year
horizon, keep it host-neutral and test observed failures rather than maintain a duplicate catalog.

## Implementation plan

1. Reconcile origin and preserve unrelated handoffs.
2. Review descriptions and existing instruction ownership; change only demonstrated ambiguity.
3. Add canonical routing policy and linked adoption guidance; regenerate the public guide.
4. Freeze routing examples; compare baseline/candidate selection and record evidence limitations.
5. Run site/document checks, adversarial review and independent verification; fix real findings.
6. Commit and push the verified unit on its working branch. Release gates and merge authority
   remain separate from local verification.

## Run notes

- Origin matched the starting commit `7587b764d9d909b39a4c75a814cacf2dfee1fcd9` after fetch.
- Existing 23 root skill descriptions already distinguish the important overlapping capabilities;
  no mass rewrite is justified. Vendored collection skills are not hand-edited.
- Existing guide already advocated progressive disclosure. This change adds phase transitions,
  explicit-only trigger preservation, unavailable-skill handling and an adoption boundary.
- Initial non-escalated Git fetch was denied by the sandbox; the approved retry succeeded.
- Initial Codex CLI availability probe could not confirm an account; no behavioral result inferred.
- Selection probes and native end-to-end instruction compliance must be reported separately.

See [tests.json](tests.json) for check status. Raw provider outputs stay in ignored scratch.

## Evaluation results

Four initial supplied-catalog runs used the same 14 frozen synthetic requests and 23 root
skill descriptions, with expected answers excluded from prompts. Claude baseline/candidate:
14/14 exact primary matches each; Codex baseline: 14/14; candidate: 13/14. After the review
clarification, candidate reruns remained Claude 14/14 and Codex 13/14. The unchanged mismatch
is `review-only`: the frozen answer is expert review, while Codex chooses production readiness
for a deployment-plan review and explicitly forbids edits/deployment. That is a plausible
specialist interpretation, not permission escalation. The frozen expected answer was not changed.
All runs included both security and production-readiness gates for the staging request.

These are single-run selection probes, not an improvement claim. Claude ran with ambient host
instructions, so its baseline is not an isolated no-policy control. Codex's supplied-catalog
probes disabled project-doc loading, but host/runtime context was not normalized across providers.
The 23-skill catalog does not establish behavior against the entire installed host catalog or
all 42 vendored collection skills. No token savings or statistically reliable effect is claimed.

A native Codex explanation task (repo-file loading, not proof of host catalog discovery) did read `skills/mneves-eli5/SKILL.md` before answering with
an audience-appropriate OAuth example. This establishes one real load-and-answer path only;
phase transitions and every other skill's procedural compliance are not certified.

## Review disposition

Two fresh Opus contexts reviewed Standards and Spec separately. Accepted: explicitly preserve
user/host mandates, follow-up skill requests, phase-change precedence, strict output formats,
and missing-capability authority; eliminate the duplicate copyable policy. The guide now points
to the canonical AGENTS section. Unsupported concerns were checked: plain `ship` and `full-stop`
restrictions are in the shipped descriptions; build-site rewrites the guide link to GitHub;
frozen cases and actual results exist (they were omitted from the first review packet).
No source executable changed, so source complexity measurement is inapplicable.

## Follow-up controls and limitations

The separately frozen `cases-v2.json` adds multiple acceptable plan-review routes, explicit
required gate names, a named explicit-only invocation, a mid-task skill request and a missing
mandatory gate. It does not replace or reclassify `cases.json`. The v2 probes exposed unnecessary
blocking when an optional named skill was missing. The final policy explicitly continues
ordinary authorized work unless the user required that skill exclusively.

`cases-final.json` freezes that optional-versus-mandatory distinction before the acceptance
runs. Codex satisfied all 17 controls. Claude satisfied 16/17: it omitted production readiness
from its additional-skill list for the staging request. This is retained as FAIL for that
selection control, not recast as a pass. Both correctly continued optional work and blocked the
missing mandatory security gate. These limited probes cannot prove actions or gate execution;
read-only boundaries and full lifecycle compliance remain untested by classification alone.

The native Claude explanation task read the repository's eli5 skill too. Both native explanation
paths loaded repository files; neither proves the installed host catalog supplied that path.
The native prompts name no specific skill. Raw prompts, outputs, review packets, model usage and
logs are retained privately under `.scratch/skill-routing-implementation/`. Probe configuration:
Codex requested `gpt-6.1-sol`, reasoning high; Claude requested Opus, effort high, and its returned
model usage identifies `claude-opus-5-5`. No cross-provider performance comparison is made.

Second-round review dispositions: preserve the first exact-match mismatch and baseline contamination
limits; gate-list observations in the first set are descriptive, not frozen gate assertions;
freeze explicit gate expectations in the follow-up set; record actual loading separately from
host discovery. The table now names production readiness and its overlap with general plan review.
The release-file consistency and defaults-block checks passed. Review status is synchronized below.

Local browser check: the generated guide rendered at 390px and 1440px with no document overflow;
its routing link resolved to the intended GitHub main URL. That new target will be available only
after merge. This was local HTTP preview, not a deployed preview or production check. No layout,
style or interactive behavior was changed. The existing skill installer still discovered 23 root
skills; collections remain separate.

The first independent mneves-verify pass returned PASS for the five local implementation criteria,
with bookkeeping corrections and explicit limits. Those corrections are incorporated; the final
reverification checks the amended policy and completed record. Production and machine-wide adoption
are separate authorization boundaries. At that checkpoint no global configuration had been changed.

The native read-only Claude staging-plan task read the deployment, security and production-readiness
procedures and explicitly identified both mandatory gates, with blockers and no claim they passed.
This closes the targeted procedure-reading check; it does not erase the supplied-catalog omission
or certify the entire deployment plan. No deployment or gate execution occurred.

Final model review scope is the repository policy and documentation only. The machine-wide
adoption proposal is unapplied and outside that scope; owner approval is required before changing
external configuration. This implementation does not claim a production release.

## Evidence packaging correction

The full reverify passed policy, independence of skill entrypoints, adoption boundaries and
site/version consistency, but failed criterion 4: its allowed evidence packet lacked Claude
Read-tool traces, and the native plan's returned model usage included a second model not named
in this record. That FAIL is retained in the private `verification-final.json` receipt.

Scoped transcript excerpts now retain only repository Read calls and their matching results in
`claude-native-eli5-read-trace.json` and `native-gates-read-trace.json` under the private evidence
directory. They exclude reasoning and unrelated messages. The native plan's model usage includes
both `claude-opus-5-5` and `claude-fable-5-1`; the second model's role is not established. The
explanation run reports only `claude-opus-5-5`. No single-model claim is made for the native plan.
A fresh evidence acceptance checks all five local criteria with the complete packet; previous
FAIL receipts and the 16/17 classification result remain intact.

## Local acceptance

Fresh independent evidence acceptance returned PASS on all five local implementation criteria.
The native plan trace retains 9 entries for 5 distinct Read call ids; repeated call ids remain
visible rather than being silently deduplicated. The native plan prompt is now packaged too.
The earlier verifier FAIL and the Claude 16/17 selection failure remain part of the evidence.
This is acceptance of the policy, documentation and truthful evaluation, not universal routing
reliability or production acceptance.

After the owner instructed continuation on the exact host proposal, the shared host contract was
updated separately. Existing workflow/model rules were moved verbatim behind absolute reference
links, section anchors and consumer symlinks were preserved, and the canonical file fits its size
budget. A pre-existing unrelated host edit was preserved. Those private host files are not in
this repository's diff. The task-owned browser and preview server were stopped; the 158 MiB
browser profile was removed. Small private evidence is retained.
