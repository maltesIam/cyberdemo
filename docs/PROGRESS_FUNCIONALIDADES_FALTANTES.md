# Progreso - Funcionalidades Faltantes CyberDemo

> **Plan:** [PLAN_FUNCIONALIDADES_FALTANTES.md](PLAN_FUNCIONALIDADES_FALTANTES.md)
> **Referencia:** [FUNCIONALIDADES_FALTANTESV2.md](FUNCIONALIDADES_FALTANTESV2.md)
> **Inicio:** 2026-02-15
> **Metodologia:** TDD Estricto (Red -> Green -> Refactor)
> **Estado:** 🔴 PENDIENTE

---

## Dashboard de Progreso

```
+------------------------------------------------------------------------------+
|                         PROGRESO GENERAL: 0%                                 |
+------------------------------------------------------------------------------+
|  Fase A (Alta):   __________   0%    Fase B (Media):  __________   0%        |
+------------------------------------------------------------------------------+
```

### Estado por Feature

#### Fase A: Prioridad Alta (Critico para Demo)

| ID   | Feature                          | Agente | Tests QA | Impl Dev | Verif QA | Estado |
| ---- | -------------------------------- | ------ | -------- | -------- | -------- | ------ |
| FA-1 | Confidence Score completo        | A1     | [ ] 0/13 | [ ] 0/3  | [ ]      | 🔴     |
| FA-2 | SKILL.md contenido completo      | A1     | [ ] 0/5  | [ ] 0/1  | [ ]      | 🔴     |
| FA-3 | Capas visualizacion superficie   | A4     | [ ] 0/10 | [ ] 0/5  | [ ]      | 🔴     |
| FA-4 | Escenario: Ransomware Multi-Host | A1     | [ ] 0/6  | [ ] 0/4  | [ ]      | 🔴     |
| FA-5 | Escenario: Insider Threat        | A1     | [ ] 0/5  | [ ] 0/4  | [ ]      | 🔴     |
| FA-6 | Escenario: Supply Chain Attack   | A1     | [ ] 0/5  | [ ] 0/3  | [ ]      | 🔴     |
| FA-7 | Hooks SoulInTheBot               | A1     | [ ] 0/6  | [ ] 0/2  | [ ]      | 🔴     |

#### Fase B: Prioridad Media (Mejora significativa)

| ID    | Feature                               | Agente | Tests QA | Impl Dev | Verif QA | Estado |
| ----- | ------------------------------------- | ------ | -------- | -------- | -------- | ------ |
| FB-1  | Grafana Stack (Docker)                | A2     | [ ] 0/6  | [ ] 0/5  | [ ]      | 🔴     |
| FB-2  | 5 Dashboards Grafana                  | A2     | [ ] 0/6  | [ ] 0/6  | [ ]      | 🔴     |
| FB-3  | Metricas Prometheus Backend           | A2     | [ ] 0/7  | [ ] 0/3  | [ ]      | 🔴     |
| FB-4  | Logs centralizados (Loki)             | A2     | [ ] 0/2  | [ ] 0/1  | [ ]      | 🔴     |
| FB-5  | Trazas distribuidas (Tempo)           | A2     | [ ] 0/2  | [ ] 0/2  | [ ]      | 🔴     |
| FB-6  | Sistema de Playbooks                  | A3     | [ ] 0/13 | [ ] 0/7  | [ ]      | 🔴     |
| FB-7  | Sistema de Notificaciones             | A3     | [ ] 0/6  | [ ] 0/5  | [ ]      | 🔴     |
| FB-8  | Canal de Colaboracion                 | A3     | [ ] 0/6  | [ ] 0/2  | [ ]      | 🔴     |
| FB-9  | APIs faltantes (Config/Audit/Reports) | A3     | [ ] 0/7  | [ ] 0/5  | [ ]      | 🔴     |
| FB-10 | Pagina Configuracion UI               | A4     | [ ] 0/5  | [ ] 0/3  | [ ]      | 🔴     |
| FB-11 | Pagina Auditoria UI                   | A4     | [ ] 0/4  | [ ] 0/3  | [ ]      | 🔴     |
| FB-12 | Pagina Reportes Ejecutivos UI         | A4     | [ ] 0/5  | [ ] 0/3  | [ ]      | 🔴     |
| FB-13 | Pagina Playbooks UI                   | A4     | [ ] 0/5  | [ ] 0/3  | [ ]      | 🔴     |

