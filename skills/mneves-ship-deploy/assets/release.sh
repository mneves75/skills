#!/usr/bin/env bash
# Reference scripts/release.sh for ONE Cloudflare Worker with two Wrangler environments
# (`staging` and `production`) and no database. It follows references/release-contract.md.
#
#   scripts/release.sh <staging|production> [--check] [--dry-run] [--waive <gate>=<reason>]... [--yes]
#
#   staging     the tip of the remote default branch; tag vX.Y.Z-betaN after verify-live passes
#   production  the commit of the newest staging tag, only while staging serves it; tag vX.Y.Z
#   --check     print the plan (target, version, commit, tag, URL), check the runtime pin, exit
#   --dry-run   everything up to the deploy; nothing is published and no tag is made
#   --waive     skip ONE named gate for a stated reason; recorded in release.json (repeatable)
#   --yes       skip the production confirmation prompt (the owner already approved the candidate)
# There is no flag that skips every gate: an unknown argument prints the usage and exits 2.
#
# Install: copy this file and verify-live.sh to scripts/, make both executable, replace every
# __PLACEHOLDER__ below, edit the gate list, and give the Worker a /health handler that answers
# {"status":"ok","commit":"<APP_COMMIT>","version":"<APP_VERSION>","env":"<APP_ENV>"} from the vars
# this script passes to `wrangler deploy --var`. The script refuses to run while a placeholder remains.
# The repository must ignore `.scratch/` (evidence and the build checkout live there).
#
# Guarantees covered here: 1 pushed source, 2 promotion, 3 runtime pin, 4 gates and waivers,
# 6 target parity (secrets on the target, a build per target), 7 live proof with a rollback command,
# 8 tag after proof, 9 release.json, 10 --check.
# Guarantee 5 (recovery point) does not apply to a Worker without a database. A project with
# migrations MUST add it before the deploy step: export the database, capture a recovery point
# (D1 Time Travel bookmark), refuse destructive SQL unless its own flag is passed, then migrate.
#
# Wrangler surface it relies on (check each against your pinned Wrangler before the first real run):
# `whoami` printing the account id; `deployments status --json` printing a `versions` array whose items carry `version_id` and
# `percentage`; `secret list --format json` printing items with a `name`; `deploy --var KEY:VALUE`
# (repeatable) with `--tag` and `--message`; and `rollback <id> -m "<message>" -y`; each with `--env <target>`.
#
# Needs bash 3.2+ (macOS default), git, curl, sed, awk and tr, plus wrangler and the package manager
# the repository pins. The release runs `npm ci` and the gates in a fresh checkout of the commit;
# change that line and the gate commands for pnpm, bun or yarn.
set -euo pipefail

usage="usage: scripts/release.sh <staging|production> [--check] [--dry-run] [--waive <gate>=<reason>]... [--yes]"

# ---- ADAPT: values this project owns ----
STAGING_URL="__STAGING_URL__"
PRODUCTION_URL="__PRODUCTION_URL__"
ACCOUNT_ID="__ACCOUNT_ID__"
# Secrets that must exist on each target, space separated; the word none states there are none.
REQUIRED_SECRETS="__REQUIRED_SECRETS__"
# One gate per line: <name>=<command>. Each runs in the fresh checkout; --waive names one of these.
GATES="lint=npm run lint
typecheck=npm run typecheck
test=npm run test
build=npm run build"

die() { echo "release: $*" >&2; exit 1; }
say() { printf '\n==> %s\n' "$*"; }
bad_usage() { echo "release: $*" >&2; echo "$usage" >&2; exit 2; }

gate_names() { printf '%s\n' "$GATES" | sed -n 's/^\([^=]*\)=.*/\1/p'; }

