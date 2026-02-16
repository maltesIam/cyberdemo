# CyberDemoDescription

## Resumen ejecutivo

CyberDemo es una plataforma de simulacion SOC que permite demostrar un analista SOC Tier-1 automatizado sobre SoulInTheBot usando datos sinteticos, APIs REST, servidores MCP y una interfaz web operativa.

### Inventario de elementos construidos

| Dominio          | Elementos principales                                                                                                        | Estado funcional                                        |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Interfaz grafica | App React con 14 vistas, grafo, timeline, colaboracion, configuracion, auditoria                                             | Operativa para exploracion y seguimiento de incidentes  |
| APIs backend     | Router unificado FastAPI con dominios SIEM/EDR/Intel/CTEM, enrichment, demo, config, audit, playbooks, collab, notifications | Operativas para UI, flujos SOC y demo                   |
| MCP frontend     | Servidor WebSocket y 8 tools de visualizacion                                                                                | Operativo para controlar la UI desde el agente          |
| MCP backend/data | Servidor MCP SOC + servidor MCP de datos sinteticos                                                                          | Operativos para exponer herramientas al agente          |
| Programas Python | Generadores de datos, enriquecimiento, escenarios demo, triggers automaticos                                                 | Operativos para simulacion, enrichment y automatizacion |
| Plugin y skill   | `extensions/cyberdemo` con skill `soc-analyst`, comandos, hooks y servicios TS                                               | Operativo para flujos `/investigate` y `/demo`          |
| Calidad          | Suite de tests unitarios, integracion y E2E en frontend/backend/plugin                                                       | Cobertura funcional reportada en docs de progreso       |

### Beneficio funcional por capa

| Capa                 | Que aporta                                                                             |
| -------------------- | -------------------------------------------------------------------------------------- |
| UI                   | Visibilidad end-to-end de incidentes, activos, decisiones, trazabilidad y colaboracion |
| API REST             | Contratos claros para poblar UI, ejecutar acciones SOC y exponer configuracion         |
| MCP                  | Interaccion agente↔sistema (acciones SOC) y agente↔UI (visualizacion guiada)           |
| Generacion sintetica | Datos realistas y reproducibles para demos y pruebas                                   |
| Enrichment           | Contexto de amenazas y vulnerabilidades para decisiones con mayor confianza            |
| Plugin/skill         | Orquestacion SOC Tier-1 reusable desde SoulInTheBot                                    |

---

## 1) Interfaz grafica: que es, funcionalidades, ventajas, que hace cada parte y como usarla

### Que es

La UI de CyberDemo es una aplicacion React/Vite para operar y visualizar el ciclo SOC completo:

- Ubicacion: `CyberDemo/frontend/`
- Entrada y rutas: `CyberDemo/frontend/src/App.tsx`
- Layout general: `CyberDemo/frontend/src/components/Layout.tsx`, `CyberDemo/frontend/src/components/Sidebar.tsx`
- Cliente API: `CyberDemo/frontend/src/services/api.ts`

### Ventajas funcionales

- Centraliza en una sola consola datos de SIEM, EDR, CTEM, tickets, postmortems y acciones del agente.
- Permite explicar demos de punta a punta con evidencia visual (timeline, grafo, estado).
- Habilita operacion asistida por agente via MCP frontend sin abandonar la interfaz.
- Facilita auditoria y gobernanza (configuracion, logs, historial de acciones).

### Vistas y como usarlas

1. `GenerationPage` (`/generation`)
   - Para que sirve: generar/resetear datos sinteticos y verificar estado de generacion.
   - Como usar: iniciar con esta vista, ejecutar generacion y validar estado antes de correr demos.

2. `DashboardPage` (`/dashboard`)
   - Para que sirve: KPIs SOC y estado agregado.
   - Como usar: revisar salud operativa y cambios tras ejecutar casos demo.

