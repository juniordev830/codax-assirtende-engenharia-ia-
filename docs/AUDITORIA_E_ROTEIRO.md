# Auditoria inicial — J.A.R.V.I.S. Dev

Esta revisão foi feita por leitura estática do código e da documentação. Os testes e a execução local ainda precisam ser realizados.

## Estado confirmado

- O backend expõe uma API FastAPI local e chama a OpenAI Responses API.
- A interface React tem uma configuração de desenvolvimento no host local.
- A documentação é explícita: esta versão conversa sobre programação, mas não lê o sistema de arquivos, não executa comandos e não altera projetos.
- A chave da API deve ficar no `backend/.env`, fora do frontend e do Git.

## Prioridades

### P1 — Definir limites de custo e privacidade
A integração externa pode gerar custos de API separados da assinatura do ChatGPT. Documentar estimativa de uso, tratamento de erros e não registrar segredos ou conteúdo sensível nos logs.

### P1 — Criar capacidades de análise com escopo restrito
Para evoluir além do chat, começar com upload/seleção explícita de arquivos e análise somente leitura. Exibir os arquivos analisados e as alterações sugeridas; nunca aplicar mudanças silenciosamente.

### P1 — Segurança antes de automação
Se futuramente houver execução de comandos ou escrita de arquivos, implementar lista de permissões, diretório de trabalho limitado, confirmação explícita por ação, diff revisável e opção de desfazer. Não executar comandos arbitrários recebidos do modelo.

### P2 — Testes e validação
Adicionar testes para endpoint de saúde, validação de mensagens, resposta de sucesso e erros da API externa (credenciais inválidas, limite de uso, falha de rede e erro do provedor). Executar build do frontend e testes do backend antes de alegar que a aplicação está validada.

### P2 — Documentação de instalação
Documentar versões recomendadas, criação do ambiente virtual Python, instalação das dependências, configuração do `.env`, inicialização dos dois processos e portas locais. Incluir passos de solução de problemas sem pedir ao usuário que compartilhe a chave.

## Critério de portfólio
Demonstrar uma conversa funcional, tratamento de erros, configuração segura da chave, testes repetíveis e uma funcionalidade concreta de análise de código. Qualquer ferramenta de alteração de arquivos deve apresentar um diff e exigir aprovação antes de gravar.
