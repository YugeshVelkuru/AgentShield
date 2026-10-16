from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .models import AssessmentRequest
from .service import assess


def main() -> None:
    parser = argparse.ArgumentParser(description="Assess a JSON agent action trace without executing its actions.")
    parser.add_argument("trace", type=Path, help="JSON file containing an actions array")
    parser.add_argument("--audit-file", help="Optional JSONL audit log path")
    args = parser.parse_args()
    request = AssessmentRequest.model_validate_json(args.trace.read_text(encoding="utf-8"))
    report = assess(request, audit_file=args.audit_file)
    print(report.model_dump_json(indent=2))
    if not report.passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
