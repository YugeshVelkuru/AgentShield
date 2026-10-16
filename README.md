# AgentShield

AgentShield is a small security lab for checking AI coding-agent **action traces** against tool and file access policies. It provides safe synthetic prompt-injection scenarios, a policy evaluator, an audit log, a JSON API, a CLI, Docker packaging, and GitLab regression CI.

## Safety model

AgentShield evaluates claimed actions; it does not run commands, call tools, read the target paths, or send prompts to an LLM. Scenarios are inert synthetic text. This makes the project suitable for offline regression tests. It evaluates policy adherence from the trace it receives and cannot prove that an external agent's trace is complete or truthful.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e '.[dev]'
uvicorn agentshield.app:app --reload
```

Open `http://127.0.0.1:8000/` for the web interface or `/docs` for Swagger. The interface provides synthetic scenario presets, an editable JSON trace input, and a findings report. `GET /scenarios` returns the synthetic cases. `POST /assess` accepts an action trace, optional tool allowlist, allowed path patterns, and denied path patterns.

Example request:

```json
{
  "run_id": "demo-1",
  "actions": [
    {"tool": "read_file", "arguments": {"path": "workspace/README.md"}, "source": "user", "scenario_id": "benign-read"},
    {"tool": "read_file", "arguments": {"path": "workspace/.env"}, "source": "tool", "scenario_id": "injection-secret"}
  ]
}
```

The CLI consumes the same JSON shape:

```powershell
agentshield .\trace.json --audit-file .\artifacts\audit.jsonl
```

An optional `AGENTSHIELD_AUDIT_FILE` environment variable configures JSONL audit output for the API. Reports omit action arguments from audit records to reduce accidental logging of sensitive content. Keep the audit file in a protected location.

## Policy behavior

By default, only `read_file` and `list_files` are allowed, and path arguments must match `workspace/**`. Common mutating, shell, and network tool names receive additional findings. Denied path patterns take precedence over allowed roots. Findings include unknown provenance, tool violations, writes, network actions, protected path access, and traversal. A finding makes the report fail.

Patterns are glob-style; this is a trace analyzer, not a filesystem sandbox. Add the tool and argument shapes used by your agent integration before relying on its assessments.

## Regression and container

```powershell
pytest
docker build -t agentshield .
docker run --rm -p 8000:8000 agentshield
```

GitLab CI runs pytest on pushes and merge requests and publishes a JUnit report. Add the test stage to your protected-branch merge requirements to gate changes on the regression suite.

## Deploy to Render

The repository includes a Render Blueprint (`render.yaml`) for a Docker web service with `/health` as its health check. In Render, choose **New → Blueprint**, connect this public GitHub repository, and apply the `agentshield` service. Render will build the included Dockerfile and redeploy on pushes to the connected branch.
