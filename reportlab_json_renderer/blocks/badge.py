"""Badge block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph

from reportlab_json_renderer.blocks.base import BaseBlock


class BadgeBlock(BaseBlock):
    """Render a small inline badge label."""

    block_type = "badge"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        label = block.get("label", "")
        tone = block.get("tone", "primary")

        bg_color = theme.resolve_tone(tone) if theme else "#7CB518"
        text_color = "#FFFFFF"

        html = (
            f'<font size="8" color="{text_color}">'
            f'<b>{label}</b>'
            f'</font>'
        )

        style = ParagraphStyle(
            "Badge",
            fontName=theme.font_bold if theme else "Helvetica-Bold",
            fontSize=8,
            textColor=colors.HexColor(text_color),
            backColor=colors.HexColor(bg_color),
            spaceAfter=4,
        )

        return [Paragraph(html, style)]
