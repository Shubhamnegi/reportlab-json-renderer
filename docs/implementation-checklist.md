# Implementation Checklist

Release work is now tracked in [release-readiness-checklist.md](release-readiness-checklist.md).
This document remains the implementation history for the original build-out.

> Track progress by checking off items as they are completed.  
> Source of truth: [`pdf-generator.md`](../pdf-generator.md)

---

## Phase 1 — Project Scaffolding

- [x] Create Python package structure (`reportlab_json_renderer/`)
- [x] Create `__init__.py` with public API surface (`render_pdf`)
- [x] Set up `pyproject.toml` / `setup.cfg` with dependencies (`reportlab`, `matplotlib`)
- [x] Create `tests/` directory with `conftest.py` and fixtures folder
- [x] Set up linting config (ruff or flake8)
- [x] Set up test runner config (pytest)
- [x] Set up coverage config
- [x] Create pre-commit hook (lint → test → coverage)
- [x] Set up `.gitignore` for Python projects

---

## Phase 2 — Error & Utility Foundation

- [x] `utils/errors.py` — custom exception hierarchy (`ValidationError`, `RenderError`, `ThemeError`, `TemplateError`)
- [x] `utils/units.py` — cm/mm/pt conversion helpers
- [x] `utils/colors.py` — tone-to-hex resolver (reads from theme, never raw hex from JSON)
- [x] `utils/text.py` — text truncation, sanitization, line-break helpers
- [x] `utils/images.py` — local file loader, optional HTTP/S3/base64 loader with validation
- [x] `utils/charts.py` — matplotlib chart renderers (bar, horizontal_bar, line, area, pie, donut, stacked_bar, grouped_bar)

---

## Phase 3 — Schema & Validation

- [x] `schema/base.py` — Pydantic models for root spec, metadata, page config, all block types
- [x] `schema/validators.py` — `validate_spec(json)` and `validate_spec_or_raise(json)` with structured errors
- [x] Unit tests for valid specs, missing fields, unknown block types, invalid tones (24 tests)

---

## Phase 4 — Theme System

- [x] `themes/base.py` — `Theme` class with color palette, font config, tone resolution
- [x] `themes/green.py` — default public green theme
- [x] `themes/neutral.py` — grayscale / neutral theme
- [x] `themes/dark.py` — dark background theme
- [x] `themes/registry.py` — Theme resolver: look up theme by name, register custom themes
- [x] Unit tests for tone resolution, missing theme fallback (17 tests)

---

## Phase 5 — Template System

- [x] `templates/base.py` — `Template` class (page size, margins, header/footer defaults, section spacing, allowed blocks)
- [x] `templates/analytics_report_v1.py`
- [x] `templates/business_report_v1.py`
- [x] `templates/invoice_v1.py`
- [x] `templates/proposal_v1.py`
- [x] `templates/compact_report_v1.py`
- [x] `templates/registry.py` — Template resolver: look up template by name, merge with page overrides from JSON
- [x] Unit tests for template resolution and page config merging (16 tests)

---

## Phase 6 — Block Renderer Registry

- [x] `blocks/base.py` — `BaseBlock` abstract class (`render(spec, theme, template) → list[Flowable]`)
- [x] `blocks/registry.py` — block type → renderer mapping, register, get_renderer, render_block
- [x] Unit tests for registry (11 tests)

---

## Phase 7 — Block Renderers (Individual) ✅

- [x] `blocks/title.py` — title block (entity, title, subtitle, right_text)
- [x] `blocks/section.py` — section header (number + title)
- [x] `blocks/paragraph.py` — paragraph with style variants
- [x] `blocks/rich_text.py` — inline styled runs (bold, italic, color tones)
- [x] `blocks/kpi_grid.py` — KPI cards in grid layout (columns, tone per card)
- [x] `blocks/table.py` — striped/standard table with column widths, per-cell styling
- [x] `blocks/callout.py` — colored callout box (tone, title, text)
- [x] `blocks/insight_list.py` — numbered/bulleted insight items
- [x] `blocks/recommendations.py` — priority/action/owner/impact table
- [x] `blocks/image.py` — image block (local, HTTP, S3, base64, contain/cover fit, alignment)
- [x] `blocks/chart.py` — chart block (renders via matplotlib utils, embeds as image flowable)
- [x] `blocks/layout.py` — two-column (and future multi-column) layout container
- [x] `blocks/spacer.py` — vertical spacer
- [x] `blocks/page_break.py` — explicit page break
- [x] `blocks/matrix_table.py` — matrix/comparison table (column-based, no key mapping)
- [x] `blocks/callout_group.py` — grouped callouts under a shared title
- [x] `blocks/divider.py` — horizontal line with tone and thickness
- [x] `blocks/badge.py` — small inline badge label
- [x] `blocks/summary_box.py` — executive summary card

