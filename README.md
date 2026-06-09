# Projeto Multi-tenant SaaS AI

## Sobre o Projeto

Backend de uma plataforma SaaS corporativa de gerenciamento de tarefas construída como solução ao desafio técnico da Clara.AI. A aplicação é multi-tenant, orientada a eventos e integrada a um agente de IA conversacional.

Foram implementados três pilares técnicos completos: isolamento de dados por organização com RBAC baseado em escopos JWT, agente conversacional com PydanticAI e tool calling que persiste ações reais no banco, e motor de automações via webhook com notificações push em tempo real por WebSocket. O projeto inclui 29 testes automatizados cobrindo todos os pilares e está 100% containerizado com Docker Compose.

---

## Stack Tecnológica

| Categoria | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Framework Web | FastAPI (async) |
| Validação & IA | Pydantic v2 + PydanticAI |
| Banco de Dados | PostgreSQL 16 via SQLAlchemy (async) |
| Driver Async | asyncpg |
| Migrações | Alembic |
| Autenticação | JWT (PyJWT) + bcrypt |
| Assincronismo | asyncio nativo + BackgroundTasks |
| LLM Provider | OpenAI (gpt-4o-mini) |
| Containerização | Docker + Docker Compose |
| Testes | pytest + pytest-asyncio |
| Linting | Ruff |

---

## Entregáveis

- [x] Repositório no GitHub com histórico de commits organizado por feature
- [x] README com instruções completas de execução, arquitetura e questionário técnico
- [x] Dados iniciais (seed) para testes imediatos com dois tenants
- [x] Endpoints funcionais da API com documentação automática (Swagger/ReDoc)
- [x] Agente de IA com Tool Calling via PydanticAI
- [x] Notificações em tempo real via WebSocket (multi-tenant isolado)
- [x] Testes automatizados — 29 testes cobrindo os 3 pilares

---

## Estrutura do Projeto

```
app/
├── main.py                      # Entrypoint FastAPI com lifespan
├── config.py                    # Configurações via pydantic-settings
├── api/
│   ├── deps.py                  # CurrentUser, injeção de sessão DB
│   └── v1/
│       ├── router.py            # Agregador de rotas
│       └── endpoints/
│           ├── auth.py          # POST /v1/auth/login
│           ├── tasks.py         # CRUD /v1/tasks
│           ├── chat.py          # POST /v1/chat
│           ├── webhook.py       # POST /v1/webhook/event
│           └── websocket.py     # WS /v1/ws/notifications
├── core/
│   ├── database.py              # AsyncEngine + async_sessionmaker
│   ├── security.py              # JWT, bcrypt
│   ├── scopes.py                # Constantes de escopos RBAC
│   ├── permissions.py           # require_scope() — dependency factory
│   └── websocket_manager.py     # ConnectionManager multi-tenant
├── models/
│   ├── base.py                  # UUIDMixin, TimestampMixin, TenantMixin
│   ├── organization.py          # Tabela organizations
│   ├── user.py                  # Tabela users
│   ├── role.py                  # Tabela roles (escopos em JSONB)
│   ├── task.py                  # Tabela tasks
│   └── audit_log.py             # Tabela audit_logs
├── schemas/                     # Schemas Pydantic de entrada/saída
├── repositories/                # Queries SQL filtradas por organization_id
├── services/                    # Regras de negócio
│   ├── task_service.py
│   ├── webhook_service.py
│   └── notification_service.py
└── agent/
    ├── agent.py                 # Singleton PydanticAI Agent
    ├── tools.py                 # create_task, list_tasks + AgentDeps
    └── prompts.py               # System prompt
alembic/                         # Migrações do banco de dados
seed/
└── seed_data.py                 # Dados iniciais (2 orgs, 4 usuários, tarefas)
tests/
├── conftest.py                  # Fixtures: engine por teste, OrgFixture
├── test_auth.py                 # Autenticação e JWT
├── test_tasks.py                # CRUD de tarefas e RBAC
├── test_multi_tenant.py         # Isolamento entre organizações
├── test_chat.py                 # Agente IA com TestModel (sem chamar OpenAI)
├── test_webhook.py              # Processamento de eventos e AuditLog
└── test_websocket.py            # Conexão, ping/pong, broadcast, isolamento
```

