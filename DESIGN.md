---
version: alpha
name: ReportLab-JSON-Renderer-design-system
description: Current PDF visual design system for reportlab-json-renderer. The system is a backend-owned report UI built from semantic themes, reusable ReportLab block components, and document templates. It favors compact business reporting: A4 pages, semantic tone colors, DejaVu fonts, dense tables, KPI cards, callouts, charts, and repeatable header/footer chrome.
colors:
  tones:
    primary: Semantic brand/action color. Green theme uses "#7CB518".
    secondary: Secondary brand color. Green theme uses "#5A8A12".
    danger: Negative/destructive state. Green theme uses "#C62828".
    success: Positive state. Green theme uses "#2E7D32".
    warning: Caution state. Green theme uses "#E65100".
    info: Informational state. Green theme uses "#1565C0".
    light: Soft background/inset surface. Green theme uses "#F5F5F5".
    dark: Primary text color. Green theme uses "#2D2D2D".
    muted: Secondary text color. Green theme uses "#757575".
  builtInThemes:
    green:
      primary: "#7CB518"
      secondary: "#5A8A12"
      danger: "#C62828"
      success: "#2E7D32"
      warning: "#E65100"
      info: "#1565C0"
      light: "#F5F5F5"
      dark: "#2D2D2D"
      muted: "#757575"
      tableHeaderBg: "#C8E6C9"
    neutral:
      primary: "#424242"
      secondary: "#757575"
      danger: "#B71C1C"
      success: "#1B5E20"
      warning: "#E65100"
      info: "#0D47A1"
      light: "#FAFAFA"
      dark: "#212121"
      muted: "#9E9E9E"
      tableHeaderBg: "#EEEEEE"
    dark:
      primary: "#80CBC4"
      secondary: "#4DB6AC"
      danger: "#EF5350"
      success: "#66BB6A"
      warning: "#FFA726"
      info: "#42A5F5"
      light: "#37474F"
      dark: "#ECEFF1"
      muted: "#90A4AE"
      tableHeaderBg: "#37474F"
typography:
  fontBody: DejaVuSans
  fontBold: DejaVuSans-Bold
  fontMono: DejaVuSansMono
  titleMain: { fontSize: 22pt, lineHeight: 27pt, weight: bold }
  sectionHeader: { fontSize: 14pt, lineHeight: 18pt, weight: bold }
  blockTitle: { fontSize: 11-12pt, weight: bold }
  paragraphLead: { fontSize: 12pt, lineHeight: 18pt }
  paragraphBody: { fontSize: 10pt, lineHeight: 14pt }
  paragraphSmall: { fontSize: 9pt, lineHeight: 12.6pt }
  caption: { fontSize: 8pt, lineHeight: 11.2pt }
  tableText: { fontSize: 9pt, lineHeight: 14pt }
  headerFooter: { fontSize: 8pt }
rounded:
  card: 4pt
  badge: 4pt
spacing:
  pageMarginCompact: 1.0-1.2cm
  pageMarginDefault: 1.5-2.2cm
  pageMarginEditorial: 2.0-2.5cm
  sectionSpacing: 10-22pt
  blockGap: 8pt
  paragraphGap: 4-10pt
  tableCellPadding: "6pt horizontal, 4pt vertical"
  cardPadding: 8-14pt
components:
  title-block:
    typography: "{typography.titleMain}"
    separator: "3pt {colors.primary}"
  section-header:
    typography: "{typography.sectionHeader}"
    separator: "0.5pt {colors.primary}"
  paragraph:
    typography: "{typography.paragraphBody}"
  kpi-grid:
    backgroundColor: "{colors.light}"
    borderColor: "{colors.primary}"
    accent: "3pt left primary rule"
  callout:
    backgroundColor: "tone tint"
    borderColor: "selected tone"
    accent: "left rule using callout_border_width"
  table:
    headerBackground: "{colors.dark}"
    gridColor: "#D8DCE2"
    rowStripe: "{colors.light}"
  chart:
    renderer: matplotlib PNG
    size: "90% content width by 50% of image width"
---

## Overview

`reportlab-json-renderer` does not have a browser UI. Its current UI design system is the visual language used to render JSON into polished PDFs: semantic themes, document templates, and reusable ReportLab block renderers.

