#!/usr/bin/env python3
"""Reject rendered HTML outside a strict accepted subset. Standard library only, Python 3.11+.

Reads an HTML fragment on stdin and exits 1, naming each finding, unless every piece of markup
in it is one the guard can classify as inert. Python's parser and a browser's HTML5 parser can
disagree about where markup ends, so the guard accepts only markup on which they agree:

- no element that switches an HTML5 parser into another state (raw text, RCDATA, plaintext,
  foreign content, templates) or that runs, embeds or submits content;
- only the attributes marked and build-site.sh emit, never an on* event handler, and no
  attribute value at all whose entity-decoded form starts with javascript:, vbscript: or data:;
- an element the guard does not name only when it carries no attribute (an HTML5 tokenizer
  reads it as an ordinary tag);
- no comment, declaration, CDATA section or processing instruction, and no `<` the parser
  left as text: the guard fails closed instead of guessing where such markup ends.

Escaped text is never inspected, so a fenced `<button onclick="x()">` example or an inline
`javascript:` mention passes.
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser

# Elements after which a browser may read text as markup that this parser reads as text (or the
# reverse), and elements that run, embed or submit content.
REJECTED_ELEMENTS = frozenset({
    "script", "style", "textarea", "title", "xmp", "plaintext", "iframe", "noembed", "noframes",
    "noscript", "template", "svg", "math", "object", "embed", "applet", "frame", "frameset",
    "form", "base", "meta", "link",
})
# What marked renders from GitHub-flavored Markdown; these may carry the accepted attributes.
ACCEPTED_ELEMENTS = frozenset({
    "a", "blockquote", "br", "code", "del", "em", "h1", "h2", "h3", "h4", "h5", "h6", "hr",
    "img", "input", "li", "ol", "p", "pre", "strong", "table", "tbody", "td", "th", "thead",
    "tr", "ul",
})
# What marked and build-site.sh put on them.
ACCEPTED_ATTRIBUTES = frozenset({
    "href", "src", "alt", "title", "class", "id", "tabindex", "start", "align", "type",
    "checked", "disabled",
})
ACTIVE_SCHEMES = ("javascript:", "vbscript:", "data:")
TAG_NAME = re.compile(r"[a-z][a-z0-9-]*")


class SubsetChecker(HTMLParser):
    def __init__(self) -> None:
        # Character references stay encoded in text, so a `<` the parser left as text is a raw
        # one; attribute values are entity-decoded either way.
        super().__init__(convert_charrefs=False)
        self.findings: list[str] = []

    def report(self, what: str) -> None:
        line, _ = self.getpos()
        self.findings.append(f"line {line}: {what}")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if not TAG_NAME.fullmatch(tag):
            self.report(f"unclassifiable tag <{tag}>")
        elif tag in REJECTED_ELEMENTS:
            self.report(f"element <{tag}> is outside the accepted subset")
        elif tag not in ACCEPTED_ELEMENTS and attrs:
            self.report(f"element <{tag}> is not a rendered Markdown element and carries attributes")
        for name, value in attrs:
            if name.startswith("on"):
                self.report(f"event handler {name}= on <{tag}>")
            elif name not in ACCEPTED_ATTRIBUTES:
                self.report(f"attribute {name}= on <{tag}> is outside the accepted subset")
            # Browsers ignore control characters and whitespace around and inside a scheme.
            if value is not None and "".join(ch for ch in value if ch > " ").lower().startswith(ACTIVE_SCHEMES):
                self.report(f"{name}= uses an executable scheme on <{tag}>")

    handle_startendtag = handle_starttag

    def handle_endtag(self, tag: str) -> None:
        if tag in REJECTED_ELEMENTS or not TAG_NAME.fullmatch(tag):
            self.report(f"end tag </{tag}> is outside the accepted subset")

    def handle_data(self, data: str) -> None:
        if "<" in data:
            self.report("a `<` the parser could not read as a tag")

    def handle_comment(self, data: str) -> None:
        self.report("a comment")

    def handle_decl(self, decl: str) -> None:
        self.report("a declaration")

    def unknown_decl(self, data: str) -> None:
        self.report("a declaration or CDATA section")

    def handle_pi(self, data: str) -> None:
        self.report("a processing instruction")


def main() -> int:
    checker = SubsetChecker()
    checker.feed(sys.stdin.read())
    checker.close()
    for finding in checker.findings:
        print(f"check-html-active: {finding}", file=sys.stderr)
    return 1 if checker.findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
