"""Section header block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Spacer

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.text import safe_paragraph_text


class SectionHeaderBlock(BaseBlock):
    """Render a numbered section header."""

    block_type = "section_header"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        number = safe_paragraph_text(str(block.get("number", "")))
        title = safe_paragraph_text(str(block.get("title", "")))
        flowables: list[Flowable] = []

        spacing = template.section_spacing if template else 18.0
        flowables.append(Spacer(1, spacing))

        display = f"{number}. {title}" if number else title
        style = ParagraphStyle(
            "SectionHeader",
            fontName=theme.font_bold if theme else "Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor(theme.resolve_tone("dark")) if theme else colors.black,
            spaceAfter=6,
            spaceBefore=10,
            keepWithNext=True,
        )
        flowables.append(Paragraph(display, style))

        # Thin line under the header.
        flowables.append(_SectionLine(available_width, theme))
        flowables.append(Spacer(1, 8))

        return flowables


class _SectionLine(Flowable):
    def __init__(self, width: float, theme: Any = None) -> None:
        super().__init__()
        self.width = width
        self.height = 1
        self._theme = theme

    def draw(self) -> None:
        hex_color = self._theme.resolve_tone("primary") if self._theme else "#7CB518"
        self.canv.setStrokeColor(colors.HexColor(hex_color))
        self.canv.setLineWidth(0.5)
        self.canv.line(0, 0, self.width, 0)
