"""Divider block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.platypus import Flowable, Spacer

from reportlab_json_renderer.blocks.base import BaseBlock


class DividerBlock(BaseBlock):
    """Render a horizontal divider line."""

    block_type = "divider"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        tone = block.get("tone", "primary")
        thickness = block.get("thickness", 1.0)
        line = _DividerLine(available_width, tone, thickness, theme)
        return [Spacer(1, 4), line, Spacer(1, 4)]


class _DividerLine(Flowable):
    def __init__(self, width: float, tone: str, thickness: float, theme: Any = None) -> None:
        super().__init__()
        self.width = width
        self.height = thickness
        self._tone = tone
        self._thickness = thickness
        self._theme = theme

    def draw(self) -> None:
        hex_color = self._theme.resolve_tone(self._tone) if self._theme else "#7CB518"
        self.canv.setStrokeColor(colors.HexColor(hex_color))
        self.canv.setLineWidth(self._thickness)
        self.canv.line(0, 0, self.width, 0)
