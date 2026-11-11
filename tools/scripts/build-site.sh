#!/usr/bin/env bash
# Build the generated parts of site/ (published by GitHub Pages). Needs node, python3 and
# `bun install` in tools/ (marked is locked there with its integrity hash).
#   site/howto.html          <- HOWTO.md (marked, links rewritten to GitHub, heading ids)
#   site/index.html changelog <- top four entries of CHANGELOG.md, between the markers
# Run after editing HOWTO.md or CHANGELOG.md; CI fails if the outputs are stale.
set -euo pipefail
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)

# Write to a file first: the CLI's piped stdout can close before the full HTML flushes.
rendered=$(mktemp "${TMPDIR:-/tmp}/skills-howto.XXXXXX")
trap 'rm -f -- "$rendered"' EXIT
marked="$root/tools/node_modules/.bin/marked"
[ -x "$marked" ] || { echo "build-site: run 'bun install' in tools/ first" >&2; exit 1; }
"$marked" --gfm -i "$root/HOWTO.md" --output "$rendered"

# Relative links point at repo files; on Pages they must go to GitHub.
body=$(sed -E 's#href="([^"#/][^":]*)"#href="https://github.com/mneves75/skills/blob/main/\1"#g' "$rendered" \
  | sed -e 's/<pre>/<pre tabindex="0">/g' -e 's/<table>/<table tabindex="0">/g' \
  | perl -pe 's{<h2>([^<]+)</h2>}{my $t=$1; (my $id=lc $t) =~ s/[^a-z0-9]+/-/g; $id =~ s/^-|-$//g; "<h2 id=\"$id\">$t</h2>"}e')

# marked does not sanitize: raw HTML in HOWTO.md would land on the Pages origin
# as-is. The rendered body is parsed (not grepped) and must stay inside a strict
# subset: no element that switches an HTML5 parser's state or runs or embeds
# code, only the attributes marked emits, no on* handler, no attribute value
# that decodes to an executable scheme, and no comment, declaration or markup
# the parser cannot classify. Escaped code examples are text and pass.
# The template head below is not scanned (it legitimately carries <meta>).
printf '%s\n' "$body" | python3 "$root/tools/scripts/check-html-active.py" \
  || { echo "HOWTO.md renders active HTML; fix HOWTO.md (details above)" >&2; exit 1; }

# Table of contents: one entry per section heading the body already carries an id for.
toc=$(printf '%s\n' "$body" | perl -ne 'print qq{<li><a href="#$1">$2</a></li>\n} while m{<h2 id="([^"]+)">([^<]+)</h2>}g')

