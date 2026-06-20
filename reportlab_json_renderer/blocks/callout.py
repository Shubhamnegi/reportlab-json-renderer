"""Callout block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Spacer, Table, TableStyle

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.colors import tone_tint
from reportlab_json_renderer.utils.text import safe_paragraph_text


class CalloutBlock(BaseBlock):
    """Render a coloured callout box with optional title and text."""

    block_type = "callout"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        tone = block.get("tone", "primary")
        title = safe_paragraph_text(str(block.get("title", "")))
        text = safe_paragraph_text(str(block.get("text", ""))).replace("\n", "<br/>")

        border_color = theme.resolve_tone(tone) if theme else "#7CB518"
        bg_color = tone_tint(tone, theme.tones if theme else None)
        border_width = theme.callout_border_width if theme else 3.0

        # Build inner content.
        inner_parts: list[str] = []
        if title:
            inner_parts.append(f'<b><font size="10">{title}</font></b><br/>')
        inner_parts.append(f'<font size="9">{text}</font>')
        html = "".join(inner_parts)

        text_style = ParagraphStyle(
            "CalloutText",
            fontName=theme.font_body if theme else "Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
        )

        para = Paragraph(html, text_style)

        # Wrap in a table for the left-border effect.
        table = Table([[para]], colWidths=[available_width - border_width - 12])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg_color)),
                    ("LEFTPADDING", (0, 0), (-1, -1), 14),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    (
                        "LINEBEFORETABLE",
                        (0, 0),
                        (0, -1),
                        border_width,
                        colors.HexColor(border_color),
                    ),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor(border_color)),
                    ("ROUNDEDCORNERS", [4, 4, 4, 4]),
                ]
            )
        )

        return [Spacer(1, 6), table, Spacer(1, 8)]
