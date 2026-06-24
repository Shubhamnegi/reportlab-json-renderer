"""Table block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Spacer, Table, TableStyle

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.text import safe_paragraph_text
from reportlab_json_renderer.visual.constants import (
    BORDER_MUTED,
    TABLE_HEADER_TEXT,
)
from reportlab_json_renderer.visual.tables import table_header_background, table_stripe_colors


class TableBlock(BaseBlock):
    """Render a table with columns, rows, and optional striping."""

    block_type = "table"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        title = safe_paragraph_text(str(block.get("title", "")))
        style = block.get("style", "standard")
        columns = block.get("columns", [])
        rows = block.get("rows", [])
        flowables: list[Flowable] = []

        if title:
            title_style = ParagraphStyle(
                "TableTitle",
                fontName=theme.font_bold if theme else "Helvetica-Bold",
                fontSize=11,
                textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
                spaceAfter=6,
                keepWithNext=True,
            )
            flowables.append(Paragraph(title, title_style))

        if not columns:
            return flowables

        # Build header row.
        header_bg = table_header_background(theme)
        header = [
            Paragraph(
                f"<b>{safe_paragraph_text(str(col.get('label', '')))}</b>",
                ParagraphStyle(
                    "TableHeader",
                    fontName=theme.font_bold if theme else "Helvetica-Bold",
                    fontSize=9,
                    textColor=colors.HexColor(TABLE_HEADER_TEXT),
                ),
            )
            for col in columns
        ]

        # Build data rows.
        data_rows: list[list[Paragraph]] = []
        cell_style = ParagraphStyle(
            "TableCell",
            fontName=theme.font_body if theme else "Helvetica",
            fontSize=9,
            leading=14,
        )
        for row in rows:
            data_rows.append(
                [
                    Paragraph(
                        safe_paragraph_text(str(row.get(col.get("key", ""), ""))),
                        cell_style,
                    )
                    for col in columns
                ]
            )

        all_data = [header, *data_rows]

        # Column widths — normalize so they sum to available_width.
        raw_widths = [col.get("width", 1.0 / len(columns)) for col in columns]
        total = sum(raw_widths) or 1.0
        col_widths = [(w / total) * available_width for w in raw_widths]

        table = Table(all_data, colWidths=col_widths, hAlign="LEFT")

        # Build style commands.
        style_cmds = [
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor(header_bg),
            ),
            (
                "LINEBELOW",
                (0, 0),
                (-1, 0),
                0.8,
                colors.HexColor(header_bg),
            ),
        ]

        # Striping via ROWBACKGROUNDS.
        if style != "plain":
            style_cmds.append(("ROWBACKGROUNDS", (0, 1), (-1, -1), table_stripe_colors(theme)))

        # Repeat header row on multi-page tables.
        style_cmds.append(("REPEATROWS", (0, 0), (-1, 0)))

        # Borders.
        style_cmds.append(
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor(BORDER_MUTED),
            )
        )

        table.setStyle(TableStyle(style_cmds))

        flowables.append(table)
        flowables.append(Spacer(1, 8))
        return flowables
