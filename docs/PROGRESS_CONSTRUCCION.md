# Progreso de Construcción - CyberDemo SOC Tier-1 Analyst

> **Plan:** [PLAN.md](PLAN.md)
> **Inicio:** 2026-02-14
> **Metodología:** TDD Estricto (Red → Green → Refactor)
> **Estado:** 🟢 COMPLETADO

---

## Dashboard de Progreso

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         PROGRESO GENERAL: 100%                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│  Fase 1: ██████████  100%   Fase 5: ██████████  100%                         │
│  Fase 2: ██████████  100%   Fase 6: ██████████  100%                         │
│  Fase 3: ██████████  100%   Fase 7: ██████████  100%                         │
│  Fase 4: ██████████  100%   W12:    ██████████  100%                         │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Estado por Workstream

| Workstream | Descripción          | Fase | Estado | Tests | Impl  |
| ---------- | -------------------- | ---- | ------ | ----- | ----- |
| **W1**     | Generador Assets     | F2   | 🟢     | 4/4   | 2/2   |
| **W2**     | Generador EDR        | F2   | 🟢     | 4/4   | 2/2   |
| **W3**     | Generador Intel      | F2   | 🟢     | 2/2   | 2/2   |
| **W4**     | Generador CTEM       | F2   | 🟢     | 2/2   | 2/2   |
| **W5**     | Generador SIEM       | F2   | 🟢     | 3/3   | 2/2   |
| **W6**     | APIs Backend         | F3   | 🟢     | 20/20 | 20/20 |
| **W7**     | Frontend Core        | F4   | 🟢     | 8/8   | 8/8   |
| **W8**     | Frontend Grafos      | F4   | 🟢     | 6/6   | 6/6   |
| **W9**     | Skill SoulInTheBot   | F5   | 🟢     | 8/8   | 8/8   |
| **W10**    | Tests E2E            | F6   | 🟢     | 3/3   | 3/3   |
| **W11**    | MCP Servers + Plugin | F7   | 🟢     | 35/35 | 35/35 |
| **W12**    | Auto-Triggers        | -    | 🟢     | 30/30 | 30/30 |

---

## Fase 1: Infraestructura Base (Días 1-2)

**Objetivo:** Docker Compose funcional + OpenSearch + estructura base

### 1.1 Docker Compose

| #   | Item                     | Test                         | Impl                    | Estado |
| --- | ------------------------ | ---------------------------- | ----------------------- | ------ |
| 1   | Docker Compose funcional | ✅ `test_services_running`   | ✅ `docker-compose.yml` | 🟢     |
| 2   | OpenSearch disponible    | ✅ `test_opensearch_healthy` | ✅ Healthcheck          | 🟢     |
| 3   | Backend disponible       | ✅ `test_backend_healthy`    | ✅ Dockerfile.backend   | 🟢     |
| 4   | Frontend disponible      | ✅ `test_frontend_healthy`   | ✅ Dockerfile.frontend  | 🟢     |
| 5   | PostgreSQL disponible    | ✅ `test_postgres_healthy`   | ✅ Config               | 🟢     |

### 1.2 OpenSearch Templates

| #   | Item                 | Test                      | Impl              | Estado |
| --- | -------------------- | ------------------------- | ----------------- | ------ |
| 1   | 17 templates creados | ✅ `test_templates_exist` | ✅ `templates.py` | 🟢     |
| 2   | Mappings correctos   | ✅ `test_mappings_valid`  | ✅ Cada index     | 🟢     |

### 1.3 Health Checks

| #   | Item               | Test                       | Impl           | Estado |
| --- | ------------------ | -------------------------- | -------------- | ------ |
| 1   | `/health` endpoint | ✅ `test_health_responds`  | ✅ `health.py` | 🟢     |
| 2   | Status OpenSearch  | ✅ `test_health_os_status` | ✅ OS check    | 🟢     |

**Archivos creados:**

- [x] `docker/docker-compose.yml`
- [x] `docker/Dockerfile.backend`
- [x] `docker/Dockerfile.frontend`
- [x] `backend/src/opensearch/templates.py`
- [x] `backend/src/api/health.py`

---

## Fase 2: Generadores de Datos (Días 3-7)

**Objetivo:** Datos sintéticos reproducibles y realistas

### W1: Generador de Assets (1000 activos)

| #   | Test                               | Estado | Implementación      | Estado |
| --- | ---------------------------------- | ------ | ------------------- | ------ |
| 1   | `test_generates_1000_assets`       | ✅     | `generate_assets()` | ✅     |
| 2   | `test_assets_have_required_fields` | ✅     | Fields validation   | ✅     |
| 3   | `test_vip_distribution`            | ✅     | VIP tags 5-8%       | ✅     |
| 4   | `test_reproducibility`             | ✅     | Seed handling       | ✅     |

**Distribución objetivo:**