---

## Detalle por Feature

### FA-1: Confidence Score - Algoritmo Completo

**Agente Dev:** Agente 1 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_intel_component_vt_high_detections`
- [ ] `test_intel_component_vt_low_detections`
- [ ] `test_intel_component_malware_labels_boost`
- [ ] `test_behavior_component_high_risk_technique`
- [ ] `test_behavior_component_suspicious_cmdline`
- [ ] `test_behavior_component_benign_process`
- [ ] `test_context_component_critical_asset`
- [ ] `test_context_component_high_ctem_risk`
- [ ] `test_propagation_3plus_hosts`
- [ ] `test_propagation_single_host`
- [ ] `test_configurable_weights_by_threat_type`
- [ ] `test_score_boundaries_0_and_100`
- [ ] `test_all_components_sum_to_total`

#### Implementacion (Agente 1)

- [ ] `backend/src/services/confidence_score.py` - Extender pesos configurables
- [ ] `backend/src/core/config.py` - Config pesos por threat_type
- [ ] `backend/config/confidence_weights.yaml` - YAML pesos

#### Verificacion Funcional (Agente 5)

- [ ] Pesos configurables por tipo de amenaza implementados
- [ ] Tests unitarios para cada componente del score pasan
- [ ] Documentacion de umbrales por escenario completa
- [ ] Score total = suma de componentes
- [ ] Limites 0-100 respetados

---

### FA-2: SKILL.md Contenido Completo

**Agente Dev:** Agente 1 | **Estado:** 🔴 Pendiente

#### Verificacion (Agente 5)

- [ ] Seccion "Rol" con descripcion completa
- [ ] Workflow 5 pasos documentado
- [ ] Todas las tools con ejemplos de uso
- [ ] Politicas deterministas documentadas
- [ ] 3+ ejemplos de investigacion completos (input/output)

#### Implementacion (Agente 1)

- [ ] `extensions/cyberdemo/skills/soc-analyst/SKILL.md` - Reescribir completo

---

### FA-3: Capas Visualizacion Superficie de Ataque

**Agente Dev:** Agente 4 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_layer_base_renders_all_assets`
- [ ] `test_layer_edr_shows_detections`
- [ ] `test_layer_siem_shows_incidents`
- [ ] `test_layer_ctem_gradient`
- [ ] `test_layer_threats_connections`
- [ ] `test_layer_containment_timeline`
- [ ] `test_layer_toggle_switches`
- [ ] `test_time_slider`
- [ ] `test_semantic_zoom`
- [ ] `test_export_view`

#### Implementacion (Agente 4)

- [ ] `LayerToggle.tsx` - Mejorado
- [ ] `TimeSlider.tsx` - Nuevo
- [ ] `SemanticZoom.tsx` - Nuevo
- [ ] `ExportView.tsx` - Nuevo
- [ ] `layers/` - 6 capas individuales

#### Verificacion Funcional (Agente 5)

- [ ] 6 capas (Base, EDR, SIEM, CTEM, Threats, Containment) implementadas
- [ ] Toggle por capa funciona
- [ ] Slider de tiempo cambia vista temporal
- [ ] Zoom semantico (cluster -> individual) funciona
- [ ] Export de vista actual funciona
- [ ] Colores correctos por capa

---

### FA-4: Escenario Ransomware Multi-Host

