# Guia compartilhado: VS Code, Git e integração GitHub MCP

Este guia é a referência canônica dos projetos públicos `juniordev830`. Cada projeto mantém seus próprios arquivos `.vscode/tasks.json` e `.vscode/mcp.json`, pois o VS Code carrega tarefas e integrações por workspace. O objetivo é evitar dezenas de cópias de instruções idênticas.

## Abrir e validar o projeto

1. Abra a pasta do projeto no VS Code, localmente ou no Codespaces.
2. Salve as alterações antes de executar tarefas. `git add` não salva buffers do editor.
3. Abra **Ctrl+Shift+P → Tasks: Run Task** para consultar as tarefas disponíveis.
4. Escolha a tarefa de testes apropriada para o projeto (Python, Node, Go, .NET, Java etc.). Quando não houver tarefa, siga o README do próprio projeto.

## Tarefas Git

- **Git: ver estado** → consulta a branch e as alterações atuais.
- **Git: atualizar do GitHub (pull --rebase)** → atualiza a branch; conflitos exigem revisão manual.
- **Git: adicionar alterações** → prepara as alterações com `git add -A`. Revise `git status` antes para não incluir arquivos indevidos.
- **Git: criar commit** → solicita mensagem e registra o commit. Em alguns projetos, esta tarefa já prepara os arquivos antes de commitar.
- **Git: enviar para GitHub (push)** → publica commits existentes; depende das permissões do GitHub.
- **Git: salvar e enviar** → encadeia a preparação, commit e push. O encadeamento é configurado para evitar preparar duas vezes os mesmos arquivos.

Os comandos não ignoram regras de proteção, autenticação, conflitos, verificações de CI nem a necessidade de revisar modificações antes de publicar.

## GitHub MCP

A configuração do servidor está em `.vscode/mcp.json`. Ela pode ser idêntica entre projetos, por exigência da integração de workspace.

1. Use uma versão do VS Code com suporte a MCP.
2. No menu de comandos, abra **MCP: List Servers**.
3. Selecione o servidor `github`, confira o endereço e autorize a conexão.
4. Conceda apenas permissões necessárias e revise cada ação de escrita.

**Não grave tokens, credenciais ou segredos nos arquivos versionados.** Não trate a presença do servidor MCP como prova de que ele está autenticado ou de que possui permissão de escrita.

## Informações específicas por repositório

Cada repositório possui um `README.md` e um arquivo `.codax/project.json` com tecnologias, comandos de teste e foco da revisão. Use essas informações para executar verificações reais. Este documento trata apenas do fluxo comum do VS Code.

Atualize aqui as instruções comuns; evite copiar novamente o texto completo para todos os projetos.
