#!/usr/bin/env bash
# Proves tools/scripts/deploy.sh without GitHub, Pages or a network: a throwaway repository with a local
# bare remote stands in for origin, a fake `gh` answers from state files and performs the merge in a
# second clone, and a fake `curl` serves bodies from files. The script under test is the real one.
# Usage: bash tools/scripts/deploy.test.sh   (bash 3.2+, git, python3, shasum)
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# DEPLOY_SH points the suite at another copy of the script (a control against a previous version).
script="${DEPLOY_SH:-$here/deploy.sh}"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/deploy-test.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=test GIT_AUTHOR_EMAIL=test@example.invalid GIT_COMMITTER_NAME=test GIT_COMMITTER_EMAIL=test@example.invalid
pass=0; fail=0
ok() { echo "PASS $1"; pass=$((pass + 1)); }
bad() { echo "FAIL $1"; fail=$((fail + 1)); }

export FAKE_STATE="$tmp/state" FAKE_WEB="$tmp/web"
mkdir -p "$tmp/bin" "$FAKE_STATE" "$FAKE_WEB"
# Fixture dates come from the clock, so the suite does not start failing on a calendar day.
future=$(python3 -I -c 'import datetime; print((datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=400)).strftime("%Y-%m-%dT%H:%M:%SZ"))')
soon=$(python3 -I -c 'import datetime; print((datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"))')
past=$(python3 -I -c 'import datetime; print((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"))')

# ---- Fake gh: pr view / pr merge / run list, driven by $FAKE_STATE ----
cat > "$tmp/bin/gh" <<'FAKE'
#!/bin/bash
set -e
echo "gh $*" >> "$FAKE_STATE/calls"
case "$1 $2" in
  "pr view")
    if [[ "$*" == *"--json mergeCommit"* ]]; then
      if [ -f "$FAKE_STATE/merge" ]; then cat "$FAKE_STATE/merge"; else echo null; fi; exit 0
    fi
    cat "$FAKE_STATE/pr.json" ;;
  "pr merge")
    [[ "$*" == *"--match-head-commit $(cat "$FAKE_STATE/head")"* ]] || { echo "head moved" >&2; exit 1; }
    git -C "$FAKE_STATE/merger" checkout -q main
    git -C "$FAKE_STATE/merger" merge -q --no-ff -m "Merge pull request #7 from test/release/9.9.9" "origin/$(cat "$FAKE_STATE/head_ref")"
    git -C "$FAKE_STATE/merger" push -q origin main
    git -C "$FAKE_STATE/merger" rev-parse HEAD > "$FAKE_STATE/merge" ;;
  "run list")
    # The real gh applies --jq itself; the fake keeps the state files in the shape the --jq yields.
    if [[ "$*" == *"--workflow ci.yml"* ]]; then cat "$FAKE_STATE/ci"; else cat "$FAKE_STATE/pages"; fi ;;
  *) echo "fake gh: unexpected $*" >&2; exit 97 ;;
esac
FAKE
# ---- Fake curl: serves $FAKE_WEB/<path> for .../<path>?v=... ----
cat > "$tmp/bin/curl" <<'FAKE'
#!/bin/bash
url="${@: -1}"
path="${url#*://example.test/skills/}"
path="${path%%\?*}"
[ -f "$FAKE_WEB/$path" ] || { echo "fake curl: no $path" >&2; exit 22; }
cat "$FAKE_WEB/$path"
FAKE
chmod +x "$tmp/bin/gh" "$tmp/bin/curl"
export PATH="$tmp/bin:$PATH"

