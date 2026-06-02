from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from intent_parser.config import Settings
from intent_parser.models import RegionScope, ScenarioType
from intent_parser.parsers import HeuristicDemandParser, parse_customer_demand_json
from intent_parser.workflow import DemandWorkflow


class WorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        settings = Settings(
            llm_api_key=None,
            llm_model="test",
            llm_base_url=None,
            per_user_bandwidth_mbps=1,
            high_bandwidth_threshold_mbps=100,
        )
        self.workflow = DemandWorkflow(settings=settings, parser=HeuristicDemandParser(settings))

    def test_overseas_access_demand(self) -> None:
        result = self.workflow.analyze(
            "客户上海办公室大概10个人，想先试一个月访问美国 SaaS，预算5000左右。"
        )

        self.assertEqual(result.structured_data.user_count, 10)
        self.assertEqual(result.structured_data.bandwidth_est_mbps, 10)
        self.assertEqual(result.structured_data.target_scope, RegionScope.overseas)
        self.assertEqual(result.structured_data.budget, 5000)
        self.assertEqual(result.decision.route, "flow_overseas_access")
        self.assertEqual(result.action_result.owner_team, "海外访问技术组")

    def test_high_bandwidth_routes_to_dedicated_flow(self) -> None:
        result = self.workflow.analyze("深圳和广州两个点要内网互通，150人办公，先按半年看。")

        self.assertEqual(result.structured_data.bandwidth_est_mbps, 150)
        self.assertEqual(
            result.structured_data.scenario_type,
            ScenarioType.dedicated_ip_or_high_bandwidth,
        )
        self.assertEqual(result.decision.route, "flow_dedicated_ip_bandwidth")

    def test_fixed_ip_routes_to_dedicated_flow(self) -> None:
        result = self.workflow.analyze("北京办公室50人访问业务系统，要求固定公网 IP。")

        self.assertTrue(result.structured_data.requires_fixed_ip)
        self.assertEqual(result.decision.route, "flow_dedicated_ip_bandwidth")

    def test_incomplete_demand_routes_to_clarification(self) -> None:
        result = self.workflow.analyze("客户想了解一下网络方案。")

        self.assertEqual(result.decision.route, "flow_clarify_requirements")
        self.assertIn("user_count", result.structured_data.missing_fields)

    def test_parse_json_from_markdown_fence(self) -> None:
        demand = parse_customer_demand_json(
            """```json
            {
              "access_source": "上海办公室",
              "source_scope": "domestic",
              "target_region": "美国 SaaS",
              "target_scope": "overseas",
              "user_count": 10,
              "bandwidth_est_mbps": 10,
              "duration": "试用1个月",
              "budget": 5000,
              "requires_fixed_ip": false,
              "scenario_type": "overseas_access",
              "raw_keywords": ["上海", "10人"],
              "confidence": 0.9,
              "missing_fields": []
            }
            ```"""
        )

        self.assertEqual(demand.user_count, 10)
        self.assertEqual(demand.target_scope, RegionScope.overseas)


if __name__ == "__main__":
    unittest.main()
