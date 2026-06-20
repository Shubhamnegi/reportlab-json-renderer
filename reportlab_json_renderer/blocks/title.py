"""Title block renderer.

Renders the report title header with entity name, title, subtitle,
and optional right-aligned text.
"""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Spacer

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.text import safe_paragraph_text


class TitleBlock(BaseBlock):
    """Render a title block with entity, title, subtitle, and right text."""

    block_type = "title"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        entity = safe_paragraph_text(str(block.get("entity", "")))
        title = safe_paragraph_text(str(block.get("title", "")))
        subtitle = safe_paragraph_text(str(block.get("subtitle", "")))
        right_text = safe_paragraph_text(str(block.get("right_text", "")))
        flowables: list[Flowable] = []

        # Entity name (small, muted)
        if entity:
            entity_style = ParagraphStyle(
                "TitleEntity",
                fontName=theme.font_bold if theme else "Helvetica-Bold",
                fontSize=9,
                textColor=colors.HexColor(theme.resolve_tone("muted")) if theme else colors.grey,
                spaceAfter=2,
            )
            flowables.append(Paragraph(entity, entity_style))

        # Main title
        if title:
            title_style = ParagraphStyle(
                "TitleMain",
                fontName=theme.font_bold if theme else "Helvetica-Bold",
                fontSize=18,
                leading=22,
                textColor=colors.HexColor(theme.resolve_tone("dark")) if theme else colors.black,
                spaceAfter=4,
            )
            flowables.append(Paragraph(title, title_style))

        # Subtitle
        if subtitle:
            sub_style = ParagraphStyle(
                "TitleSub",
                fontName=theme.font_body if theme else "Helvetica",
                fontSize=11,
                textColor=colors.HexColor(theme.resolve_tone("muted")) if theme else colors.grey,
                spaceAfter=2,
            )
            flowables.append(Paragraph(subtitle, sub_style))

        # Right-aligned text
        if right_text:
            right_style = ParagraphStyle(
                "TitleRight",
                fontName=theme.font_body if theme else "Helvetica",
                fontSize=9,
                textColor=colors.HexColor(theme.resolve_tone("muted")) if theme else colors.grey,
                alignment=TA_RIGHT,
                spaceAfter=6,
            )
            flowables.append(Paragraph(right_text, right_style))

        # Bottom separator line
        flowables.append(Spacer(1, 12))
        line = _HorizontalLine(available_width, theme)
        flowables.append(line)
        flowables.append(Spacer(1, 12))

        return flowables


class _HorizontalLine(Flowable):
    """A simple horizontal line flowable."""

    def __init__(self, width: float, theme: Any = None) -> None:
        super().__init__()
        self.width = width
        self.height = 2
        self.theme = theme

    def draw(self) -> None:
        hex_color = self.theme.resolve_tone("primary") if self.theme else "#7CB518"
        self.canv.setStrokeColor(colors.HexColor(hex_color))
        self.canv.setLineWidth(2.0)
        self.canv.line(0, 0, self.width, 0)