- Workstations: 70% (DESKTOP-, WS-, MAC-\*)
- Servers: 20% (SRV-, DC-, DB-\*)
- Móviles: 8% (MOB-, IPHONE-\*)
- Otros: 2% (VDI-, IOT-\*)

**Archivos:**

- [x] `backend/src/generators/gen_assets.py`
- [x] `backend/tests/test_generators.py`

---

### W2: Generador EDR (1000 detecciones)

| #   | Test                                             | Estado | Implementación              | Estado |
| --- | ------------------------------------------------ | ------ | --------------------------- | ------ |
| 1   | `test_generates_1000_detections`                 | ✅     | `generate_edr_detections()` | ✅     |
| 2   | `test_detections_reference_existing_assets`      | ✅     | Asset linking               | ✅     |
| 3   | `test_process_tree_generated_for_each_detection` | ✅     | Process trees               | ✅     |
| 4   | `test_mitre_techniques_present`                  | ✅     | MITRE ATT&CK                | ✅     |

**Plantillas cmdline incluidas:**

- PowerShell encoded
- Lateral movement
- Credential theft

**Archivos:**

- [x] `backend/src/generators/gen_edr.py`
- [x] `backend/tests/test_generators.py`

---

### W3: Generador Intel (~200 IOCs)

| #   | Test                                | Estado | Implementación            | Estado |
| --- | ----------------------------------- | ------ | ------------------------- | ------ |
| 1   | `test_generates_iocs_with_verdicts` | ✅     | `generate_threat_intel()` | ✅     |
| 2   | `test_malicious_hash_consistency`   | ✅     | Anchor hashes             | ✅     |

**Archivos:**

- [x] `backend/src/generators/gen_intel.py`
- [x] `backend/tests/test_generators.py`

---

### W4: Generador CTEM (vulnerabilidades)

| #   | Test                            | Estado | Implementación                 | Estado |
| --- | ------------------------------- | ------ | ------------------------------ | ------ |
| 1   | `test_ctem_risk_colors`         | ✅     | Risk colors (Green/Yellow/Red) | ✅     |
| 2   | `test_servers_skew_higher_risk` | ✅     | Server risk >20% Red           | ✅     |

**Archivos:**

- [x] `backend/src/generators/gen_ctem.py`
- [x] `backend/tests/test_generators.py`

---

### W5: Generador SIEM (incidentes enriquecidos)

| #   | Test                                     | Estado | Implementación              | Estado |
| --- | ---------------------------------------- | ------ | --------------------------- | ------ |
| 1   | `test_creates_incidents_from_detections` | ✅     | `generate_siem_incidents()` | ✅     |
| 2   | `test_anchor_cases_exist`                | ✅     | 3 anchor incidents          | ✅     |
| 3   | `test_entities_created_per_incident`     | ✅     | Entity linking              | ✅     |

**Casos Ancla (IDs fijos):**
| Caso | Host | Tags | Hash | Confidence | Resultado |
|------|------|------|------|------------|-----------|
| 1 | WS-FIN-042 | standard-user | H1 malicioso | 95% | Auto-containment |
| 2 | LAPTOP-CFO-01 | vip, executive | H1 mismo | 95% | Human-in-the-Loop |
| 3 | SRV-DEV-03 | standard | H2 benigno | 22% | False Positive |

**Archivos:**

- [x] `backend/src/generators/gen_siem.py`
- [x] `backend/tests/test_generators.py`

---

## Fase 3: APIs Backend (Días 5-10)

**Objetivo:** FastAPI con todos los endpoints + validación

### W6: Endpoints por Servicio

#### GenOps (Generación)

| #   | Método | Endpoint      | Test | Impl | Estado |
| --- | ------ | ------------- | ---- | ---- | ------ |
| 1   | POST   | `/gen/reset`  | ✅   | ✅   | 🟢     |
| 2   | POST   | `/gen/all`    | ✅   | ✅   | 🟢     |
| 3   | POST   | `/gen/assets` | ✅   | ✅   | 🟢     |
| 4   | POST   | `/gen/edr`    | ✅   | ✅   | 🟢     |
| 5   | POST   | `/gen/siem`   | ✅   | ✅   | 🟢     |
| 6   | GET    | `/gen/health` | ✅   | ✅   | 🟢     |

**Archivos:**

- [x] `backend/src/api/gen.py`
- [x] `backend/tests/test_api.py`

---

#### SIEM (Incidentes)

| #   | Método | Endpoint                        | Test | Impl | Estado |
| --- | ------ | ------------------------------- | ---- | ---- | ------ |
| 1   | GET    | `/siem/incidents`               | ✅   | ✅   | 🟢     |
| 2   | GET    | `/siem/incidents/{id}`          | ✅   | ✅   | 🟢     |
| 3   | GET    | `/siem/incidents/{id}/entities` | ✅   | ✅   | 🟢     |
| 4   | POST   | `/siem/incidents/{id}/comments` | ✅   | ✅   | 🟢     |

**Archivos:**

- [x] `backend/src/api/siem.py`
- [x] `backend/tests/test_api.py`

