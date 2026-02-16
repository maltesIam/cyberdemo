# CyberDemo - SOC Tier-1 Agentic AI Analyst

Infraestructura de simulación para demostrar un agente SOC Tier-1 que investiga alertas de malware, toma decisiones de contención y aplica Human-in-the-Loop para activos críticos.

**Nota:** CyberDemo NO implementa un agente propio. **SoulInTheBot** (el agente existente) consume las APIs y herramientas que CyberDemo expone.

## Arquitectura MCP Bidireccional

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         SoulInTheBot                                      │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  Gateway (puerto 18789)                                             │  │
│  │  - Plugin: cyberdemo-soc-analyst                                    │  │
│  │  - MCP Clients configurados:                                        │  │
│  │    • cyberdemo-frontend (MCP Server del Frontend)                   │  │
│  │    • cyberdemo-data (MCP Server de Datos Sintéticos)                │  │
│  │    • cyberdemo-api (MCP Server del Backend FastAPI)                 │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  Claude puede llamar herramientas de cualquier MCP desde conversaciones   │
└───────────────────────────┬───────────────────────────────────────────────┘
                            │ MCP Protocol (bidireccional)
                            ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                      CyberDemo (Este Proyecto)                             │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  Frontend Web (React + Vite) + MCP Server                            │  │
│  │  Puerto: 3000 (Web) + 3001 (MCP)                                     │  │
│  │  Tools: show_simulation, generate_chart, run_demo_scenario, etc.     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  Backend API (FastAPI) + MCP Server                                  │  │
│  │  Puerto: 8000 (REST) + 8001 (MCP)                                    │  │
│  │  Tools: siem.*, edr.*, intel.*, ctem.*, approvals.*, tickets.*       │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  MCP Datos Sintéticos (Independiente)                                │  │
│  │  Puerto: 8002 (MCP)                                                  │  │
│  │  Tools: data.generate_*, data.reset, data.get_health                 │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌──────────────┐  ┌──────────────┐                                       │
│  │  OpenSearch  │  │  PostgreSQL  │                                       │
│  │    :9200     │  │    :5432     │                                       │
│  └──────────────┘  └──────────────┘                                       │
└───────────────────────────────────────────────────────────────────────────┘
```

## Stack Tecnológico

| Capa              | Tecnología                                   | Puerto    |
| ----------------- | -------------------------------------------- | --------- |
| **Backend**       | Python 3.12+ / FastAPI / Uvicorn             | 8000      |
| **ORM**           | SQLAlchemy 2.0 (async) + asyncpg             | -         |
| **Backend MCP**   | Python 3.12+ / FastMCP                       | 8001      |
| **Data MCP**      | Python 3.12+ / FastMCP                       | 8002      |
| **Frontend**      | React 18 + Vite + Tailwind + Cytoscape.js    | 3000      |
| **Frontend MCP**  | TypeScript + WebSocket                       | 3001      |
| **Datos**         | OpenSearch 2.x (índices + dashboards + k-NN) | 9200/5601 |
| **Base de Datos** | PostgreSQL 15                                | 5432      |
| **Agente IA**     | SoulInTheBot (externo) via MCP               | 18789     |

## Estructura de Directorios

```
CyberDemo/
├── backend/               # FastAPI backend
│   ├── src/
│   │   ├── api/           # Endpoints REST
│   │   ├── mcp/           # MCP Servers (SOC ops + Data)
│   │   │   ├── server.py      # Backend MCP Server (:8001)
│   │   │   ├── data_server.py # Data MCP Server (:8002)
│   │   │   └── tools/         # MCP tool implementations
│   │   ├── models/        # SQLAlchemy models
│   │   ├── services/      # Policy Engine, business logic
│   │   ├── generators/    # Generadores de datos sintéticos
│   │   ├── opensearch/    # Templates, queries
│   │   └── core/          # Config, deps
│   └── tests/
├── frontend/              # React + Vite
│   ├── src/
│   │   ├── components/    # Componentes reutilizables
│   │   ├── mcp/           # Frontend MCP Server (:3001)
│   │   │   ├── server.ts      # MCP Server entry
│   │   │   ├── websocket.ts   # WebSocket handler
│   │   │   └── tools/         # Visualization tools
│   │   ├── pages/         # Pestañas de la UI
│   │   ├── services/      # API client
│   │   └── hooks/
│   └── public/
├── extensions/            # Plugin para SoulInTheBot
│   └── cyberdemo/
│       ├── package.json   # MCP servers config
│       ├── src/
│       │   ├── index.ts
│       │   └── skills/    # /investigate, /demo
│       └── README.md
├── skills/                # Skill legacy (migrar a extensions/)
│   └── soc-analyst/
│       ├── SKILL.md
│       ├── skill.yaml
│       ├── tools/
│       └── policies/
├── docker/                # Docker Compose + Dockerfiles
├── scripts/               # Build, test, deploy
├── docs/                  # PLAN.md, PROGRESS.md
│   ├── PLAN.md
│   └── PROGRESS.md
└── tests/                 # Tests E2E
```

## Datos Sintéticos Generados

| Índice                 | Volumen | Descripción                      |
| ---------------------- | ------- | -------------------------------- |
| `assets-inventory-v1`  | 1000    | Superficie de ataque (endpoints) |
| `edr-detections-v1`    | 1000    | Alertas EDR estilo CrowdStrike   |
| `edr-process-trees-v1` | 1000    | Árboles de procesos              |
| `siem-incidents-v1`    | ~650    | Incidentes tipo Sentinel         |
| `threat-intel-v1`      | ~200    | IOCs con reputación              |
| `ctem-findings-v1`     | ~3000   | Vulnerabilidades CVE             |

## Desarrollo Local

### Requisitos

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- pnpm

### Con Docker Compose (recomendado)

```bash
cd CyberDemo/docker
docker-compose up -d
```

Accesos:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- OpenSearch Dashboards: http://localhost:5601

### Sin Docker

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn src.main:app --reload --port 8000

# Frontend
cd frontend
pnpm install
pnpm dev
```

