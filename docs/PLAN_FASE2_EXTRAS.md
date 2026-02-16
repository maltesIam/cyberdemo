# Plan de Construcción: Funcionalidades Faltantes

**Versión:** 1.0
**Fecha:** 13 Febrero 2026
**Referencia:** FUNCIONALIDADES_FALTANTES.md

---

## 0. Visión General

Este plan cubre las funcionalidades identificadas como faltantes en el análisis comparativo, organizadas en fases incrementales que se construyen sobre la infraestructura existente del plan original.

### Dependencias del Plan Original

Este plan **requiere** que las siguientes fases del plan original estén completadas:

- [x] Fase 1: Infraestructura Base
- [ ] Fase 2: Generadores de Datos (requerido)
- [ ] Fase 3: APIs Backend (requerido)
- [ ] Fase 4: Frontend (requerido)
- [ ] Fase 5: Skill SoulInTheBot (parcial)
- [ ] Fase 6: Tests E2E (parcial)
- [ ] Fase 7: MCP Servers (requerido)

---

## Fase A: Observabilidad (Grafana Stack)

**Duración estimada:** 3-4 días
**Prioridad:** Media
**Dependencias:** Docker Compose funcional

### A.1 Infraestructura de Observabilidad

#### Docker Compose Additions

```yaml
# docker/docker-compose.observability.yml
services:
  prometheus:
    image: prom/prometheus:v2.47.0
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"

  grafana:
    image: grafana/grafana:10.2.0
    ports:
      - "3030:3000" # 3030 para no conflictar con frontend
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning
      - ./grafana/dashboards:/var/lib/grafana/dashboards
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false

  loki:
    image: grafana/loki:2.9.0
    ports:
      - "3100:3100"
    volumes:
      - ./loki/loki-config.yml:/etc/loki/local-config.yaml
      - loki-data:/loki

volumes:
  prometheus-data:
  grafana-data:
  loki-data:
```

#### Tareas

| Tarea                | Tests Primero             | Implementación                     |
| -------------------- | ------------------------- | ---------------------------------- |
| Prometheus config    | Test: scrape targets      | `docker/prometheus/prometheus.yml` |
| Grafana provisioning | Test: datasources ready   | `docker/grafana/provisioning/`     |
| Loki config          | Test: logs ingested       | `docker/loki/loki-config.yml`      |
| Backend metrics      | Test: `/metrics` endpoint | `backend/src/api/metrics.py`       |
| Frontend metrics     | Test: perf observers      | `frontend/src/metrics/`            |

### A.2 Métricas del Backend

```python
# backend/src/metrics/prometheus.py
from prometheus_client import Counter, Histogram, Gauge

# Incident Metrics
incidents_processed = Counter(
    'cyberdemo_incidents_processed_total',
    'Total incidents processed',
    ['severity', 'outcome']
)

containments_auto = Counter(
    'cyberdemo_containments_auto_total',
    'Auto-containments executed'
)

containments_approved = Counter(
    'cyberdemo_containments_approved_total',
    'Containments after approval'
)

false_positives = Counter(
    'cyberdemo_false_positives_total',
    'False positives identified'
)

# Performance Metrics
api_latency = Histogram(
    'cyberdemo_api_latency_seconds',
    'API request latency',
    ['endpoint', 'method']
)

approval_wait = Histogram(
    'cyberdemo_approval_wait_seconds',
    'Time waiting for human approval',
    buckets=[60, 300, 600, 1800, 3600]
)

# Gauges
open_incidents = Gauge(
    'cyberdemo_open_incidents',
    'Currently open incidents',
    ['severity']
)

contained_hosts = Gauge(
    'cyberdemo_contained_hosts',
    'Currently contained hosts'
)
```

### A.3 Dashboards Grafana

```
docker/grafana/dashboards/
├── soc-overview.json         # Overview general
├── agent-performance.json    # Métricas del agente
├── containment-analytics.json # Análisis de contención
└── approval-latency.json     # Tiempos de aprobación
```

**Dashboard: SOC Overview**

- Total incidentes (24h, 7d, 30d)
- Distribución por severidad (pie)
- Trend de incidentes (line)
- MTTR actual vs objetivo
- Top 10 técnicas MITRE

