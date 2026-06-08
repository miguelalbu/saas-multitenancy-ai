# Desafio Técnico Backend — Software Engineer (Python / AI)

## Objetivo

O objetivo deste desafio é avaliar a capacidade de arquitetar e desenvolver soluções de backend modernas, seguras, performáticas e reativas. O teste simula o core business de uma plataforma SaaS corporativa: multi-tenant, orientada a eventos, com atualizações em tempo real e integrada a agentes de Inteligência Artificial (LLMs) para automação de fluxos de trabalho.

Não buscamos um sistema 100% finalizado, mas sim um código limpo que demonstre maturidade em arquitetura de software, modelagem de dados, processamento assíncrono, comunicação em tempo real e desenvolvimento de agentes inteligentes.

## Stack Tecnológica

- **Linguagem:** Python 3.11+
- **Framework Web:** FastAPI (Assíncrono, com suporte nativo a WebSockets)
- **Validação & IA:** Pydantic (v2) e PydanticAI (obrigatórios para validação de dados e estruturação do agente)
- **Banco de Dados:** PostgreSQL (via ORM: SQLAlchemy)
- **Mensageria/Assincronismo:** `asyncio` nativo (BackgroundTasks + asyncio.create_task)
- **Containerização:** Docker e Docker Compose
- **Padrão de Código:** Código, commits, documentação e logs estritamente em inglês

> **Nota:** Este é um teste 100% focado em Backend. Não é necessário desenvolver nenhuma interface visual (Frontend). A entrega deve ser validada via documentação interativa da API (Swagger/Redoc), testes de WebSocket ou por uma suíte de testes automatizados.

## Escopo do Desafio (3 Pilares)

### Pilar 1: Isolamento Multi-Tenant e Matriz de Permissões (RBAC)

A plataforma atende múltiplas empresas (Organizações) compartilhando a mesma infraestrutura com isolamento estrito dos dados.

1. **Multi-tenancy:** Isolamento de dados via coluna `organization_id` onde cada requisição à API filtra automaticamente o escopo da organização do usuário logado (autenticação simulada via Token JWT ou header customizado `X-Organization-ID`).
2. **Controle de Acesso (RBAC):** Estrutura de grupos de acesso baseada em escopos. Um middleware/decorator nas rotas valida se o usuário possui a permissão técnica necessária para executar a ação (ex: `task:read` para listar tarefas; erro `403 Forbidden` caso tente uma rota restrita sem a credencial).

### Pilar 2: Agente de IA Conversacional com PydanticAI & Tool Calling

O agente de IA da plataforma precisa interagir ativamente com o ecossistema do sistema, gerando saídas estruturadas e confiáveis.

1. **Endpoint de Chat (`POST /v1/chat`):** Rota que recebe a mensagem do usuário.
2. **Construção do Agente:** Uso obrigatório do framework PydanticAI para orquestrar o agente inteligente (conectado à OpenAI API, Gemini API ou Ollama local).
3. **Implementação de Tools com Validação Pydantic:** O agente deve ter acesso a pelo menos uma ferramenta funcional (Tool) conectada ao banco de dados.
   - **Cenário do teste:** Se o usuário digitar: *"Cadastre uma tarefa urgente chamada 'Revisar relatório financeiro' para o departamento Comercial"*, o agente do PydanticAI deve extrair as entidades de forma tipada, validá-las usando schemas do Pydantic e acionar autonomamente a função de backend que insere a tarefa no banco de dados.

### Pilar 3: Motor de Automações e Atualização em Tempo Real (WebSockets)

O sistema permite que eventos disparem ações em segundo plano e notifiquem o usuário de forma reativa.

1. **Endpoint de Webhook/Trigger (`POST /v1/webhook/event`):** Rota que recebe eventos externos simulados (ex: uma atualização de status financeiro ou alerta de sistema).
2. **Processamento Orientado a Eventos:** O recebimento desse trigger deve disparar uma Action assíncrona (Background Task/Worker) para executar uma tarefa secundária no banco de dados (ex: alterar o status de uma tarefa para "Atrasada" ou gerar um log de auditoria).
3. **Conexão WebSocket (`/v1/ws/notifications`):** Quando a Action assíncrona for concluída com sucesso, o backend deve enviar uma mensagem de forma reativa/push através do WebSocket para o cliente logado, simulando uma atualização em tempo real.

## Critérios de Avaliação

- **Maturidade Assíncrona:** Uso correto de concorrência com async/await, gerenciamento de conexões WebSocket estáveis e tarefas em segundo plano.
- **Uso do PydanticAI:** Organização do agente, clareza na definição de prompts do sistema e robustez na injeção de Tools.
- **Tratamento de Erros:** Resiliência caso a conexão WebSocket caia ou a API da LLM retorne dados corrompidos.
- **Segurança Multi-tenant:** Garantia de que mensagens via WebSocket ou requisições HTTP nunca vazem dados entre organizações diferentes.

