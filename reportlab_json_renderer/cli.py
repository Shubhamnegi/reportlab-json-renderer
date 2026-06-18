"""Command-line interface for reportlab-json-renderer.

Usage:
    pdf-renderer render --input report.json --output report.pdf
    pdf-renderer validate --input report.json
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser.

    Returns:
        Configured ``ArgumentParser`` with ``render`` and ``validate`` sub-commands.
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

    if args.command == "render":
        return _cmd_render(args)
    if args.command == "validate":
        return _cmd_validate(args)

    return 1


def _cmd_render(args: argparse.Namespace) -> int:
    """Handle the ``render`` sub-command.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code.
    """
    # Stub — will be implemented in Phase 9.
    print(
        f"[stub] render: {args.input} → {args.output}",
        file=sys.stderr,
    )
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    """Handle the ``validate`` sub-command.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code.
    """
    # Stub — will be implemented in Phase 9.
    print(
        f"[stub] validate: {args.input}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