3. `AssetsPage` (`/assets`)
   - Para que sirve: inventario de activos con filtros (tipo, OS, riesgo, tags).
   - Como usar: buscar activos criticos/VIP y revisar contexto antes de contencion.

4. `IncidentsPage` (`/incidents`)
   - Para que sirve: gestion de incidentes SIEM.
   - Como usar: abrir incidente, revisar comentarios/entidades, seguir su estado.

5. `DetectionsPage` (`/detections`)
   - Para que sirve: detecciones EDR y detalle tecnico.
   - Como usar: inspeccionar severidad, hash, cmdline y arbol de procesos.

6. `CTEMPage` (`/ctem`)
   - Para que sirve: exposicion de vulnerabilidades y riesgo.
   - Como usar: validar criticidad de activos para decisiones del policy engine.

7. `TimelinePage` (`/timeline`)
   - Para que sirve: secuencia de acciones del agente.
   - Como usar: auditar pasos, tiempos y decisiones durante investigacion.

8. `PostmortemsPage` (`/postmortems`)
   - Para que sirve: consulta de informes post-incidente.
   - Como usar: revisar causa raiz, impacto, remediacion y lecciones.

9. `TicketsPage` (`/tickets`)
   - Para que sirve: seguimiento de tickets asociados a incidentes.
   - Como usar: validar apertura/cierre y prioridad de tareas operativas.

10. `GraphPage` (`/graph`, `/graph/:incidentId`)

- Para que sirve: visualizacion de relaciones incidente-activo-indicadores.
- Como usar: navegar nodos, filtrar y resaltar activos afectados.

11. `CollabPage` (`/collab`)

- Para que sirve: colaboracion en tiempo real del equipo SOC.
- Como usar: mensajeria, reacciones y canales para coordinacion de respuesta.

12. `ConfigPage` (`/config`)

- Para que sirve: politica, notificaciones e integraciones.
- Como usar: ajustar umbrales/reglas y resetear configuracion cuando sea necesario.

13. `AuditPage` (`/audit`)

- Para que sirve: trazabilidad de acciones y exportacion de logs.
- Como usar: filtrar por usuario/accion/resultado y exportar evidencia.

### Componentes UI clave

- Grafo y analisis visual:
  - `CyberDemo/frontend/src/components/Graph/CytoscapeGraph.tsx`
  - `CyberDemo/frontend/src/components/Graph/GraphControls.tsx`
  - `CyberDemo/frontend/src/components/Graph/NodeDetailPanel.tsx`
- Superficie de ataque:
  - `CyberDemo/frontend/src/components/AttackSurface/AttackSurfaceLayers.tsx`
  - `CyberDemo/frontend/src/components/AttackSurface/LayerToggle.tsx`
  - `CyberDemo/frontend/src/components/AttackSurface/TimeSlider.tsx`
- Colaboracion:
  - `CyberDemo/frontend/src/components/Collab/CollabChat.tsx`
  - `CyberDemo/frontend/src/components/Collab/CollabMessage.tsx`
  - `CyberDemo/frontend/src/components/Collab/CollabInput.tsx`
  - `CyberDemo/frontend/src/components/Collab/CollabAttachments.tsx`

---

## 2) APIs creadas para que la interfaz y el agente ejecuten acciones y reflejen resultados

### 2.1 API REST del backend (FastAPI)

Router unificado: `CyberDemo/backend/src/api/router.py`

Dominios principales y uso:

- Salud: `CyberDemo/backend/src/api/health.py`
  - `GET /health`, `GET /health/opensearch`, `GET /health/database`
- Generacion: `CyberDemo/backend/src/api/gen.py`
  - `POST /gen/reset`, `POST /gen/all`, `POST /gen/assets`, `GET /gen/status`, `GET /gen/health`
- SIEM: `CyberDemo/backend/src/api/siem.py`
  - lista/detalle/comentarios/actualizacion de incidentes
