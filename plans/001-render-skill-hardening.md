# Plan 001: Rename and verify the Markdown renderer skill

## What the review changes

The first delivery was a useful procedure, but its one-page happy-path evidence did not
establish that the supplied defaults preserve other valid inputs. The next delivery will
use the requested name `mneves-render`, preserve document metadata visibly, add repeatable
starter acceptance tests and retain honest format/engine limits. It will also reconcile
the already-published version on main before release.

## Status and scope

- Priority: P1; effort: M; implementation risk: low, release integration risk: medium.
- Planned against `51a4d0b`; remote main observed at `6f6492a` after fetching.
- Scope: the renderer skill, its directly related catalog/docs/tests, CI for those tests,
  version/changelog, local installations and the authorized repository release.
- Other branch work: preserve the release-contract, model-routing and pstack changes
  already present. Integrate main's reviewed complexity work without redesigning it.
- Not a universal converter, hosted service, new package manager or application rewrite.
- No arbitrary engine installation or claim of PDF/UA conformance. OptChat runtime changes
  are outside this repository; its backends explicitly disable external skills.

The owner approved all requested formats, editable Word, Markdown as the authority,
project-local repeatable renderers and local installation for detected agents. The later
request authorizes review, fixes, docs/version updates, commit/push, merging, branch cleanup
and deployment to the actual production target. It does not require inventing a staging
environment for this repository.

## First principles and acceptance

1. A renderer preserves meaning before styling it. Titles, subtitles, authors and dates are
   content when the source uses them as document metadata; clearing them by default is unsafe.
2. A successful process and a nonempty file do not prove fidelity. Test source-derived
   content, semantic structures, regeneration and actual rendered pages independently.
3. Reusable guidance should fit the user's project. A skill should not impose a second
   universal rendering framework or pretend that CSS controls Word styles.
4. Render engines are not security sandboxes. Authorized local inputs, resources and
   process limits are boundaries; untrusted content needs an explicitly stronger route.
5. Releasing means proving the named candidate at the target, not merely pushing a tag.

Frozen acceptance:

- New folder/frontmatter/catalog/install name is `mneves-render`; obsolete installed links
  and registry entries are removed without touching other skills.
- Starter commands preserve metadata-only and body-title documents, literal code, Unicode,
  lists, tables, links, notes and local images supported by the chosen reader.
- Shared HTML/PDF styling remains responsive and legible; DOCX is editable and its distinct
  style/preview requirements are explicit.
- A repeatable acceptance command exercises actual engines and detects silent content loss;
  missing tools and unsupported features are not represented as a successful full check.
- Source files remain unchanged by checks; all temporary writes are scoped and cleaned.
- Updated docs, catalog/version consistency, required local gates and final-candidate CI pass.
- Independent code-review axes and final verification have no unresolved in-scope findings.
- Main is restored after the authorized merge; production Pages artifacts match the merged
  candidate before an unused version tag is published. No fake beta deployment is recorded.

## Research and evidence

These are published technical sources, not personal endorsements or interviews:

