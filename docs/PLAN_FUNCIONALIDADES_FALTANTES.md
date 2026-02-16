# Plan de Construccion - Funcionalidades Faltantes CyberDemo

> **Referencia:** [FUNCIONALIDADES_FALTANTESV2.md](FUNCIONALIDADES_FALTANTESV2.md)
> **Fecha:** 15 Febrero 2026
> **Metodologia:** TDD Estricto (Red -> Green -> Refactor)
> **Agentes:** 5 (4 desarrollo paralelo + 1 QA/Verificacion)

---

## Resumen Ejecutivo

Este plan cubre las funcionalidades identificadas como faltantes en el analisis comparativo entre el documento original de funcionalidad (`Plan_Demo_SOC_AI_Agent_v3.md.docx`) y lo actualmente construido. Se organiza en **4 workstreams paralelos** ejecutados por 4 agentes de desarrollo, mas un **agente de QA** dedicado exclusivamente a:

1. Escribir tests ANTES de la implementacion (TDD Red)
2. Ejecutar tests despues de la implementacion (TDD Green)
3. Verificar en el codigo que lo construido cumple al 100% la definicion funcional
4. Solo entonces marcar como completado en el documento de progreso

---

## Arquitectura de Agentes

```
+---------------------------------------------------------------------------+
|                        ORQUESTACION DE 5 AGENTES                          |
+---------------------------------------------------------------------------+
|                                                                           |
|  AGENTE 1 (Backend SOC)     AGENTE 2 (Observability)                     |
|  - Confidence Score          - Grafana + Prometheus                       |
|  - 3 Escenarios nuevos       - Loki + Tempo                              |
|  - SKILL.md completo         - 5 Dashboards                              |
|  - Hooks SoulInTheBot        - Metricas backend                          |
|                                                                           |
|  AGENTE 3 (Backend Services) AGENTE 4 (Frontend)                         |
|  - Playbooks Engine          - Superficie ataque capas                   |
|  - Notificaciones            - Pagina Configuracion                      |
|  - Canal Colaboracion        - Pagina Auditoria                          |
|  - APIs faltantes            - Pagina Reportes Ejecutivos                |
|                                                                           |
|                     AGENTE 5 (QA & Verificacion)                          |
|                     - Escribe tests PRIMERO (TDD)                         |
|                     - Ejecuta y valida tests                              |
|                     - Verifica definicion funcional                       |
|                     - Actualiza PROGRESS                                  |
|                                                                           |
+---------------------------------------------------------------------------+
```

### Flujo de Trabajo TDD por Feature

```
AGENTE 5 (QA)              AGENTE 1-4 (Dev)           AGENTE 5 (QA)
     |                          |                          |
     | 1. Escribe tests         |                          |
     |    (TDD RED)             |                          |
     |------------------------->|                          |
     |                          | 2. Implementa codigo     |
     |                          |    (TDD GREEN)           |
     |                          |------------------------->|
     |                          |                          | 3. Ejecuta tests
     |                          |                          | 4. Verifica 100%
     |                          |                          |    definicion funcional
     |                          |                          | 5. Si OK: marca en
     |                          |                          |    PROGRESS
     |                          |                          | 6. Si FAIL: reporta
     |                          |<-------------------------|    al agente dev
```

---

## Priorizacion

### Fase A: Prioridad Alta (Critico para Demo) - Sprint 1-2

| ID   | Funcionalidad                         | Agente   | Esfuerzo |
| ---- | ------------------------------------- | -------- | -------- |
| FA-1 | Confidence Score algoritmo completo   | Agente 1 | 4h       |
| FA-2 | SKILL.md con contenido completo       | Agente 1 | 3h       |
| FA-3 | Capas visualizacion superficie ataque | Agente 4 | 6h       |
| FA-4 | Escenario 4: Ransomware Multi-Host    | Agente 1 | 5h       |
| FA-5 | Escenario 5: Insider Threat           | Agente 1 | 5h       |
| FA-6 | Escenario 6: Supply Chain Attack      | Agente 1 | 5h       |
| FA-7 | Hooks SoulInTheBot                    | Agente 1 | 3h       |

### Fase B: Prioridad Media (Mejora significativa) - Sprint 3-4

| ID    | Funcionalidad                           | Agente   | Esfuerzo |
| ----- | --------------------------------------- | -------- | -------- |
| FB-1  | Grafana Observability Stack             | Agente 2 | 8h       |
| FB-2  | 5 Dashboards Grafana                    | Agente 2 | 6h       |
| FB-3  | Metricas Prometheus Backend             | Agente 2 | 4h       |
| FB-4  | Logs centralizados (Loki)               | Agente 2 | 3h       |
| FB-5  | Trazas distribuidas (Tempo)             | Agente 2 | 3h       |
| FB-6  | Sistema de Playbooks                    | Agente 3 | 8h       |
| FB-7  | Sistema de Notificaciones               | Agente 3 | 5h       |
| FB-8  | Canal de Colaboracion                   | Agente 3 | 6h       |
| FB-9  | APIs faltantes (Config, Audit, Reports) | Agente 3 | 5h       |
| FB-10 | Pagina Configuracion UI                 | Agente 4 | 5h       |
| FB-11 | Pagina Auditoria UI                     | Agente 4 | 4h       |
| FB-12 | Pagina Reportes Ejecutivos UI           | Agente 4 | 4h       |
| FB-13 | Pagina Playbooks UI                     | Agente 4 | 5h       |