The design direction is compact, operational, and business-report oriented. Pages use mostly white canvas, semantic color accents, dense data tables, KPI grids, callouts, chart images, and repeating header/footer chrome. The styling is intentionally backend-owned so callers and agents choose report structure and semantic tones rather than low-level coordinates or raw ReportLab styling.

Key characteristics:

- Semantic tone-first color use. Blocks should use `primary`, `danger`, `success`, `warning`, `info`, `light`, `dark`, and `muted`, not hardcoded hex colors.
- Compact PDF typography. Most body content renders at 9-10pt, with 11-12pt block titles, 14pt section headers, and 22pt document titles.
- Controlled accent hierarchy. Primary color is reserved for brand chrome, title rules, and state accents; dense tables use muted hairlines.
- Table-driven layout. Cards, badges, callouts, KPI grids, and two-column layouts are implemented with ReportLab tables.
- Template-owned page density. Templates set margins, header/footer defaults, and section spacing.

## Professional PDF Standard

The current polish target is modeled on professional operating reports such as the attached `LimeTray_WA_Ticket_Report.pdf`: strong report identity, one clear brand accent, compact KPI cards, low-noise tables, and consistent footer metadata.

Applied standards:

- Visual hierarchy should guide the reader through scale, contrast, grouping, and color. NN/g describes hierarchy as using color/contrast, scale, and grouping to direct attention to important page elements.
- Body text and table text should maintain strong contrast. WCAG 2.2 recommends at least 4.5:1 contrast for normal text and 3:1 for large text.
- Data tables should be given enough width and consistent row/header sizing. IBM Carbon notes that data tables organize dense data efficiently, can use zebra striping for scanning, and should avoid cramped placements.
- Repeating chrome should orient, not dominate. Header/footer text is metadata; it should be muted and consistent while brand color appears as a controlled top rule.
- State color should be semantic. Red/green/amber/blue communicate status, but the same information should still be readable through labels and hierarchy.

Sources:

- W3C WCAG 2.2 contrast guidance: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- IBM Carbon data-table guidance: https://carbondesignsystem.com/components/data-table/usage/
- Nielsen Norman Group visual hierarchy definition: https://www.nngroup.com/articles/visual-hierarchy-ux-definition/

## Colors

### Semantic Tones

The canonical color API is the `Theme.tones` mapping in `reportlab_json_renderer/themes/base.py`. Every theme must provide:

| Tone | Role |
|---|---|
| `primary` | Brand/action accent, top page band, title separator, KPI/card accents, default chart tone. |
| `secondary` | Secondary brand accent. Present in themes, lightly used by current blocks. |
| `danger` | Negative metric, destructive or risky condition. |
| `success` | Positive metric or recommended/healthy condition. |
| `warning` | Caution, pending, medium risk. |
| `info` | Informational state and supporting chart/category color. |
| `light` | Soft card/table stripe/header background. |
| `dark` | Main text on light PDF canvas. |
| `muted` | Secondary labels, metadata, captions, header/footer text. |

### Built-In Palettes

#### Green

Default public report theme. It is the most branded palette and currently drives samples and examples.

| Token | Value |
|---|---|
| `primary` | `#7CB518` |
| `secondary` | `#5A8A12` |
| `danger` | `#C62828` |
| `success` | `#2E7D32` |
| `warning` | `#E65100` |
| `info` | `#1565C0` |
| `light` | `#F5F5F5` |
| `dark` | `#2D2D2D` |
| `muted` | `#757575` |
| `table_header_bg` | `#C8E6C9` |

#### Neutral

Restrained grayscale theme for invoices, proposals, and reports where brand color should be quiet.

| Token | Value |
|---|---|
| `primary` | `#424242` |
| `secondary` | `#757575` |
| `danger` | `#B71C1C` |
| `success` | `#1B5E20` |
| `warning` | `#E65100` |
| `info` | `#0D47A1` |
| `light` | `#FAFAFA` |
| `dark` | `#212121` |
| `muted` | `#9E9E9E` |
| `table_header_bg` | `#EEEEEE` |

#### Dark

Dark-token theme for presentation/dashboard-style accents. In v1, page background remains white, so the dark theme mainly affects text, headers, tables, and component colors.

