"""Tests for the theme system.

Covers:
  - Theme base class (resolve_tone, hex_to_rgb, merge)
  - All built-in themes (limetray_green, neutral, dark)
  - Theme registry (get_theme, register_theme, list_themes)
  - Missing / unknown theme errors
"""

from __future__ import annotations

import pytest

from reportlab_json_renderer.themes import (
    get_theme,
    list_themes,
    register_theme,
)
from reportlab_json_renderer.themes.base import (
    DEFAULT_TONES,
    build_theme,
)
from reportlab_json_renderer.utils.errors import ThemeError

_TEST_TONES = {
    "primary": "#FF0000", "danger": "#00FF00", "success": "#0000FF",
    "warning": "#AAAA00", "secondary": "#555555", "info": "#005555",
    "light": "#EEE", "dark": "#111", "muted": "#999999",
}

# ── Theme Base Class ─────────────────────────────────────────────────


class TestThemeBase:
    def test_resolve_known_tone(self) -> None:
        theme = build_theme("t", tones=dict(_TEST_TONES))
        assert theme.resolve_tone("primary") == "#FF0000"

    def test_resolve_unknown_tone_passthrough(self) -> None:
        theme = build_theme("t", tones=dict(_TEST_TONES))
        # Unknown tone falls back to the raw value.
        assert theme.resolve_tone("#ABCDEF") == "#ABCDEF"

    def test_hex_to_rgb(self) -> None:
        theme = build_theme("t", tones=dict(_TEST_TONES))
        assert theme.hex_to_rgb("#FF0000") == (255, 0, 0)
        assert theme.hex_to_rgb("#00FF00") == (0, 255, 0)
        assert theme.hex_to_rgb("#FFFFFF") == (255, 255, 255)
        assert theme.hex_to_rgb("#000000") == (0, 0, 0)

    def test_merge_returns_new_theme(self) -> None:
        theme = build_theme("t", tones=dict(_TEST_TONES))
        new = theme.merge({"font_body": "Arial"})
        assert new.font_body == "Arial"
        assert new.font_bold == "Helvetica-Bold"  # unchanged

    def test_merge_raises_on_bad_key(self) -> None:
        theme = build_theme("t", tones=dict(_TEST_TONES))
        with pytest.raises(ValueError, match="Unknown theme override"):
            theme.merge({"nonexistent_field": "x"})

    def test_theme_is_frozen(self) -> None:
        theme = build_theme("t", tones=dict(_TEST_TONES))
        with pytest.raises(AttributeError):
            theme.name = "changed"  # type: ignore[misc]


# ── Build Theme ──────────────────────────────────────────────────────


class TestBuildTheme:
    def test_build_theme_success(self) -> None:
        tones = {t: "#000000" for t in DEFAULT_TONES}
        theme = build_theme("test", tones=tones)
        assert theme.name == "test"

    def test_build_theme_missing_tone(self) -> None:
        with pytest.raises(ValueError, match="missing required tones"):
            build_theme("test", tones={"primary": "#FF0000"})

    def test_custom_fonts(self) -> None:
        tones = {t: "#000000" for t in DEFAULT_TONES}
        theme = build_theme("t", tones=tones, font_body="Arial", font_bold="Arial-Bold")
        assert theme.font_body == "Arial"
        assert theme.font_bold == "Arial-Bold"


# ── Built-in Themes ──────────────────────────────────────────────────


class TestBuiltInThemes:
    def test_limetray_green_loaded(self) -> None:
        theme = get_theme("limetray_green")
        assert theme.name == "limetray_green"
        assert theme.resolve_tone("primary") == "#7CB518"

    def test_neutral_loaded(self) -> None:
        theme = get_theme("neutral")
        assert theme.name == "neutral"
        assert theme.resolve_tone("primary") == "#424242"

    def test_dark_loaded(self) -> None:
        theme = get_theme("dark")
        assert theme.name == "dark"
        assert theme.resolve_tone("primary") == "#80CBC4"

    def test_all_builtins_have_all_default_tones(self) -> None:
        for name in ("limetray_green", "neutral", "dark"):
            theme = get_theme(name)
            for tone in DEFAULT_TONES:
                assert tone in theme.tones, f"{name} missing tone {tone}"


# ── Theme Registry ───────────────────────────────────────────────────


class TestThemeRegistry:
    def test_list_themes(self) -> None:
        names = list_themes()
        assert "limetray_green" in names
        assert "neutral" in names
        assert "dark" in names

    def test_get_unknown_theme(self) -> None:
        with pytest.raises(ThemeError, match="Unknown theme"):
            get_theme("nonexistent_theme_xyz")

    def test_register_custom_theme(self) -> None:
        custom = build_theme(
            "custom_test_theme",
            tones={t: "#AAAAAA" for t in DEFAULT_TONES},
        )
        register_theme(custom, overwrite=True)
        assert get_theme("custom_test_theme").name == "custom_test_theme"
        # Clean up.
        register_theme(custom, overwrite=True)  # prevent leak

    def test_register_duplicate_without_overwrite(self) -> None:
        custom = build_theme(
            "dup_test_theme",
            tones={t: "#AAAAAA" for t in DEFAULT_TONES},
        )
        register_theme(custom, overwrite=True)
        with pytest.raises(ValueError, match="already registered"):
            register_theme(custom, overwrite=False)
        # Clean up.
        from reportlab_json_renderer.themes.registry import _REGISTRY
        if _REGISTRY is not None:
            _REGISTRY.pop("dup_test_theme", None)
