"""Custom exception hierarchy for reportlab-json-renderer.

All library exceptions inherit from ``RendererError`` so callers can
catch the base class when they want to handle every library-level fault.
"""

from __future__ import annotations


class RendererError(Exception):
    """Base exception for all renderer errors."""


class ValidationError(RendererError):
    """Raised when the JSON spec fails schema validation."""


class RenderError(RendererError):
    """Raised when a block cannot be rendered."""


class ThemeError(RendererError):
    """Raised when a theme is missing or misconfigured."""


class TemplateError(RendererError):
    """Raised when a template is missing or misconfigured."""


__all__ = [
    "RenderError",
    "RendererError",
    "TemplateError",
    "ThemeError",
    "ValidationError",
]
