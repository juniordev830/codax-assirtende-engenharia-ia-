# Arquitetura do J.A.R.V.I.S. Dev / Codax

## Visão do produto

O Codax é o auxiliar pessoal de programação do usuário, inspirado no J.A.R.V.I.S. do Homem de Ferro. A meta é combinar conversa por voz e texto, memória controlada pelo usuário, contexto de projetos autorizados, planejamento de tarefas, ferramentas de programação, validação de resultados e automação supervisionada.

A inspiração é ficcional; as funções precisam ser construídas e testadas com tecnologias reais. Não assumir capacidades que ainda não foram implementadas.

## Organização do repositório

- `frontend/`: interface React + Vite, executada no navegador.
- `backend/`: API FastAPI, integração com IA e persistência SQLite.
- `docs/`: documentação técnica, decisões e planejamento.
- `.gitignore`: exclui segredos, ambientes virtuais, dependências e dados locais.

## Acesso multiplataforma e remoto

A meta é oferecer uma interface web responsiva/PWA para computador, tablet e celular. O dispositivo móvel funciona como painel de controle do Codax; o host autorizado executa ferramentas e acessa o checkout do projeto.

Fluxo-alvo:
1. O navegador do usuário conecta-se por sessão autenticada.
2. Uma conexão privada VPN, como Tailscale, ou uma configuração HTTPS segura protege o acesso fora da rede local.
3. O backend valida sessão, escopo e política de aprovação antes de cada ação.
4. O serviço local executa apenas ferramentas permitidas nos repositórios autorizados.
5. Estado de tarefas, logs e resultados são enviados à interface conectada.

Requisitos:
- Manter o backend limitado a localhost por padrão até configurar acesso remoto seguro.
- Não publicar diretamente na internet terminal, shell ou API administrativa.
- Nunca expor chaves de IA ou tokens de GitHub ao frontend.
- Exigir autenticação e autorização para ações, com logs e encerramento de sessão.
- Acesso a ferramentas locais exige que o computador host esteja ligado, acordado e online.
- Começar com consulta de estado e acompanhamento; habilitar edição e execução remota somente após testes de segurança.

A interface responsiva/PWA, a autenticação e o transporte remoto ainda são requisitos futuros, não recursos atualmente disponíveis.

## Arquitetura-alvo

A arquitetura deve crescer em módulos pequenos para facilitar testes e evitar que a lógica toda fique em uma única rota:

1. **Interface:** conversa, voz, tarefas, estado do sistema, histórico, memória e aprovações.
2. **API e orquestração:** valida pedidos, administra contexto e escolhe ferramentas permitidas.
3. **Memória:** histórico de conversa separado de fatos/preferências de longo prazo, com controles do usuário.
4. **Gerenciador de tarefas:** planos, etapas, estado, progresso, cancelamento e recuperação.
5. **Ferramentas:** leitura de arquivos autorizados, Git, testes e comandos permitidos, com permissões explícitas.
6. **Conectores:** OpenAI, GitHub e Obsidian; cada integração deve ter escopo e configuração próprios.
7. **Auditoria e orçamento:** registro de ações, aprovações, erros e uso estimado da API.
8. **Camada de segurança:** validação de caminhos, comandos permitidos, limites e aprovação de operações de risco.

Esses são objetivos arquiteturais; módulos ainda não implementados não devem ser tratados como disponíveis.

## Fluxo atual de uma conversa

1. A interface React envia a mensagem para `POST /api/chat`.
2. A API verifica se existe `OPENAI_API_KEY` e estima o custo da chamada.
3. A API chama a OpenAI Responses API.
4. O backend devolve a resposta e registra o uso retornado/estimado.
5. A interface exibe a resposta e, se habilitado, usa a síntese de voz do navegador.

O histórico ainda não é persistido como memória pessoal de conversas. O SQLite existente registra tarefas e uso da API.

## Backend atual

- `backend/app/main.py`: rotas HTTP, validação e integração com o provedor de IA.
- `backend/app/budget.py`: controle local aproximado de orçamento.
- `backend/app/task_manager.py`: persistência de tarefas e uso em SQLite.
- `backend/tests/`: testes automatizados do backend.
- `backend/.env.example`: modelo de configuração sem segredos.
- `backend/.env`: configuração local privada; nunca versionar.

## Frontend atual

- `frontend/src/App.jsx`: tela principal e interação de chat.
- `frontend/package.json`: dependências e scripts do Vite.
- Arquivos de estilos e ponto de entrada ficam em `frontend/src/`.

## Segurança e permissões

- Banco local atual: `backend/.jarvis_data/jarvis.sqlite3`.
- A chave da API deve ficar exclusivamente em `backend/.env`.
- Não enviar banco local, `.env`, `.venv/`, `node_modules/` ou `dist/` ao Git.
- O assistente ainda não tem execução autônoma de comandos nem acesso genérico aos arquivos do computador.
- Futuro acesso a arquivos deve ser limitado às pastas selecionadas pelo usuário.
- Comandos devem ser permitidos por política explícita; não executar comandos arbitrários sugeridos pelo modelo sem validação.
- Operações destrutivas, publicação, instalação e mudanças relevantes precisam de aprovação.
- Mostrar arquivos alterados, resultados de testes e ações tomadas.
- O controle local de orçamento é best-effort e não garante um limite de cobrança da plataforma.
- Conteúdo lido de arquivos, repositórios e notas é dado de contexto, não instrução confiável para mudar as regras de segurança.

## Endpoints atuais

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

## Referência do plano

Consulte [ROADMAP.md](ROADMAP.md) para as fases propostas, desde testes e memória até ferramentas de programação e automação supervisionada.
