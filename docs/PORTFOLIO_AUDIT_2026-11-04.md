# Auditoria inicial do portfólio — 60 repositórios

**Data do levantamento:** 04/11/2026 · **Conta:** [juniordev830](https://github.com/juniordev830) · **Escopo:** inventário, pendências, segurança, qualidade e prioridades.

> Documento de auditoria inicial, **não** certificação de segurança. O inventário foi obtido por consultas ao GitHub. Foram verificadas as estruturas de diretórios dos 60 repositórios; a leitura detalhada de código, execução local e testes ponta a ponta **não** foram concluídos para todos. Nenhum achado abaixo deve ser interpretado como exploit confirmado.

## Resumo executivo

| Métrica | Levantamento |
|---|---:|
| Repositórios próprios acessíveis | 60 |
| Contêm arquivos de implementação ou infraestrutura | 51 |
| Contêm apenas `README.md` na raiz | 9 |
| Pull requests abertos na conta no momento da consulta | 41 |
| Issues abertas identificadas na conta | 3 |
| Projetos com histórico recente do GitHub Actions consultado | 8 |

**Critério:** “código presente” indica apenas que a raiz contém arquivos além de `README.md`, **não** que a aplicação esteja executável ou completa. O número de PRs/execuções muda com o tempo; recontar antes de decisões de merge.

## Achados confirmados por documentação e estrutura

1. **[payment-service-java](https://github.com/juniordev830/payment-service-java/issues/3):** há controles iniciais por token de serviço, mas a [issue #3](https://github.com/juniordev830/payment-service-java/issues/3) permanece aberta porque faltam TLS/gestão de segredos na implantação e identidade/autorização por proprietário. **Não publicar como solução real de pagamentos.**
2. **[controle-gastos-residenciais](https://github.com/juniordev830/controle-gastos-residenciais/issues/2):** o README documenta API .NET/SQLite, tokens opcionais para uso local e ausência de frontend React e de autenticação individual. **Não disponibilizar na internet com dados financeiros reais.**
3. **[site-e-commerce-](https://github.com/juniordev830/site-e-commerce-):** catálogo, carrinho e pedidos demonstrativos são descritos no README; **não há gateway de pagamento, cobrança ou entrega real**. Não apresentar checkout completo como recurso finalizado.
4. **[plataforma-de-recrutamento](https://github.com/juniordev830/plataforma-de-recrutamento):** demonstração com Node/Express, SQLite, JWT e testes; o README alerta que precisa de mais revisão antes de uso público. Revisar autorização por recurso/rota, cadastro, permissões e fluxos de candidatura.
5. **[sentinel-atlas](https://github.com/juniordev830/sentinel-atlas):** API, painel web, Docker e testes presentes. O README distingue camadas com dados simulados de fontes externas; não confundir demonstração com monitoramento em tempo real. Avaliar o [PR #20](https://github.com/juniordev830/sentinel-atlas/pull/20) de visibilidade do globo antes de integrar.
6. **[codax-assirtende-engenharia-ia-](https://github.com/juniordev830/codax-assirtende-engenharia-ia-):** frontend React e backend FastAPI, modos local/API externa; o README esclarece que o assistente ainda **não** altera automaticamente arquivos locais. Examinar exposição de chaves, proteção do acesso remoto e experiência de erro.
7. **[rpg-quest-python](https://github.com/juniordev830/rpg-quest-python):** a versão padrão documentada é um protótipo de combate por turnos em terminal, **não** um jogo 3D completo.
8. **[code-security-scanner](https://github.com/juniordev830/code-security-scanner):** regras estáticas simples, com possibilidade de falsos positivos e falsos negativos; não substitui ferramenta profissional de SAST.

**CI consultado:** execuções recentes de `sentinel-atlas`, `plataforma-de-recrutamento`, `codax-assirtende-engenharia-ia-`, `site-e-commerce-`, `controle-gastos-residenciais`, `payment-service-java`, `rpg-quest-python` e `code-security-scanner`. As execuções mais recentes vistas concluíram com sucesso; isso não prova ausência de defeitos, cobertura adequada ou aprovação de todos os PRs.

## Etapas de execução

### Etapa 1 — inventário e triagem

- [x] Confirmar 60 repositórios e classificar presença de arquivos na raiz.
- [x] Identificar 9 conceitos com apenas README.
- [x] Consultar backlog de PRs e issues abertas (41 PRs, 3 issues no retrato inicial).
- [ ] Separar PRs por risco, conflitos, testes e alterações sobrepostas; **nenhum merge automático**.
- [ ] Confirmar relevância e atualizar a [issue transversal #6](https://github.com/juniordev830/codax-assirtende-engenharia-ia-/issues/6), que ainda descreve 20 repositórios.

### Etapa 2 — segurança (P0 antes de exposição pública)

- [ ] Pagamentos: identidade, autorização por recurso, rotação de segredos, TLS e auditoria antes de hospedagem externa.
- [ ] Gastos: autenticação/autorizações por usuário, isolamento de dados e testes 401/403.
- [ ] Recrutamento e e-commerce: permissões por perfil/recurso, proteção de entradas, tratamento seguro de erros, operações financeiras simuladas.
- [ ] Sentinel/Codax: limites de rede, segredos, fontes de dados, modos de demonstração vs produção.
- [ ] Varredura de segredos versionados e dependências vulneráveis em **todos** os projetos; nenhuma varredura completa foi executada nesta primeira rodada. Segredos reais encontrados exigem revogação/rotação.

### Etapa 3 — testes e qualidade

- [ ] Para cada projeto: identificar comando de build/teste, rodá-lo, registrar resultado (passa/falha/não existe), anexar evidência e investigar falhas.
- [ ] Analisar dependências, duplicações, legibilidade, cobertura dos fluxos críticos e comportamento de borda.
- [ ] Abrir interfaces no navegador quando aplicável; verificar desktop, celular, teclado e estados de erro.
- [ ] Conferir `GitHub Actions` no commit exato de cada PR, não apenas uma execução antiga da main.

### Etapa 4 — melhorias e portfólio

- [ ] Corrigir P0 antes de ampliar funcionalidades ou promover implantações.
- [ ] Para cada mudança, criar branch isolada, commit, testes e PR; **não fazer merge na main** sem revisão/autorização.
- [ ] Desenvolver gradualmente os 9 conceitos com README-only e descrever fielmente seu estágio.
- [ ] Priorizar demonstrações reproduzíveis, documentação clara, screenshots reais, acessibilidade e um conjunto pequeno de projetos-farol para candidaturas.

## Inventário completo

Legenda: a coluna **situação observada** descreve exclusivamente a **estrutura da raiz**. Não é avaliação de conclusão, segurança ou qualidade.

| # | Repositório | Situação observada |
|---:|---|---|
| 1 | [`2d-platformer-csharp`](https://github.com/juniordev830/2d-platformer-csharp) | Código ou infraestrutura presente |
| 2 | [`acessibilidade-checklist`](https://github.com/juniordev830/acessibilidade-checklist) | Somente README (conceito) |
| 3 | [`achados-perdidos`](https://github.com/juniordev830/achados-perdidos) | Somente README (conceito) |
| 4 | [`agenda-servicos`](https://github.com/juniordev830/agenda-servicos) | Código ou infraestrutura presente |
| 5 | [`ai-incident-analyzer`](https://github.com/juniordev830/ai-incident-analyzer) | Código ou infraestrutura presente |
| 6 | [`ai-service-python`](https://github.com/juniordev830/ai-service-python) | Código ou infraestrutura presente |
| 7 | [`api-test-studio`](https://github.com/juniordev830/api-test-studio) | Código ou infraestrutura presente |
| 8 | [`arduino-lab`](https://github.com/juniordev830/arduino-lab) | Código ou infraestrutura presente |
| 9 | [`auth-service-go`](https://github.com/juniordev830/auth-service-go) | Código ou infraestrutura presente |
| 10 | [`bike-care`](https://github.com/juniordev830/bike-care) | Código ou infraestrutura presente |
| 11 | [`caderno-offline`](https://github.com/juniordev830/caderno-offline) | Código ou infraestrutura presente |
| 12 | [`candidaturas-tracker`](https://github.com/juniordev830/candidaturas-tracker) | Código ou infraestrutura presente |
| 13 | [`catalogo-municipios`](https://github.com/juniordev830/catalogo-municipios) | Código ou infraestrutura presente |
| 14 | [`cifras-transpositor`](https://github.com/juniordev830/cifras-transpositor) | Código ou infraestrutura presente |
| 15 | [`codax-assirtende-engenharia-ia-`](https://github.com/juniordev830/codax-assirtende-engenharia-ia-) | Código ou infraestrutura presente |
| 16 | [`code-security-scanner`](https://github.com/juniordev830/code-security-scanner) | Código ou infraestrutura presente |
| 17 | [`codvision`](https://github.com/juniordev830/codvision) | Código ou infraestrutura presente |
| 18 | [`coleta-seletiva`](https://github.com/juniordev830/coleta-seletiva) | Somente README (conceito) |
| 19 | [`comparador-json`](https://github.com/juniordev830/comparador-json) | Código ou infraestrutura presente |
| 20 | [`consumo-energia`](https://github.com/juniordev830/consumo-energia) | Somente README (conceito) |
| 21 | [`contratos-prazos`](https://github.com/juniordev830/contratos-prazos) | Código ou infraestrutura presente |
| 22 | [`controle-gastos-residenciais`](https://github.com/juniordev830/controle-gastos-residenciais) | Código ou infraestrutura presente |
| 23 | [`corrida-maluca-`](https://github.com/juniordev830/corrida-maluca-) | Código ou infraestrutura presente |
| 24 | [`database-migration-auditor`](https://github.com/juniordev830/database-migration-auditor) | Código ou infraestrutura presente |
| 25 | [`despensa-validades`](https://github.com/juniordev830/despensa-validades) | Somente README (conceito) |
| 26 | [`devops-control-center`](https://github.com/juniordev830/devops-control-center) | Código ou infraestrutura presente |
| 27 | [`diario-leitura`](https://github.com/juniordev830/diario-leitura) | Somente README (conceito) |
| 28 | [`distributed-task-queue`](https://github.com/juniordev830/distributed-task-queue) | Código ou infraestrutura presente |
| 29 | [`divide-viagem`](https://github.com/juniordev830/divide-viagem) | Código ou infraestrutura presente |
| 30 | [`documentos-validade`](https://github.com/juniordev830/documentos-validade) | Código ou infraestrutura presente |
| 31 | [`ebd-planejador`](https://github.com/juniordev830/ebd-planejador) | Código ou infraestrutura presente |
| 32 | [`empresta-comunidade`](https://github.com/juniordev830/empresta-comunidade) | Código ou infraestrutura presente |
| 33 | [`escala-equipes`](https://github.com/juniordev830/escala-equipes) | Código ou infraestrutura presente |
| 34 | [`estoque-rastreavel`](https://github.com/juniordev830/estoque-rastreavel) | Código ou infraestrutura presente |
| 35 | [`feature-flags-service`](https://github.com/juniordev830/feature-flags-service) | Código ou infraestrutura presente |
| 36 | [`fila-atendimento`](https://github.com/juniordev830/fila-atendimento) | Somente README (conceito) |
| 37 | [`food-intelligence-`](https://github.com/juniordev830/food-intelligence-) | Código ou infraestrutura presente |
| 38 | [`garantias-compras`](https://github.com/juniordev830/garantias-compras) | Código ou infraestrutura presente |
| 39 | [`helpdesk-suporte`](https://github.com/juniordev830/helpdesk-suporte) | Código ou infraestrutura presente |
| 40 | [`infrastructure-as-code-lab`](https://github.com/juniordev830/infrastructure-as-code-lab) | Código ou infraestrutura presente |
| 41 | [`observability-platform`](https://github.com/juniordev830/observability-platform) | Código ou infraestrutura presente |
| 42 | [`oficina-digital`](https://github.com/juniordev830/oficina-digital) | Código ou infraestrutura presente |
| 43 | [`orcamento-freelancer`](https://github.com/juniordev830/orcamento-freelancer) | Código ou infraestrutura presente |
| 44 | [`order-service-csharp`](https://github.com/juniordev830/order-service-csharp) | Código ou infraestrutura presente |
| 45 | [`payment-service-java`](https://github.com/juniordev830/payment-service-java) | Código ou infraestrutura presente |
| 46 | [`plataforma-de-recrutamento`](https://github.com/juniordev830/plataforma-de-recrutamento) | Código ou infraestrutura presente |
| 47 | [`puzzle-adventure-ts`](https://github.com/juniordev830/puzzle-adventure-ts) | Código ou infraestrutura presente |
| 48 | [`quiz-sala`](https://github.com/juniordev830/quiz-sala) | Código ou infraestrutura presente |
| 49 | [`relatorio-altomatizado-de-contas-`](https://github.com/juniordev830/relatorio-altomatizado-de-contas-) | Código ou infraestrutura presente |
| 50 | [`reserva-salas`](https://github.com/juniordev830/reserva-salas) | Código ou infraestrutura presente |
| 51 | [`retro-arcade-cpp`](https://github.com/juniordev830/retro-arcade-cpp) | Código ou infraestrutura presente |
| 52 | [`revisao-espacada`](https://github.com/juniordev830/revisao-espacada) | Código ou infraestrutura presente |
| 53 | [`rpg-quest-python`](https://github.com/juniordev830/rpg-quest-python) | Código ou infraestrutura presente |
| 54 | [`secure-api-gateway`](https://github.com/juniordev830/secure-api-gateway) | Código ou infraestrutura presente |
| 55 | [`sentinel-atlas`](https://github.com/juniordev830/sentinel-atlas) | Código ou infraestrutura presente |
| 56 | [`site-e-commerce-`](https://github.com/juniordev830/site-e-commerce-) | Código ou infraestrutura presente |
| 57 | [`space-shooter-js`](https://github.com/juniordev830/space-shooter-js) | Código ou infraestrutura presente |
| 58 | [`trilhas-locais`](https://github.com/juniordev830/trilhas-locais) | Somente README (conceito) |
| 59 | [`voluntariado-hub`](https://github.com/juniordev830/voluntariado-hub) | Somente README (conceito) |
| 60 | [`web-dashboard-ts`](https://github.com/juniordev830/web-dashboard-ts) | Código ou infraestrutura presente |

## Atualização de execução — 04/11/2026

Esta seção registra **código e testes reais em PRs ainda não integrados**, não uma declaração de prontidão para produção:

| Repositório | Entrega na branch | Validação |
|---|---|---|
| [controle-gastos-residenciais — PR #14](https://github.com/juniordev830/controle-gastos-residenciais/pull/14) | Consulta GET por ID de pessoas e transações, testes HTTP 404/401 e documentação | [CI aprovado no último commit da PR](https://github.com/juniordev830/controle-gastos-residenciais/actions/runs/41825911351) |
| [controle-gastos-residenciais — PR #15](https://github.com/juniordev830/controle-gastos-residenciais/pull/15) | Modo de autenticação obrigatória com falha segura, rejeição de cabeçalhos ambíguos, respostas sem cache e limite de requisição de 16 KiB | [CI aprovado com o teste HTTP 413](https://github.com/juniordev830/controle-gastos-residenciais/actions/runs/41830217559) |
| [payment-service-java — PR #16](https://github.com/juniordev830/payment-service-java/pull/16) | Rejeição de Authorization duplicado, no-store e cabeçalhos de proteção HTTP; mensagens de falha de configuração genéricas | [CI aprovado](https://github.com/juniordev830/payment-service-java/actions/runs/41830346847) |
| [secure-api-gateway — PR #3](https://github.com/juniordev830/secure-api-gateway/pull/3) | Cabeçalhos de origem e de autenticação mais rigorosos, testes de requisições rejeitadas | [CI aprovado no commit do PR](https://github.com/juniordev830/secure-api-gateway/actions/runs/41830590023) |

**Pendências críticas que permanecem:** identidade por usuário e autorização por recurso nos dois projetos financeiros, TLS, rotação de segredos, persistência de produção e implantação revisada. A proteção por tokens de operador **não** fornece isolamento entre usuários. A documentação de 60 repositórios não prova que os outros projetos foram auditados linha a linha.

**Política confirmada:** todos os PRs desta atualização continuam separados, sem merge na `main`.

## Prioridades validadas — 04/11/2026

A validação de código confirma que os dois serviços financeiros usam tokens compartilhados, mas não associam dados a contas autenticadas. Autenticação sem autorização por proprietário não resolve o isolamento.

1. **P0 — Identidade e isolamento por conta:** introduzir usuário/residência no Controle de Gastos e proprietário de pagamento no Java. Exigir filtros por conta em listagens, detalhes, resumos e escritas. Testar dois usuários com dados distintos, 401/403 e negação de acesso cruzado.
2. **P0 — Integridade e publicação segura:** idempotência de criação no Payment Service, migrations, backup/restore, TLS e configuração externa revisada.
3. **P1 — Gestão de segredos:** rotação, revogação, armazenamento seguro e logs sem credenciais.
4. **P1 — Testes de segurança:** matriz de endpoints/papéis, integração com banco e testes negativos de acesso entre contas.

Documentação técnica nas branches em revisão: [Controle de Gastos](https://github.com/juniordev830/controle-gastos-residenciais/blob/security/require-local-auth-config-20261104/docs/SECURITY_PRIORITIES_2026-11-04.md) e [Payment Service Java](https://github.com/juniordev830/payment-service-java/blob/security/reject-ambiguous-authorization-20261104/docs/SECURITY_PRIORITIES_2026-11-04.md).

**Status:** prioridades verificadas e documentadas; nenhuma implementação de conta multiusuária foi concluída nem integrada à `main`.

## Fundação de políticas por proprietário — 04/11/2026

As primeiras implementações independentes dos modelos de acesso já estão em revisão:

- [Controle de Gastos — PR #16](https://github.com/juniordev830/controle-gastos-residenciais/pull/16): política de vínculos entre usuário e residência, papéis leitor/editor/administrador e testes xUnit para impedir acesso cruzado e rejeitar papéis desconhecidos. A suíte roda no GitHub Actions.
- [Payment Service Java — PR #17](https://github.com/juniordev830/payment-service-java/pull/17): política de operações por proprietário e escopo com testes JUnit para negar leitura/criação entre contas. [CI aprovado](https://github.com/juniordev830/payment-service-java/actions/runs/41832834351).

**Limite crítico:** essas são regras isoladas, ainda **não chamadas pelos endpoints**. Não há login multiusuário nem autorização persistida. As próximas etapas devem implementar identidade validada no servidor, propriedades de conta/residência no banco, migrations e testes de integração por recurso antes de expor as APIs. Os PRs ficam abertos e não são mesclados à main.

## Próxima rodada de trabalho

1. **P0:** aprofundar a [issue de autenticação do controle de gastos](https://github.com/juniordev830/controle-gastos-residenciais/issues/2) e a [issue de pagamentos](https://github.com/juniordev830/payment-service-java/issues/3), conferindo o código atual contra os riscos documentados.
2. **P1:** analisar PRs abertos dos projetos de maior impacto (segurança e visual), verificar CI e evitar propostas duplicadas.
3. **P1:** registrar build/teste reproduzível e status real nos 8 projetos-farol.
4. **P2:** criar um escopo técnico mínimo para cada projeto só-README, sem afirmar funcionalidades ainda inexistentes.

**Política de alteração:** mudanças futuras ficam em branches distintas, por repositório e objetivo, com PR; sem merge direto nem alteração de backend fora do escopo.
