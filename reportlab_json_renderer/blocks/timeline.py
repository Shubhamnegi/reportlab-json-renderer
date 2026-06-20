"""Timeline block renderer.

Renders a vertical timeline with events, each showing date, title,
description, and optional tone indicator.
"""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Spacer, Table, TableStyle

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.text import safe_paragraph_text


class TimelineBlock(BaseBlock):
    """Render a vertical timeline with events."""

    block_type = "timeline"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        title = safe_paragraph_text(str(block.get("title", "")))
        items = block.get("items", [])
        flowables: list[Flowable] = []

        if title:
            title_style = ParagraphStyle(
                "TimelineTitle",
                fontName=theme.font_bold if theme else "Helvetica-Bold",
                fontSize=12,
                textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
                spaceAfter=8,
            )
            flowables.append(Paragraph(title, title_style))

        if not items:
            return flowables

        dark_hex = theme.resolve_tone("dark") if theme else "#2D2D2D"
        muted_hex = theme.resolve_tone("muted") if theme else "#555555"
        primary_hex = theme.resolve_tone("primary") if theme else "#7CB518"

        body_style = ParagraphStyle(
            "TimelineBody",
            fontName=theme.font_body if theme else "Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor(dark_hex),
        )

        # Build timeline rows.
        data_rows: list[list[Paragraph | str]] = []
        dot_width = 20
        content_width = available_width - dot_width - 10

        for _, item in enumerate(items):
            date_text = safe_paragraph_text(str(item.get("date", "")))
            item_title = safe_paragraph_text(str(item.get("title", "")))
            description = safe_paragraph_text(str(item.get("description", "")))
            tone = item.get("tone", "primary")
            tone_hex = theme.resolve_tone(tone) if theme else primary_hex

            # Dot placeholder (simulated with a small colored table).
            dot_para = Paragraph(
                f'<font size="14" color="{tone_hex}">&#x25CF;</font>',
                ParagraphStyle("Dot", fontSize=14, leading=16),
            )

            # Content cell.
            content_parts: list[str] = []
            if date_text:
                content_parts.append(f'<font size="8" color="{muted_hex}">{date_text}</font><br/>')
            if item_title:
                content_parts.append(f"<b>{item_title}</b><br/>")
            if description:
                content_parts.append(f'<font size="9">{description}</font>')

            content_html = "".join(content_parts) or "&nbsp;"
            content_para = Paragraph(content_html, body_style)

            data_rows.append([dot_para, content_para])

        # Vertical line column.
        table = Table(
            data_rows,
            colWidths=[dot_width, content_width],
            hAlign="LEFT",
        )

        style_cmds = [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (0, -1), 4),
            ("RIGHTPADDING", (0, 0), (0, -1), 4),
            ("LEFTPADDING", (1, 0), (1, -1), 8),
            ("RIGHTPADDING", (1, 0), (1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]

        # Add horizontal separator lines between items.
        for row_idx in range(len(data_rows)):
            if row_idx > 0:
                style_cmds.append(
                    (
                        "LINEABOVE",
                        (0, row_idx),
                        (-1, row_idx),
                        0.5,
                        colors.HexColor(theme.resolve_tone("muted") if theme else "#CCCCCC"),
                    )
                )

        table.setStyle(TableStyle(style_cmds))

        flowables.append(table)
        flowables.append(Spacer(1, 8))
        return flowables
