"""Theme registry — lookup and registration of named themes.

The registry ships with three built-in themes and exposes a simple API for
user-defined themes.
"""

from __future__ import annotations

from reportlab_json_renderer.themes.base import Theme
from reportlab_json_renderer.utils.errors import ThemeError

# Lazily populated on first access so that importing this module
# does not trigger heavy imports (matplotlib, reportlab, etc.) at
# module level.
_REGISTRY: dict[str, Theme] | None = None


def _ensure_builtins() -> dict[str, Theme]:
    """Populate the registry with built-in themes (once)."""
    global _REGISTRY
    if _REGISTRY is not None:
        return _REGISTRY

    from reportlab_json_renderer.themes.dark import DARK
    from reportlab_json_renderer.themes.green import GREEN_THEME
    from reportlab_json_renderer.themes.neutral import NEUTRAL

    _REGISTRY = {
        "green": GREEN_THEME,
        "neutral": NEUTRAL,
        "dark": DARK,
    }
    return _REGISTRY


def get_theme(name: str) -> Theme:
    """Look up a theme by name.

    Args:
        name: Theme identifier (e.g. ``"green"``).

    Returns:
        The matching :class:`Theme`.

    Raises:
        ThemeError: If no theme with that name is registered.
    """
    registry = _ensure_builtins()
    if name not in registry:
        available = ", ".join(sorted(registry))
        raise ThemeError(f"Unknown theme {name!r}. Available themes: {available}")
    return registry[name]


def register_theme(theme: Theme, *, overwrite: bool = False) -> None:
    """Register a custom theme at runtime.

    Args:
        theme: The :class:`Theme` instance to register.
        overwrite: Allow overwriting an existing theme with the same name.

    Raises:
        ValueError: If a theme with the same name already exists and
            *overwrite* is ``False``.
    """
    registry = _ensure_builtins()
    if theme.name in registry and not overwrite:
        raise ValueError(
            f"Theme {theme.name!r} already registered. " f"Use overwrite=True to replace it."
        )
    registry[theme.name] = theme


def list_themes() -> list[str]:
    """Return sorted list of all registered theme names."""
    registry = _ensure_builtins()
    return sorted(registry)