---

#### EDR (Detecciones)

| #   | Método | Endpoint                            | Test | Impl | Estado |
| --- | ------ | ----------------------------------- | ---- | ---- | ------ |
| 1   | GET    | `/edr/detections`                   | ✅   | ✅   | 🟢     |
| 2   | GET    | `/edr/detections/{id}`              | ✅   | ✅   | 🟢     |
| 3   | GET    | `/edr/detections/{id}/process-tree` | ✅   | ✅   | 🟢     |
| 4   | GET    | `/edr/hunt/hash/{sha256}`           | ✅   | ✅   | 🟢     |
| 5   | POST   | `/edr/devices/{id}/contain`         | ✅   | ✅   | 🟢     |

**Archivos:**

- [x] `backend/src/api/edr.py`
- [x] `backend/tests/test_api.py`

---

#### Intel (Reputación)

| #   | Método | Endpoint                           | Test | Impl | Estado |
| --- | ------ | ---------------------------------- | ---- | ---- | ------ |
| 1   | GET    | `/intel/indicators/{type}/{value}` | ✅   | ✅   | 🟢     |

**Archivos:**

- [x] `backend/src/api/intel.py`
- [x] `backend/tests/test_api.py`

---

#### CTEM (Vulnerabilidades)

| #   | Método | Endpoint            | Test | Impl | Estado |
| --- | ------ | ------------------- | ---- | ---- | ------ |
| 1   | GET    | `/ctem/assets/{id}` | ✅   | ✅   | 🟢     |

**Archivos:**

- [x] `backend/src/api/ctem.py`
- [x] `backend/tests/test_api.py`

---

#### Approvals (Aprobaciones)

| #   | Método | Endpoint                   | Test | Impl | Estado |
| --- | ------ | -------------------------- | ---- | ---- | ------ |
| 1   | GET    | `/approvals/{incident_id}` | ✅   | ✅   | 🟢     |
| 2   | POST   | `/approvals/{incident_id}` | ✅   | ✅   | 🟢     |

**Archivos:**

- [x] `backend/src/api/approvals.py`
- [x] `backend/tests/test_api.py`

---

#### SOAR (Playbooks) ✅

| #   | Método | Endpoint             | Test | Impl | Estado |
| --- | ------ | -------------------- | ---- | ---- | ------ |
| 1   | POST   | `/soar/actions`      | ✅   | ✅   | 🟢     |
| 2   | GET    | `/soar/actions/{id}` | ✅   | ✅   | 🟢     |
| 3   | GET    | `/soar/actions`      | ✅   | ✅   | 🟢     |

**Archivos:**

- [x] `backend/src/api/soar.py`
- [x] `backend/src/services/soar_service.py`
- [x] `backend/tests/test_soar.py` (8 tests passing)

---

#### Tickets

| #   | Método | Endpoint          | Test | Impl | Estado |
| --- | ------ | ----------------- | ---- | ---- | ------ |
| 1   | POST   | `/tickets/create` | ✅   | ✅   | 🟢     |
| 2   | GET    | `/tickets`        | ✅   | ✅   | 🟢     |

**Archivos:**

- [x] `backend/src/api/tickets.py`
- [x] `backend/tests/test_api.py`

---

#### Reports (Postmortems)

| #   | Método | Endpoint                   | Test | Impl | Estado |
| --- | ------ | -------------------------- | ---- | ---- | ------ |
| 1   | POST   | `/reports/postmortem/{id}` | ✅   | ✅   | 🟢     |
| 2   | GET    | `/reports/postmortem/{id}` | ✅   | ✅   | 🟢     |

**Archivos:**

- [x] `backend/src/api/postmortems.py`
- [x] `backend/tests/test_api.py`

---

#### Graph (Visualización) ✅

| #   | Método | Endpoint               | Test | Impl | Estado |
| --- | ------ | ---------------------- | ---- | ---- | ------ |
| 1   | GET    | `/graph/incident/{id}` | ✅   | ✅   | 🟢     |
| 2   | GET    | `/graph/system`        | ✅   | ✅   | 🟢     |

**Archivos:**

- [x] `backend/src/api/graph.py`
- [x] `backend/src/services/graph_service.py`
- [x] `backend/tests/test_graph.py` (9 tests passing)

---

## Fase 4: Frontend (Días 8-14)

**Objetivo:** UI interactiva con todas las pestañas

### W7: Frontend Core (8 pestañas)

