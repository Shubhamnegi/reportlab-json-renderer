"""KPI grid block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Spacer, Table, TableStyle

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.colors import tone_tint
from reportlab_json_renderer.utils.text import safe_paragraph_text
from reportlab_json_renderer.visual.constants import BORDER_MUTED, CANVAS_WHITE


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
        title = safe_paragraph_text(str(block.get("title", "")))
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

        style_cmds = [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("ROUNDEDCORNERS", [4, 4, 4, 4]),
        ]
        style_cmds.extend(_build_card_style_commands(items, num_cols, theme))
        table.setStyle(TableStyle(style_cmds))

        flowables.append(table)
        flowables.append(Spacer(1, 8))
        return flowables

    def _build_cell(self, item: dict, theme: Any, cell_width: float) -> Paragraph:
        label = safe_paragraph_text(str(item.get("label", "")))
        value = safe_paragraph_text(str(item.get("value", "")))
        sub = safe_paragraph_text(str(item.get("sub", "")))
        tone = item.get("tone")

        value_color = (
            theme.resolve_tone(tone)
            if theme and tone
            else (theme.resolve_tone("dark") if theme else "#2D2D2D")
        )

        muted_hex = theme.resolve_tone("muted") if theme else "#555555"
        parts = [
            f'<font size="8" color="{muted_hex}">{label}</font>',
            "<br/>",
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


def _build_card_style_commands(items: list[dict], num_cols: int, theme: Any) -> list[tuple]:
    """Build per-card backgrounds, borders, and tone accents."""
    commands: list[tuple] = []
    for index, item in enumerate(items):
        row = index // num_cols
        col = index % num_cols
        tone = item.get("tone") or "primary"
        border_color = theme.resolve_tone(tone) if theme else "#7CB518"
        try:
            background = tone_tint(tone, theme.tones if theme else None, factor=0.92)
        except Exception:
            background = theme.resolve_tone("light") if theme else "#F5F5F5"
        commands.extend(
            [
                ("BACKGROUND", (col, row), (col, row), colors.HexColor(background)),
                ("BOX", (col, row), (col, row), 0.5, colors.HexColor(BORDER_MUTED)),
                ("LINEBEFORE", (col, row), (col, row), 3, colors.HexColor(border_color)),
            ]
        )

    padded_cells = ((len(items) + num_cols - 1) // num_cols) * num_cols
    for index in range(len(items), padded_cells):
        row = index // num_cols
        col = index % num_cols
        commands.append(("BACKGROUND", (col, row), (col, row), colors.HexColor(CANVAS_WHITE)))
    return commands