**Agente Dev:** Agente 1 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_ransomware_detection_created`
- [ ] `test_ransomware_hunt_finds_5_hosts`
- [ ] `test_ransomware_mass_containment`
- [ ] `test_ransomware_executive_notification`
- [ ] `test_ransomware_playbook_executed`
- [ ] `test_ransomware_postmortem_multi_host`

#### Implementacion (Agente 1)

- [ ] Caso ancla INC-ANCHOR-004 en generadores
- [ ] Hash compartido en 5+ hosts
- [ ] Escenario en demo/scenarios.py
- [ ] Test E2E plugin ransomware.test.ts

#### Verificacion Funcional (Agente 5)

- [ ] 5+ hosts detectados con mismo hash
- [ ] Contencion masiva coordinada
- [ ] Notificacion ejecutiva generada
- [ ] Playbook de response activado
- [ ] Postmortem incluye todos los hosts

---

### FA-5: Escenario Insider Threat

**Agente Dev:** Agente 1 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_insider_anomalous_volume`
- [ ] `test_insider_schedule_correlation`
- [ ] `test_insider_requires_hr_approval`
- [ ] `test_insider_evidence_preservation`
- [ ] `test_insider_no_auto_containment`

#### Implementacion (Agente 1)

- [ ] Caso ancla INC-ANCHOR-005
- [ ] Deteccion exfiltracion
- [ ] Escenario demo
- [ ] Regla insider_threat en policy engine

#### Verificacion Funcional (Agente 5)

- [ ] Volumen anomalo detectado correctamente
- [ ] Correlacion con horario/ubicacion implementada
- [ ] Requiere aprobacion HR (nunca auto-contiene)
- [ ] Evidencia preservada (no borrada)

---

### FA-6: Escenario Supply Chain Attack

**Agente Dev:** Agente 1 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_supply_chain_anomalous_behavior`
- [ ] `test_supply_chain_hash_verification`
- [ ] `test_supply_chain_alert_generated`
- [ ] `test_supply_chain_org_hunt`
- [ ] `test_supply_chain_all_instances_found`

#### Implementacion (Agente 1)

- [ ] Caso ancla INC-ANCHOR-006
- [ ] Deteccion supply chain
- [ ] Escenario demo

#### Verificacion Funcional (Agente 5)

- [ ] App conocida con comportamiento anomalo detectada
- [ ] Hash no coincide con vendor verificado
- [ ] Alerta de supply chain generada
- [ ] Hunting organizacional encuentra todas las instancias

---

### FA-7: Hooks SoulInTheBot

**Agente Dev:** Agente 1 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_on_tool_start_logs_event`
- [ ] `test_on_tool_complete_updates_timeline`
- [ ] `test_on_tool_complete_notifies_frontend`
- [ ] `test_on_containment_verifies_policy`
- [ ] `test_on_containment_creates_audit_log`
- [ ] `test_on_approval_resumes_workflow`

#### Implementacion (Agente 1)

- [ ] `hooks.ts` reescrito completo
- [ ] `hooks.yaml` config declarativa

#### Verificacion Funcional (Agente 5)

- [ ] on_tool_start registra evento
- [ ] on_tool_complete actualiza timeline
- [ ] on_containment verifica politica
- [ ] on_approval reanuda workflow

---

### FB-1: Grafana Stack (Docker)

**Agente Dev:** Agente 2 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_prometheus_scrapes_backend`
- [ ] `test_grafana_healthy`
- [ ] `test_loki_receives_logs`
- [ ] `test_tempo_receives_traces`
- [ ] `test_backend_exposes_metrics`
- [ ] `test_grafana_datasources_configured`

#### Implementacion (Agente 2)

- [ ] docker-compose.yml - 4 servicios nuevos
- [ ] grafana/provisioning/datasources/all.yml
- [ ] prometheus/prometheus.yml
- [ ] loki/loki-config.yml
- [ ] tempo/tempo-config.yml

#### Verificacion Funcional (Agente 5)

- [ ] Grafana responde en :3000
- [ ] Prometheus scraping metricas backend
- [ ] Loki recibiendo logs
- [ ] Tempo recibiendo trazas
- [ ] 3 datasources auto-provisioned

---

### FB-2: 5 Dashboards Grafana

**Agente Dev:** Agente 2 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_dashboard_soc_overview_loads`
- [ ] `test_dashboard_agent_performance_loads`
- [ ] `test_dashboard_containment_rate_loads`
- [ ] `test_dashboard_mttr_analytics_loads`
- [ ] `test_dashboard_approval_latency_loads`
- [ ] `test_all_panels_have_data`

