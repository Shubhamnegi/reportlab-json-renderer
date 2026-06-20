#!/usr/bin/env python3
"""Generate a test PDF exercising all 7 new block components."""

import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from reportlab_json_renderer import render_pdf

SPEC = {
    "version": "1.0",
    "template": "analytics_report_v1",
    "theme": "green",
    "metadata": {
        "entity_name": "Acme Corp",
        "report_title": "New Components Demo",
        "period": "Q2 2026",
        "generated_at": "2026-06-20",
        "powered_by": "Public PDF Renderer",
        "confidential": False,
    },
    "page": {"size": "A4", "orientation": "portrait"},
    "header": {"enabled": True},
    "footer": {"enabled": True, "show_page_number": True},
    "blocks": [
        {
            "type": "title",
            "entity": "Acme Corp",
            "title": "New Components Demo Report",
            "subtitle": "Exercising all 7 newly implemented block types",
        },
        # ── comparison_card ────────────────────────────────────────
        {
            "type": "section_header",
            "number": "1",
            "title": "Comparison Card",
        },
        {
            "type": "comparison_card",
            "title": "Revenue Comparison",
            "left": {
                "label": "This Quarter",
                "value": "\u20b912.5L",
                "delta": "+8.2%",
                "tone": "success",
            },
            "right": {
                "label": "Last Quarter",
                "value": "\u20b911.6L",
                "delta": "+3.1%",
                "tone": "warning",
            },
        },
        # ── metric_delta ──────────────────────────────────────────
        {
            "type": "section_header",
            "number": "2",
            "title": "Metric Delta",
        },
        {
            "type": "metric_delta",
            "label": "Monthly Active Users",
            "value": "1,24,500",
            "delta": "+12.4%",
            "delta_tone": "success",
            "subtitle": "vs previous month",
            "tone": "success",
        },
        # ── timeline ──────────────────────────────────────────────
        {
            "type": "section_header",
            "number": "3",
            "title": "Timeline",
        },
        {
            "type": "timeline",
            "title": "Project Milestones",
            "items": [
                {
                    "date": "2026-01-15",
                    "title": "Kickoff",
                    "description": "Project planning completed",
                    "tone": "primary",
                },
                {
                    "date": "2026-03-01",
                    "title": "Alpha Release",
                    "description": "Internal testing phase",
                    "tone": "info",
                },
                {
                    "date": "2026-05-10",
                    "title": "Beta Launch",
                    "description": "Public beta with 500 users",
                    "tone": "warning",
                },
                {
                    "date": "2026-06-20",
                    "title": "GA Release",
                    "description": "Full production rollout",
                    "tone": "success",
                },
            ],
        },
        # ── milestone_list ────────────────────────────────────────
        {
            "type": "section_header",
            "number": "4",
            "title": "Milestone List",
        },
        {
            "type": "milestone_list",
            "title": "Release Milestones",
            "items": [
                {
                    "title": "Schema Validation",
                    "description": "Pydantic models finalized",
                    "status": "completed",
                    "date": "2026-01-20",
                },
                {
                    "title": "Core Renderers",
                    "description": "All block types implemented",
                    "status": "completed",
                    "date": "2026-03-15",
                },
                {
                    "title": "Documentation",
                    "description": "API docs and examples",
                    "status": "in_progress",
                    "date": "2026-06-01",
                },
                {
                    "title": "Performance Tuning",
                    "description": "Optimize render pipeline",
                    "status": "pending",
                    "date": "2026-07-01",
                },
            ],
        },
        {"type": "page_break"},
        # ── risk_register ─────────────────────────────────────────
        {
            "type": "section_header",
            "number": "5",
            "title": "Risk Register",
        },
        {
            "type": "risk_register",
            "title": "Project Risk Register",
            "columns": [
                {"key": "risk", "label": "Risk", "width": 0.35},
                {"key": "impact", "label": "Impact", "width": 0.15},
                {"key": "likelihood", "label": "Likelihood", "width": 0.15},
                {"key": "mitigation", "label": "Mitigation", "width": 0.35},
            ],
            "rows": [
                {
                    "risk": "Schema instability",
                    "impact": "High",
                    "likelihood": "Medium",
                    "mitigation": "Strict validation, versioning",
                },
                {
                    "risk": "Render failures",
                    "impact": "High",
                    "likelihood": "Low",
                    "mitigation": "Comprehensive test suite",
                },
                {
                    "risk": "Dependency drift",
                    "impact": "Medium",
                    "likelihood": "Medium",
                    "mitigation": "Pin versions, Dependabot",
                },
            ],
        },
        # ── status_table ──────────────────────────────────────────
        {
            "type": "section_header",
            "number": "6",
            "title": "Status Table",
        },
        {
            "type": "status_table",
            "title": "Component Status",
            "columns": [
                {"key": "component", "label": "Component", "width": 0.4},
                {"key": "status", "label": "Status", "width": 0.2},
                {"key": "owner", "label": "Owner", "width": 0.2},
                {"key": "notes", "label": "Notes", "width": 0.2},
            ],
            "rows": [
                {
                    "component": "comparison_card",
                    "status": "complete",
                    "owner": "Python Dev",
                    "notes": "Merged",
                },
                {
                    "component": "metric_delta",
                    "status": "complete",
                    "owner": "Python Dev",
                    "notes": "Merged",
                },
                {
                    "component": "timeline",
                    "status": "complete",
                    "owner": "Python Dev",
                    "notes": "Merged",
                },
                {
                    "component": "milestone_list",
                    "status": "complete",
                    "owner": "Python Dev",
                    "notes": "Merged",
                },
                {
                    "component": "risk_register",
                    "status": "complete",
                    "owner": "Python Dev",
                    "notes": "Merged",
                },
                {
                    "component": "status_table",
                    "status": "complete",
                    "owner": "Python Dev",
                    "notes": "Merged",
                },
                {
                    "component": "markdown_block",
                    "status": "complete",
                    "owner": "Python Dev",
                    "notes": "Merged",
                },
            ],
        },
        {"type": "page_break"},
        # ── markdown_block ────────────────────────────────────────
        {
            "type": "section_header",
            "number": "7",
            "title": "Markdown Block",
        },
        {
            "type": "markdown_block",
            "title": "Release Notes",
            "markdown": (
                "## What's New\n\n"
                "Seven new block types have been added to the report specification:\n\n"
                "- **comparison_card** - side-by-side comparisons with delta indicators\n"
                "- **metric_delta** - single metrics with change indicators\n"
                "- **timeline** - event timelines with visual markers\n"
                "- **milestone_list** - project milestone tracking\n"
                "- **risk_register** - structured risk documentation\n"
                "- **status_table** - component status tracking\n"
                "- **markdown_block** - rich text via standard markdown\n\n"
                "### Migration\n\n"
                "All new blocks are **backward compatible**. No existing specs will break.\n\n"
                "```python\n"
                "from reportlab_json_renderer import render_pdf\n"
                'result = render_pdf(spec, output_path="report.pdf")\n'
                "print(result['pages'])\n"
                "```\n\n"
            ),
        },
    ],
}


def main():
    out_dir = Path(__file__).parent / "test_output"
    out_dir.mkdir(exist_ok=True)

    pdf_path = out_dir / "new_components_demo.pdf"
    result = render_pdf(SPEC, output_path=str(pdf_path))

    print(f"PDF generated: {pdf_path}")
    print(f"  Pages: {result.get('pages', 'N/A')}")
    print(f"  Size: {pdf_path.stat().st_size} bytes")
    print(f"  Warnings: {result.get('warnings', [])}")

    # Create zip for upload
    zip_path = out_dir / "new_components_demo.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(pdf_path, pdf_path.name)
    print(f"  Zip: {zip_path} ({zip_path.stat().st_size} bytes)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
