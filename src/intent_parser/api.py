from __future__ import annotations

from intent_parser.models import DemandAnalysisRequest, WorkflowResult
from intent_parser.workflow import DemandWorkflow

try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
except ImportError as exc:
    raise RuntimeError(
        "FastAPI is not installed. Install project dependencies before running the API."
    ) from exc


class UTF8JSONResponse(JSONResponse):
    media_type = "application/json; charset=utf-8"


app = FastAPI(
    title="Sales Intent Parser Engine",
    description="Parse B2B sales demand text into structured business routing decisions.",
    version="0.1.0",
    default_response_class=UTF8JSONResponse,
)
workflow = DemandWorkflow()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze_demand", response_model=WorkflowResult)
def analyze_demand(request: DemandAnalysisRequest) -> WorkflowResult:
    return workflow.analyze(request)
