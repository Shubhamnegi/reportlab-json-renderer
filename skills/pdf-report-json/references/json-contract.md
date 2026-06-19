# JSON Specification Contract

## Root Structure

```json
{
  "version": "1.0",
  "template": "<template_id>",
  "theme": "<theme_id>",
  "metadata": {},
  "page": {},
  "header": {},
  "footer": {},
  "blocks": []
}
```

## Top-Level Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `version` | `string` | No | `"1.0"` | Schema version. Must be `"1.0"`. |
| `template` | `string` | **Yes** | — | Template identifier. |
| `theme` | `string` | No | `"green"` | Theme identifier. |
| `metadata` | `object` | **Yes** | — | Report metadata. |
| `page` | `object` | No | `A4 portrait` | Page size, orientation, margins. |
| `header` | `object` | No | `{ "enabled": true }` | Header configuration. |
| `footer` | `object` | No | `{ "enabled": true }` | Footer configuration. |
| `blocks` | `array` | No | `[]` | Ordered content blocks. |

## `metadata`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `entity_name` | `string` | **Yes** | — | Business/entity name in headers. |
| `report_title` | `string` | **Yes** | — | Report title. |
| `period` | `string` | No | `null` | Reporting period. |
| `generated_at` | `string` | No | `null` | ISO date or date string. |
| `powered_by` | `string` | No | `null` | Attribution text in footer. |
| `confidential` | `boolean` | No | `false` | Confidentiality flag. |

## `page`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `size` | `string` | No | `"A4"` | `"A4"`, `"letter"`, `"legal"`, `"A3"`. |
| `orientation` | `string` | No | `"portrait"` | `"portrait"` or `"landscape"`. |
| `margins` | `object` | No | see below | Margins in centimetres. |

### `page.margins`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `left_cm` | `number` | No | `1.5` | Left margin in cm. |
| `right_cm` | `number` | No | `1.5` | Right margin in cm. |
| `top_cm` | `number` | No | `2.2` | Top margin in cm. |
| `bottom_cm` | `number` | No | `2.0` | Bottom margin in cm. |

## `header`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `enabled` | `boolean` | No | `true` | Render page header. |
| `variant` | `string` | No | `"default"` | Header style variant. |

## `footer`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `enabled` | `boolean` | No | `true` | Render page footer. |
| `show_page_number` | `boolean` | No | `true` | Show page numbers. |
