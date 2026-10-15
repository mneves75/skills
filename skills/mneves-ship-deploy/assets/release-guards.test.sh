#!/usr/bin/env bash
# Proves the guards of the reference release.sh and verify-live.sh without a network or a Cloudflare
# account. Each case builds a throwaway Git repository with a local bare remote, installs both reference
# scripts with fake values in place of their placeholders, and runs them against fake `wrangler`, `npm`,
# `node` and `curl` programs on PATH. The scripts themselves are real; only the programs they call at the
# edge are fake. A fake `curl` serves bodies from files, so no server runs and nothing leaves the machine.
#
# Usage: bash release-guards.test.sh        (needs bash 3.2+, git, sed, awk, tr)
# Run it from a checkout of the skill; it reads release.sh and verify-live.sh beside itself.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/release-guards.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT

# Keep the owner's Git configuration (signing, hooks, aliases) out of the throwaway repositories.
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=test GIT_AUTHOR_EMAIL=test@example.invalid
export GIT_COMMITTER_NAME=test GIT_COMMITTER_EMAIL=test@example.invalid

STAGING_URL="https://staging.example.test"
PRODUCTION_URL="https://app.example.test"
ACCOUNT="example-account-id"

export FAKE_STATE="$tmp/state" FAKE_WEB="$tmp/web"
mkdir -p "$tmp/bin" "$FAKE_STATE" "$FAKE_WEB"
export FAKE_ACCOUNT="$ACCOUNT" FAKE_SECRETS="API_TOKEN" FAKE_NODE_VERSION="v22.11.0" FAKE_FAIL_GATE=""
export VERIFY_LIVE_ATTEMPTS=1 VERIFY_LIVE_DELAY=1
REAL_CP="$(command -v cp)"
export REAL_CP FAKE_SWAP_RECORD=""
REAL_DATE="$(command -v date)"
export REAL_DATE FAKE_NOW="" FAKE_AFTER_BUILD=""

# ---- Fake programs ----
cat > "$tmp/bin/date" <<'FAKE'
#!/bin/bash
if [ "$*" = '-u +%Y-%m-%dT%H:%M:%SZ' ] && [ -n "$FAKE_NOW" ]; then
  if [ -n "$FAKE_AFTER_BUILD" ] && [ -f "$FAKE_STATE/build-finished" ]; then
    echo "$FAKE_AFTER_BUILD"
  else echo "$FAKE_NOW"; fi
else "$REAL_DATE" "$@"; fi
FAKE
cat > "$tmp/bin/cp" <<'FAKE'
#!/bin/bash
"$REAL_CP" "$@" || exit $?
if [ -n "$FAKE_SWAP_RECORD" ] && [ "$1" -ef "$FAKE_SWAP_RECORD" ]; then
  "$REAL_CP" "$FAKE_SWAP_RECORD.replacement" "$FAKE_SWAP_RECORD"
  printf '%s\n' "$2" > "$FAKE_STATE/snapshot-path"
fi
FAKE
cat > "$tmp/bin/wrangler" <<'FAKE'
#!/bin/bash
echo "wrangler $*" >> "$FAKE_STATE/calls.log"
env=""; prev=""
for a in "$@"; do [ "$prev" = --env ] && env="$a"; prev="$a"; done
live="$FAKE_STATE/live-$env"
case "$1" in
  whoami) echo "Account Name: test  Account ID: $FAKE_ACCOUNT" ;;
  deployments)
    v="ver-0"; [ -f "$live" ] && v="$(cat "$live")"
    printf '{\n  "id": "d1",\n  "versions": [\n    {\n      "version_id": "%s",\n      "percentage": 100\n    }\n  ]\n}\n' "$v" ;;
  secret)
    printf '['; sep=""
    for s in $FAKE_SECRETS; do printf '%s{"name":"%s","type":"secret_text"}' "$sep" "$s"; sep=","; done
    printf ']\n' ;;
  deploy)
    n=1; [ -f "$FAKE_STATE/count" ] && n=$(( $(cat "$FAKE_STATE/count") + 1 ))
    echo "$n" > "$FAKE_STATE/count"; echo "ver-$n" > "$live"; echo "Deployed ver-$n" ;;
  *) ;;
esac
FAKE
cat > "$tmp/bin/npm" <<'FAKE'
#!/bin/bash
echo "npm $*" >> "$FAKE_STATE/calls.log"
case "$1" in
  --version) echo "10.9.2" ;;
  run)
    [ "$2" = "$FAKE_FAIL_GATE" ] && { echo "gate $2 failed" >&2; exit 1; }
    [ "$2" != build ] || touch "$FAKE_STATE/build-finished" ;;
esac
exit 0
FAKE
cat > "$tmp/bin/node" <<'FAKE'
#!/bin/bash
echo "node $*" >> "$FAKE_STATE/calls.log"
[ "$1" = "--version" ] && echo "$FAKE_NODE_VERSION"
exit 0
FAKE
# curl: the body of a URL is the file named after it in $FAKE_WEB (scheme dropped, / ? & = as _); a
# sibling <name>.status sets the HTTP status (default 200). -f turns a status >= 400 into exit 22, and
# -w '%{http_code}' prints the status instead of the body.
cat > "$tmp/bin/curl" <<'FAKE'
#!/bin/bash
echo "curl $*" >> "$FAKE_STATE/calls.log"
url=""; fail=0; code=0; prev=""
for a in "$@"; do
  case "$a" in
    http://* | https://*) url="$a" ;;
    -*f*) case "$a" in --*) ;; *) fail=1 ;; esac ;;
  esac
  [ "$prev" = -w ] && code=1
  prev="$a"
