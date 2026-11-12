# Operação e qualidade — J.A.R.V.I.S. Dev

## Escopo existente

Assistente local com backend FastAPI e frontend React, modo sem chave e integração opcional com a OpenAI API.

## Código e testes

`backend/app/main.py`, `backend/app/security.py`, `backend/app/github_readonly.py`, `frontend/` e `backend/tests/`.

## Reprodução local

Instalar requisitos de `backend/requirements.txt`, executar testes em `backend/tests/`; consultar scripts de `frontend/package.json` antes de buildar a interface.

Ao alterar funcionalidade, registrar no PR os comandos executados e os resultados; não tratar verificações não executadas como aprovadas.

## Cenários a incluir na regressão

Testar ausência de chave, falha de rede, entrada vazia, contexto excessivo, execução de instrução maliciosa no prompt e arquivos de código fornecidos por usuário.

## Riscos e evolução

Evitar registrar chaves e histórico sensível. Verificar isolamento do acesso GitHub e nunca confundir revisão estática com execução de código confiável.

### Checklist de entrega

- [ ] Novo comportamento ligado a caso de uso real.
- [ ] Testes e exemplo documentados, quando aplicável.
- [ ] Nenhum segredo ou dado de cliente adicionado.
- [ ] Código revisado em branch, sem merge automático.
