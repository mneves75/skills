# SRE workflows: focused skills, prompts and evidence

## Status

- Planned at: `53ea5adaf420fa03e17559d0c31cbbfb0a89eb76`
- Branch: `feat/sre-workflows`
- Status: PROMPTS/GUIDES CANDIDATE — both entrypoints retired after R4; production BLOCKED
- Priority: P1
- Dependencies: none; reuse the released readiness, security, ship and verify contracts.

## Observable goal

Make SLO design and incident learning discoverable as two small, portable procedures, with
eight reusable prompts and bounded integration into existing skills. Demonstrate usefulness
against the simpler prompt-only approach before retaining either entrypoint. Preserve existing
security/readiness verdicts, stage policy, authority and optional sibling behavior.

The owner approved implementing the reviewed plan and requested review, independent proof,
documentation, version/changelog, branch delivery, merge and applicable release delivery. The
main coordinator owns review, merge, security/readiness gates, publication and cleanup. The
implementation worker never deploys, publishes, merges or edits other projects/host settings.

## Current evidence and chosen approach

The two-entrypoint experiment is complete and failed its retention rule. R4 improved three
paired cases but introduced new wrong behavior in each skill; discovery and correct negative
routes did not offset those failures. Apply the pre-agreed prompts/references-only fallback:
retain eight explicit templates and the complete guides under `docs/sre-guides/`, remove both
installable entrypoints and their four sibling routes, and restore the catalog to fifteen.
R1–R4 failures stay in the evaluation history; they are not acceptance of error-free prompts.

Further instruction patches were rejected after the bounded correction loops still produced
unsupported facts. The broader orchestrator remains rejected for duplicated policy. Five years
out, explicit guides with preserved evidence contracts and failed experiments are more useful
than growing automatically loaded instructions whose benefit did not meet their own rule.
The original scope/procedure below records the experiment; the final delivery scope is this
fallback. Production remains subject to exact-candidate security/readiness gates and authority.

The source release is 1.37.0. `mneves-production-readiness` already owns OBS-01..OBS-10,
BR-01..BR-04, integration correctness and evidence scopes. The staging readiness set remains
DM-02, DM-03 and TST-05, with security a separate gate. Do not create another SRE verdict or
require every project to adopt an SLO. A draft objective cannot become a release blocker.

Choose two candidate entrypoints plus concise references/prompts. Rejected alternatives:
one monolithic SRE orchestrator (duplicated policy/context overhead), and prompts/references
only (simpler but potentially less discoverable). Retain the latter if pilots show no useful
increment from an entrypoint. Do not make productivity, reliability or prevention claims from
small synthetic evaluations. Five-year principle: preserve evidence/authority contracts and a
merge/retire path; keep provider/model details out of the new procedures.

## Historical experiment scope

- `skills/mneves-slo/`: entrypoint, two routed references and original synthetic example.
- `skills/mneves-incident-learning/`: entrypoint, evidence/learning reference and original
  incident/action examples.
- Narrow routes/examples in `mneves-production-readiness`, `mneves-ship-deploy`,
  `mneves-verify`, and `mneves-agent-readiness`. Read their complete affected references first.
- `docs/sre-prompts.md`: eight compact Task/Acceptance/Constraints/Delivery/Target templates.
- `docs/specs/sre-workflows/spec.md` and a concise evaluation record with reproducible synthetic
  inputs and honest proposed/observed status. Use the existing local tracker; no GitHub issues.
- Catalog/HOWTO/AGENTS tree, relevant PRODUCT/MEMORY/FOR_YOU_KNOW/usage docs, VERSION,
  changelog/badge, NOTICE if required, and generated site. Keep CLAUDE.md as its import pointer.
- Site content and discoverability for the new procedures using the existing design. Any
  design adjustment must solve a concrete reviewed problem, preserve accessibility and stay
  dependency-free; no unrelated redesign or framework.
- Proposed release 1.38.0, after rechecking remote/main/tags. Another session's dependency
  updates, existing worktrees/branches, vendored collections and unrelated handoffs are excluded.

## Historical experiment procedure

1. Read root instructions, README, status/memory, PRODUCT/DESIGN, contribution and CI policy,
   the existing skill surfaces and their tests. Run the drift check:
   `git diff 53ea5adaf420fa03e17559d0c31cbbfb0a89eb76 -- <in-scope paths>`.
2. Docs first: create the normative spec, evaluation matrix and minimal project-independent
   contracts. No private project paths/names, session identifiers, book text or customer data
   may enter tracked files. Attribute general concepts through public primary references.
3. Run a meaningful red control before completing the new catalog/skill surfaces (existing
   build-site tests and discovery should expose missing catalog/guide/skill consistency).
   Preserve its actual result; do not invent a failure or write tautological text tests.
4. Implement the two focused candidates and eight prompts. Keep SKILL.md short, under 500
   lines; valid allowed frontmatter; name equals directory; references linked directly once
   from the entrypoint. A single skill bundle must not require unshipped tools/siblings.
