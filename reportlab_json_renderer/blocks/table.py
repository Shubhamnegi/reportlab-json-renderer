"""Table block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Spacer, Table, TableStyle

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.text import safe_paragraph_text


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
            )
            flowables.append(Paragraph(title, title_style))

        if not columns:
            return flowables

        # Build header row.
        header = [
            Paragraph(
                f"<b>{safe_paragraph_text(str(col.get('label', '')))}</b>",
                ParagraphStyle(
                    "TableHeader",
                    fontName=theme.font_bold if theme else "Helvetica-Bold",
                    fontSize=9,
                    textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
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
            leading=12,
        )
        for row in rows:
            data_rows.append([
                Paragraph(
                    safe_paragraph_text(str(row.get(col.get("key", ""), ""))),
                    cell_style,
                )
                for col in columns
            ])

        all_data = [header, *data_rows]

        # Column widths.
        col_widths = [
            col.get("width", 1.0 / len(columns)) * available_width
            for col in columns
        ]

        table = Table(all_data, colWidths=col_widths, hAlign="LEFT")

        # Build style commands.
        style_cmds = [
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(
                theme.table_header_bg if theme else "#F0F0F0"
            )),
            ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor(
                theme.resolve_tone("primary") if theme else "#7CB518"
            )),
        ]

        # Striping.
        if style == "striped":
            stripe_color = theme.resolve_tone("light") if theme else "#F5F5F5"
            for i in range(1, len(all_data)):
                if i % 2 == 0:
                    style_cmds.append(
                        ("BACKGROUND", (0, i), (-1, i), colors.HexColor(stripe_color))
                    )

        # Borders.
        style_cmds.append(("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor(
            theme.resolve_tone("primary") if theme else "#7CB518"
        )))

        table.setStyle(TableStyle(style_cmds))

        flowables.append(table)
        flowables.append(Spacer(1, 8))
        return flowables