| Token | Value |
|---|---|
| `primary` | `#80CBC4` |
| `secondary` | `#4DB6AC` |
| `danger` | `#EF5350` |
| `success` | `#66BB6A` |
| `warning` | `#FFA726` |
| `info` | `#42A5F5` |
| `light` | `#37474F` |
| `dark` | `#ECEFF1` |
| `muted` | `#90A4AE` |
| `table_header_bg` | `#37474F` |

### Tone Tints

Callouts, summary boxes, and metric deltas use `tone_tint()` to create soft background fills from a semantic tone. The visual pattern is: tinted background, selected tone border, dark body text.

### Chart Palette

Charts use the selected tone first when provided, then a fallback palette:

`#7CB518`, `#1565C0`, `#E65100`, `#C62828`, `#2E7D32`, `#555555`, `#9C27B0`, `#00838F`

## Typography

### Font Families

The built-in themes use:

- Body: `DejaVuSans`
- Bold: `DejaVuSans-Bold`
- Mono: `DejaVuSansMono`

The renderer registers Unicode fonts on import, which supports rupee symbols and broader report text better than base Helvetica.

### Type Scale

| Token | Size | Leading | Weight | Current Use |
|---|---:|---:|---|---|
| Document title | 22pt | 27pt | Bold | Main `title` block heading. |
| Section header | 14pt | 18pt | Bold | Numbered section headers. |
| Card/block title large | 12pt | Auto | Bold | KPI grid, insight list, comparison card, timeline, milestone list. |
| Card/block title medium | 11pt | Auto | Bold | Tables, charts, status/risk tables. |
| Lead paragraph | 12pt | 18pt | Regular | Paragraph style `lead`. |
| Body paragraph | 10pt | 14pt | Regular | Paragraph, rich text, insight text, card bodies. |
| Table text | 9pt | 14pt | Regular/Bold | Table headers and cells. |
| Small text | 9pt | 12.6pt | Regular | Paragraph style `small`, metadata labels. |
| Caption | 8pt | 11.2pt | Regular | Paragraph style `caption`, KPI labels/subtext, badges. |
| Header/footer | 8pt | Auto | Regular/Bold | Page header/footer metadata. |

### Typography Principles

- PDF density is high. Body copy defaults to 10pt and tables default to 9pt.
- Bold is used for hierarchy more often than size increases.
- Section and title hierarchy is simple: 22pt title, 14pt section, 11-12pt block title.
- Inline rich text supports bold and semantic-tone emphasis, especially `bold_danger`, `bold_success`, and `bold_warning`.

## Layout

### Page System

Supported page sizes are `A4`, `LETTER`, `LEGAL`, and `A3`, with portrait or landscape orientation.

| Template | Margins | Header | Footer | Section Spacing | Intended Density |
|---|---|---|---|---:|---|
| `analytics_report_v1` | 1.5cm left/right, 2.2cm top, 2.0cm bottom | Default | Page number | 18pt | Full-featured analytics reports. |
| `business_report_v1` | 2.0cm left/right, 2.5cm top, 2.0cm bottom | Branded | Page number | 20pt | Professional structured reports. |
| `compact_report_v1` | 1.0cm left/right, 1.2cm top, 1.0cm bottom | Compact | Page number | 10pt | Dense, data-heavy reports. |
| `invoice_v1` | 1.5cm all sides | Minimal | No page number | 12pt | Compact financial documents. |
| `proposal_v1` | 2.0cm left/right, 2.5cm top, 2.0cm bottom | Hero | Page number | 22pt | Sales/pitch documents. |

Header variants are named in templates, but current renderer behavior draws the same header structure for all variants.

### Header And Footer Chrome

The page header uses:

- A full-width top brand band using `primary`.
- Bold 8pt metadata text.
- `muted` text color.
- Left entity name and right report period.
- 0.8pt neutral divider line.

The page footer uses:

- 0.5pt neutral separator line.
- 8pt `muted` text.
- Centered page number when enabled.
- Right-aligned `powered_by` metadata when provided.

### Spacing

The active spacing scale is implicit, not centralized:

