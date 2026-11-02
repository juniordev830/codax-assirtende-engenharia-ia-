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
- Explorador GitHub **somente de leitura** para listar repositórios públicos e consultar prévias de README (sem token GitHub).
- Revisão inicial de código: seleção explícita de um arquivo público, visualização do texto e sugestões **heurísticas** com números de linha, gratuitas e sem IA externa.
- Análise semântica opcional com IA: exige autorização específica por arquivo e pode gerar custos adicionais de API.
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

## GitHub: leitura de projetos públicos

A aba **GitHub** do frontend lista até **100 repositórios públicos** da conta configurada em `CODAX_GITHUB_OWNER` (padrão: `juniordev830`) e permite abrir uma prévia em texto do README, limitada a 8 KB. Não existe paginação nesta primeira versão.

- `GET /api/github/repos`: lista de repositórios públicos do usuário configurado.
- `GET /api/github/repos/{repo_name}`: resumo e prévia do README público.
- Consultas são feitas do **backend** exclusivamente para `https://api.github.com`, sem enviar senhas ou tokens do GitHub pelo navegador.
- **Nenhuma rota de escrita** é criada: sem commits, exclusões, ações em issues ou pull requests; acesso a repositórios privados ainda não existe.
- O controle de autenticação do Codax também protege essas rotas no acesso remoto. As consultas GitHub compartilham o limite local de 20 requisições por IP/minuto; limites de API pública do próprio GitHub continuam aplicáveis.
- Não habilite uso remoto público sem configurar `CODAX_ACCESS_TOKEN`, HTTPS e as origens permitidas. Este recurso **não cria hospedagem**.

O Codax ainda **não interpreta automaticamente código**, não baixa projetos completos e não pode executar comandos. O modo GitHub é exclusivamente um leitor de metadados e README públicos.

## Revisão de código selecionado

Na aba **Revisão de código**, escolha um repositório público, depois um arquivo de código e pressione **Revisar arquivo selecionado**. A leitura do arquivo só acontece após esse comando explícito.

- `GET /api/github/repos/{repo_name}/files`: enumera arquivos de código elegíveis na primeira árvore da branch padrão (até 200 nomes visíveis), sem arquivos ocultos ou caminhos com nomes típicos de credenciais.
- `GET /api/github/repos/{repo_name}/source?path=...`: lê um único arquivo regular UTF-8 de até **32 KiB** após confirmar que o repositório pertence à conta configurada e é público.
- Aceita extensões de código conhecidas, não executa scripts, não modifica repositórios, não lê arquivos privados nem usa token GitHub.
- A revisão detecta **pistas simples** como `eval()`, execução dinâmica, `shell=True`, `os.system()`, HTML dinâmico, `TODO`, `FIXME` e exceções genéricas. As sugestões **não comprovam vulnerabilidades** e a ausência de achados não garante segurança.
- Na **revisão local**, o código permanece no backend apenas durante a requisição e na visualização atual do navegador; **não é enviado a um modelo externo nem gravado na memória do chat**. A revisão opcional com IA, descrita abaixo, tem comportamento diferente. Revogar acesso remoto exige encerrar a sessão correspondente no navegador.
- A listagem pode recusar repositórios gigantes ou árvores incompletas. Não existem compilação, análise de múltiplos arquivos, correções automáticas ou pull requests criadas pela aplicação.
- Mesmo em arquivos públicos, não cole segredos ou dados pessoais no chat. Confira o repositório antes de publicar código.

## Análise aprofundada opcional com IA

Depois de executar a **revisão local**, o usuário pode marcar uma confirmação explícita e clicar em **Solicitar análise com IA**. Essa ação faz **uma requisição separada**. O consentimento não é permanente; o botão não executa automaticamente após selecionar um arquivo.

- `POST /api/github/repos/{repo_name}/ai-review` recebe apenas o caminho, o SHA do arquivo visualizado e `confirmed_external_processing=true`. O backend **não confia no código enviado pelo navegador**: busca o arquivo público novamente, compara seu SHA e recusa alterações entre a prévia e o envio.
- A chamada exige `OPENAI_API_KEY` configurada **somente no backend**. Sem essa chave, o servidor devolve 503 e a revisão local gratuita continua disponível.
- Apenas arquivos públicos UTF-8 com até **12.000 caracteres** podem ser enviados. Nomes típicos de credenciais e alguns padrões de segredos no conteúdo são bloqueados; esse filtro é heurístico e **não garante detectar todas as informações sensíveis**. Leia o arquivo antes de confirmar.
- Após a confirmação, o **conteúdo completo do único arquivo escolhido** é enviado à API externa da OpenAI, sob a conta de API configurada, para identificar possíveis problemas, explicar o código e sugerir correções **textuais**. **Pode haver custos cobrados separadamente da assinatura do ChatGPT.**
- O arquivo é tratado como entrada não confiável nas instruções do modelo. A resposta é exibida como texto e pode conter erros; não há verificação automática do comportamento do programa nem execução de testes.
- O Codax **não executa código, não escreve arquivos, não faz commits e não cria pull requests** por meio deste recurso. Não envia histórico de chat nem tokens ao provedor de análise.
- A chamada é limitada pela proteção de acesso e pelo limitador atual do backend, que opera por processo. Antes de uma implantação pública, adicione quotas de gasto por usuário no provedor ou servidor e rate limiting compartilhado na borda.

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
- `frontend/tests/`: testes de memória e dos clientes de API executados por `npm test`.
- `frontend/src/githubApi.mjs`: cliente para navegação pública em projetos.
- `backend/app/github_readonly.py`: chamadas públicas de leitura GitHub, com validação de nomes e respostas.
- `backend/app/code_inspection.py`: listagem e revisão heurística de arquivos selecionados com limites estritos.
- `backend/app/ai_code_review.py`: revisão opcional de um arquivo pela OpenAI, somente com consentimento e sem ações de escrita.
- `frontend/src/CodeReviewPanel.jsx`: interface de revisão explícita e visualização segura de texto.
- `frontend/src/codeReviewApi.mjs`: chamadas de revisão a partir do navegador.
- `backend/app/main.py`: API FastAPI, validação de mensagens e integração com a OpenAI.
- `backend/tests/`: testes automatizados de contrato da API.
- `.github/workflows/ci.yml`: testes automatizados do backend e build do frontend.

## Próximas etapas

1. Evoluir o histórico local para sincronização segura entre dispositivos, caso seja necessário, com identidade própria e política de retenção.
2. Implementar configuração de API por interface sem expor segredos.
3. Criar análise de código em arquivos explicitamente selecionados.
4. Planejar ações locais somente com aprovação explícita, logs e limites de segurança.
5. Expandir a revisão semântica opcional de **um arquivo** para múltiplos arquivos com quotas, aprovação por arquivo e propostas de alteração revisáveis; planejar acesso privado separadamente.

## Acesso por celular/tablet

Configure `VITE_API_URL` no frontend com a URL HTTPS do backend e `CORS_ORIGINS` no backend com a origem exata do frontend. Configure `CODAX_ACCESS_TOKEN` com um segredo aleatório de pelo menos 32 caracteres; informe-o no campo de autorização da interface. A sessão dura uma hora e usa cookie HttpOnly; o segredo não é salvo no armazenamento do navegador. Prefira frontend e API no mesmo site para compatibilidade dos cookies SameSite. Acesso remoto sem token é bloqueado. O limite é de 20 requisições POST por IP/minuto por processo; não confie em cabeçalhos de proxy não verificados. Não publique HTTP sem TLS. O suporte à configuração remota não cria hospedagem automaticamente.
