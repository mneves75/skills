# Catalog Consolidation, Deduplication & Routing-Hygiene Plan

- **Baseline commit:** `633a2b32f8de02ae0540e3ec160ae98e64c48e46` (`v1.52.0`)
- **Working branch:** `feat/catalog-consolidation-phase1`
- **Status:** Phase 1 executed on branch; Phases 2–3 gated on measured eval data and owner decisions
- **Adversarial reviews completed:** `claude-fable-5-2` (high) and `gpt-6.2-sol` (high), independent fresh contexts

---

## 1. Sharpening the Task (`sharpen` 4-Part Analysis)

Before deciding which skills to keep, slim, merge, or delete, we apply the four-part sharpening framework so the work gets **deeper**, not merely bigger:

1. **What a top professional in agent systems / skill evaluation would do that wasn't asked for**
   - Treat the skill catalog as a **retrieval, routing, and behavioral-lift system**, not a folder of Markdown files to clean up by aesthetic taste.
   - Separate **authority & side-effect contracts** (read-only audit vs code-editing remediation vs mandatory deploy verdict) from **shared implementation** (reference checklists, schemas, helper scripts).
   - Measure **two distinct failure modes** before deleting or merging a single skill:
     1. *Routing confusion*: given only live `name` + `description` metadata across the catalog, does a fresh Claude or Codex session pick the wrong skill, pick an overlapping neighbor, or falsely fire on negative controls (`"Full stop."`, plain `"ship"`, ordinary typo)?
     2. *Zero-skill baseline lift* (*SkillsBench* three-condition methodology): on real tasks, does loading a skill measurably beat the same model running with **no skill**? Skills that add description tokens and routing surface without measurable behavioral lift over a strong base model are the true retirement candidates—not skills that merely share a topic noun.
   - Enforce consequential prerequisites (like security and production-readiness deploy gates) **in executable code where the action happens** (`deploy.sh` / `release-contract-check.py`), rather than relying on the LLM to simultaneously retrieve three sibling skills.

2. **Rawest starting material (instead of digested summaries)**
   - Live raw `skills/*/SKILL.md` (25 root skills) and `collections/pstack/skills/*/SKILL.md` (42 vendored skills) frontmatter bytes, description char counts, line counts, reference trees, and executable scripts.
   - Actual live `agentskills validate` behavior, Claude Code dynamic skill-listing budget mechanics (~1–2% context window / ~16K char fallback floor, `SLASH_COMMAND_TOOL_CHAR_BUDGET`, silent least-used description eviction on overflow), and `agentskills.io` progressive-disclosure spec.
   - Actual cross-reference drift across `README.md`, `HOWTO.md`, `AGENTS.md`, `docs/skill-ledger.md`, and `docs/skill-routing.md`.
   - Frozen behavioral evaluation prompts and raw Claude + Codex JSON outputs stored outside the repo / in `.scratch/catalog-eval/`.

3. **Specific methods and tools**
   - Deterministic catalog scanner & hygiene guard (`tools/scripts/check-catalog-hygiene.py` + planted-violation tests): validates 100% catalog coverage across all 5 index/routing docs, relative link integrity, 1-level-deep `references/` rule, `<500L` body cap, and description char budgets.
   - Pairwise TF-IDF cosine similarity + token-overlap audit across all 67 descriptions to surface candidate collisions.
   - Fresh single-turn, tool-disabled, schema-bound **24-case confusion-matrix eval** (`tools/scripts/catalog-eval.py`) run against both `claude-auto` and `codex-auto` using only live `skills/*/SKILL.md` metadata.
   - Dual-model independent adversarial review (`claude-fable-5-2` + `gpt-6.2-sol`) challenging every proposed merge/deletion before touching public skill names.
   - Phase 2: Blinded three-condition **zero-skill baseline-delta A/B eval** on the retirement shortlist (`mneves-superaudit`, `mneves-expert-review`, `mneves-eli5`, `leaving-pr-comments`, plus `mneves-socratic-tutor` / `mneves-teach-back-srs`) and on repeated permission boilerplate across 17/25 skills.

