# Plan de Construcción: CyberDemo - SOC Tier-1 Agentic AI Analyst

**Versión:** 1.0
**Fecha:** 13 Febrero 2026
**Autor:** Claude + Oscar

---

## 0. Visión General

Este documento describe cómo construir **CyberDemo**, una infraestructura de simulación completa para demostrar un agente SOC Tier-1 que investiga alertas de malware, toma decisiones de contención, y aplica Human-in-the-Loop para activos críticos.

### Principio Fundamental: SoulInTheBot es el Agente

**CyberDemo NO implementa un agente propio**. SoulInTheBot (el agente ya existente) consumirá las APIs y herramientas que CyberDemo expone mediante **MCP (Model Context Protocol)**.

CyberDemo proporciona:

1. **Datos sintéticos realistas** (superficie de ataque, EDR, SIEM, Intel, CTEM)
2. **APIs Mock** que simulan SIEM/EDR/Intel/SOAR/Ticketing
3. **Frontend interactivo** con **MCP Server integrado** para visualización bidireccional
4. **Plugin SoulInTheBot** con skills, tools y configuración MCP
5. **MCP Datos Sintéticos** independiente y reutilizable

### Arquitectura Bidireccional MCP

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
│  │                                                                       │  │
│  │  Herramientas MCP expuestas:                                          │  │
│  │  • show_simulation(data)      - Muestra simulación en tiempo real    │  │
│  │  • generate_chart(config)     - Genera visualización                 │  │
│  │  • run_demo_scenario(id)      - Ejecuta escenario de demo            │  │
│  │  • get_demo_state()           - Obtiene estado actual de la demo     │  │
│  │  • update_dashboard(metrics)  - Actualiza métricas del dashboard     │  │
│  │  • show_alert_timeline(id)    - Muestra timeline de investigación    │  │
│  │  • highlight_asset(id)        - Resalta activo en el grafo           │  │
│  │  • show_postmortem(id)        - Muestra informe postmortem           │  │
│  │                                                                       │  │
│  │  WebSocket: ws://localhost:3001/ws (updates en tiempo real)          │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  Backend API (FastAPI) + MCP Server                                  │  │
│  │  Puerto: 8000 (REST) + 8001 (MCP)                                    │  │
│  │                                                                       │  │
│  │  Herramientas MCP (SOC Operations):                                   │  │
│  │  • siem.list_incidents()      • edr.get_detection()                  │  │
│  │  • siem.get_incident()        • edr.get_process_tree()               │  │
│  │  • siem.add_comment()         • edr.hunt_hash()                      │  │
│  │  • siem.close_incident()      • edr.contain_host()                   │  │
│  │  • intel.get_indicator()      • ctem.get_asset_risk()                │  │
│  │  • approvals.get()            • soar.run_playbook()                  │  │
│  │  • approvals.request()        • tickets.create()                     │  │
│  │  • reports.generate_postmortem()                                      │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  MCP Datos Sintéticos (Independiente)                                │  │
│  │  Puerto: 8002 (MCP)                                                  │  │
│  │                                                                       │  │
│  │  Herramientas MCP:                                                    │  │
│  │  • data.generate_assets(count, seed)                                 │  │
│  │  • data.generate_edr_detections(count, seed)                         │  │
│  │  • data.generate_siem_incidents(seed)                                │  │
│  │  • data.generate_threat_intel(count, seed)                           │  │
│  │  • data.generate_ctem_findings(seed)                                 │  │
│  │  • data.generate_all(seed)                                           │  │
│  │  • data.reset()                                                       │  │
│  │  • data.get_health()                                                  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌──────────────┐  ┌──────────────┐                                       │
│  │  OpenSearch  │  │  PostgreSQL  │                                       │
│  │    :9200     │  │    :5432     │                                       │
│  └──────────────┘  └──────────────┘                                       │
└───────────────────────────────────────────────────────────────────────────┘
```

### Flujo de Ejemplo con MCP

```
Usuario → "Investiga el incidente INC-001 y muestra el resultado"
         ↓
    SoulInTheBot (Claude)
         ↓
    1. Llama: cyberdemo-api.siem.get_incident("INC-001")
         ↓
    2. Llama: cyberdemo-api.edr.get_process_tree(detection_id)
         ↓
    3. Llama: cyberdemo-api.intel.get_indicator("filehash", sha256)
         ↓
    4. Llama: cyberdemo-frontend.show_alert_timeline("INC-001")
         ↓
    5. Llama: cyberdemo-frontend.highlight_asset(asset_id)
         ↓
    Frontend Web muestra visualización en tiempo real
         ↓
    SoulInTheBot genera resumen y recomendaciones
```

### Ventajas de la Arquitectura MCP

- **Bidireccional completo**: SoulInTheBot controla el frontend y viceversa
- **Estándar MCP**: Todo habla el mismo protocolo
- **Modular**: Componentes independientes y reutilizables
- **Descubrimiento automático**: Claude ve todas las herramientas disponibles
- **WebSockets**: Updates en tiempo real del frontend
- **Extensible**: Fácil añadir nuevos MCPs o herramientas

---

## 1. Flujo Objetivo

```
[1] CS Alert → Ingestion → Sentinel Incident → Trigger
    ↓