# ---- Arguments ----
target="${1:-}"
case "$target" in staging | production) shift ;; *) echo "$usage" >&2; exit 2 ;; esac
check=0 dry=0 yes=0 waivers=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --check) check=1 ;;
    --dry-run) dry=1 ;;
    --yes) yes=1 ;;
    --waive)
      [ "$#" -ge 2 ] || bad_usage "--waive needs <gate>=<reason>"
      case "$2" in *=*) ;; *) bad_usage "--waive needs <gate>=<reason>, got '$2'" ;; esac
      w_gate="${2%%=*}"
      w_reason="$(printf '%s' "${2#*=}" | tr -d '\n\r' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')"
      [ -n "$w_reason" ] || bad_usage "--waive $w_gate needs a reason a reader can check"
      gate_names | awk -v g="$w_gate" '$0 == g { found = 1 } END { exit !found }' ||
        bad_usage "unknown gate '$w_gate' (gates: $(gate_names | tr '\n' ' '))"
      waivers="$waivers$w_gate=$w_reason
"
      shift ;;
    *) echo "$usage" >&2; exit 2 ;;
  esac
  shift
done

for pair in "STAGING_URL=$STAGING_URL" "PRODUCTION_URL=$PRODUCTION_URL" "ACCOUNT_ID=$ACCOUNT_ID" "REQUIRED_SECRETS=$REQUIRED_SECRETS"; do
  case "${pair#*=}" in *__[A-Z]*__*) die "${pair%%=*} still holds a placeholder (${pair#*=}): edit the ADAPT block of this script" ;; esac
done

waiver_reason() { printf '%s' "$waivers" | awk -F= -v g="$1" '$1 == g { sub(/^[^=]*=/, ""); print; exit }'; }
json_field() { printf '%s' "$1" | tr -d '\n' | sed -n "s/.*\"$2\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p"; }
json_escape() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }

root="$(git rev-parse --show-toplevel 2>/dev/null)" || die "not inside a Git repository"
cd "$root"

# ---- Guards (Git and the live staging page; nothing is written) ----
# The remote's own answer: a local tracking ref can be stale, so it is never trusted. This also
# names the default branch, so nothing here hard-codes `main`.
symref="$(git ls-remote --symref origin HEAD)" || die "cannot reach origin"
default_ref="$(printf '%s\n' "$symref" | sed -n 's/^ref: \(refs\/heads\/[^[:space:]]*\)[[:space:]]*HEAD$/\1/p')"
remote_tip="$(printf '%s\n' "$symref" | awk '$2 == "HEAD" && $1 !~ /^ref:/ { print $1; exit }')"
[ -n "$default_ref" ] && [ "${#remote_tip}" -ge 40 ] || die "cannot read the default branch of origin"
default_branch="${default_ref#refs/heads/}"
git fetch --quiet origin "$default_branch" || die "cannot fetch $default_branch from origin"
git cat-file -e "$remote_tip^{commit}" 2>/dev/null || die "origin's $default_branch ($remote_tip) could not be fetched"

# Tags as origin has them, one "<commit><TAB><tag>" per line (annotated tags peeled to their commit).
remote_tags="$(git ls-remote --tags origin | awk -F'\t' '{
  ref = $2; peeled = (substr(ref, length(ref) - 2) == "^{}")
  if (peeled) ref = substr(ref, 1, length(ref) - 3)
  sub(/^refs\/tags\//, "", ref)
  if (peeled || !(ref in sha)) sha[ref] = $1
} END { for (t in sha) print sha[t] "\t" t }')"
tag_exists() { printf '%s\n' "$remote_tags" | awk -F'\t' -v t="$1" '$2 == t { found = 1 } END { exit !found }'; }
# Files of a commit are read into a variable first: a reader that stops early would kill `git show`
# with SIGPIPE, which pipefail reports as a missing file once the file outgrows the pipe buffer.
version_at() {
  local pkg
  pkg="$(git show "$1:package.json")"
  printf '%s\n' "$pkg" | sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1
}
changelog_has() {
  local log
  log="$(git show "$1:CHANGELOG.md")" || return 1
  printf '%s\n' "$log" | grep -E "^## \\[${2//./\\.}\\]" > /dev/null
}

