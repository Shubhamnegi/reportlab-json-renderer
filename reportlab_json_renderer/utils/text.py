"""Text sanitisation, truncation, and formatting helpers.

Keeps rendering logic clean by isolating string manipulation that
multiple block renderers need.
"""

from __future__ import annotations

import re


def sanitize(text: str) -> str:
    """Remove control characters that ReportLab cannot render.

    Preserves newlines (\\n) and tabs (\\t) but strips other control
    characters (U+0000-U+001F except \\n, \\t; and U+007F-U+009F).

    Args:
        text: Raw input string.

    Returns:
        Cleaned string safe for ReportLab paragraph flowables.
    """
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)


def truncate(text: str, max_length: int, suffix: str = "…") -> str:
    """Truncate *text* to *max_length* characters, appending *suffix*.

    If the text is already short enough it is returned unchanged.

    Args:
        text: Input string.
        max_length: Maximum total length **including** the suffix.
        suffix: String appended when truncation occurs.

    Returns:
        Truncated string.
    """
    if max_length < 0:
        raise ValueError("max_length must be >= 0")
    if len(text) <= max_length:
        return text
    if max_length <= len(suffix):
        return suffix[:max_length]
    return text[: max_length - len(suffix)] + suffix


def normalize_whitespace(text: str) -> str:
    """Collapse runs of whitespace into single spaces and strip.

    Args:
        text: Input string.

    Returns:
        String with collapsed whitespace.
    """
    return re.sub(r"\s+", " ", text).strip()


def normalize_line_breaks(text: str) -> str:
    """Normalise Windows (``\\r\\n``) and old-Mac (``\\r``) line endings
    to Unix-style ``\\n``.

    Args:
        text: Input string.

    Returns:
        String with normalised line breaks.
    """
    return text.replace("\r\n", "\n").replace("\r", "\n")


def escape_xml(text: str) -> str:
    """Escape ``&``, ``<``, ``>`` for ReportLab XML paragraph markup.

    Args:
        text: Raw text.

    Returns:
        Escaped text safe for ``<para>`` tags.
    """
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


__all__ = [
    "escape_xml",
    "normalize_line_breaks",
    "normalize_whitespace",
    "sanitize",
    "truncate",
]
