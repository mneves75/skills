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
#    carry) must still be inside it; a stale assessment is run again, not reused. A record is in scope when
#    it sits in the candidate's own folder or names the candidate's tree (or a commit with that tree) anywhere
#    in its text; every in-scope record must be well-formed (readable, no repeated key at any depth, exactly
#    the keys its contract names, bound to the tree) or the release refuses naming it; the newest one decides.
#    A MERGED pull request resumes at step 4 (its merge commit's tree must be the gated one): for a
#    release that stopped after the merge.
# 4. Waits for the CI push run on main and the Pages run for the merge commit, then compares every tracked
#    file under site/ with the bytes the site serves.
# 5. Writes the reuse records for the merge commit, preserving the original audit's `reused_from`
#    (or source commit on first transfer). Same-commit rewrites keep the field's existing form.
#    Prints the annotated tag message in the house format. With --tag it creates and pushes
#    `vX.Y.Z` on the merge commit.
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
scratch=$(mktemp -d "${TMPDIR:-/tmp}/deploy-sh.XXXXXX")
trap 'rm -rf "$scratch"' EXIT

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
    # Security records key a waiver as `id`, readiness records as `control`.
    print(" ".join(str(item.get("id") or item.get("control")) if isinstance(item, dict) else str(item) for item in value))
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
[ "$base" = main ] || fail "PR #$pr targets $base, not main"
resume=0; merge=""
if [ "$state" = MERGED ]; then
  # A release that stopped after its merge (a cancelled CI run, a lost connection) resumes at the CI wait:
  # the merge commit's tree must be the gated one, and the tag must not exist yet (step 2).
  resume=1
  merge=$(gh pr view "$pr" --repo "$repo" --json mergeCommit --jq '.mergeCommit.oid')
  [ -n "$merge" ] && [ "$merge" != null ] || fail "PR #$pr is MERGED but shows no merge commit"
  git fetch -q origin main || fail "cannot fetch origin/main"
  git cat-file -e "$merge^{commit}" 2>/dev/null || fail "merge commit $merge is not in this repository after fetching main"
  git merge-base --is-ancestor "$merge" origin/main || fail "merge commit $merge is not on origin/main: nothing to resume"
  tree=$(git rev-parse "$merge^{tree}")
  [ "$(git rev-parse "$head^{tree}")" = "$tree" ] || fail "PR #$pr head tree differs from its merge tree: cannot resume"
  say "candidate: PR #$pr ($head_ref) head $head, merged as $merge, tree $tree"
else
  [ "$state" = OPEN ] || fail "PR #$pr is $state, not OPEN"
  git fetch -q origin "+refs/heads/$head_ref:refs/remotes/origin/$head_ref" || fail "cannot fetch origin/$head_ref"
  git cat-file -e "$head^{commit}" 2>/dev/null || fail "head commit $head is not in this repository after the fetch"
  tree=$(git rev-parse "$head^{tree}")
  say "candidate: PR #$pr ($head_ref) head $head tree $tree"
fi

# A record binds to a tree. Security records state `tree`; readiness records state only `commit`, so the
# tree is the commit's tree when that commit is in this repository. For each kind, the NEWEST production
# record with the candidate's tree (by created_at; the head's own folder wins a tie) is the authoritative
# assessment: it is used when valid in full (target, verdict, acceptance or blockers, waivers in force,
# validity window) and refused with its reasons otherwise. An older approval never stands in for a newer
# assessment that blocks or has gone stale: a reassessment can block production without changing a byte.
select_record() {
  python3 -I - "$1" "$head" "$tree" "$records" <<'PY'
import datetime, glob, json, os, re, subprocess, sys
kind, head, tree, records = sys.argv[1:5]
now = datetime.datetime.now(datetime.timezone.utc)
own = os.path.join(records, kind, head, "production.json")

CONTRACT = {
    # mneves-security references/report.md (the security record) and
    # mneves-production-readiness references/ledger.md (the readiness record): every top-level key.
    "security-gate": ({"schema", "unit", "target", "commit", "tree", "verdict", "open_blockers", "blockers",
                       "independent_acceptance", "created_at", "waivers"}, {"reused_from"}),
    "readiness": ({"schema", "unit", "target", "catalog", "commit", "verdict", "open_blockers", "created_at",
                   "valid_until", "waivers"}, {"tree", "independent_acceptance", "evidence", "reused_from"}),
}
REPEATED = object()  # a key no JSON document can contain, so a record cannot forge the marker

def refuse(message):
    print(f"the production {kind} record {message}")
    sys.exit(1)

def invalid_constant(value):
    raise ValueError(f"{value} is not a JSON value")

def note_repeats(pairs):
    """Last value wins, as json.load does, but every object remembers which of its keys were repeated."""
    seen = {}
    repeated = []
    for key, value in pairs:
        if key in seen:
            repeated.append(key)
        seen[key] = value
    if repeated:
        seen[REPEATED] = repeated
    return seen

def repeated_keys(value, where=""):
    """Every repeated key at any depth (a waiver inside the waivers array included), as paths."""
    found = []
    if isinstance(value, dict):
        found.extend(f"{where}.{key}" if where else key for key in value.pop(REPEATED, []))
        for key, inner in value.items():
            found.extend(repeated_keys(inner, f"{where}.{key}" if where else key))
    elif isinstance(value, list):
        for index, inner in enumerate(value):
            found.extend(repeated_keys(inner, f"{where}[{index}]"))
    return found

def when(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value):
        raise ValueError("timestamp must be UTC YYYY-MM-DDTHH:MM:SSZ")
    return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)

