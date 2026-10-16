from agentshield.models import Action, AssessmentRequest
from agentshield.policy import evaluate_action
from agentshield.service import assess


def check(action: Action):
    return evaluate_action(action, allowed_tools={"read_file", "list_files"},
                           allowed_paths=["workspace/**"], denied_paths=["**/.env", "**/secrets/**"], index=0)


def test_allowed_workspace_read_passes():
    assert check(Action(tool="read_file", arguments={"path": "workspace/README.md"}, source="user")) == []


def test_denied_secret_path_is_flagged():
    findings = check(Action(tool="read_file", arguments={"path": "workspace/.env"}, source="tool"))
    assert any(f.code == "DENIED_PATH_ACCESS" for f in findings)


def test_unlisted_shell_is_critical():
    findings = check(Action(tool="shell", arguments={"command": "echo synthetic"}, source="unknown"))
    assert any(f.code == "TOOL_NOT_ALLOWED" and f.severity == "critical" for f in findings)


def test_path_outside_workspace_is_flagged():
    findings = check(Action(tool="read_file", arguments={"path": "../outside.txt"}, source="user"))
    assert any(f.code == "PATH_OUTSIDE_ALLOWLIST" for f in findings)
    assert any(f.code == "PATH_TRAVERSAL" for f in findings)


def test_report_summarizes_findings():
    report = assess(AssessmentRequest(actions=[Action(tool="write_file", arguments={"path": "workspace/a"}, source="tool")]))
    assert not report.passed
    assert report.summary["high"] >= 1
