"""Tests for the core rendering pipeline.

Covers:
  - render_pdf with minimal and full specs
  - PDF output to file and bytes
  - Validation error propagation
  - Warning collection for failed blocks
  - Template/theme resolution integration
"""

from __future__ import annotations

from pathlib import Path

import pytest

from reportlab_json_renderer import render_pdf
from reportlab_json_renderer.utils.errors import RenderError, ValidationError

# ── Helpers ──────────────────────────────────────────────────────────


def _minimal_spec(**overrides: object) -> dict:
    """Build a minimal valid spec with optional overrides."""
    spec: dict = {
        "version": "1.0",
        "template": "analytics_report_v1",
        "theme": "green",
        "metadata": {
            "entity_name": "Test Entity",
            "report_title": "Test Report",
        },
        "blocks": [],
    }
    spec.update(overrides)
    return spec


def _spec_with_blocks(blocks: list[dict]) -> dict:
    return {
        "version": "1.0",
        "template": "analytics_report_v1",
        "theme": "green",
        "metadata": {
            "entity_name": "Test Entity",
            "report_title": "Test Report",
            "period": "1 Jun - 7 Jun 2026",
            "powered_by": "Public PDF Renderer",
        },
        "blocks": blocks,
    }


# ── Basic Rendering ─────────────────────────────────────────────────


class TestRenderPDFMinimal:
    def test_empty_blocks_to_bytes(self) -> None:
        result = render_pdf(_minimal_spec())
        assert result["success"] is True
        assert result["path"] is None
        assert result["bytes"] is not None
        assert len(result["bytes"]) > 0
        assert result["pages"] == 1
        assert result["warnings"] == []
        assert result["metadata"]["template"] == "analytics_report_v1"
        assert result["metadata"]["theme"] == "green"

    def test_empty_blocks_to_file(self, tmp_path: Path) -> None:
        out = tmp_path / "output.pdf"
        result = render_pdf(_minimal_spec(), output_path=str(out))
        assert result["success"] is True
        assert result["path"] == str(out)
        assert result["bytes"] is None
        assert result["pages"] == 1
        assert out.exists()
        assert out.stat().st_size > 0


# ── Blocks Rendering ────────────────────────────────────────────────


class TestRenderWithBlocks:
    def test_title_block(self) -> None:
        spec = _spec_with_blocks([
            {"type": "title", "entity": "Acme", "title": "Q1 Report"},
        ])
        result = render_pdf(spec)
        assert result["success"] is True
        assert result["bytes"] is not None

    def test_multiple_blocks(self) -> None:
        spec = _spec_with_blocks([
            {"type": "title", "entity": "Acme", "title": "Report"},
            {"type": "section_header", "number": "1", "title": "Summary"},
            {"type": "paragraph", "text": "This is a test paragraph."},
            {"type": "spacer", "height": 12},
            {"type": "divider"},
            {"type": "page_break"},
            {"type": "paragraph", "text": "Page 2 content."},
        ])
        result = render_pdf(spec)
        assert result["success"] is True

    def test_table_block(self) -> None:
        spec = _spec_with_blocks([
            {"type": "table", "title": "Data", "columns": [
                {"key": "a", "label": "A", "width": 0.5},
                {"key": "b", "label": "B", "width": 0.5},
            ], "rows": [{"a": "1", "b": "2"}]},
        ])
        result = render_pdf(spec)
        assert result["success"] is True

    def test_chart_block(self) -> None:
        spec = _spec_with_blocks([
            {"type": "chart", "chart_type": "bar", "labels": ["A", "B"], "values": [10, 20]},
        ])
        result = render_pdf(spec)
        assert result["success"] is True

    def test_kpi_grid_block(self) -> None:
        spec = _spec_with_blocks([
            {"type": "kpi_grid", "columns": 2, "items": [
                {"label": "Orders", "value": "1,000"},
                {"label": "Revenue", "value": "₹50K"},
            ]},
        ])
        result = render_pdf(spec)
        assert result["success"] is True

    def test_callout_block(self) -> None:
        spec = _spec_with_blocks([
            {"type": "callout", "tone": "danger", "text": "Warning!"},
        ])
        result = render_pdf(spec)
        assert result["success"] is True

    def test_image_block_resolves_within_asset_root(self, tmp_path: Path) -> None:
        from PIL import Image as PILImage

        image_path = tmp_path / "chart.png"
        PILImage.new("RGB", (20, 20), color=(124, 181, 24)).save(image_path, "PNG")
        spec = _spec_with_blocks([
            {"type": "image", "src": "chart.png"},
        ])
        result = render_pdf(spec, asset_root=tmp_path)
        assert result["success"] is True


# ── Theme / Template Variations ─────────────────────────────────────