if [ "$target" = staging ]; then
  commit="$(git rev-parse HEAD)"
  [ "$commit" = "$remote_tip" ] || die "HEAD is not pushed: it differs from origin/$default_branch (${remote_tip:0:7})"
  version="$(version_at "$commit")"
  [ -n "$version" ] || die "package.json at ${commit:0:7} has no version"
  changelog_has "$commit" "$version" || die "CHANGELOG.md has no '## [$version]' entry at ${commit:0:7}"
  ! tag_exists "v$version" || die "v$version already exists on origin (released to production): bump the version"
  last="$(printf '%s\n' "$remote_tags" | awk -F'\t' -v p="v$version-beta" 'index($2, p) == 1 { n = substr($2, length(p) + 1); if (n ~ /^[0-9]+$/ && n + 0 > max) max = n + 0 } END { print max + 0 }')"
  tag="v$version-beta$((last + 1))"
  url="$STAGING_URL"
  plan_tag="tag $tag"
else
  # The newest staging tag of the highest version on origin.
  staged_tag="$(printf '%s\n' "$remote_tags" | awk -F'\t' '$2 ~ /^v[0-9]+\.[0-9]+\.[0-9]+-beta[0-9]+$/ {
    split($2, p, /^v|\.|-beta/)
    printf "%06d.%06d.%06d.%06d\t%s\n", p[2], p[3], p[4], p[5], $2
  }' | sort | tail -1 | cut -f2)"
  [ -n "$staged_tag" ] || die "no staging tag (vX.Y.Z-betaN) on origin: release to staging first"
  commit="$(printf '%s\n' "$remote_tags" | awk -F'\t' -v t="$staged_tag" '$2 == t { print $1 }')"
  version="${staged_tag#v}"
  version="${version%-beta*}"
  git cat-file -e "$commit^{commit}" 2>/dev/null || git fetch --quiet origin "refs/tags/$staged_tag:refs/tags/$staged_tag" ||
    die "cannot fetch $staged_tag"
  ! tag_exists "v$version" || die "v$version already exists on origin: production already has this version"
  [ "$(version_at "$commit")" = "$version" ] || die "$staged_tag points at a commit whose package.json is not $version"
  changelog_has "$commit" "$version" || die "CHANGELOG.md has no '## [$version]' entry at $staged_tag"
  git merge-base --is-ancestor "$commit" "$remote_tip" || die "the staged commit ${commit:0:7} ($staged_tag) is not on origin/$default_branch"
  health="$(curl -fsS --max-time 20 "$STAGING_URL/health")" || die "cannot read $STAGING_URL/health"
  live="$(json_field "$health" commit)"
  [ -n "$live" ] || die "$STAGING_URL/health reports no commit"
  case "$live" in *[!0-9a-f]*) die "staging serves a value that is not a commit id: $live" ;; esac
  # A served id of 7 or more characters that starts the staged commit; anything else is another commit.
  case "$commit" in "$live"*) ;; *) die "staging serves $live, not the staged commit ${commit:0:7} ($staged_tag): restage before promoting" ;; esac
  [ "${#live}" -ge 7 ] || die "staging serves an id too short to name one commit: $live"
  tag="v$version"
  url="$PRODUCTION_URL"
  plan_tag="tag $tag (promotes $staged_tag)"
fi

short="$(git rev-parse --short=7 "$commit")"
# A tag left behind locally (an earlier failed push) would make the tag step fail after the deploy.
! git rev-parse -q --verify "refs/tags/$tag" > /dev/null ||
  die "the tag $tag already exists locally but not on origin: inspect it, then delete it with git"

say "Release plan"
echo "target $target"
echo "version $version"
echo "commit $commit"
echo "$plan_tag"
echo "url $url"
dirty="$(git status --porcelain --untracked-files=no | wc -l | tr -d ' ')"
[ "$dirty" -eq 0 ] || echo "note: $dirty uncommitted tracked file(s) in this checkout are NOT part of this release"