- [Pandoc manual](https://pandoc.org/MANUAL.html): readers and writers use an intermediate
  document representation, with conversion limits; reference DOCX controls Word styles.
  Its sandbox limits reader/writer I/O, not filters or PDF subprocesses.
- [WeasyPrint security guidance](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#security):
  untrusted input can cause local/remote resource access and resource exhaustion.
- [WeasyPrint specialized PDFs](https://doc.courtbouillon.org/weasyprint/stable/common_use_cases.html#generate-specialized-pdfs):
  selecting a PDF variant does not guarantee conformance; language, title and structure matter.
- [W3C WAI tables tutorial](https://www.w3.org/WAI/tutorials/tables/): table structure must expose
  header/data relationships; visual borders are not semantic proof.
- [Microsoft WordprocessingML styles](https://learn.microsoft.com/en-us/office/open-xml/word/working-with-styles):
  Word styles are document structures, separate from CSS.

Own inference: the best long-term investment is a small tested starter contract and clear
format-specific acceptance, rather than a framework that tries to hide all engine differences.
The independent plan advisor confirmed this choice, with the corrections recorded below.

Advisor corrections adopted: explicitly test literal punctuation, plain-token wrapping,
oversized figures and native Markdown active attributes. Render metadata titles and body
headings independently; never guess which one to discard. Put a bounded AST policy guard in
the executed starter commands, not just the tests, without claiming filesystem isolation.
Produce all DOCX previews through LibreOffice in CI and inspect them before acceptance.
Keep wrapper atomicity a procedure requirement, separate from starter evidence.

The deep audit reproduced all four issues against the original starter with real engines.
The regression suite first failed on punctuation, metadata and clipped text/figures; the
existing editable-DOCX structure control passed. The filter has separate adversarial controls.

## Current state and confirmed risks

- `skills/mneves-md-renderers/assets/docx.yaml` contains `metadata: {title: ""}`. It prevents
  a duplicate title in one fixture but suppresses a metadata-only title for other inputs.
- `assets/document.html` emits only `$body$` visibly; document metadata is not rendered.
- `assets/sample.md` exercises a single short page. No tracked automated engine acceptance
  command keeps future edits from breaking these starter contracts.
- The original DOCX preview was unavailable: the local `soffice` shim points to an absent app.
  Structural validation passed; visual validation must remain separate until a real viewer runs.
- `v1.32.0` was already released on 2026-10-08. The feature branch incorrectly reused that
  version for a new entry. Use a new unused version, provisionally `1.33.0`.
- `git merge-tree --write-tree --name-only HEAD origin/main` reports conflicts in
  `CHANGELOG.md`, `site/index.html` and the orchestrator skill. Preserve main's real release
  history, the branch's newer routing policy, and both sides' relevant improvements.

## Alternatives and five-year review

| Approach | Benefits | Costs / reason to reject |
|---|---|---|
| A. Harden the procedure and tested starter assets (chosen) | Small maintenance surface, project autonomy, reproducible evidence | Engine-specific styling still belongs in the project |
| B. Ship a universal HTML/DOCX/PDF conversion CLI | One entry point and centralized failures | Changes the approved product; dependency, resource-policy and layout support become a new application |
| C. Remove the skill and rely solely on existing document-specific skills | Least new code; challenges whether another skill is needed | Loses the cross-format source-of-truth and repeatable-project-command contract; assumes those other skills are installed |

Five years later, the costly mistake would be relying on undocumented engine defaults,
ephemeral smoke evidence and hidden content loss. Keep source-level fixtures and meaningful
assertions; record versions in evidence rather than hardcoding fast-aging versions into
prose. Preserve simple assets and replaceable engines. Avoid promising identical pagination
or compliance without the necessary validation. Do not add speculative plugins or adapters.

## Implementation sequence

### 1. Obtain the advisor challenge and finish the evidence-backed plan

Use a fresh read-only advisor with this plan and current artifacts. Incorporate confirmed
findings and record rejected suggestions with reasons. Keep the approved scope; no interview
restart is needed for these reversible improvements.

### 2. Integrate main without rewriting published history

On `feat/release-lessons`, merge `origin/main`. Resolve the three known conflicts explicitly;
inspect automatically merged CI and documentation. Retain main's `1.32.0` changelog entry;
move the renderer and accumulated unreleased work into the new release entry. Regenerate
site files from the reconciled sources. Keep the current branch model-routing choices and
main's complexity evidence guidance. A new unrelated conflict requires examination, not
blanket `ours`/`theirs` resolution.

### 3. Rename and add the missing behavioral baseline first

Move `skills/mneves-md-renderers/` to `skills/mneves-render/`; change its frontmatter and all
active catalog references. Preserve a rename explanation in release/history documentation.
Create a Python-standard-library integration suite adjacent to the skill, following the
repository's subprocess/temporary-directory conventions. Use real installed Pandoc and
WeasyPrint; no mocked successful conversions. Capture the original defaults failing the
metadata-only fidelity case before correcting them.

The new suite is a test of the starter assets, not a generic project renderer and not a
claim of full visual compliance. Explicit optional checks may be separated from the core
suite, but the CI invocation must require every engine its advertised checks use.

### 4. Fix only demonstrated starter defects

Preserve metadata-only content in both HTML and Word. Remove the unconditional title reset.
Choose a visible-title contract that does not silently discard data; test body-only and
metadata-only sources and document the treatment of combined metadata/body titles.
Disable smart punctuation in both readers, inherit plain-text wrapping and cap figure height
without changing aspect ratio. Require readable page rasters, not just extracted markers.
Ship a small Python AST policy filter in both actual Pandoc commands: reject active schemes,
raw nodes and undeclared attributes before output, preserve IDs/classes and valid image
dimensions, and reject remote image destinations. This is not a filesystem or SVG sandbox.
Test negative controls through the real engine alongside valid links/local images. Keep raw
source code literal, compare accents/numbers, and verify semantic document structures.

Expand fixtures to exercise a local image, relative paths with spaces/accents, regenerated
sentinels and multipage content. Unsupported math/diagrams should be explicitly described,
not silently advertised as supported. Keep PDF/UA validation conditional on an actual
conformance requirement and available validator.

### 5. Wire repeatable checks and inspect actual artifacts

Add a scoped CI job for the acceptance suite with explicit tool installation on its runner.
Run structural assertions on generated HTML/DOCX/PDF; inspect HTML at desktop/mobile widths
and every page of the bounded PDF fixtures. Attempt DOCX preview with a genuine available
engine; if none is available, keep that claim BLOCKED and do not disguise it with another PDF.
Record what has and has not been proven in the plan's execution record.

### 6. Review, documentation, version and installation

Run Matt Pocock's two code-review axes on the frozen task diff; fix substantiated findings.
Use a fresh mneves-verify context for final acceptance. Re-run affected checks after fixes,
not unrelated passing suites repeatedly. Update README, HOWTO, AGENTS, changelog, VERSION,
generated catalog and any directly affected status docs. CLAUDE remains the AGENTS pointer.
Reverify the orchestrator's current model IDs and release date as required by its guard.

Install the new name through the skills CLI for detected agents, verify file hashes and
custom local links, then remove only the known old installation. Update its registry entry.
Do not change OptChat's external-skill policy in another repository. Save the owner's
requested memory note with the final name and verified release state.

### 7. Git and production closeout

Stage explicit task paths, commit conventionally and push. Update the existing PR and wait
for final-candidate required CI. Merge only with no unresolved required checks/review findings.
Restore main and verify its remote state. Confirm the Pages deployment for the merged SHA,
fetch the production landing/HOWTO and compare their bodies with the deployed candidate.
Then create the unused production version tag. No staging environment is configured: beta
deployment/tagging is N/A, not PASS. App Store/TestFlight/device deployment is also N/A.
Do not create a GitHub Release unless separately required by the repository's release policy
or explicitly requested; a production tag and a release object are different actions.
Delete the merged working branch (safe `-d`, remote delete if still present), remove task
worktrees if any, and clean only task-owned scratch. Keep the detailed plan and evidence summary.

## Verification commands

| Command | Expected |
|---|---|
| `python3 skills/mneves-render/tests/test_starters.py` | Real starter acceptance passes; missing required engine is explicit failure |
| `npx skills-ref@0.1.5 validate skills/mneves-render` | Skill valid |
| `npx skills@latest add . --list` | New name discovered, old name absent |
| `bash tools/scripts/build-site.test` | Complete and repeatable generated catalog |
| `tools/scripts/build-site.sh` | Generated files match committed sources |
| `bash tools/scripts/check-defaults-block.sh` and `.test` | Release/date/role guards and planted controls pass |
| `ast-grep scan --config sgconfig.yml .` | No forbidden types |
| `bash .githooks/pre-commit.test` | Hook controls pass |
| `cd tools && bun run typecheck && bun run lint` | Existing tools gates pass |
| `git diff --check` | No whitespace errors |
| Final GitHub CI run | All required jobs pass on the exact candidate |

## Stop conditions

Do not overwrite another session's work, force-push, reuse an existing version tag, bypass
required checks, fabricate an absent staging environment or suppress an essential failed gate.
If DOCX visual acceptance is an essential release criterion and no real engine can run, report
the concrete blocker. Do not claim a CSS/HTML check proves Word pagination. Confirm any
materially expanded runtime installation before changing host applications.

## Execution and advisor record

Completed: read-only plan adviser and deep audit; original starters produced six regression
failures, then nine starter tests passed after corrections. Local Pandoc 3.12.1, WeasyPrint
70.0 and Poppler 26.10 were used. Inspected all five generated fixture PDF pages and sample
HTML at 1280/390 px: complete readable content, shared styling, no mobile overflow; axe 4.12.1
reported 31 passes and zero violations. Local DOCX preview command failed because its target
application is absent; CI LibreOffice previews are the selected acceptance route.

Existing gates passed: site repeatability, defaults guard/control, precommit hook, ast-grep,
tools typecheck/lint (preexisting lint warnings), codex-lane and 163 release-contract tests.
The active-content filter passed eight test methods with adversarial subcases, including
real Pandoc HTML/DOCX refusal while preserving existing outputs, and the nine rendering
tests passed with that filter installed. The implementation is complete; independent review,
CI previews and deployment receipts are tracked in the pull request and Actions runs so
release evidence names the actual immutable candidate rather than a predicted commit.
