"""Tests for the block renderer registry.

Covers:
  - BaseBlock interface
  - Registry: register, get_renderer, list_registered, render_block
  - Unknown block type errors
  - Double-registration prevention
"""

from __future__ import annotations

from typing import Any

import pytest
from reportlab.platypus import Flowable, Spacer

from reportlab_json_renderer.blocks.base import BaseBlock
from reportlab_json_renderer.blocks.registry import (
    _REGISTRY,
    get_renderer,
    list_registered,
    register,
    render_block,
)
from reportlab_json_renderer.utils.errors import RenderError

# ── Helpers ──────────────────────────────────────────────────────────


class _StubRenderer(BaseBlock):
    """Minimal concrete renderer for testing."""

    block_type = "stub_block"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        return [Spacer(1, 12)]

    def validate(self, block: dict[str, Any]) -> list[str]:
        warnings: list[str] = []
        if block.get("strict") is True:
            warnings.append("strict mode warning")
        return warnings


class _AnotherStubRenderer(BaseBlock):
    block_type = "another_stub"

    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        return [Spacer(1, 6)]


# ── BaseBlock ────────────────────────────────────────────────────────


class TestBaseBlock:
    def test_cannot_instantiate_without_render(self) -> None:
        """Abstract class should not be directly instantiable."""

        class Incomplete(BaseBlock):
            block_type = "incomplete"

        with pytest.raises(TypeError):
            Incomplete()

    def test_stub_renderer_is_concrete(self) -> None:
        r = _StubRenderer()
        assert r.block_type == "stub_block"

    def test_validate_returns_empty_by_default(self) -> None:
        class NoValidate(BaseBlock):
            block_type = "nov"

            def render(self, block, *, theme, template, available_width):
                return []

        r = NoValidate()
        assert r.validate({}) == []


# ── Registry: register / get ─────────────────────────────────────────


class TestRegistryRegister:
    def _cleanup(self, block_type: str) -> None:
        _REGISTRY.pop(block_type, None)

    def test_register_and_get(self) -> None:
        r = _StubRenderer()
        register(r)
        try:
            assert get_renderer("stub_block") is r
        finally:
            self._cleanup("stub_block")

    def test_double_register_raises(self) -> None:
        r1 = _StubRenderer()
        register(r1)
        try:
            with pytest.raises(ValueError, match="already registered"):
                register(_StubRenderer())
        finally:
            self._cleanup("stub_block")

    def test_get_unknown_renderer(self) -> None:
        with pytest.raises(RenderError, match="No renderer"):
            get_renderer("completely_unknown_type_xyz")


# ── Registry: list ───────────────────────────────────────────────────


class TestRegistryList:
    def _cleanup(self, block_type: str) -> None:
        _REGISTRY.pop(block_type, None)

    def test_list_includes_registered(self) -> None:
        r = _StubRenderer()
        register(r)
        try:
            assert "stub_block" in list_registered()
        finally:
            self._cleanup("stub_block")


# ── Registry: render_block ──────────────────────────────────────────


class TestRegistryRenderBlock:
    def _cleanup(self, block_type: str) -> None:
        _REGISTRY.pop(block_type, None)

    def test_render_block_returns_flowables(self) -> None:
        r = _StubRenderer()
        register(r)
        try:
            result = render_block(
                {"type": "stub_block"},
                theme=None,
                template=None,
                available_width=500,
            )
            assert len(result) == 1
            assert isinstance(result[0], Flowable)
        finally:
            self._cleanup("stub_block")

    def test_render_block_unknown_type(self) -> None:
        with pytest.raises(RenderError, match="No renderer"):
            render_block(
                {"type": "nonexistent"},
                theme=None,
                template=None,
                available_width=500,
            )

    def test_render_block_missing_type_key(self) -> None:
        with pytest.raises(RenderError, match="No renderer"):
            render_block(
                {"text": "hello"},
                theme=None,
                template=None,
                available_width=500,
            )

    def test_validate_called_before_render(self) -> None:
        r = _StubRenderer()
        register(r)
        try:
            # strict=True triggers a warning from validate()
            result = render_block(
                {"type": "stub_block", "strict": True},
                theme=None,
                template=None,
                available_width=500,
            )
            # Render still succeeds; warnings are collected (not raised).
            assert len(result) == 1
        finally:
            self._cleanup("stub_block")
