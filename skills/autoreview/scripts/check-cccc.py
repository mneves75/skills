#!/usr/bin/env python3
"""Real cccc CLI controls against disposable inputs. Python 3.10+, standard library."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile


def require(condition: bool, evidence) -> None:
    if not condition:
        raise RuntimeError(f"cccc control failed: {evidence}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    args = parser.parse_args()
    binary = str(args.binary.resolve(strict=True))
    pin = json.loads(Path(__file__).with_name("cccc-release.json").read_text())
    version = subprocess.run([binary, "--version"], check=True, text=True,
                             capture_output=True, timeout=15)
    require(version.stdout.strip() == f"cccc {pin['version']}", version.stdout)
    with tempfile.TemporaryDirectory(prefix="cccc-controls.") as temporary:
        root = Path(temporary)
        source = root / "simple.ts"
        source.write_text("function choose(value: boolean) { if (value) return 1; return 0; }\n")
        broken = root / "broken.py"
        broken.write_text("def broken(:\n    return 1\n")
        empty = root / "empty"
        empty.mkdir()

        def run(path, *flags):
            result = subprocess.run([binary, "--no-config", "--no-cache", "--min", "0",
                                     *flags, str(path)], cwd=root, text=True,
                                    capture_output=True, timeout=15)
            document = json.loads(result.stdout) if result.stdout.strip() else None
            return result, document

        result, report = run(source)
        require(result.returncode == 0 and not result.stderr, result)
        require(report is not None, result)
        require(report["summary"]["file_count"] == 1, report)
        require(report["summary"]["function_count"] == 1, report)
        require(report["summary"]["parse_error_count"] == 0, report)
        function = report["files"][0]["functions"][0]
        require((function["cognitive"], function["cyclomatic"]) == (1, 2), function)
        print("PASS: known function, cognitive=1, cyclomatic=2, complete JSON coverage")
        result, report = run(source, "--max-cognitive", "0")
        require(result.returncode == 1, result)
        require(report is not None, result)
        require(report["summary"]["file_count"] == 1 and
                report["summary"]["function_count"] == 1 and
                report["summary"]["parse_error_count"] == 0, report)
        function = report["files"][0]["functions"][0]
        require((function["cognitive"], function["cyclomatic"]) == (1, 2), function)
        print("PASS: existing threshold breach preserves status 1 and JSON")
        result, report = run(broken)
        require(report is not None and report["summary"]["parse_error_count"] > 0, report)
        print(f"PASS: malformed source exposes parse errors even with status {result.returncode}")
        result, report = run(empty)
        require(report is None and result.stderr, result)
        print(f"PASS: empty scan detectable despite status {result.returncode}")
        result, report = run(root / "absent.ts")
        require(bool(result.stderr) and report is None, result)
        print(f"PASS: nonexistent input detectable despite status {result.returncode}")
        (root / "cccc.toml").write_text("table = true\nmin = 100\ncache = true\n")
        result = subprocess.run([binary, "--no-cache", "--min", "0", str(source)], cwd=root,
                                text=True, capture_output=True, timeout=15)
        require(result.returncode == 0 and "choose" in result.stdout, result)
        require(not (root / ".cccc.cache").exists(), "Review created a cache")
        try:
            json.loads(result.stdout)
        except json.JSONDecodeError:
            print("PASS: table config preserved, min overridden, cache disabled")
        else:
            raise AssertionError("Expected table config to prevent JSON")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