#### Implementacion (Agente 2)

- [ ] dashboard.yml - Dashboard provider
- [ ] soc-overview.json
- [ ] agent-performance.json
- [ ] containment-rate.json
- [ ] mttr-analytics.json
- [ ] approval-latency.json

#### Verificacion Funcional (Agente 5)

- [ ] 5 dashboards cargan sin error
- [ ] Todos los paneles muestran datos (no "No data")
- [ ] Metricas del backend se visualizan correctamente

---

### FB-3: Metricas Prometheus Backend

**Agente Dev:** Agente 2 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_incidents_processed_counter`
- [ ] `test_containments_auto_counter`
- [ ] `test_containments_approved_counter`
- [ ] `test_false_positives_counter`
- [ ] `test_approval_wait_histogram`
- [ ] `test_api_latency_histogram`
- [ ] `test_metrics_endpoint_format`

#### Implementacion (Agente 2)

- [ ] `backend/src/services/metrics.py`
- [ ] `backend/src/api/metrics.py`
- [ ] `backend/src/main.py` - Middleware latencia

#### Verificacion Funcional (Agente 5)

- [ ] 8 metricas expuestas en /metrics
- [ ] Formato Prometheus valido
- [ ] Counters incrementan correctamente
- [ ] Histograms con buckets apropiados

---

### FB-4: Logs Centralizados (Loki)

**Agente Dev:** Agente 2 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_structured_logging_format`
- [ ] `test_request_id_propagated`

#### Implementacion (Agente 2)

- [ ] `backend/src/core/logging.py`

---

### FB-5: Trazas Distribuidas (Tempo)

**Agente Dev:** Agente 2 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_trace_spans_created`
- [ ] `test_trace_context_propagated`

#### Implementacion (Agente 2)

- [ ] `backend/src/core/tracing.py`
- [ ] `backend/src/main.py` - Middleware tracing

---

### FB-6: Sistema de Playbooks

**Agente Dev:** Agente 3 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_load_playbook_from_yaml`
- [ ] `test_playbook_steps_execute_in_order`
- [ ] `test_playbook_on_error_handler`
- [ ] `test_playbook_timeout`
- [ ] `test_playbook_variable_substitution`
- [ ] `test_contain_and_investigate_playbook`
- [ ] `test_vip_escalation_playbook`
- [ ] `test_false_positive_closure_playbook`
- [ ] `test_lateral_movement_hunt_playbook`
- [ ] `test_ransomware_response_playbook`
- [ ] `test_list_playbooks_api`
- [ ] `test_run_playbook_api`
- [ ] `test_playbook_run_history`

#### Implementacion (Agente 3)

- [ ] `playbook_engine.py` - Motor ejecucion
- [ ] `api/playbooks.py` - Endpoints REST
- [ ] `contain_and_investigate.yaml`
- [ ] `vip_escalation.yaml`
- [ ] `false_positive_closure.yaml`
- [ ] `lateral_movement_hunt.yaml`
- [ ] `ransomware_response.yaml`

#### Verificacion Funcional (Agente 5)

- [ ] Playbooks cargan desde YAML
- [ ] Pasos se ejecutan en orden
- [ ] on_error maneja fallos
- [ ] Variables sustituidas correctamente
- [ ] 5 playbooks pre-definidos funcionan
- [ ] API REST lista/ejecuta/historial

---

### FB-7: Sistema de Notificaciones

