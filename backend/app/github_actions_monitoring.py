"""Read-only GitHub Actions workflow status for public repositories.

No token, write operation, or user-supplied URL. Failures never imply a healthy repo.
"""
from fastapi import HTTPException
from app.github_readonly import (
    NAME_PATTERN, configured_owner, _client_factory, _read, _public_repo,
)
from app.devops_monitoring import summarize_pipelines

async def public_workflow_status(repo_name: str):
    if not NAME_PATTERN.fullmatch(repo_name) or repo_name in (".", ".."):
        raise HTTPException(status_code=422, detail="Nome de repositório inválido.")
    owner = configured_owner()
    async with _client_factory() as client:
        metadata = await _read(client, f"/repos/{owner}/{repo_name}")
        if _public_repo(metadata, owner) is None:
            raise HTTPException(status_code=404, detail="Repositório público não encontrado.")
        payload = await _read(
            client, f"/repos/{owner}/{repo_name}/actions/runs",
            params={"per_page": 30, "page": 1},
        )
    if not isinstance(payload, dict) or not isinstance(payload.get("workflow_runs"), list):
        raise HTTPException(status_code=502, detail="Resposta de workflows inválida.")
    runs = []
    for item in payload["workflow_runs"][:30]:
        if not isinstance(item, dict):
            continue
        state = item.get("status")
        conclusion = item.get("conclusion")
        status = ("running" if state != "completed"
                  else "success" if conclusion == "success"
                  else "failure" if conclusion else "unknown")
        runs.append({
            "id": item.get("id"),
            "repository": repo_name,
            "name": str(item.get("name") or "")[:120],
            "status": status,
            "conclusion": conclusion,
            "html_url": str(item.get("html_url") or "")[:500],
            "created_at": item.get("created_at"),
        })
    summary = summarize_pipelines(runs)
    # Other conclusions (cancelled, skipped, etc.) must not be silently counted as success.
    summary["counts"]["unknown"] = sum(run["status"] == "unknown" for run in runs)
    return {"owner": owner, "repository": repo_name, "source": "github-actions-public",
            "live": True, "sample_size": len(runs), "runs": runs, "summary": summary}
