"""Summary box block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Spacer, Table, TableStyle

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.colors import tone_tint
from reportlab_json_renderer.utils.text import safe_paragraph_text


class SummaryBoxBlock(BaseBlock):
    """Render an executive summary card."""

    block_type = "summary_box"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        title = safe_paragraph_text(str(block.get("title", "")))
        text = safe_paragraph_text(str(block.get("text", ""))).replace("\n", "<br/>")
        tone = block.get("tone", "primary")

        border_color = theme.resolve_tone(tone) if theme else "#7CB518"
        bg_color = tone_tint(tone, theme.tones if theme else None)

        inner_parts: list[str] = []
        if title:
            inner_parts.append(
                f'<b><font size="11">{title}</font></b><br/>'
            )
        inner_parts.append(f'<font size="9">{text}</font>')
        html = "".join(inner_parts)

        text_style = ParagraphStyle(
            "SummaryText",
            fontName=theme.font_body if theme else "Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
        )

        para = Paragraph(html, text_style)

        table = Table([[para]], colWidths=[available_width - 20])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg_color)),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("BOX", (0, 0), (-1, -1), 2, colors.HexColor(border_color)),
        ]))

        return [Spacer(1, 4), table, Spacer(1, 8)]
