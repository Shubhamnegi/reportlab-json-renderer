"""Template registry — lookup and registration of named templates.

Ships with five built-in templates and exposes a simple API for
user-defined templates.
"""

from __future__ import annotations

from reportlab_json_renderer.templates.base import Template
from reportlab_json_renderer.utils.errors import TemplateError

# Lazily populated on first access.
_REGISTRY: dict[str, Template] | None = None


def _ensure_builtins() -> dict[str, Template]:
    """Populate the registry with built-in templates (once)."""
    global _REGISTRY
    if _REGISTRY is not None:
        return _REGISTRY

    from reportlab_json_renderer.templates.analytics_report_v1 import ANALYTICS_REPORT_V1
    from reportlab_json_renderer.templates.business_report_v1 import BUSINESS_REPORT_V1
    from reportlab_json_renderer.templates.compact_report_v1 import COMPACT_REPORT_V1
    from reportlab_json_renderer.templates.invoice_v1 import INVOICE_V1
    from reportlab_json_renderer.templates.proposal_v1 import PROPOSAL_V1

    _REGISTRY = {
        "analytics_report_v1": ANALYTICS_REPORT_V1,
        "business_report_v1": BUSINESS_REPORT_V1,
        "compact_report_v1": COMPACT_REPORT_V1,
        "invoice_v1": INVOICE_V1,
        "proposal_v1": PROPOSAL_V1,
    }
    return _REGISTRY


def get_template(name: str) -> Template:
    """Look up a template by name.

    Args:
        name: Template identifier (e.g. ``"analytics_report_v1"``).

    Returns:
        The matching :class:`Template`.

    Raises:
        TemplateError: If no template with that name is registered.
    """
    registry = _ensure_builtins()
    if name not in registry:
        available = ", ".join(sorted(registry))
        raise TemplateError(f"Unknown template {name!r}. Available templates: {available}")
    return registry[name]


def register_template(template: Template, *, overwrite: bool = False) -> None:
    """Register a custom template at runtime.

    Args:
        template: The :class:`Template` instance to register.
        overwrite: Allow overwriting an existing template with the same name.

    Raises:
        ValueError: If a template with the same name already exists and
            *overwrite* is ``False``.
    """
    registry = _ensure_builtins()
    if template.name in registry and not overwrite:
        raise ValueError(
            f"Template {template.name!r} already registered. Use overwrite=True to replace it."
        )
    registry[template.name] = template


def list_templates() -> list[str]:
    """Return sorted list of all registered template names."""
    registry = _ensure_builtins()
    return sorted(registry)
