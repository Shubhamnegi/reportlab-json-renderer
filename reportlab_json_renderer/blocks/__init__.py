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

# ── Auto-register all built-in block renderers ──────────────────────


def _register_builtins() -> None:
    """Register all built-in block renderers on first import."""
    from reportlab_json_renderer.blocks.badge import BadgeBlock
    from reportlab_json_renderer.blocks.callout import CalloutBlock
    from reportlab_json_renderer.blocks.callout_group import CalloutGroupBlock
    from reportlab_json_renderer.blocks.chart import ChartBlock
    from reportlab_json_renderer.blocks.divider import DividerBlock
    from reportlab_json_renderer.blocks.image import ImageBlock
    from reportlab_json_renderer.blocks.insight_list import InsightListBlock
    from reportlab_json_renderer.blocks.kpi_grid import KPIGridBlock
    from reportlab_json_renderer.blocks.layout import TwoColumnBlock
    from reportlab_json_renderer.blocks.matrix_table import MatrixTableBlock
    from reportlab_json_renderer.blocks.page_break import PageBreakBlock
    from reportlab_json_renderer.blocks.paragraph import ParagraphBlock
    from reportlab_json_renderer.blocks.recommendations import RecommendationsBlock
    from reportlab_json_renderer.blocks.registry import _REGISTRY
    from reportlab_json_renderer.blocks.rich_text import RichTextBlock
    from reportlab_json_renderer.blocks.section import SectionHeaderBlock
    from reportlab_json_renderer.blocks.spacer import SpacerBlock
    from reportlab_json_renderer.blocks.summary_box import SummaryBoxBlock
    from reportlab_json_renderer.blocks.table import TableBlock
    from reportlab_json_renderer.blocks.title import TitleBlock

    for renderer_cls in (
        TitleBlock, SectionHeaderBlock, ParagraphBlock, RichTextBlock,
        KPIGridBlock, CalloutBlock, CalloutGroupBlock, TableBlock,
        MatrixTableBlock, InsightListBlock, RecommendationsBlock,
        ImageBlock, ChartBlock, TwoColumnBlock, SpacerBlock,
        PageBreakBlock, DividerBlock, BadgeBlock, SummaryBoxBlock,
    ):
        r = renderer_cls()
        if r.block_type not in _REGISTRY:
            _REGISTRY[r.block_type] = r


_register_builtins()