**Dashboard: Agent Performance**

- Incidentes procesados/hora
- Auto-containments vs approvals
- False positive rate
- Confidence score distribution
- Tool usage breakdown

---

## Fase B: Algoritmo de Confidence Score

**Duración estimada:** 2 días
**Prioridad:** Alta
**Dependencias:** Generadores de datos, Intel API

### B.1 Implementación del Algoritmo

```python
# backend/src/services/confidence_score.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class ConfidenceComponents:
    intel_score: float      # 0-40
    behavior_score: float   # 0-30
    context_score: float    # 0-20
    propagation_score: float # 0-10

    @property
    def total(self) -> float:
        return (self.intel_score + self.behavior_score +
                self.context_score + self.propagation_score)


class ConfidenceScoreCalculator:
    """Calcula el confidence score para decisiones de contención."""

    # Weights (configurable)
    INTEL_WEIGHT = 40
    BEHAVIOR_WEIGHT = 30
    CONTEXT_WEIGHT = 20
    PROPAGATION_WEIGHT = 10

    def calculate(
        self,
        detection: dict,
        intel: Optional[dict],
        ctem: Optional[dict],
        propagation: Optional[dict]
    ) -> ConfidenceComponents:
        """Calculate all confidence components."""
        return ConfidenceComponents(
            intel_score=self._calculate_intel(intel),
            behavior_score=self._calculate_behavior(detection),
            context_score=self._calculate_context(ctem),
            propagation_score=self._calculate_propagation(propagation)
        )

    def _calculate_intel(self, intel: Optional[dict]) -> float:
        """
        Intel component (0-40):
        - VT score: 0-20 points
        - Malware labels: 0-10 points
        - Source reliability: 0-10 points
        """
        if not intel:
            return 0.0

        score = 0.0

        # VT Score (format: "N/M")
        vt_score = intel.get("vt_score", "0/74")
        try:
            detected, total = map(int, vt_score.split("/"))
            vt_ratio = detected / total if total > 0 else 0
            score += vt_ratio * 20  # Max 20 points
        except ValueError:
            pass

        # Malware labels
        labels = intel.get("labels", [])
        if "ransomware" in labels:
            score += 10
        elif "trojan" in labels or "backdoor" in labels:
            score += 8
        elif "malware" in labels:
            score += 6
        elif "pup" in labels:
            score += 2

        # Source reliability
        sources = intel.get("sources", [])
        reliable_sources = {"virustotal", "crowdstrike", "mandiant"}
        if set(sources) & reliable_sources:
            score += 10
        elif sources:
            score += 5

        return min(score, self.INTEL_WEIGHT)

    def _calculate_behavior(self, detection: dict) -> float:
        """
        Behavior component (0-30):
        - MITRE technique severity: 0-15 points
        - Command line analysis: 0-15 points
        """
        score = 0.0

        # MITRE Technique scoring
        high_severity_techniques = {
            "T1059.001",  # PowerShell
            "T1003.001",  # LSASS Memory
            "T1021.002",  # SMB/Windows Admin Shares
            "T1486",      # Data Encrypted for Impact
            "T1562.001",  # Disable/Modify Tools
        }
        medium_severity_techniques = {
            "T1055",      # Process Injection
            "T1057",      # Process Discovery
            "T1083",      # File and Directory Discovery
            "T1082",      # System Information Discovery
        }

        technique_id = detection.get("technique_id", "")
        if technique_id in high_severity_techniques:
            score += 15
        elif technique_id in medium_severity_techniques:
            score += 8
        else:
            score += 3

        # Command line analysis
        cmdline = detection.get("command_line", "").lower()
        suspicious_patterns = [
            ("-enc", 8),           # Encoded PowerShell
            ("-w hidden", 5),      # Hidden window
            ("mimikatz", 10),      # Credential theft
            ("procdump", 8),       # Memory dump
            ("psexec", 7),         # Lateral movement
            ("wmic /node", 7),     # Remote execution
            ("-nop", 3),           # No profile
            ("bypass", 5),         # Execution policy bypass
        ]

        for pattern, points in suspicious_patterns:
            if pattern in cmdline:
                score += points
                break  # Only count highest match

        return min(score, self.BEHAVIOR_WEIGHT)

    def _calculate_context(self, ctem: Optional[dict]) -> float:
        """
        Context component (0-20):
        - CTEM risk level: 0-10 points
        - Asset criticality: 0-10 points
        """
        if not ctem:
            return 0.0

        score = 0.0

        # CTEM Risk
        risk_color = ctem.get("risk_color", "Green")
        if risk_color == "Red":
            score += 10
        elif risk_color == "Yellow":
            score += 5

        # Asset criticality (from tags)
        tags = ctem.get("asset_tags", [])
        if "domain-controller" in tags:
            score += 10
        elif "server" in tags:
            score += 7
        elif "vip" in tags or "executive" in tags:
            score += 5

        return min(score, self.CONTEXT_WEIGHT)

    def _calculate_propagation(self, propagation: Optional[dict]) -> float:
        """
        Propagation component (0-10):
        - Number of affected hosts
        """
        if not propagation:
            return 0.0

        hosts = propagation.get("total_hosts_found", 0)

        if hosts >= 10:
            return 10.0
        elif hosts >= 5:
            return 7.0
        elif hosts >= 3:
            return 5.0
        elif hosts >= 2:
            return 3.0
        return 0.0
```

