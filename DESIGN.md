---
name: "mneves75/skills landing page"
description: "A civic wayfinding index for portable coding-agent procedures."
colors:
  accent: "#164bd6"
  blue: "#164bd6"
  on-blue: "#fff"
  blue-muted: "#d7e4ff"
  lime: "#def59b"
  on-lime: "#203615"
  paper: "#fff"
  ink: "#132236"
  muted: "#43556c"
  rule: "#d5dce5"
  soft: "#f0f5ff"
  code: "#edf1f7"
  focus: "#164bd6"
  accent-dark: "#abc4ff"
  blue-dark: "#1645bd"
  paper-dark: "#111b2b"
  ink-dark: "#f1f5fc"
  muted-dark: "#b6c4d8"
  rule-dark: "#36465d"
  soft-dark: "#1b2d49"
  code-dark: "#21324a"
  focus-dark: "#d8ee9c"
typography:
  display:
    fontFamily: "Bricolage,Arial,sans-serif"
    fontSize: "clamp(3rem,6.3vw,5.65rem)"
    fontWeight: 650
    lineHeight: 1.1
    letterSpacing: "-.025em"
  headline:
    fontFamily: "Bricolage,Arial,sans-serif"
    fontSize: "clamp(2rem,3.8vw,3.3rem)"
    fontWeight: 650
    lineHeight: 1.1
    letterSpacing: "-.025em"
  title:
    fontFamily: "Bricolage,Arial,sans-serif"
    fontSize: "1.3rem"
    fontWeight: 650
    lineHeight: 1.1
    letterSpacing: "-.015em"
  body:
    fontFamily: 'Bricolage,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif'
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: 'Bricolage,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif'
    fontSize: ".95rem"
    fontWeight: 600
    lineHeight: 1.55
  nav:
    fontFamily: 'Bricolage,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif'
    fontSize: ".95rem"
    fontWeight: 400
    lineHeight: 1.55
  action:
    fontFamily: 'Bricolage,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif'
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: 1.55
  copy:
    fontFamily: 'Bricolage,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif'
    fontSize: ".85rem"
    fontWeight: 400
    lineHeight: 1.55
  command:
    fontFamily: "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
    fontSize: ".79rem"
    fontWeight: 400
    lineHeight: 1.8
rounded:
  inline: "3px"
  control: "4px"
spacing:
  xs: ".5rem"
  sm: ".75rem"
  md: "1rem"
  inset: "1.25rem"
  lg: "1.5rem"
  xl: "2rem"
  group: "2.5rem"
  section: "3.5rem"
  section-wide: "4rem"
  gutter: "clamp(1.25rem,4vw,3rem)"
components:
  action:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.action}"
    rounded: "{rounded.control}"
    padding: ".65rem 1.1rem"
  action-hover:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.paper}"
  copy-button:
    backgroundColor: "transparent"
    textColor: "{colors.on-blue}"
    typography: "{typography.copy}"
    rounded: "{rounded.control}"
    padding: ".4rem .65rem"
  copy-button-hover:
    backgroundColor: "{colors.on-blue}"
    textColor: "{colors.blue}"
  site-nav:
    textColor: "{colors.ink}"
    typography: "{typography.nav}"
    padding: ".5rem 0"
  category-link:
    backgroundColor: "{colors.soft}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.inline}"
    padding: ".7rem .8rem"
  category-link-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
  skill-entry:
    textColor: "{colors.ink}"
    typography: "{typography.title}"
  new-procedure:
    backgroundColor: "{colors.lime}"
    textColor: "{colors.on-lime}"
    rounded: "{rounded.control}"
    padding: "{spacing.inset}"
  sample-card:
    backgroundColor: "{colors.soft}"
    rounded: "{rounded.control}"
    padding: "1.65rem"
  release-row:
    textColor: "{colors.ink}"
    padding: "1rem 0"
---

# Design System: mneves75/skills landing page

## Overview

**Creative North Star: "The Civic Wayfinding Index"**

A clear public index: expressive headings establish the route, thin rules align the categories, and each procedure remains easy to read. White and deep ink carry the reading surface; committed cobalt gives installation a distinct place, while lime marks the new procedure and selected browser states.

