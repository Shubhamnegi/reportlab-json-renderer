# JSON Contract Reference

Human-readable field reference for the report specification JSON contract.

## Top-Level Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `version` | `string` | No | `"1.0"` | Schema version. Must be `"1.0"`. |
| `template` | `string` | **Yes** | — | Template identifier (e.g. `"analytics_report_v1"`). |
| `theme` | `string` | No | `"limetray_green"` | Theme identifier (e.g. `"limetray_green"`, `"neutral"`, `"dark"`). |
| `metadata` | `object` | **Yes** | — | Report metadata (entity, title, period). |
| `page` | `object` | No | See below | Page size, orientation, and margins. |
| `header` | `object` | No | `{ "enabled": true }` | Header configuration. |
| `footer` | `object` | No | `{ "enabled": true }` | Footer configuration. |
| `blocks` | `array` | No | `[]` | Ordered list of content blocks. |

---

## `metadata`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `entity_name` | `string` | **Yes** | — | Business/entity name shown in headers. |
| `report_title` | `string` | **Yes** | — | Report title. |
| `period` | `string` | No | `null` | Reporting period (e.g. `"1 Jun – 7 Jun 2026"`). |
| `generated_at` | `string` | No | `null` | ISO date or date string. |
| `powered_by` | `string` | No | `null` | Attribution text shown in footer. |
| `confidential` | `boolean` | No | `false` | Confidentiality flag. |

---

## `page`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `size` | `string` | No | `"A4"` | Paper size: `"A4"`, `"letter"`, `"legal"`, `"A3"`. |
| `orientation` | `string` | No | `"portrait"` | `"portrait"` or `"landscape"`. |
| `margins` | `object` | No | See below | Margins in centimetres. |

### `page.margins`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `left_cm` | `number` | No | `1.5` | Left margin in cm. |
| `right_cm` | `number` | No | `1.5` | Right margin in cm. |
| `top_cm` | `number` | No | `2.2` | Top margin in cm. |
| `bottom_cm` | `number` | No | `2.0` | Bottom margin in cm. |

---

## `header`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `enabled` | `boolean` | No | `true` | Whether to render a page header. |
| `variant` | `string` | No | `"default"` | Header style variant. |

---

## `footer`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `enabled` | `boolean` | No | `true` | Whether to render a page footer. |
| `show_page_number` | `boolean` | No | `true` | Show page numbers in the footer. |

---

## Block Types

All blocks have a required `type` field that identifies the block kind. Additional
fields are specific to each block type.

### `title`

Report title block with entity name, title, subtitle, and optional right-aligned text.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `entity` | `string` | No | `null` | Entity name. |
| `title` | `string` | No | `null` | Main title text. |
| `subtitle` | `string` | No | `null` | Subtitle text. |
| `right_text` | `string` | No | `null` | Right-aligned text (e.g. date). |

### `section_header`

Section header with optional numbering.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | `string` | **Yes** | — | Section title. |
| `number` | `string` | No | `null` | Section number (e.g. `"1"`, `"2.3"`). |

### `paragraph`

Body text with style variants.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `text` | `string` | **Yes** | — | Paragraph text. |
| `style` | `string` | No | `"body"` | Style variant: `"body"`, `"bold"`, `"italic"`, `"small"`. |

### `rich_text`

Inline styled text with mixed formatting runs.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `runs` | `array` | **Yes** | — | List of text runs. |

Each run:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `text` | `string` | **Yes** | — | Text content. |
| `bold` | `boolean` | No | `false` | Bold text. |
| `italic` | `boolean` | No | `false` | Italic text. |
| `tone` | `string` | No | `null` | Colour tone name. |

### `kpi_grid`

Grid of KPI (Key Performance Indicator) cards.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | `string` | No | `null` | Section title above the grid. |
| `columns` | `integer` | No | `4` | Number of columns (1–12). |
| `items` | `array` | **Yes** | — | List of KPI items. |

Each item:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `label` | `string` | **Yes** | — | KPI label. |
| `value` | `string` | **Yes** | — | KPI value. |
| `sub` | `string` | No | `null` | Sub-text (e.g. `"+12% WoW"`). |
| `tone` | `string` | No | `null` | Colour tone. |

### `callout`

Coloured callout box.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | `string` | No | `null` | Callout title. |
| `text` | `string` | **Yes** | — | Callout body text. |
| `tone` | `string` | No | `"info"` | Colour tone. |

### `callout_group`