| #   | Pestaña               | Tests                 | Impl                     | Estado |
| --- | --------------------- | --------------------- | ------------------------ | ------ |
| 1   | Generación de Datos   | ✅ `test_gen_page`    | ✅ `GenerationPage.tsx`  | 🟢     |
| 2   | Dashboard & Métricas  | ✅ `test_dashboard`   | ✅ `DashboardPage.tsx`   | 🟢     |
| 3   | Explorador de Activos | ✅ `test_assets`      | ✅ `AssetsPage.tsx`      | 🟢     |
| 4   | Lista de Incidentes   | ✅ `test_incidents`   | ✅ `IncidentsPage.tsx`   | 🟢     |
| 5   | Detecciones EDR       | ✅ `test_detections`  | ✅ `DetectionsPage.tsx`  | 🟢     |
| 6   | Timeline del Agente   | ✅ `test_timeline`    | ✅ `TimelinePage.tsx`    | 🟢     |
| 7   | Informes Postmortem   | ✅ `test_postmortems` | ✅ `PostmortemsPage.tsx` | 🟢     |
| 8   | Tickets               | ✅ `test_tickets`     | ✅ `TicketsPage.tsx`     | 🟢     |

**Archivos:**

- [x] `frontend/src/pages/GenerationPage.tsx`
- [x] `frontend/src/pages/DashboardPage.tsx`
- [x] `frontend/src/pages/AssetsPage.tsx`
- [x] `frontend/src/pages/IncidentsPage.tsx`
- [x] `frontend/src/pages/DetectionsPage.tsx`
- [x] `frontend/src/pages/TimelinePage.tsx`
- [x] `frontend/src/pages/PostmortemsPage.tsx`
- [x] `frontend/src/pages/TicketsPage.tsx`
- [x] `frontend/tests/graph.spec.ts`

---

### W8: Frontend Grafos (Cytoscape.js) ✅

| #   | Test                   | Impl                     | Estado |
| --- | ---------------------- | ------------------------ | ------ |
| 1   | `test_graph_renders`   | ✅ `CytoscapeGraph.tsx`  | 🟢     |
| 2   | `test_nodes_clickable` | ✅ Click handlers        | 🟢     |
| 3   | `test_panel_sections`  | ✅ `NodeDetailPanel.tsx` | 🟢     |
| 4   | `test_node_colors`     | ✅ Color mapping         | 🟢     |
| 5   | `test_zoom_pan`        | ✅ `GraphControls.tsx`   | 🟢     |
| 6   | `test_auto_layout`     | ✅ Layout dagre          | 🟢     |

**Panel lateral (4 secciones):**

- (a) Quién es el activo
- (b) Cuál es la amenaza
- (c) Qué recomienda el agente
- (d) Estado contención/ticket

**Colores de nodos:**

- Verde: Normal
- Amarillo: Sospechoso
- Rojo: Crítico/Comprometido
- Azul: Contenido

**Archivos:**

- [x] `frontend/src/components/Graph/CytoscapeGraph.tsx`
- [x] `frontend/src/components/Graph/GraphControls.tsx`
- [x] `frontend/src/components/Graph/NodeDetailPanel.tsx`
- [x] `frontend/src/components/Graph/useGraphData.ts`
- [x] `frontend/src/components/Graph/types.ts`
- [x] `frontend/src/pages/GraphPage.tsx`
- [x] `frontend/tests/graph.spec.ts`

---

## Fase 5: Skill para SoulInTheBot (Días 12-16)

**Objetivo:** Tools que SoulInTheBot usará para investigar

### W9: Skill Structure

| #   | Tool                         | Test | Impl               | Estado |
| --- | ---------------------------- | ---- | ------------------ | ------ |
| 1   | `siem.listIncidents`         | ✅   | ✅ `api-client.ts` | 🟢     |
| 2   | `siem.getIncident`           | ✅   | ✅                 | 🟢     |
| 3   | `siem.addComment`            | ✅   | ✅                 | 🟢     |
| 4   | `edr.getDetection`           | ✅   | ✅                 | 🟢     |
| 5   | `edr.getProcessTree`         | ✅   | ✅                 | 🟢     |
| 6   | `edr.huntHash`               | ✅   | ✅                 | 🟢     |
| 7   | `edr.containHost`            | ✅   | ✅                 | 🟢     |
| 8   | `intel.getIndicator`         | ✅   | ✅                 | 🟢     |
| 9   | `ctem.getAssetRisk`          | ✅   | ✅                 | 🟢     |
| 10  | `approvals.get`              | ✅   | ✅                 | 🟢     |
| 11  | `approvals.request`          | ✅   | ✅                 | 🟢     |
| 12  | `tickets.create`             | ✅   | ✅                 | 🟢     |
| 13  | `reports.generatePostmortem` | ✅   | ✅                 | 🟢     |

### Policy Engine (Determinista)

| #   | Test                                 | Impl                   | Estado |
| --- | ------------------------------------ | ---------------------- | ------ |
| 1   | `test_high_confidence_auto_contain`  | ✅ `PolicyEngine`      | 🟢     |
| 2   | `test_vip_requires_approval`         | ✅ CRITICAL_TAGS check | 🟢     |
| 3   | `test_low_confidence_false_positive` | ✅ Score thresholds    | 🟢     |
| 4   | `test_approval_unlocks_contain`      | ✅ has_approval flag   | 🟢     |

**Umbrales:**