### B.2 Tests del Confidence Score

```python
# backend/tests/services/test_confidence_score.py
import pytest
from src.services.confidence_score import ConfidenceScoreCalculator

@pytest.fixture
def calculator():
    return ConfidenceScoreCalculator()


class TestIntelComponent:
    def test_high_vt_score_gives_high_intel(self, calculator):
        intel = {"vt_score": "60/74", "labels": ["trojan"], "sources": ["virustotal"]}
        components = calculator.calculate({}, intel, None, None)
        assert components.intel_score >= 30

    def test_no_intel_gives_zero(self, calculator):
        components = calculator.calculate({}, None, None, None)
        assert components.intel_score == 0

    def test_ransomware_label_adds_points(self, calculator):
        intel_ransomware = {"vt_score": "0/74", "labels": ["ransomware"]}
        intel_pup = {"vt_score": "0/74", "labels": ["pup"]}

        r = calculator.calculate({}, intel_ransomware, None, None)
        p = calculator.calculate({}, intel_pup, None, None)

        assert r.intel_score > p.intel_score


class TestBehaviorComponent:
    def test_encoded_powershell_high_score(self, calculator):
        detection = {
            "technique_id": "T1059.001",
            "command_line": "powershell.exe -enc SGVsbG8="
        }
        components = calculator.calculate(detection, None, None, None)
        assert components.behavior_score >= 20

    def test_mimikatz_highest_cmdline_score(self, calculator):
        detection = {"technique_id": "", "command_line": "mimikatz.exe sekurlsa"}
        components = calculator.calculate(detection, None, None, None)
        assert components.behavior_score >= 10


class TestContextComponent:
    def test_red_risk_domain_controller(self, calculator):
        ctem = {"risk_color": "Red", "asset_tags": ["domain-controller"]}
        components = calculator.calculate({}, None, ctem, None)
        assert components.context_score == 20

    def test_green_risk_low_score(self, calculator):
        ctem = {"risk_color": "Green", "asset_tags": []}
        components = calculator.calculate({}, None, ctem, None)
        assert components.context_score == 0


class TestPropagationComponent:
    def test_many_hosts_max_score(self, calculator):
        prop = {"total_hosts_found": 15}
        components = calculator.calculate({}, None, None, prop)
        assert components.propagation_score == 10

    def test_single_host_no_propagation(self, calculator):
        prop = {"total_hosts_found": 1}
        components = calculator.calculate({}, None, None, prop)
        assert components.propagation_score == 0


class TestTotalScore:
    def test_anchor_case_1_high_confidence(self, calculator):
        """Escenario 1: Malware evidente debe dar score alto."""
        detection = {
            "technique_id": "T1059.001",
            "command_line": "powershell.exe -enc SGVsbG8= -w hidden"
        }
        intel = {"vt_score": "55/74", "labels": ["trojan"], "sources": ["virustotal"]}
        ctem = {"risk_color": "Yellow", "asset_tags": []}
        prop = {"total_hosts_found": 3}

        components = calculator.calculate(detection, intel, ctem, prop)
        assert components.total >= 90

    def test_anchor_case_3_low_confidence(self, calculator):
        """Escenario 3: Script legítimo debe dar score bajo."""
        detection = {
            "technique_id": "T1082",
            "command_line": "systeminfo.exe"
        }
        intel = {"vt_score": "0/74", "labels": [], "sources": []}

        components = calculator.calculate(detection, intel, None, None)
        assert components.total < 50
```

