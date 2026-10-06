#!/usr/bin/env python3
"""Read-only conformance checker for references/release-contract.md.

Usage:
    release-contract-check.py <repo>... [--json]
    release-contract-check.py --fleet <dir> [--json]

A repository is checked as one or more deployable units: a directory with a Wrangler config, a
Dockerfile or a Compose file, found at the repository root and up to three levels below it (skipping
dependency, build, hidden and test directories). Each unit gets its own report, labelled
<repo>/<relative path>. For a nested unit, Wrangler checks, source searches and the runtime pin read
the unit (the unit's own pin wins; otherwise the repository root's), scripts/release.sh and
scripts/verify-live.sh are looked up in the unit and then at the repository root, and the guardrails
read the repository root. A path passed as <repo> that sits below a directory holding `.git` is
checked as that single unit; a repository root expands to its units.

Reports PASS, FAIL, WARN or NA per check, with one evidence line (path:line where one exists).
Checks that infer behaviour from script or source text carry the label `heuristic`: they read
text, never run it, so a comment-free but unusual script can fool them either way.
Exit code: 0 when no check FAILs, 1 when any does, 2 on a usage error.

The checker never writes, never runs a repository's scripts and never touches the network.

Requires Python 3.11 or newer (tomllib, to read wrangler.toml); standard library only.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 11):
    sys.exit("release-contract-check: Python 3.11 or newer is required (tomllib)")

import argparse
import json
import os
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

PASS, FAIL, WARN, NA = "PASS", "FAIL", "WARN", "NA"
SYMBOL = {PASS: "P", FAIL: "F", WARN: "W", NA: "-"}
SEVERITY = {FAIL: 3, WARN: 2, PASS: 1, NA: 0}

IDS = (
    "entry.release", "entry.verify-live", "release.check-mode", "release.waivers",
    "release.pushed-source", "release.tag-after-proof", "release.evidence", "release.rollback",
    "release.runtime-pin", "served-commit", "cf.targets", "cf.env-routes", "cf.env-triggers",
    "cf.env-bindings", "cf.worker-cache", "cf.workers-dev-origin", "guardrail.local", "guardrail.ci",
)

SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", ".scratch", ".wrangler", ".next", ".turbo", ".venv", "venv",
    "__pycache__", "coverage", "vendor", ".cache", "target", ".idea", ".vscode",
}
TEST_DIRS = {"tests", "test", "__tests__", "spec", "fixtures", "docs", "examples"}
APP_SUFFIXES = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts", ".html", ".htm", ".py", ".go", ".rb", ".rs",
    ".php", ".vue", ".svelte", ".astro",
}
CONFIG_SUFFIXES = {".json", ".jsonc", ".toml", ".yml", ".yaml", ".env", ".cfg", ".ini"}
HTML_SUFFIXES = {".html", ".htm"}
APP_HTML_DIRS = {"src", "app", "pages", "public", "templates", "views", "web", "client"}
LOCK_FILES = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "composer.lock", "Cargo.lock", "uv.lock"}
MAX_FILE_BYTES = 1_000_000
MAX_FILES = 20_000

# Wrangler configuration reference, "Non-inheritable keys": environments do not inherit these.
DOCUMENTED_NON_INHERITABLE = (
    "define", "vars", "durable_objects", "kv_namespaces", "r2_buckets", "analytics", "ai_search_namespaces",
    "ai_search", "vectorize", "services", "queues", "workflows", "tail_consumers", "secrets", "secrets_store_secrets",
)
# Binding sections of the same reference that its explicit lists do not name. Its prose says bindings are
# not inheritable ("Bindings, such as `vars` or `kv_namespaces`, are not inheritable"), yet `assets` sits in
# the bindings section and the inheritable list, so the prose alone does not settle each of these keys.
# Reported as heuristic.
UNLISTED_BINDINGS = (
    "d1_databases", "hyperdrive", "browser", "ai", "images", "send_email", "mtls_certificates",
    "analytics_engine_datasets", "dispatch_namespaces",
)
# Configuration values rather than resources: an omission is worth a warning, not a failure.
VALUE_KEYS = {"vars", "define"}

MESSAGE_WORDS = {
    "echo", "printf", "die", "say", "warn", "log", "error", "usage", "bad_usage", "fail", "print",
    "console.log", "console.error", "exit", "return", "reject",
}


@dataclass(frozen=True)
class Result:
    id: str
    status: str
    evidence: str
    heuristic: bool = False

    def as_dict(self) -> dict:
        return {"id": self.id, "status": self.status, "heuristic": self.heuristic, "evidence": " ".join(self.evidence.split())}


# ---- JSONC ----

def strip_jsonc(text: str) -> str:
    """Remove comments and trailing commas, leaving string contents (URLs included) untouched."""
    out: list[str] = []
    i, n, in_string = 0, len(text), False
    while i < n:
        c = text[i]
        if in_string:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_string = False
            i += 1
        elif c == '"':
            in_string = True
            out.append(c)
            i += 1
        elif text.startswith("//", i):
            while i < n and text[i] != "\n":
                i += 1
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end == -1 else end + 2
            out.append(" ")
        else:
            out.append(c)
            i += 1
    return _drop_trailing_commas("".join(out))


def _drop_trailing_commas(text: str) -> str:
    out: list[str] = []
    i, n, in_string = 0, len(text), False
    while i < n:
        c = text[i]
        if in_string:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_string = False
        elif c == '"':
            in_string = True
            out.append(c)
        elif c == ",":
            j = i + 1
            while j < n and text[j] in " \t\r\n":
                j += 1
            if j >= n or text[j] not in "}]":
                out.append(c)
        else:
            out.append(c)
        i += 1
    return "".join(out)


# ---- Repository view ----

class Repo:
    def __init__(self, root: Path) -> None:
        self.root = root
        self._text: dict[Path, str | None] = {}
        self._walk: list[Path] | None = None

    def rel(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()

    def read(self, path: Path) -> str | None:
        if path not in self._text:
            try:
                with open(path, encoding="utf-8-sig", errors="replace") as handle:
                    self._text[path] = handle.read(MAX_FILE_BYTES + 1) if path.stat().st_size <= MAX_FILE_BYTES else None
            except OSError:
                self._text[path] = None
        return self._text[path]

    def files(self) -> list[Path]:
        if self._walk is None:
            found: list[Path] = []
            for dirpath, dirnames, filenames in os.walk(self.root):
                dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
                for name in sorted(filenames):
                    found.append(Path(dirpath) / name)
                if len(found) > MAX_FILES:
                    break
            self._walk = found
        return self._walk

    def source_files(self, suffixes: set[str], under: Path | None = None) -> list[Path]:
        """Files the application builds or runs. HTML counts only as an entry or template: index.html at the
        unit root, or HTML under an application directory; other HTML is documentation or an export."""
        picked = []
        base = under or self.root
        for path in self.files():
            if under is not None and not path.is_relative_to(under):
                continue
            if path.suffix in HTML_SUFFIXES:
                below = path.relative_to(base)
                if not (below.as_posix() == "index.html" or set(below.parts[:-1]) & APP_HTML_DIRS):
                    continue
            parts = set(path.relative_to(self.root).parts[:-1])
            name = path.name
            if path.suffix not in suffixes or name in LOCK_FILES or parts & TEST_DIRS:
                continue
            if re.search(r"\.(?:test|spec)\.", name):
                continue
            picked.append(path)
        return picked


@dataclass(frozen=True)
class Line:
    path: str
    no: int
    text: str

    def where(self) -> str:
        return f"{self.path}:{self.no}"


def code_lines(repo: Repo, path: Path) -> list[Line]:
    text = repo.read(path) or ""
    return [Line(repo.rel(path), no, raw) for no, raw in enumerate(text.splitlines(), 1)
            if raw.strip() and not raw.lstrip().startswith("#")]


def find_script(repo: Repo, unit: Path, name: str) -> Path | None:
    """scripts/<name> in the unit first, then at the repository root."""
    for base in (unit, repo.root):
        path = base / "scripts" / name
        if path.is_file():
            return path
    return None


def release_view(repo: Repo, script: Path | None) -> list[Line] | None:
    """Code lines of the release script; a short wrapper is read together with the file it hands over to."""
    if script is None:
        return None
    lines = code_lines(repo, script)
    if len(lines) <= 5:
        root = repo.root.resolve()
        seen = {script.resolve()}
        for line in list(lines):
            for candidate in re.findall(r"([\w./-]+\.(?:sh|bash|py|mjs|cjs|js|ts))\b", line.text):
                for target in (script.parent / Path(candidate).name, repo.root / candidate.lstrip("/")):
                    if target.is_file() and target.resolve() not in seen and target.resolve().is_relative_to(root):
                        seen.add(target.resolve())
                        lines.extend(code_lines(repo, target))
                        break
    return lines


def first_word(text: str) -> str:
    words = text.strip().lstrip("({!").split()
    return words[0] if words else ""


def is_message(text: str) -> bool:
    word = first_word(text)
    return word in MESSAGE_WORDS or word.startswith(("usage=", "usage ="))


FAILING_WORDS = {"die", "fail", "bad_usage", "error", "reject"}
TALKING_WORDS = {"echo", "printf", "usage", "print", "warn", "log", "say"}
REMOVAL_WORDS = re.compile(r"remov|no longer|deprecat|dropped|obsolet|not (?:supported|available|offered)|refus|recus|n[ãa]o (?:existe|[ée] mais)", re.I)


def split_statements(body: str) -> list[str]:
    """Split shell text on newlines, `;`, `&&` and `||` outside quotes."""
    out: list[str] = []
    current: list[str] = []
    quote = ""
    i = 0
    while i < len(body):
        c = body[i]
        if quote:
            current.append(c)
            if c == "\\" and quote == '"' and i + 1 < len(body):
                current.append(body[i + 1])
                i += 1
            elif c == quote:
                quote = ""
        elif c in "\"'":
            quote = c
            current.append(c)
        elif c in "\n;" or body.startswith(("&&", "||"), i):
            out.append("".join(current))
            current = []
            i += 1 if c in "\n;" else 2
            continue
        else:
            current.append(c)
        i += 1
    out.append("".join(current))
    return [st.strip() for st in out if st.strip()]


def arm_body(lines: list[Line], index: int, rest: str) -> tuple[str, int]:
    """Text of a case arm from after its label up to the closing `;;` (or `esac`), and the index of its last line."""
    if ";;" in rest:
        return rest.split(";;")[0], index
    parts = [rest]
    last = index
    for offset, line in enumerate(lines[index + 1:index + 30], 1):
        if ";;" in line.text:
            parts.append(line.text.split(";;")[0])
            last = index + offset
            break
        if re.match(r"\s*esac\b", line.text):
            break
        parts.append(line.text)
        last = index + offset
    return "\n".join(parts), last


def only_refuses(body: str) -> bool:
    """True when the arm does nothing but fail: die-like calls, messages, and `exit <non-zero>`."""
    ends = False
    for statement in split_statements(body):
        words = statement.lstrip("({!").split()
        word = words[0] if words else ""
        if word in FAILING_WORDS:
            ends = True
        elif word == "exit" and len(words) > 1 and re.fullmatch(r"[1-9]\d*", words[1]):
            ends = True
        elif word not in TALKING_WORDS:
            return False
    return ends


def lists_flag_as_available(line: Line, flag: str) -> re.Match[str] | None:
    """A usage or help line that names the flag as an option, unless it says the flag was removed."""
    if REMOVAL_WORDS.search(line.text) or re.search(r"\b(?:die|fail|bad_usage)\s+[\"']", line.text):
        return None  # says the flag was removed, or is the text of a refusal
    usage_line = re.search(r"usage", line.text, re.I)
    help_entry = re.match(rf"""\s*(?:(?:echo|printf)\s+)?["']?\s*\[?(?P<flag>{flag})(?:\]|\s|$)""", line.text)
    return re.search(rf"""(?<![\w-])(?P<flag>{flag})(?![\w-])""", line.text) if usage_line else help_entry