5. SLO behavior: good/eligible specification separate from collection implementation; observe
   user success/freshness rather than HTTP 200; weighted event counts; missing/zero telemetry
   unknown; `N>0` and `0<s<1` for normalized budget/burn; 100% requirement cannot divide by
   zero. Third-party failures remain in customer impact. Correctness/security are not allowed
   loss. Targets remain draft until adopted; no automatic SLA, feature disable or release gate.
6. Incident behavior: distinguish real incident, near miss and workflow/test event; source
   identity, time/clock limits, planned vs executed actions, reported vs observed claims;
   contributing conditions and alternatives, local decision context, what worked and luck;
   owned/dated actions with effectiveness proof. Active mitigation stays with existing runbook.
7. Integrate conditionally using existing control IDs and evidence scope. Preserve staging,
   prototype/live/contract policy, exact candidate approval, security binding and deploy/tag
   order. Installation checks distinguish entrypoint hashes, full package resources and actual
   runtime discovery. Do not overwrite installed host skills.
8. Update catalog/docs/site coherently and run affected gates. New dependencies/executables
   are not justified by this Markdown-first change. Never alter model IDs or claim a new
   verification date without current primary evidence. Report a policy/tool blocker honestly.
   On 2026-10-18 the coordinator checked the existing routing IDs against the current official
   [Claude model catalog](https://platform.claude.com/docs/en/models/overview) and
   [OpenAI model catalog](https://developers.openai.com/api/docs/models). Refresh only the
   truthful Defaults verification date to match the new release; model assignments stay intact.
9. Freeze the candidate for parent-owned behavioral evaluations, improve-deep review, the two
   code-review axes and independent mneves-verify. Address precise corrections in the same lane.

## Experiment evaluation and acceptance

Use synthetic/public cases inside this repository, not customer data or changes to another
project. Compare prompt-only vs candidate for Worker freshness, local data completeness and
native/durable recovery semantics. Record consumer/model/source identity and distinguish a
document exercise from actual deployment/device/recovery proof. Never report unrun evaluations.

Cover weighted counts, no data, 100% targets, provider failure, stale 200 responses, a planned
deploy without execution, successful near miss, ineffective backup-only action, prompt
injection in a log, absent sibling, and nearby non-trigger tasks. Main will execute cross-host
invocation checks. Retain a skill only if it adds useful discoverability/procedure without
overlap; no causal cost/time or reliability gain claim.

Advisor precision: keep period-budget and burn-window populations separate. Synthetic case:
99.9% objective; period 1,000,000 events/100 failures consumes 10% of that period's budget;
contained hour 1,000 events/20 failures has burn rate 20. Do not call that 2,000% monthly
budget consumption. Completeness needs an independent expected-source denominator (99/99
observed is not complete when 100 were expected; unknown expectation means unknown coverage).
Compare competent baseline/candidate with the same facts/access/model/criteria. Explicit use
is not spontaneous discovery; equal behavior can justify an entrypoint only when an actual
discovery/maintenance benefit is observed and recorded without a causal savings claim.

Documented gates (re-read current CI; run only applicable extras):

```bash
npx skills@latest add . --list
npx -y skills-ref@0.1.5 validate skills/mneves-slo
npx -y skills-ref@0.1.5 validate skills/mneves-incident-learning
python3 tools/scripts/check-readiness-catalog.py
bash tools/scripts/check-readiness-catalog.test
python3 skills/mneves-ship-deploy/scripts/run-tests.py
bash skills/mneves-ship-deploy/assets/release-guards.test.sh
bash tools/scripts/check-defaults-block.sh
bash tools/scripts/build-site.test
tools/scripts/build-site.sh
git diff --exit-code -- site/
```

The final diff check means generated files are current after their intended changes are staged
or compared against a pre-generation digest; do not confuse intended generated changes with
stale output. Run real browser desktop/mobile and keyboard checks on changed published content.
No application builds or device interactions are needed for Markdown procedures.

## Stop conditions and recovery

Current deployment inventory: `.github/workflows/static.yml` publishes GitHub Pages directly
from `site/**` pushes to main and defines no staging target or CI dependency. The final tree
must pass release gates before that push. Local/browser preview is QA evidence, not staging;
do not fabricate a beta deployment tag or introduce another provider merely to claim staging.

Stop only the affected action for unknown destructive authority, credential/data access,
concurrent overlapping changes, an unavailable required tool or an unmet release gate. Continue
independent permitted work and return the exact failure. Never weaken a test/guard, backdate a
release, fake model verification or print secrets to get green. Existing source behavior and
all unrelated changes stay intact. Working-branch commits use explicit task-owned paths and
Conventional Commits. Parent owns all remote writes and final cleanup.

## Worker report

Return COMPLETE or STOPPED, changed paths, actual red/green commands and exit results, required
unrun checks, reasoning for retained entrypoints, source/provenance limits and exact blockers.
Do not declare shipped or independently verified. Keep verbose logs in task-owned ignored
scratch and do not copy private planning evidence into the public repository.
