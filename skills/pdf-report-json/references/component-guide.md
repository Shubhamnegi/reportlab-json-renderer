# Component Selection Guide

## Block Types and When to Use Them

| Block | Use When | Key Fields |
|-------|----------|------------|
| `title` | Report header with entity name, title, subtitle, right-aligned text | `entity`, `title`, `subtitle`, `right_text` |
| `section_header` | Numbered section headings that divide the report into logical parts | `title`, `number` |
| `kpi_grid` | Top metrics or KPI cards | `title`, `columns`, `items[]` |
| `callout` | Key insight, alert, or single highlight with tone-tinted background | `tone`, `title`, `text` |
| `callout_group` | Multiple callouts under a shared heading | `title`, `items[]` |
| `summary_box` | Executive summary card with tone-matched background | `title`, `text`, `tone` |
| `table` | Structured data comparisons | `title`, `style`, `columns[]`, `rows[]` |
| `matrix_table` | Cross-tab / pivot comparisons | `title`, `columns[]`, `rows[][]` |
| `chart` | Visual trends (bar, line, pie, doughnut, horizontal_bar, grouped_bar, stacked_bar, area) | `chart_type`, `labels`, `values`, `series`, `data_ref` |
| `insight_list` | Numbered or bulleted analysis points | `title`, `items[]` |
| `recommendations` | Action items with priority, action, owner, impact | `title`, `items[]` |
| `rich_text` | Inline-styled text runs with mixed bold/italic/colour | `runs[]` |
| `paragraph` | Body text; supports HTML tags: `<b>`, `<i>`, `<u>`, `<br/>` | `text`, `style` |
| `badge` | Small inline labels (e.g. status tags) | `label`, `tone` |
| `divider` | Horizontal separator line | `tone`, `thickness` |
| `spacer` | Vertical spacing | `height` |
| `page_break` | Force a page break between major sections | _(none)_ |
| `image` | Image from local filesystem | `src`, `title`, `width_cm`, `height_cm`, `align` |
| `two_column` | Two short charts/tables side by side | `left[]`, `right[]`, `left_width`, `right_width` |

## Tones

Semantic colour names resolved by the active theme. All themes define:

`primary`, `secondary`, `danger`, `success`, `warning`, `info`, `light`, `dark`, `muted`

Raw hex values (e.g. `"#FF0000"`) are also accepted.

## Limit Constants

| Constant | Value |
|----------|-------|
| `MAX_SPEC_BYTES` | 1,000,000 |
| `MAX_BLOCK_COUNT` | 200 |
| `MAX_TABLE_ROWS` | 500 |
| `MAX_TABLE_COLUMNS` | 20 |
| `MAX_MATRIX_ROWS` | 500 |
| `MAX_MATRIX_COLUMNS` | 20 |
| `MAX_CHART_POINTS` | 500 |
| `MAX_CHART_SERIES` | 10 |
