from __future__ import annotations

import math
from typing import Any

from intent_parser.models import ActionResult, CustomerDemand, RouteDecision


TEAM_BY_ROUTE = {
    "flow_overseas_access": "海外访问技术组",
    "flow_domestic_networking": "国内组网技术组",
    "flow_dedicated_ip_bandwidth": "专线与公网 IP 技术组",
    "flow_clarify_requirements": "售前需求澄清组",
}


class ActionExecutor:
    def execute(self, demand: CustomerDemand, decision: RouteDecision) -> ActionResult:
        quote = build_quote(demand, decision.route)
        next_steps = build_next_steps(demand, decision.route)
        return ActionResult(
            action_type=decision.route,
            owner_team=TEAM_BY_ROUTE[decision.route],
            quote=quote,
            next_steps=next_steps,
            crm_payload={
                "scenario_type": demand.scenario_type,
                "route": decision.route,
                "priority": decision.priority,
                "owner_team": TEAM_BY_ROUTE[decision.route],
                "missing_fields": demand.missing_fields,
            },
        )


def build_quote(demand: CustomerDemand, route: str) -> dict[str, Any]:
    bandwidth = max(demand.bandwidth_est_mbps, 10 if route != "flow_clarify_requirements" else 0)
    unit_price = {
        "flow_overseas_access": 120,
        "flow_domestic_networking": 80,
        "flow_dedicated_ip_bandwidth": 180,
        "flow_clarify_requirements": 0,
    }[route]
    monthly_estimate = math.ceil(bandwidth * unit_price) if unit_price else None
    return {
        "currency": "CNY",
        "bandwidth_mbps": bandwidth,
        "monthly_estimate": monthly_estimate,
        "budget": demand.budget,
        "duration": demand.duration,
        "note": quote_note(route),
    }


def build_next_steps(demand: CustomerDemand, route: str) -> list[str]:
    if route == "flow_clarify_requirements":
        return [
            "回收访问来源、目标位置、用户规模、试用周期和预算。",
            "字段完整后重新提交 /analyze_demand。",
        ]

    steps = [
        "生成标准报价草案。",
        "同步结构化字段到 CRM 商机记录。",
    ]
    if demand.missing_fields:
        steps.append(f"补充字段：{', '.join(demand.missing_fields)}。")
    if route == "flow_overseas_access":
        steps.append("安排海外访问链路可用性评估。")
    elif route == "flow_domestic_networking":
        steps.append("核对站点数量和互通拓扑。")
    elif route == "flow_dedicated_ip_bandwidth":
        steps.append("查询公网 IP/专线资源库存。")
    return steps


def quote_note(route: str) -> str:
    return {
        "flow_overseas_access": "按海外访问加速基础单价估算，最终以线路资源为准。",
        "flow_domestic_networking": "按国内组网基础单价估算，需结合站点拓扑确认。",
        "flow_dedicated_ip_bandwidth": "按专线或公网 IP 资源预估，需库存确认。",
        "flow_clarify_requirements": "需求字段不足，暂不生成价格估算。",
    }[route]
