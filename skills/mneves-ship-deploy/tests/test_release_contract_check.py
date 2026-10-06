"""Tests for scripts/release-contract-check.py.

The conforming repository is built at test time from tests/fixtures/conforming plus the shipped
reference scripts in assets/, so it can never drift from them. Every planted violation is that
repository with exactly one mutation; each test asserts that the specific check fails and that every
other check keeps the status it has on the conforming repository.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
CHECKER = SKILL / "scripts" / "release-contract-check.py"
ASSETS = SKILL / "assets"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "conforming"

IDS = [
    "entry.release", "entry.verify-live", "release.check-mode", "release.waivers",
    "release.pushed-source", "release.tag-after-proof", "release.evidence", "release.rollback",
    "release.runtime-pin", "served-commit", "cf.targets", "cf.env-routes", "cf.env-triggers",
    "cf.env-bindings", "cf.worker-cache", "cf.workers-dev-origin", "guardrail.local", "guardrail.ci",
]
# What the conforming repository reports: everything passes, and no workflow files means NA for CI.
CONFORMING = {i: "PASS" for i in IDS}
CONFORMING["guardrail.ci"] = "NA"


def load_module():
    spec = importlib.util.spec_from_file_location("release_contract_check", CHECKER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolve their module through sys.modules
    spec.loader.exec_module(module)
    return module


def build_conforming(dest: Path) -> Path:
    shutil.copytree(FIXTURE, dest)
    (dest / "scripts").mkdir()
    for name in ("release.sh", "verify-live.sh"):
        shutil.copy2(ASSETS / name, dest / "scripts" / name)
        (dest / "scripts" / name).chmod(0o755)
    return dest


def mutate(repo: Path, rel: str, old: str, new: str, count: int = -1) -> None:
    """Replace text in a repository file; fails the test when the text is absent (no silent no-ops)."""
    path = repo / rel
    text = path.read_text()
    if old not in text:
        raise AssertionError(f"mutation target not found in {rel}: {old!r}")
    path.write_text(text.replace(old, new, count))


def run_checker(*args: str) -> subprocess.CompletedProcess:
    env = {k: os.environ[k] for k in ("PATH", "LANG", "LC_ALL", "SYSTEMROOT") if k in os.environ}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "HOME": tempfile.gettempdir()})
    return subprocess.run([sys.executable, "-B", str(CHECKER), *args], capture_output=True, text=True, env=env)


def report_for(repo: Path) -> dict:
    proc = run_checker(str(repo), "--json")
    data = json.loads(proc.stdout)
    return {c["id"]: c for c in data["repos"][0]["checks"]}


def digest(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        h.update(str(path.relative_to(root)).encode())
        h.update(path.read_bytes())
        h.update(str(path.stat().st_mode).encode())
    return h.hexdigest()


HOME_PATH = re.compile(r"/(?:Users|home)/(?![<{$])[A-Za-z0-9._-]+/")
ACCOUNT_ID_SHAPE = re.compile(r"(?<![0-9A-Za-z_])[0-9a-f]{32}(?![0-9A-Za-z_])")
WORKERS_DEV_HOST = re.compile(r"([A-Za-z0-9-]+)\.workers\.dev\b")


def find_private_strings(text: str) -> list[str]:
    """Shapes that identify a person or an account: home-directory paths, 32-hex ids, and
    workers.dev account hosts other than example-*. Placeholders such as __ACCOUNT_ID__ never match."""
    found = [m.group(0) for m in HOME_PATH.finditer(text)]
    found += [m.group(0) for m in ACCOUNT_ID_SHAPE.finditer(text)]
    found += [m.group(0) for m in WORKERS_DEV_HOST.finditer(text) if not m.group(1).startswith("example-")]
    return found


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="release-contract.")
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.repo = build_conforming(self.tmp / "repo")

    def statuses(self, repo: Path | None = None) -> dict:
        return {i: c["status"] for i, c in report_for(repo or self.repo).items()}


class ConformingRepository(Base):
    def test_every_check_is_reported_once_in_order(self) -> None:
        proc = run_checker(str(self.repo), "--json")
        ids = [c["id"] for c in json.loads(proc.stdout)["repos"][0]["checks"]]
        self.assertEqual(ids, IDS)

    def test_conforming_repository_passes_every_check_and_exits_zero(self) -> None:
        proc = run_checker(str(self.repo), "--json")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(self.statuses(), CONFORMING)

    def test_every_result_carries_one_evidence_line(self) -> None:
        for check_id, check in report_for(self.repo).items():
            with self.subTest(check_id):
                self.assertTrue(check["evidence"].strip(), "empty evidence")
                self.assertNotIn("\n", check["evidence"])

    def test_evidence_names_path_and_line_where_one_exists(self) -> None:
        checks = report_for(self.repo)
        for check_id, pattern in {
            "release.check-mode": r"scripts/release\.sh:\d+",
            "release.pushed-source": r"scripts/release\.sh:\d+",
            "release.tag-after-proof": r"scripts/release\.sh:\d+",
            "release.evidence": r"scripts/release\.sh:\d+",
            "release.runtime-pin": r"scripts/release\.sh:\d+",
            "served-commit": r"src/worker\.ts:\d+",
            "cf.targets": r"wrangler\.jsonc",
        }.items():
            with self.subTest(check_id):
                self.assertRegex(checks[check_id]["evidence"], pattern)

    def test_text_output_labels_heuristic_checks(self) -> None:
        lines = {line.split()[1]: line for line in run_checker(str(self.repo)).stdout.splitlines() if line[:4].strip() in ("PASS", "FAIL", "WARN", "NA")}
        for check_id in ("release.pushed-source", "release.tag-after-proof", "release.rollback", "served-commit"):
            with self.subTest(check_id):
                self.assertIn("[heuristic]", lines[check_id])
        self.assertNotIn("[heuristic]", lines["entry.release"])

    def test_json_labels_heuristic_checks(self) -> None:
        checks = report_for(self.repo)
        for check_id in ("release.pushed-source", "release.tag-after-proof", "release.rollback", "served-commit", "cf.workers-dev-origin"):
            with self.subTest(check_id):
                self.assertTrue(checks[check_id]["heuristic"])
        for check_id in ("entry.release", "release.check-mode", "release.waivers", "release.evidence", "cf.env-routes"):
            with self.subTest(check_id):
                self.assertFalse(checks[check_id]["heuristic"])


# (name, mutation, check id, expected status, heuristic label expected or None, evidence pattern)
def _m_inherited_routes(repo: Path) -> None:
    mutate(repo, "wrangler.jsonc", '  "main": "src/worker.ts",\n', '  "main": "src/worker.ts",\n  "routes": [{ "pattern": "app.example.com", "custom_domain": true }],\n')
    mutate(repo, "wrangler.jsonc", '      "routes": [{ "pattern": "staging.example.com", "custom_domain": true }],\n', "")


def _m_env_missing_kv(repo: Path) -> None:
    mutate(repo, "wrangler.jsonc", '      "kv_namespaces": [{ "binding": "CACHE", "id": "staging-kv-id" }],\n', "")


def _m_env_missing_d1(repo: Path) -> None:
    mutate(repo, "wrangler.jsonc", '      "d1_databases": [{ "binding": "DB", "database_name": "demo-staging", "database_id": "staging-db-id" }],\n', "")


def _m_env_missing_vars(repo: Path) -> None:
    mutate(repo, "wrangler.jsonc", '      "vars": { "APP_ENV": "staging" },\n', "")


def _m_env_missing_triggers(repo: Path) -> None:
    mutate(repo, "wrangler.jsonc", '      "triggers": { "crons": ["0 10 * * *"] },\n', "", count=1)


def _m_cache_top(repo: Path) -> None:
    mutate(repo, "wrangler.jsonc", '  "main": "src/worker.ts",\n', '  "main": "src/worker.ts",\n  "cache": { "enabled": true },\n')


def _m_cache_off(repo: Path) -> None:
    mutate(repo, "wrangler.jsonc", '  "main": "src/worker.ts",\n', '  "main": "src/worker.ts",\n  "cache": { "enabled": false },\n')


def _m_cache_env_only(repo: Path) -> None:
    mutate(repo, "wrangler.jsonc", '      "vars": { "APP_ENV": "production" },\n', '      "vars": { "APP_ENV": "production" },\n      "cache": { "enabled": true },\n')


def _m_single_target(repo: Path) -> None:
    (repo / "wrangler.jsonc").write_text('{ "name": "demo-worker", "main": "src/worker.ts", "compatibility_date": "2026-01-01" }\n')


def _blanket(flag: str):
    def mutation(repo: Path) -> None:
        mutate(repo, "scripts/release.sh", "    --yes) yes=1 ;;\n", f"    --yes) yes=1 ;;\n    {flag}) skip_gates=1 ;;\n")
    return mutation


def _m_tag_before_verify(repo: Path) -> None:
    mutate(repo, "scripts/release.sh", 'say "Live checks against $url"\n', 'git -C "$root" tag -a "$tag" "$commit" -m early\nsay "Live checks against $url"\n')


def _m_no_tag_step(repo: Path) -> None:
    mutate(repo, "scripts/release.sh", 'git -C "$root" tag -a', 'echo not-a-tag -a')


def _m_missing_verify_live(repo: Path) -> None:
    (repo / "scripts" / "verify-live.sh").unlink()


def _m_verify_live_not_executable(repo: Path) -> None:
    (repo / "scripts" / "verify-live.sh").chmod(0o644)


def _m_missing_release(repo: Path) -> None:
    (repo / "scripts" / "release.sh").unlink()


def _m_release_not_executable(repo: Path) -> None:
    (repo / "scripts" / "release.sh").chmod(0o644)


def _m_no_pin(repo: Path) -> None:
    (repo / ".nvmrc").unlink()
    mutate(repo, "package.json", '  "packageManager": "npm@10.9.2"\n', "")
    mutate(repo, "package.json", '"version": "1.2.3",', '"version": "1.2.3"')


def _m_pin_not_compared(repo: Path) -> None:
    (repo / "scripts" / "release.sh").write_text(
        '#!/usr/bin/env bash\nset -euo pipefail\ncase "${1:-}" in staging|production) ;; *) exit 2 ;; esac\nfor a in "$@"; do case "$a" in --check) exit 0 ;; --waive) shift ;; esac; done\n'
        'git ls-remote --symref origin HEAD\nscripts/verify-live.sh "$1"\ngit tag -a "v1" HEAD\necho release.json\necho "wrangler rollback x"\n'
    )
    (repo / "scripts" / "release.sh").chmod(0o755)


def _m_no_check_flag(repo: Path) -> None:
    mutate(repo, "scripts/release.sh", "    --check) check=1 ;;\n", "")


def _m_no_waive(repo: Path) -> None:
    mutate(repo, "scripts/release.sh", "    --waive)\n", "    --waivx)\n")


def _m_no_remote_default_branch(repo: Path) -> None:
    mutate(repo, "scripts/release.sh", 'symref="$(git ls-remote --symref origin HEAD)"', 'symref="$(git rev-parse origin/HEAD)"')


def _m_no_evidence(repo: Path) -> None:
    mutate(repo, "scripts/release.sh", "release.json", "release.txt")


def _m_no_rollback(repo: Path) -> None:
    mutate(repo, "scripts/release.sh", 'wrangler rollback $previous --env $target -m \\"rollback $tag\\" -y', "wrangler status")


def _m_no_health_commit(repo: Path) -> None:
    mutate(repo, "src/worker.ts", "commit: env.APP_COMMIT, ", "")


def _m_workers_dev_origin(repo: Path) -> None:
    (repo / "src" / "proxy.ts").write_text('export const API_ORIGIN = "https://api-demo.example-account.workers.dev";\n')


def _m_no_hook(repo: Path) -> None:
    shutil.rmtree(repo / ".githooks")


def _m_workflow(repo: Path) -> None:
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "ci.yml").write_text("name: ci\non: push\njobs: {}\n")


VIOLATIONS = [
    ("inherited routes", _m_inherited_routes, "cf.env-routes", "FAIL", False, r"wrangler\.jsonc:\d+"),
    ("environment missing a kv binding", _m_env_missing_kv, "cf.env-bindings", "FAIL", False, r"kv_namespaces"),
    ("environment missing a d1 binding (not on the documented list)", _m_env_missing_d1, "cf.env-bindings", "FAIL", True, r"d1_databases"),
    ("environment missing vars", _m_env_missing_vars, "cf.env-bindings", "WARN", False, r"vars"),
    ("environment without its own triggers", _m_env_missing_triggers, "cf.env-triggers", "WARN", False, r"triggers"),
    ("Workers Cache on at the top level", _m_cache_top, "cf.worker-cache", "WARN", False, r"wrangler\.jsonc:\d+ Workers Cache is on for the top level; its key ignores Cookie and Authorization"),
    ("Workers Cache explicitly off", _m_cache_off, "cf.worker-cache", "PASS", False, r"off or absent"),
    ("Workers Cache on only under one environment", _m_cache_env_only, "cf.worker-cache", "WARN", False, r"wrangler\.jsonc:\d+ Workers Cache is on for env\.production;"),
    ("single deploy target", _m_single_target, "cf.targets", "FAIL", False, r"wrangler\.jsonc"),
    ("blanket --skip-checks", _blanket("--skip-checks"), "release.waivers", "FAIL", False, r"scripts/release\.sh:\d+"),
    ("blanket --skip-gates", _blanket("--skip-gates"), "release.waivers", "FAIL", False, r"--skip-gates"),
    ("blanket --no-verify", _blanket("--no-verify"), "release.waivers", "FAIL", False, r"--no-verify"),
    ("blanket --skip-tests", _blanket("--skip-tests"), "release.waivers", "FAIL", False, r"--skip-tests"),
    ("tag created before verify-live", _m_tag_before_verify, "release.tag-after-proof", "FAIL", True, r"scripts/release\.sh:\d+"),
    ("no tag step at all", _m_no_tag_step, "release.tag-after-proof", "WARN", True, r"no tag"),
    ("missing verify-live.sh", _m_missing_verify_live, "entry.verify-live", "FAIL", False, r"scripts/verify-live\.sh"),
    ("verify-live.sh not executable", _m_verify_live_not_executable, "entry.verify-live", "FAIL", False, r"executable"),
    ("missing release.sh", _m_missing_release, "entry.release", "FAIL", False, r"scripts/release\.sh"),
    ("release.sh not executable", _m_release_not_executable, "entry.release", "FAIL", False, r"executable"),
    ("undeclared runtime pin", _m_no_pin, "release.runtime-pin", "FAIL", True, r"no runtime pin"),
    ("pin declared but never compared", _m_pin_not_compared, "release.runtime-pin", "FAIL", True, r"compar"),
    ("no --check", _m_no_check_flag, "release.check-mode", "FAIL", False, r"--check"),
    ("no --waive and no blanket flag", _m_no_waive, "release.waivers", "WARN", False, r"--waive"),
    ("default branch not asked of the remote", _m_no_remote_default_branch, "release.pushed-source", "FAIL", True, r"ls-remote"),
    ("no release.json", _m_no_evidence, "release.evidence", "FAIL", False, r"release\.json"),
    ("no rollback command", _m_no_rollback, "release.rollback", "FAIL", True, r"rollback"),
    ("no commit in the health handler", _m_no_health_commit, "served-commit", "WARN", True, r"app-commit|commit"),
    ("hard-coded workers.dev origin", _m_workers_dev_origin, "cf.workers-dev-origin", "WARN", True, r"src/proxy\.ts:\d+"),
    ("no pre-commit hook", _m_no_hook, "guardrail.local", "FAIL", False, r"pre-commit"),
    ("workflow files present", _m_workflow, "guardrail.ci", "WARN", False, r"not proven to run"),
]

# Release-script mutations change what the release.* checks see, never the other checks.
SIDE_EFFECTS = {
    "missing release.sh": {"release.check-mode", "release.waivers", "release.pushed-source", "release.tag-after-proof",
                          "release.evidence", "release.rollback", "release.runtime-pin"},
    "release.sh not executable": set(),
    "pin declared but never compared": {"release.waivers", "release.check-mode"},
    "single deploy target": {"cf.env-routes", "cf.env-triggers", "cf.env-bindings"},
}


class PlantedViolations(Base):
    def test_each_violation_fails_its_own_check_and_nothing_else_moves(self) -> None:
        for name, mutation, check_id, status, heuristic, evidence in VIOLATIONS:
            with self.subTest(name):
                repo = build_conforming(self.tmp / re.sub(r"\W+", "-", name))
                mutation(repo)
                checks = report_for(repo)
                self.assertEqual(checks[check_id]["status"], status, checks[check_id])
                self.assertEqual(checks[check_id]["heuristic"], heuristic, checks[check_id])
                self.assertRegex(checks[check_id]["evidence"], evidence)
                allowed = {check_id} | SIDE_EFFECTS.get(name, set())
                for other, check in checks.items():
                    if other in allowed:
                        continue
                    expected = "WARN" if (other == "guardrail.ci" and name == "workflow files present") else CONFORMING[other]
                    self.assertEqual(check["status"], expected, f"{other} moved while planting '{name}': {check}")

    def test_exit_code_is_one_only_when_a_check_fails(self) -> None:
        for name, mutation, _check_id, status, *_ in VIOLATIONS:
            with self.subTest(name):
                repo = build_conforming(self.tmp / ("exit-" + re.sub(r"\W+", "-", name)))
                mutation(repo)
                proc = run_checker(str(repo), "--json")
                fails = [c for c in json.loads(proc.stdout)["repos"][0]["checks"] if c["status"] == "FAIL"]
                self.assertEqual(proc.returncode, 1 if fails else 0, proc.stdout)


class ReleaseScriptReading(Base):
    def test_a_comment_or_message_is_not_an_offered_bypass(self) -> None:
        mutate(self.repo, "scripts/release.sh", "set -euo pipefail\n", 'set -euo pipefail\n# there is no --skip-checks, no --no-verify\n', count=1)
        mutate(self.repo, "scripts/release.sh", '    *) echo "$usage" >&2; exit 2 ;;', '    --skip-checks) die "no blanket bypass: use --waive <gate>=<reason>" ;;\n    *) echo "$usage" >&2; exit 2 ;;')
        self.assertEqual(self.statuses()["release.waivers"], "PASS")

    def test_a_tag_command_in_a_message_or_a_list_is_not_a_tag_step(self) -> None:
        mutate(self.repo, "scripts/release.sh", 'say "Release plan"\n', 'echo "if it fails: git tag -d $tag"\ngit tag --list > /dev/null\nsay "Release plan"\n')
        self.assertEqual(self.statuses()["release.tag-after-proof"], "PASS")

    def test_a_check_for_the_script_file_is_not_a_call_to_it(self) -> None:
        # The conforming script tests `[ -x scripts/verify-live.sh ]` long before the proof; only the call counts.
        text = (self.repo / "scripts" / "release.sh").read_text()
        self.assertLess(text.index("-x scripts/verify-live.sh"), text.index("git -C \"$root\" tag -a"))
        self.assertEqual(self.statuses()["release.tag-after-proof"], "PASS")

    def test_a_two_line_wrapper_around_an_implementation_conforms(self) -> None:
        impl = self.repo / "scripts" / "release-impl.sh"
        shutil.move(self.repo / "scripts" / "release.sh", impl)
        (self.repo / "scripts" / "release.sh").write_text('#!/usr/bin/env bash\nexec "$(dirname "$0")/release-impl.sh" "$@"\n')
        (self.repo / "scripts" / "release.sh").chmod(0o755)
        statuses = self.statuses()
        for check_id in ("release.check-mode", "release.waivers", "release.pushed-source", "release.tag-after-proof",
                         "release.evidence", "release.rollback", "release.runtime-pin"):
            with self.subTest(check_id):
                self.assertEqual(statuses[check_id], "PASS")

    def test_the_pin_the_repository_declares_is_the_one_the_script_must_read(self) -> None:
        (self.repo / ".nvmrc").unlink()
        mutate(self.repo, "package.json", '  "packageManager": "npm@10.9.2"\n', '  "engines": { "node": "22.11.0" }\n')
        self.assertEqual(self.statuses()["release.runtime-pin"], "FAIL")  # declared in engines; the script reads packageManager
        mutate(self.repo, "scripts/release.sh", "packageManager", "engines")
        self.assertEqual(self.statuses()["release.runtime-pin"], "PASS")

    def test_tool_versions_counts_as_a_declared_pin(self) -> None:
        (self.repo / ".nvmrc").unlink()
        mutate(self.repo, "package.json", '  "packageManager": "npm@10.9.2"\n', "")
        mutate(self.repo, "package.json", '"version": "1.2.3",', '"version": "1.2.3"')
        (self.repo / ".tool-versions").write_text("nodejs 22.11.0\n")
        self.assertEqual(self.statuses()["release.runtime-pin"], "FAIL")
        mutate(self.repo, "scripts/release.sh", ".nvmrc", ".tool-versions")
        self.assertEqual(self.statuses()["release.runtime-pin"], "PASS")


class SourceSearch(Base):
    def test_app_commit_meta_tag_counts_as_served_commit(self) -> None:
        mutate(self.repo, "src/worker.ts", "commit: env.APP_COMMIT, ", "")
        self.assertEqual(self.statuses()["served-commit"], "WARN")
        (self.repo / "index.html").write_text('<html><head><meta name="app-commit" content="abc1234"></head></html>\n')
        self.assertEqual(self.statuses()["served-commit"], "PASS")

    def test_workers_dev_in_documentation_or_dependencies_is_ignored(self) -> None:
        (self.repo / "README.md").write_text("Preview at https://demo.example-account.workers.dev\n")
        (self.repo / "node_modules" / "dep").mkdir(parents=True)
        (self.repo / "node_modules" / "dep" / "index.js").write_text('const u = "https://x.example-account.workers.dev";\n')
        self.assertEqual(self.statuses()["cf.workers-dev-origin"], "PASS")

    def test_workers_dev_in_the_wrangler_config_is_reported(self) -> None:
        mutate(self.repo, "wrangler.jsonc", '"DOCS_URL": "https://docs.example.com/guide"', '"API_ORIGIN": "https://api.example-account.workers.dev"')
        proc = report_for(self.repo)
        self.assertEqual(proc["cf.workers-dev-origin"]["status"], "WARN")
        self.assertRegex(proc["cf.workers-dev-origin"]["evidence"], r"wrangler\.jsonc:\d+")


class WranglerConfig(Base):
    def toml_repo(self, text: str) -> Path:
        (self.repo / "wrangler.jsonc").unlink()
        (self.repo / "wrangler.toml").write_text(text)
        return self.repo

    CONFORMING_TOML = (
        'name = "demo-worker"\nmain = "src/worker.ts"\ncompatibility_date = "2026-01-01"\n'
        '[[kv_namespaces]]\nbinding = "CACHE"\nid = "top"\n'
        '[env.staging]\nroutes = ["staging.example.com/*"]\n[[env.staging.kv_namespaces]]\nbinding = "CACHE"\nid = "s"\n'
        '[env.production]\nroutes = ["app.example.com/*"]\n[[env.production.kv_namespaces]]\nbinding = "CACHE"\nid = "p"\n'
    )

    def test_wrangler_toml_is_read(self) -> None:
        statuses = self.statuses(self.toml_repo(self.CONFORMING_TOML))
        self.assertEqual(statuses["cf.targets"], "PASS")
        self.assertEqual(statuses["cf.env-routes"], "PASS")
        self.assertEqual(statuses["cf.env-bindings"], "PASS")

    def test_wrangler_toml_inherited_routes_and_missing_binding(self) -> None:
        text = self.CONFORMING_TOML.replace('main = "src/worker.ts"\n', 'main = "src/worker.ts"\nroute = "app.example.com/*"\n')
        text = text.replace('[env.staging]\nroutes = ["staging.example.com/*"]\n[[env.staging.kv_namespaces]]\nbinding = "CACHE"\nid = "s"\n', "[env.staging]\n")
        checks = report_for(self.toml_repo(text))
        self.assertEqual(checks["cf.env-routes"]["status"], "FAIL")
        self.assertRegex(checks["cf.env-routes"]["evidence"], r"wrangler\.toml:\d+")
        self.assertEqual(checks["cf.env-bindings"]["status"], "FAIL")

    def test_two_environments_without_a_second_top_level_target_count(self) -> None:
        text = 'name = "w"\n[env.staging]\nname = "w-s"\n[env.production]\nname = "w-p"\n'
        self.assertEqual(self.statuses(self.toml_repo(text))["cf.targets"], "PASS")

    def test_no_wrangler_config_makes_the_cloudflare_checks_not_applicable(self) -> None:
        (self.repo / "wrangler.jsonc").unlink()
        statuses = self.statuses()
        for check_id in ("cf.targets", "cf.env-routes", "cf.env-triggers", "cf.env-bindings", "cf.worker-cache"):
            with self.subTest(check_id):
                self.assertEqual(statuses[check_id], "NA")

    def test_an_empty_binding_list_in_the_environment_still_counts_as_set(self) -> None:
        mutate(self.repo, "wrangler.jsonc", '      "kv_namespaces": [{ "binding": "CACHE", "id": "staging-kv-id" }],\n', '      "kv_namespaces": [],\n')
        self.assertEqual(self.statuses()["cf.env-bindings"], "PASS")

    CACHE_MESSAGE = ("its key ignores Cookie and Authorization, so every response that depends on them "
                     "must be private, no-store")

    def test_workers_cache_message_is_the_one_the_incident_calls_for(self) -> None:
        _m_cache_top(self.repo)
        evidence = report_for(self.repo)["cf.worker-cache"]["evidence"]
        self.assertIn(f"Workers Cache is on for the top level; {self.CACHE_MESSAGE}", evidence)

    def test_the_top_level_is_reported_and_inheritance_is_called_unknown(self) -> None:
        _m_cache_top(self.repo)
        check = report_for(self.repo)["cf.worker-cache"]
        self.assertEqual(check["status"], "WARN")
        self.assertIn("environments may inherit it", check["evidence"])
        self.assertNotIn("env.staging", check["evidence"])  # inheriting environments are not counted

    def test_an_environment_that_turns_it_off_under_a_top_level_true_is_still_reported_for_the_top_level_only(self) -> None:
        _m_cache_top(self.repo)
        mutate(self.repo, "wrangler.jsonc", '      "vars": { "APP_ENV": "staging" },\n', '      "vars": { "APP_ENV": "staging" },\n      "cache": { "enabled": false },\n')
        mutate(self.repo, "wrangler.jsonc", '      "vars": { "APP_ENV": "production" },\n', '      "vars": { "APP_ENV": "production" },\n      "cache": { "enabled": false },\n')
        check = report_for(self.repo)["cf.worker-cache"]
        self.assertEqual(check["status"], "WARN")
        self.assertIn("for the top level;", check["evidence"])
        self.assertNotIn("environments may inherit it", check["evidence"])  # every environment states its own value

    def test_an_environment_only_true_names_that_environment_and_not_the_top_level(self) -> None:
        _m_cache_env_only(self.repo)
        evidence = report_for(self.repo)["cf.worker-cache"]["evidence"]
        self.assertIn("env.production", evidence)
        self.assertNotIn("top level", evidence)
        self.assertNotIn("may inherit", evidence)

    def test_every_target_that_enables_it_is_named(self) -> None:
        _m_cache_top(self.repo)
        _m_cache_env_only(self.repo)
        evidence = report_for(self.repo)["cf.worker-cache"]["evidence"]
        self.assertIn("the top level", evidence)
        self.assertIn("env.production", evidence)

    def test_a_value_that_is_not_true_does_not_count(self) -> None:
        mutate(self.repo, "wrangler.jsonc", '  "main": "src/worker.ts",\n', '  "main": "src/worker.ts",\n  "cache": { "enabled": "true" },\n')
        self.assertEqual(self.statuses()["cf.worker-cache"], "PASS")

    def test_a_cache_table_without_enabled_is_off(self) -> None:
        mutate(self.repo, "wrangler.jsonc", '  "main": "src/worker.ts",\n', '  "main": "src/worker.ts",\n  "cache": {},\n')
        self.assertEqual(self.statuses()["cf.worker-cache"], "PASS")

    def test_toml_top_level_cache_table(self) -> None:
        text = self.CONFORMING_TOML.replace('[[kv_namespaces]]', '[cache]\nenabled = true\n[[kv_namespaces]]', 1)
        check = report_for(self.toml_repo(text))["cf.worker-cache"]
        self.assertEqual(check["status"], "WARN")
        self.assertRegex(check["evidence"], r"wrangler\.toml:\d+ Workers Cache is on for the top level;")

    def test_toml_environment_cache_table(self) -> None:
        text = self.CONFORMING_TOML.replace('[env.staging]\n', '[env.staging]\n[env.staging.cache]\nenabled = true\n', 1)
        check = report_for(self.toml_repo(text))["cf.worker-cache"]
        self.assertEqual(check["status"], "WARN")
        self.assertRegex(check["evidence"], r"wrangler\.toml:\d+ Workers Cache is on for env\.staging;")

    def test_toml_inline_cache_key_inside_an_environment(self) -> None:
        text = self.CONFORMING_TOML.replace('[env.production]\n', '[env.production]\ncache = { enabled = true }\n', 1)
        evidence = report_for(self.toml_repo(text))["cf.worker-cache"]["evidence"]
        self.assertRegex(evidence, r"wrangler\.toml:\d+ Workers Cache is on for env\.production;")

    def test_toml_without_a_cache_table_passes(self) -> None:
        self.assertEqual(self.statuses(self.toml_repo(self.CONFORMING_TOML))["cf.worker-cache"], "PASS")

    def test_workers_cache_follows_the_bindings_check_in_every_report(self) -> None:
        ids = [c["id"] for c in json.loads(run_checker(str(self.repo), "--json").stdout)["repos"][0]["checks"]]
        self.assertEqual(ids.index("cf.worker-cache"), ids.index("cf.env-bindings") + 1)

    def test_wrangler_json_is_read(self) -> None:
        data = json.dumps({"name": "w", "routes": ["x.example.com/*"], "env": {"staging": {}, "production": {"routes": ["y.example.com/*"]}}})
        (self.repo / "wrangler.jsonc").unlink()
        (self.repo / "wrangler.json").write_text(data)
        checks = report_for(self.repo)
        self.assertEqual(checks["cf.env-routes"]["status"], "FAIL")
        self.assertIn("env.staging", checks["cf.env-routes"]["evidence"])


class JsoncReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_module()

    def parse(self, text: str):
        return json.loads(self.mod.strip_jsonc(text))

    def test_line_and_block_comments_are_removed(self) -> None:
        self.assertEqual(self.parse('{ // one\n "a": 1, /* two */ "b": 2 }'), {"a": 1, "b": 2})

    def test_a_url_inside_a_string_survives(self) -> None:
        self.assertEqual(self.parse('{ "u": "https://example.com/a//b" }'), {"u": "https://example.com/a//b"})

    def test_a_comment_marker_after_an_escaped_quote_inside_a_string_survives(self) -> None:
        self.assertEqual(self.parse(r'{ "s": "say \"hi\" // not a comment" }'), {"s": 'say "hi" // not a comment'})

    def test_trailing_commas_are_removed_in_objects_and_arrays(self) -> None:
        self.assertEqual(self.parse('{ "a": [1, 2,], "b": { "c": 3, }, }'), {"a": [1, 2], "b": {"c": 3}})

    def test_a_trailing_comma_before_a_comment_and_a_closing_bracket(self) -> None:
        self.assertEqual(self.parse('{ "a": [1, // note\n ] }'), {"a": [1]})

    def test_a_comma_inside_a_string_next_to_a_bracket_survives(self) -> None:
        self.assertEqual(self.parse('{ "a": ",]" }'), {"a": ",]"})


class CommandLine(Base):
    def test_no_arguments_is_a_usage_error(self) -> None:
        proc = run_checker()
        self.assertEqual(proc.returncode, 2)
        self.assertIn("usage", (proc.stderr + proc.stdout).lower())

    def test_unknown_flag_is_a_usage_error(self) -> None:
        self.assertEqual(run_checker(str(self.repo), "--frobnicate").returncode, 2)

    def test_missing_directory_is_a_usage_error(self) -> None:
        self.assertEqual(run_checker(str(self.tmp / "nowhere")).returncode, 2)

    def test_fleet_without_a_directory_is_a_usage_error(self) -> None:
        self.assertEqual(run_checker("--fleet").returncode, 2)

    def test_fleet_and_repositories_together_are_a_usage_error(self) -> None:
        self.assertEqual(run_checker("--fleet", str(self.tmp), str(self.repo)).returncode, 2)

    def test_several_repositories_in_one_run(self) -> None:
        other = build_conforming(self.tmp / "other")
        _m_no_hook(other)
        proc = run_checker(str(self.repo), str(other), "--json")
        data = json.loads(proc.stdout)
        self.assertEqual([Path(r["path"]).name for r in data["repos"]], ["repo", "other"])
        self.assertEqual(proc.returncode, 1)

    def test_text_output_has_one_line_per_check_and_a_summary(self) -> None:
        out = run_checker(str(self.repo)).stdout
        for check_id in IDS:
            with self.subTest(check_id):
                self.assertEqual(sum(1 for line in out.splitlines() if line.split()[1:2] == [check_id]), 1)
        self.assertRegex(out, r"\d+ pass")


class FleetMode(Base):
    def make_fleet(self) -> Path:
        fleet = self.tmp / "fleet"
        fleet.mkdir()
        shutil.copytree(self.repo, fleet / "alpha")
        broken = build_conforming(fleet / "beta")
        _m_inherited_routes(broken)
        docker = fleet / "gamma"
        docker.mkdir()
        (docker / "Dockerfile").write_text("FROM scratch\n")
        compose = fleet / "delta"
        compose.mkdir()
        (compose / "compose.yaml").write_text("services: {}\n")
        (fleet / "notes").mkdir()
        (fleet / "notes" / "README.md").write_text("not a deployable\n")
        (fleet / "loose-file.txt").write_text("x\n")
        return fleet

    def test_one_row_per_deployable_child_one_character_per_check(self) -> None:
        proc = run_checker("--fleet", str(self.make_fleet()))
        rows = {line.split()[0]: line.split()[1] for line in proc.stdout.splitlines() if re.match(r"^\S+\s+[PFWN-]{18}$", line)}
        self.assertEqual(sorted(rows), ["alpha", "beta", "delta", "gamma"])
        self.assertEqual(len(rows["alpha"]), len(IDS))
        self.assertEqual(rows["alpha"].count("F"), 0)
        self.assertEqual(rows["beta"][IDS.index("cf.env-routes")], "F")
        self.assertEqual(rows["alpha"][IDS.index("guardrail.ci")], "-")
        self.assertEqual(proc.returncode, 1)

    def test_fleet_prints_a_legend_naming_the_columns_and_the_characters(self) -> None:
        legend = [line for line in run_checker("--fleet", str(self.make_fleet())).stdout.splitlines() if line.startswith("legend")]
        self.assertEqual(len(legend), 1)
        for token in ("P=pass", "F=fail", "W=warn", "-=n/a", *IDS):
            self.assertIn(token, legend[0])

    def test_fleet_json(self) -> None:
        fleet = self.make_fleet()
        data = json.loads(run_checker("--fleet", str(fleet), "--json").stdout)
        self.assertEqual(sorted(Path(r["path"]).name for r in data["repos"]), ["alpha", "beta", "delta", "gamma"])

    def test_a_fleet_with_no_failure_exits_zero(self) -> None:
        fleet = self.tmp / "clean"
        fleet.mkdir()
        shutil.copytree(self.repo, fleet / "only")
        self.assertEqual(run_checker("--fleet", str(fleet)).returncode, 0)

    def test_a_fleet_directory_with_no_deployable_child_exits_zero_and_says_so(self) -> None:
        empty = self.tmp / "empty"
        (empty / "docs").mkdir(parents=True)
        proc = run_checker("--fleet", str(empty))
        self.assertEqual(proc.returncode, 0)
        self.assertIn("no deployable", proc.stdout.lower())


def build_monorepo(dest: Path) -> Path:
    """Repository-level scripts, hook and pin, with two Worker units below apps/: web conforms, api inherits routes."""
    build_conforming(dest)
    for name in ("web", "api"):
        unit = dest / "apps" / name
        (unit / "src").mkdir(parents=True)
        shutil.copy2(dest / "src" / "worker.ts", unit / "src" / "worker.ts")
        shutil.copy2(dest / "wrangler.jsonc", unit / "wrangler.jsonc")
    (dest / "wrangler.jsonc").unlink()
    (dest / "src" / "worker.ts").unlink()
    (dest / "src").rmdir()
    _m_inherited_routes_at(dest / "apps" / "api")
    return dest


def _m_inherited_routes_at(unit: Path) -> None:
    mutate(unit, "wrangler.jsonc", '  "main": "src/worker.ts",\n', '  "main": "src/worker.ts",\n  "routes": [{ "pattern": "app.example.com", "custom_domain": true }],\n')
    mutate(unit, "wrangler.jsonc", '      "routes": [{ "pattern": "staging.example.com", "custom_domain": true }],\n', "")


def units_of(*args: str) -> dict:
    """{unit label: {check id: status}} for a run."""
    proc = run_checker(*args, "--json")
    return {r["unit"]: {c["id"]: c["status"] for c in r["checks"]} for r in json.loads(proc.stdout)["repos"]}


def evidence_of(*args: str) -> dict:
    proc = run_checker(*args, "--json")
    return {r["unit"]: {c["id"]: c["evidence"] for c in r["checks"]} for r in json.loads(proc.stdout)["repos"]}


class Monorepos(Base):
    def fleet(self) -> Path:
        fleet = self.tmp / "fleet"
        fleet.mkdir()
        return fleet

    def test_each_unit_of_a_monorepo_gets_its_own_row_with_its_own_statuses(self) -> None:
        fleet = self.fleet()
        build_monorepo(fleet / "mono")
        units = units_of("--fleet", str(fleet))
        self.assertEqual(sorted(units), ["mono/apps/api", "mono/apps/web"])
        self.assertEqual(units["mono/apps/web"], CONFORMING)
        self.assertEqual({k: v for k, v in units["mono/apps/api"].items() if v != CONFORMING[k]}, {"cf.env-routes": "FAIL"})

    def test_the_fleet_table_labels_units_by_repository_and_relative_path(self) -> None:
        fleet = self.fleet()
        build_monorepo(fleet / "mono")
        rows = {line.split()[0]: line.split()[1] for line in run_checker("--fleet", str(fleet)).stdout.splitlines()
                if re.match(r"^\S+\s+[PFWN-]{18}$", line)}
        self.assertEqual(sorted(rows), ["mono/apps/api", "mono/apps/web"])
        self.assertEqual(rows["mono/apps/api"][IDS.index("cf.env-routes")], "F")
        self.assertEqual(rows["mono/apps/web"].count("F"), 0)

    def test_a_repository_whose_only_config_is_nested_appears(self) -> None:
        fleet = self.fleet()
        (fleet / "solo" / "worker").mkdir(parents=True)
        (fleet / "solo" / "worker" / "wrangler.toml").write_text('name = "w"\n[env.staging]\n[env.production]\n')
        units = units_of("--fleet", str(fleet))
        self.assertEqual(list(units), ["solo/worker"])
        self.assertEqual(units["solo/worker"]["cf.targets"], "PASS")

    def test_the_repository_itself_is_a_unit_when_it_has_its_own_config(self) -> None:
        fleet = self.fleet()
        shutil.copytree(self.repo, fleet / "both")
        (fleet / "both" / "apps" / "x").mkdir(parents=True)
        (fleet / "both" / "apps" / "x" / "wrangler.toml").write_text('name = "x"\n')
        self.assertEqual(sorted(units_of("--fleet", str(fleet))), ["both", "both/apps/x"])

    def test_discovery_stops_three_levels_below_the_repository_and_skips_ignored_directories(self) -> None:
        fleet = self.fleet()
        config = 'name = "w"\n'
        for rel in ("r/a/b/c", "r/a/b/c/d", "r/node_modules/dep", "r/.hidden/h", "r/tests/fixture", "r/dist/out"):
            (fleet / rel).mkdir(parents=True)
            (fleet / rel / "wrangler.toml").write_text(config)
        self.assertEqual(list(units_of("--fleet", str(fleet))), ["r/a/b/c"])

    def test_a_unit_script_is_used_before_the_repository_script(self) -> None:
        fleet = self.fleet()
        mono = build_monorepo(fleet / "mono")
        (mono / "apps" / "web" / "scripts").mkdir()
        (mono / "apps" / "web" / "scripts" / "release.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
        (mono / "apps" / "web" / "scripts" / "release.sh").chmod(0o755)
        units = units_of("--fleet", str(fleet))
        evidence = evidence_of("--fleet", str(fleet))
        self.assertEqual(units["mono/apps/web"]["release.check-mode"], "FAIL")
        self.assertEqual(units["mono/apps/api"]["release.check-mode"], "PASS")
        self.assertIn("apps/web/scripts/release.sh", evidence["mono/apps/web"]["entry.release"])
        self.assertNotIn("apps/api", evidence["mono/apps/api"]["entry.release"])  # the repository-level script
        self.assertEqual(units["mono/apps/web"]["entry.verify-live"], "PASS")  # falls back to the repository's

    def test_a_missing_script_names_both_places_looked(self) -> None:
        fleet = self.fleet()
        mono = build_monorepo(fleet / "mono")
        (mono / "scripts" / "verify-live.sh").unlink()
        evidence = evidence_of("--fleet", str(fleet))["mono/apps/web"]["entry.verify-live"]
        self.assertIn("apps/web/scripts/verify-live.sh", evidence)
        self.assertIn("repository root", evidence)

    def test_guardrails_come_from_the_repository_root(self) -> None:
        fleet = self.fleet()
        mono = build_monorepo(fleet / "mono")
        (mono / ".github" / "workflows").mkdir(parents=True)
        (mono / ".github" / "workflows" / "ci.yml").write_text("name: ci\n")
        units = units_of("--fleet", str(fleet))
        self.assertEqual(len(units), 2)
        for unit in units.values():
            self.assertEqual(unit["guardrail.local"], "PASS")
            self.assertEqual(unit["guardrail.ci"], "WARN")

    def test_the_repository_pin_serves_a_unit_that_declares_none(self) -> None:
        fleet = self.fleet()
        build_monorepo(fleet / "mono")
        self.assertEqual(units_of("--fleet", str(fleet))["mono/apps/web"]["release.runtime-pin"], "PASS")

    def test_a_unit_pin_takes_precedence_over_the_repository_pin(self) -> None:
        fleet = self.fleet()
        mono = build_monorepo(fleet / "mono")
        (mono / "apps" / "web" / "package.json").write_text('{ "name": "web", "engines": { "node": "22.11.0" } }\n')
        units = units_of("--fleet", str(fleet))
        # The unit declares engines, which the repository release script never reads; the repository pins no longer count.
        self.assertEqual(units["mono/apps/web"]["release.runtime-pin"], "FAIL")
        self.assertEqual(units["mono/apps/api"]["release.runtime-pin"], "PASS")

    def test_a_unit_pin_counts_when_the_repository_declares_none(self) -> None:
        fleet = self.fleet()
        mono = build_monorepo(fleet / "mono")
        (mono / ".nvmrc").unlink()
        mutate(mono, "package.json", '  "packageManager": "npm@10.9.2"\n', "")
        mutate(mono, "package.json", '"version": "1.2.3",', '"version": "1.2.3"')
        (mono / "apps" / "web" / ".nvmrc").write_text("22.11.0\n")
        units = units_of("--fleet", str(fleet))
        self.assertEqual(units["mono/apps/web"]["release.runtime-pin"], "PASS")
        self.assertEqual(units["mono/apps/api"]["release.runtime-pin"], "FAIL")

    def test_source_searches_stay_inside_the_unit(self) -> None:
        fleet = self.fleet()
        mono = build_monorepo(fleet / "mono")
        mutate(mono, "apps/api/src/worker.ts", "commit: env.APP_COMMIT, ", "")
        (mono / "apps" / "api" / "src" / "proxy.ts").write_text(f'export const ORIGIN = "{PLANTED_WORKERS_HOST}";\n')
        units = units_of("--fleet", str(fleet))
        self.assertEqual(units["mono/apps/api"]["served-commit"], "WARN")  # web's health handler does not count for api
        self.assertEqual(units["mono/apps/api"]["cf.workers-dev-origin"], "WARN")
        self.assertEqual(units["mono/apps/web"]["served-commit"], "PASS")
        self.assertEqual(units["mono/apps/web"]["cf.workers-dev-origin"], "PASS")  # api's hard-coded origin is not web's

    def test_a_nested_unit_path_passed_as_the_repository_is_read_like_its_fleet_row(self) -> None:
        mono = build_monorepo(self.tmp / "mono")
        (mono / ".git").mkdir()
        fleet = self.fleet()
        shutil.copytree(mono, fleet / "mono")
        via_fleet = units_of("--fleet", str(fleet))["mono/apps/api"]
        direct = units_of(str(mono / "apps" / "api"))
        self.assertEqual(list(direct), ["mono/apps/api"])
        self.assertEqual(direct["mono/apps/api"], via_fleet)
        self.assertRegex(evidence_of(str(mono / "apps" / "api"))["mono/apps/api"]["cf.env-routes"], r"apps/api/wrangler\.jsonc:\d+")

    def test_a_repository_root_passed_as_the_repository_reports_each_of_its_units(self) -> None:
        mono = build_monorepo(self.tmp / "mono")
        self.assertEqual(sorted(units_of(str(mono))), ["mono/apps/api", "mono/apps/web"])
        self.assertEqual(run_checker(str(mono)).returncode, 1)

    def test_a_repository_with_no_unit_is_still_reported_as_itself(self) -> None:
        bare = self.tmp / "bare"
        bare.mkdir()
        self.assertEqual(list(units_of(str(bare))), ["bare"])


class ReadOnly(Base):
    def test_a_run_changes_nothing_and_executes_nothing(self) -> None:
        marker = self.tmp / "marker"
        (self.repo / "scripts" / "release.sh").write_text(
            f'#!/usr/bin/env bash\ntouch {marker}\ncase "$1" in --check) ;; esac\n'
        )
        (self.repo / "scripts" / "verify-live.sh").write_text(f"#!/usr/bin/env bash\ntouch {marker}\n")
        (self.repo / ".githooks" / "pre-commit").write_text(f"#!/usr/bin/env bash\ntouch {marker}\n")
        before = digest(self.repo)
        run_checker(str(self.repo))
        run_checker("--fleet", str(self.tmp))
        self.assertEqual(digest(self.repo), before)
        self.assertFalse(marker.exists(), "the checker ran a repository script")

    def test_the_checker_imports_no_network_or_process_module_and_never_writes(self) -> None:
        tree = ast.parse(CHECKER.read_text())
        forbidden = {"subprocess", "socket", "urllib", "http", "requests", "ssl", "ftplib", "smtplib", "shutil", "tempfile", "multiprocessing"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom):
                names = {(node.module or "").split(".")[0]}
            else:
                names = set()
            self.assertFalse(names & forbidden, f"forbidden import {names & forbidden}")
            if isinstance(node, ast.Call):
                func = node.func
                name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
                self.assertNotIn(name, {"system", "popen", "write_text", "write_bytes", "unlink", "rmdir", "mkdir", "rename",
                                        "touch", "chmod", "symlink_to", "exec", "eval", "Popen", "check_output"})
                if name == "open":
                    mode = ""
                    if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                        mode = str(node.args[1].value)
                    for kw in node.keywords:
                        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                            mode = str(kw.value.value)
                    self.assertFalse(set(mode) & set("wax+"), f"open() for writing: {mode}")

    def test_the_stated_python_floor_matches_the_syntax_it_uses(self) -> None:
        text = CHECKER.read_text()
        self.assertRegex(text, r"Python 3\.11")
        self.assertIn("tomllib", text)


class ShellSyntax(unittest.TestCase):
    def test_shipped_shell_files_parse_under_bash(self) -> None:
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("bash not available")
        for name in ("release.sh", "verify-live.sh", "release-guards.test.sh"):
            with self.subTest(name):
                proc = subprocess.run([bash, "-n", str(ASSETS / name)], capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_shipped_files_name_no_person_machine_or_account(self) -> None:
        tests_dir = Path(__file__).resolve().parent
        roots = [ASSETS, SKILL / "scripts", tests_dir]
        for root in roots:
            for path in sorted(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
                with self.subTest(str(path.relative_to(SKILL))):
                    self.assertEqual(find_private_strings(path.read_text()), [])


# Strings are assembled from parts so that this file does not itself contain what it forbids.
PLANTED_HOME = "/" + "Users" + "/" + "someone" + "/dev/project"
PLANTED_LINUX_HOME = "/" + "home" + "/" + "someone" + "/project"
PLANTED_ACCOUNT_ID = "0123456789abcdef" * 2
PLANTED_WORKERS_HOST = "https://api." + "acme-prod" + ".workers" + ".dev"


class PrivateStringScan(unittest.TestCase):
    def test_a_macos_home_path_is_found(self) -> None:
        self.assertTrue(find_private_strings(f"cd {PLANTED_HOME}"))

    def test_a_linux_home_path_is_found(self) -> None:
        self.assertTrue(find_private_strings(f"cd {PLANTED_LINUX_HOME}"))

    def test_a_32_hex_account_id_is_found(self) -> None:
        self.assertTrue(find_private_strings(f'ACCOUNT_ID="{PLANTED_ACCOUNT_ID}"'))

    def test_a_workers_dev_host_that_is_not_an_example_is_found(self) -> None:
        self.assertTrue(find_private_strings(f'const origin = "{PLANTED_WORKERS_HOST}";'))

    def test_placeholders_and_example_hosts_are_not_flagged(self) -> None:
        clean = (
            'ACCOUNT_ID="__ACCOUNT_ID__"\n'
            "see /" + "Users" + "/<name>/ for a home path\n"
            'origin = "https://api.example-account.workers' + '.dev"\n'
            "sha 0123456789abcdef0123456789abcde (31 hex) and 0123456789abcdef0123456789abcdef0 (33 hex)\n"
        )
        self.assertEqual(find_private_strings(clean), [])

    def test_a_planted_string_in_a_shipped_file_would_fail_the_tree_scan(self) -> None:
        with tempfile.TemporaryDirectory(prefix="private-scan.") as tmp:
            planted = Path(tmp) / "release.sh"
            planted.write_text(f"#!/usr/bin/env bash\ncd {PLANTED_HOME}\nACCOUNT_ID={PLANTED_ACCOUNT_ID}\n")
            self.assertEqual(len(find_private_strings(planted.read_text())), 2)


if __name__ == "__main__":
    unittest.main()
