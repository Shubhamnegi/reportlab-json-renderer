"""Paragraph block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.text import safe_paragraph_html


class ParagraphBlock(BaseBlock):
    """Render a paragraph with configurable style."""

    block_type = "paragraph"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        text = safe_paragraph_html(str(block.get("text", "")))
        style_name = block.get("style", "body")

        font_map = {
            "body": (theme.font_body if theme else "Helvetica", 10),
            "bold": (theme.font_bold if theme else "Helvetica-Bold", 10),
            "caption": (theme.font_body if theme else "Helvetica", 8),
            "small": (theme.font_body if theme else "Helvetica", 9),
            "lead": (theme.font_body if theme else "Helvetica", 12),
        }

        font_name, font_size = font_map.get(
            style_name, (theme.font_body if theme else "Helvetica", 10)
        )
        text_color = theme.resolve_tone("dark") if theme else "#2D2D2D"

        # Style-specific spacing and leading.
        if style_name == "lead":
            leading = font_size * 1.5
            space_after = 10
        elif style_name == "caption":
            leading = font_size * 1.4
            space_after = 4
        else:
            leading = font_size * 1.4
            space_after = 6

        style = ParagraphStyle(
            "Paragraph",
            fontName=font_name,
            fontSize=font_size,
            leading=leading,
            textColor=colors.HexColor(text_color),
            spaceBefore=2,
            spaceAfter=space_after,
        )

        if style_name == "caption":
            style.spaceBefore = 2

        return [Paragraph(text, style)]