[2] AI Reasoning Loop (SoulInTheBot):
    • Parsea host/hash/user
    • Enriquece con VirusTotal + Intel
    • Decodifica comandos
    • Busca propagación en la org
    • Calcula Confidence Score
    ↓
[3] Human & Execution:
    • Score alto + no-VIP → Auto-containment
    • VIP/Server → Solicita aprobación humana
    • Score bajo → Marca como False Positive
    ↓
[4] Action & Closure:
    • Ejecuta contención (mock)
    • Notifica al cliente
    • Crea ticket
    • Genera postmortem
    • Cierra incidente
```

---

## 2. Criterios de Éxito

| Criterio        | Descripción                                       | Cómo se Demuestra                                 |
| --------------- | ------------------------------------------------- | ------------------------------------------------- |
| **Reasoning**   | SoulInTheBot decide qué tools usar según contexto | Decision logs + tool trace en `agent-events-v1`   |
| **Integration** | Acceso R/W bidireccional al EDR (mock)            | Lee detecciones, escribe contenciones             |
| **Safety**      | VIP/Server requiere Human-in-the-Loop             | Policy Engine determinista bloquea sin aprobación |
| **Reporting**   | Resumen en lenguaje natural                       | Postmortem auto-generado por SoulInTheBot         |

---

## 3. Arquitectura

### 3.1 Stack Tecnológico

| Capa              | Tecnología                             | Versión      |
| ----------------- | -------------------------------------- | ------------ |
| **Backend**       | Python + FastAPI + Uvicorn             | Python 3.12+ |
| **ORM**           | SQLAlchemy 2.0 (async)                 | 2.0+         |
| **DB Driver**     | asyncpg (PostgreSQL async)             | 0.29+        |
| **Base de Datos** | PostgreSQL                             | 15           |
| **Búsqueda**      | OpenSearch (índices + k-NN)            | 2.x          |
| **Frontend**      | React + Vite + Tailwind + Cytoscape.js | React 18     |
| **MCP Backend**   | Python + FastMCP                       | -            |
| **MCP Frontend**  | TypeScript + WebSocket                 | -            |

### 3.2 Componentes y Puertos

| Componente                | Tecnología                       | Puerto | Responsabilidad                              |
| ------------------------- | -------------------------------- | ------ | -------------------------------------------- |
| **Frontend**              | React 18 + Vite + Tailwind       | 3000   | UI: dashboard, grafos, timeline, postmortems |
| **Frontend MCP Server**   | TypeScript + WebSocket           | 3001   | Herramientas MCP para visualización          |
| **Backend API**           | Python 3.12+ / FastAPI / Uvicorn | 8000   | APIs para SIEM/EDR/Intel/CTEM/SOAR/Tickets   |
| **Backend MCP Server**    | Python 3.12+ / FastMCP           | 8001   | Herramientas MCP para operaciones SOC        |
| **Data MCP Server**       | Python 3.12+ / FastMCP           | 8002   | Herramientas MCP para datos sintéticos       |
| **OpenSearch**            | OpenSearch 2.x                   | 9200   | Almacén de datos (17 índices)                |
| **OpenSearch Dashboards** | OS Dashboards                    | 5601   | Dashboards nativos SOC                       |
| **Generadores**           | Python 3.12+ scripts             | -      | Datos sintéticos reproducibles               |
| **PostgreSQL**            | PostgreSQL 15 + asyncpg          | 5432   | Metadatos, usuarios, sesiones                |
| **Zammad** (opcional)     | Zammad                           | 8080   | Sistema de tickets real                      |

### 3.3 Diagrama de Capas

```
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND WEB (React) - Puerto 3000                               │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐│
│ │Generación│ │Dashboard │ │Superficie│ │ Timeline │ │Postmortem││
│ │ de Datos │ │ & Métr.  │ │de Ataque │ │ Agente   │ │ Tickets  ││
│ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘│
├──────┴───────────┴───────────┴───────────┴───────────┴──────────┤
│ BACKEND API (FastAPI) - Puerto 8000                              │
│ /gen/* /siem/* /edr/* /intel/* /ctem/* /approvals/* /soar/*     │
│ /tickets/* /reports/* /graph/* /skill/*                          │
├─────────────────────────────────────────────────────────────────┤
│ OPENSEARCH (17 índices -v1) - Puerto 9200                        │
│ assets-inventory  edr-detections  edr-process-trees  siem-*     │
│ ctem-*  threat-intel  approvals  soar-actions  agent-events     │
├─────────────────────────────────────────────────────────────────┤
│ GENERADORES SINTÉTICOS (Python)                                  │
│ gen_assets.py  gen_edr.py  gen_siem.py  gen_intel.py  gen_ctem.py│
└─────────────────────────────────────────────────────────────────┘
```

### 3.4 Índices OpenSearch (17 índices -v1)

| Índice                 | Volumen  | Descripción                    |
| ---------------------- | -------- | ------------------------------ |
| `assets-inventory-v1`  | 1000     | Inventario de activos          |
| `edr-detections-v1`    | 1000     | Alertas EDR estilo CrowdStrike |
| `edr-process-trees-v1` | 1000     | Árboles de procesos            |
| `edr-hunt-results-v1`  | ~50      | Propagación por hash           |
| `edr-host-actions-v1`  | Variable | Acciones sobre hosts           |
| `siem-incidents-v1`    | ~650     | Incidentes tipo Sentinel       |
| `siem-entities-v1`     | ~2000    | Entidades por incidente        |
| `siem-comments-v1`     | Variable | Timeline de comentarios        |
| `ctem-findings-v1`     | ~3000    | Vulnerabilidades CVE           |
| `ctem-asset-risk-v1`   | 1000     | Riesgo agregado por activo     |
| `threat-intel-v1`      | ~200     | Reputación de IOCs             |
| `collab-messages-v1`   | Variable | Mensajes canal SOC             |
| `approvals-v1`         | Variable | Decisiones humanas             |
| `soar-actions-v1`      | Variable | Playbooks ejecutados           |
| `tickets-sync-v1`      | Variable | Mirror de tickets              |
| `agent-events-v1`      | Variable | Traza del agente               |
| `postmortems-v1`       | Variable | Metadatos de informes          |

---

## 4. Estrategia de Desarrollo: TDD + Agentes en Paralelo

### 4.1 Principio TDD

**Orden obligatorio para cada componente:**

1. Escribir tests unitarios (RED)
2. Escribir tests de integración (RED)
3. Implementar código mínimo para pasar tests (GREEN)
4. Refactorizar si es necesario (REFACTOR)

### 4.2 Workstreams Paralelos (8-10 Agentes)

El desarrollo se organiza en workstreams independientes que pueden ejecutarse en paralelo:

| #       | Workstream         | Responsabilidad                     | Dependencias      |
| ------- | ------------------ | ----------------------------------- | ----------------- |
| **W1**  | Generador Assets   | `gen_assets.py` + tests             | OpenSearch        |
| **W2**  | Generador EDR      | `gen_edr.py` + tests                | W1 (usa assets)   |
| **W3**  | Generador Intel    | `gen_intel.py` + tests              | OpenSearch        |
| **W4**  | Generador CTEM     | `gen_ctem.py` + tests               | W1 (usa assets)   |
| **W5**  | Generador SIEM     | `gen_siem.py` + tests               | W2, W3, W4        |
| **W6**  | APIs Backend       | FastAPI endpoints + tests           | W1-W5 (lee datos) |
| **W7**  | Frontend Core      | React + Vite + pages                | W6 (consume APIs) |
| **W8**  | Frontend Grafos    | Cytoscape.js + visualización        | W7                |
| **W9**  | Skill SoulInTheBot | Tools + integration                 | W6                |
| **W10** | Tests E2E          | Playwright + scenarios              | Todo              |
| **W11** | MCP Servers        | 3 MCP servers + plugin SoulInTheBot | W6, W7            |

```
Semana 1-2 (Paralelo):
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│ W1  │ │ W3  │ │ W6  │ │ W7  │
│Asset│ │Intel│ │APIs │ │Front│
└──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘
   │       │       │       │
Semana 2-3 (Secuencial parcial):
┌──┴──┐ ┌──┴──┐    │       │
│ W2  │ │ W4  │    │       │
│ EDR │ │CTEM │    │       │
└──┬──┘ └──┬──┘    │       │
   │       │       │       │
Semana 3-4:        │       │
┌──┴───────┴──┐    │    ┌──┴──┐
│     W5      │    │    │ W8  │
│    SIEM     │    │    │Graph│
└─────────────┘    │    └─────┘
                   │
Semana 4-5:     ┌──┴──┐ ┌─────┐
                │ W9  │ │ W10 │
                │Skill│ │ E2E │
                └─────┘ └─────┘
```

---

## 5. Fases de Construcción

### Fase 1: Infraestructura Base (Días 1-2)

**Objetivo:** Docker Compose funcional + OpenSearch + estructura base

| Tarea                | Tests Primero              | Implementación                        |
| -------------------- | -------------------------- | ------------------------------------- |
| Docker Compose       | Test: servicios levantados | `docker/docker-compose.yml`           |
| OpenSearch templates | Test: templates creados    | `backend/src/opensearch/templates.py` |
| Health checks        | Test: `/health` responde   | `backend/src/api/health.py`           |

### Fase 2: Generadores de Datos (Días 3-7)

**Objetivo:** Datos sintéticos reproducibles y realistas

#### W1: Generador de Assets (1000 activos)

```python
# Tests primero (backend/tests/generators/test_gen_assets.py)
def test_generates_1000_assets():
    assets = generate_assets(count=1000, seed=42)
    assert len(assets) == 1000

def test_assets_have_required_fields():
    assets = generate_assets(count=10, seed=42)
    for asset in assets:
        assert "asset_id" in asset
        assert "hostname" in asset
        assert "tags" in asset

def test_vip_distribution():
    assets = generate_assets(count=1000, seed=42)
    vip_count = sum(1 for a in assets if "vip" in a.get("tags", []))
    assert 30 < vip_count < 100  # ~5-8% VIPs

def test_reproducibility():
    assets1 = generate_assets(count=100, seed=42)
    assets2 = generate_assets(count=100, seed=42)
    assert assets1 == assets2
```

Distribución de activos:
| Tipo | % | Ejemplos |
|------|---|----------|
| Workstations | 70% | DESKTOP-, WS-, MAC-_ |
| Servers | 20% | SRV-, DC-, DB-_ |
| Móviles | 8% | MOB-, IPHONE-_ |
| Otros | 2% | VDI-, IOT-_ |

#### W2: Generador EDR (1000 detecciones)

```python
# Tests primero
def test_generates_1000_detections():
    detections = generate_edr_detections(count=1000, seed=42)
    assert len(detections) == 1000

def test_detections_reference_existing_assets():
    assets = generate_assets(count=100, seed=42)
    detections = generate_edr_detections(count=50, assets=assets, seed=42)
    asset_ids = {a["asset_id"] for a in assets}
    for det in detections:
        assert det["asset_id"] in asset_ids

def test_process_tree_generated_for_each_detection():
    detections = generate_edr_detections(count=10, seed=42)
    for det in detections:
        assert "process_tree" in det or det["detection_id"] in process_trees

def test_mitre_techniques_present():
    detections = generate_edr_detections(count=100, seed=42)
    techniques = {d["behavior"]["technique_id"] for d in detections}
    assert "T1059.001" in techniques  # PowerShell
```

**Plantillas de cmdline realistas:**

```python
CMDLINE_TEMPLATES = {
    "powershell_encoded": [
        "powershell.exe -enc {base64} -ExecutionPolicy Bypass",
        "powershell.exe -w hidden -nop -enc {base64}",
    ],
    "lateral_movement": [
        "wmic /node:{host} process call create 'cmd.exe /c {payload}'",
        "psexec.exe \\\\{host} -u {domain}\\{user} cmd.exe",
    ],
    "credential_theft": [
        "mimikatz.exe \"sekurlsa::logonpasswords\" exit",
        "procdump.exe -ma lsass.exe lsass_dump.dmp",
    ],
}
```

#### W3: Generador Intel (~200 IOCs)

```python
def test_generates_iocs_with_verdicts():
    iocs = generate_threat_intel(count=200, seed=42)
    verdicts = {ioc["verdict"] for ioc in iocs}
    assert "malicious" in verdicts
    assert "benign" in verdicts

def test_malicious_hash_consistency():
    """Los hashes usados en casos ancla deben ser maliciosos."""
    iocs = generate_threat_intel(seed=42)
    h1 = find_ioc_by_value(iocs, ANCHOR_HASH_1)
    assert h1["verdict"] == "malicious"
    assert h1["vt_score"] >= "60/74"
```

#### W4: Generador CTEM (vulnerabilidades)

```python
def test_ctem_risk_colors():
    assets = generate_assets(count=100, seed=42)
    ctem = generate_ctem_findings(assets=assets, seed=42)
    colors = {c["risk"] for c in ctem}
    assert colors == {"Green", "Yellow", "Red"}

def test_servers_skew_higher_risk():
    assets = generate_assets(count=100, seed=42)
    ctem = generate_ctem_findings(assets=assets, seed=42)
    server_assets = [a for a in assets if "server" in a.get("tags", [])]
    server_risks = [c for c in ctem if c["asset_id"] in {a["asset_id"] for a in server_assets}]
    red_count = sum(1 for r in server_risks if r["risk"] == "Red")
    assert red_count / len(server_risks) > 0.2  # >20% rojos
```

#### W5: Generador SIEM (incidentes enriquecidos)

```python
def test_creates_incidents_from_detections():
    detections = generate_edr_detections(count=100, seed=42)
    incidents = generate_siem_incidents(detections=detections, seed=42)
    assert len(incidents) > 0
    assert len(incidents) <= len(detections)

def test_anchor_cases_exist():
    """Los 3 casos ancla siempre se crean."""
    incidents = generate_siem_incidents(seed=42)
    ids = {i["incident_id"] for i in incidents}
    assert ANCHOR_INCIDENT_1 in ids
    assert ANCHOR_INCIDENT_2 in ids
    assert ANCHOR_INCIDENT_3 in ids

def test_entities_created_per_incident():
    incidents = generate_siem_incidents(seed=42)
    entities = get_all_entities()
    for inc in incidents:
        inc_entities = [e for e in entities if e["incident_id"] == inc["incident_id"]]
        assert len(inc_entities) >= 1  # Al menos host entity
```

### Fase 3: APIs Backend (Días 5-10)

**Objetivo:** FastAPI con todos los endpoints + validación

#### Endpoints por Servicio

| Servicio  | Método | Endpoint                            | Descripción                      |
| --------- | ------ | ----------------------------------- | -------------------------------- |
| GenOps    | POST   | `/gen/reset`                        | Borra índices y recrea templates |
| GenOps    | POST   | `/gen/all`                          | Genera todos los datos           |
| GenOps    | POST   | `/gen/assets`                       | Solo superficie de ataque        |
| GenOps    | POST   | `/gen/edr`                          | Solo detecciones EDR             |
| GenOps    | POST   | `/gen/siem`                         | Solo incidentes SIEM             |
| GenOps    | GET    | `/gen/health`                       | Estado de generación             |
| SIEM      | GET    | `/siem/incidents`                   | Lista incidentes                 |
| SIEM      | GET    | `/siem/incidents/{id}`              | Detalle incidente                |
| SIEM      | GET    | `/siem/incidents/{id}/entities`     | Entidades                        |
| SIEM      | POST   | `/siem/incidents/{id}/comments`     | Añadir comentario                |
| EDR       | GET    | `/edr/detections`                   | Lista detecciones                |
| EDR       | GET    | `/edr/detections/{id}`              | Detalle detección                |
| EDR       | GET    | `/edr/detections/{id}/process-tree` | Árbol de procesos                |
| EDR       | GET    | `/edr/hunt/hash/{sha256}`           | Propagación                      |
| EDR       | POST   | `/edr/devices/{id}/contain`         | Contener host                    |
| Intel     | GET    | `/intel/indicators/{type}/{value}`  | Reputación                       |
| CTEM      | GET    | `/ctem/assets/{id}`                 | Riesgo CTEM                      |
| Approvals | GET    | `/approvals/{incident_id}`          | Estado aprobación                |
| Approvals | POST   | `/approvals/{incident_id}`          | Aprobar/rechazar                 |
| SOAR      | POST   | `/soar/actions`                     | Ejecutar playbook                |
| Tickets   | POST   | `/tickets/create`                   | Crear ticket                     |
| Reports   | POST   | `/reports/postmortem/{id}`          | Generar postmortem               |
| Graph     | GET    | `/graph/incident/{id}`              | Datos para grafo                 |

```python
# backend/tests/api/test_siem.py
@pytest.mark.asyncio
async def test_list_incidents(client: AsyncClient):
    response = await client.get("/siem/incidents")
    assert response.status_code == 200
    data = response.json()
    assert "incidents" in data
    assert isinstance(data["incidents"], list)

@pytest.mark.asyncio
async def test_get_incident_detail(client: AsyncClient):
    response = await client.get(f"/siem/incidents/{ANCHOR_INCIDENT_1}")
    assert response.status_code == 200
    data = response.json()
    assert data["incident_id"] == ANCHOR_INCIDENT_1
    assert "severity" in data
    assert "entities_ref" in data
```

### Fase 4: Frontend (Días 8-14)

**Objetivo:** UI interactiva con todas las pestañas

#### Pestañas del Frontend

1. **Generación de Datos**
   - Botones para cada generador
   - Barra de progreso
   - Contadores por índice
   - Seed editable

2. **Dashboard & Métricas**
   - KPIs: Total incidentes, Críticos abiertos, Hosts contenidos, MTTR
   - Gráficos: Incidentes por hora, distribución severidad, top MITRE

3. **Explorador de Activos**
   - Tabla filtrable (tipo, OS, site, risk, tags)
   - Panel detalle al click
   - Capas: Base/EDR/SIEM/CTEM/Threats

4. **Visualización Grafos** (Cytoscape.js)
   - Grafo sistema: fuentes → incidentes → assets
   - Grafo incidente: host → hash → procesos → acciones
   - Colores: Verde/Amarillo/Rojo/Azul(contenido)
   - Panel lateral con 4 secciones:
     - (a) Quién es el activo
     - (b) Cuál es la amenaza
     - (c) Qué recomienda el agente
     - (d) Estado contención/ticket

5. **Timeline del Agente**
   - Vista waterfall paso a paso
   - Cada fase expandible
   - Links a evidencias

6. **Lista de Incidentes**
   - Tabla con filtros
   - Detalle con entidades y timeline

7. **Informes Postmortem**
   - Lista de informes generados
   - Vista del informe con gráficos

8. **Tickets**
   - Lista sincronizada con Zammad
   - Estado y enlaces

```typescript
// frontend/src/pages/__tests__/Dashboard.test.tsx
describe('Dashboard', () => {
  it('renders KPIs correctly', async () => {
    render(<Dashboard />);
    expect(await screen.findByText(/Total Incidentes/i)).toBeInTheDocument();
    expect(await screen.findByText(/Críticos Abiertos/i)).toBeInTheDocument();
  });

  it('fetches data on mount', async () => {
    const mockFetch = jest.spyOn(api, 'getDashboardStats');
    render(<Dashboard />);
    await waitFor(() => expect(mockFetch).toHaveBeenCalled());
  });
});
```

### Fase 5: Skill para SoulInTheBot (Días 12-16)

**Objetivo:** Tools que SoulInTheBot usará para investigar

#### Estructura del Skill

```
skills/soc-analyst/
├── SKILL.md              # Documentación
├── skill.yaml            # Definición del skill
├── tools/
│   ├── siem_query.py     # siem.listIncidents, siem.getIncident
│   ├── edr_investigate.py # edr.getDetection, edr.getProcessTree
│   ├── edr_contain.py    # edr.containHost
│   ├── intel_lookup.py   # intel.getIndicator
│   ├── ctem_lookup.py    # ctem.getAssetRisk
│   ├── approval.py       # approvals.get, approvals.request
│   ├── ticket.py         # tickets.create
│   └── report.py         # reports.generatePostmortem
├── policies/
│   └── containment_policy.yaml
└── tests/
    ├── test_siem_tools.py
    ├── test_edr_tools.py
    └── test_integration.py
```

#### Interfaz de Tools

```python
# Lo que SoulInTheBot puede usar
siem.listIncidents(filters) -> {incidents[]}
siem.getIncident(incident_id) -> {incident}
siem.addComment(incident_id, message) -> {comment_id}

edr.getDetection(detection_id) -> {detection}
edr.getProcessTree(detection_id) -> {process_tree}
edr.huntHash(sha256) -> {scope: hosts[]}
edr.containHost(device_id, reason) -> {action_id, status}

intel.getIndicator(type, value) -> {verdict, confidence, labels[]}

ctem.getAssetRisk(asset_id) -> {risk_color, findings[]}

approvals.get(incident_id) -> {status, decided_by}
approvals.request(incident_id, card_data) -> {approval_id}

tickets.create(payload) -> {ticket_id, url}

reports.generatePostmortem(incident_id) -> {report_id, artifacts[]}
```

#### Policy Engine (Determinista - NO depende del LLM)

```python
class PolicyEngine:
    CONFIDENCE_HIGH = 90
    CONFIDENCE_MEDIUM = 50
    CRITICAL_TAGS = {"vip", "executive", "server", "domain-controller"}

    def evaluate(self, confidence_score, device_tags, has_approval=False):
        is_critical = bool(set(device_tags) & self.CRITICAL_TAGS)

        if confidence_score < self.CONFIDENCE_MEDIUM:
            return {"action": "mark_false_positive", "requires_approval": False}

        if is_critical:
            if has_approval:
                return {"action": "contain", "requires_approval": False}
            return {"action": "request_approval", "requires_approval": True}

        if confidence_score >= self.CONFIDENCE_HIGH:
            return {"action": "contain", "requires_approval": False}

        return {"action": "request_approval", "requires_approval": True}
```

### Fase 6: Tests E2E (Días 14-18)

**Objetivo:** Validar los 3 escenarios de demo end-to-end

#### Los 3 Escenarios Ancla

| Caso | Host          | Tags           | Hash           | Confidence | Resultado         |
| ---- | ------------- | -------------- | -------------- | ---------- | ----------------- |
| 1    | WS-FIN-042    | standard-user  | H1 (malicioso) | 95%        | Auto-containment  |
| 2    | LAPTOP-CFO-01 | vip, executive | H1 (mismo)     | 95%        | Human-in-the-Loop |
| 3    | SRV-DEV-03    | standard       | H2 (benigno)   | 22%        | False Positive    |

```python
# tests/e2e/test_scenarios.py
@pytest.mark.e2e
async def test_scenario_1_auto_containment():
    """Escenario 1: Malware en workstation estándar → Auto-containment."""
    # 1. Verificar que el incidente ancla existe
    incident = await api.get_incident(ANCHOR_INCIDENT_1)
    assert incident["severity"] == "High"

    # 2. Simular que SoulInTheBot investiga
    detection = await api.get_detection(incident["relatedDetections"][0])
    process_tree = await api.get_process_tree(detection["detection_id"])
    intel = await api.get_indicator("filehash", detection["file"]["sha256"])
    hunt = await api.hunt_hash(detection["file"]["sha256"])

    # 3. Verificar datos correctos
    assert intel["verdict"] == "malicious"
    assert hunt["total_hosts_found"] >= 3

    # 4. Verificar que Policy Engine permite auto-containment
    asset = await api.get_asset(detection["asset_id"])
    policy = PolicyEngine()
    decision = policy.evaluate(95, asset["tags"])
    assert decision["action"] == "contain"
    assert decision["requires_approval"] == False

    # 5. Ejecutar contención
    result = await api.contain_host(detection["device_id"], "Auto-containment")
    assert result["status"] == "success"

    # 6. Verificar que el asset está contenido
    asset = await api.get_asset(detection["asset_id"])
    assert asset["edr"]["containment"] == "contained"

@pytest.mark.e2e
async def test_scenario_2_vip_requires_approval():
    """Escenario 2: Malware en laptop VIP → Requiere aprobación."""
    incident = await api.get_incident(ANCHOR_INCIDENT_2)
    detection = await api.get_detection(incident["relatedDetections"][0])
    asset = await api.get_asset(detection["asset_id"])

    # Verificar que es VIP
    assert "vip" in asset["tags"] or "executive" in asset["tags"]

    # Policy Engine debe requerir aprobación
    policy = PolicyEngine()
    decision = policy.evaluate(95, asset["tags"], has_approval=False)
    assert decision["requires_approval"] == True

    # Simular aprobación
    await api.set_approval(incident["incident_id"], "approved")

    # Ahora sí permite containment
    decision = policy.evaluate(95, asset["tags"], has_approval=True)
    assert decision["action"] == "contain"

@pytest.mark.e2e
async def test_scenario_3_false_positive():
    """Escenario 3: Script legítimo → False Positive."""
    incident = await api.get_incident(ANCHOR_INCIDENT_3)
    detection = await api.get_detection(incident["relatedDetections"][0])
    intel = await api.get_indicator("filehash", detection["file"]["sha256"])

    # Verificar bajo confidence
    assert intel["vt_score"] < "10/74" or intel["verdict"] == "benign"

    # Policy Engine debe marcar como FP
    policy = PolicyEngine()
    decision = policy.evaluate(22, [])
    assert decision["action"] == "mark_false_positive"
```

### Fase 7: MCP Servers y Plugin SoulInTheBot (Días 15-20)

**Objetivo:** 3 MCP Servers + Plugin completo para SoulInTheBot

#### W11: MCP Servers

##### Frontend MCP Server (Puerto 3001)

```typescript
// frontend/src/mcp/server.ts
export const frontendMCPTools = {
  show_simulation: {
    description: "Muestra simulación en tiempo real en el dashboard",
    parameters: { data: "object" },
    handler: async (data) => {
      /* actualiza UI via WebSocket */
    },
  },
  generate_chart: {
    description: "Genera y muestra una visualización",
    parameters: { type: "string", config: "object" },
    handler: async (type, config) => {
      /* renderiza chart */
    },
  },
  run_demo_scenario: {
    description: "Ejecuta un escenario de demo (1, 2 o 3)",
    parameters: { scenario_id: "number" },
    handler: async (id) => {
      /* trigger demo flow */
    },
  },
  get_demo_state: {
    description: "Obtiene el estado actual de la demo",
    handler: async () => {
      /* retorna state */
    },
  },
  update_dashboard: {
    description: "Actualiza métricas del dashboard",
    parameters: { metrics: "object" },
  },
  show_alert_timeline: {
    description: "Muestra timeline de investigación de una alerta",
    parameters: { incident_id: "string" },
  },
  highlight_asset: {
    description: "Resalta un activo en el grafo de superficie",
    parameters: { asset_id: "string" },
  },
  show_postmortem: {
    description: "Muestra informe postmortem en pantalla",
    parameters: { incident_id: "string" },
  },
};
```

##### Backend MCP Server (Puerto 8001)

```python
# backend/src/mcp/server.py
from fastmcp import FastMCP