---

## Como Executar

### Pré-requisitos

- Docker e Docker Compose instalados
- Chave de API da OpenAI

### 1. Configurar variáveis de ambiente

Copie o arquivo de exemplo e preencha os valores:

```bash
cp .env.example .env
```

Edite o `.env` e defina sua chave da OpenAI:

```env
OPENAI_API_KEY=sk-...

# Demais variáveis já vêm preenchidas com valores de desenvolvimento:
APP_NAME=desafio-backend-python-ai
DEBUG=true
DATABASE_URL=postgresql+asyncpg://app:app@db:5432/desafio
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
```

### 2. Subir os containers

```bash
docker compose up --build
```

Ou usando o Makefile:

```bash
make up-build
```

Aguarde até ver no log:

```
desafio-api | INFO:     Application startup complete.
```

### 3. Aplicar as migrações

```bash
docker compose exec api alembic upgrade head
```

Ou via Makefile:

```bash
make upgrade
```

### 4. Popular os dados iniciais (seed)

```bash
docker compose exec api python -m seed.seed_data
```

Ou via Makefile:

```bash
make seed
```

O seed cria dois tenants com usuários prontos para teste:

| Organização | Email | Senha | Role |
|---|---|---|---|
| Acme Corp | admin@acme.com | password123 | admin |
| Acme Corp | member@acme.com | password123 | member |
| Globex Inc | admin@globex.com | password123 | admin |
| Globex Inc | member@globex.com | password123 | member |

### 5. Acessar a API

| Interface | URL |
|---|---|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health check | http://localhost:8000/health |

---

## Comandos Úteis (Makefile)

```bash
make up            # Sobe os containers em background
make up-build      # Reconstrói a imagem e sobe
make down          # Para e remove os containers
make logs          # Acompanha todos os logs
make logs-api      # Acompanha apenas os logs da API

make upgrade       # Aplica migrações pendentes
make downgrade     # Reverte a última migração
make seed          # Popula os dados iniciais
make db-shell      # Abre psql dentro do container

make test          # Roda a suite completa de testes
make test-pillar1  # Testes de auth, tasks e multi-tenant
make test-pillar2  # Testes do agente de IA
make test-pillar3  # Testes de webhook e WebSocket
make lint          # Executa o linter (ruff)
```

---

## Executando os Testes

Os testes sobem um banco PostgreSQL isolado por teste (schema recriado a cada execução) e não dependem de OpenAI — o agente é testado com `TestModel` do PydanticAI.

```bash
make test
```

Resultado esperado:

```
29 passed in ~24s
```

Cobertura por pilar:

| Arquivo | Pilar | Testes |
|---|---|---|
| test_auth.py | 1 | Login, JWT inválido, usuário inativo |
| test_tasks.py | 1 | CRUD, admin vs member, validações |
| test_multi_tenant.py | 1 | Cross-tenant retorna 404, não 403 |
| test_chat.py | 2 | Tool calling, isolamento de org, erros |
| test_webhook.py | 3 | 202 Accepted, AuditLog, overdue, tenant |
| test_websocket.py | 3 | Conexão, ping/pong, broadcast, isolamento |

---

## Endpoints da API

### Autenticação

```
POST /v1/auth/login
Body: { "email": "admin@acme.com", "password": "password123" }
Retorna: { "access_token": "<jwt>", "token_type": "bearer" }
```

### Tarefas

