# Skill dispositions (2.2.0)

One row per shipped skill: the 23 root skills and the 43 pstack skills. Four read-only agents read
every body, and the main session re-read the rows marked **yes** under Checked. Three agent claims
did not survive that re-read: `mneves-ship-deploy` gives a fallback for each platform skill it
names (`SKILL.md:46-49`), `modernize` states `--force-with-lease` (`:23`, `:92`), and
`mneves-handoff`'s description already says "discussion".

Dispositions:

- **keep**: no change needed.
- **fixed**: fixed in this release.
- **patch**: a pstack defect that needs a new adaptation patch; reported, not fixed here.
- **owner**: a retire or merge call for the owner.

Nothing is retired in this release.

The 350-character description cap (`tools/scripts/check-catalog-hygiene.py`) covers root skills.
pstack descriptions over it are listed as patch candidates for the listing budget, not as
violations.

## Root skills

| Skill | Disposition | Finding | Nearest neighbour | Checked |
|---|---|---|---|---|
| `autoreview` | keep | Engine defaults sit in one table in `scripts/autoreview`; the other model names are compatibility maps | `code-review`, `thermos` | yes |
| `babysit-pr` | keep | Owns PR watching; pstack `babysit` defers to it | `babysit` | yes |
| `council` | keep | Request-scoped (explicit council or second-opinion requests), not explicit-only | `mneves-expert-review` | yes |
| `full-stop` | owner | Explicit-only by its body, but `agents/openai.yaml` does not set `allow_implicit_invocation: false` | none | yes |
| `imagegen-frontend-mobile` | keep | None | `mneves-render` | no |
| `leaving-pr-comments` | keep | None | `get-pr-comments` | no |
| `mneves-agent-readiness` | keep | Uses the repository's `tools/readiness-check.ts` with a fallback; the README install path is the public repository | `mneves-production-readiness` | yes |
| `mneves-chatgpt-search` | keep | None | none | no |
| `mneves-expert-review` | keep | Its complexity-evidence paragraph repeats `mneves-verify`'s | `interrogate`, `council` | no |
| `mneves-fable-orchestrator` | fixed | `references/codex-dispatch.md` hardcoded the review fallback's model; it now takes it from the Defaults block | `swarm` | yes |
| `mneves-handoff` | keep | None | none | yes |
| `mneves-mode` | fixed | Rewritten as the v3 gate director | `poteto-mode` | yes |
| `mneves-motion-film` | fixed | Step 4 was done only once step 5's scenes existed; the reviewer seat had no fallback | `mneves-render` | yes |
| `mneves-production-readiness` | keep | None | `mneves-agent-readiness` | no |
| `mneves-render` | keep | None | `mneves-motion-film` | no |
| `mneves-security` | keep | Shares the word "audit" with `security-audit`; the boundary is stated in the body | `security-audit` | yes |
| `mneves-ship-deploy` | owner | Explicit-only by its body, with no `agents/openai.yaml` | none | yes |
| `mneves-teach-back-srs` | keep | None | `teach` | no |
| `mneves-verify` | keep | None | `mneves-expert-review` | no |
| `modernize` | keep | None | `fix-merge-conflicts` | yes |
| `security-audit` | keep | None | `mneves-security` | no |
| `takeover` | keep | None | `figure-it-out` | no |
| `untangle-codebase` | keep | None | `how` | no |

## pstack skills

| Skill | Disposition | Finding | Nearest neighbour | Checked |
|---|---|---|---|---|
| `architect` | keep | None | `statechart` | no |
| `arena` | fixed | Cited the retired Laziness Protocol (patch `02`) | `swarm` | yes |
| `automate-me` | patch | Depends on a plugin authoring skill with no in-body fallback | `reflect` | yes |
| `babysit` | owner | Defers to `babysit-pr` when installed, and poteto-mode's Babysit playbook supersedes it; the description says neither | `babysit-pr` | yes |
| `benchmark-checklist` | keep | None | none | no |
| `blast-radius` | patch | Description is 401 characters | `make-pr-easy-to-review` | yes |
| `bro` | keep | None | none | no |
| `correct` | keep | None | `interrogate` | no |
| `create-formal-verification-skill` | keep | Distinct from the executable-check pair | `create-verification-skill` | no |
| `create-verification-skill` | keep | None | `create-formal-verification-skill` | no |
| `deslop` | patch | Description names no trigger | `no-comments` | yes |
| `figure-it-out` | fixed | Routed to retired principle skills (patch `02`) | `takeover` | yes |
| `fix-ci` | keep | None | `babysit-pr` | no |
| `fix-merge-conflicts` | keep | None | `modernize` | no |
| `get-pr-comments` | keep | None | `leaving-pr-comments` | no |
| `how` | patch | Dispatches a general-purpose subagent with no fallback | `why` | no |
| `in-your-own-words` | keep | None | `sharpen` | no |
| `interrogate` | keep | None | `mneves-expert-review` | no |
| `ketchup` | keep | Distinct from the video variant | `ketchup-video` | no |
| `ketchup-video` | keep | None | `ketchup` | no |
| `maintain-formal-verification-skill` | patch | Description is 415 characters | `maintain-verification-skill` | yes |
| `maintain-verification-skill` | patch | Writes a skill but states no explicit-only clause | `maintain-formal-verification-skill` | no |
| `make-pr-easy-to-review` | keep | None | `blast-radius` | no |
| `no-comments` | patch | Description names no trigger | `deslop` | yes |
| `poteto-help` | patch | Its hand-kept skill table omits the thermo review skills | `poteto-mode` | yes |
| `poteto-mode` | fixed | Explicit-only policy, a concrete description and the operator-mode boundary (patch `14`) | `mneves-mode` | yes |
| `recall` | patch | Description is 351 characters, a `<plugin>` placeholder path, and no subagent fallback | `what-did-i-get-done` | yes |
| `reflect` | keep | None | `automate-me` | no |
| `reframe` | keep | `metadata.disable-model-invocation` is spec-valid; no host reads it | `sharpen` | yes |
| `setup-pstack` | keep | None | none | no |
| `sharpen` | keep | None | `in-your-own-words` | no |
| `show-me-your-work` | patch | Asks for a cross-family subagent with no fallback | `mneves-verify` | no |
| `statechart` | keep | None | `architect` | no |
| `swarm` | patch | Dispatches a general-purpose subagent with no fallback | `arena` | no |
| `tdd` | keep | Shares its name with Matt Pocock's `tdd`; mneves-mode uses whichever the host lists | `tdd` (Pocock) | yes |
| `teach` | keep | None | `mneves-teach-back-srs` | no |
| `technical-writing` | keep | None | `deslop` | no |
| `thermo-nuclear-code-quality-review` | keep | Not a merge candidate: it covers code quality, not breakage | `thermo-nuclear-review` | no |
| `thermo-nuclear-review` | keep | None | `thermos` | no |
| `thermos` | patch | Requires the pstack plugin's subagent types, with no fallback for a skills-only install | `autoreview` | yes |
| `typescript-best-practices` | keep | `metadata.paths` is spec-valid; no host reads it | none | yes |
| `what-did-i-get-done` | patch | Description names no trigger | `recall` | yes |
| `why` | keep | None | `how` | no |

## Cross-cutting

- Four root skills repeat the paragraph that treats PR and tool text as data. It is short and each
  skill must work alone, so it stays.
- Every patch row needs a new adaptation patch. A pstack fix made by editing the synced tree is
  overwritten on the next sync.
