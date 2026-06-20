"""Block renderer registry.

Maps block type names (from the JSON ``"type"`` field) to their renderer
instances.  Renderers are registered at import time via :func:`register`
or lazily via :func:`get_renderer`.
"""

from __future__ import annotations

from typing import Any

from reportlab.platypus import Flowable

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.utils.errors import RenderError

# type → renderer instance
_REGISTRY: dict[str, BaseBlock] = {}


def register(renderer: BaseBlock) -> None:
    """Register a block renderer instance.

    Args:
        renderer: A :class:`BaseBlock` subclass instance.

    Raises:
        ValueError: If a renderer for ``renderer.block_type`` is already
            registered.
    """
    if renderer.block_type in _REGISTRY:
        raise ValueError(f"Renderer for block type {renderer.block_type!r} already registered.")
    _REGISTRY[renderer.block_type] = renderer


def get_renderer(block_type: str) -> BaseBlock:
    """Look up a renderer by block type.

    Args:
        block_type: The JSON ``"type"`` value (e.g. ``"title"``).

    Returns:
        The matching :class:`BaseBlock` instance.

    Raises:
        RenderError: If no renderer is registered for this block type.
    """
    if block_type not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY))
        raise RenderError(
            f"No renderer for block type {block_type!r}. Registered types: {available}"
        )
    return _REGISTRY[block_type]


def list_registered() -> list[str]:
    """Return sorted list of all registered block type names."""
    return sorted(_REGISTRY)


def render_block(
    block: dict[str, Any],
    *,
    theme: Any,
    template: Any,
    available_width: float,
) -> list[Flowable]:
    """Dispatch a single block dict to the correct renderer.

    Args:
        block: The block dictionary from the JSON spec.
        theme: Active theme.
        template: Active template.
        available_width: Usable width in points.

    Returns:
        List of ReportLab flowables.

    Raises:
        RenderError: If the block type is unknown or rendering fails.
    """
    block_type = block.get("type", "")
    renderer = get_renderer(block_type)

    # Validate returns warnings but does not block rendering.
    renderer.validate(block)
    return renderer.render(
        block,
        theme=theme,
        template=template,
        available_width=available_width,
    )
