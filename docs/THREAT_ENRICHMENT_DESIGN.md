# Diseño del Sistema de Enriquecimiento de Amenazas (Threat Enrichment)

**Versión:** 2.0
**Fecha:** 2026-02-16
**Estado:** DISEÑO COMPLETO
**Objetivo:** Sistema de enriquecimiento de IOCs de nivel enterprise que impresione a expertos en ciberseguridad

---

## 🎯 Visión General

El sistema de **Threat Enrichment** consulta **18+ fuentes de inteligencia de amenazas** para enriquecer cada Indicador de Compromiso (IOC) con contexto completo: reputación, geolocalización, ASN, malware asociado, campañas de ataque, tácticas MITRE ATT&CK, y más.

### Tipos de IOCs Soportados

| Tipo                            | Ejemplo                            | Fuentes Principales                  |
| ------------------------------- | ---------------------------------- | ------------------------------------ |
| **IP Address**                  | `192.168.1.100`                    | AbuseIPDB, GreyNoise, OTX, Shodan    |
| **Domain**                      | `evil-malware.com`                 | VirusTotal, URLhaus, Pulsedive       |
| **URL**                         | `http://bad.com/mal.exe`           | URLhaus, VirusTotal, ThreatFox       |
| **File Hash** (MD5/SHA1/SHA256) | `d41d8cd98f00b204e9800998ecf8427e` | VirusTotal, MalwareBazaar, ThreatFox |
| **Email**                       | `attacker@evil.com`                | HaveIBeenPwned, Pulsedive            |
| **CVE**                         | `CVE-2024-12345`                   | NVD, EPSS, GitHub Advisories         |

---

## 🔌 Fuentes de Inteligencia de Amenazas

### Tier 1: APIs Gratuitas de Alta Calidad