def tree_of_commit(commit):
    try:
        done = subprocess.run(["git", "rev-parse", "--verify", "-q", "--end-of-options", f"{commit}^{{tree}}"], capture_output=True, text=True)
    except ValueError:  # a malformed JSON string can contain a NUL; it is not a Git revision
        return None
    return done.stdout.strip() or None

def in_scope(path, text):
    """The candidate's own folder, or any text that names the candidate's tree or a commit whose tree it is."""
    if path == own or tree in text:
        return True
    candidates = set(re.findall(r"\b[0-9a-f]{40}\b", text))
    # Decode before deciding scope. Keeping object pairs also preserves names hidden by a
    # duplicate key, so escaped or repeated fields cannot conceal a newer assessment.
    def names(value):
        if isinstance(value, (list, tuple)):
            if len(value) == 2 and value[0] == "commit" and isinstance(value[1], str):
                candidates.add(value[1])
            for item in value:
                yield from names(item)
        elif isinstance(value, str):
            yield value
    try:
        decoded = json.loads(text, object_pairs_hook=list)
        for value in names(decoded):
            if tree in value:
                return True
            candidates.update(re.findall(r"\b[0-9a-f]{40}\b", value))
    except ValueError:
        pass  # malformed text that names this tree is still scoped by its raw identifiers
    return any(tree_of_commit(cid) == tree for cid in candidates if cid != tree)

