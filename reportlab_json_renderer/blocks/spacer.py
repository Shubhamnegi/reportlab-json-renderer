"""Spacer block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.platypus import Flowable
from reportlab.platypus import Spacer as RLSpacer

from reportlab_json_renderer.blocks.base import BaseBlock


class SpacerBlock(BaseBlock):
    """Render vertical space."""

    block_type = "spacer"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        height = block.get("height", 12)
        return [RLSpacer(1, height)]