| #   | Fuente                                           | API  | Límite Free | Datos que Aporta                                                      |
| --- | ------------------------------------------------ | ---- | ----------- | --------------------------------------------------------------------- |
| 1   | **[AlienVault OTX](https://otx.alienvault.com)** | REST | Ilimitado   | Pulses, malware families, ATT&CK TTPs, threat actors                  |
| 2   | **[AbuseIPDB](https://www.abuseipdb.com)**       | REST | 1,000/día   | Confidence score (0-100), abuse reports, ISP, usage type              |
| 3   | **[GreyNoise](https://www.greynoise.io)**        | REST | 50/día      | Internet scanner detection, classification (benign/malicious/unknown) |
| 4   | **[ThreatFox](https://threatfox.abuse.ch)**      | REST | Ilimitado   | Malware IOCs, malware families, tags, threat types                    |
| 5   | **[URLhaus](https://urlhaus.abuse.ch)**          | REST | Ilimitado   | Malicious URLs, distribution method, payload type                     |
| 6   | **[MalwareBazaar](https://bazaar.abuse.ch)**     | REST | Ilimitado   | Malware samples, signatures, YARA rules                               |
| 7   | **[IPinfo](https://ipinfo.io)**                  | REST | 50,000/mes  | Geolocation, ASN, company, VPN/proxy/Tor detection                    |
| 8   | **[Pulsedive](https://pulsedive.com)**           | REST | 100/día     | Risk score, risk factors, related threats, feeds                      |

### Tier 2: APIs Gratuitas con Límites Moderados

| #   | Fuente                                           | API  | Límite Free          | Datos que Aporta                                          |
| --- | ------------------------------------------------ | ---- | -------------------- | --------------------------------------------------------- |
| 9   | **[VirusTotal](https://www.virustotal.com)**     | REST | 500/día              | AV detections, sandboxing, relationships, community score |
| 10  | **[Shodan](https://www.shodan.io)**              | REST | 100/mes              | Open ports, services, banners, CVEs, hostnames            |
| 11  | **[Censys](https://censys.io)**                  | REST | 250/mes              | Services, certificates, autonomous systems                |
| 12  | **[HaveIBeenPwned](https://haveibeenpwned.com)** | REST | Pwned Passwords free | Breach exposure, breach names, breach dates               |

### Tier 3: Fuentes Sin API (Scraping Limitado o STIX/TAXII)

| #   | Fuente                                       | Método     | Datos que Aporta                                       |
| --- | -------------------------------------------- | ---------- | ------------------------------------------------------ |
| 13  | **[MITRE ATT&CK](https://attack.mitre.org)** | STIX/TAXII | Tactics, techniques, procedures (TTPs), threat actors  |
| 14  | **[Maltiverse](https://maltiverse.com)**     | REST       | Aggregated IOCs from 100+ sources, risk classification |
| 15  | **[InQuest Labs](https://labs.inquest.net)** | REST       | DFI (Deep File Inspection), YARA intelligence          |

### Tier 4: Datos Sintéticos (Fallback cuando APIs fallan)

| #   | Fuente                  | Datos que Aporta                           |
| --- | ----------------------- | ------------------------------------------ |
| 16  | **Synthetic Generator** | Realistic mock data para demos y testing   |
| 17  | **Local Threat DB**     | Cached historical enrichment data          |
| 18  | **MISP Instance**       | Organization-specific threat intel sharing |

---

## 📊 Modelo de Datos Enriquecidos

### Estructura de IOC Enriquecido

```typescript
interface EnrichedThreatIndicator {
  // === IDENTIFICACIÓN ===
  id: string; // UUID único
  type: "ip" | "domain" | "url" | "hash" | "email" | "cve";
  value: string; // El IOC en sí
  first_seen: string; // ISO 8601
  last_seen: string;

  // === PUNTUACIONES DE RIESGO ===
  risk_score: number; // 0-100 (agregado de todas las fuentes)
  risk_level: "critical" | "high" | "medium" | "low" | "unknown";
  confidence: number; // 0-100 (confianza en la clasificación)

  // === GEOLOCALIZACIÓN (IPs) ===
  geo?: {
    country: string; // "ES", "US", etc.
    country_name: string; // "Spain", "United States"
    city: string;
    region: string;
    latitude: number;
    longitude: number;
    timezone: string;
  };

  // === INFORMACIÓN DE RED (IPs) ===
  network?: {
    asn: number; // Autonomous System Number
    asn_org: string; // "Google LLC"
    isp: string;
    company: string;
    is_vpn: boolean;
    is_proxy: boolean;
    is_tor: boolean;
    is_datacenter: boolean;
    is_mobile: boolean;
  };

  // === SERVICIOS EXPUESTOS (IPs, Shodan/Censys) ===
  services?: {
    port: number;
    protocol: string;
    service: string;
    version: string;
    banner: string;
    cves: string[]; // CVEs asociadas al servicio
  }[];

  // === REPUTACIÓN (Múltiples Fuentes) ===
  reputation: {
    abuseipdb?: {
      confidence_score: number; // 0-100
      total_reports: number;
      last_reported: string;
      abuse_categories: string[]; // "SSH Brute Force", "Port Scan", etc.
    };
    greynoise?: {
      classification: "benign" | "malicious" | "unknown";
      noise: boolean; // ¿Es un scanner conocido?
      riot: boolean; // ¿Es infraestructura legítima?
      bot: boolean;
      vpn: boolean;
      actor: string; // "Shodan", "Censys", etc.
    };
    virustotal?: {
      malicious_count: number; // AV detections
      suspicious_count: number;
      harmless_count: number;
      undetected_count: number;
      community_score: number; // -100 to +100
      last_analysis_date: string;
    };
    pulsedive?: {
      risk: "critical" | "high" | "medium" | "low" | "unknown";
      risk_factors: string[]; // Razones del score
      feeds_count: number; // Apariciones en feeds
    };
  };

  // === INTELIGENCIA DE AMENAZAS ===
  threat_intel: {
    // Malware asociado
    malware_families: string[]; // ["Emotet", "TrickBot", "Cobalt Strike"]

    // Actores de amenazas
    threat_actors: string[]; // ["APT29", "Lazarus Group"]

    // Campañas conocidas
    campaigns: string[]; // ["SolarWinds", "Log4Shell exploitation"]

    // Tags de la comunidad
    tags: string[]; // ["c2", "botnet", "phishing", "ransomware"]

    // URLs maliciosas asociadas (para IPs/dominios)
    malicious_urls?: {
      url: string;
      threat: string;
      date_added: string;
    }[];

    // Hashes de malware distribuidos (para IPs/URLs)
    distributed_malware?: {
      hash: string;
      hash_type: "md5" | "sha1" | "sha256";
      malware_name: string;
      file_type: string;
    }[];
  };

  // === MITRE ATT&CK TTPs ===
  mitre_attack: {
    tactics: {
      id: string; // "TA0001"
      name: string; // "Initial Access"
    }[];
    techniques: {
      id: string; // "T1566.001"
      name: string; // "Spearphishing Attachment"
      data_sources: string[];
    }[];
    software: {
      id: string; // "S0154"
      name: string; // "Cobalt Strike"
    }[];
  };

  // === PULSES/FEEDS DE INTELIGENCIA ===
  intel_feeds: {
    source: string; // "AlienVault OTX", "ThreatFox"
    feed_name: string;
    feed_id: string;
    description: string;
    created: string;
    author: string;
    tlp: "white" | "green" | "amber" | "red";
    reference_urls: string[];
  }[];

  // === INFORMACIÓN DE BREACH (Emails) ===
  breach_data?: {
    breached: boolean;
    breach_count: number;
    breaches: {
      name: string; // "LinkedIn"
      breach_date: string;
      pwn_count: number;
      data_classes: string[]; // ["Email", "Password", "Phone"]
    }[];
    paste_count: number; // Apariciones en pastes
  };

  // === INFORMACIÓN DE CVE (Vulnerabilidades) ===
  cve_data?: {
    cvss_v3_score: number;
    cvss_v3_vector: string;
    cvss_v2_score: number;
    epss_score: number; // Exploit Prediction Scoring
    epss_percentile: number;
    cwe_ids: string[]; // ["CWE-79", "CWE-89"]
    cpe_uris: string[];
    exploited_in_wild: boolean; // CISA KEV
    has_public_exploit: boolean;
    references: {
      url: string;
      source: string;
      tags: string[]; // ["Exploit", "Patch", "Vendor Advisory"]
    }[];
  };

  // === METADATOS DE ENRIQUECIMIENTO ===
  enrichment_meta: {
    enriched_at: string; // ISO 8601
    sources_queried: string[];
    sources_successful: string[];
    sources_failed: string[];
    total_sources: number;
    successful_sources: number;
    cache_hit: boolean;
    processing_time_ms: number;
  };

  // === RELACIONES ===
  relationships: {
    related_ips: string[];
    related_domains: string[];
    related_urls: string[];
    related_hashes: string[];
    passive_dns: {
      domain: string;
      ip: string;
      first_seen: string;
      last_seen: string;
    }[];
    ssl_certificates: {
      sha256: string;
      issuer: string;
      subject: string;
      not_before: string;
      not_after: string;
    }[];
  };
}
```

---

## 🎨 Visualización en UI

### Dashboard de Enriquecimiento

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🔍 Threat Enrichment Dashboard                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  [🔴 Critical: 12] [🟠 High: 34] [🟡 Medium: 89] [🟢 Low: 156]      │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ Últimos IOCs Enriquecidos                                    │    │
│  ├──────────────┬────────┬───────┬──────────────────────────────┤   │
│  │ IOC          │ Type   │ Risk  │ Fuentes                      │   │
│  ├──────────────┼────────┼───────┼──────────────────────────────┤   │
│  │ 45.33.32.156 │ IP     │ 🔴 92 │ OTX ✓ AIPDB ✓ VT ✓ GN ✓     │   │
│  │ evil.com     │ Domain │ 🟠 78 │ URLhaus ✓ Pulsedive ✓        │   │
│  │ abc123...    │ Hash   │ 🟠 65 │ VT ✓ MalwareBazaar ✓         │   │
│  └──────────────┴────────┴───────┴──────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────┐  ┌─────────────────────────────────┐   │
│  │ 🌍 Mapa de Geolocalización │  │ 📊 Distribución por Tipo       │   │
│  │ [Mapa interactivo con    │  │ IP: ████████░░ 45%              │   │
│  │  puntos de IOCs maliciosos│  │ Domain: ████░░░░ 25%           │   │
│  │  por país]               │  │ Hash: ███░░░░░ 18%              │   │
│  └─────────────────────────┘  │ URL: ██░░░░░░ 12%                │   │
│                               └─────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 🎯 MITRE ATT&CK Coverage                                     │    │
│  │ [Matriz ATT&CK con técnicas detectadas resaltadas]          │    │
│  │                                                              │    │
│  │ TA0001 Initial Access    ████░░ 4 técnicas                   │    │
│  │ TA0002 Execution         ██████ 6 técnicas                   │    │
│  │ TA0003 Persistence       ███░░░ 3 técnicas                   │    │
│  │ TA0011 C&C               ████████ 8 técnicas                 │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 🦠 Top Malware Families                                      │    │
│  │                                                              │    │
│  │ 1. Cobalt Strike    ████████████ 23 IOCs                     │    │
│  │ 2. Emotet           ████████░░░░ 15 IOCs                     │    │
│  │ 3. TrickBot         ██████░░░░░░ 11 IOCs                     │    │
│  │ 4. QakBot           ████░░░░░░░░ 8 IOCs                      │    │
│  │ 5. IcedID           ███░░░░░░░░░ 6 IOCs                      │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 👤 Threat Actors Identificados                               │    │
│  │                                                              │    │
│  │ [APT29] [Lazarus Group] [FIN7] [Wizard Spider] [TA505]       │    │
│  │                                                              │    │
│  │ Click para ver IOCs asociados a cada actor →                 │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Vista Detallada de IOC

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🔍 IP: 45.33.32.156                                    Risk: 🔴 92  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  📍 GEOLOCALIZACIÓN           🌐 RED                                │
│  ├─ País: Russia 🇷🇺           ├─ ASN: AS16276                      │
│  ├─ Ciudad: Moscow            ├─ Org: OVH SAS                       │
│  ├─ Coord: 55.75, 37.61       ├─ ISP: OVH Hosting                   │
│  └─ TZ: Europe/Moscow         ├─ VPN: ❌  Proxy: ✓  Tor: ❌         │
│                               └─ Datacenter: ✓                      │
│                                                                     │
│  ⚠️ REPUTACIÓN                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ AbuseIPDB      Confidence: 89%  │ Reports: 234  │ Last: 2h  │   │
│  │                Categories: SSH Brute Force, Port Scan        │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │ GreyNoise      Classification: MALICIOUS                     │   │
│  │                Actor: Unknown Scanner  │ Noise: Yes          │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │ VirusTotal     Malicious: 12/89  │ Community: -45            │   │
│  │                Last scan: 2026-02-15 14:32:00                │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │ Pulsedive      Risk: Critical                                │   │
│  │                Factors: [C2 Server] [Known Malicious]        │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  🦠 MALWARE ASOCIADO                                                 │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ • Cobalt Strike Beacon (8 reports)                           │   │
│  │ • Emotet Loader (3 reports)                                  │   │
│  │ • Generic.Trojan (2 reports)                                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  🎯 MITRE ATT&CK TTPs                                                │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ T1059.001 - PowerShell                                       │   │
│  │ T1071.001 - Web Protocols                                    │   │
│  │ T1105 - Ingress Tool Transfer                                │   │
│  │ T1573.002 - Asymmetric Cryptography                          │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  📡 SERVICIOS DETECTADOS (Shodan)                                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Port 22/tcp   SSH        OpenSSH 8.2p1      CVE-2023-51385   │   │
│  │ Port 80/tcp   HTTP       nginx/1.18.0       -                │   │
│  │ Port 443/tcp  HTTPS      nginx/1.18.0       -                │   │
│  │ Port 8443/tcp HTTPS      Cobalt Strike C2   🚨 MALWARE       │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  📰 PULSES DE INTELIGENCIA                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ 🔴 "Cobalt Strike C2 Infrastructure - Feb 2026"              │   │
│  │    Author: ThreatHunter42  │  TLP: Amber  │  Feb 14, 2026    │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │ 🟠 "Russian APT Infrastructure Tracking"                     │   │
│  │    Author: CrowdStrike     │  TLP: Green  │  Feb 10, 2026    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  🔗 RELACIONES                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Dominios resolviendo a esta IP:                              │   │
│  │   • update-service.xyz (first: 2026-02-01)                   │   │
│  │   • cdn-static.net (first: 2026-01-28)                       │   │
│  │                                                              │   │
│  │ Certificados SSL:                                            │   │
│  │   • CN=*.update-service.xyz (SHA: a1b2c3...)                 │   │
│  │                                                              │   │
│  │ IOCs relacionados:                                           │   │
│  │   • Hash: e3b0c44298fc1c149afbf4c8996fb924                   │   │
│  │   • URL: http://update-service.xyz/beacon.exe                │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  📊 METADATOS DE ENRIQUECIMIENTO                                     │
│  ├─ Enriquecido: 2026-02-16 10:45:32 UTC                            │
│  ├─ Fuentes consultadas: 8/8 ✓                                      │
│  ├─ Tiempo de procesamiento: 2.3s                                   │
│  └─ Cache: Miss (datos frescos)                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujo de Enriquecimiento

```
┌─────────────┐     ┌─────────────────────────────────────────────────┐
│   Frontend  │────▶│  POST /api/enrichment/threats                   │
│   Button    │     │  { indicators: [...], sources: [...] }          │
└─────────────┘     └─────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EnrichmentService.enrich_threats()               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Crear Job (UUID) y tracking                                     │
│  2. Para cada IOC:                                                  │
│     ┌─────────────────────────────────────────────────────────┐     │
│     │  Parallel Enrichment (asyncio.gather)                   │     │
│     │  ┌──────────────────────────────────────────────────┐   │     │
│     │  │ AbuseIPDB   │ GreyNoise  │ OTX      │ VirusTotal │   │     │
│     │  │ Pulsedive   │ ThreatFox  │ URLhaus  │ Shodan     │   │     │
│     │  │ IPinfo      │ Censys     │ MITRE    │ Maltiverse │   │     │
│     │  └──────────────────────────────────────────────────┘   │     │
│     └─────────────────────────────────────────────────────────┘     │
│  3. Agregar resultados y calcular risk_score                        │
│  4. Actualizar progreso (polling desde frontend)                    │
│  5. Guardar en OpenSearch index: "threat-indicators-enriched"       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    OpenSearch Storage                               │
├─────────────────────────────────────────────────────────────────────┤
│  Index: threat-indicators-enriched                                  │
│  Mappings: Optimized for threat intel queries                       │
│  Retention: 90 days (configurable)                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📈 Algoritmo de Risk Score

```python
def calculate_risk_score(enrichment_data: dict) -> int:
    """
    Calcula un risk score agregado de 0-100 basado en múltiples fuentes.

    Pesos de cada fuente (suma = 100):
    - AbuseIPDB confidence: 20%
    - VirusTotal detections: 25%
    - GreyNoise classification: 15%
    - Pulsedive risk: 15%
    - ThreatFox presence: 10%
    - OTX pulses count: 10%
    - Shodan vulnerabilities: 5%
    """
    score = 0
    confidence = 0

    # AbuseIPDB (0-100) → contribuye 20 puntos max
    if abuseipdb := enrichment_data.get("reputation", {}).get("abuseipdb"):
        score += abuseipdb["confidence_score"] * 0.20
        confidence += 20

    # VirusTotal detections
    if vt := enrichment_data.get("reputation", {}).get("virustotal"):
        total = vt["malicious_count"] + vt["suspicious_count"]
        total_scanners = total + vt["harmless_count"] + vt["undetected_count"]
        if total_scanners > 0:
            detection_rate = (total / total_scanners) * 100
            score += min(detection_rate * 0.25, 25)
            confidence += 25

    # GreyNoise classification
    if gn := enrichment_data.get("reputation", {}).get("greynoise"):
        if gn["classification"] == "malicious":
            score += 15
        elif gn["classification"] == "unknown" and gn["noise"]:
            score += 8
        confidence += 15

    # Pulsedive risk level
    if pd := enrichment_data.get("reputation", {}).get("pulsedive"):
        risk_map = {"critical": 15, "high": 12, "medium": 8, "low": 3, "unknown": 0}
        score += risk_map.get(pd["risk"], 0)
        confidence += 15

    # ThreatFox presence (binary: presente o no)
    if enrichment_data.get("threat_intel", {}).get("malware_families"):
        score += 10
        confidence += 10

    # OTX pulses (logarithmic scale)
    if feeds := enrichment_data.get("intel_feeds"):
        pulse_count = len([f for f in feeds if f["source"] == "AlienVault OTX"])
        score += min(pulse_count * 2, 10)
        confidence += 10

    # Shodan/Censys CVEs
    if services := enrichment_data.get("services"):
        cve_count = sum(len(s.get("cves", [])) for s in services)
        score += min(cve_count, 5)
        confidence += 5

    # Normalizar al rango 0-100
    if confidence > 0:
        return int(min((score / confidence) * 100, 100))
    return 0
```

---

## 🛡️ Características que Impresionarán

### 1. **Cobertura Completa**

- 18 fuentes de inteligencia
- Soporte para 6 tipos de IOCs
- Datos en tiempo real + cache inteligente

### 2. **Correlación MITRE ATT&CK**

- Mapeo automático de IOCs a TTPs
- Visualización de matriz ATT&CK
- Tracking de actores de amenazas

### 3. **Análisis de Relaciones**

- Passive DNS
- Certificados SSL
- IOCs relacionados
- Infraestructura de C&C

### 4. **Risk Scoring Inteligente**

- Algoritmo multi-fuente ponderado
- Confidence score basado en fuentes disponibles
- Histórico de scores

### 5. **Visualización Profesional**

- Mapa geográfico de amenazas
- Matriz ATT&CK interactiva
- Timeline de actividad
- Grafos de relaciones

### 6. **Graceful Degradation**

- Circuit breakers por fuente
- Fallback a datos sintéticos
- Nunca falla completamente

---

## 🚀 Siguientes Pasos

1. **Implementar `enrich_threats()` en EnrichmentService**
2. **Crear clientes para las 18 fuentes**
3. **Crear índice OpenSearch para IOCs enriquecidos**
4. **Crear página de visualización ThreatEnrichmentPage**
5. **Agregar tests E2E para verificar funcionalidad**

---

## 🗺️ Diseño Visual Avanzado: Mapa Mundi de Amenazas

### Concepto Visual

Un **mapa mundi interactivo** que muestra en tiempo real de dónde vienen las amenazas y hacia dónde atacan. Las líneas animadas conectan países origen con el SOC/target, creando un efecto visual tipo "war room" de Hollywood.

### Especificación del Mapa de Amenazas

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 🌍 GLOBAL THREAT MAP - Live Attack Visualization                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│                        🔴 Active Threats: 47                                    │
│                        ⚡ Attacks/min: 234                                      │
│                        🌐 Countries: 18                                         │
│                                                                                 │
│     ┌───────────────────────────────────────────────────────────────────┐       │
│     │                                                                   │       │
│     │     🔴                                                            │       │
│     │    Russia ════════════════╗                                      │       │
│     │     ╔═══════════════════════════════════════╗                     │       │
│     │     ║ 🟠                   ║                 ║                     │       │
│     │    China ═══════════════════════════════════╬═══════▶ 🎯          │       │
│     │                          ║                  ║        YOUR SOC     │       │
│     │    🟡                     ║                  ║       (Madrid)      │       │
│     │   N.Korea ═══════════════╝                  ║                     │       │
│     │                                             ║                     │       │
│     │    🟠                                        ║                     │       │
│     │   Iran ════════════════════════════════════╝                     │       │
│     │                                                                   │       │
│     │                   🟡 Brazil                                       │       │
│     │                    ╚════════════════════════════════▶ 🎯         │       │
│     │                                                                   │       │
│     └───────────────────────────────────────────────────────────────────┘       │
│                                                                                 │
│  LEYENDA:                                                                       │
│  🔴 Critical (80-100)  🟠 High (60-79)  🟡 Medium (40-59)  🟢 Low (0-39)       │
│  ════▶ Línea animada con partículas moviéndose hacia el target                 │
│  ⚫ Pulso en origen indicando actividad reciente                               │
│                                                                                 │
│  [🔍 Zoom]  [🌐 Vista 3D]  [📊 Stats]  [⏸️ Pause]  [📥 Export]                │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Elementos Visuales del Mapa

#### 1. **Marcadores de País Origen**

```
Diseño: Círculo pulsante con tamaño proporcional a número de amenazas

Estados:
- 🔴 Pulsando rápido (1Hz) → Ataque activo ahora
- 🟠 Pulsando lento (0.5Hz) → Amenaza reciente (<1h)
- 🟡 Estático → Amenaza histórica
- 🟢 Ausente → Sin amenazas

Tamaño:
- Radio = log(num_threats) * 5px
- Mínimo: 8px, Máximo: 40px

Tooltip al hover:
┌─────────────────────────────┐
│ 🇷🇺 Russia                  │
│ ─────────────────────────── │
│ Active Threats: 23          │
│ Risk Score: 87 (Critical)   │
│ Top Malware: Cobalt Strike  │
│ Top Actor: APT29            │
│ [Click para detalles →]     │
└─────────────────────────────┘
```

#### 2. **Líneas de Ataque Animadas**

```
Diseño: Curvas Bézier con gradiente y partículas móviles

Propiedades:
- Grosor: Proporcional a severidad (1-5px)
- Color: Gradiente del color de riesgo al blanco
- Opacidad: 0.6 base, 1.0 al hover
- Curvatura: Arco hacia arriba proporcional a distancia

Animación:
- Partículas (círculos 3px) viajando por la curva
- Velocidad: 100-300ms por partícula
- Density: 1 partícula cada 50px
- Trail: Efecto estela degradado

Algoritmo de curva:
  controlPoint.y = midpoint.y - (distance * 0.3)
  // Curva más alta para distancias largas

CSS Animation:
@keyframes threat-particle {
  0% { offset-distance: 0%; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { offset-distance: 100%; opacity: 0; }
}
```

#### 3. **Marker del SOC (Target)**

```
Diseño: Escudo o torre de defensa con ondas radar

Visualización:
   ╭─────╮
   │ 🎯  │ ← Centro: Logo empresa o icono SOC
   ╰─────╯
     ╱│╲   ← Ondas concéntricas expandiéndose
    ╱ │ ╲     (radar scan effect)
   ╱  │  ╲

Animación ondas:
- 3 círculos concéntricos expandiéndose
- Cada uno con delay de 0.3s
- Duración: 2s loop infinito
- Opacidad: 1 → 0 mientras se expande
```

### Interacciones del Mapa

#### Click en País

```
Acción: Abre panel lateral con detalles del país

┌─ Threats from Russia ──────────────────────┐
│                                            │
│ 📊 Summary                                 │
│ ├─ Total IOCs: 45                         │
│ ├─ Critical: 12 | High: 18 | Medium: 15   │
│ └─ First seen: 2026-02-10                 │
│                                            │
│ 🦠 Top Malware                             │
│ ├─ Cobalt Strike (23)                     │
│ ├─ Agent Tesla (12)                       │
│ └─ TrickBot (10)                          │
│                                            │
│ 👤 Threat Actors                           │
│ ├─ APT29 (Cozy Bear)                      │
│ ├─ APT28 (Fancy Bear)                     │
│ └─ Turla                                  │
│                                            │
│ 📋 IOC List                                │
│ ┌────────────────────────────────────┐    │
│ │ IP          │ Risk │ Malware      │    │
│ ├────────────────────────────────────┤    │
│ │ 45.33.32.1  │ 🔴92 │ Cobalt Strike│    │
│ │ 185.234.1.2 │ 🟠78 │ Agent Tesla  │    │
│ │ ...más...                          │    │
│ └────────────────────────────────────┘    │
│                                            │
│ [Ver todos los IOCs de Russia →]          │
│                                            │
└────────────────────────────────────────────┘
```

#### Click en Línea de Ataque

```
Acción: Muestra detalles del vector de ataque específico

Popup sobre la línea:
┌───────────────────────────────────────┐
│ 🔗 Attack Vector: Russia → Your SOC  │
├───────────────────────────────────────┤
│ First attack: 2026-02-14 08:23 UTC   │
│ Last attack: 2026-02-16 11:45 UTC    │
│ Total IOCs: 23                       │
│ Unique IPs: 8                        │
│ Primary TTP: T1071 (Web Protocols)   │
│                                       │
│ [Block All] [Investigate] [Details]  │
└───────────────────────────────────────┘
```

#### Zoom y Pan

```
Controles:
- Scroll: Zoom in/out (1x - 10x)
- Drag: Pan del mapa
- Double-click: Zoom in centrado
- Pinch (touch): Zoom táctil

Niveles de zoom:
1x: Vista mundial completa
2x: Vista continental
5x: Vista regional
10x: Vista de país (muestra ciudades)
```

---

## 📄 Sistema de Páginas Anidadas

### Arquitectura de Navegación

```
/threats                          ← Dashboard principal
  │
  ├── /threats/map                ← Mapa mundi interactivo (pantalla completa)
  │
  ├── /threats/iocs               ← Lista de todos los IOCs
  │     │
  │     └── /threats/iocs/:id     ← Detalle completo de IOC específico
  │           │
  │           ├── /threats/iocs/:id/reputation    ← Tab: Reputación
  │           ├── /threats/iocs/:id/network       ← Tab: Info de red
  │           ├── /threats/iocs/:id/mitre         ← Tab: MITRE ATT&CK
  │           ├── /threats/iocs/:id/relationships ← Tab: Relaciones
  │           └── /threats/iocs/:id/timeline      ← Tab: Timeline
  │
  ├── /threats/actors             ← Lista de threat actors
  │     └── /threats/actors/:name ← Detalle de actor (ej: APT29)
  │
  ├── /threats/malware            ← Lista de familias de malware
  │     └── /threats/malware/:family ← Detalle de familia (ej: Cobalt Strike)
  │
  ├── /threats/mitre              ← Matriz MITRE ATT&CK completa
  │     └── /threats/mitre/:technique ← Detalle de técnica (ej: T1059.001)
  │
  ├── /threats/feeds              ← Intel feeds suscritos
  │     └── /threats/feeds/:id    ← IOCs de un feed específico
  │
  └── /threats/search             ← Búsqueda avanzada de IOCs
```

### Página: Detalle de IOC (`/threats/iocs/:id`)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ ← Back to IOC List                                                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 🔴 45.33.32.156                                         Risk Score: 92 │    │
│  │ IP Address • Russia 🇷🇺 • ASN16276 (OVH SAS)                           │    │
│  │                                                                         │    │
│  │ First Seen: 2026-02-10 14:23 UTC    Last Seen: 2026-02-16 11:45 UTC   │    │
│  │ Enriched: 2 minutes ago             Sources: 8/8 successful            │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                 │
│  ┌─────┬──────────┬─────────┬───────────────┬──────────────┬──────────┐         │
│  │ 📊  │ ⚠️        │ 🌐       │ 🎯             │ 🔗            │ 📅       │         │
│  │Over-│Reputation│ Network │ MITRE ATT&CK  │Relationships │Timeline │         │
│  │view │          │         │               │              │         │         │
│  └─────┴──────────┴─────────┴───────────────┴──────────────┴──────────┘         │
│                                                                                 │
│  ═══════════════════════════════════════════════════════════════════════════   │
│                                                                                 │
│  TAB: Overview                                                                  │
│  ─────────────────────────────────────────────────────────────────────────────  │
│                                                                                 │
│  ┌─ Quick Stats ─────────────────┐  ┌─ Risk Breakdown ──────────────────────┐  │
│  │                               │  │                                       │  │
│  │  🔴 Risk: CRITICAL (92)       │  │  AbuseIPDB ████████████░░ 89%        │  │
│  │  ✓ Confidence: 87%            │  │  VirusTotal ███████████░░░ 78%       │  │
│  │  📡 Sources: 8                │  │  GreyNoise ████████████░░ 85%        │  │
│  │  🦠 Malware: 3 families       │  │  Pulsedive ██████████████ 95%        │  │
│  │  👤 Actors: APT29, Turla      │  │  ThreatFox █████████░░░░░ 65%        │  │
│  │  🎯 TTPs: 7 techniques        │  │                                       │  │
│  │                               │  │  Overall ████████████░░ 92           │  │
│  └───────────────────────────────┘  └───────────────────────────────────────┘  │
│                                                                                 │
│  ┌─ Geolocation ─────────────────┐  ┌─ Network Info ────────────────────────┐  │
│  │  📍 Moscow, Russia            │  │  ASN: 16276 (OVH SAS)                │  │
│  │  Lat: 55.7558, Lon: 37.6173   │  │  ISP: OVH Hosting                    │  │
│  │  Timezone: Europe/Moscow      │  │  Company: OVH                        │  │
│  │                               │  │                                       │  │
│  │  ┌─────────────────────────┐  │  │  Flags:                              │  │
│  │  │ [Mini map con pin]      │  │  │  ✓ Datacenter  ✓ Proxy  ✗ Tor       │  │
│  │  │                         │  │  │  ✗ VPN  ✗ Mobile                     │  │
│  │  └─────────────────────────┘  │  │                                       │  │
│  └───────────────────────────────┘  └───────────────────────────────────────┘  │
│                                                                                 │
│  ┌─ Associated Malware ──────────────────────────────────────────────────────┐ │
│  │                                                                           │ │
│  │  ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐       │ │
│  │  │ 🦠 Cobalt Strike  │ │ 🦠 Agent Tesla    │ │ 🦠 Emotet         │       │ │
│  │  │ APT Tool          │ │ Infostealer       │ │ Banking Trojan    │       │ │
│  │  │ 8 detections      │ │ 3 detections      │ │ 2 detections      │       │ │
│  │  │ [View Details →]  │ │ [View Details →]  │ │ [View Details →]  │       │ │
│  │  └───────────────────┘ └───────────────────┘ └───────────────────┘       │ │
│  │                                                                           │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌─ Actions ─────────────────────────────────────────────────────────────────┐ │
│  │                                                                           │ │
│  │  [🚫 Block IP]  [🔍 Investigate]  [📋 Copy IOC]  [📥 Export Report]       │ │
│  │  [🔄 Re-enrich]  [➕ Add to Watchlist]  [🏷️ Add Tags]                     │ │
│  │                                                                           │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Tab: MITRE ATT&CK (`/threats/iocs/:id/mitre`)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  TAB: MITRE ATT&CK                                                              │
│  ─────────────────────────────────────────────────────────────────────────────  │
│                                                                                 │
│  Techniques associated with this IOC:                                           │
│                                                                                 │
│  ┌─ Execution ─────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │   │
│  │  │ T1059.001 - PowerShell                                           │  │   │
│  │  │ ─────────────────────────────────────────────────────────────────│  │   │
│  │  │ Adversaries may abuse PowerShell commands and scripts for        │  │   │
│  │  │ execution. PowerShell is a powerful interactive command-line...  │  │   │
│  │  │                                                                   │  │   │
│  │  │ Evidence from this IOC:                                          │  │   │
│  │  │ • OTX Pulse: "Cobalt Strike C2 using PowerShell stagers"         │  │   │
│  │  │ • ThreatFox: Associated with PowerShell-based dropper            │  │   │
│  │  │                                                                   │  │   │
│  │  │ Data Sources: Command, Script, Process, Module                   │  │   │
│  │  │ Platforms: Windows                                               │  │   │
│  │  │                                                                   │  │   │
│  │  │ [View on MITRE →]  [Related IOCs (23)]                           │  │   │
│  │  └──────────────────────────────────────────────────────────────────┘  │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─ Command and Control ───────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │   │
│  │  │ T1071.001 - Web Protocols                                        │  │   │
│  │  │ Adversaries may communicate using web protocols to avoid...      │  │   │
│  │  └──────────────────────────────────────────────────────────────────┘  │   │
│  │                                                                         │   │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │   │
│  │  │ T1573.002 - Asymmetric Cryptography                              │  │   │
│  │  │ Adversaries may employ asymmetric encryption to conceal...       │  │   │
│  │  └──────────────────────────────────────────────────────────────────┘  │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─ ATT&CK Matrix Visualization ───────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │  [Mini matriz ATT&CK con las técnicas de este IOC resaltadas]          │   │
│  │                                                                         │   │
│  │  IA │ EX │ PE │ PR │ DE │ CR │ DI │ LA │ CO │ EX │ IM                  │   │
│  │  ─────────────────────────────────────────────────────────────         │   │
│  │   ░ │ ██ │  ░ │  ░ │ ██ │  ░ │  ░ │  ░ │ ██ │  ░ │  ░                  │   │
│  │   ░ │  ░ │  ░ │  ░ │  ░ │  ░ │  ░ │  ░ │ ██ │  ░ │  ░                  │   │
│  │                                                                         │   │
│  │  ██ = Técnica detectada en este IOC                                    │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Tab: Relationships (`/threats/iocs/:id/relationships`)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  TAB: Relationships                                                             │
│  ─────────────────────────────────────────────────────────────────────────────  │
│                                                                                 │
│  ┌─ Graph View ─────────────────────────────────────────────────────────────┐  │
│  │                                                                          │  │
│  │                      ┌─────────────┐                                     │  │
│  │                      │ 🌐 Domain   │                                     │  │
│  │                  ┌───│update.xyz   │───┐                                 │  │
│  │                  │   └─────────────┘   │                                 │  │
│  │                  │                     │                                 │  │
│  │    ┌─────────────┴─┐               ┌───┴─────────────┐                  │  │
│  │    │ 📄 Certificate│               │ 🔴 IP (THIS)    │                  │  │
│  │    │ *.update.xyz  │               │ 45.33.32.156    │                  │  │
│  │    └───────────────┘               └───────┬─────────┘                  │  │
│  │                                            │                             │  │
│  │                        ┌───────────────────┼───────────────────┐        │  │
│  │                        │                   │                   │        │  │
│  │              ┌─────────┴───┐     ┌─────────┴───┐     ┌─────────┴───┐   │  │
│  │              │ 📁 Hash     │     │ 🔗 URL      │     │ 🟠 IP       │   │  │
│  │              │ e3b0c44...  │     │ /beacon.exe │     │ 45.33.32.2  │   │  │
│  │              └─────────────┘     └─────────────┘     └─────────────┘   │  │
│  │                                                                          │  │
│  │  [🔍 Expand] [📊 Table View] [📥 Export Graph]                          │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│  ┌─ Related IOCs ───────────────────────────────────────────────────────────┐  │
│  │                                                                          │  │
│  │  Type     │ Value                           │ Relation        │ Risk    │  │
│  │  ─────────┼─────────────────────────────────┼─────────────────┼─────────│  │
│  │  Domain   │ update-service.xyz              │ Resolves to     │ 🔴 88   │  │
│  │  Domain   │ cdn-static.net                  │ Resolves to     │ 🟠 72   │  │
│  │  Hash     │ e3b0c44298fc1c149afbf4c8996fb92│ Hosted          │ 🔴 95   │  │
│  │  URL      │ http://update-service.xyz/mal  │ Hosted          │ 🔴 91   │  │
│  │  IP       │ 45.33.32.157                    │ Same subnet     │ 🟠 67   │  │
│  │  Cert     │ CN=*.update-service.xyz         │ SSL Certificate │ -       │  │
│  │                                                                          │  │
│  │  [View all 23 related IOCs →]                                           │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│  ┌─ Passive DNS History ────────────────────────────────────────────────────┐  │
│  │                                                                          │  │
│  │  Domain                  │ First Seen         │ Last Seen          │    │  │
│  │  ────────────────────────┼────────────────────┼────────────────────│    │  │
│  │  update-service.xyz      │ 2026-02-01 08:00   │ 2026-02-16 10:00   │    │  │
│  │  cdn-static.net          │ 2026-01-28 14:23   │ 2026-02-15 22:00   │    │  │
│  │  api.malware-cdn.ru      │ 2026-01-15 03:12   │ 2026-01-20 18:45   │    │  │
│  │                                                                          │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Tab: Timeline (`/threats/iocs/:id/timeline`)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  TAB: Timeline                                                                  │
│  ─────────────────────────────────────────────────────────────────────────────  │
│                                                                                 │
│  Activity timeline for 45.33.32.156                                            │
│                                                                                 │
│  Feb 2026                                                                       │
│  ──────────────────────────────────────────────────────────────────────────    │
│                                                                                 │
│  16 │ 11:45 ●──── Last seen attacking your network                             │
│     │ 10:30 ●──── Re-enriched: Risk score increased 85→92                      │
│     │ 08:23 ●──── New OTX pulse: "APT29 February Campaign"                     │
│  ───│──────────────────────────────────────────────────────────────────────    │
│  15 │ 22:10 ●──── VirusTotal: 3 new AV detections                              │
│     │ 14:00 ●──── AbuseIPDB: 45 new abuse reports                              │
│     │ 09:15 ●──── First detected attacking your network                        │
│  ───│──────────────────────────────────────────────────────────────────────    │
│  14 │ 18:30 ●──── ThreatFox: Added to "Cobalt Strike C2" feed                  │
│     │ 12:00 ●──── GreyNoise: Classification changed to MALICIOUS               │
│  ───│──────────────────────────────────────────────────────────────────────    │
│  10 │ 08:00 ●──── First seen in AlienVault OTX                                 │
│  ───│──────────────────────────────────────────────────────────────────────    │
│  01 │ 14:23 ●──── First observed globally (Shodan scan)                        │
│                                                                                 │
│  ┌─ Risk Score Evolution ───────────────────────────────────────────────────┐  │
│  │                                                                          │  │
│  │  100 ┤                                               ╭────── 92          │  │
│  │   80 ┤                              ╭────────────────╯                   │  │
│  │   60 ┤              ╭───────────────╯                                    │  │
│  │   40 ┤     ╭────────╯                                                    │  │
│  │   20 ┤─────╯                                                             │  │
│  │    0 ┼──────┬──────┬──────┬──────┬──────┬──────┬──────                  │  │
│  │      Feb 1  Feb 5  Feb 10 Feb 12 Feb 14 Feb 15 Feb 16                   │  │
│  │                                                                          │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎮 Comandos y Acciones de la UI

### Barra de Comandos (Command Palette)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ Press Ctrl+K or click here to open command palette...                          │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│ 🔍 Type a command or search...                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  QUICK ACTIONS                                                                  │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  ⌨️ enrich <ip|domain|hash>    Enrich a single IOC                              │
│  ⌨️ bulk-enrich                 Open bulk enrichment dialog                     │
│  ⌨️ search <query>              Search IOCs by any field                        │
│  ⌨️ block <ip|domain>           Add to blocklist (requires confirmation)        │
│                                                                                 │
│  VIEWS                                                                          │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  ⌨️ goto map                    Open threat map fullscreen                      │
│  ⌨️ goto iocs                   Open IOC list                                   │
│  ⌨️ goto mitre                  Open MITRE ATT&CK matrix                        │
│  ⌨️ goto actors                 Open threat actors list                         │
│                                                                                 │
│  FILTERS                                                                        │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  ⌨️ filter country:<code>       Filter by country (e.g., RU, CN, IR)            │
│  ⌨️ filter risk:critical        Show only critical IOCs                         │
│  ⌨️ filter malware:<name>       Filter by malware family                        │
│  ⌨️ filter actor:<name>         Filter by threat actor                          │
│  ⌨️ filter last24h              Show IOCs from last 24 hours                    │
│                                                                                 │
│  EXPORTS                                                                        │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  ⌨️ export csv                  Export current view as CSV                      │
│  ⌨️ export stix                 Export as STIX 2.1 bundle                       │
│  ⌨️ export misp                 Export as MISP event                            │
│  ⌨️ export pdf                  Generate PDF report                             │
│                                                                                 │
│  INTEGRATIONS                                                                   │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  ⌨️ push-to-firewall            Push blocklist to firewall                      │
│  ⌨️ create-ticket               Create investigation ticket                     │
│  ⌨️ notify-team                 Send alert to SOC team                          │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Keyboard Shortcuts

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  KEYBOARD SHORTCUTS                                                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Navigation                          Actions                                    │
│  ──────────────────────────────────  ──────────────────────────────────────    │
│  Ctrl + K    Command palette         E          Enrich selected                 │
│  Ctrl + /    Quick search            B          Block selected                  │
│  G then M    Go to Map               I          Investigate selected            │
│  G then L    Go to IOC List          C          Copy IOC value                  │
│  G then A    Go to MITRE ATT&CK      R          Refresh/Re-enrich               │
│  Esc         Close panel/modal       Delete     Remove from list                │
│                                                                                 │
│  Map Controls                        Filters                                    │
│  ──────────────────────────────────  ──────────────────────────────────────    │
│  + / -       Zoom in/out             1          Critical only                   │
│  Arrow keys  Pan map                 2          High and above                  │
│  Space       Pause animations        3          Medium and above                │
│  F           Toggle fullscreen       0          Clear filters                   │
│  3           Toggle 3D view          T          Toggle time filter              │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Efectos Visuales Adicionales

### 1. **Real-time Pulse Effect**

```
Cuando llega un nuevo IOC crítico:

1. Flash rojo en el header (0.5s)
2. Nuevo marcador en el mapa aparece con animación "drop"
3. Línea de ataque se dibuja progresivamente (1s)
4. Badge contador se incrementa con bounce
5. Notificación toast aparece en esquina

CSS:
@keyframes new-threat-flash {
  0%, 100% { background: var(--bg); }
  50% { background: rgba(239, 68, 68, 0.3); }
}

@keyframes marker-drop {
  0% { transform: translateY(-50px) scale(0); opacity: 0; }
  60% { transform: translateY(10px) scale(1.2); }
  100% { transform: translateY(0) scale(1); opacity: 1; }
}
```

### 2. **Heatmap Overlay**

```
Toggle para mostrar densidad de amenazas por región:

┌─────────────────────────────────────────────────────────┐
│                                                         │
│                 ████████                                │
│              ██████████████     ← Zona caliente (RU)    │
│           █████████████████                             │
│              ████████████                               │
│                                                         │
│                              ████                       │
│                           ████████  ← Zona media (CN)   │
│                              ████                       │
│                                                         │
└─────────────────────────────────────────────────────────┘

Colores:
- 🟣 Muy alta densidad (>50 IOCs)
- 🔴 Alta densidad (20-50 IOCs)
- 🟠 Media densidad (10-20 IOCs)
- 🟡 Baja densidad (1-10 IOCs)
```

### 3. **Connection Strength Indicator**

```
Las líneas de ataque muestran "grosor" variable:

───────────────  1-5 IOCs (thin)
═══════════════  6-20 IOCs (medium)
████████████████ 21+ IOCs (thick, glowing)

Efecto glow para ataques masivos:
box-shadow: 0 0 10px rgba(239, 68, 68, 0.8);
```

### 4. **3D Globe View (Opcional)**

```
Vista alternativa con globo 3D rotatorio:

      ╭───────────────╮
    ╭─┤   🌍 Globe    ├─╮
   ╱  ╰───────────────╯  ╲
  ╱   ╭─────────────╮     ╲
 │   ╱   ●  ●        ╲     │
 │  │   ● ● ●  ●      │    │  ← Amenazas como puntos 3D
 │   ╲      ●   ●    ╱     │     que orbitan el globo
  ╲   ╰─────────────╯     ╱
   ╲                     ╱
    ╰─────────────────────╯

Interacciones:
- Drag: Rotar globo
- Scroll: Zoom
- Click en punto: Detalle de amenaza
- Auto-rotate cuando idle
```

---

## 📱 Responsive Design

### Mobile View (< 768px)

```
┌─────────────────────┐
│ 🔍 Threats    ≡    │
├─────────────────────┤
│                     │
│ [Stats row]         │
│ 🔴12 🟠34 🟡89 🟢156│
│                     │
├─────────────────────┤
│                     │
│ ┌─────────────────┐ │
│ │                 │ │
│ │  [Mini Map]     │ │
│ │                 │ │
│ └─────────────────┘ │
│                     │
│ [Toggle: Map/List]  │
│                     │
├─────────────────────┤
│ IOC List (scrollable)
│ ┌─────────────────┐ │
│ │45.33.32.156 🔴92│ │
│ │Russia • C.Strike│ │
│ └─────────────────┘ │
│ ┌─────────────────┐ │
│ │evil.com    🟠78 │ │
│ │China • TrickBot│ │
│ └─────────────────┘ │
│ ...                 │
│                     │
└─────────────────────┘
```

---

## 🔧 Tecnologías Sugeridas para Implementación

### Mapa y Visualizaciones

| Componente          | Opciones                           | Recomendación                          |
| ------------------- | ---------------------------------- | -------------------------------------- |
| **Mapa 2D**         | Leaflet, Mapbox, react-simple-maps | `react-simple-maps` (ligero, SVG puro) |
| **Mapa 3D**         | Three.js + globe.gl, Cesium        | `globe.gl` (WebGL, fácil de usar)      |
| **Líneas animadas** | SVG + CSS animations               | CSS `stroke-dashoffset` animation      |
| **Grafos**          | D3.js, vis.js, react-force-graph   | `react-force-graph` (3D y 2D)          |
| **Charts**          | Recharts, Chart.js, Nivo           | `Recharts` (ya usado en proyecto)      |

### Performance

| Técnica                   | Uso                              |
| ------------------------- | -------------------------------- |
| **Virtual scrolling**     | Lista de IOCs (>1000 items)      |
| **Web Workers**           | Cálculos de paths, aggregations  |
| **RequestAnimationFrame** | Animaciones suaves del mapa      |
| **Canvas fallback**       | Si SVG es lento con muchos paths |

---

## 🚀 Resumen: Qué hace esto impresionante

1. **Visualización "War Room"** - Mapa con ataques en tiempo real como en películas de hackers
2. **Datos de 18+ fuentes** - Cobertura completa de inteligencia de amenazas
3. **MITRE ATT&CK integrado** - Mapeo profesional de TTPs
4. **Páginas de detalle profundo** - Click en cualquier cosa para ver más
5. **Líneas animadas** - Partículas viajando de origen a destino
6. **Command palette** - Acciones rápidas tipo Slack/VSCode
7. **Exportación STIX/MISP** - Integración con estándares de la industria
8. **Responsive** - Funciona en móvil para SOC on-the-go

---

**Autor:** Claude
**Revisión:** Pendiente de aprobación
**Clasificación:** TLP:GREEN