def iter_offers(lines: list[Line], flag: str, *, reject_ok: bool = False):
    """Lines where the script handles `flag` as an option: a case label, a comparison or a quoted literal.
    With reject_ok, a case arm whose whole body only refuses is not an offer, and a usage or help line
    that lists the flag as available is. Yields (line, matched flag) in file order."""
    label = re.compile(
        rf"""(?:^\s*|;;\s*|\bin\s+)(?:["']?[\w*.=-]+["']?\s*\|\s*)*["']?(?P<flag>{flag})["']?\s*(?:\|\s*["']?[\w*.=-]+["']?\s*)*\)(?P<rest>.*)$"""
    )
    compare = re.compile(rf"""(?:==?|!=)\s*["']?(?P<flag>{flag})["']?(?![\w-])""")
    quoted = re.compile(rf"""["'](?P<flag>{flag})["']""")
    skip_to = -1
    for index, line in enumerate(lines):
        if index <= skip_to:
            continue  # inside an arm that only refuses: its text is a refusal, not an offer
        match = label.search(line.text)
        if match:
            body, last = arm_body(lines, index, match.group("rest"))
            if reject_ok and only_refuses(body):
                skip_to = last
                continue
            yield line, match.group("flag")
            continue
        if reject_ok:
            match = lists_flag_as_available(line, flag)
            if match:
                yield line, match.group("flag")
                continue
        if is_message(line.text):
            continue
        match = compare.search(line.text) or quoted.search(line.text)
        if match:
            yield line, match.group("flag")


