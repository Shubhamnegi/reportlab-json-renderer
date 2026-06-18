"""Unit conversion helpers for PDF layout.

All internal layout uses ReportLab points (1 pt = 1/72 inch).
These helpers convert common units to points so block renderers
can accept centimetre or millimetre values from the JSON spec.
"""

from __future__ import annotations

# Conversion constants — points per unit.
_PT_PER_CM: float = 28.3464567
_PT_PER_MM: float = 2.83464567
_PT_PER_INCH: float = 72.0


def cm_to_pt(cm: float) -> float:
    """Convert centimetres to ReportLab points.

    Args:
        cm: Value in centimetres.

    Returns:
        Equivalent value in points.
    """
    return cm * _PT_PER_CM


def mm_to_pt(mm: float) -> float:
    """Convert millimetres to ReportLab points.

    Args:
        mm: Value in millimetres.

    Returns:
        Equivalent value in points.
    """
    return mm * _PT_PER_MM


def inch_to_pt(inch: float) -> float:
    """Convert inches to ReportLab points.

    Args:
        inch: Value in inches.

    Returns:
        Equivalent value in points.
    """
    return inch * _PT_PER_INCH


def pt_to_cm(pt: float) -> float:
    """Convert ReportLab points to centimetres.

    Args:
        pt: Value in points.

    Returns:
        Equivalent value in centimetres.
    """
    return pt / _PT_PER_CM


def pt_to_mm(pt: float) -> float:
    """Convert ReportLab points to millimetres.

    Args:
        pt: Value in points.

    Returns:
        Equivalent value in millimetres.
    """
    return pt / _PT_PER_MM


__all__ = [
    "cm_to_pt",
    "inch_to_pt",
    "mm_to_pt",
    "pt_to_cm",
    "pt_to_mm",
]