def shape_problems(record):
    """What makes a record malformed, whatever it says: judged on every in-scope record before any is chosen."""
    out = []
    required, optional = CONTRACT[kind]
    missing = sorted(required - set(record))
    unknown = sorted(set(record) - required - optional)
    if missing:
        out.append("missing required key(s): " + ", ".join(missing))
    if unknown:
        out.append("key(s) outside the record contract: " + ", ".join(unknown))
    if type(record.get("schema")) is not int or record["schema"] != 1:
        out.append("schema must be 1")
    if record.get("unit") != ".":
        out.append("unit must be . for this repository release")
    if kind == "readiness" and (type(record.get("catalog")) is not int or record["catalog"] != 3):
        out.append("catalog must be 3")
    if "evidence" in record and not isinstance(record["evidence"], dict):
        out.append("evidence must be an object")
    if "reused_from" in record:
        reused = record["reused_from"]
        empty_security_origin = kind == "security-gate" and reused == ""
        if not isinstance(reused, str) or not (empty_security_origin or re.fullmatch(r"[0-9a-f]{40}", reused)):
            out.append("reused_from must be a full lowercase 40-character SHA (or empty for security)")
    commit = record.get("commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        out.append("commit must be a full lowercase 40-character SHA")
        commit_tree = None
    else:
        commit_tree = tree_of_commit(commit)
    stated_tree = record.get("tree")
    if "tree" in record and (not isinstance(stated_tree, str) or not re.fullmatch(r"[0-9a-f]{40}", stated_tree)):
        out.append("tree must be a full lowercase 40-character SHA")
    bound = stated_tree if "tree" in record else commit_tree
    if bound != tree:
        out.append("does not bind the candidate's tree " + tree)
    if commit_tree != tree:
        out.append("commit's tree does not equal the candidate's tree " + tree)
    try:
        created = when(record.get("created_at"))
        if created > now:
            out.append("created_at is in the future")
        if kind == "readiness":
            until = when(record.get("valid_until"))
            if not created < until or until - created > datetime.timedelta(hours=24):
                out.append("valid_until must be after created_at and within 24 hours")
    except ValueError:
        out.append("created_at or valid_until is not a valid UTC YYYY-MM-DDTHH:MM:SSZ timestamp")
    waivers = record.get("waivers")
    if not isinstance(waivers, list) or any(not isinstance(w, dict) for w in waivers):
        out.append("waivers is not a list of objects")
    else:
        fields = {"id" if kind == "security-gate" else "control", "owner", "reason", "expires"}
        for index, waiver in enumerate(waivers):
            if set(waiver) != fields:
                out.append(f"waivers[{index}] must hold exactly {', '.join(sorted(fields))}")
            for field, value in waiver.items():
                if not isinstance(value, str) or not value.strip():
                    out.append(f"waivers[{index}].{field} must be a non-empty string")
                elif any(ord(char) < 32 or ord(char) == 127 for char in value):
                    out.append(f"waivers[{index}].{field} contains a control character")
            try:
                expiry = when(waiver.get("expires"))
                if kind == "readiness" and when(record.get("valid_until")) > expiry:
                    out.append(f"valid_until exceeds waivers[{index}] expiry")
            except ValueError:
                out.append(f"waivers[{index}] or valid_until has an unreadable UTC expiry")
    if kind == "security-gate":
        count = record.get("open_blockers")
        if type(count) is not int or count < 0:
            out.append("open_blockers must be a non-negative integer")
        else:
            expected = "block" if count else ("waived" if waivers else "pass")
            if record.get("verdict") != expected:
                out.append("verdict contradicts open_blockers or the waivers array")
            blockers = record.get("blockers")
            if not isinstance(blockers, str) or bool(blockers.strip()) != bool(count):
                out.append("blockers contradicts open_blockers")
    return out

def verdict_problems(record):
    """What keeps the chosen record from admitting the tree."""
    out = []
    if record.get("target") != "production":
        out.append(f"target is {record.get('target')!r}, not production")
    if kind == "security-gate":
        if record.get("verdict") not in ("pass", "waived"):
            out.append(f"verdict is {record.get('verdict')!r}")
        if record.get("independent_acceptance") != "pass":
            out.append(f"independent acceptance is {record.get('independent_acceptance')!r}")
        if type(record.get("open_blockers")) is not int or record["open_blockers"] != 0:
            out.append(f"{record.get('open_blockers')} open blocker(s)")
    else:
        if record.get("verdict") != "ready":
            out.append(f"verdict is {record.get('verdict')!r}")
        if type(record.get("open_blockers")) is not int or record["open_blockers"] != 0:
            out.append(f"{record.get('open_blockers')} open blocker(s)")
        if record.get("independent_acceptance") != "pass":  # readiness step 5, the verifier's own check
            out.append(f"independent acceptance is {record.get('independent_acceptance')!r}")
    waivers = record.get("waivers")
    if waivers is None:
        waivers = []
    if not isinstance(waivers, list) or any(not isinstance(w, dict) for w in waivers):
        out.append("waivers is not a list of objects")
    else:
        for waiver in waivers:
            name = waiver.get("id") or waiver.get("control")
            try:
                if when(waiver.get("expires")) <= now:
                    out.append(f"waiver {name} expired {waiver.get('expires')}")
            except ValueError:
                out.append(f"waiver {name} has an unreadable expiry {waiver.get('expires')!r}")
    if record.get("valid_until") is not None:
        try:
            if when(record["valid_until"]) <= now:
                out.append(f"was valid until {record['valid_until']}; run that assessment again on this tree")
        except ValueError:
            out.append(f"unreadable valid_until {record['valid_until']!r}")
    return out

# 1. Scope: every record that may be an assessment of this tree, the candidate's own folder first of all.
scope = []
skipped = []  # records that cannot be opened, so cannot be scoped: named, never dropped in silence
for path in sorted(glob.glob(os.path.join(records, kind, "*", "production.json"))):
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as error:
        if path == own:
            refuse(f"in the candidate's own folder is unreadable ({error}); fix or rewrite it, no other record substitutes")
        skipped.append(f"{path}: unreadable ({error})")
        continue
    if not in_scope(path, text):
        continue
    label = "in the candidate's own folder" if path == own else f"{path} (it names this tree)"
    try:
        record = json.loads(text, object_pairs_hook=note_repeats, parse_constant=invalid_constant)
    except ValueError as error:
        refuse(f"{label} is unreadable ({error}); fix or rewrite it, no other record substitutes")
    if not isinstance(record, dict):
        refuse(f"{label} is not a JSON object; fix or rewrite it, no other record substitutes")
    repeated = repeated_keys(record)
    if repeated:
        refuse(f"{label} has a repeated key {', '.join(repeated)}; fix or rewrite it, no other record substitutes")
    scope.append((path, record))
if not scope:
    print(f"no production {kind} record for tree {tree} under {records}/{kind}/"
          + (" (" + "; ".join(skipped) + ")" if skipped else ""))
    sys.exit(1)
if skipped:
    print("unreadable record(s) skipped: " + "; ".join(skipped), file=sys.stderr)

# 2. Every in-scope record must be well-formed before any is chosen: a malformed assessment is never ranked around.
for path, record in scope:
    found = shape_problems(record)
    if found:
        refuse(f"{path} is malformed: " + "; ".join(found) + "; fix or rewrite it, no other record substitutes")

# 3. The newest well-formed record is the authoritative assessment (the head's own wins a tie); an older
#    approval never stands in for a newer assessment that blocks or has gone stale.
scope.sort(key=lambda item: (when(item[1]["created_at"]), item[0] == own), reverse=True)
newest_path, newest = scope[0]
found = verdict_problems(newest)
if found:
    older = len(scope) - 1
    print(f"the newest production {kind} record for tree {tree}, {newest_path}, does not admit it: " + "; ".join(found)
          + (f" ({older} older record(s) for the same tree do not substitute for it)" if older else ""))
    sys.exit(1)
print(newest_path)
PY
}
security=$(select_record security-gate) || fail "$security (run the mneves-security deploy gate on the candidate)"
readiness=$(select_record readiness) || fail "$readiness"
sec_verdict=$(jget "$security" verdict); sec_accept=$(jget "$security" independent_acceptance)
ready_verdict=$(jget "$readiness" verdict); ready_open=$(jget "$readiness" open_blockers)
gated_commit=$(jget "$security" commit)
sec_waivers=$(jget "$security" waivers); ready_waivers=$(jget "$readiness" waivers)
# The Readiness line names only the waivers the readiness gate adds; the security ids it imports are on the Security line.
# Computed in Python so that an id is never word-split or glob-expanded by the shell.
ready_only=$(python3 -I - "$security" "$readiness" <<'PY'
import json, sys
ids = lambda path: [str(w.get("id") or w.get("control")) for w in json.load(open(path, encoding="utf-8")).get("waivers") or []]
security = set(ids(sys.argv[1]))
print(", ".join(c for c in ids(sys.argv[2]) if c not in security))
PY
)
# The tag's Waivers line names every waiver with its own owner and expiry, grouped; a PASS with none prints no line.
waivers_line=$(python3 -I - "$security" "$readiness" <<'PY'
import json, sys
groups = {}
for path in sys.argv[1:]:
    for waiver in json.load(open(path, encoding="utf-8")).get("waivers") or []:
        key = (str(waiver.get("owner")), str(waiver.get("expires")))
        ids = groups.setdefault(key, [])
        name = str(waiver.get("id") or waiver.get("control"))
        if name not in ids:  # the readiness record repeats the security ids it imports
            ids.append(name)
print("; ".join(f"{owner} to {expires} ({', '.join(ids)})" for (owner, expires), ids in groups.items()))
PY
)
say "security gate: $sec_verdict (acceptance $sec_accept) record $security"
say "readiness: $ready_verdict, $ready_open open blockers, record $readiness"