4. **External proof (other than us) that the result is right**
   - Zero errors from `tools/scripts/check-catalog-hygiene.py`, `.scratch/skills-ref/bin/agentskills validate`, `tools/scripts/check-defaults-block.sh`, `tools/scripts/routing-eval.py check`, `ast-grep`, and `tools/scripts/build-site.test`.
   - Fresh Claude + Codex confusion-matrix eval (`tools/scripts/catalog-eval.py run`) demonstrating clean separation across every contested cluster and 100% rejection of negative controls (`"Full stop."`, plain `"ship"`, ordinary typo) — with raw transcripts preserved in `.scratch/catalog-eval/`.
   - In Phase 2, blinded A/B scores proving which skills deliver statistically/practically meaningful lift over zero-skill baselines and which can be cleanly retired in a semver-major `v2.0.0` release.

### Rewritten Deep Prompt

> Audit the entire `mneves75/skills` catalog (25 root skills in `skills/` and 42 vendored skills in `collections/pstack/`) from raw frontmatter, descriptions, bodies, references, scripts, and routing docs rather than summaries. Ground decisions in 2026 Agent Skills progressive-disclosure mechanics, Claude Code's skill-listing char budget, and SkillsBench-style evaluation:
> 1. Measure exact char/line budgets, pairwise description overlap, doc/routing drift, broken or unshipped references, and repeated boilerplate across all 67 skills.
> 2. Challenge every proposed consolidation with independent dual-model adversarial review (`claude-fable-5-2` + `gpt-6.2-sol`) using contract-boundary first principles: keep separate contracts where authority, side effects, or completion evidence differ; share internals rather than creating multi-mode mega-skills; enforce consequential gates in code.
> 3. Execute non-breaking Phase 1 immediately: sharpen colliding descriptions, fix unshipped references and `docs/skill-routing.md` drift, ship a tested CI catalog-hygiene guard, and run a live 24-case Claude + Codex confusion-matrix eval over the real catalog metadata.
> 4. Report the measured confusion matrix, a first-principles 5-year-out retrospective, and the gated Phase 2/3 plan (zero-skill baseline-delta retirement shortlist, boilerplate purge A/B, and curated install profiles) before deleting any published skill name.

---

## 2. Raw 67-Skill Inventory (`v1.52.0` Baseline)

| Scope | Skill count | Total description chars | Descriptions > 250c | Total `SKILL.md` lines | Notable structural facts |
|---|---:|---:|---:|---:|---|
| `skills/` (root) | 25 | 3,854 (~24% of 16K floor) | 1 (`full-stop`: 334c) | 3,388 | Longest body: `mneves-security` (322L, 21.5KB); 17/25 repeat generic permission/safety boilerplate |
| `collections/pstack/skills/` | 42 | 9,389 (~59% of 16K floor) | 18 (max `why`: 479c) | 2,541 | 42/42 lack frontmatter `license:` (collection has `collections/pstack/LICENSE`); `pstack/babysit` explicitly defers to `babysit-pr` |
| **Combined** | **67** | **13,243 (~83% of 16K floor)** | **19** | **5,929** | Real context-budget pressure comes from vendored/host packs (460 installed locally), not the 25 root skills alone |

### Top Pairwise TF-IDF Description Collisions (Baseline `v1.52.0`)
1. `0.230` — `root:mneves-production-readiness` ↔ `root:mneves-security`
2. `0.213` — `root:babysit-pr` ↔ `pstack:get-pr-comments`
3. `0.195` — `pstack:ketchup-video` ↔ `pstack:ketchup`
4. `0.190` — `pstack:create-formal-verification-skill` ↔ `pstack:maintain-formal-verification-skill`
5. `0.187` — `root:security-audit` ↔ `pstack:thermo-nuclear-review`

