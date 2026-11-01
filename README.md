# J.A.R.V.I.S. Dev

Assistente de programação inspirado no J.A.R.V.I.S., com interface React e serviço local FastAPI.

## Requisitos
- Windows 10
- Python 3.10+
- Node.js LTS
- VS Code (recomendado)

## Segurança desta primeira versão
- O chat está em modo demonstração; ainda não usa um modelo de IA.
- Não executa comandos de terminal nem lê/altera arquivos do computador.
- Não envie senhas, tokens ou chaves secretas para o chat.
- A integração com IA será configurada somente no backend, nunca expondo chaves no frontend.

## 1. Iniciar o backend
Abra um PowerShell na pasta `backend`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

Se a ativação do ambiente virtual for bloqueada, execute:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

Teste a API em `http://127.0.0.1:8765/api/health`.

## 2. Iniciar a interface
Abra outro PowerShell na pasta `frontend`:

```powershell
npm install
npm run dev
```

Abra o endereço local exibido pelo Vite, normalmente `http://127.0.0.1:5173`.

## 3. Voz
Use uma versão atualizada do Microsoft Edge ou Google Chrome. O reconhecimento de voz depende do suporte do navegador e da permissão de microfone; a fala de resposta usa a síntese de voz do navegador.

## Próximas etapas
1. Testar a interface e a comunicação local no Windows.
2. Conectar um provedor de IA com chave guardada no backend.
3. Adicionar seleção explícita de pastas e ferramentas de leitura com permissões.
4. Implementar análise de código e execução controlada de testes.
5. Integrar VS Code e GitHub, com revisão antes de gravar ou enviar alterações.

O trabalho está na branch `feature/jarvis-foundation` e em um pull request de rascunho para revisão; a branch principal não foi alterada.