# The page shell and tokens follow site/index.html (DESIGN.md); the guide adds a reading column
# and a contents list shown as a sticky sidebar on wide screens and a <details> block on narrow ones.
cat > "$root/site/howto.html" <<HTML
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src 'self' data:; font-src 'self'; base-uri 'none'; form-action 'none'">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>How to use these skills</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='4' fill='%23132236'/%3E%3Ctext x='16' y='23' font-size='23' font-family='sans-serif' font-weight='700' text-anchor='middle' fill='white'%3Es%3C/text%3E%3C/svg%3E">
<link rel="preload" href="assets/fonts/bricolage-grotesque.woff2" as="font" type="font/woff2" crossorigin>
<style>
@font-face{font-family:Bricolage;src:url('assets/fonts/bricolage-grotesque.woff2') format('woff2');font-weight:200 800;font-style:normal;font-display:swap}
:root{color-scheme:light dark;--paper:#fff;--ink:#132236;--muted:#43556c;--rule:#d5dce5;--accent:#164bd6;--soft:#f0f5ff;--lime:#def59b;--on-lime:#203615;--code:#edf1f7;--focus:#164bd6;--display:Bricolage,Arial,sans-serif;--body:Bricolage,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
@media(prefers-color-scheme:dark){:root{--paper:#111b2b;--ink:#f1f5fc;--muted:#b6c4d8;--rule:#36465d;--accent:#abc4ff;--soft:#1b2d49;--code:#21324a;--focus:#d8ee9c}}
*{box-sizing:border-box}
html{scroll-padding-top:1.5rem}
body{margin:0;background:var(--paper);color:var(--ink);font:400 17px/1.6 var(--body);-webkit-font-smoothing:antialiased}
::selection{background:var(--lime);color:var(--on-lime)}
:focus-visible{outline:3px solid var(--focus);outline-offset:5px}
a{color:var(--accent);text-decoration-thickness:1px;text-underline-offset:.22em}
a:hover{text-decoration-thickness:2px}
code,pre{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
code{font-size:.88em;background:var(--code);padding:.12em .3em;border-radius:3px;overflow-wrap:anywhere}
h1,h2,h3,h4{font-family:var(--display);font-weight:650;line-height:1.15;letter-spacing:-.015em;text-wrap:balance}
.wrap{max-width:78rem;margin-inline:auto;padding-inline:clamp(1.25rem,4vw,3rem)}
.skip{position:absolute;top:.6rem;left:1rem;padding:.7rem 1rem;background:var(--ink);color:var(--paper);transform:translateY(-150%);z-index:3}.skip:focus{transform:translateY(0)}
.masthead{display:flex;align-items:center;justify-content:space-between;gap:2rem;padding-block:1.5rem;border-bottom:1px solid var(--rule)}
.brand{display:flex;gap:.65rem;align-items:center;color:var(--ink);font-size:1.1rem;font-weight:700;text-decoration:none;white-space:nowrap}
.mark{width:32px;height:32px;display:grid;place-items:center;background:var(--ink);color:var(--paper);border-radius:4px;font-size:1.55rem;line-height:1}
.nav{display:flex;flex-wrap:wrap;align-items:center;gap:1.5rem}.nav a{color:var(--ink);font-size:.95rem;text-decoration:none;padding-block:.5rem}.nav a:hover,.nav a[aria-current]{text-decoration:underline}
.guide{display:grid;grid-template-columns:13rem minmax(0,1fr);gap:3.5rem;align-items:start}
.guide>main{min-width:0;max-width:48rem;padding-block:2.5rem 3rem}
.toc ol{list-style:none;margin:0;padding:0}
.toc a{display:block;padding:.3rem 0;color:var(--muted);font-size:.88rem;line-height:1.35;text-decoration:none;overflow-wrap:anywhere}.toc a:hover{color:var(--ink);text-decoration:underline}
.toc a:focus-visible{outline-offset:2px}
.toc-side{position:sticky;top:0;max-height:100vh;overflow-y:auto;padding:2.5rem .5rem 2rem;margin-inline:-.5rem}
.toc-title{margin:0 0 .5rem;font-size:.8125rem;font-weight:600;color:var(--ink)}
.toc-inline{display:none}
.toc-inline details{background:var(--soft);border-radius:3px}
.toc-inline summary{min-height:48px;padding:.75rem .8rem;font-size:.95rem;font-weight:600;cursor:pointer}
.toc-inline ol{padding:0 .8rem .7rem}
main h1{margin:0 0 1.25rem;font-size:clamp(2.4rem,4.6vw,3.6rem);letter-spacing:-.025em;line-height:1.1}
main h2{margin:3rem 0 1rem;padding-top:1.5rem;border-top:1px solid var(--rule);font-size:clamp(1.6rem,2.4vw,2rem);overflow-wrap:anywhere}
main h3{margin:2rem 0 .6rem;font-size:1.2rem}main h4{margin:1.5rem 0 .5rem;font-size:1rem}
main p,main li,main blockquote{max-width:34em}
main p,main ul,main ol{margin:0 0 1rem}main li+li{margin-top:.3rem}
pre{margin:0 0 1.25rem;padding:1rem 1.2rem;background:var(--code);border-radius:4px;font-size:.82rem;line-height:1.7;white-space:pre;overflow-x:auto;scrollbar-color:var(--muted) var(--code)}pre code{background:none;padding:0;font-size:inherit;overflow-wrap:normal}
table{display:block;max-width:100%;overflow-x:auto;border-collapse:collapse;margin:0 0 1.25rem;font-size:.92rem}th,td{text-align:left;padding:.55rem .8rem .55rem 0;border-bottom:1px solid var(--rule);vertical-align:top}th{color:var(--muted);font-weight:600}td code,th code{white-space:nowrap;overflow-wrap:normal}
blockquote{margin:0 0 1rem;padding:.25rem 1rem;border-left:3px solid var(--rule)}hr{border:0;border-top:1px solid var(--rule);margin:2rem 0}
.footer{display:flex;gap:1.25rem;flex-wrap:wrap;padding-block:1.5rem 2rem;border-top:1px solid var(--rule);font-size:.85rem;color:var(--muted)}
@media(prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
@media(max-width:64rem){.guide{grid-template-columns:minmax(0,1fr);gap:0}.toc-side{display:none}.toc-inline{display:block;max-width:48rem;width:100%;margin-inline:auto;padding-top:1.5rem}.guide>main{padding-top:2rem;margin-inline:auto;width:100%}}
@media(max-width:48rem){body{font-size:16px}.masthead{gap:1rem;flex-wrap:wrap;padding-block:1.15rem}.nav{gap:1.15rem}}
@media(max-width:36rem){.brand{font-size:1rem}.nav{gap:1rem;font-size:.88rem}}
@media(forced-colors:active){.toc-inline details{border:1px solid ButtonText}}
</style>
</head>
<body>
<a class="skip" href="#guide">Skip to the guide</a>
<div class="wrap">
<header class="masthead">
  <a class="brand" href="./"><span class="mark" aria-hidden="true">s</span>mneves75/skills</a>
  <nav class="nav" aria-label="Site"><a href="index.html#skills">Catalog</a><a href="index.html#install">Install</a><a href="howto.html" aria-current="page">Guide</a><a href="https://github.com/mneves75/skills">GitHub</a></nav>
</header>
<div class="guide">
<nav class="toc toc-side" aria-label="Guide contents"><p class="toc-title">Contents</p><ol>
$toc
</ol></nav>
<nav class="toc toc-inline" aria-label="Guide contents"><details><summary>Contents</summary><ol>
$toc
</ol></details></nav>
<main id="guide">
$body
</main>
</div>
<footer class="footer"><span>Source: <a href="https://github.com/mneves75/skills/blob/main/HOWTO.md">HOWTO.md</a></span><a href="https://github.com/mneves75/skills">mneves75/skills</a></footer>
</div>
</body>
</html>
HTML
echo "wrote site/howto.html ($(wc -c < "$root/site/howto.html") bytes)"

python3 "$root/tools/scripts/changelog-rows.py" "$root/CHANGELOG.md" "$root/site/index.html"
echo "updated changelog rows in site/index.html"
