#!/usr/bin/env python3
"""Unit and integration tests for the autoreview CLI; Python 3.11+, standard library only."""
from __future__ import annotations

import argparse
import contextlib
import copy
import importlib.util
import io
import itertools
import json
import os
import re
import runpy
import stat
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock


SCRIPT_PATH = Path(__file__).with_name("autoreview")
LOADER = SourceFileLoader("autoreview_module", str(SCRIPT_PATH))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
assert SPEC is not None
AUTOREVIEW = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(AUTOREVIEW)


FINAL_REPORT = {
    "findings": [],
    "overall_correctness": "patch is correct",
    "overall_explanation": "clean",
    "overall_confidence": 0.9,
}

DRAFT_REPORT = {
    "findings": [
        {
            "title": "Draft finding",
            "body": "draft",
            "priority": "P3",
            "confidence": 0.2,
            "category": "maintainability",
            "code_location": {"file_path": "draft.js", "line": 1},
        }
    ],
    "overall_correctness": "patch is incorrect",
    "overall_explanation": "draft",
    "overall_confidence": 0.2,
}


class AutoreviewCursorTests(unittest.TestCase):
    def test_parser_resource_errors_are_invalid_reports(self) -> None:
        args = argparse.Namespace(engine="codex", max_priority="P2")
        for raw in ("[" * 2000 + "]" * 2000, '{"findings":[],"number":' + "9" * 10000 + "}"):
            with self.subTest(length=len(raw)), mock.patch.object(
                AUTOREVIEW, "run_engine", return_value=raw,
            ), mock.patch.object(AUTOREVIEW, "scan_outgoing_review_pack"):
                with self.assertRaises(AUTOREVIEW.ReviewerUnavailable) as caught:
                    AUTOREVIEW.run_reviewer(args, Path.cwd(), "synthetic", set(), [])
                self.assertEqual(caught.exception.reason, "invalid_report")

    def test_container_valued_report_enums_are_invalid_reports(self) -> None:
        args = argparse.Namespace(engine="codex", max_priority="P2")
        finding = copy.deepcopy(DRAFT_REPORT["findings"][0])
        finding["source_attribution"] = {
            "target": "index", "record_id": "record", "source_id": "source",
            "side": "present", "column": 1, "excerpt": "text",
        }
        for field in ("overall_correctness", "priority", "category", "target", "side"):
            for value in ([], {}, None, 42, False):
                report = copy.deepcopy(FINAL_REPORT)
                report["findings"] = [copy.deepcopy(finding)]
                owner = report if field == "overall_correctness" else report["findings"][0]
                if field in {"target", "side"}:
                    owner = owner["source_attribution"]
                owner[field] = value
                with self.subTest(field=field, value=value), mock.patch.object(
                    AUTOREVIEW, "run_engine", return_value=json.dumps({**report, "review_completion": "complete"}),
                ), mock.patch.object(AUTOREVIEW, "scan_outgoing_review_pack"):
                    with self.assertRaises(AUTOREVIEW.ReviewerUnavailable) as caught:
                        AUTOREVIEW.run_reviewer(args, Path.cwd(), "synthetic", {"draft.js"}, [])
                    self.assertEqual(caught.exception.reason, "invalid_report")

    def test_private_completion_is_required_validated_and_stripped(self) -> None:
        args = argparse.Namespace(engine="codex", max_priority="P2")
        for completion in ("complete", "incomplete"):
            provider = {**FINAL_REPORT, "review_completion": completion}
            with self.subTest(completion=completion), mock.patch.object(
                AUTOREVIEW, "run_engine", return_value=json.dumps(provider),
            ), mock.patch.object(AUTOREVIEW, "scan_outgoing_review_pack"):
                result = AUTOREVIEW.run_reviewer(args, Path.cwd(), "synthetic", set(), [])
            self.assertEqual(result.complete, completion == "complete")
            self.assertEqual(result.report["provider_report"], FINAL_REPORT)
            self.assertNotIn("review_completion", result.report)
            self.assertEqual(
                AUTOREVIEW.review_status(result.report, complete=result.complete),
                "scoped-clean" if result.complete else "incomplete",
            )
        for provider in (
            FINAL_REPORT,
            *({**FINAL_REPORT, "review_completion": value}
              for value in ("", "deferred", [], {}, None, 42, False)),
        ):
            with self.subTest(provider=provider), mock.patch.object(
                AUTOREVIEW, "run_engine", return_value=json.dumps(provider),
            ), mock.patch.object(AUTOREVIEW, "scan_outgoing_review_pack"):
                with self.assertRaises(AUTOREVIEW.ReviewerUnavailable) as caught:
                    AUTOREVIEW.run_reviewer(args, Path.cwd(), "synthetic", set(), [])
            self.assertEqual(caught.exception.reason, "invalid_report")
            self.assertIn("missing or invalid review_completion", str(caught.exception))

    def test_provider_schema_keeps_completion_out_of_public_schema(self) -> None:
        self.assertEqual(
            AUTOREVIEW.PROVIDER_SCHEMA["required"],
            [*AUTOREVIEW.SCHEMA["required"], "review_completion"],
        )
        self.assertEqual(
            AUTOREVIEW.PROVIDER_SCHEMA["properties"]["review_completion"],
            {"type": "string", "enum": ["complete", "incomplete"]},
        )
        self.assertFalse(AUTOREVIEW.PROVIDER_SCHEMA["additionalProperties"])
        self.assertNotIn("review_completion", AUTOREVIEW.SCHEMA["properties"])
        prompt = AUTOREVIEW.render_review_prompt(
            "task", "local", None, AUTOREVIEW.ReviewChunk("change"), "", "", (1, 2),
        )
        self.assertIn(json.dumps(AUTOREVIEW.PROVIDER_SCHEMA), prompt)
        self.assertIn("independent, complete assignment", prompt)
        self.assertIn("no shared conversation or future evidence batch", prompt)
        self.assertIn("Make the report understandable on its own", prompt)
        self.assertIn("identify the affected behavior and the conditions under which it fails", prompt)

    def test_extract_json_prefers_terminal_result_event(self) -> None:
        stream = "\n".join(
            [
                json.dumps(
                    {
                        "type": "assistant",
                        "message": {"role": "assistant", "content": [{"type": "text", "text": json.dumps(DRAFT_REPORT)}]},
                    }
                ),
                json.dumps(
                    {
                        "type": "result",
                        "subtype": "success",
                        "result": json.dumps(FINAL_REPORT),
                        "session_id": "session-id",
                        "request_id": "request-id",
                    }
                ),
            ]
        )
        self.assertEqual(AUTOREVIEW.extract_json(stream), FINAL_REPORT)

    def test_extract_json_can_fallback_to_assistant_message(self) -> None:
        stream = json.dumps(
            {
                "type": "assistant",
                "message": {"role": "assistant", "content": [{"type": "text", "text": json.dumps(FINAL_REPORT)}]},
            }
        )
        self.assertEqual(AUTOREVIEW.extract_json(stream), FINAL_REPORT)

    def test_extract_json_does_not_fallback_past_bad_terminal_result(self) -> None:
        stream = "\n".join(
            [
                json.dumps(
                    {
                        "type": "assistant",
                        "message": {"role": "assistant", "content": [{"type": "text", "text": json.dumps(FINAL_REPORT)}]},
                    }
                ),
                json.dumps(
                    {
                        "type": "result",
                        "subtype": "success",
                        "result": "not json",
                    }
                ),
            ]
        )
        with self.assertRaises(SystemExit) as exc_info:
            AUTOREVIEW.extract_json(stream)
        self.assertIn("review engine result was not structured JSON", str(exc_info.exception))


class AutoreviewPriorityTests(unittest.TestCase):
    def test_default_priority_is_p0(self) -> None:
        with mock.patch.object(sys, "argv", ["autoreview"]):
            args = AUTOREVIEW.parse_args()
        self.assertEqual(args.max_priority, "P0")

    def test_priority_filter_preserves_lower_findings_and_provider_verdict(self) -> None:
        report = copy.deepcopy(DRAFT_REPORT)
        AUTOREVIEW.filter_findings_by_priority(report, "P0")
        self.assertEqual(report["findings"], [])
        self.assertEqual(report["priority_filtered_findings"], DRAFT_REPORT["findings"])
        for key in ("overall_correctness", "overall_explanation", "overall_confidence"):
            self.assertEqual(report[key], DRAFT_REPORT[key])

    def test_unfinished_assessment_keeps_filtered_observations_incomplete(self) -> None:
        args = argparse.Namespace(engine="codex", max_priority="P0")
        with mock.patch.object(
            AUTOREVIEW, "run_engine",
            return_value=json.dumps({**DRAFT_REPORT, "review_completion": "incomplete"}),
        ), mock.patch.object(AUTOREVIEW, "scan_outgoing_review_pack"):
            result = AUTOREVIEW.run_reviewer(args, Path.cwd(), "synthetic", {"draft.js"}, [])
        self.assertFalse(result.complete)
        self.assertEqual(result.report["provider_report"], DRAFT_REPORT)
        self.assertEqual(result.report["findings"], [])
        self.assertEqual(result.report["priority_filtered_findings"], DRAFT_REPORT["findings"])
        self.assertEqual(AUTOREVIEW.review_status(result.report, complete=result.complete), "incomplete")


class AutoreviewResultScopeTests(unittest.TestCase):
    def test_scope_rejection_preserves_provider_conclusion_and_audit(self) -> None:
        report = copy.deepcopy(DRAFT_REPORT)
        with contextlib.redirect_stderr(io.StringIO()):
            AUTOREVIEW.validate_report(report, Path.cwd(), {"changed.js"}, [])
        self.assertEqual(report["findings"], [])
        for key in ("overall_correctness", "overall_explanation", "overall_confidence"):
            self.assertEqual(report[key], DRAFT_REPORT[key])
        self.assertEqual(report["scope_rejected_findings"], DRAFT_REPORT["findings"])
        report["review_status"] = AUTOREVIEW.review_status(report, complete=True)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            AUTOREVIEW.print_report(report)
        self.assertIn("incomplete", output.getvalue())
        self.assertIn("Draft finding", output.getvalue())
        self.assertIn("draft.js:1", output.getvalue())
        self.assertNotIn("clean:", output.getvalue())

    def test_chunk_merge_keeps_rejections_explanations_and_conservative_confidence(self) -> None:
        rejected = copy.deepcopy(DRAFT_REPORT)
        with contextlib.redirect_stderr(io.StringIO()):
            AUTOREVIEW.validate_report(rejected, Path.cwd(), {"changed.js"}, [])
        reports = [("chunk 1/2", copy.deepcopy(FINAL_REPORT)), ("chunk 2/2", rejected)]
        merged = AUTOREVIEW.merge_chunk_reports(reports)
        self.assertEqual(merged["overall_correctness"], "patch is incorrect")
        self.assertEqual(merged["overall_confidence"], 0.2)
        self.assertEqual(len(merged["scope_rejected_findings"]), 1)
        self.assertEqual(merged["pass_reports"][1]["report"], rejected)
        merged["review_status"] = AUTOREVIEW.review_status(merged, complete=True)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            AUTOREVIEW.print_report(merged)
        self.assertIn("draft", output.getvalue())
        self.assertIn("incomplete", output.getvalue())
        self.assertNotIn("clean:", output.getvalue())

    def test_required_finding_must_survive_priority_filter_for_every_pass_count(self) -> None:
        args = argparse.Namespace(engine="codex", max_priority="P0", require_finding=["Draft finding"])
        for count in (1, 2):
            with self.subTest(count=count), mock.patch.object(
                AUTOREVIEW, "scan_outgoing_review_pack"
            ), mock.patch.object(AUTOREVIEW, "run_engine", return_value=json.dumps({**DRAFT_REPORT, "review_completion": "complete"})):
                results = AUTOREVIEW.run_review_passes(
                    args, [args], Path.cwd(), ["pack"] * count, {"draft.js"}
                )
            self.assertTrue(all(result.complete for _, result in results))
            reports = [(label, result.report) for label, result in results]
            report = reports[0][1] if count == 1 else AUTOREVIEW.merge_chunk_reports(reports)
            self.assertEqual(
                AUTOREVIEW.missing_required_findings(report, args.require_finding), ["Draft finding"]
            )
            self.assertEqual(report["overall_correctness"], "patch is incorrect")
            self.assertTrue(report["priority_filtered_findings"])

    def test_provider_cannot_supply_local_audit_metadata(self) -> None:
        for key in ("scope_rejected_findings", "priority_filtered_findings", "pass_reports", "review_status", "review_completion"):
            report = copy.deepcopy(FINAL_REPORT)
            report[key] = []
            with self.subTest(key=key), self.assertRaisesRegex(SystemExit, "unexpected top-level"):
                AUTOREVIEW.validate_report(report, Path.cwd(), set(), [])

    def test_required_finding_survives_merge_deduplication_and_body_prefix(self) -> None:
        first = copy.deepcopy(DRAFT_REPORT)
        second = copy.deepcopy(DRAFT_REPORT)
        second["findings"][0]["body"] = "x" * 1980 + " required tail"
        merged = AUTOREVIEW.merge_chunk_reports([("chunk 1/2", first), ("chunk 2/2", second)])
        self.assertEqual(len(merged["findings"]), 1)
        self.assertEqual(AUTOREVIEW.missing_required_findings(merged, ["required tail"]), [])


