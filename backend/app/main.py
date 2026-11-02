import os
import re
import hmac
import time
from collections import OrderedDict
from threading import Lock
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import APIConnectionError, APIStatusError, AuthenticationError, AsyncOpenAI, RateLimitError
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Literal

from app.github_readonly import list_public_repositories, read_public_repository
from app.code_inspection import list_reviewable_files, inspect_public_source
from app.ai_code_review import review_with_ai

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
SYSTEM_INSTRUCTIONS = """
Você é J.A.R.V.I.S. Dev, um assistente de programação em português do Brasil.
Ajude o usuário a aprender, entender erros, planejar e implementar software.
Seja direto, didático e honesto. Explique riscos antes de sugerir comandos destrutivos.
Você não tem acesso ao computador, terminal, arquivos ou GitHub nesta versão.
Nunca diga que executou uma ação externa. Forneça código e passos seguros quando solicitado.
Não solicite que o usuário envie chaves de API, senhas ou tokens pelo chat.
"""

app = FastAPI(title="JARVIS Dev Local API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# Bounded per-process limiter. Configure a shared edge limiter for multiple workers.
_buckets = OrderedDict()
_bucket_lock = Lock()
def _limited(host: str) -> bool:
    now = time.monotonic()
    with _bucket_lock:
        started, count = _buckets.pop(host, (now, 0))
        if now - started >= 60:
            started, count = now, 0
        _buckets[host] = (started, count + 1)
        while len(_buckets) > 10000:
            _buckets.popitem(last=False)
        return count >= 20

@app.middleware("http")
async def access_control(request: Request, call_next):
    if request.url.path.startswith("/api/") and request.method != "OPTIONS":
        host = request.client.host if request.client else ""
        if (request.method == "POST" or request.url.path.startswith("/api/github/")) and _limited(host):
            return JSONResponse({"detail": "Muitas requisições. Aguarde um minuto."}, status_code=429, headers={"Retry-After": "60"})
        if request.url.path not in {"/api/health", "/api/session"}:
            token = os.getenv("CODAX_ACCESS_TOKEN", "")
            local = host in {"127.0.0.1", "::1", "testclient"}
            if not token and not local:
                return JSONResponse({"detail": "Configure CODAX_ACCESS_TOKEN antes do acesso remoto."}, status_code=503)
            if token:
                if len(token) < 32:
                    return JSONResponse({"detail": "Configure um token de acesso com pelo menos 32 caracteres."}, status_code=503)
                authorization = request.headers.get("authorization", "")
                supplied = authorization[7:] if authorization.startswith("Bearer ") else ""
                cookie = request.cookies.get("codax_session", "")
                valid_cookie = False
                try:
                    expiry, signature = cookie.split(".", 1)
                    expected = hmac.new(token.encode(), ("codax:" + expiry).encode(), "sha256").hexdigest()
                    valid_cookie = int(expiry) > time.time() and hmac.compare_digest(signature, expected)
                except (ValueError, TypeError):
                    pass
                if not (hmac.compare_digest(supplied.encode("utf-8"), token.encode("utf-8")) or valid_cookie):
                    return JSONResponse({"detail": "Autenticação necessária."}, status_code=401)
                if valid_cookie and request.method == "POST":
                    allowed = os.getenv("CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173").split(",")
                    if request.headers.get("origin") not in allowed:
                        return JSONResponse({"detail": "Origem não autorizada."}, status_code=403)
    return await call_next(request)

@app.get("/api/github/repos")
async def github_repositories():
    return await list_public_repositories()


@app.get("/api/github/repos/{repo_name}/files")
async def github_repository_files(repo_name: str):
    return await list_reviewable_files(repo_name)


@app.get("/api/github/repos/{repo_name}/source")
async def github_repository_source(repo_name: str, path: str):
    return await inspect_public_source(repo_name, path)


class AIReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: str = Field(min_length=1, max_length=220)
    expected_sha: str = Field(min_length=40, max_length=40)
    confirmed_external_processing: Literal[True]


@app.post("/api/github/repos/{repo_name}/ai-review")
async def github_ai_review(repo_name: str, payload: AIReviewRequest):
    # The explicit confirmation and expected file SHA are mandatory.
    return await review_with_ai(repo_name, payload.path, payload.expected_sha)


@app.get("/api/github/repos/{repo_name}")
async def github_repository(repo_name: str):
    return await read_public_repository(repo_name)


class SessionRequest(BaseModel):
    token: str = Field(min_length=1, max_length=512)

@app.post("/api/session")
def session(payload: SessionRequest, request: Request, response: Response):
    token = os.getenv("CODAX_ACCESS_TOKEN", "")
    allowed = os.getenv("CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173").split(",")
    if request.headers.get("origin") not in allowed:
        raise HTTPException(status_code=403, detail="Origem não autorizada.")
    if len(token) < 32:
        raise HTTPException(status_code=503, detail="Configure um token de acesso com pelo menos 32 caracteres.")
    if not hmac.compare_digest(payload.token.encode("utf-8"), token.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Token inválido.")
    expiry = str(int(time.time()) + 3600)
    signature = hmac.new(token.encode(), ("codax:" + expiry).encode(), "sha256").hexdigest()
    response.set_cookie("codax_session", expiry + "." + signature, httponly=True, samesite="strict",
                        secure=request.url.scheme == "https", max_age=3600)
    return {"authenticated": True}


# Previous turns are supplied by the client, never stored on the server.
# Strict role validation prevents callers from injecting system/developer roles.
class ChatTurn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatTurn] = Field(default_factory=list, max_length=12)

    @model_validator(mode="after")
    def validate_history_budget(self):
        if sum(len(turn.content) for turn in self.history) > 12000:
            raise ValueError("O histórico ultrapassa o limite de 12000 caracteres.")
        return self


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "jarvis-dev-local",
        "ai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "model": MODEL,
        "time_utc": datetime.now(timezone.utc).isoformat(),
    }


