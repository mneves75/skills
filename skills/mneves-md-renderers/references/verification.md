# Renderer acceptance

Freeze the formats and features required by the source before testing. Keep fixture output
separate from user deliverables. The starter sample covers ordinary text, accents, a number,
headings, emphasis, lists, tables, code, links and a footnote; it does not cover every dialect.

## Content and structure

- Compare the source document tree with extracted output: all sections, numeric values,
  captions, table cells, code, links and footnotes must survive. Normalize only presentation
  whitespace and pagination; keep case, punctuation and accents meaningful.
- Check HTML with a DOM parser: language/title, heading hierarchy, actual link targets,
  image alt text, tables and no unwanted executable source content.
- Open DOCX as a ZIP and inspect `word/document.xml`, styles and relationships, or reopen it
  with a document library. Confirm editable paragraphs, real tables, heading styles,
  numbering and hyperlinks; a nonempty ZIP is not acceptance.
- Extract PDF text with an available tool such as `pdftotext`. Check key sentences, values,
  footnotes and the final section. Inspect embedded links and page count where supported.
  Text extraction alone does not prove reading order, accessibility or good layout.

## Visual acceptance

- HTML: inspect desktop (for example 1280 px) and mobile (390 px) screenshots. Check the
  full content, keyboard focus, tables, code and long URLs; no unintended page overflow.
- PDF: rasterize **every page** with a tool such as `pdftoppm`, then inspect them for clipped
  text, missing glyphs/images, broken tables, stranded headings and excessive blank space.
- DOCX: render with an available Word-compatible viewer and inspect every page. Do not
  substitute the independently generated PDF for the DOCX preview.
- Compare equivalent HTML/PDF sections: same design and content, with pagination adaptations.
  Check DOCX against the same design intent, accounting for engine-specific line wrapping.

For a short fixture all pages fit in a small review. For a long deliverable, do not quietly
substitute a spot check: report the actual coverage and anything uninspected.

## Meaningful probes

Run the project entry point, not only individual engines:

1. Render a small valid document to each requested format. Check actual artifacts.
2. Change a sentinel sentence and regenerate; old text must disappear and new text appear.
3. Use a source/output path with spaces and accents. Resolve a local image from a source
   directory different from the launch directory.
4. Supply a missing source, missing image or missing engine. Expect a clear failure and
   no stale final output represented as fresh success.
5. Exercise actual special features: a multipage table, long code, math, Mermaid, raw HTML
   or unusual scripts when present. Either support them or name the blocked feature.

Keep output logs and engine versions as evidence. Clean only task-created temporary files;
never remove user documents to tidy the output folder. Report structural and visual results
separately and disclose untested engines or formats.
