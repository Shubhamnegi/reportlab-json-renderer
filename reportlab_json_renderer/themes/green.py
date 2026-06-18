"""Default public green theme.

Green primary with a clean, professional palette suited for business reports.
"""

from reportlab_json_renderer.themes.base import Theme, build_theme

GREEN_THEME: Theme = build_theme(
    name="green",
    tones={
        "primary": "#7CB518",
        "secondary": "#5A8A12",
        "danger": "#C62828",
        "success": "#2E7D32",
        "warning": "#E65100",
        "info": "#1565C0",
        "light": "#F5F5F5",
        "dark": "#2D2D2D",
        "muted": "#757575",
    },
    font_body="DejaVuSans",
    font_bold="DejaVuSans-Bold",
    font_mono="DejaVuSansMono",
    table_header_bg="#E8F5E9",
    callout_border_width=3.0,
    kpi_card_padding=8.0,
)
