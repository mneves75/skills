# Skills landing-page redesign

Status: Implemented and visually reviewed; final branch acceptance tracked in PR #13.
Requested surface: `https://mneves75.github.io/skills/`, implemented by `site/index.html`.
Original delivery: working-branch PR. The owner separately authorized merging and
publishing during release closeout on 2026-10-13.

## Observed problem

The live page presents a long list of capabilities before its skill catalog. Its
introductory paragraph, repeated equal-sized cards and generic platform typography
provide little help choosing among the procedures. The live catalog has thirteen
skills; this task's source catalog adds the fourteenth, `mneves-security`.

## Confirmed product context

Developers using coding agents need to find an appropriate procedure, understand its
boundaries and install it. Preserve English product copy, actual skill descriptions,
install commands, guide/source links, collection/readiness information and changelog.
The existing stack is static HTML/CSS with minimal JavaScript and GitHub Pages; no
framework migration is necessary. No customer claims, fake metrics or testimonials.

## Research and alternatives

Checked 2026-10-13:

- [Webflow's 2026 design review](https://webflow.com/blog/web-design-trends-2026)
  treats distinctive systems and edited copy as responses to visual sameness. This is
  a vendor's trend interpretation, not a security/performance standard.
- [NN/g visual-design guidance](https://www.nngroup.com/articles/good-visual-design/)
  supports hierarchy, consistent alignment and purposeful color.
- [Responsive typography](https://web.dev/learn/design/typography) and
  [reduced motion](https://www.w3.org/WAI/WCAG22/Techniques/css/C39) support the
  implementation/accessibility checks.

Compare an editorial catalog organized around the visitor's jobs, a restrained
documentation index and a promotional landing page. The proposed editorial catalog
prioritizes comprehension and installation while allowing a distinctive visual system.
The promotional alternative risks burying the actual procedures beneath a sales story.
Five-year preference: static content, local assets, semantic links and durable tokens;
avoid animation libraries, fragile layout tricks and decorative metrics.

## Frozen acceptance

1. Retain all fourteen source skills exactly once in the catalog, their guide links,
   installation options, pstack collection information, readiness example/provenance
   and generated changelog markers. Preserve factual content and working functions.
   Copy feedback must be truthful when the clipboard is unavailable or rejects a write.
2. Replace the landing page's visual system with a coherent direction using Impeccable;
   record product truth, surface direction, final design tokens and its sidecar.
3. Responsive at desktop, tablet and narrow mobile widths with no page overflow,
   unreadable controls or hidden content. Keyboard focus, semantic structure, contrast
   and reduced-motion preferences remain usable. No new application dependency.
4. Inspect actual desktop/mobile renders and interactions; run the detector once and
   a fresh finish review. Fix material defects in a bounded correction pass.
5. Site generation remains complete/repeatable and skill/docs/version release gates
   remain passing. Explain any unverified runtime or publication surface honestly.
6. Provide a reviewable working-branch change and screenshots. Do not merge/publish or
   alter host installations without the authorized target.

## Ordered implementation

1. Product context and delegated visual judgment confirmed by “continue, decide what it is best.”
2. Write PRODUCT.md; run the required direction seed and compare grounded alternatives.
   Record the chosen direction in a development-only surface brief before UI edits.
3. Read the craft floor, implement the complete responsive landing page, and self-host
   any selected font with its license/provenance. Keep truthful copy and existing links.
4. Exercise preserved interactions and failure states, capture the desktop/mobile
   matrix, run accessibility/overflow checks and the mechanical design detector.
5. Run a fresh finish reviewer; correct its material findings and recapture
   once. Extract the final DESIGN.md and sidecar from the actual built surface.
6. Rerun generation/release gates affected by the redesign, record evidence, commit,
   update the PR and observe CI. Remove task-owned temporary evidence/processes.

## Selected direction and verification seam

Read mode, code-led civic wayfinding index: expressive self-hosted grotesk typography,
white/deep-ink grounds, cobalt install area, thin structural rules and four job-based
catalog groups. The seed `a5028a8b` assigns grounded candidate 6. The owner delegated
selection, so no further design interview is required. The development-only surface
brief records the full direction contract and the evaluated challengers.

The copy regression uses the actual browser control and synthetic Clipboard API
success/rejection/unavailability. This public seam catches false success and copied
text mismatches without a fake DOM or an application dependency. Run
`tools/scripts/check-site-copy.sh <site-url>` through the approved browser route.

## Risk and rollback

Owner: frontend code/documentation. No backend, data or provider change. Preserve
changelog markers because the existing generator rewrites that region. Revert the
redesign commit and regenerate the site to recover the prior presentation.

## Evidence

Public live desktop page inspected before editing. A real isolated browser probe made
`navigator.clipboard` unavailable, clicked the existing npx copy button, and observed
`Copied` / `Command copied` despite no copy operation. This is the failing control for
the copy error-state fix; test successful and rejected writes after the implementation.

Impeccable context loaded; the owner confirmed context and delegated visual judgment.
PRODUCT.md records that scope. The implemented direction preserves all fourteen skills
and guide anchors, both install commands, the separate collection, historical assessment
provenance and generated changelog. The font is self-hosted, with its OFL and source pin
in NOTICE; the browser loaded only local runtime resources.

The copy regression failed against the prior public page when clipboard access was
unavailable, then passed all three scenarios against the local implementation. The
generation test now compares the catalog with source skills and HOWTO targets. Its
planted missing-entry control failed before the guard; missing, duplicate and broken
guide controls all passed after implementation. This adopts the advisor's maintenance
recommendation without adding a content framework.

Actual browser checks covered 1440px desktop, 768px tablet, 390px mobile and 320px narrow
mobile. A grid minimum-width defect was corrected; page width matches the viewport.
Axe 4.12.1 reported zero WCAG A/AA violations and zero incomplete checks on the final
desktop/mobile/narrow checks and the dark palette. Keyboard focus is visible; the code
sample is focusable when horizontally scrollable. Reduced motion yields automatic
scrolling and a zero-duration arrow transition.

The mechanical detector ran once and returned eight cramped-padding warnings. The
fresh visual reviewer disproved those warnings against the rendered spacing and
computed catalog/changelog insets of 24px/16px. It found one material guide-grouping
defect; the post-fix verdict scored that issue resolved with no visible regressions.
That verdict covers the named fix, not a second whole-surface audit. The named
Impeccable reviewer/documenter roles were unavailable; fresh available agents applied
their documented procedures. No approved comp or official quality-bar card exists for
the custom grounded direction, so no comp-fidelity or official-ceiling pass is claimed.

Local checks passed: site generation and repeatability/catalog controls, JavaScript
syntax, Bash syntax, ast-grep, the pre-commit hook test and model-defaults guard. cccc
1.8.0 used CLI defaults with no repository configuration: one expected JavaScript file,
one analyzed, zero parse errors, exit 0; cognitive 2 and cyclomatic 6. HTML/CSS/Markdown
and Bash are outside that source scan. Codemap did not index the changed static/docs
targets; its missing importer results are not zero-importer proof. Direct source
inspection identified the site generator, test and GitHub Pages workflow as callers.

Reviewable captures: [desktop](assets/desktop.png) and [mobile](assets/mobile.png).
Independent acceptance and final CI results are recorded on the exact PR revision.
Publication is checked against the authorized merge and its Pages workflow.

## Release integration

PR #13 merged as `a50ef5c`, preserving a concurrent pstack synchronization that raised
the collection inventory from 33 to 36 skills. The landing page and PRODUCT.md carried
the older count. A regression at the existing generated-site seam reproduced the
mismatch before those two texts were corrected. The guard compares the published
stated collection quantity with its current source inventory, so future synchronizations
cannot silently preserve a stale landing count. Version remains 1.34.0 for this
release closeout; its existing README badge and changelog stay aligned.