done
key="$(printf '%s' "${url#*://}" | sed 's|[/?&=]|_|g')"
status=404; body=""
if [ -f "$FAKE_WEB/$key" ]; then
  status=200; [ -f "$FAKE_WEB/$key.status" ] && status="$(cat "$FAKE_WEB/$key.status")"; body="$(cat "$FAKE_WEB/$key")"
fi
if [ "$code" = 1 ]; then printf '%s' "$status"; exit 0; fi
if [ "$fail" = 1 ] && [ "$status" -ge 400 ]; then exit 22; fi
printf '%s\n' "$body"
FAKE
chmod +x "$tmp/bin/"*
export PATH="$tmp/bin:$PATH"

# ---- Helpers ----
failures=0
pass() { echo "PASS $1"; }
fail() { echo "FAIL $1"; shift; [ "$#" -eq 0 ] || printf '    | %s\n' "$@"; failures=$((failures + 1)); }

# install_scripts <dir>: the reference scripts with their placeholders replaced, as an adopter would.
install_scripts() {
  mkdir -p "$1/scripts"
  for f in release.sh verify-live.sh; do
    sed -e "s|__STAGING_URL__|$STAGING_URL|g" -e "s|__PRODUCTION_URL__|$PRODUCTION_URL|g" \
      -e "s|__ACCOUNT_ID__|$ACCOUNT|g" -e "s|__REQUIRED_SECRETS__|API_TOKEN|g" \
      "$here/$f" > "$1/scripts/$f"
    chmod +x "$1/scripts/$f"
  done
}

# new_repo <name>: a clone on main with a bare origin, one pushed commit, version 1.2.3, a CHANGELOG entry
# and a runtime pin. Sets $work and $origin.
new_repo() {
  origin="$tmp/$1.git"; work="$tmp/$1"
  git init -q --bare "$origin"
  git --git-dir="$origin" symbolic-ref HEAD refs/heads/main
  git init -q "$work"
  (
    cd "$work"
    git checkout -q -b main
    git remote add origin "$origin"
    install_scripts "$work"
    printf '{\n  "name": "demo",\n  "version": "1.2.3",\n  "packageManager": "npm@10.9.2"\n}\n' > package.json
    printf '22.11.0\n' > .nvmrc
    printf '# Changelog\n\n## [1.2.3] - 2026-01-01\n\n- first\n' > CHANGELOG.md
    printf '.scratch/\n' > .gitignore
    git add -A
    git commit -q -m "init"
    git push -q origin main
  )
  : > "$FAKE_STATE/calls.log"; rm -f "$FAKE_STATE"/live-* "$FAKE_STATE/count"
  rm -rf "$FAKE_WEB"; mkdir -p "$FAKE_WEB"
  FAKE_SECRETS="API_TOKEN"; FAKE_NODE_VERSION="v22.11.0"; FAKE_FAIL_GATE=""; FAKE_SWAP_RECORD=""
  FAKE_NOW=""; FAKE_AFTER_BUILD=""; rm -f "$FAKE_STATE/build-finished"
  export FAKE_SECRETS FAKE_NODE_VERSION FAKE_FAIL_GATE
  write_readiness staging
  write_readiness production
}
head_sha() { git -C "$work" rev-parse HEAD; }
commit_push() {
  git -C "$work" add -A && git -C "$work" commit -q -m "$1" && git -C "$work" push -q origin main
  write_readiness staging
  write_readiness production
}
write_readiness() {
  mkdir -p "$work/.scratch/readiness"
  cat > "$work/.scratch/readiness/$1.json" << JSON
{
  "schema": 1,
  "unit": ".",
  "target": "$1",
  "catalog": 1,
  "commit": "$(head_sha)",
  "verdict": "ready",
  "open_blockers": 0,
  "created_at": "2000-01-01T00:00:00Z",
  "valid_until": "9999-01-01T00:00:00Z",
  "waivers": []
}
JSON
}

# serve <base url> <commit> <env>: the health page and the two controls of a healthy deployment.
serve() {
  local key
  key="$(printf '%s' "${1#*://}" | sed 's|[/?&=]|_|g')"
  printf '{"status":"ok","commit":"%s","version":"1.2.3","env":"%s"}' "$2" "$3" > "$FAKE_WEB/${key}_health"
  printf '{"items":[1]}' > "$FAKE_WEB/${key}_api_items"
  printf '{"error":"unauthorized"}' > "$FAKE_WEB/${key}_api_admin"
  printf '401' > "$FAKE_WEB/${key}_api_admin.status"
}

out=""; code=0
# run <release.sh args...>: in $work, stdin closed; sets $out and $code.
run() {
  code=0
  out="$(cd "$work" && "$BASH" scripts/release.sh "$@" 2>&1 < /dev/null)" || code=$?
}
# expect <name> <exit code> <text the output must contain> -- <args...>
expect() {
  local name="$1" want="$2" text="$3"; shift 4
  run "$@"
  if [ "$code" = "$want" ] && printf '%s\n' "$out" | grep -F -- "$text" > /dev/null; then pass "$name"
  else fail "$name (exit $code, wanted $want and \"$text\")" "$out"; fi
}
log_has() { grep -E -- "$1" "$FAKE_STATE/calls.log" > /dev/null; }
remote_tags() { git -C "$work" ls-remote --tags origin; }
check() { # <name> <command...>: passes when the command succeeds
  local name="$1"; shift
  if "$@"; then pass "$name"; else fail "$name" "$out"; fi
}
no_deploy() { ! log_has '^wrangler deploy( |$)'; }
no_build() { ! log_has '^npm (ci|run)' && ! log_has '^wrangler'; }
# release_json: the evidence file of the last release in $work, or nothing.
release_json() { find "$work/.scratch" -name release.json 2> /dev/null | head -1 || true; }
no_tags() { [ -z "$(remote_tags)" ] && [ -z "$(git -C "$work" tag)" ]; }

set_readiness_expiries() {
  awk -v first="$2" -v last="$3" '/"waivers":/ {
    printf "  \"waivers\": [\n    {\n      \"expires\": \"%s\"\n    },\n    {\n      \"expires\": \"%s\"\n    }\n  ]\n", first, last
    next
  } { print }' "$1" > "$1.waivers"
  mv "$1.waivers" "$1"
}

# ==== Calendar validation for every timestamp source ====
for field in created_at valid_until expires; do
  for day in 2026-02-31 2026-04-31 2100-02-29 2028-02-29; do
    new_repo "calendar-$field-$day"
    record="$work/.scratch/readiness/staging.json"
    FAKE_NOW=2000-01-01T00:00:00Z
    if [ "$field" = created_at ]; then FAKE_NOW=2130-01-01T00:00:00Z; fi
    if [ "$field" = expires ]; then
      set_readiness_expiries "$record" "${day}T00:00:00Z" 9999-01-01T00:00:00Z
      problem='a readiness waiver has expired'
    else
      sed -i.bak "s/\"$field\": \"[^\"]*\"/\"$field\": \"${day}T00:00:00Z\"/" "$record"
      problem="$field"
    fi
    run staging --dry-run
    if [ "$day" = 2028-02-29 ]; then
      if [ "$code" = 0 ]; then pass "calendar accepts $field=$day"
      else fail "calendar accepts $field=$day (exit $code)" "$out"; fi
    elif [ "$code" = 1 ] && printf '%s' "$out" | grep -F "$problem" > /dev/null && no_build; then
      pass "calendar refuses $field=$day before build"
    else fail "calendar refuses $field=$day before build (exit $code)" "$out"; fi
  done
done

# ==== Expiry at the deploy boundary, without waiting for a real clock ====
for target_case in staging production; do
  for deadline_case in record boundary waiver-first waiver-last waived; do
    new_repo "deadline-$target_case-$deadline_case"
    serve "$STAGING_URL" "$(head_sha)" staging
    serve "$PRODUCTION_URL" "$(head_sha)" production
    if [ "$target_case" = production ]; then
      git -C "$work" tag -a v1.2.3-beta1 -m staged
      git -C "$work" push -q origin v1.2.3-beta1
    fi
    record="$work/.scratch/readiness/$target_case.json"
    FAKE_NOW=2026-10-15T12:00:01Z
    FAKE_AFTER_BUILD=2026-10-15T12:00:03Z
    case "$deadline_case" in
      record | boundary | waived)
        sed -i.bak 's/9999-01-01T00:00:00Z/2026-10-15T12:00:02Z/' "$record" ;;
      waiver-first) set_readiness_expiries "$record" 2026-10-15T12:00:02Z 9999-01-01T00:00:00Z ;;
      waiver-last) set_readiness_expiries "$record" 9999-01-01T00:00:00Z 2026-10-15T12:00:02Z ;;
    esac
    [ "$deadline_case" != boundary ] || FAKE_AFTER_BUILD=2026-10-15T12:00:02Z
    if [ "$deadline_case" = waived ]; then
      expect "$target_case waived readiness skips deploy deadline" 0 "Released" -- "$target_case" --yes --waive readiness=incident
    else
      run "$target_case" --yes
      if [ "$code" = 1 ] && printf '%s' "$out" | grep -F 'readiness record expired before deploy; run the readiness gate again' > /dev/null &&
        log_has '^npm run build$' && no_deploy && [ -z "$(release_json)" ]; then
        pass "$target_case refuses $deadline_case expiry after build before deploy"
      else fail "$target_case refuses $deadline_case expiry after build before deploy (exit $code)" "$out"; fi
    fi
  done
