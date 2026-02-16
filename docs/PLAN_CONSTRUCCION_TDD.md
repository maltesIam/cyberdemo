# Plan de Construcción TDD - CyberDemo

> **Documento:** Plan de Construcción con TDD Estricto
> **Fecha:** 2026-02-14
> **Estado:** 📋 PLANIFICACIÓN
> **Metodología:** Test-Driven Development (Red → Green → Refactor)

---

## Resumen Ejecutivo

### Estado Actual del Proyecto

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     ESTADO ACTUAL: ~75% COMPLETADO                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ████████████████████████████████████████░░░░░░░░░░░░░░  75%           │
│                                                                         │
│  ✅ Completado (75%)           │  🔴 Pendiente (25%)                   │
│  ─────────────────────────────  │  ─────────────────────────────        │
│  • Infraestructura Docker       │  • W8: Grafos Cytoscape              │
│  • OpenSearch Templates (17)    │  • W11: MCP Servers (35 tools)       │
│  • Generadores (5)              │  • W12: Auto-Triggers (30)           │
│  • APIs REST (19 endpoints)     │  • Demo Scenarios E2E (3)            │
│  • Frontend (9 páginas)         │  • SOAR Endpoints                    │
│  • Policy Engine                │  • Graph Endpoints                   │
│  • Skill SoulInTheBot           │                                      │
│  • Tests E2E básicos            │                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Trabajo Pendiente por Workstream

| Workstream             | Componentes | Tests   | Impl   | Esfuerzo |
| ---------------------- | ----------- | ------- | ------ | -------- |
| **W8: Grafos**         | 3           | 4       | 11     | 16h      |
| **W11: MCP Backend**   | 8           | 20      | 9      | 20h      |
| **W11: MCP Frontend**  | 6           | 10      | 8      | 16h      |
| **W11: MCP Data**      | 3           | 9       | 4      | 12h      |
| **W12: Auto-Triggers** | 8           | 24      | 35     | 36h      |
| **Demo Scenarios**     | 3           | 27      | 6      | 12h      |
| **APIs Faltantes**     | 2           | 6       | 4      | 8h       |
| **Total**              | **33**      | **100** | **77** | **120h** |

### Línea Temporal

```
Semana 1          Semana 2          Semana 3          Semana 4
│                 │                 │                 │
├─ W11.1 MCP Bck  ├─ W8 Grafos      ├─ W12 Triggers   ├─ Demo Final
├─ W11.2 MCP Frt  ├─ W11.3 MCP Data ├─ W12 Triggers   ├─ Integración
├─ APIs Faltantes ├─ Demo Scenarios ├─ E2E Tests      ├─ Polish
│                 │                 │                 │
▼                 ▼                 ▼                 ▼
20% ──────────── 50% ──────────── 80% ──────────── 100%
```

---

## Metodología TDD Estricta

### Ciclo Red-Green-Refactor

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CICLO TDD OBLIGATORIO                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│     ┌──────────┐                                                        │
│     │   RED    │  1. Escribir test que FALLA                           │
│     │  (Fail)  │     - Define el comportamiento esperado               │
│     └────┬─────┘     - NO escribir código de implementación aún        │
│          │                                                              │
│          ▼                                                              │
│     ┌──────────┐                                                        │
│     │  GREEN   │  2. Escribir código MÍNIMO para pasar                 │
│     │  (Pass)  │     - Solo lo necesario para que el test pase         │
│     └────┬─────┘     - No optimizar, no generalizar                    │
│          │                                                              │
│          ▼                                                              │
│     ┌──────────┐                                                        │
│     │ REFACTOR │  3. Mejorar código manteniendo tests verdes           │
│     │ (Clean)  │     - Eliminar duplicación                            │
│     └────┬─────┘     - Mejorar nombres, estructura                     │
│          │                                                              │
│          └──────────► Siguiente test                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Reglas TDD Inquebrantables

1. **NUNCA** escribir código de producción sin un test que falle primero
2. **NUNCA** escribir más de un test que falle a la vez
3. **NUNCA** escribir más código del necesario para pasar el test
4. **SIEMPRE** ejecutar todos los tests después de cada cambio
5. **SIEMPRE** refactorizar después de que el test pase

### Estructura de Tests

```python
# Patrón AAA (Arrange-Act-Assert)
def test_nombre_descriptivo_del_comportamiento():
    # Arrange - Preparar datos y dependencias
    sut = SystemUnderTest()
    input_data = create_test_data()

    # Act - Ejecutar la acción
    result = sut.method_under_test(input_data)

    # Assert - Verificar resultado
    assert result.status == "expected"
    assert result.value == expected_value
```

---

## Sprint 1: APIs Faltantes + MCP Backend (Semana 1)

### 1.1 SOAR Endpoints (Día 1-2)

#### Tests TDD (escribir PRIMERO)

