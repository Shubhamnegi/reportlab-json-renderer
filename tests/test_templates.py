"""Tests for the template system.

Covers:
  - Template base class (merge_spec, is_block_allowed)
  - All five built-in templates
  - Template registry (get_template, register_template, list_templates)
  - Unknown template errors
"""

from __future__ import annotations

import pytest

from reportlab_json_renderer.templates import (
    get_template,
    list_templates,
    register_template,
)
from reportlab_json_renderer.templates.base import PageSpec, build_template
from reportlab_json_renderer.utils.errors import TemplateError

# ── Template Base Class ──────────────────────────────────────────────


class TestTemplateBase:
    def test_merge_spec_none(self) -> None:
        tpl = build_template("t")
        merged = tpl.merge_spec(None)
        assert merged.size == "A4"
        assert merged.orientation == "portrait"

    def test_merge_spec_overrides(self) -> None:
        tpl = build_template("t")
        merged = tpl.merge_spec({"size": "A3", "orientation": "landscape"})
        assert merged.size == "A3"
        assert merged.orientation == "landscape"
        # Margins should fall back to template defaults.
        assert merged.margins["left_cm"] == 1.5

    def test_merge_spec_partial_margins(self) -> None:
        tpl = build_template("t")
        merged = tpl.merge_spec({"margins": {"left_cm": 3.0}})
        assert merged.margins["left_cm"] == 3.0
        assert merged.margins["right_cm"] == 1.5  # default preserved

    def test_is_block_allowed_empty_set(self) -> None:
        tpl = build_template("t")
        assert tpl.is_block_allowed("title") is True
        assert tpl.is_block_allowed("anything") is True

    def test_is_block_allowed_restricted(self) -> None:
        tpl = build_template("t", allowed_blocks={"title", "paragraph"})
        assert tpl.is_block_allowed("title") is True
        assert tpl.is_block_allowed("paragraph") is True
        assert tpl.is_block_allowed("chart") is False

    def test_template_is_frozen(self) -> None:
        tpl = build_template("t")
        with pytest.raises(AttributeError):
            tpl.name = "changed"  # type: ignore[misc]


# ── Built-in Templates ───────────────────────────────────────────────


class TestBuiltInTemplates:
    def test_analytics_report_v1(self) -> None:
        tpl = get_template("analytics_report_v1")
        assert tpl.name == "analytics_report_v1"
        assert tpl.page.size == "A4"
        assert tpl.footer_show_page_number is True

    def test_business_report_v1(self) -> None:
        tpl = get_template("business_report_v1")
        assert tpl.name == "business_report_v1"
        assert tpl.page.margins["left_cm"] == 2.0
        assert tpl.header_variant == "branded"

    def test_invoice_v1(self) -> None:
        tpl = get_template("invoice_v1")
        assert tpl.name == "invoice_v1"
        assert tpl.footer_show_page_number is False
        assert "table" in tpl.allowed_blocks
        assert "chart" not in tpl.allowed_blocks

    def test_proposal_v1(self) -> None:
        tpl = get_template("proposal_v1")
        assert tpl.name == "proposal_v1"
        assert tpl.header_variant == "hero"
        assert tpl.section_spacing == 22.0

    def test_compact_report_v1(self) -> None:
        tpl = get_template("compact_report_v1")
        assert tpl.name == "compact_report_v1"
        assert tpl.page.margins["left_cm"] == 1.0
        assert tpl.section_spacing == 10.0

    def test_all_templates_have_valid_page_spec(self) -> None:
        for name in list_templates():
            tpl = get_template(name)
            assert isinstance(tpl.page, PageSpec)
            assert tpl.page.size in ("A4", "A3", "letter", "legal")
            assert tpl.page.orientation in ("portrait", "landscape")


# ── Template Registry ────────────────────────────────────────────────


class TestTemplateRegistry:
    def test_list_templates(self) -> None:
        names = list_templates()
        assert "analytics_report_v1" in names
        assert len(names) >= 5

    def test_get_unknown_template(self) -> None:
        with pytest.raises(TemplateError, match="Unknown template"):
            get_template("nonexistent_template_xyz")

    def test_register_custom_template(self) -> None:
        custom = build_template("custom_test_tpl")
        register_template(custom, overwrite=True)
        assert get_template("custom_test_tpl").name == "custom_test_tpl"
        # Clean up.
        from reportlab_json_renderer.templates.registry import _REGISTRY

        if _REGISTRY is not None:
            _REGISTRY.pop("custom_test_tpl", None)

    def test_register_duplicate_without_overwrite(self) -> None:
        custom = build_template("dup_test_tpl")
        register_template(custom, overwrite=True)
        with pytest.raises(ValueError, match="already registered"):
            register_template(custom, overwrite=False)
        # Clean up.
        from reportlab_json_renderer.templates.registry import _REGISTRY

        if _REGISTRY is not None:
            _REGISTRY.pop("dup_test_tpl", None)
