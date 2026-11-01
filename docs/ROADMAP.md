# Plano de desenvolvimento do Codax

Este documento separa o que já existe do que ainda precisa ser implementado. Não considerar uma etapa concluída sem alteração de código e validação.

## Implementado no repositório

- [x] Interface React para conversa por texto.
- [x] Controles de microfone e síntese de voz dependentes do navegador.
- [x] API FastAPI e integração com OpenAI Responses API.
- [x] Registro local de tarefas em SQLite.
- [x] Registro local aproximado do uso da API e estimativa preventiva de orçamento.
- [x] Exemplo de configuração sem chave real.
- [x] Documentação inicial de instalação e endpoints.

## Próximas etapas recomendadas

1. [ ] Rodar os testes no ambiente Windows e corrigir falhas encontradas.
2. [ ] Mostrar tarefas, progresso e orçamento na interface.
3. [ ] Salvar histórico de conversas de forma persistente.
4. [ ] Implementar memória pessoal editável, consultável e apagável pelo usuário.
5. [ ] Integrar o Obsidian usando uma pasta/abordagem autorizada pelo usuário.
6. [ ] Adicionar leitura apenas de pastas explicitamente selecionadas.
7. [ ] Adicionar edição de arquivos e execução de testes em ambiente limitado.
8. [ ] Pedir aprovação antes de comandos destrutivos, alterações importantes ou publicação.
9. [ ] Integrar GitHub mantendo mudanças em branch e revisão por pull request.

## Critérios de conclusão

- Testes relevantes executados e resultado documentado.
- Nenhuma chave ou dado privado adicionado ao Git.
- Mudanças desenvolvidas em `feature/jarvis-foundation` ou em uma branch de tarefa.
- Instruções de instalação atualizadas.
- Nenhuma alegação de memória, acesso a arquivos ou autonomia sem implementação real.
