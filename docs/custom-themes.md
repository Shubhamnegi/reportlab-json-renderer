# Custom Themes

This guide explains how to create and register custom colour/font themes.

## Overview

A theme is a coherent set of colours, fonts, and style tokens that ensure consistent
visual presentation across all blocks. Themes are plain data — no ReportLab objects.

Every theme must define at least the required tones:
`primary`, `secondary`, `danger`, `success`, `warning`, `info`, `light`, `dark`, `muted`

## Step 1: Create the Theme

### Using `build_theme()` (Recommended)

```python
from reportlab_json_renderer.themes.base import build_theme

MY_BRAND_THEME = build_theme(
    name="my_brand",
    tones={
        "primary": "#1A5276",
        "secondary": "#2E86C1",
        "danger": "#E74C3C",
        "success": "#27AE60",
        "warning": "#F39C12",
        "info": "#3498DB",
        "light": "#F8F9FA",
        "dark": "#2C3E50",
        "muted": "#7F8C8D",
    },
    font_body="Helvetica",
    font_bold="Helvetica-Bold",
    font_mono="Courier",
    table_header_bg="#EBF5FB",
    callout_border_width=3.0,
    kpi_card_padding=8.0,
)
```

### Using the `Theme` Dataclass Directly

```python
from reportlab_json_renderer.themes.base import Theme

MY_BRAND_THEME = Theme(
    name="my_brand",
    tones={
        "primary": "#1A5276",
        "secondary": "#2E86C1",
        "danger": "#E74C3C",
        "success": "#27AE60",
        "warning": "#F39C12",
        "info": "#3498DB",
        "light": "#F8F9FA",
        "dark": "#2C3E50",
        "muted": "#7F8C8D",
    },
    font_body="Helvetica",
    font_bold="Helvetica-Bold",
    font_mono="Courier",
    table_header_bg="#EBF5FB",
)
```

## Step 2: Register the Theme

Register your theme **before** calling `render_pdf()`. Do this once at application startup.

```python
from reportlab_json_renderer.themes.registry import register_theme

register_theme(MY_BRAND_THEME)
```

## Step 3: Use in JSON

Once registered, use `"theme": "my_brand"` in your JSON spec:

```json
{
  "version": "1.0",
  "template": "analytics_report_v1",
  "theme": "my_brand",
  "metadata": { ... },
  "blocks": [ ... ]
}
```

## Theme Fields Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | — | Machine-readable identifier. |
| `tones` | `dict[str, str]` | `{}` | Tone name → `#RRGGBB` hex mapping. |
| `font_body` | `str` | `"Helvetica"` | Regular body font name. |
| `font_bold` | `str` | `"Helvetica-Bold"` | Bold font name. |
| `font_mono` | `str` | `"Courier"` | Monospace/code font name. |
| `table_header_bg` | `str` | `"#F0F0F0"` | Table header background colour. |
| `callout_border_width` | `float` | `3.0` | Callout side-border width (pt). |
| `kpi_card_padding` | `float` | `8.0` | KPI card inner padding (pt). |

## Extending an Existing Theme

Use `theme.merge()` to create a variant of a built-in theme with some overrides:

```python
from reportlab_json_renderer.themes.registry import get_theme

base = get_theme("green")
custom = base.merge({
    "name": "green_custom",
    "tones": {
        **base.tones,
        "primary": "#0055A4",  # override just primary
    },
})

register_theme(custom)
```

## Tones

Tones are the primary way blocks reference colours. Instead of hardcoding hex values,
blocks use tone names like `"primary"` or `"danger"`. The active theme resolves them:

```
block.json:  {"tone": "success"}
block.py:    theme.resolve_tone("success")  →  "#27AE60"
```

If a tone is not found in the theme, the raw value is returned as-is (allowing raw hex).

## See Also

- [`custom-blocks.md`](custom-blocks.md) — Creating custom block types
- [`custom-templates.md`](custom-templates.md) — Creating custom templates
- [`themes/base.py`](../reportlab_json_renderer/themes/base.py) — Theme class source
- [`themes/registry.py`](../reportlab_json_renderer/themes/registry.py) — Theme registry source
