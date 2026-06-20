"""Status table block renderer.

Renders a table with status badges, useful for tracking task or item status.
"""

from __future__ import annotations

from typing import Any, ClassVar

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Spacer, Table, TableStyle

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.text import safe_paragraph_text


class StatusTableBlock(BaseBlock):
    """Render a table with status badges for each row."""

    block_type = "status_table"

    # Status to tone mapping.
    STATUS_TONES: ClassVar[dict[str, str]] = {
        "done": "success",
        "completed": "success",
        "in_progress": "info",
        "in progress": "info",
        "pending": "warning",
        "blocked": "danger",
        "cancelled": "muted",
        "not started": "muted",
    }

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        title = safe_paragraph_text(str(block.get("title", "")))
        columns = block.get("columns", [])
        rows = block.get("rows", [])
        flowables: list[Flowable] = []

        if title:
            title_style = ParagraphStyle(
                "StatusTableTitle",
                fontName=theme.font_bold if theme else "Helvetica-Bold",
                fontSize=11,
                textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
                spaceAfter=6,
                keepWithNext=True,
            )
            flowables.append(Paragraph(title, title_style))

        if not columns:
            return flowables

        header_style = ParagraphStyle(
            "StatusTableHeader",
            fontName=theme.font_bold if theme else "Helvetica-Bold",
            fontSize=9,
        )
        cell_style = ParagraphStyle(
            "StatusTableCell",
            fontName=theme.font_body if theme else "Helvetica",
            fontSize=9,
            leading=14,
        )

        # Build header row.
        header = [
            Paragraph(f"<b>{safe_paragraph_text(str(col.get('label', '')))}</b>", header_style)
            for col in columns
        ]

        # Build data rows with status badge styling.
        data_rows: list[list[Paragraph]] = []
        status_col_indices: list[int] = []

        # Find status column indices.
        for i, col in enumerate(columns):
            key = col.get("key", "").lower()
            if "status" in key:
                status_col_indices.append(i)

        for row in rows:
            if isinstance(row, dict):
                cells = []
                for i, col in enumerate(columns):
                    cell_text = safe_paragraph_text(str(row.get(col.get("key", ""), "")))
                    if i in status_col_indices:
                        # Apply status badge styling.
                        status_lower = cell_text.lower().replace(" ", "_")
                        tone = self.STATUS_TONES.get(status_lower, "primary")
                        tone_hex = theme.resolve_tone(tone) if theme else "#7CB518"
                        styled_text = f'<font color="{tone_hex}"><b>{cell_text}</b></font>'
                        cells.append(Paragraph(styled_text, cell_style))
                    else:
                        cells.append(Paragraph(cell_text, cell_style))
            elif isinstance(row, list):
                cells = []
                for i, cell in enumerate(row):
                    cell_text = safe_paragraph_text(str(cell))
                    if i in status_col_indices:
                        status_lower = cell_text.lower().replace(" ", "_")
                        tone = self.STATUS_TONES.get(status_lower, "primary")
                        tone_hex = theme.resolve_tone(tone) if theme else "#7CB518"
                        styled_text = f'<font color="{tone_hex}"><b>{cell_text}</b></font>'
                        cells.append(Paragraph(styled_text, cell_style))
                    else:
                        cells.append(Paragraph(cell_text, cell_style))
            else:
                continue
            data_rows.append(cells)

        all_data = [header, *data_rows]
        num_cols = len(columns)

        # Calculate column widths.
        col_widths = []
        for col in columns:
            width_str = col.get("width", "0.2")
            try:
                width_pct = float(width_str)
            except (ValueError, TypeError):
                width_pct = 1.0 / num_cols
            col_widths.append(available_width * width_pct)

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
        ]

        # Striping via ROWBACKGROUNDS.
        stripe_color = theme.resolve_tone("light") if theme else "#F5F5F5"
        style_cmds.append(
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(stripe_color)])
        )

        # Repeat header row on multi-page tables.
        style_cmds.append(("REPEATROWS", (0, 0), (-1, 0)))

        table.setStyle(TableStyle(style_cmds))

        flowables.append(table)
        flowables.append(Spacer(1, 8))
        return flowables
