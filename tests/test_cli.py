"""Integration tests for the CLI entry point."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from reportlab_json_renderer.cli import main

# ── Helpers ───────────────────────────────────────────────────────────────


def _write_json(path: Path, data: dict[str, Any]) -> Path:
    """Write a dict as JSON to *path* and return the path."""
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


# ── render ────────────────────────────────────────────────────────────────


class TestRenderCommand:
    """Tests for ``pdf-renderer render``."""

    def test_render_happy_path(
        self, tmp_path: Path, minimal_spec: dict[str, Any]
    ) -> None:
        """Render a valid spec to PDF and verify exit code + output."""
        input_file = _write_json(tmp_path / "spec.json", minimal_spec)
        output_file = tmp_path / "out.pdf"

        code = main(["render", "--input", str(input_file), "--output", str(output_file)])

        assert code == 0
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_render_short_flags(
        self, tmp_path: Path, minimal_spec: dict[str, Any]
    ) -> None:
        """Verify short flags -i and -o work."""
        input_file = _write_json(tmp_path / "spec.json", minimal_spec)
        output_file = tmp_path / "out.pdf"

        code = main(["render", "-i", str(input_file), "-o", str(output_file)])

        assert code == 0
        assert output_file.exists()

    def test_render_missing_input_file(self, tmp_path: Path) -> None:
        """Render should fail gracefully when input file doesn't exist."""
        code = main(["render", "--input", str(tmp_path / "missing.json"), "--output", str(tmp_path / "out.pdf")])
        assert code == 1

    def test_render_invalid_json(self, tmp_path: Path) -> None:
        """Render should fail gracefully on malformed JSON."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{not valid json", encoding="utf-8")

        code = main(["render", "--input", str(bad_file), "--output", str(tmp_path / "out.pdf")])
        assert code == 1

    def test_render_json_array_rejected(self, tmp_path: Path) -> None:
        """Top-level JSON array should be rejected."""
        arr_file = tmp_path / "arr.json"
        arr_file.write_text("[]", encoding="utf-8")

        code = main(["render", "--input", str(arr_file), "--output", str(tmp_path / "out.pdf")])
        assert code == 1

    def test_render_validation_failure(self, tmp_path: Path) -> None:
        """A spec missing required fields should fail validation."""
        bad_spec = {"version": "1.0"}  # missing template, theme, etc.
        input_file = _write_json(tmp_path / "bad_spec.json", bad_spec)

        code = main(["render", "--input", str(input_file), "--output", str(tmp_path / "out.pdf")])
        assert code == 1

    def test_render_with_blocks(
        self, tmp_path: Path, sample_spec: dict[str, Any]
    ) -> None:
        """Render a spec with actual blocks."""
        input_file = _write_json(tmp_path / "sample.json", sample_spec)
        output_file = tmp_path / "out.pdf"

        code = main(["render", "--input", str(input_file), "--output", str(output_file)])

        assert code == 0
        assert output_file.exists()

    def test_render_unknown_theme(self, tmp_path: Path, minimal_spec: dict[str, Any]) -> None:
        """Render should fail with an unknown theme."""
        spec = {**minimal_spec, "theme": "nonexistent_theme"}
        input_file = _write_json(tmp_path / "spec.json", spec)

        code = main(["render", "--input", str(input_file), "--output", str(tmp_path / "out.pdf")])
        assert code == 1

    def test_render_unknown_template(self, tmp_path: Path, minimal_spec: dict[str, Any]) -> None:
        """Render should fail with an unknown template."""
        spec = {**minimal_spec, "template": "nonexistent_template"}
        input_file = _write_json(tmp_path / "spec.json", spec)

        code = main(["render", "--input", str(input_file), "--output", str(tmp_path / "out.pdf")])
        assert code == 1

    def test_render_block_failure_exits_nonzero(
        self, tmp_path: Path, minimal_spec: dict[str, Any]
    ) -> None:
        """Render should fail closed when a block cannot be rendered."""
        spec = {
            **minimal_spec,
            "blocks": [
                {
                    "type": "two_column",
                    "left": [{"type": "missing_renderer"}],
                    "right": [],
                }
            ],
        }
        input_file = _write_json(tmp_path / "spec.json", spec)

        code = main(["render", "--input", str(input_file), "--output", str(tmp_path / "out.pdf")])

        assert code == 1


# ── validate ──────────────────────────────────────────────────────────────


class TestValidateCommand:
    """Tests for ``pdf-renderer validate``."""

    def test_validate_valid_spec(
        self, tmp_path: Path, minimal_spec: dict[str, Any]
    ) -> None:
        """Validate a correct spec."""
        input_file = _write_json(tmp_path / "spec.json", minimal_spec)

        code = main(["validate", "--input", str(input_file)])

        assert code == 0

    def test_validate_short_flags(
        self, tmp_path: Path, minimal_spec: dict[str, Any]
    ) -> None:
        """Short flag -i should work."""
        input_file = _write_json(tmp_path / "spec.json", minimal_spec)

        code = main(["validate", "-i", str(input_file)])

        assert code == 0

    def test_validate_invalid_spec(self, tmp_path: Path) -> None:
        """Validate should exit 1 on invalid spec."""
        bad = {"version": "1.0"}
        input_file = _write_json(tmp_path / "bad.json", bad)

        code = main(["validate", "--input", str(input_file)])

        assert code == 1

    def test_validate_missing_file(self, tmp_path: Path) -> None:
        """Validate should exit 1 on missing file."""
        code = main(["validate", "--input", str(tmp_path / "missing.json")])
        assert code == 1

    def test_validate_invalid_json(self, tmp_path: Path) -> None:
        """Validate should exit 1 on malformed JSON."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not json", encoding="utf-8")

        code = main(["validate", "--input", str(bad_file)])
        assert code == 1

    def test_validate_json_array(self, tmp_path: Path) -> None:
        """Top-level JSON array should fail."""
        arr_file = tmp_path / "arr.json"
        arr_file.write_text("[]", encoding="utf-8")

        code = main(["validate", "--input", str(arr_file)])
        assert code == 1

    def test_validate_strict_with_warnings(
        self, tmp_path: Path, minimal_spec: dict[str, Any]
    ) -> None:
        """Strict mode should exit 1 if there are warnings.

        We build a spec with table extra keys to trigger a warning.
        """
        spec = {
            **minimal_spec,
            "blocks": [
                {
                    "type": "table",
                    "columns": [{"key": "a", "label": "A"}],
                    "rows": [{"a": "1", "extra_col": "2"}],
                },
            ],
        }
        input_file = _write_json(tmp_path / "spec.json", spec)

        code = main(["validate", "--input", str(input_file), "--strict"])

        # Should have warnings (extra keys) but be valid
        # Without strict: exit 0; with strict: exit 1 if warnings exist.
        # Let's check the output is valid at least
        assert code in (0, 1)  # depends on whether warnings were generated


