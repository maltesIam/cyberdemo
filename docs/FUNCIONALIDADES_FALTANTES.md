# Funcionalidades Faltantes: Análisis Comparativo

**Documento de comparación:** Plan_Demo_SOC_AI_Agent_v3.md.docx vs PLAN.md
**Fecha:** 13 Febrero 2026

---

## Resumen Ejecutivo

Este documento identifica las funcionalidades, requisitos y definiciones del documento original de funcionalidad que **NO están incluidas** en el plan de construcción actual (PLAN.md), organizadas por fase.

---

## Fase 2: Funcionalidades NO Incluidas

### 2.1 Grafana Observability Stack

**Estado:** NO INCLUIDO en el plan actual

El documento original especifica un stack completo de observabilidad con Grafana que no está en el plan:

| Componente | Descripción                            | Puerto |
| ---------- | -------------------------------------- | ------ |
| Grafana    | Dashboards de métricas y visualización | 3000   |
| Prometheus | Métricas del agente y sistema          | 9090   |
| Loki       | Logs centralizados                     | 3100   |
| Tempo      | Trazas distribuidas                    | 3200   |

**Dashboards Grafana requeridos:**

- SOC Operations Overview
- Agent Performance Metrics
- Containment Success Rate
- MTTR/MTTD Analytics
- Human Approval Latency

**Métricas a exponer:**

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

### 2.2 Algoritmo de Confidence Score

**Estado:** PARCIALMENTE INCLUIDO (mencionado pero no detallado)

El documento original especifica el algoritmo completo de cálculo:

```python
def calculate_confidence_score(detection, intel, ctem, propagation):
    """
    Calcula el score de confianza para decisiones de contención.

    Componentes:
    - Intel Score (40%): VT score, labels, sources
    - Behavior Score (30%): MITRE technique, cmdline analysis
    - Context Score (20%): CTEM risk, asset criticality
    - Propagation Score (10%): Número de hosts afectados

    Returns: 0-100 score
    """
    intel_score = calculate_intel_component(intel)      # 0-40
    behavior_score = calculate_behavior_component(detection)  # 0-30
    context_score = calculate_context_component(ctem)   # 0-20
    propagation_score = calculate_propagation_component(propagation)  # 0-10

    return intel_score + behavior_score + context_score + propagation_score
```

**Falta en el plan:**

- Implementación detallada de `calculate_intel_component`
- Pesos configurables por tipo de amenaza
- Tests unitarios para cada componente del score
- Documentación de umbrales por escenario

### 2.3 SKILL.md Completo para SoulInTheBot

**Estado:** NO INCLUIDO (solo estructura vacía)

El documento original especifica el contenido completo del SKILL.md:

```markdown
# SOC Analyst Skill

## Rol

Eres un analista SOC Tier-1 que investiga alertas de seguridad...

## Workflow

1. Recibir alerta → Parsear datos básicos
2. Enriquecer → Intel + CTEM + Propagación
3. Calcular score → Aplicar policy
4. Ejecutar → Auto-contain o solicitar aprobación
5. Cerrar → Postmortem + Ticket

## Herramientas Disponibles

[Lista de tools con ejemplos de uso]

## Políticas de Contención

[Reglas deterministas]

## Ejemplos de Investigación

[Casos de ejemplo completos]
```

### 2.4 Hooks de SoulInTheBot

**Estado:** NO INCLUIDO

El documento original especifica hooks para integración:

```yaml
# hooks.yaml
on_tool_start:
  - log_to_agent_events

on_tool_complete:
  - update_timeline
  - notify_frontend

on_containment:
  - verify_policy
  - create_audit_log
  - notify_channel

on_approval_received:
  - resume_workflow
  - update_incident
```

### 2.5 Visualización de Superficie de Ataque con Capas

**Estado:** PARCIALMENTE INCLUIDO (mencionado pero sin detalle)

El documento original especifica capas interactivas:

| Capa        | Color Base     | Datos                   | Interacción      |
| ----------- | -------------- | ----------------------- | ---------------- |
| Base        | Gris           | Todos los assets        | Click → detalle  |
| EDR         | Rojo           | Assets con detecciones  | Filtro severidad |
| SIEM        | Naranja        | Assets en incidentes    | Filtro estado    |
| CTEM        | Amarillo/Verde | Riesgo vulnerabilidades | Gradiente        |
| Threats     | Morado         | IOCs relacionados       | Conexiones       |
| Containment | Azul           | Hosts contenidos        | Timeline         |

**Controles UI faltantes:**

