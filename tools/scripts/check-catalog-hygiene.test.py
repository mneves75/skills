#!/usr/bin/env python3
"""Unit and planted-violation tests for tools/scripts/check-catalog-hygiene.py. Python 3.11+."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parent / "check-catalog-hygiene.py"
SPEC = importlib.util.spec_from_file_location("check_catalog_hygiene", SCRIPT)
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def make_fixture(root: Path) -> None:
    (root / "skills" / "alpha" / "references").mkdir(parents=True)
    (root / "docs").mkdir(parents=True)
    (root / "skills" / "alpha" / "SKILL.md").write_text(
        "---\nname: alpha\ndescription: Run alpha checks on local source files.\nlicense: Apache-2.0\n---\n\n"
        "See [guide](references/guide.md).\n",
        encoding="utf-8",
    )
    (root / "skills" / "alpha" / "references" / "guide.md").write_text(
        "# Guide\n\nNo sibling links here.\n", encoding="utf-8"
    )
    for doc in ("README.md", "HOWTO.md", "AGENTS.md", "docs/skill-ledger.md"):
        (root / doc).write_text("Contains `alpha`.\n", encoding="utf-8")
    (root / "docs" / "skill-routing.md").write_text(
        "| Situation | Route | Boundary |\n|---|---|---|\n| Run alpha | `alpha` | None |\n",
        encoding="utf-8",
    )


class CatalogHygieneTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_fixture(root)
            res = MOD.check_repo(root)
            self.assertTrue(res["ok"], res)
            self.assertEqual(res["root_skill_count"], 1)
            self.assertEqual(res["errors"], [])

    def test_missing_routing_table_row_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_fixture(root)
            # Mention alpha only in prose, not as a Route cell
            (root / "docs" / "skill-routing.md").write_text(
                "Mentioning alpha in prose without a route row.\n", encoding="utf-8"
            )
            res = MOD.check_repo(root)
            self.assertFalse(res["ok"])
            self.assertTrue(any("docs/skill-routing.md" in e for e in res["errors"]), res["errors"])

    def test_broken_relative_link_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_fixture(root)
            (root / "skills" / "alpha" / "SKILL.md").write_text(
                "---\nname: alpha\ndescription: Run alpha checks on local source files.\n---\n"
                "See [missing](references/nope.md).\n",
                encoding="utf-8",
            )
            res = MOD.check_repo(root)
            self.assertFalse(res["ok"])
            self.assertTrue(any("broken relative link" in e for e in res["errors"]), res["errors"])

    def test_reference_to_reference_link_fails_except_security_audit_bare_basename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_fixture(root)
            (root / "skills" / "alpha" / "references" / "other.md").write_text("# Other\n", encoding="utf-8")
            (root / "skills" / "alpha" / "references" / "guide.md").write_text(
                "See [other](other.md).\n", encoding="utf-8"
            )
            res = MOD.check_repo(root)
            self.assertFalse(res["ok"])
            self.assertTrue(any("reference-to-reference" in e for e in res["errors"]), res["errors"])

    def test_oversized_description_and_body_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_fixture(root)
            long_desc = "x" * 360
            long_body = "\n".join(["line"] * 505)
            (root / "skills" / "alpha" / "SKILL.md").write_text(
                f"---\nname: alpha\ndescription: {long_desc}\n---\n{long_body}\n",
                encoding="utf-8",
            )
            res = MOD.check_repo(root)
            self.assertFalse(res["ok"])
            self.assertTrue(any("description exceeds" in e for e in res["errors"]), res["errors"])
            self.assertTrue(any("must be < 500" in e for e in res["errors"]), res["errors"])

    def test_security_audit_bare_basename_exempt_but_nested_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_fixture(root)
            sdir = root / "skills" / "security-audit" / "references"
            sdir.mkdir(parents=True)
            (root / "skills" / "security-audit" / "SKILL.md").write_text(
                "---\nname: security-audit\ndescription: Run a six-phase coverage-led source security audit.\n---\n"
                "See [a](references/A.md) and [b](references/B.md).\n",
                encoding="utf-8",
            )
            (sdir / "A.md").write_text("# A\nSee [B](B.md).\n", encoding="utf-8")
            (sdir / "B.md").write_text("# B\n", encoding="utf-8")
            for doc in ("README.md", "HOWTO.md", "AGENTS.md", "docs/skill-ledger.md"):
                p = root / doc
                p.write_text(p.read_text(encoding="utf-8") + "Contains `security-audit`.\n", encoding="utf-8")
            rp = root / "docs" / "skill-routing.md"
            rp.write_text(
                rp.read_text(encoding="utf-8") + "| Deep source audit | `security-audit` | Read-only |\n",
                encoding="utf-8",
            )
            res = MOD.check_repo(root)
            self.assertTrue(res["ok"], res)

            # Nested relative path should still be rejected even inside security-audit
            (sdir / "A.md").write_text("# A\nSee [B](./B.md).\n", encoding="utf-8")
            res2 = MOD.check_repo(root)
            self.assertFalse(res2["ok"])
            self.assertTrue(any("reference-to-reference" in e for e in res2["errors"]), res2["errors"])

    def test_unlinked_reference_and_ref_style_link_and_missing_skills_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Missing skills/ returns full schema cleanly without KeyError
            missing = MOD.check_repo(root)
            self.assertFalse(missing["ok"])
            self.assertEqual(missing["root_skill_count"], 0)
            self.assertEqual(missing["total_description_chars"], 0)
            self.assertEqual(missing["total_skill_lines"], 0)

            make_fixture(root)
            # Unlinked file under references/ fails — even with inline code links, escaped backticks, or escaped \[unused]
            (root / "skills" / "alpha" / "references" / "orphan.md").write_text("# Orphan\n", encoding="utf-8")
            (root / "skills" / "alpha" / "SKILL.md").write_text(
                "---\nname: alpha\ndescription: Run alpha checks on local source files.\n---\n"
                "See [guide](references/guide.md), an escaped \\` backtick, literal `[unused]` code, "
                "literal `[orphan](references/orphan.md)` code, and escaped \\[unused] text.\n\n"
                "[unused]: references/orphan.md\n",
                encoding="utf-8",
            )
            res_orphan = MOD.check_repo(root)
            self.assertFalse(res_orphan["ok"])
            self.assertTrue(any("unlinked reference file" in e for e in res_orphan["errors"]), res_orphan["errors"])

            # Reference label inside HTML comment, indented code block, or inline link title (incl. escaped quotes) must NOT count
            for bogus in (
                "See [guide](references/guide.md).\n<!-- [orphan] -->\n\n[orphan]: references/orphan.md\n",
                'See [guide](references/guide.md "[orphan]").\n\n[orphan]: references/orphan.md\n',
                'See [guide](references/guide.md "say \\"[orphan]\\"").\n\n[orphan]: references/orphan.md\n',
                'See [Self [label]](references/guide.md "say [orphan]").\n\n[orphan]: references/orphan.md\n',
                "See [guide](references/guide.md).\n\n    [orphan]\n\n[orphan]: references/orphan.md\n",
                "# Heading\n    [orphan]\n\n[orphan]: references/orphan.md\n",
            ):
                (root / "skills" / "alpha" / "SKILL.md").write_text(
                    "---\nname: alpha\ndescription: Run alpha checks on local source files.\n---\n" + bogus,
                    encoding="utf-8",
                )
                res_bogus = MOD.check_repo(root)
                self.assertFalse(res_bogus["ok"], bogus)
                self.assertTrue(any("unlinked reference file" in e for e in res_bogus["errors"]), res_bogus["errors"])

            # Fence marker inside an HTML comment, and `<!--` inside inline or indented code, must NOT hide real links
            for valid_md in (
                "<!--\n~~~\n-->\nSee [guide](references/guide.md).\n",
                "Use `<!--` then [guide](references/guide.md).\n",
                "    <!--\n\nSee [guide](references/guide.md).\n",
            ):
                self.assertIn("references/guide.md", MOD.extract_relative_links(valid_md, cited_only=True), valid_md)

            # Parenthesized destination resolves intact without truncating at the inner ')'
            (root / "skills" / "alpha" / "references" / "note(1).md").write_text("# Note\n", encoding="utf-8")
            self.assertIn(
                "references/note(1).md",
                MOD.extract_relative_links("See [note](references/note(1).md).\n", cited_only=True),
            )
            (root / "skills" / "alpha" / "references" / "note(1).md").unlink()

            # Reference-style sibling link inside references/ fails
            (root / "skills" / "alpha" / "SKILL.md").write_text(
                "---\nname: alpha\ndescription: Run alpha checks on local source files.\n---\n"
                "See [guide][g] and [orphan][o].\n\n[g]: references/guide.md\n[o]: references/orphan.md\n",
                encoding="utf-8",
            )
            (root / "skills" / "alpha" / "references" / "guide.md").write_text(
                "See [orphan][o].\n\n[o]: orphan.md\n", encoding="utf-8"
            )
            res_ref = MOD.check_repo(root)
            self.assertFalse(res_ref["ok"])
            self.assertTrue(any("reference-to-reference" in e for e in res_ref["errors"]), res_ref["errors"])

    def test_fenced_code_links_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_fixture(root)
            (root / "skills" / "alpha" / "SKILL.md").write_text(
                "---\nname: alpha\ndescription: Run alpha checks on local source files.\n---\n"
                "See [guide](references/guide.md).\n"
                "```markdown\n[fake](does/not/exist.md)\n```\n",
                encoding="utf-8",
            )
            res = MOD.check_repo(root)
            self.assertTrue(res["ok"], res)


if __name__ == "__main__":
    unittest.main()