mcp = FastMCP("CyberDemo SOC Operations")

@mcp.tool()
async def siem_list_incidents(status: str = "open", severity: str = None):
    """Lista incidentes del SIEM con filtros opcionales."""
    # ... implementación

@mcp.tool()
async def siem_get_incident(incident_id: str):
    """Obtiene detalle completo de un incidente."""
    # ... implementación

@mcp.tool()
async def siem_add_comment(incident_id: str, message: str):
    """Añade un comentario al timeline del incidente."""
    # ... implementación

@mcp.tool()
async def edr_get_detection(detection_id: str):
    """Obtiene detalle de una detección EDR."""
    # ... implementación

@mcp.tool()
async def edr_get_process_tree(detection_id: str):
    """Obtiene el árbol de procesos de una detección."""
    # ... implementación

@mcp.tool()
async def edr_hunt_hash(sha256: str):
    """Busca propagación de un hash en la organización."""
    # ... implementación

@mcp.tool()
async def edr_contain_host(device_id: str, reason: str):
    """Ejecuta contención de red en un host."""
    # ... implementación

@mcp.tool()
async def intel_get_indicator(indicator_type: str, value: str):
    """Obtiene reputación de un indicador (hash, IP, dominio)."""
    # ... implementación

@mcp.tool()
async def ctem_get_asset_risk(asset_id: str):
    """Obtiene riesgo CTEM y vulnerabilidades de un activo."""
    # ... implementación