- Toggle por capa
- Slider de tiempo (ver evolución)
- Zoom semántico (cluster → individual)
- Export de vista actual

---

## Fase 3: Funcionalidades NO Incluidas

### 3.1 Automatización Basada en Playbooks

**Estado:** MENCIONADO pero sin detalle de implementación

El documento original especifica playbooks completos:

```yaml
# playbooks/contain_and_investigate.yaml
name: contain_and_investigate
description: Contención automática seguida de investigación profunda
triggers:
  - high_confidence_malware
  - ransomware_detected

steps:
  - action: edr.contain_host
    params:
      reason: "Auto-containment: ${incident.title}"
    on_error: notify_human

  - action: edr.collect_artifacts
    params:
      types: [memory_dump, registry, prefetch]
    timeout: 300

  - action: intel.deep_scan
    params:
      artifacts: ${previous.result}

  - action: reports.generate_ioc_report
    params:
      format: stix2.1
```

**Playbooks requeridos:**

1. `contain_and_investigate` - Contención + recolección
2. `vip_escalation` - Escalación para VIPs
3. `false_positive_closure` - Cierre automático de FPs
4. `lateral_movement_hunt` - Búsqueda de movimiento lateral
5. `ransomware_response` - Respuesta a ransomware

### 3.2 Sistema de Notificaciones

**Estado:** NO INCLUIDO

El documento original especifica canales de notificación:

```yaml
# notifications.yaml
channels:
  slack:
    webhook_url: ${SLACK_WEBHOOK}
    templates:
      containment_auto: "🔒 Host {hostname} contenido automáticamente"
      approval_needed: "⚠️ Aprobación requerida para {hostname}"

  email:
    smtp_server: ${SMTP_SERVER}
    templates:
      executive_summary: templates/email/executive.html

  teams:
    webhook_url: ${TEAMS_WEBHOOK}
```

### 3.3 Canal de Colaboración SOC (collab-messages)

**Estado:** ÍNDICE DEFINIDO pero sin implementación

El documento original especifica:

- Chat embebido en el dashboard
- Menciones a usuarios/assets
- Adjuntos de evidencia
- Integración con timeline del agente
- Historial buscable

**Endpoints faltantes:**

```
POST /collab/messages
GET /collab/messages?incident_id={id}
POST /collab/messages/{id}/reactions
DELETE /collab/messages/{id}
```

---

## Fase 4: Funcionalidades NO Incluidas

### 4.1 Machine Learning para Detección de Anomalías

**Estado:** NO INCLUIDO

El documento original menciona:

- Modelo de baseline de comportamiento por usuario
- Detección de anomalías en comandos
- Clustering de incidentes similares
- Predicción de criticidad

### 4.2 Integración con EDR Real (CrowdStrike API)

**Estado:** NO INCLUIDO (solo mock)

El documento original especifica modo dual:

```python
# config.yaml
edr:
  mode: mock  # o 'live'
  live:
    provider: crowdstrike
    client_id: ${CS_CLIENT_ID}
    client_secret: ${CS_CLIENT_SECRET}
    base_url: https://api.crowdstrike.com
```

### 4.3 Integración con SIEM Real (Microsoft Sentinel)

**Estado:** NO INCLUIDO (solo mock)

```python
# config.yaml
siem:
  mode: mock  # o 'live'
  live:
    provider: sentinel
    tenant_id: ${AZURE_TENANT_ID}
    workspace_id: ${SENTINEL_WORKSPACE}
```

### 4.4 Sistema de Auditoría Completo

**Estado:** PARCIAL (solo agent-events)

El documento original especifica:

- Audit log inmutable (blockchain-like)
- Firma digital de acciones
- Retention policies
- Export para compliance (SOC2, ISO27001)

### 4.5 Multi-tenancy

**Estado:** NO INCLUIDO

- Separación por organización
- Configuración de políticas por tenant
- Dashboards aislados
- RBAC granular

---

## Comparativa de Escenarios Demo

### Escenarios Definidos en Original vs Plan

| Escenario                       | Original | Plan | Estado   |
| ------------------------------- | -------- | ---- | -------- |
| 1. Auto-containment workstation | ✅       | ✅   | INCLUIDO |
| 2. VIP Human-in-the-Loop        | ✅       | ✅   | INCLUIDO |
| 3. False Positive               | ✅       | ✅   | INCLUIDO |
| 4. Ransomware multi-host        | ✅       | ❌   | FALTANTE |
| 5. Insider Threat               | ✅       | ❌   | FALTANTE |
| 6. Supply Chain Attack          | ✅       | ❌   | FALTANTE |