### B.3 Integración con Policy Engine

```python
# backend/src/services/policy_engine.py (actualizado)
from .confidence_score import ConfidenceScoreCalculator, ConfidenceComponents

class PolicyEngine:
    CONFIDENCE_HIGH = 90
    CONFIDENCE_MEDIUM = 50
    CRITICAL_TAGS = {"vip", "executive", "server", "domain-controller"}

    def __init__(self):
        self.score_calculator = ConfidenceScoreCalculator()

    def evaluate_with_enrichment(
        self,
        detection: dict,
        intel: dict,
        ctem: dict,
        propagation: dict,
        device_tags: list,
        has_approval: bool = False
    ) -> dict:
        """Evaluate using full enrichment data."""
        components = self.score_calculator.calculate(
            detection, intel, ctem, propagation
        )
        return self._make_decision(
            components.total,
            device_tags,
            has_approval,
            components
        )

    def _make_decision(
        self,
        confidence_score: float,
        device_tags: list,
        has_approval: bool,
        components: ConfidenceComponents
    ) -> dict:
        is_critical = bool(set(device_tags) & self.CRITICAL_TAGS)

        base = {
            "confidence_score": confidence_score,
            "components": {
                "intel": components.intel_score,
                "behavior": components.behavior_score,
                "context": components.context_score,
                "propagation": components.propagation_score,
            }
        }

        if confidence_score < self.CONFIDENCE_MEDIUM:
            return {**base, "action": "mark_false_positive", "requires_approval": False}

        if is_critical:
            if has_approval:
                return {**base, "action": "contain", "requires_approval": False}
            return {**base, "action": "request_approval", "requires_approval": True}

        if confidence_score >= self.CONFIDENCE_HIGH:
            return {**base, "action": "contain", "requires_approval": False}

        return {**base, "action": "request_approval", "requires_approval": True}
```

---

## Fase C: SKILL.md Completo

**Duración estimada:** 1 día
**Prioridad:** Alta
**Dependencias:** APIs Backend definidas

### C.1 Contenido del SKILL.md

```markdown
# skills/soc-analyst/SKILL.md

# SOC Analyst Skill - CyberDemo

## Rol

Eres un analista SOC Tier-1 especializado en investigación de alertas de malware.
Tu objetivo es investigar incidentes de seguridad, determinar su severidad real,
y tomar acciones de contención cuando sea apropiado.

## Contexto

Trabajas en un SOC que monitorea ~1000 endpoints. Tienes acceso a:

- EDR (CrowdStrike-like) para detecciones y contención
- SIEM (Sentinel-like) para incidentes correlacionados
- Threat Intelligence para reputación de IOCs
- CTEM para contexto de vulnerabilidades

## Workflow de Investigación

### Paso 1: Recepción de Alerta
```

Cuando recibas un incidente, extrae:

- Hostname afectado
- Hash del archivo sospechoso
- Usuario involucrado
- Técnica MITRE detectada

```

### Paso 2: Enriquecimiento
```

Ejecuta en paralelo:

1. intel.getIndicator("filehash", sha256) → Reputación
2. edr.getProcessTree(detection_id) → Contexto de ejecución
3. edr.huntHash(sha256) → Propagación organizacional
4. ctem.getAssetRisk(asset_id) → Vulnerabilidades del host

```

### Paso 3: Análisis y Scoring
```

Calcula el Confidence Score basado en:

- Intel (40%): VT score, labels, sources
- Behavior (30%): Técnica MITRE, cmdline
- Context (20%): CTEM risk, criticidad del asset
- Propagation (10%): Hosts afectados

