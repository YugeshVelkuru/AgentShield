from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .models import AssessmentReport, AssessmentRequest
from .scenarios import list_scenarios
from .service import assess

app = FastAPI(title="AgentShield", version="0.1.0",
              description="Safe evaluation of AI coding-agent action traces. Actions are inspected, never executed.")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def frontend() -> str:
    return Path(__file__).with_name("index.html").read_text(encoding="utf-8")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/scenarios")
def scenarios() -> list[dict[str, str]]:
    return list_scenarios()


@app.post("/assess", response_model=AssessmentReport)
def assess_trace(request: AssessmentRequest) -> AssessmentReport:
    return assess(request, audit_file=os.getenv("AGENTSHIELD_AUDIT_FILE"))