---

## AGENTE 1: Backend SOC Core

### FA-1: Confidence Score - Algoritmo Completo

**Estado actual:** Parcialmente implementado en `backend/src/services/confidence_score.py`
**Gap:** Faltan pesos configurables por tipo de amenaza, documentacion de umbrales por escenario

#### Tests (TDD - Agente 5 escribe primero)

```
tests/unit/services/test_confidence_score_detailed.py
```

| #   | Test                                          | Descripcion                                |
| --- | --------------------------------------------- | ------------------------------------------ |
| 1   | `test_intel_component_vt_high_detections`     | VT score >60 = 35-40 puntos                |
| 2   | `test_intel_component_vt_low_detections`      | VT score <10 = 0-5 puntos                  |
| 3   | `test_intel_component_malware_labels_boost`   | Labels conocidas +5 puntos                 |
| 4   | `test_behavior_component_high_risk_technique` | T1003.001 = 25-30 puntos                   |
| 5   | `test_behavior_component_suspicious_cmdline`  | encoded cmd = +10 puntos                   |
| 6   | `test_behavior_component_benign_process`      | notepad.exe = 0-5 puntos                   |
| 7   | `test_context_component_critical_asset`       | asset criticality=critical = 15-20         |
| 8   | `test_context_component_high_ctem_risk`       | CTEM Red = +15 puntos                      |
| 9   | `test_propagation_3plus_hosts`                | >=3 hosts = 8-10 puntos                    |
| 10  | `test_propagation_single_host`                | 1 host = 1-2 puntos                        |
| 11  | `test_configurable_weights_by_threat_type`    | ransomware pesos diferentes                |
| 12  | `test_score_boundaries_0_and_100`             | Nunca <0 ni >100                           |
| 13  | `test_all_components_sum_to_total`            | intel+behavior+context+propagation = total |

#### Implementacion

| #   | Archivo                                    | Descripcion                             |
| --- | ------------------------------------------ | --------------------------------------- |
| 1   | `backend/src/services/confidence_score.py` | Extender con pesos configurables        |
| 2   | `backend/src/core/config.py`               | Agregar config de pesos por threat_type |
| 3   | `backend/config/confidence_weights.yaml`   | YAML con pesos por escenario            |

---

### FA-2: SKILL.md Contenido Completo

**Estado actual:** Existe en `extensions/cyberdemo/skills/soc-analyst/SKILL.md` pero necesita mas ejemplos y workflows detallados

#### Tests (TDD - Agente 5 valida)

| #   | Verificacion           | Descripcion                                             |
| --- | ---------------------- | ------------------------------------------------------- |
| 1   | Rol definido           | Tiene seccion "Rol" con descripcion completa            |
| 2   | Workflow 5 pasos       | Recibir -> Enriquecer -> Calcular -> Ejecutar -> Cerrar |
| 3   | Tools listados         | Todas las tools con ejemplos de uso                     |
| 4   | Politicas documentadas | Reglas deterministas completas                          |
| 5   | 3+ ejemplos completos  | Casos de uso con input/output                           |

#### Implementacion

| #   | Archivo                                            | Descripcion                       |
| --- | -------------------------------------------------- | --------------------------------- |
| 1   | `extensions/cyberdemo/skills/soc-analyst/SKILL.md` | Reescribir con contenido completo |

---

### FA-4/5/6: 3 Escenarios Adicionales

#### Escenario 4: Ransomware Multi-Host

**Trigger:** Deteccion de cifrado masivo en 5+ hosts

##### Tests (TDD)

```
backend/tests/e2e/test_scenario_ransomware.py
```

| #   | Test                                     | Descripcion                        |
| --- | ---------------------------------------- | ---------------------------------- |
| 1   | `test_ransomware_detection_created`      | Deteccion inicial en 1 host        |
| 2   | `test_ransomware_hunt_finds_5_hosts`     | Hunt hash encuentra 5+ hosts       |
| 3   | `test_ransomware_mass_containment`       | Contencion coordinada de todos     |
| 4   | `test_ransomware_executive_notification` | Notificacion ejecutiva generada    |
| 5   | `test_ransomware_playbook_executed`      | Playbook de response activado      |
| 6   | `test_ransomware_postmortem_multi_host`  | Postmortem incluye todos los hosts |

##### Implementacion