```
GET    /v1/tasks           # Lista tarefas da org (task:read)
POST   /v1/tasks           # Cria tarefa (task:write)
GET    /v1/tasks/{id}      # Busca tarefa por ID (task:read)
PUT    /v1/tasks/{id}      # Atualiza tarefa (task:write)
DELETE /v1/tasks/{id}      # Remove tarefa (task:delete)
```

### Agente de IA

```
POST /v1/chat
Headers: Authorization: Bearer <token>
Body: { "message": "Crie uma tarefa urgente chamada Deploy v2 para o departamento de Infra" }
Retorna: { "response": "...", "actions_taken": [{ "tool": "create_task", "result": {...} }] }
```

### Webhook

```
POST /v1/webhook/event
Headers: Authorization: Bearer <token>  (requer webhook:manage)
Body: { "event_type": "task_overdue", "payload": { "task_id": "<uuid>" } }
Retorna: 202 Accepted — { "status": "accepted", "message": "..." }
```

Tipos de evento suportados:
- `task_overdue` — atualiza o status da tarefa para `overdue` e notifica via WebSocket
- `financial_alert` — registra no AuditLog e notifica via WebSocket
- qualquer outro — registra como evento genérico no AuditLog

### WebSocket

```
WS /v1/ws/notifications?token=<jwt>
```

Após conectar, envie `"ping"` para receber `"pong"` (keepalive). Notificações chegam automaticamente quando eventos são processados.

---

## Arquitetura — Os 3 Pilares

### Pilar 1: Multi-tenancy + RBAC

**Isolamento de dados:** toda tabela com escopo de tenant herda `TenantMixin`, que adiciona a coluna `organization_id`. Cada repositório filtra todas as queries por essa coluna — nunca há acesso a dados de outra organização.

```python
# Exemplo: list_tasks sempre filtra pela org do usuário autenticado
WHERE tasks.organization_id = :org_id
```

**Decisão de segurança:** cross-tenant retorna `404 Not Found`, não `403 Forbidden`. Isso evita confirmar a existência de recursos em outras organizações (information leakage).

**RBAC via JWT scopes:** o token carrega os escopos do usuário (`task:read`, `task:write`, `task:delete`, `chat:use`, `webhook:manage`). A função `require_scope()` é um dependency factory do FastAPI — qualquer rota que a use como `Depends(require_scope("task:write"))` rejeita automaticamente com 403 se o escopo estiver ausente.

| Escopo | Admin | Member |
|---|---|---|
| `task:read` | ✅ | ✅ |
| `task:write` | ✅ | ❌ |
| `task:delete` | ✅ | ❌ |
| `chat:use` | ✅ | ❌ |
| `webhook:manage` | ✅ | ❌ |

**Nota sobre email:** o email é único dentro da organização, não globalmente. `admin@acme.com` e `admin@globex.com` são usuários completamente distintos. O endpoint de login aceita um header opcional `X-Organization-ID` para desambiguação quando o mesmo email existe em múltiplas orgs.

---

### Pilar 2: Agente de IA com PydanticAI

O agente é um singleton `Agent[AgentDeps, str]` configurado com GPT-4o-mini. Ele recebe a mensagem do usuário, decide quais tools chamar e retorna uma resposta em texto junto com a lista de ações executadas.

**AgentDeps:** o contexto injetado em cada tool call. Carrega `organization_id` e `user_id` do JWT, garantindo que todas as ações do agente fiquem isoladas ao tenant do usuário autenticado. O `session_factory` é injetável para permitir testes sem banco de produção.

**Tools disponíveis:**

| Tool | Descrição |
|---|---|
| `create_task` | Extrai título, prioridade, departamento e descrição da mensagem e cria a tarefa no banco |
| `list_tasks` | Retorna as tarefas mais recentes da organização |

**Concorrência segura:** cada tool abre sua própria sessão de banco de dados. Isso evita o erro `cannot perform operation: another operation is in progress` quando o agente encadeia múltiplos tool calls no mesmo turno.

**Fluxo de uma mensagem:**

