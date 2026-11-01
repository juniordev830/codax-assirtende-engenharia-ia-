# J.A.R.V.I.S. Dev

Assistente de programação em português, com interface React, API local FastAPI e integração com a OpenAI Responses API. A fundação do agente inclui registro persistente de tarefas e contabilização local aproximada do uso da API.

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
- O assistente atual ainda não executa comandos de terminal, não lê arquivos do projeto nem altera código.
- Não cole chaves, senhas ou tokens na conversa do assistente.
- O banco local de tarefas e consumo fica em `backend/.jarvis_data/`, ignorado pelo Git.

## 1. Configurar a chave e o orçamento
1. Entre no painel de API da OpenAI: https://platform.openai.com/api-keys
2. Crie uma chave de API e guarde-a com segurança.
3. Dentro da pasta `backend`, copie `.env.example` para um novo arquivo chamado `.env`.
4. Edite `backend/.env` e substitua `cole_sua_chave_aqui` pela chave real. Não compartilhe esse arquivo.

Exemplo de configuração local:

```dotenv
OPENAI_API_KEY=sua_chave_real_aqui
OPENAI_MODEL=gpt-5.4-mini
JARVIS_MONTHLY_BUDGET_USD=4.50
JARVIS_INPUT_PRICE_PER_MILLION=0.75
JARVIS_OUTPUT_PRICE_PER_MILLION=4.50
```

O padrão de US$ 4,50 é uma reserva conservadora para tentar ficar abaixo de R$ 30, mas o valor em reais varia com câmbio e impostos. Os preços por token são configuráveis e devem ser conferidos na página oficial de preços antes de mudar o modelo.

**Limitação importante do orçamento:** o backend estima o custo antes de cada chamada e registra o uso retornado pela API depois da resposta. Isso é uma proteção local de melhor esforço, não um limite financeiro garantido pela plataforma. O painel de uso/cobrança da API continua sendo a referência oficial e pode apresentar atrasos. Configure também os controles disponíveis na plataforma.

## 2. Iniciar o backend
Abra um PowerShell na pasta `backend`:

```powershell
py -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

Se a ativação do ambiente virtual for bloqueada:

```powershell
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
.\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

Confira `http://127.0.0.1:8765/api/health`. Quando a chave estiver carregada, `ai_configured` deve ser `true`.

## 3. Iniciar a interface
Abra outro PowerShell na pasta `frontend`:

```powershell
npm install
npm run dev
```

Abra o endereço local mostrado pelo Vite, normalmente `http://127.0.0.1:5173`.

## 4. Endpoints locais adicionados
- `GET /api/budget`: mostra orçamento configurado, gasto registrado e saldo estimado do mês UTC.
- `GET /api/tasks`: lista tarefas salvas.
- `POST /api/tasks`: cria uma tarefa persistente com título e descrição.
- `GET /api/tasks/{task_id}`: consulta uma tarefa.
- `PATCH /api/tasks/{task_id}`: atualiza estado, progresso e etapas.
- `POST /api/chat`: verifica o orçamento local estimado antes de chamar a IA e registra o uso após uma resposta.

Exemplo de criação de tarefa:

```json
{
  "title": "Corrigir testes da API",
  "description": "Investigar falhas, propor alterações pequenas e validar os testes."
}
```

Os estados permitidos são `planned`, `running`, `waiting_approval`, `completed`, `failed` e `cancelled`. Neste marco, o sistema **registra e acompanha tarefas**, mas ainda não as executa automaticamente.

## 5. Testes
A partir da pasta `backend`, com o ambiente virtual ativado:

```powershell
python -m unittest discover -s tests -v
```

## 6. Voz
Use uma versão atualizada do Microsoft Edge ou Google Chrome. O reconhecimento de voz depende do suporte do navegador e da permissão do microfone; as respostas faladas usam a síntese de voz do navegador.

## Como funciona hoje
A interface envia a mensagem para a API local; o backend chama a OpenAI Responses API e devolve o texto. A chave nunca é enviada ao navegador. O modelo pode ser alterado por meio de `OPENAI_MODEL` no arquivo local `.env`.

## Próximas etapas
1. Validar testes e orçamento no Windows local.
2. Mostrar tarefas e orçamento na interface React.
3. Adicionar leitura autorizada de pastas selecionadas.
4. Implementar edição de arquivos, execução de testes e aprovação explícita.
5. Integrar VS Code e GitHub com revisão antes de alterar ou enviar arquivos.

O trabalho está na branch `feature/jarvis-foundation` e em um pull request de rascunho para revisão. A branch principal não deve ser alterada diretamente.
