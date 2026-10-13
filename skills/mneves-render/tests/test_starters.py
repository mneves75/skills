#!/usr/bin/env python3
"""Real-engine starter acceptance; Python 3.10+, standard library only.

Run directly. --artifacts DIR retains fixtures, logs, PDFs and page PNGs for
human inspection. --require-office also requires actual DOCX-to-PDF conversion
and rasterization; structural checks alone never establish visual acceptance.
Fixtures are trusted local content, not a test of an engine security sandbox.
"""

import argparse
from contextlib import ExitStack
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/package/2006/relationships}"
PDF = "{http://www.w3.org/1999/xhtml}"
PUNCTUATION = 'Keep "literal quotes", an apostrophe\'s value, ... and -- and --- exactly.'
METADATA = ("Metadata title ação", "Metadata subtitle café", "Fixture Author", "2026-10-12")
LONG_TOKEN = "BEGIN" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 24 + "END"


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_body = False
        self.hidden = 0
        self.text = []

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.in_body = True
        if tag in ("script", "style"):
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag == "body":
            self.in_body = False
        if tag in ("script", "style"):
            self.hidden -= 1

    def handle_data(self, data):
        if self.in_body and not self.hidden:
            self.text.append(data)


class StarterAcceptance(unittest.TestCase):
    workspace: Path
    assets: Path
    require_office = False
    retain = False

    def run_engine(self, arguments, cwd, expect_success=True):
        result = subprocess.run(arguments, cwd=cwd, capture_output=True, text=True,
                                encoding="utf-8", timeout=120, check=False)
        with (self.workspace / "engines.log").open("a", encoding="utf-8") as log:
            log.write(f"$ {arguments!r}\nexit={result.returncode}\n")
            log.write(result.stdout + result.stderr + "\n")
        if expect_success:
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, "Invalid input was accepted")
            self.assertTrue(result.stderr.strip(), "Engine failed without a diagnostic")
        return result.stdout

    def render(self, name, source, formats=("html", "docx"), resources=None):
        fixture = self.workspace / name
        fixture.mkdir()
        for asset in self.assets.iterdir():
            if asset.is_file():
                shutil.copy2(asset, fixture / asset.name)
        scripts = self.assets.parent / "scripts"
        if scripts.is_dir():
            shutil.copytree(scripts, fixture / "scripts")
        for filename, content in (resources or {}).items():
            (fixture / filename).write_text(content, encoding="utf-8")
        markdown = fixture / "source ação.md"
        markdown.write_text(source, encoding="utf-8")
        before = markdown.read_bytes()
        outputs = {}
        for kind in formats:
            output = fixture / f"output.{kind}"
            self.run_engine(["pandoc", f"--defaults={kind}.yaml", "--resource-path=.",
                             f"--metadata=pagetitle:{name}",
                             str(markdown), f"--output={output}"], fixture)
            self.assertTrue(output.is_file() and output.stat().st_size > 0)
            outputs[kind] = output
            if kind == "docx" and self.require_office:
                self.office_preview(output)
        self.assertEqual(markdown.read_bytes(), before, "Rendering changed the source")
        return outputs

    def visible_html(self, output):
        parser = VisibleText()
        parser.feed(output.read_text(encoding="utf-8"))
        return " ".join("".join(parser.text).split())

    def docx_xml(self, output, member="word/document.xml"):
        with zipfile.ZipFile(output) as archive:
            return ET.fromstring(archive.read(member))

    def docx_text(self, output):
        paragraphs = []
        for paragraph in self.docx_xml(output).iter(W + "p"):
            parts = []
            for node in paragraph.iter():
                if node.tag == W + "t":
                    parts.append(node.text or "")
                elif node.tag in (W + "br", W + "cr"):
                    parts.append("\n")
                elif node.tag == W + "tab":
                    parts.append("\t")
            paragraphs.append("".join(parts))
        return "\n".join(paragraphs)

    def make_pdf(self, html):
        pdf = html.with_suffix(".pdf")
        self.run_engine(["weasyprint", str(html), str(pdf)], html.parent)
        self.assertTrue(pdf.is_file() and pdf.stat().st_size > 0)
        text = self.run_engine(["pdftotext", "-layout", str(pdf), "-"], html.parent)
        if self.retain:
            self.rasterize(pdf)
        return pdf, text

    def rasterize(self, pdf):
        prefix = pdf.parent / (pdf.stem + "-page")
        self.run_engine(["pdftoppm", "-r", "85", "-png", str(pdf), str(prefix)], pdf.parent)
        pages = list(pdf.parent.glob(prefix.name + "-*.png"))
        info = self.run_engine(["pdfinfo", str(pdf)], pdf.parent)
        count = next(int(line.split(":", 1)[1]) for line in info.splitlines()
                     if line.startswith("Pages:"))
        self.assertEqual(len(pages), count, "Every PDF page needs a raster artifact")

    def office_preview(self, docx):
        office = shutil.which("libreoffice") or shutil.which("soffice")
        self.assertIsNotNone(office, "Required DOCX preview engine is absent")
        preview = docx.parent / "office-preview"
        preview.mkdir(exist_ok=True)
        profile = docx.parent / "office-profile"
        self.run_engine([office, f"-env:UserInstallation={profile.as_uri()}", "--headless",
                         "--convert-to", "pdf", "--outdir", str(preview), str(docx)], preview)
        pdf = preview / (docx.stem + ".pdf")
        self.assertTrue(pdf.is_file() and pdf.stat().st_size > 0,
                        "Office did not produce an actual DOCX preview")
        text = " ".join(self.run_engine(["pdftotext", str(pdf), "-"], preview).split())
        for paragraph in self.docx_text(docx).splitlines():
            if paragraph.strip():
                self.assertIn(" ".join(paragraph.split()), text)
        self.rasterize(pdf)

    def test_metadata_visible_in_html(self):
        source = (f'---\ntitle: {METADATA[0]}\nsubtitle: {METADATA[1]}\n'
                  f'author: {METADATA[2]}\ndate: "{METADATA[3]}"\n---\n\nBody sentinel.\n')
        outputs = self.render("metadata-html", source, ("html",))
        visible = self.visible_html(outputs["html"])
        for field in METADATA:
            self.assertIn(field, visible)

    def test_metadata_visible_in_docx(self):
        source = (f'---\ntitle: {METADATA[0]}\nsubtitle: {METADATA[1]}\n'
                  f'author: {METADATA[2]}\ndate: "{METADATA[3]}"\n---\n\nBody sentinel.\n')
        outputs = self.render("metadata-docx", source, ("docx",))
        visible = self.docx_text(outputs["docx"])
        for field in METADATA:
            self.assertIn(field, visible)

    def test_literal_punctuation(self):
        outputs = self.render("punctuation", "# Punctuation\n\n" + PUNCTUATION + "\n")
        with self.subTest(format="html"):
            self.assertIn(PUNCTUATION, self.visible_html(outputs["html"]))
        with self.subTest(format="docx"):
            self.assertIn(PUNCTUATION, self.docx_text(outputs["docx"]))
        _, text = self.make_pdf(outputs["html"])
        with self.subTest(format="pdf"):
            self.assertIn(PUNCTUATION, " ".join(text.split()))

    def test_distinct_metadata_and_body_titles_survive(self):
        outputs = self.render("distinct-titles", "---\ntitle: Metadata heading\n---\n\n"
                              "# Distinct body heading\n\nBody sentence.\n")
        for kind, text in (("html", self.visible_html(outputs["html"])),
                           ("docx", self.docx_text(outputs["docx"]))):
            with self.subTest(format=kind):
                self.assertIn("Metadata heading", text)
                self.assertIn("Distinct body heading", text)

    def test_regeneration_reads_changed_source(self):
        outputs = self.render("regeneration", "# Regeneration\n\nORIGINALSENTINEL.\n")
        fixture = outputs["html"].parent
        source = fixture / "source ação.md"
        for text in (self.visible_html(outputs["html"]), self.docx_text(outputs["docx"])):
            self.assertIn("ORIGINALSENTINEL", text)
        source.write_text("# Regeneration\n\nREPLACEMENTSENTINEL.\n", encoding="utf-8")
        before = source.read_bytes()
        for kind, output in outputs.items():
            self.run_engine(["pandoc", f"--defaults={kind}.yaml", "--resource-path=.",
                             "--metadata=pagetitle:Regeneration",
                             str(source), f"--output={output}"], fixture)
            if kind == "docx" and self.require_office:
                self.office_preview(output)
        _, pdf_text = self.make_pdf(outputs["html"])
        for text in (self.visible_html(outputs["html"]), self.docx_text(outputs["docx"]), pdf_text):
            self.assertIn("REPLACEMENTSENTINEL", text)
            self.assertNotIn("ORIGINALSENTINEL", text)
        self.assertEqual(source.read_bytes(), before)

    def test_missing_source_and_asset_are_engine_failures(self):
        outputs = self.render("negative-inputs", "# Valid local fixture\n", ("html",))
        fixture = outputs["html"].parent
        self.run_engine(["pandoc", "--defaults=html.yaml", "missing-source.md",
                         "--metadata=pagetitle:Missing source",
                         "--output=missing-source.html"], fixture, expect_success=False)
        source = fixture / "missing-asset.md"
        source.write_text("# Missing asset\n\n![Unavailable](missing.svg)\n", encoding="utf-8")
        self.run_engine(["pandoc", "--defaults=html.yaml", "--resource-path=.",
                         "--metadata=pagetitle:Missing asset",
                         str(source), "--output=missing-asset.html"], fixture, expect_success=False)

    def test_long_plain_token_survives_pdf(self):
        outputs = self.render("long-token", "# Long plain token\n\n" + LONG_TOKEN + "\n",
                              ("html",))
        _, text = self.make_pdf(outputs["html"])
        self.assertIn(LONG_TOKEN, "".join(text.split()), "PDF clipped a plain text token")

    def test_tall_local_svg_fits_pdf_page(self):
        # Text near both vertical extremes reveals clipping of an oversized figure.
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="600" height="2400" '
               'viewBox="0 0 600 2400"><rect width="600" height="2400" fill="white" '
               'stroke="black"/><text x="15" y="65" font-size="48">FIGURETOP</text>'
               '<text x="15" y="2370" font-size="48">FIGUREBOTTOM</text></svg>')
        outputs = self.render("tall-image", "# Tall figure\n\n![Tall local figure](tall%20figure.svg)\n",
                              ("html",), {"tall figure.svg": svg})
        fixture = outputs["html"].parent
        pdf, text = self.make_pdf(outputs["html"])
        self.assertIn("FIGURETOP", text)
        self.assertIn("FIGUREBOTTOM", text)
        bbox = fixture / "bounds.html"
        self.run_engine(["pdftotext", "-bbox", str(pdf), str(bbox)], fixture)
        tree = ET.parse(bbox)
        found = {}
        for page in tree.iter(PDF + "page"):
            for word in page.iter(PDF + "word"):
                if word.text in ("FIGURETOP", "FIGUREBOTTOM"):
                    found[word.text] = page
                    self.assertGreaterEqual(float(word.attrib["yMin"]), 0)
                    self.assertLessEqual(float(word.attrib["yMax"]), float(page.attrib["height"]))
                    self.assertGreaterEqual(float(word.attrib["xMin"]), 0)
                    self.assertLessEqual(float(word.attrib["xMax"]), float(page.attrib["width"]))
        self.assertEqual(set(found), {"FIGURETOP", "FIGUREBOTTOM"})
        self.assertIs(found["FIGURETOP"], found["FIGUREBOTTOM"], "Figure spans pages")

    def test_sample_has_editable_docx_structures(self):
        outputs = self.render("sample", (self.assets / "sample.md").read_text(encoding="utf-8"))
        document = self.docx_xml(outputs["docx"])
        title = "Renderer acceptance sample"
        self.assertEqual(self.docx_text(outputs["docx"]).count(title), 1,
                         "A body title should appear once")
        self.assertEqual(self.visible_html(outputs["html"]).count(title), 1,
                         "A body title should appear once")
        styles = {node.attrib.get(W + "val") for node in document.iter(W + "pStyle")}
        self.assertTrue({"Heading1", "Heading2"}.issubset(styles), styles)
        self.assertTrue(list(document.iter(W + "tbl")), "DOCX lacks an editable table")
        self.assertTrue(list(document.iter(W + "numPr")), "DOCX lacks a real list")
        self.assertTrue(list(document.iter(W + "hyperlink")), "DOCX lacks links")
        self.assertTrue(list(document.iter(W + "footnoteReference")), "DOCX lacks a footnote")
        relationships = self.docx_xml(outputs["docx"], "word/_rels/document.xml.rels")
        targets = {node.attrib.get("Target") for node in relationships.iter(R + "Relationship")}
        self.assertIn("https://pandoc.org/MANUAL.html", targets)
        footnotes = self.docx_xml(outputs["docx"], "word/footnotes.xml")
        self.assertIn("This footnote must survive conversion.",
                      "".join(node.text or "" for node in footnotes.iter(W + "t")))
        for sentinel in ("ação", "café", "1,234.56", '<not-an-html-element> & a "quoted" value'):
            self.assertIn(sentinel, self.docx_text(outputs["docx"]))
        _, text = self.make_pdf(outputs["html"])
        for sentinel in ("ação", "café", "1,234.56", "This footnote must survive conversion."):
            self.assertIn(sentinel, " ".join(text.split()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--artifacts", type=Path)
    parser.add_argument("--require-office", action="store_true")
    args = parser.parse_args()
    engines = ["pandoc", "weasyprint", "pdftotext"]
    if args.artifacts or args.require_office:
        engines += ["pdftoppm", "pdfinfo"]
    missing = [engine for engine in engines if not shutil.which(engine)]
    if missing:
        parser.exit(2, "BLOCKED: missing engines: " + ", ".join(missing) + "\n")
    with ExitStack() as stack:
        if args.artifacts:
            args.artifacts.mkdir(parents=True, exist_ok=True)
            workspace = Path(tempfile.mkdtemp(prefix="starter-", dir=args.artifacts.resolve()))
        else:
            workspace = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="render-starters-")))
        StarterAcceptance.workspace = workspace
        StarterAcceptance.assets = args.skill_dir.resolve() / "assets"
        StarterAcceptance.require_office = args.require_office
        StarterAcceptance.retain = bool(args.artifacts)
        print(f"Artifacts: {workspace}", flush=True)
        print("DOCX visual inspection remains a human gate; "
              + ("Office preview required." if args.require_office else "Office preview not required."), flush=True)
        versions = {"pandoc": "--version", "weasyprint": "--version", "pdftotext": "-v",
                    "pdftoppm": "-v", "pdfinfo": "-v"}
        with (workspace / "engines.log").open("a", encoding="utf-8") as log:
            for engine in engines:
                result = subprocess.run([engine, versions[engine]], capture_output=True,
                                        text=True, encoding="utf-8", timeout=30, check=False)
                log.write(f"$ {engine} {versions[engine]}\nexit={result.returncode}\n")
                log.write(result.stdout + result.stderr + "\n")
                if result.returncode:
                    parser.exit(2, f"BLOCKED: {engine} version command failed\n")
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(StarterAcceptance)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