```
POST /v1/chat { "message": "Crie uma tarefa urgente de Deploy v2 para Infra" }
  ↓ verifica escopo chat:use (403 se ausente)
  ↓ monta AgentDeps com org_id + user_id do JWT
  ↓ task_agent.run(message, deps=deps)
      ↓ GPT-4o-mini decide chamar create_task(title="Deploy v2", priority="urgent", department="Infra")
      ↓ tool abre sessão, chama task_service.create_task(...)
      ↓ tarefa salva no banco
  ↓ retorna { response: "Tarefa criada!", actions_taken: [{tool: "create_task", result: {...}}] }
```

---

### Pilar 3: WebSocket + Motor de Automações

**ConnectionManager** (`app/core/websocket_manager.py`): singleton que mantém um `dict[UUID, set[WebSocket]]` particionado por `organization_id`. O método `broadcast(org_id, payload)` entrega a mensagem exclusivamente aos clientes daquela org — isolamento multi-tenant no nível do transport layer.

**Autenticação WebSocket:** browsers não suportam headers customizados em conexões WebSocket, então o JWT é passado como query param `?token=<jwt>`. Token inválido fecha a conexão com código 1008 (Policy Violation).

**Fluxo de webhook:**

```
POST /v1/webhook/event { "event_type": "task_overdue", "payload": { "task_id": "..." } }
  ↓ valida JWT + escopo webhook:manage
  ↓ força organization_id do evento = org do token (guarda de segurança cross-tenant)
  ↓ retorna 202 Accepted imediatamente
  ↓ asyncio.create_task(webhook_service.process_event(...))  ← background, não bloqueia a resposta
      ↓ atualiza status da tarefa para "overdue" no banco
      ↓ escreve AuditLog
      ↓ notification_service.notify(org_id, "task_updated", {...})
          ↓ manager.broadcast(org_id, payload)  ← push para todos os WS conectados da org
```

**202 Accepted** é uma escolha arquitetural intencional: o cliente externo (sistema financeiro, scheduler, etc.) não precisa esperar o processamento completar — apenas a recepção e validação do evento.

---

## Justificativa das Decisões Técnicas

**asyncio nativo vs Celery/RabbitMQ:** o escopo do desafio não requer workers distribuídos. `asyncio.create_task` demonstra domínio do modelo de concorrência nativo do Python sem adicionar complexidade de infraestrutura. Em produção, a evolução natural seria Redis Pub/Sub para o WebSocket distribuído e Celery para tasks mais pesadas.

**bcrypt direto vs passlib:** a versão atual do bcrypt (5.x) é incompatível com passlib. Optamos por usar o bcrypt diretamente, eliminando a dependência intermediária.

**Engine por teste vs TRUNCATE:** os testes criam e destroem o schema inteiro a cada execução em vez de usar TRUNCATE entre testes. Isso evita conflitos de event loop entre fixtures de escopos diferentes e garante isolamento total entre testes.

**404 em vez de 403 para cross-tenant:** retornar 403 confirmaria que o recurso existe em outra organização, o que é uma forma de information leakage. O padrão correto é 404.

---

## Questionário Técnico (Avaliação de Arquitetura Sênior)

### 1. Arquitetura Contextual e Bancos de Grafos

Em cenários de produção com IA, lidamos com relacionamentos complexos de contexto e conhecimento RAG. Como você planejaria a integração de um Banco de Dados Orientado a Grafos (como o Neo4j) com o ciclo de vida de um agente para otimizar a recuperação de dados e o custo de tokens das LLMs?

**Resposta:**

A integração do Neo4j se daria em duas camadas distintas do ciclo de vida do agente: **pré-raciocínio** (recuperação de contexto) e **pós-execução** (persistência de memória episódica).

