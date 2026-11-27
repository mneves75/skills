#!/usr/bin/env python3
"""Unit and planted-violation tests for tools/scripts/check-catalog-hygiene.py. Python 3.11+."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import time
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

    def test_router_rot_guard(self) -> None:
        def build(root: Path, body: str, rows: str, extra: dict[str, str]) -> None:
            make_fixture(root)
            rdir = root / "skills" / "mneves-mode" / "references"
            rdir.mkdir(parents=True)
            links = "".join(f" [{name}](references/{name})" for name in extra)
            (rdir.parent / "SKILL.md").write_text(
                "---\nname: mneves-mode\ndescription: Explicit operator mode that orders phases and gates.\n---\n\n"
                f"{body}\n\nSee [siblings](references/optional-siblings.md).{links}\n",
                encoding="utf-8",
            )
            for name, text in extra.items():
                (rdir / name).write_text(text, encoding="utf-8")
            (rdir / "optional-siblings.md").write_text(
                "| Skill | Public source | Used for | Fallback |\n|---|---|---|---|\n" + rows, encoding="utf-8"
            )
            for doc in ("README.md", "HOWTO.md", "AGENTS.md", "docs/skill-ledger.md"):
                (root / doc).write_text("Contains `alpha` and `mneves-mode`.\n", encoding="utf-8")
            with (root / "docs" / "skill-routing.md").open("a", encoding="utf-8") as f:
                f.write("| Run the mode | `mneves-mode` | None |\n")

        good_row = "| `beta-ext` | `someone/skills` | Testing | Do it by hand |\n"
        url_row = "| `gamma-ext` | https://example.com/skills | Testing | Do it by hand |\n"
        ghost = "unknown skill token `zz-ghost`"
        pstack = "collections/pstack/skills"
        cases = {
            "valid": ("Use `alpha`, ` alpha `, `/alpha`, `$beta-ext`, `alpha/SKILL.md`, `gamma-ext.`, `pstack`, "
                      "`BLOCKED`, `--mode x` and `git branch -d`.", good_row + url_row, {}, None, {}),
            "unknown token": ("Use `alpha` and `delegate-wave`.", good_row, {}, "unknown skill token `delegate-wave`", {}),
            "padded span": ("Use ` zz-ghost `.", good_row, {}, ghost, {}),
            "slash form": ("Type `/zz-ghost`.", good_row, {}, ghost, {}),
            "dollar form": ("Use `$zz-ghost`.", good_row, {}, ghost, {}),
            "skill path": ("Open `zz-ghost/SKILL.md`.", good_row, {}, ghost, {}),
            "trailing period": ("Use `zz-ghost.`", good_row, {}, ghost, {}),
            "skill path with period": ("Open `zz-ghost/SKILL.md.`", good_row, {}, ghost, {}),
            "escaped backtick": ("Use \\` as a delimiter, then `/zz-ghost`.", good_row, {}, ghost, {}),
            "literal backslash in span": ("Paths like `dir\\` `alpha` and ``a ` b`` stay literal.", good_row, {}, None, {}),
            "double-backtick span": ("Run ``zz-ghost`` first.", good_row, {}, ghost, {}),
            "leading-dot repo": ("Use `beta-ext`.", "| `beta-ext` | `someone/.skills` | Testing | By hand |\n", {},
                                 None, {}),
            "dot-only repo": ("Use `beta-ext`.", "| `beta-ext` | `someone/...` | Testing | By hand |\n", {},
                              "needs a public source", {}),
            "span after escaped backtick": ("Use the legacy prefix \\``/zz-ghost` here.", good_row, {}, ghost, {}),
            "relative source": ("Use `beta-ext`.", "| `beta-ext` | `../private-skills` | Testing | By hand |\n", {},
                                "needs a public source", {}),
            "row without fallback": ("Use `beta-ext`.", "| `beta-ext` | `someone/skills` | Testing |  |\n", {},
                                     "needs a public source", {}),
            "placeholder source": ("Use `beta-ext`.", "| `beta-ext` | TBD | Testing | Do it by hand |\n", {},
                                   "needs a public source", {}),
            "pstack skill": ("Use `gamma`.", good_row, {}, None, {f"{pstack}/gamma/SKILL.md": "# gamma\n"}),
            "pstack dir without SKILL.md": ("Use `zz-ghost`.", good_row, {}, ghost,
                                            {f"{pstack}/zz-ghost/assets/x.txt": "x\n"}),
            "openai.yaml ghost": ("Use `alpha`.", good_row, {}, "unknown skill token `$zz-ghost`",
                                  {"skills/mneves-mode/agents/openai.yaml": 'default_prompt: "Use $zz-ghost."\n'}),
            "span across a line break": ("Run `zz-\nghost` and `zz-ghost\n` now.", good_row, {}, ghost, {}),
            "slash command with arguments": ("Type `/zz-ghost now`.", good_row, {}, ghost, {}),
            "dollar command with arguments": ("Type `$zz-ghost review this`.", good_row, {}, ghost, {}),
            "repo skill path": ("Open `skills/zz-ghost/SKILL.md`.", good_row, {}, ghost, {}),
            "trailing slash": ("Open `zz-ghost/`.", good_row, {}, ghost, {}),
            "reference path": ("Open `zz-ghost/references/x.md`.", good_row, {}, ghost, {}),
            "plugin prefix": ("Use `plugin:zz-ghost`.", good_row, {}, ghost, {}),
            "quoted or parenthesized": ("Use `\"zz-ghost\"` or `(zz-ghost)`.", good_row, {}, ghost, {}),
            "commands stay allowed": ("Run `git branch -d x`, `python3 tools/x.py`, `/alpha now` and "
                                      "`skills/alpha/SKILL.md`.", good_row, {}, None, {}),
            "ghost in a reference .txt": ("Use `alpha`. See [x](references/x.txt).", good_row,
                                          {"x.txt": "Use `zz-ghost`.\n"}, ghost, {}),
            "dash fallback": ("Use `beta-ext`.", "| `beta-ext` | `someone/skills` | Testing | - |\n", {},
                              "needs a public source", {}),
            "oversize asset": ("Use `alpha`.", good_row, {}, "SKILL.md plus references over",
                               {"skills/mneves-mode/assets/big.txt": "word " * 6200}),
            "oversize body": ("line\n" * 161, good_row, {}, "router SKILL.md over", {}),
            "oversize playbook": ("Use `alpha`.", good_row, {"playbook-big.md": "word " * 520}, "playbook over", {}),
            "oversize total": ("Use `alpha`.", good_row, {"notes.md": "word " * 6200}, "SKILL.md plus references over", {}),
            # A linked file would be read and sized from outside the skill.
            "symlinked reference": ("Use `alpha`.", good_row, {}, "symlink in the router skill",
                                    {"skills/mneves-mode/references/linked.md": Path("../../../README.md")}),
            # A linked siblings file or openai.yaml must not be read: its rows or tokens stay unknown.
            "symlinked siblings file": ("Use `beta-ext`.", good_row, {}, "unknown skill token `beta-ext`",
                                        {"outside.md": "| Skill | Source | Use | Fallback |\n|---|---|---|---|\n" + good_row,
                                         "skills/mneves-mode/references/optional-siblings.md": Path("../../../outside.md")}),
            "symlinked openai.yaml": ("Use `alpha`.", good_row, {}, "not:unknown skill token `$zz-ghost`",
                                      {"outside.yaml": 'default_prompt: "Use $zz-ghost."\n',
                                       "skills/mneves-mode/agents/openai.yaml": Path("../../../outside.yaml")}),
        }
        for label, (body, rows, extra, expected, tree) in cases.items():
            with self.subTest(label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                build(root, body, rows, extra)
                for rel, text in tree.items():
                    (root / rel).parent.mkdir(parents=True, exist_ok=True)
                    (root / rel).unlink(missing_ok=True)
                    if isinstance(text, Path):
                        (root / rel).symlink_to(text)
                    else:
                        (root / rel).write_text(text, encoding="utf-8")
                res = MOD.check_repo(root)
                if expected is None:
                    self.assertTrue(res["ok"], res["errors"])
                elif expected.startswith("not:"):
                    self.assertFalse(res["ok"])
                    self.assertFalse(any(expected[4:] in e for e in res["errors"]), res["errors"])
                else:
                    self.assertFalse(res["ok"])
                    self.assertTrue(any(expected in e for e in res["errors"]), res["errors"])

    def test_router_span_scan_is_linear(self) -> None:
        # Escaped, never-closed openers made the old lazy regex rescan to the paragraph end for
        # each one: about 36 s on this input.
        text = "\\``a" * 10000 + "\n\n`zz-ghost`"
        start = time.perf_counter()
        spans = MOD._router_spans(text)
        self.assertLess(time.perf_counter() - start, 2.0)
        self.assertEqual(spans, ["zz-ghost"])


if __name__ == "__main__":
    unittest.main()
