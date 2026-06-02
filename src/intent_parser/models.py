from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class RegionScope(str, Enum):
    domestic = "domestic"
    overseas = "overseas"
    unknown = "unknown"


class ScenarioType(str, Enum):
    overseas_access = "overseas_access"
    domestic_networking = "domestic_networking"
    dedicated_ip_or_high_bandwidth = "dedicated_ip_or_high_bandwidth"
    trial_or_poc = "trial_or_poc"
    unknown = "unknown"


class DemandAnalysisRequest(BaseModel):
    text: str = Field(min_length=1, description="Raw sales conversation or demand text.")
    channel: str | None = Field(default=None, description="Source channel, e.g. CRM.")
    request_id: str | None = Field(default=None, description="External trace id.")


class CustomerDemand(BaseModel):
    access_source: str | None = Field(
        default=None, description="Source office, site, or region."
    )
    source_scope: RegionScope = Field(default=RegionScope.unknown)
    target_region: str | None = Field(
        default=None, description="Target application, site, or region."
    )
    target_scope: RegionScope = Field(default=RegionScope.unknown)
    user_count: int | None = Field(default=None, ge=1)
    bandwidth_est_mbps: int = Field(default=0, ge=0)
    duration: str | None = Field(default=None, description="Contract or trial duration.")
    budget: float | None = Field(default=None, ge=0, description="Budget in CNY.")
    requires_fixed_ip: bool = False
    scenario_type: ScenarioType = ScenarioType.unknown
    raw_keywords: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.6, ge=0, le=1)
    missing_fields: list[str] = Field(default_factory=list)

    @field_validator("bandwidth_est_mbps")
    @classmethod
    def round_bandwidth(cls, value: int) -> int:
        return max(0, int(value))


class RouteDecision(BaseModel):
    route: Literal[
        "flow_overseas_access",
        "flow_domestic_networking",
        "flow_dedicated_ip_bandwidth",
        "flow_clarify_requirements",
    ]
    action: str
    matched_rules: list[str] = Field(default_factory=list)
    priority: int = Field(ge=0, le=100)
    reason: str


class ActionResult(BaseModel):
    action_type: str
    owner_team: str
    quote: dict[str, Any]
    next_steps: list[str]
    crm_payload: dict[str, Any]


class WorkflowResult(BaseModel):
    request_id: str | None = None
    structured_data: CustomerDemand
    decision: RouteDecision
    action_result: ActionResult
