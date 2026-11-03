# Monitoramento de GitHub Actions no Codax

A branch de integração contém um endpoint FastAPI e um painel React para consultar execuções públicas do GitHub Actions. A implementação é somente leitura: não executa código, não dispara pipelines e não altera repositórios.

## Fluxo

1. O painel consulta `GET /api/github/repos/{repo_name}/actions`.
2. O middleware aplica os controles de sessão/acesso remoto do Codax e o limite específico de consultas de Actions.
3. O backend valida o nome e usa o proprietário configurado em `CODAX_GITHUB_OWNER`.
4. Uma única chamada GET consulta até 30 execuções na API pública do GitHub. Não há token GitHub, URL arbitrária ou redirecionamento.
5. A resposta informa origem, amostra, execuções e resumo. A interface representa a última execução da amostra, não a saúde geral do projeto.

Não é necessária uma segunda consulta de metadados: o endpoint público sem credenciais do GitHub não concede acesso a repositórios privados. Uma resposta 404 permanece erro; não vira um painel verde ou uma lista vazia de execuções.

## Classificação

| Estado ou conclusão do GitHub | Classificação no Codax |
| --- | --- |
| queued, in_progress, waiting, pending, requested | running |
| completed + success | success |
| completed + failure, timed_out ou startup_failure | failure |
| completed + cancelled, skipped, neutral ou action_required | unknown |
| Estado/conclusão ausente, inválido ou desconhecido | unknown |

A taxa de sucesso usa apenas `success / (success + failure)`. Se não houver resultados com classificação de sucesso/falha, ela é `null`. Cancelamentos e execuções ignoradas não contam como falhas. `summary.counts.unknown` mantém visíveis os resultados não classificados.

## Testes e evidências

- Testes unitários da classificação, filtros e resumo em `backend/tests/test_devops_monitoring.py`.
- Integração HTTP simulada em `backend/tests/test_github_actions_monitoring.py`: 40 repositórios com uma consulta por repositório, erros upstream, acesso remoto e estados desconhecidos.
- Execute `python -m pytest -q` na pasta backend após instalar `requirements.txt`.
- [CI da integração](https://github.com/juniordev830/codax-assirtende-engenharia-ia-/actions?query=branch%3Afeature%2Fdevops-monitoring-integration).

## Limites

A amostra abrange somente as 30 execuções retornadas; não há paginação nem cache. Abrir o painel de 40 repositórios consome 40 chamadas upstream, além das demais operações do Codax. A API pública continua sujeita à cota compartilhada do GitHub; 403/429 são apresentados como erro controlado. `live: true` indica consulta bem-sucedida naquele momento, não monitoramento contínuo.

O frontend existe na branch, mas ainda não possui teste de navegador nesta entrega. Repositórios privados, identidade GitHub com escopo mínimo e automação de escrita permanecem fora do escopo.