# ---- Runtime pin: the tools in use equal what the commit declares ----
pin_matches() { [ "$2" = "$1" ] || case "$2" in "$1".*) true ;; *) false ;; esac; }
check_pin() {
  local pkg pm nvm name want have
  pkg="$(git show "$commit:package.json")"
  pm="$(printf '%s\n' "$pkg" | sed -n 's/.*"packageManager"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
  nvm="$({ git show "$commit:.nvmrc" 2> /dev/null || true; } | tr -d '[:space:]' | sed 's/^v//')"
  [ -n "$pm$nvm" ] || die "no runtime pin at $short: declare packageManager in package.json or add .nvmrc"
  if [ -n "$pm" ]; then
    name="${pm%%@*}"; want="${pm#*@}"; want="${want%%+*}"
    have="$("$name" --version)" || die "cannot run '$name --version'"
    pin_matches "$want" "$have" || die "runtime pin: $name $have does not match the pinned $want"
    echo "pin ok: $name $have"
  fi
  if [ -n "$nvm" ]; then
    have="$(node --version | sed 's/^v//')" || die "cannot run 'node --version'"
    pin_matches "$nvm" "$have" || die "runtime pin: node $have does not match the pinned $nvm"
    echo "pin ok: node $have"
  fi
}
check_pin
[ "$check" -eq 0 ] || { echo; echo "guards passed (--check: nothing built or deployed)"; exit 0; }

# ---- Build and verify in a fresh checkout of the commit ----
export WRANGLER_SEND_METRICS=false CLOUDFLARE_ACCOUNT_ID="$ACCOUNT_ID"
export RELEASE_TARGET="$target" RELEASE_COMMIT="$commit"
run_dir="$root/.scratch/release/$tag-$(date +%Y%m%d-%H%M%S)"
work="$run_dir/worktree"
evidence="$run_dir/evidence"
mkdir -p "$evidence"
wrangler_err="$(mktemp "${TMPDIR:-/tmp}/release-wrangler.XXXXXX")"
cleanup() { rm -f "$wrangler_err"; git -C "$root" worktree remove --force "$work" 2> /dev/null || true; }
trap cleanup EXIT

say "Checkout of $short and a clean install"
git worktree add --quiet --detach "$work" "$commit"
cd "$work"
[ -x scripts/verify-live.sh ] || die "$short has no executable scripts/verify-live.sh: it predates this release flow"
PATH="$work/node_modules/.bin:$PATH"
npm ci --no-audit --no-fund < /dev/null

wrangler_env() { wrangler "$@" --env "$target"; }
# live_version: the version id serving 100% of the target Worker; fails when it cannot be read.
live_version() {
  local out
  out="$(wrangler_env deployments status --json 2> "$wrangler_err")" || return 1
  printf '%s' "$out" | tr -d ' \n\t' | tr '{' '\n' | { grep '"percentage":100[,}]' || true; } |
    sed -n 's/.*"version_id":"\([^"]*\)".*/\1/p' | head -1
}

say "Cloudflare account $ACCOUNT_ID"
whoami_out="$(wrangler whoami 2> "$wrangler_err")" || die "Cloudflare login check failed: $(cat "$wrangler_err")"
case "$whoami_out" in *"$ACCOUNT_ID"*) echo "account reachable" ;; *) die "logged in without access to the account $ACCOUNT_ID" ;; esac

say "Current $target deployment (the rollback target)"
previous=""
if previous="$(live_version)" && [ -n "$previous" ]; then
  echo "live version $previous"
elif grep -q "code: 10007" "$wrangler_err"; then
  echo "no $target Worker yet: this is its first deploy, so there is nothing to roll back to"
else
  die "cannot read the current deployment: $(cat "$wrangler_err")"
fi

say "Secrets on the $target Worker"
if [ "$REQUIRED_SECRETS" != none ]; then
  secrets_out="$(wrangler_env secret list --format json 2> "$wrangler_err")" ||
    { [ -z "$previous" ] && grep -q "not found" "$wrangler_err" && secrets_out="[]"; } ||
    die "cannot list secrets: $(cat "$wrangler_err")"
  flat="$(printf '%s' "$secrets_out" | tr -d ' \n\t')"
  missing=""
  for s in $REQUIRED_SECRETS; do
    case "$flat" in *"\"name\":\"$s\""*) ;; *) missing="$missing $s" ;; esac
  done
  [ -z "$missing" ] || die "missing secret(s) on the $target Worker:$missing"
  echo "secrets present: $REQUIRED_SECRETS"
else
  echo "no secrets required"
fi

