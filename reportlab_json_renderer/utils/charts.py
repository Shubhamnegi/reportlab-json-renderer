"""Matplotlib-based chart renderers.

Each renderer accepts chart data from the JSON spec and returns a PNG
``BytesIO`` buffer that can be embedded as a ReportLab ``Image`` flowable.

Supported chart types (v1):
  bar, horizontal_bar, line, area, pie, donut, stacked_bar, grouped_bar
"""

from __future__ import annotations

import io
from typing import Any

import matplotlib
import numpy as np
from matplotlib import pyplot as plt

from reportlab_json_renderer.utils.errors import RenderError

# Non-interactive backend — safe for servers.
matplotlib.use("Agg")

# Default figure size in inches (≈ 16 cm wide, 8 cm tall).
_DEFAULT_FIGSIZE: tuple[float, float] = (6.3, 3.15)
_DEFAULT_DPI: int = 150

# Fallback palette when no theme colours are supplied.
_FALLBACK_COLOURS: list[str] = [
    "#7CB518",
    "#1565C0",
    "#E65100",
    "#C62828",
    "#2E7D32",
    "#555555",
    "#9C27B0",
    "#00838F",
]


def _apply_default_style(ax: plt.Axes, title: str | None = None) -> None:
    """Apply consistent styling to an axes object.

    Args:
        ax: Matplotlib axes.
        title: Optional chart title.
    """
    if title:
        ax.set_title(title, fontsize=11, fontweight="bold", pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=9)


def _fig_to_png_buffer(fig: plt.Figure) -> io.BytesIO:
    """Render a matplotlib figure to a PNG ``BytesIO`` buffer.

    Args:
        fig: The figure to render.

    Returns:
        In-memory PNG image buffer.
    """
    buf = io.BytesIO()
    fig.savefig(
        buf,
        format="png",
        dpi=_DEFAULT_DPI,
        bbox_inches="tight",
        facecolor="white",
        edgecolor="none",
    )
    plt.close(fig)
    buf.seek(0)
    return buf


def _pick_colours(
    count: int, tone: str | None = None, theme_palette: dict[str, str] | None = None
) -> list[str]:
    """Pick *count* colours from the theme palette or fallback.

    Args:
        count: Number of colours needed.
        tone: Optional tone to use as the primary colour.
        theme_palette: Optional theme colour palette.

    Returns:
        List of hex colour strings.
    """
    from reportlab_json_renderer.utils.colors import resolve_tone

    if tone:
        try:
            primary = resolve_tone(tone, theme_palette)
            # Generate a gradient from primary to a lighter shade.
            return [primary, *_FALLBACK_COLOURS[: count - 1]]
        except Exception:
            pass

    return [_FALLBACK_COLOURS[i % len(_FALLBACK_COLOURS)] for i in range(count)]


def _format_indian_currency(value: float) -> str:
    """Format a number in Indian comma grouping (lakhs/crores).

    Args:
        value: Numeric value.

    Returns:
        Formatted string, e.g. ``"19,62,261"``.
    """
    if value < 0:
        return "-" + _format_indian_currency(-value)
    s = str(int(value))
    if len(s) <= 3:
        return s
    last3 = s[-3:]
    rest = s[:-3]
    parts = []
    while rest:
        parts.append(rest[-2:])
        rest = rest[:-2]
    parts.reverse()
    return ",".join(parts) + "," + last3


# ── Chart renderers ──────────────────────────────────────────────────


def render_bar(
    labels: list[str],
    values: list[float],
    title: str | None = None,
    tone: str | None = None,
    theme_palette: dict[str, str] | None = None,
) -> io.BytesIO:
    """Render a vertical bar chart.

    Args:
        labels: Category labels.
        values: Numeric values per category.
        title: Optional chart title.
        tone: Optional colour tone.
        theme_palette: Optional theme palette.

    Returns:
        PNG ``BytesIO`` buffer.
    """
    fig, ax = plt.subplots(figsize=_DEFAULT_FIGSIZE)
    colours = _pick_colours(1, tone, theme_palette)
    ax.bar(labels, values, color=colours[0], edgecolor="white", linewidth=0.5)
    _apply_default_style(ax, title)
    ax.set_ylabel("")
    fig.tight_layout()
    return _fig_to_png_buffer(fig)