@mcp.tool()
async def approvals_get(incident_id: str):
    """Obtiene estado de aprobación para un incidente."""
    # ... implementación

@mcp.tool()
async def approvals_request(incident_id: str, card_data: dict):
    """Solicita aprobación humana para una acción."""
    # ... implementación

@mcp.tool()
async def tickets_create(title: str, description: str, incident_id: str = None):
    """Crea un ticket en el sistema."""
    # ... implementación

@mcp.tool()
async def reports_generate_postmortem(incident_id: str):
    """Genera un informe postmortem para un incidente."""
    # ... implementación
```

##### Data MCP Server (Puerto 8002)

```python
# backend/src/mcp/data_server.py
from fastmcp import FastMCP

mcp = FastMCP("CyberDemo Synthetic Data")

@mcp.tool()
async def data_generate_assets(count: int = 1000, seed: int = 42):
    """Genera activos sintéticos para la superficie de ataque."""
    # ... implementación

@mcp.tool()
async def data_generate_edr_detections(count: int = 1000, seed: int = 42):
    """Genera detecciones EDR sintéticas."""
    # ... implementación

@mcp.tool()
async def data_generate_siem_incidents(seed: int = 42):
    """Genera incidentes SIEM correlacionados."""
    # ... implementación

@mcp.tool()
async def data_generate_threat_intel(count: int = 200, seed: int = 42):
    """Genera IOCs con reputación."""
    # ... implementación

