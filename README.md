# J.A.R.V.I.S. Dev

Assistente de programação em português do Brasil, com interface React, API local FastAPI e integração com a OpenAI Responses API.

## Estado atual

- API local com endpoint de saúde `GET /api/health`.
- Endpoint de conversa `POST /api/chat` com validação de entrada.
- Mensagens vazias ou formadas somente por espaços são rejeitadas.
- Erros comuns da API externa são convertidos em mensagens controladas.
- Testes automatizados da API e execução via GitHub Actions.
- A chave da API fica no backend e nunca deve ser colocada no frontend ou enviada ao GitHub.

> O assistente ainda não executa comandos no computador, não lê arquivos locais nem altera projetos automaticamente. A interface não deve ser interpretada como prova de que essas funções existem.

## Requisitos

- Windows 10 ou superior
- Python 3.10+
- Node.js LTS
- Chave da OpenAI API com uso habilitado (o uso da API é cobrado separadamente da assinatura ChatGPT)
- VS Code (opcional)

## Configuração

### 1. Configurar a chave da API

Na pasta `backend`, copie `.env.example` para `.env` e configure sua chave localmente:

```dotenv
OPENAI_API_KEY=sua_chave_real
OPENAI_MODEL=gpt-5.4-mini
```

Nunca publique o arquivo `.env` nem compartilhe a chave. O arquivo está listado no `.gitignore`.

### 2. Iniciar a API

No PowerShell, dentro de `backend`:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

Teste `http://127.0.0.1:8765/api/health`. O campo `ai_configured` indica se a variável da chave foi carregada.

### 3. Iniciar a interface

Em outro terminal, na pasta `frontend`:

```powershell
npm install
npm run dev
```

Abra o endereço local informado pelo Vite, normalmente `http://127.0.0.1:5173`.

## Testes automatizados

Na pasta `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Os testes verificam o endpoint de saúde, o comportamento sem chave, a rejeição de mensagens em branco e uma resposta simulada da IA, sem consumir créditos da API.

O GitHub Actions executa os testes de backend em pushes para a branch principal e branches `feature/**), além de pull requests direcionados à principal.

## Arquitetura

- `frontend/`: interface React/Vite e recursos de voz do navegador.
- `backend/app/main.py`: API FastAPI, validação de mensagens e integração com a OpenAI.
- `backend/tests/`: testes automatizados de contrato da API.
- `.github/workflows/ci.yml`: verificação automatizada de testes.

## Próximas etapas

1. Adicionar histórico de conversa com limite de contexto.
2. Implementar configuração de API por interface sem expor segredos.
3. Criar análise de código em arquivos explicitamente selecionados.
4. Planejar ações locais somente com aprovação explícita, logs e limites de segurança.
5. Integrar GitHub por permissões mínimas e revisão antes de publicar alterações.
