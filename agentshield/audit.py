from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger("agentshield.audit")


def record_report(report: dict, audit_file: str | None = None) -> None:
    """Log a report and optionally append JSONL to an explicitly configured audit file."""
    safe_record = {k: v for k, v in report.items() if k != "actions"}
    logger.info("assessment_complete %s", json.dumps(safe_record, default=str, sort_keys=True))
    if audit_file:
        target = Path(audit_file)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(safe_record, default=str, sort_keys=True) + "\n")