**Agente Dev:** Agente 3 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_send_slack_notification`
- [ ] `test_send_email_notification`
- [ ] `test_send_teams_notification`
- [ ] `test_template_rendering`
- [ ] `test_notification_config_loading`
- [ ] `test_notification_api_endpoint`

#### Implementacion (Agente 3)

- [ ] `notification_service.py`
- [ ] `api/notifications.py`
- [ ] `config/notifications.yaml`
- [ ] `templates/slack/`
- [ ] `templates/email/`

#### Verificacion Funcional (Agente 5)

- [ ] 3 canales soportados (Slack, Email, Teams)
- [ ] Templates se renderizan correctamente
- [ ] Config carga desde YAML
- [ ] API endpoint funciona

---

### FB-8: Canal de Colaboracion

**Agente Dev:** Agente 3 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_post_message`
- [ ] `test_get_messages_by_incident`
- [ ] `test_add_reaction`
- [ ] `test_delete_message`
- [ ] `test_message_mentions_parsed`
- [ ] `test_collab_websocket`

#### Implementacion (Agente 3)

- [ ] `collab_service.py`
- [ ] `api/collab.py`

#### Verificacion Funcional (Agente 5)

- [ ] CRUD de mensajes funciona
- [ ] Filtro por incident_id
- [ ] Menciones parseadas
- [ ] WebSocket envia updates

---

### FB-9: APIs Faltantes (Config, Audit, Reports)

**Agente Dev:** Agente 3 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_get_policy_config`
- [ ] `test_update_policy_config`
- [ ] `test_get_audit_logs`
- [ ] `test_export_audit_logs`
- [ ] `test_weekly_executive_report`
- [ ] `test_monthly_executive_report`
- [ ] `test_roi_report`

#### Implementacion (Agente 3)

- [ ] `api/config.py`
- [ ] `api/audit.py`
- [ ] `api/reports_executive.py`
- [ ] `services/audit_service.py`
- [ ] `services/executive_report_service.py`

#### Verificacion Funcional (Agente 5)

- [ ] GET/PUT /config/policy funciona
- [ ] GET /audit/logs con filtros
- [ ] Export CSV auditoria
- [ ] Reportes weekly/monthly generan
- [ ] ROI calcula tiempo ahorrado

---

### FB-10: Pagina Configuracion UI

**Agente Dev:** Agente 4 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_config_page_loads`
- [ ] `test_policy_thresholds_editable`
- [ ] `test_notification_channels_config`
- [ ] `test_api_keys_masked`
- [ ] `test_save_config_persists`

#### Implementacion (Agente 4)

- [ ] `pages/ConfigPage.tsx`
- [ ] Sidebar link
- [ ] App.tsx ruta

#### Verificacion Funcional (Agente 5)

- [ ] Pagina carga sin errores
- [ ] Umbrales editables y guardables
- [ ] API keys enmascaradas
- [ ] Cambios persisten

---

### FB-11: Pagina Auditoria UI

**Agente Dev:** Agente 4 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_audit_page_loads`
- [ ] `test_audit_filters_work`
- [ ] `test_audit_export_csv`
- [ ] `test_audit_shows_actions`

#### Implementacion (Agente 4)

- [ ] `pages/AuditPage.tsx`
- [ ] Sidebar link
- [ ] App.tsx ruta

#### Verificacion Funcional (Agente 5)

- [ ] Pagina carga sin errores
- [ ] Filtros por usuario/fecha/tipo funcionan
- [ ] Export CSV descarga archivo
- [ ] Acciones con timestamp visibles

---

### FB-12: Pagina Reportes Ejecutivos UI

**Agente Dev:** Agente 4 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_executive_page_loads`
- [ ] `test_weekly_report_renders`
- [ ] `test_monthly_report_renders`
- [ ] `test_roi_metrics_displayed`
- [ ] `test_trend_charts_render`

#### Implementacion (Agente 4)

- [ ] `pages/ExecutiveReportsPage.tsx`
- [ ] Sidebar link
- [ ] App.tsx ruta

#### Verificacion Funcional (Agente 5)