done

# ==== Readiness: refusal before installing, building, deploying or making a run directory ====
for defect in missing symlink directory malformed missing-key schema unit target commit short-sha future expired verdict blockers timestamp single-line duplicate invalid-created invalid-until expired-waiver malformed-waiver inline-waiver scratch-link readiness-link; do
  new_repo "readiness-$defect"
  record="$work/.scratch/readiness/staging.json"
  serve "$STAGING_URL" "$(head_sha)" staging
  problem="$defect"
  case "$defect" in
    missing) rm "$record"; problem=missing ;;
    symlink) mv "$record" "$record.real"; ln -s "$record.real" "$record" ;;
    directory) rm "$record"; mkdir "$record"; problem=regular ;;
    malformed) sed -i.bak 's/"schema": 1/"schema": nope/' "$record"; problem=schema ;;
    missing-key) sed -i.bak '/"catalog"/d' "$record"; problem=catalog ;;
    schema) sed -i.bak 's/"schema": 1/"schema": 2/' "$record" ;;
    unit) sed -i.bak 's/"unit": "."/"unit": "app"/' "$record" ;;
    target) sed -i.bak 's/"target": "staging"/"target": "production"/' "$record" ;;
    commit) sed -i.bak "s/$(head_sha)/$(printf '%040d' 0)/" "$record" ;;
    short-sha) sed -i.bak "s/$(head_sha)/$(head_sha | cut -c1-7)/" "$record"; problem=commit ;;
    future) sed -i.bak 's/2000-01-01/9999-01-01/' "$record"; problem=created_at ;;
    expired) sed -i.bak 's/9999-01-01/2000-01-01/' "$record"; problem=valid_until ;;
    verdict) sed -i.bak 's/"ready"/"not-ready"/' "$record" ;;
    blockers) sed -i.bak 's/"open_blockers": 0/"open_blockers": 1/' "$record"; problem=open_blockers ;;
    timestamp) sed -i.bak 's/2000-01-01T00:00:00Z/yesterday/' "$record"; problem=created_at ;;
    single-line) tr -d '\n' < "$record" > "$record.flat"; mv "$record.flat" "$record"; problem=record ;;
    invalid-created) sed -i.bak 's/2000-01-01T00:00:00Z/2000-13-45T25:61:61Z/' "$record"; problem=created_at ;;
    invalid-until) sed -i.bak 's/9999-01-01T00:00:00Z/9999-99-99T99:99:99Z/' "$record"; problem=valid_until ;;
    expired-waiver | malformed-waiver)
      expiry=2001-01-01T00:00:00Z
      [ "$defect" != malformed-waiver ] || expiry=9999-99-99T99:99:99Z
      awk -v expiry="$expiry" '/"waivers":/ {
        printf "  \"waivers\": [{\n    \"expires\": \"%s\"\n  }]\n", expiry; next
      } { print }' "$record" > "$record.waivers"
      mv "$record.waivers" "$record"
      problem='a readiness waiver has expired' ;;
    inline-waiver)
      sed -i.bak 's/"waivers": \[\]/"waivers": [{"control": "BR-02", "owner": "@o", "reason": "r", "expires": "2001-01-01T00:00:00Z"}]/' "$record"
      problem='waiver fields must sit on their own lines' ;;
    scratch-link) mv "$work/.scratch" "$work/scratch-real"; ln -s "$work/scratch-real" "$work/.scratch"; problem=symlink ;;
    readiness-link) mv "$work/.scratch/readiness" "$work/.scratch/readiness-real"; ln -s "$work/.scratch/readiness-real" "$work/.scratch/readiness"; problem=symlink ;;
    duplicate) sed -i.bak 's/"schema": 1,/"schema": 1,\
  "schema": 1,/' "$record"; problem=schema ;;
  esac
  run staging
  if [ "$code" = 1 ] && printf '%s' "$out" | grep -F "$problem" > /dev/null &&
    printf '%s' "$out" | grep -F "run the readiness gate for staging on $(head_sha | cut -c1-7)" > /dev/null &&
    printf '%s' "$out" | grep -F -- '--waive readiness=<reason>' > /dev/null &&
    no_build && no_tags && [ ! -e "$work/.scratch/release" ]; then
    pass "readiness refuses $defect before build with remediation"
  else fail "readiness refuses $defect before build with remediation (exit $code)" "$out"; fi
