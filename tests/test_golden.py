"""Golden PDF / snapshot metadata tests.

These tests verify that each template produces a valid PDF with the
expected structural properties (page count, file size, success status).
They also exercise edge-case fixtures (empty blocks, minimal fields,
all block types, page size overrides).
"""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest
from pypdf import PdfReader

from reportlab_json_renderer.renderer import build_pdf
from reportlab_json_renderer.schema.validators import validate_spec

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict[str, Any]:
    """Load a fixture JSON by filename stem."""
    return json.loads((FIXTURES_DIR / f"{name}.json").read_text(encoding="utf-8"))


# ── Template golden tests ────────────────────────────────────────────────


@pytest.mark.parametrize(
    "fixture,min_pages,min_bytes",
    [
        ("minimal_spec", 0, 500),
        ("full_spec", 1, 2_000),
        ("business_report_spec", 1, 1_000),
        ("compact_report_spec", 1, 1_000),
        ("invoice_spec", 1, 1_000),
        ("proposal_spec", 2, 2_000),
    ],
    ids=[
        "minimal",
        "full-analytics",
        "business-report",
        "compact-report",
        "invoice",
        "proposal",
    ],
)
class TestTemplateGolden:
    """Verify each template produces a valid, non-trivial PDF."""

    def test_renders_successfully(
        self, tmp_path: Path, fixture: str, min_pages: int, min_bytes: int
    ) -> None:
        """PDF renders without errors and meets size/page minimums."""
        spec = _load(fixture)
        out = tmp_path / f"{fixture}.pdf"

        result = build_pdf(spec, output_path=str(out))

        assert result["success"] is True
        assert out.exists()
        assert out.stat().st_size >= min_bytes, (
            f"{fixture}: {out.stat().st_size} bytes < {min_bytes} minimum"
        )
        assert result["pages"] >= min_pages, (
            f"{fixture}: {result['pages']} pages < {min_pages} minimum"
        )

    def test_result_metadata(
        self, tmp_path: Path, fixture: str, min_pages: int, min_bytes: int
    ) -> None:
        """Result dict contains expected keys and metadata."""
        spec = _load(fixture)
        out = tmp_path / f"{fixture}.pdf"

        result = build_pdf(spec, output_path=str(out))

        assert "success" in result
        assert "path" in result
        assert "pages" in result
        assert "warnings" in result
        assert "metadata" in result
        assert result["metadata"]["template"] == spec["template"]
        assert result["metadata"]["theme"] == spec["theme"]

    def test_passes_validation(self, fixture: str, min_pages: int, min_bytes: int) -> None:
        """Each fixture spec passes schema validation."""
        spec = _load(fixture)
        result = validate_spec(spec)
        assert result.valid, f"{fixture} failed validation: {result.errors}"


# ── Edge-case tests ──────────────────────────────────────────────────────


class TestEdgeCases:
    """Edge-case fixture rendering tests."""

    def test_empty_blocks(self, tmp_path: Path) -> None:
        """A spec with zero blocks renders as a single-page valid PDF."""
        spec = _load("edge_empty_blocks")
        out = tmp_path / "empty.pdf"

        result = build_pdf(spec, output_path=str(out))

        assert result["success"] is True
        assert result["pages"] == 1
        assert out.exists()
        assert out.stat().st_size > 0

    def test_minimal_fields(self, tmp_path: Path) -> None:
        """A spec with minimal optional fields renders successfully."""
        spec = _load("edge_minimal_fields")
        out = tmp_path / "minimal.pdf"

        result = build_pdf(spec, output_path=str(out))

        assert result["success"] is True
        assert out.exists()

    def test_all_block_types(self, tmp_path: Path) -> None:
        """A spec exercising every block type renders successfully."""
        spec = _load("edge_all_block_types")
        out = tmp_path / "all_blocks.pdf"

        result = build_pdf(spec, output_path=str(out))

        assert result["success"] is True
        assert out.exists()
        assert out.stat().st_size > 3_000, "All-blocks PDF should be substantial"
        assert result["pages"] >= 2, "All-blocks PDF has a page_break, expect >= 2 pages"

    def test_page_size_letter_landscape(self, tmp_path: Path) -> None:
        """Letter landscape page size renders correctly."""
        spec = _load("edge_page_sizes")
        out = tmp_path / "letter.pdf"

        result = build_pdf(spec, output_path=str(out))

        assert result["success"] is True
        assert out.exists()

    def test_all_fixtures_pass_validation(self) -> None:
        """Every fixture file passes schema validation."""
        fixture_files = sorted(FIXTURES_DIR.glob("*.json"))
        assert len(fixture_files) >= 6, "Expected at least 6 fixture files"

        failures: list[str] = []
        for path in fixture_files:
            spec = json.loads(path.read_text(encoding="utf-8"))
            result = validate_spec(spec)
            if not result.valid:
                failures.append(f"{path.name}: {result.errors}")

        assert not failures, "Validation failures:\n" + "\n".join(failures)