def find_offer(lines: list[Line], flag: str, *, reject_ok: bool = False) -> tuple[Line, str] | None:
    return next(iter_offers(lines, flag, reject_ok=reject_ok), None)


# ---- Entry points and release script ----

def entry(repo: Repo, unit: Path, check_id: str, name: str) -> Result:
    path = find_script(repo, unit, name)
    if path is None:
        if unit == repo.root:
            return Result(check_id, FAIL, f"scripts/{name} is missing")
        return Result(check_id, FAIL, f"{repo.rel(unit)}/scripts/{name} is missing, and so is scripts/{name} at the repository root")
    rel = repo.rel(path)
    if not os.access(path, os.X_OK):
        return Result(check_id, FAIL, f"{rel} exists but is not executable")
    return Result(check_id, PASS, f"{rel} is executable")


def no_script(check_id: str, heuristic: bool = False) -> Result:
    return Result(check_id, NA, "no scripts/release.sh to read", heuristic)


# Flags that turn off gates or verification as a class. Any other --skip-* or --no-* flag skips one named step.
BLANKET = (r"--(?:skip(?:-(?:checks?|gates?|tests?|verify|verification|validation|all))?"
           r"|no-(?:verify|checks?|gates?|tests?)|ignore-(?:gates?|checks?|failures?)|bypass(?:-[a-z0-9]+)*|unsafe)")
SPECIFIC = r"--(?:skip|no)-[a-z0-9][a-z0-9-]*"
SPECIFIC_NOTE = "specific skip flags; confirm none turns off a fixed guarantee (pushed source, promotion, recovery point, target parity, live proof)"


