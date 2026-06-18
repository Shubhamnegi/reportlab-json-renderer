"""Base template class for the PDF renderer.

A template defines report-level defaults: page size, margins, header/footer
configuration, section spacing, and allowed block types.  Templates are
resolved by name from the registry and merged with per-spec overrides.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PageSpec:
    """Page-level settings that a template defines.

    Attributes:
        size: Paper size identifier (e.g. ``"A4"``).
        orientation: ``"portrait"`` or ``"landscape"``.
        margins: Dict with ``left_cm``, ``right_cm``, ``top_cm``, ``bottom_cm``.
    """

    size: str = "A4"
    orientation: str = "portrait"
    margins: dict[str, float] = field(
        default_factory=lambda: {
            "left_cm": 1.5,
            "right_cm": 1.5,
            "top_cm": 2.2,
            "bottom_cm": 2.0,
        }
    )


@dataclass(frozen=True)
class Template:
    """Immutable template definition.

    Attributes:
        name: Machine-readable identifier (e.g. ``"analytics_report_v1"``).
        description: Human-readable description.
        page: Default page configuration.
        header_enabled: Whether to render a page header by default.
        header_variant: Default header style variant.
        footer_enabled: Whether to render a page footer by default.
        footer_show_page_number: Whether page numbers appear in the footer.
        section_spacing: Vertical space after section headers (pt).
        allowed_blocks: Set of block type names allowed by this template.
            An empty set means all blocks are allowed.
    """

    name: str
    description: str = ""
    page: PageSpec = field(default_factory=PageSpec)
    header_enabled: bool = True
    header_variant: str = "default"
    footer_enabled: bool = True
    footer_show_page_number: bool = True
    section_spacing: float = 18.0
    allowed_blocks: set[str] = field(default_factory=set)

    def merge_spec(self, spec_page: dict[str, Any] | None) -> PageSpec:
        """Merge a per-spec page config on top of this template's defaults.

        Args:
            spec_page: ``"page"`` dict from the JSON spec, or ``None``.

        Returns:
            Merged :class:`PageSpec`.
        """
        if spec_page is None:
            return self.page

        margins = {**self.page.margins}
        if "margins" in spec_page and isinstance(spec_page["margins"], dict):
            margins.update(spec_page["margins"])

        return PageSpec(
            size=spec_page.get("size", self.page.size),
            orientation=spec_page.get("orientation", self.page.orientation),
            margins=margins,
        )

    def is_block_allowed(self, block_type: str) -> bool:
        """Check whether *block_type* is permitted by this template.

        If ``allowed_blocks`` is empty, all block types are permitted.

        Args:
            block_type: Block type string (e.g. ``"title"``).

        Returns:
            ``True`` if the block is allowed.
        """
        if not self.allowed_blocks:
            return True
        return block_type in self.allowed_blocks


def build_template(
    name: str,
    *,
    description: str = "",
    page: PageSpec | None = None,
    header_enabled: bool = True,
    header_variant: str = "default",
    footer_enabled: bool = True,
    footer_show_page_number: bool = True,
    section_spacing: float = 18.0,
    allowed_blocks: set[str] | None = None,
) -> Template:
    """Convenience factory for building a :class:`Template`.

    Args:
        name: Template identifier.
        description: Human-readable description.
        page: Default page settings.
        header_enabled: Enable header rendering.
        header_variant: Header style variant.
        footer_enabled: Enable footer rendering.
        footer_show_page_number: Show page numbers in footer.
        section_spacing: Space after section headers (pt).
        allowed_blocks: Restrict to these block types (empty = all).

    Returns:
        New :class:`Template` instance.
    """
    return Template(
        name=name,
        description=description,
        page=page or PageSpec(),
        header_enabled=header_enabled,
        header_variant=header_variant,
        footer_enabled=footer_enabled,
        footer_show_page_number=footer_show_page_number,
        section_spacing=section_spacing,
        allowed_blocks=allowed_blocks or set(),
    )
