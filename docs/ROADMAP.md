# Visão e plano de desenvolvimento do Codax

## Visão do produto

O Codax é o auxiliar pessoal de programação do João, inspirado nas capacidades do J.A.R.V.I.S. do Homem de Ferro. O objetivo não é criar apenas um chatbot: é construir um assistente multimodal, contextual, com memória persistente, capaz de compreender projetos autorizados, planejar tarefas, usar ferramentas, verificar resultados e explicar suas ações.

A referência é ficcional; cada capacidade será implementada com tecnologia real, de forma incremental e validada. Nunca apresentar uma capacidade como pronta sem implementação e teste.

## Princípios obrigatórios de projeto

1. **Voz natural:** conversar por fala e texto, permitir interrupções e manter contexto.
2. **Memória controlada pelo usuário:** guardar histórico e preferências úteis, permitir consultar, corrigir, exportar e apagar memórias.
3. **Contexto de trabalho:** acessar apenas projetos, arquivos, repositórios e notas que o usuário autorizar.
4. **Planejamento e execução:** decompor pedidos em etapas, informar progresso, executar ações permitidas e conferir os resultados.
5. **Ferramentas reais:** ler e editar código, executar testes e comandos permitidos, consultar GitHub e Obsidian por integrações explícitas.
6. **Supervisão e segurança:** pedir aprovação para ações destrutivas, publicação, mudanças importantes, instalação de programas e operações fora das permissões concedidas.
7. **Transparência:** explicar o que fez, o que falhou, quais arquivos mudou e quais verificações executou.
8. **Custo previsível:** priorizar modelos e ferramentas econômicos, limitar chamadas quando possível e mostrar estimativas; controles locais não são garantia absoluta de cobrança.
9. **Resiliência:** registrar tarefas e estado para recuperação após reinício, com logs úteis e erros compreensíveis.
10. **Computador modesto:** projetar para Windows e recursos limitados; não exigir modelos locais grandes nem serviços caros como premissa.

## Implementado no repositório

- [x] Interface React para conversa por texto.
- [x] Controles de microfone e síntese de voz dependentes do navegador.
- [x] API FastAPI e integração com OpenAI Responses API.
- [x] Registro local de tarefas em SQLite.
- [x] Registro local aproximado do uso da API e estimativa preventiva de orçamento.
- [x] Exemplo de configuração sem chave real.
- [x] Documentação de instalação, arquitetura e endpoints.

## Roadmap por fases

### Fase 0 — Base confiável
- [ ] Executar os testes no Windows e corrigir falhas reais.
- [ ] Confirmar instalação reproduzível de frontend e backend.
- [ ] Exibir erros de conexão e configuração com clareza.
- [ ] Manter desenvolvimento em branch de funcionalidade e revisar antes de merge.

### Fase 1 — Conversa e memória
- [ ] Persistir conversas e mensagens em SQLite.
- [ ] Retomar conversas após fechar e abrir o programa.
- [ ] Adicionar memória de longo prazo separada do histórico.
- [ ] Permitir visualizar, editar, exportar e apagar memórias.
- [ ] Recuperar apenas memórias relevantes para cada conversa.
- [ ] Evitar guardar segredos e dados sensíveis desnecessários.

### Fase 2 — Voz de assistente
- [ ] Melhorar ciclo de ouvir, responder e falar.
- [ ] Implementar interrupção da fala e estados visuais de escuta/processamento/resposta.
- [ ] Oferecer ativação por botão; considerar palavra de ativação apenas depois de avaliar privacidade, consumo e suporte técnico.
- [ ] Tornar claro quando o microfone estiver ativo.

### Fase 3 — Contexto do computador e projetos
- [ ] Permitir selecionar explicitamente pastas e projetos autorizados.
- [ ] Criar indexação local e pesquisa de código com exclusões configuráveis.
- [ ] Mostrar quais arquivos e trechos foram consultados.
- [ ] Integrar GitHub respeitando repositório, branch e permissões.
- [ ] Nunca ler todo o computador silenciosamente.

### Fase 4 — Agente de programação
- [ ] Transformar pedidos em planos com etapas e critérios de conclusão.
- [ ] Ler arquivos autorizados e propor mudanças pequenas.
- [ ] Exibir diff antes de aplicar mudanças importantes.
- [ ] Executar testes e comandos de uma lista permitida, em processo isolado quando possível.
- [ ] Reunir logs, diagnosticar falhas e tentar correções limitadas.
- [ ] Pedir aprovação para ações destrutivas, publicação, instalação e escopo novo.
- [ ] Criar checkpoints e facilitar reversão.

### Fase 5 — Obsidian como base de conhecimento
- [ ] Deixar o usuário selecionar o vault ou uma pasta específica.
- [ ] Pesquisar notas autorizadas e citar as notas usadas.
- [ ] Criar rascunhos de documentação e aprendizados para revisão.
- [ ] Escrever notas apenas conforme as permissões escolhidas.
- [ ] Não confundir conteúdo de notas com instruções de sistema confiáveis.

### Fase 6 — Painel J.A.R.V.I.S.
- [ ] Painel de conversa, voz, tarefas, progresso e cancelamento.
- [ ] Indicadores reais de backend, conexão e uso estimado.
- [ ] Visualizador de arquivos alterados e resultados de testes.
- [ ] Histórico de ações e aprovações.
- [ ] Configurações de memória, permissões, pastas e orçamento.
- [ ] Interface responsiva e acessível, sem animações pesadas desnecessárias.

### Fase 7 — Automação supervisionada
- [ ] Permitir tarefas em várias etapas com progresso persistente.
- [ ] Recuperar tarefas interrompidas e pedir decisão quando o estado for ambíguo.
- [ ] Agendar tarefas somente com consentimento explícito.
- [ ] Definir limites de tempo, custo, comandos e número de tentativas.
- [ ] Interromper com segurança quando houver incerteza ou risco.

## Critérios de conclusão

- Testes relevantes executados e resultado documentado.
- Nenhuma chave, banco pessoal ou dado privado enviado ao Git.
- Alterações desenvolvidas em `feature/jarvis-foundation` ou branch de tarefa.
- Documentação e configuração atualizadas junto ao código.
- Ações relevantes registradas; aprovações respeitadas.
- Nenhuma alegação de memória, acesso a arquivos, voz ou autonomia sem implementação e validação reais.
