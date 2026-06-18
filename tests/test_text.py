"""Tests for utils/text.py."""

from __future__ import annotations

import pytest

from reportlab_json_renderer.utils.text import (
    escape_xml,
    normalize_line_breaks,
    normalize_whitespace,
    sanitize,
    truncate,
)


class TestSanitize:
    def test_removes_null_byte(self) -> None:
        assert sanitize("hello\x00world") == "helloworld"

    def test_preserves_newline(self) -> None:
        assert sanitize("line1\nline2") == "line1\nline2"

    def test_preserves_tab(self) -> None:
        assert sanitize("a\tb") == "a\tb"

    def test_removes_control_chars(self) -> None:
        assert sanitize("a\x01\x02b") == "ab"

    def test_preserves_unicode(self) -> None:
        assert sanitize("₹19,62,261") == "₹19,62,261"

    def test_empty_string(self) -> None:
        assert sanitize("") == ""


class TestTruncate:
    def test_short_text_unchanged(self) -> None:
        assert truncate("hello", 10) == "hello"

    def test_exact_length_unchanged(self) -> None:
        assert truncate("hello", 5) == "hello"

    def test_long_text_truncated(self) -> None:
        assert truncate("hello world", 8) == "hello w…"

    def test_max_length_equals_suffix(self) -> None:
        assert truncate("hello", 1) == "…"

    def test_max_length_less_than_suffix(self) -> None:
        assert truncate("hello", 0) == ""

    def test_negative_max_length_raises(self) -> None:
        with pytest.raises(ValueError, match="max_length must be >= 0"):
            truncate("hello", -1)

    def test_custom_suffix(self) -> None:
        assert truncate("hello world", 7, suffix="...") == "hell..."

    def test_no_suffix(self) -> None:
        assert truncate("hello world", 5, suffix="") == "hello"


class TestNormalizeWhitespace:
    def test_collapses_spaces(self) -> None:
        assert normalize_whitespace("hello   world") == "hello world"

    def test_strips_leading_trailing(self) -> None:
        assert normalize_whitespace("  hello  ") == "hello"

    def test_collapses_tabs_and_newlines(self) -> None:
        assert normalize_whitespace("hello\t\n  world") == "hello world"

    def test_empty_string(self) -> None:
        assert normalize_whitespace("") == ""

    def test_single_space(self) -> None:
        assert normalize_whitespace(" ") == ""


class TestNormalizeLineBreaks:
    def test_windows_line_endings(self) -> None:
        assert normalize_line_breaks("a\r\nb") == "a\nb"

    def test_old_mac_line_endings(self) -> None:
        assert normalize_line_breaks("a\rb") == "a\nb"

    def test_unix_unchanged(self) -> None:
        assert normalize_line_breaks("a\nb") == "a\nb"

    def test_mixed_endings(self) -> None:
        assert normalize_line_breaks("a\r\nb\rc\nd") == "a\nb\nc\nd"


class TestEscapeXml:
    def test_escapes_ampersand(self) -> None:
        assert escape_xml("a&b") == "a&amp;b"

    def test_escapes_lt_gt(self) -> None:
        assert escape_xml("<b>text</b>") == "&lt;b&gt;text&lt;/b&gt;"

    def test_no_special_chars(self) -> None:
        assert escape_xml("hello") == "hello"

    def test_empty_string(self) -> None:
        assert escape_xml("") == ""

    def test_combined(self) -> None:
        assert escape_xml("<a&b>") == "&lt;a&amp;b&gt;"