@mcp.tool()
async def data_generate_ctem_findings(seed: int = 42):
    """Genera vulnerabilidades CTEM por activo."""
    # ... implementación

@mcp.tool()
async def data_generate_all(seed: int = 42):
    """Genera todos los datos sintéticos en orden correcto."""
    # ... implementación

@mcp.tool()
async def data_reset():
    """Borra todos los índices y recrea templates."""
    # ... implementación

@mcp.tool()
async def data_get_health():
    """Obtiene estado y conteos de todos los índices."""
    # ... implementación
```

#### Plugin SoulInTheBot

```yaml
# extensions/cyberdemo/package.json
{
  "name": "@soulinthebot/cyberdemo-soc-analyst",
  "version": "1.0.0",
  "description": "SOC Tier-1 Analyst plugin for CyberDemo",
  "main": "dist/index.js",
  "dependencies": { "moltbot": "*" },
  "moltbot":
    {
      "type": "plugin",
      "mcpServers":
        {
          "cyberdemo-frontend":
            { "url": "ws://localhost:3001/mcp", "description": "Frontend visualization tools" },
          "cyberdemo-api":
            {
              "url": "http://localhost:8001/mcp",
              "transport": "streamable-http",
              "description": "SOC operations API tools",
            },
          "cyberdemo-data":
            {
              "url": "http://localhost:8002/mcp",
              "transport": "streamable-http",
              "description": "Synthetic data generation tools",
            },
        },
      "skills":
        [
          {
            "name": "investigate-incident",
            "description": "Investiga un incidente SOC completo",
            "trigger": "/investigate",
          },
          { "name": "run-demo", "description": "Ejecuta un escenario de demo", "trigger": "/demo" },
        ],
    },
}
```

#### Configuración MCP en SoulInTheBot

```yaml
# ~/.SoulInTheBot/config.yaml (fragmento)
plugins:
  - name: cyberdemo-soc-analyst
    enabled: true

