#!/usr/bin/env bash
# Production release of this repository, as CONTRIBUTING.md "Preparing a Release" describes it.
# There is no staging: merging a pull request into `main` publishes GitHub Pages after CI succeeds,
# and `main` is what `npx skills add mneves75/skills` installs.
#
#   tools/scripts/deploy.sh <pr-number> [--dry-run] [--tag]
#
# 1. Reads the pull request's head commit and tree and refuses unless the private gate records exist
#    for that tree: `.scratch/security-gate/<sha>/production.json` (verdict pass or waived, independent
#    acceptance pass) and `.scratch/readiness/<sha>/production.json` (verdict ready, no open blocker).
#    A record for another commit with the same tree counts: the verdicts bind to the tree.
# 2. Checks VERSION against the top CHANGELOG entry and the README badge at that commit.
# 3. Computes the tree the merge would produce (`git merge-tree --write-tree origin/main <head>`, Git 2.38+)
#    and refuses unless it equals the gated tree: when main moved under the candidate, merge main into the
#    branch and gate again. Then merges with `gh pr merge --merge --match-head-commit` and checks the merge
#    commit's tree again; a main that moved in the seconds between the two checks is reported as a published
#    ungated tree with the rollback command, and nothing further runs (GitHub offers no base pin to close
#    that window; branch protection "require branches to be up to date" would).
#    Every waiver in both records must be unexpired: an expired waiver restores its blocker, so the record
#    no longer admits the tree. A record that states a validity window (`valid_until`, which readiness records
#    carry) must still be inside it; a stale assessment is run again, not reused.
# 4. Waits for the CI push run on main and the Pages run for the merge commit, then compares every tracked
#    file under site/ with the bytes the site serves.
# 5. Writes the reuse records for the merge commit (`reused_from` the gated candidate) and prints the
#    annotated tag message in the house format. With --tag it creates and pushes `vX.Y.Z` on the merge commit.
# --dry-run stops after step 2 and prints the plan and the tag message it would write; it changes nothing.
#
# Exit 1 names the first failed check; nothing after it runs. Exit 2 is a usage error.
# Environment (defaults suit this repository; the test sets them): DEPLOY_REPO (mneves75/skills),
# DEPLOY_SITE_URL (https://mneves75.github.io/skills), DEPLOY_RECORDS (.scratch),
# DEPLOY_POLL_SECONDS (30), DEPLOY_TIMEOUT_SECONDS (2400), DEPLOY_SERVE_ATTEMPTS (10).
set -euo pipefail

usage() { sed -n '2,21p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//' >&2; exit 2; }
pr=""; dry_run=0; make_tag=0
for arg in "$@"; do
  case $arg in
    --dry-run) dry_run=1 ;;
    --tag) make_tag=1 ;;
    -*) usage ;;
    *) [ -z "$pr" ] && [[ $arg =~ ^[0-9]+$ ]] || usage; pr=$arg ;;
  esac
done
[ -n "$pr" ] || usage

