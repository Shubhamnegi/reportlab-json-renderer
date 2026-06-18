"""Block renderers.

Each module in this package implements one block type (title, table, chart, …)
and is registered with the block registry so the renderer can dispatch by type.

Usage::

    from reportlab_json_renderer.blocks import get_renderer, render_block

    renderer = get_renderer("title")
    flowables = renderer.render(block_data, theme=theme, template=tpl, available_width=500)
"""

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.blocks.registry import (
    get_renderer,
    list_registered,
    register,
    render_block,
)

__all__ = [
    "BaseBlock",
    "get_renderer",
    "list_registered",
    "register",
    "render_block",
]