done

new_repo readiness-reserved
sed -i.bak 's/GATES="lint=/GATES="readiness=true\
lint=/' "$work/scripts/release.sh"
expect "readiness is reserved even when waived" 2 'readiness is reserved' -- staging --check --waive readiness=incident
check "reserved readiness gate builds nothing" no_build

new_repo readiness-line-format
record="$work/.scratch/readiness/staging.json"
sed 's/"schema": 1,/"schema": 1/' "$record" | awk '{ printf "%s\r\n", $0 }' > "$record.lines"
mv "$record.lines" "$record"
expect "line reader accepts CRLF and optional commas" 0 'readiness: ready' -- staging --check

new_repo readiness-valid
serve "$STAGING_URL" "$(head_sha)" staging
expect "--check reports ready" 0 'readiness: ready (valid until 9999-01-01T00:00:00Z)' -- staging --check
run staging
json="$(release_json)"
if [ "$code" = 0 ] && [ -f "$json" ] &&
  grep -F '"readiness": {"status": "ready", "record": "readiness.json", "valid_until": "9999-01-01T00:00:00Z"}' "$json" > /dev/null &&
  cmp "$work/.scratch/readiness/staging.json" "$(dirname "$json")/readiness.json"; then
  pass "valid readiness deploys and preserves the record and summary"
else fail "valid readiness deploys and preserves the record and summary" "$out"; fi

new_repo readiness-waived
rm "$work/.scratch/readiness/staging.json"
serve "$STAGING_URL" "$(head_sha)" staging
expect "--check reports NOT READY without failing" 0 'readiness: NOT READY:' -- staging --check
expect "--check reports WAIVED" 0 'readiness: WAIVED: incident' -- staging --check --waive readiness=incident
check "readiness --check statuses build nothing" no_build
run staging --waive readiness=incident
json="$(release_json)"
if [ "$code" = 0 ] && [ -f "$json" ] &&
  printf '%s' "$out" | grep -F 'WAIVED readiness: incident' > /dev/null &&
  grep -F '"readiness": {"status": "waived", "reason": "incident"}' "$json" > /dev/null &&
  grep -F '{"gate": "readiness", "reason": "incident"}' "$json" > /dev/null; then
  pass "readiness waiver deploys without a record and records the reason"
else fail "readiness waiver deploys without a record and records the reason" "$out"; fi

for initial in ready expired; do
  new_repo "readiness-snapshot-$initial"
  serve "$STAGING_URL" "$(head_sha)" staging
  record="$work/.scratch/readiness/staging.json"
  cp "$record" "$record.expected"
  cp "$record" "$record.replacement"
  if [ "$initial" = ready ]; then
    sed -i.bak 's/9999-01-01/2000-01-01/' "$record.replacement"
  else
    sed -i.bak 's/9999-01-01/2000-01-01/' "$record"
  fi
  FAKE_SWAP_RECORD="$record"
  run staging
  FAKE_SWAP_RECORD=""
  json="$(release_json)"
  if [ "$initial" = ready ]; then
    if [ "$code" = 0 ] && [ -f "$json" ] &&
      cmp "$record.expected" "$(dirname "$json")/readiness.json" &&
      [ -f "$FAKE_STATE/snapshot-path" ] && [ ! -e "$(cat "$FAKE_STATE/snapshot-path")" ]; then
      pass "readiness validates and preserves the private snapshot despite source replacement"
    else fail "readiness validates and preserves the private snapshot despite source replacement" "$out"; fi
  elif [ "$code" = 1 ] && printf '%s' "$out" | grep -F 'valid_until' > /dev/null && no_build &&
    [ -f "$FAKE_STATE/snapshot-path" ] && [ ! -e "$(cat "$FAKE_STATE/snapshot-path")" ]; then
    pass "readiness refuses an expired snapshot despite a valid source replacement"
  else fail "readiness refuses an expired snapshot despite a valid source replacement" "$out"; fi
