"""Analytics report template — full-featured business analytics layout."""

from reportlab_json_renderer.templates.base import PageSpec, Template, build_template

ANALYTICS_REPORT_V1: Template = build_template(
    name="analytics_report_v1",
    description="Full-featured analytics report with charts, KPIs, and tables.",
    page=PageSpec(
        size="A4",
        orientation="portrait",
        margins={"left_cm": 1.5, "right_cm": 1.5, "top_cm": 2.2, "bottom_cm": 2.0},
    ),
    header_enabled=True,
    header_variant="default",
    footer_enabled=True,
    footer_show_page_number=True,
    section_spacing=18.0,
    allowed_blocks=set(),  # all blocks allowed
)