mcpServers:
  cyberdemo-frontend:
    url: ws://localhost:3001/mcp
    autoConnect: true
  cyberdemo-api:
    url: http://localhost:8001/mcp
    transport: streamable-http
  cyberdemo-data:
    url: http://localhost:8002/mcp
    transport: streamable-http
```

---

## 6. Docker Compose

```yaml
# docker/docker-compose.yml
version: "3.8"

services:
  opensearch:
    image: opensearchproject/opensearch:2.11.0
    environment:
      - discovery.type=single-node
      - DISABLE_SECURITY_PLUGIN=true
      - "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - opensearch-data:/usr/share/opensearch/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9200"]
      interval: 10s
      timeout: 5s
      retries: 5

  opensearch-dashboards:
    image: opensearchproject/opensearch-dashboards:2.11.0
    environment:
      - OPENSEARCH_HOSTS=["http://opensearch:9200"]
      - DISABLE_SECURITY_DASHBOARDS_PLUGIN=true
    ports:
      - "5601:5601"
    depends_on:
      opensearch:
        condition: service_healthy

  backend:
    build:
      context: ../backend
      dockerfile: ../docker/Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - OPENSEARCH_HOST=opensearch
      - OPENSEARCH_PORT=9200
    depends_on:
      opensearch:
        condition: service_healthy
    volumes:
      - ../backend/src:/app/src
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ../frontend
      dockerfile: ../docker/Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ../frontend/src:/app/src
    command: pnpm dev --host

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=cyberdemo
      - POSTGRES_PASSWORD=cyberdemo
      - POSTGRES_DB=cyberdemo
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  opensearch-data:
  postgres-data:
