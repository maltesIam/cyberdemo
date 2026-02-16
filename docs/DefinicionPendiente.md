# Definición de Triggers Automáticos Backend → SoulInTheBot

> **Documento de Definición Pendiente**
> Fecha: 2026-02-13
> Estado: 📋 DEFINICIÓN
> Workstream: W12 (Auto-Triggers)

---

## Resumen Ejecutivo

Este documento define todas las funcionalidades donde el backend de CyberDemo debe llamar automáticamente a SoulInTheBot/Claude para ejecutar acciones inteligentes basadas en eventos, alertas, o cambios de estado.

### Arquitectura de Triggers

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA AUTO-TRIGGERS                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────┐    Trigger    ┌──────────────┐    Mensaje           │
│   │   EVENTO     │──────────────►│   BACKEND    │───────────────►      │
│   │   (Source)   │               │  (Evaluador) │                      │
│   └──────────────┘               └──────────────┘                      │
│         │                              │                               │
│         │                              ▼                               │
│         │                     ┌──────────────┐                         │
│         │                     │   FILTROS    │                         │
│         │                     │  - Severity  │                         │
│         │                     │  - Cooldown  │                         │
│         │                     │  - Dedup     │                         │
│         │                     └──────────────┘                         │
│         │                              │                               │
│         │                              ▼                               │
│         │                     ┌──────────────┐    /investigate         │
│         │                     │   GATEWAY    │───────────────►         │
│         │                     │  (18789)     │                         │
│         │                     └──────────────┘                         │
│         │                              │                               │
│         │                              ▼                               │
│         │                     ┌──────────────┐                         │
│         │                     │ SOULINTHEBOT │                         │
│         │                     │   (Claude)   │                         │
│         │                     └──────────────┘                         │
│         │                              │                               │
│         │         ┌────────────────────┼────────────────────┐          │
│         │         ▼                    ▼                    ▼          │
│         │   ┌──────────┐        ┌──────────┐        ┌──────────┐       │
│         │   │ Contain  │        │ Escalate │        │ Report   │       │
│         │   └──────────┘        └──────────┘        └──────────┘       │
│         │                                                              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Catálogo de Triggers

### Categoría 1: SIEM (Incidentes)

| ID   | Trigger                | Evento                               | Comando a Claude                                 | Prioridad |
| ---- | ---------------------- | ------------------------------------ | ------------------------------------------------ | --------- |
| T1.1 | `incident.created`     | Nuevo incidente creado               | `/investigate {incident_id}`                     | 🔴 Alta   |
| T1.2 | `incident.escalated`   | Incidente escalado a crítico         | `/investigate {incident_id} --priority critical` | 🔴 Alta   |
| T1.3 | `incident.sla_breach`  | SLA de respuesta incumplido          | `/escalate {incident_id} --reason sla_breach`    | 🔴 Alta   |
| T1.4 | `incident.correlation` | Múltiples incidentes correlacionados | `/correlate {incident_ids}`                      | 🟡 Media  |
| T1.5 | `incident.reopened`    | Incidente reabierto                  | `/reinvestigate {incident_id}`                   | 🟡 Media  |

#### Detalle T1.1: `incident.created`

```python
# Trigger: Nuevo incidente creado en SIEM
# Condiciones:
#   - severity IN ['critical', 'high']
#   - status = 'new'
#   - no hay investigación activa para este incidente
# Cooldown: 5 minutos por incidente
# Acción: Investigación automática completa

@event_handler("incident.created")
async def on_incident_created(incident: Incident):
    if incident.severity not in ["critical", "high"]:
        return  # Ignorar low/medium para evitar ruido

    await gateway.send_message(
        f"/investigate {incident.incident_id}",
        metadata={
            "trigger": "incident.created",
            "severity": incident.severity,
            "source": "auto-trigger"
        }
    )
```

#### Detalle T1.2: `incident.escalated`

```python
# Trigger: Incidente cambia de severity a critical
# Condiciones:
#   - previous_severity != 'critical'
#   - new_severity = 'critical'
# Acción: Re-investigación con prioridad máxima

@event_handler("incident.updated")
async def on_incident_escalated(incident: Incident, changes: dict):
    if changes.get("severity") == "critical":
        await gateway.send_message(
            f"/investigate {incident.incident_id} --priority critical --reason escalated",
            metadata={"trigger": "incident.escalated"}
        )
```

#### Detalle T1.3: `incident.sla_breach`

