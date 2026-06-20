"""Badge block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Table, TableStyle

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.text import safe_paragraph_text


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
        label = safe_paragraph_text(str(block.get("label", "")))
        tone = block.get("tone", "primary")

        bg_color = theme.resolve_tone(tone) if theme else "#7CB518"
        text_color = "#FFFFFF"

        html = f'<font size="8" color="{text_color}"><b>{label}</b></font>'

        style = ParagraphStyle(
            "BadgeInner",
            fontName=theme.font_bold if theme else "Helvetica-Bold",
            fontSize=8,
            textColor=colors.HexColor(text_color),
            spaceAfter=0,
        )

        para = Paragraph(html, style)
        table = Table([[para]], colWidths=[available_width * 0.3])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg_color)),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("ROUNDEDCORNERS", [4, 4, 4, 4]),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]
            )
        )

        return [table]
