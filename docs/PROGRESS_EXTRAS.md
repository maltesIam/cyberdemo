# Progreso: Funcionalidades Faltantes

**Última actualización:** 13 Febrero 2026
**Referencia:** PLAN_FASE2_EXTRAS.md

---

## Estado General

| Fase   | Descripción                   | Estado      | Progreso | Prioridad  |
| ------ | ----------------------------- | ----------- | -------- | ---------- |
| Fase A | Observabilidad (Grafana)      | Pendiente   | 0%       | Media      |
| Fase B | Confidence Score              | ✅ COMPLETO | 100%     | Alta       |
| Fase C | SKILL.md Completo             | ✅ COMPLETO | 100%     | Alta       |
| Fase D | Escenarios Demo Extra         | Pendiente   | 0%       | Media-Alta |
| Fase E | Notificaciones y Colaboración | Pendiente   | 0%       | Media      |
| Fase F | Playbooks SOAR                | Pendiente   | 0%       | Media      |

---

## 🎯 Enriquecimiento CTEM (Plan Original) - COMPLETO

| Componente                  | Estado | Tests              |
| --------------------------- | ------ | ------------------ |
| EnrichmentService           | ✅     | 55 PASS            |
| ConfidenceScoreCalculator   | ✅     | 46 PASS            |
| EnrichmentCache             | ✅     | Creado             |
| CircuitBreaker              | ✅     | Creado             |
| NVDClient                   | ✅     | Tests PASS         |
| EPSSClient                  | ✅     | Tests PASS         |
| OTXClient                   | ✅     | Tests PASS         |
| AbuseIPDBClient             | ✅     | Tests PASS         |
| GreyNoiseClient             | ✅     | Tests PASS         |
| RecordedFutureMock          | ✅     | 17 PASS            |
| TenableMock                 | ✅     | 7 PASS             |
| CrowdStrikeMock             | ✅     | 4 PASS             |
| EnrichmentButtons (UI)      | ✅     | Creado             |
| CTEMPage (UI)               | ✅     | Creado             |
| E2E Tests Playwright        | ✅     | enrichment.spec.ts |
| functional-complete.spec.ts | ✅     | Creado             |

**Total Backend Tests: 125+ PASS**

---

## Fase A: Observabilidad (Grafana Stack)

### A.1 Infraestructura Docker

- [ ] `docker/docker-compose.observability.yml`
- [ ] `docker/prometheus/prometheus.yml`
- [ ] `docker/grafana/provisioning/datasources/`
- [ ] `docker/grafana/provisioning/dashboards/`
- [ ] `docker/loki/loki-config.yml`
- [ ] Test: todos los servicios healthy

### A.2 Métricas del Backend

- [ ] `backend/src/metrics/__init__.py`
- [ ] `backend/src/metrics/prometheus.py`
- [ ] Endpoint `/metrics` (prometheus format)
- [ ] Counter: `cyberdemo_incidents_processed_total`
- [ ] Counter: `cyberdemo_containments_auto_total`
- [ ] Counter: `cyberdemo_containments_approved_total`
- [ ] Counter: `cyberdemo_false_positives_total`
- [ ] Histogram: `cyberdemo_api_latency_seconds`
- [ ] Histogram: `cyberdemo_approval_wait_seconds`
- [ ] Gauge: `cyberdemo_open_incidents`
- [ ] Gauge: `cyberdemo_contained_hosts`
- [ ] Test: métricas exportadas correctamente

### A.3 Dashboards Grafana

- [ ] `docker/grafana/dashboards/soc-overview.json`
- [ ] `docker/grafana/dashboards/agent-performance.json`
- [ ] `docker/grafana/dashboards/containment-analytics.json`
- [ ] `docker/grafana/dashboards/approval-latency.json`
- [ ] Test: dashboards importados correctamente

### A.4 Integración Frontend

- [ ] Performance observers en React
- [ ] Métricas de navegación
- [ ] Error tracking

---

## Fase B: Algoritmo de Confidence Score ✅ COMPLETO

### B.1 Tests (TDD) - 46 PASS

#### Intel Component Tests

- [x] `test_high_vt_score_gives_30_points`
- [x] `test_high_vt_score_with_malware_labels_gives_40`
- [x] `test_malware_labels_only_gives_10`
- [x] `test_no_detections_gives_zero`
- [x] `test_never_exceeds_40`

#### Behavior Component Tests

- [x] `test_high_risk_mitre_gives_20`
- [x] `test_suspicious_cmdline_encoded_powershell_gives_10`
- [x] `test_suspicious_cmdline_mimikatz_gives_10`
- [x] `test_high_risk_technique_plus_suspicious_cmdline_gives_30`
- [x] `test_never_exceeds_30`