- EDR: `CyberDemo/backend/src/api/edr.py`
  - lista/detalle/procesos/hunt/contain/lift containment
- Intel: `CyberDemo/backend/src/api/intel.py`
  - reputacion de indicadores y busqueda
- CTEM: `CyberDemo/backend/src/api/ctem.py`
  - riesgo por activo, hallazgos y resumen
- Approvals: `CyberDemo/backend/src/api/approvals.py`
  - estado, solicitud, decision y pendientes
- Dashboard: `CyberDemo/backend/src/api/dashboard.py`
  - KPIs para la vista principal
- Timeline: `CyberDemo/backend/src/api/timeline.py`
  - acciones del agente
- Tickets: `CyberDemo/backend/src/api/tickets.py`
- Postmortems: `CyberDemo/backend/src/api/postmortems.py`
- Graph: `CyberDemo/backend/src/api/graph.py`
- SOAR: `CyberDemo/backend/src/api/soar.py`
- Enrichment: `CyberDemo/backend/src/api/enrichment.py`
  - `POST /api/vulnerabilities`, `POST /api/threats`, `GET /api/status/{job_id}`
- Collaboration: `CyberDemo/backend/src/api/collab.py`
  - REST + WebSocket para chat/canales/reacciones/busqueda
- Notifications: `CyberDemo/backend/src/api/notifications.py`
- Playbooks: `CyberDemo/backend/src/api/playbooks.py`
- Configuracion: `CyberDemo/backend/src/api/config.py`
- Auditoria: `CyberDemo/backend/src/api/audit.py`
- Demo: `CyberDemo/backend/src/demo/demo_api.py`
  - ejecucion de casos ancla y estado de demo

Como lo usa la interfaz:

- El cliente `CyberDemo/frontend/src/services/api.ts` encapsula llamadas por dominio (gen, assets, incidents, detections, timeline, postmortems, tickets, ctem, config, audit).
- La UI invoca estas funciones para poblar tablas, KPIs, detalles y acciones.

### 2.2 API del frontend para control por agente (MCP WebSocket)

Servidor: `CyberDemo/frontend/src/mcp/server.ts` (puerto 3001)

Tools de visualizacion (registro en `CyberDemo/frontend/src/mcp/tools/index.ts`):

1. `show_simulation`
2. `generate_chart`
3. `run_demo_scenario`
4. `get_demo_state`
5. `update_dashboard`
6. `show_alert_timeline`
7. `highlight_asset`
8. `show_postmortem`

Uso:

- El agente llama una tool MCP.
- La tool actualiza estado in-memory.
- El servidor hace broadcast a clientes React conectados para reflejar cambios en UI.

### 2.3 APIs MCP backend para operaciones SOC y datos sinteticos

MCP SOC:

- Servidor: `CyberDemo/backend/src/mcp/server.py`
- Endpoints JSON-RPC: `GET /mcp/health`, `POST /mcp/messages`, `GET /mcp/sse`
- Tools por dominio:
  - SIEM (`CyberDemo/backend/src/mcp/tools/siem.py`)
  - EDR (`CyberDemo/backend/src/mcp/tools/edr.py`)
  - Intel (`CyberDemo/backend/src/mcp/tools/intel.py`)
  - CTEM (`CyberDemo/backend/src/mcp/tools/ctem.py`)
  - Approvals (`CyberDemo/backend/src/mcp/tools/approvals.py`)
  - Tickets (`CyberDemo/backend/src/mcp/tools/tickets.py`)
  - Reports (`CyberDemo/backend/src/mcp/tools/reports.py`)

MCP de datos:

- Servidor: `CyberDemo/backend/src/mcp/data_server.py`
- Endpoints JSON-RPC: `GET /data-mcp/health`, `POST /data-mcp/messages`
- Tools de generacion:
  - `data_generate_assets`
  - `data_generate_edr_detections`
  - `data_generate_siem_incidents`
  - `data_generate_threat_intel`
  - `data_generate_ctem_findings`
  - `data_generate_all`
  - `data_reset`
  - `data_get_health`