done

# ==== Usage and flags ====
new_repo usage
expect "no arguments prints usage" 2 "usage:" --
expect "an unknown target prints usage" 2 "usage:" -- prod --check
for flag in --skip-checks --skip-gates --no-verify --force; do
  expect "a blanket bypass ($flag) is rejected" 2 "usage:" -- staging --check "$flag"
done
expect "--waive without a reason is rejected" 2 "usage:" -- staging --check --waive lint
expect "--waive with an empty reason is rejected" 2 "reason" -- staging --check --waive "lint="
expect "--waive of an unknown gate is rejected" 2 "unknown gate" -- staging --check --waive "bogus=because"

# ==== Placeholders ====
new_repo raw
cp "$here/release.sh" "$work/scripts/release.sh"
expect "a placeholder left in the script stops the release" 1 "placeholder" -- staging --check

# ==== --check ====
new_repo check
sha="$(head_sha)"
expect "--check plans the release" 0 "tag v1.2.3-beta1" -- staging --check
for line in "target staging" "version 1.2.3" "commit $sha" "url $STAGING_URL"; do
  expect "--check prints '${line%% *}'" 0 "$line" -- staging --check
done
check "--check builds nothing and deploys nothing" no_build
check "--check creates no worktree" test ! -e "$work/.scratch/release"
git -C "$work" tag v1.2.3-beta1 && git -C "$work" push -q origin v1.2.3-beta1 && git -C "$work" tag -d v1.2.3-beta1 > /dev/null
expect "the beta number follows the tags origin has" 0 "tag v1.2.3-beta2" -- staging --check

# ==== Staging guards ====
new_repo guards
git -C "$work" commit -q --allow-empty -m "local only"
expect "staging refuses a HEAD that is not pushed" 1 "HEAD is not pushed" -- staging --check
git -C "$work" reset -q --hard origin/main
printf '# Changelog\n' > "$work/CHANGELOG.md"; commit_push "drop the entry"
expect "staging refuses a version with no changelog entry" 1 "CHANGELOG.md has no" -- staging --check
git -C "$work" revert --no-edit HEAD > /dev/null && git -C "$work" push -q origin main
git -C "$work" tag v1.2.3 && git -C "$work" push -q origin v1.2.3 && git -C "$work" tag -d v1.2.3 > /dev/null
expect "staging refuses a version production already has" 1 "bump the version" -- staging --check
git -C "$work" push -q origin :refs/tags/v1.2.3
FAKE_NODE_VERSION="v20.0.0"
expect "a runtime that differs from the pin is refused" 1 "does not match the pinned" -- staging --check
FAKE_NODE_VERSION="v22.11.0"
rm "$work/.nvmrc"; sed -i.bak '/packageManager/d; s/"version": "1.2.3",/"version": "1.2.3"/' "$work/package.json"; rm -f "$work/package.json.bak"
commit_push "drop the pin"
expect "a repository with no declared runtime pin is refused" 1 "no runtime pin" -- staging --check

# ==== Production guards ====
new_repo prod
sha="$(head_sha)"
serve "$STAGING_URL" "$sha" staging
expect "production refuses without a staging tag" 1 "no staging tag" -- production --check
git -C "$work" tag v1.2.3-beta1 && git -C "$work" push -q origin v1.2.3-beta1
expect "production promotes the commit staging serves (control)" 0 "tag v1.2.3 (promotes v1.2.3-beta1)" -- production --check
expect "production plans the staged commit" 0 "commit $sha" -- production --check
serve "$STAGING_URL" "abcdef1234567" staging
expect "production refuses when staging serves another commit" 1 "staging serves abcdef1" -- production --check
serve "$STAGING_URL" "${sha}-dirty" staging
expect "production refuses a dirty staging build" 1 "is not a commit id" -- production --check
serve "$STAGING_URL" "$sha" staging
git -C "$work" tag v1.2.3 && git -C "$work" push -q origin v1.2.3
expect "production refuses a version that already has its tag" 1 "already exists on origin" -- production --check
git -C "$work" push -q origin :refs/tags/v1.2.3 && git -C "$work" tag -d v1.2.3 > /dev/null
expect "production without --yes and without a terminal is refused" 1 "needs --yes" -- production

# ==== A whole staging release ====
new_repo staging
sha="$(head_sha)"
serve "$STAGING_URL" "$sha" staging
expect "staging releases a pushed commit" 0 "Released v1.2.3-beta1" -- staging
check "the tag is pushed after the live proof" test -n "$(remote_tags | grep 'refs/tags/v1.2.3-beta1')"
json="$(release_json)"
for field in '"target": "staging"' '"tag": "v1.2.3-beta1"' '"version": "1.2.3"' "\"commit\": \"$sha\"" \
  '"deployedVersionId": "ver-1"' '"previousVersionId": "ver-0"' '"waivers": []' "\"url\": \"$STAGING_URL\""; do
  if [ -f "$json" ] && grep -F -- "$field" "$json" > /dev/null; then pass "release.json records $field"; else fail "release.json records $field" "$out"; fi
done
check "every gate ran" log_has '^npm run lint'
check "the deploy is the target's own environment" log_has '^wrangler deploy .*--env staging( |$)'