def check_mode(view: list[Line] | None) -> Result:
    if view is None:
        return no_script("release.check-mode")
    found = find_offer(view, r"--check")
    if found:
        return Result("release.check-mode", PASS, f"{found[0].where()} handles --check")
    return Result("release.check-mode", FAIL, "scripts/release.sh has no --check option")


def waivers(view: list[Line] | None) -> Result:
    if view is None:
        return no_script("release.waivers")
    blanket = find_offer(view, BLANKET, reject_ok=True)
    if blanket:
        return Result("release.waivers", FAIL, f"{blanket[0].where()} offers {blanket[1]}, a blanket bypass; offer --waive <gate>=<reason> instead")
    specific: dict[str, Line] = {}
    for line, flag in iter_offers(view, SPECIFIC, reject_ok=True):
        if not re.fullmatch(BLANKET, flag):
            specific.setdefault(flag, line)
    offers_waive = find_offer(view, r"--waive")
    if specific:
        flags = list(specific)
        shown = ", ".join(flags[:5]) + (f" and {len(flags) - 5} more" if len(flags) > 5 else "")
        missing = "" if offers_waive else "; no --waive either"
        return Result("release.waivers", WARN, f"{specific[flags[0]].where()} offers {shown}: {SPECIFIC_NOTE}{missing}", True)
    if offers_waive:
        return Result("release.waivers", PASS, f"{offers_waive[0].where()} offers --waive and no skip flag")
    return Result("release.waivers", WARN, "scripts/release.sh offers no --waive (and no blanket bypass either)")


def pushed_source(view: list[Line] | None) -> Result:
    if view is None:
        return no_script("release.pushed-source", True)
    pattern = re.compile(r"ls-remote\b.*(?:--symref|\bHEAD\b|refs/heads)|\bgit\s+remote\s+show\b")
    for line in view:
        if not is_message(line.text) and pattern.search(line.text):
            return Result("release.pushed-source", PASS, f"{line.where()} asks the remote for the default branch", True)
    return Result("release.pushed-source", FAIL, "scripts/release.sh never asks the remote for its default branch (git ls-remote ... HEAD)", True)


TAG_CREATE = re.compile(
    r"\bgit\b(?:\s+(?:-C\s+\S+|-c\s+\S+|--\S+))*\s+tag\s+(?!-[ldvn]\b|--(?:list|delete|verify)\b)[^\s|;&>)]|\bgh\s+release\s+create\b"
)
VERIFY_MENTION_AS_TEST = re.compile(r"(?:^|\s)-[a-zA-Z]\s+\S*verify-live|\b(?:chmod|ls|cat|stat)\b")


def tag_after_proof(view: list[Line] | None) -> Result:
    if view is None:
        return no_script("release.tag-after-proof", True)
    tag = next((i for i, l in enumerate(view) if not is_message(l.text) and TAG_CREATE.search(l.text)), None)
    proof = next((i for i, l in enumerate(view)
                  if "verify-live" in l.text and not is_message(l.text) and not VERIFY_MENTION_AS_TEST.search(l.text)), None)
    if tag is None:
        return Result("release.tag-after-proof", WARN, "no tag step found in scripts/release.sh", True)
    if proof is None:
        return Result("release.tag-after-proof", FAIL, f"{view[tag].where()} creates a tag and the script never calls verify-live", True)
    if tag < proof:
        return Result("release.tag-after-proof", FAIL, f"{view[tag].where()} creates a tag before verify-live is called at {view[proof].where()}", True)
    return Result("release.tag-after-proof", PASS, f"{view[tag].where()} tags after verify-live at {view[proof].where()}", True)


def evidence(view: list[Line] | None) -> Result:
    if view is None:
        return no_script("release.evidence")
    for line in view:
        if "release.json" in line.text:
            return Result("release.evidence", PASS, f"{line.where()} writes release.json")
    return Result("release.evidence", FAIL, "scripts/release.sh never writes release.json")


ROLLBACK = re.compile(r"\b(?:wrangler|npx|pnpm|bunx?|yarn|vercel|flyctl|fly|cf|kubectl|helm|docker|git)\b.*\brollback\b")
PRINTS = re.compile(r"\b(?:echo|printf|cat|print|console\.\w+)\b|>&2")


def rollback(view: list[Line] | None) -> Result:
    if view is None:
        return no_script("release.rollback", True)
    for line in view:
        if ROLLBACK.search(line.text) and PRINTS.search(line.text):
            return Result("release.rollback", PASS, f"{line.where()} prints a rollback command", True)
    return Result("release.rollback", FAIL, "scripts/release.sh never prints a rollback command", True)


def pins_in(repo: Repo, directory: Path) -> list[tuple[str, str, int | None]]:
    """(source name, path, line) for each runtime pin declared in one directory."""
    pins: list[tuple[str, str, int | None]] = []
    package = directory / "package.json"
    text = repo.read(package) if package.is_file() else None
    if text:
        try:
            data = json.loads(text)
        except ValueError:
            data = {}
        if isinstance(data, dict):
            if isinstance(data.get("packageManager"), str):
                pins.append(("packageManager", repo.rel(package), line_of(text, r'"packageManager"\s*:')))
            if isinstance(data.get("engines"), dict) and data["engines"]:
                pins.append(("engines", repo.rel(package), line_of(text, r'"engines"\s*:')))
    for name in (".nvmrc", ".tool-versions"):
        if (directory / name).is_file():
            pins.append((name, repo.rel(directory / name), 1))
    return pins