```python
# Trigger: Tiempo de respuesta excede SLA
# Condiciones:
#   - incident.status IN ['new', 'in_progress']
#   - time_since_created > sla_threshold[severity]
# SLA Thresholds:
#   - critical: 15 minutos
#   - high: 1 hora
#   - medium: 4 horas
# Acción: Notificar y escalar

@scheduled_task(interval="1m")
async def check_sla_breaches():
    breached = await siem.get_sla_breached_incidents()
    for incident in breached:
        await gateway.send_message(
            f"/escalate {incident.incident_id} --reason sla_breach --elapsed {incident.elapsed_time}",
            metadata={"trigger": "incident.sla_breach"}
        )
```

---

### Categoría 2: EDR (Detecciones)

| ID   | Trigger                 | Evento                        | Comando a Claude                                  | Prioridad |
| ---- | ----------------------- | ----------------------------- | ------------------------------------------------- | --------- |
| T2.1 | `detection.created`     | Nueva detección de amenaza    | `/analyze-detection {detection_id}`               | 🔴 Alta   |
| T2.2 | `detection.propagation` | Mismo hash en múltiples hosts | `/hunt {sha256} --propagation`                    | 🔴 Alta   |
| T2.3 | `containment.failed`    | Fallo en contención           | `/retry-containment {device_id} --reason {error}` | 🔴 Alta   |
| T2.4 | `containment.completed` | Host contenido exitosamente   | `/postmortem {incident_id}`                       | 🟢 Baja   |
| T2.5 | `containment.lifted`    | Contención levantada          | `/verify-clean {device_id}`                       | 🟡 Media  |

#### Detalle T2.1: `detection.created`

```python
# Trigger: EDR detecta nueva amenaza
# Condiciones:
#   - detection.severity IN ['critical', 'high']
#   - detection.status = 'new'
# Acción: Análisis rápido de la detección

@event_handler("detection.created")
async def on_detection_created(detection: Detection):
    if detection.severity in ["critical", "high"]:
        await gateway.send_message(
            f"/analyze-detection {detection.detection_id}",
            metadata={
                "trigger": "detection.created",
                "technique": detection.technique_id,
                "asset": detection.asset_id
            }
        )
```

#### Detalle T2.2: `detection.propagation`

```python
# Trigger: El mismo hash aparece en múltiples hosts
# Condiciones:
#   - hosts_affected >= propagation_threshold (default: 3)
#   - time_window <= 1 hora
# Acción: Hunting proactivo y posible contención masiva

@event_handler("hunt.completed")
async def on_propagation_detected(hunt_result: HuntResult):
    if hunt_result.total_hosts_found >= 3:
        await gateway.send_message(
            f"/hunt {hunt_result.sha256} --propagation --hosts {hunt_result.total_hosts_found}",
            metadata={
                "trigger": "detection.propagation",
                "hosts": hunt_result.hosts,
                "urgency": "critical"
            }
        )
```

#### Detalle T2.3: `containment.failed`

```python
# Trigger: Intento de contención falló
# Condiciones:
#   - containment.status = 'failed'
#   - retry_count < max_retries (default: 3)
# Acción: Reintentar con estrategia alternativa

@event_handler("containment.result")
async def on_containment_failed(result: ContainmentResult):
    if result.status == "failed":
        await gateway.send_message(
            f"/retry-containment {result.device_id} --reason '{result.reason}' --attempt {result.retry_count + 1}",
            metadata={
                "trigger": "containment.failed",
                "previous_error": result.reason
            }
        )
```

---

### Categoría 3: Intel (Threat Intelligence)

| ID   | Trigger                 | Evento                          | Comando a Claude                             | Prioridad |
| ---- | ----------------------- | ------------------------------- | -------------------------------------------- | --------- |
| T3.1 | `intel.new_ioc`         | Nuevo IOC recibido              | `/hunt-ioc {type} {value}`                   | 🟡 Media  |
| T3.2 | `intel.ioc_match`       | IOC coincide con activo interno | `/alert-ioc-match {indicator_id} {asset_id}` | 🔴 Alta   |
| T3.3 | `intel.campaign_update` | Nueva campaña de amenazas       | `/brief-campaign {campaign_id}`              | 🟡 Media  |
| T3.4 | `intel.attribution`     | Atribución a actor conocido     | `/threat-actor-brief {actor_id}`             | 🟢 Baja   |

#### Detalle T3.1: `intel.new_ioc`

