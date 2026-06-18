"""Shared fixtures for reportlab-json-renderer tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture()
def fixtures_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture()
def minimal_spec() -> dict[str, Any]:
    """Return the smallest valid report specification.

    This is the canonical "hello world" spec that exercises the root
    schema contract: version, template, theme, metadata, page, and an
    empty block list. Rendering it should still produce a single-page PDF.
    """
    return {
        "version": "1.0",
        "template": "analytics_report_v1",
        "theme": "green",
        "metadata": {
            "entity_name": "Test Entity",
            "report_title": "Test Report",
            "period": "1 Jan – 7 Jan 2026",
            "generated_at": "2026-01-07",
            "powered_by": "Public PDF Renderer",
            "confidential": True,
        },
        "page": {
            "size": "A4",
            "orientation": "portrait",
            "margins": {
                "left_cm": 1.5,
                "right_cm": 1.5,
                "top_cm": 2.2,
                "bottom_cm": 2.0,
            },
        },
        "header": {"enabled": True, "variant": "default"},
        "footer": {"enabled": True, "show_page_number": True},
        "blocks": [],
    }


@pytest.fixture()
def sample_spec(minimal_spec: dict[str, Any]) -> dict[str, Any]:
    """Return a spec with a few representative blocks for integration tests."""
    spec = {**minimal_spec, "blocks": [
        {"type": "title", "entity": "Demo Store", "title": "Weekly Report", "subtitle": "11 Jun – 17 Jun 2026"},
        {"type": "section_header", "number": "1", "title": "Brand KPI Summary"},
        {"type": "paragraph", "text": "Revenue declined by 12.3% week over week.", "style": "body"},
    ]}
    return spec


def load_fixture(name: str) -> dict[str, Any]:
    """Load a JSON fixture file by name (without extension).

    Args:
        name: Fixture filename stem, e.g. ``"minimal_spec"``.

    Returns:
        Parsed JSON content as a Python dict.

    Raises:
        FileNotFoundError: If the fixture file does not exist.
    """
    path = FIXTURES_DIR / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))