- Implementacion: `CyberDemo/backend/src/mcp/data_tools/generators.py`

---

## 3) Programas Python generados (datos sinteticos, enrichment, escenarios y automatizacion)

### 3.1 Generacion de datos sinteticos

Ubicacion: `CyberDemo/backend/src/generators/`

- `gen_assets.py`: genera inventario de activos realista (tipos, hostnames, tags, red, owner, EDR, CTEM).
- `gen_edr.py`: genera detecciones EDR (MITRE, cmdline, hashes, severidad, usuarios).
- `gen_process_trees.py`: genera arboles de procesos para detecciones.
- `gen_siem.py`: correlaciona detecciones/intel/ctem en incidentes SIEM.
- `gen_intel.py`: genera IOCs (hash/IP/domain) con veredictos y fuentes.
- `gen_ctem.py`: genera hallazgos CVE y riesgo agregado por activo.
- `constants.py`: distribuciones, plantillas y valores semilla.

Como usar:

- Via API: endpoints `POST /gen/*`.
- Via MCP data: `data_generate_*`.
- Via flujo completo: `POST /gen/all` o `data_generate_all`.

### 3.2 Programas de enrichment (amenazas y vulnerabilidades)

Orquestacion:

- `CyberDemo/backend/src/services/enrichment_service.py`
  - limita lotes (max 100 por fuente),
  - maneja degradacion controlada,
  - usa circuit breaker y cache.
- Endpoint API: `CyberDemo/backend/src/api/enrichment.py`

Clientes externos (fuentes reales):

- `clients/nvd_client.py` (CVEs/CVSS)
- `clients/epss_client.py` (probabilidad de explotacion)
- `clients/otx_client.py` (threat intel IOC)
- `clients/abuseipdb_client.py` (reputacion IP)
- `clients/greynoise_client.py` (clasificacion de IP)

Generadores/simuladores de enrichment:

- `generators/enrichment/crowdstrike_mock.py` (sandbox report sintetico)
- `generators/enrichment/recorded_future_mock.py` (risk score sintetico)
- `generators/enrichment/tenable_mock.py` (VPR sintetico)

Como usar:

- Vulnerabilidades: `POST /api/vulnerabilities`
- Amenazas: `POST /api/threats`
- Estado de job: `GET /api/status/{job_id}`

### 3.3 Programas demo Python

- `CyberDemo/backend/src/demo/demo_runner.py`
  - orquesta los casos ancla de demo (incluyendo casos 4-6 avanzados).
- `CyberDemo/backend/src/demo/demo_api.py`
  - endpoints para ejecutar casos y consultar estado.
- Escenarios especializados:
  - `scenario_ransomware.py`
  - `scenario_insider_threat.py`
  - `scenario_supply_chain.py`

### 3.4 Automatizacion por triggers

Ubicacion: `CyberDemo/backend/src/triggers/`

- base y cliente gateway:
  - `base.py`, `gateway_client.py`
- familias de triggers:
  - `siem/` (creacion, escalado, SLA, correlacion, reopen)
  - `edr/` (detecciones severas, propagation, containment complete/failed/lifted)
  - `intel/` (IOC nuevo, score change, network match, feed)
  - `ctem/` (vuln critica, exploit, cambios de riesgo, VIP vuln)
  - `approvals/` (need/approved/rejected/timeout)
  - `reports/` (ticket/postmortem/incidente cerrado/resumen diario)
  - `system/` (health checks, alerta volumen, warning, opensearch down)

Uso:

- disparo de eventos backend -> evaluacion trigger -> accion/notificacion hacia gateway/canales.

---

## 4) Plugin con su skill, comandos, programas, APIs, hooks: que hace cada uno y como usarlo

### 4.1 Plugin CyberDemo SOC Analyst

