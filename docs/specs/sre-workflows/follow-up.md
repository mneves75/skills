# SRE workflows: proposed follow-up

Companion to [spec.md](spec.md), [evaluation.md](evaluation.md) and [review.md](review.md).
Round 3 ended that correction loop with BEHAVIOR (criterion 4) FAIL, and the three items below
were written then as proposals. The owner authorized a new loop: items 1 and 2 were executed in
round 4, which still failed criterion 4 and retention for both skills, so both entrypoints were
retired into `docs/sre-guides/`. Item 3 is rescoped to the guides and prompts and is pending.
Each item keeps its original text below its status; paths under `skills/mneves-slo/` and
`skills/mneves-incident-learning/` are where the files lived then. Tracked here as local
Markdown; no GitHub issue is opened.

## 1. Bounded absence for every claim

Type: change
Status: executed; acceptance 3 failed
Blocked by: 2 (for its final full run only)

Round 4 outcome: the source correction landed and the packages were bound at `bae3fd4`. The
round 3 absences did not recur in the candidate's E9 and E18, and the export-gap regressions
met, but new unsupported claims appeared (candidate E2 and E10, two Claude regressions and two
Claude probes), so acceptance 3 failed. Acceptance 2's validator paths no longer exist after the
retirement. Details: "Round 4 (retention decision)" in [evaluation.md](evaluation.md).

- **Failure it prevents.** Round 3's E9 answer, the Claude explicit-invocation probe and the E18
  answer each stated an absence as fact (a missing safeguard, a data check that never ran, an
  export never attempted) without a source that said so.
- **Change.** Extend the existing bounded-absence rule from timeline and responder context to
  every contributing condition, action-history claim and export or attempt claim. A claimed
  absence needs a supplied source that shows it; an artifact that was not supplied means "not
  observed" or `unknown`. A speculative safeguard becomes a proposed action or a question. Reuse
  the current rule owners and templates; no new skill, framework or gate.
- **Files and responsibility.** Rule owners first:
  `skills/mneves-incident-learning/references/evidence-and-learning.md` (contributing conditions,
  action history) and `skills/mneves-slo/references/specification.md` (completeness and export
  attempts). Then one-line pointers in both `SKILL.md` files, the affected prompts in
  `docs/sre-prompts.md` and the matching contracts in `spec.md`. The example review changes only
  where it states an absence. Builder: the implementation seat; reviewer: a different model.
- **Acceptance.**
  1. New scored variants under the existing IDs reproduce the three bad outputs: E9 (absent
     safeguards), an explicit restore probe (no data check, chat as completion signal) and E18
     (never attempted). Positive controls cover an absence that a supplied source does show,
     which must still be reported as observed. Each variant is added alongside the frozen
     criteria; recorded failures stay as recorded.
  2. Source checks pass: `agentskills validate` (the hashed PyPI reference validator from
     `AGENTS.md` Commands, never the npm `skills-ref`) on `skills/mneves-slo/` and
     `skills/mneves-incident-learning/`; `bash tools/scripts/build-site.test`; the other CI gates the change touches.
  3. A fresh, source-blind full E1–E19 run on both arms, under item 2's method, meets every new
     variant, keeps E2, E3 and E13 met, and adds no new wrong behaviour.
- **Rollout and recovery.** Documentation only; nothing deploys. If the run regresses, revert the
  rule edits and keep the failure in `evaluation.md`.
- **Stop conditions.** Stop and report when the fresh run reproduces any invented-absence claim,
  or after the bounded verification loop allows no further round; another loop needs the
  owner's explicit override.

## 2. Evaluation method repair

Type: change
Status: executed with one deviation
Blocked by: none

Round 4 outcome: E15 was scoped, before any answer, to the active native consumer profile
instead of physical absence from the host, because removing unrelated global packages was
neither required nor authorized; Claude returned a real "Unknown skill" (PASS), and Codex has
no equivalent call (N/A). E16 used a linked synthetic dashboard: 4 of 4 non-triggers per host
passed and both hosts read the value. Change 3 was not adopted for the paired comparison, which
stayed one identical full prompt per arm; the probes and regressions ran standalone. Call logs
and inputs stay in the private run record.

- **Failure it prevents.** E15 was tested as unavailability in a project-only profile while the
  frozen criterion asks for physical absence from the host; E16 had a supplied dashboard figure
  but no dashboard link. Both stayed partial for method reasons.
- **Change.**
  1. E15: run the consumer in an isolated profile that physically lacks the readiness sibling
     (a fresh temporary home or container holding only the two target packages), on both hosts,
     without uninstalling anything global.
  2. E16: provide an actual bounded, read-only dashboard link with a known value (for example a
     local static page), and keep standalone call logs on both hosts.
  3. Prefer case-separated runs at a bounded cost over one large bundle, so cases cannot
     interfere; both arms get the same method.
- **Files and responsibility.** `evaluation.md` gains the method as additions; the frozen
  criteria, the round 1–3 records and their failures are kept verbatim, and no answer already
  judged is rescored or passed retroactively. Harness inputs and logs stay in the coordinating
  session's private evidence.
- **Acceptance.** A dry run of each fixture shows the sibling absent from the isolated profile
  (a real "unknown skill" or missing-file result there, the global packages untouched) and the
  dashboard link returning its known value; the reviewer can read the call logs for every
  standalone probe.
- **Rollout and recovery.** The isolated profile and local page are temporary and removed after
  the run; nothing on the host is reconfigured.
- **Stop conditions.** Stop if physical absence cannot be shown without a global uninstall;
  report that instead of weakening the criterion.

## 3. Final checks and release decision

Type: gate
Status: pending, rescoped
Blocked by: 1, 2, or an owner decision to proceed without them (1 and 2 executed)

Rescoped after the retirement: the candidate is now the guides and prompts, with no skill
entrypoint, so no skill validator or BEHAVIOR run applies and no runtime reliability is
claimed. What remains is the site rebuild and its test, the CI gates on the exact candidate, a
recheck of the fifteen-card catalog in a browser, the security gate and the owner's merge
decision. The text below is the original proposal.

- **Failure it prevents.** Treating a green source gate, a PASS on a local preview or a
  successful process exit as release readiness.
- **Change.** Fresh independent SOURCE and BEHAVIOR checks on the frozen candidate, the actual
  gates, exact-candidate CI, the security gate and a binding readiness run, following the
  canonical bounded verification loop or an explicit owner override.
- **Files and responsibility.** Evidence goes to the ignored release records and the pull
  request; `docs/readiness/ledger.md` and `plan.md` change only with observed results. The
  restricted security, provider and operator gaps stay in the readiness plan with a named owner,
  evidence and expiry requirement; their details stay private.
- **Acceptance.** Exact-candidate CI green; a security gate record for that commit and target
  with no open block, or each block waived there by a named owner with an expiry; a binding
  readiness record; an independent verification result.
- **Rollout and recovery.** No production merge before the owner's exact approval and the
  clearance of every open block. A failed check leaves the current production site untouched.
- **Stop conditions.** Stop at any open block or missing owner approval; never self-waive.