def local_reply(message: str) -> str:
    """Small deterministic helper for offline use; this is not a generative AI model."""
    normalized = message.casefold()
    # Match greetings as whole words/phrases, not arbitrary substrings (e.g. "coisas").
    if re.search(r"\b(?:olá|ola|oi|bom dia|boa tarde|boa noite)\b", normalized):
        return "Olá! Estou no modo local, sem chave de API e sem cobrança de IA. Minhas respostas são limitadas e baseadas em regras simples."
    if any(word in normalized for word in ("ajuda", "comandos", "o que você faz", "o que voce faz")):
        return (
            "Modo local ativo. Posso orientar sobre comandos comuns de desenvolvimento: "
            "git status para ver alterações, pytest para testes Python, npm test para testes JavaScript "
            "e npm run build para compilar um frontend. Ainda não executo esses comandos nem acesso seus arquivos."
        )
    if "git status" in normalized or "git" in normalized:
        return "Para conferir o estado do repositório, abra o terminal na pasta do projeto e execute `git status`. Eu não executo o comando neste modo."
    if "pytest" in normalized or "teste python" in normalized:
        return "Para rodar os testes Python, entre na pasta do projeto e execute `python -m pytest -q`. Leia a saída para localizar testes que falharam."
    if "npm" in normalized or "javascript" in normalized or "typescript" in normalized:
        return "Em projetos Node.js, `npm install` instala dependências, `npm test` executa testes se houver script configurado e `npm run build` compila se o projeto definir esse script."
    if "python" in normalized:
        return "Para verificar a versão do Python, execute `python --version`. Para testar um projeto com pytest, use `python -m pytest -q`. Não compartilhe senhas nem tokens."
    return (
        "Estou funcionando no modo local, sem chamar uma IA externa. Minhas respostas offline são limitadas. "
        "Posso ajudar com orientações básicas de Git, Python e Node.js; para análise generativa mais ampla, "
        "a integração opcional com a API de IA pode ser configurada no backend."
    )


@app.post("/api/chat")
async def chat(payload: ChatRequest):
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="A mensagem não pode estar vazia.")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"reply": local_reply(message), "mode": "local", "model": "rules"}

    try:
        async with AsyncOpenAI(api_key=api_key, timeout=45.0, max_retries=1) as client:
            response = await client.responses.create(
                model=MODEL,
                instructions=SYSTEM_INSTRUCTIONS,
                input=[
                    *[{"role": turn.role, "content": turn.content} for turn in payload.history],
                    {"role": "user", "content": message},
                ],
                max_output_tokens=900,
            )
        answer = (response.output_text or "").strip()
        if not answer:
            raise HTTPException(status_code=502, detail="A IA não retornou texto. Tente novamente.")
        return {"reply": answer, "mode": "openai", "model": MODEL}
    except HTTPException:
        raise
    except AuthenticationError:
        raise HTTPException(
            status_code=503,
            detail="A chave da API foi recusada. Confira OPENAI_API_KEY no arquivo backend/.env.",
        ) from None
    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="A API atingiu um limite de uso ou não há saldo disponível. Confira seu painel de API.",
        ) from None
    except APIConnectionError:
        raise HTTPException(
            status_code=502,
            detail="Não consegui conectar à API de IA. Verifique sua internet e tente novamente.",
        ) from None
    except APIStatusError:
        raise HTTPException(
            status_code=502,
            detail="O provedor de IA retornou um erro. Tente novamente em instantes.",
        ) from None
