"""Read explicitly selected source files from a verified public GitHub repository.

Never runs repository code, edits files, handles GitHub tokens, or invokes a paid AI API.
Findings are narrow, heuristic review prompts — not proven vulnerabilities.
"""
import base64
import binascii
import re
from urllib.parse import quote

from fastapi import HTTPException

from app.github_readonly import (
    _client_factory, _public_repo, _read, configured_owner, NAME_PATTERN
)

MAX_SOURCE_BYTES = 32768
MAX_FILE_LIST = 200
MAX_TREE_ENTRIES = 20000
SOURCE_EXTENSIONS = frozenset({
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".cs",
    ".c", ".cpp", ".h", ".hpp", ".rs", ".rb", ".php", ".sh", ".sql"
})
EXCLUDED_SEGMENTS = frozenset({
    ".git", ".github", ".venv", "venv", "node_modules", "vendor",
    "dist", "build", "coverage", "__pycache__", ".next", "fixtures",
    "secrets", "credentials", "private", "generated"
})
SENSITIVE_NAMES = ("secret", "token", "password", "credential", "apikey", "api_key", "private_key", "id_rsa")


def safe_source_path(path: str) -> bool:
    if not isinstance(path, str) or not path or len(path) > 220 or "\x00" in path or "\\" in path:
        return False
    segments = path.split("/")
    if any(
        not segment or segment in {".", ".."} or segment.startswith(".")
        or segment.casefold() in EXCLUDED_SEGMENTS
        for segment in segments
    ):
        return False
    name = segments[-1].casefold()
    if any(part in name for part in SENSITIVE_NAMES) or name.endswith(".min.js"):
        return False
    suffix = "." + name.rsplit(".", 1)[-1] if "." in name else ""
    return suffix in SOURCE_EXTENSIONS


async def _verified_repo(client, owner: str, name: str):
    if not NAME_PATTERN.fullmatch(name) or name in {".", ".."}:
        raise HTTPException(status_code=422, detail="Nome de repositório inválido.")
    metadata = await _read(client, f"/repos/{owner}/{name}")
    if _public_repo(metadata, owner) is None:
        raise HTTPException(status_code=404, detail="Repositório público não encontrado.")
    return metadata


async def list_reviewable_files(name: str):
    owner = configured_owner()
    async with _client_factory() as client:
        metadata = await _verified_repo(client, owner, name)
        branch = metadata.get("default_branch")
        if not isinstance(branch, str) or not re.fullmatch(r"[A-Za-z0-9_.\-/]{1,120}", branch):
            raise HTTPException(status_code=502, detail="Branch principal inválida na resposta do GitHub.")
        tree = await _read(
            client, f"/repos/{owner}/{name}/git/trees/{quote(branch, safe='')}",
            params={"recursive": "1"},
        )
    if not isinstance(tree, dict) or not isinstance(tree.get("tree"), list):
        raise HTTPException(status_code=502, detail="Árvore de arquivos inválida.")
    if tree.get("truncated") or len(tree["tree"]) > MAX_TREE_ENTRIES:
        raise HTTPException(status_code=413, detail="Repositório grande demais para listar com segurança.")
    eligible = []
    for item in tree["tree"]:
        if not isinstance(item, dict) or item.get("type") != "blob" or item.get("mode") == "120000":
            continue
        path = item.get("path")
        size = item.get("size")
        if safe_source_path(path) and isinstance(size, int) and 0 <= size <= MAX_SOURCE_BYTES:
            eligible.append({"path": path, "size": size})
    eligible.sort(key=lambda item: item["path"])
    return {
        "repository": name, "branch": branch,
        "files": eligible[:MAX_FILE_LIST], "total_eligible": len(eligible),
        "truncated": len(eligible) > MAX_FILE_LIST, "scope": "public-source-read-only"
    }


def inspect_source(source: str, path: str):
    """Bounded low-confidence hints on single lines. No evaluation or execution."""
    checks = (
        (r"\beval\s*\(", "warning", "Uso de eval",
         "Verifique se dados externos podem chegar a eval; prefira um parser específico."),
        (r"\bexec\s*\(", "warning", "Execução dinâmica",
         "Revise a origem do texto executado e evite executar código não confiável."),
        (r"\bshell\s*=\s*True\b", "warning", "Comando com shell=True",
         "Prefira argumentos em lista e shell=False; valide entradas."),
        (r"\bos\.system\s*\(", "warning", "Comando de sistema",
         "Evite concatenar entrada do usuário em comandos de sistema."),
        (r"\bdangerouslySetInnerHTML\b|\binnerHTML\s*=", "warning", "HTML dinâmico",
         "Confira sanitização e origem dos dados antes de inserir HTML."),
        (r"\b(?:TODO|FIXME)\b", "info", "Pendência no código",
         "Confirme se esta pendência continua válida e registre uma tarefa."),
        (r"^\s*except\s*:\s*(?:#.*)?$", "info", "Exceção genérica",
         "Capture exceções específicas para evitar ocultar erros inesperados."),
    )
    findings = []
    for number, line in enumerate(source.splitlines(), start=1):
        if len(findings) >= 20:
            break
        if len(line) > 1000:
            continue
        for pattern, severity, title, advice in checks:
            if re.search(pattern, line, flags=re.IGNORECASE):
                findings.append({"line": number, "severity": severity, "title": title, "suggestion": advice})
                break
    return {
        "path": path, "method": "heuristic",
        "findings": findings, "findings_truncated": len(findings) >= 20,
        "disclaimer": "Pistas baseadas em padrões, não uma auditoria de segurança ou prova de erro."
    }


async def inspect_public_source(name: str, path: str):
    if not safe_source_path(path):
        raise HTTPException(status_code=422, detail="Caminho de arquivo não permitido para análise.")
    owner = configured_owner()
    async with _client_factory() as client:
        await _verified_repo(client, owner, name)
        escaped = "/".join(quote(segment, safe="") for segment in path.split("/"))
        data = await _read(client, f"/repos/{owner}/{name}/contents/{escaped}")
    if not isinstance(data, dict) or data.get("type") != "file":
        raise HTTPException(status_code=422, detail="Selecione um arquivo regular de código.")
    size = data.get("size")
    if not isinstance(size, int) or size < 0 or size > MAX_SOURCE_BYTES:
        raise HTTPException(status_code=413, detail="Arquivo acima do limite de 32 KB.")
    if data.get("encoding") != "base64" or not isinstance(data.get("content"), str):
        raise HTTPException(status_code=422, detail="Este arquivo não está disponível como texto.")
    try:
        encoded = "".join(data["content"].split())
        raw = base64.b64decode(encoded, validate=True)
        if len(raw) > MAX_SOURCE_BYTES:
            raise HTTPException(status_code=413, detail="Arquivo acima do limite de 32 KB.")
        source = raw.decode("utf-8")
    except (binascii.Error, ValueError, UnicodeDecodeError):
        raise HTTPException(status_code=422, detail="Arquivo não é texto UTF-8 válido.") from None
    if "\x00" in source:
        raise HTTPException(status_code=422, detail="Arquivos binários não podem ser analisados.")
    return {
        "repository": name, "path": path, "size": len(raw),
        "content": source, "review": inspect_source(source, path),
        "scope": "read-only", "external_ai_used": False
    }