| #   | Archivo                                             | Descripcion                       |
| --- | --------------------------------------------------- | --------------------------------- |
| 1   | `backend/src/generators/gen_siem.py`                | Agregar caso ancla INC-ANCHOR-004 |
| 2   | `backend/src/generators/gen_edr.py`                 | Hash compartido en 5+ hosts       |
| 3   | `backend/src/demo/scenarios.py`                     | Escenario ransomware              |
| 4   | `extensions/cyberdemo/tests/e2e/ransomware.test.ts` | Test E2E plugin                   |

---

#### Escenario 5: Insider Threat

**Trigger:** Usuario privilegiado exfiltra datos

##### Tests (TDD)

```
backend/tests/e2e/test_scenario_insider.py
```

| #   | Test                                 | Descripcion                       |
| --- | ------------------------------------ | --------------------------------- |
| 1   | `test_insider_anomalous_volume`      | Volumen anormalo detectado        |
| 2   | `test_insider_schedule_correlation`  | Fuera de horario laboral          |
| 3   | `test_insider_requires_hr_approval`  | Requiere aprobacion de HR         |
| 4   | `test_insider_evidence_preservation` | Evidencia preservada (no borrada) |
| 5   | `test_insider_no_auto_containment`   | Nunca auto-contiene (requiere HR) |

##### Implementacion

| #   | Archivo                                 | Descripcion               |
| --- | --------------------------------------- | ------------------------- |
| 1   | `backend/src/generators/gen_siem.py`    | Caso ancla INC-ANCHOR-005 |
| 2   | `backend/src/generators/gen_edr.py`     | Deteccion exfiltracion    |
| 3   | `backend/src/demo/scenarios.py`         | Escenario insider         |
| 4   | `backend/src/services/policy_engine.py` | Regla insider_threat      |

---

#### Escenario 6: Supply Chain Attack

**Trigger:** Software legitimo comprometido

##### Tests (TDD)

```
backend/tests/e2e/test_scenario_supply_chain.py
```

| #   | Test                                    | Descripcion                          |
| --- | --------------------------------------- | ------------------------------------ |
| 1   | `test_supply_chain_anomalous_behavior`  | App conocida, comportamiento anomalo |
| 2   | `test_supply_chain_hash_verification`   | Hash no coincide con vendor          |
| 3   | `test_supply_chain_alert_generated`     | Alerta de supply chain               |
| 4   | `test_supply_chain_org_hunt`            | Hunting en toda la organizacion      |
| 5   | `test_supply_chain_all_instances_found` | Todas las instancias del software    |

##### Implementacion

| #   | Archivo                              | Descripcion               |
| --- | ------------------------------------ | ------------------------- |
| 1   | `backend/src/generators/gen_siem.py` | Caso ancla INC-ANCHOR-006 |
| 2   | `backend/src/generators/gen_edr.py`  | Deteccion supply chain    |
| 3   | `backend/src/demo/scenarios.py`      | Escenario supply chain    |

---

### FA-7: Hooks SoulInTheBot

**Estado actual:** Existe `extensions/cyberdemo/src/hooks.ts` pero incompleto

#### Tests (TDD)

```
extensions/cyberdemo/tests/unit/hooks.test.ts
```

| #   | Test                                      | Descripcion                              |
| --- | ----------------------------------------- | ---------------------------------------- |
| 1   | `test_on_tool_start_logs_event`           | Hook registra inicio de tool             |
| 2   | `test_on_tool_complete_updates_timeline`  | Hook actualiza timeline                  |
| 3   | `test_on_tool_complete_notifies_frontend` | Hook notifica frontend via WS            |
| 4   | `test_on_containment_verifies_policy`     | Hook verifica politica antes de contener |
| 5   | `test_on_containment_creates_audit_log`   | Hook crea log de auditoria               |
| 6   | `test_on_approval_resumes_workflow`       | Hook reanuda workflow post-aprobacion    |

#### Implementacion

| #   | Archivo                             | Descripcion                    |
| --- | ----------------------------------- | ------------------------------ |
| 1   | `extensions/cyberdemo/src/hooks.ts` | Reescribir con hooks completos |
| 2   | `extensions/cyberdemo/hooks.yaml`   | Config declarativa de hooks    |

---

## AGENTE 2: Observability Stack

### FB-1: Grafana + Prometheus + Loki + Tempo

#### Tests (TDD)

```
CyberDemo/tests/integration/test_observability.py
```

| #   | Test                                  | Descripcion                         |
| --- | ------------------------------------- | ----------------------------------- |
| 1   | `test_prometheus_scrapes_backend`     | Prometheus recoge metricas          |
| 2   | `test_grafana_healthy`                | Grafana responde en :3000           |
| 3   | `test_loki_receives_logs`             | Loki recibe logs del backend        |
| 4   | `test_tempo_receives_traces`          | Tempo recibe trazas                 |
| 5   | `test_backend_exposes_metrics`        | /metrics endpoint Prometheus format |
| 6   | `test_grafana_datasources_configured` | 3 datasources auto-provisioned      |