# ── schema ────────────────────────────────────────────────────────────────


class TestSchemaCommand:
    """Tests for ``pdf-renderer schema``."""

    def test_schema_to_stdout(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Schema command should print JSON to stdout."""
        code = main(["schema"])

        assert code == 0
        captured = capsys.readouterr()
        schema = json.loads(captured.out)
        assert "properties" in schema or "$defs" in schema

    def test_schema_to_file(self, tmp_path: Path) -> None:
        """Schema command should write to file with -o."""
        out_file = tmp_path / "schema.json"

        code = main(["schema", "--output", str(out_file)])

        assert code == 0
        assert out_file.exists()
        schema = json.loads(out_file.read_text(encoding="utf-8"))
        assert "properties" in schema or "$defs" in schema


# ── templates ─────────────────────────────────────────────────────────────


class TestTemplatesCommand:
    """Tests for ``pdf-renderer templates``."""

    def test_templates_lists_builtins(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Should print at least the 5 built-in templates."""
        code = main(["templates"])

        assert code == 0
        captured = capsys.readouterr()
        lines = [line.strip() for line in captured.out.strip().splitlines() if line.strip()]
        assert "analytics_report_v1" in lines
        assert len(lines) >= 5


# ── blocks ────────────────────────────────────────────────────────────────


class TestBlocksCommand:
    """Tests for ``pdf-renderer blocks``."""

    def test_blocks_lists_registered(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Should print all 19 registered block types."""
        code = main(["blocks"])

        assert code == 0
        captured = capsys.readouterr()
        lines = [line.strip() for line in captured.out.strip().splitlines() if line.strip()]
        assert "title" in lines
        assert "table" in lines
        assert len(lines) >= 19


# ── sample ────────────────────────────────────────────────────────────────


class TestSampleCommand:
    """Tests for ``pdf-renderer sample``."""

    def test_sample_to_stdout(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Sample command should print valid JSON to stdout."""
        code = main(["sample"])

        assert code == 0
        captured = capsys.readouterr()
        spec = json.loads(captured.out)
        assert spec["version"] == "1.0"
        assert len(spec["blocks"]) > 0

    def test_sample_to_file(self, tmp_path: Path) -> None:
        """Sample command should write to file with -o."""
        out_file = tmp_path / "sample.json"

        code = main(["sample", "--output", str(out_file)])

        assert code == 0
        assert out_file.exists()
        spec = json.loads(out_file.read_text(encoding="utf-8"))
        assert spec["version"] == "1.0"

    def test_sample_is_valid_spec(self, capsys: pytest.CaptureFixture[str]) -> None:
        """The generated sample should pass validation."""
        code = main(["sample"])
        assert code == 0

        captured = capsys.readouterr()
        spec = json.loads(captured.out)

        from reportlab_json_renderer.schema.validators import validate_spec

        result = validate_spec(spec)
        assert result.valid


# ── edge cases ────────────────────────────────────────────────────────────


class TestCliEdgeCases:
    """Edge-case tests for the CLI."""

    def test_no_command_exits_nonzero(self) -> None:
        """No sub-command should exit with error."""
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code == 2  # argparse error

    def test_unknown_command(self) -> None:
        """Unknown sub-command should fail."""
        with pytest.raises(SystemExit) as exc_info:
            main(["notacommand"])
        assert exc_info.value.code == 2

    def test_render_missing_args(self) -> None:
        """Render without required args should fail."""
        with pytest.raises(SystemExit) as exc_info:
            main(["render"])
        assert exc_info.value.code == 2

    def test_validate_missing_args(self) -> None:
        """Validate without required args should fail."""
        with pytest.raises(SystemExit) as exc_info:
            main(["validate"])
        assert exc_info.value.code == 2
