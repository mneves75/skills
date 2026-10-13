# Pandoc starter recipe

Use this when the project has no established renderer. Requires external `pandoc`;
the PDF example also needs `weasyprint`. Browser printing is an alternative, not a required
second engine. Discover installed versions and check their supported flags before use.

Copy the skill's `assets/` files into a project-owned renderer directory, such as
`docs/render/`. Run the following smoke commands **from that directory**. The defaults
resolve template/CSS paths against the working directory; a production wrapper must set
that directory itself and resolve source/output paths before changing it.

The stylesheet gives the generated footnote-return link an ASCII `[back]` label because
symbol/variation-selector glyph coverage differs across PDF engines. It keeps the same
link target. Localize that label with the document language when adapting the stylesheet.

```sh
pandoc --version
weasyprint --version
mkdir -p output
pandoc --defaults=html.yaml --resource-path=. sample.md --output=output/sample.html
pandoc --defaults=docx.yaml --resource-path=. sample.md --output=output/sample.docx
weasyprint output/sample.html output/sample.pdf
```

These commands exercise the templates; they are not the complete production wrapper.
Implement the failure/temporary-output contract in `SKILL.md` when exposing a project command.
WeasyPrint can emit warnings and still exit successfully: read stderr and reject missing
resources; do not assume `fail-if-warnings` in Pandoc applies to another engine.

For real input, explicitly choose `--resource-path` containing the source's asset directory.
Pass the absolute source/output paths, selected language and page title as data. The template
does not print metadata `title` as another heading: the source owns the visible title.
For a frontmatter-only title, add a title heading deliberately to the render tree; do not
silently omit it or duplicate a source H1. Never insert title metadata as unescaped raw HTML.
The DOCX defaults clear the metadata title for this body-H1 fixture; adapt that override
for frontmatter-only titles as described in the Word reference.

The sample uses Pandoc Markdown, which includes footnotes and tables. Select the actual
reader rather than treating `gfm`, CommonMark and Pandoc Markdown as interchangeable.
Turning off `raw_html` and `raw_tex` is a conservative starter choice, not a sanitizer or
a guarantee that all unsupported extensions will raise warnings. Inspect the document tree
and compare content. Do not silently change the reader just to suppress a warning.

For untrusted documents, inspect image/resource destinations and relevant metadata before
rendering, and use host sandbox/network restrictions where available. `embed-resources`
can read local or remote resources. Disabling raw HTML does not stop image URLs from fetching.
Allow only authorized resources inside approved roots; do not follow arbitrary absolute
paths or traversal outside them. This recipe assumes its bundled sample is trusted.

Keep the generated HTML as the PDF input. With a browser, wait for document fonts and images,
use print CSS and CSS page size, enable necessary background printing and disable browser
URL/date headers. With WeasyPrint, check actual layout and font availability: not all browser
CSS or JavaScript rendering works there. Math/diagrams need a supported static representation
shared with DOCX/PDF; install no network-dependent runtime in the final artifact by default.

`--embed-resources` makes local HTML dependencies self-contained. Verify by opening the
result offline; JavaScript-loaded assets and remote font assumptions need separate handling.
For asset bundles instead, copy/rewrite paths deliberately and deliver the whole bundle.

Primary reference: [Pandoc manual](https://pandoc.org/MANUAL.html), especially readers,
defaults files, resource paths, templates, reference documents and PDF engines.
