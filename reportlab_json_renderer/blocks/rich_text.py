"""Rich text block renderer."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.text import safe_paragraph_text

_STYLE_MAP = {
    "normal": ("", False, False),
    "bold": ("-Bold", True, False),
    "italic": ("-Oblique", False, True),
    "bold_italic": ("-BoldOblique", True, True),
    "bold_danger": ("-Bold", True, False),
    "bold_success": ("-Bold", True, False),
    "bold_warning": ("-Bold", True, False),
}


class RichTextBlock(BaseBlock):
    """Render inline-styled text runs as a single paragraph."""

    block_type = "rich_text"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        runs = block.get("runs", [])
        body_font = theme.font_body if theme else "Helvetica"
        base_family = body_font.replace("-Bold", "").replace("-Oblique", "")

        xml_parts: list[str] = []
        for run in runs:
            text = safe_paragraph_text(str(run.get("text", "")))
            style = run.get("style", "normal")
            suffix, is_bold, _is_italic = _STYLE_MAP.get(style, ("", False, False))
            if run.get("bold") is True:
                is_bold = True
            if run.get("italic") is True and not is_bold:
                style = "italic"
                suffix = _STYLE_MAP["italic"][0]

            font_tag = f'font face="{base_family}{suffix}"'

            # Handle tone-based colouring.
            tone_color = None
            if style in ("bold_danger", "bold_success", "bold_warning"):
                tone_map = {
                    "bold_danger": "danger",
                    "bold_success": "success",
                    "bold_warning": "warning",
                }
                tone_name = tone_map[style]
                tone_color = theme.resolve_tone(tone_name) if theme else "#C62828"
            elif run.get("tone"):
                tone_name = run["tone"]
                tone_color = theme.resolve_tone(tone_name) if theme else "#2D2D2D"

            tags_open = f"<{font_tag}"
            if tone_color:
                tags_open += f' color="{tone_color}"'
            if is_bold:
                tags_open += ">"
                tags_open = tags_open.replace(">", "><b>")
            else:
                tags_open += ">"
            tags_close = "</b>" if is_bold else ""
            tags_close += f"</{font_tag.split(' ')[0]}>"

            # Simplify: use ReportLab's <b> and <font> tags directly.
            if is_bold and tone_color:
                xml_parts.append(f'<b><font color="{tone_color}">{text}</font></b>')
            elif is_bold:
                xml_parts.append(f"<b>{text}</b>")
            elif tone_color:
                xml_parts.append(f'<font color="{tone_color}">{text}</font>')
            else:
                xml_parts.append(text)

        combined = "".join(xml_parts)

        style = ParagraphStyle(
            "RichText",
            fontName=body_font,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
            spaceBefore=2,
            spaceAfter=6,
        )

        return [Paragraph(combined, style)]
