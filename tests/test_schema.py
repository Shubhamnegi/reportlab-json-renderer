"""Tests for schema/base.py and schema/validators.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from reportlab_json_renderer.schema.base import (
    SUPPORTED_CHART_TYPES,
    ReportSpec,
)
from reportlab_json_renderer.schema.validators import (
    generate_schema_file,
    generate_schema_json,
    validate_spec,
    validate_spec_or_raise,
)
from reportlab_json_renderer.utils.errors import ValidationError
from tests.conftest import load_fixture

# ── Valid spec tests ─────────────────────────────────────────────────


class TestValidSpec:
    def test_minimal_spec(self, minimal_spec: dict) -> None:
        result = validate_spec(minimal_spec)
        assert result.valid is True
        assert result.errors == []
        assert result.parsed is not None
        assert result.parsed.version == "1.0"
        assert result.parsed.template == "analytics_report_v1"
        assert result.parsed.theme == "green"

    def test_sample_spec_with_blocks(self, sample_spec: dict) -> None:
        result = validate_spec(sample_spec)
        assert result.valid is True
        assert len(result.parsed.blocks) == 3  # type: ignore[union-attr]

    def test_parsed_metadata(self, minimal_spec: dict) -> None:
        result = validate_spec(minimal_spec)
        assert result.parsed.metadata.entity_name == "Test Entity"
        assert result.parsed.metadata.report_title == "Test Report"

    def test_parsed_page_config(self, minimal_spec: dict) -> None:
        result = validate_spec(minimal_spec)
        assert result.parsed.page.size.value == "A4"
        assert result.parsed.page.orientation.value == "portrait"
        assert result.parsed.page.margins.left_cm == 1.5

    def test_load_fixture_from_file(self) -> None:
        spec = load_fixture("minimal_spec")
        result = validate_spec(spec)
        assert result.valid is True


# ── Missing required fields ──────────────────────────────────────────


class TestMissingFields:
    def test_missing_template(self) -> None:
        spec = {"version": "1.0", "metadata": {"entity_name": "X", "report_title": "Y"}, "blocks": []}
        result = validate_spec(spec)
        assert result.valid is False
        assert any("template" in e for e in result.errors)

    def test_missing_metadata(self) -> None:
        spec = {"version": "1.0", "template": "analytics_report_v1", "blocks": []}
        result = validate_spec(spec)
        assert result.valid is False

    def test_missing_entity_name_in_metadata(self) -> None:
        spec = {
            "version": "1.0",
            "template": "analytics_report_v1",
            "metadata": {"report_title": "Report"},
            "blocks": [],
        }
        result = validate_spec(spec)
        assert result.valid is False

    def test_empty_dict(self) -> None:
        result = validate_spec({})
        assert result.valid is False
        assert len(result.errors) >= 1

    def test_wrong_version_is_rejected(self) -> None:
        spec = {
            "version": "2.0",
            "template": "analytics_report_v1",
            "metadata": {"entity_name": "X", "report_title": "Y"},
            "blocks": [],
        }
        result = validate_spec(spec)
        assert result.valid is False

    def test_extra_top_level_field_is_rejected(self) -> None:
        spec = {
            "version": "1.0",
            "template": "analytics_report_v1",
            "metadata": {"entity_name": "X", "report_title": "Y"},
            "blocks": [],
            "unexpected": True,
        }
        result = validate_spec(spec)
        assert result.valid is False


# ── Block type validation ────────────────────────────────────────────


class TestBlockValidation:
    def test_unknown_block_type_causes_error(self) -> None:
        spec = {
            "version": "1.0",
            "template": "test",
            "metadata": {"entity_name": "X", "report_title": "Y"},
            "blocks": [{"type": "unknown_widget"}],
        }
        result = validate_spec(spec)
        assert result.valid is False

    def test_title_block(self) -> None:
        spec = {
            "version": "1.0",
            "template": "test",
            "metadata": {"entity_name": "X", "report_title": "Y"},
            "blocks": [{"type": "title", "title": "Hello"}],
        }
        result = validate_spec(spec)
        assert result.valid is True
        block = result.parsed.blocks[0]
        assert hasattr(block, "title")

    def test_all_block_types_parse(self) -> None:
        """Every supported block type must parse successfully."""
        blocks: list[dict] = [
            {"type": "title", "title": "t"},
            {"type": "section_header", "title": "s"},
            {"type": "paragraph", "text": "p"},
            {"type": "rich_text", "runs": [{"text": "r"}]},
            {"type": "kpi_grid", "items": [{"label": "L", "value": "V"}]},
            {"type": "callout", "text": "c"},
            {"type": "callout_group", "items": [{"text": "c"}]},
            {"type": "table", "columns": [{"key": "k", "label": "K"}], "rows": [{"k": "v"}]},
            {"type": "matrix_table", "columns": ["A"], "rows": [["B"]]},
            {"type": "insight_list", "items": [{"title": "I", "text": "t"}]},
            {"type": "recommendations", "items": [{"priority": "P", "action": "A"}]},
            {"type": "image", "src": "/tmp/test.png"},
            {"type": "chart", "chart_type": "bar"},
            {"type": "two_column"},
            {"type": "page_break"},
            {"type": "spacer"},
            {"type": "divider"},
            {"type": "badge", "label": "X"},
            {"type": "summary_box", "text": "s"},
        ]
        spec = {
            "version": "1.0",
            "template": "test",
            "metadata": {"entity_name": "X", "report_title": "Y"},
            "blocks": blocks,
        }
        result = validate_spec(spec)
        assert result.valid is True
        assert len(result.parsed.blocks) == 19


# ── Chart type validation ────────────────────────────────────────────


class TestChartValidation:
    def test_valid_chart_type(self) -> None:
        for chart_type in SUPPORTED_CHART_TYPES:
            spec = {
                "version": "1.0",
                "template": "test",
                "metadata": {"entity_name": "X", "report_title": "Y"},
                "blocks": [{"type": "chart", "chart_type": chart_type}],
            }
            result = validate_spec(spec)
            assert result.valid, f"chart_type {chart_type} should be valid"

    def test_image_src_must_not_be_empty(self) -> None:
        spec = {
            "version": "1.0",
            "template": "analytics_report_v1",
            "theme": "green",
            "metadata": {
                "entity_name": "Test Entity",
                "report_title": "Test Report",
            },
            "blocks": [{"type": "image", "src": ""}],
        }
        result = validate_spec(spec)
        assert not result.valid

    def test_unknown_chart_type_gives_warning(self) -> None:
        spec = {
            "version": "1.0",
            "template": "test",
            "metadata": {"entity_name": "X", "report_title": "Y"},
            "blocks": [{"type": "chart", "chart_type": "treemap"}],
        }
        result = validate_spec(spec)
        assert result.valid is True
        assert any("treemap" in w for w in result.warnings)


# ── Table validation ─────────────────────────────────────────────────


class TestTableValidation:
    def test_column_width_warning(self) -> None:
        spec = {
            "version": "1.0",
            "template": "test",
            "metadata": {"entity_name": "X", "report_title": "Y"},
            "blocks": [{
                "type": "table",
                "columns": [
                    {"key": "a", "label": "A", "width": 0.8},
                    {"key": "b", "label": "B", "width": 0.8},
                ],
                "rows": [],
            }],
        }
        result = validate_spec(spec)
        assert result.valid is True
        assert any("widths sum" in w for w in result.warnings)

    def test_extra_row_key_warning(self) -> None:
        spec = {
            "version": "1.0",
            "template": "test",
            "metadata": {"entity_name": "X", "report_title": "Y"},
            "blocks": [{
                "type": "table",
                "columns": [{"key": "a", "label": "A"}],
                "rows": [{"a": "1", "extra": "2"}],
            }],
        }
        result = validate_spec(spec)
        assert result.valid is True
        assert any("extra keys" in w for w in result.warnings)

    def test_matching_row_keys_no_warning(self) -> None:
        spec = {
            "version": "1.0",
            "template": "test",
            "metadata": {"entity_name": "X", "report_title": "Y"},
            "blocks": [{
                "type": "table",
                "columns": [
                    {"key": "a", "label": "A", "width": 0.5},
                    {"key": "b", "label": "B", "width": 0.5},
                ],
                "rows": [{"a": "1", "b": "2"}],
            }],
        }
        result = validate_spec(spec)
        assert result.valid is True
        assert result.warnings == []


# ── Two-column validation ────────────────────────────────────────────


class TestTwoColumnValidation:
    def test_widths_not_summing_to_one_gives_warning(self) -> None:
        spec = {
            "version": "1.0",
            "template": "test",
            "metadata": {"entity_name": "X", "report_title": "Y"},
            "blocks": [{"type": "two_column", "left_width": 0.3, "right_width": 0.3}],
        }
        result = validate_spec(spec)
        assert result.valid is True
        assert any("two_column" in w for w in result.warnings)


# ── validate_spec_or_raise ───────────────────────────────────────────


class TestValidateOrRaise:
    def test_valid_returns_spec(self, minimal_spec: dict) -> None:
        spec = validate_spec_or_raise(minimal_spec)
        assert isinstance(spec, ReportSpec)

    def test_invalid_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError, match="validation failed"):
            validate_spec_or_raise({})


# ── ValidationResult ─────────────────────────────────────────────────


class TestValidationResult:
    def test_to_dict_valid(self, minimal_spec: dict) -> None:
        result = validate_spec(minimal_spec)
        d = result.to_dict()
        assert d["valid"] is True
        assert d["errors"] == []
        assert "metadata" in d

    def test_to_dict_invalid(self) -> None:
        result = validate_spec({})
        d = result.to_dict()
        assert d["valid"] is False
        assert len(d["errors"]) > 0
        assert "metadata" not in d


# ── JSON Schema generation ──────────────────────────────────────────


class TestSchemaGeneration:
    def test_generate_schema_json(self) -> None:
        schema = generate_schema_json()
        assert "properties" in schema
        assert "version" in schema["properties"]
        assert "blocks" in schema["properties"]

    def test_generate_schema_file(self, tmp_path: Path) -> None:
        p = generate_schema_file(tmp_path / "schema.json")
        assert p.exists()
        data = json.loads(p.read_text())
        assert "$schema" in data or "properties" in data
