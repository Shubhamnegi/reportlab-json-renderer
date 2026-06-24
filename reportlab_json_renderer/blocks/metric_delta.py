"""Metric delta block renderer.

Renders a single metric with a delta/change indicator, useful for
showing KPI values with period-over-period changes.
"""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Spacer, Table, TableStyle

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.colors import tone_tint
from reportlab_json_renderer.utils.text import safe_paragraph_text
from reportlab_json_renderer.visual.constants import BORDER_MUTED


class MetricDeltaBlock(BaseBlock):
    """Render a metric card with label, value, and optional delta indicator."""

    block_type = "metric_delta"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        label = safe_paragraph_text(str(block.get("label", "")))
        value = safe_paragraph_text(str(block.get("value", "")))
        delta = safe_paragraph_text(str(block.get("delta", "")))
        delta_tone = block.get("delta_tone")
        subtitle = safe_paragraph_text(str(block.get("subtitle", "")))
        tone = block.get("tone", "primary")

        dark_hex = theme.resolve_tone("dark") if theme else "#2D2D2D"
        muted_hex = theme.resolve_tone("muted") if theme else "#555555"
        border_color = theme.resolve_tone(tone) if theme else "#7CB518"
        bg_color = tone_tint(tone, theme.tones if theme else None)

        inner_parts: list[str] = []
        if label:
            inner_parts.append(f'<font size="9" color="{muted_hex}">{label}</font><br/>')
        if value:
            # Use slightly smaller font for very long values to prevent overlap
            value_font_size = 20 if len(str(value)) <= 10 else 16
            inner_parts.append(f'<font size="{value_font_size}"><b>{value}</b></font>')
        if delta:
            delta_color = theme.resolve_tone(delta_tone) if theme and delta_tone else dark_hex
            inner_parts.append(f'<br/><font size="10" color="{delta_color}">{delta}</font>')
        if subtitle:
            inner_parts.append(f'<br/><font size="8" color="{muted_hex}">{subtitle}</font>')

        html = "".join(inner_parts) or "&nbsp;"

        text_style = ParagraphStyle(
            "MetricDeltaText",
            fontName=theme.font_body if theme else "Helvetica",
            fontSize=10,
            leading=16,
            textColor=colors.HexColor(dark_hex),
        )

        para = Paragraph(html, text_style)

        table = Table([[para]], colWidths=[available_width - 20])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg_color)),
                    ("LEFTPADDING", (0, 0), (-1, -1), 14),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                    ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor(BORDER_MUTED)),
                    ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor(border_color)),
                    ("ROUNDEDCORNERS", [4, 4, 4, 4]),
                ]
            )
        )

        return [Spacer(1, 4), table, Spacer(1, 8)]
