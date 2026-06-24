"""Matrix table block renderer."""

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


class MatrixTableBlock(BaseBlock):
    """Render a comparison matrix table (columns as headers, rows as data lists)."""

    block_type = "matrix_table"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        title = safe_paragraph_text(str(block.get("title", "")))
        col_headers = block.get("columns", [])
        rows = block.get("rows", [])
        flowables: list[Flowable] = []

        if title:
            title_style = ParagraphStyle(
                "MatrixTitle",
                fontName=theme.font_bold if theme else "Helvetica-Bold",
                fontSize=11,
                textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
                spaceAfter=6,
                keepWithNext=True,
            )
            flowables.append(Paragraph(title, title_style))

        if not col_headers:
            return flowables

        header_style = ParagraphStyle(
            "MatrixHeader",
            fontName=theme.font_bold if theme else "Helvetica-Bold",
            fontSize=9,
            textColor=colors.HexColor(TABLE_HEADER_TEXT),
        )
        cell_style = ParagraphStyle(
            "MatrixCell",
            fontName=theme.font_body if theme else "Helvetica",
            fontSize=9,
            leading=14,
        )

        header = [
            Paragraph(f"<b>{safe_paragraph_text(str(h))}</b>", header_style) for h in col_headers
        ]
        data_rows = [
            [Paragraph(safe_paragraph_text(str(cell)), cell_style) for cell in row] for row in rows
        ]

        all_data = [header, *data_rows]
        num_cols = len(col_headers)
        col_width = available_width / num_cols

        table = Table(all_data, colWidths=[col_width] * num_cols, hAlign="LEFT")
        header_bg = table_header_background(theme)

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
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor(BORDER_MUTED),
            ),
        ]

        # Striping via ROWBACKGROUNDS.
        style_cmds.append(("ROWBACKGROUNDS", (0, 1), (-1, -1), table_stripe_colors(theme)))

        # Repeat header row on multi-page tables.
        style_cmds.append(("REPEATROWS", (0, 0), (-1, 0)))

        table.setStyle(TableStyle(style_cmds))

        flowables.append(table)
        flowables.append(Spacer(1, 8))
        return flowables