# ---- Throwaway repository: main, a release branch, records for its head ----
make_repo() {
  rm -rf "$tmp/bare" "$tmp/work" "$FAKE_STATE/merger" "$FAKE_STATE"/merge "$FAKE_STATE"/calls
  git init -q --bare -b main "$tmp/bare"
  git init -q -b main "$tmp/work"
  (
    cd "$tmp/work"
    mkdir -p site tools/scripts .scratch
    echo "9.9.8" > VERSION
    printf '# Changelog\n\n## [9.9.8] - 2026-01-01\n\n- old\n' > CHANGELOG.md
    printf '![Version](https://img.shields.io/badge/version-9.9.8-blue)\n' > README.md
    echo "<h1>old</h1>" > site/index.html
    echo "<p>guide</p>" > site/howto.html
    git add . && git commit -q -m "9.9.8"
    git remote add origin "$tmp/bare" && git push -q -u origin main
    git checkout -q -b release/9.9.9
    echo "9.9.9" > VERSION
    printf '# Changelog\n\n## [9.9.9] - 2026-11-04\n\nShips the thing.\nAnd proves it.\n\n### Changed\n- new\n\n## [9.9.8] - 2026-01-01\n\n- old\n' > CHANGELOG.md
    printf '![Version](https://img.shields.io/badge/version-9.9.9-blue)\n' > README.md
    echo "<h1>new</h1>" > site/index.html
    git add . && git commit -q -m "9.9.9" && git push -q -u origin release/9.9.9
    git checkout -q main
  )
  git clone -q "$tmp/bare" "$FAKE_STATE/merger"
  head=$(git -C "$tmp/work" rev-parse release/9.9.9)
  tree=$(git -C "$tmp/work" rev-parse "release/9.9.9^{tree}")
  echo "$head" > "$FAKE_STATE/head"; echo "release/9.9.9" > "$FAKE_STATE/head_ref"
  cat > "$FAKE_STATE/pr.json" <<JSON
{"state":"OPEN","headRefOid":"$head","headRefName":"release/9.9.9","baseRefName":"main","mergeable":"MERGEABLE","title":"release 9.9.9"}
JSON
  echo '1001 completed success' > "$FAKE_STATE/ci"
  echo '2002 completed success' > "$FAKE_STATE/pages"
  mkdir -p "$tmp/work/.scratch/security-gate/$head" "$tmp/work/.scratch/readiness/$head"
  cat > "$tmp/work/.scratch/security-gate/$head/production.json" <<JSON
{"schema":1,"unit":".","target":"production","commit":"$head","tree":"$tree","verdict":"waived","open_blockers":0,"blockers":"","independent_acceptance":"pass","created_at":"2026-11-04T00:00:00Z","waivers":[{"id":"SEC-15","owner":"@owner","reason":"r","expires":"$future"},{"id":"CMP-06","owner":"@owner","reason":"r","expires":"$future"}]}
JSON
  cat > "$tmp/work/.scratch/readiness/$head/production.json" <<JSON
{"schema":1,"unit":".","target":"production","catalog":3,"commit":"$head","tree":"$tree","verdict":"ready","open_blockers":0,"created_at":"2026-11-04T00:00:00Z","valid_until":"$soon","waivers":[{"id":"DEL-04","owner":"@owner","expires":"$future"}]}
JSON
  # The fake site serves the release bytes.
  mkdir -p "$FAKE_WEB"; echo "<h1>new</h1>" > "$FAKE_WEB/index.html"; echo "<p>guide</p>" > "$FAKE_WEB/howto.html"
}
run_deploy() { (cd "$tmp/work" && DEPLOY_REPO=test/skills DEPLOY_SITE_URL=https://example.test/skills DEPLOY_POLL_SECONDS=0 DEPLOY_TIMEOUT_SECONDS=5 DEPLOY_SERVE_ATTEMPTS=2 bash "$script" "$@" 2>&1); }

# 1. Dry run: plan and tag message, no merge call.
make_repo
out=$(run_deploy 7 --dry-run) && code=0 || code=$?
if [ "$code" -eq 0 ] && grep -q 'dry run: would check the merge tree against origin/main, merge PR #7' <<<"$out" && grep -q 'Security gate: WAIVED (SEC-15, CMP-06)' <<<"$out" && ! grep -q 'gh pr merge' "$FAKE_STATE/calls"; then
  ok "dry run prints the plan and tag message and merges nothing"
else bad "dry run (exit $code): $out"; fi

# 2. No security record for the tree: refused before any merge.
make_repo; rm "$tmp/work/.scratch/security-gate/$(cat "$FAKE_STATE/head")/production.json"
out=$(run_deploy 7) && code=0 || code=$?
if [ "$code" -eq 1 ] && grep -q 'no production security-gate record for tree' <<<"$out" && ! grep -q 'gh pr merge' "$FAKE_STATE/calls"; then
  ok "missing security record refuses before merging"
else bad "missing security record (exit $code): $out"; fi

# 3. A security record whose tree is another tree: refused.
make_repo; python3 -I - "$tmp/work/.scratch/security-gate/$(cat "$FAKE_STATE/head")/production.json" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p)); d["tree"] = "0" * 40; json.dump(d, open(p, "w"))
PY
out=$(run_deploy 7) && code=0 || code=$?
if [ "$code" -eq 1 ] && grep -q 'no production security-gate record for tree' <<<"$out"; then ok "a record for another tree does not count"
else bad "other-tree record (exit $code): $out"; fi

