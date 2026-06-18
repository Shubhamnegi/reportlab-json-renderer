"""Font registration for Unicode-capable rendering.

Registers DejaVu Sans TTF fonts with ReportLab so that Unicode characters
(₹ ↑ ↓ − × ⚠️ etc.) render correctly instead of showing black boxes.

DejaVu Sans ships with matplotlib and is always available in the venv.
"""

from __future__ import annotations

import os
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def _find_dejavu_dir() -> Path | None:
    """Locate the DejaVu fonts directory via matplotlib."""
    try:
        import matplotlib.font_manager as fm  # noqa: WPS433

        sample = fm.findfont("DejaVu Sans")
        return Path(sample).parent
    except Exception:
        return None


_FONTS_REGISTERED = False


def ensure_unicode_fonts() -> None:
    """Register DejaVu Sans family with ReportLab (once).

    Safe to call multiple times; only the first call has any effect.
    """
    global _FONTS_REGISTERED  # noqa: PLW0603
    if _FONTS_REGISTERED:
        return

    font_dir = _find_dejavu_dir()
    if font_dir is None:
        return

    font_map = {
        "DejaVuSans": "DejaVuSans.ttf",
        "DejaVuSans-Bold": "DejaVuSans-Bold.ttf",
        "DejaVuSans-Oblique": "DejaVuSans-Oblique.ttf",
        "DejaVuSans-BoldOblique": "DejaVuSans-BoldOblique.ttf",
        "DejaVuSansMono": "DejaVuSansMono.ttf",
        "DejaVuSansMono-Bold": "DejaVuSansMono-Bold.ttf",
    }

    for face_name, filename in font_map.items():
        ttf_path = font_dir / filename
        if ttf_path.exists():
            pdfmetrics.registerFont(TTFont(face_name, str(ttf_path)))

    # Register font families so ReportLab can resolve <b> and <i> tags.
    pdfmetrics.registerFontFamily(
        "DejaVuSans",
        normal="DejaVuSans",
        bold="DejaVuSans-Bold",
        italic="DejaVuSans-Oblique",
        boldItalic="DejaVuSans-BoldOblique",
    )
    pdfmetrics.registerFontFamily(
        "DejaVuSansMono",
        normal="DejaVuSansMono",
        bold="DejaVuSansMono-Bold",
        italic="DejaVuSansMono",
        boldItalic="DejaVuSansMono-Bold",
    )

    _FONTS_REGISTERED = True


__all__ = ["ensure_unicode_fonts"]