Each block renderer must have:
- [x] Unit tests with at least one fixture JSON → flowable assertion
- [x] Edge case tests (empty data, missing optional fields)

---

## Phase 8 — PDF Builder & Core Renderer ✅

- [x] `renderer.py` — `build_pdf(spec, output_path)` pipeline:
  1. Validate JSON
  2. Normalize / preprocess
  3. Resolve template
  4. Resolve theme
  5. Iterate blocks → dispatch to registry → collect flowables
  6. Build PDF with header/footer
  7. Return result object
- [x] Header renderer (logo, title, date, powered-by)
- [x] Footer renderer (page numbers, disclaimer)
- [x] Page setup (size, orientation, margins from template + JSON overrides)
- [x] Result object: `{ success, path, bytes, pages, warnings, metadata }`
- [x] Unit tests for full render pipeline with sample JSON

---

## Phase 9 — CLI ✅

- [x] `cli.py` — `pdf-renderer render --input report.json --output report.pdf`
- [x] `pdf-renderer validate --input report.json` (validate-only mode)
- [x] `pdf-renderer schema [--output schema.json]` (export JSON Schema)
- [x] `pdf-renderer templates` (list available templates)
- [x] `pdf-renderer blocks` (list registered block types)
- [x] `pdf-renderer sample [--output sample.json]` (generate sample spec)
- [x] Argument parsing, help text, exit codes
- [x] CLI integration tests (27 test cases)

---

## Phase 10 — Testing & Quality ✅

- [x] Golden PDF / snapshot metadata tests for each template
- [x] Fixtures: one valid JSON per template type (5 templates + 1 full spec)
- [x] Fixtures: edge-case JSONs (empty blocks, minimal fields, all block types, page sizes)
- [x] Edge-case validation tests (invalid inputs, post-validation warnings)
- [x] Coverage target ≥ 90% (99.07%)
- [x] All tests pass via `pytest` (309 tests)

---

## Phase 11 — Documentation & Packaging ✅

- [x] Update `README.md` — problem, install, quick-start, API usage, CLI usage, JSON contract overview, extending with custom blocks/themes/templates
- [x] Update `AGENTS.md` if conventions change
- [x] Add `docs/json-schema.md` — human-readable JSON contract reference
- [x] Add `docs/custom-blocks.md` — guide for extending with new block types
- [x] Add `docs/custom-themes.md` — guide for creating new themes
- [x] Add `docs/custom-templates.md` — guide for creating new templates
- [ ] Package for PyPI (or internal registry) if applicable

---

## Future Blocks (Not in v1)

Tracked here for awareness. Do not implement until explicitly requested.

- [ ] `comparison_card`
- [ ] `metric_delta`
- [ ] `timeline`
- [ ] `milestone_list`
- [ ] `risk_register`
- [ ] `status_table`
- [ ] `financial_statement`
- [ ] `invoice_line_items`
- [ ] `signature_block`
- [ ] `appendix`
- [ ] `toc`
- [ ] `qr_code`
- [ ] `watermark`
- [ ] `geo_map_image`
- [ ] `heatmap_image`
- [ ] `sparkline_grid`
- [ ] `grouped_kpi_section`
- [ ] `nested_sections`
- [ ] `markdown_block`
- [ ] `raw_html_to_image`
- [ ] `external_chart_image`

---

## Decision Log

| # | Decision | Status | Notes |
|---|----------|--------|-------|
| 1 | Charting library | ✅ Done | Matplotlib (Agg backend) |
| 2 | Validation library | Pending | jsonschema or pydantic? |
| 3 | CLI framework | ✅ Done | argparse (stdlib) |
| 4 | Linting tool | ✅ Done | ruff |
| 5 | PDF snapshot testing approach | Pending | Byte-level vs metadata comparison |

---

*Last updated: 2026-06-18*