# 4. Readiness not ready: refused.
make_repo; python3 -I - "$tmp/work/.scratch/readiness/$(cat "$FAKE_STATE/head")/production.json" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p)); d["verdict"] = "not-ready"; d["open_blockers"] = 2; json.dump(d, open(p, "w"))
PY
out=$(run_deploy 7) && code=0 || code=$?
if [ "$code" -eq 1 ] && grep -q "readiness verdict is 'not-ready'" <<<"$out"; then ok "readiness not ready refuses"
else bad "readiness not ready (exit $code): $out"; fi

# 5. CHANGELOG top entry behind VERSION: refused.
make_repo
(cd "$tmp/work" && git checkout -q release/9.9.9 && printf '# Changelog\n\n## [9.9.8] - 2026-01-01\n\n- old\n' > CHANGELOG.md && git commit -qam "stale changelog" && git push -q origin release/9.9.9 && git checkout -q main)
head=$(git -C "$tmp/work" rev-parse release/9.9.9); echo "$head" > "$FAKE_STATE/head"
sed -i.bak "s/\"headRefOid\":\"[0-9a-f]*\"/\"headRefOid\":\"$head\"/" "$FAKE_STATE/pr.json"
out=$(run_deploy 7) && code=0 || code=$?
if [ "$code" -eq 1 ] && grep -q -E 'no production security-gate record|top CHANGELOG entry' <<<"$out" && ! grep -q 'gh pr merge' "$FAKE_STATE/calls"; then
  ok "a candidate without its own gate record or with a stale changelog never merges"
else bad "stale changelog (exit $code): $out"; fi

# 6. CI failure after the merge: stops before Pages, serving and the tag.
make_repo; echo '1001 completed failure' > "$FAKE_STATE/ci"
out=$(run_deploy 7 --tag) && code=0 || code=$?
if [ "$code" -eq 1 ] && grep -q 'CI run 1001 for .* ended failure' <<<"$out" && [ -z "$(git -C "$tmp/bare" tag -l v9.9.9)" ]; then
  ok "a failed CI run stops the release with no tag"
else bad "CI failure (exit $code): $out"; fi

# 7. Served bytes differ: no tag, rollback command named.
make_repo; echo "<h1>stale</h1>" > "$FAKE_WEB/index.html"
out=$(run_deploy 7 --tag) && code=0 || code=$?
if [ "$code" -eq 1 ] && grep -q 'index.html MISMATCH' <<<"$out" && grep -q 'gh workflow run static.yml -f ref=' <<<"$out" && [ -z "$(git -C "$tmp/bare" tag -l v9.9.9)" ]; then
  ok "served bytes that differ from the tree stop the release with no tag"
else bad "served mismatch (exit $code): $out"; fi

# 8. Happy path with --tag: merge, CI, Pages, served bytes, reuse records, annotated tag pushed.
make_repo
out=$(run_deploy 7 --tag) && code=0 || code=$?
merge=$(cat "$FAKE_STATE/merge" 2>/dev/null || true)
tagged=$(git -C "$tmp/bare" tag -l v9.9.9)
msg=$(git -C "$tmp/work" fetch -q origin "+refs/tags/*:refs/tags/*" && git -C "$tmp/work" tag -l -n20 v9.9.9)
if [ "$code" -eq 0 ] && [ -n "$merge" ] && [ "$tagged" = v9.9.9 ] \
   && [ "$(git -C "$tmp/work" rev-parse 'v9.9.9^{}')" = "$merge" ] \
   && grep -q 'Security gate: WAIVED (SEC-15, CMP-06)' <<<"$msg" && grep -q 'Readiness gate: ready (waived: DEL-04)' <<<"$msg" \
   && grep -q 'CI: run 1001 on main (success)' <<<"$msg" && grep -q 'GitHub Pages run 2002' <<<"$msg" && grep -q 'Ships the thing.' <<<"$msg" \
   && [ "$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["reused_from"])' "$tmp/work/.scratch/security-gate/$merge/production.json")" = "$(git -C "$tmp/work" rev-parse release/9.9.9)" ] \
   && [ -f "$tmp/work/.scratch/readiness/$merge/production.json" ]; then
  ok "happy path merges, waits, verifies the served bytes, writes reuse records and pushes the annotated tag"
