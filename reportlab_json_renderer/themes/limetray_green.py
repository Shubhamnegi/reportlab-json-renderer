"""Default LimeTray brand theme.

Green primary with a clean, professional palette suited for business reports.
"""

from reportlab_json_renderer.themes.base import Theme, build_theme

LIMETRAY_GREEN: Theme = build_theme(
    name="limetray_green",
    tones={
        "primary": "#7CB518",
        "secondary": "#5A8A12",
        "danger": "#C62828",
        "success": "#2E7D32",
        "warning": "#E65100",
        "info": "#1565C0",
        "light": "#F5F5F5",
        "dark": "#2D2D2D",
    },
    font_body="Helvetica",
    font_bold="Helvetica-Bold",
    font_mono="Courier",
    table_header_bg="#E8F5E9",
    callout_border_width=3.0,
    kpi_card_padding=8.0,
)
