"""Page break block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.platypus import Flowable
from reportlab.platypus import PageBreak as RLPageBreak

from reportlab_json_renderer.blocks.base import BaseBlock


class PageBreakBlock(BaseBlock):
    """Render an explicit page break."""

    block_type = "page_break"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        return [RLPageBreak()]
