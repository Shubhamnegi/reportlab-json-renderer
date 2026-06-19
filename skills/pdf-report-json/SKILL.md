---
name: pdf-report-json
description: Generates compact JSON report specifications for the ReportLab JSON wrapper. Use when the user asks to create, draft, or structure a PDF report (business, analytics, invoice, proposal, KPI, marketing, operational). Do not use when the user asks to modify the wrapper, write ReportLab/Python code, or generate HTML/CSS.
---

# PDF Report JSON Generator

## Procedures

**Step 1: Determine template and theme**

1. Select the template based on report type:
   - `analytics_report_v1` → KPI / data-heavy reports (default when unsure)
   - `business_report_v1` → general business summaries
   - `invoice_v1` → invoices / billing
   - `proposal_v1` → sales / proposal docs
   - `compact_report_v1` → short 1–2 page reports
2. Select the theme (default: `green`). Available: `green`, `neutral`, `dark`.

**Step 2: Assemble the JSON specification**

1. Build the root object with `version`, `template`, `theme`, `metadata`, and `blocks`.
2. Ensure `metadata` includes `entity_name` and `report_title`. Add `period` when available.
3. Add blocks in logical order. Read `references/component-guide.md` to choose the correct block type for each section.
4. Apply tones (`primary`, `secondary`, `danger`, `success`, `warning`, `info`, `light`, `dark`, `muted`) for per-block colour semantics. Use tones, not raw colours.
5. Follow the recommended analytics report flow:
   ```
   title → kpi_grid → section_header + callouts → section_header + action items
   → section_header + performance table → section_header + chart/table
   → section_header + deep-dive → section_header + recommendations
   → divider + disclaimer
   ```

**Step 3: Apply JSON rules and validate**

1. Keep JSON compact. Omit layout dimensions unless necessary.
2. Prefer `data_ref` over inline `labels`/`values` when backend data exists.
3. Escape quotes correctly. Keep table rows aligned with table columns.
4. Do not invent data. Use short but meaningful titles.
5. Read `references/json-contract.md` to verify field names and types against the contract.

**Step 4: Handle missing data**

1. If data is unavailable, insert a warning callout:
   ```json
   {"type": "callout", "tone": "warning", "title": "Data Missing", "text": "<reason>."}
   ```
2. Alternatively, omit the section entirely.
3. Never fabricate numbers.

## Output Contract

Output valid JSON only. Read `references/examples.md` for reference specimens.

Core rule: always produce a compact JSON spec. Never produce ReportLab, Python, matplotlib, HTML, CSS, or shell commands unless explicitly asked.

## Error Handling

* If a block type is not recognised, consult `references/component-guide.md` for the full list of supported blocks.
* If the spec exceeds `MAX_BLOCK_COUNT` (200 blocks) or other limits in `references/component-guide.md`, reduce the block count or split into multiple reports.
* If `metadata` fields are missing, ask the user to provide `entity_name` and `report_title` before generating the spec.
* If the user requests a chart type not in the supported list (`bar`, `line`, `pie`, `doughnut`, `horizontal_bar`, `grouped_bar`, `stacked_bar`, `area`), suggest the closest alternative and explain the limitation.
