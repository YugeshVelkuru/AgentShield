from __future__ import annotations

from fnmatch import fnmatchcase
from pathlib import PurePosixPath
from typing import Any

from .models import Action, Finding

_PATH_KEYS = {"path", "file", "filename", "filepath", "target"}
_WRITE_TOOLS = {"write_file", "delete_file", "move_file", "patch_file"}
_EXEC_TOOLS = {"shell", "run_command", "execute", "terminal", "subprocess"}
_NETWORK_TOOLS = {"http", "http_request", "fetch", "browser", "web_request"}


def _paths(value: Any, key: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for child_key, child in value.items():
            found.extend(_paths(child, str(child_key).lower()))
    elif isinstance(value, (list, tuple)):
        for child in value:
            found.extend(_paths(child, key))
    elif isinstance(value, str) and key in _PATH_KEYS:
        found.append(value)
    return found


def _normalize_path(path: str) -> str:
    # Keep leading ``..`` segments intact so traversal checks can detect them.
    return str(PurePosixPath(path.replace("\\", "/")))


def _matches(path: str, patterns: list[str]) -> bool:
    normalized = _normalize_path(path)
    for pattern in patterns:
        p = _normalize_path(pattern)
        if fnmatchcase(normalized, p) or (p.endswith("/**") and normalized.startswith(p[:-3] + "/")):
            return True
    return False


def evaluate_action(
    action: Action,
    *,
    allowed_tools: set[str],
    allowed_paths: list[str],
    denied_paths: list[str],
    index: int,
) -> list[Finding]:
    """Check a trace event. This function only evaluates metadata; it does not invoke tools."""
    findings: list[Finding] = []
    tool = action.tool.lower()
    if tool not in {name.lower() for name in allowed_tools}:
        severity = "critical" if tool in _EXEC_TOOLS else "high"
        findings.append(Finding(severity=severity, code="TOOL_NOT_ALLOWED", action_index=index,
                                message=f"Tool '{action.tool}' is not on the allowlist."))
    if tool in _WRITE_TOOLS:
        findings.append(Finding(severity="high", code="MUTATING_TOOL", action_index=index,
                                message=f"Mutating tool '{action.tool}' requires explicit authorization."))
    if tool in _NETWORK_TOOLS:
        findings.append(Finding(severity="high", code="NETWORK_TOOL", action_index=index,
                                message=f"Network tool '{action.tool}' is outside the default safe policy."))
    for path in _paths(action.arguments):
        normalized = _normalize_path(path)
        if _matches(normalized, denied_paths):
            findings.append(Finding(severity="critical", code="DENIED_PATH_ACCESS", action_index=index,
                                    message="Action targets a protected path.", details={"path": normalized}))
        elif not _matches(normalized, allowed_paths):
            findings.append(Finding(severity="high", code="PATH_OUTSIDE_ALLOWLIST", action_index=index,
                                    message="Action targets a path outside the allowed roots.", details={"path": normalized}))
        if normalized.startswith("../") or normalized == "..":
            findings.append(Finding(severity="critical", code="PATH_TRAVERSAL", action_index=index,
                                    message="Action contains a parent-directory traversal path.", details={"path": normalized}))
    if action.source == "unknown":
        findings.append(Finding(severity="medium", code="UNKNOWN_ACTION_SOURCE", action_index=index,
                                message="Action provenance is missing or unknown."))
    return findings
