# Plugins, Skills, Herramientas, Hooks — SoulInTheBot

**Versión:** 1.0.0
**Fecha:** 2026-02-16
**Proyecto:** SoulInTheBot Ecosystem (CyberDemo + Medicum + SoulBot)

---

## Tabla de Contenidos

1. [Visión General de la Arquitectura](#1-visión-general-de-la-arquitectura)
2. [Proyecto CyberDemo — Componentes Custom](#2-proyecto-cyberdemo--componentes-custom)
3. [Proyecto Medicum — Componentes Custom](#3-proyecto-medicum--componentes-custom)
4. [Proyecto SoulInTheBot (SolBot) — Componentes Custom](#4-proyecto-soulinthebot-solbot--componentes-custom)
5. [Inventario Global: Dentro del Contenedor](#5-inventario-global-dentro-del-contenedor)
6. [Inventario Global: Fuera del Contenedor](#6-inventario-global-fuera-del-contenedor)
7. [Resumen Consolidado](#7-resumen-consolidado)

---

## 1. Visión General de la Arquitectura

El ecosistema SoulInTheBot tiene dos entornos de ejecución claramente diferenciados:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                       FUERA DEL CONTENEDOR (Host)                           │
│                                                                              │
│  ┌─────────────────────────┐    ┌──────────────────────────────────────┐   │
│  │  CLAUDE CODE (CLI Local) │    │  PLUGINS CUSTOM (~/custom-claude-)   │   │
│  │                          │    │  • software-builder-x                │   │
│  │  • Slash Commands        │    │  • answer-with-precision-x           │   │
│  │  • Agente navegador      │    │  • sync-origin                      │   │
│  │  • Hook global           │    │  • python2wf2p                      │   │
│  └──────────┬───────────────┘    └──────────────────────────────────────┘   │
│             │                                                                │
│             │  MCP HTTP Bridge (scripts/mcp-http-bridge.js)                  │
│             │  Whisper Proxy (medicum-demo/whisper-proxy.js)                  │
│             │                                                                │
├─────────────┼────────────────────────────────────────────────────────────────┤
│             │       DENTRO DEL CONTENEDOR (Docker)                           │
│             ▼                                                                │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  CYBERDEMO STACK (docker-compose)                                    │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌───────────────────────┐ │   │
│  │  │  Backend        │  │  Frontend       │  │  Infraestructura     │ │   │
│  │  │  (Port 8000)    │  │  (Port 3000)    │  │  • OpenSearch 9200   │ │   │
│  │  │                 │  │                 │  │  • Dashboards 5601   │ │   │
│  │  │  MCP HTTP Server│  │  MCP WS Server  │  │  • PostgreSQL 5433   │ │   │
│  │  │  12 módulos     │  │  8 tools UI     │  └───────────────────────┘ │   │
│  │  │  50+ tools      │  │  (Port 3001)    │                            │   │
│  │  │  + Data Server  │  │                 │                            │   │
│  │  └────────────────┘  └────────────────┘                            │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  OPENCLAW GATEWAY (Port 18789 — Host process)                        │   │
│  │  Plugin: @soulinthebot/cyberdemo-soc-analyst                         │   │
│  │  Plugin: @soulinthebot/medicum-ai (planificado)                      │   │
│  │  Skill: soc-analyst, investigate-incident, run-demo                  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Definiciones clave

| Término | Significado |
|---------|-------------|
| **Plugin** | Paquete de extensión con skills, hooks, agents y/o MCP servers |
| **Skill** | Instrucciones en lenguaje natural (SKILL.md) que definen el comportamiento del agente |
| **Tool (Herramienta MCP)** | Función callable vía protocolo MCP (JSON-RPC 2.0) |
| **Hook** | Interceptor que se ejecuta antes/después de una acción del agente (Pre/PostToolUse, Stop) |
| **MCP Server** | Servidor que expone tools al agente via protocolo estándar MCP |
| **Contenedor** | Entorno Docker donde se ejecutan los servicios de la plataforma |

---

## 2. Proyecto CyberDemo — Componentes Custom

**Repositorio:** `/home/oscar/NewProjects/SoulInTheBot/cyberdemo/`

CyberDemo es la plataforma de simulación SOC que demuestra cómo un Analista SOC Tier-1 puede ser automatizado usando IA.

---

### 2.1 MCP Servers (3 servidores)

#### 2.1.1 Backend MCP HTTP Server

| Atributo | Valor |
|----------|-------|
| **Ubicación** | `backend/src/mcp/server.py` |
| **Protocolo** | HTTP POST (JSON-RPC 2.0) |
| **Endpoint** | `/mcp/messages` |
| **Puerto** | 8000 |
| **Ejecuta** | Dentro del contenedor (`cyberdemo-backend`) |

**Funcionalidad:** Servidor MCP principal que expone todas las herramientas de operación SOC. Incluye rate limiting (100 req/min por sesión), audit logging, validación HMAC, y health check.

**Ejemplo de uso:**
```json
POST /mcp/messages
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "siem_get_incident",
    "arguments": { "incident_id": "INC-001" }
  },
  "id": 1
}
```

#### 2.1.2 Frontend MCP WebSocket Server

| Atributo | Valor |
|----------|-------|
| **Ubicación** | `frontend/src/mcp/server.ts` |
| **Protocolo** | WebSocket |
| **Endpoint** | `ws://localhost:3001` |
| **Puerto** | 3001 |
| **Ejecuta** | Dentro del contenedor (`cyberdemo-frontend`) |

**Funcionalidad:** Servidor WebSocket MCP que maneja clientes híbridos (Claude + React). Sincroniza el estado del demo con la interfaz React en tiempo real. Detecta el tipo de cliente via header `x-client-type`.

**Ejemplo de uso:**
```json
// Desde Claude/SoulBot via WebSocket
{
  "method": "tools/call",
  "params": {
    "name": "run_demo_scenario",
    "arguments": { "scenario_id": 1 }
  }
}
// → Dispara el escenario de auto-contención en la UI
```

#### 2.1.3 Backend MCP Data Server

| Atributo | Valor |
|----------|-------|
| **Ubicación** | `backend/src/mcp/data_server.py` |
| **Protocolo** | HTTP POST (JSON-RPC 2.0) |
| **Endpoint** | `/data-mcp/messages` |
| **Puerto** | 8000 (mismo backend, diferente ruta) |
| **Ejecuta** | Dentro del contenedor (`cyberdemo-backend`) |

**Funcionalidad:** Servidor MCP separado para generación de datos sintéticos realistas (incidentes, alertas, detecciones EDR, inteligencia de amenazas).

---

### 2.2 MCP Tools — Backend (12 módulos, 50+ herramientas)

Todas se ejecutan **dentro del contenedor** (`cyberdemo-backend`).

| Módulo | Archivo | Tools | Descripción |
|--------|---------|-------|-------------|
| **SIEM** | `mcp/tools/siem.py` | `siem_list_incidents`, `siem_get_incident`, `siem_add_comment`, `siem_close_incident` | Gestión de incidentes de seguridad |
| **EDR** | `mcp/tools/edr.py` | `edr_get_detection`, `edr_get_process_tree`, `edr_contain_host`, `edr_hunt_hash` | Endpoint Detection & Response |
| **Intel** | `mcp/tools/intel.py` | `intel_get_indicator`, `intel_search` | Inteligencia de amenazas (IoC, reputación) |
| **CTEM** | `mcp/tools/ctem.py` | `ctem_get_asset_risk`, `ctem_list_vulnerabilities` | Gestión continua de exposición a amenazas |
| **Approvals** | `mcp/tools/approvals.py` | `approvals_request`, `approvals_approve`, `approvals_reject` | Flujo de aprobación humana |
| **Tickets** | `mcp/tools/tickets.py` | `tickets_create`, `tickets_update`, `tickets_list` | Gestión de tickets de seguimiento |
| **Reports** | `mcp/tools/reports.py` | `reports_generate_postmortem` | Generación de informes post-incidente |
| **Threat Enrichment** | `mcp/tools/threat_enrichment.py` | Enriquecimiento de datos de amenazas | Enriquecimiento con fuentes externas |
| **Vulnerability** | `mcp/tools/vulnerability.py` | Gestión de vulnerabilidades | CVEs, scoring, remediación |
| **Agent Orchestration** | `mcp/tools/agent_orchestration.py` | `agent_analyze_alert`, `agent_investigate_ioc`, `agent_recommend_action`, `agent_generate_report`, `agent_explain_decision`, `agent_correlate_events` | 6 herramientas de orquestación del agente IA |
| **Attack Simulation** | `mcp/tools/attack_simulation.py` | `attack_start_scenario`, `attack_pause`, `attack_resume`, `attack_speed`, `attack_jump_to_stage`, `attack_inject_event` | 6 herramientas de simulación de ataques APT |
| **aIP Assist** | `mcp/tools/aip_assist.py` | `aip_get_suggestion`, `aip_explain_why`, `aip_auto_complete` | 3 herramientas de asistencia proactiva |

**Registro centralizado:** `backend/src/mcp/tools/__init__.py`

**Ejemplo de tool — Agent Orchestration:**
```python
# La Persona IA analiza una alerta
result = await agent_analyze_alert({
    "alert_id": "ALT-2024-0892",
    "include_mitre_mapping": True,
    "include_recommendations": True
})
# → Retorna: threat_assessment, mitre_mapping, affected_hosts, recommended_actions
```

---

### 2.3 MCP Tools — Frontend (8 herramientas)

Todas se ejecutan **dentro del contenedor** (`cyberdemo-frontend`).

| Tool | Archivo | Descripción | Ejemplo Input |
|------|---------|-------------|---------------|
| `show_simulation` | `mcp/tools/show-simulation.ts` | Muestra simulación de ataque en UI | `{ scenario: "apt29", phase: "execution" }` |
| `generate_chart` | `mcp/tools/generate-chart.ts` | Crea gráficos (bar/line/pie) | `{ type: "bar", title: "Alertas", data: [...] }` |
| `run_demo_scenario` | `mcp/tools/run-demo-scenario.ts` | Ejecuta escenario demo (1, 2 o 3) | `{ scenario_id: 1 }` |
| `get_demo_state` | `mcp/tools/get-demo-state.ts` | Obtiene estado actual del demo | `{}` |
| `update_dashboard` | `mcp/tools/update-dashboard.ts` | Actualiza dashboard con KPIs | `{ kpis: {...}, alerts: [...] }` |
| `show_alert_timeline` | `mcp/tools/show-alert-timeline.ts` | Muestra timeline de incidentes | `{ entries: [...] }` |
| `highlight_asset` | `mcp/tools/highlight-asset.ts` | Resalta asset en grafo | `{ asset_id: "WS-FIN-042", mode: "pulse" }` |
| `show_postmortem` | `mcp/tools/show-postmortem.ts` | Muestra informe post-incidente | `{ incident_id: "INC-001" }` |

**Registro:** `frontend/src/mcp/tools/index.ts`

---

### 2.4 Infraestructura MCP de Soporte

Todos ejecutan **dentro del contenedor** (`cyberdemo-backend`).

| Componente | Archivo | Función |
|------------|---------|---------|
| **Rate Limiter** | `backend/src/mcp/rate_limiter.py` | Limita a 100 req/min por sesión MCP |
| **Audit Logger** | `backend/src/mcp/audit_logger.py` | Registro inmutable de todas las invocaciones MCP |
| **HMAC Validator** | `backend/src/mcp/hmac_validator.py` | Autenticación HMAC-SHA256 para webhooks |
| **UIBridge** | `backend/src/services/ui_bridge.py` | Cliente WebSocket del backend → frontend (port 3001) |
| **MCP Handler** | `frontend/src/mcp/handler.ts` | Enrutamiento y validación de mensajes MCP |
| **MCP Context** | `frontend/src/mcp/context.tsx` | React Context Provider para estado MCP |
| **Data Generators** | `backend/src/mcp/data_tools/generators.py` | Generadores de datos sintéticos |

---

### 2.5 Plugin SOC Analyst (Dentro del contenedor/gateway)

| Atributo | Valor |
|----------|-------|
| **Plugin Name** | `@soulinthebot/cyberdemo-soc-analyst` |
| **Ubicación planificada** | `extensions/cyberdemo/` |
| **Ejecuta** | Dentro del gateway OpenClaw (Port 18789) |

**Componentes del plugin:**

| Componente | Archivo | Función |
|------------|---------|---------|
| **Plugin Config** | `SoulInTheBot.plugin.json` | Manifiesto con MCP servers, skills y configuración |
| **Skill: SOC Analyst** | `skills/soc-analyst/SKILL.md` | Define el rol de Analista SOC Tier-1, workflow de investigación, reglas de decisión |
| **API Client** | `src/api-client.ts` | Cliente tipado para las APIs del backend |
| **Policy Engine** | `src/policy-engine.ts` | Motor de reglas determinísticas para decisiones de contención |
| **Confidence Score** | `src/confidence-score.ts` | Algoritmo de cálculo del score (Intel 40%, Behavior 30%, Context 20%, Propagation 10%) |
| **Hooks** | `src/hooks.ts` | Eventos de trazabilidad y auditoría |

**Skills del plugin:**

| Skill | Trigger | Descripción |
|-------|---------|-------------|
| `investigate-incident` | `/investigate <id>` | Investiga un incidente SIEM completo con enriquecimiento, scoring y decisión |
| `run-demo` | `/demo <1\|2\|3>` | Ejecuta uno de los 3 escenarios ancla de la demo |

**MCP Servers que el plugin consume:**

| MCP Server | Protocolo | Tools |
|------------|-----------|-------|
| `cyberdemo-frontend` | WebSocket `ws://localhost:3001/mcp` | 8 tools de visualización UI |
| `cyberdemo-api` | HTTP `http://localhost:8001/mcp` | 30+ tools de operación SOC |
| `cyberdemo-data` | HTTP `http://localhost:8002/mcp` | Tools de generación de datos |

---

### 2.6 Bridge Script (Fuera del contenedor)

| Atributo | Valor |
|----------|-------|
| **Ubicación** | `scripts/mcp-http-bridge.js` |
| **Protocolo** | stdio (Content-Length framed) → HTTP |
| **Ejecuta** | Fuera del contenedor (Host) |

**Funcionalidad:** Convierte el protocolo MCP basado en stdio (que usa OpenClaw gateway con su plugin mcp-bridge) al formato HTTP POST que entiende el backend MCP server.

**Ejemplo de uso:**
```bash
node scripts/mcp-http-bridge.js http://localhost:8000/mcp/messages
# Lee de stdin, envía a HTTP, responde a stdout
```

---

### 2.7 Docker — Contenedores CyberDemo

**Archivo:** `docker/docker-compose.yml`

| Servicio | Contenedor | Puerto | Función |
|----------|-----------|--------|---------|
| `backend` | `cyberdemo-backend` | 8000 | FastAPI + MCP HTTP Server + Data Server |
| `frontend` | `cyberdemo-frontend` | 3000, 3001 | React + MCP WebSocket Server |
| `opensearch` | `cyberdemo-opensearch` | 9200 | Motor de búsqueda para datos SOC |
| `opensearch-dashboards` | `cyberdemo-dashboards` | 5601 | Visualización de datos |
| `postgres` | `cyberdemo-postgres` | 5433 | Base de datos PostgreSQL |

---

### 2.8 Resumen CyberDemo

| Tipo | Cantidad | Dentro Contenedor | Fuera Contenedor |
|------|----------|-------------------|------------------|
| **MCP Servers** | 3 | 3 (HTTP, WS, Data) | 0 |
| **MCP Tools Backend** | 50+ (12 módulos) | 50+ | 0 |
| **MCP Tools Frontend** | 8 | 8 | 0 |
| **Plugin SOC Analyst** | 1 | 1 (en gateway) | 0 |
| **Skills** | 2 | 2 (en gateway) | 0 |
| **Hooks** | 1 (en plugin) | 1 (en gateway) | 0 |
| **Bridge Scripts** | 1 | 0 | 1 |
| **Infraestructura MCP** | 7 componentes | 7 | 0 |
| **Contenedores Docker** | 5 | 5 | 0 |

---

## 3. Proyecto Medicum — Componentes Custom

**Código fuente:** `/home/oscar/NewProjects/SoulInTheBot/SoulInTheBot/AIPerson/person.ai/medicum-demo/`
**Documentación:** `/home/oscar/NewProjects/SoulInTheBot/cyberdemo/docs/` (centralizada en cyberdemo)

Medicum es un asistente de consulta médica con transcripción en tiempo real, notas SOAP, codificación CIE-10, y análisis de imágenes médicas.

---

### 3.1 MCP Client (Implementado)

| Atributo | Valor |
|----------|-------|
| **Ubicación** | `src/services/mcpClient.ts` |
| **Protocolo** | WebSocket (OpenClaw Gateway Protocol) |
| **Endpoint** | `ws://localhost:18789/gateway` |
| **Ejecuta** | En el navegador (cliente React) — Fuera del contenedor |

**Funcionalidad:** Cliente WebSocket que conecta con el gateway OpenClaw. Recibe comandos MCP de la Persona IA (SoulBot) y los ejecuta en la UI:

| Comando MCP | Función |
|-------------|---------|
| `navigate_to_tab` | Navega entre pestañas de la interfaz (Consulta, Historia, Codificación, Visor) |
| `get_state` | Obtiene el estado actual de la UI |
| `fill_field` | Rellena campos de formulario programáticamente |
| `click_element` | Simula clic en elementos de la interfaz |

**Ejemplo:**
```typescript
// La Persona IA (via gateway) envía un comando MCP:
{
  "command": "navigate_to_tab",
  "params": { "tab": "codificacion" }
}
// → El frontend cambia a la pestaña de Codificación CIE-10
```

---

### 3.2 Whisper Proxy Server (Implementado)

| Atributo | Valor |
|----------|-------|
| **Ubicación** | `whisper-proxy.js` |
| **Protocolo** | HTTP |
| **Puerto** | 3050 |
| **Ejecuta** | Fuera del contenedor (proceso Node.js en host) |

**Funcionalidad:** Servidor HTTP que actúa como puente entre el navegador y el servidor Whisper (transcripción de audio). Convierte audio WebM a WAV usando ffmpeg y lo envía al socket Unix de Whisper.

| Endpoint | Función |
|----------|---------|
| `GET /health` | Verifica estado del proxy y del servidor Whisper |
| `POST /transcribe` | Recibe audio WebM, lo convierte a WAV, lo envía a Whisper y retorna la transcripción |

**Ejemplo:**
```bash
# El frontend envía audio grabado del micrófono:
POST http://localhost:3050/transcribe
Content-Type: multipart/form-data
Body: audio.webm (grabación del doctor hablando)

# → Respuesta: { "text": "El paciente presenta dolor en la rodilla derecha..." }
```

---

### 3.3 Plugin Medicum-AI (Planificado, no implementado)

Según las especificaciones funcionales (`MEDICUM_OPENCLOUD_FUNCTIONAL_SPEC.md` y `MEDICUM_SOULBOT_FUNCTIONAL_SPEC.md`), el plugin `medicum-ai` está diseñado pero aún no construido.

| Atributo | Valor |
|----------|-------|
| **Plugin Name** | `medicum-ai` |
| **Ubicación planificada** | `extensions/medicum-ai/` |
| **Ejecuta (planificado)** | Dentro del gateway OpenClaw (Docker) |
| **Estado** | No implementado |

**5 Acciones planificadas:**

| Acción | Descripción | Input |
|--------|-------------|-------|
| `generate_soap` | Genera nota SOAP desde transcripción real usando Claude | Segmentos de transcripción + contexto del paciente |
| `suggest_icd10` | Sugiere códigos CIE-10 usando Claude + catálogo de 70K códigos | Texto de diagnóstico + contexto clínico |
| `search_icd10` | Búsqueda determinística en catálogo CIE-10 (sin LLM) | Texto de búsqueda |
| `analyze_image` | Analiza imagen médica usando Claude Vision | Imagen (base64) + indicación clínica |
| `generate_report` | Genera informe radiológico estructurado | Hallazgos + contexto clínico |

**3 Hooks planificados:**

| Hook | Tipo | Función |
|------|------|---------|
| `disclaimer-hook` | PostToolUse | Añade disclaimer médico obligatorio a toda respuesta de IA |
| `audit-hook` | PostToolUse | Registra todas las invocaciones para auditoría clínica |
| `validation-hook` | PreToolUse | Valida códigos CIE-10 antes de asignarlos |

**Skill planificado:**

| Skill | Ubicación planificada | Función |
|-------|----------------------|---------|
| `medicum-consult` | `skills/medicum-consult/SKILL.md` | Instrucciones para que SoulBot actúe como asistente médico durante consultas |

---

### 3.4 State Management (Implementado)

| Atributo | Valor |
|----------|-------|
| **Ubicación** | `src/stores/connectionStore.ts` |
| **Tecnología** | Zustand |
| **Ejecuta** | En el navegador (cliente React) |

**Funcionalidad:** Gestiona el estado de la conexión WebSocket con el gateway OpenClaw: estados (connecting, connected, disconnected, error), intentos de reconexión, y errores.

---

### 3.5 Resumen Medicum

| Tipo | Cantidad | Dentro Contenedor | Fuera Contenedor |
|------|----------|-------------------|------------------|
| **MCP Client** | 1 | 0 | 1 (navegador) |
| **Proxy Server** | 1 (Whisper) | 0 | 1 (Node.js host) |
| **Plugin medicum-ai** | 0 (planificado) | 0 (plan: 1 en gateway) | 0 |
| **Skills** | 0 (planificado) | 0 (plan: 1 en gateway) | 0 |
| **Hooks** | 0 (planificado) | 0 (plan: 3 en gateway) | 0 |
| **MCP Tools** | 0 (planificado) | 0 (plan: 5 en plugin) | 0 |
| **Contenedores Docker** | 0 | 0 | N/A |

---

## 4. Proyecto SoulInTheBot (SolBot) — Componentes Custom

Más allá de CyberDemo y Medicum, el proyecto SoulInTheBot incluye componentes de desarrollo creados como plugins de Claude Code para asistir en la construcción del software.

---

### 4.1 Plugins Custom de Desarrollo

Almacenados en `/home/oscar/custom-claude-plugins/` y enlazados a `~/.claude/plugins/`.
Todos se ejecutan **fuera del contenedor** (Claude Code CLI local).

#### 4.1.1 software-builder-x (v23.0.0)

**Propósito:** Construcción determinística de software con TDD, agentes paralelos, enforcement de log de ejecución, aislamiento de tests unitarios, y trazabilidad completa.

| Componente | Cantidad | Detalle |
|------------|----------|---------|
| **Skills** | 6 | `sbx` (orquestación), `design` (spec funcional), `plan` (BUILD/TEST/PROGRESS), `build` (4 agentes TDD), `verify` (verificación final), `analyze` (compliance) |
| **Agents** | 5 | `build-agent` (×4 instancias), `tdd-verifier`, `review-agent`, `design-reviewer`, `gap-analyzer` |
| **Hooks** | 6 | `sbx-flow-enforcer` (PreToolUse), `sbx-require-init-for-agents` (PreToolUse), `sbx-protect-execution-log` (PreToolUse), `sbx-log-spec-written` (PostToolUse), `sbx-audit-edits` (PostToolUse), `sbx-stop-validation` (Stop) |

**Ejemplo de uso:**
```bash
# En Claude Code CLI:
/sbx-design                    # Crea la especificación funcional
/sbx-plan                      # Genera BUILD_PLAN.md, TEST_PLAN.md, PROGRESS.md
/sbx-build                     # Lanza 4 build-agents + tdd-verifier + review-agent
/sbx-verify                    # Verificación final de requisitos
```

**Modelo de seguridad (3 capas):**
1. **Enforcer físico** — Cuenta archivos reales, detecta stubs, ejecuta tests
2. **Agentes semánticos** — TDD Verifier y Review Agent hacen análisis de coherencia
3. **Validación de ejecución** — El enforcer verifica que los agentes realmente hicieron su trabajo

#### 4.1.2 answer-with-precision-x (v3.1.0)

**Propósito:** Sistema de Q&A sobre datos con 99% de precisión. Usa flujo determinístico de 8 pasos con abstención controlada (si la confianza es baja, se abstiene de responder).

| Componente | Cantidad | Detalle |
|------------|----------|---------|
| **Skills** | 13 | `awpx` (principal), `catalog-discovery`, `run-data-query`, `ask-data-insight`, `anomaly-investigator`, `compare-periods`, `explain-metric`, `build-executive-brief`, `governance-audit`, `data-source-health`, `debug-query-failure`, `continuous-improvement`, `hola-mundo` |
| **Agents** | 6 | `planner-agent`, `catalog-agent`, `executor-agent`, `reflection-agent`, `insight-agent`, `governance-agent` |
| **Hooks** | 3 | `pre_query_validation` (PreToolUse), `post_query_provenance` (PostToolUse), `stop_completeness_check` (Stop) |

**Flujo de 8 pasos:** DISCOVER → PLAN → VALIDATE → EXECUTE → ANALYZE → RECORD → VERIFY → OUTPUT

**Ejemplo de uso:**
```bash
# En Claude Code CLI:
> ¿Cuántos incidentes críticos hubo en enero?
# → AWPX descubre tablas → planifica query → valida → ejecuta →
#   analiza → registra proveniencia → verifica → retorna respuesta con fuente
```

#### 4.1.3 sync-origin (v18.0.0)

**Propósito:** Sincronización determinística entre fork (SoulInTheBot) y repositorio origen (OpenClaw). Usa manifest + supervisor + auditoría + agentes paralelos por categoría.

| Componente | Cantidad | Detalle |
|------------|----------|---------|
| **Skills** | 1 | `sync-origin` — Sincronización completa con clasificación de archivos |
| **Agents** | 9 | `supervisor`, `category-a` (conflictos), `category-b` (solo local), `category-c` (solo origin), `category-d` (renombrados), `category-e` (configuración), `diff-analyzer`, `compatibility-checker`, `impact-analyzer` |
| **Hooks** | 10 | `pretooluse_verify_action`, `pretooluse_block_overwrite`, `pretooluse_block_git_overwrite`, `posttooluse_supervisor_audit`, `posttooluse_category_check`, `posttooluse_anti_false_missing`, `stop_guard_v18` (+3 más) |

**Clasificación de archivos en 5 categorías:**

| Categoría | Significado | Acción |
|-----------|-------------|--------|
| A | Modificado en ambos (conflicto) | Merge inteligente |
| B | Solo modificado localmente | Mantener sin cambios |
| C | Solo modificado en origin | Aplicar verificando impacto |
| D | Archivo renombrado | Seguir el rename |
| E | Configuración (JSON/YAML) | Merge campo a campo |

#### 4.1.4 python2wf2p (v1.0.0)

**Propósito:** Convierte programas Python (LangChain/LangGraph) a flujos Flowise V3 / ActivePieces.

| Componente | Cantidad | Detalle |
|------------|----------|---------|
| **Skills** | 1 | `workflow-generator` — Conversión Python → Workflow |
| **Agents** | 5 | `python-analyzer`, `workflow-mapper`, `response-extractor`, `document-generator`, `consistency-verifier` |
| **Hooks** | 3 | Pre-write validation, post-write verification, stop completeness |

---

### 4.2 Slash Commands Custom

Almacenados en `~/.claude/commands/`. Se ejecutan **fuera del contenedor**.

| Comando | Función | Ejemplo de uso |
|---------|---------|----------------|
| `/CommitX` | Stage all → commit con Co-Authored-By → push al remote | Después de completar una tarea |
| `/CompilaX` | Auto-detecta tipo de proyecto y lo compila/levanta | Después de cambios en código |
| `/TestandRunX` | Ejecuta tests unitarios y E2E, levanta Docker si necesario | Antes de commitear |
| `/ralph-loopXX` | Loop iterativo inteligente hasta cumplir condición | Tareas repetitivas |

---

### 4.3 Agente Custom Global

| Atributo | Valor |
|----------|-------|
| **Nombre** | `pruebas-en-navegador` |
| **Ubicación** | `~/.claude/agents/` |
| **Modelo** | Sonnet |
| **Ejecuta** | Fuera del contenedor (Claude Code CLI) |

**Funcionalidad:** Agente especializado en tests E2E con Playwright. Simula un usuario real navegando e interactuando con la aplicación web.

**Herramientas disponibles:** Bash, Read, Write, Edit, Grep, Glob

**Ejemplo de uso:**
```
El agente pruebas-en-navegador es invocado automáticamente cuando se necesita
verificar funcionalidades en el navegador. Navega a URLs, hace clic en elementos,
rellena formularios, y verifica resultados visuales.
```

---

### 4.4 Hook Global

| Atributo | Valor |
|----------|-------|
| **Nombre** | `sbx-build-log-protection.sh` |
| **Ubicación** | `~/.claude/hooks/` |
| **Tipo** | PreToolUse (Write, Edit, Bash) |
| **Ejecuta** | Fuera del contenedor (Claude Code CLI) |

**Funcionalidad:** Protege los archivos de ejecución del build enforcer de software-builder-x. Impide que cualquier agente escriba directamente en:
- `.sbx/build-execution-log.json`
- `.sbx/progress.json`
- `.sbx/tdd-semantic-verification.json`
- `.sbx/review-semantic-verification.json`

Solo `build-enforcer.py` puede escribir en estos archivos.

---

### 4.5 OpenClaw Gateway

| Atributo | Valor |
|----------|-------|
| **Nombre** | OpenClaw Gateway |
| **Puerto** | 18789 |
| **Comando** | `moltbot gateway run --port 18789` |
| **Protocolo** | OpenAI-compatible Chat Completions API |
| **Ejecuta** | En el host (proceso independiente, NO en Docker de CyberDemo) |

**Funcionalidad:** Es el "cerebro" del agente SoulBot. Ejecuta como proceso en el host y:
- Proporciona API compatible con OpenAI (`/v1/chat/completions`)
- Invocación directa de tools (`/tools/invoke`)
- Enrutamiento de agentes (`x-openclaw-agent-id` header)
- Gestión de sesiones (`x-openclaw-session-key` header)
- Autenticación Bearer token
- Carga plugins y skills de `extensions/`

**Plugins cargados:**
- `@soulinthebot/cyberdemo-soc-analyst` — Conecta a los 3 MCP servers de CyberDemo
- `medicum-ai` (planificado) — Conectará al backend de Medicum

---

## 5. Inventario Global: Dentro del Contenedor

Componentes **custom nuestros** que se ejecutan dentro del entorno Docker/Gateway y están disponibles para SoulBot.

### 5.1 MCP Servers Custom

| Servidor | Proyecto | Puerto | Protocolo | Función |
|----------|----------|--------|-----------|---------|
| Backend MCP HTTP | CyberDemo | 8000 | HTTP JSON-RPC | 50+ tools de operación SOC |
| Frontend MCP WS | CyberDemo | 3001 | WebSocket | 8 tools de visualización UI |
| Data MCP Server | CyberDemo | 8000 | HTTP JSON-RPC | Generación de datos sintéticos |

### 5.2 MCP Tools Custom (disponibles para SoulBot)

| Categoría | Proyecto | Cantidad | Ejemplos |
|-----------|----------|----------|----------|
| Operación SIEM | CyberDemo | 4+ | `siem_list_incidents`, `siem_get_incident`, `siem_close_incident` |
| Detección EDR | CyberDemo | 4+ | `edr_get_detection`, `edr_contain_host`, `edr_hunt_hash` |
| Inteligencia | CyberDemo | 2+ | `intel_get_indicator`, `intel_search` |
| Exposición CTEM | CyberDemo | 2+ | `ctem_get_asset_risk`, `ctem_list_vulnerabilities` |
| Aprobaciones | CyberDemo | 3+ | `approvals_request`, `approvals_approve`, `approvals_reject` |
| Tickets | CyberDemo | 3+ | `tickets_create`, `tickets_update`, `tickets_list` |
| Reportes | CyberDemo | 1+ | `reports_generate_postmortem` |
| Enriquecimiento | CyberDemo | 2+ | Enriquecimiento de amenazas |
| Vulnerabilidades | CyberDemo | 2+ | Gestión de CVEs |
| Orquestación Agente | CyberDemo | 6 | `agent_analyze_alert`, `agent_correlate_events`, etc. |
| Simulación Ataques | CyberDemo | 6 | `attack_start_scenario`, `attack_pause`, etc. |
| Asistencia Proactiva | CyberDemo | 3 | `aip_get_suggestion`, `aip_explain_why`, `aip_auto_complete` |
| Visualización UI | CyberDemo | 8 | `show_simulation`, `generate_chart`, `highlight_asset`, etc. |
| **TOTAL** | | **50+** | |

### 5.3 Plugin Custom (en Gateway)

| Plugin | Proyecto | Skills | Hooks | Función |
|--------|----------|--------|-------|---------|
| `cyberdemo-soc-analyst` | CyberDemo | 2 (`investigate-incident`, `run-demo`) | 1 (trazabilidad) | Analista SOC Tier-1 automatizado |
| `medicum-ai` (planificado) | Medicum | 1 (planificado) | 3 (planificados) | Asistente médico IA |

### 5.4 Infraestructura de Soporte (en contenedor)

| Componente | Proyecto | Función |
|------------|----------|---------|
| Rate Limiter | CyberDemo | 100 req/min por sesión |
| Audit Logger | CyberDemo | Registro inmutable de invocaciones |
| HMAC Validator | CyberDemo | Autenticación de webhooks |
| UIBridge | CyberDemo | Backend → Frontend via WebSocket |
| Data Generators | CyberDemo | Datos sintéticos realistas |
| Policy Engine | CyberDemo (plugin) | Decisiones determinísticas de contención |
| Confidence Score | CyberDemo (plugin) | Cálculo de score de amenaza |

---

## 6. Inventario Global: Fuera del Contenedor

Componentes **custom nuestros** que se ejecutan en el host y **NO están disponibles** para SoulBot dentro del contenedor.

### 6.1 Plugins de Desarrollo (Claude Code CLI)

| Plugin | Versión | Skills | Agents | Hooks | Función principal |
|--------|---------|--------|--------|-------|-------------------|
| `software-builder-x` | 23.0.0 | 6 | 5 | 6 | Construcción TDD con 6 agentes paralelos |
| `answer-with-precision-x` | 3.1.0 | 13 | 6 | 3 | Q&A sobre datos con 99% precisión |
| `sync-origin` | 18.0.0 | 1 | 9 | 10 | Sync fork ↔ origin con 5 categorías |
| `python2wf2p` | 1.0.0 | 1 | 5 | 3 | Convertir Python a Workflows |
| **TOTAL** | | **21** | **25** | **22** | |

### 6.2 Comandos Custom (Claude Code CLI)

| Comando | Función |
|---------|---------|
| `/CommitX` | Stage + commit + push en un solo paso |
| `/CompilaX` | Auto-detectar y compilar/levantar proyecto |
| `/TestandRunX` | Ejecutar tests + Docker + health checks |
| `/ralph-loopXX` | Loop iterativo inteligente |

### 6.3 Agente Custom Global

| Agente | Función |
|--------|---------|
| `pruebas-en-navegador` | Tests E2E con Playwright |

### 6.4 Hook Global

| Hook | Tipo | Función |
|------|------|---------|
| `sbx-build-log-protection.sh` | PreToolUse | Proteger archivos de ejecución SBX |

### 6.5 Bridge Scripts y Proxies

| Componente | Proyecto | Puerto | Función |
|------------|----------|--------|---------|
| `mcp-http-bridge.js` | CyberDemo | — (stdio) | Convierte stdio MCP → HTTP MCP |
| `whisper-proxy.js` | Medicum | 3050 | Puente navegador → Whisper (audio → texto) |

---

## 7. Resumen Consolidado

### 7.1 Totales por Tipo y Ubicación

| Tipo | Dentro Contenedor | Fuera Contenedor | Total |
|------|-------------------|------------------|-------|
| **MCP Servers** | 3 | 0 | 3 |
| **MCP Tools** | 50+ | 0 | 50+ |
| **Plugins Custom** | 1 (+ 1 planificado) | 4 | 5 (+ 1 plan) |
| **Skills** | 2 (+ 1 planificada) | 21 | 23 (+ 1 plan) |
| **Agents** | 0 | 25 + 1 global | 26 |
| **Hooks** | 1 (+ 3 planificados) | 22 + 1 global | 23 (+ 3 plan) |
| **Slash Commands** | 0 | 4 | 4 |
| **Bridge/Proxy Scripts** | 0 | 2 | 2 |
| **Contenedores Docker** | 5 | 0 | 5 |
| **Infraestructura MCP** | 7 | 0 | 7 |

### 7.2 Mapa Visual Completo

```
═══════════════════════════════════════════════════════════════════════════
 FUERA DEL CONTENEDOR (Host — Claude Code CLI)
═══════════════════════════════════════════════════════════════════════════

 PLUGINS DE DESARROLLO (4 plugins, 21 skills, 25 agents, 22 hooks)
 ├── software-builder-x ─── TDD + 6 agentes paralelos
 ├── answer-with-precision-x ─── Q&A datos, 8 pasos, 99% precisión
 ├── sync-origin ─── Sync fork↔origin, 5 categorías, 9 agentes
 └── python2wf2p ─── Python → Workflows (Flowise/ActivePieces)

 COMANDOS (4)
 ├── /CommitX ─── Stage + commit + push
 ├── /CompilaX ─── Auto-detect + compile + run
 ├── /TestandRunX ─── Tests + Docker + health
 └── /ralph-loopXX ─── Loop inteligente

 AGENTE GLOBAL (1)
 └── pruebas-en-navegador ─── Tests E2E Playwright

 HOOK GLOBAL (1)
 └── sbx-build-log-protection.sh ─── Proteger logs SBX

 BRIDGES Y PROXIES (2)
 ├── mcp-http-bridge.js ─── stdio→HTTP (CyberDemo)
 └── whisper-proxy.js ─── audio→texto (Medicum, port 3050)

═══════════════════════════════════════════════════════════════════════════
 DENTRO DEL CONTENEDOR / GATEWAY (Docker + OpenClaw)
═══════════════════════════════════════════════════════════════════════════

 CYBERDEMO (5 contenedores Docker)
 ├── Backend (port 8000)
 │   ├── MCP HTTP Server (JSON-RPC 2.0)
 │   │   ├── SIEM Tools (4+) ─── Incidentes, comentarios, cierre
 │   │   ├── EDR Tools (4+) ─── Detecciones, procesos, contención
 │   │   ├── Intel Tools (2+) ─── Reputación IoC, búsqueda
 │   │   ├── CTEM Tools (2+) ─── Riesgo activos, vulnerabilidades
 │   │   ├── Approvals Tools (3+) ─── Solicitar/aprobar/rechazar
 │   │   ├── Tickets Tools (3+) ─── Crear/actualizar/listar
 │   │   ├── Reports Tools (1+) ─── Postmortem
 │   │   ├── Threat Enrichment Tools ─── Enriquecer amenazas
 │   │   ├── Vulnerability Tools ─── CVEs, scoring
 │   │   ├── Agent Orchestration (6) ─── Análisis IA de alertas
 │   │   ├── Attack Simulation (6) ─── Simular ataques APT
 │   │   └── aIP Assist (3) ─── Asistencia proactiva
 │   ├── Data Server (JSON-RPC 2.0) ─── Datos sintéticos
 │   ├── Rate Limiter ─── 100 req/min
 │   ├── Audit Logger ─── Trazabilidad
 │   ├── HMAC Validator ─── Autenticación
 │   └── UIBridge ─── Backend→Frontend WS
 │
 ├── Frontend (port 3000, 3001)
 │   ├── MCP WebSocket Server (port 3001)
 │   │   ├── show_simulation ─── Simulación de ataques
 │   │   ├── generate_chart ─── Gráficos bar/line/pie
 │   │   ├── run_demo_scenario ─── Ejecutar escenarios 1/2/3
 │   │   ├── get_demo_state ─── Estado actual
 │   │   ├── update_dashboard ─── Actualizar KPIs
 │   │   ├── show_alert_timeline ─── Timeline incidentes
 │   │   ├── highlight_asset ─── Resaltar en grafo
 │   │   └── show_postmortem ─── Informe post-incidente
 │   └── React Context + Handler ─── Enrutamiento MCP
 │
 ├── OpenSearch (port 9200) ─── Motor de búsqueda
 ├── Dashboards (port 5601) ─── Visualización
 └── PostgreSQL (port 5433) ─── Base de datos

 OPENCLAW GATEWAY (port 18789 — proceso host)
 ├── Plugin: cyberdemo-soc-analyst
 │   ├── Skill: investigate-incident ─── /investigate <id>
 │   ├── Skill: run-demo ─── /demo <1|2|3>
 │   ├── Policy Engine ─── Decisiones determinísticas
 │   ├── Confidence Score ─── Intel 40%, Behavior 30%, Context 20%, Prop 10%
 │   └── API Client ─── Comunicación tipada con backend
 │
 └── Plugin: medicum-ai (PLANIFICADO)
     ├── 5 acciones: SOAP, ICD-10 suggest, ICD-10 search, image analysis, report
     ├── 3 hooks: disclaimer, audit, validation
     └── 1 skill: medicum-consult

═══════════════════════════════════════════════════════════════════════════
```

### 7.3 Lo que SoulBot puede usar vs. lo que no puede

| Disponible para SoulBot (Contenedor/Gateway) | NO disponible para SoulBot |
|----------------------------------------------|----------------------------|
| 50+ MCP Tools SOC (backend) | Plugins de desarrollo (sbx, awpx, sync, p2w) |
| 8 MCP Tools UI (frontend) | Slash Commands (/CommitX, /CompilaX, etc.) |
| Plugin cyberdemo-soc-analyst | Agente pruebas-en-navegador |
| Policy Engine + Confidence Score | Hook global sbx-build-log-protection |
| Infraestructura MCP (rate limit, audit, HMAC) | 25 agentes de plugins de desarrollo |
| Data Generators (datos sintéticos) | 22 hooks de plugins de desarrollo |
| UIBridge (control de UI) | 21 skills de plugins de desarrollo |

### 7.4 Notas importantes

1. **El gateway OpenClaw NO es un contenedor Docker de CyberDemo.** Se ejecuta como proceso independiente en el host, pero se comunica con los contenedores de CyberDemo via MCP.

2. **Los plugins de desarrollo son herramientas de construcción**, no de ejecución de producto. software-builder-x construyó CyberDemo, pero CyberDemo no lo usa en runtime.

3. **El MCP HTTP Bridge** es necesario para que OpenClaw (que usa protocolo stdio) pueda comunicarse con el backend MCP (que usa HTTP). Sin este bridge, el gateway no puede llamar a las herramientas del backend.

4. **Medicum tiene sus componentes funcionales implementados** (client MCP, whisper proxy) pero el plugin de IA (`medicum-ai`) que conectaría con Claude para funcionalidades avanzadas está pendiente de desarrollo.

5. **ActivePieces (OpenCloud)** actúa como MCP Bridge adicional, exponiendo sus flujos de automatización como tools MCP. Esto es un componente genérico, no custom nuestro, pero integrado en la arquitectura.

---

*Documento generado: 2026-02-16*
*Basado en: análisis del código fuente de CyberDemo, Medicum, SoulInTheBot, plugins custom, y documentación del ecosistema.*
