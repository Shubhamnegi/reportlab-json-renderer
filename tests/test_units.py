"""Tests for utils/units.py."""

from __future__ import annotations

import pytest

from reportlab_json_renderer.utils.units import (
    cm_to_pt,
    inch_to_pt,
    mm_to_pt,
    pt_to_cm,
    pt_to_mm,
)


class TestCmToPt:
    def test_zero(self) -> None:
        assert cm_to_pt(0) == 0.0

    def test_one_cm(self) -> None:
        assert abs(cm_to_pt(1) - 28.3464567) < 0.001

    def test_ten_cm(self) -> None:
        assert abs(cm_to_pt(10) - 283.464567) < 0.01

    def test_negative(self) -> None:
        assert cm_to_pt(-1) < 0


class TestMmToPt:
    def test_zero(self) -> None:
        assert mm_to_pt(0) == 0.0

    def test_ten_mm(self) -> None:
        assert abs(mm_to_pt(10) - 28.3464567) < 0.001


class TestInchToPt:
    def test_one_inch(self) -> None:
        assert inch_to_pt(1) == 72.0

    def test_half_inch(self) -> None:
        assert inch_to_pt(0.5) == 36.0


class TestPtToCm:
    def test_roundtrip(self) -> None:
        original = 5.0
        assert abs(pt_to_cm(cm_to_pt(original)) - original) < 1e-6

    def test_known_value(self) -> None:
        assert abs(pt_to_cm(28.3464567) - 1.0) < 0.001


class TestPtToMm:
    def test_roundtrip(self) -> None:
        original = 50.0
        assert abs(pt_to_mm(mm_to_pt(original)) - original) < 1e-6


class TestInverseRelationship:
    """cm_to_pt and pt_to_cm must be exact inverses."""

    @pytest.mark.parametrize("value", [0.1, 1.0, 5.5, 100.0, 999.9])
    def test_cm_roundtrip(self, value: float) -> None:
        assert abs(pt_to_cm(cm_to_pt(value)) - value) < 1e-6

    @pytest.mark.parametrize("value", [0.1, 1.0, 10.0, 100.0])
    def test_mm_roundtrip(self, value: float) -> None:
        assert abs(pt_to_mm(mm_to_pt(value)) - value) < 1e-6