class AutoreviewTargetResultTests(unittest.TestCase):
    def setUp(self):
        source = AUTOREVIEW.SourceVersion
        self.record = AUTOREVIEW.MixedPath(
            "src/migrate.py", "synthetic-record",
            source("base-source", "100644", "original()\nkeep()\n"),
            source("index-source", "100644", "obsolete()\nkeep()\n"),
            source("working-source", "100644", "corrected()\nkeep()\nbroken()\n"),
            "synthetic staged delta", "synthetic unstaged delta",
            ((1, "original()"),), ((1, "obsolete()"),), (),
        )

    def finding(self, target="index", side="present", line=1, excerpt=None, **changes):
        source = ((self.record.base if target == "index" else self.record.index)
                  if side == "removed" else getattr(self.record, target))
        if excerpt is None:
            excerpt = source.content.splitlines()[line - 1]
        finding = {
            "title": "Synthetic defect", "body": "A concrete synthetic claim.",
            "priority": "P0", "confidence": 0.8, "category": "bug",
            "code_location": {"file_path": self.record.path, "line": line},
            "source_attribution": {"target": target, "record_id": self.record.identity,
                                   "source_id": source.identity, "side": side,
                                   "column": 1, "excerpt": excerpt},
        }
        finding.update(changes)
        return finding

    def validate(self, findings, available=True):
        report = copy.deepcopy(FINAL_REPORT)
        report["findings"] = copy.deepcopy(findings)
        AUTOREVIEW.validate_report(report, Path.cwd(), {self.record.path}, [], (self.record,),
                                   {self.record.identity} if available else set())
        return report

    def test_explicit_targets_anchors_and_pass_availability(self):
        accepted = [self.finding(), self.finding("working_tree", line=3),
                    self.finding("working_tree", line=2), self.finding(side="removed"),
                    self.finding("working_tree", side="removed")]
        self.assertEqual(self.validate(accepted)["findings"], accepted)
        cases = []
        missing = self.finding()
        missing.pop("source_attribution")
        cases.append((missing, "requires explicit"))
        null = self.finding(source_attribution=None)
        cases.append((null, "requires explicit"))
        for field, value, reason in (
            ("record_id", "wrong", "record identity"),
            ("source_id", "wrong", "source identity"),
            ("column", 1000, "excerpt"),
            ("excerpt", "invented()", "excerpt"),
        ):
            finding = self.finding()
            finding["source_attribution"][field] = value
            cases.append((finding, reason))
        cases.extend([
            (self.finding("working_tree", excerpt="obsolete()"), "excerpt"),
            (self.finding("working_tree", line=900, excerpt="broken()"), "out of range"),
            (self.finding("working_tree", side="removed", line=2), "genuinely removed"),
        ])
        for finding, reason in cases:
            with self.subTest(reason=reason, finding=finding):
                report = self.validate([finding])
                self.assertEqual(report["findings"], [])
                self.assertIn(reason, report["attribution_rejected_findings"][0]["attribution_rejection_reason"])
                self.assertEqual(AUTOREVIEW.review_status(report, complete=True), "incomplete")
                self.assertEqual(report["overall_correctness"], "patch is correct")
        report = self.validate([self.finding()], available=False)
        self.assertIn("not available", report["attribution_rejected_findings"][0]["attribution_rejection_reason"])
        original = self.record
        for path in (" src/migrate.py", "src/migrate.py ", " "):
            with self.subTest(path=path):
                self.record = original._replace(path=path)
                finding = self.finding()
                self.assertEqual(self.validate([finding])["findings"], [finding])
            self.record = original

    def test_absence_readd_and_removed_side_are_distinct(self):
        absent = AUTOREVIEW.SourceVersion("absent", None, None)
        for target in ("index", "working_tree"):
            with self.subTest(target=target):
                original = self.record
                if target == "index":
                    self.record = original._replace(index=absent, working_tree_removed=())
                else:
                    self.record = original._replace(working_tree=absent)
                present = self.finding(target, excerpt="obsolete()")
                removed = self.finding(target, side="removed")
                report = self.validate([present, removed])
                self.assertEqual(report["findings"], [removed])
                self.assertIn("absent", report["attribution_rejected_findings"][0]["attribution_rejection_reason"])
                self.record = original

        original = self.record
        for target, side, content, line in (
            ("index", "present", "", 1), ("working_tree", "present", "", 1),
            ("index", "present", "before()\n\n", 2), ("working_tree", "present", "before()\n\n", 2),
            ("index", "removed", "\n", 1), ("working_tree", "removed", "\n", 1),
        ):
            with self.subTest(target=target, side=side, content=content):
                owner = ("base" if target == "index" else "index") if side == "removed" else target
                self.record = original._replace(**{owner: getattr(original, owner)._replace(content=content)})
                if side == "removed":
                    self.record = self.record._replace(**{target + "_removed": ((line, ""),)})
                valid = self.finding(target, side=side, line=line, excerpt="")
                self.assertEqual(self.validate([valid])["findings"], [valid])
                invalid = []
                for key, value in (("record_id", "wrong"), ("source_id", "wrong"),
                                   ("column", 2), ("excerpt", "invented")):
                    bad = copy.deepcopy(valid)
                    bad["source_attribution"][key] = value
                    invalid.append(bad)
                bad = copy.deepcopy(valid)
                bad["code_location"]["line"] = 2 if not content else 900
                invalid.append(bad)
                if side == "present" and content:
                    bad = copy.deepcopy(valid)
                    bad["code_location"]["line"] = 1
                    invalid.append(bad)
                for bad in invalid:
                    report = self.validate([bad])
                    self.assertEqual(report["findings"], [])
                    self.assertEqual(AUTOREVIEW.review_status(report, complete=True), "incomplete")
                self.record = original
        for target in ("index", "working_tree"):
            for side in ("present", "removed"):
                report = self.validate([self.finding(target, side=side, excerpt="")])
                self.assertEqual(report["findings"], [])
            self.record = original._replace(**{target: absent})
            report = self.validate([self.finding(target, excerpt="")])
            self.assertIn("absent", report["attribution_rejected_findings"][0]["attribution_rejection_reason"])
            self.record = original

    def test_title_independent_groups_keep_variants_targets_and_observations(self):
        reports = []
        for index in range(8):
            finding = self.finding(title=f"Index title {index}")
            findings = [finding]
            if index == 7:
                findings += [self.finding(body="Distinct consequence requiring a different fix."),
                             self.finding("working_tree")]
            reports.append((f"pass {index}", self.validate(findings)))
        for selected in (reports, [("single", self.validate([
            finding for _, report in reports for finding in report["findings"]
        ]))]):
            with self.subTest(passes=len(selected)):
                result = AUTOREVIEW.merge_chunk_reports(selected)
                self.assertEqual(len(result["findings"]), 2)
                grouped = result["findings"][0]
                self.assertEqual(len(grouped["claim_variants"]), 2)
                self.assertEqual(len(grouped["claim_variants"][0]["observations"]), 8)
                self.assertEqual(AUTOREVIEW.missing_required_findings(result, ["Index title 7", "different fix"]), [])
                self.assertEqual(len(result["pass_reports"]), len(selected))
                result["review_status"] = AUTOREVIEW.review_status(result, complete=True)
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    AUTOREVIEW.print_report(result)
                for text in ("INDEX-only", "WORKING_TREE", "Index title 7", "different fix"):
                    self.assertIn(text, output.getvalue())

    def test_all_engines_keep_raw_reports_before_normalization_and_filters(self):
        captured = AUTOREVIEW.CapturedBundle("delta", {self.record.path}, (self.record,), ())
        prompt = AUTOREVIEW.ReviewPass("synthetic pack", AUTOREVIEW.ReviewChunk("delta", sources=(self.record,)))
        valid = self.finding()
        valid["code_location"]["file_path"] = r".\src\migrate.py"
        stale = self.finding("working_tree", excerpt="obsolete()")
        outside = self.finding(code_location={"file_path": "outside.py", "line": 1})
        provider = {**FINAL_REPORT, "findings": [valid, stale, outside],
                    "overall_correctness": "patch is incorrect", "overall_confidence": 0.43}
        for engine in AUTOREVIEW.ENGINES:
            with self.subTest(engine=engine), mock.patch.object(
                    AUTOREVIEW, "run_engine", return_value=json.dumps({**provider, "review_completion": "complete"})), \
                    mock.patch.object(AUTOREVIEW, "scan_outgoing_review_pack"), \
                    mock.patch.object(AUTOREVIEW, "verify_mixed_sources"), contextlib.redirect_stderr(io.StringIO()):
                result = AUTOREVIEW.run_reviewer(argparse.Namespace(engine=engine, max_priority="P0"),
                                                 Path.cwd(), prompt, captured, [])
            self.assertTrue(result.complete)
            report = result.report
            self.assertEqual(report["provider_report"], provider)
            self.assertEqual(report["overall_confidence"], 0.43)
            self.assertEqual(len(report["findings"]), 1)
            self.assertEqual(len(report["scope_rejected_findings"]), 1)
            self.assertEqual(len(report["attribution_rejected_findings"]), 1)
            self.assertEqual(AUTOREVIEW.review_status(report, complete=result.complete), "incomplete")
            self.assertEqual(report["available_source_records"], [self.record.identity])
        low = self.validate([self.finding(priority="P2")])
        AUTOREVIEW.filter_findings_by_priority(low, "P0")
        self.assertEqual(AUTOREVIEW.missing_required_findings(low, ["Synthetic defect"]), ["Synthetic defect"])
        self.assertEqual(AUTOREVIEW.review_status(low, complete=True), "filtered")
        for bad in ({}, {**self.finding()["source_attribution"], "column": True}):
            with self.assertRaisesRegex(SystemExit, "source_attribution"):
                self.validate([self.finding(source_attribution=bad)])

def amp_test_stream(
    cwd: Path,
    *,
    tools: list[object] | None = None,
    mcp_servers: list[object] | None = None,
    trigger: str = "Run the isolated autoreview adapter.",
    tool_name: str = "autoreview_generate",
    tool_input: object = None,
    tool_result_id: str = "amp-tool-use",
    tool_error: bool = False,
    tool_result_content: str | None = None,
) -> str:
    if tool_input is None:
        tool_input = {}
    if tool_result_content is None:
        tool_result_content = (
            "Autoreview generation failed." if tool_error else "Adapter completed."
        )
    return "\n".join(
        [
            json.dumps(
                {
                    "type": "system",
                    "subtype": "init",
                    "cwd": str(cwd),
                    "session_id": "amp-test-session",
                    "tools": ["autoreview_generate"] if tools is None else tools,
                    "mcp_servers": [] if mcp_servers is None else mcp_servers,
                    "agent_mode": "medium",
                }
            ),
            json.dumps(
                {
                    "type": "user",
                    "message": {
                        "role": "user",
                        "content": [{"type": "text", "text": trigger}],
                    },
                    "parent_tool_use_id": None,
                    "session_id": "amp-test-session",
                }
            ),
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "amp-tool-use",
                                "name": tool_name,
                                "input": tool_input,
                            }
                        ],
                    },
                    "parent_tool_use_id": None,
                    "session_id": "amp-test-session",
                }
            ),
            json.dumps(
                {
                    "type": "user",
                    "message": {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_result_id,
                                "content": tool_result_content,
                                "is_error": tool_error,
                            }
                        ],
                    },
                    "parent_tool_use_id": None,
                    "session_id": "amp-test-session",
                }
            ),
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "role": "assistant",
                        "content": [{"type": "text", "text": "Completed."}],
                    },
                    "parent_tool_use_id": None,
                    "session_id": "amp-test-session",
                }
            ),
            json.dumps(
                {
                    "type": "result",
                    "subtype": "success",
                    "is_error": False,
                    "result": "Completed.",
                    "session_id": "amp-test-session",
                }
            ),
        ]
    ) + "\n"


def amp_test_plugin_list(plugin_path: Path) -> str:
    return "\n".join(
        [
            f"✓ {plugin_path} active",
            "  tool: autoreview_generate",
            "  agent: autoreview-adapter",
            "  agent mode: autoreview",
        ]
    ) + "\n"


