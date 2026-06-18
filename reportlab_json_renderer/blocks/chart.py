"""Chart block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Spacer
from reportlab.platypus import Image as RLImage

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.charts import render_chart
from reportlab_json_renderer.utils.errors import RenderError
from reportlab_json_renderer.utils.text import safe_paragraph_text


class ChartBlock(BaseBlock):
    """Render a chart as an embedded PNG image."""

    block_type = "chart"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        chart_type = block.get("chart_type", "bar")
        title = safe_paragraph_text(str(block.get("title", "")))
        labels = block.get("labels", [])
        values = block.get("values", [])
        series = block.get("series")
        tone = block.get("tone")
        flowables: list[Flowable] = []

        if title:
            title_style = ParagraphStyle(
                "ChartTitle",
                fontName=theme.font_bold if theme else "Helvetica-Bold",
                fontSize=11,
                textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
                spaceAfter=6,
            )
            flowables.append(Paragraph(title, title_style))

        try:
            theme_palette = theme.tones if theme else None
            buf = render_chart(
                chart_type=chart_type,
                labels=labels,
                values=values,
                series=series,
                tone=tone,
                theme_palette=theme_palette,
            )
            img_width = available_width * 0.9
            img_height = img_width * 0.5
            img = RLImage(buf, width=img_width, height=img_height)
            img.hAlign = "CENTER"
            flowables.append(img)
        except Exception as exc:
            raise RenderError(f"Chart render failed: {exc}") from exc

        flowables.append(Spacer(1, 8))
        return flowables