```

### Paso 4: Decisión (Policy Engine)
```

Score < 50: → False Positive, cerrar
Score >= 90: → Auto-containment (si no es VIP)
Score 50-89: → Requiere aprobación
Asset es VIP/DC: → SIEMPRE requiere aprobación

```

### Paso 5: Ejecución
```

Si auto-containment:
edr.containHost(device_id, reason)

Si requiere aprobación:
approvals.request(incident_id, card_data)
[ESPERAR]
Si approved: edr.containHost(...)
Si rejected: cerrar incidente

```

### Paso 6: Cierre
```

1. tickets.create(payload)
2. reports.generatePostmortem(incident_id)
3. siem.closeIncident(incident_id)

````

## Herramientas Disponibles

### SIEM Operations
| Tool | Descripción | Ejemplo |
|------|-------------|---------|
| `siem.listIncidents()` | Lista incidentes abiertos | `siem.listIncidents(status="open")` |
| `siem.getIncident(id)` | Detalle de incidente | `siem.getIncident("INC-2024-001")` |
| `siem.addComment(id, msg)` | Añadir comentario | `siem.addComment("INC-001", "Iniciando investigación")` |
| `siem.closeIncident(id)` | Cerrar incidente | `siem.closeIncident("INC-001")` |

### EDR Operations
| Tool | Descripción | Ejemplo |
|------|-------------|---------|
| `edr.getDetection(id)` | Detalle de detección | `edr.getDetection("DET-123")` |
| `edr.getProcessTree(id)` | Árbol de procesos | `edr.getProcessTree("DET-123")` |
| `edr.huntHash(sha256)` | Buscar propagación | `edr.huntHash("a1b2c3...")` |
| `edr.containHost(id, reason)` | Contener host | `edr.containHost("DEV-001", "Malware confirmed")` |

### Intelligence
| Tool | Descripción | Ejemplo |
|------|-------------|---------|
| `intel.getIndicator(type, value)` | Reputación IOC | `intel.getIndicator("filehash", "abc123")` |

### CTEM
| Tool | Descripción | Ejemplo |
|------|-------------|---------|
| `ctem.getAssetRisk(id)` | Riesgo del activo | `ctem.getAssetRisk("ASSET-001")` |

### Approvals
| Tool | Descripción | Ejemplo |
|------|-------------|---------|
| `approvals.get(id)` | Estado de aprobación | `approvals.get("INC-001")` |
| `approvals.request(id, data)` | Solicitar aprobación | `approvals.request("INC-001", {...})` |

### Tickets & Reports
| Tool | Descripción | Ejemplo |
|------|-------------|---------|
| `tickets.create(payload)` | Crear ticket | `tickets.create({title: "..."})` |
| `reports.generatePostmortem(id)` | Generar informe | `reports.generatePostmortem("INC-001")` |

## Políticas de Contención

### Reglas Deterministas (Policy Engine)

```yaml
# NUNCA contener automáticamente si:
critical_assets:
  - tag: vip
  - tag: executive
  - tag: server
  - tag: domain-controller

# Contención automática si:
auto_contain:
  confidence_score: >= 90
  asset_is_critical: false

# Marcar como False Positive si:
false_positive:
  confidence_score: < 50
````

## Ejemplos de Investigación

### Ejemplo 1: Malware Evidente (Auto-Containment)

```
Usuario: "Investiga INC-2024-042"

Agente:
1. Obtengo detalles del incidente...
   → siem.getIncident("INC-2024-042")
   → Host: WS-FIN-042, Detection: DET-789

2. Enriqueciendo con threat intel...
   → intel.getIndicator("filehash", "abc123...")
   → VT: 58/74, Labels: [trojan, emotet]

3. Analizando propagación...
   → edr.huntHash("abc123...")
   → 3 hosts afectados: WS-FIN-042, WS-HR-011, WS-MKT-023

4. Calculando confidence score...
   → Intel: 35/40, Behavior: 25/30, Context: 5/20, Prop: 5/10
   → Total: 70/100

5. Policy Engine: Score 70, no es VIP
   → Requiere aprobación

[Si aprobado]
6. Ejecutando contención...
   → edr.containHost("WS-FIN-042", "Emotet confirmed")
   → Status: Success