# ---- 2. Version consistency at the candidate ---------------------------------------------------
# Each file is read whole into the scratch directory first: a filter that stops early (grep -m1, an awk
# `exit`) on a pipe from `git show` would otherwise close it mid-write and, under pipefail, abort the release.
version_commit=$head
[ "$resume" -eq 0 ] || version_commit=$merge
for file in VERSION CHANGELOG.md README.md; do
  git show "$version_commit:$file" > "$scratch/$file" || fail "$file is not in commit $version_commit"
done
version=$(tr -d '[:space:]' < "$scratch/VERSION")
[[ $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || fail "VERSION at $version_commit is '$version'"
top_entry=$(grep -m1 -E '^## \[[0-9]+\.[0-9]+\.[0-9]+\]' "$scratch/CHANGELOG.md" || true)
[[ $top_entry == "## [$version]"* ]] || fail "top CHANGELOG entry '$top_entry' is not $version"
grep -q "badge/version-$version-" "$scratch/README.md" || fail "README badge is not $version"
tags=$(git ls-remote --tags origin "refs/tags/v$version")
[ -z "$tags" ] || fail "tag v$version already exists on origin"
summary=$(awk -v h="$top_entry" '$0==h{f=1; next} f && /^## /{exit} f && NF{print} f && !NF && n{exit} f && NF{n=1}' "$scratch/CHANGELOG.md")
# The tag message's verdict lines are the only lines of their shape: a summary line that looks like one
# would read as a verdict to a rollback reader, so it is refused rather than copied.
if grep -q -E '^(Security gate|Readiness gate|Waivers|Independent acceptance|Gated tree|Gated commit|CI|Deployed):' <<<"$summary"; then
  fail "the CHANGELOG entry's first paragraph contains a line shaped like a tag verdict line; reword it before releasing"
fi
say "version: $version ($top_entry)"

tag_message() {
  # $1 merge commit, $2 CI run, $3 Pages run
  printf 'v%s\n\n%s\n\n' "$version" "$summary"
  printf 'Security gate: %s' "$(tr a-z A-Z <<<"$sec_verdict")"; [ -n "$sec_waivers" ] && printf ' (%s)' "${sec_waivers// /, }"; printf '\n'
  printf 'Readiness gate: %s' "$ready_verdict"; [ -n "$ready_only" ] && printf ' (waived: %s)' "$ready_only"; printf '\n'
  [ -n "$waivers_line" ] && printf 'Waivers: %s\n' "$waivers_line"
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
if [ "$resume" -eq 1 ]; then
  say "resuming after the merge: $merge (tree equal to the gated tree)"
else
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
[ "$merge_tree" = "$tree" ] || fail "PUBLISHED AN UNGATED TREE: merge $merge has tree $merge_tree, not the gated tree $tree (main moved in the window between the check at $base_tip and the merge). No record, no tag. A Pages run for $merge may already be queued (gh run list --workflow static.yml --commit $merge); roll back with: gh workflow run static.yml -f ref=$base_tip after it, then merge main into the branch and gate again"
say "merged: $merge (tree equal to the gated tree)"
fi

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
    # Only a successful download is hashed: a failed request must never equal an empty tracked file.
    if curl -fsSL -H 'Cache-Control: no-cache' -o "$scratch/served" "$site_url/$rel?v=$merge"; then
      got=$(shasum -a 256 "$scratch/served" | cut -d' ' -f1)
    else
      got=""
    fi
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
if record["commit"] != sys.argv[3]:
    record["reused_from"] = record.get("reused_from") or record["commit"]
record["commit"] = sys.argv[3]
record["created_at"] = sys.argv[4]
json.dump(record, open(sys.argv[2], "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PY
  printf '# Reused for merge %s\n\nSame tree `%s` as the gated candidate; see `%s`. Written by tools/scripts/deploy.sh at %s.\n' "$merge" "$tree" "$1" "$now" > "$2/production.md"
}
write_reuse "$security" "$records/security-gate/$merge"
write_reuse "$readiness" "$records/readiness/$merge"
say "records: $records/security-gate/$merge and $records/readiness/$merge"

message_file="$scratch/tag-message.txt"
tag_message "$merge" "$ci_run" "$pages_run" > "$message_file"
if [ "$make_tag" -eq 1 ]; then
  git tag -a "v$version" "$merge" -F "$message_file"
  git push -q origin "refs/tags/v$version"
  say "tagged: v$version on $merge (pushed)"
else
  cp "$message_file" "$records/security-gate/$merge/tag-message.txt"
  say "tag message (create with --tag, or: git tag -a v$version $merge -F $records/security-gate/$merge/tag-message.txt && git push origin v$version):"
  sed 's/^/    /' "$message_file"
fi