```python
# Trigger: Feed de inteligencia entrega nuevo IOC
# Condiciones:
#   - ioc.verdict IN ['malicious', 'suspicious']
#   - ioc.confidence >= 70%
# Acción: Búsqueda proactiva en infraestructura

@event_handler("intel.feed_update")
async def on_new_ioc(indicator: IntelIndicator):
    if indicator.verdict in ["malicious", "suspicious"]:
        await gateway.send_message(
            f"/hunt-ioc {indicator.indicator_type} {indicator.value}",
            metadata={
                "trigger": "intel.new_ioc",
                "sources": indicator.sources,
                "confidence": indicator.vt_score
            }
        )
```

#### Detalle T3.2: `intel.ioc_match`

```python
# Trigger: IOC conocido encontrado en activo interno
# Condiciones:
#   - match.confidence >= 90%
#   - asset.status = 'active'
# Acción: Alerta inmediata e investigación

@event_handler("intel.correlation")
async def on_ioc_match(match: IOCMatch):
    await gateway.send_message(
        f"/alert-ioc-match {match.indicator_id} {match.asset_id} --verdict {match.indicator.verdict}",
        metadata={
            "trigger": "intel.ioc_match",
            "priority": "critical",
            "auto_contain": match.indicator.verdict == "malicious"
        }
    )
```

---

### Categoría 4: CTEM (Vulnerabilidades)

| ID   | Trigger                  | Evento                       | Comando a Claude                                  | Prioridad |
| ---- | ------------------------ | ---------------------------- | ------------------------------------------------- | --------- |
| T4.1 | `ctem.critical_vuln`     | Nueva vulnerabilidad crítica | `/assess-vuln {cve_id} {asset_id}`                | 🔴 Alta   |
| T4.2 | `ctem.risk_change`       | Cambio en nivel de riesgo    | `/risk-report {asset_id} --change {old} to {new}` | 🟡 Media  |
| T4.3 | `ctem.exploit_available` | Exploit público disponible   | `/prioritize-patch {cve_id}`                      | 🔴 Alta   |
| T4.4 | `ctem.asset_exposed`     | Activo expuesto a internet   | `/exposure-analysis {asset_id}`                   | 🟡 Media  |

#### Detalle T4.1: `ctem.critical_vuln`

```python
# Trigger: Scanner encuentra vulnerabilidad crítica
# Condiciones:
#   - vuln.cvss >= 9.0
#   - vuln.exploitable = True
#   - asset.criticality IN ['high', 'critical']
# Acción: Evaluación de impacto y priorización

@event_handler("ctem.scan_completed")
async def on_critical_vuln(finding: VulnFinding):
    if finding.cvss >= 9.0 and finding.exploitable:
        await gateway.send_message(
            f"/assess-vuln {finding.cve_id} {finding.asset_id} --cvss {finding.cvss}",
            metadata={
                "trigger": "ctem.critical_vuln",
                "exploit_available": finding.exploit_available,
                "asset_criticality": finding.asset.criticality
            }
        )
```

#### Detalle T4.3: `ctem.exploit_available`

```python
# Trigger: Se publica exploit para CVE conocido
# Condiciones:
#   - cve existe en activos del cliente
#   - exploit.maturity IN ['poc', 'weaponized']
# Acción: Priorizar parche urgente

@event_handler("intel.exploit_feed")
async def on_exploit_available(exploit: ExploitInfo):
    affected_assets = await ctem.get_assets_by_cve(exploit.cve_id)
    if affected_assets:
        await gateway.send_message(
            f"/prioritize-patch {exploit.cve_id} --affected {len(affected_assets)} --maturity {exploit.maturity}",
            metadata={
                "trigger": "ctem.exploit_available",
                "assets": [a.asset_id for a in affected_assets]
            }
        )
```

---

### Categoría 5: Approvals (Workflow Humano)

| ID   | Trigger              | Evento                    | Comando a Claude                                  | Prioridad |
| ---- | -------------------- | ------------------------- | ------------------------------------------------- | --------- |
| T5.1 | `approval.approved`  | Aprobación recibida       | `/execute-containment {incident_id}`              | 🔴 Alta   |
| T5.2 | `approval.rejected`  | Aprobación rechazada      | `/mark-fp {incident_id} --reason rejected`        | 🟡 Media  |
| T5.3 | `approval.timeout`   | Timeout sin respuesta     | `/escalate-approval {incident_id}`                | 🔴 Alta   |
| T5.4 | `approval.delegated` | Delegado a otro aprobador | `/notify-delegation {incident_id} {new_approver}` | 🟢 Baja   |

#### Detalle T5.1: `approval.approved`