This records the implemented landing page in site/index.html and its copy controller in site/copy-command.js. It does not govern the generated HOWTO or the historical readiness report. The visual system uses a local display face, native links and small controls, with no raster artwork or ornamental scene.

The normative frontmatter preserves the source's color names and exact values. Dark
variants are separate primitives; the sidecar maps them to the same CSS roles under
the system preference. Component snippets include font and color fallbacks so they
can render independently; the live page loads its local font.

**Key Characteristics:**

- Expressive Bricolage headings over aligned, lightly ruled category rows.
- Solid cobalt installation surfaces with restrained lime emphasis.
- Flat, nearly square forms; readable content stays visible without JavaScript.
- System light/dark preferences, visible focus and reduced-motion support.

## Colors

Clean reading neutrals meet saturated installation blue and a small lime highlight.

### Primary

- **Route Cobalt** (`accent`, `blue`, `focus`): links and keyboard focus on the reading surface, plus the solid installation region.
- **Night Route Cobalt** (`blue-dark`): the dark-preference installation fill.
- **Light Route Blue** (`accent-dark`): links and action hover on the dark reading surface.
- **Blue-Surface Text** (`on-blue`, `blue-muted`): white command text and a tinted secondary status line on cobalt.

### Secondary

- **Fresh Lime** (`lime`, `on-lime`): the new-procedure fill and its dark green text; also browser text selection and focus inside installation.
- **Night Focus Lime** (`focus-dark`): keyboard outlines on the dark reading surface.

### Neutral

- **Reading Paper and Deep Ink** (`paper`, `ink`): page background, headings and primary action; the action reverses the pair.
- **Quiet Ink and Structural Rule** (`muted`, `rule`): supporting prose and thin separators.
- **Soft Blue Paper and Code Surface** (`soft`, `code`): category navigation, the sample aside and code backgrounds.
- **Night Reading Neutrals** (`paper-dark`, `ink-dark`, `muted-dark`, `rule-dark`, `soft-dark`, `code-dark`): replacements for those six reading roles when the system requests dark mode.

**The Role Before Hue Rule.** Keep reading surfaces, installation surfaces and new-procedure emphasis distinct; use the existing theme assignments rather than applying one accent to every region.

## Typography

**Display Font:** local Bricolage Grotesque, registered as Bricolage, with Arial and sans-serif fallbacks.
**Body Font:** Bricolage, followed by the platform stack recorded in the frontmatter.
**Label/Mono Font:** the same body face for labels; native monospace for commands and code.

The variable face carries expressive, compact headings without changing the reading
voice. Headings balance their lines; long procedure names can wrap anywhere. The
local font declares weights (200–800) with swap loading.

### Hierarchy

- **Display** (`typography.display`): the main heading, limited to a short measure (14ch).
- **Headline** (`typography.headline`): major sections; category and installation headings use a smaller contextual title (1.6rem).
- **Title** (`typography.title`): procedure and resource titles; the how-to steps use a slight contextual increase (1.35rem).
- **Body** (`typography.body`): the reading baseline. Catalog summaries use a smaller inherited-body size (.95rem); introductory copy is larger (1.15rem).
- **Label** (`typography.label`): category links. Site navigation uses its own regular-weight `nav` role; `action` and `copy` preserve the two control sizes.
- **Command** (`typography.command`): installation commands. The longer assessor block uses a different reading setting (.82rem, line-height 1.7).

These are observed roles, not a mathematical type scale. Short catalog summaries
use bounded measures (45ch), widened on narrow phones (65ch); the longer privacy note
uses a reading measure (75ch). The introductory measure changes with composition
rather than imposing one line length on all content.

**The Expressive Heading Rule.** Use the local Bricolage face for headings; keep monospace for commands and inline code.

## Layout

A centered reading container has a maximum width (78rem) and the fluid `gutter`
spacing token. The opening pairs a wider heading column with a narrower introduction
(1.7fr / 1fr). The installation strip groups commands beneath its title. The catalog
uses a fixed category column (13rem), followed by a two-column procedure list.

Spacing distinguishes tight content groups from larger section boundaries. Catalog
groups keep `spacing.lg` above and `spacing.xl` below their contents; release rows keep
`spacing.md` above and below. Thin rules sit outside that inset. The regular procedures
remain unboxed; the new procedure and historical sample use filled surfaces.