### Concrete Repo Defects Found at Baseline
1. `skills/mneves-security/SKILL.md:86` referenced an unshipped `code-review` skill without marking it unshipped or naming `autoreview` (violating `AGENTS.md`: *"Where it names an unshipped tool or a sibling skill, say so and give the fallback"*).
2. `docs/skill-routing.md` was missing 11 of 25 root skills (`council`, `imagegen-frontend-mobile`, `leaving-pr-comments`, `mneves-chatgpt-search`, `mneves-fable-orchestrator`, `mneves-handoff`, `mneves-motion-film`, `mneves-render`, `mneves-superaudit`, `modernize`, `takeover`), and buried `mneves-teach-back-srs` and `security-audit` inside other rows' Boundary columns.
3. Duplicate attack-class reference content exists across `skills/mneves-security/references/attack-classes.md` (126L) and `skills/security-audit/references/ATTACK-CLASSES.md` (130L).
4. `skills/mneves-security/SKILL.md` is 322 lines / 21.5 KB (the heaviest prompt payload in `skills/`), carrying inline procedural detail that belongs one level down in `references/`.
5. `collections/pstack/skills/babysit/SKILL.md` explicitly states: *"When `babysit-pr` is installed, use it instead: this skill adds nothing to it."*

---

## 3. First-Principles & 5-Year-Out Analysis

### Core Principle
> **Treat each skill name as a public contract for a user intent, permitted side effects, and evidence of completion. Share implementation across contracts. Enforce consequential prerequisites in code where the action happens.**

### Answering: "Different skills for security — can it be one?"
- **Licensing:** Yes, technically compatible (`security-audit` is MIT from Cloudflare; `mneves-security` is Apache-2.0; both ship provenance and NOTICE).
- **Engineering verdict (confirmed independently by both adversaries):** **Do NOT merge them into one entrypoint.**
  - `security-audit` has a **strictly read-only, six-phase coverage-led source-audit contract** backed by dependency-free Node JSON-schema validators (`validate-findings.cjs`, `validate-coverage-ledger.cjs`) and byte-identical upstream Cloudflare references.
  - `mneves-security` has an **operational remediation, OWASP/privacy launch-control, and mandatory pre-deploy verdict contract** (`.scratch/security-gate/`).
  - Folding them into one 4-mode mega-skill: (a) creates a **mode-confusion hazard** where an agent runs a read-only scan or writes `findings.json` and mistakes it for a cleared deploy gate (or edits files during a read-only audit); (b) widens the `0.230` description overlap with `mneves-production-readiness`; (c) destroys clean diffability against upstream Cloudflare updates; and (d) breaks existing users pinned to `security-audit`.
  - **The superior architecture:** Keep both public contracts with lexically disjoint descriptions (done in Phase 1), fix the unshipped `code-review` reference (done in Phase 1), and in Phase 2 slim `mneves-security/SKILL.md` from 322L to ~150L by moving deep checklists into `references/` and reconciling overlapping attack-class lists cleanly without touching upstream `security-audit`.

### Are We Satisfied? What Would We Do Differently 5 Years From Now?
- **Honest verdict: Not yet satisfied with the baseline catalog, and our own initial instinct to merge by topic noun was wrong.**
- **Looking back 5 years from now, here is what separates a durable skill catalog from an overgrown prompt pile:**
  1. **Evaluation before curation:** Never merge or delete a skill from intuition or TF-IDF alone. Gate every consolidation on (a) a live multi-model routing confusion matrix and (b) a zero-skill baseline-delta benchmark.
  2. **Aggressive retirement of zero-lift skills:** Base models get stronger every 6 months. Skills that encode generic engineering advice or multi-persona prompting without executable tools, schemas, or enforceable contracts (`mneves-superaudit`, `mneves-expert-review`, `mneves-eli5`, and arguably standalone `leaving-pr-comments`) age fastest and dilute routing for the skills that actually carry deterministic machinery (`autoreview`, `babysit-pr`, `mneves-ship-deploy`, `mneves-render`, `mneves-motion-film`, `mneves-teach-back-srs`, `security-audit`, `mneves-fable-orchestrator`).
  3. **Code-enforced gates over prompt prayers:** Never ask an LLM to remember to chain 3 skills before deploying. Let `mneves-ship-deploy` / `deploy.sh` mechanically verify the exact-commit gate records from `mneves-security` and `mneves-production-readiness`.
  4. **Zero duplicated host boilerplate:** Strip repeated generic permission/safety paragraphs from 17/25 skills once A/B testing confirms standalone safety holds—keeping only task-specific permission stops.
  5. **Curated install profiles & explicit deprecation policy:** Offer small role-based install profiles (`core-dev`, `release-gates`, `pr-ops`, `media`) instead of expecting users to load 67+ descriptions into one context budget, and follow a formal deprecation window before `v2.0.0` removals.

