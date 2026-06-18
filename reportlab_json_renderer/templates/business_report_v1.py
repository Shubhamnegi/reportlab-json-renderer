"""Business report template — professional document layout."""

from reportlab_json_renderer.templates.base import PageSpec, Template, build_template

BUSINESS_REPORT_V1: Template = build_template(
    name="business_report_v1",
    description="Professional business document with structured sections.",
    page=PageSpec(
        size="A4",
        orientation="portrait",
        margins={"left_cm": 2.0, "right_cm": 2.0, "top_cm": 2.5, "bottom_cm": 2.0},
    ),
    header_enabled=True,
    header_variant="branded",
    footer_enabled=True,
    footer_show_page_number=True,
    section_spacing=20.0,
    allowed_blocks=set(),
)