#### Implementacion

##### Docker Compose (servicios nuevos)

| #   | Servicio   | Puerto | Descripcion            |
| --- | ---------- | ------ | ---------------------- |
| 1   | Grafana    | 3000   | Dashboards de metricas |
| 2   | Prometheus | 9090   | Scraping de metricas   |
| 3   | Loki       | 3100   | Logs centralizados     |
| 4   | Tempo      | 3200   | Trazas distribuidas    |

##### Archivos

| #   | Archivo                                           | Descripcion                |
| --- | ------------------------------------------------- | -------------------------- |
| 1   | `docker/docker-compose.yml`                       | Agregar 4 servicios        |
| 2   | `docker/grafana/provisioning/datasources/all.yml` | Auto-provision datasources |
| 3   | `docker/prometheus/prometheus.yml`                | Config scrape targets      |
| 4   | `docker/loki/loki-config.yml`                     | Config Loki                |
| 5   | `docker/tempo/tempo-config.yml`                   | Config Tempo               |

---

### FB-2: 5 Dashboards Grafana

#### Tests (TDD)

```
CyberDemo/tests/integration/test_grafana_dashboards.py
```

| #   | Test                                     | Descripcion                       |
| --- | ---------------------------------------- | --------------------------------- |
| 1   | `test_dashboard_soc_overview_loads`      | Dashboard SOC Overview carga      |
| 2   | `test_dashboard_agent_performance_loads` | Dashboard Agent Performance carga |
| 3   | `test_dashboard_containment_rate_loads`  | Dashboard Containment Rate carga  |
| 4   | `test_dashboard_mttr_analytics_loads`    | Dashboard MTTR/MTTD carga         |
| 5   | `test_dashboard_approval_latency_loads`  | Dashboard Approval Latency carga  |
| 6   | `test_all_panels_have_data`              | Ningun panel muestra "No data"    |

#### Implementacion

| #   | Archivo                                                | Descripcion               |
| --- | ------------------------------------------------------ | ------------------------- |
| 1   | `docker/grafana/provisioning/dashboards/dashboard.yml` | Dashboard provider        |
| 2   | `docker/grafana/dashboards/soc-overview.json`          | SOC Operations Overview   |
| 3   | `docker/grafana/dashboards/agent-performance.json`     | Agent Performance Metrics |
| 4   | `docker/grafana/dashboards/containment-rate.json`      | Containment Success Rate  |
| 5   | `docker/grafana/dashboards/mttr-analytics.json`        | MTTR/MTTD Analytics       |
| 6   | `docker/grafana/dashboards/approval-latency.json`      | Human Approval Latency    |

---

### FB-3: Metricas Prometheus Backend

#### Tests (TDD)

```
backend/tests/unit/test_metrics.py
```

| #   | Test                                 | Descripcion                        |
| --- | ------------------------------------ | ---------------------------------- |
| 1   | `test_incidents_processed_counter`   | Counter incrementa por incidente   |
| 2   | `test_containments_auto_counter`     | Counter para auto-containments     |
| 3   | `test_containments_approved_counter` | Counter para approved containments |
| 4   | `test_false_positives_counter`       | Counter para FPs                   |
| 5   | `test_approval_wait_histogram`       | Histogram de tiempo de espera      |
| 6   | `test_api_latency_histogram`         | Histogram de latencia API          |
| 7   | `test_metrics_endpoint_format`       | /metrics en formato Prometheus     |

#### Implementacion

| #   | Archivo                           | Descripcion              |
| --- | --------------------------------- | ------------------------ |
| 1   | `backend/src/services/metrics.py` | Definicion de metricas   |
| 2   | `backend/src/api/metrics.py`      | Endpoint /metrics        |
| 3   | `backend/src/main.py`             | Middleware para latencia |

##### Metricas a exponer

```
# Agent Metrics
cyberdemo_incidents_processed_total
cyberdemo_containments_auto_total
cyberdemo_containments_approved_total
cyberdemo_false_positives_total
cyberdemo_approval_wait_seconds

# System Metrics
cyberdemo_api_requests_total
cyberdemo_api_latency_seconds
cyberdemo_opensearch_queries_total
```

---

### FB-4/5: Logs (Loki) y Trazas (Tempo)

#### Tests (TDD)

| #   | Test                             | Descripcion                       |
| --- | -------------------------------- | --------------------------------- |
| 1   | `test_structured_logging_format` | Logs en JSON estructurado         |
| 2   | `test_request_id_propagated`     | request_id en todos los logs      |
| 3   | `test_trace_spans_created`       | Spans creados para cada request   |
| 4   | `test_trace_context_propagated`  | Context propagado entre servicios |

#### Implementacion

| #   | Archivo                       | Descripcion               |
| --- | ----------------------------- | ------------------------- |
| 1   | `backend/src/core/logging.py` | Structured logging config |
| 2   | `backend/src/core/tracing.py` | OpenTelemetry setup       |
| 3   | `backend/src/main.py`         | Middleware de tracing     |