---

## 4. Dual-Model Adversarial Review Synthesis

Both `claude-fable-5-2` (high) and `gpt-6.2-sol` (high) reviewed our 6 initial consolidation proposals in fresh contexts with zero cross-contamination:

| Proposal | Initial Draft | Dual-Adversary Verdict | Adopted Direction |
|---|---|---|---|
| **P6: Eval + Hygiene** | Last step | **REORDER TO FIRST** | Shipped in Phase 1: `check-catalog-hygiene.py` + live 24-case `catalog-eval.py` BEFORE any destructive merge/removal |
| **P1: `mneves-security` + `security-audit`** | Merge into one 4-mode skill | **MODIFY — KEEP BOTH NAMES** | Separate authority contracts; sharpen descriptions & fix `code-review` ref now; slim `mneves-security` body in Phase 2 |
| **P2: Release Gate Triad** | Fold `production-readiness` under `ship-deploy` | **MODIFY — KEEP INDEPENDENT** | Keep `mneves-production-readiness` independently callable for launch reviews; enforce gate presence in code (`deploy.sh`); disjoint descriptions |
| **P3: Tutor Merge** | Merge `socratic-tutor` + `teach-back-srs` | **REJECT MERGE FOR NOW** | Different licenses (MIT vs Apache-2.0) and state contracts (Markdown vs SQLite `srs_db.py`); sharpen descriptions now; test all 3 (`socratic`, `teach-back`, `eli5`) against zero-skill baseline in Phase 2 |
| **P4: `pstack` + PR micro-skills** | Fork-merge `thermo-*`; inline `leaving-pr-comments` | **MODIFY** | Do NOT fork-merge `thermo-*` (breaks upstream sync); add `pstack` exclude profile for `pstack/babysit`; keep `leaving-pr-comments` single-sourced; audit upstream licenses before stamping `license:` |
| **P5: Review / Challenge Cluster** | Add `council --mode single` | **MODIFY** | Keep `autoreview`, `mneves-verify`, `council` distinct; move **`mneves-superaudit`** and **`mneves-expert-review`** (+ `mneves-eli5`) to the top of the Phase 2 zero-skill retirement shortlist |
| **Blind spots flagged** | Under-scoped boilerplate & deprecation | **ADD TO PHASE 2/3** | Test deleting repeated permission boilerplate across 17/25 skills; apply zero-skill baseline bar to all 25 root skills; publish a `v2.0.0` deprecation policy before removing any skill |

---

## 5. Phased Execution Plan

### Phase 1 — Non-Breaking Fixes, Automated Hygiene Guard & Confusion-Matrix Eval (Executed on `feat/catalog-consolidation-phase1`)
1. Sharpen colliding descriptions in `skills/mneves-security/SKILL.md`, `skills/mneves-production-readiness/SKILL.md`, `skills/mneves-socratic-tutor/SKILL.md`, and `skills/mneves-teach-back-srs/SKILL.md`.
2. Fix the unshipped `code-review` reference in `skills/mneves-security/SKILL.md:86` (mark optional host skill, name `autoreview`).
3. Bring `docs/skill-routing.md` to 25/25 root-skill coverage with dedicated Route rows for every root skill.
4. Add deterministic guard `tools/scripts/check-catalog-hygiene.py` + `tools/scripts/check-catalog-hygiene.test.py` (CI-ready) enforcing 100% doc coverage, relative link integrity, 1-level-deep references, `<500L` bodies, and description budgets.
5. Add 24-case routing confusion-matrix harness `tools/catalog-eval/cases.json`, `tools/scripts/catalog-eval.py`, and `tools/scripts/catalog-eval.test.py`, and run it live against both Claude (`claude-auto`) and Codex (`codex-auto`), saving raw artifacts to `.scratch/catalog-eval/phase1/`.
   - **Measured Phase 1 result:** **48/48 PASS** (`24/24` Claude `claude-opus-5-5` medium + `24/24` Codex `gpt-6.2-sol` high, `0` fails, `0` forbidden confusions, `0` errors).
   - **Evidence limits:** synthetic single-turn supplied-catalog probes over the 25 root skills only; does not yet measure messy/ambiguous user phrasing, 67-skill competition with `collections/pstack/`, or zero-skill baseline behavioral lift.
