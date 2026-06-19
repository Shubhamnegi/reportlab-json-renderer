# Examples

## Good: Compact JSON Spec

```json
{
  "version": "1.0",
  "template": "analytics_report_v1",
  "theme": "green",
  "metadata": {
    "entity_name": "Demo Store",
    "report_title": "Order Performance Evaluation Report",
    "period": "11 Jun – 17 Jun 2026"
  },
  "blocks": [
    {
      "type": "kpi_grid",
      "title": "Brand KPI Summary",
      "columns": 5,
      "items": [
        {"label": "Total Orders", "value": "3,743", "sub": "This Week", "tone": "primary"},
        {"label": "Net Sales", "value": "₹19,62,261", "sub": "↓ −12% vs LW", "tone": "danger"}
      ]
    },
    {
      "type": "callout",
      "tone": "danger",
      "title": "Brand-Wide Decline",
      "text": "Order volume is down 12.3% week over week."
    }
  ]
}
```

## Good: Using `data_ref` for Token Efficiency

```json
{
  "type": "chart",
  "chart_type": "bar",
  "data_ref": "orders_by_outlet"
}
```

## Bad: Inline Data (Avoid)

```json
{
  "type": "chart",
  "chart_type": "bar",
  "labels": ["Outlet 1", "Outlet 2"],
  "values": [100, 200]
}
```

Only use inline data when no `data_ref` exists.

## Bad: ReportLab Code (Never Output This)

```python
from reportlab.platypus import Table, Paragraph
story.append(Table(...))
```

The wrapper owns layout and rendering. Never generate Python or ReportLab code.