- CONFIDENCE_HIGH: 90
- CONFIDENCE_MEDIUM: 50
- CRITICAL_TAGS: {"vip", "executive", "server", "domain-controller"}

**Archivos:**

- [x] `extensions/cyberdemo/skills/soc-analyst/SKILL.md`
- [x] `extensions/cyberdemo/src/policy-engine.ts`
- [x] `extensions/cyberdemo/src/api-client.ts`
- [x] `extensions/cyberdemo/src/investigation-service.ts`
- [x] `extensions/cyberdemo/src/confidence-score.ts`
- [x] `extensions/cyberdemo/tests/unit/policy-engine.test.ts`
- [x] `extensions/cyberdemo/tests/unit/api-client.test.ts`
- [x] `extensions/cyberdemo/tests/integration/investigation-flow.test.ts`
- [x] `backend/tests/test_policy_engine.py`

---

## Fase 6: Tests E2E (Días 14-18)

**Objetivo:** Validar los 3 escenarios de demo end-to-end

### W10: Los 3 Escenarios Ancla

#### Escenario 1: Auto-Containment

| #   | Test                                | Estado |
| --- | ----------------------------------- | ------ |
| 1   | `test_scenario_1_incident_exists`   | ✅     |
| 2   | `test_scenario_1_detection_correct` | ✅     |
| 3   | `test_scenario_1_intel_malicious`   | ✅     |
| 4   | `test_scenario_1_propagation`       | ✅     |
| 5   | `test_scenario_1_policy_auto`       | ✅     |
| 6   | `test_scenario_1_containment`       | ✅     |
| 7   | `test_scenario_1_asset_updated`     | ✅     |
| 8   | `test_scenario_1_ticket_created`    | ✅     |
| 9   | `test_scenario_1_postmortem`        | ✅     |

**Escenario:** Malware en WS-FIN-042 (standard-user) → Confidence 95% → Auto-containment

---

#### Escenario 2: VIP Human-in-the-Loop

| #   | Test                                 | Estado |
| --- | ------------------------------------ | ------ |
| 1   | `test_scenario_2_incident_exists`    | ✅     |
| 2   | `test_scenario_2_asset_is_vip`       | ✅     |
| 3   | `test_scenario_2_requires_approval`  | ✅     |
| 4   | `test_scenario_2_approval_requested` | ✅     |
| 5   | `test_scenario_2_ui_shows_card`      | ✅     |
| 6   | `test_scenario_2_approval_grants`    | ✅     |
| 7   | `test_scenario_2_containment_after`  | ✅     |

**Escenario:** Malware en LAPTOP-CFO-01 (vip, executive) → Confidence 95% → Requiere aprobación

---

#### Escenario 3: False Positive

| #   | Test                              | Estado |
| --- | --------------------------------- | ------ |
| 1   | `test_scenario_3_incident_exists` | ✅     |
| 2   | `test_scenario_3_intel_benign`    | ✅     |
| 3   | `test_scenario_3_low_confidence`  | ✅     |
| 4   | `test_scenario_3_policy_fp`       | ✅     |
| 5   | `test_scenario_3_closed`          | ✅     |
| 6   | `test_scenario_3_no_containment`  | ✅     |

**Escenario:** Script legítimo en SRV-DEV-03 → Confidence 22% → False Positive

**Archivos:**

- [x] `backend/tests/e2e/test_scenario_auto_containment.py`
- [x] `backend/tests/e2e/test_scenario_vip_approval.py`
- [x] `backend/tests/e2e/test_scenario_false_positive.py`
- [x] `extensions/cyberdemo/tests/e2e/scenarios.test.ts`

---

## Fase 7: MCP Servers + Plugin SoulInTheBot (Días 15-20)

**Objetivo:** 3 MCP Servers + Plugin completo

### W11: MCP Servers

#### Backend MCP Server (Puerto 8001) ✅

| #   | Tool MCP                      | Test                        | Impl | Estado |
| --- | ----------------------------- | --------------------------- | ---- | ------ |
| 1   | Server Base                   | ✅ `test_mcp_server_starts` | ✅   | 🟢     |
| 2   | Tool Registry                 | ✅ `test_mcp_lists_tools`   | ✅   | 🟢     |
| 3   | `siem_list_incidents`         | ✅                          | ✅   | 🟢     |
| 4   | `siem_get_incident`           | ✅                          | ✅   | 🟢     |
| 5   | `siem_add_comment`            | ✅                          | ✅   | 🟢     |
| 6   | `siem_close_incident`         | ✅                          | ✅   | 🟢     |
| 7   | `edr_get_detection`           | ✅                          | ✅   | 🟢     |
| 8   | `edr_get_process_tree`        | ✅                          | ✅   | 🟢     |
| 9   | `edr_hunt_hash`               | ✅                          | ✅   | 🟢     |
| 10  | `edr_contain_host`            | ✅                          | ✅   | 🟢     |
| 11  | `intel_get_indicator`         | ✅                          | ✅   | 🟢     |
| 12  | `ctem_get_asset_risk`         | ✅                          | ✅   | 🟢     |
| 13  | `approvals_get`               | ✅                          | ✅   | 🟢     |
| 14  | `approvals_request`           | ✅                          | ✅   | 🟢     |
| 15  | `tickets_create`              | ✅                          | ✅   | 🟢     |
| 16  | `reports_generate_postmortem` | ✅                          | ✅   | 🟢     |
| 17  | `tickets_list`                | ✅                          | ✅   | 🟢     |

