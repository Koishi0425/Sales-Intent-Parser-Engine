from __future__ import annotations

from intent_parser.actions import ActionExecutor
from intent_parser.config import Settings
from intent_parser.models import DemandAnalysisRequest, WorkflowResult
from intent_parser.parsers import DemandParser, ResilientDemandParser
from intent_parser.rules import RuleEngine


class DemandWorkflow:
    def __init__(
        self,
        *,
        settings: Settings | None = None,
        parser: DemandParser | None = None,
        rule_engine: RuleEngine | None = None,
        action_executor: ActionExecutor | None = None,
    ):
        self.settings = settings or Settings.from_env()
        self.parser = parser or ResilientDemandParser(self.settings)
        self.rule_engine = rule_engine or RuleEngine(self.settings)
        self.action_executor = action_executor or ActionExecutor()

    def analyze(self, request: DemandAnalysisRequest | str) -> WorkflowResult:
        if isinstance(request, str):
            request = DemandAnalysisRequest(text=request)

        structured_data = self.parser.parse(request.text)
        decision = self.rule_engine.route(structured_data)
        action_result = self.action_executor.execute(structured_data, decision)
        return WorkflowResult(
            request_id=request.request_id,
            structured_data=structured_data,
            decision=decision,
            action_result=action_result,
        )
