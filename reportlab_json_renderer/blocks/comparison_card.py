"""Comparison card block renderer.

Renders a side-by-side comparison of two items, each with label,
value, and optional delta/change indicator.
"""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Spacer, Table, TableStyle

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.text import safe_paragraph_text


class ComparisonCardBlock(BaseBlock):
    """Render a two-item comparison card with optional delta indicators."""

    block_type = "comparison_card"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        title = safe_paragraph_text(str(block.get("title", "")))
        left_item = block.get("left", {})
        right_item = block.get("right", {})
        flowables: list[Flowable] = []

        if title:
            title_style = ParagraphStyle(
                "ComparisonTitle",
                fontName=theme.font_bold if theme else "Helvetica-Bold",
                fontSize=12,
                textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
                spaceAfter=8,
            )
            flowables.append(Paragraph(title, title_style))

        left_cell = self._build_cell(left_item, theme)
        right_cell = self._build_cell(right_item, theme)

        col_width = (available_width - 12) / 2
        table = Table([[left_cell, right_cell]], colWidths=[col_width, col_width], hAlign="LEFT")

        border_color = theme.resolve_tone("primary") if theme else "#7CB518"
        style_cmds = [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                colors.HexColor(theme.resolve_tone("light") if theme else "#F5F5F5"),
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                1,
                colors.HexColor(border_color),
            ),
            ("ROUNDEDCORNERS", [4, 4, 4, 4]),
            (
                "LINEAFTER",
                (0, 0),
                (0, -1),
                1,
                colors.HexColor(theme.resolve_tone("muted") if theme else "#CCCCCC"),
            ),
        ]
        table.setStyle(TableStyle(style_cmds))

        flowables.append(table)
        flowables.append(Spacer(1, 8))
        return flowables

    def _build_cell(self, item: dict[str, Any], theme: Any) -> Paragraph:
        label = safe_paragraph_text(str(item.get("label", "")))
        value = safe_paragraph_text(str(item.get("value", "")))
        delta = safe_paragraph_text(str(item.get("delta", "")))
        tone = item.get("tone")

        muted_hex = theme.resolve_tone("muted") if theme else "#555555"
        dark_hex = theme.resolve_tone("dark") if theme else "#2D2D2D"
        delta_color = theme.resolve_tone(tone) if theme and tone else dark_hex

        parts = []
        if label:
            parts.append(f'<font size="9" color="{muted_hex}">{label}</font><br/>')
        if value:
            parts.append(f'<font size="16"><b>{value}</b></font>')
        if delta:
            parts.append(f'<br/><font size="9" color="{delta_color}">{delta}</font>')

        html = "".join(parts) or "&nbsp;"

        style = ParagraphStyle(
            "ComparisonCell",
            fontName=theme.font_body if theme else "Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor(dark_hex),
        )

        return Paragraph(html, style)