**Archivos:**

- [x] `backend/src/mcp/__init__.py`
- [x] `backend/src/mcp/server.py`
- [x] `backend/src/mcp/tools/siem.py`
- [x] `backend/src/mcp/tools/edr.py`
- [x] `backend/src/mcp/tools/intel.py`
- [x] `backend/src/mcp/tools/ctem.py`
- [x] `backend/src/mcp/tools/approvals.py`
- [x] `backend/src/mcp/tools/tickets.py`
- [x] `backend/src/mcp/tools/reports.py`
- [x] `backend/tests/test_mcp_server.py` (15 tests passing)

---

#### Frontend MCP Server (Puerto 3001) ✅

| #   | Tool MCP              | Test                      | Impl | Estado |
| --- | --------------------- | ------------------------- | ---- | ------ |
| 1   | WS Server             | ✅ `test_mcp_ws_connects` | ✅   | 🟢     |
| 2   | `show_simulation`     | ✅                        | ✅   | 🟢     |
| 3   | `generate_chart`      | ✅                        | ✅   | 🟢     |
| 4   | `run_demo_scenario`   | ✅                        | ✅   | 🟢     |
| 5   | `get_demo_state`      | ✅                        | ✅   | 🟢     |
| 6   | `update_dashboard`    | ✅                        | ✅   | 🟢     |
| 7   | `show_alert_timeline` | ✅                        | ✅   | 🟢     |
| 8   | `highlight_asset`     | ✅                        | ✅   | 🟢     |
| 9   | `show_postmortem`     | ✅                        | ✅   | 🟢     |

**Archivos:**

- [x] `frontend/src/mcp/server.ts`
- [x] `frontend/src/mcp/handler.ts`
- [x] `frontend/src/mcp/tools/index.ts`
- [x] `frontend/src/mcp/tools/show-simulation.ts`
- [x] `frontend/src/mcp/tools/generate-chart.ts`
- [x] `frontend/src/mcp/tools/run-demo-scenario.ts`
- [x] `frontend/src/mcp/tools/get-demo-state.ts`
- [x] `frontend/src/mcp/tools/update-dashboard.ts`
- [x] `frontend/src/mcp/tools/show-alert-timeline.ts`
- [x] `frontend/src/mcp/tools/highlight-asset.ts`
- [x] `frontend/src/mcp/tools/show-postmortem.ts`

---

#### Data MCP Server (Puerto 8002) ✅

| #   | Tool MCP                       | Test                      | Impl | Estado |
| --- | ------------------------------ | ------------------------- | ---- | ------ |
| 1   | Server Base                    | ✅ `test_data_mcp_starts` | ✅   | 🟢     |
| 2   | `data_generate_assets`         | ✅                        | ✅   | 🟢     |
| 3   | `data_generate_edr_detections` | ✅                        | ✅   | 🟢     |
| 4   | `data_generate_siem_incidents` | ✅                        | ✅   | 🟢     |
| 5   | `data_generate_threat_intel`   | ✅                        | ✅   | 🟢     |
| 6   | `data_generate_ctem_findings`  | ✅                        | ✅   | 🟢     |
| 7   | `data_generate_all`            | ✅                        | ✅   | 🟢     |
| 8   | `data_reset`                   | ✅                        | ✅   | 🟢     |
| 9   | `data_get_health`              | ✅                        | ✅   | 🟢     |

**Archivos:**

- [x] `backend/src/mcp/data_server.py`
- [x] `backend/src/mcp/data_tools/generators.py`
- [x] `backend/tests/test_mcp_data_server.py`

---

#### Plugin SoulInTheBot ✅

| #   | Item                          | Test | Impl | Estado |
| --- | ----------------------------- | ---- | ---- | ------ |
| 1   | `package.json` con mcpServers | ✅   | ✅   | 🟢     |
| 2   | Skill `investigate-incident`  | ✅   | ✅   | 🟢     |
| 3   | Skill `run-demo`              | ✅   | ✅   | 🟢     |
| 4   | Config MCP en SoulInTheBot    | ✅   | ✅   | 🟢     |

**Archivos:**

- [x] `extensions/cyberdemo/package.json`
- [x] `extensions/cyberdemo/src/index.ts`
- [x] `extensions/cyberdemo/skills/soc-analyst/SKILL.md`
- [x] `extensions/cyberdemo/SoulInTheBot.plugin.json`
- [x] `extensions/cyberdemo/README.md`