# ==== A waiver ====
new_repo waive
sha="$(head_sha)"
serve "$STAGING_URL" "$sha" staging
expect "--waive lint=<reason> is accepted" 0 "WAIVED gate lint: ticket 7 is flaky" -- staging --waive "lint=ticket 7 is flaky"
json="$(release_json)"
if [ -f "$json" ] && grep -F '{"gate": "lint", "reason": "ticket 7 is flaky"}' "$json" > /dev/null; then pass "release.json records the waiver"
else fail "release.json records the waiver" "$out"; fi
check "the waived gate did not run" sh -c "! grep -E '^npm run lint' '$FAKE_STATE/calls.log'"
for gate in typecheck test build; do check "the other gate $gate still ran" log_has "^npm run $gate"; done

# ==== A failing gate ====
new_repo gate
serve "$STAGING_URL" "$(head_sha)" staging
FAKE_FAIL_GATE="test"; export FAKE_FAIL_GATE
expect "a failing gate stops the release" 1 "gate test failed" -- staging
check "a failing gate deploys nothing" no_deploy
check "a failing gate leaves no tag" no_tags

# ==== --dry-run ====
new_repo dry
serve "$STAGING_URL" "$(head_sha)" staging
expect "--dry-run runs the gates and stops" 0 "dry run passed" -- staging --dry-run
check "--dry-run deploys nothing" no_deploy
check "--dry-run leaves no tag" no_tags

# ==== Target parity ====
new_repo parity
serve "$STAGING_URL" "$(head_sha)" staging
FAKE_SECRETS=""; export FAKE_SECRETS
expect "a secret missing on the target stops the release" 1 "missing secret" -- staging
check "a missing secret deploys nothing" no_deploy
FAKE_SECRETS="API_TOKEN"; export FAKE_SECRETS
FAKE_ACCOUNT="other-account-id"; export FAKE_ACCOUNT
expect "a login without the account stops the release" 1 "account" -- staging
FAKE_ACCOUNT="$ACCOUNT"; export FAKE_ACCOUNT
check "a wrong account deploys nothing" no_deploy

# ==== A failing live proof ====
new_repo live
serve "$STAGING_URL" "0000000000000000000000000000000000000000" staging
expect "a failing verify-live fails the release" 1 "NOT tagged" -- staging
check "a failing verify-live leaves no tag" no_tags
if printf '%s\n' "$out" | grep -F 'wrangler rollback ver-0 --env staging' > /dev/null; then pass "the rollback command names the version it replaced"
else fail "the rollback command names the version it replaced" "$out"; fi
check "a failing verify-live writes no release.json" test -z "$(release_json)"

# ==== A whole production release ====
new_repo promote
sha="$(head_sha)"
serve "$STAGING_URL" "$sha" staging
serve "$PRODUCTION_URL" "$sha" production
git -C "$work" tag -a v1.2.3-beta1 -m staged && git -C "$work" push -q origin v1.2.3-beta1
expect "production releases the commit staging serves" 0 "Released v1.2.3 to production" -- production --yes
check "the production tag is pushed" test -n "$(remote_tags | grep -F 'refs/tags/v1.2.3^{}')"
check "the deploy is the production environment" log_has '^wrangler deploy .*--env production( |$)'
git -C "$work" tag -a v1.2.3 -m again 2> /dev/null || true

# ==== verify-live.sh on its own (read-only; the same script serves a schedule and an agent) ====
new_repo live2
sha="$(head_sha)"
vl() { code=0; out="$(cd "$work" && "$BASH" scripts/verify-live.sh "$@" 2>&1 < /dev/null)" || code=$?; }
vl_expect() { # <name> <exit code> <text> -- <args>
  local name="$1" want="$2" text="$3"; shift 4
  vl "$@"
  if [ "$code" = "$want" ] && printf '%s\n' "$out" | grep -F -- "$text" > /dev/null; then pass "$name"
  else fail "$name (exit $code, wanted $want and \"$text\")" "$out"; fi
}
vl_expect "verify-live without a target prints usage" 2 "usage:" --
serve "$STAGING_URL" "$sha" staging
vl_expect "verify-live passes on a healthy target (control)" 0 "all assertions passed" -- staging
export EXPECT_COMMIT="${sha:0:7}"
vl_expect "verify-live accepts a released commit given as a short id" 0 "all assertions passed" -- staging
export EXPECT_COMMIT="1111111111111111111111111111111111111111"
vl_expect "verify-live fails when another commit is served" 1 "served commit is the released commit" -- staging
unset EXPECT_COMMIT
serve "$STAGING_URL" "$sha" production
vl_expect "verify-live fails when the target answers as another environment" 1 "wiring" -- staging
printf '{"commit":"%s","env":"staging"}' "$sha" > "$FAKE_WEB/staging.example.test_health"
vl_expect "verify-live fails on a 2xx health body without its fields" 1 "health body says status ok" -- staging
serve "$STAGING_URL" "$sha" staging
printf '{"items":[1]}' > "$FAKE_WEB/staging.example.test_api_admin"; rm -f "$FAKE_WEB/staging.example.test_api_admin.status"
vl_expect "verify-live fails when the request that must be refused succeeds" 1 "is refused" -- staging
serve "$STAGING_URL" "$sha" staging
printf '{}' > "$FAKE_WEB/staging.example.test_api_items"
vl_expect "verify-live fails when the success control has no real data" 1 "real data" -- staging
cp "$here/verify-live.sh" "$tmp/verify-live-raw.sh"
code=0; out="$("$BASH" "$tmp/verify-live-raw.sh" staging 2>&1 < /dev/null)" || code=$?
if [ "$code" = 1 ] && printf '%s\n' "$out" | grep -F placeholder > /dev/null; then pass "verify-live refuses to run with a placeholder left"
else fail "verify-live refuses to run with a placeholder left" "$out"; fi
: > "$FAKE_STATE/calls.log"; serve "$STAGING_URL" "$sha" staging; vl staging
if ! grep -E '^(wrangler|npm|node)' "$FAKE_STATE/calls.log" > /dev/null && ! grep -E 'curl .*(-X|--request|-d |--data)' "$FAKE_STATE/calls.log" > /dev/null; then pass "verify-live only reads"
else fail "verify-live only reads" "$(cat "$FAKE_STATE/calls.log")"; fi

