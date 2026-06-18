"""Compact report template — dense, data-heavy layout."""

from reportlab_json_renderer.templates.base import PageSpec, Template, build_template

COMPACT_REPORT_V1: Template = build_template(
    name="compact_report_v1",
    description="Dense layout for data-heavy reports with minimal whitespace.",
    page=PageSpec(
        size="A4",
        orientation="portrait",
        margins={"left_cm": 1.0, "right_cm": 1.0, "top_cm": 1.2, "bottom_cm": 1.0},
    ),
    header_enabled=True,
    header_variant="compact",
    footer_enabled=True,
    footer_show_page_number=True,
    section_spacing=10.0,
    allowed_blocks=set(),
)
