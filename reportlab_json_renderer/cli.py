"""Command-line interface for reportlab-json-renderer.

Usage:
    pdf-renderer render --input report.json --output report.pdf
    pdf-renderer validate --input report.json
    pdf-renderer schema [--output schema.json]
    pdf-renderer templates
    pdf-renderer blocks
    pdf-renderer sample [--output sample.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from reportlab_json_renderer.renderer import build_pdf
from reportlab_json_renderer.schema.validators import (
    generate_schema_json,
    validate_spec,
)
from reportlab_json_renderer.utils.errors import ValidationError


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser.

    Returns:
        Configured ``ArgumentParser`` with sub-commands.
    """
    parser = argparse.ArgumentParser(
        prog="pdf-renderer",
        description="Generate PDFs from validated JSON specifications.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- render ---
    render_cmd = subparsers.add_parser(
        "render",
        help="Render a JSON spec into a PDF file.",
    )
    render_cmd.add_argument(
        "--input", "-i",
        required=True,
        type=Path,
        help="Path to the input JSON file.",
    )
    render_cmd.add_argument(
        "--output", "-o",
        required=True,
        type=Path,
        help="Path for the generated PDF.",
    )
    render_cmd.add_argument(
        "--pretty",
        action="store_true",
        default=False,
        help="Pretty-print the result JSON to stdout.",
    )

    # --- validate ---
    validate_cmd = subparsers.add_parser(
        "validate",
        help="Validate a JSON spec without rendering.",
    )
    validate_cmd.add_argument(
        "--input", "-i",
        required=True,
        type=Path,
        help="Path to the input JSON file.",
    )
    validate_cmd.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit non-zero on warnings as well as errors.",
    )

    # --- schema ---
    schema_cmd = subparsers.add_parser(
        "schema",
        help="Print the JSON Schema for the report spec.",
    )
    schema_cmd.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Write schema to a file instead of stdout.",
    )

    # --- templates ---
    subparsers.add_parser(
        "templates",
        help="List available templates.",
    )

    # --- blocks ---
    subparsers.add_parser(
        "blocks",
        help="List registered block types.",
    )

    # --- sample ---
    sample_cmd = subparsers.add_parser(
        "sample",
        help="Generate a minimal sample JSON spec.",
    )
    sample_cmd.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Write sample JSON to a file instead of stdout.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the CLI.

    Args:
        argv: Command-line arguments. Defaults to ``sys.argv[1:]``.

    Returns:
        Exit code: 0 for success, 1 for errors.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    dispatch = {
        "render": _cmd_render,
        "validate": _cmd_validate,
        "schema": _cmd_schema,
        "templates": _cmd_templates,
        "blocks": _cmd_blocks,
        "sample": _cmd_sample,
    }
    handler = dispatch.get(args.command)
    if handler is None:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1
    try:
        return handler(args)
    except _CliError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Sub-command handlers
# ---------------------------------------------------------------------------


class _CliError(Exception):
    """Internal error raised by CLI helpers to signal user-facing failures."""


def _read_json(path: Path) -> dict[str, object] | list[object]:
    """Read and parse a JSON file.

    Args:
        path: Path to the JSON file.

    Returns:
        Parsed JSON data.

    Raises:
        _CliError: On file or JSON errors.
    """
    if not path.exists():
        raise _CliError(f"file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise _CliError(f"invalid JSON in {path}: {exc}") from exc


def _cmd_render(args: argparse.Namespace) -> int:
    """Handle the ``render`` sub-command.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code.
    """
    spec = _read_json(args.input)
    if not isinstance(spec, dict):
        print("Error: top-level JSON must be an object.", file=sys.stderr)
        return 1

    try:
        result = build_pdf(
            spec,
            output_path=str(args.output),
            asset_root=args.input.parent,
        )
    except ValidationError as exc:
        print(f"Validation failed:\n{exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Render failed: {exc}", file=sys.stderr)
        return 1

    if result.get("success"):
        pages = result.get("pages", "?")
        out_path = result.get("path", str(args.output))
        print(f"PDF written: {out_path} ({pages} page{'s' if pages != 1 else ''})")
        return 0

    print("Render did not succeed.", file=sys.stderr)
    if result.get("warnings"):
        for w in result["warnings"]:
            print(f"  warning: {w}", file=sys.stderr)
    return 1


def _cmd_validate(args: argparse.Namespace) -> int:
    """Handle the ``validate`` sub-command.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code.
    """
    spec = _read_json(args.input)
    if not isinstance(spec, dict):
        print("Error: top-level JSON must be an object.", file=sys.stderr)
        return 1

    result = validate_spec(spec)

    output = result.to_dict()
    indent = 2
    print(json.dumps(output, indent=indent))

    if not result.valid:
        return 1

    if args.strict and result.warnings:
        return 1

    return 0


def _cmd_schema(args: argparse.Namespace) -> int:
    """Handle the ``schema`` sub-command.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code.
    """
    schema = generate_schema_json()
    schema_str = json.dumps(schema, indent=2) + "\n"

    if args.output is not None:
        args.output.write_text(schema_str, encoding="utf-8")
        print(f"Schema written: {args.output}")
    else:
        print(schema_str, end="")

    return 0


def _cmd_templates(args: argparse.Namespace) -> int:
    """Handle the ``templates`` sub-command.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code.
    """
    from reportlab_json_renderer.templates.registry import list_templates

    names = sorted(list_templates())
    if not names:
        print("No templates registered.")
    else:
        for name in names:
            print(name)
    return 0


def _cmd_blocks(args: argparse.Namespace) -> int:
    """Handle the ``blocks`` sub-command.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code.
    """
    from reportlab_json_renderer.blocks.registry import list_registered

    names = list_registered()
    if not names:
        print("No block types registered.")
    else:
        for name in names:
            print(name)
    return 0


def _cmd_sample(args: argparse.Namespace) -> int:
    """Handle the ``sample`` sub-command.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code.
    """
    sample = {
        "version": "1.0",
        "template": "analytics_report_v1",
        "theme": "green",
        "metadata": {
            "entity_name": "Demo Business",
            "report_title": "Weekly Performance Report",
            "period": "1 Jun – 7 Jun 2026",
            "generated_at": "2026-06-08",
            "powered_by": "Public PDF Renderer",
            "confidential": False,
        },
        "page": {
            "size": "A4",
            "orientation": "portrait",
            "margins": {
                "left_cm": 1.5,
                "right_cm": 1.5,
                "top_cm": 2.2,
                "bottom_cm": 2.0,
            },
        },
        "header": {"enabled": True, "variant": "default"},
        "footer": {"enabled": True, "show_page_number": True},
        "blocks": [
            {
                "type": "title",
                "entity": "Demo Business",
                "title": "Weekly Performance",
                "subtitle": "1 Jun – 7 Jun 2026",
            },
            {
                "type": "kpi_grid",
                "columns": 3,
                "items": [
                    {"label": "Orders", "value": "1,234", "tone": "success"},
                    {"label": "Revenue", "value": "₹5,67,890", "tone": "primary"},
                    {"label": "Avg Ticket", "value": "₹460", "tone": "info"},
                ],
            },
            {
                "type": "section_header",
                "number": "1",
                "title": "Key Insights",
            },
            {
                "type": "paragraph",
                "text": "This is a sample report generated by pdf-renderer.",
            },
        ],
    }
    sample_str = json.dumps(sample, indent=2) + "\n"

    if args.output is not None:
        args.output.write_text(sample_str, encoding="utf-8")
        print(f"Sample written: {args.output}")
    else:
        print(sample_str, end="")

    return 0


if __name__ == "__main__":
    sys.exit(main())