root=$(git rev-parse --show-toplevel 2>/dev/null) || { echo "deploy.sh: run it inside the repository" >&2; exit 2; }
cd "$root"
repo=${DEPLOY_REPO:-mneves75/skills}
site_url=${DEPLOY_SITE_URL:-https://mneves75.github.io/skills}
records=${DEPLOY_RECORDS:-.scratch}
poll=${DEPLOY_POLL_SECONDS:-30}
timeout=${DEPLOY_TIMEOUT_SECONDS:-2400}
serve_attempts=${DEPLOY_SERVE_ATTEMPTS:-10}

fail() { echo "deploy.sh: $*" >&2; exit 1; }
say() { printf '%s\n' "$*"; }

# JSON field of a record file: `jget FILE a.b.0`; a list prints its items' ids (or the items) space-separated.
jget() {
  python3 -I - "$1" "$2" <<'PY'
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
for part in sys.argv[2].split("."):
    value = value[int(part)] if isinstance(value, list) else value.get(part)
    if value is None:
        break
if isinstance(value, list):
    print(" ".join(item["id"] if isinstance(item, dict) and "id" in item else str(item) for item in value))
elif value is None:
    print("")
else:
    print(value)
PY
}

# ---- 1. The candidate -------------------------------------------------------------------------
pr_json=$(gh pr view "$pr" --repo "$repo" --json state,headRefOid,headRefName,baseRefName,mergeable,title)
pr_field() { printf '%s' "$pr_json" | python3 -I -c 'import json,sys; print(json.load(sys.stdin)[sys.argv[1]])' "$1"; }
state=$(pr_field state); head=$(pr_field headRefOid); head_ref=$(pr_field headRefName); base=$(pr_field baseRefName)
[ "$state" = OPEN ] || fail "PR #$pr is $state, not OPEN"
[ "$base" = main ] || fail "PR #$pr targets $base, not main"
git fetch -q origin "+refs/heads/$head_ref:refs/remotes/origin/$head_ref" || fail "cannot fetch origin/$head_ref"
git cat-file -e "$head^{commit}" 2>/dev/null || fail "head commit $head is not in this repository after the fetch"
tree=$(git rev-parse "$head^{tree}")
say "candidate: PR #$pr ($head_ref) head $head tree $tree"

# A record binds to a tree: the candidate's own folder first, then any production record with the same tree.
find_record() {
  local kind=$1 file
  file="$records/$kind/$head/production.json"
  if [ -f "$file" ] && [ "$(jget "$file" tree)" = "$tree" ]; then printf '%s' "$file"; return; fi
  for file in "$records"/"$kind"/*/production.json; do
    [ -f "$file" ] || continue
    [ "$(jget "$file" target)" = production ] || continue
    [ "$(jget "$file" tree)" = "$tree" ] && { printf '%s' "$file"; return; }
  done
  return 1
}
security=$(find_record security-gate) || fail "no production security-gate record for tree $tree under $records/security-gate/ (run the mneves-security deploy gate on the candidate)"
readiness=$(find_record readiness) || fail "no production readiness record for tree $tree under $records/readiness/"
sec_verdict=$(jget "$security" verdict); sec_accept=$(jget "$security" independent_acceptance)
case $sec_verdict in pass|waived) ;; *) fail "security gate verdict is '$sec_verdict' ($security)" ;; esac
[ "$sec_accept" = pass ] || fail "security gate independent acceptance is '$sec_accept' ($security)"
ready_verdict=$(jget "$readiness" verdict); ready_open=$(jget "$readiness" open_blockers)
[ "$ready_verdict" = ready ] || fail "readiness verdict is '$ready_verdict' ($readiness)"
[ "${ready_open:-0}" = 0 ] || fail "readiness has $ready_open open blocker(s) ($readiness)"
gated_commit=$(jget "$security" commit)
sec_waivers=$(jget "$security" waivers); ready_waivers=$(jget "$readiness" waivers)
# An expired waiver restores its blocker, so a record that leans on one no longer admits the tree.
expired=$(python3 -I - "$security" "$readiness" <<'PY'
import datetime, json, sys
now = datetime.datetime.now(datetime.timezone.utc)
bad = []
for path in sys.argv[1:]:
    for waiver in json.load(open(path, encoding="utf-8")).get("waivers") or []:
        if not isinstance(waiver, dict):
            continue
        expires = waiver.get("expires")
        try:
            when = datetime.datetime.fromisoformat(str(expires).replace("Z", "+00:00"))
        except ValueError:
            bad.append(f"{waiver.get('id')} (unreadable expiry {expires!r})"); continue
        if when.tzinfo is None or when <= now:
            bad.append(f"{waiver.get('id')} (expired {expires})")
print(" ".join(bad))
PY
)
[ -z "$expired" ] || fail "waiver(s) no longer in force: $expired; the gate must be renewed before this tree can merge"
# A readiness assessment is valid for the window its record states; past it the run is repeated, not reused.
for record in "$security" "$readiness"; do
  until=$(jget "$record" valid_until)
  [ -z "$until" ] && continue
  python3 -I -c 'import datetime, sys
when = datetime.datetime.fromisoformat(sys.argv[1].replace("Z", "+00:00"))
sys.exit(0 if when.tzinfo and when > datetime.datetime.now(datetime.timezone.utc) else 1)' "$until" 2>/dev/null \
    || fail "record $record was valid until $until; run that assessment again on this tree before merging"
done
# The tag's Waivers line comes from whichever record carries one; a PASS with none prints no line.
waiver_owner=""; waiver_expiry=""
for record in "$security" "$readiness"; do
  if [ -n "$(jget "$record" waivers)" ]; then waiver_owner=$(jget "$record" waivers.0.owner); waiver_expiry=$(jget "$record" waivers.0.expires); break; fi
done
say "security gate: $sec_verdict (acceptance $sec_accept) record $security"
say "readiness: $ready_verdict, $ready_open open blockers, record $readiness"

# ---- 2. Version consistency at the candidate ---------------------------------------------------
version=$(git show "$head:VERSION" | tr -d '[:space:]')
[[ $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || fail "VERSION at $head is '$version'"
top_entry=$(git show "$head:CHANGELOG.md" | grep -m1 -E '^## \[[0-9]+\.[0-9]+\.[0-9]+\]')
[[ $top_entry == "## [$version]"* ]] || fail "top CHANGELOG entry '$top_entry' is not $version"
git show "$head:README.md" | grep -q "badge/version-$version-" || fail "README badge is not $version"
git ls-remote --tags origin "refs/tags/v$version" | grep -q . && fail "tag v$version already exists on origin"
summary=$(git show "$head:CHANGELOG.md" | awk -v h="$top_entry" '$0==h{f=1; next} f && /^## /{exit} f && NF{print} f && !NF && n{exit} f && NF{n=1}')
say "version: $version ($top_entry)"

tag_message() {
  # $1 merge commit, $2 CI run, $3 Pages run
  printf 'v%s\n\n%s\n\n' "$version" "$summary"
  printf 'Security gate: %s' "$(tr a-z A-Z <<<"$sec_verdict")"; [ -n "$sec_waivers" ] && printf ' (%s)' "${sec_waivers// /, }"; printf '\n'
  printf 'Readiness gate: %s' "$ready_verdict"; [ -n "$ready_waivers" ] && printf ' (waived: %s)' "${ready_waivers// /, }"; printf '\n'
  [ -n "$waiver_owner" ] && printf 'Waivers: %s, expiry %s\n' "$waiver_owner" "$waiver_expiry"
  printf 'Independent acceptance: %s\n' "$(tr a-z A-Z <<<"$sec_accept")"
  printf 'Gated tree: %s\n' "$tree"
  printf 'Gated commit: %s (merged as %s, identical tree)\n' "$gated_commit" "$1"
  printf 'CI: run %s on main (success)\n' "$2"
  printf 'Deployed: GitHub Pages run %s (success); served files match the gated tree byte for byte\n' "$3"
}

if [ "$dry_run" -eq 1 ]; then
  say "dry run: would check the merge tree against origin/main, merge PR #$pr at $head, wait for CI and Pages, compare $(git ls-tree -r --name-only "$head" -- site/ | wc -l | tr -d ' ') served files, write reuse records, and tag v$version with:"
  tag_message "<merge>" "<ci-run>" "<pages-run>" | sed 's/^/    /'
  exit 0
fi

# ---- 3. Merge ------------------------------------------------------------------------------------
# The tree the merge would produce must be the gated one BEFORE main changes, since the merge itself
# publishes: a moved main that changes the result means the branch must take main in and be gated again.
git fetch -q origin main || fail "cannot fetch origin/main"
base_tip=$(git rev-parse origin/main)
predicted=$(git merge-tree --write-tree origin/main "$head" 2>/dev/null) || fail "the merge of $head into origin/main ($base_tip) does not apply cleanly (git merge-tree); merge main into the branch, resolve, and gate again"
predicted=${predicted%%$'\n'*}
[ "$predicted" = "$tree" ] || fail "merging $head into origin/main ($base_tip) would produce tree $predicted, not the gated tree $tree: main moved under the candidate; merge main into the branch and run the gate again"
say "merge tree: $predicted equals the gated tree (origin/main at $base_tip)"
gh pr merge "$pr" --repo "$repo" --merge --match-head-commit "$head" || fail "merge of PR #$pr refused"
merge=$(gh pr view "$pr" --repo "$repo" --json mergeCommit --jq '.mergeCommit.oid')
[ -n "$merge" ] && [ "$merge" != null ] || fail "PR #$pr shows no merge commit after the merge"
git fetch -q origin main
git cat-file -e "$merge^{commit}" 2>/dev/null || fail "merge commit $merge not found after fetching main"
merge_tree=$(git rev-parse "$merge^{tree}")
[ "$merge_tree" = "$tree" ] || fail "PUBLISHED AN UNGATED TREE: merge $merge has tree $merge_tree, not the gated tree $tree (main moved in the window between the check at $base_tip and the merge). No record, no tag. Roll back with: gh workflow run static.yml -f ref=$base_tip, then merge main into the branch and gate again"
say "merged: $merge (tree equal to the gated tree)"

# ---- 4. CI, Pages, served bytes ---------------------------------------------------------------------
wait_run() {
  # $1 workflow file, $2 label, $3 extra gh args; prints the run id
  local started=$SECONDS line status conclusion id
  while :; do
    line=$(gh run list --repo "$repo" --workflow "$1" --commit "$merge" $3 --limit 1 --json databaseId,status,conclusion --jq '.[0] | "\(.databaseId) \(.status) \(.conclusion)"' 2>/dev/null || true)
    read -r id status conclusion <<<"${line:-  }"
    if [ "$status" = completed ]; then
      [ "$conclusion" = success ] || fail "$2 run $id for $merge ended $conclusion"
      printf '%s' "$id"; return
    fi
    [ $((SECONDS - started)) -lt "$timeout" ] || fail "$2 run for $merge did not complete within ${timeout}s (last: ${status:-none})"
    sleep "$poll"
  done
}
ci_run=$(wait_run ci.yml "CI" "--branch main --event push"); say "CI: run $ci_run success"
pages_run=$(wait_run static.yml "Pages" ""); say "Pages: run $pages_run success"

served_ok=1
while IFS= read -r path; do
  rel=${path#site/}
  expected=$(git show "$merge:$path" | shasum -a 256 | cut -d' ' -f1)
  got=""
  for attempt in $(seq 1 "$serve_attempts"); do
    got=$(curl -fsSL -H 'Cache-Control: no-cache' "$site_url/$rel?v=$merge" | shasum -a 256 | cut -d' ' -f1 || true)
    [ "$got" = "$expected" ] && break
    [ "$attempt" -lt "$serve_attempts" ] && sleep "$poll"
  done
  if [ "$got" = "$expected" ]; then say "served: $rel $expected"; else say "served: $rel MISMATCH expected $expected got ${got:-nothing}"; served_ok=0; fi
done < <(git ls-tree -r --name-only "$merge" -- site/)
[ "$served_ok" -eq 1 ] || fail "the site does not serve the gated tree; no tag. Fix forward or roll back with: gh workflow run static.yml -f ref=<earlier main commit>"

# ---- 5. Records and tag ------------------------------------------------------------------------------
now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
write_reuse() {
  # $1 source record, $2 destination dir
  mkdir -p "$2"
  python3 -I - "$1" "$2/production.json" "$merge" "$now" <<'PY'
import json, sys
record = json.load(open(sys.argv[1], encoding="utf-8"))
record["reused_from"] = record.get("commit")
record["commit"] = sys.argv[3]
record["created_at"] = sys.argv[4]
json.dump(record, open(sys.argv[2], "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PY
  printf '# Reused for merge %s\n\nSame tree `%s` as the gated candidate; see `%s`. Written by tools/scripts/deploy.sh at %s.\n' "$merge" "$tree" "$1" "$now" > "$2/production.md"
}
write_reuse "$security" "$records/security-gate/$merge"
write_reuse "$readiness" "$records/readiness/$merge"
say "records: $records/security-gate/$merge and $records/readiness/$merge"

message_file=$(mktemp "${TMPDIR:-/tmp}/deploy-tag.XXXXXX")
tag_message "$merge" "$ci_run" "$pages_run" > "$message_file"
if [ "$make_tag" -eq 1 ]; then
  git tag -a "v$version" "$merge" -F "$message_file"
  git push -q origin "refs/tags/v$version"
  say "tagged: v$version on $merge (pushed)"
else
  say "tag message (create with --tag, or: git tag -a v$version $merge -F $message_file && git push origin v$version):"
  sed 's/^/    /' "$message_file"
fi