7. Generando postmortem...
   → reports.generatePostmortem("INC-2024-042")
```

### Ejemplo 2: VIP Laptop (Human-in-the-Loop)

```
Usuario: "Investiga INC-2024-043"

Agente:
1. Obtengo detalles...
   → Host: LAPTOP-CFO-01
   → Tags: [vip, executive]

2. Aunque el score es 95, el asset es VIP
   → Policy Engine: requires_approval = true

3. Solicitando aprobación...
   → approvals.request("INC-2024-043", {
       hostname: "LAPTOP-CFO-01",
       owner: "CFO",
       confidence: 95,
       recommendation: "CONTAIN"
     })

[Esperando decisión humana]
```

### Ejemplo 3: False Positive

```
Usuario: "Investiga INC-2024-044"

Agente:
1. Obtengo detalles...
   → Detection: PowerShell script legítimo

2. Verificando intel...
   → VT: 0/74, Labels: []
   → Script firmado por Microsoft

3. Confidence score: 22/100
   → Policy Engine: action = "mark_false_positive"

4. Cerrando como FP...
   → siem.closeIncident("INC-2024-044", reason="False Positive")
```

## Notas Importantes

1. **NUNCA** contengas un asset VIP/server sin aprobación
2. **SIEMPRE** documenta tus decisiones con comentarios
3. **SIEMPRE** genera postmortem después de contención
4. Si tienes dudas, solicita aprobación humana

````

---

## Fase D: Escenarios Demo Adicionales

**Duración estimada:** 2-3 días
**Prioridad:** Media-Alta
**Dependencias:** Generadores completos, Policy Engine

### D.1 Escenario 4: Ransomware Multi-Host

#### Datos Ancla

```python
# backend/src/generators/anchors/ransomware_scenario.py
RANSOMWARE_ANCHOR = {
    "incident_id": "INC-RANSOMWARE-001",
    "title": "Potential Ransomware - Mass File Encryption",
    "severity": "Critical",
    "detections": [
        {"host": "WS-ACC-001", "detection_id": "DET-RANSOM-001"},
        {"host": "WS-ACC-002", "detection_id": "DET-RANSOM-002"},
        {"host": "WS-ACC-003", "detection_id": "DET-RANSOM-003"},
        {"host": "WS-ACC-004", "detection_id": "DET-RANSOM-004"},
        {"host": "SRV-FILE-01", "detection_id": "DET-RANSOM-005"},
    ],
    "hash": "ransomware_anchor_hash_001",
    "technique_id": "T1486",  # Data Encrypted for Impact
    "expected_outcome": "mass_containment_with_approval"
}
````

#### Test E2E

```python
@pytest.mark.e2e
async def test_scenario_4_ransomware_multi_host():
    """Escenario 4: Ransomware afectando múltiples hosts."""
    # 1. Verificar incidente existe
    incident = await api.get_incident("INC-RANSOMWARE-001")
    assert incident["severity"] == "Critical"
    assert len(incident["detections"]) >= 5

    # 2. Verificar propagación
    detection = await api.get_detection("DET-RANSOM-001")
    hunt = await api.hunt_hash(detection["file"]["sha256"])
    assert hunt["total_hosts_found"] >= 5

    # 3. Verificar que incluye servidor (requiere aprobación)
    affected_hosts = hunt["hosts"]
    server_affected = any("SRV" in h for h in affected_hosts)
    assert server_affected

    # 4. Policy debe requerir aprobación por servidor
    # (implementar lógica de contención masiva)
```

### D.2 Escenario 5: Insider Threat

```python
INSIDER_ANCHOR = {
    "incident_id": "INC-INSIDER-001",
    "title": "Unusual Data Access - Potential Exfiltration",
    "severity": "High",
    "user": "john.smith",
    "host": "WS-SALES-042",
    "behavior": {
        "files_accessed": 1500,
        "after_hours": True,
        "external_transfer": True,
    },
    "expected_outcome": "escalate_to_hr_approval"
}
```

### D.3 Escenario 6: Supply Chain Attack

