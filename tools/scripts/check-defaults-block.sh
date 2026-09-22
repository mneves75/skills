#!/usr/bin/env bash
# Guard the AGENTS.md invariant "model ids and reasoning tiers live in exactly one clearly
# marked block per skill" for the orchestrator's SKILL.md.
#
# The protected vocabulary is DERIVED from the Defaults block itself, so the block is the only
# thing to edit on a model release and every value it names is automatically protected:
#   * vendor ids            gpt-6-astra, gpt-5.6-sol, claude-opus-5   (plus their alphabetic
#                           segments of 3+ letters: gpt, astra, sol, claude, opus)
#   * Claude seats          "<Name>, latest release (... alias `x`)" -> Name and x
#   * reasoning tiers       the word after "reasoning "
#   * anything backticked   `fable`, `opus`
# Outside the block those words may not appear as whole words, compared case-insensitively
# (hyphenated words stay whole, so "high-stakes" is not "high"), and no token shaped like a
# vendor model id (letters, then hyphenated segments with a digit, e.g. claude-opus-5) may
# appear at all, named in the block or not. The H1 title line and the frontmatter are exempt. The block's "Verified against the vendor model lists on YYYY-MM-DD"
# date must equal the top CHANGELOG entry's date, and that entry's version must equal VERSION,
# so a release cut without re-verifying the ids fails CI.
# Usage: tools/scripts/check-defaults-block.sh [SKILL.md] [CHANGELOG.md] [VERSION]
set -euo pipefail
f="${1:-skills/mneves-fable-orchestrator/SKILL.md}"
changelog="${2:-CHANGELOG.md}"
version_file="${3:-VERSION}"
for p in "$f" "$changelog" "$version_file"; do [ -f "$p" ] || { echo "$p: not found" >&2; exit 2; }; done

awk -v f="$f" '
  function add(w) { w = tolower(w); sub(/\.+$/, "", w); if (length(w) >= 3) vocab[w] = 1 }
  function add_id_segments(id,   n, i, seg) {
    n = split(id, seg, "-")
    for (i = 1; i <= n; i++) if (seg[i] ~ /^[A-Za-z]{3,}$/) add(seg[i])
  }
  function learn(line,   n, i, t, rest, k) {
    n = split(line, t, /[^A-Za-z0-9_.-]+/)
    for (i = 1; i <= n; i++) {
      if (t[i] ~ /^[A-Za-z]+(-[A-Za-z0-9.]+)+$/) { add(t[i]); add_id_segments(t[i]) }   # vendor id
    }
    if (match(line, /reasoning [A-Za-z]+/))          add(substr(line, RSTART + 10, RLENGTH - 10))
    if (match(line, /[A-Za-z]+, latest release/))    add(substr(line, RSTART, RLENGTH - 16))
    rest = line
    while (match(rest, /`[^`]+`/)) {                 # backticked aliases
      k = substr(rest, RSTART + 1, RLENGTH - 2); if (k ~ /^[A-Za-z0-9_.-]+$/) add(k)
      rest = substr(rest, RSTART + RLENGTH)
    }
  }
  # pass 1 (FNR == NR): find the block and learn its vocabulary
  FNR == NR {
    if (FNR == 1 && $0 == "---") { infront = 1; next }
    if (infront) { if ($0 == "---") infront = 0; next }
    if ($0 ~ /^### Defaults/) { headings++; armed = 1; next }
    if ($0 ~ /^```/) { if (inblock) { inblock = 0; closed = 1 } else if (armed && !closed) inblock = 1; next }
    if (inblock) { blocklines++; learn($0) }
    next
  }
  # pass 2: scan every line outside the block
  FNR == 1 { infront = 0; inblock = 0; closed2 = 0; armed2 = 0
             if ($0 == "---") { infront = 1; next } }
  infront { if ($0 == "---") infront = 0; next }
  /^# / { next }
  /^Verified against the vendor model lists on/ { next }
  /^### Defaults/ { armed2 = 1; next }
  /^```/ { if (inblock) { inblock = 0; closed2 = 1 } else if (armed2 && !closed2) inblock = 1; next }
  inblock { next }
  {
    n = split(tolower($0), t, /[^a-z0-9_.-]+/)
    for (i = 1; i <= n; i++) { w = t[i]; sub(/\.+$/, "", w)
      if (w in vocab) { print f ":" FNR ": Defaults value \"" w "\" appears outside the Defaults block: " $0; bad = 1 }
      # Structural rule, independent of the block: anything shaped like a vendor
      # model id (letters, then hyphenated segments including a digit) is an id.
      else if (w ~ /^[a-z]+(-[a-z0-9.]+)+$/ && w ~ /[0-9]/) { print f ":" FNR ": vendor-id-shaped token \"" w "\" outside the Defaults block: " $0; bad = 1 } }
  }
  END {
    if (headings != 1) { print f ": expected exactly one \"### Defaults\" heading, found " headings + 0; bad = 1 }
    if (!closed)       { print f ": no closed fenced block under Defaults"; bad = 1 }
    if (blocklines < 1 || length(vocab) < 3) { print f ": Defaults block did not yield a vocabulary (ids, tiers, aliases)"; bad = 1 }
    exit bad
  }
' "$f" "$f"

version="$(tr -d '[:space:]' < "$version_file")"
top="$(grep -Em1 '^## \[[0-9]+\.[0-9]+\.[0-9]+\] - [0-9]{4}-[0-9]{2}-[0-9]{2}' "$changelog" || true)"
[ -n "$top" ] || { echo "$changelog: no '## [X.Y.Z] - YYYY-MM-DD' entry" >&2; exit 1; }
top_version="$(printf '%s' "$top" | sed -E 's/^## \[([^]]+)\].*/\1/')"
top_date="$(printf '%s' "$top" | sed -E 's/.* - ([0-9]{4}-[0-9]{2}-[0-9]{2}).*/\1/')"
[ "$top_version" = "$version" ] \
  || { echo "$changelog: top entry is $top_version but $version_file says $version" >&2; exit 1; }

verified="$(grep -Eom1 '^Verified against the vendor model lists on [0-9]{4}-[0-9]{2}-[0-9]{2}' "$f" | grep -Eo '[0-9]{4}-[0-9]{2}-[0-9]{2}' || true)"
[ -n "$verified" ] \
  || { echo "$f: missing the 'Verified against the vendor model lists on YYYY-MM-DD' line" >&2; exit 1; }
[ "$verified" = "$top_date" ] \
  || { echo "$f: Defaults verified on $verified, but release $version is dated $top_date in $changelog; re-verify the ids and update the date" >&2; exit 1; }
echo "defaults block OK: $f (release $version verified $verified)"
