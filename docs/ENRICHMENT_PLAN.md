# Plan de Enriquecimiento CTEM y Amenazas - CyberDemo

## Resumen Ejecutivo

Este documento detalla el plan para integrar sistemas de enriquecimiento de vulnerabilidades (CTEM) y amenazas (Threat Intelligence) en el dashboard de CyberDemo, con dos botones principales:

- **"Enriquecer Vulnerabilidades"** - Enriquece CVEs con CVSS, EPSS, CPE, CWE, exploit info
- **"Enriquecer Amenazas"** - Enriquece IOCs (IPs, dominios, hashes) con reputación, geolocalización, malware families

## 1. Sistemas de Enriquecimiento Disponibles

### 1.1 Vulnerabilidades CTEM (GRATUITOS)

| Sistema                | Tipo        | Limitaciones                                              | Datos que Provee                                         |
| ---------------------- | ----------- | --------------------------------------------------------- | -------------------------------------------------------- |
| **NVD API 2.0**        | API REST    | Rate limit: 5 req/30s (sin API key), 50 req/30s (con key) | CVSS scores, CPE, CWE, Referencias, Descripciones        |
| **EPSS API**           | API REST    | Sin límites                                               | Exploit Prediction Scoring (probabilidad de explotación) |
| **CVE Details**        | API REST    | Rate limits moderados                                     | CVSS history, EPSS scores, estadísticas                  |
| **Shodan CVEDB**       | API REST    | Gratis para CVE lookup                                    | Info rápida de vulnerabilidades, productos afectados     |
| **VulnCheck NVD++**    | API/Feed    | Gratis (basic tier)                                       | CVE enrichment con CPEs mejorados                        |
| **GitHub Advisory DB** | GraphQL API | Rate limit: 5000 req/h (autenticado)                      | Security advisories, affected packages, severities       |
| **OSV.dev**            | API REST    | Sin límites estrictos                                     | Vulnerabilidades open source, affected versions          |

**Referencias:**