```python
# backend/tests/test_soar.py

import pytest
from httpx import AsyncClient

# TEST 1: Ejecutar playbook de contención
@pytest.mark.asyncio
async def test_run_playbook_contain_executes_action(client: AsyncClient):
    """
    GIVEN un dispositivo válido y un playbook de contención
    WHEN se ejecuta POST /soar/actions con action=contain
    THEN debe retornar action_id y status=success
    """
    # Arrange
    payload = {
        "action": "contain",
        "device_id": "DEV-001",
        "reason": "Malware detected"
    }

    # Act
    response = await client.post("/soar/actions", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "action_id" in data
    assert data["status"] == "success"
    assert data["action"] == "contain"


# TEST 2: Ejecutar playbook de kill process
@pytest.mark.asyncio
async def test_run_playbook_kill_process_terminates_process(client: AsyncClient):
    """
    GIVEN un proceso malicioso identificado
    WHEN se ejecuta POST /soar/actions con action=kill_process
    THEN debe terminar el proceso y retornar success
    """
    payload = {
        "action": "kill_process",
        "device_id": "DEV-001",
        "process_id": 12345,
        "reason": "Suspicious behavior"
    }

    response = await client.post("/soar/actions", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["process_terminated"] == True


# TEST 3: Playbook crea log de acción
@pytest.mark.asyncio
async def test_playbook_creates_action_log(client: AsyncClient):
    """
    GIVEN una acción ejecutada exitosamente
    WHEN se consulta el log de acciones
    THEN debe existir un registro de la acción
    """
    # Arrange - ejecutar acción primero
    payload = {"action": "contain", "device_id": "DEV-002", "reason": "Test"}
    action_response = await client.post("/soar/actions", json=payload)
    action_id = action_response.json()["action_id"]

    # Act
    log_response = await client.get(f"/soar/actions/{action_id}")

    # Assert
    assert log_response.status_code == 200
    log = log_response.json()
    assert log["action_id"] == action_id
    assert "timestamp" in log
    assert log["actor"] == "system"


# TEST 4: Listar acciones por dispositivo
@pytest.mark.asyncio
async def test_list_actions_by_device(client: AsyncClient):
    """
    GIVEN múltiples acciones en un dispositivo
    WHEN se consulta GET /soar/actions?device_id=X
    THEN debe retornar todas las acciones de ese dispositivo
    """
    response = await client.get("/soar/actions?device_id=DEV-001")

    assert response.status_code == 200
    data = response.json()
    assert "actions" in data
    assert all(a["device_id"] == "DEV-001" for a in data["actions"])


# TEST 5: Playbook con dispositivo inválido
@pytest.mark.asyncio
async def test_playbook_invalid_device_returns_404(client: AsyncClient):
    """
    GIVEN un device_id que no existe
    WHEN se intenta ejecutar una acción
    THEN debe retornar 404
    """
    payload = {"action": "contain", "device_id": "INVALID", "reason": "Test"}

    response = await client.post("/soar/actions", json=payload)

    assert response.status_code == 404


# TEST 6: Playbook con acción inválida
@pytest.mark.asyncio
async def test_playbook_invalid_action_returns_400(client: AsyncClient):
    """
    GIVEN una acción no soportada
    WHEN se intenta ejecutar
    THEN debe retornar 400 Bad Request
    """
    payload = {"action": "invalid_action", "device_id": "DEV-001", "reason": "Test"}

    response = await client.post("/soar/actions", json=payload)

    assert response.status_code == 400
```

#### Implementación (escribir DESPUÉS de tests)

```
backend/src/api/soar.py
├── POST /soar/actions          → run_playbook()
├── GET /soar/actions/{id}      → get_action()
└── GET /soar/actions           → list_actions()

backend/src/services/soar_service.py
├── execute_contain()
├── execute_kill_process()
├── create_action_log()
└── get_action_log()
```

#### Checklist TDD SOAR

- [ ] 🔴 `test_run_playbook_contain` → escribir test
- [ ] 🟢 `test_run_playbook_contain` → implementar hasta pasar
- [ ] 🔵 Refactorizar
- [ ] 🔴 `test_run_playbook_kill_process` → escribir test
- [ ] 🟢 `test_run_playbook_kill_process` → implementar hasta pasar
- [ ] 🔵 Refactorizar
- [ ] 🔴 `test_playbook_creates_action_log` → escribir test
- [ ] 🟢 `test_playbook_creates_action_log` → implementar hasta pasar
- [ ] 🔵 Refactorizar
- [ ] 🔴 `test_list_actions_by_device` → escribir test
- [ ] 🟢 `test_list_actions_by_device` → implementar hasta pasar
- [ ] 🔵 Refactorizar
- [ ] 🔴 `test_playbook_invalid_device_returns_404` → escribir test
- [ ] 🟢 `test_playbook_invalid_device_returns_404` → implementar hasta pasar
- [ ] 🔴 `test_playbook_invalid_action_returns_400` → escribir test
- [ ] 🟢 `test_playbook_invalid_action_returns_400` → implementar hasta pasar

---

### 1.2 Graph Endpoints (Día 2-3)

#### Tests TDD

```python
# backend/tests/test_graph.py

import pytest
from httpx import AsyncClient

# TEST 1: Obtener grafo de incidente
@pytest.mark.asyncio
async def test_get_graph_incident_returns_nodes_and_edges(client: AsyncClient):
    """
    GIVEN un incidente con detecciones y activos asociados
    WHEN se solicita GET /graph/incident/{id}
    THEN debe retornar nodos y edges en formato Cytoscape
    """
    response = await client.get("/graph/incident/INC-ANCHOR-001")

    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) > 0
    assert len(data["edges"]) > 0


# TEST 2: Formato de nodos
@pytest.mark.asyncio
async def test_graph_nodes_have_cytoscape_format(client: AsyncClient):
    """
    GIVEN un grafo de incidente
    WHEN se obtienen los nodos
    THEN cada nodo debe tener id, label, type, y data
    """
    response = await client.get("/graph/incident/INC-ANCHOR-001")
    data = response.json()

    for node in data["nodes"]:
        assert "data" in node
        assert "id" in node["data"]
        assert "label" in node["data"]
        assert "type" in node["data"]
        assert node["data"]["type"] in ["incident", "detection", "asset", "process", "hash"]


# TEST 3: Formato de edges
@pytest.mark.asyncio
async def test_graph_edges_have_cytoscape_format(client: AsyncClient):
    """
    GIVEN un grafo de incidente
    WHEN se obtienen los edges
    THEN cada edge debe tener source, target, y relation
    """
    response = await client.get("/graph/incident/INC-ANCHOR-001")
    data = response.json()

    for edge in data["edges"]:
        assert "data" in edge
        assert "source" in edge["data"]
        assert "target" in edge["data"]
        assert "relation" in edge["data"]


# TEST 4: Colores de nodos según estado
@pytest.mark.asyncio
async def test_graph_nodes_have_correct_colors(client: AsyncClient):
    """
    GIVEN un grafo con activos en diferentes estados
    WHEN se obtienen los nodos
    THEN los colores deben reflejar el estado:
         - Green: sin riesgo
         - Yellow: riesgo medio
         - Red: riesgo alto
         - Blue: contenido
    """
    response = await client.get("/graph/incident/INC-ANCHOR-001")
    data = response.json()

    asset_nodes = [n for n in data["nodes"] if n["data"]["type"] == "asset"]

    for node in asset_nodes:
        assert "color" in node["data"]
        assert node["data"]["color"] in ["green", "yellow", "red", "blue"]


# TEST 5: Grafo de incidente inexistente
@pytest.mark.asyncio
async def test_graph_incident_not_found_returns_404(client: AsyncClient):
    """
    GIVEN un incidente que no existe
    WHEN se solicita su grafo
    THEN debe retornar 404
    """
    response = await client.get("/graph/incident/INVALID")

    assert response.status_code == 404


# TEST 6: Grafo de sistema completo
@pytest.mark.asyncio
async def test_get_graph_system_returns_overview(client: AsyncClient):
    """
    GIVEN el sistema con múltiples incidentes
    WHEN se solicita GET /graph/system
    THEN debe retornar un grafo con fuentes, incidentes y activos
    """
    response = await client.get("/graph/system")

    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data

    types = set(n["data"]["type"] for n in data["nodes"])
    assert "source" in types or len(data["nodes"]) > 0
```

