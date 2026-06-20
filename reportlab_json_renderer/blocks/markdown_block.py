"""Markdown block renderer.

Renders markdown text as PDF paragraphs using ReportLab's supported HTML tags.
Supports headings, bold, italic, inline code, lists, and blockquotes.
"""

from __future__ import annotations

import re
from typing import Any, ClassVar

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Spacer

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.text import safe_paragraph_html


class MarkdownBlock(BaseBlock):
    """Render markdown text as PDF paragraphs."""

    block_type = "markdown_block"

    # Markdown patterns and their ReportLab HTML replacements.
    _PATTERNS: ClassVar[list[tuple[str, str]]] = [
        # Headings (h1-h6) → bold text.
        (r"^#{6}\s+(.+)$", r"<b>\1</b>"),
        (r"^#{5}\s+(.+)$", r"<b>\1</b>"),
        (r"^#{4}\s+(.+)$", r"<b>\1</b>"),
        (r"^#{3}\s+(.+)$", r"<b>\1</b>"),
        (r"^#{2}\s+(.+)$", r"<b>\1</b>"),
        (r"^#{1}\s+(.+)$", r"<b>\1</b>"),
        # Bold.
        (r"\*\*(.+?)\*\*", r"<b>\1</b>"),
        (r"__(.+?)__", r"<b>\1</b>"),
        # Italic.
        (r"\*(.+?)\*", r"<i>\1</i>"),
        (r"_(.+?)_", r"<i>\1</i>"),
        # Strikethrough (ReportLab doesn't support <s>, use italic as fallback).
        (r"~~(.+?)~~", r"<i>\1</i>"),
        # Inline code.
        (r"`([^`]+)`", r'<font face="Courier">\1</font>'),
        # Links - just show text.
        (r"\[([^\]]+)\]\([^)]+\)", r"\1"),
        # Images - just show alt text.
        (r"!\[([^\]]*)\]\([^)]+\)", r"[\1]"),
    ]

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        title = block.get("title", "")
        markdown_text = block.get("markdown", "")
        flowables: list[Flowable] = []

        if title:
            title_style = ParagraphStyle(
                "MarkdownTitle",
                fontName=theme.font_bold if theme else "Helvetica-Bold",
                fontSize=12,
                textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
                spaceAfter=8,
            )
            flowables.append(Paragraph(safe_paragraph_html(str(title)), title_style))

        if not markdown_text:
            return flowables

        # Convert markdown to HTML.
        html = self._markdown_to_html(str(markdown_text))

        # Split into paragraphs by double newlines.
        paragraphs = re.split(r"\n\s*\n", html)

        text_style = ParagraphStyle(
            "MarkdownText",
            fontName=theme.font_body if theme else "Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
        )

        for para_text in paragraphs:
            para_text = para_text.strip()
            if not para_text:
                continue
            # Apply safe_paragraph_html to preserve ReportLab-recognised tags.
            safe_html = safe_paragraph_html(para_text)
            flowables.append(Paragraph(safe_html, text_style))
            flowables.append(Spacer(1, 6))

        return flowables

    def _markdown_to_html(self, text: str) -> str:
        """Convert markdown text to HTML with ReportLab-supported tags.

        Args:
            text: Raw markdown text.

        Returns:
            HTML string with ReportLab-compatible tags.
        """
        lines = text.split("\n")
        result_lines: list[str] = []
        in_code_block = False
        code_block_lines: list[str] = []

        for line in lines:
            # Handle fenced code blocks.
            if line.strip().startswith("```"):
                if in_code_block:
                    # End code block.
                    code_html = "<br/>".join(code_block_lines)
                    result_lines.append(f'<font face="Courier" size="9">{code_html}</font>')
                    code_block_lines = []
                    in_code_block = False
                else:
                    # Start code block.
                    in_code_block = True
                continue

            if in_code_block:
                # Escape HTML in code blocks and preserve whitespace.
                escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                code_block_lines.append(escaped)
                continue

            # Process inline markdown patterns.
            processed = line
            for pattern, replacement in self._PATTERNS:
                processed = re.sub(pattern, replacement, processed, flags=re.MULTILINE)

            # Handle horizontal rules.
            if re.match(r"^(-{3,}|\*{3,}|_{3,})$", processed.strip()):
                result_lines.append(
                    '<font color="#CCCCCC">----------------------------------------</font>'
                )
                continue

            result_lines.append(processed)

        # If we were in a code block at the end, close it.
        if in_code_block and code_block_lines:
            code_html = "<br/>".join(code_block_lines)
            result_lines.append(f'<font face="Courier" size="9">{code_html}</font>')

        return "\n".join(result_lines)