```python
SUPPLY_CHAIN_ANCHOR = {
    "incident_id": "INC-SUPPLY-001",
    "title": "Trusted Application Anomaly - Potential Supply Chain",
    "severity": "Critical",
    "application": "UpdateHelper.exe",  # Legítimo pero comprometido
    "signed_by": "TrustedVendor Inc.",
    "anomalous_behavior": "network_callback_to_unknown_c2",
    "expected_outcome": "vendor_notification_and_org_hunt"
}
```

---

## Fase E: Notificaciones y Colaboración

**Duración estimada:** 2 días
**Prioridad:** Media
**Dependencias:** Backend APIs

### E.1 Sistema de Notificaciones

```python
# backend/src/services/notifications.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class NotificationChannel(ABC):
    @abstractmethod
    async def send(self, template: str, data: Dict[str, Any]) -> bool:
        pass


class SlackNotifier(NotificationChannel):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send(self, template: str, data: Dict[str, Any]) -> bool:
        # Implementación mock para demo
        pass


class EmailNotifier(NotificationChannel):
    def __init__(self, smtp_config: dict):
        self.config = smtp_config

    async def send(self, template: str, data: Dict[str, Any]) -> bool:
        pass


class NotificationService:
    TEMPLATES = {
        "containment_auto": "Host {hostname} contenido automáticamente. Score: {score}",
        "approval_needed": "Aprobación requerida para {hostname}. Score: {score}",
        "containment_approved": "Contención aprobada por {approver} para {hostname}",
        "false_positive": "Incidente {incident_id} cerrado como False Positive",
    }

    def __init__(self):
        self.channels: list[NotificationChannel] = []

    def register_channel(self, channel: NotificationChannel):
        self.channels.append(channel)

    async def notify(self, template: str, data: Dict[str, Any]):
        message = self.TEMPLATES[template].format(**data)
        for channel in self.channels:
            await channel.send(template, {"message": message, **data})
```

### E.2 Canal de Colaboración

```python
# backend/src/api/collab.py
from fastapi import APIRouter, WebSocket
from typing import List

router = APIRouter(prefix="/collab", tags=["Collaboration"])

# In-memory store (OpenSearch en producción)
messages: List[dict] = []
connections: List[WebSocket] = []


@router.post("/messages")
async def send_message(incident_id: str, user: str, content: str):
    """Enviar mensaje al canal de colaboración."""
    msg = {
        "id": f"MSG-{len(messages)+1:04d}",
        "incident_id": incident_id,
        "user": user,
        "content": content,
        "timestamp": datetime.utcnow().isoformat()
    }
    messages.append(msg)

    # Broadcast a todos los conectados
    for ws in connections:
        await ws.send_json(msg)

    return msg


@router.get("/messages")
async def get_messages(incident_id: str = None):
    """Obtener mensajes del canal."""
    if incident_id:
        return [m for m in messages if m["incident_id"] == incident_id]
    return messages


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para updates en tiempo real."""
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages
    except:
        connections.remove(websocket)
```

---

## Fase F: Playbooks SOAR

**Duración estimada:** 2-3 días
**Prioridad:** Media
**Dependencias:** Policy Engine, EDR APIs

### F.1 Motor de Playbooks

