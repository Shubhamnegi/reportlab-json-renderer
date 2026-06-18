"""Tone-to-colour resolver.

The JSON spec uses semantic *tones* (``"primary"``, ``"danger"``, …) instead of
raw hex values.  This module resolves a tone name to a hex string using the
active theme's colour palette.  If no theme is loaded it falls back to a
sensible default palette.

ReportLab expects colours as ``"#RRGGBB"`` strings or ``Color`` objects.
This module returns hex strings; the block renderers convert as needed.
"""

from __future__ import annotations

from reportlab.lib.colors import HexColor

from reportlab_json_renderer.utils.errors import ThemeError

# Default palette — used when no theme is provided or a tone is missing
# from the active theme.
_DEFAULT_PALETTE: dict[str, str] = {
    "primary": "#7CB518",
    "danger": "#C62828",
    "success": "#2E7D32",
    "warning": "#E65100",
    "info": "#1565C0",
    "dark": "#2D2D2D",
    "muted": "#555555",
    "light_bg": "#F5F5F5",
    "white": "#FFFFFF",
    "black": "#000000",
}


def resolve_tone(tone: str, theme_palette: dict[str, str] | None = None) -> str:
    """Resolve a semantic tone name to a ``"#RRGGBB"`` hex string.

    Args:
        tone: Semantic tone name, e.g. ``"primary"``, ``"danger"``.
        theme_palette: Optional colour palette from the active theme.
            Keys are tone names, values are hex strings.

    Returns:
        Hex colour string (e.g. ``"#7CB518"``).

    Raises:
        ThemeError: If the tone is not found in *theme_palette* **and**
            not in the default palette.
    """
    palette = {**_DEFAULT_PALETTE, **(theme_palette or {})}

    try:
        hex_value = palette[tone]
    except KeyError:
        raise ThemeError(
            f"Unknown tone {tone!r}. "
            f"Available tones: {', '.join(sorted(palette))}"
        ) from None

    return hex_value


def tone_to_color(tone: str, theme_palette: dict[str, str] | None = None) -> HexColor:
    """Resolve a tone and return a ReportLab ``HexColor``.

    Args:
        tone: Semantic tone name.
        theme_palette: Optional theme colour palette.

    Returns:
        A ``reportlab.lib.colors.HexColor`` instance.

    Raises:
        ThemeError: If the tone cannot be resolved.
    """
    return HexColor(resolve_tone(tone, theme_palette))


def is_valid_tone(tone: str, theme_palette: dict[str, str] | None = None) -> bool:
    """Check whether *tone* is a known tone without raising.

    Args:
        tone: Tone name to check.
        theme_palette: Optional theme colour palette.

    Returns:
        ``True`` if the tone can be resolved, ``False`` otherwise.
    """
    palette = {**_DEFAULT_PALETTE, **(theme_palette or {})}
    return tone in palette


__all__ = [
    "is_valid_tone",
    "resolve_tone",
    "tone_to_color",
]