#### Implementación

```
backend/src/api/graph.py
├── GET /graph/incident/{id}    → get_incident_graph()
└── GET /graph/system           → get_system_graph()

backend/src/services/graph_service.py
├── build_incident_graph()
├── build_system_graph()
├── node_to_cytoscape()
└── edge_to_cytoscape()
```

#### Checklist TDD Graph

- [ ] 🔴 `test_get_graph_incident` → escribir test
- [ ] 🟢 `test_get_graph_incident` → implementar
- [ ] 🔵 Refactorizar
- [ ] 🔴 `test_graph_nodes_format` → escribir test
- [ ] 🟢 `test_graph_nodes_format` → implementar
- [ ] 🔵 Refactorizar
- [ ] 🔴 `test_graph_edges_format` → escribir test
- [ ] 🟢 `test_graph_edges_format` → implementar
- [ ] 🔵 Refactorizar
- [ ] 🔴 `test_graph_node_colors` → escribir test
- [ ] 🟢 `test_graph_node_colors` → implementar
- [ ] 🔴 `test_graph_not_found` → escribir test
- [ ] 🟢 `test_graph_not_found` → implementar
- [ ] 🔴 `test_get_graph_system` → escribir test
- [ ] 🟢 `test_get_graph_system` → implementar

---

### 1.3 MCP Backend Server (Día 3-5)

#### Arquitectura MCP

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MCP BACKEND SERVER (Puerto 8001)                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  FastAPI App                                                            │
│  ├── /mcp/sse          → Server-Sent Events endpoint                   │
│  └── /mcp/messages     → JSON-RPC messages                             │
│                                                                         │
│  MCP Tools (19)                                                         │
│  ├── SIEM (5)                                                          │
│  │   ├── siem_list_incidents                                           │
│  │   ├── siem_get_incident                                             │
│  │   ├── siem_get_entities                                             │
│  │   ├── siem_add_comment                                              │
│  │   └── siem_close_incident                                           │
│  │                                                                      │
│  ├── EDR (6)                                                           │
│  │   ├── edr_list_detections                                           │
│  │   ├── edr_get_detection                                             │
│  │   ├── edr_get_process_tree                                          │
│  │   ├── edr_hunt_hash                                                 │
│  │   ├── edr_contain_host                                              │
│  │   └── edr_lift_containment                                          │
│  │                                                                      │
│  ├── Intel (1): intel_get_indicator                                    │
│  ├── CTEM (1): ctem_get_asset_risk                                     │
│  ├── Approvals (2): approvals_get, approvals_request                   │
│  ├── Tickets (2): tickets_create, tickets_list                         │
│  └── Reports (2): reports_generate_postmortem, reports_get_postmortem  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Tests TDD MCP Server

```python
# backend/tests/test_mcp_server.py

import pytest
from httpx import AsyncClient
import json

# TEST 1: MCP Server inicia
@pytest.mark.asyncio
async def test_mcp_server_starts_and_responds(client: AsyncClient):
    """
    GIVEN el servidor MCP configurado
    WHEN se conecta al endpoint SSE
    THEN debe establecer conexión y responder
    """
    async with client.stream("GET", "/mcp/sse") as response:
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"


# TEST 2: Listar herramientas disponibles
@pytest.mark.asyncio
async def test_mcp_lists_available_tools(client: AsyncClient):
    """
    GIVEN una conexión MCP establecida
    WHEN se envía tools/list
    THEN debe retornar las 19 herramientas
    """
    message = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }

    response = await client.post("/mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "tools" in data["result"]
    assert len(data["result"]["tools"]) == 19


# TEST 3: Ejecutar tool SIEM list_incidents
@pytest.mark.asyncio
async def test_mcp_siem_list_incidents_tool(client: AsyncClient):
    """
    GIVEN el tool siem_list_incidents
    WHEN se invoca sin parámetros
    THEN debe retornar lista de incidentes
    """
    message = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "siem_list_incidents",
            "arguments": {}
        }
    }

    response = await client.post("/mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "content" in data["result"]


# TEST 4: Ejecutar tool con filtros
@pytest.mark.asyncio
async def test_mcp_siem_list_incidents_with_filters(client: AsyncClient):
    """
    GIVEN el tool siem_list_incidents
    WHEN se invoca con filtros de severidad
    THEN debe retornar solo incidentes críticos
    """
    message = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "siem_list_incidents",
            "arguments": {"severity": "critical"}
        }
    }

    response = await client.post("/mcp/messages", json=message)

    data = response.json()
    content = json.loads(data["result"]["content"][0]["text"])
    assert all(i["severity"] == "critical" for i in content["data"])


# TEST 5: Tool EDR contain_host
@pytest.mark.asyncio
async def test_mcp_edr_contain_host_tool(client: AsyncClient):
    """
    GIVEN un dispositivo válido
    WHEN se invoca edr_contain_host
    THEN debe ejecutar contención y retornar resultado
    """
    message = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "edr_contain_host",
            "arguments": {
                "device_id": "DEV-001",
                "reason": "Malware detected"
            }
        }
    }

    response = await client.post("/mcp/messages", json=message)

    data = response.json()
    assert "result" in data
    content = json.loads(data["result"]["content"][0]["text"])
    assert content["status"] == "success"


# TEST 6: Tool con parámetros inválidos
@pytest.mark.asyncio
async def test_mcp_tool_invalid_params_returns_error(client: AsyncClient):
    """
    GIVEN un tool que requiere parámetros
    WHEN se invoca sin parámetros requeridos
    THEN debe retornar error
    """
    message = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "siem_get_incident",
            "arguments": {}  # Falta incident_id
        }
    }

    response = await client.post("/mcp/messages", json=message)

    data = response.json()
    assert "error" in data


# TEST 7: Tool inexistente
@pytest.mark.asyncio
async def test_mcp_unknown_tool_returns_error(client: AsyncClient):
    """
    GIVEN un nombre de tool que no existe
    WHEN se intenta invocar
    THEN debe retornar error
    """
    message = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "unknown_tool",
            "arguments": {}
        }
    }

    response = await client.post("/mcp/messages", json=message)

    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == -32601  # Method not found
```

