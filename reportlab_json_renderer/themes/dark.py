"""Dark background theme.

Designed for presentations or dashboards where a dark background provides
better contrast.  Note that ReportLab rendering on a dark background is
non-standard — this theme is primarily for header/footer branding and
colour tokens; the page background itself remains white in v1.
"""

from reportlab_json_renderer.themes.base import Theme, build_theme

DARK: Theme = build_theme(
    name="dark",
    tones={
        "primary": "#80CBC4",
        "secondary": "#4DB6AC",
        "danger": "#EF5350",
        "success": "#66BB6A",
        "warning": "#FFA726",
        "info": "#42A5F5",
        "light": "#37474F",
        "dark": "#ECEFF1",
        "muted": "#90A4AE",
    },
    font_body="Helvetica",
    font_bold="Helvetica-Bold",
    font_mono="Courier",
    table_header_bg="#37474F",
    callout_border_width=3.0,
    kpi_card_padding=10.0,
)