say "Gates"
while IFS= read -r line; do
  [ -n "$line" ] || continue
  name="${line%%=*}"; cmd="${line#*=}"
  reason="$(waiver_reason "$name")"
  if [ -n "$reason" ]; then echo "WAIVED gate $name: $reason"; continue; fi
  echo "gate $name: $cmd"
  # stdin is closed so a gate cannot read the rest of the gate list.
  bash -c "$cmd" < /dev/null || die "gate $name failed ('$cmd'); fix it, or waive this one gate with --waive $name=<reason>"
done << GATE_LIST
$GATES
GATE_LIST

if [ "$dry" -eq 1 ]; then
  echo; echo "dry run passed: $tag ($short) verified; nothing deployed, no tag"
  exit 0
fi

if [ "$target" = production ] && [ "$yes" -eq 0 ]; then
  [ -t 0 ] || die "production needs --yes when not run from a terminal"
  read -r -p "Type 'production' to deploy $tag ($short) to $PRODUCTION_URL: " answer
  [ "$answer" = production ] || die "not confirmed"
fi

# ---- Deploy ----
say "Deploy $tag ($short) to $target"
wrangler_env deploy --tag "$tag" --message "$tag $short" \
  --var "APP_COMMIT:$commit" --var "APP_VERSION:$version" --var "APP_ENV:$target" 2>&1 | tee "$evidence/deploy.log"
deployed="$(live_version)" || die "deployed, but cannot read the new version: $(cat "$wrangler_err")"
echo "deployed version $deployed"

rollback_hint() {
  echo >&2
  echo "The live checks failed: $tag is deployed but NOT tagged. Investigate, or roll back:" >&2
  if [ -n "$previous" ]; then
    echo "  wrangler rollback $previous --env $target -m \"rollback $tag\" -y" >&2
  else
    echo "  first $target deploy: there is no earlier version; fix forward and release again" >&2
  fi
  echo "Evidence: $evidence" >&2
  exit 1
}

# ---- Live proof (retried: a first deploy to a new hostname waits for DNS and its certificate) ----
say "Live checks against $url"
attempts="${VERIFY_LIVE_ATTEMPTS:-18}"
delay="${VERIFY_LIVE_DELAY:-10}"
proved=0
n=0
while [ "$n" -lt "$attempts" ]; do
  n=$((n + 1))
  if EXPECT_COMMIT="$commit" EXPECT_VERSION="$version" scripts/verify-live.sh "$target" > "$evidence/verify-live.log" 2>&1; then proved=1; break; fi
  if [ "$n" -lt "$attempts" ]; then echo "verify-live attempt $n failed; retrying in ${delay}s"; sleep "$delay"; fi
done
cat "$evidence/verify-live.log"
[ "$proved" -eq 1 ] || rollback_hint

# ---- Tag (only after the proof; a pushed tag is never moved) ----
say "Tag $tag"
tag_failed=0
if git -C "$root" tag -a "$tag" "$commit" -m "$target release $tag ($short)" && git -C "$root" push --quiet origin "refs/tags/$tag"; then
  echo "pushed $tag"
else
  echo "release: $tag is live and passed its checks, but the tag was not pushed. Finish by hand:" >&2
  echo "  git tag -a $tag $commit -m '$target release $tag ($short)'; git push origin refs/tags/$tag" >&2
  tag_failed=1
fi

# ---- Evidence ----
waiver_json=""
while IFS= read -r line; do
  [ -n "$line" ] || continue
  waiver_json="$waiver_json${waiver_json:+,
    }{\"gate\": \"$(json_escape "${line%%=*}")\", \"reason\": \"$(json_escape "${line#*=}")\"}"
done << WAIVER_LIST
$waivers
WAIVER_LIST
if [ -n "$waiver_json" ]; then waiver_json="
    $waiver_json
  "; fi
cat > "$evidence/release.json" << JSON
{
  "target": "$target",
  "tag": "$tag",
  "version": "$version",
  "commit": "$commit",
  "deployedVersionId": "$deployed",
  "previousVersionId": "$previous",
  "waivers": [$waiver_json],
  "url": "$url",
  "releasedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
JSON
say "Released $tag to $target"
echo "release.json: $evidence/release.json"
cat "$evidence/release.json"
[ "$tag_failed" -eq 0 ] || exit 1
