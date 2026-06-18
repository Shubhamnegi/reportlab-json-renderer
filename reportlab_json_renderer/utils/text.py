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
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def safe_paragraph_text(text: str) -> str:
    """Normalize, sanitize, and XML-escape user text for Paragraph content."""
    return escape_xml(sanitize(normalize_line_breaks(text)))


# ReportLab-recognised HTML tags that should NOT be escaped.
_RECOGNISED_TAGS = re.compile(
    r"<(/?)(\s*(?:b|i|u|br/?|font|a|sup|sub|para|strong|em)" r"(?:\s[^>]*)?\s*/?)>",
    re.IGNORECASE,
)


def safe_paragraph_html(text: str) -> str:
    """Normalize, sanitize, and partially XML-escape user text.

    Unlike :func:`safe_paragraph_text`, this function *preserves*
    ReportLab-recognised HTML tags (``<b>``, ``<i>``, ``<br/>``, etc.)
    so they render as styled markup rather than literal angle-bracket text.

    Unrecognised ``<`` and ``>`` characters are still escaped.
    """
    text = sanitize(normalize_line_breaks(text))
    # Replace <br> variants with self-closing <br/> for ReportLab.
    text = re.sub(r"<br\s*/?>", "<br/>", text, flags=re.IGNORECASE)
    # Protect recognised tags from escaping.
    placeholder = "\x00TAG\x00"
    protected: list[str] = []
    for match in _RECOGNISED_TAGS.finditer(text):
        protected.append(match.group(0))
    # Strip recognised tags, escape the rest, then put them back.
    stripped = _RECOGNISED_TAGS.sub(placeholder, text)
    escaped = escape_xml(stripped)
    for tag in protected:
        escaped = escaped.replace(placeholder, tag, 1)
    return escaped


__all__ = [
    "escape_xml",
    "normalize_line_breaks",
    "normalize_whitespace",
    "safe_paragraph_html",
    "safe_paragraph_text",
    "sanitize",
    "truncate",
]
