"""Shared table styling helpers for report components."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors

from reportlab_json_renderer.visual.constants import BORDER_MUTED, TABLE_ROW_STRIPE


def table_header_background(theme: Any) -> str:
    """Return a high-contrast table header background."""
    if theme is None:
        return "#2D2D2D"
    if getattr(theme, "name", "") == "dark":
        return theme.resolve_tone("light")
    return theme.resolve_tone("dark")


def table_grid_color() -> colors.HexColor:
    """Return the standard muted table grid colour."""
    return colors.HexColor(BORDER_MUTED)


def table_stripe_colors(theme: Any) -> list[colors.Color]:
    """Return alternating row colours for data tables."""
    stripe_color = theme.resolve_tone("light") if theme else TABLE_ROW_STRIPE
    return [colors.white, colors.HexColor(stripe_color)]