| Spacing | Use |
|---:|---|
| 2pt | Paragraph `spaceBefore`, title metadata gap. |
| 4pt | Image title gap, summary/metric top spacer, compact table vertical padding. |
| 6pt | Table title gap, callout top spacer, divider vertical gap. |
| 8pt | Common block bottom spacer, card padding, table horizontal padding, KPI card padding. |
| 10pt | Section header `spaceBefore`, metric/summary vertical padding. |
| 12pt | Title block separator breathing room. |
| 14pt | Callout/summary/metric horizontal padding. |
| 18-22pt | Template section spacing. |

## Components

### Title Block

Document-level identity block with optional entity, title, subtitle, and right-aligned note.

- Entity: 9pt bold, `muted`.
- Main title: 22pt bold, 27pt leading, `dark`.
- Subtitle/right text: 9-11pt, `muted`.
- Bottom rule: 3pt `primary`, full content width.
- Bottom spacing: 8pt above and 14pt below the rule.

### Section Header

Numbered report section header.

- Top spacer from template `section_spacing`.
- Text: 14pt bold, 18pt leading, `dark`.
- Underline: 0.5pt `primary`.
- Bottom spacer: 8pt.

### Paragraph

Body text block with named styles: `body`, `bold`, `caption`, `small`, and `lead`.

- Default: 10pt, 14pt leading, `dark`.
- Lead: 12pt, 18pt leading, 10pt bottom gap.
- Caption: 8pt, 11.2pt leading, 4pt bottom gap.

### Rich Text

Single paragraph made from styled runs.

- Base: 10pt, 14pt leading, `dark`.
- Supports normal, bold, italic, bold italic, and semantic bold states.
- Semantic tone runs resolve through the active theme.

### KPI Grid

Grid of compact KPI cards rendered as a table.

- Title: 12pt bold.
- Card background: `light`.
- Border: 0.5pt muted hairline.
- Accent: 3pt per-card semantic tone line.
- Background: per-card semantic tone tint.
- Padding: 8pt all sides.
- Label/subtext: 8pt.
- Value: 14pt bold.
- Bottom spacer: 8pt.

Impact: cards now scan as separate semantic metrics instead of one large bordered table.

### Callout

Tone-coded message panel.

- Background: `tone_tint(tone)`.
- Left rule: selected tone, width from `theme.callout_border_width`.
- Border: 0.5pt selected tone.
- Padding: 14pt left, 8pt right, 6pt top/bottom.
- Title: inline 10pt bold.
- Body: 9pt, 13pt leading.

### Summary Box

Executive summary panel.

- Background: tone tint.
- Border: 0.7pt muted hairline.
- Accent: 3pt selected tone line.
- Padding: 14pt horizontal, 10pt vertical.
- Title: 11pt bold.
- Body: 9pt, 13pt leading.

### Metric Delta

Single metric card with label, value, delta, and subtitle.

- Background: tone tint.
- Border: 0.7pt muted hairline.
- Accent: 3pt selected tone line.
- Padding: 14pt horizontal, 10pt vertical.
- Label/subtitle: 9pt/8pt `muted`.
- Value: 20pt bold, reduced to 16pt for long values.
- Delta: 10pt, optionally tone-colored.

### Tables

The base table system appears in `table`, `matrix_table`, `status_table`, `risk_register`, and `recommendations`.

- Titles: 11pt or 12pt bold.
- Headers: 9pt bold.
- Cells: 9pt, 14pt leading.
- Header background: high-contrast `dark`.
- Header text: white.
- Grid/borders: 0.5pt muted hairline.
- Padding: 6pt horizontal, 4pt vertical.
- Striped rows use white and `light` by default; `style: plain` disables striping.
- Header rows repeat on multi-page tables for table-like components.

Impact: tables look closer to professional reports because data has structure without heavy brand-colored boxes around every cell.

### Comparison Card

Two side-by-side metric cards.

- Background: `light`.
- Border: 0.7pt muted hairline.
- Accent: 3pt `primary` line on the left.
- Center divider: 0.5pt muted hairline.
- Rounded corners: 4pt.
- Padding: 10pt all sides.
- Label/delta: 9pt.
- Value: 16pt bold.

Impact: comparison cards now align with the KPI/summary card language and avoid heavy outlines.

### Timeline

Vertical event list using a narrow marker column and content column.

- Title: 12pt bold.
- Body: 9pt, 13pt leading.
- Dot marker: 14pt.
- Row padding: 4pt vertical, 4-8pt horizontal.
- Separator lines use muted/theme tones.

