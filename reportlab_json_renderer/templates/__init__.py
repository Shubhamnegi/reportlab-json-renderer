"""Built-in report templates.

Each template defines page-level defaults (size, margins, header, footer,
section spacing, allowed block types) for a specific report style.

Usage::

    from reportlab_json_renderer.templates import get_template

    tpl = get_template("analytics_report_v1")
"""

from reportlab_json_renderer.templates.base import (
    PageSpec,
    Template,
    build_template,
)
from reportlab_json_renderer.templates.registry import (
    get_template,
    list_templates,
    register_template,
)

__all__ = [
    "PageSpec",
    "Template",
    "build_template",
    "get_template",
    "list_templates",
    "register_template",
]
