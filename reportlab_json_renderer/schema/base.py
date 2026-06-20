"""Pydantic models for the JSON report specification.

These models serve as the single source of truth for the JSON contract.
They can also export a JSON Schema file via ``ReportSpec.model_json_schema()``.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# ── Enums ────────────────────────────────────────────────────────────


class PageSize(StrEnum):
    A4 = "A4"
    LETTER = "letter"
    LEGAL = "legal"
    A3 = "A3"


class Orientation(StrEnum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class ImageFit(StrEnum):
    CONTAIN = "contain"
    COVER = "cover"
    STRETCH = "stretch"


class ImageAlign(StrEnum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class TableStyle(StrEnum):
    STRIPED = "striped"
    STANDARD = "standard"
    COMPACT = "compact"


class StrictModel(BaseModel):
    """Base model for public JSON schema objects."""

    model_config = ConfigDict(extra="forbid")


# ── Common sub-models ────────────────────────────────────────────────


class PageMargins(StrictModel):
    left_cm: float = Field(default=1.5, ge=0)
    right_cm: float = Field(default=1.5, ge=0)
    top_cm: float = Field(default=2.2, ge=0)
    bottom_cm: float = Field(default=2.0, ge=0)


class PageConfig(StrictModel):
    size: PageSize = PageSize.A4
    orientation: Orientation = Orientation.PORTRAIT
    margins: PageMargins = Field(default_factory=PageMargins)


class HeaderConfig(StrictModel):
    enabled: bool = True
    variant: str = "default"


class FooterConfig(StrictModel):
    enabled: bool = True
    show_page_number: bool = True


class ReportMetadata(StrictModel):
    entity_name: str
    report_title: str
    period: str | None = None
    generated_at: str | None = None
    powered_by: str | None = None
    confidential: bool = False


# ── Block models ─────────────────────────────────────────────────────


class TitleBlock(StrictModel):
    type: Literal["title"] = "title"
    entity: str | None = None
    title: str | None = None
    subtitle: str | None = None
    right_text: str | None = None


class SectionHeaderBlock(StrictModel):
    type: Literal["section_header"] = "section_header"
    number: str | None = None
    title: str


class ParagraphBlock(StrictModel):
    type: Literal["paragraph"] = "paragraph"
    text: str
    style: str = "body"


class RichTextRun(StrictModel):
    text: str
    style: str = "normal"
    bold: bool = False
    italic: bool = False
    tone: str | None = None


class RichTextBlock(StrictModel):
    type: Literal["rich_text"] = "rich_text"
    runs: list[RichTextRun]


class KPIItem(StrictModel):
    label: str
    value: str
    sub: str | None = None
    tone: str | None = None


class KPIGridBlock(StrictModel):
    type: Literal["kpi_grid"] = "kpi_grid"
    title: str | None = None
    columns: int = Field(default=4, ge=1, le=12)
    items: list[KPIItem]


class CalloutBlock(StrictModel):
    type: Literal["callout"] = "callout"
    tone: str = "primary"
    title: str | None = None
    text: str


class CalloutItem(StrictModel):
    tone: str = "primary"
    title: str | None = None
    text: str


class CalloutGroupBlock(StrictModel):
    type: Literal["callout_group"] = "callout_group"
    title: str | None = None
    items: list[CalloutItem]


class TableColumn(StrictModel):
    key: str
    label: str
    width: float = Field(default=0.2, gt=0, le=1)


class TableBlock(StrictModel):
    type: Literal["table"] = "table"
    title: str | None = None
    style: TableStyle = TableStyle.STANDARD
    columns: list[TableColumn]
    rows: list[dict[str, str]]


class MatrixTableBlock(StrictModel):
    type: Literal["matrix_table"] = "matrix_table"
    title: str | None = None
    columns: list[str]
    rows: list[list[str]]


class InsightItem(StrictModel):
    title: str
    text: str


class InsightListBlock(StrictModel):
    type: Literal["insight_list"] = "insight_list"
    title: str | None = None
    items: list[InsightItem]


class RecommendationItem(StrictModel):
    priority: str
    action: str
    owner: str | None = None
    impact: str | None = None


class RecommendationsBlock(StrictModel):
    type: Literal["recommendations"] = "recommendations"
    title: str | None = None
    items: list[RecommendationItem]


class ImageBlock(StrictModel):
    type: Literal["image"] = "image"
    title: str | None = None
    src: str = Field(min_length=1)
    width_cm: float | None = Field(default=None, gt=0)
    height_cm: float | None = Field(default=None, gt=0)
    fit: ImageFit = ImageFit.CONTAIN
    align: ImageAlign = ImageAlign.CENTER


class ChartBlock(StrictModel):
    type: Literal["chart"] = "chart"
    chart_type: str
    title: str | None = None
    labels: list[str] = Field(default_factory=list)
    values: list[float] = Field(default_factory=list)
    series: dict[str, list[float]] | None = None
    tone: str | None = None


class TwoColumnBlock(StrictModel):
    type: Literal["two_column"] = "two_column"
    left_width: float = Field(default=0.5, gt=0, lt=1)
    right_width: float = Field(default=0.5, gt=0, lt=1)
    left: list[dict[str, Any]] = Field(default_factory=list)
    right: list[dict[str, Any]] = Field(default_factory=list)


class PageBreakBlock(StrictModel):
    type: Literal["page_break"] = "page_break"


class SpacerBlock(StrictModel):
    type: Literal["spacer"] = "spacer"
    height: float = Field(default=6, ge=0)


class DividerBlock(StrictModel):
    type: Literal["divider"] = "divider"
    tone: str = "primary"
    thickness: float = Field(default=1, gt=0)


class BadgeBlock(StrictModel):
    type: Literal["badge"] = "badge"
    label: str
    tone: str = "primary"


class SummaryBoxBlock(StrictModel):
    type: Literal["summary_box"] = "summary_box"
    title: str | None = None
    text: str
    tone: str = "primary"


class ComparisonCardItem(StrictModel):
    label: str
    value: str
    delta: str | None = None
    tone: str | None = None


class ComparisonCardBlock(StrictModel):
    type: Literal["comparison_card"] = "comparison_card"
    title: str | None = None
    left: ComparisonCardItem = Field(default_factory=ComparisonCardItem)
    right: ComparisonCardItem = Field(default_factory=ComparisonCardItem)


class MetricDeltaBlock(StrictModel):
    type: Literal["metric_delta"] = "metric_delta"
    label: str | None = None
    value: str
    delta: str | None = None
    delta_tone: str | None = None
    subtitle: str | None = None
    tone: str = "primary"


class TimelineItem(StrictModel):
    date: str | None = None
    title: str
    description: str | None = None
    tone: str = "primary"


class TimelineBlock(StrictModel):
    type: Literal["timeline"] = "timeline"
    title: str | None = None
    items: list[TimelineItem] = Field(default_factory=list)


class MilestoneItem(StrictModel):
    title: str
    description: str | None = None
    status: str = "pending"
    date: str | None = None


class MilestoneListBlock(StrictModel):
    type: Literal["milestone_list"] = "milestone_list"
    title: str | None = None
    items: list[MilestoneItem] = Field(default_factory=list)


class RiskRegisterBlock(StrictModel):
    type: Literal["risk_register"] = "risk_register"
    title: str | None = None
    columns: list[TableColumn] = Field(default_factory=list)
    rows: list[dict[str, str]] = Field(default_factory=list)


class StatusTableBlock(StrictModel):
    type: Literal["status_table"] = "status_table"
    title: str | None = None
    columns: list[TableColumn] = Field(default_factory=list)
    rows: list[dict[str, str]] = Field(default_factory=list)


class MarkdownBlock(StrictModel):
    type: Literal["markdown_block"] = "markdown_block"
    title: str | None = None
    markdown: str


# ── Union of all block types ─────────────────────────────────────────

Block = Annotated[
    TitleBlock
    | SectionHeaderBlock
    | ParagraphBlock
    | RichTextBlock
    | KPIGridBlock
    | CalloutBlock
    | CalloutGroupBlock
    | TableBlock
    | MatrixTableBlock
    | InsightListBlock
    | RecommendationsBlock
    | ImageBlock
    | ChartBlock
    | TwoColumnBlock
    | PageBreakBlock
    | SpacerBlock
    | DividerBlock
    | BadgeBlock
    | SummaryBoxBlock
    | ComparisonCardBlock
    | MetricDeltaBlock
    | TimelineBlock
    | MilestoneListBlock
    | RiskRegisterBlock
    | StatusTableBlock
    | MarkdownBlock,
    Field(discriminator="type"),
]

SUPPORTED_BLOCK_TYPES: list[str] = [
    "title",
    "section_header",
    "paragraph",
    "rich_text",
    "kpi_grid",
    "callout",
    "callout_group",
    "table",
    "matrix_table",
    "insight_list",
    "recommendations",
    "image",
    "chart",
    "two_column",
    "page_break",
    "spacer",
    "divider",
    "badge",
    "summary_box",
    "comparison_card",
    "metric_delta",
    "timeline",
    "milestone_list",
    "risk_register",
    "status_table",
    "markdown_block",
]

SUPPORTED_CHART_TYPES: list[str] = [
    "bar",
    "horizontal_bar",
    "line",
    "area",
    "pie",
    "donut",
    "stacked_bar",
    "grouped_bar",
]

SUPPORTED_TONES: list[str] = [
    "primary",
    "danger",
    "success",
    "warning",
    "info",
    "dark",
    "muted",
    "light_bg",
]


# ── Root spec ────────────────────────────────────────────────────────


class ReportSpec(StrictModel):
    """Top-level report specification.

    This is the root model that the JSON input must conform to.
    """

    version: Literal["1.0"] = "1.0"
    template: str
    theme: str = "green"
    metadata: ReportMetadata
    page: PageConfig = Field(default_factory=PageConfig)
    header: HeaderConfig = Field(default_factory=HeaderConfig)
    footer: FooterConfig = Field(default_factory=FooterConfig)
    blocks: list[Block] = Field(default_factory=list)


__all__ = [
    "SUPPORTED_BLOCK_TYPES",
    "SUPPORTED_CHART_TYPES",
    "SUPPORTED_TONES",
    "BadgeBlock",
    "Block",
    "CalloutBlock",
    "CalloutGroupBlock",
    "CalloutItem",
    "ChartBlock",
    "ComparisonCardBlock",
    "ComparisonCardItem",
    "DividerBlock",
    "FooterConfig",
    "HeaderConfig",
    "ImageAlign",
    "ImageBlock",
    "ImageFit",
    "InsightItem",
    "InsightListBlock",
    "KPIGridBlock",
    "KPIItem",
    "MarkdownBlock",
    "MatrixTableBlock",
    "MetricDeltaBlock",
    "MilestoneItem",
    "MilestoneListBlock",
    "Orientation",
    "PageBreakBlock",
    "PageConfig",
    "PageMargins",
    "PageSize",
    "ParagraphBlock",
    "RecommendationItem",
    "RecommendationsBlock",
    "ReportMetadata",
    "ReportSpec",
    "RichTextBlock",
    "RichTextRun",
    "RiskRegisterBlock",
    "SectionHeaderBlock",
    "SpacerBlock",
    "StatusTableBlock",
    "SummaryBoxBlock",
    "TableColumn",
    "TableStyle",
    "TimelineBlock",
    "TimelineItem",
    "TitleBlock",
    "TwoColumnBlock",
]
