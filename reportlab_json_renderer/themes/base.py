"""Base theme class for the PDF renderer.

A theme is a coherent set of colours, fonts, spacing, and style tokens that
blocks use for consistent visual presentation.  Themes do *not* contain any
ReportLab-specific objects — they are plain data containers resolved by the
block renderers.

Conventions
-----------
- Agents must reference tones (``"primary"``, ``"danger"`` …) not hex codes.
- Every theme must define at least the ``DEFAULT_TONES`` keys.
- Fonts are identified by name; the renderer resolves them to ReportLab
  font objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Tones every theme must define.
DEFAULT_TONES: list[str] = [
    "primary",
    "secondary",
    "danger",
    "success",
    "warning",
    "info",
    "light",
    "dark",
    "muted",
]


@dataclass(frozen=True)
class Theme:
    """Immutable theme definition.

    Attributes:
        name: Machine-readable identifier (e.g. ``"limetray_green"``).
        tones: Mapping of tone name → ``"#RRGGBB"`` hex string.
        font_body: Regular body font name.
        font_bold: Bold font name.
        font_mono: Monospace / code font name.
        table_header_bg: Background hex for table header rows.
        callout_border_width: Default width for callout side-borders (pt).
        kpi_card_padding: Inner padding for KPI cards (pt).
    """

    name: str
    tones: dict[str, str] = field(default_factory=dict)
    font_body: str = "Helvetica"
    font_bold: str = "Helvetica-Bold"
    font_mono: str = "Courier"
    table_header_bg: str = "#F0F0F0"
    callout_border_width: float = 3.0
    kpi_card_padding: float = 8.0

    # ── helpers ──────────────────────────────────────────────────────

    def resolve_tone(self, tone: str) -> str:
        """Resolve a tone name to its ``#RRGGBB`` hex value.

        Falls back to the *tone name itself* if the tone is not present,
        so that a raw hex like ``"#FF0000"`` can still be passed through.

        Args:
            tone: Semantic tone name (e.g. ``"danger"``).

        Returns:
            Hex colour string.
        """
        return self.tones.get(tone, tone)

    def hex_to_rgb(self, hex_color: str) -> tuple[int, int, int]:
        """Convert a ``#RRGGBB`` hex string to an ``(R, G, B)`` tuple.

        Args:
            hex_color: Six-character hex string with leading ``#``.

        Returns:
            Tuple of red, green, blue integers (0-255).
        """
        h = hex_color.lstrip("#")
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    def merge(self, overrides: dict[str, Any]) -> Theme:
        """Return a new ``Theme`` with selected fields overridden.

        Args:
            overrides: Key/value pairs matching ``Theme`` fields.

        Returns:
            New ``Theme`` instance.

        Raises:
            ValueError: If an override key is not a valid ``Theme`` field.
        """
        valid_fields = {f.name for f in self.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        bad = set(overrides) - valid_fields
        if bad:
            raise ValueError(f"Unknown theme override keys: {bad}")
        # Build a dict of current values, apply overrides, return new Theme.
        current: dict[str, Any] = {
            f.name: getattr(self, f.name)  # type: ignore[attr-defined]
            for f in self.__dataclass_fields__.values()  # type: ignore[attr-defined]
        }
        current.update(overrides)
        return Theme(**current)


def build_theme(
    name: str,
    tones: dict[str, str],
    *,
    font_body: str = "Helvetica",
    font_bold: str = "Helvetica-Bold",
    font_mono: str = "Courier",
    table_header_bg: str = "#F0F0F0",
    callout_border_width: float = 3.0,
    kpi_card_padding: float = 8.0,
) -> Theme:
    """Convenience factory that validates the tone set.

    Raises:
        ValueError: If a required default tone is missing.
    """
    missing = [t for t in DEFAULT_TONES if t not in tones]
    if missing:
        raise ValueError(f"Theme {name!r} is missing required tones: {missing}")
    return Theme(
        name=name,
        tones=tones,
        font_body=font_body,
        font_bold=font_bold,
        font_mono=font_mono,
        table_header_bg=table_header_bg,
        callout_border_width=callout_border_width,
        kpi_card_padding=kpi_card_padding,
    )