#### Tests por cada Tool (20 tests adicionales)

```python
# backend/tests/test_mcp_tools.py

# SIEM Tools
- test_mcp_siem_get_incident_tool
- test_mcp_siem_get_entities_tool
- test_mcp_siem_add_comment_tool
- test_mcp_siem_close_incident_tool

# EDR Tools
- test_mcp_edr_list_detections_tool
- test_mcp_edr_get_detection_tool
- test_mcp_edr_get_process_tree_tool
- test_mcp_edr_hunt_hash_tool
- test_mcp_edr_lift_containment_tool

# Intel Tools
- test_mcp_intel_get_indicator_tool

# CTEM Tools
- test_mcp_ctem_get_asset_risk_tool

# Approvals Tools
- test_mcp_approvals_get_tool
- test_mcp_approvals_request_tool

# Tickets Tools
- test_mcp_tickets_create_tool
- test_mcp_tickets_list_tool

# Reports Tools
- test_mcp_reports_generate_postmortem_tool
- test_mcp_reports_get_postmortem_tool
```

#### Implementación MCP Backend

```
backend/src/mcp/
├── __init__.py
├── server.py                   # FastMCP server setup
├── router.py                   # FastAPI router for /mcp/*
├── protocol.py                 # JSON-RPC protocol handling
│
├── tools/
│   ├── __init__.py
│   ├── base.py                 # Tool base class
│   ├── siem.py                 # 5 SIEM tools
│   ├── edr.py                  # 6 EDR tools
│   ├── intel.py                # 1 Intel tool
│   ├── ctem.py                 # 1 CTEM tool
│   ├── approvals.py            # 2 Approval tools
│   ├── tickets.py              # 2 Ticket tools
│   └── reports.py              # 2 Report tools
│
└── schemas/
    ├── __init__.py
    └── tool_schemas.py         # JSON Schema for tools
```

#### Checklist TDD MCP Backend

**Server Base:**

- [ ] 🔴 `test_mcp_server_starts` → test
- [ ] 🟢 Implementar server base
- [ ] 🔴 `test_mcp_lists_tools` → test
- [ ] 🟢 Implementar tool registry
- [ ] 🔴 `test_mcp_tool_invalid_params` → test
- [ ] 🟢 Implementar validación
- [ ] 🔴 `test_mcp_unknown_tool` → test
- [ ] 🟢 Implementar error handling

**SIEM Tools (5):**

- [ ] 🔴 `test_mcp_siem_list_incidents` → test
- [ ] 🟢 Implementar
- [ ] 🔴 `test_mcp_siem_get_incident` → test
- [ ] 🟢 Implementar
- [ ] 🔴 `test_mcp_siem_get_entities` → test
- [ ] 🟢 Implementar
- [ ] 🔴 `test_mcp_siem_add_comment` → test
- [ ] 🟢 Implementar
- [ ] 🔴 `test_mcp_siem_close_incident` → test
- [ ] 🟢 Implementar

**EDR Tools (6):**

- [ ] 🔴 `test_mcp_edr_list_detections` → test
- [ ] 🟢 Implementar
- [ ] 🔴 `test_mcp_edr_get_detection` → test
- [ ] 🟢 Implementar
- [ ] 🔴 `test_mcp_edr_get_process_tree` → test
- [ ] 🟢 Implementar
- [ ] 🔴 `test_mcp_edr_hunt_hash` → test
- [ ] 🟢 Implementar
- [ ] 🔴 `test_mcp_edr_contain_host` → test
- [ ] 🟢 Implementar
- [ ] 🔴 `test_mcp_edr_lift_containment` → test
- [ ] 🟢 Implementar

**Otros Tools (6):**

- [ ] 🔴 `test_mcp_intel_get_indicator` → test
- [ ] 🟢 Implementar
- [ ] 🔴 `test_mcp_ctem_get_asset_risk` → test
- [ ] 🟢 Implementar
- [ ] 🔴 `test_mcp_approvals_get` → test
- [ ] 🟢 Implementar
- [ ] 🔴 `test_mcp_approvals_request` → test
- [ ] 🟢 Implementar
- [ ] 🔴 `test_mcp_tickets_create` → test
- [ ] 🟢 Implementar
- [ ] 🔴 `test_mcp_tickets_list` → test
- [ ] 🟢 Implementar
- [ ] 🔴 `test_mcp_reports_generate` → test
- [ ] 🟢 Implementar
- [ ] 🔴 `test_mcp_reports_get` → test
- [ ] 🟢 Implementar

