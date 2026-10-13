#!/usr/bin/env python3
"""Validate a Pandoc JSON document before writing artifacts; Python 3.10+.

Standard library only. This filter does not execute source content. It is not
a filesystem/network sandbox or an SVG sanitizer; remaining local resources
must be trusted and authorized by the project.
"""

import json
import re
import sys
import unicodedata
from urllib.parse import unquote, urlsplit


DIMENSION = re.compile(r"(?:\d+(?:\.\d+)?|\.\d+)(?:px|pt|cm|mm|in|inch|%)?", re.ASCII)
ATTRIBUTE_NODES = {"Code", "CodeBlock", "Span", "Div", "Figure", "Table", "Header"}


def check_text(value):
    if not isinstance(value, str):
        raise ValueError("invalid attribute text")
    if "\\" in value or any(unicodedata.category(char) in {"Cc", "Cf"} for char in value):
        raise ValueError("control characters or backslashes in attributes")


def check_attributes(attributes, *, image=False):
    if not (isinstance(attributes, list) and len(attributes) == 3
            and isinstance(attributes[1], list) and isinstance(attributes[2], list)):
        raise ValueError("invalid Pandoc attributes")
    check_text(attributes[0])
    for name in attributes[1]:
        check_text(name)
    for pair in attributes[2]:
        if not (isinstance(pair, list) and len(pair) == 2):
            raise ValueError("invalid attribute pair")
        key, value = pair
        check_text(key)
        check_text(value)
        if not image or key not in {"width", "height"}:
            raise ValueError("attribute is not allowed; only image width/height are supported")
        if not DIMENSION.fullmatch(value):
            raise ValueError("invalid image dimension")


def check_destination(destination, *, image=False):
    check_text(destination)
    decoded = unquote(destination)
    check_text(decoded)
    parsed = urlsplit(decoded)
    if decoded.startswith("//"):
        raise ValueError("network-relative destinations are not supported")
    if image:
        if parsed.scheme:
            raise ValueError("image destinations must be trusted local paths")
    elif parsed.scheme not in {"", "http", "https", "mailto"}:
        raise ValueError("unsupported link destination scheme")
    if parsed.scheme in {"http", "https"} and not parsed.netloc:
        raise ValueError("invalid web link destination")


def check_document(value):
    if isinstance(value, dict):
        kind = value.get("t")
        if kind in {"RawInline", "RawBlock"}:
            raise ValueError("raw nodes are not supported by this starter")
        if kind in ATTRIBUTE_NODES or kind in {"Link", "Image"}:
            content = value.get("c")
            position = 1 if kind == "Header" else 0
            if not isinstance(content, list) or len(content) <= position:
                raise ValueError("invalid attributed Pandoc node")
            check_attributes(content[position], image=kind == "Image")
            if kind in {"Link", "Image"}:
                if not (len(content) == 3 and isinstance(content[2], list)
                        and len(content[2]) == 2 and isinstance(content[2][1], str)):
                    raise ValueError("invalid Pandoc link/image destination")
                check_destination(content[2][0], image=kind == "Image")
            for index, item in enumerate(content):
                if index != position:
                    check_document(item)
            return
        for item in value.values():
            check_document(item)
    elif isinstance(value, list):
        # Table rows/cells store Attr tuples without a named AST node.
        if (len(value) == 3 and isinstance(value[0], str)
                and isinstance(value[1], list) and isinstance(value[2], list)):
            check_attributes(value)
        else:
            for item in value:
                check_document(item)


def reject_constant(_value):
    raise ValueError("non-finite numbers are not valid Pandoc JSON")


def main():
    try:
        document = json.load(sys.stdin, parse_constant=reject_constant)
        if not (isinstance(document, dict) and isinstance(document.get("meta"), dict)
                and isinstance(document.get("blocks"), list)
                and isinstance(document.get("pandoc-api-version"), list)
                and document["pandoc-api-version"]
                and all(type(part) is int for part in document["pandoc-api-version"])):
            raise ValueError("expected a Pandoc document with version, metadata and blocks")
        check_document(document)
        serialized = json.dumps(document, ensure_ascii=False)
    except (ValueError, TypeError, RecursionError) as error:
        print(f"check_ast: {error}", file=sys.stderr)
        return 1
    sys.stdout.write(serialized + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
