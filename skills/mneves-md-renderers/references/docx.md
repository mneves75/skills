# Editable Word output and shared styles

Pandoc writes a real DOCX from the document tree. Avoid HTML screenshots or whole-page
images: they lose editable text, heading navigation, list structure and searchable content.
The bundled defaults create a functional first draft with Pandoc's built-in styles; they
do **not** make it visually match the HTML automatically.

The starter clears the metadata title because the sample has a visible H1 in its body.
This prevents Word from printing the title twice. For a source with only a frontmatter
title, remove that override or map the title into a body heading first. Check this choice
per input rather than blindly discarding titles.

For the final project renderer, create a project-owned reference document:

```sh
(set -C; pandoc --print-default-data-file reference.docx > reference.docx)
```

Run in a task-owned directory where that filename does not already hold user work. Customize
the reference using Word, LibreOffice or the project's OOXML library, then pass
`--reference-doc=reference.docx` on subsequent conversions. Never require one agent vendor's
document tool; if an installed document skill helps, use it, otherwise use local capabilities.

Map the chosen design to these Word concepts:

| Shared choice | Word mapping |
|---|---|
| Body font, size, line height and paragraph spacing | Normal, Body Text and First Paragraph |
| Heading hierarchy | Heading 1–6, with keep-with-next |
| Link color and underline | Hyperlink |
| Code family and size | Verbatim Char and Source Code |
| Table text, borders, padding and header contrast | Table style plus generated table properties |
| Print size and margins | Section page size/margins |
| Figures and captions | Image dimensions and caption styles |

Pandoc's writer may apply direct formatting that overrides reference styles. Inspect the
generated file, not just the reference. Table width, row splitting, repeated header rows,
image alt text, language and internal links all need output checks. Only claim a feature
that survives generation and reopening. If post-processing is necessary, make it part of
the repeatable command rather than hand-editing each generated output.

For the starter CSS, the corresponding baseline is Arial body at 12 pt, 1.55 line spacing,
Heading 1 at 24 pt, Heading 2 at 18 pt, Heading 3 at 13.5 pt, and A4 with 20 mm margins.
CSS pixels map at 96 px/in; Word points at 72 pt/in. Match colors and spacing as well.
Use an installed font family with glyph coverage; record substitutions instead of pretending
unavailable fonts rendered. Higher heading levels need deliberate styles when the source uses them.

Reopen the DOCX and verify its heading/list/table structure. Render it through an available
Word-compatible engine to PDF or page images, then inspect **every page**. Give the preview
a separate path from the requested PDF so it cannot overwrite the HTML-derived PDF.
Use an isolated conversion profile if the engine supports one; do not disrupt an open editor.
If no preview engine exists, report DOCX visual validation as unverified, not passed.

Word and HTML/PDF can preserve the same content and design while line wraps or pagination
differ. Do not claim pixel parity between independent layout engines. Keep the generated
DOCX free of accidental author names, machine paths, comments and revision history.

Primary reference: [Pandoc reference documents](https://pandoc.org/MANUAL.html#option--reference-doc).
