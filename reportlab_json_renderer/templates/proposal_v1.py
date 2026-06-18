"""Proposal template — sales / pitch document layout."""

from reportlab_json_renderer.templates.base import PageSpec, Template, build_template

PROPOSAL_V1: Template = build_template(
    name="proposal_v1",
    description="Sales proposal with hero sections and call-to-action blocks.",
    page=PageSpec(
        size="A4",
        orientation="portrait",
        margins={"left_cm": 2.0, "right_cm": 2.0, "top_cm": 2.5, "bottom_cm": 2.0},
    ),
    header_enabled=True,
    header_variant="hero",
    footer_enabled=True,
    footer_show_page_number=True,
    section_spacing=22.0,
    allowed_blocks=set(),
)
