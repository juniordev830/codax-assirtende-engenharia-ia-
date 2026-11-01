# Visão e plano de desenvolvimento do Codax

## Decisões pessoais definidas

A especificação completa está em [PERSONAL_SPEC.md](PERSONAL_SPEC.md). As decisões que orientam a implementação são:

- **Prioridade:** programação, GitHub e projetos de software.
- **Interação:** voz e texto, mantendo o texto como alternativa sempre disponível.
- **Acesso:** computador, tablet e celular via interface web responsiva/PWA; acesso remoto autenticado por VPN privada ou HTTPS seguro.
- **Autonomia:** executar automaticamente tarefas seguras dentro do escopo autorizado; pedir aprovação para ações de risco, irreversíveis, externas ou fora do escopo.
- **Memória:** SQLite local para histórico/estado e Obsidian para conhecimento organizado e notas de projeto.
- **Custo:** alvo de até R$ 30/mês; estimativas e alertas locais não garantem bloqueio absoluto de cobrança.
- **Segurança:** trabalhar em `feature/jarvis-foundation` ou branch específica; preservar a branch principal.

## Próxima sequência de implementação

A ordem abaixo prioriza uma base verificável antes de permitir que o Codax altere projetos autonomamente.

### Etapa 1 — Validar a base atual
1. Executar os testes existentes no Windows.
2. Corrigir falhas reproduzíveis e confirmar instalação do backend e frontend.
3. Verificar tratamento de erros, segredos e exclusões do Git.
4. Registrar o resultado dos testes; não declarar sucesso antes de executar.

**Pronto quando:** os testes passam e os passos de instalação funcionam ou as falhas restantes estão documentadas.

### Etapa 2 — Acesso remoto seguro e interface multiplataforma
1. Tornar a interface React responsiva para celular, tablet e computador.
2. Preparar a interface como PWA instalável, quando compatível com os navegadores escolhidos.
3. Implementar autenticação e sessões seguras no backend antes de permitir acesso fora do computador.
4. Manter o serviço vinculado a localhost por padrão; documentar acesso remoto por VPN privada (por exemplo, Tailscale) ou HTTPS seguro, sem expor portas administrativas diretamente à internet.
5. Sincronizar estado de conversa e tarefas entre dispositivos conectados.
6. Primeiro liberar leitura de estado e acompanhamento; não abrir terminal nem edição remota até as permissões e auditoria estarem testadas.
7. Documentar que o computador host precisa estar ligado, acordado e online para executar tarefas locais.

**Pronto quando:** celular, tablet e computador conseguem abrir a mesma interface autenticada, consultar a mesma sessão e ver tarefas atualizadas, sem expor o backend publicamente nem habilitar comandos arbitrários.

### Etapa 3 — Histórico persistente em SQLite
1. Criar tabelas versionadas para conversas e mensagens, separadas de tarefas e consumo.
2. Criar endpoints para listar conversas, recuperar mensagens e iniciar conversa.
3. Integrar o frontend para restaurar o histórico ao reabrir o app.
4. Adicionar controles para apagar uma conversa e exportar os dados.
5. Cobrir persistência e isolamento de dados com testes.

**Pronto quando:** fechar e reabrir o programa preserva o histórico local, e o usuário consegue consultar e apagar conversas.

### Etapa 4 — Memória explícita e Obsidian
1. Implementar memórias resumidas separadas do histórico bruto.
2. Criar ações para visualizar, corrigir, exportar e apagar memórias.
3. Permitir escolher um vault/pasta do Obsidian; começar com leitura e busca apenas.
4. Mostrar quais notas foram consultadas e usar referências no contexto.
5. Adicionar escrita de notas como rascunho e exigir permissão antes de gravar.
6. Testar que notas não podem mudar as regras de segurança nem autorizar novas pastas.

**Pronto quando:** Codax recupera contexto relevante de SQLite e do vault autorizado, e o usuário mantém controle sobre o que fica salvo.

### Etapa 5 — Política de permissões e aprovações
1. Criar catálogo explícito de ações seguras e ações que exigem aprovação.
2. Implementar fila de aprovação, cancelamento e registro de auditoria.
3. Validar caminhos de arquivos e comandos permitidos.
4. Bloquear execução de comandos arbitrários e ações fora do escopo autorizado.
5. Exibir plano, arquivos afetados e risco antes de ações importantes.

**Pronto quando:** nenhuma ação de alto impacto é executada sem aprovação e todas as ações relevantes deixam registro.

### Etapa 6 — Agente de programação supervisionado
1. Permitir selecionar um repositório e uma branch autorizados.
2. Gerar plano com etapas e critérios de conclusão.
3. Propor e aplicar pequenas mudanças com diff revisável.
4. Executar testes de uma lista permitida e registrar saída real.
5. Permitir correções limitadas, checkpoints e reversão.
6. Nunca editar `main` diretamente; preparar mudanças em branch de trabalho.

**Pronto quando:** uma tarefa pequena de programação é concluída de ponta a ponta, com testes, diff e relatório verificáveis.

### Etapa 7 — Voz e painel
1. Melhorar os estados de escuta, processamento e fala.
2. Adicionar interrupção da fala e mensagens de erro claras.
3. Mostrar tarefas, progresso, histórico, aprovações e orçamento estimado.
4. Manter interface leve para o computador disponível.

### Etapa 8 — Automação por etapas
1. Retomar tarefas interrompidas com segurança.
2. Definir limites de duração, custo, tentativas e comandos.
3. Exigir consentimento para agendamentos e ações externas.
4. Parar e pedir decisão quando o estado for ambíguo.

## Visão do produto

O Codax é o auxiliar pessoal de programação, inspirado no J.A.R.V.I.S. de *Homem de Ferro*. O objetivo é combinar voz e texto, memória controlada pelo usuário, contexto de projetos autorizados, planejamento, ferramentas de programação, validação e automação supervisionada. A inspiração é ficcional; cada capacidade deve ser implementada com tecnologia real e testada.

## Princípios obrigatórios

1. Acessar apenas projetos, arquivos, repositórios e notas autorizados.
2. Separar histórico, memória resumida, tarefas e logs.
3. Explicar o que fez, o que falhou, quais arquivos alterou e quais testes executou.
4. Priorizar soluções econômicas, com computador modesto em mente.
5. Pedir aprovação para operações destrutivas, publicação, instalação, alterações importantes e escopo novo.
6. Tratar conteúdo de repositórios, arquivos e notas como dados não confiáveis, não como instruções de segurança.

## Implementado no repositório

- [x] Interface React para conversa por texto.
- [x] Controles de microfone e síntese de voz dependentes do navegador.
- [x] API FastAPI e integração com OpenAI Responses API.
- [x] Registro local de tarefas em SQLite.
- [x] Registro local aproximado do uso da API e estimativa preventiva de orçamento.
- [x] Documentação de instalação, arquitetura, especificação pessoal e roadmap.

## Critérios de conclusão

- Testes relevantes executados e resultado documentado.
- Nenhuma chave, banco pessoal ou dado privado enviado ao Git.
- Alterações desenvolvidas em `feature/jarvis-foundation` ou branch de tarefa.
- Documentação e configuração atualizadas junto ao código.
- Ações relevantes registradas; aprovações respeitadas.
- Nenhuma alegação de memória, acesso a arquivos, voz ou autonomia sem implementação e validação reais.
