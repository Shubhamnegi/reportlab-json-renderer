"""KPI grid block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Spacer, Table, TableStyle

from reportlab_json_renderer.blocks.base import BaseBlock


class KPIGridBlock(BaseBlock):
    """Render KPI cards in a grid layout."""

    block_type = "kpi_grid"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        title = block.get("title", "")
        num_cols = block.get("columns", 4)
        items = block.get("items", [])
        flowables: list[Flowable] = []

        if title:
            title_style = ParagraphStyle(
                "KPITitle",
                fontName=theme.font_bold if theme else "Helvetica-Bold",
                fontSize=12,
                textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
                spaceAfter=8,
            )
            flowables.append(Paragraph(title, title_style))

        if not items:
            return flowables

        # Build cells.
        cells = []
        for item in items:
            cell = self._build_cell(item, theme, available_width / num_cols)
            cells.append(cell)

        # Pad to fill last row.
        while len(cells) % num_cols != 0:
            cells.append("")

        # Build table rows.
        rows = [cells[i : i + num_cols] for i in range(0, len(cells), num_cols)]

        col_width = (available_width - (num_cols - 1) * 6) / num_cols
        table = Table(rows, colWidths=[col_width] * num_cols, hAlign="LEFT")

        # Style: light background per card.
        style_cmds = [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(
                theme.resolve_tone("light") if theme else "#F5F5F5"
            )),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor(
                theme.resolve_tone("primary") if theme else "#7CB518"
            )),
        ]
        table.setStyle(TableStyle(style_cmds))

        flowables.append(table)
        flowables.append(Spacer(1, 8))
        return flowables

    def _build_cell(self, item: dict, theme: Any, cell_width: float) -> Paragraph:
        label = item.get("label", "")
        value = item.get("value", "")
        sub = item.get("sub", "")
        tone = item.get("tone")

        value_color = theme.resolve_tone(tone) if theme and tone else (
            theme.resolve_tone("dark") if theme else "#2D2D2D"
        )

        muted_hex = theme.resolve_tone("muted") if theme else "#555555"
        parts = [
            f'<font size="8" color="{muted_hex}">{label}</font>',
            '<br/>',
            f'<font size="14"><b>{value}</b></font>',
        ]
        if sub:
            parts.append(f'<br/><font size="8" color="{value_color}">{sub}</font>')

        html = "".join(parts)

        style = ParagraphStyle(
            "KPICell",
            fontName=theme.font_body if theme else "Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
        )

        return Paragraph(html, style)
