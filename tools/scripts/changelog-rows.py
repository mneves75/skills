#!/usr/bin/env python3
"""Rewrite the changelog rows in site/index.html from the top four CHANGELOG.md entries.

Rows go between `<!-- changelog:start -->` and `<!-- changelog:end -->`. Each row is the
version, the date, and the first sentence of the entry's first bullet (bold and links dropped,
backticks kept as <code>). Stdlib only; called by build-site.sh.
"""

import html
import re
import sys

ENTRY = re.compile(r"^## \[(\d+\.\d+\.\d+)\] - (\S+)\n(.*?)(?=^## \[|\Z)", re.M | re.S)
MARKERS = re.compile(r"(<!-- changelog:start -->).*?(<!-- changelog:end -->)", re.S)


def first_sentence(body: str) -> str:
    bullet = re.search(r"^- (.+)$", body, re.M)
    text = bullet.group(1) if bullet else ""
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.split(". ")[0].rstrip(".") + "."
    text = html.escape(text, quote=False)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", text)


def main(changelog: str, index: str) -> None:
    entries = ENTRY.findall(open(changelog, encoding="utf-8").read())[:4]
    if not entries:
        sys.exit("changelog-rows: no entries found in CHANGELOG.md")
    rows = "\n".join(
        f'        <li><span class="v">{v}<span class="d">{d}</span></span>'
        f"<span>{first_sentence(body)}</span></li>"
        for v, d, body in entries
    )
    page = open(index, encoding="utf-8").read()
    new, n = MARKERS.subn(lambda m: m.group(1) + "\n" + rows + "\n        " + m.group(2), page)
    if n != 1:
        sys.exit("changelog-rows: markers not found in site/index.html")
    open(index, "w", encoding="utf-8").write(new)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: changelog-rows.py CHANGELOG.md site/index.html")
    main(sys.argv[1], sys.argv[2])
