# Custom Templates

This guide explains how to create and register custom report templates.

## Overview

A template defines report-level defaults:

- **Page size and margins**
- **Header and footer configuration**
- **Section spacing**
- **Allowed block types** (restrict which blocks can appear)

Templates are resolved by name from the JSON spec's `"template"` field.
Any per-spec `"page"` overrides are merged on top of the template defaults at
render time.

## Step 1 — Create the Template

### Using `build_template()` (Recommended)

```python
from reportlab_json_renderer.templates.base import (
    PageSpec,
    build_template,
)

MY_REPORT_V1 = build_template(
    name="my_report_v1",
    description="Custom quarterly summary report.",
    page=PageSpec(
        size="A4",
        orientation="portrait",
        margins={
            "left_cm": 2.0,
            "right_cm": 2.0,
            "top_cm": 2.5,
            "bottom_cm": 2.0,
        },
    ),
    header_enabled=True,
    header_variant="default",
    footer_enabled=True,
    footer_show_page_number=True,
    section_spacing=20.0,
    allowed_blocks=set(),  # empty = all blocks allowed
)
```

### Using the `Template` Dataclass Directly

```python
from reportlab_json_renderer.templates.base import PageSpec, Template

MY_REPORT_V1 = Template(
    name="my_report_v1",
    description="Custom quarterly summary report.",
    page=PageSpec(
        size="A4",
        orientation="portrait",
        margins={
            "left_cm": 2.0,
            "right_cm": 2.0,
            "top_cm": 2.5,
            "bottom_cm": 2.0,
        },
    ),
    header_enabled=True,
    header_variant="default",
    footer_enabled=True,
    footer_show_page_number=True,
    section_spacing=20.0,
    allowed_blocks=set(),
)
```

## Step 2 — Register the Template

Call `register_template()` before rendering any spec that references it.

```python
from reportlab_json_renderer.templates.registry import register_template

register_template(MY_REPORT_V1)
```

You can now use `"template": "my_report_v1"` in your JSON spec.

## Step 3 — Use in a JSON Spec

```json
{
  "version": "1.0",
  "template": "my_report_v1",
  "theme": "green",
  "metadata": {
    "entity_name": "Acme Corp",
    "report_title": "Quarterly Summary",
    "period": "Q1 2026"
  },
  "blocks": [
    { "type": "title", "entity": "Acme Corp", "title": "Quarterly Summary" }
  ]
}
```

---

## Template Fields Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | *(required)* | Machine-readable identifier used in the JSON spec. |
| `description` | `str` | `""` | Human-readable description shown in `pdf-renderer templates`. |
| `page` | `PageSpec` | A4 portrait, 1.5/1.5/2.2/2.0 cm margins | Default page size, orientation, and margins. |
| `header_enabled` | `bool` | `True` | Whether to render a page header (entity name, period, line). |
| `header_variant` | `str` | `"default"` | Header style variant (`"default"` or `"minimal"`). |
| `footer_enabled` | `bool` | `True` | Whether to render a page footer. |
| `footer_show_page_number` | `bool` | `True` | Show page numbers in the footer. |
| `section_spacing` | `float` | `18.0` | Vertical space (pt) after section headers. |
| `allowed_blocks` | `set[str]` | `set()` (all allowed) | Restrict which block types this template accepts. Empty means no restriction. |

### `PageSpec` Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `size` | `str` | `"A4"` | Paper size: `"A4"`, `"letter"`, `"legal"`, `"A3"`. |
| `orientation` | `str` | `"portrait"` | `"portrait"` or `"landscape"`. |
| `margins` | `dict` | `{"left_cm": 1.5, "right_cm": 1.5, "top_cm": 2.2, "bottom_cm": 2.0}` | Margins in centimetres. |

---

## Restricting Block Types

Use `allowed_blocks` to limit which blocks a template accepts.
This is useful for specialised layouts like invoices or receipts.

```python
INVOICE_TEMPLATE = build_template(
    name="my_invoice_v1",
    description="Compact invoice — tables and totals only.",
    page=PageSpec(size="A4", orientation="portrait"),
    header_variant="minimal",
    footer_show_page_number=False,
    section_spacing=12.0,
    allowed_blocks={
        "title",
        "section_header",
        "paragraph",
        "table",
        "spacer",
        "divider",
        "badge",
    },
)
```

If a spec contains a block type not in `allowed_blocks`, the renderer will
skip it and add a warning to the result.

---

## Page Override from JSON

The spec's `"page"` object is merged on top of the template defaults at
render time. Only the fields present in the spec override the template;
all other defaults are preserved.

```json
{
  "template": "my_report_v1",
  "page": {
    "size": "letter",
    "margins": { "left_cm": 2.5 }
  }
}
```

This uses `"letter"` page size and `2.5 cm` left margin while keeping all
other template defaults (orientation, right/top/bottom margins, etc.).

---

## Overwriting an Existing Template

To replace a built-in or previously registered template:

```python
register_template(MY_REPORT_V1, overwrite=True)
```

Without `overwrite=True`, registering a template with an existing name
raises `ValueError`.

---

## Listing Registered Templates

```python
from reportlab_json_renderer.templates.registry import list_templates

print(list_templates())
# ['analytics_report_v1', 'business_report_v1', 'compact_report_v1', ...]
```

Or via the CLI:

```bash
pdf-renderer templates
```

---

## Best Practices

1. **Choose a descriptive name** — use lowercase with underscores (e.g. `quarterly_ops_v1`).
2. **Restrict blocks for specialised layouts** — invoices and receipts should only allow the blocks they need.
3. **Set sensible margins** — wider margins for print-heavy reports, tighter for screen-only.
4. **Keep templates immutable** — they are frozen dataclasses by design; create new versions instead of mutating.
5. **Version your templates** — append `_v1`, `_v2` to names so specs can reference a specific version.
