# mneves-mode playbooks

Open only the playbook that matches the current task. Every step names the preferred sibling skill
and a single-skill standalone fallback when that sibling is not installed.

## 1. Feature or bug fix

1. **Frame & scope:** restate the goal, entry points, callers, and acceptance criteria. For bug
   fixes, reproduce the failure first and stop to rethink after two failed fix attempts.
2. **Design check (when crossing boundaries):**
   - Sibling: `architect` (optional `pstack`) or `mneves-expert-review` for non-trivial tradeoffs.
   - Fallback: sketch interfaces and invariants in a short note before editing; prototype
     reversible technical forks locally.
3. **Implement & test:**
   - Single-track: edit directly with minimal scope and add tests that fail without the fix.
   - Multi-track: route to `mneves-fable-orchestrator` with explicit Goal / Context / Constraints /
     Done-when briefs. Fallback: execute tracks sequentially in the current session without
     claiming parallel review independence.
4. **Code review (adversarial):**
   - Sibling: `autoreview` on the fixed diff (with local `cccc` complexity evidence when available).
   - Fallback: dispatch a fresh read-only reviewer session on the diff; if no independent reviewer
     can run on risky work, mark the review gate `BLOCKED`.
5. **Independent verification:**
   - Sibling: `mneves-verify` in a fresh context against explicit pass/fail criteria (checking
     real execution, negative controls, and separation of product vs verification edits).
   - Fallback: run the full validation commands directly and state clearly that independent
     fresh-context verification did not run (for risky work, keep the gate `BLOCKED`).

## 2. Scoped refactor

1. **Freeze scope & baseline:** require an explicit target module or file boundary. Never expand a
   vague "clean up" into a repo-wide edit. Capture current tests, types, and behavior as baseline.
2. **Diagnose & plan:**
   - Sibling: `untangle-codebase`. Naming it alone produces diagnosis + plan and waits for edit
     approval; an explicit refactoring request authorizes bounded implementation.
   - Fallback: map callers, dependency direction, and duplicated rules; propose the smallest
     behavior-preserving edits before changing files.
3. **Apply & prove:** preserve public contracts and safety checks, re-run the baseline suite after
   each coherent unit, then run step 4 (adversarial review) and step 5 (independent verification)
   from Playbook 1.

## 3. High-stakes decision or plan

1. **Separate facts from guesses:** gather primary-source evidence (code, logs, official docs,
   specs). Confirm every cited source supports the exact claim; cut unconfirmed citations.
2. **Stress-test:**
   - Sibling: `mneves-expert-review` for memos, architecture choices, and strategy; `council` when
     multi-CLI independent deliberation is requested.
   - Fallback: write the strongest objection to the preferred option, compare at least two viable
     alternatives, and record reversibility and failure modes.
3. **Settle empirical forks locally:** run a small local benchmark or prototype before escalating a
   reversible technical question to the user. Leave product and preference calls to the owner.
4. **Report:** keep review-only and planning requests strictly read-only.

## 4. PR lifecycle

Match the exact PR situation — do not stack overlapping PR workflows:

- **Watch CI & bots on an active PR:** route to `babysit-pr` (fallback: read `gh pr checks` and
  paginated review comments, fix real findings within a finite 2-3 round bound, stop at merge).
- **Aging or stale PR:** route to `modernize` (fallback: inspect base-branch commits first and
  decide MODERNIZE, REWORK, or CLOSE before rebasing).
- **Finish someone else's PR or thread:** route to `takeover` (fallback: preserve original commits
  and author attribution; never rewrite shared history).
- **Unattended change to a ready PR:** route to `full-stop` ONLY when the user invoked it by name.
- **Post GitHub comments:** route to `leaving-pr-comments` (fallback: clearly disclose that an
  agent drafted/posted the comment on the user's behalf).
- **Hand off to another session:** route to `mneves-handoff` (fallback: write a path-free,
  discussion-first continuation prompt with goal, verified facts, and open questions).

Stop condition for every PR workflow: **never merge, never force-push shared history, and never
alter auto-merge settings without explicit user authorization.**

## 5. Release and production deploy

Plain "ship" is never a deployment authorization. Require explicit target authorization (such as
`ship-staging` or `ship-prod`) and run gates in strict order on the **exact candidate commit/tree**:

1. **Security gate (mandatory):**
   - Sibling: `mneves-security` -> exact-commit `pass` or owner-waived verdict with independent
     acceptance. Missing skill or failed acceptance blocks deploy unless waived by name by the
     authority named in the governing rule.
2. **Production readiness gate (mandatory for staging/prod):**
   - Sibling: `mneves-production-readiness` -> imports security rows from `mneves-security`,
     verifies data/recovery/cost/ops/ownership controls, and checks candidate identity, preview
     writable bindings, observation windows, and persistent-state vs code rollback limits.
3. **Deploy, prove live, then tag:**
   - Sibling: `mneves-ship-deploy` -> deploy the exact gated artifact, verify live behavior and
     served bytes/version against the candidate commit, then tag.
   - Fallback: if any required gate sibling is unavailable, report `BLOCKED` and stop before
     merging, deploying, or tagging. Never fabricate or bypass a gate record.

## 6. Audit or independent verification

1. **Keep it read-only:** answer, review, diagnosis, and audit requests inspect and report without
   editing code unless the user explicitly authorizes remediation.
2. **Route to the exact audit type:**
   - Deep source security audit (no edits, machine-readable ledger): `security-audit`.
   - Security audit with remediation plan or deploy gate: `mneves-security`.
   - Operational launch readiness: `mneves-production-readiness`.
   - Codebase AI-agent DX readiness: `mneves-agent-readiness`.
   - ChatGPT Search crawler/citation audit: `mneves-chatgpt-search`.
   - Completion proof against acceptance criteria: `mneves-verify`.
   - Fallback: state which sibling is missing, run direct read-only checks on the exact target,
     and label any unverified dimension `NOT TESTED` or `BLOCKED`.

## 7. Specialized artifacts & learning

Use the dedicated sibling when installed; on a single-skill install, follow these boundaries and
fallbacks instead of improvising an incompatible workflow:

- **Markdown -> HTML/DOCX/PDF export (`mneves-render`):**
  - Fallback: build a minimal project-local export script using already-installed document tools
    (such as Pandoc/WeasyPrint), reject raw active HTML/script content, and inspect rendered output
    before claiming success; report `BLOCKED` if required document engines are absent.
- **Product launch video (`mneves-motion-film`):**
  - Fallback: ground every on-screen claim in verbatim product copy/URLs (never invent metrics or
    claims), verify available media tools (such as FFmpeg/Remotion) before rendering, and check
    output duration, codecs, and audio sync; report `BLOCKED` if rendering tools are unavailable.
- **Mobile UI screen/flow concept images (`imagegen-frontend-mobile`):**
  - Fallback: generate visual concept assets only (never write application code unless explicitly
    requested), follow target iOS/Android platform conventions, and inspect generated images for
    legibility and visual consistency; report `BLOCKED` if no image tool is available.
- **Codebase teach-back & spaced repetition (`mneves-teach-back-srs`):**
  - Fallback: verify the user's explanation directly against actual repository source files,
    correct inaccuracies with exact file/line citations, and provide concise follow-up review
    prompts in plain text (noting that persistent SQLite SM-2 scheduling requires the sibling skill).