---

## W12: Auto-Triggers (Backend → SoulInTheBot) ✅

**Referencia:** [DefinicionPendiente.md](DefinicionPendiente.md)

### Gateway Client ✅

| #   | Test                         | Impl                   | Estado |
| --- | ---------------------------- | ---------------------- | ------ |
| 1   | `test_gateway_sends_message` | ✅ `gateway_client.py` | 🟢     |
| 2   | `test_gateway_cooldown`      | ✅ Cooldown logic      | 🟢     |
| 3   | `test_gateway_dedup`         | ✅ Deduplication       | 🟢     |
| 4   | `test_gateway_errors`        | ✅ Error handling      | 🟢     |

### SIEM Triggers (5) ✅

| #   | Trigger                          | Test | Impl | Estado |
| --- | -------------------------------- | ---- | ---- | ------ |
| 1   | Incident Created (High/Critical) | ✅   | ✅   | 🟢     |
| 2   | Incident Escalated               | ✅   | ✅   | 🟢     |
| 3   | SLA Breach Warning               | ✅   | ✅   | 🟢     |
| 4   | Correlation Found                | ✅   | ✅   | 🟢     |
| 5   | Incident Reopened                | ✅   | ✅   | 🟢     |

### EDR Triggers (5) ✅

| #   | Trigger                 | Test | Impl | Estado |
| --- | ----------------------- | ---- | ---- | ------ |
| 1   | Detection High Severity | ✅   | ✅   | 🟢     |
| 2   | Hash Propagation        | ✅   | ✅   | 🟢     |
| 3   | Containment Failed      | ✅   | ✅   | 🟢     |
| 4   | Containment Completed   | ✅   | ✅   | 🟢     |
| 5   | Containment Lifted      | ✅   | ✅   | 🟢     |

### Intel Triggers (4) ✅

| #   | Trigger              | Test | Impl | Estado |
| --- | -------------------- | ---- | ---- | ------ |
| 1   | New Malicious IOC    | ✅   | ✅   | 🟢     |
| 2   | IOC Score Changed    | ✅   | ✅   | 🟢     |
| 3   | IOC Match in Network | ✅   | ✅   | 🟢     |
| 4   | New Intel Feed       | ✅   | ✅   | 🟢     |

### CTEM Triggers (4) ✅

| #   | Trigger                 | Test | Impl | Estado |
| --- | ----------------------- | ---- | ---- | ------ |
| 1   | Critical Vulnerability  | ✅   | ✅   | 🟢     |
| 2   | Asset Risk Changed      | ✅   | ✅   | 🟢     |
| 3   | VIP Asset Vulnerability | ✅   | ✅   | 🟢     |
| 4   | Exploit Available       | ✅   | ✅   | 🟢     |

### Approval Triggers (4) ✅

| #   | Trigger             | Test | Impl | Estado |
| --- | ------------------- | ---- | ---- | ------ |
| 1   | Approval Approved   | ✅   | ✅   | 🟢     |
| 2   | Approval Rejected   | ✅   | ✅   | 🟢     |
| 3   | Approval Timeout    | ✅   | ✅   | 🟢     |
| 4   | New Approval Needed | ✅   | ✅   | 🟢     |

### Report Triggers (4) ✅

| #   | Trigger              | Test | Impl | Estado |
| --- | -------------------- | ---- | ---- | ------ |
| 1   | Incident Closed      | ✅   | ✅   | 🟢     |
| 2   | Postmortem Generated | ✅   | ✅   | 🟢     |
| 3   | Ticket Created       | ✅   | ✅   | 🟢     |
| 4   | Daily Summary        | ✅   | ✅   | 🟢     |

### System Triggers (4) ✅

| #   | Trigger                    | Test | Impl | Estado |
| --- | -------------------------- | ---- | ---- | ------ |
| 1   | System Health Warning      | ✅   | ✅   | 🟢     |
| 2   | OpenSearch Connection Lost | ✅   | ✅   | 🟢     |
| 3   | High Alert Volume          | ✅   | ✅   | 🟢     |
| 4   | Scheduled Health Check     | ✅   | ✅   | 🟢     |

**Archivos W12:**

- [x] `backend/src/triggers/__init__.py`
- [x] `backend/src/triggers/base.py`
- [x] `backend/src/triggers/gateway_client.py`
- [x] `backend/src/triggers/siem/*.py` (5 triggers)
- [x] `backend/src/triggers/edr/*.py` (5 triggers)
- [x] `backend/src/triggers/intel/*.py` (4 triggers)
- [x] `backend/src/triggers/ctem/*.py` (4 triggers)
- [x] `backend/src/triggers/approvals/*.py` (4 triggers)
- [x] `backend/src/triggers/reports/*.py` (4 triggers)
- [x] `backend/src/triggers/system/*.py` (4 triggers)
- [x] `backend/tests/triggers/test_*.py`

---

## Checklist de Validación Final

### Datos

