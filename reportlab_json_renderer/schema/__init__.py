"""Schema definitions and validation for the JSON report specification."""

from reportlab_json_renderer.schema.base import ReportSpec
from reportlab_json_renderer.schema.validators import (
    ValidationResult,
    generate_schema_file,
    generate_schema_json,
    validate_spec,
    validate_spec_or_raise,
)

__all__ = [
    "ReportSpec",
    "ValidationResult",
    "generate_schema_file",
    "generate_schema_json",
    "validate_spec",
    "validate_spec_or_raise",
]
