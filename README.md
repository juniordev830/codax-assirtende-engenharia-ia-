# J.A.R.V.I.S. Dev

Assistente de programação em português do Brasil, com interface React e API local FastAPI. Funciona em modo local sem chave ou, opcionalmente, com integração à OpenAI Responses API.

## Estado atual

- API local com endpoint de saúde `GET /api/health`.
- Endpoint de conversa `POST /api/chat` com validação de entrada.
- Mensagens vazias ou formadas somente por espaços são rejeitadas.
- Sem `OPENAI_API_KEY`, o backend oferece respostas locais determinísticas para orientações básicas de Git, Python e Node.js.
- Com `OPENAI_API_KEY`, o backend pode usar a OpenAI Responses API; esse uso é opcional e pode gerar custos.
- Testes automatizados da API, testes de memória no frontend e execução via GitHub Actions.
- Conversas com contexto recente limitado: até 12 mensagens anteriores e 12.000 caracteres por requisição.
- Histórico opcional no armazenamento deste navegador (máximo de 40 mensagens), com opção de apagar a conversa.
- A chave da API fica no backend e nunca deve ser colocada no frontend ou enviada ao GitHub.

> O assistente ainda não executa comandos no computador, não lê arquivos locais nem altera projetos automaticamente. A interface não deve ser interpretada como prova de que essas funções existem.

## Requisitos

- Windows 10 ou superior
- Python 3.10+
- Node.js LTS
- Chave da OpenAI API apenas se quiser habilitar respostas generativas (uso da API é cobrado separadamente da assinatura ChatGPT)
- VS Code (opcional)

## Configuração

### 1. Modo local sem chave (padrão)

Você pode iniciar a aplicação sem configurar chave de IA. Nesse modo, o assistente responde a um conjunto limitado de orientações determinísticas e deixa claro que não é uma IA generativa. Não há cobrança de API.

### 2. Habilitar respostas generativas (opcional)

Se quiser usar a OpenAI, na pasta `backend`, copie `.env.example` para `.env` e configure sua chave localmente:

```dotenv
OPENAI_API_KEY=sua_chave_real
OPENAI_MODEL=gpt-5.4-mini
```

Nunca publique o arquivo `.env` nem compartilhe a chave. O arquivo está listado no `.gitignore`.

### 3. Iniciar a API

No PowerShell, dentro de `backend`:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

Teste `http://127.0.0.1:8765/api/health`. O campo `ai_configured` indica se a variável da chave foi carregada.

### 4. Iniciar a interface

Em outro terminal, na pasta `frontend`:

```powershell
npm install
npm run dev
```

Abra o endereço local informado pelo Vite, normalmente `http://127.0.0.1:5173`.

## Memória de conversa

- Cada nova mensagem enviada pelo frontend inclui uma janela de **até 12 mensagens anteriores** e **12.000 caracteres**, validada também pelo backend. A mensagem atual tem limite de 4.000 caracteres.
- A integração generativa opcional recebe esse contexto como mensagens de usuário/assistente. O **modo local sem API continua baseado em regras**: ele não gera respostas contextuais.
- O histórico aparece durante a sessão. Marcar **Salvar conversa neste navegador** grava até 40 mensagens no armazenamento local do navegador. Essa opção vem **desativada por padrão** e não sincroniza entre dispositivos.
- **Limpar conversa** apaga o histórico exibido e o histórico salvo neste navegador. Desativar o salvamento remove o histórico gravado, mas mantém as mensagens visíveis até limpar ou recarregar a página.
- O backend **não persiste conversas**; o contexto é enviado pelo próprio navegador a cada chamada. Histórico salvo pode ser lido por quem tiver acesso ao mesmo perfil do navegador.
- **Não envie senhas, tokens, credenciais ou outros segredos pelo chat.** Se a integração com a OpenAI estiver ativa, o contexto incluído na requisição é enviado à API externa.

## Testes automatizados

Na pasta `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Os testes verificam o endpoint de saúde, o modo local sem chave, a rejeição de mensagens em branco e uma resposta simulada da IA, sem consumir créditos da API.

O GitHub Actions executa os testes do backend e do frontend (incluindo verificação de dependências e build). Para testar a memória no frontend:

```powershell
cd frontend
npm test
npm run build
```

Para testar o backend sem consumir créditos de IA:

```powershell
cd backend
python -m pytest -q
```


## Arquitetura

- `frontend/`: interface React/Vite, recursos de voz e memória opcional do navegador.
- `frontend/src/chatHistory.mjs`: limite, serialização e limpeza de contexto.
- `frontend/tests/`: testes de memória executados por `npm test`.
- `backend/app/main.py`: API FastAPI, validação de mensagens e integração com a OpenAI.
- `backend/tests/`: testes automatizados de contrato da API.
- `.github/workflows/ci.yml`: testes automatizados do backend e build do frontend.

## Próximas etapas

1. Evoluir o histórico local para sincronização segura entre dispositivos, caso seja necessário, com identidade própria e política de retenção.
2. Implementar configuração de API por interface sem expor segredos.
3. Criar análise de código em arquivos explicitamente selecionados.
4. Planejar ações locais somente com aprovação explícita, logs e limites de segurança.
5. Integrar GitHub por permissões mínimas e revisão antes de publicar alterações.

## Acesso por celular/tablet

Configure `VITE_API_URL` no frontend com a URL HTTPS do backend e `CORS_ORIGINS` no backend com a origem exata do frontend. Configure `CODAX_ACCESS_TOKEN` com um segredo aleatório de pelo menos 32 caracteres; informe-o no campo de autorização da interface. A sessão dura uma hora e usa cookie HttpOnly; o segredo não é salvo no armazenamento do navegador. Prefira frontend e API no mesmo site para compatibilidade dos cookies SameSite. Acesso remoto sem token é bloqueado. O limite é de 20 requisições POST por IP/minuto por processo; não confie em cabeçalhos de proxy não verificados. Não publique HTTP sem TLS. O suporte à configuração remota não cria hospedagem automaticamente.