# ==== The header names the Wrangler surface the script relies on ====
header="$(sed -n '1,/^set -euo pipefail/p' "$here/release.sh")"
for needle in 'deployments status --json' 'version_id' 'percentage' 'secret list --format json' 'deploy --var KEY:VALUE' '--tag' '--message' 'rollback <id> -m "<message>" -y'; do
  if printf '%s\n' "$header" | grep -F -- "$needle" > /dev/null; then pass "release.sh header names $needle"
  else fail "release.sh header names $needle"; fi
done

# ==== The retry variables cannot skip the proof (attempts 0, non-numbers, delay) ====
new_repo retry
serve "$STAGING_URL" "$(head_sha)" staging
for bad in 0 abc -1 1.5 " 2"; do
  : > "$FAKE_STATE/calls.log"
  VERIFY_LIVE_ATTEMPTS="$bad" run staging
  if [ "$code" = 1 ] && printf '%s\n' "$out" | grep -F 'VERIFY_LIVE_ATTEMPTS' > /dev/null && no_deploy && no_tags; then pass "VERIFY_LIVE_ATTEMPTS='$bad' is refused before anything is deployed"
  else fail "VERIFY_LIVE_ATTEMPTS='$bad' is refused before anything is deployed (exit $code)" "$out"; fi
done
for bad in 0 abc -3 2.5; do
  : > "$FAKE_STATE/calls.log"
  VERIFY_LIVE_DELAY="$bad" run staging
  if [ "$code" = 1 ] && printf '%s\n' "$out" | grep -F 'VERIFY_LIVE_DELAY' > /dev/null && no_deploy && no_tags; then pass "VERIFY_LIVE_DELAY='$bad' is refused before anything is deployed"
  else fail "VERIFY_LIVE_DELAY='$bad' is refused before anything is deployed (exit $code)" "$out"; fi
done
VERIFY_LIVE_ATTEMPTS=2 VERIFY_LIVE_DELAY=1 run staging
if [ "$code" = 0 ]; then pass "valid retry variables run the release (control)"; else fail "valid retry variables run the release (control)" "$out"; fi

# ==== A missing or non-executable proof stops the release before the deploy ====
new_repo noproof
serve "$STAGING_URL" "$(head_sha)" staging
git -C "$work" rm -q scripts/verify-live.sh && git -C "$work" commit -q -m "drop the proof" && git -C "$work" push -q origin main
write_readiness staging
serve "$STAGING_URL" "$(head_sha)" staging
expect "a commit with no verify-live.sh is refused" 1 "verify-live.sh" -- staging
check "a missing proof deploys nothing" no_deploy
check "a missing proof leaves no tag" no_tags
new_repo noexec
git -C "$work" update-index --chmod=-x scripts/verify-live.sh && git -C "$work" commit -q -m "not executable" && git -C "$work" push -q origin main
write_readiness staging
serve "$STAGING_URL" "$(head_sha)" staging
expect "a verify-live.sh that is not executable is refused" 1 "executable" -- staging
check "a non-executable proof deploys nothing" no_deploy

# ==== A waiver reason with control characters still yields valid JSON ====
valid_json() {
  if command -v python3 > /dev/null; then python3 -m json.tool "$1" > /dev/null 2>&1; return; fi
  if grep -q "$(printf '\t')" "$1"; then return 1; fi
}
n=0
for reason in "$(printf 'tab\there')" "$(printf 'bell\001and\033esc')" 'quote " and back\slash' "$(printf 'cr\rlf')"; do
  n=$((n + 1)); new_repo "ctl$n"
  serve "$STAGING_URL" "$(head_sha)" staging
  run staging --waive "lint=$reason"
  json="$(release_json)"
  if [ "$code" = 0 ] && [ -f "$json" ] && valid_json "$json"; then pass "release.json is valid JSON for the waiver reason $(printf '%s' "$reason" | od -An -c | tr -s ' ' | head -c 40)"
  else fail "release.json is valid JSON for a waiver reason with control characters (exit $code)" "$out" "$([ -f "$json" ] && cat "$json")"; fi
done
new_repo ctlmsg
serve "$STAGING_URL" "$(head_sha)" staging
run staging --waive "lint=$(printf 'a\tb')"
json="$(release_json)"
if [ -f "$json" ] && grep -F '"reason": "a b"' "$json" > /dev/null; then pass "a tab in a waiver reason becomes a space"
else fail "a tab in a waiver reason becomes a space" "$out"; fi