```python
# Trigger: Humano aprueba acción de contención
# Condiciones:
#   - approval.status = 'approved'
#   - approval.action = 'contain'
# Acción: Ejecutar contención previamente solicitada

@event_handler("approval.decision")
async def on_approval_approved(approval: ApprovalStatus):
    if approval.status == "approved":
        await gateway.send_message(
            f"/execute-containment {approval.incident_id} --approved-by {approval.decided_by}",
            metadata={
                "trigger": "approval.approved",
                "approver": approval.decided_by,
                "timestamp": approval.decided_at
            }
        )
```

#### Detalle T5.3: `approval.timeout`

```python
# Trigger: Solicitud de aprobación sin respuesta
# Condiciones:
#   - approval.status = 'pending'
#   - time_since_request > approval_timeout (default: 30 min)
# Acción: Escalar a siguiente nivel

@scheduled_task(interval="5m")
async def check_approval_timeouts():
    pending = await approvals.get_timed_out()
    for approval in pending:
        await gateway.send_message(
            f"/escalate-approval {approval.incident_id} --elapsed {approval.elapsed_time}",
            metadata={
                "trigger": "approval.timeout",
                "original_request_time": approval.requested_at
            }
        )
```

---

### Categoría 6: Reports (Documentación)

| ID   | Trigger             | Evento                | Comando a Claude                     | Prioridad |
| ---- | ------------------- | --------------------- | ------------------------------------ | --------- |
| T6.1 | `incident.closed`   | Incidente cerrado     | `/generate-postmortem {incident_id}` | 🟢 Baja   |
| T6.2 | `ticket.created`    | Ticket creado         | `/enrich-ticket {ticket_id}`         | 🟢 Baja   |
| T6.3 | `report.scheduled`  | Reporte programado    | `/daily-summary`                     | 🟢 Baja   |
| T6.4 | `metrics.threshold` | Métrica excede umbral | `/alert-metrics {metric} {value}`    | 🟡 Media  |

#### Detalle T6.1: `incident.closed`

```python
# Trigger: Incidente marcado como cerrado
# Condiciones:
#   - incident.status = 'closed'
#   - incident.resolution IN ['contained', 'remediated']
# Acción: Generar postmortem automático

@event_handler("incident.status_changed")
async def on_incident_closed(incident: Incident, old_status: str):
    if incident.status == "closed" and incident.resolution:
        await gateway.send_message(
            f"/generate-postmortem {incident.incident_id}",
            metadata={
                "trigger": "incident.closed",
                "resolution": incident.resolution,
                "duration": incident.time_to_close
            }
        )
```

#### Detalle T6.3: `report.scheduled`

```python
# Trigger: Hora programada para reportes
# Condiciones:
#   - current_time = scheduled_time (e.g., 08:00 UTC)
# Acción: Generar resumen diario

@scheduled_task(cron="0 8 * * *")  # 8:00 AM UTC diario
async def daily_summary_report():
    await gateway.send_message(
        "/daily-summary --period 24h",
        metadata={
            "trigger": "report.scheduled",
            "type": "daily_summary"
        }
    )
```

---

### Categoría 7: System (Salud del Sistema)

| ID   | Trigger                     | Evento                         | Comando a Claude               | Prioridad |
| ---- | --------------------------- | ------------------------------ | ------------------------------ | --------- |
| T7.1 | `system.high_volume`        | Alto volumen de alertas        | `/triage-bulk --count {count}` | 🟡 Media  |
| T7.2 | `system.connection_lost`    | Pérdida de conexión con source | `/diagnostic {source}`         | 🔴 Alta   |
| T7.3 | `system.queue_backlog`      | Cola de procesamiento llena    | `/prioritize-queue`            | 🟡 Media  |
| T7.4 | `system.resource_exhausted` | Recursos del sistema agotados  | `/scale-alert`                 | 🔴 Alta   |

---

## Resumen de Triggers

### Por Prioridad

| Prioridad | Cantidad | Triggers                                                                     |
| --------- | -------- | ---------------------------------------------------------------------------- |
| 🔴 Alta   | 14       | T1.1, T1.2, T1.3, T2.1, T2.2, T2.3, T3.2, T4.1, T4.3, T5.1, T5.3, T7.2, T7.4 |
| 🟡 Media  | 10       | T1.4, T1.5, T2.5, T3.1, T3.3, T4.2, T4.4, T5.2, T6.4, T7.1, T7.3             |
| 🟢 Baja   | 5        | T2.4, T3.4, T5.4, T6.1, T6.2, T6.3                                           |
| **Total** | **29**   |                                                                              |

