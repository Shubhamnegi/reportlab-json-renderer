"""Structural smoke tests for every built-in block type.

Each test renders a single block through the full PDF pipeline
(``build_pdf``) and verifies the output is a valid PDF by parsing it
with ``pypdf``.  This goes beyond the unit tests in
``test_block_renderers.py`` which only check that the renderer returns
flowables — here we verify the complete round-trip to PDF bytes.

The tests validate:
  - Rendering succeeds (``result["success"] is True``).
  - The PDF has at least one page.
  - The file / bytes are non-trivial.
  - Expected text is extractable from the rendered PDF (where applicable).
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

import pytest
from PIL import Image
from pypdf import PdfReader

from reportlab_json_renderer.renderer import build_pdf
from reportlab_json_renderer.utils.errors import RenderError

# ── Helpers ──────────────────────────────────────────────────────────


def _base_spec(*blocks: dict[str, Any]) -> dict[str, Any]:
    """Return a minimal valid spec wrapping the given blocks."""
    return {
        "version": "1.0",
        "template": "analytics_report_v1",
        "theme": "green",
        "metadata": {
            "entity_name": "Smoke Test",
            "report_title": "Component Smoke",
            "period": "2026",
            "powered_by": "Test Suite",
        },
        "blocks": list(blocks),
    }


def _render_and_parse(
    spec: dict[str, Any], **build_kwargs: Any
) -> tuple[dict[str, Any], PdfReader]:
    """Render a spec and return (result, parsed reader)."""
    result = build_pdf(spec, **build_kwargs)
    assert result["success"] is True, f"Render failed: {result}"
    assert result["bytes"] is not None
    assert len(result["bytes"]) > 0
    assert result["bytes"][:4] == b"%PDF"
    reader = PdfReader(BytesIO(result["bytes"]))
    assert len(reader.pages) >= 1
    return result, reader


def _extract_text(reader: PdfReader) -> str:
    """Concatenate text from all pages."""
    return "\n".join(page.extract_text() or "" for page in reader.pages)


# ── Title ────────────────────────────────────────────────────────────


class TestTitleSmoke:
    def test_title_renders_to_pdf(self) -> None:
        spec = _base_spec(
            {
                "type": "title",
                "entity": "Acme Corp",
                "title": "Q1 Revenue Report",
                "subtitle": "Jan–Mar 2026",
                "right_text": "Confidential",
            }
        )
        _result, reader = _render_and_parse(spec)
        text = _extract_text(reader)
        assert "Q1 Revenue Report" in text

    def test_minimal_title_renders(self) -> None:
        spec = _base_spec({"type": "title"})
        _render_and_parse(spec)


# ── Section Header ───────────────────────────────────────────────────


class TestSectionHeaderSmoke:
    def test_numbered_section_renders(self) -> None:
        spec = _base_spec(
            {
                "type": "section_header",
                "number": "1",
                "title": "Executive Summary",
            }
        )
        _result, reader = _render_and_parse(spec)
        text = _extract_text(reader)
        assert "Executive Summary" in text

    def test_unnumbered_section_renders(self) -> None:
        spec = _base_spec(
            {
                "type": "section_header",
                "title": "Appendix",
            }
        )
        _render_and_parse(spec)


# ── Paragraph ────────────────────────────────────────────────────────


class TestParagraphSmoke:
    def test_body_paragraph_renders(self) -> None:
        spec = _base_spec(
            {
                "type": "paragraph",
                "text": "Revenue increased by 15% year-over-year.",
                "style": "body",
            }
        )
        _result, reader = _render_and_parse(spec)
        text = _extract_text(reader)
        assert "Revenue increased" in text

    def test_all_styles_render(self) -> None:
        for style in ("body", "bold", "caption"):
            spec = _base_spec(
                {
                    "type": "paragraph",
                    "text": f"Style test: {style}",
                    "style": style,
                }
            )
            _result, reader = _render_and_parse(spec)
            text = _extract_text(reader)
            assert style in text


# ── Rich Text ────────────────────────────────────────────────────────


class TestRichTextSmoke:
    def test_mixed_runs_render(self) -> None:
        spec = _base_spec(
            {
                "type": "rich_text",
                "runs": [
                    {"text": "Orders grew ", "style": "normal"},
                    {"text": "12%", "style": "bold"},
                    {"text": " this month.", "style": "normal"},
                ],
            }
        )
        _result, reader = _render_and_parse(spec)
        text = _extract_text(reader)
        assert "Orders grew" in text
        assert "12%" in text

    def test_tone_colored_runs_render(self) -> None:
        spec = _base_spec(
            {
                "type": "rich_text",
                "runs": [
                    {"text": "Critical", "style": "bold_danger"},
                    {"text": " issue detected", "style": "normal"},
                ],
            }
        )
        _result, reader = _render_and_parse(spec)
        text = _extract_text(reader)
        assert "Critical" in text


# ── KPI Grid ─────────────────────────────────────────────────────────


class TestKPIGridSmoke:
    def test_kpi_grid_renders_to_pdf(self) -> None:
        spec = _base_spec(
            {
                "type": "kpi_grid",
                "title": "Key Metrics",
                "columns": 3,
                "items": [
                    {"label": "Orders", "value": "1,250", "sub": "This Week", "tone": "primary"},
                    {"label": "Revenue", "value": "₹2.5L", "sub": "↑ 12%", "tone": "success"},
                    {"label": "Returns", "value": "34", "sub": "↓ 5%", "tone": "danger"},
                ],
            }
        )
        _result, reader = _render_and_parse(spec)
        text = _extract_text(reader)
        assert "Key Metrics" in text
        assert "Orders" in text
        assert "Revenue" in text


# ── Callout ───────────────────────────────────────────────────────────


class TestCalloutSmoke:
    def test_callout_with_title_renders(self) -> None:
        spec = _base_spec(
            {
                "type": "callout",
                "tone": "danger",
                "title": "Alert",
                "text": "Order volume dropped 15% WoW.",
            }
        )
        _result, reader = _render_and_parse(spec)
        text = _extract_text(reader)
        assert "15%" in text

    def test_callout_without_title_renders(self) -> None:
        spec = _base_spec(
            {
                "type": "callout",
                "tone": "success",
                "text": "All systems operational.",
            }
        )
        _render_and_parse(spec)


# ── Callout Group ────────────────────────────────────────────────────


class TestCalloutGroupSmoke:
    def test_callout_group_renders(self) -> None:
        spec = _base_spec(
            {
                "type": "callout_group",
                "title": "Insights",
                "items": [
                    {"tone": "danger", "title": "Issue", "text": "Sales declining"},
                    {"tone": "success", "title": "Win", "text": "Retention up"},
                ],
            }
        )
        _result, reader = _render_and_parse(spec)
        text = _extract_text(reader)
        assert "Sales declining" in text
        assert "Retention up" in text


# ── Table ─────────────────────────────────────────────────────────────


class TestTableSmoke:
    def test_table_renders_to_pdf(self) -> None:
        spec = _base_spec(
            {
                "type": "table",
                "title": "Source Mix",
                "style": "striped",
                "columns": [
                    {"key": "source", "label": "Source", "width": 0.4},
                    {"key": "orders", "label": "Orders", "width": 0.3},
                    {"key": "revenue", "label": "Revenue", "width": 0.3},
                ],
                "rows": [
                    {"source": "Online", "orders": "2,000", "revenue": "₹5L"},
                    {"source": "Offline", "orders": "500", "revenue": "₹1.2L"},
                ],
            }
        )
        _result, reader = _render_and_parse(spec)
        text = _extract_text(reader)
        assert "Online" in text
        assert "2,000" in text

    def test_standard_style_renders(self) -> None:
        spec = _base_spec(
            {
                "type": "table",
                "title": "Standard",
                "style": "standard",
                "columns": [{"key": "a", "label": "A"}],
                "rows": [{"a": "1"}],
            }
        )
        _render_and_parse(spec)


# ── Matrix Table ─────────────────────────────────────────────────────


class TestMatrixTableSmoke:
    def test_matrix_renders_to_pdf(self) -> None:
        spec = _base_spec(
            {
                "type": "matrix_table",
                "title": "Comparison",
                "columns": ["Metric", "This Week", "Last Week"],
                "rows": [
                    ["Orders", "500", "450"],
                    ["Revenue", "₹2L", "₹1.8L"],
                ],
            }
        )
        _result, reader = _render_and_parse(spec)
        text = _extract_text(reader)
        assert "Metric" in text
        assert "This Week" in text


# ── Insight List ─────────────────────────────────────────────────────


class TestInsightListSmoke:
    def test_insight_list_renders(self) -> None:
        spec = _base_spec(
            {
                "type": "insight_list",
                "title": "Key Insights",
                "items": [
                    {"title": "Growth Driver", "text": "Mobile adoption increased 30%."},
                    {"title": "Risk", "text": "Churn rose in Tier-2 cities."},
                ],
            }
        )
        _result, reader = _render_and_parse(spec)
        text = _extract_text(reader)
        assert "Mobile adoption" in text
        assert "Churn" in text


# ── Recommendations ──────────────────────────────────────────────────


class TestRecommendationsSmoke:
    def test_recommendations_renders(self) -> None:
        spec = _base_spec(
            {
                "type": "recommendations",
                "title": "Next Steps",
                "items": [
                    {
                        "priority": "High",
                        "action": "Fix checkout bug",
                        "owner": "Eng",
                        "impact": "Revenue",
                    },
                    {
                        "priority": "Medium",
                        "action": "Run promo",
                        "owner": "Marketing",
                        "impact": "AOV",
                    },
                ],
            }
        )
        _result, reader = _render_and_parse(spec)
        text = _extract_text(reader)
        assert "Fix checkout bug" in text
        assert "Eng" in text


# ── Summary Box ──────────────────────────────────────────────────────


class TestSummaryBoxSmoke:
    def test_summary_box_renders(self) -> None:
        spec = _base_spec(
            {
                "type": "summary_box",
                "title": "Executive Summary",
                "text": "Overall performance is strong with 15% YoY growth.",
                "tone": "success",
            }
        )
        _result, reader = _render_and_parse(spec)
        text = _extract_text(reader)
        assert "Executive Summary" in text

    def test_summary_box_without_title_renders(self) -> None:
        spec = _base_spec(
            {
                "type": "summary_box",
                "text": "Quick summary.",
                "tone": "info",
            }
        )
        _render_and_parse(spec)


# ── Image ─────────────────────────────────────────────────────────────


class TestImageSmoke:
    def test_local_image_renders(self, tmp_path: Path) -> None:
        """Create a tiny PNG on disk and render it via the image block."""
        # 1x1 red PNG generated via Pillow to guarantee a valid file.
        img_path = tmp_path / "test.png"
        Image.new("RGB", (1, 1), "red").save(img_path, "PNG")

        spec = _base_spec(
            {
                "type": "image",
                "src": str(img_path),
                "title": "Test Image",
            }
        )
        _result, _reader = _render_and_parse(spec, asset_root=tmp_path)
        assert _result["pages"] >= 1

    def test_nonexistent_image_raises(self) -> None:
        spec = _base_spec(
            {
                "type": "image",
                "src": "/nonexistent/path.png",
            }
        )
        with pytest.raises(RenderError):
            build_pdf(spec)


# ── Chart ─────────────────────────────────────────────────────────────


class TestChartSmoke:
    def test_bar_chart_renders(self) -> None:
        spec = _base_spec(
            {
                "type": "chart",
                "chart_type": "bar",
                "title": "Monthly Sales",
                "labels": ["Jan", "Feb", "Mar"],
                "values": [100, 150, 120],
                "tone": "primary",
            }
        )
        _result, _reader = _render_and_parse(spec)
        assert _result["pages"] >= 1

    def test_pie_chart_renders(self) -> None:
        spec = _base_spec(
            {
                "type": "chart",
                "chart_type": "pie",
                "title": "Share",
                "labels": ["Direct", "Organic", "Referral"],
                "values": [40, 35, 25],
            }
        )
        _render_and_parse(spec)

    def test_grouped_bar_chart_renders(self) -> None:
        spec = _base_spec(
            {
                "type": "chart",
                "chart_type": "grouped_bar",
                "title": "Multi-Series",
                "labels": ["Q1", "Q2"],
                "series": {
                    "Product A": [100, 120],
                    "Product B": [80, 90],
                },
            }
        )
        _render_and_parse(spec)


# ── Two Column ────────────────────────────────────────────────────────


class TestTwoColumnSmoke:
    def test_two_column_renders(self) -> None:
        spec = _base_spec(
            {
                "type": "two_column",
                "left_width": 0.5,
                "right_width": 0.5,
                "left": [
                    {"type": "paragraph", "text": "Left column content."},
                ],
                "right": [
                    {"type": "paragraph", "text": "Right column content."},
                ],
            }
        )
        _result, reader = _render_and_parse(spec)
        text = _extract_text(reader)
        # Both columns should appear somewhere in the PDF.
        assert "Left column" in text
        assert "Right column" in text

    def test_empty_two_column_renders(self) -> None:
        spec = _base_spec({"type": "two_column"})
        _render_and_parse(spec)


# ── Spacer ────────────────────────────────────────────────────────────


class TestSpacerSmoke:
    def test_spacer_renders(self) -> None:
        spec = _base_spec({"type": "spacer", "height": 20})
        _result, _reader = _render_and_parse(spec)
        assert _result["pages"] >= 1


# ── Page Break ────────────────────────────────────────────────────────


class TestPageBreakSmoke:
    def test_page_break_creates_multiple_pages(self) -> None:
        spec = _base_spec(
            {"type": "paragraph", "text": "Page one."},
            {"type": "page_break"},
            {"type": "paragraph", "text": "Page two."},
        )
        _result, reader = _render_and_parse(spec)
        assert len(reader.pages) >= 2


# ── Divider ───────────────────────────────────────────────────────────


class TestDividerSmoke:
    def test_divider_renders(self) -> None:
        spec = _base_spec(
            {
                "type": "divider",
                "tone": "primary",
                "thickness": 1.5,
            }
        )
        _result, _reader = _render_and_parse(spec)
        assert _result["pages"] >= 1


# ── Badge ─────────────────────────────────────────────────────────────


class TestBadgeSmoke:
    def test_badge_renders(self) -> None:
        spec = _base_spec(
            {
                "type": "badge",
                "label": "URGENT",
                "tone": "danger",
            }
        )
        _result, reader = _render_and_parse(spec)
        text = _extract_text(reader)
        assert "URGENT" in text


# ── Cross-Block Integration ──────────────────────────────────────────


class TestCrossBlockSmoke:
    """Verify that combining multiple block types in one document works."""

    def test_all_blocks_in_one_document(self, tmp_path: Path) -> None:
        """The full_spec fixture renders and has expected structure."""
        fixture = Path(__file__).parent / "fixtures" / "full_spec.json"
        spec = __import__("json").loads(fixture.read_text(encoding="utf-8"))
        out = tmp_path / "all_blocks_smoke.pdf"

        result = build_pdf(spec, output_path=str(out))

        assert result["success"] is True
        assert out.exists()
        assert out.stat().st_size > 1_000

        reader = PdfReader(out)
        assert len(reader.pages) >= 1
        text = _extract_text(reader)
        assert "Demo Store" in text
        assert "Weekly Performance Report" in text

    def test_each_template_produces_valid_pdf(self, tmp_path: Path) -> None:
        """Every template renders the minimal spec without error."""
        minimal = {
            "version": "1.0",
            "template": "analytics_report_v1",
            "theme": "green",
            "metadata": {
                "entity_name": "Test",
                "report_title": "Test Report",
                "period": "2026",
                "powered_by": "Test Suite",
            },
            "blocks": [
                {"type": "paragraph", "text": "Hello from the smoke test."},
            ],
        }
        for tpl in (
            "analytics_report_v1",
            "business_report_v1",
            "compact_report_v1",
            "invoice_v1",
            "proposal_v1",
        ):
            spec = {**minimal, "template": tpl}
            result = build_pdf(spec)
            assert result["success"] is True, f"Template {tpl} failed"
            reader = PdfReader(BytesIO(result["bytes"]))
            assert len(reader.pages) >= 1
