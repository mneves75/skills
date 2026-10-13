#!/usr/bin/env bash
# Real-browser regression for the public copy control. Requires agent-browser on PATH.
# Run through the host's approved browser execution route; no owner profile is used.
# Usage: tools/scripts/check-site-copy.sh http://127.0.0.1:PORT/
set -euo pipefail
copy_url="${1:?Usage: check-site-copy.sh <site-url>}"
copy_session="skills-copy-${$}"
trap 'agent-browser --session "$copy_session" close >/dev/null 2>&1 || true' EXIT
browser() { agent-browser --session "$copy_session" "$@" >/dev/null; }

for scenario in unavailable rejected success; do
  browser open "$copy_url"
  browser eval --stdin <<JS
window.copyProbe = { scenario: '$scenario', text: null };
Object.defineProperty(navigator, 'clipboard', { configurable: true, value:
  window.copyProbe.scenario === 'unavailable' ? undefined : {
    writeText: async text => {
      if (window.copyProbe.scenario === 'rejected') throw new Error('Synthetic denial');
      window.copyProbe.text = text;
    }
  }
});
JS
  browser find role button click --name 'Copy npx command'
  if [ "$scenario" = success ]; then
    browser wait --text 'Command copied'
  else
    browser wait --text 'Copy unavailable'
  fi
  browser eval --stdin <<'JS'
const result = document.getElementById('copied').textContent;
const expected = document.getElementById('c1').textContent;
if (window.copyProbe.scenario === 'success') {
  if (window.copyProbe.text !== expected || !result.includes('Command copied')) {
    throw new Error('Copy success did not match the visible command');
  }
} else if (!result.includes('Copy unavailable') || window.copyProbe.text !== null) {
  throw new Error('Copy failure was reported as success');
}
JS
  echo "PASS: copy $scenario"
done
