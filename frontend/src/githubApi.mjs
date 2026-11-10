"""Public, read-only GitHub integration. No GitHub credentials or write scopes."""
import base64
import json
import os
import re

import httpx
from fastapi import HTTPException

API_ROOT = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "Codax-ReadOnly-Assistant",
}
NAME_PATTERN = re.compile(r"[A-Za-z0-9_.-]{1,100}\Z")
OWNER_PATTERN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?\Z")
README_PREVIEW_BYTES = 8000
PROFILE_MAX_BYTES = 4096
PROFILE_PATH = ".codax/project.json"


def configured_owner() -> str:
    owner = os.getenv("CODAX_GITHUB_OWNER", "juniordev830").strip()
    if not OWNER_PATTERN.fullmatch(owner):
        raise HTTPException(status_code=503, detail="Configure CODAX_GITHUB_OWNER com um usuário GitHub válido.")
    return owner


def _client_factory():
    return httpx.AsyncClient(timeout=10.0, follow_redirects=False)


async def _read(client: httpx.AsyncClient, path: str, *, params=None, optional=False):
    try:
        response = await client.get(API_ROOT + path, params=params, headers=HEADERS)
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="O GitHub demorou para responder.") from None
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Não foi possível consultar o GitHub.") from None
    if response.status_code == 404:
        if optional:
            return None
        raise HTTPException(status_code=404, detail="Repositório público não encontrado.")
    if response.status_code in (403, 429):
        raise HTTPException(status_code=503, detail="Limite de consultas ao GitHub atingido; tente mais tarde.")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="O GitHub retornou uma resposta inesperada.")
    try:
        return response.json()
    except ValueError:
        raise HTTPException(status_code=502, detail="Resposta inválida do GitHub.") from None


def _public_repo(data, owner):
    if not isinstance(data, dict):
        return None
    actual_owner = (data.get("owner") or {}).get("login", "")
    name = data.get("name")
    if (
        not isinstance(actual_owner, str)
        or actual_owner.casefold() != owner.casefold()
        or data.get("private") is not False
        or not isinstance(name, str)
        or not NAME_PATTERN.fullmatch(name)
        or name in (".", "..")
    ):
        return None
    return {
        "name": name,
        "description": str(data.get("description") or "")[:300],
        "language": str(data.get("language") or "")[:50],
        "updated_at": str(data.get("updated_at") or ""),
        "html_url": f"https://github.com/{owner}/{name}",
    }


async def list_public_repositories(page: int = 1, per_page: int = 100):
    if page < 1 or per_page < 1 or per_page > 100:
        raise HTTPException(status_code=422, detail="Parâmetros de paginação inválidos.")
    owner = configured_owner()
    async with _client_factory() as client:
        data = await _read(
            client,
            f"/users/{owner}/repos",
            params={"type": "owner", "sort": "updated", "per_page": per_page, "page": page},
        )
    if not isinstance(data, list):
        raise HTTPException(status_code=502, detail="Formato inesperado da lista do GitHub.")
    repos = [item for entry in data if (item := _public_repo(entry, owner)) is not None]
    return {"owner": owner, "repositories": repos, "limit": per_page, "page": page, "scope": "public-read-only"}


def _clean_profile(document):
    """Return inert presentation data only. Commands are shown, never executed."""
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        return None
    kind = document.get("project_kind")
    if not isinstance(kind, str) or not 1 <= len(kind) <= 64:
        return None

    def clean_list(key, *, limit=8):
        items = document.get(key)
        if not isinstance(items, list) or len(items) > limit:
            return []
        return [item for item in items if isinstance(item, str) and 0 < len(item) <= 280 and "\\x00" not in item][:limit]

    return {
        "schema_version": 1,
        "project_kind": kind,
        "entry_points": clean_list("entry_points"),
        "test_commands": clean_list("test_commands"),
        "review_focus": clean_list("review_focus"),
    }


def _decode_profile(data):
    if not isinstance(data, dict) or data.get("type") != "file":
        return None
    size = data.get("size")
    if not isinstance(size, int) or size < 1 or size > PROFILE_MAX_BYTES:
        return None
    if data.get("encoding") != "base64" or not isinstance(data.get("content"), str):
        return None
    try:
        raw = base64.b64decode("".join(data["content"].split()), validate=True)
        if len(raw) > PROFILE_MAX_BYTES:
            return None
        return _clean_profile(json.loads(raw.decode("utf-8")))
    except (ValueError, TypeError, UnicodeDecodeError, base64.binascii.Error):
        return None


async def read_public_repository(name: str):
    if not NAME_PATTERN.fullmatch(name) or name in (".", ".."):
        raise HTTPException(status_code=422, detail="Nome de repositório inválido.")
    owner = configured_owner()
    async with _client_factory() as client:
        metadata = await _read(client, f"/repos/{owner}/{name}")
        repo = _public_repo(metadata, owner)
        if repo is None:
            raise HTTPException(status_code=404, detail="Repositório público não encontrado.")
        readme_data = await _read(client, f"/repos/{owner}/{name}/readme", optional=True)
        profile_data = await _read(client, f"/repos/{owner}/{name}/contents/{PROFILE_PATH}", optional=True)

    readme = ""
    if isinstance(readme_data, dict) and readme_data.get("encoding") == "base64":
        if isinstance(readme_data.get("content"), str) and int(readme_data.get("size") or 0) <= 128000:
            try:
                raw = base64.b64decode(readme_data["content"], validate=False)
                readme = raw[:README_PREVIEW_BYTES].decode("utf-8", errors="replace")
            except (ValueError, TypeError, base64.binascii.Error):
                readme = ""
    return {
        **repo,
        "readme_preview": readme,
        "readme_truncated": len(readme.encode("utf-8")) >= README_PREVIEW_BYTES,
        "codax_profile": _decode_profile(profile_data),
    }
