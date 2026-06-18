# Custom Block Types

This guide explains how to create and register custom block types.

## Overview

Each block type is a Python class that:
1. Subclasses `BaseBlock` (an ABC)
2. Sets a `block_type` class attribute matching the JSON `"type"` value
3. Implements `render()` → returns a list of ReportLab `Flowable` objects

## Step 1: Create the Block Renderer

```python
# my_package/blocks/metric_card.py

from __future__ import annotations

from typing import Any

from reportlab.platypus import Flowable, Paragraph, Spacer
from reportlab.lib.units import cm

from reportlab_json_renderer.blocks.base import BaseBlock


class MetricCardBlock(BaseBlock):
    """Renders a large metric card with a value and delta indicator."""

    block_type = "metric_card"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        value = block.get("value", "")
        label = block.get("label", "")
        delta = block.get("delta", "")
        tone = block.get("tone", "primary")

        colour = theme.resolve_tone(tone)

        # Build flowables — use theme colours, fonts, spacing
        elements: list[Flowable] = []

        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER

        value_style = ParagraphStyle(
            "MetricValue",
            fontName=theme.font_bold,
            fontSize=28,
            textColor=colour,
            alignment=TA_CENTER,
        )
        label_style = ParagraphStyle(
            "MetricLabel",
            fontName=theme.font_body,
            fontSize=10,
            textColor="#666666",
            alignment=TA_CENTER,
        )

        elements.append(Paragraph(str(value), value_style))
        elements.append(Paragraph(label, label_style))
        if delta:
            elements.append(Paragraph(delta, label_style))
        elements.append(Spacer(1, 0.5 * cm))

        return elements

    def validate(self, block: dict[str, Any]) -> list[str]:
        """Optional pre-render validation."""
        warnings: list[str] = []
        if not block.get("value"):
            warnings.append("metric_card: 'value' is empty")
        return warnings
```

## Step 2: Register the Block

Register your block **before** calling `render_pdf()`. Do this once at application startup.

```python
from reportlab_json_renderer.blocks.registry import register
from my_package.blocks.metric_card import MetricCardBlock

register(MetricCardBlock())
```

## Step 3: Use in JSON

Once registered, use `"type": "metric_card"` in your JSON spec:

```json
{
  "type": "metric_card",
  "value": "₹4,50,000",
  "label": "Total Revenue",
  "delta": "+12% vs last week",
  "tone": "success"
}
```

## Adding to the Schema

To include your custom block in schema validation (JSON Schema export, `validate_spec()`),
you need to extend the Pydantic models:

```python
from pydantic import BaseModel
from typing import Literal

class MetricCardBlockModel(BaseModel):
    type: Literal["metric_card"] = "metric_card"
    value: str
    label: str = ""
    delta: str | None = None
    tone: str = "primary"
```

> **Note:** Without extending the schema, your block type will fail validation. The schema
> uses a discriminated union on the `type` field. To add custom blocks to validation,
> subclass `ReportSpec` or patch the `Block` union. For simple use cases, you can
> bypass validation by building the spec dict directly and passing it to `build_pdf()`.

## Accessing Theme and Template

The `theme` and `template` parameters give your renderer access to:

**Theme** (`Theme` dataclass):
- `theme.resolve_tone("primary")` → `"#7CB518"` hex colour
- `theme.hex_to_rgb("#FF0000")` → `(255, 0, 0)`
- `theme.font_body`, `theme.font_bold`, `theme.font_mono`
- `theme.table_header_bg`, `theme.callout_border_width`

**Template** (`Template` dataclass):
- `template.section_spacing` → spacing in points
- `template.is_block_allowed("metric_card")` → `True`/`False`

## See Also

- [`custom-themes.md`](custom-themes.md) — Creating custom themes
- [`custom-templates.md`](custom-templates.md) — Creating custom templates
- [`blocks/base.py`](../reportlab_json_renderer/blocks/base.py) — `BaseBlock` ABC source
- [`blocks/registry.py`](../reportlab_json_renderer/blocks/registry.py) — Block registry source
