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

# ---- Fake programs ----
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
  run) [ "$2" = "$FAKE_FAIL_GATE" ] && { echo "gate $2 failed" >&2; exit 1; } ;;
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
  FAKE_SECRETS="API_TOKEN"; FAKE_NODE_VERSION="v22.11.0"; FAKE_FAIL_GATE=""
  export FAKE_SECRETS FAKE_NODE_VERSION FAKE_FAIL_GATE
}
head_sha() { git -C "$work" rev-parse HEAD; }
commit_push() { git -C "$work" add -A && git -C "$work" commit -q -m "$1" && git -C "$work" push -q origin main; }

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
check "--check creates no worktree" test ! -e "$work/.scratch"
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
serve "$STAGING_URL" "$(head_sha)" staging
expect "a commit with no verify-live.sh is refused" 1 "verify-live.sh" -- staging
check "a missing proof deploys nothing" no_deploy
check "a missing proof leaves no tag" no_tags
new_repo noexec
git -C "$work" update-index --chmod=-x scripts/verify-live.sh && git -C "$work" commit -q -m "not executable" && git -C "$work" push -q origin main
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