---

## Sprint 2: W8 Grafos + MCP Frontend/Data (Semana 2)

### 2.1 W8: Frontend Grafos con Cytoscape.js (Día 1-3)

#### Tests TDD (Playwright + React Testing Library)

```typescript
// frontend/tests/graph.spec.ts

import { test, expect } from "@playwright/test";

// TEST 1: Grafo se renderiza
test("graph component renders with nodes", async ({ page }) => {
  // Arrange
  await page.goto("/incidents/INC-ANCHOR-001");

  // Act
  await page.click('[data-testid="view-graph-btn"]');

  // Assert
  const graphContainer = page.locator('[data-testid="cytoscape-graph"]');
  await expect(graphContainer).toBeVisible();

  // Verificar que hay nodos
  const nodes = await page.evaluate(() => {
    // @ts-ignore
    return window.cy.nodes().length;
  });
  expect(nodes).toBeGreaterThan(0);
});

// TEST 2: Nodos son clickeables
test("graph nodes are clickable and open panel", async ({ page }) => {
  await page.goto("/incidents/INC-ANCHOR-001");
  await page.click('[data-testid="view-graph-btn"]');

  // Click en un nodo de asset
  await page.evaluate(() => {
    const assetNode = window.cy.nodes('[type="asset"]').first();
    assetNode.emit("tap");
  });

  // Panel de detalle debe abrirse
  const panel = page.locator('[data-testid="node-detail-panel"]');
  await expect(panel).toBeVisible();
});

// TEST 3: Panel muestra información correcta
test("node panel shows correct sections", async ({ page }) => {
  await page.goto("/incidents/INC-ANCHOR-001");
  await page.click('[data-testid="view-graph-btn"]');

  // Click en nodo
  await page.evaluate(() => {
    window.cy.nodes().first().emit("tap");
  });

  // Verificar 4 secciones
  await expect(page.locator('[data-testid="section-asset-info"]')).toBeVisible();
  await expect(page.locator('[data-testid="section-threat"]')).toBeVisible();
  await expect(page.locator('[data-testid="section-recommendation"]')).toBeVisible();
  await expect(page.locator('[data-testid="section-status"]')).toBeVisible();
});

// TEST 4: Colores de nodos correctos
test("graph nodes have correct colors based on risk", async ({ page }) => {
  await page.goto("/incidents/INC-ANCHOR-001");
  await page.click('[data-testid="view-graph-btn"]');

  const colors = await page.evaluate(() => {
    return window.cy.nodes('[type="asset"]').map((n) => ({
      id: n.id(),
      color: n.style("background-color"),
    }));
  });

  // Verificar que hay colores válidos
  for (const node of colors) {
    expect(
      ["green", "yellow", "red", "blue"].some(
        (c) => node.color.includes(c) || node.color.match(/#[0-9a-f]{6}/i),
      ),
    ).toBeTruthy();
  }
});

// TEST 5: Zoom y pan funcionan
test("graph supports zoom and pan", async ({ page }) => {
  await page.goto("/incidents/INC-ANCHOR-001");
  await page.click('[data-testid="view-graph-btn"]');

  const initialZoom = await page.evaluate(() => window.cy.zoom());

  // Zoom in
  await page.click('[data-testid="zoom-in-btn"]');

  const newZoom = await page.evaluate(() => window.cy.zoom());
  expect(newZoom).toBeGreaterThan(initialZoom);
});

// TEST 6: Layout automático
test("graph has automatic layout", async ({ page }) => {
  await page.goto("/incidents/INC-ANCHOR-001");
  await page.click('[data-testid="view-graph-btn"]');

  // Ejecutar layout
  await page.click('[data-testid="auto-layout-btn"]');

  // Verificar que los nodos no están todos en la misma posición
  const positions = await page.evaluate(() => {
    return window.cy.nodes().map((n) => n.position());
  });

  const uniquePositions = new Set(positions.map((p) => `${p.x},${p.y}`));
  expect(uniquePositions.size).toBeGreaterThan(1);
});
```

#### Implementación Frontend Grafos

```
frontend/src/
├── components/
│   ├── Graph/
│   │   ├── index.tsx              # Export principal
│   │   ├── CytoscapeGraph.tsx     # Componente Cytoscape
│   │   ├── GraphControls.tsx      # Zoom, layout buttons
│   │   ├── NodeDetailPanel.tsx    # Panel lateral
│   │   ├── useGraphData.ts        # Hook para datos
│   │   ├── styles.ts              # Estilos Cytoscape
│   │   └── types.ts               # TypeScript types
│   │
│   └── NodePanel/
│       ├── AssetInfoSection.tsx   # (a) Quién es el activo
│       ├── ThreatSection.tsx      # (b) Cuál es la amenaza
│       ├── RecommendationSection.tsx # (c) Qué recomienda
│       └── StatusSection.tsx      # (d) Estado contención/ticket
│
├── pages/
│   └── GraphPage.tsx              # Página de grafo
│
└── services/
    └── graphApi.ts                # API calls para grafos
```

#### Checklist TDD W8 Grafos

- [ ] 🔴 `test_graph_renders` → escribir test
- [ ] 🟢 Implementar CytoscapeGraph base
- [ ] 🔵 Refactorizar
- [ ] 🔴 `test_nodes_clickable` → escribir test
- [ ] 🟢 Implementar click handlers
- [ ] 🔵 Refactorizar
- [ ] 🔴 `test_panel_sections` → escribir test
- [ ] 🟢 Implementar NodeDetailPanel
- [ ] 🔵 Refactorizar
- [ ] 🔴 `test_node_colors` → escribir test
- [ ] 🟢 Implementar color mapping
- [ ] 🔵 Refactorizar
- [ ] 🔴 `test_zoom_pan` → escribir test
- [ ] 🟢 Implementar GraphControls
- [ ] 🔵 Refactorizar
- [ ] 🔴 `test_auto_layout` → escribir test
- [ ] 🟢 Implementar layout options
- [ ] 🔵 Refactorizar

