#!/usr/bin/env bash
# One-command, idempotent setup of this repository's development tools.
#
#   tools/scripts/init.sh           install what is missing, report what is present
#   tools/scripts/init.sh --check   report only; install nothing (exit 1 names a missing program)
#
# It installs two things, both inside the repository:
#   tools/node_modules      the locked dev tools (Biome, TypeScript, ast-grep, marked): `bun install --frozen-lockfile`
#   .scratch/skills-ref     the Agent Skills reference validator (`agentskills`), from the hashed requirements file
# and reports the host programs the gates need. Required: git, bun, node, and `python3` at 3.11 or later (the command the scripts run).
# Optional (named when absent, never installed): ffmpeg, ffprobe, gh, gitleaks, cccc, python3.11.
# Nothing is written outside the repository. Run it from any directory; it finds the repository root itself.
set -euo pipefail

# The usage is the file's leading comment block, which ends where the code starts, so it cannot drift.
usage() { sed -n -e '1d' -e '/^[^#]/q' -e 'p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//' >&2; exit 2; }
check=0
case $# in
  0) ;;
  1) [ "$1" = --check ] || usage; check=1 ;;
  *) usage ;;
esac

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)
cd "$root"
[ -f AGENTS.md ] && [ -d tools ] && [ -f .github/requirements/skills-ref.txt ] \
  || { echo "init.sh: $root is not the mneves-skills repository root" >&2; exit 2; }

missing=0
report() { printf '%-8s %-11s %s\n' "$1" "$2" "$3"; }
need() {
  local program=$1 hint=$2
  if command -v "$program" >/dev/null 2>&1; then report ok "$program" "$(command -v "$program")"
  else report missing "$program" "$hint"; missing=1; fi
}
optional() {
  local program=$1 hint=$2
  if command -v "$program" >/dev/null 2>&1; then report ok "$program" "$(command -v "$program")"
  else report absent "$program" "optional: $hint"; fi
}

# The gates, deploy.sh and the helpers invoke `python3` itself, so that command must meet the 3.11 floor;
# a separate `python3.11` does not help a script that calls `python3`.
python=""
if command -v python3 >/dev/null 2>&1 \
   && python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
  python=$(command -v python3)
fi
if [ -n "$python" ]; then report ok "python3 (3.11+)" "$python"; else report missing "python3 (3.11+)" "python3 must be 3.11 or later (python.org, Homebrew or uv); a python3.11 alias is not enough"; missing=1; fi

need git "git-scm.com"
need bun "https://bun.sh (the tools/ lockfile is Bun's)"
need node "Node 22+ (site build and the security-audit validators)"
optional ffmpeg "motion-film checks and tests"
optional ffprobe "motion-film checks and tests"
optional gh "GitHub reads and tools/scripts/deploy.sh"
optional gitleaks "the security gate's redacted secret scan"
optional cccc "optional complexity evidence in reviews"
optional python3.11 "the ship-deploy floor compile check"

[ "$missing" -eq 0 ] || { echo "init.sh: install the missing programs above, then run it again" >&2; exit 1; }

state_tools="absent"; [ -x tools/node_modules/.bin/biome ] && state_tools="present"
state_ref="absent"; [ -x .scratch/skills-ref/bin/agentskills ] && state_ref="present"
if [ "$check" -eq 1 ]; then
  report "$state_tools" "tools/" "tools/node_modules (bun install --frozen-lockfile)"
  report "$state_ref" "validator" ".scratch/skills-ref/bin/agentskills"
  exit 0
fi

(cd tools && bun install --frozen-lockfile)
if [ "$state_ref" = absent ]; then
  "$python" -m venv .scratch/skills-ref
  .scratch/skills-ref/bin/pip install --quiet --require-hashes -r .github/requirements/skills-ref.txt
fi
report ok tools/ "tools/node_modules ($(tools/node_modules/.bin/biome --version 2>/dev/null | head -1))"
report ok validator ".scratch/skills-ref/bin/agentskills ($(.scratch/skills-ref/bin/agentskills --version 2>/dev/null | head -1))"
echo "ready: run the gates with the commands in AGENTS.md (Commands); add .scratch/skills-ref/bin to PATH for agentskills"