**Modelagem do grafo:** cada entidade do domínio (Organization, User, Task, Department) vira um nó. As arestas carregam semântica rica — `ASSIGNED_TO`, `DEPENDS_ON`, `CREATED_BY`, `BLOCKED_BY`. Isso permite queries que um banco relacional resolveria com múltiplos JOINs caros — como "quais tarefas bloqueiam projetos do usuário X com prazo esta semana?" — como um único traversal Cypher:

```cypher
MATCH (u)-[:ASSIGNED_TO]-(t)-[:BLOCKS]->(t2)
WHERE u.id = $user_id AND t2.due < $now
RETURN t2
```

**Fluxo de injeção no agente:**
1. Antes de chamar a LLM, um *retrieval tool* executa uma query Cypher parametrizada pelo `organization_id` e pelo contexto da mensagem do usuário (extraído via embedding ou keyword match).
2. O subgrafo retornado (JSON compacto, não os nós brutos) é injetado no system prompt como "contexto estruturado", evitando enviar toda a base de dados.
3. O resultado é truncado por relevância — somente os `k` nós mais próximos ao nó-âncora da query, controlando custo de tokens.

**Memória episódica:** após cada execução do agente, as ações realizadas (tarefas criadas, status alterados) são persistidas como novos nós com timestamp. Em conversas futuras, o agente recupera o histórico via:

```cypher
MATCH (u)-[:PERFORMED]->(a:Action)
WHERE u.id = $user_id
ORDER BY a.timestamp DESC LIMIT 10
```

**Redução de custo de tokens:** o grafo entrega contexto pré-filtrado e estruturado em vez de documentos inteiros. Uma query RAG vetorial traz parágrafos de texto; o grafo traz fatos relacionais compactos como `{"task": "Deploy v2", "status": "blocked", "blocker": "DB migration", "owner": "alice"}`, reduzindo em 60–80% os tokens necessários para o modelo entender o estado do sistema.

---

### 2. WebSockets em Alta Escala

Manter milhares de conexões WebSocket abertas simultaneamente consome muita memória de microsserviços. Como você arquitetaria a infraestrutura e o backend (ex: usando Redis Pub/Sub ou brokers de mensageria) para garantir que as notificações em tempo real funcionem de forma distribuída entre múltiplas instâncias da API de backend?

**Resposta:**

O problema central é o **acoplamento de estado**: o `ConnectionManager` atual é um singleton em memória. Se a instância A recebe um evento e precisa notificar um cliente conectado na instância B, a mensagem é perdida. A solução passa por desacoplar o transporte WebSocket do roteamento de mensagens.

**Arquitetura proposta com Redis Pub/Sub:**

```
[Evento de domínio]
        │
        ▼
[Qualquer instância API] ──PUBLISH──▶ Redis Channel: "org:{org_id}"
                                               │
                         ┌─────────────────────┼─────────────────────┐
                         ▼                     ▼                     ▼
                   [API Instance 1]    [API Instance 2]    [API Instance N]
                   SUBSCRIBE listener  SUBSCRIBE listener  SUBSCRIBE listener
                         │                     │
                   [WS clients org_X]   [WS clients org_X]
```

Cada instância mantém suas conexões WebSocket locais e uma task assíncrona que faz `SUBSCRIBE` nos canais Redis das orgs com clientes conectados naquela instância. Quando chega uma mensagem pelo canal, ela é distribuída apenas para os clientes locais — zero coordenação entre instâncias.

**Detalhes de implementação:**
- **Canal por org:** `org:{organization_id}` garante isolamento multi-tenant no próprio roteamento.
- **Redis Streams (alternativa):** para durabilidade e replay, Redis Streams com consumer groups supera o Pub/Sub fire-and-forget — clientes que desconectaram brevemente podem recuperar mensagens perdidas.
- **Subscriptions dinâmicas:** ao conectar o primeiro cliente de uma org, a instância faz `SUBSCRIBE`; ao desconectar o último, faz `UNSUBSCRIBE`, evitando canais ociosos.
- **Sticky sessions (opcional):** consistent hashing por `org_id` no load balancer concentra clientes da mesma org na mesma instância, reduzindo o tráfego Redis inter-instâncias.

