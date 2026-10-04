#!/usr/bin/env bash
# Vendor the pstack skills from a pstack-claude checkout into collections/pstack.
#
#   tools/scripts/sync-pstack.sh <pstack-claude-repo> <ref> [dest]
#
# Copies only files tracked at <ref> (git archive), so a local node_modules or
# scratch file never ships. Moves frontmatter keys outside the Agent Skills spec
# under `metadata:` so every agent that follows the spec can load the skill.
# A fork's own commits ship as <dest>/local-overrides.patch, so the collection
# can be rebuilt from the published commit named in UPSTREAM.
# Owns <dest>/skills, <dest>/UPSTREAM, <dest>/LICENSE and <dest>/local-overrides.patch;
# other files in <dest> are hand-written and left alone. Validates before
# replacing, so a failed run leaves the collection unchanged.
#
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Marcus Neves
set -euo pipefail

[ $# -ge 2 ] || { echo "usage: $0 <pstack-claude-repo> <ref> [dest]" >&2; exit 2; }
src=$1
ref=$2
repo_root=$(cd "$(dirname "$0")/../.." && pwd)
dest=${3:-$repo_root/collections/pstack}

sha=$(git -C "$src" rev-parse --verify --quiet "$ref^{commit}") || { echo "unknown ref: $ref" >&2; exit 1; }
git -C "$src" cat-file -e "$sha:plugins/pstack/skills" 2>/dev/null || { echo "$sha has no plugins/pstack/skills" >&2; exit 1; }

# Stage beside the destination so the final moves are renames on one filesystem.
mkdir -p "$(dirname "$dest")"
stage=$(mktemp -d "$(dirname "$dest")/.sync-pstack.XXXXXX")
trap 'rm -rf "$stage"' EXIT
mkdir -p "$stage/skills"
git -C "$src" archive "$sha" plugins/pstack/skills | tar -x -C "$stage/skills" --strip-components=3

python3 - "$stage/skills" <<'PY'
# Python 3.6+ (f-strings), standard library only.
import json, os, re, sys

SPEC = {"name", "description", "license", "compatibility", "allowed-tools", "metadata"}
root = sys.argv[1]
errors = []
for name in sorted(os.listdir(root)):
    path = os.path.join(root, name, "SKILL.md")
    if not os.path.isfile(path):
        continue
    text = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append(f"{name}: no frontmatter")
        continue
    entries = []  # [key, [lines]]
    for line in m.group(1).split("\n"):
        km = re.match(r"([A-Za-z0-9_-]+):(.*)$", line)
        if km and not line.startswith((" ", "\t")):
            entries.append([km.group(1), [line]])
        elif entries:
            entries[-1][1].append(line)
        else:
            errors.append(f"{name}: unparseable frontmatter line {line!r}")
    if not any(k == "name" and lines[0] == f"name: {name}" for k, lines in entries):
        errors.append(f"{name}: frontmatter name must equal the directory name")
    moved = []
    kept = []
    for key, lines in entries:
        if key in SPEC:
            kept.append([key, lines])
            continue
        if len(lines) != 1:
            errors.append(f"{name}: non-spec key {key!r} spans several lines")
            continue
        value = lines[0].split(":", 1)[1].strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        moved.append(f"  {key}: {json.dumps(value)}")
    if not moved:
        continue
    meta = next((e for e in kept if e[0] == "metadata"), None)
    if meta is None:
        kept.append(["metadata", ["metadata:"] + moved])
    elif meta[1][0].strip() != "metadata:":
        errors.append(f"{name}: flow-style metadata cannot take moved keys")
        continue
    else:
        meta[1].extend(moved)
    head = "\n".join(line for _, lines in kept for line in lines)
    open(path, "w", encoding="utf-8").write(f"---\n{head}\n---\n" + text[m.end():])
if errors:
    sys.exit("\n".join(errors))
PY

git -C "$src" show "$sha:LICENSE" > "$stage/LICENSE"
version=$(git -C "$src" show "$sha:plugins/pstack/.claude-plugin/plugin.json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["version"])')
# UPSTREAM is published: keep only an http(s) URL, without credentials.
origin=$(git -C "$src" remote get-url origin 2>/dev/null || true)
origin=$(printf '%s' "$origin" | sed -nE 's#^(https?://)([^/@]*@)?(.+)$#\1\3#p')
[ -n "$origin" ] || origin=local
# A fork's own commits exist only locally, so name the published commit they sit on.
base=$sha
for published in refs/remotes/origin/HEAD refs/remotes/origin/main; do
  if git -C "$src" rev-parse --verify --quiet "$published" >/dev/null; then
    base=$(git -C "$src" merge-base "$sha" "$published")
    break
  fi
done
local_commits=$(git -C "$src" rev-list --count "$base..$sha")
printf 'source: %s\ncommit: %s\nbased-on: %s\nlocal-commits: %s\nversion: %s\n' \
  "$origin" "$sha" "$base" "$local_commits" "$version" > "$stage/UPSTREAM"
if [ "$local_commits" -gt 0 ]; then
  git -C "$src" diff --binary "$base" "$sha" -- plugins/pstack/skills > "$stage/local-overrides.patch"
fi

mkdir -p "$dest"
rm -rf "$dest/skills" "$dest/local-overrides.patch"
mv "$stage/skills" "$dest/skills"
mv "$stage/LICENSE" "$stage/UPSTREAM" "$dest/"
[ ! -e "$stage/local-overrides.patch" ] || mv "$stage/local-overrides.patch" "$dest/"
echo "synced $(find "$dest/skills" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ') skills from $sha ($version) into $dest"
