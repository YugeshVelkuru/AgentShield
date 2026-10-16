from __future__ import annotations

from uuid import uuid4

from .audit import record_report
from .models import AssessmentReport, AssessmentRequest
from .policy import evaluate_action


def assess(request: AssessmentRequest, audit_file: str | None = None) -> AssessmentReport:
    findings = []
    for index, action in enumerate(request.actions):
        findings.extend(evaluate_action(action, allowed_tools=request.allowed_tools,
                                        allowed_paths=request.allowed_paths,
                                        denied_paths=request.denied_paths, index=index))
    counts = {level: sum(f.severity == level for f in findings)
              for level in ("critical", "high", "medium", "low")}
    report = AssessmentReport(run_id=request.run_id or str(uuid4()), action_count=len(request.actions),
                              passed=not findings, findings=findings, summary=counts)
    record_report(report.model_dump(mode="json"), audit_file=audit_file)
    return report