Ubicacion: `extensions/cyberdemo/`

Archivo de configuracion: `extensions/cyberdemo/SoulInTheBot.plugin.json`

Incluye:

- ID: `cyberdemo-soc-analyst`
- Skill path: `./skills`
- MCP servers configurados:
  - `cyberdemo-api`
  - `cyberdemo-gen`
  - `cyberdemo-frontend`
- `configSchema` con:
  - `apiBaseUrl`
  - `autoContainmentEnabled`
  - `confidenceThresholdHigh`
  - `confidenceThresholdMedium`

Como usar:

```bash
moltbot extensions load extensions/cyberdemo
```

### 4.2 Skill `soc-analyst`

Archivo: `extensions/cyberdemo/skills/soc-analyst/SKILL.md`

Que hace:

- Define rol SOC Tier-1, workflow de investigacion y reglas operativas.
- Estandariza decisiones de contencion con policy engine y HITL para activos criticos.

Comandos definidos en la skill:

- `/investigate <incident_id>`
- `/demo <scenario>`
- `/demo_case_1`
- `/demo_case_2`
- `/demo_case_3`
- `/status`
- `/assets [filter]`
- `/pending`

Como usar:

- Ejecutar los comandos desde el canal de agente para recorrer investigacion o escenarios demo.

### 4.3 Programas TypeScript del plugin

Ubicacion: `extensions/cyberdemo/src/`

- `api-client.ts`: cliente tipado para dominios SIEM/EDR/Intel/CTEM/Approvals/Tickets/Reports.
- `confidence-score.ts`: calculo de score (intel, behavior, context, propagation).
- `policy-engine.ts`: reglas deterministas de decision (contain/request approval/false positive).
- `investigation-service.ts`: orquesta investigacion y cierre (ticket/postmortem).
- `demo-commands.ts`: escenarios demo preconfigurados (`INC-ANCHOR-001..003`).
- `hooks.ts`: hooks de ciclo de herramientas, aprobaciones, contencion, timeline y auditoria.
- `index.ts`: ensamblado e inicializacion (`initializePlugin`).

### 4.4 Hooks creados

Archivo: `extensions/cyberdemo/src/hooks.ts`

Hooks principales:

- `onToolStart`: log de inicio + notificacion frontend.
- `onToolComplete`: actualizacion timeline + notificacion frontend.
- `onContainment`: verificacion de politica + audit log + notificacion de canal.
- `onApprovalReceived`: reanudacion de workflow + actualizacion de incidente.
- `onInvestigationStart`: inicia estado de workflow y traza.
- `onInvestigationComplete`: cierre de workflow, auditoria y notificacion final.

Handlers de comandos demo:

- `handleDemoCase1`
- `handleDemoCase2`
- `handleDemoCase3`

Como se usan:

- Se crean por `createHooks(...)` y `createCommandHandlers(...)` durante `initializePlugin(...)`.
- Se conectan al flujo del gateway/agente para trazar y sincronizar acciones.

### 4.5 APIs consumidas por el plugin

- REST backend via `CyberDemoApiClient` (incidentes, detecciones, intel, ctem, approvals, tickets, reportes).
- MCP servers definidos en manifest para operaciones SOC, generacion y visualizacion.

### 4.6 Tests del plugin

Ubicacion: `extensions/cyberdemo/tests/`

- Unitarios:
  - `unit/api-client.test.ts`
  - `unit/confidence-score.test.ts`
  - `unit/policy-engine.test.ts`
- Integracion:
  - `integration/investigation-flow.test.ts`
- E2E:
  - `e2e/skill-integration.test.ts`
  - `e2e/scenarios.test.ts`

---

## 5) Interfaz grafica hecha para el skill y funcionalidades especificas

La UI que consume el skill no es una pantalla aislada, sino un conjunto coordinado de vistas y tools MCP:

