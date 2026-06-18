"""Validation entry point for the JSON report specification.

Public API:
  - ``validate_spec(data)`` — parse and validate, returning a ``ValidationResult``.
  - ``validate_spec_or_raise(data)`` — parse and validate, raising ``ValidationError``.
  - ``generate_schema_json()`` — export the JSON Schema as a dict.
  - ``generate_schema_file(path)`` -- write the JSON Schema to a file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from reportlab_json_renderer.schema.base import (
    SUPPORTED_CHART_TYPES,
    ReportSpec,
)
from reportlab_json_renderer.utils.errors import ValidationError


class ValidationResult:
    """Structured result from spec validation.

    Attributes:
        valid: Whether the spec passed all checks.
        parsed: The parsed ``ReportSpec`` model (``None`` if invalid).
        errors: Human-readable error messages (empty if valid).
        warnings: Non-fatal warnings.
    """

    __slots__ = ("errors", "parsed", "valid", "warnings")

    def __init__(
        self,
        valid: bool,
        parsed: ReportSpec | None = None,
        errors: list[str] | None = None,
        warnings: list[str] | None = None,
    ) -> None:
        self.valid = valid
        self.parsed = parsed
        self.errors = errors or []
        self.warnings = warnings or []

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dictionary.

        Returns:
            Dictionary with keys: valid, errors, warnings, metadata (if valid).
        """
        result: dict[str, Any] = {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }
        if self.parsed is not None:
            result["metadata"] = {
                "template": self.parsed.template,
                "theme": self.parsed.theme,
            }
        return result


def _post_validate(spec: ReportSpec) -> list[str]:
    """Run additional business-rule checks beyond Pydantic model validation.

    Args:
        spec: The already-parsed ``ReportSpec`` model.

    Returns:
        List of warning messages. Empty if everything is fine.
    """
    warnings: list[str] = []

    for idx, block in enumerate(spec.blocks):
        block_dict = block.model_dump()

        # Check chart types.
        if block_dict.get("type") == "chart":
            chart_type = block_dict.get("chart_type", "")
            if chart_type not in SUPPORTED_CHART_TYPES:
                warnings.append(
                    f"Block {idx}: chart type {chart_type!r} may not be supported. "
                    f"Known types: {', '.join(sorted(SUPPORTED_CHART_TYPES))}"
                )

        # Check table column widths sum approximately to 1.0.
        if block_dict.get("type") == "table":
            columns = block_dict.get("columns", [])
            if columns:
                total_width = sum(c.get("width", 0.2) for c in columns)
                if abs(total_width - 1.0) > 0.15:
                    warnings.append(
                        f"Block {idx}: table column widths sum to {total_width:.2f}, "
                        f"expected ~1.0"
                    )

        # Check table row keys match columns.
        if block_dict.get("type") == "table":
            columns = block_dict.get("columns", [])
            rows = block_dict.get("rows", [])
            col_keys = {c.get("key") for c in columns}
            for r_idx, row in enumerate(rows):
                extra = set(row.keys()) - col_keys
                if extra:
                    warnings.append(
                        f"Block {idx}, row {r_idx}: extra keys {extra} not in columns"
                    )

        # Check two_column widths sum approximately to 1.0.
        if block_dict.get("type") == "two_column":
            left_w = block_dict.get("left_width", 0.5)
            right_w = block_dict.get("right_width", 0.5)
            if abs(left_w + right_w - 1.0) > 0.01:
                warnings.append(
                    f"Block {idx}: two_column widths {left_w} + {right_w} != 1.0"
                )

    return warnings


def validate_spec(data: dict[str, Any]) -> ValidationResult:
    """Validate a JSON spec dictionary.

    Checks:
      - Pydantic model parsing (required fields, types, constraints).
      - Post-validation business rules (column widths, chart types, etc.).

    Args:
        data: Raw JSON spec as a Python dictionary.

    Returns:
        ``ValidationResult`` with ``valid``, ``errors``, and ``warnings``.
    """
    errors: list[str] = []

    try:
        spec = ReportSpec.model_validate(data)
    except PydanticValidationError as exc:
        for err in exc.errors():
            loc = " → ".join(str(part) for part in err.get("loc", []))
            msg = err.get("msg", "Unknown error")
            errors.append(f"{loc}: {msg}" if loc else msg)
        return ValidationResult(valid=False, errors=errors)

    warnings = _post_validate(spec)
    return ValidationResult(valid=True, parsed=spec, warnings=warnings)


def validate_spec_or_raise(data: dict[str, Any]) -> ReportSpec:
    """Validate a JSON spec, raising ``ValidationError`` on failure.

    Args:
        data: Raw JSON spec as a Python dictionary.

    Returns:
        Parsed ``ReportSpec`` model.

    Raises:
        ValidationError: If the spec is invalid.
    """
    result = validate_spec(data)
    if not result.valid:
        msg = "Spec validation failed:\n" + "\n".join(
            f"  - {e}" for e in result.errors
        )
        raise ValidationError(msg)
    return result.parsed  # type: ignore[return-value]


def generate_schema_json() -> dict[str, Any]:
    """Generate the JSON Schema dict from the Pydantic models.

    Returns:
        JSON Schema dictionary.
    """
    return ReportSpec.model_json_schema()


def generate_schema_file(path: str | Path) -> Path:
    """Write the JSON Schema to a file.

    Args:
        path: Destination file path.

    Returns:
        Resolved ``Path`` of the written file.
    """
    schema = generate_schema_json()
    p = Path(path).resolve()
    p.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    return p


__all__ = [
    "ValidationResult",
    "generate_schema_file",
    "generate_schema_json",
    "validate_spec",
    "validate_spec_or_raise",
]