#### Context Component Tests

- [x] `test_red_risk_gives_15`
- [x] `test_vip_criticality_gives_5`
- [x] `test_red_risk_plus_vip_gives_20`
- [x] `test_green_risk_low_criticality_gives_zero`
- [x] `test_never_exceeds_20`

#### Propagation Component Tests

- [x] `test_one_host_gives_2`
- [x] `test_two_hosts_gives_5`
- [x] `test_six_hosts_gives_10`
- [x] `test_never_exceeds_10`

#### Integration Tests

- [x] `test_scenario_high_confidence_malware`
- [x] `test_scenario_low_confidence_benign`
- [x] `test_scenario_medium_confidence_suspicious`
- [x] `test_components_breakdown_matches_total`

### B.2 Implementación ✅

- [x] `backend/src/services/confidence_score.py`
- [x] Clase `ConfidenceComponents` (dataclass)
- [ ] Clase `ConfidenceScoreCalculator`
- [ ] Método `_calculate_intel()`
- [ ] Método `_calculate_behavior()`
- [ ] Método `_calculate_context()`
- [ ] Método `_calculate_propagation()`
- [ ] Weights configurables

### B.3 Integración con Policy Engine

- [ ] Actualizar `PolicyEngine` para usar `ConfidenceScoreCalculator`
- [ ] Método `evaluate_with_enrichment()`
- [ ] Retornar componentes del score en decisión
- [ ] Tests de integración Policy + Score

---

## Fase C: SKILL.md Completo

### C.1 Contenido del SKILL.md

- [ ] Sección: Rol del Agente
- [ ] Sección: Contexto de Trabajo
- [ ] Sección: Workflow de Investigación (6 pasos)
- [ ] Sección: Herramientas Disponibles (tabla completa)
- [ ] Sección: Políticas de Contención
- [ ] Sección: Ejemplos de Investigación
  - [ ] Ejemplo 1: Auto-Containment
  - [ ] Ejemplo 2: VIP Human-in-the-Loop
  - [ ] Ejemplo 3: False Positive
- [ ] Sección: Notas Importantes

### C.2 skill.yaml

- [ ] Definición del skill
- [ ] Lista de tools disponibles
- [ ] Triggers configurados

### C.3 Integración SoulInTheBot

- [ ] Copiar skill a `extensions/cyberdemo/`
- [ ] Registrar en package.json del plugin
- [ ] Test: skill cargado correctamente

---

## Fase D: Escenarios Demo Adicionales

### D.1 Escenario 4: Ransomware Multi-Host

#### Datos Ancla

- [ ] Incidente `INC-RANSOMWARE-001`
- [ ] 5 detecciones relacionadas
- [ ] Hash único propagado
- [ ] Incluye servidor (requiere aprobación)

#### Tests E2E

- [ ] `test_e2e_scenario_4_incident_exists`
- [ ] `test_e2e_scenario_4_multiple_hosts`
- [ ] `test_e2e_scenario_4_server_affected`
- [ ] `test_e2e_scenario_4_requires_approval`
- [ ] `test_e2e_scenario_4_mass_containment`

#### Implementación

- [ ] Generador de datos ancla
- [ ] Lógica de contención masiva
- [ ] UI para mostrar afectación múltiple

### D.2 Escenario 5: Insider Threat

#### Datos Ancla

- [ ] Incidente `INC-INSIDER-001`
- [ ] Usuario con acceso privilegiado
- [ ] Comportamiento anómalo
- [ ] Requiere aprobación HR

#### Tests E2E

- [ ] `test_e2e_scenario_5_incident_exists`
- [ ] `test_e2e_scenario_5_user_behavior`
- [ ] `test_e2e_scenario_5_requires_hr_approval`

#### Implementación

- [ ] Generador de datos ancla
- [ ] Tipo de aprobación: HR
- [ ] Preservación de evidencia

### D.3 Escenario 6: Supply Chain Attack

#### Datos Ancla

- [ ] Incidente `INC-SUPPLY-001`
- [ ] Aplicación legítima comprometida
- [ ] Firma digital válida
- [ ] Comportamiento C2

#### Tests E2E

- [ ] `test_e2e_scenario_6_incident_exists`
- [ ] `test_e2e_scenario_6_trusted_app`
- [ ] `test_e2e_scenario_6_anomalous_behavior`
- [ ] `test_e2e_scenario_6_vendor_notification`

#### Implementación

- [ ] Generador de datos ancla
- [ ] Verificación de firma vs comportamiento
- [ ] Hunting organizacional

---

## Fase E: Notificaciones y Colaboración

