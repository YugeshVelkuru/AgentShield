from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class Action(BaseModel):
    """A claimed action from an agent trace; AgentShield never executes it."""

    tool: str = Field(min_length=1, max_length=100)
    arguments: dict[str, Any] = Field(default_factory=dict)
    source: Literal["user", "system", "tool", "unknown"] = "unknown"
    scenario_id: str | None = None


class Finding(BaseModel):
    severity: Literal["low", "medium", "high", "critical"]
    code: str
    message: str
    action_index: int | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class AssessmentRequest(BaseModel):
    actions: list[Action]
    allowed_tools: set[str] = Field(default_factory=lambda: {"read_file", "list_files"})
    allowed_paths: list[str] = Field(default_factory=lambda: ["workspace/**"])
    denied_paths: list[str] = Field(default_factory=lambda: ["**/.env", "**/secrets/**", "**/id_rsa"])
    run_id: str | None = None


class AssessmentReport(BaseModel):
    run_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    action_count: int
    passed: bool
    findings: list[Finding]
    summary: dict[str, int]
