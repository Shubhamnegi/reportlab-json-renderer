"""Image block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Spacer
from reportlab.platypus import Image as RLImage

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.units import cm_to_pt


class ImageBlock(BaseBlock):
    """Render an image block from a local file path."""

    block_type = "image"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        title = block.get("title", "")
        src = block.get("src", "")
        width_cm = block.get("width_cm")
        height_cm = block.get("height_cm")
        align = block.get("align", "center")
        flowables: list[Flowable] = []

        if title:
            title_style = ParagraphStyle(
                "ImageTitle",
                fontName=theme.font_bold if theme else "Helvetica-Bold",
                fontSize=10,
                textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
                spaceAfter=4,
            )
            flowables.append(Paragraph(title, title_style))

        if not src:
            return flowables

        # Resolve dimensions.
        w = cm_to_pt(width_cm) if width_cm else available_width * 0.8
        h = cm_to_pt(height_cm) if height_cm else w * 0.5

        try:
            img = RLImage(src, width=w, height=h)
            img.hAlign = align.upper()
            flowables.append(img)
        except Exception:
            # Fallback: show the path as text if image can't be loaded.
            error_style = ParagraphStyle(
                "ImageError",
                fontName=theme.font_body if theme else "Helvetica",
                fontSize=9,
                textColor=colors.HexColor(theme.resolve_tone("danger") if theme else "#C62828"),
            )
            flowables.append(Paragraph(f"[Image not found: {src}]", error_style))

        flowables.append(Spacer(1, 8))
        return flowables
