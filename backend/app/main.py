import os
from datetime import datetime, timezone
from math import ceil
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import APIConnectionError, APIStatusError, AuthenticationError, AsyncOpenAI, RateLimitError
from pydantic import BaseModel, Field

from .budget import (
    budget_status,
    can_afford_estimate,
    input_price_per_million,
    output_price_per_million,
)
from .task_manager import (
    create_task,
    get_task,
    initialize_storage,
    list_tasks,
    record_api_usage,
    update_task,
)

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
MAX_OUTPUT_TOKENS = 900
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
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type"],
)


@app.on_event("startup")
def startup() -> None:
    initialize_storage()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=12000)


class TaskUpdateRequest(BaseModel):
    state: str | None = None
    progress: int | None = Field(default=None, ge=0, le=100)
    steps: list[dict[str, Any]] | None = None


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "jarvis-dev-local",
        "ai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "model": MODEL,
        "time_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/budget")
def get_budget():
    return budget_status()


@app.get("/api/tasks")
def get_tasks():
    return {"tasks": list_tasks()}


@app.post("/api/tasks", status_code=201)
def post_task(payload: TaskCreateRequest):
    return create_task(payload.title, payload.description)


@app.get("/api/tasks/{task_id}")
def get_task_by_id(task_id: str):
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    return task


@app.patch("/api/tasks/{task_id}")
def patch_task(task_id: str, payload: TaskUpdateRequest):
    try:
        task = update_task(
            task_id,
            state=payload.state,
            progress=payload.progress,
            steps=payload.steps,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    if task is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    return task


@app.post("/api/chat")
async def chat(payload: ChatRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "A IA ainda não está configurada. Crie o arquivo backend/.env "
                "com sua OPENAI_API_KEY e reinicie o backend. Não cole a chave no chat."
            ),
        )

    message = payload.message.strip()
    # Conservative token estimate includes system instructions and maximum output.
    estimated_input_tokens = ceil((len(SYSTEM_INSTRUCTIONS) + len(message)) / 4)
    if not can_afford_estimate(estimated_input_tokens, MAX_OUTPUT_TOKENS):
        raise HTTPException(
            status_code=429,
            detail=(
                "A chamada foi bloqueada pelo controle de orçamento local. "
                "Confira GET /api/budget e o painel de uso da API antes de continuar."
            ),
        )

    try:
        async with AsyncOpenAI(api_key=api_key, timeout=45.0, max_retries=1) as client:
            response = await client.responses.create(
                model=MODEL,
                instructions=SYSTEM_INSTRUCTIONS,
                input=message,
                max_output_tokens=MAX_OUTPUT_TOKENS,
            )
        answer = (response.output_text or "").strip()
        if not answer:
            raise HTTPException(status_code=502, detail="A IA não retornou texto. Tente novamente.")

        usage = getattr(response, "usage", None)
        input_tokens = getattr(usage, "input_tokens", None)
        if input_tokens is None:
            input_tokens = estimated_input_tokens
        output_tokens = getattr(usage, "output_tokens", None)
        if output_tokens is None:
            output_tokens = MAX_OUTPUT_TOKENS
        record_api_usage(
            MODEL,
            input_tokens,
            output_tokens,
            input_price_per_million(),
            output_price_per_million(),
        )
        return {
            "reply": answer,
            "mode": "openai",
            "model": MODEL,
            "budget": budget_status(),
        }
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
