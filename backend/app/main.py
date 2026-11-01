from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="JARVIS Dev Local API", version="0.1.0")

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
        "time_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/chat")
def chat(payload: ChatRequest):
    # Safe demo: no shell execution and no filesystem access.
    return {
        "reply": (
            f"Recebi sua mensagem: “{payload.message.strip()}”. "
            "Estou no modo de demonstração. A conexão com um modelo de IA "
            "será configurada no backend na próxima etapa."
        ),
        "mode": "demo",
    }