def declared_pins(repo: Repo, unit: Path) -> list[tuple[str, str, int | None]]:
    """The unit's own pin when it declares one; otherwise the repository root's."""
    return pins_in(repo, unit) or (pins_in(repo, repo.root) if unit != repo.root else [])


def runtime_pin(repo: Repo, unit: Path, view: list[Line] | None) -> Result:
    pins = declared_pins(repo, unit)
    if not pins:
        return Result("release.runtime-pin", FAIL, "no runtime pin declared (packageManager, .nvmrc, .tool-versions or engines)", True)
    declared = ", ".join(f"{name} ({path}:{no})" if no else f"{name} ({path})" for name, path, no in pins)
    if view is None:
        return Result("release.runtime-pin", NA, f"pin declared in {declared}; no scripts/release.sh to compare it", True)
    names = [name for name, _path, _no in pins]
    reads = next((l for l in view if not is_message(l.text) and any(name in l.text for name in names)), None)
    probes = next((l for l in view if re.search(r"--version|\bnode\s+-v\b|process\.version", l.text)), None)
    if reads and probes:
        return Result("release.runtime-pin", PASS, f"{reads.where()} reads the declared pin and {probes.where()} compares it with the running tool", True)
    return Result("release.runtime-pin", FAIL, f"pin declared in {declared} but scripts/release.sh never compares it with the running tools", True)


COMMENT_START = ("//", "#", "*", "/*", "<!--", "--")


def live_lines(text: str):
    """(line number, text) for lines that are not comment-only."""
    for no, raw in enumerate(text.splitlines(), 1):
        if raw.strip() and not raw.lstrip().startswith(COMMENT_START):
            yield no, raw


def served_commit(repo: Repo, unit: Path) -> Result:
    meta = re.compile(r"app-commit")
    key = re.compile(r"""["']?\bcommit\b["']?\s*[:=,}]""")
    handler = re.compile(r"health|[\"'`]/(?:api/)?version\b", re.I)
    health_file = None
    files = repo.source_files(APP_SUFFIXES, unit)
    for path in files:
        text = repo.read(path)
        if not text:
            continue
        lines = list(live_lines(text))
        for no, raw in lines:
            if meta.search(raw):
                return Result("served-commit", PASS, f"{repo.rel(path)}:{no} exposes app-commit", True)
        if health_file is None and any(handler.search(raw) for _no, raw in lines):
            for no, raw in lines:
                if key.search(raw):
                    health_file = f"{repo.rel(path)}:{no}"
                    break
    if health_file:
        return Result("served-commit", PASS, f"{health_file} reports a commit field in a health handler", True)
    where = "." if unit == repo.root else repo.rel(unit)
    return Result("served-commit", WARN,
                  f"no app-commit meta tag or health commit field found in {len(files)} application files under {where} "
                  "(code, index.html and HTML under src/, app/, pages/, public/, templates/, views/, web/ or client/; "
                  "documentation, tests and other HTML are not read)", True)


# ---- Wrangler ----

@dataclass
class WranglerConfig:
    path: str
    text: str
    data: dict


def line_of(text: str, pattern: str, start: int = 0, end: int | None = None) -> int | None:
    lines = text.splitlines()
    regex = re.compile(pattern)
    for index in range(start, len(lines) if end is None else min(end, len(lines))):
        if regex.search(lines[index]):
            return index + 1
    return None


def load_wrangler(repo: Repo, unit: Path) -> tuple[list[WranglerConfig], list[str]]:
    """The Wrangler configs in the unit's own directory (nested units are reported as units of their own)."""
    configs: list[WranglerConfig] = []
    errors: list[str] = []
    for name in ("wrangler.toml", "wrangler.jsonc", "wrangler.json"):
        path = unit / name
        if not path.is_file():
            continue
        text = repo.read(path)
        rel = repo.rel(path)
        if text is None:
            errors.append(f"{rel}: unreadable")
            continue
        try:
            data = tomllib.loads(text) if name.endswith(".toml") else json.loads(strip_jsonc(text))
        except (ValueError, tomllib.TOMLDecodeError) as error:
            errors.append(f"{rel}: cannot parse ({error})")
            continue
        if isinstance(data, dict):
            configs.append(WranglerConfig(rel, text, data))
    return configs, errors


def environments(config: WranglerConfig) -> dict:
    env = config.data.get("env")
    return {name: body if isinstance(body, dict) else {} for name, body in env.items()} if isinstance(env, dict) else {}


