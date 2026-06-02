from __future__ import annotations

from intent_parser.config import Settings
from intent_parser.models import CustomerDemand, RegionScope, RouteDecision, ScenarioType


class RuleEngine:
    def __init__(self, settings: Settings):
        self.settings = settings

    def route(self, demand: CustomerDemand) -> RouteDecision:
        matched_rules: list[str] = []

        if (
            demand.requires_fixed_ip
            or demand.bandwidth_est_mbps > self.settings.high_bandwidth_threshold_mbps
            or demand.scenario_type == ScenarioType.dedicated_ip_or_high_bandwidth
        ):
            matched_rules.append("requires_fixed_ip_or_bandwidth_gt_threshold")
            return RouteDecision(
                route="flow_dedicated_ip_bandwidth",
                action="执行：固定IP/大带宽专线流程",
                matched_rules=matched_rules,
                priority=90,
                reason=(
                    "需求包含固定 IP/公网 IP/专线语义，或预估带宽超过 "
                    f"{self.settings.high_bandwidth_threshold_mbps} Mbps。"
                ),
            )

        if demand.target_scope == RegionScope.overseas or demand.scenario_type == ScenarioType.overseas_access:
            matched_rules.append("domestic_source_to_overseas_destination")
            return RouteDecision(
                route="flow_overseas_access",
                action="执行：访问海外应用子流程",
                matched_rules=matched_rules,
                priority=80,
                reason="目标位置或应用被识别为海外，适合进入海外访问方案分支。",
            )

        if (
            demand.source_scope == RegionScope.domestic
            and demand.target_scope in {RegionScope.domestic, RegionScope.unknown}
        ) or demand.scenario_type == ScenarioType.domestic_networking:
            matched_rules.append("domestic_network_or_multi_site")
            return RouteDecision(
                route="flow_domestic_networking",
                action="执行：国内多点组网流程",
                matched_rules=matched_rules,
                priority=70,
                reason="来源和目标均偏国内，或文本包含国内组网/多点互通语义。",
            )

        matched_rules.append("insufficient_structured_fields")
        return RouteDecision(
            route="flow_clarify_requirements",
            action="执行：补充需求信息流程",
            matched_rules=matched_rules,
            priority=30,
            reason="缺少足够的来源、目标或规模信息，建议先向销售侧回收关键字段。",
        )
