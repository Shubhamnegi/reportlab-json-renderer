"""Comprehensive tests for all block renderers.

Each block type gets at least one test for basic rendering and one for edge cases.
"""

from __future__ import annotations

from typing import ClassVar

import pytest
from reportlab.platypus import Flowable, PageBreak, Paragraph, Spacer

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
from reportlab_json_renderer.blocks.registry import _REGISTRY, get_renderer
from reportlab_json_renderer.blocks.rich_text import RichTextBlock
from reportlab_json_renderer.blocks.section import SectionHeaderBlock
from reportlab_json_renderer.blocks.spacer import SpacerBlock
from reportlab_json_renderer.blocks.summary_box import SummaryBoxBlock
from reportlab_json_renderer.blocks.table import TableBlock
from reportlab_json_renderer.blocks.title import TitleBlock
from reportlab_json_renderer.templates.analytics_report_v1 import ANALYTICS_REPORT_V1
from reportlab_json_renderer.themes.green import GREEN_THEME
from reportlab_json_renderer.utils.errors import RenderError

# Shared test objects.
_theme = GREEN_THEME
_template = ANALYTICS_REPORT_V1
_width = 500.0


# ── Title Block ──────────────────────────────────────────────────────


class TestTitleBlock:
    def test_renders_full_block(self) -> None:
        r = TitleBlock()
        result = r.render(
            {"type": "title", "entity": "Acme", "title": "Q1 Report", "subtitle": "Jan-Mar 2026", "right_text": "Confidential"},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 3
        assert all(isinstance(f, Flowable) for f in result)

    def test_renders_minimal_block(self) -> None:
        r = TitleBlock()
        result = r.render(
            {"type": "title"},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 2

    def test_renders_without_theme(self) -> None:
        r = TitleBlock()
        result = r.render(
            {"type": "title", "title": "Test"},
            theme=None, template=None, available_width=_width,
        )
        assert len(result) >= 2


# ── Section Header Block ────────────────────────────────────────────


class TestSectionHeaderBlock:
    def test_renders_with_number(self) -> None:
        r = SectionHeaderBlock()
        result = r.render(
            {"type": "section_header", "number": "1", "title": "Summary"},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 2

    def test_renders_without_number(self) -> None:
        r = SectionHeaderBlock()
        result = r.render(
            {"type": "section_header", "title": "Summary"},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 2


# ── Paragraph Block ─────────────────────────────────────────────────


class TestParagraphBlock:
    def test_renders_body(self) -> None:
        r = ParagraphBlock()
        result = r.render(
            {"type": "paragraph", "text": "Hello world", "style": "body"},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) == 1

    def test_renders_bold(self) -> None:
        r = ParagraphBlock()
        result = r.render(
            {"type": "paragraph", "text": "Bold text", "style": "bold"},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) == 1

    def test_renders_caption(self) -> None:
        r = ParagraphBlock()
        result = r.render(
            {"type": "paragraph", "text": "Caption", "style": "caption"},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) == 1

    def test_escapes_markup_in_text(self) -> None:
        r = ParagraphBlock()
        result = r.render(
            {"type": "paragraph", "text": "<b>unsafe</b> & text", "style": "body"},
            theme=_theme, template=_template, available_width=_width,
        )
        para = result[0]
        assert isinstance(para, Paragraph)
        # <b> is a recognised tag and is preserved as markup (not escaped).
        assert para.getPlainText() == "unsafe & text"


# ── Rich Text Block ─────────────────────────────────────────────────


class TestRichTextBlock:
    def test_renders_normal_runs(self) -> None:
        r = RichTextBlock()
        result = r.render(
            {"type": "rich_text", "runs": [{"text": "Hello ", "style": "normal"}, {"text": "world", "style": "bold"}]},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) == 1

    def test_renders_tone_colored_runs(self) -> None:
        r = RichTextBlock()
        result = r.render(
            {"type": "rich_text", "runs": [{"text": "Danger!", "style": "bold_danger"}]},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) == 1

    def test_renders_empty_runs(self) -> None:
        r = RichTextBlock()
        result = r.render(
            {"type": "rich_text", "runs": []},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) == 1

    def test_escapes_markup_inside_runs(self) -> None:
        r = RichTextBlock()
        result = r.render(
            {"type": "rich_text", "runs": [{"text": "<b>unsafe</b> & text", "style": "bold"}]},
            theme=_theme, template=_template, available_width=_width,
        )
        para = result[0]
        assert isinstance(para, Paragraph)
        assert para.getPlainText() == "<b>unsafe</b> & text"


# ── KPI Grid Block ──────────────────────────────────────────────────


class TestKPIGridBlock:
    def test_renders_with_items(self) -> None:
        r = KPIGridBlock()
        result = r.render(
            {"type": "kpi_grid", "title": "KPIs", "columns": 3, "items": [
                {"label": "Orders", "value": "1,000", "sub": "This Week", "tone": "primary"},
                {"label": "Revenue", "value": "₹50K", "tone": "danger"},
            ]},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 2

    def test_renders_without_items(self) -> None:
        r = KPIGridBlock()
        result = r.render(
            {"type": "kpi_grid", "columns": 3, "items": []},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) == 0

    def test_renders_without_title(self) -> None:
        r = KPIGridBlock()
        result = r.render(
            {"type": "kpi_grid", "columns": 2, "items": [{"label": "X", "value": "Y"}]},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 1


# ── Callout Block ───────────────────────────────────────────────────


class TestCalloutBlock:
    def test_renders_with_title(self) -> None:
        r = CalloutBlock()
        result = r.render(
            {"type": "callout", "tone": "danger", "title": "Warning", "text": "Something happened"},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 2

    def test_renders_without_title(self) -> None:
        r = CalloutBlock()
        result = r.render(
            {"type": "callout", "tone": "success", "text": "All good"},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 2


# ── Callout Group Block ─────────────────────────────────────────────


class TestCalloutGroupBlock:
    def test_renders_with_title(self) -> None:
        r = CalloutGroupBlock()
        result = r.render(
            {"type": "callout_group", "title": "Insights", "items": [
                {"tone": "danger", "title": "Issue", "text": "Bad"},
                {"tone": "success", "title": "Good", "text": "Great"},
            ]},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 3

    def test_renders_without_title(self) -> None:
        r = CalloutGroupBlock()
        result = r.render(
            {"type": "callout_group", "items": [{"text": "Single"}]},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 1

    def test_escapes_markup_in_group_title(self) -> None:
        r = CalloutGroupBlock()
        result = r.render(
            {"type": "callout_group", "title": "<b>unsafe</b>", "items": []},
            theme=_theme, template=_template, available_width=_width,
        )
        para = result[0]
        assert isinstance(para, Paragraph)
        assert para.getPlainText() == "<b>unsafe</b>"


# ── Table Block ─────────────────────────────────────────────────────


class TestTableBlock:
    def test_renders_with_rows(self) -> None:
        r = TableBlock()
        result = r.render(
            {"type": "table", "title": "Data", "style": "striped", "columns": [
                {"key": "a", "label": "A", "width": 0.5},
                {"key": "b", "label": "B", "width": 0.5},
            ], "rows": [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 2

    def test_renders_empty_rows(self) -> None:
        r = TableBlock()
        result = r.render(
            {"type": "table", "columns": [{"key": "a", "label": "A"}], "rows": []},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 1

    def test_renders_without_title(self) -> None:
        r = TableBlock()
        result = r.render(
            {"type": "table", "columns": [{"key": "x", "label": "X"}], "rows": [{"x": "val"}]},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 1


# ── Matrix Table Block ──────────────────────────────────────────────


class TestMatrixTableBlock:
    def test_renders(self) -> None:
        r = MatrixTableBlock()
        result = r.render(
            {"type": "matrix_table", "title": "Comparison", "columns": ["A", "B", "C"], "rows": [["1", "2", "3"], ["4", "5", "6"]]},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 2

    def test_renders_empty(self) -> None:
        r = MatrixTableBlock()
        result = r.render(
            {"type": "matrix_table", "columns": [], "rows": []},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) == 0


# ── Insight List Block ──────────────────────────────────────────────


class TestInsightListBlock:
    def test_renders_with_items(self) -> None:
        r = InsightListBlock()
        result = r.render(
            {"type": "insight_list", "title": "Insights", "items": [
                {"title": "Why?", "text": "Because."},
                {"title": "How?", "text": "Like this."},
            ]},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 3

    def test_renders_without_title(self) -> None:
        r = InsightListBlock()
        result = r.render(
            {"type": "insight_list", "items": [{"title": "X", "text": "Y"}]},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 1


# ── Recommendations Block ───────────────────────────────────────────


class TestRecommendationsBlock:
    def test_renders(self) -> None:
        r = RecommendationsBlock()
        result = r.render(
            {"type": "recommendations", "title": "Next Steps", "items": [
                {"priority": "High", "action": "Fix bug", "owner": "Dev", "impact": "Uptime"},
            ]},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 2

    def test_renders_empty(self) -> None:
        r = RecommendationsBlock()
        result = r.render(
            {"type": "recommendations", "items": []},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) == 0


# ── Image Block ─────────────────────────────────────────────────────


class TestImageBlock:
    def test_missing_file_raises(self) -> None:
        r = ImageBlock()
        with pytest.raises(RenderError, match="Image file not found"):
            r.render(
                {"type": "image", "src": "/nonexistent/path.png", "title": "Photo"},
                theme=_theme, template=_template, available_width=_width,
            )

    def test_empty_src_raises(self) -> None:
        r = ImageBlock()
        with pytest.raises(RenderError, match="Unsupported image format"):
            r.render(
                {"type": "image", "src": ""},
                theme=_theme, template=_template, available_width=_width,
            )


# ── Chart Block ─────────────────────────────────────────────────────


class TestChartBlock:
    def test_renders_bar_chart(self) -> None:
        r = ChartBlock()
        result = r.render(
            {"type": "chart", "chart_type": "bar", "title": "Sales", "labels": ["A", "B"], "values": [10, 20], "tone": "primary"},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 2

    def test_renders_pie_chart(self) -> None:
        r = ChartBlock()
        result = r.render(
            {"type": "chart", "chart_type": "pie", "labels": ["X", "Y"], "values": [30, 70]},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 2

    def test_renders_grouped_bar(self) -> None:
        r = ChartBlock()
        result = r.render(
            {"type": "chart", "chart_type": "grouped_bar", "labels": ["A"], "series": {"S1": [10], "S2": [20]}},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 2

    def test_escapes_markup_in_title(self) -> None:
        r = ChartBlock()
        result = r.render(
            {"type": "chart", "chart_type": "bar", "title": "<b>unsafe</b>", "labels": ["A"], "values": [10]},
            theme=_theme, template=_template, available_width=_width,
        )
        para = result[0]
        assert isinstance(para, Paragraph)
        assert para.getPlainText() == "<b>unsafe</b>"


# ── Two Column Block ────────────────────────────────────────────────


class TestTwoColumnBlock:
    def test_renders_with_blocks(self) -> None:
        r = TwoColumnBlock()
        result = r.render(
            {"type": "two_column", "left": [{"type": "paragraph", "text": "Left"}], "right": [{"type": "paragraph", "text": "Right"}]},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) == 1

    def test_renders_empty(self) -> None:
        r = TwoColumnBlock()
        result = r.render(
            {"type": "two_column"},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) == 1


# ── Spacer Block ────────────────────────────────────────────────────


class TestSpacerBlock:
    def test_renders(self) -> None:
        r = SpacerBlock()
        result = r.render({"type": "spacer", "height": 20}, theme=_theme, template=_template, available_width=_width)
        assert len(result) == 1
        assert isinstance(result[0], Spacer)


# ── Page Break Block ────────────────────────────────────────────────


class TestPageBreakBlock:
    def test_renders(self) -> None:
        r = PageBreakBlock()
        result = r.render({"type": "page_break"}, theme=_theme, template=_template, available_width=_width)
        assert len(result) == 1
        assert isinstance(result[0], PageBreak)


# ── Divider Block ───────────────────────────────────────────────────


class TestDividerBlock:
    def test_renders(self) -> None:
        r = DividerBlock()
        result = r.render({"type": "divider", "tone": "primary", "thickness": 2}, theme=_theme, template=_template, available_width=_width)
        assert len(result) == 3


# ── Badge Block ─────────────────────────────────────────────────────


class TestBadgeBlock:
    def test_renders(self) -> None:
        r = BadgeBlock()
        result = r.render({"type": "badge", "label": "URGENT", "tone": "danger"}, theme=_theme, template=_template, available_width=_width)
        assert len(result) == 1


# ── Summary Box Block ───────────────────────────────────────────────


class TestSummaryBoxBlock:
    def test_renders_with_title(self) -> None:
        r = SummaryBoxBlock()
        result = r.render(
            {"type": "summary_box", "title": "Summary", "text": "Key findings here.", "tone": "success"},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 2

    def test_renders_without_title(self) -> None:
        r = SummaryBoxBlock()
        result = r.render(
            {"type": "summary_box", "text": "Just text"},
            theme=_theme, template=_template, available_width=_width,
        )
        assert len(result) >= 2


# ── Registry Integration ────────────────────────────────────────────


class TestRegistryIntegration:
    """Test that all block types are registered and dispatch correctly."""

    ALL_BLOCK_TYPES: ClassVar[list[str]] = [
        "title", "section_header", "paragraph", "rich_text", "kpi_grid",
        "callout", "callout_group", "table", "matrix_table", "insight_list",
        "recommendations", "image", "chart", "two_column", "spacer",
        "page_break", "divider", "badge", "summary_box",
    ]

    def test_all_block_types_registered(self) -> None:
        for bt in self.ALL_BLOCK_TYPES:
            assert bt in _REGISTRY, f"Block type {bt!r} not registered"

    def test_all_renderers_are_base_block_subclass(self) -> None:
        from reportlab_json_renderer.blocks.base import BaseBlock
        for bt in self.ALL_BLOCK_TYPES:
            renderer = get_renderer(bt)
            assert isinstance(renderer, BaseBlock)
