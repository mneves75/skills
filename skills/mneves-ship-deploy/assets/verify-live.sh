#!/usr/bin/env bash
# Reference scripts/verify-live.sh for ONE Cloudflare Worker. It follows references/release-contract.md.
#
#   scripts/verify-live.sh <staging|production>
#
# Read-only: it sends GET requests and prints PASS or FAIL per assertion, and exits 0 only when every
# assertion holds. The same script serves the release (after a deploy), a schedule between deploys
# and an agent at the start of a session. It asserts:
#   served commit   /health reports the commit being released (EXPECT_COMMIT; without it, a well-formed id)
#   health body     /health answers {"status":"ok","commit":...,"version":...,"env":...}, not just a 2xx
#   two controls    one request that must succeed with real data, one that must be refused
#   wiring          /health reports env equal to the target, so a target that inherited another
#                   environment's routes or variables fails here
# EXPECT_VERSION, when set, must equal the version /health reports. release.sh sets both.
#
# A Worker with cron triggers must add an assertion that the platform's schedules for the target
# match wrangler's `triggers.crons`; a design that depends on a service binding adds one for the
# transport it reports (for example a response header). Neither applies to this reference.
#
# Install: replace the __PLACEHOLDERS__ (the same URLs as release.sh) and edit the ADAPT block.
# Needs bash 3.2+, curl, sed and tr.
set -euo pipefail

usage="usage: scripts/verify-live.sh <staging|production>"
target="${1:-}"
case "$target" in staging | production) ;; *) echo "$usage" >&2; exit 2 ;; esac
[ "$#" -eq 1 ] || { echo "$usage" >&2; exit 2; }

# ---- ADAPT ----
STAGING_URL="__STAGING_URL__"
PRODUCTION_URL="__PRODUCTION_URL__"
HEALTH_PATH="/health"
DATA_PATH="/api/items"        # must answer 200 and contain DATA_EXPECT
DATA_EXPECT='"items"'
REFUSED_PATH="/api/admin"     # must be refused with REFUSED_STATUS
REFUSED_STATUS="401"

for pair in "STAGING_URL=$STAGING_URL" "PRODUCTION_URL=$PRODUCTION_URL"; do
  case "${pair#*=}" in
    *__[A-Z]*__*) echo "verify-live: ${pair%%=*} still holds a placeholder (${pair#*=}): edit the ADAPT block of this script" >&2; exit 1 ;;
  esac
done
if [ "$target" = staging ]; then base="$STAGING_URL"; else base="$PRODUCTION_URL"; fi

failures=0
check() { # <name> <ok: 0|1> [detail]
  if [ "$2" -eq 1 ]; then echo "PASS $1${3:+: $3}"; else echo "FAIL $1${3:+: $3}"; failures=$((failures + 1)); fi
}
json_field() { printf '%s' "$1" | tr -d '\n' | sed -n "s/.*\"$2\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p"; }
ok_if() { if "$@"; then echo 1; else echo 0; fi; }
is_commit_id() { case "$1" in "" | *[!0-9a-f]*) return 1 ;; esac; [ "${#1}" -ge 7 ]; }

echo "verify-live: $target at $base"

# ---- Health body and served commit ----
if health="$(curl -fsS --max-time 20 "$base$HEALTH_PATH" 2>&1)"; then
  check "health answers 2xx" 1 "$base$HEALTH_PATH"
  status="$(json_field "$health" status)"; commit="$(json_field "$health" commit)"
  version="$(json_field "$health" version)"; env_name="$(json_field "$health" env)"
  check "health body says status ok" "$(ok_if [ "$status" = ok ])" "status '$status'"
  check "health body carries a commit id" "$(ok_if is_commit_id "$commit")" "commit '$commit'"
  if [ -n "${EXPECT_COMMIT:-}" ]; then
    # Either side may be the shorter id, but never shorter than 7 characters.
    match=0
    case "$EXPECT_COMMIT" in "$commit"*) [ "${#commit}" -ge 7 ] && match=1 ;; esac
    case "$commit" in "$EXPECT_COMMIT"*) [ "${#EXPECT_COMMIT}" -ge 7 ] && match=1 ;; esac
    check "served commit is the released commit" "$match" "serves '$commit', expected '$EXPECT_COMMIT'"
  fi
  if [ -n "${EXPECT_VERSION:-}" ]; then
    check "served version is the released version" "$(ok_if [ "$version" = "$EXPECT_VERSION" ])" "serves '$version', expected '$EXPECT_VERSION'"
  fi
  check "wiring: the environment answering is $target" "$(ok_if [ "$env_name" = "$target" ])" "health says env '$env_name'"
else
  check "health answers 2xx" 0 "$base$HEALTH_PATH: $health"
fi

# ---- Two controls ----
if data="$(curl -fsS --max-time 20 "$base$DATA_PATH" 2>&1)"; then
  case "$data" in *"$DATA_EXPECT"*) check "control: $DATA_PATH answers with real data" 1 ;; *) check "control: $DATA_PATH answers with real data" 0 "body lacks $DATA_EXPECT" ;; esac
else
  check "control: $DATA_PATH answers with real data" 0 "$data"
fi
refused="$(curl -sS --max-time 20 -o /dev/null -w '%{http_code}' "$base$REFUSED_PATH" 2>&1 || true)"
check "control: $REFUSED_PATH is refused" "$(ok_if [ "$refused" = "$REFUSED_STATUS" ])" "status $refused, expected $REFUSED_STATUS"

if [ "$failures" -ne 0 ]; then echo "verify-live: $failures assertion(s) failed against $base"; exit 1; fi
echo "verify-live: all assertions passed against $base"