# ==== scripts/release.env keeps project values out of the committed script ====
# use_env_file: install the scripts raw (placeholders intact) and put the values in an ignored release.env.
use_env_file() {
  cp "$here/release.sh" "$work/scripts/release.sh"; cp "$here/verify-live.sh" "$work/scripts/verify-live.sh"
  chmod +x "$work/scripts/release.sh" "$work/scripts/verify-live.sh"
  printf '.scratch/\nscripts/release.env\n' > "$work/.gitignore"
  commit_push "raw scripts"
  printf 'STAGING_URL="%s"\nPRODUCTION_URL="%s"\nACCOUNT_ID="%s"\nREQUIRED_SECRETS="API_TOKEN"\n' "$STAGING_URL" "$PRODUCTION_URL" "$ACCOUNT" > "$work/scripts/release.env"
}
new_repo envfile
use_env_file
sha="$(head_sha)"
serve "$STAGING_URL" "$sha" staging
check "release.env is ignored by Git" test -z "$(git -C "$work" status --porcelain)"
expect "placeholders in the committed script are filled from scripts/release.env" 0 "Released v1.2.3-beta1" -- staging
check "the release deployed with the values of release.env" log_has '^wrangler deploy .*--env staging( |$)'
rm -f "$work/scripts/release.env"
expect "placeholders with no scripts/release.env are still refused" 1 "placeholder" -- staging --check
code=0; out="$(cd "$work" && "$BASH" scripts/verify-live.sh staging 2>&1 < /dev/null)" || code=$?
if [ "$code" = 1 ] && printf '%s\n' "$out" | grep -F placeholder > /dev/null; then pass "verify-live.sh with placeholders and no release.env is still refused"
else fail "verify-live.sh with placeholders and no release.env is still refused" "$out"; fi
printf 'STAGING_URL="%s"\nPRODUCTION_URL="%s"\n' "$STAGING_URL" "$PRODUCTION_URL" > "$work/scripts/release.env"
code=0; out="$(cd "$work" && "$BASH" scripts/verify-live.sh staging 2>&1 < /dev/null)" || code=$?
if [ "$code" = 0 ]; then pass "verify-live.sh reads its URLs from scripts/release.env"
else fail "verify-live.sh reads its URLs from scripts/release.env" "$out"; fi

# ==== --check says what is true ====
new_repo checkline
run staging --check
if printf '%s\n' "$out" | grep -F 'nothing built, deployed or tagged' > /dev/null && printf '%s\n' "$out" | grep -F 'remote was fetched' > /dev/null; then pass "--check says nothing is built, deployed or tagged and that the remote is fetched"
else fail "--check says nothing is built, deployed or tagged and that the remote is fetched" "$out"; fi
if printf '%s\n' "$out" | grep -F 'nothing built or deployed)' > /dev/null; then fail "--check no longer claims it only builds nothing"; else pass "--check no longer claims it only builds nothing"; fi

# ==== The header is honest about what the script asserts ====
header="$(sed -n '1,/^set -euo pipefail/p' "$here/release.sh")"
for needle in 'scripts/release.env' 'git-ignored' 'RELEASE_TARGET' 'gate of its own' 'fetch'; do
  if printf '%s\n' "$header" | grep -F -- "$needle" > /dev/null; then pass "release.sh header says: $needle"
  else fail "release.sh header says: $needle"; fi
done
if printf '%s\n' "$header" | grep -F 'a build per target' > /dev/null; then fail "release.sh header no longer claims 'a build per target'"; else pass "release.sh header no longer claims 'a build per target'"; fi
vheader="$(sed -n '1,/^set -euo pipefail/p' "$here/verify-live.sh")"
if printf '%s\n' "$vheader" | grep -F 'scripts/release.env' > /dev/null; then pass "verify-live.sh header names scripts/release.env"; else fail "verify-live.sh header names scripts/release.env"; fi

# ==== A pushed tag is never moved, deleted or force-pushed ====
# tag_hazard <file>: succeeds when the file's code (comments excluded) force-moves or deletes a tag or force-pushes.
tag_hazard() {
  grep -v '^[[:space:]]*#' "$1" | grep -E \
    -e 'git[^|;&]*[[:space:]]tag[[:space:]]([^|;&]*[[:space:]])?(-[a-zA-Z]*[fd][a-zA-Z]*|--force|--delete)([[:space:]]|$)' \
    -e '\+refs/tags/' \
    -e 'push[^|;&]*[[:space:]"'"'"']:refs/tags/' \
    -e 'push[^|;&]*(--force|--delete|--prune)' \
    -e 'push[^|;&]*[[:space:]]-[a-zA-Z]*f([[:space:]]|$)' > /dev/null
}
while IFS= read -r variant; do
  printf '#!/usr/bin/env bash\n%s\n' "$variant" > "$tmp/hazard.sh"
  if tag_hazard "$tmp/hazard.sh"; then pass "the tag guard catches: $variant"; else fail "the tag guard catches: $variant"; fi
done << 'HAZARDS'
git tag -f v1 HEAD
git tag -a -f v1 HEAD -m x
git tag --force v1 HEAD
git -C "$root" tag -fa "$tag" "$commit"
git tag -d v1
git tag --delete v1
git push origin +refs/tags/v1
git push origin "+refs/tags/$tag"
git push origin :refs/tags/v1
git push origin ":refs/tags/$tag"
git push --delete origin v1
git push --force origin main
git push -f origin v1
git push --force-with-lease origin v1
HAZARDS
while IFS= read -r clean; do
  printf '#!/usr/bin/env bash\n%s\n' "$clean" > "$tmp/clean.sh"
  if tag_hazard "$tmp/clean.sh"; then fail "the tag guard leaves alone: $clean"; else pass "the tag guard leaves alone: $clean"; fi
done << 'CLEAN'
git -C "$root" tag -a "$tag" "$commit" -m "release"
git push --quiet origin "refs/tags/$tag"
git fetch --quiet origin "refs/tags/$t:refs/tags/$t"
# git tag -f is only a comment here
git tag --list
CLEAN
if tag_hazard "$here/release.sh"; then fail "release.sh never moves, deletes or force-pushes a tag"
else pass "release.sh never moves, deletes or force-pushes a tag"; fi

if [ "$failures" -ne 0 ]; then echo "release guard tests FAILED ($failures)"; exit 1; fi
echo "release guard tests passed"
