#!/usr/bin/env python3
"""Acceptance tests for the Pandoc JSON filter; Python 3.10+, stdlib only.

Run directly with an installed Pandoc. Tests use the filter's stdin/stdout and
real engine conversions, never importing its implementation or executing HTML.
"""

import base64
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile


SKILL = Path(__file__).resolve().parents[1]
FILTER = SKILL / "scripts" / "check_ast.py"
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aP1sAAAAASUVORK5CYII="
)


class Elements(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []

    def handle_starttag(self, tag, attributes):
        self.tags.append((tag, dict(attributes)))


class CheckAstAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("pandoc"):
            raise RuntimeError("BLOCKED: these acceptance tests require Pandoc")

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="render-ast-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        (self.directory / "image.png").write_bytes(PNG)

    def pandoc(self, source, output, *, filtered=True, reader="markdown-smart-raw_html-raw_tex"):
        markdown = self.directory / "source ação.md"
        markdown.write_text(source, encoding="utf-8")
        command = ["pandoc", f"--from={reader}", "--standalone", "--resource-path=.",
                   str(markdown), f"--output={output}"]
        if filtered:
            command.extend(["--filter", str(FILTER)])
        result = subprocess.run(command, cwd=self.directory, capture_output=True,
                                text=True, encoding="utf-8", timeout=30, check=False)
        self.assertEqual(markdown.read_text(encoding="utf-8"), source)
        return result

    def ast(self, source):
        result = subprocess.run(["pandoc", "--from=markdown", "--to=json"],
                                input=source, capture_output=True, text=True,
                                encoding="utf-8", timeout=30, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def filter_input(self, content):
        return subprocess.run([sys.executable, "-B", str(FILTER), "html"],
                              input=content, capture_output=True, text=True,
                              encoding="utf-8", timeout=30, check=False)

    def test_safe_content_and_structural_attributes_survive_actual_conversion(self):
        source = """---
title: Trusted fixture
lang: pt-BR
---

# Texto ação {#section .report}

[HTTPS](https://example.invalid/path?q=1#part),
[mail](mailto:reader@example.invalid), [section](#section),
[relative](chapter.md).

![Alt café](image.png){#figure .diagram width=20px height=10px}
"""
        output = self.directory / "delivery.html"
        result = self.pandoc(source, output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(output.is_file())
        rendered = output.read_text(encoding="utf-8")
        elements = Elements()
        elements.feed(rendered)
        links = {attributes["href"] for tag, attributes in elements.tags if tag == "a"}
        self.assertEqual(links, {"https://example.invalid/path?q=1#part",
                                 "mailto:reader@example.invalid", "#section", "chapter.md"})
        self.assertIn(("h1", {"id": "section", "class": "report"}), elements.tags)
        image = next(attributes for tag, attributes in elements.tags if tag == "img")
        self.assertTrue(any(attributes.get("id") == "figure"
                            for _, attributes in elements.tags))
        self.assertEqual(image["class"], "diagram")
        self.assertEqual(image["alt"], "Alt café")
        self.assertIn("20", image.get("width", image.get("style", "")))
        self.assertIn("Texto ação", rendered)
        word_output = self.directory / "delivery.docx"
        result = self.pandoc(source, word_output)
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(word_output) as archive:
            document = ET.fromstring(archive.read("word/document.xml"))
            namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
            self.assertEqual(len(list(document.iter(namespace + "drawing"))), 1)
            media = [name for name in archive.namelist() if name.startswith("word/media/")]
            self.assertEqual(len(media), 1)
            self.assertEqual(archive.read(media[0]), PNG)

    def test_active_attributes_fail_before_publication_in_both_writers(self):
        sources = [
            '[link](https://example.invalid){onclick="alert(1)"}',
            '![image](image.png){onload="alert(1)"}',
            '[span]{onclick="alert(1)"}',
            '# Heading {style="background:url(https://example.invalid/image.png)"}',
            '![image](image.png){srcset="https://example.invalid/image.png 2x"}',
            '![image](image.png){width="20px;background:url(https://example.invalid/x)"}',
            '[link](https://example.invalid){width=20px}',
        ]
        for source in sources:
            for kind in ("html", "docx"):
                with self.subTest(source=source, kind=kind):
                    output = self.directory / f"delivery.{kind}"
                    previous = b"Existing hand-edited delivery"
                    output.write_bytes(previous)
                    result = self.pandoc(source, output)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn("check_ast:", result.stderr)
                    self.assertEqual(output.read_bytes(), previous)

    def test_active_links_and_obfuscated_destinations_fail_without_json_output(self):
        destinations = [
            "javascript:alert(1)", "JaVaScRiPt:alert(1)", "vbscript:msgbox(1)",
            "data:text/html;base64,PHNjcmlwdD4=", "file:///private/document",
            "java\nscript:alert(1)", "java\tscript:alert(1)",
            "java%0ascript:alert(1)", "javascript%3Aalert(1)",
            "jav%61script:alert(1)", "https://example.invalid/\\path",
            "https://example.invalid/%5cpath", "https://example.invalid/\u200bpath",
            "//example.invalid/path",
        ]
        for destination in destinations:
            with self.subTest(destination=destination):
                document = self.ast("[link](#section)")
                document["blocks"][0]["c"][0]["c"][2][0] = destination
                result = self.filter_input(json.dumps(document))
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn("check_ast:", result.stderr)

    def test_image_destinations_are_local_before_the_writer_can_fetch(self):
        for destination in ("https://example.invalid/image.png", "//example.invalid/image.png",
                            "file:///private/image.png", "data:image/svg+xml,<svg/>"):
            with self.subTest(destination=destination):
                document = self.ast("![image](image.png)")
                image = document["blocks"][0]["c"][2][0]["c"][0]
                image["c"][2][0] = destination
                result = self.filter_input(json.dumps(document))
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn("check_ast:", result.stderr)

    def test_active_link_does_not_create_a_fresh_artifact(self):
        for kind in ("html", "docx"):
            with self.subTest(kind=kind):
                output = self.directory / f"fresh.{kind}"
                result = self.pandoc("[link](javascript:alert%281%29)", output)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("check_ast:", result.stderr)
                self.assertFalse(output.exists())

    def test_raw_nodes_and_active_metadata_fail_before_publication(self):
        sources = ["<script>alert(1)</script>", "text <b>raw inline</b>",
                   "---\ntitle: '[title](javascript:alert%281%29)'\n---\n\nBody"]
        for index, source in enumerate(sources):
            with self.subTest(source=source):
                output = self.directory / f"raw-{index}.html"
                result = self.pandoc(source, output, reader="markdown")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("check_ast:", result.stderr)
                self.assertFalse(output.exists())

    def test_missing_or_malformed_json_is_a_clear_failure(self):
        invalid = ["", "{", "null", "[]", "{}", '{"blocks":[]}',
                   '{"pandoc-api-version":[1,23],"meta":{}}',
                   '{"pandoc-api-version":[],"meta":{},"blocks":[]}',
                   '{"pandoc-api-version":[1,23],"meta":{},"blocks":[NaN]}']
        for content in invalid:
            with self.subTest(content=content):
                result = self.filter_input(content)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn("check_ast:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_nested_table_attributes_are_checked_without_rewriting_the_ast(self):
        document = self.ast("| Key | Value |\n|---|---|\n| a | b |")
        attributes = document["blocks"][0]["c"][3][1][0][0]
        attributes[0] = "header-row"
        attributes[1] = ["report-header"]
        result = self.filter_input(json.dumps(document))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), document)
        attributes[2] = [["style", "background:url(https://example.invalid/x)"]]
        result = self.filter_input(json.dumps(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("check_ast:", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
