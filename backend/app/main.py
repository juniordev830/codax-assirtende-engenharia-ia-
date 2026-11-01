import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import APIConnectionError, APIStatusError, AuthenticationError, AsyncOpenAI, RateLimitError
from pydantic import BaseModel, Field

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
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "jarvis-dev-local",
        "ai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "model": MODEL,
        "time_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/chat")
async def chat(payload: ChatRequest):
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="A mensagem não pode estar vazia.")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "A IA ainda não está configurada. Crie o arquivo backend/.env "
                "com sua OPENAI_API_KEY e reinicie o backend. Não cole a chave no chat."
            ),
        )

    try:
        async with AsyncOpenAI(api_key=api_key, timeout=45.0, max_retries=1) as client:
            response = await client.responses.create(
                model=MODEL,
                instructions=SYSTEM_INSTRUCTIONS,
                input=message,
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