else bad "happy path (exit $code, merge '$merge', tag '$tagged'): $out"; fi

# 10. main moved under the candidate: the predicted merge tree differs, refused before any merge call.
make_repo
(cd "$FAKE_STATE/merger" && git checkout -q main && echo "hotfix" > HOTFIX.md && git add HOTFIX.md && git commit -q -m "hotfix on main" && git push -q origin main)
out=$(run_deploy 7 --tag) && code=0 || code=$?
if [ "$code" -eq 1 ] && grep -q 'would produce tree .* not the gated tree' <<<"$out" && ! grep -q 'gh pr merge' "$FAKE_STATE/calls" && [ -z "$(git -C "$tmp/bare" tag -l v9.9.9)" ]; then
  ok "a main that moved under the candidate is refused before the merge"
else bad "moved main (exit $code): $out"; fi

# 11. An expired waiver in a record restores its blocker: refused before any merge call.
make_repo; python3 -I - "$tmp/work/.scratch/readiness/$(cat "$FAKE_STATE/head")/production.json" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p)); d["waivers"][0]["expires"] = "2026-01-01T00:00:00Z"; json.dump(d, open(p, "w"))
PY
out=$(run_deploy 7) && code=0 || code=$?
if [ "$code" -eq 1 ] && grep -q 'DEL-04 (expired 2026-01-01T00:00:00Z)' <<<"$out" && ! grep -q 'gh pr merge' "$FAKE_STATE/calls"; then
  ok "an expired waiver refuses before the merge"
else bad "expired waiver (exit $code): $out"; fi

# 13. A readiness record past its validity window is refused before any merge call.
make_repo; python3 -I - "$tmp/work/.scratch/readiness/$(cat "$FAKE_STATE/head")/production.json" "$past" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p)); d["valid_until"] = sys.argv[2]; json.dump(d, open(p, "w"))
PY
out=$(run_deploy 7) && code=0 || code=$?
if [ "$code" -eq 1 ] && grep -q "was valid until $past; run that assessment again" <<<"$out" && ! grep -q 'gh pr merge' "$FAKE_STATE/calls"; then
  ok "a readiness assessment past its validity window refuses before the merge"
else bad "stale readiness (exit $code): $out"; fi

