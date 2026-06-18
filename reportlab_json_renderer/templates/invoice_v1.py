"""Invoice template — compact financial document layout."""

from reportlab_json_renderer.templates.base import PageSpec, Template, build_template

INVOICE_V1: Template = build_template(
    name="invoice_v1",
    description="Compact invoice layout with tables and totals.",
    page=PageSpec(
        size="A4",
        orientation="portrait",
        margins={"left_cm": 1.5, "right_cm": 1.5, "top_cm": 1.5, "bottom_cm": 1.5},
    ),
    header_enabled=True,
    header_variant="minimal",
    footer_enabled=True,
    footer_show_page_number=False,
    section_spacing=12.0,
    allowed_blocks={"title", "section_header", "paragraph", "table", "spacer", "divider", "badge"},
)