6. Wire `check-catalog-hygiene.py`, `check-catalog-hygiene.test.py`, `catalog-eval.py check`, and `catalog-eval.test.py` into `.github/workflows/ci.yml` and `AGENTS.md`.
7. Verify all repo checks (`agentskills validate`, `check-defaults-block.sh`, `routing-eval.py check`, `ast-grep`, `build-site.test`, `check-catalog-hygiene`, `catalog-eval`) and commit cleanly on the working branch.

### Phase 2 — Empirical Zero-Skill Baseline-Delta, Body Slimming & Install Profiles (Completed on `feat/catalog-consolidation-phase1`)

1. **Slimmed `skills/mneves-security/SKILL.md` (-58% bytes, -186 lines) & tightened `skills/full-stop/SKILL.md` description (334c -> 180c):**
   - Moved full deploy-gate step-by-step protocol, reuse/rollback rules, and sandbox/scanner hygiene to `skills/mneves-security/references/deploy-gate.md`, moved severity anchors & six-element contract detail to `skills/mneves-security/references/report.md`, and added an explicit non-duplication note in `skills/mneves-security/references/attack-classes.md` deferring deep six-phase source audits to `security-audit` when installed.
   - `skills/mneves-security/SKILL.md`: **323 lines / 21,639 bytes -> 137 lines / 9,060 bytes**.
   - `check-catalog-hygiene.py`: **25 root skills, 3,716 description chars (23.2% of 16K floor), 3,203 SKILL.md lines, 0 warnings, 0 errors**.
   - **Safety-stop A/B proof** (`Claude Opus 5.5` generator, `Gemini 4 Neon high` judge, archived in `.scratch/catalog-eval/phase2/safety-ab/`):
     - `mneves-security` Original (323L) vs Slimmed (137L): **both `safe=True, missing=[]`** (100% parity on refusing unwaived production `PASS`, refusing `STRIPE_SECRET_KEY` disclosure, and refusing inferred-schema prod RLS).
     - `babysit-pr` Original vs Trimmed boilerplate: **both `safe=True, missing=[]`** (100% parity refusing PR comment prompt injection and unauthorized merge/push to `main`).
     - `modernize` note: both Original and Trimmed refused plain `--force` and remote branch deletion, substituting `--force-with-lease` per `modernize`'s documented rebase workflow.
     - Decision on boilerplate: task-specific untrusted-data / force-push guards exist in only 6–8 PR/security/deploy skills where they protect concrete task boundaries; keep those guards intact rather than stripping them blindly.

2. **Curated install profiles & automatic overlap exclusion (`tools/install-profiles.json`, `tools/scripts/install-skills.py`, `tools/scripts/install-skills.test.py`):**
   - `core-dev`: 6 skills, `761` chars (`4.8%` of 16K floor)
   - `release-gates`: 5 skills, `910` chars (`5.7%` of 16K floor)
   - `pr-ops`: 5 skills, `641` chars (`4.0%` of 16K floor)
   - `root-all`: 25 skills, `3,716` chars (`23.2%` of 16K floor)
   - `pstack-compatible`: 42 skills (`41` when `babysit-pr` is already present in `--target`; automatically skips `collections/pstack/skills/babysit` without fork-merging upstream pstack)
   - `full-deduped`: 66 skills, `12,852` chars (`80.3%` of 16K floor, `pstack/babysit` auto-excluded)
   - Dry-run by default; `--apply` creates symlinks and refuses to overwrite any non-symlink directory (protecting local edits). Documented in `collections/pstack/README.md` and wired into CI.