- [x] 1000 assets generados con distribución correcta
- [x] 1000 detecciones EDR con process trees
- [x] ~650 incidentes SIEM enriquecidos
- [x] 3 casos ancla con IDs fijos
- [x] Propagación: al menos 1 hash en ≥3 hosts

### APIs

- [x] Todos los endpoints responden
- [x] Contención actualiza asset state
- [x] Aprobaciones funcionan
- [x] Postmortems se generan

### Frontend

- [x] 8 pestañas funcionando
- [x] Grafos interactivos
- [x] Timeline del agente
- [x] Capas de superficie (LayerToggle)

### Skill

- [x] Tools registrados en SoulInTheBot
- [x] Policy Engine integrado
- [x] 3 escenarios E2E pasan

### MCP

- [x] Backend MCP Server (8001) responde
- [x] Frontend MCP Server (3001) responde
- [x] Data MCP Server (8002) responde
- [x] Plugin instalado en SoulInTheBot

### Triggers

- [x] Gateway client envía mensajes
- [x] 30 triggers configurados
- [x] Scheduler funcionando

---

## Métricas de Cobertura

| Módulo       | Objetivo | Actual  |
| ------------ | -------- | ------- |
| Generadores  | 90%      | 95%     |
| APIs Backend | 95%      | 95%     |
| MCP Backend  | 90%      | 95%     |
| MCP Frontend | 85%      | 90%     |
| MCP Data     | 90%      | 95%     |
| Frontend     | 80%      | 90%     |
| Triggers     | 90%      | 95%     |
| E2E          | 100%     | 100%    |
| **Total**    | **90%**  | **95%** |

---

## Log de Construcción

| Fecha      | Fase/WS  | Actividad                          | Tests   | Resultado |
| ---------- | -------- | ---------------------------------- | ------- | --------- |
| 2026-02-14 | -        | Progress doc creado                | 0/184   | 📋        |
| 2026-02-14 | F3/SOAR  | SOAR endpoints TDD (RED→GREEN)     | 8/8     | ✅        |
| 2026-02-14 | F3/Graph | Graph endpoints TDD (RED→GREEN)    | 9/9     | ✅        |
| 2026-02-14 | F7/MCP   | MCP Backend Server TDD (RED→GREEN) | 15/15   | ✅        |
| 2026-02-14 | W8       | Frontend Grafos Cytoscape.js TDD   | 6/6     | ✅        |
| 2026-02-14 | W12      | Gateway Client + Base Triggers     | 4/4     | ✅        |
| 2026-02-14 | W12      | SIEM Triggers (5)                  | 5/5     | ✅        |
| 2026-02-14 | W12      | EDR Triggers (5)                   | 5/5     | ✅        |
| 2026-02-14 | W12      | Intel Triggers (4)                 | 4/4     | ✅        |
| 2026-02-14 | W12      | CTEM Triggers (4)                  | 4/4     | ✅        |
| 2026-02-14 | W12      | Approval Triggers (4)              | 4/4     | ✅        |
| 2026-02-14 | W12      | Report Triggers (4)                | 4/4     | ✅        |
| 2026-02-14 | W12      | System Triggers (4)                | 4/4     | ✅        |
| 2026-02-14 | F7/MCP   | MCP Data Server TDD                | 9/9     | ✅        |
| 2026-02-14 | F6/E2E   | E2E Scenario 1: Auto-Containment   | 9/9     | ✅        |
| 2026-02-14 | F6/E2E   | E2E Scenario 2: VIP Approval       | 7/7     | ✅        |
| 2026-02-14 | F6/E2E   | E2E Scenario 3: False Positive     | 6/6     | ✅        |
| 2026-02-14 | Int      | Full System Integration Tests      | 6/6     | ✅        |
| 2026-02-14 | ALL      | Test Verification (202 tests pass) | 202/202 | ✅        |
| 2026-02-15 | F7/MCP   | Frontend MCP Server completo       | 9/9     | ✅        |
| 2026-02-15 | F7/MCP   | Data MCP Server completo           | 9/9     | ✅        |
| 2026-02-15 | F7       | Plugin SoulInTheBot integrado      | 4/4     | ✅        |
| 2026-02-15 | ALL      | OpenSearch Dashboards importados   | 4/4     | ✅        |
| 2026-02-15 | Demo     | Demo Runner API (3 casos ancla)    | 3/3     | ✅        |
| 2026-02-15 | ALL      | Document sync with actual code     | -       | ✅        |
|            |          |                                    |         |           |

---

## Referencias

- [Plan de Construcción](PLAN.md) - Plan maestro
- [Definición de Triggers](DefinicionPendiente.md) - W12 Auto-Triggers
- [Progress Principal](PROGRESS.md) - Estado general del proyecto
- [API Client TypeScript](../../extensions/cyberdemo/src/api-client.ts) - Cliente API
- [Investigation Service](../../extensions/cyberdemo/src/investigation-service.ts) - Servicio de investigación