### Milestone List

Structured list of milestones with status/date/content.

- Title: 12pt bold.
- Body: 9pt, 13pt leading.
- Status/date labels: 8pt.
- Row padding: 6pt.
- Stripe background uses `light`.

### Insight List

Numbered narrative insight list.

- Title: 12pt bold.
- Item text: 10pt, 14pt leading.
- Item spacing: 6pt before/after.
- Item heading is inline bold with numeric prefix.

### Badge

Small inline label.

- Background: selected semantic tone.
- Text: white, 8pt bold.
- Padding: 8pt horizontal, 3pt vertical.
- Width: constrained to 30% of available content width.
- Alignment: centered.

Current polish issue: long labels may clip because the badge has a fixed width fraction.

### Divider

Simple horizontal separator.

- Top/bottom spacer: 6pt.
- Tone defaults to `primary`.
- Thickness supplied by block or default renderer value.

### Image

Local image block with optional title.

- Title: 10pt bold, `dark`, 4pt gap.
- Default width: 80% content width.
- Default height: 50% of width.
- Alignment defaults to center.
- Relative paths are validated under the configured asset root.

### Chart

Matplotlib-backed image chart.

- Title: 11pt bold, `dark`, 6pt gap.
- Rendered PNG: 6.3in x 3.15in at 150 DPI before PDF placement.
- PDF placement: 90% available width, height = 50% of placed width.
- Chart title inside matplotlib is 11pt bold.
- Axes hide top/right spines and use 9pt tick labels.

### Two Column Layout

Composition primitive for side-by-side blocks.

- Left/right widths default to 50/50.
- Table-based layout.
- Gutter: 16pt total through right padding on left cell and left padding on right cell.
- Cell padding otherwise zero.

## Templates

### Analytics Report

Default full-featured report template. Best fit for KPI-heavy reports with charts, tables, callouts, and insight sections.

### Business Report

More editorial than analytics, with wider margins and more section spacing. Good for narrative reports and professional summaries.

### Compact Report

Dense layout with small margins and reduced section spacing. Best for data-heavy output where page count matters.

### Invoice

Restricted block set: `title`, `section_header`, `paragraph`, `table`, `spacer`, `divider`, and `badge`. Uses no page number by default.

### Proposal

Sales/pitch template with the roomiest section spacing. The `hero` header variant exists as a template name but is not visually distinct in the current renderer.

## Extension Model

The design system is intentionally extensible:

- New themes are plain `Theme` dataclass instances registered with `register_theme()`.
- New templates are plain `Template` dataclass instances registered with `register_template()`.
- New blocks subclass `BaseBlock`, set `block_type`, and register with the block registry.
- JSON should stay semantic. Agents and callers should use tones, template names, and block types rather than raw ReportLab code.

## Current Polish Opportunities

- Centralize remaining spacing and type tokens. Sizes and spacing are still repeated inside several block renderers.
- Make template header variants real. `default`, `branded`, `compact`, `minimal`, and `hero` are named but still render through one header/footer implementation.
- Define surface tokens. `white`, `light`, `table_header_bg`, and tone tints are used as surfaces, but there is no explicit surface scale.
- Clarify dark theme behavior. Dark theme tokens imply dark UI, but the actual page background remains white in v1.
- Add border/radius tokens to the theme. Most cards still hardcode 4pt rounded corners and some border widths.
- Normalize block title typography. Similar blocks use 10pt, 11pt, and 12pt titles without a shared naming system.
- Improve badge sizing. Current badge width can clip long labels.
- Decide chart visual language. Matplotlib charts use a fallback palette that is broader than the three built-in themes.

## Source Files

Primary implementation sources:

- `pdf-generator.md`
- `reportlab_json_renderer/themes/base.py`
- `reportlab_json_renderer/themes/green.py`
- `reportlab_json_renderer/themes/neutral.py`
- `reportlab_json_renderer/themes/dark.py`
- `reportlab_json_renderer/templates/base.py`
- `reportlab_json_renderer/templates/*.py`
- `reportlab_json_renderer/renderer.py`
- `reportlab_json_renderer/blocks/*.py`
- `reportlab_json_renderer/utils/charts.py`