# ── PDF bytes-only rendering ─────────────────────────────────────────────


class TestBytesOnlyRendering:
    """Test rendering without writing to disk."""

    def test_bytes_only_returns_pdf(self, minimal_spec: dict[str, Any]) -> None:
        """Rendering without output_path returns bytes in result."""
        result = build_pdf(minimal_spec)

        assert result["success"] is True
        assert result["bytes"] is not None
        assert len(result["bytes"]) > 0
        assert result["bytes"][:4] == b"%PDF", "Should start with PDF magic bytes"
        assert result["path"] is None

    def test_bytes_match_file(self, tmp_path: Path, minimal_spec: dict[str, Any]) -> None:
        """Bytes-only output matches file output."""
        out = tmp_path / "test.pdf"

        result_file = build_pdf(minimal_spec, output_path=str(out))
        result_bytes = build_pdf(minimal_spec)

        # Both should succeed and produce similar sizes
        assert result_file["success"] is True
        assert result_bytes["success"] is True
        assert result_file["pages"] == result_bytes["pages"]
        # Size may differ slightly due to metadata, but should be in the same ballpark
        file_size = out.stat().st_size
        bytes_size = len(result_bytes["bytes"])
        assert abs(file_size - bytes_size) < file_size * 0.1, (
            f"File ({file_size}) and bytes ({bytes_size}) sizes differ significantly"
        )


# ── Parsed PDF verification ──────────────────────────────────────────────


class TestParsedPdfVerification:
    """Verify generated PDFs are structurally readable and contain expected text."""

    def test_reader_page_count_matches_result(self, minimal_spec: dict[str, Any]) -> None:
        result = build_pdf(minimal_spec)
        reader = PdfReader(BytesIO(result["bytes"]))

        assert len(reader.pages) == result["pages"]

    def test_extracted_text_contains_core_fields(self) -> None:
        spec = {
            "version": "1.0",
            "template": "analytics_report_v1",
            "theme": "green",
            "metadata": {
                "entity_name": "Test Entity",
                "report_title": "Test Report",
                "period": "1 Jun - 7 Jun 2026",
                "powered_by": "Public PDF Renderer",
            },
            "blocks": [
                {
                    "type": "title",
                    "entity": "Test Entity",
                    "title": "Test Report",
                    "subtitle": "1 Jun - 7 Jun 2026",
                },
                {"type": "paragraph", "text": "Hello world"},
            ],
        }

        result = build_pdf(spec)
        reader = PdfReader(BytesIO(result["bytes"]))
        extracted = "\n".join(page.extract_text() or "" for page in reader.pages)

        assert "Test Entity" in extracted
        assert "Test Report" in extracted
        assert "Hello world" in extracted


# ── Theme coverage ───────────────────────────────────────────────────────


class TestThemeCoverage:
    """Verify all built-in themes render without errors."""

    @pytest.mark.parametrize("theme", ["green", "neutral", "dark"])
    def test_theme_renders(self, tmp_path: Path, theme: str, minimal_spec: dict[str, Any]) -> None:
        """Each built-in theme produces a valid PDF."""
        spec = {**minimal_spec, "theme": theme}
        out = tmp_path / f"{theme}.pdf"

        result = build_pdf(spec, output_path=str(out))

        assert result["success"] is True
        assert result["metadata"]["theme"] == theme


# ── Idempotency ──────────────────────────────────────────────────────────


class TestIdempotency:
    """Rendering the same spec twice should produce equivalent results."""

    def test_same_bytes(self, minimal_spec: dict[str, Any]) -> None:
        """Two renders of the same spec produce identical PDF bytes."""
        r1 = build_pdf(minimal_spec)
        r2 = build_pdf(minimal_spec)

        assert r1["success"] == r2["success"]
        assert r1["pages"] == r2["pages"]
        assert r1["bytes"] == r2["bytes"]
