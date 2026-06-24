"""reportlab-json-renderer: JSON-driven PDF generation over ReportLab."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from reportlab_json_renderer.renderer import build_pdf

__version__ = "0.3.0"


def render_pdf(
    spec: dict[str, Any],
    output_path: str | None = None,
    *,
    allow_partial: bool = False,
    asset_root: str | Path | None = None,
) -> dict[str, Any]:
    """Render a PDF from a validated JSON specification.

    Args:
        spec: The JSON document specification conforming to the report schema.
        output_path: Optional filesystem path for the generated PDF.
            If ``None``, the PDF is returned as bytes only.
        allow_partial: If ``True``, continue after block-level render errors and
            return them as warnings. If ``False``, raise on the first block-level
            render failure.
        asset_root: Directory boundary for local assets such as images. Relative
            image paths are resolved under this root, and traversal outside it is
            rejected. Defaults to the current working directory.

    Returns:
        A result dictionary containing:
            - ``success`` (bool): Whether rendering completed without errors.
            - ``path`` (str | None): The output file path, if written.
            - ``bytes`` (bytes | None): Raw PDF bytes when no output_path given.
            - ``pages`` (int): Number of pages in the generated PDF.
            - ``warnings`` (list[str]): Non-fatal warnings collected during render.
            - ``metadata`` (dict): Echo of template and theme used.

    Raises:
        reportlab_json_renderer.utils.errors.ValidationError:
            If the spec fails schema validation.
        reportlab_json_renderer.utils.errors.RenderError:
            If a block cannot be rendered.
    """
    return build_pdf(
        spec,
        output_path=output_path,
        allow_partial=allow_partial,
        asset_root=asset_root,
    )


__all__ = ["__version__", "render_pdf"]