def key_line(config: WranglerConfig, key: str, env: str | None = None) -> int | None:
    text, toml = config.text, config.path.endswith(".toml")
    lines = text.splitlines()
    if toml:
        first_env = line_of(text, r"^\s*\[\[?env\.")
        if env is None:
            return line_of(text, rf"^\s*(?:\[\[?)?{re.escape(key)}\b", 0, (first_env - 1) if first_env else None)
        found = line_of(text, rf"^\s*\[\[?env\.{re.escape(env)}\.{re.escape(key)}\b")
        if found:
            return found
        header = line_of(text, rf"^\s*\[env\.{re.escape(env)}\]")
        if header:
            for index in range(header, len(lines)):
                if re.match(r"^\s*\[", lines[index]):
                    break
                if re.match(rf"^\s*{re.escape(key)}\s*=", lines[index]):
                    return index + 1
        return None
    env_start = line_of(text, r'"env"\s*:')
    if env is None:
        return line_of(text, rf'"{re.escape(key)}"\s*:', 0, (env_start - 1) if env_start else None)
    if env_start is None:
        return None
    own = line_of(text, rf'"{re.escape(env)}"\s*:', env_start)
    return line_of(text, rf'"{re.escape(key)}"\s*:', own) if own else None


def env_line(config: WranglerConfig, name: str | None = None) -> int | None:
    """The line of the `env` block, or of one environment's own block."""
    text = config.text
    if config.path.endswith(".toml"):
        if name is None:
            return line_of(text, r"^\s*\[\[?env\.")
        return line_of(text, rf"^\s*\[\[?env\.{re.escape(name)}[.\]]")
    start = line_of(text, r'"env"\s*:')
    if name is None or start is None:
        return start
    return line_of(text, rf'"{re.escape(name)}"\s*:', start) or start


def at(config: WranglerConfig, line: int | None) -> str:
    return f"{config.path}:{line}" if line else config.path


def worst(results: list[Result], check_id: str, empty: Result) -> Result:
    if not results:
        return empty
    top = max(results, key=lambda r: SEVERITY[r.status])
    return Result(check_id, top.status, top.evidence, top.heuristic)


def cf_targets(config: WranglerConfig) -> Result:
    envs = environments(config)
    if not envs:
        return Result("cf.targets", FAIL, f"{config.path} declares no environment: one deploy target, so no staging beside production")
    return Result("cf.targets", PASS, f"{at(config, env_line(config))} top level plus env {', '.join(envs)}")


def cf_routes(config: WranglerConfig) -> Result:
    top = [k for k in ("routes", "route") if k in config.data]
    if not top:
        return Result("cf.env-routes", PASS, f"{config.path} sets no top-level route; nothing to inherit")
    bad = [name for name, body in environments(config).items() if "route" not in body and "routes" not in body]
    if not bad:
        return Result("cf.env-routes", PASS, f"{config.path} gives every environment its own route")
    first = bad[0]
    return Result("cf.env-routes", FAIL,
                  f"{at(config, env_line(config, first))} env.{first} inherits {top[0]} from the top level ({at(config, key_line(config, top[0]))})"
                  + (f"; also {', '.join('env.' + n for n in bad[1:])}" if bad[1:] else ""))


def cf_triggers(config: WranglerConfig) -> Result:
    if "triggers" not in config.data:
        return Result("cf.env-triggers", PASS, f"{config.path} sets no top-level triggers; nothing to inherit")
    bad = [name for name, body in environments(config).items() if "triggers" not in body]
    if not bad:
        return Result("cf.env-triggers", PASS, f"{config.path} gives every environment its own triggers")
    return Result("cf.env-triggers", WARN,
                  f"{at(config, env_line(config, bad[0]))} env.{bad[0]} inherits triggers (cron schedules) from the top level ({at(config, key_line(config, 'triggers'))})"
                  + (f"; also {', '.join('env.' + n for n in bad[1:])}" if bad[1:] else ""))


def cf_bindings(config: WranglerConfig) -> Result:
    top_keys = [k for k in (*DOCUMENTED_NON_INHERITABLE, *UNLISTED_BINDINGS) if k in config.data]
    if not top_keys:
        return Result("cf.env-bindings", PASS, f"{config.path} sets no non-inheritable key at the top level")
    missing: list[tuple[str, str]] = []
    for name, body in environments(config).items():
        for key in top_keys:
            if key not in body:
                missing.append((name, key))
    if not missing:
        return Result("cf.env-bindings", PASS, f"{config.path} sets every top-level non-inheritable key in each environment")

    def describe(items: list[tuple[str, str]]) -> str:
        shown = [f"{at(config, env_line(config, name))} env.{name} omits {key} (top level: {at(config, key_line(config, key))})" for name, key in items[:2]]
        return "; ".join(shown) + (f"; and {len(items) - 2} more" if len(items) > 2 else "")

    failing = [m for m in missing if m[1] not in VALUE_KEYS]
    if failing:
        only_unlisted = all(key in UNLISTED_BINDINGS for _name, key in failing)
        note = " (not on the documented non-inheritable list; the reference says bindings are not inherited)" if only_unlisted else ""
        return Result("cf.env-bindings", FAIL, describe(failing) + note, only_unlisted)
    return Result("cf.env-bindings", WARN, describe(missing))