## Questionário Técnico (Avaliação de Arquitetura Sênior)

> Responda às seguintes perguntas sobre cenários de alta escala:

### 1. Arquitetura Contextual e Bancos de Grafos

Em cenários de produção com IA, lidamos com relacionamentos complexos de contexto e conhecimento RAG. Como você planejaria a integração de um Banco de Dados Orientado a Grafos (como o Neo4j) com o ciclo de vida de um agente para otimizar a recuperação de dados e o custo de tokens das LLMs?

**Resposta:** _TODO_

### 2. WebSockets em Alta Escala

Manter milhares de conexões WebSocket abertas simultaneamente consome muita memória de microsserviços. Como você arquitetaria a infraestrutura e o backend (ex: usando Redis Pub/Sub ou brokers de mensageria) para garantir que as notificações em tempo real funcionem de forma distribuída entre múltiplas instâncias da API de backend?

**Resposta:** _TODO_

### 3. Evolução de Domínio

Olhando para as regras de negócio propostas neste desafio, como você aplicaria os conceitos de Domain-Driven Design (DDD) para separar claramente os limites de contexto (Bounded Contexts) entre o módulo conversacional de IA e o motor de execução de automações/workflows?

**Resposta:** _TODO_

## Justificativa da Estratégia Assíncrona

Escolhemos **`asyncio` nativo** (FastAPI BackgroundTasks + `asyncio.create_task`) como estratégia de mensageria/assincronismo porque:

- O escopo do desafio é limitado e não requer workers distribuídos
- Evita complexidade extra de infraestrutura (containers RabbitMQ/Kafka)
- Demonstra domínio do modelo de concorrência nativa do Python
- Para push via WebSocket, um `ConnectionManager` in-memory particionado por organização é suficiente
- Em produção, poderia evoluir para Redis Pub/Sub ou um broker de mensagens para escalonamento horizontal

## Como Executar

### Pré-requisitos

- Docker & Docker Compose
- (Opcional) Python 3.12+ para desenvolvimento local sem Docker

### Executando com Docker Compose

```bash
docker compose up --build
```

A API estará disponível em `http://localhost:8000`

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Executando Localmente (Desenvolvimento)

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt  # (opcional) para testes & linting
```

### Migrações de Banco de Dados (Alembic)

Certifique-se que o PostgreSQL está rodando (via Docker ou localmente) e que o `.env` possui o `DATABASE_URL` correto.

```bash
# Gerar uma nova migração após alterar os models
alembic revision --autogenerate -m "descrição das alterações"

# Aplicar todas as migrações pendentes
alembic upgrade head

# Reverter a última migração
alembic downgrade -1

# Verificar estado atual das migrações
alembic current
```

> **Dica:** Se estiver rodando apenas o banco de dados via Docker:
> ```bash
> docker compose up db -d
> ```
> Depois configure `DATABASE_URL=postgresql+asyncpg://app:app@localhost:5433/desafio` no seu `.env` para desenvolvimento local.

### Dados Iniciais (Seed)

```bash
python -m seed.seed_data
```

### Iniciar o Servidor

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Executando Testes

```bash
pytest -v
```

## Estratégia Multi-Tenant

O isolamento de dados é garantido por uma coluna global `organization_id` presente em todas as tabelas com escopo de tenant. Toda query ao banco de dados é automaticamente filtrada através de um mecanismo de injeção de dependência (`get_current_organization`) que extrai o contexto da organização a partir do token JWT autenticado ou do header `X-Organization-ID`.

As conexões WebSocket são gerenciadas por um `ConnectionManager` que particiona as conexões ativas por `organization_id`, garantindo que as notificações sejam enviadas apenas para usuários dentro da mesma organização.

## Estrutura do Projeto

```
app/
├── main.py                  # Entrypoint da aplicação FastAPI
├── config.py                # Configurações (pydantic-settings)
├── api/
│   ├── deps.py              # Dependências compartilhadas (DB session, auth, org)
│   └── v1/
│       ├── router.py        # Agregador de rotas
│       └── endpoints/       # Um arquivo por recurso
├── core/
│   ├── security.py          # JWT, hash de senhas
│   ├── database.py          # AsyncEngine, AsyncSession
│   ├── permissions.py       # Middleware/decorator RBAC
│   └── websocket_manager.py # ConnectionManager multi-tenant
├── models/                  # Models SQLAlchemy
├── schemas/                 # Schemas Pydantic
├── services/                # Lógica de negócio
├── agent/                   # Agente PydanticAI, tools, prompts
└── repositories/            # Camada de acesso a dados
```

## Entregáveis

- [x] Repositório no GitHub
- [x] README com instruções de Docker Compose, estratégia multi-tenant e questionário técnico
- [ ] Massa de dados (seed) para testes imediatos
- [ ] Endpoints funcionais da API
- [ ] Agente de IA com Tool Calling
- [ ] Notificações em tempo real via WebSocket
- [ ] Testes automatizados
