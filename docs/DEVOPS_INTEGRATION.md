# Integração Codax + DevOps Control Center (fase 1)

O módulo `backend/app/devops_monitoring.py` adapta ao Python a lógica de filtros e resumo da API demonstrativa do repositório `juniordev830/devops-control-center`. O repositório de origem permanece intacto.

- `filter_pipelines`: filtra execuções por status e nome parcial do repositório.
- `summarize_pipelines`: total, contagem por estado e taxa de sucesso de execuções concluídas.
- `backend/tests/test_devops_monitoring.py`: testes unitários de filtros, validação e métricas.

**Limites desta fase:** módulo isolado, sem rotas novas, sem interface, sem leitura de execuções reais do GitHub, sem agente autônomo e sem ações de escrita. Não confundir dados de demonstração com monitoramento ao vivo.

Próximas etapas propostas: conectar uma fonte de dados autenticada de leitura mínima do GitHub Actions; criar endpoints protegidos no FastAPI; adicionar painel React com estados desconhecidos claramente identificados; validar testes e controles de acesso antes de habilitar qualquer automação de escrita.

## Fase 2 — consulta pública de GitHub Actions

- `GET /api/github/repos/{repo_name}/actions`: consulta até 30 execuções recentes de workflows públicos via API oficial do GitHub, com validação do proprietário e do nome do repositório.
- Mantém o middleware de autenticação do Codax e limites de requisição; não recebe URLs arbitrárias ou credenciais no navegador.
- Retorna `source: github-actions-public` e `live: true` apenas quando a consulta à API é bem-sucedida. Não equivale a monitoramento contínuo, nem a uma auditoria completa do repositório.
- Resultados cancelados, ignorados ou sem conclusão são apresentados como `unknown`, sem classificá-los como sucesso. A amostra é limitada aos 30 últimos runs.
- Testes simulados foram adicionados, mas ainda dependem da execução do CI para confirmação.
- Próximo passo: interface visual React e paginação/caching; autenticação de escopo mínimo para repositórios privados, somente após aprovação.
