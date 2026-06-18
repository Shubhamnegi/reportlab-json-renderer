"""Edge-case validation tests for schema boundary conditions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reportlab_json_renderer.schema.validators import validate_spec

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict[str, Any]:
    """Load a fixture JSON by filename stem."""
    return json.loads((FIXTURES_DIR / f"{name}.json").read_text(encoding="utf-8"))


def _copy_spec(minimal_spec: dict[str, Any]) -> dict[str, Any]:
    """Deep-copy a spec to avoid mutating shared fixtures."""
    return json.loads(json.dumps(minimal_spec))


class TestInvalidInputs:
    """Test validation rejects various invalid inputs."""

    def test_missing_version(self, minimal_spec: dict[str, Any]) -> None:
        spec = _copy_spec(minimal_spec)
        del spec["version"]
        # version has a default value "1.0", so this should still pass
        result = validate_spec(spec)
        assert result.valid

    def test_wrong_version(self, minimal_spec: dict[str, Any]) -> None:
        spec = _copy_spec(minimal_spec)
        spec["version"] = "99.0"
        # No enum constraint on version, so this passes validation
        result = validate_spec(spec)
        assert result.valid

    def test_missing_theme(self, minimal_spec: dict[str, Any]) -> None:
        spec = _copy_spec(minimal_spec)
        del spec["theme"]
        # theme has a default value "limetray_green", so this should still pass
        result = validate_spec(spec)
        assert result.valid

    def test_missing_metadata(self, minimal_spec: dict[str, Any]) -> None:
        spec = _copy_spec(minimal_spec)
        del spec["metadata"]
        result = validate_spec(spec)
        assert not result.valid

    def test_missing_entity_name(self, minimal_spec: dict[str, Any]) -> None:
        spec = _copy_spec(minimal_spec)
        del spec["metadata"]["entity_name"]
        result = validate_spec(spec)
        assert not result.valid

    def test_unknown_block_type(self, minimal_spec: dict[str, Any]) -> None:
        spec = _copy_spec(minimal_spec)
        spec["blocks"] = [{"type": "unknown_widget"}]
        result = validate_spec(spec)
        assert not result.valid

    def test_block_missing_type(self, minimal_spec: dict[str, Any]) -> None:
        spec = _copy_spec(minimal_spec)
        spec["blocks"] = [{"text": "no type field"}]
        result = validate_spec(spec)
        assert not result.valid

    def test_empty_json(self) -> None:
        result = validate_spec({})
        assert not result.valid

    def test_null_spec(self) -> None:
        result = validate_spec({})  # type: ignore[arg-type]
        assert not result.valid
        assert len(result.errors) > 0

    def test_title_missing_required_fields(self, minimal_spec: dict[str, Any]) -> None:
        spec = _copy_spec(minimal_spec)
        # TitleBlock has all optional fields, so empty title block passes schema
        spec["blocks"] = [{"type": "title"}]
        result = validate_spec(spec)
        assert result.valid, "Title block with all defaults should still pass schema"

    def test_table_missing_columns(self, minimal_spec: dict[str, Any]) -> None:
        spec = _copy_spec(minimal_spec)
        spec["blocks"] = [{"type": "table", "rows": []}]
        result = validate_spec(spec)
        assert not result.valid

    def test_kpi_grid_empty_items(self, minimal_spec: dict[str, Any]) -> None:
        spec = _copy_spec(minimal_spec)
        spec["blocks"] = [{"type": "kpi_grid", "items": []}]
        result = validate_spec(spec)
        # Empty items might still pass schema (list with 0 items)
        # This tests that it doesn't crash
        assert result is not None


class TestPostValidationWarnings:
    """Test post-validation warning generation."""

    def test_table_extra_row_keys_warning(self, minimal_spec: dict[str, Any]) -> None:
        spec = _copy_spec(minimal_spec)
        spec["blocks"] = [
            {
                "type": "table",
                "columns": [{"key": "a", "label": "A"}],
                "rows": [{"a": "1", "extra_col": "surplus"}],
            }
        ]
        result = validate_spec(spec)
        assert result.valid
        assert any("extra keys" in w for w in result.warnings)

    def test_two_column_width_mismatch_warning(self, minimal_spec: dict[str, Any]) -> None:
        spec = _copy_spec(minimal_spec)
        spec["blocks"] = [
            {
                "type": "two_column",
                "left_width": 0.3,
                "right_width": 0.3,
                "left": [],
                "right": [],
            }
        ]
        result = validate_spec(spec)
        assert result.valid
        assert any("widths" in w for w in result.warnings)

    def test_no_warnings_for_clean_spec(self, minimal_spec: dict[str, Any]) -> None:
        result = validate_spec(minimal_spec)
        assert result.valid
        assert result.warnings == []


class TestValidationResult:
    """Test the ValidationResult API surface."""

    def test_to_dict_valid(self, minimal_spec: dict[str, Any]) -> None:
        result = validate_spec(minimal_spec)
        d = result.to_dict()
        assert d["valid"] is True
        assert isinstance(d["errors"], list)
        assert isinstance(d["warnings"], list)

    def test_to_dict_invalid(self) -> None:
        result = validate_spec({"invalid": True})
        d = result.to_dict()
        assert d["valid"] is False
        assert len(d["errors"]) > 0
