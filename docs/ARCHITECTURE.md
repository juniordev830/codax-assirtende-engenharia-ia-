# Arquitetura do J.A.R.V.I.S. Dev

## Visão geral

O projeto está separado em duas aplicações independentes:

- `frontend/`: interface React + Vite, executada no navegador.
- `backend/`: API FastAPI, integração com a OpenAI e persistência SQLite.
- `docs/`: documentação técnica, decisões e planejamento.
- `.gitignore`: exclui segredos, ambientes virtuais, dependências e dados locais.

## Fluxo de uma conversa

1. A interface React envia a mensagem para `POST /api/chat`.
2. A API verifica se existe `OPENAI_API_KEY` e estima o custo da chamada.
3. A API chama a OpenAI Responses API.
4. O backend devolve a resposta e registra o uso estimado/retornado.
5. A interface exibe a resposta e, se habilitado, usa a síntese de voz do navegador.

## Backend

- `backend/app/main.py`: rotas HTTP, validação, integração com o provedor de IA.
- `backend/app/budget.py`: controle local aproximado de orçamento.
- `backend/app/task_manager.py`: persistência de tarefas e uso em SQLite.
- `backend/tests/`: testes automatizados do backend.
- `backend/.env.example`: modelo de configuração sem segredos.
- `backend/.env`: configuração local privada; nunca versionar.

## Frontend

- `frontend/src/App.jsx`: tela principal e interação de chat.
- `frontend/package.json`: dependências e scripts do Vite.
- Arquivos de estilos e ponto de entrada ficam em `frontend/src/`.

## Dados e segurança

- Banco local: `backend/.jarvis_data/jarvis.sqlite3`.
- Chave de API deve ficar exclusivamente em `backend/.env`.
- Não enviar banco local, `.env`, `.venv/`, `node_modules/` ou `dist/` ao Git.
- O assistente ainda não tem execução autônoma de comandos nem acesso genérico aos arquivos do computador.
- Qualquer futura edição de arquivos ou execução de comandos deve usar permissões limitadas e aprovação para ações importantes.

## Endpoints principais

- `GET /api/health`: saúde da API e indicação se a chave foi configurada.
- `GET /api/budget`: resumo local do orçamento.
- `GET /api/tasks`: lista tarefas.
- `POST /api/tasks`: cria tarefa.
- `GET /api/tasks/{task_id}`: consulta tarefa.
- `PATCH /api/tasks/{task_id}`: atualiza estado, progresso ou etapas.
- `POST /api/chat`: envia mensagem para a IA.

## Portas locais

- Frontend Vite: `http://127.0.0.1:5173`
- Backend FastAPI: `http://127.0.0.1:8765`
- Documentação interativa FastAPI: `http://127.0.0.1:8765/docs`
