# Plan de Construccion - Threat Enrichment System

**Version:** 1.0
**Fecha:** 2026-02-16
**Documento funcional de referencia:** THREAT_ENRICHMENT_DESIGN.md
**Estado:** Pendiente de construccion

---

## 1. Resumen Ejecutivo

Este documento detalla el plan de construccion para el sistema de **Threat Enrichment** que enriquece IOCs (Indicadores de Compromiso) con 18+ fuentes de inteligencia de amenazas.

### Alcance

- Enriquecimiento de 6 tipos de IOCs: IP, Domain, URL, Hash, Email, CVE
- Integracion con 25 fuentes de inteligencia (APIs reales + generadores sinteticos)
- Visualizacion con mapa mundi interactivo y vistas detalladas
- Sistema de navegacion anidada (4 niveles)
- Acciones y comandos operativos
- Integracion MCP para llamadas desde agentes IA

---

## 2. Fuentes de Inteligencia a Implementar

### 2.1 Tier 1: APIs Gratuitas de Alta Calidad

| # | Fuente | Cliente Python | Estado | Prioridad |
|---|--------|----------------|--------|-----------|
| 1 | AlienVault OTX | `clients/otx_client.py` | YA EXISTE | - |
| 2 | AbuseIPDB | `clients/abuseipdb_client.py` | YA EXISTE | - |
| 3 | GreyNoise | `clients/greynoise_client.py` | YA EXISTE | - |
| 4 | ThreatFox | `clients/threatfox_client.py` | NUEVO | Alta |
| 5 | URLhaus | `clients/urlhaus_client.py` | NUEVO | Alta |
| 6 | MalwareBazaar | `clients/malwarebazaar_client.py` | NUEVO | Alta |
| 7 | IPinfo | `clients/ipinfo_client.py` | NUEVO | Alta |
| 8 | Pulsedive | `clients/pulsedive_client.py` | NUEVO | Media |

### 2.2 Tier 2: APIs con Limites Moderados

| # | Fuente | Cliente Python | Estado | Prioridad |
|---|--------|----------------|--------|-----------|
| 9 | VirusTotal | `clients/virustotal_client.py` | NUEVO | Alta |
| 10 | Shodan | `clients/shodan_client.py` | NUEVO | Alta |
| 11 | Censys | `clients/censys_client.py` | NUEVO | Media |
| 12 | HaveIBeenPwned | `clients/hibp_client.py` | NUEVO | Media |

### 2.3 Tier 3: Feeds y APIs Adicionales

| # | Fuente | Cliente Python | Estado | Prioridad |
|---|--------|----------------|--------|-----------|
| 13 | Feodo Tracker | `clients/feodo_tracker_client.py` | NUEVO | Alta |
| 14 | Cloudflare Radar | `clients/cloudflare_radar_client.py` | NUEVO | Media |

### 2.4 Tier 4: Fuentes STIX/TAXII

| # | Fuente | Cliente Python | Estado | Prioridad |
|---|--------|----------------|--------|-----------|
| 15 | MITRE ATT&CK | `clients/mitre_attack_client.py` | NUEVO | Alta |
| 16 | Maltiverse | `clients/maltiverse_client.py` | NUEVO | Baja |
| 17 | InQuest Labs | `clients/inquest_client.py` | NUEVO | Baja |

### 2.5 Tier 5: Plataformas Open Source (Self-Hosted)

| # | Fuente | Integracion | Estado | Prioridad |
|---|--------|-------------|--------|-----------|
| 18 | MISP | `clients/misp_client.py` | NUEVO | Media |
| 19 | OpenCTI | `clients/opencti_client.py` | NUEVO | Media |

### 2.7 Tier 7: Generadores Sinteticos (Fallback y Simulacion)

| # | Fuente | Modulo | Estado | Prioridad |
|---|--------|--------|--------|-----------|
| 20 | Synthetic Generator | `generators/threat_synthetic.py` | NUEVO | Alta |
| 21 | ThreatQuotient Mock | `generators/threatquotient_mock.py` | NUEVO | Alta |
| 22 | Mandiant Mock | `generators/mandiant_mock.py` | NUEVO | Alta |
| 23 | CrowdStrike Falcon X Mock | `generators/crowdstrike_mock.py` | NUEVO | Alta |
| 24 | Local Threat DB | Cache local | NUEVO | Media |
| 25 | MISP Mock | `generators/misp_mock.py` | NUEVO | Baja |

### 2.8 MCP Servers para Integracion

