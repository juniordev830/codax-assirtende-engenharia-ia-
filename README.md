# J.A.R.V.I.S. Dev

Assistente de programação em português, com interface React, API local FastAPI e integração com a OpenAI Responses API.

## Requisitos
- Windows 10
- Python 3.10+
- Node.js LTS
- Uma chave de API da OpenAI com faturamento/uso de API habilitado
- VS Code (recomendado)

**Importante:** a assinatura do ChatGPT e o uso da API são serviços/faturamentos separados. A API pode gerar cobranças conforme o uso.

## Segurança
- A chave fica no arquivo local `backend/.env`; nunca a coloque no frontend ou faça commit dela.
- O arquivo `.env` já está no `.gitignore`.
- O assistente responde perguntas e ajuda com código, mas ainda não executa comandos de terminal, não lê arquivos e não altera projetos.
- Não cole chaves, senhas ou tokens na conversa do assistente.

## 1. Configurar a chave da API
1. Entre no painel de API da OpenAI: https://platform.openai.com/api-keys
2. Crie uma chave de API e guarde-a com segurança.
3. Dentro da pasta `backend`, copie `.env.example` para um novo arquivo chamado `.env`.
4. Edite `backend/.env` e substitua `cole_sua_chave_aqui` pela chave real. Não compartilhe esse arquivo.

Exemplo do formato do arquivo local `backend/.env`:

```dotenv
OPENAI_API_KEY=sua_chave_real_aqui
OPENAI_MODEL=gpt-5.4-mini
```

O exemplo acima é apenas um formato ilustrativo. Nunca coloque uma chave real no GitHub.

## 2. Iniciar o backend
Abra um PowerShell na pasta `backend`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

Se a ativação do ambiente virtual for bloqueada:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

Confira `http://127.0.0.1:8765/api/health`. Quando a chave estiver carregada, o campo `ai_configured` deve ser `true`.

## 3. Iniciar a interface
Abra outro PowerShell na pasta `frontend`:

```powershell
npm install
npm run dev
```

Abra o endereço local mostrado pelo Vite, normalmente `http://127.0.0.1:5173`.

## 4. Voz
Use uma versão atualizada do Microsoft Edge ou Google Chrome. O reconhecimento de voz depende do suporte do navegador e da permissão do microfone; as respostas faladas usam a síntese de voz do navegador.

## Como funciona
A interface envia a mensagem para a API local; o backend chama a OpenAI Responses API e devolve o texto. A chave nunca é enviada ao navegador. O modelo pode ser alterado por meio de `OPENAI_MODEL` no arquivo local `.env`.

## Próximas etapas
1. Testar a conexão da API no Windows.
2. Adicionar contexto de conversa.
3. Implementar leitura autorizada de pastas selecionadas.
4. Criar análise de código e execução de testes com aprovação.
5. Integrar VS Code e GitHub com revisão antes de alterar ou enviar arquivos.

O trabalho está na branch `feature/jarvis-foundation` e em um pull request de rascunho para revisão. A branch principal não foi alterada.