### Por Categoría

| Categoría | Triggers | Descripción                |
| --------- | -------- | -------------------------- |
| SIEM      | 5        | Incidentes y correlaciones |
| EDR       | 5        | Detecciones y contención   |
| Intel     | 4        | Threat intelligence        |
| CTEM      | 4        | Vulnerabilidades           |
| Approvals | 4        | Workflow humano            |
| Reports   | 4        | Documentación automática   |
| System    | 4        | Salud del sistema          |
| **Total** | **30**   |                            |

---

## Implementación Técnica

### Componentes Necesarios

```
backend/src/
├── triggers/
│   ├── __init__.py
│   ├── base.py              # TriggerHandler base class
│   ├── gateway_client.py    # Cliente para llamar a SoulInTheBot
│   ├── filters.py           # Filtros (severity, cooldown, dedup)
│   ├── scheduler.py         # Tareas programadas
│   │
│   ├── siem/
│   │   ├── incident_created.py
│   │   ├── incident_escalated.py
│   │   ├── incident_sla_breach.py
│   │   ├── incident_correlation.py
│   │   └── incident_reopened.py
│   │
│   ├── edr/
│   │   ├── detection_created.py
│   │   ├── detection_propagation.py
│   │   ├── containment_failed.py
│   │   ├── containment_completed.py
│   │   └── containment_lifted.py
│   │
│   ├── intel/
│   │   ├── new_ioc.py
│   │   ├── ioc_match.py
│   │   ├── campaign_update.py
│   │   └── attribution.py
│   │
│   ├── ctem/
│   │   ├── critical_vuln.py
│   │   ├── risk_change.py
│   │   ├── exploit_available.py
│   │   └── asset_exposed.py
│   │
│   ├── approvals/
│   │   ├── approved.py
│   │   ├── rejected.py
│   │   ├── timeout.py
│   │   └── delegated.py
│   │
│   ├── reports/
│   │   ├── incident_closed.py
│   │   ├── ticket_created.py
│   │   ├── scheduled.py
│   │   └── metrics_threshold.py
│   │
│   └── system/
│       ├── high_volume.py
│       ├── connection_lost.py
│       ├── queue_backlog.py
│       └── resource_exhausted.py
```

### Gateway Client

```python
# backend/src/triggers/gateway_client.py

import httpx
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class TriggerMetadata:
    trigger_id: str
    trigger_type: str
    source: str
    timestamp: datetime
    priority: str
    extra: Dict[str, Any]

class GatewayClient:
    """Cliente para enviar mensajes a SoulInTheBot via Gateway."""

    def __init__(
        self,
        gateway_url: str = "http://localhost:18789",
        channel: str = "cyberdemo",
        timeout: float = 30.0
    ):
        self.gateway_url = gateway_url
        self.channel = channel
        self.timeout = timeout
        self._cooldowns: Dict[str, datetime] = {}

    async def send_command(
        self,
        command: str,
        metadata: TriggerMetadata,
        cooldown_key: Optional[str] = None,
        cooldown_seconds: int = 300
    ) -> Optional[str]:
        """Envía comando a SoulInTheBot con control de cooldown."""

        # Check cooldown
        if cooldown_key:
            if self._is_in_cooldown(cooldown_key):
                return None
            self._set_cooldown(cooldown_key, cooldown_seconds)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.gateway_url}/api/messages",
                json={
                    "channel": self.channel,
                    "message": command,
                    "metadata": {
                        "trigger_id": metadata.trigger_id,
                        "trigger_type": metadata.trigger_type,
                        "source": metadata.source,
                        "timestamp": metadata.timestamp.isoformat(),
                        "priority": metadata.priority,
                        **metadata.extra
                    }
                }
            )
            response.raise_for_status()
            return response.json().get("response_id")

    def _is_in_cooldown(self, key: str) -> bool:
        if key not in self._cooldowns:
            return False
        return datetime.utcnow() < self._cooldowns[key]

    def _set_cooldown(self, key: str, seconds: int):
        self._cooldowns[key] = datetime.utcnow() + timedelta(seconds=seconds)
```

### Configuración de Triggers

