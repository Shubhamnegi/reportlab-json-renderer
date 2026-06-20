"""Risk register block renderer.

Renders a table of risks with impact, likelihood, and mitigation columns.
Useful for project risk management and reporting.
"""

from __future__ import annotations

from typing import Any, ClassVar

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Spacer, Table, TableStyle

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.text import safe_paragraph_text


class RiskRegisterBlock(BaseBlock):
    """Render a risk register table with risk details and mitigation."""

    block_type = "risk_register"

    # Default column definitions.
    DEFAULT_COLUMNS: ClassVar[list[dict[str, str]]] = [
        {"key": "risk", "label": "Risk", "width": "0.35"},
        {"key": "impact", "label": "Impact", "width": "0.15"},
        {"key": "likelihood", "label": "Likelihood", "width": "0.15"},
        {"key": "mitigation", "label": "Mitigation", "width": "0.35"},
    ]

    # Impact/likelihood to tone mapping.
    LEVEL_TONES: ClassVar[dict[str, str]] = {
        "high": "danger",
        "medium": "warning",
        "low": "success",
        "critical": "danger",
        "very high": "danger",
        "very low": "success",
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
        columns = block.get("columns", self.DEFAULT_COLUMNS)
        rows = block.get("rows", [])
        flowables: list[Flowable] = []

        if title:
            title_style = ParagraphStyle(
                "RiskRegisterTitle",
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
            "RiskHeader",
            fontName=theme.font_bold if theme else "Helvetica-Bold",
            fontSize=9,
        )
        cell_style = ParagraphStyle(
            "RiskCell",
            fontName=theme.font_body if theme else "Helvetica",
            fontSize=9,
            leading=14,
        )

        # Build header row.
        header = [
            Paragraph(f"<b>{safe_paragraph_text(str(col.get('label', '')))}</b>", header_style)
            for col in columns
        ]

        # Build data rows.
        data_rows: list[list[Paragraph]] = []
        for row in rows:
            if isinstance(row, dict):
                cells = [
                    Paragraph(
                        safe_paragraph_text(str(row.get(col.get("key", ""), ""))),
                        cell_style,
                    )
                    for col in columns
                ]
            elif isinstance(row, list):
                cells = [Paragraph(safe_paragraph_text(str(cell)), cell_style) for cell in row]
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

        # Add tone-based coloring for impact/likelihood columns if they exist.
        impact_col_idx = None
        likelihood_col_idx = None
        for i, col in enumerate(columns):
            key = col.get("key", "")
            if key == "impact":
                impact_col_idx = i
            elif key == "likelihood":
                likelihood_col_idx = i

        if impact_col_idx is not None or likelihood_col_idx is not None:
            for row_idx, row_data in enumerate(data_rows, start=1):
                for col_idx in [impact_col_idx, likelihood_col_idx]:
                    if col_idx is not None and col_idx < len(row_data):
                        cell_text = row_data[col_idx].getPlainText().lower()
                        tone = self.LEVEL_TONES.get(cell_text, "primary")
                        tone_hex = theme.resolve_tone(tone) if theme else "#7CB518"
                        style_cmds.append(
                            (
                                "TEXTCOLOR",
                                (col_idx, row_idx),
                                (col_idx, row_idx),
                                colors.HexColor(tone_hex),
                            )
                        )

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