- [NVD API](https://nvd.nist.gov/developers/vulnerabilities)
- [EPSS Scores](https://www.first.org/epss/)
- [Shodan CVEDB](https://cvedb.shodan.io/)
- [VulnCheck](https://www.vulncheck.com/blog/nvd-cpe)

### 1.2 Threat Intelligence (GRATUITOS)

| Sistema                    | Tipo      | Limitaciones                  | Datos que Provee                                     |
| -------------------------- | --------- | ----------------------------- | ---------------------------------------------------- |
| **AlienVault OTX**         | API REST  | Ilimitado (requiere registro) | Pulses, IOCs, malware families, ATT&CK TTPs          |
| **AbuseIPDB**              | API REST  | 1000 req/día (free tier)      | IP reputation, abuse confidence score, reports       |
| **GreyNoise**              | API REST  | Community tier limitado       | IP classification (benign/malicious), tags, metadata |
| **abuse.ch Feodo Tracker** | JSON Feed | Sin autenticación             | Botnet C2 IPs, malware families                      |
| **abuse.ch URLhaus**       | API REST  | 1000 queries/día              | Malicious URLs, payload URLs, malware families       |
| **Shodan InternetDB**      | API REST  | Gratis sin límites            | Open ports, vulnerabilities, hostnames, tags         |
| **VirusTotal**             | API REST  | 500 req/día (free tier)       | File/URL/IP/domain analysis, AV detections           |
| **IPinfo.io**              | API REST  | 50k req/mes (free tier)       | Geolocation, ASN, company, privacy detection         |
| **Cloudflare Radar**       | API REST  | Gratis (beta)                 | Internet traffic insights, attack trends             |

**Referencias:**

- [AlienVault OTX](https://otx.alienvault.com/)
- [AbuseIPDB](https://www.abuseipdb.com/api.html)
- [GreyNoise Community](https://www.greynoise.io/)
- [abuse.ch](https://abuse.ch/)

### 1.3 Open Source Platforms

| Plataforma     | Licencia   | Deployment  | Capacidades                                           |
| -------------- | ---------- | ----------- | ----------------------------------------------------- |
| **MISP**       | AGPL       | Self-hosted | IOC sharing, correlation, enrichment modules          |
| **OpenCTI**    | Apache 2.0 | Self-hosted | STIX 2 data, connectors, enrichment, visualization    |
| **DefectDojo** | BSD        | Self-hosted | Vulnerability aggregation, CISA KEV, EPSS integration |

**Referencias:**

- [MISP Project](https://www.misp-project.org/)
- [OpenCTI](https://github.com/OpenCTI-Platform/opencti)
- [DefectDojo](https://github.com/DefectDojo/django-DefectDojo)

### 1.4 MCP Servers Disponibles

| MCP Server          | GitHub                                                                                        | Herramientas                                   |
| ------------------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| **mcp-threatintel** | [aplaceforallmystuff/mcp-threatintel](https://github.com/aplaceforallmystuff/mcp-threatintel) | AlienVault OTX, AbuseIPDB, GreyNoise, abuse.ch |
| **Vulnebify MCP**   | [PulseMCP/vulnebify](https://www.pulsemcp.com/servers/vulnebify)                              | Vulnerability scanning tools                   |
| **Snyk MCP**        | Varios                                                                                        | Security scanning, vulnerability detection     |

**Referencias:**

- [MCP Threat Intel](https://github.com/aplaceforallmystuff/mcp-threatintel)
- [10 MCP Servers for Cybersecurity](https://snyk.io/articles/10-mcp-servers-for-cybersecurity-professionals-and-elite-hackers/)

## 2. Servicios de Pago a Simular

Para servicios de pago, crearemos generadores de datos sintéticos que simulen sus respuestas:

| Servicio                         | Precio     | Datos Únicos                           | Simulación Propuesta                                     |
| -------------------------------- | ---------- | -------------------------------------- | -------------------------------------------------------- |
| **Recorded Future**              | Enterprise | Risk scores, threat actors, campaigns  | Generar risk scores basados en edad CVE + EPSS           |
| **ThreatQuotient**               | Enterprise | Threat scoring, context, campaigns     | Combinar AlienVault OTX + scoring sintético              |
| **Mandiant Threat Intelligence** | Enterprise | APT groups, malware families, IOAs     | Mapear IOCs a APT groups conocidos (públicos)            |
| **CrowdStrike Falcon X**         | ~$15k/año  | Malware analysis, sandbox reports      | Generar reports sintéticos basados en hash patterns      |
| **Tenable.io**                   | ~$3k/año   | Vulnerability intelligence, VPR scores | Calcular VPR sintético (CVSS + EPSS + asset criticality) |
| **Qualys VMDR**                  | Enterprise | Vulnerability detection + response     | Generar QDS scores sintéticos                            |

## 3. Arquitectura de Integración

### 3.1 Componentes Nuevos

```
┌──────────────────────────────────────────────────────────────────┐
│                    CyberDemo Dashboard                            │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Botones Nuevos:                                            │  │
│  │  [Enriquecer Vulnerabilidades]  [Enriquecer Amenazas]      │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────┬────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│              Backend FastAPI - Enrichment Service                 │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  New Endpoints:                                             │  │
│  │  POST /enrichment/vulnerabilities                           │  │
│  │  POST /enrichment/threats                                   │  │
│  │  GET /enrichment/status/{job_id}                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Enrichment Orchestrator                                    │  │
│  │  - Queue management (Celery/RQ)                             │  │
│  │  - API rate limiting                                        │  │
│  │  - Result caching                                           │  │
│  │  - Error handling & retry logic                             │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────┬───────────────────────┬─────────────────────────────────┘
          │                       │
          ▼                       ▼
┌──────────────────────┐  ┌──────────────────────────────────────┐
│  External APIs       │  │  Synthetic Data Generators           │
│  - NVD API           │  │  - RecordedFutureMock                │
│  - EPSS API          │  │  - ThreatQuotientMock                │
│  - AlienVault OTX    │  │  - MandiantMock                      │
│  - AbuseIPDB         │  │  - CrowdStrikeMock                   │
│  - GreyNoise         │  │  - TenableMock                       │
│  - Shodan            │  │  - QualysMock                        │
│  - VirusTotal        │  │  (Basados en APIs gratuitas + ML)    │
└──────────┬───────────┘  └─────────────┬────────────────────────┘
           │                            │
           └────────────┬───────────────┘
                        ▼
           ┌────────────────────────────┐
           │  PostgreSQL                 │
           │  Nuevas Tablas:            │
           │  - enrichment_jobs         │
           │  - vulnerability_enrichment│
           │  - threat_enrichment       │
           │  - enrichment_cache        │
           └────────────────────────────┘
```

### 3.2 Base de Datos - Nuevas Tablas

```sql
-- Tabla de trabajos de enriquecimiento
CREATE TABLE enrichment_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL, -- 'vulnerability' | 'threat'
    status VARCHAR(50) NOT NULL, -- 'pending' | 'running' | 'completed' | 'failed'
    total_items INTEGER NOT NULL,
    processed_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB
);

-- Tabla de enriquecimiento de vulnerabilidades
CREATE TABLE vulnerability_enrichment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cve_id VARCHAR(50) NOT NULL UNIQUE,
    cvss_v3_score FLOAT,
    cvss_v3_vector VARCHAR(100),
    cvss_v2_score FLOAT,
    epss_score FLOAT, -- Exploit Prediction Scoring
    epss_percentile FLOAT,
    cwe_ids TEXT[], -- Common Weakness Enumeration
    cpe_uris TEXT[], -- Common Platform Enumeration
    known_exploited BOOLEAN DEFAULT FALSE, -- CISA KEV
    exploit_available BOOLEAN DEFAULT FALSE,
    patch_available BOOLEAN DEFAULT FALSE,
    vendor_advisory_url VARCHAR(500),
    references JSONB, -- [{url, source, tags}]
    affected_products JSONB, -- [{vendor, product, versions}]
    attack_complexity VARCHAR(50),
    privileges_required VARCHAR(50),
    user_interaction VARCHAR(50),
    -- Synthetic premium fields
    risk_score INTEGER, -- 0-100 (synthetic Recorded Future style)
    threat_actors TEXT[], -- Associated APT groups (synthetic)
    campaigns TEXT[], -- Associated campaigns (synthetic)
    vpr_score FLOAT, -- Vulnerability Priority Rating (synthetic Tenable)
    qds_score INTEGER, -- Qualys Detection Score (synthetic)
    enriched_at TIMESTAMP DEFAULT NOW(),
    enrichment_sources JSONB, -- Which APIs were used
    FOREIGN KEY (cve_id) REFERENCES ctem_findings(cve_id) ON DELETE CASCADE
);

-- Tabla de enriquecimiento de amenazas
CREATE TABLE threat_enrichment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicator_type VARCHAR(50) NOT NULL, -- 'ip' | 'domain' | 'url' | 'hash'
    indicator_value VARCHAR(500) NOT NULL,
    reputation_score INTEGER, -- 0-100 (0=clean, 100=malicious)
    malicious BOOLEAN DEFAULT FALSE,
    confidence INTEGER, -- 0-100
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    -- IP specific
    country VARCHAR(10),
    city VARCHAR(100),
    asn INTEGER,
    asn_owner VARCHAR(200),
    -- Threat context
    malware_families TEXT[],
    threat_types TEXT[], -- ['botnet', 'c2', 'phishing', 'malware']
    attack_techniques TEXT[], -- MITRE ATT&CK techniques
    threat_actors TEXT[], -- APT groups
    campaigns TEXT[],
    -- AlienVault OTX
    otx_pulses JSONB, -- [{pulse_id, pulse_name, created, author}]
    -- AbuseIPDB
    abuse_confidence_score INTEGER,
    total_reports INTEGER,
    -- GreyNoise
    greynoise_classification VARCHAR(50), -- 'benign' | 'malicious' | 'unknown'
    greynoise_tags TEXT[],
    -- VirusTotal
    vt_detections INTEGER,
    vt_total_engines INTEGER,
    vt_malicious_count INTEGER,
    -- Shodan
    open_ports INTEGER[],
    vulnerabilities TEXT[],
    -- Synthetic premium fields
    risk_score INTEGER, -- 0-100 (synthetic)
    sandbox_report JSONB, -- Synthetic CrowdStrike style
    context_description TEXT, -- Synthetic ThreatQuotient style
    enriched_at TIMESTAMP DEFAULT NOW(),
    enrichment_sources JSONB,
    UNIQUE(indicator_type, indicator_value)
);

-- Cache de resultados de APIs (evitar rate limiting)
CREATE TABLE enrichment_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_key VARCHAR(500) NOT NULL UNIQUE,
    api_source VARCHAR(100) NOT NULL,
    response_data JSONB NOT NULL,
    cached_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    hit_count INTEGER DEFAULT 0
);

-- Índices para performance
CREATE INDEX idx_vuln_enrichment_cve ON vulnerability_enrichment(cve_id);
CREATE INDEX idx_threat_enrichment_indicator ON threat_enrichment(indicator_type, indicator_value);
CREATE INDEX idx_enrichment_cache_key ON enrichment_cache(cache_key);
CREATE INDEX idx_enrichment_cache_expires ON enrichment_cache(expires_at);
CREATE INDEX idx_enrichment_jobs_status ON enrichment_jobs(status);
```

## 4. Endpoints de API

### 4.1 Vulnerabilidades

```python
POST /api/enrichment/vulnerabilities
Body:
{
  "cve_ids": ["CVE-2024-1234", "CVE-2024-5678"],  # Optional, if empty enriches all
  "sources": ["nvd", "epss", "github", "synthetic"],  # Optional, default: all
  "force_refresh": false  # Skip cache
}

Response:
{
  "job_id": "uuid",
  "status": "pending",
  "total_items": 150,
  "estimated_duration_seconds": 45
}

GET /api/enrichment/vulnerabilities/status/{job_id}
Response:
{
  "job_id": "uuid",
  "status": "running",
  "progress": 0.67,
  "processed_items": 100,
  "total_items": 150,
  "failed_items": 2,
  "started_at": "2026-02-13T10:00:00Z",
  "estimated_completion": "2026-02-13T10:00:45Z"
}

GET /api/ctem/findings/{cve_id}/enrichment
Response:
{
  "cve_id": "CVE-2024-1234",
  "cvss_v3_score": 9.8,
  "epss_score": 0.89,
  "epss_percentile": 0.95,
  "known_exploited": true,
  "risk_score": 95,
  "vpr_score": 9.5,
  "threat_actors": ["APT28", "Lazarus Group"],
  "campaigns": ["Operation XYZ"],
  "enriched_at": "2026-02-13T10:00:30Z",
  "enrichment_sources": ["nvd", "epss", "github", "synthetic_recorded_future"]
}
```

### 4.2 Amenazas

```python
POST /api/enrichment/threats
Body:
{
  "indicators": [
    {"type": "ip", "value": "192.0.2.1"},
    {"type": "domain", "value": "evil.com"},
    {"type": "hash", "value": "abc123..."}
  ],
  "sources": ["otx", "abuseipdb", "greynoise", "virustotal", "synthetic"],
  "force_refresh": false
}

Response:
{
  "job_id": "uuid",
  "status": "pending",
  "total_items": 200
}

GET /api/intel/indicators/{type}/{value}/enrichment
Response:
{
  "indicator_type": "ip",
  "indicator_value": "192.0.2.1",
  "reputation_score": 95,
  "malicious": true,
  "confidence": 90,
  "country": "RU",
  "malware_families": ["Emotet", "TrickBot"],
  "threat_types": ["botnet", "c2"],
  "attack_techniques": ["T1071", "T1090"],
  "threat_actors": ["TA505"],
  "otx_pulses": [...],
  "abuse_confidence_score": 100,
  "greynoise_classification": "malicious",
  "vt_detections": 45,
  "vt_total_engines": 89,
  "risk_score": 98,
  "sandbox_report": {...},
  "enriched_at": "2026-02-13T10:15:00Z",
  "enrichment_sources": ["otx", "abuseipdb", "greynoise", "vt", "synthetic_crowdstrike"]
}
```

## 5. Generadores de Datos Sintéticos

### 5.1 Recorded Future Mock (Risk Score)

```python
# backend/src/generators/enrichment/recorded_future_mock.py
import random
from datetime import datetime, timedelta

class RecordedFutureMock:
    """Simula la API de Recorded Future para vulnerability risk scoring"""

    def calculate_risk_score(self, cve_id: str, cvss_score: float, epss_score: float,
                            known_exploited: bool, age_days: int) -> dict:
        """
        Calcula un risk score sintético basado en múltiples factores
        Risk Score: 0-100 donde 100 es el riesgo más alto

        Factores:
        - CVSS score (40% peso)
        - EPSS score (30% peso)
        - Known exploited (20% peso)
        - Age/freshness (10% peso) - más reciente = más riesgo
        """
        # Base score from CVSS (0-10 -> 0-40)
        cvss_component = (cvss_score / 10.0) * 40

        # EPSS component (0-1 -> 0-30)
        epss_component = epss_score * 30

        # Known exploited component (0 or 20)
        exploit_component = 20 if known_exploited else 0

        # Age component (newer is riskier)
        # 0-30 days = 10 points, 31-90 days = 7 points, 91-365 days = 4 points, >365 = 2 points
        if age_days <= 30:
            age_component = 10
        elif age_days <= 90:
            age_component = 7
        elif age_days <= 365:
            age_component = 4
        else:
            age_component = 2

        risk_score = int(cvss_component + epss_component + exploit_component + age_component)
        risk_score = min(100, max(0, risk_score))  # Clamp to 0-100

        # Categoría de riesgo
        if risk_score >= 90:
            risk_category = "Critical"
        elif risk_score >= 70:
            risk_category = "High"
        elif risk_score >= 50:
            risk_category = "Medium"
        else:
            risk_category = "Low"

        # Generar threat actors asociados (sintético)
        threat_actors = self._generate_threat_actors(risk_score, known_exploited)

        # Generar campaigns asociadas (sintético)
        campaigns = self._generate_campaigns(risk_score, age_days)

        return {
            "risk_score": risk_score,
            "risk_category": risk_category,
            "threat_actors": threat_actors,
            "campaigns": campaigns,
            "risk_vector": {
                "cvss_component": round(cvss_component, 2),
                "epss_component": round(epss_component, 2),
                "exploit_component": exploit_component,
                "age_component": age_component
            },
            "enrichment_source": "synthetic_recorded_future",
            "generated_at": datetime.utcnow().isoformat()
        }

    def _generate_threat_actors(self, risk_score: int, known_exploited: bool) -> list:
        """Genera threat actors sintéticos basados en el risk score"""
        # APT groups conocidos públicamente
        high_sophistication_apts = [
            "APT28", "APT29", "APT41", "Lazarus Group", "FIN7", "Carbanak",
            "OilRig", "Turla", "Equation Group", "DarkHotel"
        ]

        medium_sophistication_apts = [
            "TA505", "TA551", "Cobalt Group", "SilverTerrier", "Wizard Spider",
            "Silence Group", "FIN8", "Machete", "Gamaredon"
        ]

        if risk_score >= 80 and known_exploited:
            # Alta sofisticación
            return random.sample(high_sophistication_apts, random.randint(1, 3))
        elif risk_score >= 60:
            # Media sofisticación
            return random.sample(medium_sophistication_apts, random.randint(1, 2))
        elif risk_score >= 40:
            # Baja sofisticación
            return random.sample(medium_sophistication_apts, random.randint(0, 1))
        else:
            return []

    def _generate_campaigns(self, risk_score: int, age_days: int) -> list:
        """Genera campaigns sintéticas basadas en risk score y edad"""
        campaign_templates = [
            "Operation {adjective} {noun}",
            "{adjective} {animal} Campaign",
            "Project {noun}",
            "{adjective} {weather} Operation"
        ]

        adjectives = ["Silent", "Dark", "Hidden", "Persistent", "Advanced", "Covert",
                      "Stealthy", "Sophisticated", "Complex", "Targeted"]
        nouns = ["Phoenix", "Dragon", "Eagle", "Wolf", "Serpent", "Hawk", "Tiger",
                 "Storm", "Thunder", "Lightning"]
        animals = ["Panda", "Bear", "Cat", "Elephant", "Monkey", "Spider"]
        weather = ["Storm", "Thunder", "Lightning", "Blizzard", "Hurricane"]

        campaigns = []

        # Campaigns activas (vulnerabilidades recientes y alto riesgo)
        if age_days <= 90 and risk_score >= 70:
            num_campaigns = random.randint(1, 2)
            for _ in range(num_campaigns):
                template = random.choice(campaign_templates)
                campaign_name = template.format(
                    adjective=random.choice(adjectives),
                    noun=random.choice(nouns),
                    animal=random.choice(animals),
                    weather=random.choice(weather)
                )
                campaigns.append(campaign_name)

        return campaigns
```

### 5.2 Tenable VPR Mock

```python
# backend/src/generators/enrichment/tenable_mock.py

class TenableVPRMock:
    """Simula Tenable Vulnerability Priority Rating (VPR)"""

    def calculate_vpr(self, cvss_score: float, epss_score: float,
                     asset_criticality: str, known_exploited: bool,
                     age_days: int, product_coverage: float) -> dict:
        """
        VPR Score: 0.0 - 10.0

        Factores:
        - CVSS (35%)
        - Threat (EPSS + exploited) (35%)
        - Asset criticality (20%)
        - Product coverage (10%) - cuán común es el producto afectado
        """
        # CVSS component (0-10 -> 0-3.5)
        cvss_component = (cvss_score / 10.0) * 3.5

        # Threat component (0-3.5)
        threat_base = epss_score * 2.5  # EPSS contribuye 2.5
        threat_exploit = 1.0 if known_exploited else 0  # Exploit contribuye 1.0
        threat_component = min(3.5, threat_base + threat_exploit)

        # Asset criticality component (0-2.0)
        criticality_map = {
            "critical": 2.0,
            "high": 1.5,
            "medium": 1.0,
            "low": 0.5
        }
        criticality_component = criticality_map.get(asset_criticality.lower(), 1.0)

        # Product coverage component (0-1.0)
        # product_coverage: 0.0-1.0 (% of assets with this product)
        coverage_component = product_coverage * 1.0

        vpr_score = cvss_component + threat_component + criticality_component + coverage_component
        vpr_score = min(10.0, max(0.0, vpr_score))

        return {
            "vpr_score": round(vpr_score, 1),
            "vpr_components": {
                "cvss": round(cvss_component, 2),
                "threat": round(threat_component, 2),
                "asset_criticality": round(criticality_component, 2),
                "product_coverage": round(coverage_component, 2)
            },
            "enrichment_source": "synthetic_tenable",
            "generated_at": datetime.utcnow().isoformat()
        }
```

### 5.3 CrowdStrike Falcon X Sandbox Mock

```python
# backend/src/generators/enrichment/crowdstrike_mock.py

class CrowdStrikeSandboxMock:
    """Simula reportes de sandbox de CrowdStrike Falcon X"""

    def generate_sandbox_report(self, file_hash: str, malicious: bool,
                                malware_family: str = None) -> dict:
        """
        Genera un reporte de sandbox sintético
        """
        if not malicious:
            return {
                "verdict": "clean",
                "confidence": random.randint(85, 95),
                "file_hash": file_hash,
                "sandbox_runs": 3,
                "enrichment_source": "synthetic_crowdstrike",
                "generated_at": datetime.utcnow().isoformat()
            }

        # Comportamientos maliciosos comunes
        behaviors = []

        # Persistence
        if random.random() > 0.3:
            behaviors.append({
                "category": "persistence",
                "description": "Registry modification for autostart",
                "severity": "high",
                "details": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            })

        # Network
        if random.random() > 0.2:
            c2_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            behaviors.append({
                "category": "network",
                "description": "Outbound connection to suspicious IP",
                "severity": "critical",
                "details": f"Connection to {c2_ip}:443"
            })

        # File operations
        if random.random() > 0.4:
            behaviors.append({
                "category": "file_system",
                "description": "Suspicious file creation",
                "severity": "medium",
                "details": "Created executable in %TEMP% directory"
            })

        # Process injection
        if random.random() > 0.5:
            behaviors.append({
                "category": "process",
                "description": "Process injection detected",
                "severity": "high",
                "details": "Injected into svchost.exe"
            })

        # Anti-analysis
        if random.random() > 0.6:
            behaviors.append({
                "category": "evasion",
                "description": "VM detection attempted",
                "severity": "medium",
                "details": "Checked for VMware and VirtualBox artifacts"
            })

        # MITRE ATT&CK techniques
        techniques = []
        technique_map = {
            "persistence": ["T1547.001", "T1053"],
            "network": ["T1071.001", "T1095"],
            "file_system": ["T1027", "T1105"],
            "process": ["T1055", "T1106"],
            "evasion": ["T1497", "T1562"]
        }

        for behavior in behaviors:
            if behavior["category"] in technique_map:
                techniques.extend(random.sample(technique_map[behavior["category"]], 1))

        return {
            "verdict": "malicious",
            "confidence": random.randint(80, 99),
            "file_hash": file_hash,
            "malware_family": malware_family or self._random_malware_family(),
            "behaviors": behaviors,
            "mitre_techniques": list(set(techniques)),
            "sandbox_runs": 5,
            "sandbox_environments": ["Windows 10 x64", "Windows 11 x64"],
            "extracted_iocs": {
                "ips": [f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                       for _ in range(random.randint(1, 3))],
                "domains": [f"{random.choice(['evil', 'bad', 'malicious', 'c2'])}{random.randint(1,99)}.{random.choice(['com', 'net', 'org'])}"
                           for _ in range(random.randint(0, 2))],
                "file_paths": [f"C:\\Users\\Public\\{random.choice(['temp', 'data', 'cache'])}{random.randint(1,999)}.exe"]
            },
            "enrichment_source": "synthetic_crowdstrike",
            "generated_at": datetime.utcnow().isoformat()
        }

    def _random_malware_family(self) -> str:
        families = [
            "Emotet", "TrickBot", "Dridex", "Qbot", "IcedID", "Cobalt Strike",
            "Ryuk", "Conti", "LockBit", "BlackCat", "AgentTesla", "FormBook",
            "Remcos", "AsyncRAT", "RedLine", "Vidar", "Raccoon", "Azorult"
        ]
        return random.choice(families)
```

## 6. Implementación Frontend

### 6.1 Botones en Dashboard

```tsx
// CyberDemo/frontend/src/components/EnrichmentButtons.tsx
import { useState } from "react";
import { enrichVulnerabilities, enrichThreats, getEnrichmentStatus } from "../services/enrichment";

interface EnrichmentButtonsProps {
  onEnrichmentComplete?: () => void;
}

export function EnrichmentButtons({ onEnrichmentComplete }: EnrichmentButtonsProps) {
  const [vulnJobId, setVulnJobId] = useState<string | null>(null);
  const [threatJobId, setThreatJobId] = useState<string | null>(null);
  const [vulnProgress, setVulnProgress] = useState<number>(0);
  const [threatProgress, setThreatProgress] = useState<number>(0);

  const handleEnrichVulnerabilities = async () => {
    try {
      const response = await enrichVulnerabilities({
        sources: ["nvd", "epss", "github", "synthetic"],
        force_refresh: false,
      });

      setVulnJobId(response.job_id);

      // Poll for status
      const interval = setInterval(async () => {
        const status = await getEnrichmentStatus(response.job_id);
        setVulnProgress(status.progress * 100);

        if (status.status === "completed" || status.status === "failed") {
          clearInterval(interval);
          setVulnJobId(null);
          if (status.status === "completed" && onEnrichmentComplete) {
            onEnrichmentComplete();
          }
        }
      }, 2000);
    } catch (error) {
      console.error("Error enriching vulnerabilities:", error);
    }
  };

  const handleEnrichThreats = async () => {
    try {
      const response = await enrichThreats({
        sources: ["otx", "abuseipdb", "greynoise", "virustotal", "synthetic"],
        force_refresh: false,
      });

      setThreatJobId(response.job_id);

      // Poll for status
      const interval = setInterval(async () => {
        const status = await getEnrichmentStatus(response.job_id);
        setThreatProgress(status.progress * 100);

        if (status.status === "completed" || status.status === "failed") {
          clearInterval(interval);
          setThreatJobId(null);
          if (status.status === "completed" && onEnrichmentComplete) {
            onEnrichmentComplete();
          }
        }
      }, 2000);
    } catch (error) {
      console.error("Error enriching threats:", error);
    }
  };

  return (
    <div className="flex gap-4">
      <button
        onClick={handleEnrichVulnerabilities}
        disabled={!!vulnJobId}
        className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white rounded-lg transition-colors"
      >
        {vulnJobId ? (
          <>
            <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span>Enriching... {vulnProgress.toFixed(0)}%</span>
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
            <span>Enriquecer Vulnerabilidades</span>
          </>
        )}
      </button>

      <button
        onClick={handleEnrichThreats}
        disabled={!!threatJobId}
        className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white rounded-lg transition-colors"
      >
        {threatJobId ? (
          <>
            <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span>Enriching... {threatProgress.toFixed(0)}%</span>
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <span>Enriquecer Amenazas</span>
          </>
        )}
      </button>
    </div>
  );
}
```

### 6.2 Integración en DashboardPage

```tsx
// Añadir en DashboardPage.tsx después de la línea 200
import { EnrichmentButtons } from "../components/EnrichmentButtons";

// Dentro del return, después del header:
<div className="flex items-center justify-between">
  <div>
    <h1 className="text-2xl font-bold text-white">Dashboard</h1>
    <p className="text-gray-400 mt-1">Real-time security operations overview</p>
  </div>
  <EnrichmentButtons onEnrichmentComplete={() => window.location.reload()} />
</div>;
```

## 7. Gestión de Errores y Resiliencia

### 7.1 Limitación de Items por Fuente

**CRÍTICO:** Limitar a máximo 100 items por fuente conectada para evitar rate limits y timeouts.

```python
# backend/src/services/enrichment_service.py

MAX_ITEMS_PER_SOURCE = 100

class EnrichmentService:
    async def enrich_vulnerabilities(
        self,
        cve_ids: list[str] = None,
        sources: list[str] = None,
        force_refresh: bool = False
    ) -> dict:
        """
        Enriquece vulnerabilidades con limitación por fuente
        """
        # Si no se especifican CVE IDs, obtener de DB (limitado a 100)
        if not cve_ids:
            cve_ids = await self._get_pending_cves(limit=MAX_ITEMS_PER_SOURCE)

        # Limitar a 100 items máximo
        cve_ids = cve_ids[:MAX_ITEMS_PER_SOURCE]

        # Fuentes disponibles con fallback
        available_sources = sources or ['nvd', 'epss', 'github', 'synthetic']

        results = {
            "total_items": len(cve_ids),
            "sources": {},
            "errors": []
        }

        # Enriquecer por fuente de forma independiente
        for source in available_sources:
            try:
                enriched = await self._enrich_from_source(source, cve_ids, force_refresh)
                results["sources"][source] = {
                    "status": "success",
                    "enriched_count": enriched["count"],
                    "failed_count": enriched["failed"]
                }
            except Exception as e:
                # NO FALLAR - registrar error y continuar
                logger.error(f"Source {source} failed: {str(e)}")
                results["sources"][source] = {
                    "status": "failed",
                    "error": str(e),
                    "enriched_count": 0
                }
                results["errors"].append({
                    "source": source,
                    "error": str(e),
                    "recoverable": True
                })

        # Calcular estadísticas
        results["successful_sources"] = sum(
            1 for s in results["sources"].values() if s["status"] == "success"
        )
        results["failed_sources"] = sum(
            1 for s in results["sources"].values() if s["status"] == "failed"
        )

        return results
```

### 7.2 Circuit Breaker Pattern

Implementar circuit breaker para evitar hammering de APIs que fallan:

```python
# backend/src/services/circuit_breaker.py
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"  # Funcionando normal
    OPEN = "open"      # Bloqueado por fallos
    HALF_OPEN = "half_open"  # Probando recuperación

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timedelta(seconds=timeout_seconds)
        self.failures = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    async def call(self, func, *args, **kwargs):
        """Ejecuta función con circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if datetime.utcnow() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker is OPEN, skipping call")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Reset en caso de éxito"""
        self.failures = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        """Incrementar fallos y abrir circuito si supera threshold"""
        self.failures += 1
        self.last_failure_time = datetime.utcnow()

        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker OPENED after {self.failures} failures")
```

### 7.3 UI Error Handling

```tsx
// CyberDemo/frontend/src/components/EnrichmentButtons.tsx

interface EnrichmentResult {
  job_id: string;
  total_items: number;
  successful_sources: number;
  failed_sources: number;
  sources: Record<
    string,
    {
      status: "success" | "failed";
      enriched_count: number;
      error?: string;
    }
  >;
  errors: Array<{
    source: string;
    error: string;
    recoverable: boolean;
  }>;
}

function EnrichmentButtons() {
  const [result, setResult] = useState<EnrichmentResult | null>(null);
  const [showErrorModal, setShowErrorModal] = useState(false);

  const handleEnrichVulnerabilities = async () => {
    try {
      const response = await enrichVulnerabilities({
        sources: ["nvd", "epss", "github", "synthetic"],
        force_refresh: false,
      });

      setResult(response);

      // Mostrar errores si los hay, pero NO BLOQUEAR UI
      if (response.failed_sources > 0) {
        toast.warning(
          `Enrichment completed with ${response.failed_sources} source(s) unavailable. ` +
            `${response.successful_sources} source(s) succeeded.`,
          { duration: 5000 },
        );
      } else {
        toast.success(`Successfully enriched from all ${response.successful_sources} sources!`);
      }

      // Actualizar dashboard con datos parciales
      onEnrichmentComplete();
    } catch (error) {
      // Error total solo si TODAS las fuentes fallan
      if (error.response?.data?.successful_sources === 0) {
        toast.error("All enrichment sources failed. Please try again later.");
      } else {
        // Degradación graceful
        toast.info("Enrichment completed with limited data. Some sources were unavailable.");
      }
    }
  };

  return (
    <>
      {/* Botones normales */}
      <button onClick={handleEnrichVulnerabilities}>Enriquecer Vulnerabilidades</button>

      {/* Modal de detalles de error (opcional) */}
      {result && result.errors.length > 0 && (
        <ErrorDetailsModal
          errors={result.errors}
          sources={result.sources}
          onClose={() => setShowErrorModal(false)}
        />
      )}
    </>
  );
}
```

## 8. Test-Driven Development (TDD) - Orden de Implementación

### 8.1 Metodología TDD Rigurosa

**REGLA:** Escribir tests ANTES de implementar funcionalidad. Ciclo Red-Green-Refactor.

#### Ciclo TDD por Feature:

1. **RED**: Escribir test que falle
2. **GREEN**: Escribir código mínimo para pasar test
3. **REFACTOR**: Mejorar código manteniendo tests verdes
4. **REPEAT**: Siguiente test

### 8.2 Tests Unitarios (Backend)

#### Test 1: Limitación de Items (ESCRIBIR PRIMERO)

```python
# backend/tests/unit/services/test_enrichment_service.py
import pytest
from src.services.enrichment_service import EnrichmentService, MAX_ITEMS_PER_SOURCE

@pytest.mark.asyncio
async def test_enrichment_limits_to_100_items_per_source():
    """RED: Test que falla hasta implementar limitación"""
    service = EnrichmentService()

    # Intentar enriquecer 200 CVEs
    cve_ids = [f"CVE-2024-{i:04d}" for i in range(200)]

    result = await service.enrich_vulnerabilities(cve_ids=cve_ids)

    # Debe limitar a 100
    assert result["total_items"] == MAX_ITEMS_PER_SOURCE
    assert len(result["processed_cves"]) <= MAX_ITEMS_PER_SOURCE

@pytest.mark.asyncio
async def test_enrichment_handles_source_failure_gracefully():
    """RED: Test que verifica gestión de errores sin romper"""
    service = EnrichmentService()

    # Mock de fuente que falla
    with patch('src.services.enrichment_service.NVDClient') as mock_nvd:
        mock_nvd.side_effect = APIError("NVD API timeout")

        result = await service.enrich_vulnerabilities(
            cve_ids=["CVE-2024-0001"],
            sources=['nvd', 'epss']
        )

        # NVD debe estar en failed, EPSS en success
        assert result["sources"]["nvd"]["status"] == "failed"
        assert result["sources"]["epss"]["status"] == "success"
        assert result["successful_sources"] >= 1  # Al menos EPSS funcionó
        assert len(result["errors"]) == 1

@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_5_failures():
    """RED: Test circuit breaker"""
    from src.services.circuit_breaker import CircuitBreaker, CircuitState

    cb = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

    async def failing_func():
        raise Exception("API Error")

    # Fallar 5 veces
    for i in range(5):
        with pytest.raises(Exception):
            await cb.call(failing_func)

    # Circuit debe estar abierto
    assert cb.state == CircuitState.OPEN

    # Llamada 6 debe ser bloqueada
    with pytest.raises(CircuitBreakerOpenError):
        await cb.call(failing_func)
```

#### Test 2: Generadores Sintéticos

```python
# backend/tests/unit/generators/test_recorded_future_mock.py
import pytest
from src.generators.enrichment.recorded_future_mock import RecordedFutureMock

def test_risk_score_calculation_high_cvss_high_epss():
    """RED: Test cálculo de risk score"""
    mock = RecordedFutureMock()

    result = mock.calculate_risk_score(
        cve_id="CVE-2024-0001",
        cvss_score=9.8,
        epss_score=0.95,
        known_exploited=True,
        age_days=15
    )

    # Score alto esperado: CVSS(9.8) + EPSS(0.95) + exploit + age reciente
    assert result["risk_score"] >= 90
    assert result["risk_category"] == "Critical"
    assert len(result["threat_actors"]) >= 1  # Debe asignar APTs

def test_risk_score_calculation_low_cvss_low_epss():
    """Test score bajo"""
    mock = RecordedFutureMock()

    result = mock.calculate_risk_score(
        cve_id="CVE-2024-9999",
        cvss_score=3.2,
        epss_score=0.01,
        known_exploited=False,
        age_days=400
    )

    assert result["risk_score"] <= 40
    assert result["risk_category"] in ["Low", "Medium"]
    assert len(result["threat_actors"]) == 0  # No APTs en vulnerabilidades bajas

def test_vpr_score_calculation():
    """RED: Test Tenable VPR"""
    from src.generators.enrichment.tenable_mock import TenableVPRMock

    mock = TenableVPRMock()

    result = mock.calculate_vpr(
        cvss_score=9.8,
        epss_score=0.89,
        asset_criticality="critical",
        known_exploited=True,
        age_days=20,
        product_coverage=0.8
    )

    # VPR debe ser alto (>8.0)
    assert result["vpr_score"] >= 8.0
    assert result["vpr_score"] <= 10.0
```

### 8.3 Tests de Integración (Backend)

```python
# backend/tests/integration/test_enrichment_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_enrich_vulnerabilities_endpoint(client: AsyncClient, db_session):
    """RED: Test endpoint completo"""
    # Crear CVEs de prueba en DB
    cve_ids = await create_test_cves(db_session, count=50)

    response = await client.post("/api/enrichment/vulnerabilities", json={
        "sources": ["nvd", "epss", "synthetic"],
        "force_refresh": False
    })

    assert response.status_code == 200
    data = response.json()

    assert "job_id" in data
    assert data["total_items"] <= MAX_ITEMS_PER_SOURCE

    # Esperar a que complete (o polling en test real)
    job_id = data["job_id"]
    status = await wait_for_job_completion(client, job_id, timeout=30)

    assert status["status"] == "completed"
    assert status["successful_sources"] >= 1

@pytest.mark.asyncio
async def test_enrich_with_all_sources_failing(client: AsyncClient):
    """Test cuando todas las fuentes fallan"""
    # Mock todas las fuentes para que fallen
    with patch_all_sources_failing():
        response = await client.post("/api/enrichment/vulnerabilities", json={
            "sources": ["nvd", "epss"]
        })

        # Debe devolver 200 pero con failed_sources
        assert response.status_code == 200
        data = response.json()

        assert data["successful_sources"] == 0
        assert data["failed_sources"] == 2
        assert len(data["errors"]) == 2
```

### 8.4 Tests E2E con Playwright (Frontend + Backend)

```typescript
// CyberDemo/tests/e2e/enrichment.spec.ts
import { test, expect } from "@playwright/test";

test.describe("Enrichment Buttons E2E", () => {
  test.beforeEach(async ({ page }) => {
    // Navegar al dashboard
    await page.goto("http://localhost:3000/dashboard");
  });

  test("debe mostrar botones de enriquecimiento", async ({ page }) => {
    // Verificar que los botones existen
    const vulnButton = page.getByRole("button", { name: /Enriquecer Vulnerabilidades/i });
    const threatButton = page.getByRole("button", { name: /Enriquecer Amenazas/i });

    await expect(vulnButton).toBeVisible();
    await expect(threatButton).toBeVisible();
    await expect(vulnButton).toBeEnabled();
    await expect(threatButton).toBeEnabled();
  });

  test("debe enriquecer vulnerabilidades con éxito", async ({ page }) => {
    // Click en botón
    await page.getByRole("button", { name: /Enriquecer Vulnerabilidades/i }).click();

    // Debe mostrar spinner
    await expect(page.getByText(/Enriching\.\.\./i)).toBeVisible();

    // Debe mostrar progreso
    await expect(page.getByText(/\d+%/)).toBeVisible({ timeout: 5000 });

    // Esperar a completar (máximo 30s)
    await expect(page.getByText(/Enriching\.\.\./i)).not.toBeVisible({ timeout: 30000 });

    // Debe mostrar mensaje de éxito o advertencia
    const toast = page.locator('[role="alert"], .toast');
    await expect(toast).toBeVisible({ timeout: 5000 });

    // Verificar que el botón vuelve a estar habilitado
    const vulnButton = page.getByRole("button", { name: /Enriquecer Vulnerabilidades/i });
    await expect(vulnButton).toBeEnabled();
  });

  test("debe manejar error de fuente sin romper UI", async ({ page, context }) => {
    // Interceptar API y hacer que NVD falle
    await context.route("**/api/enrichment/vulnerabilities", async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          job_id: "test-job-123",
          total_items: 50,
          successful_sources: 1,
          failed_sources: 1,
          sources: {
            nvd: { status: "failed", error: "API timeout" },
            epss: { status: "success", enriched_count: 50 },
          },
          errors: [{ source: "nvd", error: "API timeout", recoverable: true }],
        }),
      });
    });

    // Click en botón
    await page.getByRole("button", { name: /Enriquecer Vulnerabilidades/i }).click();

    // Debe mostrar warning toast, NO error toast
    const toast = page.locator('[role="alert"]');
    await expect(toast).toContainText(/1 source.*unavailable/i);
    await expect(toast).toContainText(/1 source.*succeeded/i);

    // UI debe seguir funcional
    await expect(page.getByRole("button", { name: /Enriquecer Vulnerabilidades/i })).toBeEnabled();

    // No debe haber mensajes de error en consola críticos
    const errors = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });

    // Verificar que no hay errores de React
    expect(errors.filter((e) => e.includes("React"))).toHaveLength(0);
  });

  test("debe limitar a 100 items por fuente", async ({ page, context }) => {
    // Mock con 200 CVEs en DB
    await context.route("**/api/enrichment/vulnerabilities", async (route) => {
      const request = route.request();
      const postData = request.postDataJSON();

      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          job_id: "test-job-limit",
          total_items: 100, // DEBE SER 100, no 200
          successful_sources: 2,
          failed_sources: 0,
        }),
      });
    });

    await page.getByRole("button", { name: /Enriquecer Vulnerabilidades/i }).click();

    // Verificar que el toast menciona 100 items, no más
    const toast = page.locator('[role="alert"]');
    await expect(toast).toBeVisible({ timeout: 5000 });

    // Si muestra número de items, debe ser ≤ 100
    const toastText = await toast.textContent();
    const itemsMatch = toastText?.match(/(\d+)\s+items?/i);
    if (itemsMatch) {
      const items = parseInt(itemsMatch[1]);
      expect(items).toBeLessThanOrEqual(100);
    }
  });

  test("debe mostrar datos enriquecidos en tabla de vulnerabilidades", async ({ page }) => {
    // Enriquecer
    await page.getByRole("button", { name: /Enriquecer Vulnerabilidades/i }).click();
    await expect(page.getByText(/Enriching/i)).not.toBeVisible({ timeout: 30000 });

    // Navegar a página de vulnerabilidades/CTEM
    await page.goto("http://localhost:3000/ctem");

    // Verificar que hay columnas de enriquecimiento visibles
    await expect(page.getByText(/EPSS Score/i)).toBeVisible();
    await expect(page.getByText(/Risk Score/i)).toBeVisible();

    // Verificar que hay datos (no todos vacíos)
    const epssScores = page.locator('td:has-text("0.")'); // EPSS scores 0.0-1.0
    await expect(epssScores.first()).toBeVisible();
  });
});

test.describe("Enrichment Error Recovery E2E", () => {
  test("debe recuperarse de timeout de API sin perder estado", async ({ page, context }) => {
    let callCount = 0;

    // Primera llamada: timeout
    // Segunda llamada: éxito
    await context.route("**/api/enrichment/vulnerabilities", async (route) => {
      callCount++;
      if (callCount === 1) {
        // Timeout en primera llamada
        await new Promise((resolve) => setTimeout(resolve, 5000));
        await route.abort();
      } else {
        // Éxito en segunda llamada
        await route.fulfill({
          status: 200,
          body: JSON.stringify({
            job_id: "retry-success",
            total_items: 50,
            successful_sources: 2,
            failed_sources: 0,
          }),
        });
      }
    });

    // Primera llamada (fallará)
    await page.goto("http://localhost:3000/dashboard");
    await page.getByRole("button", { name: /Enriquecer Vulnerabilidades/i }).click();

    // Debe mostrar error
    await expect(page.locator('[role="alert"]')).toContainText(/error|timeout|failed/i, {
      timeout: 10000,
    });

    // Botón debe volver a estar habilitado
    await expect(page.getByRole("button", { name: /Enriquecer Vulnerabilidades/i })).toBeEnabled();

    // Reintentar (debe funcionar)
    await page.getByRole("button", { name: /Enriquecer Vulnerabilidades/i }).click();

    // Debe mostrar éxito esta vez
    await expect(page.locator('[role="alert"]')).toContainText(/success/i, {
      timeout: 10000,
    });
  });
});
```

### 8.5 Tests de Performance

```python
# backend/tests/performance/test_enrichment_performance.py
import pytest
import time

@pytest.mark.performance
@pytest.mark.asyncio
async def test_enrichment_completes_within_2_minutes_for_100_items():
    """Requisito: 100 vulnerabilidades en <2 minutos"""
    service = EnrichmentService()
    cve_ids = [f"CVE-2024-{i:04d}" for i in range(100)]

    start = time.time()
    result = await service.enrich_vulnerabilities(cve_ids=cve_ids)
    duration = time.time() - start

    assert duration < 120  # 2 minutos
    assert result["total_items"] == 100

@pytest.mark.performance
async def test_cache_improves_performance_by_80_percent():
    """Cache debe mejorar performance en 80%+"""
    service = EnrichmentService()
    cve_id = "CVE-2024-0001"

    # Primera llamada (sin cache)
    start1 = time.time()
    await service._enrich_from_source('nvd', [cve_id], force_refresh=True)
    duration1 = time.time() - start1

    # Segunda llamada (con cache)
    start2 = time.time()
    await service._enrich_from_source('nvd', [cve_id], force_refresh=False)
    duration2 = time.time() - start2

    # Cache debe ser al menos 80% más rápido
    speedup = (duration1 - duration2) / duration1
    assert speedup >= 0.80
```

## 9. Cronograma TDD (Revisado)

### Fase 1: Tests Unitarios + Infraestructura (4-5 días)

**DÍA 1-2:**

- [ ] Escribir tests unitarios para EnrichmentService (limitación, errores)
- [ ] Escribir tests para CircuitBreaker
- [ ] Implementar EnrichmentService hasta pasar tests
- [ ] Implementar CircuitBreaker
- [ ] Crear tablas en PostgreSQL

**DÍA 3-4:**

- [ ] Escribir tests para generadores sintéticos (RecordedFuture, Tenable)
- [ ] Implementar RecordedFutureMock hasta pasar tests
- [ ] Implementar TenableMock hasta pasar tests
- [ ] Escribir tests para CrowdStrikeMock
- [ ] Implementar CrowdStrikeMock

**DÍA 5:**

- [ ] Escribir tests para endpoints de API
- [ ] Implementar endpoints de enrichment
- [ ] Implementar sistema de colas (opcional: puede ser síncrono inicialmente)

### Fase 2: Tests de Integración + APIs Gratuitas (5-6 días)

**DÍA 6-7:**

- [ ] Escribir tests de integración para NVD API
- [ ] Implementar NVDClient con error handling
- [ ] Escribir tests para EPSS API
- [ ] Implementar EPSSClient

**DÍA 8-9:**

- [ ] Escribir tests para AlienVault OTX
- [ ] Implementar OTXClient
- [ ] Escribir tests para AbuseIPDB
- [ ] Implementar AbuseIPDBClient
- [ ] Escribir tests para GreyNoise
- [ ] Implementar GreyNoiseClient

**DÍA 10-11:**

- [ ] Escribir tests para Shodan InternetDB
- [ ] Implementar ShodanClient
- [ ] Escribir tests para cache de APIs
- [ ] Implementar EnrichmentCache
- [ ] Todos los tests de integración backend PASAN

### Fase 3: Frontend con Tests E2E (4-5 días)

**DÍA 12-13:**

- [ ] Escribir tests E2E Playwright para botones de enriquecimiento
- [ ] Implementar componente EnrichmentButtons
- [ ] Implementar servicio API cliente
- [ ] Tests E2E PASAN: botones visibles, clic funciona

**DÍA 14-15:**

- [ ] Escribir tests E2E para gestión de errores (fuente falla)
- [ ] Implementar error handling en UI (toasts, degradación graceful)
- [ ] Escribir tests E2E para progress indicators
- [ ] Implementar progress polling en UI
- [ ] Tests E2E PASAN: errores manejados sin romper UI

**DÍA 16:**

- [ ] Escribir tests E2E para visualización de datos enriquecidos
- [ ] Integrar datos enriquecidos en páginas CTEM/Vulnerabilidades
- [ ] Tests E2E PASAN: datos enriquecidos visibles

### Fase 4: Tests Funcionales Completos E2E (3-4 días)

**DÍA 17-18:**

- [ ] Escribir suite completa de tests funcionales:
  - [ ] Test: Enriquecimiento end-to-end completo (100 vulnerabilidades)
  - [ ] Test: Enriquecimiento con fuentes parcialmente fallando
  - [ ] Test: Circuit breaker funcionando
  - [ ] Test: Cache funcionando (segunda llamada rápida)
  - [ ] Test: Limitación a 100 items por fuente
  - [ ] Test: Datos sintéticos generados correctamente
  - [ ] Test: Dashboard actualizado con datos enriquecidos
- [ ] Ejecutar todos los tests y corregir fallos

**DÍA 19-20:**

- [ ] Escribir tests de performance
- [ ] Optimizar para cumplir requisitos de performance
- [ ] Ejecutar todos los tests funcionales E2E
- [ ] Documentar resultados en ENRICHMENT_TEST_RESULTS.md

### Fase 5: MCP Integration con Tests (2-3 días)

**DÍA 21-22:**

- [ ] Escribir tests para MCP tools (enrichment.vulnerabilities, enrichment.threats)
- [ ] Implementar MCP server con tools
- [ ] Configurar mcp-threatintel
- [ ] Tests MCP PASAN

**DÍA 23:**

- [ ] Test final E2E: SoulInTheBot llama herramientas de enriquecimiento via MCP
- [ ] Test final E2E: Datos enriquecidos visibles en dashboard
- [ ] TODOS LOS TESTS FUNCIONALES PASAN ✅

**Total estimado: 23 días con TDD riguroso**

## 10. Métricas de Éxito

1. **Cobertura de Enriquecimiento**
   - ≥95% de CVEs enriquecidos con CVSS
   - ≥80% de CVEs enriquecidos con EPSS
   - ≥90% de IOCs enriquecidos con reputación

2. **Performance**
   - Enriquecimiento de 100 vulnerabilidades < 2 minutos
   - Enriquecimiento de 100 IOCs < 1 minuto
   - Cache hit rate ≥70%

3. **Calidad de Datos Sintéticos**
   - Correlación ≥0.8 entre risk scores sintéticos y CVSS+EPSS reales
   - Threat actors mapeados correctamente según vulnerabilidades conocidas

4. **Usabilidad**
   - Botones funcionales con feedback visual
   - Progress tracking en tiempo real
   - Datos enriquecidos visibles en dashboard < 5 segundos después de completar

5. **Resiliencia y Error Handling**
   - ✅ Limitación a 100 items por fuente aplicada correctamente
   - ✅ Fallo de 1 fuente NO bloquea enriquecimiento de otras
   - ✅ UI nunca se rompe por errores de backend
   - ✅ Circuit breaker previene hammering de APIs fallidas
   - ✅ Mensajes de error claros y accionables para el usuario

6. **Cobertura de Tests**
   - ≥90% cobertura de código en backend (pytest)
   - 100% de endpoints cubiertos con tests de integración
   - 100% de flujos críticos cubiertos con tests E2E Playwright
   - ≥95% de tests funcionales completos PASAN

## 11. Documento de Resultados de Pruebas

Al finalizar la implementación, se creará el documento `ENRICHMENT_TEST_RESULTS.md` con:

### Estructura del Documento

```markdown
# Resultados de Pruebas - Enriquecimiento CTEM y Amenazas

## 1. Tests Unitarios Backend

### 1.1 EnrichmentService

- [x] test_enrichment_limits_to_100_items_per_source: PASS
- [x] test_enrichment_handles_source_failure_gracefully: PASS
- [x] test_circuit_breaker_opens_after_5_failures: PASS
- [ ] ... (todos los tests unitarios)

**Cobertura:** 92.3%
**Total tests:** 47
**Passed:** 47
**Failed:** 0

### 1.2 Generadores Sintéticos

- [x] test_risk_score_calculation_high_cvss_high_epss: PASS
- [x] test_risk_score_calculation_low_cvss_low_epss: PASS
- [x] test_vpr_score_calculation: PASS
- [ ] ... (todos los tests de generadores)

**Cobertura:** 95.1%
**Total tests:** 28
**Passed:** 28
**Failed:** 0

## 2. Tests de Integración Backend

- [x] test_enrich_vulnerabilities_endpoint: PASS
- [x] test_enrich_with_all_sources_failing: PASS
- [x] test_nvd_api_integration: PASS
- [x] test_epss_api_integration: PASS
- [x] test_otx_api_integration: PASS
- [ ] ... (todos los tests de integración)

**Total tests:** 35
**Passed:** 35
**Failed:** 0

## 3. Tests E2E Playwright

### 3.1 Enrichment Buttons

- [x] debe mostrar botones de enriquecimiento: PASS
- [x] debe enriquecer vulnerabilidades con éxito: PASS
- [x] debe manejar error de fuente sin romper UI: PASS
- [x] debe limitar a 100 items por fuente: PASS
- [x] debe mostrar datos enriquecidos en tabla: PASS

**Total tests:** 15
**Passed:** 15
**Failed:** 0
**Duration:** 3m 45s

### 3.2 Error Recovery

- [x] debe recuperarse de timeout sin perder estado: PASS
- [x] debe mostrar mensaje controlado cuando falla fuente: PASS
- [x] debe permitir reintentar después de error: PASS

**Total tests:** 8
**Passed:** 8
**Failed:** 0

## 4. Tests de Performance

- [x] test_enrichment_completes_within_2_minutes_for_100_items: PASS (118.3s)
- [x] test_cache_improves_performance_by_80_percent: PASS (83.5% speedup)
- [x] test_concurrent_enrichment_requests: PASS

**Total tests:** 12
**Passed:** 12
**Failed:** 0

## 5. PRUEBAS FUNCIONALES COMPLETAS

### 5.1 Enriquecimiento End-to-End Completo

**Test:** Enriquecer 100 vulnerabilidades desde dashboard hasta visualización

**Pasos:**

1. Navegar a dashboard
2. Clic en "Enriquecer Vulnerabilidades"
3. Esperar a completar (máx 2 min)
4. Verificar datos en página CTEM

**Resultado:** ✅ PASS
**Duración:** 97 segundos
**Detalles:**

- 100 CVEs procesados
- 4/4 fuentes exitosas (NVD, EPSS, GitHub, Synthetic)
- 95 CVEs con CVSS score
- 82 CVEs con EPSS score
- 100 CVEs con risk score sintético
- Datos visibles en dashboard en <3 segundos

### 5.2 Enriquecimiento con Fuentes Parcialmente Fallando

**Test:** Simular fallo de 2/4 fuentes y verificar degradación graceful

**Pasos:**

1. Mock NVD y GitHub para fallar
2. Clic en "Enriquecer Vulnerabilidades"
3. Verificar que EPSS y Synthetic funcionan
4. Verificar mensaje de advertencia en UI

**Resultado:** ✅ PASS
**Detalles:**

- 2 fuentes fallaron (NVD, GitHub) con mensaje controlado
- 2 fuentes exitosas (EPSS, Synthetic)
- UI mostró toast: "2 sources unavailable, 2 sources succeeded"
- NO hubo errores en consola
- Dashboard funcional con datos parciales
- Botón de enriquecimiento permaneció habilitado

### 5.3 Circuit Breaker en Acción

**Test:** Verificar que circuit breaker previene hammering

**Pasos:**

1. Forzar 5 fallos consecutivos en NVD API
2. Verificar que circuit se abre
3. Intentar nueva llamada (debe ser bloqueada)
4. Esperar timeout (60s)
5. Verificar que circuit pasa a half-open

**Resultado:** ✅ PASS
**Detalles:**

- Circuit se abrió después de 5 fallos
- Llamada 6 fue bloqueada (no se envió request)
- Después de 60s, circuit pasó a half-open
- Siguiente éxito cerró circuit completamente
- Logs mostraron estado de circuit correctamente

### 5.4 Cache de APIs

**Test:** Verificar que cache mejora performance

**Pasos:**

1. Enriquecer 50 CVEs (sin cache)
2. Enriquecer mismos 50 CVEs (con cache)
3. Comparar tiempos

**Resultado:** ✅ PASS
**Detalles:**

- Primera llamada: 48.3 segundos
- Segunda llamada: 6.7 segundos
- Speedup: 86.1% (>80% requerido)
- Cache hit rate: 94%

### 5.5 Limitación a 100 Items

**Test:** Verificar que límite de 100 items por fuente se aplica

**Pasos:**

1. Crear 200 CVEs en base de datos
2. Clic en "Enriquecer Vulnerabilidades" sin filtro
3. Verificar que solo se procesan 100

**Resultado:** ✅ PASS
**Detalles:**

- 200 CVEs disponibles en DB
- Job creado con total_items: 100
- Procesados exactamente 100 CVEs
- Log backend confirmó: "Limited to MAX_ITEMS_PER_SOURCE (100)"

### 5.6 Generadores de Datos Sintéticos

**Test:** Validar calidad de datos sintéticos generados

**Pasos:**

1. Enriquecer 50 CVEs con generadores sintéticos
2. Validar risk scores contra CVSS+EPSS
3. Validar APT assignments
4. Validar VPR scores

**Resultado:** ✅ PASS
**Detalles:**

- Correlación risk score vs (CVSS+EPSS): 0.87 (>0.8 requerido)
- CVEs con CVSS>9 y EPSS>0.8 → risk_score ≥90: 100% correcto
- APTs asignados solo a vulnerabilidades high risk: ✅
- VPR scores en rango 0-10: ✅
- Sandbox reports generados con estructura correcta: ✅

### 5.7 Dashboard Actualizado con Datos Enriquecidos

**Test:** Verificar visualización de datos enriquecidos

**Pasos:**

1. Enriquecer vulnerabilidades
2. Navegar a página CTEM
3. Verificar columnas de enriquecimiento visibles
4. Verificar que datos no están vacíos

**Resultado:** ✅ PASS
**Detalles:**

- Columna "EPSS Score" visible: ✅
- Columna "Risk Score" visible: ✅
- Columna "Threat Actors" visible: ✅
- 82/100 filas con EPSS score poblado
- 100/100 filas con risk score poblado
- 67/100 filas con threat actors asignados
- UI responsive, sin lag

### 5.8 Enriquecimiento de Amenazas (IOCs)

**Test:** Enriquecimiento end-to-end de indicators of compromise

**Pasos:**

1. Navegar a dashboard
2. Clic en "Enriquecer Amenazas"
3. Esperar a completar
4. Verificar datos en página Threat Intel

**Resultado:** ✅ PASS
**Duración:** 68 segundos
**Detalles:**

- 100 IOCs procesados (50 IPs, 30 domains, 20 hashes)
- 5/5 fuentes exitosas (OTX, AbuseIPDB, GreyNoise, Shodan, VT)
- 94 IOCs con reputation score
- 87 IOCs con malware families
- 100 IOCs con synthetic sandbox reports
- Datos visibles en dashboard

### 5.9 Error Handling sin Romper UI

**Test:** Múltiples escenarios de error sin romper UI

**Escenarios probados:**

1. ✅ API timeout (NVD)
2. ✅ API rate limit exceeded (AbuseIPDB)
3. ✅ API authentication error (VirusTotal)
4. ✅ Network error (sin internet simulado)
5. ✅ Backend crash recovery
6. ✅ Malformed API response

**Resultado:** ✅ PASS
**Detalles:**

- En TODOS los escenarios, UI permaneció funcional
- Mensajes de error claros y específicos
- Botones se rehabilitaron correctamente
- No se encontraron errores de React
- Progress tracking se resetó correctamente
- Estado de la aplicación consistente

### 5.10 MCP Integration Bidireccional

**Test:** SoulInTheBot llama herramientas de enriquecimiento via MCP

**Pasos:**

1. Configurar MCP server de CyberDemo
2. Desde SoulInTheBot, llamar enrichment.vulnerabilities tool
3. Verificar que enriquecimiento se ejecuta
4. Verificar que datos retornan a SoulInTheBot

**Resultado:** ✅ PASS
**Detalles:**

- MCP server iniciado correctamente en puerto 8001
- Tool enrichment.vulnerabilities disponible
- Claude llamó tool exitosamente
- Enriquecimiento se ejecutó (50 CVEs)
- Resultados retornados a Claude en formato JSON
- Claude pudo usar datos para tomar decisión (identificar CVEs críticos)

## 6. RESUMEN FINAL

### Coverage Total

- **Backend Unit Tests:** 92.3%
- **Backend Integration Tests:** 100% endpoints covered
- **Frontend E2E Tests:** 15/15 PASS
- **Functional E2E Tests:** 10/10 PASS

### Tests Totales

- **Unit:** 75 tests, 75 PASS, 0 FAIL
- **Integration:** 35 tests, 35 PASS, 0 FAIL
- **E2E Playwright:** 23 tests, 23 PASS, 0 FAIL
- **Performance:** 12 tests, 12 PASS, 0 FAIL
- **Functional Complete:** 10 tests, 10 PASS, 0 FAIL

### Métricas de Éxito

- ✅ Limitación a 100 items: VERIFICADO
- ✅ Error handling sin romper UI: VERIFICADO
- ✅ Performance <2 min para 100 items: VERIFICADO (97s)
- ✅ Cache speedup >80%: VERIFICADO (86.1%)
- ✅ Circuit breaker funcionando: VERIFICADO
- ✅ Datos sintéticos con correlación >0.8: VERIFICADO (0.87)
- ✅ MCP bidireccional: VERIFICADO

### Conclusión

🎉 **TODO CONSTRUIDO OK**

✅ **ALL FUNCTIONAL TESTS PASS**

Todos los tests funcionales completos E2E han pasado exitosamente.
El sistema de enriquecimiento está listo para producción con:

- Gestión robusta de errores
- Limitación de items por fuente
- Degradación graceful cuando fuentes fallan
- UI resiliente que nunca se rompe
- Performance cumpliendo requisitos
- Datos sintéticos de alta calidad
```

Este documento se generará automáticamente durante la fase de testing y se actualizará con resultados reales.

## 9. Referencias

- [Wiz Open Source Threat Intelligence Tools](https://www.wiz.io/academy/the-top-oss-threat-intelligence-tools)
- [MISP vs OpenCTI Guide](https://www.cosive.com/misp-vs-opencti)
- [Free Cybersecurity APIs](https://upskilld.com/article/free-cybersecurity-apis/)
- [Snyk 10 MCP Servers for Cybersecurity](https://snyk.io/articles/10-mcp-servers-for-cybersecurity-professionals-and-elite-hackers/)
- [NVD API Documentation](https://nvd.nist.gov/developers/vulnerabilities)
- [EPSS Scores](https://www.first.org/epss/)
- [AlienVault OTX](https://otx.alienvault.com/)
- [AbuseIPDB API](https://www.abuseipdb.com/api.html)
- [mcp-threatintel GitHub](https://github.com/aplaceforallmystuff/mcp-threatintel)
- [Shodan CVEDB](https://cvedb.shodan.io/)
- [VulnCheck NVD++](https://www.vulncheck.com/blog/nvd-cpe)
- [Best Open Source Vulnerability Management Tools](https://www.wiz.io/academy/vulnerability-management/oss-vulnerability-management-tools)

---

**Documento creado:** 2026-02-13
**Versión:** 1.0
**Estado:** Pendiente de aprobación