### E.1 Sistema de Notificaciones

#### Tests

- [ ] `test_notification_service_init`
- [ ] `test_register_channel`
- [ ] `test_notify_sends_to_all_channels`
- [ ] `test_template_formatting`

#### Implementación

- [ ] `backend/src/services/notifications.py`
- [ ] Clase abstracta `NotificationChannel`
- [ ] Implementación `SlackNotifier` (mock)
- [ ] Implementación `EmailNotifier` (mock)
- [ ] Clase `NotificationService`
- [ ] Templates de mensajes
- [ ] Integración con contención/aprobaciones

### E.2 Canal de Colaboración

#### Tests

- [ ] `test_send_message`
- [ ] `test_get_messages_by_incident`
- [ ] `test_websocket_connection`
- [ ] `test_websocket_broadcast`

#### Implementación

- [ ] `backend/src/api/collab.py`
- [ ] Endpoint `POST /collab/messages`
- [ ] Endpoint `GET /collab/messages`
- [ ] WebSocket `/collab/ws`
- [ ] Broadcast de mensajes

#### Frontend

- [ ] Componente de chat embebido
- [ ] Conexión WebSocket
- [ ] Historial de mensajes
- [ ] Menciones de usuarios/assets

---

## Fase F: Playbooks SOAR

### F.1 Motor de Playbooks

#### Tests

- [ ] `test_load_playbook_from_yaml`
- [ ] `test_execute_single_step`
- [ ] `test_execute_multiple_steps`
- [ ] `test_step_on_error_stop`
- [ ] `test_step_on_error_notify_human`
- [ ] `test_param_resolution`
- [ ] `test_context_passed_between_steps`

#### Implementación

- [ ] `backend/src/services/playbook_engine.py`
- [ ] Dataclass `PlaybookStep`
- [ ] Dataclass `Playbook`
- [ ] Clase `PlaybookEngine`
- [ ] Método `load_playbook()`
- [ ] Método `execute()`
- [ ] Método `_execute_step()`
- [ ] Método `_resolve_params()`

### F.2 Playbooks Predefinidos

- [ ] `playbooks/contain_and_investigate.yaml`
- [ ] `playbooks/vip_escalation.yaml`
- [ ] `playbooks/false_positive_closure.yaml`
- [ ] `playbooks/lateral_movement_hunt.yaml`
- [ ] `playbooks/ransomware_response.yaml`

### F.3 API de Playbooks

#### Tests

- [ ] `test_list_playbooks`
- [ ] `test_get_playbook_detail`
- [ ] `test_run_playbook`
- [ ] `test_get_playbook_runs`

#### Implementación

- [ ] Endpoint `GET /playbooks`
- [ ] Endpoint `GET /playbooks/{id}`
- [ ] Endpoint `POST /playbooks/{id}/run`
- [ ] Endpoint `GET /playbooks/{id}/runs`

### F.4 UI de Playbooks

- [ ] Página de lista de playbooks
- [ ] Vista de detalle con pasos
- [ ] Historial de ejecuciones
- [ ] Métricas por playbook

---

## Log de Cambios

| Fecha      | Cambio                       |
| ---------- | ---------------------------- |
| 2026-02-13 | Documento de progreso creado |
| 2026-02-13 | Fases A-F definidas          |
| 2026-02-13 | Tareas detalladas por fase   |

---

## Notas

_Espacio para notas durante la implementación_

---

## Métricas de Progreso

### Por Fase

| Fase      | Total Tareas | Completadas | %      |
| --------- | ------------ | ----------- | ------ |
| A         | 18           | 0           | 0%     |
| B         | 25           | 0           | 0%     |
| C         | 12           | 0           | 0%     |
| D         | 21           | 0           | 0%     |
| E         | 15           | 0           | 0%     |
| F         | 20           | 0           | 0%     |
| **Total** | **111**      | **0**       | **0%** |

### Por Prioridad

| Prioridad  | Tareas | Completadas | %   |
| ---------- | ------ | ----------- | --- |
| Alta       | 37     | 0           | 0%  |
| Media-Alta | 21     | 0           | 0%  |
| Media      | 53     | 0           | 0%  |

---

## Dependencias Externas

| Dependencia                        | Estado    | Notas                         |
| ---------------------------------- | --------- | ----------------------------- |
| Plan Original Fase 2 (Generadores) | Pendiente | Requerido para Escenarios     |
| Plan Original Fase 3 (APIs)        | Pendiente | Requerido para Notificaciones |
| Plan Original Fase 7 (MCP)         | Pendiente | Requerido para SKILL.md       |

---

_Documento de seguimiento para funcionalidades faltantes._
