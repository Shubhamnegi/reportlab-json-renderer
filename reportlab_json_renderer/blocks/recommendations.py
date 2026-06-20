"""Recommendations block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Spacer, Table, TableStyle

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.text import safe_paragraph_text


class RecommendationsBlock(BaseBlock):
    """Render a recommendations table with priority/action/owner/impact."""

    block_type = "recommendations"

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
                "RecsTitle",
                fontName=theme.font_bold if theme else "Helvetica-Bold",
                fontSize=12,
                textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
                spaceAfter=8,
                keepWithNext=True,
            )
            flowables.append(Paragraph(title, title_style))

        if not items:
            return flowables

        headers = ["Priority", "Action", "Owner", "Impact"]
        header_style = ParagraphStyle(
            "RecsHeader",
            fontName=theme.font_bold if theme else "Helvetica-Bold",
            fontSize=9,
        )
        cell_style = ParagraphStyle(
            "RecsCell",
            fontName=theme.font_body if theme else "Helvetica",
            fontSize=9,
            leading=14,
        )

        header = [Paragraph(f"<b>{h}</b>", header_style) for h in headers]
        data_rows = [
            [
                Paragraph(safe_paragraph_text(str(item.get("priority", ""))), cell_style),
                Paragraph(safe_paragraph_text(str(item.get("action", ""))), cell_style),
                Paragraph(safe_paragraph_text(str(item.get("owner", ""))), cell_style),
                Paragraph(safe_paragraph_text(str(item.get("impact", ""))), cell_style),
            ]
            for item in items
        ]

        all_data = [header, *data_rows]
        # Column widths — normalize ratios so they sum to available_width.
        default_ratios = [0.15, 0.40, 0.20, 0.25]
        total = sum(default_ratios) or 1.0
        col_widths = [(r / total) * available_width for r in default_ratios]

        table = Table(all_data, colWidths=col_widths, hAlign="LEFT")

        style_cmds = [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor(theme.table_header_bg if theme else "#F0F0F0"),
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor(theme.resolve_tone("primary") if theme else "#7CB518"),
            ),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(theme.resolve_tone("light") if theme else "#F5F5F5")]),
            ("REPEATROWS", (0, 0), (-1, 0)),
        ]

        table.setStyle(TableStyle(style_cmds))

        flowables.append(table)
        flowables.append(Spacer(1, 8))
        return flowables