## APIs Principales

| Servicio  | Endpoint                                | Descripción                        |
| --------- | --------------------------------------- | ---------------------------------- |
| GenOps    | `POST /gen/all`                         | Generar todos los datos sintéticos |
| GenOps    | `POST /gen/reset`                       | Limpiar y recrear índices          |
| SIEM      | `GET /siem/incidents`                   | Listar incidentes                  |
| EDR       | `GET /edr/detections/{id}/process-tree` | Árbol de procesos                  |
| EDR       | `POST /edr/devices/{id}/contain`        | Contener host                      |
| Intel     | `GET /intel/indicators/{type}/{value}`  | Reputación de IOC                  |
| CTEM      | `GET /ctem/assets/{id}`                 | Riesgo de vulnerabilidades         |
| Approvals | `POST /approvals/{incident_id}`         | Aprobar/rechazar acción            |

## Escenarios de Demo

| #   | Escenario            | Host                           | Resultado                  |
| --- | -------------------- | ------------------------------ | -------------------------- |
| 1   | **Auto-Containment** | WS-FIN-042 (standard)          | Contención automática      |
| 2   | **VIP Approval**     | LAPTOP-CFO-01 (vip, executive) | Requiere aprobación humana |
| 3   | **False Positive**   | SRV-DEV-03 (standard)          | Descartado (score bajo)    |

## Policy Engine

El Policy Engine es **determinista** (no depende del LLM):

```python
# Reglas
if confidence < 50%:
    → mark_false_positive

if asset.tags contains (vip, executive, server, domain-controller):
    if not has_approval:
        → request_approval
    else:
        → contain

if confidence >= 90%:
    → auto_contain
```

## MCP Servers

CyberDemo expone 3 MCP Servers que SoulInTheBot consume:

### Frontend MCP (Puerto 3001)

Herramientas de visualización:

```
show_simulation(data)      # Muestra simulación en tiempo real
generate_chart(config)     # Genera visualización
run_demo_scenario(id)      # Ejecuta escenario de demo (1, 2, 3)
get_demo_state()           # Obtiene estado actual
update_dashboard(metrics)  # Actualiza métricas
show_alert_timeline(id)    # Muestra timeline de investigación
highlight_asset(id)        # Resalta activo en el grafo
show_postmortem(id)        # Muestra informe postmortem
```

### Backend MCP (Puerto 8001)

Herramientas de operaciones SOC:

```
siem.list_incidents()      # Listar incidentes pendientes
siem.get_incident(id)      # Detalle de incidente
siem.add_comment(id, msg)  # Añadir comentario
edr.get_detection(id)      # Detalle de detección
edr.get_process_tree(id)   # Árbol de procesos
edr.hunt_hash(sha256)      # Buscar propagación
edr.contain_host(id)       # Ejecutar contención
intel.get_indicator(type, value)  # Reputación del IOC
ctem.get_asset_risk(id)    # Riesgo CTEM
approvals.get(id)          # Estado de aprobación
approvals.request(id, data) # Solicitar aprobación humana
tickets.create(payload)    # Crear ticket
reports.generate_postmortem(id) # Generar informe
```

### Data MCP (Puerto 8002)

Herramientas de generación de datos sintéticos:

```
data.generate_assets(count, seed)  # Genera activos
data.generate_edr_detections(count, seed)  # Genera detecciones
data.generate_siem_incidents(seed)  # Genera incidentes
data.generate_threat_intel(count, seed)  # Genera IOCs
data.generate_ctem_findings(seed)  # Genera vulnerabilidades
data.generate_all(seed)    # Genera todo en orden
data.reset()               # Limpia y recrea índices
data.get_health()          # Estado y conteos
```

## Plugin SoulInTheBot

El plugin `@soulinthebot/cyberdemo-soc-analyst` configura los 3 MCP clients y expone skills:

- `/investigate <incident_id>` - Investiga un incidente completo
- `/demo <scenario>` - Ejecuta un escenario de demo (1, 2, o 3)

## Documentación

- [PLAN.md](docs/PLAN.md) - Plan de construcción detallado
- [PROGRESS.md](docs/PROGRESS.md) - Progreso con checkboxes

## Variables de Entorno

```env
# Backend
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
DATABASE_URL=postgresql+asyncpg://cyberdemo:cyberdemo@localhost:5432/cyberdemo

# Frontend
VITE_API_URL=http://localhost:8000
```