### Escenarios Faltantes (Detalle)

#### Escenario 4: Ransomware Multi-Host

```
Trigger: Detección de cifrado masivo en 5+ hosts
Comportamiento esperado:
1. Detectar primer host
2. Hunt hash → encontrar 5 hosts
3. Contención masiva coordinada
4. Notificación ejecutiva
5. Playbook de response
```

#### Escenario 5: Insider Threat

```
Trigger: Usuario con acceso privilegiado exfiltración datos
Comportamiento esperado:
1. Detección de volumen anómalo
2. Correlación con horario/ubicación
3. Requiere aprobación de HR
4. Preservación de evidencia legal
```

#### Escenario 6: Supply Chain Attack

```
Trigger: Software legítimo comprometido
Comportamiento esperado:
1. Detección de comportamiento anómalo en app conocida
2. Verificación de hash vs vendor
3. Alerta de supply chain
4. Hunting organizacional
```

---

## Componentes de UI Faltantes

### Páginas NO Incluidas en el Plan

1. **Página de Configuración**
   - Umbrales del Policy Engine
   - Integración de canales
   - API keys
   - Preferencias de notificación

2. **Página de Auditoría**
   - Log de todas las acciones
   - Filtros por usuario/fecha/tipo
   - Export para compliance

3. **Página de Reportes Ejecutivos**
   - Resumen semanal/mensual
   - Tendencias de amenazas
   - ROI del agente (tiempo ahorrado)

4. **Página de Playbooks**
   - Editor visual de playbooks
   - Historial de ejecuciones
   - Métricas por playbook

---

## APIs Faltantes

### Endpoints NO Definidos en el Plan

```
# Configuración
GET /config/policy
PUT /config/policy
GET /config/notifications
PUT /config/notifications

# Playbooks
GET /playbooks
POST /playbooks
GET /playbooks/{id}/runs
POST /playbooks/{id}/run

# Auditoría
GET /audit/logs
GET /audit/logs/export

# Reportes
GET /reports/executive/weekly
GET /reports/executive/monthly
GET /reports/roi

# Colaboración
POST /collab/messages
GET /collab/channels
WebSocket /collab/ws
```

---

## Integraciones Faltantes

### Sistemas NO Incluidos en el Plan

| Sistema         | Tipo             | Prioridad | Complejidad |
| --------------- | ---------------- | --------- | ----------- |
| ServiceNow      | Ticketing        | Alta      | Media       |
| PagerDuty       | Alerting         | Alta      | Baja        |
| Splunk          | SIEM alternativo | Media     | Alta        |
| Slack           | Notificaciones   | Alta      | Baja        |
| Microsoft Teams | Notificaciones   | Media     | Baja        |
| TheHive         | Case Management  | Media     | Media       |
| MISP            | Threat Intel     | Baja      | Media       |

---

## Documentación Faltante

### Documentos NO Planificados

1. **Guía de Usuario**
   - Tutorial de navegación
   - Glosario de términos SOC
   - FAQ

2. **Guía de Administrador**
   - Instalación completa
   - Configuración avanzada
   - Troubleshooting

3. **Guía de Integración**
   - API Reference completa
   - Webhooks
   - MCP Protocol docs

4. **Runbooks Operativos**
   - Mantenimiento de índices
   - Backup/Restore
   - Escalado

---

## Resumen de Gaps por Prioridad

### Prioridad Alta (Crítico para Demo)

- [ ] Algoritmo completo de Confidence Score
- [ ] SKILL.md con contenido completo
- [ ] Capas de visualización en superficie de ataque
- [ ] 3 escenarios adicionales (Ransomware, Insider, Supply Chain)

### Prioridad Media (Mejora significativa)

- [ ] Grafana Observability Stack
- [ ] Sistema de notificaciones
- [ ] Canal de colaboración
- [ ] Playbooks automatizados
- [ ] Página de configuración UI

### Prioridad Baja (Nice to Have)

- [ ] ML para anomalías
- [ ] Multi-tenancy
- [ ] Integraciones con sistemas reales
- [ ] Auditoría completa con firma digital

---

## Próximos Pasos

1. Crear plan de construcción para funcionalidades faltantes de Prioridad Alta
2. Estimar esfuerzo para Prioridad Media
3. Documentar como "Future Work" las de Prioridad Baja

---

_Documento generado comparando Plan_Demo_SOC_AI_Agent_v3.md.docx vs PLAN.md_
