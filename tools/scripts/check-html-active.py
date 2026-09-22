#!/usr/bin/env python3
"""Reject rendered HTML that carries active content. Standard library only.

Reads an HTML fragment on stdin and exits 1 if it contains an element that can run
or embed code, an on* event-handler attribute, or a URL attribute whose DECODED
value uses an executable scheme. Text and escaped code are never inspected, so a
fenced `<button onclick="x()">` example or an inline `javascript:` mention passes;
an `<a href="&#106;avascript:...">` does not, because attribute values are
entity-decoded before the scheme check. Python 3.10+.
"""
from __future__ import annotations

import sys
from html.parser import HTMLParser

ACTIVE_ELEMENTS = frozenset(
    {"script", "iframe", "object", "embed", "svg", "math", "form", "base", "meta", "link", "style"}
)
URL_ATTRIBUTES = frozenset({"href", "src", "action", "formaction", "xlink:href", "data", "srcdoc"})
ACTIVE_SCHEMES = ("javascript:", "vbscript:", "data:")


class ActiveContentFinder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.findings: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        line, _ = self.getpos()
        if tag.lower() in ACTIVE_ELEMENTS:
            self.findings.append(f"line {line}: active element <{tag}>")
        for name, value in attrs:
            lname = name.lower()
            if lname.startswith("on"):
                self.findings.append(f"line {line}: event handler {name}= on <{tag}>")
            elif lname in URL_ATTRIBUTES and value is not None:
                # The parser has already decoded entities; strip the control and
                # whitespace characters browsers ignore before the scheme.
                scheme = "".join(ch for ch in value if ch > " ").lower()
                if scheme.startswith(ACTIVE_SCHEMES):
                    self.findings.append(f"line {line}: {name}= uses an executable scheme on <{tag}>")

    handle_startendtag = handle_starttag


def main() -> int:
    finder = ActiveContentFinder()
    finder.feed(sys.stdin.read())
    finder.close()
    for finding in finder.findings:
        print(f"check-html-active: {finding}", file=sys.stderr)
    return 1 if finder.findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