```python
# backend/src/services/playbook_engine.py
from dataclasses import dataclass
from typing import List, Callable, Any
import yaml

@dataclass
class PlaybookStep:
    action: str
    params: dict
    on_error: str = "stop"
    timeout: int = 60


@dataclass
class Playbook:
    name: str
    description: str
    triggers: List[str]
    steps: List[PlaybookStep]


class PlaybookEngine:
    def __init__(self, api_client):
        self.api = api_client
        self.playbooks: dict[str, Playbook] = {}

    def load_playbook(self, yaml_content: str):
        data = yaml.safe_load(yaml_content)
        playbook = Playbook(
            name=data["name"],
            description=data["description"],
            triggers=data.get("triggers", []),
            steps=[PlaybookStep(**s) for s in data["steps"]]
        )
        self.playbooks[playbook.name] = playbook

    async def execute(self, playbook_name: str, context: dict) -> dict:
        playbook = self.playbooks[playbook_name]
        results = []

        for step in playbook.steps:
            try:
                result = await self._execute_step(step, context)
                results.append({"step": step.action, "status": "success", "result": result})
                context["previous"] = {"result": result}
            except Exception as e:
                if step.on_error == "notify_human":
                    # Crear aprobación y esperar
                    pass
                else:
                    results.append({"step": step.action, "status": "failed", "error": str(e)})
                    break

        return {"playbook": playbook_name, "results": results}

    async def _execute_step(self, step: PlaybookStep, context: dict):
        # Resolver variables en params
        params = self._resolve_params(step.params, context)

        # Ejecutar acción
        action_map = {
            "edr.contain_host": self.api.contain_host,
            "edr.collect_artifacts": self.api.collect_artifacts,
            "intel.deep_scan": self.api.deep_scan,
            "reports.generate_ioc_report": self.api.generate_ioc_report,
        }

        handler = action_map.get(step.action)
        if handler:
            return await handler(**params)
        raise ValueError(f"Unknown action: {step.action}")

    def _resolve_params(self, params: dict, context: dict) -> dict:
        """Resuelve variables como ${incident.title}"""
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str) and "${" in value:
                # Simple template resolution
                resolved[key] = value  # TODO: implement proper resolution
            else:
                resolved[key] = value
        return resolved
```

### F.2 Playbooks Predefinidos

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
      device_id: ${detection.device_id}
      reason: "Auto-containment: ${incident.title}"
    on_error: notify_human

  - action: siem.add_comment
    params:
      incident_id: ${incident.incident_id}
      message: "Host contained automatically by playbook"

  - action: tickets.create
    params:
      title: "Security Incident: ${incident.title}"
      description: "Auto-generated from playbook execution"
      incident_id: ${incident.incident_id}

  - action: reports.generate_postmortem
    params:
      incident_id: ${incident.incident_id}
```

---

## Resumen de Tareas

### Prioridad Alta

| Fase | Tarea                         | Estimación | Estado    |
| ---- | ----------------------------- | ---------- | --------- |
| B    | Confidence Score Calculator   | 1 día      | Pendiente |
| B    | Tests de Confidence Score     | 0.5 día    | Pendiente |
| B    | Integración con Policy Engine | 0.5 día    | Pendiente |
| C    | SKILL.md completo             | 1 día      | Pendiente |
| D    | Escenario 4: Ransomware       | 1 día      | Pendiente |

### Prioridad Media

| Fase | Tarea                     | Estimación | Estado    |
| ---- | ------------------------- | ---------- | --------- |
| A    | Prometheus setup          | 0.5 día    | Pendiente |
| A    | Grafana dashboards        | 1 día      | Pendiente |
| A    | Backend metrics           | 0.5 día    | Pendiente |
| D    | Escenario 5: Insider      | 1 día      | Pendiente |
| D    | Escenario 6: Supply Chain | 1 día      | Pendiente |
| E    | Sistema de notificaciones | 1 día      | Pendiente |
| E    | Canal de colaboración     | 1 día      | Pendiente |
| F    | Motor de playbooks        | 1.5 días   | Pendiente |
| F    | Playbooks predefinidos    | 0.5 día    | Pendiente |

### Prioridad Baja (Future Work)

| Tarea                       | Notas                   |
| --------------------------- | ----------------------- |
| ML para anomalías           | Requiere dataset grande |
| Multi-tenancy               | Arquitectura mayor      |
| Integraciones reales        | Credenciales de cliente |
| Auditoría con firma digital | Compliance específico   |

---

## Dependencias entre Fases

```
Plan Original (Fases 1-7)
         │
         ├──► Fase A (Observabilidad)
         │         └──► Métricas exportadas
         │
         ├──► Fase B (Confidence Score)
         │         └──► Policy Engine mejorado
         │
         ├──► Fase C (SKILL.md)
         │         └──► Documentación de skill
         │
         ├──► Fase D (Escenarios Extra)
         │         └──► Datos ancla adicionales
         │
         ├──► Fase E (Notificaciones)
         │         └──► Canales configurados
         │
         └──► Fase F (Playbooks)
                   └──► Motor de automatización
```

---

_Plan complementario para funcionalidades faltantes identificadas en el análisis comparativo._