def render_horizontal_bar(
    labels: list[str],
    values: list[float],
    title: str | None = None,
    tone: str | None = None,
    theme_palette: dict[str, str] | None = None,
) -> io.BytesIO:
    """Render a horizontal bar chart.

    Args:
        labels: Category labels.
        values: Numeric values per category.
        title: Optional chart title.
        tone: Optional colour tone.
        theme_palette: Optional theme palette.

    Returns:
        PNG ``BytesIO`` buffer.
    """
    fig, ax = plt.subplots(figsize=_DEFAULT_FIGSIZE)
    colours = _pick_colours(1, tone, theme_palette)
    y_pos = np.arange(len(labels))
    ax.barh(y_pos, values, color=colours[0], edgecolor="white", linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    _apply_default_style(ax, title)
    fig.tight_layout()
    return _fig_to_png_buffer(fig)


def render_line(
    labels: list[str],
    values: list[float],
    title: str | None = None,
    tone: str | None = None,
    theme_palette: dict[str, str] | None = None,
) -> io.BytesIO:
    """Render a line chart.

    Args:
        labels: X-axis labels.
        values: Y-axis values.
        title: Optional chart title.
        tone: Optional colour tone.
        theme_palette: Optional theme palette.

    Returns:
        PNG ``BytesIO`` buffer.
    """
    fig, ax = plt.subplots(figsize=_DEFAULT_FIGSIZE)
    colours = _pick_colours(1, tone, theme_palette)
    ax.plot(labels, values, color=colours[0], linewidth=2, marker="o", markersize=5)
    ax.fill_between(range(len(labels)), values, alpha=0.08, color=colours[0])
    _apply_default_style(ax, title)
    fig.tight_layout()
    return _fig_to_png_buffer(fig)


def render_area(
    labels: list[str],
    values: list[float],
    title: str | None = None,
    tone: str | None = None,
    theme_palette: dict[str, str] | None = None,
) -> io.BytesIO:
    """Render an area chart (filled line chart).

    Args:
        labels: X-axis labels.
        values: Y-axis values.
        title: Optional chart title.
        tone: Optional colour tone.
        theme_palette: Optional theme palette.

    Returns:
        PNG ``BytesIO`` buffer.
    """
    fig, ax = plt.subplots(figsize=_DEFAULT_FIGSIZE)
    colours = _pick_colours(1, tone, theme_palette)
    ax.fill_between(range(len(labels)), values, alpha=0.35, color=colours[0])
    ax.plot(range(len(labels)), values, color=colours[0], linewidth=2)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    _apply_default_style(ax, title)
    fig.tight_layout()
    return _fig_to_png_buffer(fig)


def render_pie(
    labels: list[str],
    values: list[float],
    title: str | None = None,
    tone: str | None = None,
    theme_palette: dict[str, str] | None = None,
) -> io.BytesIO:
    """Render a pie chart.

    Args:
        labels: Slice labels.
        values: Slice values.
        title: Optional chart title.
        tone: Optional colour tone.
        theme_palette: Optional theme palette.

    Returns:
        PNG ``BytesIO`` buffer.
    """
    fig, ax = plt.subplots(figsize=_DEFAULT_FIGSIZE)
    colours = _pick_colours(len(values), tone, theme_palette)
    _wedges, _texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colours,
        autopct="%1.1f%%",
        startangle=90,
        textprops={"fontsize": 9},
    )
    for t in autotexts:
        t.set_fontsize(8)
    _apply_default_style(ax, title)
    fig.tight_layout()
    return _fig_to_png_buffer(fig)


def render_donut(
    labels: list[str],
    values: list[float],
    title: str | None = None,
    tone: str | None = None,
    theme_palette: dict[str, str] | None = None,
) -> io.BytesIO:
    """Render a donut chart (pie with a hollow centre).

    Args:
        labels: Segment labels.
        values: Segment values.
        title: Optional chart title.
        tone: Optional colour tone.
        theme_palette: Optional theme palette.

    Returns:
        PNG ``BytesIO`` buffer.
    """
    fig, ax = plt.subplots(figsize=_DEFAULT_FIGSIZE)
    colours = _pick_colours(len(values), tone, theme_palette)
    _wedges, _texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colours,
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.8,
        textprops={"fontsize": 9},
    )
    centre_circle = plt.Circle((0, 0), 0.55, fc="white")
    ax.add_artist(centre_circle)
    for t in autotexts:
        t.set_fontsize(8)
    _apply_default_style(ax, title)
    fig.tight_layout()
    return _fig_to_png_buffer(fig)


