"""Two-column layout block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.platypus import Flowable, Spacer, Table, TableStyle

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.blocks.registry import render_block


class TwoColumnBlock(BaseBlock):
    """Render a two-column layout with configurable widths."""

    block_type = "two_column"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        left_width_ratio = block.get("left_width", 0.5)
        right_width_ratio = block.get("right_width", 0.5)
        left_blocks = block.get("left", [])
        right_blocks = block.get("right", [])

        left_w = available_width * left_width_ratio
        right_w = available_width * right_width_ratio

        # Render left column blocks.
        left_flowables: list[Flowable] = []
        for b in left_blocks:
            left_flowables.extend(
                render_block(
                    b,
                    theme=theme,
                    template=template,
                    available_width=left_w,
                )
            )

        # Render right column blocks.
        right_flowables: list[Flowable] = []
        for b in right_blocks:
            right_flowables.extend(
                render_block(
                    b,
                    theme=theme,
                    template=template,
                    available_width=right_w,
                )
            )

        # Combine into a table.
        left_cell = left_flowables if left_flowables else [Spacer(1, 20)]
        right_cell = right_flowables if right_flowables else [Spacer(1, 20)]

        table = Table(
            [[left_cell, right_cell]],
            colWidths=[left_w, right_w],
            hAlign="LEFT",
        )
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (0, -1), 8),
                    ("LEFTPADDING", (1, 0), (1, -1), 8),
                ]
            )
        )

        return [table]