---

### 2.2 MCP Frontend Server (Día 3-4)

#### Tests TDD

```typescript
// frontend/tests/mcp-server.spec.ts

import { test, expect } from "@playwright/test";

// TEST 1: MCP WebSocket se conecta
test("mcp websocket connects successfully", async ({ page }) => {
  await page.goto("/");

  // Verificar conexión WebSocket
  const wsConnected = await page.evaluate(() => {
    return new Promise((resolve) => {
      const ws = new WebSocket("ws://localhost:3001/mcp");
      ws.onopen = () => resolve(true);
      ws.onerror = () => resolve(false);
    });
  });

  expect(wsConnected).toBe(true);
});

// TEST 2: Tool show_simulation actualiza UI
test("show_simulation tool updates dashboard", async ({ page }) => {
  await page.goto("/dashboard");

  // Simular llamada MCP
  await page.evaluate(() => {
    window.mcpHandler.handleTool("show_simulation", {
      incident_id: "INC-001",
      phase: "investigation",
    });
  });

  // Verificar que la simulación se muestra
  const simulation = page.locator('[data-testid="simulation-overlay"]');
  await expect(simulation).toBeVisible();
});

// TEST 3: Tool generate_chart crea gráfico
test("generate_chart tool creates chart", async ({ page }) => {
  await page.goto("/dashboard");

  const initialCharts = await page.locator(".chart-container").count();

  await page.evaluate(() => {
    window.mcpHandler.handleTool("generate_chart", {
      type: "bar",
      data: { labels: ["A", "B"], values: [10, 20] },
      title: "Test Chart",
    });
  });

  const newCharts = await page.locator(".chart-container").count();
  expect(newCharts).toBe(initialCharts + 1);
});

// TEST 4: Tool highlight_asset resalta activo
test("highlight_asset tool highlights asset in graph", async ({ page }) => {
  await page.goto("/graph/system");

  await page.evaluate(() => {
    window.mcpHandler.handleTool("highlight_asset", {
      asset_id: "ASSET-001",
    });
  });

  // Verificar que el nodo está resaltado
  const isHighlighted = await page.evaluate(() => {
    const node = window.cy.$("#ASSET-001");
    return node.hasClass("highlighted");
  });

  expect(isHighlighted).toBe(true);
});
```

#### Implementación MCP Frontend

```
frontend/src/mcp/
├── server.ts                   # MCP WebSocket server
├── handler.ts                  # Tool handler registry
├── types.ts                    # TypeScript types
│
├── tools/
│   ├── index.ts
│   ├── simulation.ts           # show_simulation
│   ├── charts.ts               # generate_chart
│   ├── demo.ts                 # run_demo_scenario, get_demo_state
│   ├── dashboard.ts            # update_dashboard
│   ├── timeline.ts             # show_alert_timeline
│   ├── assets.ts               # highlight_asset
│   └── postmortem.ts           # show_postmortem
│
└── context/
    └── MCPContext.tsx          # React context for MCP state
```

---

### 2.3 MCP Data Server (Día 4-5)

#### Tests TDD

```python
# backend/tests/test_mcp_data.py

# TEST 1: Data MCP server inicia
@pytest.mark.asyncio
async def test_data_mcp_server_starts(client: AsyncClient):
    """Data MCP server debe iniciar correctamente"""
    response = await client.get("/data-mcp/health")
    assert response.status_code == 200


# TEST 2: Tool generate_assets
@pytest.mark.asyncio
async def test_data_mcp_generate_assets_tool(client: AsyncClient):
    """generate_assets debe crear activos sintéticos"""
    message = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "generate_assets",
            "arguments": {"count": 10, "seed": 42}
        }
    }

    response = await client.post("/data-mcp/messages", json=message)

    data = response.json()
    assert "result" in data
    content = json.loads(data["result"]["content"][0]["text"])
    assert content["generated"] == 10


# TEST 3: Tool generate_all
@pytest.mark.asyncio
async def test_data_mcp_generate_all_tool(client: AsyncClient):
    """generate_all debe generar todos los datos"""
    message = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "generate_all",
            "arguments": {"seed": 42}
        }
    }

    response = await client.post("/data-mcp/messages", json=message)

    data = response.json()
    content = json.loads(data["result"]["content"][0]["text"])
    assert "assets" in content
    assert "detections" in content
    assert "incidents" in content


# TEST 4: Tool reset
@pytest.mark.asyncio
async def test_data_mcp_reset_tool(client: AsyncClient):
    """reset debe limpiar todos los datos"""
    message = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "reset",
            "arguments": {}
        }
    }

    response = await client.post("/data-mcp/messages", json=message)

    data = response.json()
    content = json.loads(data["result"]["content"][0]["text"])
    assert content["status"] == "reset_complete"
```

---

## Sprint 3: W12 Auto-Triggers (Semana 3)

### 3.1 Gateway Client Base (Día 1)

#### Tests TDD

```python
# backend/tests/triggers/test_gateway_client.py

import pytest
from unittest.mock import AsyncMock, patch
from src.triggers.gateway_client import GatewayClient

# TEST 1: Envía mensaje correctamente
@pytest.mark.asyncio
async def test_gateway_client_sends_message():
    """El cliente debe enviar mensaje al gateway"""
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.json.return_value = {"response_id": "resp-001"}
        mock_post.return_value.status_code = 200

        client = GatewayClient("http://localhost:18789")
        result = await client.send_command("/investigate INC-001")

        assert result == "resp-001"
        mock_post.assert_called_once()


# TEST 2: Respeta cooldown
@pytest.mark.asyncio
async def test_gateway_client_respects_cooldown():
    """No debe enviar si está en cooldown"""
    client = GatewayClient("http://localhost:18789")

    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.json.return_value = {"response_id": "resp-001"}
        mock_post.return_value.status_code = 200

        # Primera llamada
        await client.send_command("/investigate INC-001", cooldown_key="INC-001")

        # Segunda llamada (en cooldown)
        result = await client.send_command("/investigate INC-001", cooldown_key="INC-001")

        assert result is None
        assert mock_post.call_count == 1  # Solo una llamada


# TEST 3: Deduplica mensajes
@pytest.mark.asyncio
async def test_gateway_client_deduplicates():
    """No debe enviar mensajes duplicados"""
    client = GatewayClient("http://localhost:18789")

    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.json.return_value = {"response_id": "resp-001"}

        await client.send_command("/investigate INC-001", dedup_key="INC-001")
        await client.send_command("/investigate INC-001", dedup_key="INC-001")

        assert mock_post.call_count == 1


# TEST 4: Maneja errores gracefully
@pytest.mark.asyncio
async def test_gateway_client_handles_errors():
    """Debe manejar errores sin crashear"""
    client = GatewayClient("http://localhost:18789")

    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.side_effect = Exception("Connection refused")

        result = await client.send_command("/investigate INC-001")

        assert result is None  # No crash, retorna None
```