class TestThemeTemplateVariations:
    def test_neutral_theme(self) -> None:
        spec = _minimal_spec(theme="neutral")
        result = render_pdf(spec)
        assert result["success"] is True

    def test_dark_theme(self) -> None:
        spec = _minimal_spec(theme="dark")
        result = render_pdf(spec)
        assert result["success"] is True

    def test_business_template(self) -> None:
        spec = _minimal_spec(template="business_report_v1")
        result = render_pdf(spec)
        assert result["success"] is True

    def test_invoice_template(self) -> None:
        spec = _minimal_spec(template="invoice_v1")
        result = render_pdf(spec)
        assert result["success"] is True

    def test_compact_template(self) -> None:
        spec = _minimal_spec(template="compact_report_v1")
        result = render_pdf(spec)
        assert result["success"] is True


# ── Page Config ──────────────────────────────────────────────────────


class TestPageConfig:
    def test_landscape_orientation(self) -> None:
        spec = _minimal_spec(page={"size": "A4", "orientation": "landscape"})
        result = render_pdf(spec)
        assert result["success"] is True

    def test_custom_margins(self) -> None:
        spec = _minimal_spec(page={"margins": {"left_cm": 3.0, "right_cm": 3.0}})
        result = render_pdf(spec)
        assert result["success"] is True


# ── Validation Errors ───────────────────────────────────────────────


class TestValidationErrors:
    def test_invalid_spec_raises(self) -> None:
        with pytest.raises(ValidationError):
            render_pdf({})

    def test_missing_metadata_raises(self) -> None:
        with pytest.raises(ValidationError):
            render_pdf({"version": "1.0", "template": "x"})


# ── Warning Collection ──────────────────────────────────────────────


class TestWarnings:
    def test_template_disallowed_block_generates_warning(self) -> None:
        spec = _minimal_spec(
            template="invoice_v1",
            blocks=[{"type": "chart", "chart_type": "bar", "labels": ["A"], "values": [1]}],
        )
        result = render_pdf(spec)
        assert result["success"] is True
        assert any("not allowed by template invoice_v1" in warning for warning in result["warnings"])

    def test_validation_warnings_are_returned(self) -> None:
        spec = _spec_with_blocks([
            {
                "type": "table",
                "columns": [{"key": "a", "label": "A", "width": 0.8}],
                "rows": [{"a": "1", "extra": "2"}],
            },
        ])
        result = render_pdf(spec)
        assert result["success"] is True
        assert any("widths sum" in warning for warning in result["warnings"])
        assert any("extra keys" in warning for warning in result["warnings"])

    def test_broken_block_raises_by_default(self) -> None:
        """A block render failure should fail the render by default."""
        spec = _spec_with_blocks([
            {
                "type": "two_column",
                "left": [{"type": "missing_renderer"}],
                "right": [],
            },
        ])
        with pytest.raises(RenderError, match="Block 0 \\(two_column\\):"):
            render_pdf(spec)

    def test_broken_block_can_be_downgraded_to_warning(self) -> None:
        """Partial rendering remains an explicit opt-in."""
        spec = _spec_with_blocks([
            {
                "type": "two_column",
                "left": [{"type": "missing_renderer"}],
                "right": [],
            },
        ])
        result = render_pdf(spec, allow_partial=True)
        assert result["success"] is True
        assert any("Block 0 (two_column):" in warning for warning in result["warnings"])

    def test_image_path_traversal_is_rejected(self, tmp_path: Path) -> None:
        from PIL import Image as PILImage

        outside = tmp_path.parent / "outside.png"
        PILImage.new("RGB", (20, 20), color=(124, 181, 24)).save(outside, "PNG")
        spec = _spec_with_blocks([
            {"type": "image", "src": "../outside.png"},
        ])
        with pytest.raises(RenderError, match="Image path escapes the allowed asset root"):
            render_pdf(spec, asset_root=tmp_path)


# ── Header / Footer ─────────────────────────────────────────────────


class TestHeaderFooter:
    def test_header_footer_enabled(self) -> None:
        spec = _minimal_spec(
            header={"enabled": True, "variant": "default"},
            footer={"enabled": True, "show_page_number": True},
        )
        result = render_pdf(spec)
        assert result["success"] is True

    def test_header_footer_disabled(self) -> None:
        spec = _minimal_spec(
            header={"enabled": False},
            footer={"enabled": False},
        )
        result = render_pdf(spec)
        assert result["success"] is True


# ── Full Report Smoke Test ──────────────────────────────────────────


class TestFullReportSmoke:
    def test_full_report_from_fixture(self) -> None:
        from tests.conftest import load_fixture
        spec = load_fixture("full_spec")
        result = render_pdf(spec)
        assert result["success"] is True
        assert result["bytes"] is not None
        assert len(result["bytes"]) > 1000  # non-trivial PDF

    def test_full_report_to_file(self, tmp_path: Path) -> None:
        from tests.conftest import load_fixture
        spec = load_fixture("full_spec")
        out = tmp_path / "full_report.pdf"
        result = render_pdf(spec, output_path=str(out))
        assert result["success"] is True
        assert out.exists()
        assert out.stat().st_size > 1000
