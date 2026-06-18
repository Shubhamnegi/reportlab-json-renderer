"""Tests for utils/colors.py."""

from __future__ import annotations

import pytest

from reportlab_json_renderer.utils.colors import (
    is_valid_tone,
    resolve_tone,
    tone_to_color,
)
from reportlab_json_renderer.utils.errors import ThemeError


class TestResolveTone:
    def test_default_palette_primary(self) -> None:
        assert resolve_tone("primary") == "#7CB518"

    def test_default_palette_danger(self) -> None:
        assert resolve_tone("danger") == "#C62828"

    def test_all_default_tones(self) -> None:
        tones = ["primary", "danger", "success", "warning", "info", "dark", "muted", "light_bg"]
        for tone in tones:
            result = resolve_tone(tone)
            assert result.startswith("#"), f"{tone} should return a hex string"
            assert len(result) == 7, f"{tone} should be #RRGGBB format"

    def test_custom_palette_overrides(self) -> None:
        palette = {"primary": "#FF0000"}
        assert resolve_tone("primary", palette) == "#FF0000"

    def test_custom_palette_adds_new_tone(self) -> None:
        palette = {"brand": "#AABBCC"}
        assert resolve_tone("brand", palette) == "#AABBCC"

    def test_default_palette_not_lost_with_custom(self) -> None:
        palette = {"primary": "#FF0000"}
        assert resolve_tone("danger", palette) == "#C62828"

    def test_unknown_tone_raises_theme_error(self) -> None:
        with pytest.raises(ThemeError, match="Unknown tone"):
            resolve_tone("nonexistent")

    def test_error_message_lists_available_tones(self) -> None:
        with pytest.raises(ThemeError, match="primary"):
            resolve_tone("nope")


class TestToneToColor:
    def test_returns_color_object(self) -> None:
        from reportlab.lib.colors import Color

        result = tone_to_color("primary")
        assert isinstance(result, Color)

    def test_colour_rgb_matches(self) -> None:
        result = tone_to_color("primary")
        # #7CB518 → R=0x7C/255, G=0xB5/255, B=0x18/255
        assert abs(result.red - 0x7C / 255) < 0.01
        assert abs(result.green - 0xB5 / 255) < 0.01
        assert abs(result.blue - 0x18 / 255) < 0.01


class TestIsValidTone:
    def test_known_tone(self) -> None:
        assert is_valid_tone("primary") is True

    def test_unknown_tone(self) -> None:
        assert is_valid_tone("nonexistent") is False

    def test_custom_palette(self) -> None:
        assert is_valid_tone("brand", {"brand": "#AABBCC"}) is True

    def test_default_tone_with_custom_palette(self) -> None:
        assert is_valid_tone("danger", {"brand": "#AABBCC"}) is True