def render_stacked_bar(
    labels: list[str],
    series: dict[str, list[float]],
    title: str | None = None,
    tone: str | None = None,
    theme_palette: dict[str, str] | None = None,
) -> io.BytesIO:
    """Render a stacked bar chart.

    Args:
        labels: Category labels (x-axis).
        series: Mapping of series name → list of values (one per label).
        title: Optional chart title.
        tone: Optional colour tone.
        theme_palette: Optional theme palette.

    Returns:
        PNG ``BytesIO`` buffer.
    """
    fig, ax = plt.subplots(figsize=_DEFAULT_FIGSIZE)
    colours = _pick_colours(len(series), tone, theme_palette)
    x = np.arange(len(labels))
    width = 0.5
    bottom = np.zeros(len(labels))

    for idx, (name, vals) in enumerate(series.items()):
        ax.bar(
            x,
            vals,
            width,
            label=name,
            bottom=bottom,
            color=colours[idx],
            edgecolor="white",
            linewidth=0.5,
        )
        bottom += np.array(vals)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(fontsize=8)
    _apply_default_style(ax, title)
    fig.tight_layout()
    return _fig_to_png_buffer(fig)


def render_grouped_bar(
    labels: list[str],
    series: dict[str, list[float]],
    title: str | None = None,
    tone: str | None = None,
    theme_palette: dict[str, str] | None = None,
) -> io.BytesIO:
    """Render a grouped (side-by-side) bar chart.

    Args:
        labels: Category labels (x-axis).
        series: Mapping of series name → list of values (one per label).
        title: Optional chart title.
        tone: Optional colour tone.
        theme_palette: Optional theme palette.

    Returns:
        PNG ``BytesIO`` buffer.
    """
    fig, ax = plt.subplots(figsize=_DEFAULT_FIGSIZE)
    colours = _pick_colours(len(series), tone, theme_palette)
    x = np.arange(len(labels))
    n = len(series)
    width = 0.7 / n
    offsets = np.linspace(-(n - 1) * width / 2, (n - 1) * width / 2, n)

    for idx, (name, vals) in enumerate(series.items()):
        ax.bar(
            x + offsets[idx],
            vals,
            width,
            label=name,
            color=colours[idx],
            edgecolor="white",
            linewidth=0.5,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(fontsize=8)
    _apply_default_style(ax, title)
    fig.tight_layout()
    return _fig_to_png_buffer(fig)


# ── Dispatcher ───────────────────────────────────────────────────────

_CHART_RENDERERS: dict[str, Any] = {
    "bar": render_bar,
    "horizontal_bar": render_horizontal_bar,
    "line": render_line,
    "area": render_area,
    "pie": render_pie,
    "donut": render_donut,
    "stacked_bar": render_stacked_bar,
    "grouped_bar": render_grouped_bar,
}


def render_chart(
    chart_type: str,
    labels: list[str] | None = None,
    values: list[float] | None = None,
    series: dict[str, list[float]] | None = None,
    title: str | None = None,
    tone: str | None = None,
    theme_palette: dict[str, str] | None = None,
) -> io.BytesIO:
    """Dispatch to the correct chart renderer by *chart_type*.

    Args:
        chart_type: One of the supported chart type names.
        labels: Category/axis labels.
        values: Numeric values (for single-series charts).
        series: Multi-series data (for stacked/grouped charts).
        title: Optional chart title.
        tone: Optional colour tone.
        theme_palette: Optional theme palette.

    Returns:
        PNG ``BytesIO`` buffer.

    Raises:
        RenderError: If *chart_type* is unknown.
    """
    renderer = _CHART_RENDERERS.get(chart_type)
    if renderer is None:
        raise RenderError(
            f"Unknown chart type {chart_type!r}. "
            f"Supported: {', '.join(sorted(_CHART_RENDERERS))}"
        )

    if chart_type in ("stacked_bar", "grouped_bar"):
        return renderer(
            labels=labels or [],
            series=series or {},
            title=title,
            tone=tone,
            theme_palette=theme_palette,
        )

    return renderer(
        labels=labels or [],
        values=values or [],
        title=title,
        tone=tone,
        theme_palette=theme_palette,
    )


__all__ = [
    "render_area",
    "render_bar",
    "render_chart",
    "render_donut",
    "render_grouped_bar",
    "render_horizontal_bar",
    "render_line",
    "render_pie",
    "render_stacked_bar",
]
