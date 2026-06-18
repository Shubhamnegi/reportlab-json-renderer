"""Insight list block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.text import safe_paragraph_text


class InsightListBlock(BaseBlock):
    """Render a numbered/bulleted insight list."""

    block_type = "insight_list"

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
                "InsightTitle",
                fontName=theme.font_bold if theme else "Helvetica-Bold",
                fontSize=12,
                textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
                spaceAfter=8,
            )
            flowables.append(Paragraph(title, title_style))

        for idx, item in enumerate(items, 1):
            item_title = safe_paragraph_text(str(item.get("title", "")))
            item_text = safe_paragraph_text(str(item.get("text", ""))).replace("\n", "<br/>")

            html_parts = [f"<b>{idx}. {item_title}</b>"]
            if item_text:
                html_parts.append(f"<br/>{item_text}")
            html = "".join(html_parts)

            style = ParagraphStyle(
                "InsightItem",
                fontName=theme.font_body if theme else "Helvetica",
                fontSize=10,
                leading=14,
                textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
                spaceBefore=4,
                spaceAfter=4,
            )
            flowables.append(Paragraph(html, style))

        return flowables