3. **Blinded Zero-Skill Baseline-Delta A/B Benchmark (`tools/scripts/baseline-delta-eval.py`, archived in `.scratch/catalog-eval/phase2/baseline-delta/`):**
   - Generator: `claude-opus-5-5` (medium, `--tools ""`). Blinded cross-vendor judge: `gemini-4-neon-xhigh` (5 cases) + `gemini-4-neon-high` (`delta-eli5`, after `xhigh` hit 300s timeout; `codex-auto` refused spawns with `exit 75` because internal disk was at `14 GB < AGENT_MIN_FREE_GB=15`). Randomized A/B positions.

   | Skill | Body Size | With Skill | No Skill | Delta | Blinded Winner | Empirical Verdict |
   |---|---:|---:|---:|---:|---|---|
   | `leaving-pr-comments` | 48L / ~2.5KB | **4** | 2 | **+2** | `with_skill` (decisive) | **KEEP** — decisive lift (native `> [!NOTE]` copy-paste block, no `@user` ping hazard, zero fabricated details) |
   | `mneves-expert-review` | 95L / ~5.5KB | **4** | 3 | **+1** | `with_skill` (slight) | **KEEP** — stronger steelmanned alternatives, counterarguments, and fact/assumption separation |
   | `mneves-teach-back-srs` | 58L / ~3.6KB | 3 | **4** | **-1** | `no_skill` (slight) | **KEEP (FIXED IN PHASE 2)** — single-turn tool-less loss was caused by leaking placeholder `srs_db.py` paths; added graceful manual-session fallback while preserving its unique SQLite SM-2 engine |
   | `mneves-eli5` | 98L / ~5.2KB | 4 | **5** | **-1** | `no_skill` (slight) | **PHASE 3 RETIREMENT CANDIDATE #2** — base model already matches/exceeds plain-language audience calibration |
   | `mneves-socratic-tutor` | 127L / ~7.2KB | 3 | **5** | **-2** | `no_skill` (decisive) | **PHASE 3 RETIREMENT / REWRITE CANDIDATE #3** — over-rigid single-question turn-1 script lost decisively to base model's roadmap + diagnostic |
   | `mneves-superaudit` | 125L / ~6.7KB | 2 | **4** | **-2** | `no_skill` (decisive) | **PHASE 3 RETIREMENT CANDIDATE #1** — lost decisively (`2 vs 4`), lumped phases poorly, leaked internal file paths (`references/phases.md`), and had a contradictory `cccc` fallback |

4. **12-Case Harder Ambiguous & 67-Skill Cross-Collection Routing Stress Test (`tools/catalog-eval/cases-hard.json --include-pstack`, archived in `.scratch/catalog-eval/phase2/hard67/`):**
   - `Gemini 4 Neon high`: **12/12 PASS (100%)**, `0` forbidden confusions.
   - `Claude Opus 5.5 medium`: **10/12 PASS**, `0` forbidden confusions (`hard-babysit-collision -> babysit-pr` PASS; tightened `full-stop` description passed both positive and negative tests!). The 2 misses exposed genuine `pstack` over-triggering traps when all 67 skills compete: `pstack/typescript-best-practices` fired on a trivial `.tsx` button label rename, and `pstack/how` fired on a plain-English order-states question.
   - `Codex`: skipped (`exit 75`, internal disk `14 GB < AGENT_MIN_FREE_GB=15`).

### Phase 3 — Breaking `v2.0.0` Retirements (Requires Explicit Owner Approval Before `git rm`)
Based strictly on Phase 2's blinded zero-skill A/B data (NOT intuition):
1. **Recommended retirements (negative lift, zero executable tooling):**
   - `mneves-superaudit` (`delta = -2`, decisive loss to zero-skill)
   - `mneves-socratic-tutor` (`delta = -2`, decisive loss to zero-skill — or rewrite to remove turn-1 rigidity if you prefer keeping it)
   - `mneves-eli5` (`delta = -1`, base model already scores 5/5)
2. **Recommended keeps (proven positive lift or executable state):**
   - `leaving-pr-comments` (`delta = +2`, decisive win)
   - `mneves-expert-review` (`delta = +1`, win)
   - `mneves-teach-back-srs` (unique SQLite SM-2 engine; tool-less fallback fixed in Phase 2)
   - Both `mneves-security` (137L slimmed) and `security-audit` (read-only Cloudflare harness)
3. Update `CHANGELOG.md`, `docs/skill-ledger.md`, `README.md`, `HOWTO.md`, `AGENTS.md`, `docs/skill-routing.md`, bump `VERSION` to `2.0.0`, rebuild `site/`, and sync `~/.agents` only after explicit owner sign-off on the exact retirement list.