---

## AGENTE 3: Backend Services

### FB-6: Sistema de Playbooks

**Definicion:** Automatizacion basada en playbooks YAML

#### Tests (TDD)

```
backend/tests/unit/test_playbook_engine.py
backend/tests/integration/test_playbook_execution.py
```

| #   | Test                                    | Descripcion                            |
| --- | --------------------------------------- | -------------------------------------- |
| 1   | `test_load_playbook_from_yaml`          | Carga YAML correctamente               |
| 2   | `test_playbook_steps_execute_in_order`  | Pasos secuenciales                     |
| 3   | `test_playbook_on_error_handler`        | on_error redirige a handler            |
| 4   | `test_playbook_timeout`                 | Step con timeout aborta                |
| 5   | `test_playbook_variable_substitution`   | Variables ${incident.id} resueltas     |
| 6   | `test_contain_and_investigate_playbook` | Playbook 1 end-to-end                  |
| 7   | `test_vip_escalation_playbook`          | Playbook 2 end-to-end                  |
| 8   | `test_false_positive_closure_playbook`  | Playbook 3 end-to-end                  |
| 9   | `test_lateral_movement_hunt_playbook`   | Playbook 4 end-to-end                  |
| 10  | `test_ransomware_response_playbook`     | Playbook 5 end-to-end                  |
| 11  | `test_list_playbooks_api`               | GET /playbooks devuelve lista          |
| 12  | `test_run_playbook_api`                 | POST /playbooks/{id}/run ejecuta       |
| 13  | `test_playbook_run_history`             | GET /playbooks/{id}/runs con historial |

#### Implementacion

| #   | Archivo                                                 | Descripcion                     |
| --- | ------------------------------------------------------- | ------------------------------- |
| 1   | `backend/src/services/playbook_engine.py`               | Motor de ejecucion de playbooks |
| 2   | `backend/src/api/playbooks.py`                          | Endpoints REST                  |
| 3   | `backend/config/playbooks/contain_and_investigate.yaml` | Playbook 1                      |
| 4   | `backend/config/playbooks/vip_escalation.yaml`          | Playbook 2                      |
| 5   | `backend/config/playbooks/false_positive_closure.yaml`  | Playbook 3                      |
| 6   | `backend/config/playbooks/lateral_movement_hunt.yaml`   | Playbook 4                      |
| 7   | `backend/config/playbooks/ransomware_response.yaml`     | Playbook 5                      |

---

### FB-7: Sistema de Notificaciones

#### Tests (TDD)

```
backend/tests/unit/test_notification_service.py
```

| #   | Test                               | Descripcion                           |
| --- | ---------------------------------- | ------------------------------------- |
| 1   | `test_send_slack_notification`     | Envia a Slack webhook (mock)          |
| 2   | `test_send_email_notification`     | Envia email SMTP (mock)               |
| 3   | `test_send_teams_notification`     | Envia a Teams webhook (mock)          |
| 4   | `test_template_rendering`          | Templates se renderizan correctamente |
| 5   | `test_notification_config_loading` | Config desde YAML                     |
| 6   | `test_notification_api_endpoint`   | GET/PUT /config/notifications         |

#### Implementacion

| #   | Archivo                                        | Descripcion                |
| --- | ---------------------------------------------- | -------------------------- |
| 1   | `backend/src/services/notification_service.py` | Servicio de notificaciones |
| 2   | `backend/src/api/notifications.py`             | Endpoints REST             |
| 3   | `backend/config/notifications.yaml`            | Config canales + templates |
| 4   | `backend/src/templates/slack/`                 | Templates Slack            |
| 5   | `backend/src/templates/email/`                 | Templates Email            |

---

### FB-8: Canal de Colaboracion (collab-messages)

#### Tests (TDD)

```
backend/tests/unit/test_collab_service.py
```

| #   | Test                            | Descripcion                                |
| --- | ------------------------------- | ------------------------------------------ |
| 1   | `test_post_message`             | POST /collab/messages crea mensaje         |
| 2   | `test_get_messages_by_incident` | GET filtra por incident_id                 |
| 3   | `test_add_reaction`             | POST /collab/messages/{id}/reactions       |
| 4   | `test_delete_message`           | DELETE /collab/messages/{id}               |
| 5   | `test_message_mentions_parsed`  | @user y @asset parseados                   |
| 6   | `test_collab_websocket`         | WebSocket /collab/ws envia actualizaciones |

#### Implementacion

| #   | Archivo                                  | Descripcion                |
| --- | ---------------------------------------- | -------------------------- |
| 1   | `backend/src/services/collab_service.py` | Servicio de colaboracion   |
| 2   | `backend/src/api/collab.py`              | Endpoints REST + WebSocket |

---

### FB-9: APIs Faltantes

#### Tests (TDD)

```
backend/tests/unit/test_config_api.py
backend/tests/unit/test_audit_api.py
backend/tests/unit/test_reports_executive_api.py
```

