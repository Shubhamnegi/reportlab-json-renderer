"""Neutral / grayscale theme.

A restrained palette suitable for invoices, proposals, or any report where
brand colour should not dominate.
"""

from reportlab_json_renderer.themes.base import Theme, build_theme

NEUTRAL: Theme = build_theme(
    name="neutral",
    tones={
        "primary": "#424242",
        "secondary": "#757575",
        "danger": "#B71C1C",
        "success": "#1B5E20",
        "warning": "#E65100",
        "info": "#0D47A1",
        "light": "#FAFAFA",
        "dark": "#212121",
        "muted": "#9E9E9E",
    },
    font_body="Helvetica",
    font_bold="Helvetica-Bold",
    font_mono="Courier",
    table_header_bg="#EEEEEE",
    callout_border_width=2.0,
    kpi_card_padding=6.0,
)