```

---

## 7. Secuencia de Demo

La demo sigue este orden exacto:

1. **Generación**: Pestaña "Generación" → "Generar Todo" → ver contadores
2. **Dashboard**: Ver métricas y distribuciones
3. **Superficie**: Explorar 1000 endpoints, activar capas
4. **Trigger Caso 1**: Auto-containment en workstation
5. **Trigger Caso 2**: Human-in-the-Loop para VIP
6. **Trigger Caso 3**: False Positive descartado
7. **Postmortems**: Ver los 3 informes generados
8. **Tickets**: Ver tickets sincronizados

---

## 8. Mejoras sobre el Documento Original

| Aspecto       | Original           | Mejorado                           |
| ------------- | ------------------ | ---------------------------------- |
| Agente        | Crear nuevo agente | Usar SoulInTheBot existente        |
| Gateway TS    | Express separado   | Eliminado (FastAPI directo)        |
| Faiss         | Vectores con Faiss | Solo OpenSearch k-NN               |
| Redis         | Mencionado         | Eliminado (no necesario para demo) |
| TDD           | No especificado    | TDD obligatorio desde inicio       |
| Paralelismo   | No detallado       | 8-10 workstreams paralelos         |
| Policy Engine | Implícito          | Explícito y determinista           |

---

## 9. Checklist de Validación Final

### Datos

- [ ] 1000 assets generados con distribución correcta
- [ ] 1000 detecciones EDR con process trees
- [ ] ~650 incidentes SIEM enriquecidos
- [ ] 3 casos ancla con IDs fijos
- [ ] Propagación: al menos 1 hash en ≥3 hosts

### APIs

- [ ] Todos los endpoints responden
- [ ] Contención actualiza asset state
- [ ] Aprobaciones funcionan
- [ ] Postmortems se generan

### Frontend

- [ ] 8 pestañas funcionando
- [ ] Grafos interactivos
- [ ] Timeline del agente
- [ ] Capas de superficie

### Skill

- [ ] Tools registrados en SoulInTheBot
- [ ] Policy Engine integrado
- [ ] 3 escenarios E2E pasan

---

## 10. Referencias

- CrowdStrike Falcon API: campos de detecciones
- Microsoft Sentinel: modelo de incidentes y entidades
- OpenSearch: index templates y dashboards
- Cytoscape.js: visualización de grafos
- Zammad API: ticketing

---

_Este plan está diseñado para ejecución con múltiples agentes Claude en paralelo, siguiendo TDD, y maximizando la reutilización de SoulInTheBot como el motor de IA._