The implemented responsive thresholds are maximum widths:

- **Compact** (64rem): the opening ratio becomes (1.4fr / 1fr), the category column narrows (10rem), and install commands stack.
- **Stacked** (48rem): the body baseline becomes (16px); the opening, category groups, steps, resources and assessor section become single-column. Category navigation keeps two columns, and the procedure list still has two.
- **Narrow** (36rem): procedures become one column. The main heading uses a narrower fluid setting (`clamp(2.9rem,10.4vw,3.6rem)`), command text becomes smaller (.76rem), and release columns tighten (5.9rem / 1fr).

The rem thresholds correspond to (1024px), (768px) and (576px) at a (16px) root;
the CSS keeps rem units. Header links wrap without a separate menu. Responsive
composition follows document order and keeps the installation commands reachable.

**The Aligned Category Rule.** Use a shared category column and thin separators to organize the catalog; retain vertical padding around each group.

## Elevation & Depth

The page is flat: it uses no box shadows. Thin structural rules, solid cobalt and
soft blue surfaces separate regions. Lime gives the new procedure local emphasis.
Keyboard focus uses an offset outline, not an elevation effect.

**The Flat Surface Rule.** Separate regions with rules and solid tonal fills; the implemented system has no box shadows.

## Shapes

Small corners belong to the `inline` and `control` radius tokens: code and category
links use the former; actions, copy buttons, installation and filled asides use the
latter. Unboxed catalog entries retain their native rectangular flow. Rules are thin
(1px); category arrows are inline vector geometry (16px, stroke-width 1.5).

## Components

### Buttons

The primary action is a native link with the ink/paper reversal and compact corners.
It has a minimum target height (46px) and changes to the link accent on hover. Copy
buttons are transparent, outlined controls on cobalt with a minimum target height
(44px) and width (65px). Hover reverses them to white with the original Route Cobalt
text; that hover text remains the same in both themes.

A copy click disables the button, changes its label to “Copying” and announces
progress. A successful write shows “Copied” and resets the label after a short delay
(1500ms). A failed or unavailable write restores “Copy,” explains manual recovery
and focuses the command. The live status is polite; the command remains selectable.

**The Honest Control Rule.** Show copy progress, success and a recoverable failure; preserve the command as a selectable keyboard target.

### Navigation

Site navigation uses regular reading text, horizontal gaps and an underline on hover.
The category links are softly filled rectangles with a small downward SVG arrow.
Their hover reverses to ink/paper; the arrow moves slightly only when reduced motion
is not requested. Both use the shared visible-focus treatment.

### Cards / Containers

A standard procedure is an unboxed title, summary, example and nearby guide link.
The guide follows its content with the normal group gap; it does not stretch to
align to the bottom of a taller neighbor. The new procedure uses Fresh Lime, dark
green content and the `inset` token. The sample aside uses Soft Blue Paper with its
own observed padding. Neither surface casts a shadow.

### Release Rows

Versions and dates share a leading column; the change description follows. Rows
use vertical inset and a bottom rule. Versions and the sample result use tabular
numerals; dates are smaller supporting text.

The sidecar contains eight self-contained previews of these implemented patterns.
There are no input fields, chips, dialogs or theme-switch controls to document.
Snippet hover, focus and disabled CSS is retained; clipboard behavior belongs to
the source controller, not the previews.

## Do's and Don'ts

### Do:

- **Do** preserve the category alignment, readable procedure summaries and nearby guide links.
- **Do** use the existing light/dark color assignments and visible focus treatments.
- **Do** keep the local Bricolage face, balanced headings and the observed responsive type hierarchy.
- **Do** keep install commands selectable and show truthful copy status.

### Don't:

- **Don't** turn the unboxed catalog entries into a wall of identical filled cards.
- **Don't** replace the local display face with a system display face or use monospace as decoration.
- **Don't** add raster illustrations, decorative controls or shadows to this landing-page system.
- **Don't** hide content behind motion or make copy success appear before the clipboard write succeeds.

Source of visual truth: [landing page](site/index.html) and
[copy controller](site/copy-command.js). Product constraints stay in
[PRODUCT.md](PRODUCT.md); the surface direction stays in its
[brief](.impeccable/surfaces/site-index-html.md).

