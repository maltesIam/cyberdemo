# Interacción CyberDemo - Agente IA

## Documento Funcional de Integración Bidireccional

**Versión**: 1.0
**Fecha**: 2026-02-22
**Proyecto**: CyberDemo - SOC Tier-1 Agentic AI Analyst

---

## 1. Resumen Ejecutivo

CyberDemo es una plataforma de simulación SOC que expone sus funcionalidades a través de **MCP (Model Context Protocol)**, permitiendo que un agente IA (SoulInTheBot/Claude) interactúe con sistemas de seguridad simulados.

### Arquitectura Actual

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA MCP BIDIRECCIONAL                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                     SOULINTHEBOT (Agente IA)                          │ │
│  │                     Puerto: 18789                                      │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │ │
│  │  │  Plugin: cyberdemo-soc-analyst                                  │ │ │
│  │  │  MCP Clients configurados:                                      │ │ │
│  │  │  • cyberdemo-api (:8000/mcp)                                    │ │ │
│  │  │  • cyberdemo-data (:8000/data-mcp)                              │ │ │
│  │  │  • cyberdemo-frontend (:3001 WebSocket)                         │ │ │
│  │  └─────────────────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                              │                                              │
│                              │ JSON-RPC 2.0 / WebSocket                    │
│                              ▼                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                     CYBERDEMO (Producto)                              │ │
│  │                                                                       │ │
│  │  ┌─────────────────────┐  ┌─────────────────────┐  ┌───────────────┐ │ │
│  │  │   BACKEND MCP       │  │    DATA MCP         │  │ FRONTEND MCP  │ │ │
│  │  │   Python/FastAPI    │  │   Python/FastAPI    │  │   TS/WebSocket│ │ │
│  │  │   :8000/mcp/*       │  │   :8000/data-mcp/*  │  │   :3001       │ │ │
│  │  │                     │  │                     │  │               │ │ │
│  │  │   9 categorías      │  │   8 tools           │  │   8 tools     │ │ │
│  │  │   ~30 tools         │  │   generación datos  │  │   visualización│ │
│  │  └─────────────────────┘  └─────────────────────┘  └───────────────┘ │ │
│  │                                                                       │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │ │
│  │  │                    BASES DE DATOS                               │ │ │
│  │  │  ┌───────────────────┐    ┌───────────────────┐                 │ │ │
│  │  │  │    OpenSearch     │    │    PostgreSQL     │                 │ │ │
│  │  │  │    :9200          │    │    :5433          │                 │ │ │
│  │  │  │  • Alertas        │    │  • Assets         │                 │ │ │
│  │  │  │  • Logs           │    │  • Config         │                 │ │ │
│  │  │  │  • Threat Intel   │    │  • Audit          │                 │ │ │
│  │  │  │  • Attack Surface │    │  • Tickets        │                 │ │ │
│  │  │  └───────────────────┘    └───────────────────┘                 │ │ │
│  │  └─────────────────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. MCP Servers Implementados

### 2.1 Backend MCP Server (SOC Operations)

**Protocolo**: JSON-RPC 2.0 sobre HTTP
**Endpoint**: `POST /mcp/messages`
**Puerto**: 8000

#### Tools por Categoría

| Categoría | Tool | Descripción | Input Schema |
|-----------|------|-------------|--------------|
| **SIEM** | `siem_list_incidents` | Lista incidentes de seguridad | `{severity?, status?, limit?}` |
| | `siem_get_incident` | Detalle de incidente | `{incident_id}` |
| | `siem_add_comment` | Añade comentario de investigación | `{incident_id, comment}` |
| | `siem_close_incident` | Cierra incidente con resolución | `{incident_id, resolution, notes?}` |
| **EDR** | `edr_get_detection` | Detalle de detección | `{detection_id}` |
| | `edr_get_process_tree` | Árbol de procesos padre/hijo | `{detection_id}` |
| | `edr_hunt_hash` | Busca hash en todos los endpoints | `{hash}` |
| | `edr_contain_host` | Aísla host de la red | `{device_id, reason}` |
| | `edr_lift_containment` | Levanta aislamiento | `{device_id, reason}` |
| | `edr_list_detections` | Lista detecciones recientes | `{severity?, limit?}` |
| **Intel** | `intel_lookup_ioc` | Busca IOC en feeds | `{ioc, type}` |
| | `intel_get_campaign` | Info de campaña de amenaza | `{campaign_id}` |
| **CTEM** | `ctem_get_findings` | Hallazgos de vulnerabilidad | `{asset_id?}` |
| | `ctem_prioritize` | Prioriza vulnerabilidades | `{criteria}` |
| **Approvals** | `approval_request` | Solicita aprobación humana | `{action, asset_id, reason}` |
| | `approval_check` | Verifica estado de aprobación | `{request_id}` |
| **Tickets** | `ticket_create` | Crea ticket de remediación | `{title, description, priority}` |
| | `ticket_update` | Actualiza ticket | `{ticket_id, status?, notes?}` |
| **Reports** | `report_generate` | Genera reporte | `{type, format, filters?}` |
| **Threat Enrichment** | `threat_enrich_ip` | Enriquece IP con contexto | `{ip}` |
| | `threat_enrich_domain` | Enriquece dominio | `{domain}` |
| | `threat_enrich_hash` | Enriquece hash de archivo | `{hash}` |
| **Vulnerability** | `vuln_get_details` | Detalle de CVE | `{cve_id}` |
| | `vuln_get_affected_assets` | Assets afectados por CVE | `{cve_id}` |
| | `vuln_calculate_risk` | Calcula riesgo | `{cve_id, asset_id}` |

#### Ejemplo de Llamada

```json
// Request
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "edr_contain_host",
    "arguments": {
      "device_id": "WKS-FIN-001",
      "reason": "Ransomware AnchorDNS detected - immediate isolation required"
    }
  }
}

// Response
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\"status\": \"contained\", \"device_id\": \"WKS-FIN-001\", \"timestamp\": \"2026-02-22T10:30:00Z\"}"
    }]
  }
}
```

---

### 2.2 Data MCP Server (Synthetic Data Generation)

**Protocolo**: JSON-RPC 2.0 sobre HTTP
**Endpoint**: `POST /data-mcp/messages`
**Puerto**: 8000

| Tool | Descripción | Input Schema |
|------|-------------|--------------|
| `data_generate_assets` | Genera assets sintéticos | `{count?, seed?}` |
| `data_generate_edr_detections` | Genera detecciones EDR con MITRE | `{count?, seed?}` |
| `data_generate_siem_incidents` | Genera incidentes SIEM correlacionados | `{seed?}` |
| `data_generate_threat_intel` | Genera IOCs (hashes, IPs, dominios) | `{count?, seed?}` |
| `data_generate_ctem_findings` | Genera hallazgos CTEM con CVEs | `{seed?}` |
| `data_generate_all` | Genera todos los tipos con cross-references | `{seed?}` |
| `data_reset` | Limpia todos los datos generados | `{}` |
| `data_get_health` | Estado de la generación | `{}` |

---

### 2.3 Frontend MCP Server (Visualization Control)

**Protocolo**: WebSocket con mensajes JSON
**Endpoint**: `ws://localhost:3001`
**Puerto**: 3001

| Tool | Descripción | Input Schema |
|------|-------------|--------------|
| `show_simulation` | Muestra simulación de ataque en UI | `{scenario, speed?}` |
| `generate_chart` | Genera gráfico dinámicamente | `{type, data, title}` |
| `run_demo_scenario` | Ejecuta escenario predefinido | `{scenario_name}` |
| `get_demo_state` | Obtiene estado actual del demo | `{}` |
| `update_dashboard` | Actualiza métricas del dashboard | `{metrics}` |
| `show_alert_timeline` | Muestra timeline de alertas | `{incident_id}` |
| `highlight_asset` | Resalta asset en visualización | `{asset_id, color?}` |
| `show_postmortem` | Muestra post-mortem de incidente | `{incident_id}` |

#### Estado Compartido (DemoState)

```typescript
interface DemoState {
  activeScenario: string | null;      // Escenario activo
  simulationRunning: boolean;          // Simulación en curso
  highlightedAssets: string[];         // Assets resaltados
  currentView: string;                 // Vista actual (dashboard, surface, etc.)
  charts: Chart[];                     // Gráficos dinámicos generados
  timeline: Timeline | null;           // Timeline de eventos
}
```

---

## 3. Flujos de Comunicación

### 3.1 Agente → Producto (Dirección Principal)

El agente inicia acciones llamando tools del producto:

```
┌─────────────────┐                              ┌─────────────────┐
│   SoulInTheBot  │  ────── tools/call ───────►  │   CyberDemo     │
│   (Claude)      │                              │   MCP Server    │
│                 │  ◄───── result ───────────   │                 │
└─────────────────┘                              └─────────────────┘
```

**Casos de Uso Actuales**:
- Investigar alertas de seguridad
- Contener endpoints comprometidos
- Buscar propagación de malware
- Enriquecer IOCs con threat intel
- Crear tickets de remediación
- Generar reportes

### 3.2 Producto → Agente (Dirección Secundaria)

El producto notifica eventos al agente vía WebSocket:

```
┌─────────────────┐                              ┌─────────────────┐
│   CyberDemo     │  ────── state_update ─────►  │   SoulInTheBot  │
│   Frontend      │                              │   (escuchando)  │
│                 │  ◄───── tool response ────   │                 │
└─────────────────┘                              └─────────────────┘
```

**Eventos Actuales**:
- `state_update`: Cambios en el estado del demo
- `approval_needed`: Asset crítico requiere aprobación humana
- `alert_triggered`: Nueva alerta detectada

---

## 4. Flujo de Demo Típico

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FLUJO DE INVESTIGACIÓN SOC                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. DETECCIÓN                                                              │
│     ─────────                                                              │
│     Agente: siem_list_incidents({severity: "critical"})                    │
│     └─► Recibe lista de incidentes críticos                                │
│                                                                             │
│  2. INVESTIGACIÓN                                                          │
│     ─────────────                                                          │
│     Agente: siem_get_incident({incident_id: "INC-001"})                    │
│     └─► Obtiene detalles del incidente                                     │
│                                                                             │
│     Agente: edr_get_process_tree({detection_id: "DET-001"})                │
│     └─► Ve árbol de procesos sospechosos                                   │
│                                                                             │
│  3. ENRICHMENT                                                             │
│     ──────────                                                             │
│     Agente: threat_enrich_hash({hash: "abc123..."})                        │
│     └─► Confirma malware conocido (APT28)                                  │
│                                                                             │
│     Agente: edr_hunt_hash({hash: "abc123..."})                             │
│     └─► Encuentra 3 endpoints adicionales infectados                       │
│                                                                             │
│  4. DECISIÓN                                                               │
│     ────────                                                               │
│     Agente evalúa: Asset WKS-FIN-001 es crítico (Finance)                  │
│     └─► Requiere aprobación humana                                         │
│                                                                             │
│     Agente: approval_request({                                             │
│       action: "contain",                                                   │
│       asset_id: "WKS-FIN-001",                                             │
│       reason: "Ransomware detected on finance workstation"                 │
│     })                                                                      │
│                                                                             │
│  5. HUMAN-IN-THE-LOOP                                                      │
│     ─────────────────                                                      │
│     Frontend: Muestra modal de aprobación                                  │
│     Humano: Aprueba la contención                                          │
│     WebSocket: Notifica al agente                                          │
│                                                                             │
│  6. CONTENCIÓN                                                             │
│     ───────────                                                            │
│     Agente: edr_contain_host({device_id: "WKS-FIN-001", reason: "..."})    │
│     └─► Endpoint aislado de la red                                         │
│                                                                             │
│  7. DOCUMENTACIÓN                                                          │
│     ─────────────                                                          │
│     Agente: siem_add_comment({incident_id: "INC-001", comment: "..."})     │
│     Agente: ticket_create({title: "Remediate WKS-FIN-001", ...})           │
│                                                                             │
│  8. VISUALIZACIÓN                                                          │
│     ─────────────                                                          │
│     Agente: highlight_asset({asset_id: "WKS-FIN-001", color: "red"})       │
│     Agente: show_alert_timeline({incident_id: "INC-001"})                  │
│                                                                             │
│  9. CIERRE                                                                 │
│     ──────                                                                 │
│     Agente: siem_close_incident({                                          │
│       incident_id: "INC-001",                                              │
│       resolution: "true_positive",                                         │
│       notes: "Ransomware contained. 4 endpoints isolated."                 │
│     })                                                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Interfaces de Integración

### 5.1 React Hooks para MCP (Frontend)

```typescript
// Usar el contexto MCP completo
const { demoState, connected, setDemoState, reconnect } = useMCP();

// Solo el estado del demo
const demoState = useDemoState();

// Solo el estado de conexión
const { connected, error, reconnect } = useMCPConnection();
```

### 5.2 Protocolo JSON-RPC 2.0 (Backend)

```python
# Listar tools disponibles
POST /mcp/messages
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}

# Llamar un tool
POST /mcp/messages
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "siem_get_incident",
    "arguments": {"incident_id": "INC-001"}
  }
}
```

---

## 6. Implicaciones: Mejoras para Mayor Utilidad en Demos

### 6.1 Gaps Identificados

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ANÁLISIS DE GAPS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DIRECCIÓN AGENTE → PRODUCTO (Actual: ✅ Bien cubierta)                    │
│  ────────────────────────────────────────────────────                      │
│  • 46+ tools disponibles                                                   │
│  • Cubre SIEM, EDR, Intel, CTEM, Tickets, Reports                          │
│  • Falta: Algunas acciones de remediación automatizada                     │
│                                                                             │
│  DIRECCIÓN PRODUCTO → AGENTE (Actual: ⚠️ Limitada)                         │
│  ─────────────────────────────────────────────────                         │
│  • Solo eventos de estado vía WebSocket                                    │
│  • No hay invocación activa del agente                                     │
│  • Falta: Callbacks, webhooks, solicitudes de análisis                     │
│                                                                             │
│  ESCENARIOS DE DEMO (Actual: ⚠️ Limitados)                                 │
│  ─────────────────────────────────────────                                 │
│  • Solo 2 escenarios predefinidos (ransomware, supply chain)               │
│  • Falta: Más variedad, escenarios interactivos                            │
│                                                                             │
│  OBSERVABILIDAD (Actual: ⚠️ Básica)                                        │
│  ────────────────────────────────                                          │
│  • Logs básicos                                                            │
│  • Falta: Métricas de performance, tracing, audit completo                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Nuevos MCPs Recomendados

#### 6.2.1 MCP de Orquestación de Agente

**Propósito**: Permitir que el producto invoque activamente al agente para realizar análisis.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MCP: AGENT ORCHESTRATION                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Tools:                                                                    │
│  ───────                                                                   │
│  • agent_analyze_alert       - Pide al agente analizar una alerta          │
│  • agent_investigate_ioc     - Pide investigación de IOC                   │
│  • agent_recommend_action    - Solicita recomendación de acción            │
│  • agent_generate_report     - Pide generar reporte narrativo              │
│  • agent_explain_decision    - Pide explicación de decisión previa         │
│  • agent_correlate_events    - Pide correlación de eventos                 │
│                                                                             │
│  Flujo:                                                                    │
│  ──────                                                                    │
│  1. Usuario hace clic en "Analyze" en la UI                                │
│  2. Frontend llama: agent_analyze_alert({alert_id: "..."})                 │
│  3. MCP envía request a SoulInTheBot                                       │
│  4. Agente procesa y responde con análisis                                 │
│  5. UI muestra resultado al usuario                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 6.2.2 MCP de Playbooks Automatizados

**Propósito**: Ejecutar playbooks de respuesta con intervención del agente.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MCP: PLAYBOOK AUTOMATION                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Tools:                                                                    │
│  ───────                                                                   │
│  • playbook_list             - Lista playbooks disponibles                 │
│  • playbook_execute          - Ejecuta playbook con parámetros             │
│  • playbook_pause            - Pausa ejecución para decisión humana        │
│  • playbook_resume           - Continúa ejecución                          │
│  • playbook_rollback         - Revierte acciones del playbook              │
│  • playbook_status           - Estado de ejecución                         │
│                                                                             │
│  Playbooks Predefinidos:                                                   │
│  ───────────────────────                                                   │
│  • Ransomware Response                                                     │
│  • Phishing Investigation                                                  │
│  • Lateral Movement Detection                                              │
│  • Data Exfiltration Response                                              │
│  • Insider Threat Investigation                                            │
│  • Cloud Compromise Response                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 6.2.3 MCP de Simulación de Ataques

**Propósito**: Simular ataques en tiempo real para demos interactivas.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MCP: ATTACK SIMULATION                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Tools:                                                                    │
│  ───────                                                                   │
│  • attack_start_scenario     - Inicia escenario de ataque                  │
│  • attack_inject_event       - Inyecta evento en tiempo real               │
│  • attack_escalate           - Escala el ataque                            │
│  • attack_spread_lateral     - Simula movimiento lateral                   │
│  • attack_exfiltrate         - Simula exfiltración de datos                │
│  • attack_pause              - Pausa para explicación                      │
│  • attack_speed              - Ajusta velocidad de simulación              │
│                                                                             │
│  Escenarios:                                                               │
│  ───────────                                                               │
│  • APT29 (Cozy Bear) - Espionaje                                          │
│  • FIN7 - Financiero                                                       │
│  • Lazarus Group - Destructivo                                             │
│  • REvil/Sodinokibi - Ransomware                                          │
│  • SolarWinds-style Supply Chain                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 APIs REST Adicionales Recomendadas

#### 6.3.1 API de Narrativa de Incidentes

```yaml
POST /api/v1/narrative/generate
  Description: Genera narrativa de incidente en lenguaje natural
  Request:
    incident_id: string
    format: "executive" | "technical" | "timeline"
    language: "es" | "en"
  Response:
    narrative: string
    key_findings: string[]
    recommendations: string[]
```

#### 6.3.2 API de Métricas SOC

```yaml
GET /api/v1/metrics/soc
  Description: Métricas de performance del SOC
  Response:
    mttr: number          # Mean Time To Respond
    mttd: number          # Mean Time To Detect
    incidents_per_day: number
    automation_rate: number
    false_positive_rate: number
```

#### 6.3.3 API de Simulación Interactiva

```yaml
POST /api/v1/simulation/interactive
  Description: Control de simulación para demos en vivo
  Request:
    action: "start" | "pause" | "step" | "rewind" | "fast_forward"
    scenario: string
    commentary: boolean   # Narración del agente
```

### 6.4 Nuevas Funcionalidades de Llamadas Producto → Agente

#### 6.4.1 Webhooks de Eventos Críticos

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WEBHOOKS: PRODUCTO → AGENTE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Eventos que disparan llamada al agente:                                   │
│  ────────────────────────────────────────                                  │
│                                                                             │
│  • CRITICAL_ALERT_DETECTED                                                 │
│    └─► Agente analiza automáticamente                                      │
│                                                                             │
│  • ASSET_CRITICAL_COMPROMISED                                              │
│    └─► Agente evalúa impacto y recomienda                                  │
│                                                                             │
│  • LATERAL_MOVEMENT_DETECTED                                               │
│    └─► Agente busca scope completo                                         │
│                                                                             │
│  • DATA_EXFILTRATION_SUSPECTED                                             │
│    └─► Agente investiga destinos                                           │
│                                                                             │
│  • APPROVAL_TIMEOUT                                                        │
│    └─► Agente escala o toma acción por defecto                             │
│                                                                             │
│  • USER_REQUESTS_ANALYSIS                                                  │
│    └─► Usuario pide análisis desde UI                                      │
│                                                                             │
│  Configuración:                                                            │
│  ───────────────                                                           │
│  POST /api/v1/webhooks/configure                                           │
│  {                                                                         │
│    "event": "CRITICAL_ALERT_DETECTED",                                     │
│    "agent_endpoint": "http://soulinthebot:18789/analyze",                  │
│    "auto_invoke": true,                                                    │
│    "timeout_ms": 30000                                                     │
│  }                                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 6.4.2 Cola de Análisis Asíncrono

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ASYNC ANALYSIS QUEUE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Flujo:                                                                    │
│  ──────                                                                    │
│  1. Producto encola solicitud de análisis                                  │
│  2. Agente procesa en background                                           │
│  3. Resultado se almacena y notifica                                       │
│                                                                             │
│  APIs:                                                                     │
│  ─────                                                                     │
│  POST /api/v1/analysis/queue                                               │
│    → Encola análisis, retorna job_id                                       │
│                                                                             │
│  GET /api/v1/analysis/status/{job_id}                                      │
│    → Estado del análisis                                                   │
│                                                                             │
│  GET /api/v1/analysis/result/{job_id}                                      │
│    → Resultado cuando esté listo                                           │
│                                                                             │
│  WebSocket: /ws/analysis                                                   │
│    → Notificaciones en tiempo real                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 6.4.3 Modo Copilot Interactivo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COPILOT MODE                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Concepto:                                                                 │
│  ─────────                                                                 │
│  El agente observa las acciones del analista y ofrece sugerencias          │
│  proactivas, como un copiloto de seguridad.                                │
│                                                                             │
│  Implementación:                                                           │
│  ───────────────                                                           │
│  • Frontend envía stream de acciones del usuario                           │
│  • Agente analiza patrones y contexto                                      │
│  • Agente sugiere próximos pasos                                           │
│                                                                             │
│  Tools:                                                                    │
│  ───────                                                                   │
│  • copilot_observe_action    - Notifica acción del usuario                 │
│  • copilot_get_suggestion    - Obtiene sugerencia del agente               │
│  • copilot_explain_why       - Explica por qué sugiere algo                │
│  • copilot_auto_complete     - Autocompleta acción                         │
│                                                                             │
│  Ejemplo:                                                                  │
│  ────────                                                                  │
│  Usuario: Hace clic en un hash sospechoso                                  │
│  Agente: "Te sugiero buscar este hash en otros endpoints.                  │
│           He detectado 3 matches. ¿Quieres que los aísle?"                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.5 Mejoras de UX para Demos

#### 6.5.1 Panel de Control de Demo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DEMO CONTROL PANEL                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  [▶ Play] [⏸ Pause] [⏹ Stop] [⏪ Rewind] [⏩ 2x]    Speed: [===●==]  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Escenario: [▼ APT29 Espionage Campaign                           ]   │   │
│  │                                                                     │   │
│  │  Etapas:                                                           │   │
│  │  [✓] 1. Initial Access      [✓] 2. Execution                      │   │
│  │  [●] 3. Persistence         [ ] 4. Privilege Escalation           │   │
│  │  [ ] 5. Defense Evasion     [ ] 6. Credential Access              │   │
│  │  [ ] 7. Discovery           [ ] 8. Lateral Movement               │   │
│  │  [ ] 9. Collection          [ ] 10. Exfiltration                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Narración del Agente:                                             │   │
│  │  ────────────────────                                              │   │
│  │  "El atacante ha establecido persistencia mediante una tarea       │   │
│  │   programada. Ahora intentará escalar privilegios..."              │   │
│  │                                                                     │   │
│  │  [💡 Ver explicación técnica]  [📊 Ver métricas]                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 6.5.2 Split View: Agente + Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SPLIT VIEW MODE                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────────────┐  ┌────────────────────────────┐            │
│  │      AGENT REASONING       │  │      SOC DASHBOARD         │            │
│  │      ───────────────       │  │      ─────────────         │            │
│  │                            │  │                            │            │
│  │  🤔 Analizando alerta...   │  │  ┌──────────────────────┐ │            │
│  │                            │  │  │ Incidents: 12        │ │            │
│  │  Pasos de investigación:   │  │  │ Critical: 3 🔴       │ │            │
│  │  1. ✓ Obtener detalles     │  │  │ MTTR: 4.2h           │ │            │
│  │  2. ✓ Analizar procesos    │  │  └──────────────────────┘ │            │
│  │  3. ● Buscar IOCs          │  │                            │            │
│  │  4. ○ Evaluar impacto      │  │  [Mapa de assets]         │            │
│  │                            │  │  [Timeline]               │            │
│  │  Hallazgos:                │  │  [Detecciones]            │            │
│  │  - Malware: AnchorDNS      │  │                            │            │
│  │  - Familia: TrickBot       │  │                            │            │
│  │  - Attribution: Wizard     │  │                            │            │
│  │    Spider                  │  │                            │            │
│  │                            │  │                            │            │
│  │  Recomendación:            │  │                            │            │
│  │  [Contener endpoint]       │  │                            │            │
│  │                            │  │                            │            │
│  └────────────────────────────┘  └────────────────────────────┘            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.6 Resumen de Implicaciones

| Área | Estado Actual | Mejora Propuesta | Prioridad | Esfuerzo |
|------|---------------|------------------|-----------|----------|
| **Invocación Producto→Agente** | ⚠️ Solo WebSocket pasivo | Webhooks + Cola async | P0 | Media |
| **Escenarios de Demo** | ⚠️ 2 escenarios | +6 escenarios MITRE | P0 | Alta |
| **Narración del Agente** | ❌ No existe | Comentario en tiempo real | P1 | Media |
| **Modo Copilot** | ❌ No existe | Sugerencias proactivas | P1 | Alta |
| **Playbooks Automatizados** | ❌ No existe | 6 playbooks predefinidos | P1 | Alta |
| **Control de Demo** | ⚠️ Básico | Panel interactivo | P2 | Media |
| **Métricas SOC** | ⚠️ Básicas | MTTR, MTTD, automation rate | P2 | Baja |
| **Split View** | ❌ No existe | Agent + Dashboard side-by-side | P2 | Media |

---

## 7. Conclusiones

### 7.1 Fortalezas Actuales

- ✅ **MCP bien implementado**: 46+ tools cubriendo operaciones SOC completas
- ✅ **Protocolo estándar**: JSON-RPC 2.0 para interoperabilidad
- ✅ **Bidireccional básico**: WebSocket permite eventos del producto al agente
- ✅ **Human-in-the-loop**: Sistema de aprobaciones para activos críticos
- ✅ **Generación de datos**: Data MCP permite crear escenarios reproducibles

### 7.2 Oportunidades de Mejora

- 🔶 **Invocación activa del agente**: El producto debería poder "pedir" análisis al agente
- 🔶 **Más escenarios de demo**: Variedad de ataques para diferentes audiencias
- 🔶 **Narración en tiempo real**: El agente explicando su razonamiento
- 🔶 **Modo Copilot**: Sugerencias proactivas mientras el usuario trabaja
- 🔶 **UX de demo**: Controles de velocidad, pause, rewind para presentaciones

### 7.3 Próximos Pasos Recomendados

1. **Fase 1**: Implementar webhooks para invocación Producto→Agente
2. **Fase 2**: Crear 4-6 escenarios de ataque adicionales (APT29, FIN7, etc.)
3. **Fase 3**: Implementar narración en tiempo real del agente
4. **Fase 4**: Panel de control de demo interactivo
5. **Fase 5**: Modo Copilot para asistencia proactiva

---

*Documento generado: 2026-02-22*
*Autor: CyberDemo Architecture Team*
*Versión: 1.0*