def amp_test_mcp_denial_result(
    command: list[str],
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    skills_root = Path(env["HOME"]) / ".config" / "agents" / "skills"
    probe_roots = list(skills_root.glob("autoreview-mcp-deny-*"))
    if len(probe_roots) != 1:
        raise AssertionError(f"expected one MCP denial probe, found {probe_roots}")
    mcp_config = json.loads((probe_roots[0] / "mcp.json").read_text(encoding="utf-8"))
    probe_name = next(iter(mcp_config))
    return subprocess.CompletedProcess(
        command,
        0,
        "12 tools available\n",
        f"error connecting to {probe_name}: MCP server is not allowed by MCP permissions\n",
    )


class AutoreviewAmpTests(unittest.TestCase):
    def test_amp_bin_cli_option_and_defaults(self) -> None:
        with mock.patch.object(
            sys,
            "argv",
            ["autoreview", "--engine", "amp", "--amp-bin", "/tmp/trusted-amp"],
        ):
            args = AUTOREVIEW.parse_args()
        reviewer = AUTOREVIEW.reviewer_args(args)[0]
        self.assertEqual(reviewer.amp_bin, "/tmp/trusted-amp")
        self.assertEqual(reviewer.model, "openai/gpt-6.1-sol")
        self.assertEqual(reviewer.thinking, "xhigh")
        self.assertFalse(reviewer.tools)

    @unittest.skipIf(os.name == "nt", "Amp runtime is unsupported on native Windows")
    def test_amp_isolation_probe_requires_api_key_and_flags(self) -> None:
        args = argparse.Namespace(amp_bin="amp")
        required_flags = " ".join(
            [
                "--execute",
                "--stream-json",
                "--stream-json-input",
                "--plugin-ready-timeout",
                "--settings-file",
                "--no-ide",
            ]
        )
        with tempfile.TemporaryDirectory(prefix="autoreview-amp-probe-test.") as tmpdir, mock.patch.dict(
            os.environ,
            {"AMP_API_KEY": "test-key"},
            clear=False,
        ), mock.patch.object(
            AUTOREVIEW,
            "resolve_command",
            return_value="/usr/bin/amp",
        ), mock.patch.object(
            AUTOREVIEW,
            "safe_engine_env",
            return_value={},
        ), mock.patch.object(
            AUTOREVIEW,
            "safe_temp_root",
            return_value=Path(tmpdir),
        ), mock.patch.object(
            AUTOREVIEW,
            "run",
            return_value=subprocess.CompletedProcess(["amp", "--help"], 0, required_flags, ""),
        ):
            self.assertEqual(
                AUTOREVIEW.ensure_amp_isolation_supported(args, Path(tmpdir)),
                "/usr/bin/amp",
            )

        with mock.patch.dict(os.environ, {"AMP_API_KEY": ""}, clear=False), mock.patch.object(
            AUTOREVIEW,
            "resolve_command",
            return_value="/usr/bin/amp",
        ):
            with self.assertRaisesRegex(SystemExit, "requires AMP_API_KEY"):
                AUTOREVIEW.ensure_amp_isolation_supported(args, Path("/tmp/repo"))

    def test_amp_isolation_probe_rejects_native_windows(self) -> None:
        args = argparse.Namespace(amp_bin="amp")
        repo = Path("/tmp/repo")
        context = (
            contextlib.nullcontext()
            if os.name == "nt"
            else mock.patch.object(AUTOREVIEW.os, "name", "nt")
        )
        with context:
            with self.assertRaisesRegex(SystemExit, "native Windows"):
                AUTOREVIEW.ensure_amp_isolation_supported(args, repo)

    @unittest.skipIf(os.name == "nt", "Amp runtime is unsupported on native Windows")
    def test_amp_run_keeps_review_prompt_out_of_outer_agent(self) -> None:
        args = argparse.Namespace(
            amp_bin="amp",
            max_output_chars=2_000_000,
            model="openai/gpt-6.1-sol",
            stream_engine_output=False,
            thinking="high",
        )
        secret_prompt = "review diff PRIVATE_REVIEW_MARKER_8f3c"
        observed: dict[str, object] = {}

        def fake_preflight(
            command: list[str],
            cwd: Path,
            **kwargs: object,
        ) -> subprocess.CompletedProcess[str]:
            env = kwargs["env"]
            assert isinstance(env, dict)
            runtime_root = Path(str(env["XDG_CONFIG_HOME"])).parent
            plugin_root = Path(str(env["XDG_CONFIG_HOME"])) / "amp" / "plugins"
            plugin_path = next(plugin_root.glob("autoreview-*.ts"))
            if command[-2:] == ["tools", "list"]:
                observed["mcp_preflight_prompt_exists"] = (
                    runtime_root / "review-prompt.txt"
                ).exists()
                return amp_test_mcp_denial_result(command, env)
            observed["preflight_command"] = command
            observed["preflight_prompt_exists"] = (
                runtime_root / "review-prompt.txt"
            ).exists()
            return subprocess.CompletedProcess(
                command,
                0,
                amp_test_plugin_list(plugin_path),
                "",
            )

        def fake_execute(
            command: list[str],
            cwd: Path,
            **kwargs: object,
        ) -> subprocess.CompletedProcess[str]:
            observed["command"] = command
            observed["cwd"] = cwd
            observed["input"] = kwargs["input_text"]
            observed["env"] = kwargs["env"]
            env = kwargs["env"]
            assert isinstance(env, dict)
            runtime_root = Path(str(env["XDG_CONFIG_HOME"])).parent
            prompt_path = runtime_root / "review-prompt.txt"
            result_path = runtime_root / "review-result.json"
            settings_path = runtime_root / "settings.json"
            plugin_root = Path(str(env["XDG_CONFIG_HOME"])) / "amp" / "plugins"
            plugin_path = next(plugin_root.glob("autoreview-*.ts"))
            observed["prompt"] = prompt_path.read_text(encoding="utf-8")
            observed["settings"] = json.loads(settings_path.read_text(encoding="utf-8"))
            observed["plugin"] = plugin_path.read_text(encoding="utf-8")
            observed["plugin_path"] = plugin_path
            observed["workspace"] = list(cwd.iterdir())
            result_path.write_text(json.dumps(FINAL_REPORT), encoding="utf-8")
            result_path.chmod(0o600)
            return subprocess.CompletedProcess(command, 0, amp_test_stream(cwd), "")

        inherited = {
            "AMP_API_KEY": "test-key",
            "AMP_URL": "https://attacker.invalid",
            "NODE_OPTIONS": "--require=/tmp/attack.js",
            "PYTHONPATH": "/tmp/attack",
            "PLUGINS": "inherited-plugins",
        }
        with tempfile.TemporaryDirectory(prefix="autoreview-amp-run-test.") as tmpdir:
            repo = Path(tmpdir) / "repo"
            repo.mkdir()
            with mock.patch.dict(os.environ, inherited, clear=False), mock.patch.object(
                AUTOREVIEW,
                "ensure_amp_isolation_supported",
                return_value="/usr/bin/amp",
            ), mock.patch.object(
                AUTOREVIEW,
                "run",
                side_effect=fake_preflight,
            ), mock.patch.object(
                AUTOREVIEW,
                "run_with_heartbeat",
                side_effect=fake_execute,
            ):
                output = AUTOREVIEW.run_amp(args, repo, secret_prompt)

        self.assertEqual(json.loads(output), FINAL_REPORT)
        self.assertFalse(observed["mcp_preflight_prompt_exists"])
        self.assertFalse(observed["preflight_prompt_exists"])
        preflight_command = observed["preflight_command"]
        self.assertIsInstance(preflight_command, list)
        assert isinstance(preflight_command, list)
        self.assertEqual(preflight_command[-2:], ["plugins", "list"])
        command = observed["command"]
        self.assertIsInstance(command, list)
        assert isinstance(command, list)
        self.assertIn("--execute", command)
        self.assertIn("--stream-json-input", command)
        self.assertIn("--settings-file", command)
        self.assertNotIn("--orb-execute", command)
        self.assertEqual(command[command.index("--mode") + 1], "autoreview")
        self.assertNotIn(secret_prompt, " ".join(command))
        self.assertNotIn(secret_prompt, str(observed["input"]))
        self.assertEqual(observed["prompt"], secret_prompt)
        self.assertEqual(observed["workspace"], [])
        settings = observed["settings"]
        self.assertIsInstance(settings, dict)
        assert isinstance(settings, dict)
        self.assertNotIn("amp.tools.disable", settings)
        self.assertNotIn("amp.tools.enable", settings)
        self.assertEqual(settings["amp.updates.mode"], "disabled")
        self.assertEqual(
            settings["amp.mcpPermissions"],
            [
                {"matches": {"command": "*"}, "action": "reject"},
                {"matches": {"url": "*"}, "action": "reject"},
            ],
        )
        plugin = observed["plugin"]
        self.assertIsInstance(plugin, str)
        assert isinstance(plugin, str)
        self.assertIn("amp.ai.generate", plugin)
        self.assertIn("amp.registerTool", plugin)
        self.assertIn("amp.createAgent", plugin)
        schema, _ = json.JSONDecoder().raw_decode(plugin.split("schema: ", 1)[1])
        self.assertEqual(schema, {
            "name": "autoreview_report",
            "description": "A security-focused code-review report for the supplied patch.",
            "fields": AUTOREVIEW.PROVIDER_SCHEMA["properties"],
        })
        self.assertIn('tools: ["autoreview_generate"]', plugin)
        self.assertIn("readFileSync", plugin)
        self.assertNotIn(secret_prompt, plugin)
        env = observed["env"]
        self.assertIsInstance(env, dict)
        assert isinstance(env, dict)
        self.assertEqual(env["AMP_API_KEY"], "test-key")
        self.assertNotIn("AMP_URL", env)
        self.assertNotIn("NODE_OPTIONS", env)
        self.assertNotIn("PYTHONPATH", env)
        self.assertEqual(env["PLUGINS"], "all")
        plugin_path = observed["plugin_path"]
        self.assertIsInstance(plugin_path, Path)
        assert isinstance(plugin_path, Path)
        self.assertRegex(plugin_path.stem, r"^autoreview-[0-9a-f]{32}$")
        cwd = observed["cwd"]
        self.assertIsInstance(cwd, Path)
        assert isinstance(cwd, Path)
        self.assertNotEqual(cwd.resolve(), repo.resolve())
        self.assertEqual(Path(env["HOME"]).parent, cwd.parent)

    def test_amp_stream_attestation_rejects_bad_events(self) -> None:
        cwd = Path("/tmp/amp-review-empty")
        misplaced_events = [
            json.loads(line) for line in amp_test_stream(cwd).splitlines()
        ]
        tool_use = misplaced_events[2]["message"]["content"].pop()
        misplaced_events[4]["message"]["content"].append(tool_use)
        misplaced = "\n".join(json.dumps(event) for event in misplaced_events) + "\n"
        extra_result_events = [
            json.loads(line) for line in amp_test_stream(cwd).splitlines()
        ]
        extra_result_events[3]["message"]["content"].append(
            {"type": "text", "text": "unexpected"}
        )
        extra_result = (
            "\n".join(json.dumps(event) for event in extra_result_events) + "\n"
        )
        cases = {
            "malformed": "not-json\n",
            "tools": amp_test_stream(cwd, tools=["autoreview_generate", "shell_command"]),
            "mcp": amp_test_stream(cwd, mcp_servers=[{"name": "server"}]),
            "trigger": amp_test_stream(cwd, trigger="untrusted diff"),
            "wrong tool": amp_test_stream(cwd, tool_name="shell_command"),
            "tool input": amp_test_stream(cwd, tool_input={"command": "id"}),
            "tool result": amp_test_stream(cwd, tool_result_id="wrong-id"),
            "unsanitized error": amp_test_stream(
                cwd,
                tool_error=True,
                tool_result_content="provider echoed PRIVATE_REVIEW_MARKER_8f3c",
            ),
            "multiple init": amp_test_stream(cwd).splitlines()[0] + "\n" + amp_test_stream(cwd),
            "multiple result": amp_test_stream(cwd) + amp_test_stream(cwd).splitlines()[-1] + "\n",
            "misplaced tool use": misplaced,
            "extra tool result content": extra_result,
        }
        for label, stream in cases.items():
            with self.subTest(label=label), self.assertRaisesRegex(
                SystemExit,
                "amp isolation attestation failed",
            ):
                AUTOREVIEW.attest_amp_stream(stream, cwd)

        self.assertTrue(AUTOREVIEW.attest_amp_stream(amp_test_stream(cwd), cwd))
        self.assertFalse(
            AUTOREVIEW.attest_amp_stream(amp_test_stream(cwd, tool_error=True), cwd)
        )

    @unittest.skipIf(os.name == "nt", "Amp runtime is unsupported on native Windows")
    def test_amp_run_reports_timeout_before_stream_attestation(self) -> None:
        args = argparse.Namespace(
            amp_bin="amp",
            engine_timeout_seconds=0.01,
            max_output_chars=2_000_000,
            model="openai/gpt-6.1-sol",
            stream_engine_output=False,
            thinking="high",
        )

        def fake_preflight(
            command: list[str],
            cwd: Path,
            **kwargs: object,
        ) -> subprocess.CompletedProcess[str]:
            env = kwargs["env"]
            assert isinstance(env, dict)
            if command[-2:] == ["tools", "list"]:
                return amp_test_mcp_denial_result(command, env)
            plugin_root = Path(str(env["XDG_CONFIG_HOME"])) / "amp" / "plugins"
            plugin_path = next(plugin_root.glob("autoreview-*.ts"))
            return subprocess.CompletedProcess(
                command,
                0,
                amp_test_plugin_list(plugin_path),
                "",
            )

        def fake_execute(
            command: list[str],
            cwd: Path,
            **kwargs: object,
        ) -> subprocess.CompletedProcess[str]:
            self.assertEqual(kwargs["max_runtime_seconds"], 0.01)
            return subprocess.CompletedProcess(
                command,
                124,
                '{"type":"system","subtype":"init"}\n',
                "amp engine timed out after 0.01s",
            )

        with tempfile.TemporaryDirectory(prefix="autoreview-amp-timeout-test.") as tmpdir:
            repo = Path(tmpdir) / "repo"
            repo.mkdir()
            with mock.patch.object(
                AUTOREVIEW,
                "ensure_amp_isolation_supported",
                return_value="/usr/bin/amp",
            ), mock.patch.object(
                AUTOREVIEW,
                "run",
                side_effect=fake_preflight,
            ), mock.patch.object(
                AUTOREVIEW,
                "run_with_heartbeat",
                side_effect=fake_execute,
            ), mock.patch.object(
                AUTOREVIEW,
                "attest_amp_stream",
                side_effect=AssertionError("timeout stream must not be attested"),
            ) as attest:
                with self.assertRaises(SystemExit) as exc_info:
                    AUTOREVIEW.run_amp(args, repo, "review")

        message = str(exc_info.exception)
        self.assertIn("amp engine failed (124)", message)
        self.assertIn("amp engine timed out after 0.01s", message)
        attest.assert_not_called()

    def test_amp_failed_process_and_invalid_artifact_keep_runtime_guards(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cases = (
                (subprocess.CompletedProcess([], 7, "", "provider failed"), "expected exactly one leading"),
                (subprocess.CompletedProcess([], 7, '{"type":"system","subtype":"init"}\n', ""), "unexpected adapter event sequence"),
                (subprocess.CompletedProcess([], 0, amp_test_stream(root, tools=["shell_command"]), ""), "exposed tools"),
                (subprocess.CompletedProcess([], 0, amp_test_stream(root), ""), "produced no result file"),
                (subprocess.CompletedProcess([], 0, '{"type":[]}\n', ""), "unexpected stream event type"),
            )
            for result, diagnostic in cases:
                with self.subTest(diagnostic=diagnostic), self.assertRaises(AUTOREVIEW.ReviewerUnavailable) as caught:
                    AUTOREVIEW.amp_review_result(result, root, root / "error", root / "result")
                self.assertEqual(caught.exception.reason, "runtime_validation_failed")
                self.assertIn(diagnostic, str(caught.exception))
                self.assertEqual(caught.exception.returncode, result.returncode)
            for raw in ("[" * 2000 + "]" * 2000, '{"number":' + "9" * 10000 + "}"):
                with self.subTest(length=len(raw)), self.assertRaises(AUTOREVIEW.ReviewerUnavailable) as caught:
                    AUTOREVIEW.amp_review_result(subprocess.CompletedProcess([], 0, raw, ""), root, root / "error", root / "result")
                self.assertEqual(caught.exception.reason, "runtime_validation_failed")

    def test_amp_plugin_inventory_attestation_fails_closed(self) -> None:
        cwd = Path("/tmp/amp-review-empty")
        plugin_path = cwd.parent / "config" / "amp" / "plugins" / "autoreview-token.ts"
        valid = amp_test_plugin_list(plugin_path)
        AUTOREVIEW.attest_amp_plugin_inventory(valid, plugin_path, cwd)

        cases = {
            "missing": "",
            "inactive": valid.replace("✓", "✗", 1).replace(" active", " error", 1),
            "other plugin": valid
            + amp_test_plugin_list(plugin_path.with_name("unexpected.ts")),
            "event handler": valid + "  events: agent.start\n",
            "other tool": valid.replace(
                "  agent: autoreview-adapter",
                "  tool: shell_command\n  agent: autoreview-adapter",
            ),
        }
        for label, output in cases.items():
            with self.subTest(label=label), self.assertRaisesRegex(
                SystemExit,
                "amp plugin isolation preflight failed",
            ):
                AUTOREVIEW.attest_amp_plugin_inventory(output, plugin_path, cwd)

    @unittest.skipIf(os.name == "nt", "Amp runtime is unsupported on native Windows")
    def test_amp_run_surfaces_direct_generation_failure(self) -> None:
        args = argparse.Namespace(
            amp_bin="amp",
            max_output_chars=2_000_000,
            model="openai/gpt-6.1-sol",
            stream_engine_output=False,
            thinking="high",
        )

        def fake_preflight(
            command: list[str],
            cwd: Path,
            **kwargs: object,
        ) -> subprocess.CompletedProcess[str]:
            env = kwargs["env"]
            assert isinstance(env, dict)
            if command[-2:] == ["tools", "list"]:
                return amp_test_mcp_denial_result(command, env)
            plugin_root = Path(str(env["XDG_CONFIG_HOME"])) / "amp" / "plugins"
            plugin_path = next(plugin_root.glob("autoreview-*.ts"))
            return subprocess.CompletedProcess(
                command,
                0,
                amp_test_plugin_list(plugin_path),
                "",
            )

        def fake_execute(
            command: list[str],
            cwd: Path,
            **kwargs: object,
        ) -> subprocess.CompletedProcess[str]:
            env = kwargs["env"]
            assert isinstance(env, dict)
            error_path = Path(str(env["XDG_CONFIG_HOME"])).parent / "review-error.txt"
            error_path.write_text("provider rejected model", encoding="utf-8")
            error_path.chmod(0o600)
            return subprocess.CompletedProcess(
                command,
                0,
                amp_test_stream(cwd, tool_error=True),
                "",
            )

        with tempfile.TemporaryDirectory(prefix="autoreview-amp-error-test.") as tmpdir:
            repo = Path(tmpdir) / "repo"
            repo.mkdir()
            with mock.patch.object(
                AUTOREVIEW,
                "ensure_amp_isolation_supported",
                return_value="/usr/bin/amp",
            ), mock.patch.object(
                AUTOREVIEW,
                "run",
                side_effect=fake_preflight,
            ), mock.patch.object(
                AUTOREVIEW,
                "run_with_heartbeat",
                side_effect=fake_execute,
            ):
                with self.assertRaisesRegex(SystemExit, "provider rejected model"):
                    AUTOREVIEW.run_amp(args, repo, "review")


class AutoreviewTruffleHogTests(unittest.TestCase):
    def test_refusal_does_not_echo_input_headings_or_scanner_fields(self) -> None:
        marker = "SYNTHETIC_SCAN_SENTINEL_NOT_A_CREDENTIAL"
        headings = [
            f"# Dataset: {marker}",
            f"# Prompt file: {marker}",
            'Source snapshot: ' + json.dumps({"path": marker, "line_count": 0}),
            'Removed source: ' + json.dumps({"path": marker}),
            '# Untracked File\npath: ' + json.dumps(marker),
            f"+++ b/{marker}",
            f"diff --git a/old.txt b/{marker}\n--- a/old.txt\n+++ b/{marker}\n@@ -1 +1 @@\n+example",
        ]
        for heading in headings:
            with self.subTest(heading=heading), tempfile.TemporaryDirectory() as tempdir:
                prompt = "# Dataset: safe-evidence.txt\n" + heading
                lines = [number for number, line in enumerate(prompt.splitlines(), 1) if marker in line]
                output = json.dumps({"SourceMetadata": {"Data": {"Filesystem": {"line": lines[-1]}}},
                                     "Raw": marker, "RawV2": marker})
                with mock.patch.object(AUTOREVIEW, "find_command", return_value="/trusted/trufflehog"), \
                        mock.patch.object(AUTOREVIEW, "run", return_value=subprocess.CompletedProcess(
                            [], AUTOREVIEW.TRUFFLEHOG_FINDINGS_EXIT_CODE, output, marker,
                        )), mock.patch.object(AUTOREVIEW, "run_engine") as provider:
                    with self.assertRaises(SystemExit) as error:
                        AUTOREVIEW.run_reviewer(argparse.Namespace(engine="codex", max_priority="P0"),
                                                 Path(tempdir), prompt, {"change.txt"}, [])
                self.assertNotIn(marker, str(error.exception))
                self.assertIn("remove credential material", str(error.exception))
                provider.assert_not_called()

    def test_scanner_checks_stdin_without_literal_ignore_markers(self) -> None:
        prompt = "unicode \u03c0\r\nsource without suppression instructions\n"
        commands = []
        with tempfile.TemporaryDirectory() as tempdir:
            def scanner(command, cwd, **kwargs):
                commands.append(command[1])
                if command[1] == "filesystem":
                    self.assertEqual(Path(command[2]).read_bytes(), prompt.encode("utf-8"))
                    return subprocess.CompletedProcess(command, 0, "", "")
                self.assertEqual(command[1], "stdin")
                self.assertEqual(kwargs["stdin"].read(), prompt.encode("utf-8"))
                return subprocess.CompletedProcess(command, AUTOREVIEW.TRUFFLEHOG_FINDINGS_EXIT_CODE, "", "")

            with mock.patch.object(AUTOREVIEW, "find_command", return_value="/trusted/trufflehog"), \
                    mock.patch.object(AUTOREVIEW, "run", side_effect=scanner), \
                    mock.patch.object(AUTOREVIEW, "run_engine", return_value=json.dumps(FINAL_REPORT)) as provider:
                with self.assertRaisesRegex(SystemExit, "refusing to send review pack"):
                    AUTOREVIEW.run_reviewer(argparse.Namespace(engine="codex", max_priority="P0"),
                                             Path(tempdir), prompt, {"change.txt"}, [])
            self.assertEqual(commands, ["filesystem", "stdin"])
            provider.assert_not_called()

    def test_binary_stdin_preserves_utf8_and_crlf_bytes(self) -> None:
        payload = "unicode \u03c0\r\nnext\n".encode("utf-8")
        with tempfile.TemporaryDirectory() as tempdir, tempfile.TemporaryFile() as source:
            source.write(payload)
            source.seek(0)
            result = AUTOREVIEW.run(
                [sys.executable, "-c", "import sys; print(sys.stdin.buffer.read().hex())"],
                Path(tempdir), stdin=source,
            )
        self.assertEqual(result.stdout.strip(), payload.hex())

    def test_every_provider_scans_each_pack_and_refuses_scanner_failures(self) -> None:
        for engine in ("codex", "claude", "amp", "pi", "kimi"):
            for failed_source, failure in ((None, None), (None, "missing"),
                                           ("filesystem", "finding"), ("filesystem", "error"),
                                           ("stdin", "finding"), ("stdin", "error")):
                with self.subTest(engine=engine, source=failed_source, failure=failure), tempfile.TemporaryDirectory() as tempdir:
                    repo = Path(tempdir)
                    args = argparse.Namespace(engine=engine, max_priority="P0")
                    prompts = [f"complete pack {index}: unicode \u03c0\r\n-context\n+change\n" for index in range(2)]
                    events: list[tuple[str, str]] = []
                    packs: list[Path] = []

                    def scanner(command, cwd, **kwargs):
                        source = command[1]
                        pack = Path(command[2]) if source == "filesystem" else Path(kwargs["stdin"].name)
                        data = pack.read_bytes() if source == "filesystem" else kwargs["stdin"].read()
                        packs.append(pack)
                        prompt = data.decode("utf-8")
                        self.assertIn(prompt, prompts)
                        self.assertEqual(cwd, pack.parent)
                        if os.name != "nt":
                            self.assertEqual(stat.S_IMODE(pack.stat().st_mode), 0o600)
                            self.assertEqual(stat.S_IMODE(pack.parent.stat().st_mode), 0o700)
                        events.append((source, prompt))
                        code = 0
                        if prompt == prompts[1] and source == failed_source:
                            code = {"finding": AUTOREVIEW.TRUFFLEHOG_FINDINGS_EXIT_CODE, "error": 1}.get(failure, 0)
                        return subprocess.CompletedProcess(command, code, "", "")

                    def provider(_args, _repo, prompt):
                        events.append(("send", prompt))
                        return json.dumps({**FINAL_REPORT, "review_completion": "complete"})

                    with mock.patch.object(AUTOREVIEW, "find_command", return_value="/trusted/trufflehog") as find, \
                            mock.patch.object(AUTOREVIEW, "run", side_effect=scanner), contextlib.ExitStack() as stack:
                        providers = {
                            name: stack.enter_context(mock.patch.object(AUTOREVIEW, f"run_{name}", side_effect=provider))
                            for name in ("codex", "claude", "amp", "pi", "kimi")
                        }
                        AUTOREVIEW.run_reviewer(args, repo, prompts[0], set(), [])
                        if failure == "missing":
                            find.return_value = None
                        if failure:
                            with self.assertRaisesRegex(SystemExit, "refusing to send review pack"):
                                AUTOREVIEW.run_reviewer(args, repo, prompts[1], set(), [])
                        else:
                            AUTOREVIEW.run_reviewer(args, repo, prompts[1], set(), [])
                        for name, call in providers.items():
                            self.assertEqual(call.call_count, (1 if failure else 2) if name == engine else 0)
                    expected = [("filesystem", prompts[0]), ("stdin", prompts[0]), ("send", prompts[0])]
                    if failure != "missing":
                        expected.append(("filesystem", prompts[1]))
                        if failed_source != "filesystem":
                            expected.append(("stdin", prompts[1]))
                    if not failure:
                        expected.append(("send", prompts[1]))
                    self.assertEqual(events, expected)
                    self.assertTrue(all(not pack.parent.exists() for pack in packs))

    def test_scanner_command_is_offline_by_default_and_reports_unverified_results(self) -> None:
        prompt = "review pack with redacted examples only"
        common = ["--json", "--no-color"]
        tail = ["--fail", "--fail-on-scan-errors", "--no-update"]
        for verify_online, verification in (
            (False, ["--no-verification", "--results=verified,unknown,unverified"]),
            (True, ["--results=verified,unknown"]),
        ):
            with self.subTest(verify_online=verify_online), tempfile.TemporaryDirectory() as tempdir:
                repo = Path(tempdir)
                sources: list[str] = []

                def run_scanner(
                    command: list[str],
                    cwd: Path,
                    **kwargs: object,
                ) -> subprocess.CompletedProcess[str]:
                    pack = Path(command[2]) if command[1] == "filesystem" else Path(kwargs["stdin"].name)
                    self.assertEqual(cwd, pack.parent)
                    data = pack.read_bytes() if command[1] == "filesystem" else kwargs["stdin"].read()
                    self.assertEqual(data, prompt.encode("utf-8"))
                    self.assertEqual(
                        command[3:] if command[1] == "filesystem" else command[2:],
                        [*common, *verification, *tail],
                    )
                    self.assertEqual(kwargs["check"], False)
                    sources.append(command[1])
                    return subprocess.CompletedProcess(command, 0, "", "")

                with mock.patch.object(
                    AUTOREVIEW,
                    "find_command",
                    return_value="/trusted/trufflehog",
                ), mock.patch.object(AUTOREVIEW, "run", side_effect=run_scanner):
                    AUTOREVIEW.scan_outgoing_review_pack(repo, prompt, verify_online)
                self.assertEqual(sources, ["filesystem", "stdin"])


# Codex lists neither model with none or minimal effort.
ASTRA_MODELS = ("gpt-6-astra", "gpt-6.2-astra")
GPT_6_2_MODELS = ("gpt-6.2-astra", "gpt-6.2-sol")


class AutoreviewCompatibilityTests(unittest.TestCase):
    def test_codex_rejects_unsupported_effort_from_cli_and_environment(self) -> None:
        cases = (
            *itertools.product(("gpt-6-astra",), ("none", "minimal", "ultra")),
            *itertools.product(GPT_6_2_MODELS, ("none", "minimal")),
        )
        with tempfile.TemporaryDirectory(prefix="autoreview-invalid-effort.") as tempdir:
            for (model, effort), source in itertools.product(
                cases, ("cli", "keyed-cli", "environment", "global-environment"),
            ):
                with self.subTest(model=model, effort=effort, source=source):
                    argv = [sys.executable, str(SCRIPT_PATH), "--engine", "codex",
                            "--codex-bin", str(Path(tempdir) / "missing-codex")]
                    env = {key: value for key, value in os.environ.items()
                           if not key.startswith("AUTOREVIEW_")}
                    if source in {"cli", "keyed-cli"}:
                        prefix = "codex=" if source == "keyed-cli" else ""
                        argv += ["--model", prefix + model, "--thinking", prefix + effort]
                    else:
                        prefix = "AUTOREVIEW_CODEX_" if source == "environment" else "AUTOREVIEW_"
                        env.update({prefix + "MODEL": model, prefix + "THINKING": effort})
                    # No Git repository or engine exists: rejection must precede preparation.
                    result = subprocess.run(argv, cwd=tempdir, env=env, text=True,
                                            capture_output=True, timeout=30)
                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertEqual(result.stdout, "")
                    valid = (
                        "high, low, max, medium, ultra, xhigh" if model in GPT_6_2_MODELS
                        else "high, low, max, medium, xhigh"
                    )
                    self.assertEqual(result.stderr.strip(),
                                     f"invalid thinking level for codex model {model}: {effort} (valid: {valid})")

    def test_gpt_6_2_ultra_is_passed_to_codex_exec(self) -> None:
        for model in GPT_6_2_MODELS:
            argv = ["autoreview", "--engine", "codex", "--model", model, "--thinking", "ultra"]
            with self.subTest(model=model), mock.patch.dict(os.environ, {}, clear=True), \
                    mock.patch.object(sys, "argv", argv), mock.patch.object(
                        AUTOREVIEW, "resolve_command", return_value="synthetic-codex",
                    ):
                reviewer = AUTOREVIEW.reviewer_args(AUTOREVIEW.parse_args())[0]
                directory = Path.cwd()
                command = AUTOREVIEW.codex_command(
                    reviewer, directory, directory, directory, directory / "schema",
                    directory / "output", reviewer.model, auth_config=[],
                )
                self.assertEqual(command[command.index("--model") + 1], model)
                self.assertIn('model_reasoning_effort="ultra"', command[:command.index("exec")])

    def test_astra_validation_uses_effective_cli_overrides(self) -> None:
        cases = [
            case
            for astra in ASTRA_MODELS
            for case in (
                ({"AUTOREVIEW_CODEX_MODEL": astra, "AUTOREVIEW_CODEX_THINKING": "none"},
                 ["--thinking", "high"], astra, "high"),
                ({"AUTOREVIEW_CODEX_MODEL": astra, "AUTOREVIEW_CODEX_THINKING": "minimal"},
                 ["--model", "gpt-6-luna"], "gpt-6-luna", "minimal"),
            )
        ]
        for env, overrides, model, effort in cases:
            with self.subTest(env=env, overrides=overrides), mock.patch.dict(os.environ, env, clear=True), \
                    mock.patch.object(sys, "argv", ["autoreview", "--engine", "codex", *overrides]):
                reviewer = AUTOREVIEW.reviewer_args(AUTOREVIEW.parse_args())[0]
                self.assertEqual(reviewer.model, model)
                self.assertEqual(reviewer.thinking, effort)

    def test_astra_preserves_supported_effort_and_explicit_model(self) -> None:
        for astra, effort in itertools.product(ASTRA_MODELS, (None, "low", "medium", "high", "xhigh", "max")):
            with self.subTest(model=astra, effort=effort):
                argv = ["autoreview", "--engine", "codex", "--model", astra]
                if effort:
                    argv += ["--thinking", effort]
                with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(sys, "argv", argv):
                    reviewer = AUTOREVIEW.reviewer_args(AUTOREVIEW.parse_args())[0]
                self.assertEqual(reviewer.model, astra)
                self.assertEqual(reviewer.thinking, effort or "high")
                # An explicit specialist route must not silently change models.
                self.assertIsNone(reviewer.fallback_model)

    def test_explicit_astra_rejects_unsupported_effort(self) -> None:
        for astra, effort in itertools.product(ASTRA_MODELS, ("none", "minimal")):
            with self.subTest(model=astra, effort=effort), mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
                sys, "argv", ["autoreview", "--engine", "codex", "--model", astra, "--thinking", effort],
            ):
                with self.assertRaisesRegex(SystemExit, f"invalid thinking level for codex model {re.escape(astra)}: {effort}"):
                    AUTOREVIEW.reviewer_args(AUTOREVIEW.parse_args())

    def test_claude_opus_reviews_default_to_medium_effort(self) -> None:
        cases = (
            ([], {}, "claude-opus-5-5", "medium"),
            (["--model", "opus"], {}, "opus", "medium"),
            (["--model", "opus[1m]"], {}, "opus[1m]", "medium"),
            (["--model", "claude-opus-5-5[1m]"], {}, "claude-opus-5-5[1m]", "medium"),
            (["--fallback-model", "claude-opus-5"], {}, "claude-opus-5-5", "medium"),
            (["--model", "claude-opus-5-5", "--thinking", "high"], {}, "claude-opus-5-5", "high"),
            ([], {"AUTOREVIEW_CLAUDE_THINKING": "xhigh"}, "claude-opus-5-5", "xhigh"),
            (["--model", "claude-fable-5-2"], {}, "claude-fable-5-2", None),
            (["--model", "fable"], {}, "fable", None),
        )
        for overrides, env, model, effort in cases:
            with self.subTest(overrides=overrides, env=env), mock.patch.dict(os.environ, env, clear=True), \
                    mock.patch.object(sys, "argv", ["autoreview", "--engine", "claude", *overrides]):
                reviewer = AUTOREVIEW.reviewer_args(AUTOREVIEW.parse_args())[0]
                self.assertEqual(reviewer.model, model)
                self.assertEqual(reviewer.thinking, effort)

    def test_claude_mixed_opus_fallback_chain_needs_an_explicit_effort(self) -> None:
        # One --effort covers the whole Claude invocation, so a chain that mixes Opus with
        # another model has no default that keeps Opus at medium and the other at its own.
        for overrides in (
            ["--fallback-model", "claude-fable-5-2"],
            ["--model", "claude-fable-5-2", "--fallback-model", "opus"],
            ["--model", "fable", "--fallback-model", "claude-fable-5-1, claude-opus-5-5"],
        ):
            with self.subTest(overrides=overrides), mock.patch.dict(os.environ, {}, clear=True), \
                    mock.patch.object(sys, "argv", ["autoreview", "--engine", "claude", *overrides]):
                with self.assertRaisesRegex(SystemExit, r"mixes Opus with other models.*--thinking claude=<level>"):
                    AUTOREVIEW.reviewer_args(AUTOREVIEW.parse_args())
        for overrides, env, effort in (
            (["--fallback-model", "claude-fable-5-2", "--thinking", "high"], {}, "high"),
            (["--fallback-model", "claude-fable-5-2"], {"AUTOREVIEW_CLAUDE_THINKING": "low"}, "low"),
            (["--model", "fable", "--fallback-model", "claude-fable-5-1"], {}, None),
        ):
            with self.subTest(overrides=overrides, env=env), mock.patch.dict(os.environ, env, clear=True), \
                    mock.patch.object(sys, "argv", ["autoreview", "--engine", "claude", *overrides]):
                self.assertEqual(AUTOREVIEW.reviewer_args(AUTOREVIEW.parse_args())[0].thinking, effort)

    def test_codex_effort_restrictions_do_not_change_other_models(self) -> None:
        for effort in ("none", "minimal"):
            with self.subTest(effort=effort), mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
                sys, "argv", ["autoreview", "--engine", "codex", "--model", "gpt-6-luna", "--thinking", effort],
            ):
                reviewer = AUTOREVIEW.reviewer_args(AUTOREVIEW.parse_args())[0]
                self.assertEqual(reviewer.model, "gpt-6-luna")
                self.assertEqual(reviewer.thinking, effort)
                self.assertIsNone(reviewer.fallback_model)

    @classmethod
    def setUpClass(cls) -> None:
        cls.home_dir = tempfile.TemporaryDirectory(prefix="autoreview-test-home.")
        cls.home_patch = mock.patch.object(Path, "home", return_value=Path(cls.home_dir.name))
        cls.home_patch.start()
        cls.home_keys = ("HOME", "USERPROFILE", "HOMEDRIVE", "HOMEPATH")
        cls.old_home_env = {key: os.environ.get(key) for key in cls.home_keys}
        os.environ["HOME"] = cls.home_dir.name
        os.environ["USERPROFILE"] = cls.home_dir.name
        os.environ.pop("HOMEDRIVE", None)
        os.environ.pop("HOMEPATH", None)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.home_patch.stop()
        for key, value in cls.old_home_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        cls.home_dir.cleanup()

    def test_kimi_bin_cli_option(self) -> None:
        with mock.patch.object(
            sys,
            "argv",
            ["autoreview", "--kimi-bin", "/tmp/trusted-kimi"],
        ):
            args = AUTOREVIEW.parse_args()
        self.assertEqual(args.kimi_bin, "/tmp/trusted-kimi")

    def test_kimi_reviewer_disables_tools(self) -> None:
        args = argparse.Namespace(
            engine="kimi",
            model=None,
            thinking=["on"],
            fallback_model=None,
            codex_config=None,
            codex_speed=None,
            tools=True,
            allow_kimi_argv_prompt=True,
        )

        reviewer = AUTOREVIEW.reviewer_args(args)[0]

        self.assertEqual(reviewer.engine, "kimi")
        self.assertEqual(reviewer.thinking, "on")
        self.assertFalse(reviewer.tools)

    def test_kimi_isolation_requires_current_cli_contract(self) -> None:
        args = argparse.Namespace(kimi_bin="kimi")
        required_flags = " ".join(
            [
                "--agent-file",
                "--skills-dir",
                "--prompt",
                "--output-format",
                "--model",
            ]
        )

        def fake_run(command: list[str], *_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
            if "--version" in command:
                return subprocess.CompletedProcess(command, 0, "0.31.1", "")
            return subprocess.CompletedProcess(command, 0, required_flags, "")

        with tempfile.TemporaryDirectory(prefix="autoreview-kimi-probe-test.") as tmpdir, mock.patch.object(
            AUTOREVIEW,
            "resolve_command",
            return_value="/usr/bin/kimi",
        ), mock.patch.object(
            AUTOREVIEW,
            "safe_engine_env",
            return_value={},
        ), mock.patch.object(
            AUTOREVIEW,
            "safe_temp_root",
            return_value=Path(tmpdir),
        ), mock.patch.object(
            AUTOREVIEW,
            "run",
            side_effect=fake_run,
        ):
            self.assertEqual(
                AUTOREVIEW.ensure_kimi_isolation_supported(args, Path(tmpdir)),
                "/usr/bin/kimi",
            )

    def test_kimi_invalid_streams_are_unavailable_after_launch(self) -> None:
        args = argparse.Namespace(engine="kimi", kimi_bin="kimi", model="kimi-model",
                                  stream_engine_output=False, thinking="on", max_priority="P2")
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir) / "repo"
            repo.mkdir()
            for stream in ("malformed JSON", '{"role":"meta"}\n', '{"role":"assistant","content":"{}"}'):
                with self.subTest(stream=stream), mock.patch.object(
                    AUTOREVIEW, "ensure_kimi_isolation_supported", return_value="/usr/bin/kimi",
                ), mock.patch.object(
                    AUTOREVIEW, "load_kimi_review_config", return_value=({"telemetry": False}, None),
                ), mock.patch.object(
                    AUTOREVIEW, "run_with_heartbeat", return_value=subprocess.CompletedProcess([], 0, stream, ""),
                ), mock.patch.object(AUTOREVIEW, "scan_outgoing_review_pack"):
                    with self.assertRaises(AUTOREVIEW.ReviewerUnavailable) as caught:
                        AUTOREVIEW.run_reviewer(args, repo, "synthetic pack", set(), [])
                    self.assertEqual(caught.exception.reason, "invalid_report")

    def test_kimi_runs_with_empty_tools_skills_and_mcp(self) -> None:
        args = argparse.Namespace(
            kimi_bin="kimi",
            model="kimi-model",
            stream_engine_output=False,
            thinking="on",
        )
        observed: dict[str, object] = {}

        def fake_run(
            command: list[str],
            cwd: Path,
            **kwargs: object,
        ) -> subprocess.CompletedProcess[str]:
            observed["command"] = command
            observed["cwd"] = cwd
            observed["env"] = kwargs["env"]
            env = kwargs["env"]
            assert isinstance(env, dict)
            home = Path(str(env["KIMI_CODE_HOME"]))
            observed["agent"] = (home / "reviewer.md").read_text(encoding="utf-8")
            observed["config"] = (home / "config.toml").read_text(encoding="utf-8")
            observed["skills"] = list((home / "skills").iterdir())
            observed["workspace"] = list(cwd.iterdir())
            stream = (
                json.dumps({"role": "meta", "type": "system.version", "version": "0.31.1"})
                + "\n"
                + json.dumps({"role": "assistant", "content": json.dumps(FINAL_REPORT)})
                + "\n"
            )
            return subprocess.CompletedProcess(command, 0, stream, "")

        with tempfile.TemporaryDirectory(prefix="autoreview-kimi-run-test.") as tmpdir:
            repo = Path(tmpdir) / "repo"
            repo.mkdir()
            with mock.patch.object(
                AUTOREVIEW,
                "ensure_kimi_isolation_supported",
                return_value="/usr/bin/kimi",
            ), mock.patch.object(
                AUTOREVIEW,
                "load_kimi_review_config",
                return_value=({"telemetry": False}, None),
            ), mock.patch.object(
                AUTOREVIEW,
                "run_with_heartbeat",
                side_effect=fake_run,
            ):
                output = AUTOREVIEW.run_kimi(args, repo, "review prompt")

        self.assertEqual(json.loads(output), FINAL_REPORT)
        command = observed["command"]
        self.assertIsInstance(command, list)
        assert isinstance(command, list)
        self.assertEqual(command[command.index("--prompt") + 1], "review prompt")
        self.assertEqual(command[command.index("--output-format") + 1], "stream-json")
        self.assertEqual(command[command.index("--model") + 1], "kimi-model")
        self.assertNotIn("--thinking", command)
        agent = observed["agent"]
        self.assertIsInstance(agent, str)
        assert isinstance(agent, str)
        self.assertIn("tools: []", agent)
        self.assertIn("subagents: []", agent)
        config = observed["config"]
        self.assertIsInstance(config, str)
        assert isinstance(config, str)
        self.assertIn("[thinking]", config)
        self.assertIn("enabled = true", config)
        self.assertEqual(observed["skills"], [])
        self.assertEqual(observed["workspace"], [])
        env = observed["env"]
        self.assertIsInstance(env, dict)
        assert isinstance(env, dict)
        self.assertEqual(env["KIMI_DISABLE_TELEMETRY"], "1")
        self.assertEqual(env["KIMI_CODE_NO_AUTO_UPDATE"], "1")
        self.assertNotEqual(Path(str(env["KIMI_CODE_HOME"])), repo)

    def test_agy_defaults_and_unsupported_flag_refusals(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
            sys, "argv", ["autoreview", "--engine", "agy", "--agy-bin", "/tmp/fake-agy"],
        ):
            reviewer = AUTOREVIEW.reviewer_args(AUTOREVIEW.parse_args())[0]
        self.assertEqual(reviewer.model, "gemini-4-neon-xhigh")
        self.assertEqual(reviewer.agy_bin, "/tmp/fake-agy")
        self.assertTrue(reviewer.tools)
        self.assertTrue(reviewer.web_search)
        self.assertIsNone(reviewer.fallback_model)

        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
            sys, "argv", ["autoreview", "--engine", "agy", "--no-tools"],
        ):
            with self.assertRaises(SystemExit) as cm:
                AUTOREVIEW.reviewer_args(AUTOREVIEW.parse_args())
        self.assertIn("--no-tools is not supported by the Agy engine", str(cm.exception))

        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
            sys, "argv", ["autoreview", "--engine", "agy", "--no-web-search"],
        ):
            with self.assertRaises(SystemExit) as cm:
                AUTOREVIEW.reviewer_args(AUTOREVIEW.parse_args())
        self.assertIn("--no-web-search is not supported by the Agy engine", str(cm.exception))

    def test_agy_safe_engine_env_filters_aws_and_extra_ssh_vars(self) -> None:
        with tempfile.TemporaryDirectory(prefix="autoreview-agy-env-test.") as tmpdir:
            repo = Path(tmpdir) / "repo"
            repo.mkdir()
            gcp_creds = Path(tmpdir) / "gcp.json"
            gcp_creds.write_text("{}", encoding="utf-8")
            aws_creds = Path(tmpdir) / "aws-creds"
            aws_creds.write_text("[default]\n", encoding="utf-8")
            env_vars = {
                "AGY_ADC_AUTH": "true",
                "GEMINI_API_KEY": "test-gemini-key",
                "GOOGLE_CLOUD_LOCATION": "eu",
                "GOOGLE_CLOUD_PROJECT": "demo-project",
                "GOOGLE_CLOUD_QUOTA_PROJECT": "demo-quota-project",
                "SSH_CONNECTION": "10.0.0.1 12345 10.0.0.2 22",
                "SSH_CLIENT": "10.0.0.1 12345 22",
                "SSH_TTY": "/dev/pts/0",
                "GOOGLE_APPLICATION_CREDENTIALS": str(gcp_creds),
                "AWS_SHARED_CREDENTIALS_FILE": str(aws_creds),
                "AWS_CONFIG_FILE": str(aws_creds),
                "OPENAI_API_KEY": "sk-unrelated",
            }
            with mock.patch.dict(os.environ, env_vars, clear=True):
                filtered = AUTOREVIEW.safe_engine_env(repo, [], engine="agy")
        self.assertEqual(filtered.get("AGY_ADC_AUTH"), "true")
        self.assertEqual(filtered.get("AGY_CLI_DISABLE_AUTO_UPDATE"), "true")
        self.assertEqual(filtered.get("GEMINI_API_KEY"), "test-gemini-key")
        self.assertEqual(filtered.get("GOOGLE_CLOUD_LOCATION"), "eu")
        self.assertEqual(filtered.get("GOOGLE_CLOUD_PROJECT"), "demo-project")
        self.assertEqual(filtered.get("GOOGLE_CLOUD_QUOTA_PROJECT"), "demo-quota-project")
        self.assertEqual(filtered.get("SSH_CONNECTION"), "10.0.0.1 12345 10.0.0.2 22")
        self.assertEqual(Path(str(filtered.get("GOOGLE_APPLICATION_CREDENTIALS"))).resolve(), gcp_creds.resolve())
        for forbidden in ("SSH_CLIENT", "SSH_TTY", "AWS_SHARED_CREDENTIALS_FILE", "AWS_CONFIG_FILE", "OPENAI_API_KEY"):
            self.assertNotIn(forbidden, filtered)

    def test_agy_isolated_home_excludes_global_hooks_plugins_and_stages_auth_only(self) -> None:
        with tempfile.TemporaryDirectory(prefix="autoreview-agy-home-test.") as tmpdir:
            root = Path(tmpdir)
            repo = root / "repo"
            repo.mkdir()
            real_home = root / "real-home"
            (real_home / ".gemini" / "config").mkdir(parents=True)
            (real_home / ".gemini" / "config" / "hooks.json").write_text('{"h":{"PreInvocation":[{"command":"pwn"}]}}', encoding="utf-8")
            (real_home / ".gemini" / "antigravity-cli" / "plugins").mkdir(parents=True)
            (real_home / ".gemini" / "antigravity-cli" / "plugins" / "evil.json").write_text("{}", encoding="utf-8")
            (real_home / ".gemini" / "antigravity-cli" / "settings.json").write_text('{"allowNonWorkspaceAccess":true}', encoding="utf-8")
            (real_home / ".gemini" / "antigravity-cli" / "antigravity-oauth-token").write_text("oauth-token-bytes", encoding="utf-8")
            (real_home / ".config" / "gcloud").mkdir(parents=True)
            (real_home / ".config" / "gcloud" / "application_default_credentials.json").write_text('{"type":"authorized_user"}', encoding="utf-8")
            runtime_root = root / "runtime"
            runtime_root.mkdir()
            # On POSIX, custom XDG_CONFIG_HOME and CLOUDSDK_CONFIG must NOT
            # override the documented $HOME/.config/gcloud default ADC identity.
            xdg_alt = root / "xdg-alt"
            (xdg_alt / "gcloud").mkdir(parents=True)
            (xdg_alt / "gcloud" / "application_default_credentials.json").write_text('{"type":"wrong_xdg"}', encoding="utf-8")
            cloudsdk_alt = root / "cloudsdk-alt"
            cloudsdk_alt.mkdir()
            (cloudsdk_alt / "application_default_credentials.json").write_text('{"type":"wrong_cloudsdk"}', encoding="utf-8")
            with mock.patch.dict(
                os.environ,
                {
                    "HOME": str(real_home),
                    "USERPROFILE": str(real_home),
                    "XDG_CONFIG_HOME": str(xdg_alt),
                    "CLOUDSDK_CONFIG": str(cloudsdk_alt),
                    "AGY_ADC_AUTH": "true",
                },
                clear=True,
            ), mock.patch.object(AUTOREVIEW.sys, "platform", "linux"):
                isolated_home, extra_env = AUTOREVIEW.stage_agy_isolated_home(repo, runtime_root)
            self.assertEqual(Path(extra_env["HOME"]), isolated_home)
            self.assertEqual(Path(extra_env["USERPROFILE"]), isolated_home)
            self.assertNotEqual(isolated_home.resolve(), real_home.resolve())
            self.assertFalse((isolated_home / ".gemini" / "config").exists())
            self.assertFalse((isolated_home / ".gemini" / "antigravity-cli" / "plugins").exists())
            self.assertFalse((isolated_home / ".gemini" / "antigravity-cli" / "settings.json").exists())
            staged_token = isolated_home / ".gemini" / "antigravity-cli" / "antigravity-oauth-token"
            self.assertTrue(staged_token.is_file())
            self.assertEqual(staged_token.read_text(encoding="utf-8"), "oauth-token-bytes")
            staged_adc = Path(extra_env["GOOGLE_APPLICATION_CREDENTIALS"])
            self.assertTrue(staged_adc.is_file())
            self.assertEqual(staged_adc.read_text(encoding="utf-8"), '{"type":"authorized_user"}')
            if os.name != "nt":
                self.assertEqual(staged_token.stat().st_mode & 0o777, 0o600)
                self.assertEqual(staged_adc.stat().st_mode & 0o777, 0o600)

            # On Windows, %APPDATA%\gcloud takes precedence over ~/.config/gcloud.
            appdata_dir = root / "appdata"
            (appdata_dir / "gcloud").mkdir(parents=True)
            (appdata_dir / "gcloud" / "application_default_credentials.json").write_text('{"type":"win_appdata"}', encoding="utf-8")
            win_runtime = root / "win-runtime"
            win_runtime.mkdir()
            with mock.patch.dict(
                os.environ,
                {
                    "HOME": str(real_home),
                    "USERPROFILE": str(real_home),
                    "APPDATA": str(appdata_dir),
                    "AGY_ADC_AUTH": "true",
                },
                clear=True,
            ), mock.patch.object(AUTOREVIEW.sys, "platform", "win32"):
                _, win_env = AUTOREVIEW.stage_agy_isolated_home(repo, win_runtime)
            self.assertEqual(
                Path(win_env["GOOGLE_APPLICATION_CREDENTIALS"]).read_text(encoding="utf-8"),
                '{"type":"win_appdata"}',
            )

    def test_agy_tier_suffixed_model_effort_validation(self) -> None:
        self.assertIsNone(AUTOREVIEW.agy_effort_arg("gemini-4-neon-xhigh", None))
        self.assertIsNone(AUTOREVIEW.agy_effort_arg("gemini-4-neon-xhigh", "xhigh"))
        self.assertEqual(AUTOREVIEW.agy_effort_arg("gemini-4-neon", "high"), "high")
        with self.assertRaises(SystemExit) as cm:
            AUTOREVIEW.agy_effort_arg("gemini-4-neon-xhigh", "low")
        self.assertIn("fixes reasoning tier xhigh", str(cm.exception))

    def test_agy_isolation_requires_current_cli_contract(self) -> None:
        args = argparse.Namespace(
            agy_bin="agy",
            model="gemini-4-neon-xhigh",
            thinking=None,
            engine_timeout_seconds=None,
        )
        full_help = (
            "--disable-slash-commands --sandbox --settings --input-format "
            "--output-format --json-schema --model --print --effort --print-timeout"
        )
        cases = (
            ("1.5.11\n", full_help, "1.5.12"),
            ("1.5.12\n", "--print --model", "--sandbox"),
            ("not-a-version\n", full_help, "could not parse --version"),
        )
        with tempfile.TemporaryDirectory(prefix="autoreview-agy-probe-test.") as tmpdir:
            repo = Path(tmpdir) / "repo"
            repo.mkdir()
            for version_out, help_out, expected in cases:
                with self.subTest(expected=expected), mock.patch.object(
                    AUTOREVIEW, "resolve_command", return_value="/usr/local/bin/agy",
                ), mock.patch.object(
                    AUTOREVIEW,
                    "run",
                    side_effect=[
                        subprocess.CompletedProcess(["agy", "--version"], 0, version_out, ""),
                        subprocess.CompletedProcess(["agy", "--help"], 0, help_out, ""),
                    ],
                ):
                    with self.assertRaises(SystemExit) as cm:
                        AUTOREVIEW.ensure_agy_isolation_supported(args, repo)
                self.assertIn(expected, str(cm.exception))

            with mock.patch.object(
                AUTOREVIEW, "resolve_command", return_value="/usr/local/bin/agy",
            ), mock.patch.object(
                AUTOREVIEW,
                "run",
                side_effect=[
                    subprocess.CompletedProcess(["agy", "--version"], 0, "1.5.12\n", ""),
                    subprocess.CompletedProcess(["agy", "--help"], 0, full_help, ""),
                ],
            ):
                self.assertEqual(AUTOREVIEW.ensure_agy_isolation_supported(args, repo), "/usr/local/bin/agy")

    def test_agy_runs_in_strict_sandbox_stream_json_mode(self) -> None:
        args = argparse.Namespace(
            agy_bin="agy",
            model="gemini-4-neon-xhigh",
            stream_engine_output=False,
            thinking="xhigh",
            tools=True,
            web_search=True,
            engine_timeout_seconds=120.0,
        )
        observed: dict[str, object] = {}

        def fake_run(
            command: list[str],
            cwd: Path,
            **kwargs: object,
        ) -> subprocess.CompletedProcess[str]:
            observed["command"] = command
            observed["cwd"] = cwd
            observed["env"] = kwargs.get("env")
            observed["input_text"] = kwargs.get("input_text")
            observed["workspace"] = list(cwd.iterdir())
            settings_path = Path(command[command.index("--settings") + 1])
            schema_path = Path(command[command.index("--json-schema") + 1])
            observed["settings"] = json.loads(settings_path.read_text(encoding="utf-8"))
            observed["schema"] = json.loads(schema_path.read_text(encoding="utf-8"))
            observed["settings_mode"] = settings_path.stat().st_mode & 0o777
            stream = "\n".join([
                json.dumps({"event": "init", "init": {"permission_mode": "strict", "model": "gemini-4-neon-xhigh"}}),
                json.dumps({"event": "step_update", "step_update": {"step_type": "user_input", "state": "DONE"}}),
                json.dumps({"event": "step_update", "step_update": {"step_type": "tool", "tool_name": "search_web", "state": "DONE"}}),
                json.dumps({
                    "event": "result",
                    "result": {
                        "conversation_id": "conv-1",
                        "status": "SUCCESS",
                        "response": json.dumps(FINAL_REPORT),
                        "structured_output": FINAL_REPORT,
                    },
                }),
            ]) + "\n"
            return subprocess.CompletedProcess(command, 0, stream, "")

        with tempfile.TemporaryDirectory(prefix="autoreview-agy-run-test.") as tmpdir:
            repo = Path(tmpdir) / "repo"
            repo.mkdir()
            fake_home = Path(tmpdir) / "home"
            fake_home.mkdir()
            with mock.patch.dict(
                os.environ,
                {"HOME": str(fake_home), "USERPROFILE": str(fake_home)},
                clear=True,
            ), mock.patch.object(
                AUTOREVIEW, "ensure_agy_isolation_supported", return_value="/usr/local/bin/agy",
            ), mock.patch.object(
                AUTOREVIEW, "run_with_heartbeat", side_effect=fake_run,
            ):
                output = AUTOREVIEW.run_agy(args, repo, "review prompt")

        self.assertEqual(json.loads(output), FINAL_REPORT)
        command = observed["command"]
        assert isinstance(command, list)
        self.assertNotIn("--dangerously-skip-permissions", command)
        self.assertNotIn("--mode", command)
        self.assertIn("--disable-slash-commands", command)
        self.assertIn("--sandbox", command)
        self.assertEqual(command[command.index("--input-format") + 1], "stream-json")
        self.assertEqual(command[command.index("--output-format") + 1], "stream-json")
        self.assertEqual(command[command.index("--model") + 1], "gemini-4-neon-xhigh")
        self.assertEqual(command[command.index("--print-timeout") + 1], "120s")
        self.assertEqual(command[command.index("--print") + 1], "")
        self.assertNotIn("review prompt", command)
        self.assertNotIn("--effort", command)
        self.assertEqual(
            json.loads(str(observed["input_text"])),
            {"event": "user", "message": {"content": "review prompt"}},
        )
        self.assertEqual(observed["settings"], AUTOREVIEW.AGY_ISOLATED_SETTINGS)
        env_observed = observed["env"]
        assert isinstance(env_observed, dict)
        self.assertEqual(env_observed.get("AGY_CLI_DISABLE_AUTO_UPDATE"), "true")
        if os.name != "nt":
            self.assertEqual(observed["settings_mode"], 0o600)
        self.assertEqual(observed["workspace"], [])

        # Bare GEMINI_API_KEY without explicit provider opt-in must NOT divert
        # an Antigravity account to the direct Gemini API.
        observed.clear()
        with tempfile.TemporaryDirectory(prefix="autoreview-agy-apikey-ambient.") as tmpdir:
            repo = Path(tmpdir) / "repo"
            repo.mkdir()
            fake_home = Path(tmpdir) / "home"
            fake_home.mkdir()
            with mock.patch.dict(
                os.environ,
                {"HOME": str(fake_home), "USERPROFILE": str(fake_home), "GEMINI_API_KEY": "test-key-123"},
                clear=True,
            ), mock.patch.object(
                AUTOREVIEW, "ensure_agy_isolation_supported", return_value="/usr/local/bin/agy",
            ), mock.patch.object(
                AUTOREVIEW, "run_with_heartbeat", side_effect=fake_run,
            ):
                AUTOREVIEW.run_agy(args, repo, "review prompt")
        self.assertEqual(observed["settings"], AUTOREVIEW.AGY_ISOLATED_SETTINGS)
        env_observed = observed["env"]
        assert isinstance(env_observed, dict)
        self.assertNotIn("GEMINI_API_KEY", env_observed)

        # Explicit provider opt-in via AUTOREVIEW_AGY_MODEL_PROVIDER=gemini
        # enables modelProvider: "gemini" and forwards GEMINI_API_KEY.
        observed.clear()
        with tempfile.TemporaryDirectory(prefix="autoreview-agy-apikey-explicit.") as tmpdir:
            repo = Path(tmpdir) / "repo"
            repo.mkdir()
            fake_home = Path(tmpdir) / "home"
            fake_home.mkdir()
            with mock.patch.dict(
                os.environ,
                {
                    "HOME": str(fake_home),
                    "USERPROFILE": str(fake_home),
                    "GEMINI_API_KEY": "test-key-123",
                    "AUTOREVIEW_AGY_MODEL_PROVIDER": "gemini",
                },
                clear=True,
            ), mock.patch.object(
                AUTOREVIEW, "ensure_agy_isolation_supported", return_value="/usr/local/bin/agy",
            ), mock.patch.object(
                AUTOREVIEW, "run_with_heartbeat", side_effect=fake_run,
            ):
                AUTOREVIEW.run_agy(args, repo, "review prompt")
        expected_with_provider = dict(AUTOREVIEW.AGY_ISOLATED_SETTINGS)
        expected_with_provider["modelProvider"] = "gemini"
        self.assertEqual(observed["settings"], expected_with_provider)
        env_observed = observed["env"]
        assert isinstance(env_observed, dict)
        self.assertEqual(env_observed.get("GEMINI_API_KEY"), "test-key-123")

        # Explicit provider opt-in via user settings.json modelProvider="gemini".
        observed.clear()
        with tempfile.TemporaryDirectory(prefix="autoreview-agy-apikey-settings.") as tmpdir:
            root = Path(tmpdir)
            repo = root / "repo"
            repo.mkdir()
            fake_home = root / "home"
            (fake_home / ".gemini" / "antigravity-cli").mkdir(parents=True)
            (fake_home / ".gemini" / "antigravity-cli" / "settings.json").write_text(
                json.dumps({"modelProvider": "gemini"}), encoding="utf-8",
            )
            with mock.patch.dict(
                os.environ,
                {"HOME": str(fake_home), "USERPROFILE": str(fake_home), "GEMINI_API_KEY": "test-key-123"},
                clear=True,
            ), mock.patch.object(
                AUTOREVIEW, "ensure_agy_isolation_supported", return_value="/usr/local/bin/agy",
            ), mock.patch.object(
                AUTOREVIEW, "run_with_heartbeat", side_effect=fake_run,
            ):
                AUTOREVIEW.run_agy(args, repo, "review prompt")
        self.assertEqual(observed["settings"], expected_with_provider)

        # Custom Gemini endpoint (GOOGLE_GEMINI_BASE_URL), enterprise gateway
        # routing, home-inside-repo targets, and unpreservable ADC files must
        # fail closed in ensure_agy_isolation_supported (--dry-run) and run_agy.
        with tempfile.TemporaryDirectory(prefix="autoreview-agy-gateway-test.") as tmpdir:
            root = Path(tmpdir)
            repo = root / "repo"
            repo.mkdir()
            clean_home = root / "clean-home"
            clean_home.mkdir()
            base_home_env = {"HOME": str(clean_home), "USERPROFILE": str(clean_home)}
            for label, env_map, expected_msg in (
                (
                    "custom gemini base url",
                    {
                        **base_home_env,
                        "GEMINI_API_KEY": "test-key-123",
                        "AUTOREVIEW_AGY_MODEL_PROVIDER": "gemini",
                        "GOOGLE_GEMINI_BASE_URL": "https://proxy.corp.example/gemini",
                    },
                    "GOOGLE_GEMINI_BASE_URL",
                ),
                (
                    "enterprise gateway env",
                    {**base_home_env, "AGY_LLM_GATEWAY_URL": "https://gateway.corp.example"},
                    "AGY_LLM_GATEWAY_URL",
                ),
            ):
                with self.subTest(label=label), mock.patch.dict(os.environ, env_map, clear=True):
                    with self.assertRaises(SystemExit) as cm:
                        AUTOREVIEW.ensure_agy_isolation_supported(args, repo)
                self.assertIn(expected_msg, str(cm.exception))

            gw_home = root / "gw-home"
            (gw_home / ".gemini" / "antigravity-cli").mkdir(parents=True)
            (gw_home / ".gemini" / "antigravity-cli" / "settings.json").write_text(
                json.dumps({"gateway": {"address": "https://gateway.corp.example"}}), encoding="utf-8",
            )
            with self.subTest(label="enterprise gateway cli settings.json"), mock.patch.dict(
                os.environ, {"HOME": str(gw_home), "USERPROFILE": str(gw_home)}, clear=True,
            ):
                with self.assertRaises(SystemExit) as cm:
                    AUTOREVIEW.ensure_agy_isolation_supported(args, repo)
            self.assertIn("enterprise gateway settings", str(cm.exception))

            agy_dir_home = root / "agy-dir-home"
            (agy_dir_home / ".antigravity").mkdir(parents=True)
            (agy_dir_home / ".antigravity" / "settings.json").write_text(
                json.dumps({"gateway": {"address": "https://gateway.corp.example"}}), encoding="utf-8",
            )
            with self.subTest(label="enterprise gateway ~/.antigravity/settings.json"), mock.patch.dict(
                os.environ, {"HOME": str(agy_dir_home), "USERPROFILE": str(agy_dir_home)}, clear=True,
            ):
                with self.assertRaises(SystemExit) as cm:
                    AUTOREVIEW.ensure_agy_isolation_supported(args, repo)
            self.assertIn("enterprise gateway settings", str(cm.exception))

            with self.subTest(label="reviewing HOME itself refuses fail-closed"), mock.patch.dict(
                os.environ, {"HOME": str(agy_dir_home), "USERPROFILE": str(agy_dir_home)}, clear=True,
            ):
                with self.assertRaises(SystemExit) as cm:
                    AUTOREVIEW.ensure_agy_isolation_supported(args, agy_dir_home)
            self.assertIn("cannot be verified outside the reviewed repository", str(cm.exception))

            with self.subTest(label="blank HOME refuses fail-closed"), mock.patch.dict(
                os.environ, {"HOME": ""}, clear=True,
            ):
                with self.assertRaises(SystemExit) as cm:
                    AUTOREVIEW.ensure_agy_isolation_supported(args, repo)
                self.assertIn("HOME cannot be verified", str(cm.exception))

            in_repo_gac = repo / "adc.json"
            in_repo_gac.write_text('{"type":"service_account"}', encoding="utf-8")
            with self.subTest(label="in-repo GOOGLE_APPLICATION_CREDENTIALS under AGY_ADC_AUTH"), mock.patch.dict(
                os.environ,
                {**base_home_env, "AGY_ADC_AUTH": "true", "GOOGLE_APPLICATION_CREDENTIALS": str(in_repo_gac)},
                clear=True,
            ):
                with self.assertRaises(SystemExit) as cm:
                    AUTOREVIEW.ensure_agy_isolation_supported(args, repo)
            self.assertIn("GOOGLE_APPLICATION_CREDENTIALS cannot be preserved", str(cm.exception))

            with self.subTest(label="machine-wide admin_settings.json gateway refuses"):
                admin_settings = root / "admin_settings.json"
                admin_settings.write_text(
                    json.dumps({"gateway": {"enabled": True, "address": "https://gateway.corp.example"}}),
                    encoding="utf-8",
                )
                with mock.patch.dict(os.environ, base_home_env, clear=True), mock.patch.object(
                    AUTOREVIEW, "agy_admin_settings_path", return_value=admin_settings,
                ):
                    with self.assertRaises(SystemExit) as cm:
                        AUTOREVIEW.ensure_agy_isolation_supported(args, repo)
                self.assertIn("admin_settings.json", str(cm.exception))

            with self.subTest(label="explicitly disabled gateway is honored"):
                disabled_gw_home = root / "disabled-gw-home"
                (disabled_gw_home / ".antigravity").mkdir(parents=True)
                (disabled_gw_home / ".antigravity" / "settings.json").write_text(
                    json.dumps({"gateway": {"enabled": False, "address": "https://gateway.corp.example"}}),
                    encoding="utf-8",
                )
                with mock.patch.dict(
                    os.environ,
                    {"HOME": str(disabled_gw_home), "USERPROFILE": str(disabled_gw_home)},
                    clear=True,
                ), mock.patch.object(
                    AUTOREVIEW, "agy_admin_settings_path", return_value=root / "missing-admin.json",
                ):
                    self.assertFalse(AUTOREVIEW.agy_explicit_gemini_api_provider(repo))

            with self.subTest(label="admin_settings.json enabled=false overrides user enabled=true"):
                admin_disabled = root / "admin_disabled.json"
                admin_disabled.write_text(
                    json.dumps({"gateway": {"enabled": False, "address": "https://gateway.corp.example"}}),
                    encoding="utf-8",
                )
                with mock.patch.dict(
                    os.environ,
                    {
                        "HOME": str(agy_dir_home),
                        "USERPROFILE": str(agy_dir_home),
                        "AGY_LLM_GATEWAY_URL": "https://user-gateway.example",
                    },
                    clear=True,
                ), mock.patch.object(
                    AUTOREVIEW, "agy_admin_settings_path", return_value=admin_disabled,
                ):
                    self.assertFalse(AUTOREVIEW.agy_explicit_gemini_api_provider(repo))

            with self.subTest(label="posix ignores USERPROFILE modelProvider when HOME has no cli settings"):
                posix_home = root / "posix-home"
                posix_home.mkdir()
                other_profile = root / "other-profile"
                (other_profile / ".gemini" / "antigravity-cli").mkdir(parents=True)
                (other_profile / ".gemini" / "antigravity-cli" / "settings.json").write_text(
                    json.dumps({"modelProvider": "gemini"}),
                    encoding="utf-8",
                )
                with mock.patch.dict(
                    os.environ,
                    {
                        "HOME": str(posix_home),
                        "USERPROFILE": str(other_profile),
                        "GEMINI_API_KEY": "test-key-123",
                    },
                    clear=True,
                ), mock.patch.object(AUTOREVIEW.sys, "platform", "linux"), mock.patch.object(
                    AUTOREVIEW, "agy_admin_settings_path", return_value=root / "missing-admin.json",
                ):
                    self.assertFalse(AUTOREVIEW.agy_explicit_gemini_api_provider(repo))

            with self.subTest(label="non-exact saved modelProvider refuses"):
                bad_case_home = root / "bad-case-home"
                (bad_case_home / ".gemini" / "antigravity-cli").mkdir(parents=True)
                (bad_case_home / ".gemini" / "antigravity-cli" / "settings.json").write_text(
                    json.dumps({"modelProvider": "Gemini"}),
                    encoding="utf-8",
                )
                with mock.patch.dict(
                    os.environ,
                    {
                        "HOME": str(bad_case_home),
                        "USERPROFILE": str(bad_case_home),
                        "GEMINI_API_KEY": "test-key-123",
                    },
                    clear=True,
                ), mock.patch.object(
                    AUTOREVIEW, "agy_admin_settings_path", return_value=root / "missing-admin.json",
                ):
                    with self.assertRaises(SystemExit) as cm:
                        AUTOREVIEW.agy_explicit_gemini_api_provider(repo)
                self.assertIn("unsupported modelProvider", str(cm.exception))

            if os.name != "nt":
                adc_symlink_home = root / "adc-symlink-home"
                (adc_symlink_home / ".config" / "gcloud").mkdir(parents=True)
                (adc_symlink_home / ".config" / "gcloud" / "application_default_credentials.json").symlink_to(in_repo_gac)
                with self.subTest(label="default ADC symlink into repo under AGY_ADC_AUTH"), mock.patch.dict(
                    os.environ,
                    {"HOME": str(adc_symlink_home), "USERPROFILE": str(adc_symlink_home), "AGY_ADC_AUTH": "true"},
                    clear=True,
                ), mock.patch.object(AUTOREVIEW.sys, "platform", "linux"):
                    with self.assertRaises(SystemExit) as cm:
                        AUTOREVIEW.ensure_agy_isolation_supported(args, repo)
                self.assertIn("existing default ADC credentials file cannot be preserved", str(cm.exception))

    def test_agy_stream_parser_preserves_unicode_line_separators_inside_json(self) -> None:
        report_with_nel = dict(FINAL_REPORT)
        report_with_nel["overall_explanation"] = "line1\u0085line2\u2028line3\u2029end"
        stream = (
            json.dumps({"event": "init", "init": {"permission_mode": "strict"}}, ensure_ascii=False)
            + "\n"
            + json.dumps(
                {"event": "result", "result": {"status": "SUCCESS", "structured_output": report_with_nel}},
                ensure_ascii=False,
            )
            + "\n"
        )
        parsed = json.loads(
            AUTOREVIEW.parse_agy_stream_output(subprocess.CompletedProcess(["agy"], 0, stream, ""))
        )
        self.assertEqual(parsed["overall_explanation"], "line1\u0085line2\u2028line3\u2029end")

    def test_agy_stream_parser_distinguishes_denied_tool_attempts_from_execution(self) -> None:
        strict_init = json.dumps({"event": "init", "init": {"permission_mode": "strict"}})
        ok_result = json.dumps({
            "event": "result",
            "result": {"status": "SUCCESS", "structured_output": FINAL_REPORT},
        })
        denied_stream = "\n".join([
            strict_init,
            json.dumps({"event": "step_update", "step_update": {"step_index": 2, "step_type": "tool", "tool_name": "run_command", "state": "ACTIVE"}}),
            json.dumps({
                "event": "step_update",
                "step_update": {
                    "step_index": 2,
                    "step_type": "tool",
                    "tool_name": "run_command",
                    "state": "ERROR",
                    "tool_info": {"error": {"type": "TOOL_ERROR", "message": "permission check failed: Permission denied for command(ls)."}},
                },
            }),
            ok_result,
        ]) + "\n"
        self.assertEqual(
            json.loads(AUTOREVIEW.parse_agy_stream_output(subprocess.CompletedProcess(["agy"], 0, denied_stream, ""))),
            FINAL_REPORT,
        )

        for label, bad_step in (
            (
                "command failed after run",
                {"step_index": 2, "step_type": "tool", "tool_name": "run_command", "state": "ERROR", "tool_info": {"error": {"type": "TOOL_ERROR", "message": "command exited with status 1"}}},
            ),
            (
                "os eacces permission denied",
                {"step_index": 2, "step_type": "tool", "tool_name": "run_command", "state": "ERROR", "tool_info": {"error": {"type": "TOOL_ERROR", "message": "cat /etc/shadow: Permission denied"}}},
            ),
            (
                "canceled mid-run",
                {"step_index": 2, "step_type": "tool", "tool_name": "run_command", "state": "CANCELED"},
            ),
        ):
            bad_stream = "\n".join([
                strict_init,
                json.dumps({"event": "step_update", "step_update": {"step_index": 2, "step_type": "tool", "tool_name": "run_command", "state": "ACTIVE"}}),
                json.dumps({"event": "step_update", "step_update": bad_step}),
                ok_result,
            ]) + "\n"
            with self.subTest(label=label):
                with self.assertRaises(AUTOREVIEW.ReviewerUnavailable) as cm:
                    AUTOREVIEW.parse_agy_stream_output(subprocess.CompletedProcess(["agy"], 0, bad_stream, ""))
                self.assertIn("disallowed tool 'run_command'", str(cm.exception))

        unhashable_tool_stream = "\n".join([
            strict_init,
            json.dumps({"event": "step_update", "step_update": {"step_index": 2, "step_type": "tool", "tool_name": ["run_command"], "state": "DONE"}}),
            ok_result,
        ]) + "\n"
        with self.assertRaises(AUTOREVIEW.ReviewerUnavailable) as cm:
            AUTOREVIEW.parse_agy_stream_output(subprocess.CompletedProcess(["agy"], 0, unhashable_tool_stream, ""))
        self.assertIn("malformed tool step event", str(cm.exception))

    def test_agy_rejects_error_non_strict_disallowed_tool_and_oversized_stream(self) -> None:
        args = argparse.Namespace(
            agy_bin="agy",
            model="gemini-4-neon-xhigh",
            stream_engine_output=False,
            thinking=None,
            tools=True,
            web_search=True,
            engine_timeout_seconds=None,
        )
        strict_init = json.dumps({"event": "init", "init": {"permission_mode": "strict"}})
        ok_result = json.dumps({
            "event": "result",
            "result": {"status": "SUCCESS", "structured_output": FINAL_REPORT},
        })
        cases = (
            (
                "error status",
                strict_init + "\n" + json.dumps({
                    "event": "result",
                    "result": {"status": "ERROR", "error": "authentication failed or timed out"},
                }),
                "authentication failed or timed out",
            ),
            (
                "non-strict init",
                json.dumps({"event": "init", "init": {"permission_mode": "always-proceed"}}) + "\n" + ok_result,
                "did not start in strict permission mode",
            ),
            (
                "disallowed tool",
                strict_init + "\n"
                + json.dumps({"event": "step_update", "step_update": {"step_type": "tool", "tool_name": "run_command", "state": "DONE"}})
                + "\n" + ok_result,
                "disallowed tool 'run_command'",
            ),
            (
                "oversized output",
                "x" * (AUTOREVIEW.AGY_MAX_OUTPUT_CHARS + 1),
                "exceeded",
            ),
            (
                "malformed json",
                "not-json",
                "non-JSON stream output",
            ),
        )
        with tempfile.TemporaryDirectory(prefix="autoreview-agy-err-test.") as tmpdir, mock.patch.dict(
            os.environ, {}, clear=True,
        ):
            repo = Path(tmpdir) / "repo"
            repo.mkdir()
            for label, payload, expected in cases:
                with self.subTest(label=label), mock.patch.object(
                    AUTOREVIEW, "ensure_agy_isolation_supported", return_value="/usr/local/bin/agy",
                ), mock.patch.object(
                    AUTOREVIEW,
                    "run_with_heartbeat",
                    return_value=subprocess.CompletedProcess(["agy"], 0, payload, ""),
                ):
                    with self.assertRaises(AUTOREVIEW.ReviewerUnavailable) as cm:
                        AUTOREVIEW.run_agy(args, repo, "review prompt")
                self.assertIn(expected, str(cm.exception))
            with self.subTest(label="recursion error"), mock.patch.object(
                AUTOREVIEW, "ensure_agy_isolation_supported", return_value="/usr/local/bin/agy",
            ), mock.patch.object(
                AUTOREVIEW,
                "run_with_heartbeat",
                return_value=subprocess.CompletedProcess(["agy"], 0, "{}\n", ""),
            ), mock.patch.object(
                AUTOREVIEW.json, "loads", side_effect=RecursionError("maximum recursion depth exceeded"),
            ):
                with self.assertRaises(AUTOREVIEW.ReviewerUnavailable) as cm:
                    AUTOREVIEW.run_agy(args, repo, "review prompt")
            self.assertIn("non-JSON stream output", str(cm.exception))

    def test_codex_config_status_exposes_keys_only(self) -> None:
        args = argparse.Namespace(codex_config=['model_verbosity="low"'])
        self.assertEqual(AUTOREVIEW.codex_config_keys(args), ["model_verbosity"])

    def test_codex_defaults_and_overrides(self) -> None:
        for options, model, thinking, fallback in (
            ([], "gpt-6.2-sol", "high", None),
            (["--thinking", "medium"], "gpt-6.2-sol", "medium", None),
            (["--model", "custom-model", "--thinking", "low"], "custom-model", "low", None),
        ):
            with self.subTest(options=options), mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
                sys, "argv", ["autoreview", *options],
            ):
                reviewer = AUTOREVIEW.reviewer_args(AUTOREVIEW.parse_args())[0]
                self.assertEqual((reviewer.model, reviewer.thinking, reviewer.fallback_model),
                                 (model, thinking, fallback))

    def test_codex_retries_configured_fallback_after_access_failure(self) -> None:
        args = argparse.Namespace(
            engine="codex",
            max_priority="P0",
            codex_bin="codex",
            codex_config=None,
            codex_speed=None,
            fallback_model="gpt-6.2-sol",
            model="gpt-6.2-astra",
            stream_engine_output=False,
            thinking="xhigh",
            tools=True,
            web_search=False,
        )
        prompt = "complete retry pack: unicode \u03c0\r\n-deleted line\n unchanged context\n"
        for failed_source, failure in ((None, None), (None, "missing"),
                                       ("filesystem", "finding"), ("filesystem", "error"),
                                       ("stdin", "finding"), ("stdin", "error")):
            with self.subTest(source=failed_source, failure=failure), tempfile.TemporaryDirectory(prefix="autoreview-codex-fallback.") as tmpdir:
                events: list[str] = []
                packs: list[Path] = []

                def scanner(command, _cwd, **kwargs):
                    source = command[1]
                    pack = Path(command[2]) if source == "filesystem" else Path(kwargs["stdin"].name)
                    data = pack.read_bytes() if source == "filesystem" else kwargs["stdin"].read()
                    packs.append(pack)
                    self.assertEqual(data, prompt.encode("utf-8"))
                    events.append(source)
                    code = 0
                    if "gpt-6.2-astra" in events and source == failed_source:
                        code = {"finding": AUTOREVIEW.TRUFFLEHOG_FINDINGS_EXIT_CODE, "error": 1}.get(failure, 0)
                    return subprocess.CompletedProcess(command, code, "", "")

                def fake_run(command, _cwd, **kwargs):
                    self.assertEqual(kwargs["input_text"], prompt)
                    model = command[command.index("--model") + 1]
                    events.append(model)
                    effort = "xhigh" if model == "gpt-6.2-astra" else "high"
                    self.assertIn(f'model_reasoning_effort="{effort}"', command)
                    if model == "gpt-6.2-astra":
                        if failure == "missing":
                            find.return_value = None
                        return subprocess.CompletedProcess(
                            command, 1, "",
                            "The model `gpt-6.2-astra` does not exist or you do not have access to it.",
                        )
                    output_path = Path(command[command.index("--output-last-message") + 1])
                    output_path.write_text(json.dumps({**FINAL_REPORT, "review_completion": "complete"}))
                    return subprocess.CompletedProcess(command, 0, "", "")

                with mock.patch.object(AUTOREVIEW, "resolve_command", return_value="/usr/bin/codex"), \
                        mock.patch.object(AUTOREVIEW, "ensure_codex_isolation_supported", return_value="/usr/bin/codex"), \
                        mock.patch.object(AUTOREVIEW, "codex_auth_config_flags", return_value=[]), \
                        mock.patch.object(AUTOREVIEW, "prepare_codex_runtime_auth", return_value=None), \
                        mock.patch.object(AUTOREVIEW, "find_command", return_value="/trusted/trufflehog") as find, \
                        mock.patch.object(AUTOREVIEW, "run", side_effect=scanner), \
                        mock.patch.object(AUTOREVIEW, "run_with_heartbeat", side_effect=fake_run):
                    if failure:
                        with self.assertRaisesRegex(SystemExit, "refusing to send review pack"):
                            AUTOREVIEW.run_reviewer(args, Path(tmpdir), prompt, set(), [])
                    else:
                        result = AUTOREVIEW.run_reviewer(args, Path(tmpdir), prompt, set(), [])
                        self.assertTrue(result.complete)
                        self.assertEqual(result.report["findings"], [])
                expected = ["filesystem", "stdin", "gpt-6.2-astra"]
                if failure != "missing":
                    expected.append("filesystem")
                    if failed_source != "filesystem":
                        expected.append("stdin")
                if not failure:
                    expected.append("gpt-6.2-sol")
                self.assertEqual(events, expected)
                self.assertTrue(all(not pack.parent.exists() for pack in packs))

    def test_codex_runs_outside_repo_with_bundle_only_workspace(self) -> None:
        args = argparse.Namespace(
            codex_bin="codex",
            codex_config=None,
            codex_speed=None,
            fallback_model=None,
            model="gpt-6.2-astra",
            stream_engine_output=False,
            thinking="high",
            tools=True,
            web_search=False,
        )
        observed: dict[str, object] = {}

        def fake_run(
            command: list[str],
            cwd: Path,
            *_args: object,
            **kwargs: object,
        ) -> subprocess.CompletedProcess[str]:
            observed["cwd"] = cwd
            observed["command"] = command
            observed["command_cwd"] = Path(command[command.index("-C") + 1])
            observed["workspace_entries"] = list(cwd.iterdir())
            observed["env"] = kwargs["env"]
            observed["schema"] = json.loads(Path(command[command.index("--output-schema") + 1]).read_text())
            output_path = Path(command[command.index("--output-last-message") + 1])
            output_path.write_text(json.dumps(FINAL_REPORT))
            return subprocess.CompletedProcess(command, 0, "", "")

        with tempfile.TemporaryDirectory(prefix="autoreview-codex-workspace-test.") as tmpdir:
            repo = Path(tmpdir)
            (repo / ".env").write_text("ignored environment fixture\n")
            with mock.patch.dict(
                os.environ,
                {"CODEX_HOME": ""},
                clear=False,
            ), mock.patch.object(
                AUTOREVIEW,
                "resolve_command",
                return_value="/usr/bin/codex",
            ), mock.patch.object(
                AUTOREVIEW,
                "ensure_codex_isolation_supported",
                return_value="/usr/bin/codex",
            ), mock.patch.object(
                AUTOREVIEW,
                "codex_auth_config_flags",
                return_value=[],
            ), mock.patch.object(
                AUTOREVIEW,
                "prepare_codex_runtime_auth",
                return_value=None,
            ), mock.patch.object(
                AUTOREVIEW,
                "codex_source_home",
                return_value=None,
            ), mock.patch.object(
                AUTOREVIEW,
                "run_with_heartbeat",
                side_effect=fake_run,
            ):
                output = AUTOREVIEW.run_codex(args, repo, "review")

            self.assertEqual(json.loads(output), FINAL_REPORT)
            self.assertEqual(observed["schema"], AUTOREVIEW.PROVIDER_SCHEMA)
            observed_cwd = observed["cwd"]
            command_cwd = observed["command_cwd"]
            self.assertIsInstance(observed_cwd, Path)
            self.assertIsInstance(command_cwd, Path)
            assert isinstance(observed_cwd, Path)
            assert isinstance(command_cwd, Path)
            self.assertNotEqual(observed_cwd.resolve(), repo.resolve())
            self.assertEqual(observed_cwd, command_cwd)
            self.assertEqual(observed["workspace_entries"], [])
            env = observed["env"]
            self.assertIsInstance(env, dict)
            assert isinstance(env, dict)
            self.assertNotEqual(env["HOME"], os.environ.get("HOME"))
            self.assertEqual(env["USERPROFILE"], env["HOME"])
            self.assertNotEqual(env.get("CODEX_HOME"), str(repo.resolve()))
            self.assertEqual(Path(env["CODEX_HOME"]).name, "codex-home")
            self.assertNotEqual(env["CODEX_HOME"], str((Path.home() / ".codex").resolve()))
            self.assertIn("features.shell_snapshot=false", observed["command"])
            self.assertIn("features.hooks=false", observed["command"])
            self.assertIn("features.plugins=false", observed["command"])
            self.assertIn("skills.include_instructions=false", observed["command"])

    def test_codex_does_not_fallback_after_unrelated_failure(self) -> None:
        args = argparse.Namespace(
            codex_bin="codex",
            codex_config=None,
            codex_speed=None,
            fallback_model="gpt-6.2-sol",
            model="gpt-6.2-astra",
            stream_engine_output=False,
            thinking="high",
            tools=True,
            web_search=False,
        )
        models: list[str] = []

        def fake_run(command: list[str], *_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
            models.append(command[command.index("--model") + 1])
            return subprocess.CompletedProcess(command, 1, "", "network timeout")

        with tempfile.TemporaryDirectory(prefix="autoreview-codex-fallback.") as tmpdir, mock.patch.object(
            AUTOREVIEW,
            "resolve_command",
            return_value="/usr/bin/codex",
        ), mock.patch.object(
            AUTOREVIEW,
            "ensure_codex_isolation_supported",
            return_value="/usr/bin/codex",
        ), mock.patch.object(AUTOREVIEW, "codex_auth_config_flags", return_value=[]), mock.patch.object(
            AUTOREVIEW,
            "prepare_codex_runtime_auth",
            return_value=None,
        ), mock.patch.object(
            AUTOREVIEW,
            "run_with_heartbeat",
            side_effect=fake_run,
        ):
            with self.assertRaisesRegex(SystemExit, "network timeout"):
                AUTOREVIEW.run_codex(args, Path(tmpdir), "review")

        self.assertEqual(models, ["gpt-6.2-astra"])

    def test_codex_does_not_fallback_after_model_capacity_failure(self) -> None:
        args = argparse.Namespace(
            codex_bin="codex",
            codex_config=None,
            codex_speed=None,
            fallback_model="gpt-6.2-sol",
            model="gpt-6.2-astra",
            stream_engine_output=False,
            thinking="high",
            tools=True,
            web_search=False,
        )
        models: list[str] = []

        def fake_run(command: list[str], *_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
            models.append(command[command.index("--model") + 1])
            return subprocess.CompletedProcess(
                command,
                1,
                "",
                "model_not_available: gpt-6.2-astra is temporarily unavailable due to capacity",
            )

        with tempfile.TemporaryDirectory(prefix="autoreview-codex-fallback.") as tmpdir, mock.patch.object(
            AUTOREVIEW,
            "resolve_command",
            return_value="/usr/bin/codex",
        ), mock.patch.object(
            AUTOREVIEW,
            "ensure_codex_isolation_supported",
            return_value="/usr/bin/codex",
        ), mock.patch.object(AUTOREVIEW, "codex_auth_config_flags", return_value=[]), mock.patch.object(
            AUTOREVIEW,
            "prepare_codex_runtime_auth",
            return_value=None,
        ), mock.patch.object(
            AUTOREVIEW,
            "run_with_heartbeat",
            side_effect=fake_run,
        ):
            with self.assertRaisesRegex(SystemExit, "temporarily unavailable"):
                AUTOREVIEW.run_codex(args, Path(tmpdir), "review")

        self.assertEqual(models, ["gpt-6.2-astra"])

    def test_codex_access_fallback_ignores_structured_output_text(self) -> None:
        result = subprocess.CompletedProcess(
            ["codex"],
            1,
            '{"type":"agent_message","text":"gpt-6.2-sol does not exist or you do not have access"}',
            '{"type":"agent_message","message":"gpt-6.2-sol does not exist or you do not have access"}',
        )

        self.assertFalse(
            AUTOREVIEW.codex_model_access_failure(result, "gpt-6.2-sol")
        )

    def test_codex_access_fallback_accepts_terminal_error_event(self) -> None:
        result = subprocess.CompletedProcess(
            ["codex"],
            1,
            '{"type":"error","message":"gpt-6.2-sol does not exist or you do not have access"}',
            "",
        )

        self.assertTrue(
            AUTOREVIEW.codex_model_access_failure(result, "gpt-6.2-sol")
        )

    def test_codex_access_fallback_accepts_account_model_list_error(self) -> None:
        result = subprocess.CompletedProcess(
            ["codex"],
            1,
            "",
            (
                "The model gpt-6.2-sol does not appear in the list of models "
                "available to your account"
            ),
        )

        self.assertTrue(
            AUTOREVIEW.codex_model_access_failure(result, "gpt-6.2-sol")
        )

    def test_codex_access_fallback_ignores_plain_stdout(self) -> None:
        message = "gpt-6.2-sol does not exist or you do not have access"
        stdout_result = subprocess.CompletedProcess(["codex"], 1, message, "")
        stderr_result = subprocess.CompletedProcess(["codex"], 1, "", message)

        self.assertFalse(
            AUTOREVIEW.codex_model_access_failure(stdout_result, "gpt-6.2-sol")
        )
        self.assertTrue(
            AUTOREVIEW.codex_model_access_failure(stderr_result, "gpt-6.2-sol")
        )

    def test_extract_json_accepts_dict_result_payload(self) -> None:
        payload = {
            "type": "result",
            "subtype": "success",
            "result": FINAL_REPORT,
            "session_id": "session-id",
            "request_id": "request-id",
        }
        self.assertEqual(AUTOREVIEW.extract_json(json.dumps(payload)), FINAL_REPORT)

    def test_extract_json_rejects_result_string_with_preamble(self) -> None:
        payload = {
            "type": "result",
            "subtype": "success",
            "result": "Inspecting the diff first.\n" + json.dumps(FINAL_REPORT),
        }
        with self.assertRaisesRegex(SystemExit, "result was not structured JSON"):
            AUTOREVIEW.extract_json(json.dumps(payload))

if __name__ == "__main__":
    unittest.main()