**Métricas a monitorar:** conexões abertas por instância, lag de entrega Redis→WS (target: <10ms p99), e taxa de reconexão (indicador de dropped connections por OOM ou restart).

---

### 3. Evolução de Domínio

Olhando para as regras de negócio propostas neste desafio, como você aplicaria os conceitos de Domain-Driven Design (DDD) para separar claramente os limites de contexto (Bounded Contexts) entre o módulo conversacional de IA e o motor de execução de automações/workflows?

**Resposta:**

O ponto de tensão entre os dois módulos é que eles têm **linguagens ubíquas diferentes** e **invariantes de negócio distintas**: o módulo de chat se preocupa com intenção do usuário, histórico conversacional e qualidade da resposta; o motor de automações se preocupa com confiabilidade de execução, idempotência e auditoria de efeitos colaterais.

**Bounded Contexts identificados:**

| Contexto | Responsabilidade | Entidades raízes |
|---|---|---|
| **Conversational AI** | Interpretar linguagem natural, manter contexto de sessão, orquestrar chamadas ao LLM | `Conversation`, `Message`, `AgentRun` |
| **Task Management** | Ciclo de vida de tarefas, regras de status, atribuição, prioridade | `Task`, `Department`, `Assignment` |
| **Automation Engine** | Execução de webhooks, processamento de eventos, auditoria de ações | `WebhookConfig`, `AutomationEvent`, `AuditLog` |
| **Identity & Access** | Multi-tenancy, RBAC, tokens | `Organization`, `User`, `Role` |

**Integração entre contextos — Anti-Corruption Layer:**

O `Conversational AI` nunca manipula `Task` diretamente. Ele opera através de uma interface de fronteira:

```python
# app/agent/ports.py
class TaskPort(Protocol):
    async def create_task(self, org_id: UUID, data: TaskCreateCommand) -> TaskSummary: ...
    async def list_tasks(self, org_id: UUID, filters: TaskFilters) -> list[TaskSummary]: ...
```

O `TaskPort` é implementado pelo contexto de Task Management e injetado no agente via `AgentDeps`. O agente nunca vê `TaskStatus`, `TaskPriority` ou qualquer enum interno do domínio de tarefas — ele opera com `TaskSummary`, um DTO de fronteira. Isso permite trocar o LLM (GPT → Claude → modelo local) sem tocar em nenhuma regra de negócio de tarefas.

**Motor de automações como contexto reativo:**

O `Automation Engine` não é chamado diretamente — ele *reage* a eventos de domínio publicados pelos outros contextos. `Task Management` publica `TaskStatusChanged`; `Automation Engine` consome e decide se alguma regra de webhook se aplica. Essa inversão de dependência garante que adicionar novos triggers de automação nunca modifica o domínio de tarefas.

**Benefícios:**
- Times diferentes evoluem os contextos em velocidades distintas sem quebrar contratos.
- Testes do `Automation Engine` não precisam de um agente real — basta publicar eventos sintéticos.
- O `AuditLog` fica exclusivamente no contexto de Automações, sem poluir o modelo de domínio de tarefas com concerns de observabilidade.

---

## Por que asyncio nativo e não Celery/Redis?

A stack de mensageria usa `asyncio.create_task` em vez de workers externos (Celery, RabbitMQ, Redis) por uma decisão deliberada de escopo:

- O volume de eventos deste sistema não justifica a complexidade operacional de um broker externo
- `asyncio.create_task` é não-bloqueante, desacopla o processamento da resposta HTTP e demonstra domínio do modelo de concorrência nativo do Python
- O `ConnectionManager` in-memory particionado por `organization_id` é suficiente para WebSocket num ambiente de instância única
- Adicionar Redis Pub/Sub seria a evolução natural para escalar horizontalmente — conforme detalhado na resposta da Questão 2 do questionário técnico acima