- [ ] Pagina carga sin errores
- [ ] Reportes weekly/monthly renderizan
- [ ] Metricas ROI visibles
- [ ] Graficos de tendencia renderizan

---

### FB-13: Pagina Playbooks UI

**Agente Dev:** Agente 4 | **Estado:** 🔴 Pendiente

#### Tests (TDD - Agente 5)

- [ ] `test_playbooks_page_loads`
- [ ] `test_playbook_list_renders`
- [ ] `test_playbook_detail_opens`
- [ ] `test_playbook_run_history`
- [ ] `test_playbook_run_button`

#### Implementacion (Agente 4)

- [ ] `pages/PlaybooksPage.tsx`
- [ ] Sidebar link
- [ ] App.tsx ruta

#### Verificacion Funcional (Agente 5)

- [ ] Pagina carga sin errores
- [ ] Lista de playbooks visible
- [ ] Detalle se abre
- [ ] Historial de ejecuciones funciona
- [ ] Boton ejecutar funciona

---

## Metricas Globales

### Tests

| Tipo                       | Total     | Pasando | Fallando | Cobertura |
| -------------------------- | --------- | ------- | -------- | --------- |
| Unit Tests nuevos          | 0/82      | 0       | 0        | 0%        |
| Integration Tests nuevos   | 0/18      | 0       | 0        | 0%        |
| E2E Tests nuevos           | 0/24      | 0       | 0        | 0%        |
| Verificaciones funcionales | 0/60      | 0       | 0        | 0%        |
| **TOTAL**                  | **0/184** | **0**   | **0**    | **0%**    |

### Archivos

| Tipo           | Creados | Modificados | Total |
| -------------- | ------- | ----------- | ----- |
| Backend Python | 0       | 0           | 0     |
| Frontend TSX   | 0       | 0           | 0     |
| Docker/Config  | 0       | 0           | 0     |
| Tests          | 0       | 0           | 0     |
| **TOTAL**      | **0**   | **0**       | **0** |

---

## Log de Cambios

| Fecha      | Feature | Actividad               | Tests | Resultado |
| ---------- | ------- | ----------------------- | ----- | --------- |
| 2026-02-15 | -       | Plan y Progress creados | 0/184 | 📋        |
|            |         |                         |       |           |

---

## Reglas del Agente 5 (QA)

### Protocolo de Verificacion

```
PARA CADA FEATURE:

1. TESTS ESCRITOS?
   - Si: Continuar
   - No: BLOQUEAR. No se puede implementar sin tests.

2. TESTS PASAN?
   - Si: Continuar a verificacion funcional
   - No: REPORTAR al Agente Dev con:
     * Nombre del test que falla
     * Output del error
     * Archivo y linea

3. VERIFICACION FUNCIONAL PASA?
   - Si: MARCAR como completado en este documento
   - No: REPORTAR al Agente Dev con:
     * Requisito que no se cumple
     * Referencia en FUNCIONALIDADES_FALTANTESV2.md
     * Que falta exactamente

4. ACTUALIZAR PROGRESS:
   - Cambiar [ ] -> [x] para cada item verificado
   - Actualizar contadores de tests
   - Actualizar porcentaje en dashboard
   - Agregar entrada en Log de Cambios
```

### Lo que NUNCA debe hacer el Agente 5

- NUNCA marcar [x] sin ejecutar los tests
- NUNCA marcar [x] si hay tests fallando
- NUNCA marcar [x] sin verificar contra el documento funcional
- NUNCA implementar codigo (solo tests)
- NUNCA asumir que algo funciona sin verificar

---

## Referencias

- [Plan de Construccion](PLAN_FUNCIONALIDADES_FALTANTES.md) - Este plan
- [Funcionalidades Faltantes V2](FUNCIONALIDADES_FALTANTESV2.md) - Documento de referencia funcional
- [Progress Principal](PROGRESS.md) - Estado general del proyecto
- [Plan Original](PLAN.md) - Plan maestro del proyecto