### 3.2 Trigger Handlers (Día 2-4)

#### Tests TDD por Categoría

```python
# backend/tests/triggers/test_siem_triggers.py

# TEST: incident.created trigger
@pytest.mark.asyncio
async def test_trigger_incident_created_sends_investigate():
    """Nuevo incidente crítico debe triggerear /investigate"""
    handler = IncidentCreatedHandler(gateway_client)

    incident = Incident(
        incident_id="INC-001",
        severity="critical",
        status="new",
        title="Malware detected"
    )

    with patch.object(gateway_client, 'send_command') as mock:
        await handler.handle(incident)

        mock.assert_called_once_with(
            "/investigate INC-001",
            cooldown_key="INC-001",
            metadata={"trigger": "incident.created", "severity": "critical"}
        )


# TEST: incident.created ignora low severity
@pytest.mark.asyncio
async def test_trigger_incident_created_ignores_low_severity():
    """Incidentes low/medium no deben triggerear"""
    handler = IncidentCreatedHandler(gateway_client)

    incident = Incident(
        incident_id="INC-002",
        severity="low",
        status="new"
    )

    with patch.object(gateway_client, 'send_command') as mock:
        await handler.handle(incident)

        mock.assert_not_called()


# backend/tests/triggers/test_edr_triggers.py

# TEST: detection.propagation trigger
@pytest.mark.asyncio
async def test_trigger_detection_propagation():
    """Hash en múltiples hosts debe triggerear /hunt"""
    handler = DetectionPropagationHandler(gateway_client)

    hunt_result = HuntResult(
        sha256="abc123",
        total_hosts_found=5,
        hosts=["HOST-1", "HOST-2", "HOST-3", "HOST-4", "HOST-5"]
    )

    with patch.object(gateway_client, 'send_command') as mock:
        await handler.handle(hunt_result)

        mock.assert_called_once()
        call_args = mock.call_args[0][0]
        assert "/hunt abc123" in call_args


# TEST: containment.failed trigger
@pytest.mark.asyncio
async def test_trigger_containment_failed_retries():
    """Fallo de contención debe triggerear reintento"""
    handler = ContainmentFailedHandler(gateway_client)

    result = ContainmentResult(
        device_id="DEV-001",
        status="failed",
        reason="Agent unreachable"
    )

    with patch.object(gateway_client, 'send_command') as mock:
        await handler.handle(result)

        mock.assert_called_once()
        assert "/retry-containment DEV-001" in mock.call_args[0][0]


# backend/tests/triggers/test_approval_triggers.py

# TEST: approval.approved trigger
@pytest.mark.asyncio
async def test_trigger_approval_approved_executes():
    """Aprobación debe triggerear ejecución"""
    handler = ApprovalApprovedHandler(gateway_client)

    approval = ApprovalStatus(
        incident_id="INC-001",
        status="approved",
        decided_by="admin@company.com"
    )

    with patch.object(gateway_client, 'send_command') as mock:
        await handler.handle(approval)

        mock.assert_called_once()
        assert "/execute-containment INC-001" in mock.call_args[0][0]


# TEST: approval.timeout trigger
@pytest.mark.asyncio
async def test_trigger_approval_timeout_escalates():
    """Timeout debe triggerear escalación"""
    handler = ApprovalTimeoutHandler(gateway_client)

    with patch.object(gateway_client, 'send_command') as mock:
        await handler.check_timeouts()

        # Si hay timeouts, debe escalar
        if mock.called:
            assert "/escalate-approval" in mock.call_args[0][0]
```

### 3.3 Scheduler e Integración (Día 5)

#### Tests TDD

```python
# backend/tests/triggers/test_scheduler.py

@pytest.mark.asyncio
async def test_scheduler_runs_periodic_checks():
    """Scheduler debe ejecutar checks periódicos"""
    scheduler = TriggerScheduler()

    with patch.object(scheduler, 'check_sla_breaches') as mock:
        await scheduler.start()
        await asyncio.sleep(0.1)

        assert mock.called


# backend/tests/triggers/test_integration.py

@pytest.mark.asyncio
async def test_full_trigger_flow_incident_to_investigate():
    """Flujo completo: nuevo incidente → /investigate"""
    # Arrange
    trigger_system = TriggerSystem(gateway_client)

    # Act - Simular nuevo incidente
    incident = create_test_incident(severity="critical")
    await trigger_system.emit("incident.created", incident)

    # Assert - Verificar que se envió comando
    # (verificar en gateway mock o logs)
```

---

## Sprint 4: Demo Scenarios E2E + Integración (Semana 4)

### 4.1 Demo Scenarios E2E (Día 1-2)

#### Tests TDD Escenarios