| #   | Test                            | Descripcion                           |
| --- | ------------------------------- | ------------------------------------- |
| 1   | `test_get_policy_config`        | GET /config/policy devuelve config    |
| 2   | `test_update_policy_config`     | PUT /config/policy actualiza umbrales |
| 3   | `test_get_audit_logs`           | GET /audit/logs devuelve registros    |
| 4   | `test_export_audit_logs`        | GET /audit/logs/export formato CSV    |
| 5   | `test_weekly_executive_report`  | GET /reports/executive/weekly         |
| 6   | `test_monthly_executive_report` | GET /reports/executive/monthly        |
| 7   | `test_roi_report`               | GET /reports/roi calcula ahorro       |

#### Implementacion

| #   | Archivo                                            | Descripcion           |
| --- | -------------------------------------------------- | --------------------- |
| 1   | `backend/src/api/config.py`                        | Config endpoints      |
| 2   | `backend/src/api/audit.py`                         | Audit endpoints       |
| 3   | `backend/src/api/reports_executive.py`             | Executive reports     |
| 4   | `backend/src/services/audit_service.py`            | Audit logging service |
| 5   | `backend/src/services/executive_report_service.py` | Report generation     |

---

## AGENTE 4: Frontend

### FA-3: Capas Visualizacion Superficie de Ataque

**Estado actual:** LayerToggle basico existe. Falta interactividad avanzada.

#### Tests (TDD)

```
CyberDemo/tests/e2e/attack_surface.spec.ts
frontend/src/components/AttackSurface/__tests__/
```

| #   | Test                                 | Descripcion                         |
| --- | ------------------------------------ | ----------------------------------- |
| 1   | `test_layer_base_renders_all_assets` | Capa Base muestra todos             |
| 2   | `test_layer_edr_shows_detections`    | Capa EDR solo con detecciones       |
| 3   | `test_layer_siem_shows_incidents`    | Capa SIEM solo en incidentes        |
| 4   | `test_layer_ctem_gradient`           | Capa CTEM con gradiente riesgo      |
| 5   | `test_layer_threats_connections`     | Capa Threats muestra conexiones IOC |
| 6   | `test_layer_containment_timeline`    | Capa Containment con timeline       |
| 7   | `test_layer_toggle_switches`         | Toggle por capa funciona            |
| 8   | `test_time_slider`                   | Slider de tiempo cambia vista       |
| 9   | `test_semantic_zoom`                 | Zoom cluster -> individual          |
| 10  | `test_export_view`                   | Export de vista actual              |

#### Implementacion

| #   | Archivo                                                  | Descripcion              |
| --- | -------------------------------------------------------- | ------------------------ |
| 1   | `frontend/src/components/AttackSurface/LayerToggle.tsx`  | Mejorar toggle existente |
| 2   | `frontend/src/components/AttackSurface/TimeSlider.tsx`   | Slider temporal          |
| 3   | `frontend/src/components/AttackSurface/SemanticZoom.tsx` | Zoom semantico           |
| 4   | `frontend/src/components/AttackSurface/ExportView.tsx`   | Exportar vista           |
| 5   | `frontend/src/components/AttackSurface/layers/`          | 6 capas individuales     |

---

### FB-10: Pagina de Configuracion UI

#### Tests (TDD)

```
CyberDemo/tests/e2e/config_page.spec.ts
```

| #   | Test                                | Descripcion                 |
| --- | ----------------------------------- | --------------------------- |
| 1   | `test_config_page_loads`            | Pagina carga sin errores    |
| 2   | `test_policy_thresholds_editable`   | Umbrales editables          |
| 3   | `test_notification_channels_config` | Config canales notificacion |
| 4   | `test_api_keys_masked`              | API keys enmascaradas       |
| 5   | `test_save_config_persists`         | Guardar persiste cambios    |

#### Implementacion

| #   | Archivo                               | Descripcion             |
| --- | ------------------------------------- | ----------------------- |
| 1   | `frontend/src/pages/ConfigPage.tsx`   | Pagina de configuracion |
| 2   | `frontend/src/components/Sidebar.tsx` | Agregar link en sidebar |
| 3   | `frontend/src/App.tsx`                | Agregar ruta            |

---

### FB-11: Pagina de Auditoria UI

#### Tests (TDD)

```
CyberDemo/tests/e2e/audit_page.spec.ts
```

| #   | Test                       | Descripcion                    |
| --- | -------------------------- | ------------------------------ |
| 1   | `test_audit_page_loads`    | Pagina carga sin errores       |
| 2   | `test_audit_filters_work`  | Filtros por usuario/fecha/tipo |
| 3   | `test_audit_export_csv`    | Export a CSV funciona          |
| 4   | `test_audit_shows_actions` | Muestra acciones con timestamp |

#### Implementacion

