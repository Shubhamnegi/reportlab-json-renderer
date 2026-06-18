"""Abstract base class for block renderers.

Every block type (title, paragraph, table, …) must subclass
:class:`BaseBlock` and implement :meth:`render`.

Block renderers receive the parsed block data, the active theme, and
the active template.  They return a list of ReportLab ``Flowable``
objects that the PDF builder assembles into the document.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from reportlab.platypus import Flowable


class BaseBlock(ABC):
    """Abstract base for all block renderers.

    Subclasses must set ``block_type`` as a class attribute and
    implement :meth:`render`.

    Class Attributes:
        block_type: The JSON ``"type"`` value this renderer handles.
    """

    block_type: str

    @abstractmethod
    def render(
        self,
        block: dict[str, Any],
        *,
        theme: Any,
        template: Any,
        available_width: float,
    ) -> list[Flowable]:
        """Render a single block to ReportLab flowables.

        Args:
            block: The parsed block dictionary from the JSON spec.
            theme: The active :class:`Theme` instance.
            template: The active :class:`Template` instance.
            available_width: Usable width in points (page width minus margins).

        Returns:
            List of ReportLab :class:`Flowable` objects.
        """

    def validate(self, block: dict[str, Any]) -> list[str]:
        """Optional pre-render validation.

        Args:
            block: The raw block dictionary.

        Returns:
            List of warning strings. Empty if valid.
        """
        return []