Group of callouts under a shared title.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | `string` | No | `null` | Group title. |
| `items` | `array` | **Yes** | — | List of callout items (same fields as `callout`). |

### `table`

Data table with column definitions and rows.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | `string` | No | `null` | Table title. |
| `style` | `string` | No | `"standard"` | `"standard"`, `"striped"`, or `"compact"`. |
| `columns` | `array` | **Yes** | — | Column definitions. |
| `rows` | `array` | **Yes** | — | Row data (dicts keyed by column key). |

Each column:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `key` | `string` | **Yes** | — | Key used in row dicts. |
| `label` | `string` | **Yes** | — | Column header text. |
| `width` | `number` | No | `0.2` | Column width as fraction (0–1). |

### `matrix_table`

Column-oriented comparison table (no row key mapping).

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | `string` | No | `null` | Table title. |
| `columns` | `array[string]` | **Yes** | — | Column header labels. |
| `rows` | `array[array[string]]` | **Yes** | — | Row data as lists of strings. |

### `insight_list`

Numbered/bulleted insight items.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | `string` | No | `null` | Section title. |
| `items` | `array` | **Yes** | — | List of insight items. |

Each item:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | `string` | **Yes** | — | Insight heading. |
| `text` | `string` | **Yes** | — | Insight description. |

### `recommendations`

Action/recommendation table with priority, owner, and impact.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | `string` | No | `null` | Section title. |
| `items` | `array` | **Yes** | — | List of recommendation items. |

Each item:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `action` | `string` | **Yes** | — | Recommended action. |
| `priority` | `string` | **Yes** | — | Priority level (e.g. `"high"`, `"medium"`, `"low"`). |
| `owner` | `string` | No | `null` | Responsible party. |
| `impact` | `string` | No | `null` | Expected impact. |

### `image`

Image block supporting local files, HTTP URLs, and base64 data.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `src` | `string` | **Yes** | — | Image source (file path, URL, or data URI). |
| `title` | `string` | No | `null` | Image caption. |
| `width_cm` | `number` | No | `null` | Width in cm. |
| `height_cm` | `number` | No | `null` | Height in cm. |
| `fit` | `string` | No | `"contain"` | `"contain"`, `"cover"`, or `"stretch"`. |
| `align` | `string` | No | `"center"` | `"left"`, `"center"`, or `"right"`. |

### `chart`

Chart rendered via matplotlib.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `chart_type` | `string` | **Yes** | — | Chart type (see below). |
| `title` | `string` | No | `null` | Chart title. |
| `labels` | `array[string]` | No | `[]` | Category labels. |
| `values` | `array[number]` | No | `[]` | Data values. |
| `series` | `object` | No | `null` | Multi-series data `{ "name": [values] }`. |
| `tone` | `string` | No | `null` | Colour tone. |

Supported chart types: `bar`, `line`, `pie`, `doughnut`, `horizontal_bar`, `grouped_bar`, `stacked_bar`, `area`.

### `two_column`

Two-column layout container.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `left_width` | `number` | No | `0.5` | Left column width fraction (0–1). |
| `right_width` | `number` | No | `0.5` | Right column width fraction (0–1). |
| `left` | `array[block]` | No | `[]` | Blocks in the left column. |
| `right` | `array[block]` | No | `[]` | Blocks in the right column. |

### `page_break`

Forces a page break. No additional fields.

### `spacer`

Vertical spacing.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `height` | `number` | No | `6` | Height in points. |

### `divider`

Horizontal rule.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `tone` | `string` | No | `"light"` | Colour tone. |
| `thickness` | `number` | No | `0.5` | Line thickness in points. |

### `badge`

Small inline label.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `label` | `string` | **Yes** | — | Badge text. |
| `tone` | `string` | No | `"primary"` | Colour tone. |

### `summary_box`

Executive summary card with title and body text.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | `string` | No | `null` | Box title. |
| `text` | `string` | **Yes** | — | Summary text. |
| `tone` | `string` | No | `"primary"` | Accent colour tone. |

---

## Tones

Tones are semantic colour names resolved by the active theme. All themes must define:

`primary`, `secondary`, `danger`, `success`, `warning`, `info`, `light`, `dark`, `muted`

You can also pass raw hex values (e.g. `"#FF0000"`) — they pass through unchanged.

---

## Generating the Machine-Readable Schema

```bash
# Print to stdout
pdf-renderer schema

# Write to file
pdf-renderer schema --output schema.json
```

Or programmatically:

```python
from reportlab_json_renderer.schema.validators import generate_schema_json

schema = generate_schema_json()
```