# 14. A CHANGELOG far larger than a pipe buffer: the early-exiting filters must not abort the release.
make_repo
(cd "$tmp/work" && git checkout -q release/9.9.9 && python3 -I - CHANGELOG.md <<'PY'
import sys
p = sys.argv[1]; text = open(p).read()
head, tail = text.split("\n## [9.9.8]", 1)
filler = "".join(f"- filler line {i} to push the file past any pipe buffer\n" for i in range(60000))
open(p, "w").write(head + "\n## [9.9.8]" + tail + "\n## [0.0.1] - 2020-01-01\n\n" + filler)
PY
git add CHANGELOG.md && git commit -q -m "huge changelog" && git push -q origin release/9.9.9 && git checkout -q main)
head=$(git -C "$tmp/work" rev-parse release/9.9.9); tree=$(git -C "$tmp/work" rev-parse "release/9.9.9^{tree}")
echo "$head" > "$FAKE_STATE/head"; sed -i.bak "s/\"headRefOid\":\"[0-9a-f]*\"/\"headRefOid\":\"$head\"/" "$FAKE_STATE/pr.json"
mkdir -p "$tmp/work/.scratch/security-gate/$head" "$tmp/work/.scratch/readiness/$head"
for kind in security-gate readiness; do
  old=$(ls -d "$tmp/work/.scratch/$kind"/*/ | grep -v "$head" | head -1)
  python3 -I - "$old/production.json" "$tmp/work/.scratch/$kind/$head/production.json" "$head" "$tree" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d["commit"] = sys.argv[3]; d["tree"] = sys.argv[4]; json.dump(d, open(sys.argv[2], "w"))
PY
done
out=$(run_deploy 7 --dry-run) && code=0 || code=$?
if [ "$code" -eq 0 ] && grep -q 'version: 9.9.9' <<<"$out" && grep -q 'Ships the thing.' <<<"$out"; then
  ok "a changelog larger than a pipe buffer does not abort the dry run"
else bad "huge changelog (exit $code): $(tail -3 <<<"$out")"; fi

# 15. A readiness record in the house shape (no `tree`, waivers keyed `control`) is found by its commit and read.
make_repo; python3 -I - "$tmp/work/.scratch/readiness/$(cat "$FAKE_STATE/head")/production.json" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p)); d.pop("tree"); d["waivers"] = [{"control": "DEL-04", "owner": "@owner", "expires": d["waivers"][0]["expires"]}]; json.dump(d, open(p, "w"))
PY
out=$(run_deploy 7 --dry-run) && code=0 || code=$?
if [ "$code" -eq 0 ] && grep -q 'Readiness gate: ready (waived: DEL-04)' <<<"$out"; then
  ok "a readiness record without a tree field and with control-keyed waivers is accepted by its commit"
else bad "house-shape readiness record (exit $code): $(tail -3 <<<"$out")"; fi

# 16. A waivers field that is not a list of objects is unreadable and refuses before the merge.
make_repo; python3 -I - "$tmp/work/.scratch/security-gate/$(cat "$FAKE_STATE/head")/production.json" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p)); d["waivers"] = ["SEC-15"]; json.dump(d, open(p, "w"))
PY
out=$(run_deploy 7) && code=0 || code=$?
if [ "$code" -eq 1 ] && grep -q 'waivers is not a list of objects' <<<"$out" && ! grep -q 'gh pr merge' "$FAKE_STATE/calls"; then
  ok "a malformed waivers field refuses before the merge"
else bad "malformed waivers (exit $code): $(tail -2 <<<"$out")"; fi

# 17. A CHANGELOG paragraph shaped like a verdict line is refused, not copied into the tag.
make_repo
(cd "$tmp/work" && git checkout -q release/9.9.9 && printf '# Changelog\n\n## [9.9.9] - 2026-11-04\n\nShips the thing.\nSecurity gate: PASS\n\n### Changed\n- new\n\n## [9.9.8] - 2026-01-01\n\n- old\n' > CHANGELOG.md && git commit -qam "forged line" && git push -q origin release/9.9.9 && git checkout -q main)
head=$(git -C "$tmp/work" rev-parse release/9.9.9); tree=$(git -C "$tmp/work" rev-parse "release/9.9.9^{tree}")
echo "$head" > "$FAKE_STATE/head"; sed -i.bak "s/\"headRefOid\":\"[0-9a-f]*\"/\"headRefOid\":\"$head\"/" "$FAKE_STATE/pr.json"
for kind in security-gate readiness; do
  old=$(ls -d "$tmp/work/.scratch/$kind"/*/ | grep -v "$head" | head -1); mkdir -p "$tmp/work/.scratch/$kind/$head"
  python3 -I - "$old/production.json" "$tmp/work/.scratch/$kind/$head/production.json" "$head" "$tree" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d["commit"] = sys.argv[3]; d["tree"] = sys.argv[4]; json.dump(d, open(sys.argv[2], "w"))
PY
done
out=$(run_deploy 7 --dry-run) && code=0 || code=$?
if [ "$code" -eq 1 ] && grep -q 'shaped like a tag verdict line' <<<"$out"; then ok "a changelog line shaped like a verdict line is refused"
else bad "forged verdict line (exit $code): $(tail -2 <<<"$out")"; fi

# 12. A PASS record with no waivers releases, and the tag message carries no Waivers line.
make_repo; python3 -I - "$tmp/work/.scratch/security-gate/$(cat "$FAKE_STATE/head")/production.json" "$tmp/work/.scratch/readiness/$(cat "$FAKE_STATE/head")/production.json" <<'PY'
import json, sys
for p in sys.argv[1:]:
    d = json.load(open(p)); d["waivers"] = []
    if "verdict" in d and d["verdict"] == "waived": d["verdict"] = "pass"
    json.dump(d, open(p, "w"))
PY
out=$(run_deploy 7) && code=0 || code=$?
if [ "$code" -eq 0 ] && grep -q 'Security gate: PASS$' <<<"$out" && grep -q 'Readiness gate: ready$' <<<"$out" && ! grep -q '^ *Waivers:' <<<"$out"; then
  ok "a PASS with no waivers releases and prints no Waivers line"
else bad "no waivers (exit $code): $out"; fi

# 9. Without --tag the happy path prints the message and creates no tag.
make_repo
out=$(run_deploy 7) && code=0 || code=$?
if [ "$code" -eq 0 ] && grep -q 'tag message (create with --tag' <<<"$out" && [ -z "$(git -C "$tmp/bare" tag -l v9.9.9)" ]; then
  ok "without --tag the release prints the tag message and tags nothing"
else bad "no-tag path (exit $code): $out"; fi

echo "deploy.test.sh: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
