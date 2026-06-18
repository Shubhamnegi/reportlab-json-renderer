"""Tests for utils/charts.py."""

from __future__ import annotations

import io

import pytest

from reportlab_json_renderer.utils.charts import (
    render_area,
    render_bar,
    render_chart,
    render_donut,
    render_grouped_bar,
    render_horizontal_bar,
    render_line,
    render_pie,
    render_stacked_bar,
)
from reportlab_json_renderer.utils.errors import RenderError

LABELS = ["Alpha", "Beta", "Gamma", "Delta"]
VALUES = [120, 85, 200, 55]
SERIES = {
    "Series A": [10, 20, 30, 40],
    "Series B": [15, 25, 35, 45],
    "Series C": [5, 15, 25, 35],
}


def _assert_valid_png(buf: io.BytesIO) -> None:
    """Check that the buffer contains a valid PNG image."""
    assert buf.tell() == 0 or buf.seek(0) == 0
    header = buf.read(8)
    # PNG magic bytes
    assert header[:4] == b"\x89PNG", f"Not a PNG: {header!r}"
    buf.seek(0)


class TestRenderBar:
    def test_returns_png(self) -> None:
        buf = render_bar(LABELS, VALUES)
        _assert_valid_png(buf)

    def test_with_title(self) -> None:
        buf = render_bar(LABELS, VALUES, title="Test Bar Chart")
        _assert_valid_png(buf)

    def test_with_tone(self) -> None:
        buf = render_bar(LABELS, VALUES, tone="danger")
        _assert_valid_png(buf)

    def test_empty_data(self) -> None:
        buf = render_bar([], [])
        _assert_valid_png(buf)


class TestRenderHorizontalBar:
    def test_returns_png(self) -> None:
        buf = render_horizontal_bar(LABELS, VALUES)
        _assert_valid_png(buf)

    def test_with_title_and_tone(self) -> None:
        buf = render_horizontal_bar(LABELS, VALUES, title="H-Bar", tone="info")
        _assert_valid_png(buf)


class TestRenderLine:
    def test_returns_png(self) -> None:
        buf = render_line(LABELS, VALUES)
        _assert_valid_png(buf)


class TestRenderArea:
    def test_returns_png(self) -> None:
        buf = render_area(LABELS, VALUES)
        _assert_valid_png(buf)


class TestRenderPie:
    def test_returns_png(self) -> None:
        buf = render_pie(LABELS, VALUES)
        _assert_valid_png(buf)


class TestRenderDonut:
    def test_returns_png(self) -> None:
        buf = render_donut(LABELS, VALUES)
        _assert_valid_png(buf)


class TestRenderStackedBar:
    def test_returns_png(self) -> None:
        buf = render_stacked_bar(LABELS, SERIES)
        _assert_valid_png(buf)


class TestRenderGroupedBar:
    def test_returns_png(self) -> None:
        buf = render_grouped_bar(LABELS, SERIES)
        _assert_valid_png(buf)


class TestRenderChart:
    """Tests for the dispatcher function."""

    @pytest.mark.parametrize("chart_type", [
        "bar", "horizontal_bar", "line", "area", "pie", "donut",
    ])
    def test_single_series_types(self, chart_type: str) -> None:
        buf = render_chart(chart_type, labels=LABELS, values=VALUES, title=f"Test {chart_type}")
        _assert_valid_png(buf)

    @pytest.mark.parametrize("chart_type", ["stacked_bar", "grouped_bar"])
    def test_multi_series_types(self, chart_type: str) -> None:
        buf = render_chart(chart_type, labels=LABELS, series=SERIES, title=f"Test {chart_type}")
        _assert_valid_png(buf)

    def test_unknown_type_raises(self) -> None:
        with pytest.raises(RenderError, match="Unknown chart type"):
            render_chart("treemap", labels=LABELS, values=VALUES)


class TestFormatIndianCurrency:
    """Tests for the Indian number formatting helper."""

    def test_small_number(self) -> None:
        from reportlab_json_renderer.utils.charts import _format_indian_currency

        assert _format_indian_currency(123) == "123"

    def test_thousands(self) -> None:
        from reportlab_json_renderer.utils.charts import _format_indian_currency

        assert _format_indian_currency(3743) == "3,743"

    def test_lakhs(self) -> None:
        from reportlab_json_renderer.utils.charts import _format_indian_currency

        assert _format_indian_currency(1962261) == "19,62,261"

    def test_crores(self) -> None:
        from reportlab_json_renderer.utils.charts import _format_indian_currency

        assert _format_indian_currency(123456789) == "12,34,56,789"

    def test_negative(self) -> None:
        from reportlab_json_renderer.utils.charts import _format_indian_currency

        assert _format_indian_currency(-1962261) == "-19,62,261"

    def test_zero(self) -> None:
        from reportlab_json_renderer.utils.charts import _format_indian_currency

        assert _format_indian_currency(0) == "0"


class TestPickColours:
    """Tests for the colour picker helper."""

    def test_fallback_palette(self) -> None:
        from reportlab_json_renderer.utils.charts import _pick_colours

        colours = _pick_colours(3)
        assert len(colours) == 3
        for c in colours:
            assert c.startswith("#")

    def test_with_tone(self) -> None:
        from reportlab_json_renderer.utils.charts import _pick_colours

        colours = _pick_colours(2, tone="primary")
        assert len(colours) == 2

    def test_with_unknown_tone_falls_back(self) -> None:
        from reportlab_json_renderer.utils.charts import _pick_colours

        colours = _pick_colours(2, tone="nonexistent")
        assert len(colours) == 2
