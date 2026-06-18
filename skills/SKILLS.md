Skill: PDF Report JSON Generator

Purpose

Use this skill when the user asks to create a PDF report using the ReportLab JSON wrapper.

The agent must output only a valid JSON report specification. It must not generate Python, ReportLab, matplotlib, HTML, CSS, or shell commands unless explicitly asked by the user.

⸻

Core Rule

Always produce:

compact JSON spec → wrapper generates PDF

Never produce:

ReportLab code

⸻

When to Use

Use this skill for:

* Business reports
* Analytics reports
* Weekly performance reports
* Operational reports
* Invoices
* Proposals
* KPI summaries
* Merchant health reports
* Review reports
* Marketing reports
* Data-heavy PDF documents

⸻

Output Contract

The output must be valid JSON with this root structure:

{
  "version": "1.0",
  "template": "analytics_report_v1",
  "theme": "green",
  "metadata": {},
  "blocks": []
}

⸻

Template Selection

Choose template based on report type:

analytics_report_v1      → KPI/data-heavy reports
business_report_v1       → general business summaries
invoice_v1               → invoices/billing
proposal_v1              → sales/proposal docs
compact_report_v1        → short 1–2 page reports

When unsure, use:

analytics_report_v1

⸻

Theme Selection

Use theme names, not raw colors.

Default:

green

Available themes:

green
neutral
dark

Use tones for per-block colour semantics. Supported tones:

primary
secondary
danger
success
warning
info
light
dark
muted

⸻

Component Selection Guide

Use kpi_grid for top metrics.

Use callout or callout_group for key insights.

Use table for structured comparisons.

Use chart for visual trends.

Use insight_list for analysis points.

Use recommendations for action items.

Use page_break between major report sections.

Use image only when image source is available.

Use two_column when placing two short charts/tables side by side.

⸻

JSON Rules

* Keep JSON compact.
* Do not include layout dimensions unless necessary.
* Prefer tone over color.
* Prefer data_ref if backend already has data.
* Avoid long styling instructions.
* Avoid raw ReportLab markup.
* Escape quotes correctly.
* Keep table rows aligned with table columns.
* Do not invent data.
* Use short but meaningful titles.

⸻

Good Example

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

⸻

Bad Example

Do not output this:

from reportlab.platypus import Table, Paragraph
story.append(Table(...))

Reason: the wrapper owns layout and rendering.

⸻

Recommended Report Flow

For analytics reports, use this structure:

title metadata
kpi_grid
overall callouts
action items
performance rating table
source mix table/chart
outlet comparison table/chart
deep-dive sections
promo/driver analysis
trend table/chart
final recommendations
disclaimer

⸻

Handling Missing Data

If data is missing, use one of:

{
  "type": "callout",
  "tone": "warning",
  "title": "Data Missing",
  "text": "Outlet-level data was not available for this period."
}

or omit the section.

Do not fabricate numbers.

⸻

Token Efficiency Rules

Prefer this:

{
  "type": "chart",
  "chart_type": "bar",
  "data_ref": "orders_by_outlet"
}

Instead of this:

{
  "type": "chart",
  "chart_type": "bar",
  "labels": ["Outlet 1", "Outlet 2"],
  "values": [100, 200]
}

Use full values only when no data_ref exists.

⸻

Final Output Rule

When asked to generate a PDF spec, output JSON only.

When asked to explain the approach, explain normally.

When asked to create or modify the wrapper, provide implementation details, not PDF JSON.