| #   | Archivo                               | Descripcion         |
| --- | ------------------------------------- | ------------------- |
| 1   | `frontend/src/pages/AuditPage.tsx`    | Pagina de auditoria |
| 2   | `frontend/src/components/Sidebar.tsx` | Agregar link        |
| 3   | `frontend/src/App.tsx`                | Agregar ruta        |

---

### FB-12: Pagina de Reportes Ejecutivos UI

#### Tests (TDD)

```
CyberDemo/tests/e2e/executive_reports.spec.ts
```

| #   | Test                          | Descripcion                      |
| --- | ----------------------------- | -------------------------------- |
| 1   | `test_executive_page_loads`   | Pagina carga sin errores         |
| 2   | `test_weekly_report_renders`  | Reporte semanal se muestra       |
| 3   | `test_monthly_report_renders` | Reporte mensual se muestra       |
| 4   | `test_roi_metrics_displayed`  | Metricas ROI visibles            |
| 5   | `test_trend_charts_render`    | Graficos de tendencia renderizan |

#### Implementacion

| #   | Archivo                                       | Descripcion                |
| --- | --------------------------------------------- | -------------------------- |
| 1   | `frontend/src/pages/ExecutiveReportsPage.tsx` | Pagina reportes ejecutivos |
| 2   | `frontend/src/components/Sidebar.tsx`         | Agregar link               |
| 3   | `frontend/src/App.tsx`                        | Agregar ruta               |

---

### FB-13: Pagina de Playbooks UI

#### Tests (TDD)

```
CyberDemo/tests/e2e/playbooks_page.spec.ts
```

| #   | Test                         | Descripcion                 |
| --- | ---------------------------- | --------------------------- |
| 1   | `test_playbooks_page_loads`  | Pagina carga sin errores    |
| 2   | `test_playbook_list_renders` | Lista de playbooks visible  |
| 3   | `test_playbook_detail_opens` | Detalle de playbook se abre |
| 4   | `test_playbook_run_history`  | Historial de ejecuciones    |
| 5   | `test_playbook_run_button`   | Boton ejecutar funciona     |

#### Implementacion

| #   | Archivo                                | Descripcion         |
| --- | -------------------------------------- | ------------------- |
| 1   | `frontend/src/pages/PlaybooksPage.tsx` | Pagina de playbooks |
| 2   | `frontend/src/components/Sidebar.tsx`  | Agregar link        |
| 3   | `frontend/src/App.tsx`                 | Agregar ruta        |

---

## AGENTE 5: QA & Verificacion

### Responsabilidades

El Agente 5 es el **unico** que puede marcar items como completados en `PROGRESS_FUNCIONALIDADES_FALTANTES.md`. Su flujo es:

```
1. ANTES de que un Agente Dev comience:
   - Agente 5 escribe los tests (TDD RED)
   - Tests deben FALLAR (no existe implementacion)
   - Commit: "test(FA-X): add failing tests for [feature]"

2. DESPUES de que un Agente Dev termina:
   - Agente 5 ejecuta los tests
   - Si PASAN: continua a verificacion funcional
   - Si FALLAN: reporta al Agente Dev con detalles del fallo

3. VERIFICACION FUNCIONAL:
   - Agente 5 lee el codigo implementado
   - Compara CADA requisito del documento FUNCIONALIDADES_FALTANTESV2.md
   - Verifica que la implementacion cumple al 100%
   - Si hay gaps: reporta al Agente Dev

4. SOLO SI todo OK:
   - Agente 5 actualiza PROGRESS_FUNCIONALIDADES_FALTANTES.md
   - Marca [ ] -> [x] para cada item verificado
   - Actualiza el porcentaje de progreso
   - Actualiza el Log de Cambios

5. NUNCA marcar como completado si:
   - Tests fallan
   - Implementacion es parcial
   - No cumple al 100% la definicion funcional
```

### Checklist de Verificacion por Feature

Para cada feature, el Agente 5 debe verificar:

- [ ] Tests unitarios escritos y ejecutados
- [ ] Tests de integracion escritos y ejecutados
- [ ] Implementacion existe en los archivos correctos
- [ ] La implementacion cubre TODOS los requisitos del documento
- [ ] No hay errores de lint
- [ ] No introduce regresiones en tests existentes
- [ ] Documentacion actualizada si aplica

---

## Cronograma

### Sprint 1 (Dias 1-5): Prioridad Alta - Parte 1

| Dia | Agente 1               | Agente 2             | Agente 3              | Agente 4             | Agente 5             |
| --- | ---------------------- | -------------------- | --------------------- | -------------------- | -------------------- |
| 1   | FA-1: Confidence Score | FB-1: Docker Grafana | FB-6: Playbook Engine | FA-3: Capas (inicio) | Tests FA-1, FA-3     |
| 2   | FA-1: Continuar        | FB-1: Prometheus     | FB-6: Playbook Engine | FA-3: Capas (cont)   | Tests FB-1, FB-6     |
| 3   | FA-2: SKILL.md         | FB-3: Metricas       | FB-7: Notificaciones  | FA-3: Capas (fin)    | Verificar FA-1, FA-3 |
| 4   | FA-7: Hooks            | FB-4: Loki           | FB-7: Notificaciones  | FB-10: Config UI     | Tests FA-7, FB-10    |
| 5   | FA-4: Ransomware       | FB-5: Tempo          | FB-8: Collab          | FB-10: Config UI     | Verificar FA-2, FA-7 |