def cache_enabled(body: dict) -> bool:
    cache = body.get("cache")
    return isinstance(cache, dict) and cache.get("enabled") is True


def cf_cache(config: WranglerConfig) -> Result:
    """Workers Cache keys ignore Cookie and Authorization, so turning it on is a warning to read, not a fault.
    Whether environments inherit `cache` is unconfirmed in the Wrangler reference, so an environment that
    sets nothing next to a top-level true is not counted: the evidence only says it may inherit."""
    envs = environments(config)
    targets: list[tuple[str, int | None]] = []
    if cache_enabled(config.data):
        targets.append(("the top level", key_line(config, "cache")))
    targets += [(f"env.{name}", key_line(config, "cache", name)) for name, body in envs.items() if cache_enabled(body)]
    if not targets:
        return Result("cf.worker-cache", PASS, f"Workers Cache is off or absent in {config.path}")
    names = " and ".join(name for name, _line in targets)
    note = ""
    if cache_enabled(config.data) and any("cache" not in body for body in envs.values()):
        note = "; environments may inherit it"
    return Result("cf.worker-cache", WARN,
                  f"{at(config, targets[0][1])} Workers Cache is on for {names}; its key ignores Cookie and Authorization, "
                  f"so every response that depends on them must be private, no-store{note}")


def cloudflare(repo: Repo, unit: Path) -> list[Result]:
    configs, errors = load_wrangler(repo, unit)
    ids = ("cf.targets", "cf.env-routes", "cf.env-triggers", "cf.env-bindings", "cf.worker-cache")
    if errors and not configs:
        return [Result(i, WARN, errors[0]) for i in ids]
    if not configs:
        return [Result(i, NA, "no wrangler.toml, wrangler.json or wrangler.jsonc") for i in ids]
    empty = Result("", NA, "")
    out = [worst([cf_targets(c) for c in configs], "cf.targets", empty),
           worst([cf_routes(c) for c in configs], "cf.env-routes", empty),
           worst([cf_triggers(c) for c in configs], "cf.env-triggers", empty),
           worst([cf_bindings(c) for c in configs], "cf.env-bindings", empty),
           worst([cf_cache(c) for c in configs], "cf.worker-cache", empty)]
    if errors:
        out = [Result(r.id, r.status, f"{r.evidence} (unparsed: {errors[0]})", r.heuristic) for r in out]
    return out


def workers_dev_origin(repo: Repo, unit: Path) -> Result:
    pattern = re.compile(r"https?://[A-Za-z0-9._-]*\.workers\.dev\b")
    hits: list[str] = []
    for path in repo.source_files(APP_SUFFIXES | CONFIG_SUFFIXES, unit):
        text = repo.read(path)
        if not text or ".workers.dev" not in text:
            continue
        for no, raw in live_lines(text):
            if pattern.search(raw):
                hits.append(f"{repo.rel(path)}:{no}")
    if not hits:
        return Result("cf.workers-dev-origin", PASS, "no hard-coded workers.dev URL in source or config", True)
    more = f" (+{len(hits) - 1} more)" if len(hits) > 1 else ""
    return Result("cf.workers-dev-origin", WARN, f"{hits[0]} hard-codes a workers.dev origin{more}; use the environment's own hostname", True)


# ---- Guardrails ----

def guardrail_local(repo: Repo) -> Result:
    for rel in (".githooks/pre-commit", ".husky/pre-commit"):
        if (repo.root / rel).is_file():
            return Result("guardrail.local", PASS, f"{rel} exists")
    return Result("guardrail.local", FAIL, "no pre-commit in .githooks/ or .husky/")


def guardrail_ci(repo: Repo) -> Result:
    workflows = repo.root / ".github" / "workflows"
    found = sorted(p for p in workflows.glob("*.y*ml")) if workflows.is_dir() else []
    if found:
        return Result("guardrail.ci", WARN, f"{repo.rel(found[0])} present ({len(found)} workflow file(s)), not proven to run")
    for rel in (".gitlab-ci.yml", ".circleci/config.yml"):
        if (repo.root / rel).is_file():
            return Result("guardrail.ci", WARN, f"{rel} present, not proven to run")
    return Result("guardrail.ci", NA, "no CI workflow files")


# ---- Running ----

def check_unit(repo: Repo, unit: Path) -> list[Result]:
    """Checks for one deployable unit of a repository: the repository root itself, or a directory below it.
    Wrangler checks, source searches and the pin read the unit; scripts are looked up in the unit first and
    then at the repository root; guardrails always read the repository root."""
    view = release_view(repo, find_script(repo, unit, "release.sh"))
    cf = cloudflare(repo, unit)
    results = [
        entry(repo, unit, "entry.release", "release.sh"),
        entry(repo, unit, "entry.verify-live", "verify-live.sh"),
        check_mode(view), waivers(view), pushed_source(view), tag_after_proof(view), evidence(view), rollback(view),
        runtime_pin(repo, unit, view), served_commit(repo, unit), *cf,
        workers_dev_origin(repo, unit), guardrail_local(repo), guardrail_ci(repo),
    ]
    assert tuple(r.id for r in results) == IDS, "check order drifted from IDS"
    return results


