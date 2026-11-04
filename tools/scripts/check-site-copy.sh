#!/usr/bin/env bash
# Real-browser regression for copy controls, mobile/desktop overflow and light/dark text contrast.
# Requires agent-browser on PATH.
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

for width in 390 1440; do
  browser set viewport "$width" 1000
  for page in "$copy_url" "${copy_url%/}/howto.html"; do
    browser open "$page"
    browser eval --stdin <<'JS'
const width = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth);
if (width > innerWidth) {
  throw new Error(`${location.pathname} overflows: ${width}px at ${innerWidth}px viewport`);
}
JS
    echo "PASS: no horizontal overflow at ${width}px: $page"
  done
done

# Computed contrast in both colour schemes: text in new-skill (lime) cards and all inline code,
# each against the background actually painted behind it.
for scheme in light dark; do
  browser set media "$scheme"
  browser open "$copy_url"
  browser eval --stdin <<JS
window.expectedScheme = '$scheme';
JS
  browser eval --stdin <<'JS'
if (matchMedia('(prefers-color-scheme: dark)').matches !== (window.expectedScheme === 'dark')) {
  throw new Error(`colour scheme emulation did not apply: expected ${window.expectedScheme}`);
}
const parse = value => {
  const m = value.match(/^rgba?\(([^)]+)\)$/);
  if (!m) throw new Error(`unparsed colour: ${value}`);
  const p = m[1].split(/[\s,\/]+/).filter(Boolean).map(Number);
  return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1];
};
const over = (top, bottom) => [0, 1, 2].map(i => top[i] * top[3] + bottom[i] * (1 - top[3])).concat(1);
const backdrop = el => {
  const layers = [];
  for (let node = el; node; node = node.parentElement) {
    const color = parse(getComputedStyle(node).backgroundColor);
    if (color[3] > 0) layers.push(color);
    if (color[3] === 1) break;
  }
  return layers.reverse().reduce((base, layer) => over(layer, base), [255, 255, 255, 1]);
};
const luminance = c => {
  const [r, g, b] = c.slice(0, 3).map(v => (v /= 255) <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};
const ratio = (a, b) => {
  const [high, low] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (high + 0.05) / (low + 0.05);
};
const targets = [...document.querySelectorAll('article.skill.new *, code')]
  .filter(el => [...el.childNodes].some(n => n.nodeType === Node.TEXT_NODE && n.textContent.trim()));
if (!targets.some(el => el.matches('article.skill.new code'))) throw new Error('no inline code in a lime card to check');
const low = [];
for (const el of targets) {
  const bg = backdrop(el);
  const value = ratio(over(parse(getComputedStyle(el).color), bg), bg);
  if (value < 4.5) low.push(`${el.tagName.toLowerCase()} "${el.textContent.trim().slice(0, 40)}" ${value.toFixed(2)}:1`);
}
if (low.length) throw new Error(`text below 4.5:1 in ${window.expectedScheme} mode: ${low.join('; ')}`);
JS
  echo "PASS: contrast $scheme"
done