```yaml
# backend/config/triggers.yaml

triggers:
  enabled: true
  gateway_url: "http://localhost:18789"
  channel: "cyberdemo"

  # Filtros globales
  filters:
    min_severity: "medium" # Ignorar low severity
    dedup_window_seconds: 300
    max_rate_per_minute: 10

  # Configuración por categoría
  siem:
    incident_created:
      enabled: true
      severity_filter: ["critical", "high"]
      cooldown_seconds: 300

    incident_escalated:
      enabled: true
      cooldown_seconds: 60

    incident_sla_breach:
      enabled: true
      check_interval_seconds: 60
      sla_thresholds:
        critical: 900 # 15 min
        high: 3600 # 1 hora
        medium: 14400 # 4 horas

  edr:
    detection_created:
      enabled: true
      severity_filter: ["critical", "high"]
      cooldown_seconds: 120

    detection_propagation:
      enabled: true
      host_threshold: 3
      time_window_seconds: 3600

    containment_failed:
      enabled: true
      max_retries: 3

  intel:
    new_ioc:
      enabled: true
      verdict_filter: ["malicious", "suspicious"]
      auto_hunt: true

    ioc_match:
      enabled: true
      auto_contain_malicious: true

  ctem:
    critical_vuln:
      enabled: true
      cvss_threshold: 9.0
      exploitable_only: true

    exploit_available:
      enabled: true
      maturity_filter: ["poc", "weaponized"]

  approvals:
    timeout:
      enabled: true
      timeout_seconds: 1800 # 30 min
      check_interval_seconds: 300

  reports:
    scheduled:
      enabled: true
      daily_summary_cron: "0 8 * * *"
      weekly_report_cron: "0 9 * * 1"

  system:
    high_volume:
      enabled: true
      threshold_per_hour: 100

    connection_lost:
      enabled: true
      check_interval_seconds: 60
```

---

## Dependencias

### Para implementar W12 (Auto-Triggers):

| Dependencia          | Estado | Descripción               |
| -------------------- | ------ | ------------------------- |
| W6: APIs Backend     | ✅     | APIs para consultar datos |
| W9: Skill            | ✅     | Skill `/investigate` etc. |
| W11: MCP Servers     | 🔴     | Opcional (REST funciona)  |
| Gateway SoulInTheBot | ✅     | Endpoint `/api/messages`  |

### Estimación de Esfuerzo

| Componente            | Esfuerzo | Descripción               |
| --------------------- | -------- | ------------------------- |
| Gateway Client        | 2h       | Cliente HTTP con cooldown |
| Trigger Base          | 2h       | Clase base y filtros      |
| SIEM Triggers (5)     | 4h       | 5 handlers                |
| EDR Triggers (5)      | 4h       | 5 handlers                |
| Intel Triggers (4)    | 3h       | 4 handlers                |
| CTEM Triggers (4)     | 3h       | 4 handlers                |
| Approval Triggers (4) | 3h       | 4 handlers                |
| Report Triggers (4)   | 2h       | 4 handlers                |
| System Triggers (4)   | 2h       | 4 handlers                |
| Scheduler             | 2h       | APScheduler integration   |
| Config YAML           | 1h       | Configuración             |
| Tests                 | 8h       | Unit + integration        |
| **Total**             | **36h**  | ~4.5 días                 |

---

## Priorización de Implementación

### Fase 1: MVP (Críticos)

1. `incident.created` - Investigación automática
2. `approval.approved` - Ejecución post-aprobación
3. `containment.failed` - Reintento automático

### Fase 2: Core SOC

4. `detection.created` - Análisis de detecciones
5. `detection.propagation` - Hunting proactivo
6. `incident.sla_breach` - Alertas de SLA
7. `approval.timeout` - Escalación de aprobaciones

### Fase 3: Intelligence

8. `intel.ioc_match` - Correlación con IOCs
9. `ctem.critical_vuln` - Vulnerabilidades críticas
10. `ctem.exploit_available` - Priorización de parches

### Fase 4: Reportes y Métricas

11. `incident.closed` - Postmortems automáticos
12. `report.scheduled` - Reportes programados
13. `system.high_volume` - Triage masivo

---

## Log de Definición

| Fecha      | Cambio                                       |
| ---------- | -------------------------------------------- |
| 2026-02-13 | Documento creado con 30 triggers definidos   |
| 2026-02-13 | Arquitectura técnica y componentes definidos |
| 2026-02-13 | Estimación de esfuerzo: ~36 horas            |

---

## Próximos Pasos

1. [ ] Revisar y aprobar definición
2. [ ] Añadir W12 a PROGRESS.md
3. [ ] Implementar Gateway Client
4. [ ] Implementar Fase 1 (MVP)
5. [ ] Tests de integración con SoulInTheBot