def summarize(results: list[Result]) -> dict[str, int]:
    return {s.lower(): sum(1 for r in results if r.status == s) for s in (PASS, FAIL, WARN, NA)}


def render_repo(label: str, path: Path, results: list[Result]) -> str:
    lines = [f"== {label} ({path})"]
    for r in results:
        label = " [heuristic]" if r.heuristic else ""
        lines.append(f"{r.status:<4}  {r.id}{label}  {' '.join(r.evidence.split())}")
    s = summarize(results)
    lines.append(f"{s['pass']} pass, {s['fail']} fail, {s['warn']} warn, {s['na']} n/a")
    return "\n".join(lines)


def is_deployable(directory: Path) -> bool:
    try:
        names = {p.name for p in directory.iterdir()}
    except OSError:
        return False
    return bool(
        names & {"wrangler.toml", "wrangler.json", "wrangler.jsonc", "Dockerfile"}
        or any(re.fullmatch(r"(?:docker-)?compose(?:\..+)?\.ya?ml", n) for n in names)
    )


UNIT_DEPTH = 3


def find_units(root: Path) -> list[Path]:
    """Deployable directories in a repository: the root and up to three levels below it."""
    units: list[Path] = []
    for dirpath, dirnames, _files in os.walk(root):
        here = Path(dirpath)
        depth = len(here.relative_to(root).parts)
        dirnames[:] = sorted(
            d for d in dirnames if d not in SKIP_DIRS and d not in TEST_DIRS and not d.startswith(".")
        ) if depth < UNIT_DEPTH else []
        if is_deployable(here):
            units.append(here)
    return units


def repo_root_of(path: Path) -> Path:
    """The nearest directory at or above `path` that holds a .git; the path itself when none does."""
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    return path


def label_of(root: Path, unit: Path) -> str:
    return root.name if unit == root else f"{root.name}/{unit.relative_to(root).as_posix()}"


@dataclass(frozen=True)
class Target:
    root: Path
    unit: Path
    shown: Path

    @property
    def label(self) -> str:
        return label_of(self.root, self.unit)


def targets_for_repo(arg: str) -> list[Target]:
    """A path given as <repo>: a nested unit is one target; a repository root expands to its units."""
    given = Path(arg)
    path = given.resolve()
    root = repo_root_of(path)
    if path != root:
        return [Target(root, path, given)]
    units = find_units(root) or [root]
    return [Target(root, unit, given / unit.relative_to(root)) for unit in units]


def targets_for_fleet(directory: str) -> list[Target]:
    fleet = Path(directory)
    found: list[Target] = []
    for child in sorted((p for p in fleet.iterdir() if p.is_dir() and not p.name.startswith(".") and p.name not in SKIP_DIRS),
                        key=lambda p: p.name):
        root = child.resolve()
        found += [Target(root, unit, child / unit.relative_to(root)) for unit in find_units(root)]
    return sorted(found, key=lambda t: t.label)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="release-contract-check.py", allow_abbrev=False,
        usage="release-contract-check.py <repo>... [--json] | --fleet <dir> [--json]",
        description="Read-only conformance report for references/release-contract.md.",
    )
    parser.add_argument("repos", nargs="*", metavar="repo")
    parser.add_argument("--fleet", metavar="dir", help="check every child directory that has a Wrangler config, Dockerfile or Compose file")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)
    if args.fleet and args.repos:
        parser.error("--fleet takes a directory and no repositories")
    if not args.fleet and not args.repos:
        parser.error("give at least one repository, or --fleet <dir>")
    for target in ([args.fleet] if args.fleet else args.repos):
        if not Path(target).is_dir():
            parser.error(f"not a directory: {target}")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    targets = targets_for_fleet(args.fleet) if args.fleet else [t for repo in args.repos for t in targets_for_repo(repo)]
    repos: dict[Path, Repo] = {}
    reports = [(t, check_unit(repos.setdefault(t.root, Repo(t.root)), t.unit)) for t in targets]
    any_fail = any(r.status == FAIL for _t, results in reports for r in results)

    if args.json:
        payload: dict = {"repos": [
            {"path": str(t.shown), "unit": t.label, "checks": [r.as_dict() for r in results], "summary": summarize(results)}
            for t, results in reports]}
        if args.fleet:
            payload["fleet"] = args.fleet
        payload["summary"] = summarize([r for _t, results in reports for r in results])
        print(json.dumps(payload, indent=2))
    elif args.fleet:
        if not reports:
            print(f"no deployable child directories (Wrangler config, Dockerfile or Compose file) in {args.fleet}")
        else:
            width = max(len(t.label) for t, _ in reports)
            print(f"fleet: {args.fleet} ({len(reports)} units)")
            for t, results in reports:
                print(f"{t.label:<{width}}  {''.join(SYMBOL[r.status] for r in results)}")
            print("legend: P=pass F=fail W=warn -=n/a; columns in order: " + ", ".join(IDS))
    else:
        print("\n\n".join(render_repo(t.label, t.shown, results) for t, results in reports))
    return 1 if any_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
