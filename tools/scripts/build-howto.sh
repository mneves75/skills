#!/usr/bin/env bash
# Render HOWTO.md to examples/howto.html (published by GitHub Pages). Needs bun.
set -euo pipefail
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)
# Relative links point at repo files; on Pages they must go to GitHub.
body=$(bunx --silent marked@18 --gfm -i "$root/HOWTO.md" \
  | sed -E 's#href="([^"#/][^":]*)"#href="https://github.com/mneves75/skills/blob/main/\1"#g')
cat > "$root/examples/howto.html" <<HTML
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>How to use these skills</title>
<style>
:root{--bg:#fff;--fg:#1a1a1a;--muted:#666;--line:#e5e5e5;--code:#f4f4f4;--link:#1d4ed8}
@media (prefers-color-scheme:dark){:root{--bg:#0f0f0f;--fg:#eaeaea;--muted:#999;--line:#2a2a2a;--code:#1c1c1c;--link:#7aa2ff}}
body{margin:0 auto;max-width:46rem;padding:2rem 1.25rem 4rem;font:16px/1.6 -apple-system,system-ui,sans-serif;color:var(--fg);background:var(--bg)}
h1,h2,h3{line-height:1.25}h1{font-size:2rem}h2{margin-top:2.5rem;padding-top:1rem;border-top:1px solid var(--line)}
a{color:var(--link)}code{font:0.9em ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--code);padding:.1em .3em;border-radius:3px}
pre{background:var(--code);padding:1rem;overflow-x:auto;border-radius:6px}pre code{background:none;padding:0}
table{border-collapse:collapse;width:100%;margin:1rem 0;display:block;overflow-x:auto}th,td{text-align:left;padding:.5rem;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--muted);font-weight:600}
blockquote{margin:1rem 0;padding:.25rem 1rem;border-left:3px solid var(--line);color:var(--fg)}hr{border:0;border-top:1px solid var(--line);margin:2rem 0}
</style>
</head>
<body>
$body
<footer style="margin-top:3rem;color:var(--muted);font-size:.875rem">Source: <a href="https://github.com/mneves75/skills/blob/main/HOWTO.md">HOWTO.md</a> · <a href="https://github.com/mneves75/skills">mneves75/skills</a></footer>
</body>
</html>
HTML
echo "wrote examples/howto.html ($(wc -c < "$root/examples/howto.html") bytes)"