### Sprint 2 (Dias 6-10): Prioridad Alta - Parte 2

| Dia | Agente 1           | Agente 2            | Agente 3           | Agente 4            | Agente 5          |
| --- | ------------------ | ------------------- | ------------------ | ------------------- | ----------------- |
| 6   | FA-4: Ransomware   | FB-2: Dashboard 1-2 | FB-8: Collab       | FB-11: Audit UI     | Tests FA-4, FB-11 |
| 7   | FA-5: Insider      | FB-2: Dashboard 3-4 | FB-9: APIs Config  | FB-11: Audit UI     | Verificar FA-4    |
| 8   | FA-5: Insider      | FB-2: Dashboard 5   | FB-9: APIs Audit   | FB-12: Reports UI   | Tests FA-5, FB-12 |
| 9   | FA-6: Supply Chain | FB-2: Verificar     | FB-9: APIs Reports | FB-12: Reports UI   | Verificar FA-5    |
| 10  | FA-6: Supply Chain | Integracion         | FB-9: Finalizar    | FB-13: Playbooks UI | Tests FA-6, FB-13 |

### Sprint 3 (Dias 11-12): Integracion y Verificacion Final

| Dia | Agente 1 | Agente 2 | Agente 3 | Agente 4 | Agente 5           |
| --- | -------- | -------- | -------- | -------- | ------------------ |
| 11  | Fixes    | Fixes    | Fixes    | Fixes    | Verificacion total |
| 12  | Polish   | Polish   | Polish   | Polish   | PROGRESS final     |

---

## Resumen de Tests

### Tests Nuevos a Crear (Agente 5)

| Categoria          | Cantidad | Archivos                                         |
| ------------------ | -------- | ------------------------------------------------ |
| Confidence Score   | 13       | test_confidence_score_detailed.py                |
| Escenarios E2E     | 17       | test_scenario_ransomware/insider/supply_chain.py |
| Hooks              | 6        | hooks.test.ts                                    |
| Observability      | 10       | test_observability.py                            |
| Dashboards Grafana | 6        | test_grafana_dashboards.py                       |
| Metricas           | 7        | test_metrics.py                                  |
| Logs/Trazas        | 4        | test_logging_tracing.py                          |
| Playbooks          | 13       | test_playbook_engine.py                          |
| Notificaciones     | 6        | test_notification_service.py                     |
| Colaboracion       | 6        | test_collab_service.py                           |
| APIs faltantes     | 7        | test_config/audit/reports_api.py                 |
| Frontend E2E       | 24       | \*.spec.ts (5 archivos)                          |
| SKILL.md           | 5        | Verificacion manual                              |
| **TOTAL**          | **124**  |                                                  |

### Dependencias entre Features

```
FA-1 (Confidence Score) --> FA-4/5/6 (Escenarios usan score)
FB-6 (Playbooks) --> FA-4 (Ransomware usa playbook)
FB-7 (Notificaciones) --> FA-4 (Ransomware notifica ejecutivos)
FB-9 (APIs Config) --> FB-10 (UI Config consume APIs)
FB-9 (APIs Audit) --> FB-11 (UI Audit consume APIs)
FB-9 (APIs Reports) --> FB-12 (UI Reports consume APIs)
FB-6 (Playbooks API) --> FB-13 (UI Playbooks consume API)
FB-1 (Grafana Stack) --> FB-2 (Dashboards necesitan Grafana)
FB-3 (Metricas) --> FB-2 (Dashboards consumen metricas)
```

---

## Estimacion Total

| Item                        | Horas     |
| --------------------------- | --------- |
| Agente 1: Backend SOC Core  | 25h       |
| Agente 2: Observability     | 24h       |
| Agente 3: Backend Services  | 24h       |
| Agente 4: Frontend          | 24h       |
| Agente 5: QA & Verificacion | 30h       |
| **Total paralelo (max)**    | **~30h**  |
| **Total secuencial**        | **~127h** |

Con 5 agentes en paralelo: **~12 dias laborables** (2.5 sprints)

---

## Reglas de Oro

1. **NUNCA implementar sin tests primero** - El Agente 5 escribe tests antes
2. **NUNCA marcar progreso sin verificacion** - Solo Agente 5 actualiza PROGRESS
3. **NUNCA saltar verificacion funcional** - Cada feature se compara con el documento original
4. **Simplicidad ante todo** - Cada cambio impacta el minimo codigo necesario
5. **Sin regresiones** - Tests existentes deben seguir pasando
