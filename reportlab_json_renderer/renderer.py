"""Core rendering pipeline.

Orchestrates validation, normalisation, template/theme resolution,
block dispatch, and PDF assembly.
"""

from __future__ import annotations

import io
from typing import Any

from reportlab.lib.pagesizes import A3, A4, LEGAL, LETTER
from reportlab.platypus import (
    Frame,
    PageTemplate,
    SimpleDocTemplate,
)

from reportlab_json_renderer.blocks.registry import render_block
from reportlab_json_renderer.schema.validators import validate_spec_or_raise
from reportlab_json_renderer.templates import get_template
from reportlab_json_renderer.themes import get_theme
from reportlab_json_renderer.utils.units import cm_to_pt

# Page size mapping.
_PAGE_SIZES: dict[str, tuple[float, float]] = {
    "a4": A4,
    "letter": LETTER,
    "legal": LEGAL,
    "a3": A3,
}


def build_pdf(spec: dict[str, Any], output_path: str | None = None) -> dict[str, Any]:
    """Execute the full render pipeline and return a result dict.

    Steps:
      1. Validate JSON spec via Pydantic.
      2. Resolve template by name.
      3. Resolve theme by name.
      4. Merge per-spec page overrides into template defaults.
      5. Iterate blocks, dispatch to registry, collect flowables.
      6. Build PDF with ReportLab (header/footer via page callbacks).
      7. Return structured result.

    Args:
        spec: Raw JSON specification dictionary.
        output_path: Where to write the PDF, or ``None`` for bytes-only.

    Returns:
        Result dictionary with keys: success, path, bytes, pages, warnings, metadata.
    """
    warnings: list[str] = []

    # ── 1. Validate ──────────────────────────────────────────────────
    parsed = validate_spec_or_raise(spec)

    # ── 2. Resolve template ──────────────────────────────────────────
    tpl = get_template(parsed.template)

    # ── 3. Resolve theme ─────────────────────────────────────────────
    theme = get_theme(parsed.theme)

    # ── 4. Merge page config ─────────────────────────────────────────
    spec_page = parsed.page.model_dump() if parsed.page else None
    page_config = tpl.merge_spec(spec_page)

    page_size_key = page_config.size.value.lower()
    page_size = _PAGE_SIZES.get(page_size_key, A4)
    orientation = page_config.orientation.value
    if orientation == "landscape":
        page_size = (page_size[1], page_size[0])

    left_margin = cm_to_pt(page_config.margins["left_cm"])
    right_margin = cm_to_pt(page_config.margins["right_cm"])
    top_margin = cm_to_pt(page_config.margins["top_cm"])
    bottom_margin = cm_to_pt(page_config.margins["bottom_cm"])

    frame_width = page_size[0] - left_margin - right_margin

    # ── 5. Build flowables from blocks ───────────────────────────────
    flowables = []
    for idx, block in enumerate(parsed.blocks):
        try:
            block_dict = block.model_dump() if hasattr(block, "model_dump") else block
            block_flowables = render_block(
                block_dict,
                theme=theme,
                template=tpl,
                available_width=frame_width,
            )
            flowables.extend(block_flowables)
        except Exception as exc:
            warnings.append(f"Block {idx} ({block_dict.get('type', '?')}): {exc}")

    # ── 6. Build PDF ─────────────────────────────────────────────────
    if output_path is not None:
        buf: io.BytesIO | str = str(output_path)
    else:
        buf = io.BytesIO()

    doc = _build_document(
        buf,
        page_size=page_size,
        left_margin=left_margin,
        right_margin=right_margin,
        top_margin=top_margin,
        bottom_margin=bottom_margin,
        frame_width=frame_width,
        page_height=page_size[1],
        header_config=parsed.header,
        footer_config=parsed.footer,
        metadata=parsed.metadata,
        theme=theme,
    )

    doc.build(flowables)

    # ── 7. Assemble result ───────────────────────────────────────────
    result_bytes = None
    if output_path is None and isinstance(buf, io.BytesIO):
        buf.seek(0)
        result_bytes = buf.read()

    return {
        "success": True,
        "path": output_path,
        "bytes": result_bytes,
        "pages": doc.page,
        "warnings": warnings,
        "metadata": {
            "template": parsed.template,
            "theme": parsed.theme,
        },
    }


def _build_document(
    buf: io.BytesIO | str,
    *,
    page_size: tuple[float, float],
    left_margin: float,
    right_margin: float,
    top_margin: float,
    bottom_margin: float,
    frame_width: float,
    page_height: float,
    header_config: Any,
    footer_config: Any,
    metadata: Any,
    theme: Any,
) -> SimpleDocTemplate:
    """Create a ReportLab SimpleDocTemplate with header/footer page templates."""
    header_enabled = header_config.enabled if header_config else True
    footer_enabled = footer_config.enabled if footer_config else True
    show_page_num = footer_config.show_page_number if footer_config else True

    # Header/footer dimensions.
    header_h = 30.0 if header_enabled else 0.0
    footer_h = 25.0 if footer_enabled else 0.0

    doc = SimpleDocTemplate(
        buf,
        pagesize=page_size,
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin + header_h,
        bottomMargin=bottom_margin + footer_h,
    )

    # Custom page template with header and footer drawing.
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        frame_width,
        page_height - doc.topMargin - doc.bottomMargin,
        id="main",
    )

    def _on_page(canvas: Any, doc: Any) -> None:
        """Draw header and footer on each page."""
        canvas.saveState()
        page_w, page_h = page_size

        # Header.
        if header_enabled:
            canvas.setFont(theme.font_bold if theme else "Helvetica-Bold", 8)
            canvas.setFillColor(
                _hex_color(theme.resolve_tone("muted") if theme else "#757575")
            )
            entity = metadata.entity_name if metadata else ""
            period = metadata.period if metadata else ""
            canvas.drawString(left_margin, page_h - top_margin + 10, entity)
            canvas.drawRightString(page_w - right_margin, page_h - top_margin + 10, period)

            # Header line.
            canvas.setStrokeColor(_hex_color(theme.resolve_tone("primary") if theme else "#7CB518"))
            canvas.setLineWidth(0.5)
            canvas.line(left_margin, page_h - top_margin + 5, page_w - right_margin, page_h - top_margin + 5)

        # Footer.
        if footer_enabled:
            canvas.setFont(theme.font_body if theme else "Helvetica", 7)
            canvas.setFillColor(
                _hex_color(theme.resolve_tone("muted") if theme else "#757575")
            )
            if show_page_num:
                canvas.drawCentredString(page_w / 2, bottom_margin - 10, f"Page {canvas.getPageNumber()}")

            powered_by = metadata.powered_by if metadata else ""
            if powered_by:
                canvas.drawRightString(page_w - right_margin, bottom_margin - 10, powered_by)

        canvas.restoreState()

    template = PageTemplate(id="main", frames=[frame], onPage=_on_page)
    doc.addPageTemplates([template])

    return doc


def _hex_color(hex_str: str):
    """Convert a hex string to a ReportLab Color object."""
    from reportlab.lib.colors import HexColor
    return HexColor(hex_str)
