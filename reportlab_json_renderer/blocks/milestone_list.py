"""Milestone list block renderer.

Renders a list of milestones with title, description, status, and date.
Useful for project tracking and progress reporting.
"""

from __future__ import annotations

from typing import Any, ClassVar

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph, Spacer, Table, TableStyle

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.text import safe_paragraph_text


class MilestoneListBlock(BaseBlock):
    """Render a milestone list with status and date indicators."""

    block_type = "milestone_list"

    # Status to tone mapping.
    STATUS_TONES: ClassVar[dict[str, str]] = {
        "done": "success",
        "completed": "success",
        "in_progress": "info",
        "pending": "warning",
        "blocked": "danger",
        "cancelled": "muted",
    }

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
                "MilestoneTitle",
                fontName=theme.font_bold if theme else "Helvetica-Bold",
                fontSize=12,
                textColor=colors.HexColor(theme.resolve_tone("dark") if theme else "#2D2D2D"),
                spaceAfter=8,
            )
            flowables.append(Paragraph(title, title_style))

        if not items:
            return flowables

        dark_hex = theme.resolve_tone("dark") if theme else "#2D2D2D"
        muted_hex = theme.resolve_tone("muted") if theme else "#555555"

        body_style = ParagraphStyle(
            "MilestoneBody",
            fontName=theme.font_body if theme else "Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor(dark_hex),
        )

        data_rows: list[list[Paragraph]] = []
        status_width = 60
        date_width = 70
        content_width = available_width - status_width - date_width - 20

        for item in items:
            item_title = safe_paragraph_text(str(item.get("title", "")))
            description = safe_paragraph_text(str(item.get("description", "")))
            status = safe_paragraph_text(str(item.get("status", "")))
            date = safe_paragraph_text(str(item.get("date", "")))

            # Status badge.
            status_lower = status.lower().replace(" ", "_") if status else ""
            tone = self.STATUS_TONES.get(status_lower, "primary")
            tone_hex = theme.resolve_tone(tone) if theme else "#7CB518"
            status_para = Paragraph(
                f'<font size="8" color="{tone_hex}"><b>{status.upper()}</b></font>',
                ParagraphStyle("Status", fontSize=8, leading=10),
            )

            # Content cell.
            content_parts: list[str] = []
            if item_title:
                content_parts.append(f"<b>{item_title}</b><br/>")
            if description:
                content_parts.append(f'<font size="9">{description}</font>')
            content_html = "".join(content_parts) or "&nbsp;"
            content_para = Paragraph(content_html, body_style)

            # Date cell.
            date_para = Paragraph(
                f'<font size="8" color="{muted_hex}">{date}</font>',
                ParagraphStyle("Date", fontSize=8, leading=10),
            )

            data_rows.append([status_para, content_para, date_para])

        table = Table(
            data_rows,
            colWidths=[status_width, content_width, date_width],
            hAlign="LEFT",
        )

        style_cmds = [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor(theme.resolve_tone("light") if theme else "#F5F5F5"),
            ),
        ]

        # Add alternating row backgrounds.
        stripe_color = theme.resolve_tone("light") if theme else "#F5F5F5"
        style_cmds.append(
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor(stripe_color)])
        )

        # Add grid lines.
        style_cmds.append(
            (
                "LINEBELOW",
                (0, 0),
                (-1, -2),
                0.5,
                colors.HexColor(theme.resolve_tone("muted") if theme else "#CCCCCC"),
            )
        )

        table.setStyle(TableStyle(style_cmds))

        flowables.append(table)
        flowables.append(Spacer(1, 8))
        return flowables