```python
# tests/e2e/test_scenario_auto_containment.py

@pytest.mark.e2e
async def test_scenario_1_auto_containment_full_flow():
    """
    Escenario 1: Auto-Containment

    GIVEN: Incidente INC-ANCHOR-001 con:
           - Severidad crítica
           - Intel malicioso
           - Propagación detectada
           - Asset NO VIP

    WHEN: Se ejecuta /investigate INC-ANCHOR-001

    THEN:
           - Confidence score >= 90
           - Policy = auto-contain
           - Host contenido
           - Ticket creado
           - Postmortem generado
    """
    # Arrange
    client = CyberDemoApiClient("http://localhost:8000")

    # Verificar precondiciones
    incident = await client.siem.getIncident("INC-ANCHOR-001")
    assert incident.severity == "critical"

    # Act - Ejecutar investigación
    result = await investigation_service.investigate("INC-ANCHOR-001")

    # Assert
    assert result.confidence_score >= 90
    assert result.decision.action == "contain"
    assert result.containment_executed == True

    # Verificar ticket
    tickets = await client.tickets.list()
    assert any(t.incident_id == "INC-ANCHOR-001" for t in tickets)

    # Verificar postmortem
    postmortem = await client.reports.getPostmortem("INC-ANCHOR-001")
    assert postmortem is not None


# tests/e2e/test_scenario_vip_approval.py

@pytest.mark.e2e
async def test_scenario_2_vip_requires_approval():
    """
    Escenario 2: VIP Human-in-the-Loop

    GIVEN: Incidente INC-ANCHOR-002 con:
           - Asset VIP
           - Intel malicioso

    WHEN: Se ejecuta /investigate

    THEN:
           - Policy = request_approval
           - Approval card enviado
           - Contención espera aprobación
    """
    result = await investigation_service.investigate("INC-ANCHOR-002")

    assert result.decision.action == "request_approval"
    assert result.decision.requires_approval == True
    assert result.approval_requested == True
    assert result.containment_executed == False

    # Simular aprobación
    await client.approvals.approve("INC-ANCHOR-002", "admin@test.com")

    # Verificar contención post-aprobación
    result2 = await investigation_service.executeContainmentAfterApproval(
        "INC-ANCHOR-002",
        "DEV-VIP-001",
        ["vip", "executive"]
    )

    assert result2.status == "success"


# tests/e2e/test_scenario_false_positive.py

@pytest.mark.e2e
async def test_scenario_3_false_positive():
    """
    Escenario 3: False Positive

    GIVEN: Incidente INC-ANCHOR-003 con:
           - Intel benign
           - No propagación
           - Asset normal

    WHEN: Se ejecuta /investigate

    THEN:
           - Confidence score < 50
           - Policy = mark_false_positive
           - Sin contención
           - Incidente cerrado
    """
    result = await investigation_service.investigate("INC-ANCHOR-003")

    assert result.confidence_score < 50
    assert result.decision.action == "mark_false_positive"
    assert result.containment_executed == False

    # Verificar incidente cerrado
    incident = await client.siem.getIncident("INC-ANCHOR-003")
    assert incident.status == "closed" or "false_positive" in incident.tags
```

### 4.2 Integración Final (Día 3-4)

#### Tests de Integración Completa

```python
# tests/integration/test_full_system.py

@pytest.mark.integration
async def test_mcp_to_investigation_to_ui():
    """
    Test integración completa:
    MCP call → Investigation → UI update
    """
    # 1. Llamada MCP
    mcp_response = await mcp_client.call_tool(
        "siem_get_incident",
        {"incident_id": "INC-ANCHOR-001"}
    )
    assert mcp_response is not None

    # 2. Investigación
    result = await investigation_service.investigate("INC-ANCHOR-001")
    assert result.confidence_score > 0

    # 3. Verificar UI (via Playwright)
    # ... verificar que el dashboard muestra el incidente


@pytest.mark.integration
async def test_trigger_to_gateway_to_action():
    """
    Test integración:
    Trigger → Gateway → Claude → Action
    """
    # Simular nuevo incidente
    incident = await create_incident(severity="critical")

    # Esperar trigger
    await asyncio.sleep(1)

    # Verificar que se envió comando al gateway
    # (mock o verificar logs)
```

### 4.3 Polish y Documentación (Día 5)

- [ ] Revisar todos los tests pasan
- [ ] Documentar API
- [ ] Actualizar PROGRESS.md al 100%
- [ ] Preparar demo final

---

## Resumen de Tests TDD

### Por Categoría

| Categoría      | Tests Nuevos | Archivos                              |
| -------------- | ------------ | ------------------------------------- |
| SOAR API       | 6            | `test_soar.py`                        |
| Graph API      | 6            | `test_graph.py`                       |
| MCP Backend    | 27           | `test_mcp_*.py`                       |
| MCP Frontend   | 10           | `graph.spec.ts`, `mcp-server.spec.ts` |
| MCP Data       | 9            | `test_mcp_data.py`                    |
| Auto-Triggers  | 24           | `test_*_triggers.py`                  |
| Demo Scenarios | 9            | `test_scenario_*.py`                  |
| Integración    | 9            | `test_*_integration.py`               |
| **Total**      | **100**      |                                       |

### Por Sprint

| Sprint    | Días   | Tests   | Implementación             |
| --------- | ------ | ------- | -------------------------- |
| Sprint 1  | 5      | 33      | APIs + MCP Backend         |
| Sprint 2  | 5      | 25      | Grafos + MCP Frontend/Data |
| Sprint 3  | 5      | 24      | Auto-Triggers              |
| Sprint 4  | 5      | 18      | Demo + Integración         |
| **Total** | **20** | **100** |                            |

---

## Comandos de Ejecución

```bash
# Backend tests
cd CyberDemo/backend
pytest tests/ -v --cov=src --cov-report=html

# Frontend tests
cd CyberDemo/frontend
pnpm test

# E2E tests
cd CyberDemo
pnpm test:e2e

# All tests
pnpm test:all
```

---

## Log de Plan

| Fecha      | Cambio                           |
| ---------- | -------------------------------- |
| 2026-02-14 | Plan de construcción TDD creado  |
| 2026-02-14 | 100 tests definidos              |
| 2026-02-14 | 4 sprints planificados (20 días) |
