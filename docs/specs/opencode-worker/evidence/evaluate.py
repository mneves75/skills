#!/usr/bin/env python3
"""Grade one benchmark worktree after the worker finished.

usage: evaluate.py <task t1..t4> <worktree> <scratch_root>
Prints changed files, protected-file integrity, gate exit codes and hidden-test results.
Hidden tests are copied in only now and removed afterwards.
"""
import os
import re
import shutil
import subprocess
import sys

task, wt, root = sys.argv[1], os.path.realpath(sys.argv[2]), sys.argv[3]
tools = os.path.join(wt, "tools")
env = dict(os.environ, PWD=tools)


def run(cmd, cwd, shell=False):
    p = subprocess.run(cmd, cwd=cwd, env=dict(env, PWD=cwd), capture_output=True, text=True, shell=shell)
    return p.returncode, (p.stdout + p.stderr)


def tail_counts(text):
    m = re.findall(r"^\s*(\d+) (pass|fail)\s*$", text, re.M)
    return " ".join(f"{n} {k}" for n, k in m) or text.strip().splitlines()[-1:] if text.strip() else ""


_, status = run(["git", "status", "--short", "--untracked-files=all"], wt)
print("STATUS:", " | ".join(l for l in status.splitlines() if "node_modules" not in l) or "(clean)")
_, unstaged = run(["git", "diff", "--stat"], wt)
print("UNSTAGED DIFF:", unstaged.strip().replace("\n", " | ") or "(none)")

fixtures = {"t1": "tools/lib/cli.test.ts", "t4": "tools/lib/cli.conflict.test.ts"}
if task in fixtures:
    rel = fixtures[task]
    src = os.path.join(root, "bench/fixtures", task, os.path.basename(rel))
    same = open(src).read() == open(os.path.join(wt, rel)).read()
    print("PROTECTED TEST UNCHANGED:", same)

if task == "t3":
    _, hits = run("rg -n '\\bCheckResultWithMeta\\b' tools --glob '!node_modules'", wt, shell=True)
    print("OLD NAME HITS:", hits.strip() or "0")
    _, files = run(["git", "diff", "--name-only"], wt)
    pure = True
    for f in files.split():
        _, orig = run(["git", "show", f"HEAD:{f}"], wt)
        new = open(os.path.join(wt, f)).read()
        if new.replace("CheckOutcome", "CheckResultWithMeta") != orig:
            pure = False
            print("  NOT A PURE RENAME:", f)
    print("PURE RENAME:", pure, "files:", files.split())

for name, cmd, cwd in [
    ("bun test lib/", ["bun", "test", "lib/"], tools),
    ("typecheck", ["bun", "run", "typecheck"], tools),
    ("lint", ["bun", "run", "lint"], tools),
    ("ast-grep", ["ast-grep", "scan", "--config", "sgconfig.yml", "."], wt),
    ("help", ["bun", "--bun", "readiness-check.ts", "--help"], tools),
]:
    rc, out = run(cmd, cwd)
    extra = tail_counts(out) if name.startswith("bun test") else ""
    print(f"GATE {name}: rc={rc} {extra}")

hidden = os.path.join(root, "bench/hidden", f"{task}.hidden.test.ts")
if os.path.exists(hidden):
    dst = os.path.join(tools, "lib", f"{task}.hidden.test.ts")
    shutil.copy(hidden, dst)
    try:
        rc, out = run(["bun", "test", f"lib/{task}.hidden.test.ts"], tools)
        fails = [l.strip() for l in out.splitlines() if l.strip().startswith("(fail)")]
        print(f"HIDDEN: rc={rc} {tail_counts(out)}", *fails, sep="\n  ")
    finally:
        os.remove(dst)