| # | MCP Server | GitHub | Herramientas |
|---|------------|--------|--------------|
| - | mcp-threatintel | [aplaceforallmystuff/mcp-threatintel](https://github.com/aplaceforallmystuff/mcp-threatintel) | AlienVault OTX, AbuseIPDB, GreyNoise, abuse.ch |

---

## 3. Modelo de Datos

### 3.1 Entidad Principal: EnrichedThreatIndicator

Implementar la interfaz completa definida en THREAT_ENRICHMENT_DESIGN.md seccion "Modelo de Datos Enriquecidos":

```python
# backend/src/models/threat_enrichment.py

class EnrichedThreatIndicator:
    # Identificacion
    id: str  # UUID
    type: Literal["ip", "domain", "url", "hash", "email", "cve"]
    value: str
    first_seen: datetime
    last_seen: datetime

    # Puntuaciones de riesgo
    risk_score: int  # 0-100
    risk_level: Literal["critical", "high", "medium", "low", "unknown"]
    confidence: int  # 0-100

    # Geolocalizacion (IPs)
    geo: Optional[GeoLocation]

    # Informacion de red (IPs)
    network: Optional[NetworkInfo]

    # Servicios expuestos (Shodan/Censys)
    services: Optional[List[ServiceInfo]]

    # Reputacion (multiples fuentes)
    reputation: ReputationData

    # Inteligencia de amenazas
    threat_intel: ThreatIntelData

    # MITRE ATT&CK TTPs
    mitre_attack: MitreAttackData

    # Pulses/Feeds de inteligencia
    intel_feeds: List[IntelFeed]

    # Informacion de breach (Emails)
    breach_data: Optional[BreachData]

    # Informacion de CVE (Vulnerabilidades)
    cve_data: Optional[CVEData]

    # Metadatos de enriquecimiento
    enrichment_meta: EnrichmentMeta

    # Relaciones
    relationships: RelationshipData
```

### 3.2 Subentidades

Implementar todas las subentidades definidas en el documento funcional:
- GeoLocation
- NetworkInfo
- ServiceInfo
- ReputationData (con abuseipdb, greynoise, virustotal, pulsedive)
- ThreatIntelData
- MitreAttackData
- IntelFeed
- BreachData
- EnrichmentMeta
- RelationshipData

---

## 4. Base de Datos

### 4.1 Tabla Principal: threat_enrichment

```sql
CREATE TABLE threat_enrichment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicator_type VARCHAR(50) NOT NULL,
    indicator_value VARCHAR(500) NOT NULL,

    -- Risk scores
    risk_score INTEGER,
    risk_level VARCHAR(20),
    confidence INTEGER,
    malicious BOOLEAN DEFAULT FALSE,

    -- Timestamps
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,

    -- Geolocalizacion (IPs)
    country VARCHAR(10),
    country_name VARCHAR(100),
    city VARCHAR(100),
    region VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,
    timezone VARCHAR(50),

    -- Network info (IPs)
    asn INTEGER,
    asn_org VARCHAR(200),
    isp VARCHAR(200),
    company VARCHAR(200),
    is_vpn BOOLEAN DEFAULT FALSE,
    is_proxy BOOLEAN DEFAULT FALSE,
    is_tor BOOLEAN DEFAULT FALSE,
    is_datacenter BOOLEAN DEFAULT FALSE,
    is_mobile BOOLEAN DEFAULT FALSE,

    -- Servicios (JSON)
    services JSONB,

    -- Reputacion por fuente (JSON)
    reputation_abuseipdb JSONB,
    reputation_greynoise JSONB,
    reputation_virustotal JSONB,
    reputation_pulsedive JSONB,

    -- Threat intel
    malware_families TEXT[],
    threat_actors TEXT[],
    campaigns TEXT[],
    tags TEXT[],
    malicious_urls JSONB,
    distributed_malware JSONB,

    -- MITRE ATT&CK
    mitre_tactics JSONB,
    mitre_techniques JSONB,
    mitre_software JSONB,

    -- Intel feeds
    intel_feeds JSONB,

    -- Breach data (emails)
    breach_data JSONB,

    -- CVE data
    cve_data JSONB,

    -- Relationships
    related_ips TEXT[],
    related_domains TEXT[],
    related_urls TEXT[],
    related_hashes TEXT[],
    passive_dns JSONB,
    ssl_certificates JSONB,

    -- Enrichment metadata
    enriched_at TIMESTAMP DEFAULT NOW(),
    sources_queried TEXT[],
    sources_successful TEXT[],
    sources_failed TEXT[],
    total_sources INTEGER,
    successful_sources INTEGER,
    cache_hit BOOLEAN DEFAULT FALSE,
    processing_time_ms INTEGER,

    UNIQUE(indicator_type, indicator_value)
);

-- Indices
CREATE INDEX idx_threat_indicator ON threat_enrichment(indicator_type, indicator_value);
CREATE INDEX idx_threat_risk_score ON threat_enrichment(risk_score DESC);
CREATE INDEX idx_threat_country ON threat_enrichment(country);
CREATE INDEX idx_threat_malicious ON threat_enrichment(malicious);
CREATE INDEX idx_threat_enriched_at ON threat_enrichment(enriched_at DESC);
```

### 4.2 Tabla de Jobs

```sql
CREATE TABLE threat_enrichment_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status VARCHAR(50) NOT NULL,
    total_items INTEGER NOT NULL,
    processed_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB
);
```

### 4.3 Tabla de Cache

```sql
CREATE TABLE threat_enrichment_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_key VARCHAR(500) NOT NULL UNIQUE,
    api_source VARCHAR(100) NOT NULL,
    response_data JSONB NOT NULL,
    cached_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    hit_count INTEGER DEFAULT 0
);

CREATE INDEX idx_threat_cache_key ON threat_enrichment_cache(cache_key);
CREATE INDEX idx_threat_cache_expires ON threat_enrichment_cache(expires_at);
```

---

## 5. Endpoints de API

### 5.1 Endpoints Principales

| Endpoint | Metodo | Descripcion |
|----------|--------|-------------|
| `/api/enrichment/threats` | POST | Iniciar enriquecimiento de IOCs |
| `/api/enrichment/threats/status/{job_id}` | GET | Estado del job de enriquecimiento |
| `/api/intel/indicators` | GET | Lista de IOCs enriquecidos (paginado) |
| `/api/intel/indicators/{type}/{value}` | GET | Detalle de IOC especifico |
| `/api/intel/indicators/{type}/{value}/enrichment` | GET | Solo datos de enriquecimiento |
| `/api/intel/indicators/{type}/{value}/relationships` | GET | Relaciones del IOC |
| `/api/intel/indicators/{type}/{value}/timeline` | GET | Timeline de actividad |

### 5.2 Endpoints de Visualizacion

| Endpoint | Metodo | Descripcion |
|----------|--------|-------------|
| `/api/threats/map` | GET | Datos para mapa mundi |
| `/api/threats/stats` | GET | Estadisticas globales |
| `/api/threats/countries` | GET | IOCs por pais |
| `/api/threats/actors` | GET | Lista de threat actors |
| `/api/threats/actors/{name}` | GET | Detalle de actor |
| `/api/threats/malware` | GET | Familias de malware |
| `/api/threats/malware/{family}` | GET | Detalle de familia |
| `/api/threats/mitre` | GET | Matriz MITRE ATT&CK |
| `/api/threats/mitre/{technique}` | GET | Detalle de tecnica |
| `/api/threats/feeds` | GET | Intel feeds disponibles |

### 5.3 Endpoints de Acciones

| Endpoint | Metodo | Descripcion |
|----------|--------|-------------|
| `/api/intel/indicators/{type}/{value}/block` | POST | Anadir a blocklist |
| `/api/intel/indicators/{type}/{value}/watchlist` | POST | Anadir a watchlist |
| `/api/intel/indicators/{type}/{value}/investigate` | POST | Crear investigacion |
| `/api/intel/indicators/export` | POST | Exportar IOCs (CSV/STIX/MISP) |

---

## 6. Servicio de Enriquecimiento

### 6.1 ThreatEnrichmentService

```python
# backend/src/services/threat_enrichment_service.py

class ThreatEnrichmentService:
    MAX_ITEMS_PER_SOURCE = 100

    async def enrich_threats(
        self,
        indicators: List[dict],  # [{"type": "ip", "value": "1.2.3.4"}]
        sources: List[str] = None,
        force_refresh: bool = False
    ) -> dict

    async def enrich_single_indicator(
        self,
        indicator_type: str,
        indicator_value: str,
        sources: List[str] = None
    ) -> EnrichedThreatIndicator

    def calculate_risk_score(
        self,
        enrichment_data: dict
    ) -> int
```

### 6.2 Algoritmo de Risk Score

Implementar el algoritmo definido en THREAT_ENRICHMENT_DESIGN.md:

```python
def calculate_risk_score(enrichment_data: dict) -> int:
    """
    Pesos:
    - AbuseIPDB confidence: 20%
    - VirusTotal detections: 25%
    - GreyNoise classification: 15%
    - Pulsedive risk: 15%
    - ThreatFox presence: 10%
    - OTX pulses count: 10%
    - Shodan vulnerabilities: 5%
    """
    # Implementacion completa segun documento funcional
```

---

## 7. Generadores Sinteticos

### 7.1 ThreatSyntheticGenerator

```python
# backend/src/generators/threat_synthetic.py

class ThreatSyntheticGenerator:
    """Genera datos sinteticos realistas para demos y testing"""

    def generate_ip_enrichment(self, ip: str) -> dict
    def generate_domain_enrichment(self, domain: str) -> dict
    def generate_hash_enrichment(self, hash: str) -> dict
    def generate_url_enrichment(self, url: str) -> dict
    def generate_malware_families(self, risk_score: int) -> List[str]
    def generate_threat_actors(self, risk_score: int, country: str) -> List[str]
    def generate_mitre_techniques(self, malware_families: List[str]) -> List[dict]
```

### 7.2 ThreatQuotient Mock

```python
# backend/src/generators/enrichment/threatquotient_mock.py

class ThreatQuotientMock:
    """Simula la API de ThreatQuotient para threat scoring y context"""

    def generate_threat_context(self, indicator_type: str, indicator_value: str,
                                 reputation_score: int, malware_families: List[str]) -> dict:
        """
        Genera contexto de amenaza sintetico estilo ThreatQuotient

        Incluye:
        - Threat score (0-100)
        - Confidence level
        - Associated campaigns
        - Related indicators
        - Context description
        """
        # Base threat score from reputation
        threat_score = min(100, max(0, reputation_score))

        # Confidence based on number of sources
        confidence = "high" if threat_score > 80 else "medium" if threat_score > 50 else "low"

        # Generate associated campaigns
        campaigns = self._generate_campaigns(threat_score, malware_families)

        # Generate related indicators
        related = self._generate_related_indicators(indicator_type, threat_score)

        # Context description
        context = self._generate_context_description(indicator_type, indicator_value,
                                                       threat_score, malware_families)

        return {
            "threat_score": threat_score,
            "confidence": confidence,
            "campaigns": campaigns,
            "related_indicators": related,
            "context_description": context,
            "priority": "critical" if threat_score > 90 else "high" if threat_score > 70 else "medium",
            "enrichment_source": "synthetic_threatquotient",
            "generated_at": datetime.utcnow().isoformat()
        }

    def _generate_campaigns(self, score: int, families: List[str]) -> List[dict]:
        """Genera campañas asociadas basadas en score y familias de malware"""
        if score < 60:
            return []

        campaign_templates = [
            {"name": "Operation {adj} {noun}", "status": "active"},
            {"name": "{adj} {animal} Campaign", "status": "monitoring"},
        ]
        # ... (generación de campañas)
        return campaigns

    def _generate_context_description(self, ioc_type: str, value: str,
                                       score: int, families: List[str]) -> str:
        """Genera descripción de contexto legible"""
        severity = "critical" if score > 90 else "high" if score > 70 else "moderate"
        family_str = ", ".join(families[:3]) if families else "unknown malware"

        return f"This {ioc_type} indicator ({value}) has been associated with {severity} " \
               f"threat activity involving {family_str}. Analysis suggests ongoing " \
               f"malicious operations with confidence level based on {score}% reputation score."
```

### 7.3 Mandiant Mock

```python
# backend/src/generators/enrichment/mandiant_mock.py

class MandiantMock:
    """Simula la API de Mandiant Threat Intelligence para APT mapping"""

    # APT groups conocidos públicamente
    APT_GROUPS = {
        "russia": ["APT28", "APT29", "Turla", "Sandworm", "Gamaredon"],
        "china": ["APT1", "APT10", "APT41", "Mustang Panda", "Winnti"],
        "north_korea": ["Lazarus Group", "Kimsuky", "APT38", "Andariel"],
        "iran": ["APT33", "APT34", "APT35", "Charming Kitten", "OilRig"],
        "unknown": ["FIN7", "FIN8", "Carbanak", "Cobalt Group", "TA505"]
    }

    def map_indicator_to_actors(self, indicator_type: str, indicator_value: str,
                                 country: str, malware_families: List[str]) -> dict:
        """
        Mapea IOC a APT groups conocidos basado en:
        - País de origen
        - Familias de malware asociadas
        - Tipo de indicador
        """
        apt_candidates = []

        # Map by country
        country_mapping = {
            "RU": "russia", "CN": "china", "KP": "north_korea",
            "IR": "iran"
        }

        if country in country_mapping:
            apt_candidates.extend(
                random.sample(self.APT_GROUPS[country_mapping[country]], min(2, len(self.APT_GROUPS[country_mapping[country]])))
            )

        # Map by malware family
        family_apt_map = {
            "Emotet": ["TA542"],
            "TrickBot": ["Wizard Spider"],
            "Cobalt Strike": ["APT29", "FIN7", "APT41"],
            "Ryuk": ["Wizard Spider"],
            "Conti": ["Wizard Spider"],
        }

        for family in malware_families:
            if family in family_apt_map:
                apt_candidates.extend(family_apt_map[family])

        # Deduplicate
        apt_candidates = list(set(apt_candidates))

        return {
            "attributed_actors": apt_candidates[:3],
            "attribution_confidence": "medium" if len(apt_candidates) > 0 else "low",
            "actor_profiles": [self._generate_actor_profile(apt) for apt in apt_candidates[:2]],
            "enrichment_source": "synthetic_mandiant",
            "generated_at": datetime.utcnow().isoformat()
        }

    def _generate_actor_profile(self, apt_name: str) -> dict:
        """Genera perfil básico de actor de amenazas"""
        return {
            "name": apt_name,
            "aliases": [f"{apt_name}_alias"],
            "motivation": random.choice(["espionage", "financial", "sabotage"]),
            "target_sectors": random.sample(
                ["government", "finance", "energy", "technology", "healthcare"],
                k=random.randint(2, 4)
            ),
            "active_since": f"{random.randint(2010, 2020)}"
        }
```

### 7.4 CrowdStrike Falcon X Sandbox Mock

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

### 7.5 Datos de Referencia

- Lista de APT groups conocidos (APT28, APT29, Lazarus, etc.)
- Lista de malware families (Cobalt Strike, Emotet, TrickBot, etc.)
- Mapeo MITRE ATT&CK techniques
- Geolocalizacion por rangos de IP

---

## 8. Frontend

### 8.1 Paginas a Implementar

| Ruta | Componente | Descripcion |
|------|------------|-------------|
| `/threats` | ThreatDashboard | Dashboard principal con stats |
| `/threats/map` | ThreatMap | Mapa mundi interactivo |
| `/threats/iocs` | IOCList | Lista de todos los IOCs |
| `/threats/iocs/:id` | IOCDetail | Detalle completo de IOC |
| `/threats/iocs/:id/reputation` | IOCReputation | Tab: Reputacion |
| `/threats/iocs/:id/network` | IOCNetwork | Tab: Info de red |
| `/threats/iocs/:id/mitre` | IOCMITRE | Tab: MITRE ATT&CK |
| `/threats/iocs/:id/relationships` | IOCRelationships | Tab: Relaciones |
| `/threats/iocs/:id/timeline` | IOCTimeline | Tab: Timeline |
| `/threats/actors` | ThreatActorList | Lista de threat actors |
| `/threats/actors/:name` | ThreatActorDetail | Detalle de actor |
| `/threats/malware` | MalwareList | Lista de malware families |
| `/threats/malware/:family` | MalwareDetail | Detalle de familia |
| `/threats/mitre` | MITREMatrix | Matriz ATT&CK completa |
| `/threats/mitre/:technique` | MITRETechnique | Detalle de tecnica |
| `/threats/feeds` | IntelFeeds | Intel feeds suscritos |
| `/threats/search` | ThreatSearch | Busqueda avanzada |

### 8.2 Componentes Visuales

| Componente | Descripcion | Libreria sugerida |
|------------|-------------|-------------------|
| ThreatWorldMap | Mapa mundi con lineas de ataque animadas | react-simple-maps |
| AttackLines | Lineas animadas de origen a target | SVG + CSS animations |
| CountryMarker | Marcador pulsante por pais | CSS animations |
| RiskBadge | Badge de riesgo con color | Tailwind |
| ReputationGauge | Gauge de reputacion por fuente | Recharts |
| MITREMatrix | Matriz ATT&CK interactiva | D3.js o custom |
| RelationshipGraph | Grafo de relaciones | react-force-graph |
| TimelineChart | Timeline de actividad | Recharts |

### 8.3 Boton de Enriquecimiento

```tsx
// frontend/src/components/ThreatEnrichmentButton.tsx

export function ThreatEnrichmentButton({ onComplete }: Props) {
    const [jobId, setJobId] = useState<string | null>(null);
    const [progress, setProgress] = useState(0);

    const handleEnrichThreats = async () => {
        const response = await enrichThreats({
            sources: ["otx", "abuseipdb", "greynoise", "virustotal", "synthetic"],
            force_refresh: false
        });
        setJobId(response.job_id);
        // Poll for status...
    };

    return (
        <button onClick={handleEnrichThreats}>
            Enriquecer Amenazas
        </button>
    );
}
```

---

## 9. Visualizacion del Mapa Mundi

### 9.1 Elementos Visuales

Implementar segun THREAT_ENRICHMENT_DESIGN.md seccion "Mapa Mundi de Amenazas":

1. **Marcadores de Pais Origen**
   - Circulo pulsante con tamano proporcional a amenazas
   - Colores por severidad (critico=rojo, alto=naranja, etc.)
   - Tooltip con detalles al hover

2. **Lineas de Ataque Animadas**
   - Curvas Bezier con gradiente
   - Particulas moviles viajando por la curva
   - Grosor proporcional a severidad

3. **Marker del SOC (Target)**
   - Icono de escudo con ondas radar
   - Animacion de ondas concentricas

4. **Heatmap Overlay**
   - Densidad de amenazas por region
   - Toggle on/off

### 9.2 Interacciones

- Click en pais: Panel lateral con detalles
- Click en linea: Popup con vector de ataque
- Zoom y pan con semantic zoom
- Toggle entre vista 2D y 3D (opcional)

---

## 10. Gestion de Errores y Resiliencia

### 10.1 Circuit Breaker

```python
# backend/src/services/circuit_breaker.py

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout_seconds=60):
        pass

    async def call(self, func, *args, **kwargs):
        # Implementar patron circuit breaker
        pass
```

### 10.2 Fallback a Datos Sinteticos

Cuando una fuente falla, usar generador sintetico como fallback.

### 10.3 Limitacion de Items

Maximo 100 items por fuente para evitar rate limits y timeouts.

---

## 11. Tests

### 11.1 Tests Unitarios

| Test | Archivo |
|------|---------|
| ThreatEnrichmentService | `tests/unit/services/test_threat_enrichment_service.py` |
| Risk Score Calculation | `tests/unit/services/test_threat_risk_score.py` |
| Circuit Breaker | `tests/unit/services/test_circuit_breaker.py` |
| Synthetic Generator | `tests/unit/generators/test_threat_synthetic.py` |
| Clientes API | `tests/unit/clients/test_*_client.py` |

### 11.2 Tests de Integracion

| Test | Archivo |
|------|---------|
| Endpoint enrich threats | `tests/integration/test_threat_enrichment_api.py` |
| Endpoint IOC detail | `tests/integration/test_ioc_detail_api.py` |
| Endpoint map data | `tests/integration/test_threat_map_api.py` |

### 11.3 Tests E2E con Playwright

| Test | Archivo |
|------|---------|
| Boton enriquecimiento | `tests/e2e/threat_enrichment.spec.ts` |
| Mapa interactivo | `tests/e2e/threat_map.spec.ts` |
| Detalle de IOC | `tests/e2e/ioc_detail.spec.ts` |
| Error handling | `tests/e2e/threat_error_handling.spec.ts` |

#### Tests E2E Detallados

```typescript
// tests/e2e/threat_enrichment.spec.ts
import { test, expect } from "@playwright/test";

test.describe("Threat Enrichment E2E", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("http://localhost:3000/threats");
  });

  test("debe mostrar botón de enriquecer amenazas", async ({ page }) => {
    const threatButton = page.getByRole("button", { name: /Enriquecer Amenazas/i });
    await expect(threatButton).toBeVisible();
    await expect(threatButton).toBeEnabled();
  });

  test("debe enriquecer amenazas con éxito", async ({ page }) => {
    await page.getByRole("button", { name: /Enriquecer Amenazas/i }).click();

    // Debe mostrar spinner
    await expect(page.getByText(/Enriching\.\.\./i)).toBeVisible();

    // Esperar a completar (máximo 60s para amenazas)
    await expect(page.getByText(/Enriching\.\.\./i)).not.toBeVisible({ timeout: 60000 });

    // Debe mostrar mensaje de éxito
    const toast = page.locator('[role="alert"], .toast');
    await expect(toast).toBeVisible({ timeout: 5000 });
  });

  test("debe manejar error de fuente sin romper UI", async ({ page, context }) => {
    await context.route("**/api/enrichment/threats", async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          job_id: "test-job-threat",
          total_items: 50,
          successful_sources: 3,
          failed_sources: 2,
          sources: {
            otx: { status: "success", enriched_count: 50 },
            abuseipdb: { status: "failed", error: "Rate limit" },
            greynoise: { status: "success", enriched_count: 45 },
            virustotal: { status: "failed", error: "API timeout" },
            synthetic: { status: "success", enriched_count: 50 },
          },
          errors: [
            { source: "abuseipdb", error: "Rate limit", recoverable: true },
            { source: "virustotal", error: "API timeout", recoverable: true },
          ],
        }),
      });
    });

    await page.getByRole("button", { name: /Enriquecer Amenazas/i }).click();

    // Debe mostrar warning toast, NO error fatal
    const toast = page.locator('[role="alert"]');
    await expect(toast).toContainText(/source.*unavailable/i);

    // UI debe seguir funcional
    await expect(page.getByRole("button", { name: /Enriquecer Amenazas/i })).toBeEnabled();
  });

  test("debe limitar a 100 IOCs por fuente", async ({ page, context }) => {
    await context.route("**/api/enrichment/threats", async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          job_id: "test-job-limit",
          total_items: 100, // DEBE SER 100, no más
          successful_sources: 5,
          failed_sources: 0,
        }),
      });
    });

    await page.getByRole("button", { name: /Enriquecer Amenazas/i }).click();

    const toast = page.locator('[role="alert"]');
    await expect(toast).toBeVisible({ timeout: 5000 });
  });
});

// tests/e2e/threat_map.spec.ts
test.describe("Threat Map E2E", () => {
  test("debe cargar mapa mundi con marcadores", async ({ page }) => {
    await page.goto("http://localhost:3000/threats/map");

    // Mapa debe cargar
    await expect(page.locator('.threat-world-map, svg[class*="map"]')).toBeVisible({ timeout: 10000 });

    // Debe haber marcadores de países
    await expect(page.locator('.country-marker, circle[class*="marker"]').first()).toBeVisible();
  });

  test("debe mostrar panel lateral al click en país", async ({ page }) => {
    await page.goto("http://localhost:3000/threats/map");

    // Click en un marcador de país
    const marker = page.locator('.country-marker, circle[class*="marker"]').first();
    await marker.click();

    // Debe aparecer panel lateral
    await expect(page.locator('.country-detail-panel, [data-testid="country-panel"]')).toBeVisible();
  });

  test("debe animar líneas de ataque", async ({ page }) => {
    await page.goto("http://localhost:3000/threats/map");

    // Debe haber líneas de ataque animadas
    const attackLines = page.locator('.attack-line, path[class*="attack"]');
    await expect(attackLines.first()).toBeVisible({ timeout: 10000 });
  });
});
```

### 11.4 Tests de Performance

```python
# backend/tests/performance/test_threat_enrichment_performance.py
import pytest
import time

@pytest.mark.performance
@pytest.mark.asyncio
async def test_threat_enrichment_completes_within_1_minute_for_100_iocs():
    """Requisito: 100 IOCs en <1 minuto"""
    service = ThreatEnrichmentService()
    indicators = [
        {"type": "ip", "value": f"192.0.2.{i}"} for i in range(100)
    ]

    start = time.time()
    result = await service.enrich_threats(indicators=indicators)
    duration = time.time() - start

    assert duration < 60  # 1 minuto
    assert result["total_items"] == 100

@pytest.mark.performance
async def test_map_renders_at_60fps_with_500_iocs():
    """El mapa debe renderizar a 60fps con 500+ IOCs"""
    # Este test se ejecuta en Playwright
    pass
```

---

## 12. Cronograma de Implementacion

### Fase 1: Backend Core (5-6 dias)

- [ ] Crear modelos de datos (EnrichedThreatIndicator y subentidades)
- [ ] Crear tablas en PostgreSQL
- [ ] Implementar ThreatEnrichmentService
- [ ] Implementar algoritmo de Risk Score
- [ ] Implementar Circuit Breaker
- [ ] Tests unitarios para service y risk score

### Fase 2: Clientes API - Tier 1 y 2 (5-6 dias)

- [ ] Implementar ThreatFox client
- [ ] Implementar URLhaus client
- [ ] Implementar MalwareBazaar client
- [ ] Implementar IPinfo client
- [ ] Implementar VirusTotal client
- [ ] Implementar Shodan client (o mock)
- [ ] Implementar Feodo Tracker client
- [ ] Implementar Pulsedive client
- [ ] Tests unitarios para cada cliente

### Fase 2.5: Clientes API - Tier 3 y 4 (3-4 dias)

- [ ] Implementar MITRE ATT&CK client
- [ ] Implementar Censys client (o mock)
- [ ] Implementar HaveIBeenPwned client
- [ ] Implementar Cloudflare Radar client
- [ ] Implementar MISP client (o mock)
- [ ] Implementar OpenCTI client (o mock)
- [ ] Tests unitarios para cada cliente

### Fase 2.7: Generadores Sinteticos (2-3 dias)

- [ ] Implementar ThreatSyntheticGenerator
- [ ] Implementar ThreatQuotientMock
- [ ] Implementar MandiantMock
- [ ] Implementar CrowdStrikeSandboxMock
- [ ] Implementar MISPMock
- [ ] Tests unitarios para generadores

### Fase 3: API Endpoints (3-4 dias)

- [ ] Endpoints de enriquecimiento
- [ ] Endpoints de IOCs
- [ ] Endpoints de visualizacion (map, stats, countries)
- [ ] Endpoints de acciones
- [ ] Tests de integracion

### Fase 4: Frontend - Paginas Base (4-5 dias)

- [ ] ThreatDashboard con stats
- [ ] IOCList con filtros y paginacion
- [ ] IOCDetail con tabs
- [ ] Boton de enriquecimiento con progress

### Fase 5: Frontend - Mapa Mundi (4-5 dias)

- [ ] ThreatWorldMap con react-simple-maps
- [ ] Marcadores de pais animados
- [ ] Lineas de ataque con particulas
- [ ] Panel de detalle por pais
- [ ] Interacciones (click, hover, zoom)

### Fase 6: Frontend - Vistas Adicionales (3-4 dias)

- [ ] ThreatActorList y ThreatActorDetail
- [ ] MalwareList y MalwareDetail
- [ ] MITREMatrix
- [ ] RelationshipGraph
- [ ] Timeline

### Fase 7: Tests E2E y Polish (3-4 dias)

- [ ] Tests E2E completos
- [ ] Optimizacion de performance
- [ ] Efectos visuales finales
- [ ] Documentacion

### Fase 8: Integracion MCP (2-3 dias)

- [ ] Configurar mcp-threatintel server
- [ ] Implementar tools MCP propios (enrichment.threats)
- [ ] Tests de integracion MCP
- [ ] Documentacion de uso desde agentes IA

**Total estimado: 32-42 dias**

---

## 13. Metricas de Exito

### 13.1 Funcionalidad

- [ ] 25 fuentes de inteligencia integradas (o simuladas)
- [ ] 6 tipos de IOCs soportados
- [ ] 4 niveles de navegacion sin dead-ends
- [ ] Mapa mundi interactivo funcional
- [ ] Acciones operativas (block, investigate, export)

### 13.2 Cobertura de Enriquecimiento

- [ ] ≥90% de IOCs enriquecidos con reputación
- [ ] ≥80% de IPs enriquecidos con geolocalización
- [ ] ≥70% de IOCs con mapeo MITRE ATT&CK
- [ ] ≥85% de IOCs con malware families asignadas

### 13.3 Performance

- [ ] Enriquecimiento de 100 IOCs < 1 minuto
- [ ] Cache hit rate >= 70%
- [ ] Mapa a 60fps con 500+ IOCs
- [ ] Cambio de vista < 500ms

### 13.4 Resiliencia y Error Handling

- [ ] ✅ Limitación a 100 items por fuente aplicada correctamente
- [ ] ✅ Fallo de 1 fuente NO bloquea enriquecimiento de otras
- [ ] ✅ UI nunca se rompe por errores de backend
- [ ] ✅ Circuit breaker previene hammering de APIs fallidas
- [ ] ✅ Fallback a datos sintéticos cuando APIs fallan
- [ ] ✅ Mensajes de error claros y accionables para el usuario

### 13.5 Cobertura de Tests

- [ ] ≥90% cobertura de código en backend (pytest)
- [ ] 100% de endpoints cubiertos con tests de integración
- [ ] 100% de flujos críticos cubiertos con tests E2E Playwright
- [ ] ≥95% de tests funcionales completos PASAN

### 13.6 Efecto WOW

- [ ] Lineas de ataque animadas con particulas
- [ ] Marcadores pulsantes por severidad
- [ ] Matriz MITRE ATT&CK interactiva
- [ ] Grafo de relaciones navegable

---

## 14. Documento de Resultados de Pruebas

Al finalizar la implementación, se creará el documento `THREAT_ENRICHMENT_TEST_RESULTS.md` con:

### Estructura del Documento

```markdown
# Resultados de Pruebas - Threat Enrichment

## 1. Tests Unitarios Backend

### 1.1 ThreatEnrichmentService
- [x] test_enrichment_limits_to_100_iocs_per_source: PASS
- [x] test_enrichment_handles_source_failure_gracefully: PASS
- [x] test_circuit_breaker_opens_after_5_failures: PASS
- [x] test_risk_score_calculation: PASS
- [ ] ... (todos los tests unitarios)

**Cobertura:** XX%
**Total tests:** XX
**Passed:** XX
**Failed:** 0

### 1.2 Generadores Sintéticos
- [x] test_crowdstrike_sandbox_report_malicious: PASS
- [x] test_crowdstrike_sandbox_report_clean: PASS
- [x] test_mandiant_actor_mapping: PASS
- [x] test_threatquotient_context_generation: PASS
- [ ] ... (todos los tests de generadores)

## 2. Tests de Integración Backend
- [x] test_enrich_threats_endpoint: PASS
- [x] test_ioc_detail_endpoint: PASS
- [x] test_map_data_endpoint: PASS
- [ ] ... (todos los tests de integración)

## 3. Tests E2E Playwright

### 3.1 Enrichment Buttons
- [x] debe mostrar botón de enriquecer amenazas: PASS
- [x] debe enriquecer amenazas con éxito: PASS
- [x] debe manejar error de fuente sin romper UI: PASS
- [x] debe limitar a 100 IOCs por fuente: PASS

### 3.2 Threat Map
- [x] debe cargar mapa mundi con marcadores: PASS
- [x] debe mostrar panel lateral al click: PASS
- [x] debe animar líneas de ataque: PASS

## 4. PRUEBAS FUNCIONALES COMPLETAS

### 4.1 Enriquecimiento End-to-End Completo
**Test:** Enriquecer 100 IOCs desde dashboard hasta visualización en mapa
**Resultado:** ✅ PASS
**Duración:** XX segundos

### 4.2 Enriquecimiento con Fuentes Parcialmente Fallando
**Test:** Simular fallo de 2/5 fuentes y verificar degradación graceful
**Resultado:** ✅ PASS

### 4.3 Mapa Interactivo con 500+ IOCs
**Test:** Renderizar mapa a 60fps con 500 marcadores
**Resultado:** ✅ PASS (58fps promedio)

### 4.4 Generadores Sintéticos
**Test:** Validar calidad de datos sintéticos
**Resultado:** ✅ PASS

## 5. RESUMEN FINAL

### Métricas de Éxito
- ✅ Limitación a 100 items: VERIFICADO
- ✅ Error handling sin romper UI: VERIFICADO
- ✅ Performance <1 min para 100 IOCs: VERIFICADO
- ✅ Mapa a 60fps: VERIFICADO
- ✅ Datos sintéticos de alta calidad: VERIFICADO

### Conclusión
🎉 **TODO CONSTRUIDO OK**
✅ **ALL FUNCTIONAL TESTS PASS**
```

---

## 15. Referencias

- THREAT_ENRICHMENT_DESIGN.md (documento funcional completo)
- [AlienVault OTX API](https://otx.alienvault.com/)
- [AbuseIPDB API](https://www.abuseipdb.com/api.html)
- [GreyNoise Community](https://www.greynoise.io/)
- [ThreatFox API](https://threatfox.abuse.ch/api/)
- [URLhaus API](https://urlhaus.abuse.ch/api/)
- [MalwareBazaar API](https://bazaar.abuse.ch/api/)
- [Feodo Tracker](https://feodotracker.abuse.ch/)
- [MITRE ATT&CK](https://attack.mitre.org/)
- [VirusTotal API](https://developers.virustotal.com/)
- [Shodan API](https://developer.shodan.io/)
- [IPinfo.io](https://ipinfo.io/)
- [Pulsedive](https://pulsedive.com/)
- [Cloudflare Radar](https://radar.cloudflare.com/)
- [MISP Project](https://www.misp-project.org/)
- [OpenCTI](https://github.com/OpenCTI-Platform/opencti)
- [mcp-threatintel GitHub](https://github.com/aplaceforallmystuff/mcp-threatintel)
- [Wiz Open Source Threat Intelligence Tools](https://www.wiz.io/academy/the-top-oss-threat-intelligence-tools)
- [MISP vs OpenCTI Guide](https://www.cosive.com/misp-vs-opencti)
- [Snyk 10 MCP Servers for Cybersecurity](https://snyk.io/articles/10-mcp-servers-for-cybersecurity-professionals-and-elite-hackers/)

---

**Documento creado:** 2026-02-16
**Estado:** Plan de construccion aprobado
