"""Core rendering pipeline.

Orchestrates validation, normalisation, template/theme resolution,
block dispatch, and PDF assembly.
"""

from __future__ import annotations

import io
import json
import re
from hashlib import md5
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import A3, A4, LEGAL, LETTER
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    Frame,
    PageTemplate,
    SimpleDocTemplate,
    Spacer,
)

from reportlab_json_renderer.blocks.registry import render_block
from reportlab_json_renderer.schema.validators import validate_spec
from reportlab_json_renderer.templates import get_template
from reportlab_json_renderer.themes import get_theme
from reportlab_json_renderer.utils.errors import RenderError, ValidationError
from reportlab_json_renderer.utils.fonts import ensure_unicode_fonts
from reportlab_json_renderer.utils.images import load_local_image
from reportlab_json_renderer.utils.units import cm_to_pt

# Page size mapping.
_PAGE_SIZES: dict[str, tuple[float, float]] = {
    "a4": A4,
    "letter": LETTER,
    "legal": LEGAL,
    "a3": A3,
}


def build_pdf(
    spec: dict[str, Any],
    output_path: str | None = None,
    *,
    allow_partial: bool = False,
    asset_root: str | Path | None = None,
) -> dict[str, Any]:
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
        allow_partial: If ``True``, continue after block-level render errors and
            return them as warnings. If ``False``, raise on the first block-level
            render failure.
        asset_root: Directory boundary for local assets such as images. Relative
            image paths are resolved under this root, and traversal outside it is
            rejected. Defaults to the current working directory.

    Returns:
        Result dictionary with keys: success, path, bytes, pages, warnings, metadata.
    """
    warnings: list[str] = []

    # ── 0. Register Unicode fonts ────────────────────────────────────
    ensure_unicode_fonts()

    # ── 1. Validate ──────────────────────────────────────────────────
    validation_result = validate_spec(spec)
    if not validation_result.valid:
        msg = "Spec validation failed:\n" + "\n".join(
            f"  - {error}" for error in validation_result.errors
        )
        raise ValidationError(msg)
    parsed = validation_result.parsed
    warnings.extend(validation_result.warnings)

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
    resolved_asset_root = _resolve_asset_root(asset_root)

    # ── 5. Build flowables from blocks ───────────────────────────────
    flowables = []
    for idx, block in enumerate(parsed.blocks):
        block_dict = block.model_dump() if hasattr(block, "model_dump") else block
        block_type = block_dict.get("type", "?")
        try:
            block_dict = _normalize_block_assets(
                block_dict,
                asset_root=resolved_asset_root,
            )
            if not tpl.is_block_allowed(block_type):
                warnings.append(f"Block {idx} ({block_type}): not allowed by template {tpl.name}")
                continue
            block_flowables = render_block(
                block_dict,
                theme=theme,
                template=tpl,
                available_width=frame_width,
            )
            flowables.extend(block_flowables)
        except Exception as exc:
            message = f"Block {idx} ({block_type}): {exc}"
            if allow_partial:
                warnings.append(message)
                continue
            raise RenderError(message) from exc

    if not flowables:
        flowables.append(Spacer(1, 1))

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

    doc.build(flowables, canvasmaker=_build_canvas)

    # ── 7. Assemble result ───────────────────────────────────────────
    result_bytes = None
    normalized_bytes = None
    if output_path is None and isinstance(buf, io.BytesIO):
        buf.seek(0)
        normalized_bytes = _normalize_pdf_bytes(buf.read(), spec)
        result_bytes = normalized_bytes
    elif output_path is not None:
        output_file = Path(output_path)
        normalized_bytes = _normalize_pdf_bytes(output_file.read_bytes(), spec)
        output_file.write_bytes(normalized_bytes)

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
            # Subtle header background.
            canvas.setFillColor(_hex_color(theme.resolve_tone("light") if theme else "#F5F5F5"))
            canvas.rect(
                0, page_h - top_margin - 5, page_w, top_margin + 5, fill=True, stroke=False
            )

            canvas.setFont(theme.font_bold if theme else "Helvetica-Bold", 8)
            canvas.setFillColor(_hex_color(theme.resolve_tone("muted") if theme else "#757575"))
            entity = metadata.entity_name if metadata and metadata.entity_name else ""
            period = metadata.period if metadata and metadata.period else ""
            canvas.drawString(left_margin, page_h - top_margin + 10, entity)
            canvas.drawRightString(page_w - right_margin, page_h - top_margin + 10, period)

            # Header line.
            canvas.setStrokeColor(
                _hex_color(theme.resolve_tone("primary") if theme else "#7CB518")
            )
            canvas.setLineWidth(0.5)
            canvas.line(
                left_margin,
                page_h - top_margin + 5,
                page_w - right_margin,
                page_h - top_margin + 5,
            )

        # Footer.
        if footer_enabled:
            # Footer separator line.
            canvas.setStrokeColor(
                _hex_color(theme.resolve_tone("primary") if theme else "#7CB518")
            )
            canvas.setLineWidth(0.5)
            canvas.line(left_margin, bottom_margin, page_w - right_margin, bottom_margin)

            canvas.setFont(theme.font_body if theme else "Helvetica", 8)
            canvas.setFillColor(_hex_color(theme.resolve_tone("muted") if theme else "#757575"))
            if show_page_num:
                canvas.drawCentredString(
                    page_w / 2, bottom_margin - 12, f"Page {canvas.getPageNumber()}"
                )

            powered_by = metadata.powered_by if metadata and metadata.powered_by else ""
            if powered_by:
                canvas.drawRightString(page_w - right_margin, bottom_margin - 12, powered_by)

        canvas.restoreState()

    template = PageTemplate(id="main", frames=[frame], onPage=_on_page)
    doc.addPageTemplates([template])

    return doc


def _build_canvas(*args: Any, **kwargs: Any) -> Canvas:
    """Create a deterministic ReportLab canvas where practical."""
    kwargs.setdefault("invariant", 1)
    kwargs.setdefault("pageCompression", 1)
    return Canvas(*args, **kwargs)


def _normalize_pdf_bytes(pdf_bytes: bytes, spec: dict[str, Any]) -> bytes:
    """Normalize volatile PDF metadata that still varies across renders."""
    normalized = re.sub(
        rb"D:\d{14}(?:[+-]\d{2}'\d{2}')?",
        b"D:20000101000000+00'00'",
        pdf_bytes,
    )
    spec_digest = (
        md5(
            json.dumps(spec, sort_keys=True, separators=(",", ":")).encode("utf-8"),
            usedforsecurity=False,
        )
        .hexdigest()
        .encode("ascii")
    )
    normalized = re.sub(
        rb"/ID\s*\[\s*<[^>]{32}>\s*<[^>]{32}>\s*\]",
        b"/ID [<" + spec_digest + b"><" + spec_digest + b">]",
        normalized,
    )
    return normalized


def _resolve_asset_root(asset_root: str | Path | None) -> Path:
    """Resolve the asset root used for local file validation."""
    if asset_root is None:
        return Path.cwd().resolve()
    return Path(asset_root).resolve()


def _normalize_block_assets(
    block: dict[str, Any],
    *,
    asset_root: Path,
) -> dict[str, Any]:
    """Resolve and validate local asset references within a block tree."""
    normalized = dict(block)
    block_type = normalized.get("type")

    if block_type == "image":
        normalized["src"] = str(
            load_local_image(normalized.get("src", ""), allowed_root=asset_root)
        )

    if block_type == "two_column":
        normalized["left"] = [
            _normalize_block_assets(child, asset_root=asset_root)
            for child in normalized.get("left", [])
        ]
        normalized["right"] = [
            _normalize_block_assets(child, asset_root=asset_root)
            for child in normalized.get("right", [])
        ]

    return normalized


def _hex_color(hex_str: str):
    """Convert a hex string to a ReportLab Color object."""
    from reportlab.lib.colors import HexColor

    return HexColor(hex_str)