- Estado y contexto: `DashboardPage`, `IncidentsPage`, `TimelinePage`.
- Evidencia tecnica: `DetectionsPage`, `GraphPage`, `CTEMPage`.
- Cierre operativo: `TicketsPage`, `PostmortemsPage`.
- Asistencia en vivo: `CollabPage`.

Control directo desde el skill/agente:

- `run_demo_scenario`: inicia escenario y mueve vista a dashboard.
- `show_alert_timeline`: cambia a timeline con incidente y alertas.
- `highlight_asset`: resalta activo en grafo.
- `show_postmortem`: cambia a vista postmortem.
- `update_dashboard` y `generate_chart`: refresco visual de KPIs/charts.
- `get_demo_state`: inspeccion del estado en tiempo real.

Ventaja:

- El analista/operador puede ver inmediatamente el efecto de cada decision del agente sin cambiar de herramienta.

---

## 6) Otros elementos construidos para CyberDemo (13 hasta hoy)

Basado en evidencia de `CyberDemo/docs/PROGRESS.md`, `CyberDemo/docs/PROGRESS_CONSTRUCCION.md` y estado actual de archivos:

### 6.1 Infra y operacion

- `CyberDemo/backend/src/main.py` (arranque FastAPI, DB/OpenSearch, CORS)
- `CyberDemo/docker/docker-compose.yml` (orquestacion local)
- `CyberDemo/scripts/demo-setup.sh` (setup guiado de demo)
- `CyberDemo/start.sh` (arranque completo del entorno, usado en guias)

### 6.2 Playbooks y notificaciones

- Playbooks YAML:
  - `backend/playbooks/contain_and_investigate.yaml`
  - `backend/playbooks/ransomware_response.yaml`
  - `backend/playbooks/vip_escalation.yaml`
  - `backend/playbooks/lateral_movement_hunt.yaml`
  - `backend/playbooks/false_positive_closure.yaml`
- Plantillas de notificacion:
  - `backend/src/templates/notifications/slack_approval.json`
  - `backend/src/templates/notifications/slack_containment.json`
  - `backend/src/templates/notifications/teams_alert.json`

### 6.3 Datos y observabilidad

- OpenSearch dashboards y contenido de soporte:
  - `CyberDemo/opensearch/dashboards/README.md`
- Servicios de grafo y auditoria:
  - `backend/src/services/graph_service.py`
  - `backend/src/services/audit_service.py`

### 6.4 Testing adicional relevante

- Frontend:
  - `frontend/tests/mcp-server.spec.ts`
  - `frontend/tests/enrichment.spec.ts`
  - `frontend/tests/graph.spec.ts`
  - `frontend/tests/postmortems-features.spec.tsx`
- Backend:
  - `backend/tests/e2e/test_mcp_integration.py`
  - `backend/tests/e2e/test_scenario_vip_approval.py`
  - `backend/tests/e2e/test_scenario_false_positive.py`
  - tests unitarios de services/enrichment/generators/notificaciones/collab/playbooks.

---

## 7) Verificacion de cobertura del documento (revision final y elementos anadidos)

Tras revisar de nuevo codigo + docs, se validaron y anadieron explicitamente estos items para evitar huecos:

1. Triggers W12 por dominio (`backend/src/triggers/**`).
2. Demo avanzado de casos 4-6 (`demo_runner.py` + escenarios dedicados).
3. APIs de colaboracion, configuracion, auditoria, playbooks y notificaciones.
4. Distincion entre MCP backend (`/mcp/messages`) y MCP data (`/data-mcp/messages`).
5. Tools MCP frontend exactas (8) y su funcion concreta sobre estado UI.
6. Playbooks YAML y templates de notificaciones como artefactos operativos del demo.
7. Suite de tests de frontend/backend/plugin como parte del producto construido.

Con esto, el documento cubre: UI, APIs, Python (generacion+enrichment+demo), plugin+skill+comandos+hooks, interfaz del skill y elementos adicionales del periodo 13-hoy.
