"""Callout group block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.platypus import Flowable, Paragraph

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.blocks.callout import CalloutBlock


class CalloutGroupBlock(BaseBlock):
    """Render a group of callouts under a shared title."""

    block_type = "callout_group"

    def __init__(self) -> None:
        self._callout_renderer = CalloutBlock()

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        title = block.get("title", "")
        items = block.get("items", [])
        flowables: list[Flowable] = []

        if title:
            from reportlab.lib import colors
            from reportlab.lib.styles import ParagraphStyle

            title_style = ParagraphStyle(
                "CalloutGroupTitle",
                fontName=theme.font_bold if theme else "Helvetica-Bold",
                fontSize=12,
                textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
                spaceAfter=6,
            )
            flowables.append(Paragraph(title, title_style))

        for item in items:
            callout_flowables = self._callout_renderer.render(
                item,
                theme=theme,
                template=template,
                available_width=available_width,
            )
            flowables.extend(callout_flowables)

        return flowables
