# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-06-19

### Added

#### Core
- JSON-driven PDF generation over ReportLab with strict schema validation.
- `render_pdf` Python API and `pdf-renderer` CLI (`render`, `validate`, `schema`, `templates`).
- Pydantic-based schema validation with `extra="forbid"` and version compatibility checks.
- Validation warnings propagated into render results.

#### Block Renderers (19 types)
- `title` — report title with entity, subtitle, and right-aligned text.
- `section_header` — numbered or unnumbered section headings.
- `paragraph` — body, bold, and caption styles with markup escaping.
- `rich_text` — multi-run inline formatting with tone colours.
- `kpi_grid` — key performance indicator cards in a responsive grid.
- `callout` — single callout box with tone-based styling.
- `callout_group` — grouped callouts with optional title.
- `table` — column-keyed data table with striped and plain styles.
- `matrix_table` — row/column matrix for comparison tables.
- `insight_list` — titled insight items with body text.
- `recommendations` — action items with priority, owner, and impact.
- `summary_box` — highlighted summary with tone-based border.
- `image` — local image embedding with path traversal protection.
- `chart` — bar, pie, and grouped-bar charts via matplotlib.
- `two_column` — side-by-side layout with configurable widths.
- `spacer` — vertical spacing.
- `page_break` — explicit page break.
- `divider` — horizontal rule with tone and thickness.
- `badge` — inline label badge with tone colour.

#### Templates
- `analytics_report_v1` — default analytics report layout.
- `business_report_v1` — business-focused report layout.
- `compact_report_v1` — condensed single-page layout.
- `invoice_v1` — invoice document layout.
- `proposal_v1` — multi-page proposal layout.

#### Themes
- `green` — green-accented professional theme.
- `neutral` — grey neutral theme.
- `dark` — dark background theme.

#### Safety And Validation
- Strict schema inputs with `extra="forbid"` where appropriate.
- Schema version compatibility enforcement.
- Image path traversal protection and safe-path validation.
- Resource limits for large payloads, images, and oversized tables/charts.
- Temporary file cleanup for base64 image handling.
- User-controlled text escaping before ReportLab markup rendering.
- Fail-closed block rendering by default.
- Template `allowed_blocks` enforcement.

#### Determinism
- Reduced non-deterministic PDF output.
- Parsed-PDF verification with pypdf (page count, text extraction).
- Idempotent rendering (same spec → identical bytes).

#### Testing
- Comprehensive unit tests for all 19 block renderers.
- Golden PDF tests for all 6 templates.
- Edge-case fixtures (empty blocks, minimal fields, all block types, page sizes).
- Theme coverage tests (green, neutral, dark).
- Schema validation tests.
- CLI tests.
- Chart, colour, image, text, and unit utility tests.

#### Packaging
- MIT license.
- PyPI-ready metadata with classifiers and project URLs.
- Hatchling build system.
- Ruff linting and formatting.
- Pre-commit hook configuration.
- pytest with coverage (90% threshold).

## [Unreleased]

## [0.1.1] — 2026-06-20

### Fixed
- **CRITICAL**: Fixed invalid `LINEBEFORETABLE` ReportLab command in `kpi_grid.py` and `callout.py` — replaced with correct `LINEBEFORE` command to enable left-border accent on KPI cards and callouts.
- Fixed 25 ruff lint errors including unused imports, unsorted `__all__`, and unused variables.

### Changed
- **Typography & Spacing**: Increased section header font size from 13 to 14pt, added `keepWithNext=True` for better paragraph flow, increased spacing before section headers.
- **Title Block**: Increased horizontal line width from 1.5 to 2.0, increased spacing after title.
- **Paragraph Styles**: Added `spaceBefore=2` for better vertical rhythm, increased `lead` style spacing and leading, adjusted `caption` style spacing.
- **Rich Text**: Added `spaceBefore=2` for consistent spacing.
- **KPI Grid**: Added rounded corners, increased padding from 6 to 8, added left-border accent via `LINEBEFORE`.
- **Callout**: Increased left padding from 10 to 14, added rounded corners, added subtle border, increased spacers.
- **Summary Box**: Added rounded corners, increased padding.
- **Badge**: Rewritten from `Paragraph` to `Table` wrapper for rounded corners support with horizontal padding.
- **Two-Column Layout**: Fixed asymmetric padding (8pt gap between columns), increased empty column spacer from 12 to 20.
- **Header/Footer**: Added subtle header background, added footer separator line, increased footer page number font from 7pt to 8pt, increased footer text offset.
- **Theme**: Darkened green theme table header background from `#E8F5E9` to `#C8E6C9`.
- **Insight List**: Increased `spaceBefore/spaceAfter` from 4 to 6.
- **Divider**: Increased spacer from 4 to 6 on both sides.
- **Tables**: Normalized column widths to sum to `available_width`, added `keepWithNext` to titles, increased cell leading from 12 to 14, replaced manual striping with `ROWBACKGROUNDS`, added `REPEATROWS=1` for multi-page tables.