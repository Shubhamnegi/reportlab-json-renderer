"""Core rendering pipeline.

Orchestrates validation, normalisation, template/theme resolution,
block dispatch, and PDF assembly.
"""

from __future__ import annotations

from typing import Any


def build_pdf(spec: dict[str, Any], output_path: str | None) -> dict[str, Any]:
    """Execute the full render pipeline and return a result dict.

    Args:
        spec: Validated JSON specification.
        output_path: Where to write the PDF, or ``None`` for bytes-only.

    Returns:
        Result dictionary with keys: success, path, bytes, pages, warnings, metadata.

    Note:
        This is a stub. Full implementation will be added in Phase 8.
    """
    raise NotImplementedError("build_pdf will be implemented in Phase 8")
