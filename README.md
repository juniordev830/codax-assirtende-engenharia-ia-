# J.A.R.V.I.S. Dev — Codax

Assistente de programação em português do Brasil, com interface React, API local FastAPI e integração com a OpenAI Responses API. A base do projeto inclui registro persistente de tarefas e contabilização local aproximada do uso da API.

## Estrutura do repositório

```text
/
├── backend/
│   ├── app/
│   │   ├── main.py          # Rotas FastAPI e integração com a IA
│   │   ├── budget.py        # Estimativa e registro local de orçamento
│   │   └── task_manager.py  # Tarefas e persistência SQLite
│   ├── tests/               # Testes automatizados
│   ├── .env.example         # Modelo de configuração sem segredos
│   └── requirements.txt     # Dependências Python
├── frontend/
│   ├── src/
│   │   └── App.jsx          # Interface principal de conversa
│   └── package.json         # Scripts e dependências React/Vite
├── docs/
│   ├── ARCHITECTURE.md      # Arquitetura, fluxo e endpoints
│   └── ROADMAP.md           # Etapas implementadas e próximas entregas
├── .gitignore
└── README.md
```

Para detalhes técnicos, consulte [Arquitetura](docs/ARCHITECTURE.md) e [Plano de desenvolvimento](docs/ROADMAP.md).

## O que existe hoje

- Interface React para conversar por texto.
- Entrada de voz e respostas faladas, conforme suporte do navegador.
- API FastAPI com integração à OpenAI Responses API.
- Endpoints para listar, criar e atualizar tarefas persistidas em SQLite.
- Registro local aproximado de consumo e controle preventivo de orçamento.
- Instruções e exemplos de configuração.

**Limitações atuais:** o Codax ainda não mantém memória pessoal persistente de conversas, não consulta automaticamente o Obsidian e não executa comandos nem altera arquivos do computador. O armazenamento atual de tarefas e consumo não é memória de conversa.

## Requisitos

- Windows 10
- Python 3.10+
- Node.js LTS
- Chave da API OpenAI com uso/faturamento de API habilitado
- VS Code (recomendado)

**Importante:** a assinatura do ChatGPT e o uso da API são serviços/faturamentos separados. A API pode gerar cobranças conforme o uso.

## Segurança

- A chave fica somente no arquivo local `backend/.env`; nunca a coloque no frontend nem faça commit dela.
- `.env` está listado no `.gitignore`.
- O banco local fica em `backend/.jarvis_data/` e não deve ser enviado ao Git.
- Não cole chaves, senhas ou tokens na conversa.
- O orçamento local é uma estimativa preventiva, não um limite financeiro garantido. Confira também o painel oficial de uso e cobrança.

## 1. Configurar a chave e o orçamento

1. Acesse https://platform.openai.com/api-keys e crie uma chave.
2. Guarde-a com segurança.
3. Dentro de `backend/`, copie `.env.example` para um arquivo chamado `.env`.
4. Edite `backend/.env` localmente. Não compartilhe nem envie esse arquivo ao GitHub.

Exemplo de configuração:

```dotenv
OPENAI_API_KEY=sua_chave_real_aqui
OPENAI_MODEL=gpt-5.4-mini
JARVIS_MONTHLY_BUDGET_USD=4.50
JARVIS_INPUT_PRICE_PER_MILLION=0.75
JARVIS_OUTPUT_PRICE_PER_MILLION=4.50
```

O valor padrão em dólares busca ajudar a manter o uso reduzido, mas o equivalente em reais varia com câmbio e impostos. Confira os preços oficiais do modelo antes de alterar os valores por token.

## 2. Iniciar o backend

Abra um PowerShell na pasta `backend`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

Se a ativação do ambiente virtual for bloqueada:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

Confira `http://127.0.0.1:8765/api/health`. O campo `ai_configured` deve ser `true` quando a chave estiver carregada. A documentação interativa da API fica em `http://127.0.0.1:8765/docs`.

## 3. Iniciar a interface

Abra outro PowerShell na pasta `frontend`:

```powershell
npm install
npm run dev
```

Abra o endereço local mostrado pelo Vite, normalmente `http://127.0.0.1:5173`.

## 4. Endpoints locais

- `GET /api/health`: estado do backend e configuração da IA.
- `GET /api/budget`: orçamento configurado, gasto registrado e saldo estimado do mês UTC.
- `GET /api/tasks`: lista tarefas.
- `POST /api/tasks`: cria tarefa.
- `GET /api/tasks/{task_id}`: consulta tarefa.
- `PATCH /api/tasks/{task_id}`: atualiza estado, progresso e etapas.
- `POST /api/chat`: envia uma mensagem para a IA e registra o uso retornado.

Estados de tarefa disponíveis: `planned`, `running`, `waiting_approval`, `completed`, `failed` e `cancelled`. Nesta versão, as tarefas são registradas e acompanhadas; não são executadas automaticamente.

## 5. Executar testes

Na pasta `backend`, com o ambiente virtual ativado:

```powershell
python -m unittest discover -s tests -v
```

Os testes precisam ser executados no ambiente local para confirmar a compatibilidade com a instalação do usuário.

## 6. Voz

Use Microsoft Edge ou Google Chrome atualizado. O reconhecimento de voz depende do navegador e da permissão do microfone; a fala de respostas usa a síntese de voz do navegador.

## Fluxo de desenvolvimento

- Desenvolver na branch `feature/jarvis-foundation` ou em uma branch de tarefa.
- Não alterar a branch principal diretamente.
- Revisar as mudanças no pull request antes de fazer merge.
- Não marcar funcionalidades como concluídas sem implementação e validação reais.

Pull request de rascunho: https://github.com/juniordev830/codax-assirtende-engenharia-ia-/pull/1
