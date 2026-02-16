"""
Threat Enrichment MCP Tools.

Tools for enriching threat indicators (IOCs) with threat intelligence,
querying enriched threats, and getting map visualization data.

These tools enable AI agents to:
- Enrich IOCs with multi-source threat intel
- Query and filter enriched threat data
- Get geolocation data for threat map visualization
"""

from typing import Any, Dict, List

# Tool definitions for MCP registration
THREAT_ENRICHMENT_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "enrichment_threats",
        "description": "Enrich IOCs (IPs, domains, URLs, hashes) with threat intelligence from multiple sources. Returns enriched indicators with risk scores, geo data, reputation, and MITRE ATT&CK mapping.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "indicators": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["ip", "domain", "url", "hash", "email"],
                                "description": "Type of indicator"
                            },
                            "value": {
                                "type": "string",
                                "description": "The indicator value (IP address, domain name, etc.)"
                            }
                        },
                        "required": ["type", "value"]
                    },
                    "description": "List of indicators to enrich (max 100)"
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Sources to use for enrichment (otx, abuseipdb, greynoise, virustotal, synthetic)"
                },
                "force_refresh": {
                    "type": "boolean",
                    "description": "Bypass cache and fetch fresh data",
                    "default": False
                }
            },
            "required": ["indicators"]
        }
    },
    {
        "name": "threats_query",
        "description": "Query enriched threat indicators with filters. Returns matching threats with their enrichment data.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "risk_level": {
                    "type": "string",
                    "enum": ["critical", "high", "medium", "low"],
                    "description": "Filter by risk level"
                },
                "indicator_type": {
                    "type": "string",
                    "enum": ["ip", "domain", "url", "hash", "email"],
                    "description": "Filter by indicator type"
                },
                "country": {
                    "type": "string",
                    "description": "Filter by country code (e.g., 'RU', 'CN')"
                },
                "malware_family": {
                    "type": "string",
                    "description": "Filter by malware family name"
                },
                "threat_actor": {
                    "type": "string",
                    "description": "Filter by threat actor name"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 50,
                    "maximum": 100
                },
                "offset": {
                    "type": "integer",
                    "description": "Offset for pagination",
                    "default": 0
                }
            }
        }
    },
    {
        "name": "threats_map",
        "description": "Get threat map visualization data with country markers and attack lines for the threat world map.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time_range": {
                    "type": "string",
                    "enum": ["1h", "24h", "7d", "30d"],
                    "description": "Time range for threat data",
                    "default": "24h"
                },
                "risk_level_min": {
                    "type": "string",
                    "enum": ["critical", "high", "medium", "low"],
                    "description": "Minimum risk level to include",
                    "default": "low"
                }
            }
        }
    }
]


async def handle_enrichment_threats(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle enrichment_threats tool call.

    Enriches indicators using the EnrichmentService.
    """
    from ...services.enrichment_service import EnrichmentService

    indicators = args.get("indicators", [])
    sources = args.get("sources")
    force_refresh = args.get("force_refresh", False)

    # Validate indicators
    if not isinstance(indicators, list):
        raise ValueError("indicators must be a list")

    for indicator in indicators:
        if not isinstance(indicator, dict):
            raise ValueError("Each indicator must be an object with 'type' and 'value'")
        if "type" not in indicator:
            raise ValueError("Each indicator must have a 'type' field")
        if "value" not in indicator:
            raise ValueError("Each indicator must have a 'value' field")

    # Call the enrichment service
    service = EnrichmentService()
    result = await service.enrich_threats(
        indicators=indicators,
        sources=sources,
        force_refresh=force_refresh
    )

    return result


async def handle_threats_query(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle threats_query tool call.

    Queries enriched threats with optional filters.
    Returns synthetic demo data since we don't have a persistent store.
    """
    import random
    import hashlib
    from datetime import datetime

    risk_level = args.get("risk_level")
    indicator_type = args.get("indicator_type")
    country = args.get("country")
    malware_family = args.get("malware_family")
    threat_actor = args.get("threat_actor")
    limit = min(args.get("limit", 50), 100)
    offset = args.get("offset", 0)

    # Generate synthetic threats for demo
    threats = _generate_synthetic_threats(limit + offset)

    # Apply filters
    filtered = threats
    if risk_level:
        filtered = [t for t in filtered if t["risk_level"] == risk_level]
    if indicator_type:
        filtered = [t for t in filtered if t["type"] == indicator_type]
    if country:
        filtered = [t for t in filtered if t.get("geo", {}).get("country") == country]
    if malware_family:
        filtered = [t for t in filtered if malware_family.lower() in
                   [m.lower() for m in t.get("threat_intel", {}).get("malware_families", [])]]
    if threat_actor:
        filtered = [t for t in filtered if threat_actor.lower() in
                   [a.lower() for a in t.get("threat_intel", {}).get("threat_actors", [])]]

    # Apply pagination
    paginated = filtered[offset:offset + limit]

    return {
        "threats": paginated,
        "total_count": len(filtered),
        "limit": limit,
        "offset": offset,
        "filters_applied": {
            "risk_level": risk_level,
            "indicator_type": indicator_type,
            "country": country,
            "malware_family": malware_family,
            "threat_actor": threat_actor
        }
    }


async def handle_threats_map(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle threats_map tool call.

    Returns map visualization data with country markers and attack lines.
    """
    import random
    from datetime import datetime

    time_range = args.get("time_range", "24h")
    risk_level_min = args.get("risk_level_min", "low")

    # Risk level ordering for filtering
    risk_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    min_risk_value = risk_order.get(risk_level_min, 0)

    # Country data with coordinates
    countries_data = [
        {"code": "RU", "name": "Russia", "lat": 55.75, "lon": 37.61, "threat_count": 156, "risk_level": "critical"},
        {"code": "CN", "name": "China", "lat": 39.90, "lon": 116.40, "threat_count": 142, "risk_level": "critical"},
        {"code": "KP", "name": "North Korea", "lat": 39.03, "lon": 125.75, "threat_count": 67, "risk_level": "high"},
        {"code": "IR", "name": "Iran", "lat": 35.69, "lon": 51.39, "threat_count": 89, "risk_level": "high"},
        {"code": "US", "name": "United States", "lat": 38.89, "lon": -77.03, "threat_count": 45, "risk_level": "medium"},
        {"code": "NL", "name": "Netherlands", "lat": 52.37, "lon": 4.89, "threat_count": 78, "risk_level": "medium"},
        {"code": "DE", "name": "Germany", "lat": 52.52, "lon": 13.40, "threat_count": 34, "risk_level": "low"},
        {"code": "BR", "name": "Brazil", "lat": -15.79, "lon": -47.88, "threat_count": 56, "risk_level": "medium"},
        {"code": "IN", "name": "India", "lat": 28.61, "lon": 77.21, "threat_count": 38, "risk_level": "medium"},
        {"code": "UA", "name": "Ukraine", "lat": 50.45, "lon": 30.52, "threat_count": 23, "risk_level": "low"},
    ]

    # SOC location (target)
    soc_location = {
        "lat": 40.42,  # Madrid
        "lon": -3.70,
        "name": "SOC HQ"
    }

    # Filter countries by minimum risk level
    filtered_countries = [
        c for c in countries_data
        if risk_order.get(c["risk_level"], 0) >= min_risk_value
    ]

    # Generate attack lines from each country to SOC
    attack_lines = []
    for country in filtered_countries:
        attack_lines.append({
            "source": {
                "lat": country["lat"],
                "lon": country["lon"],
                "country": country["code"],
                "country_name": country["name"]
            },
            "target": soc_location,
            "threat_count": country["threat_count"],
            "risk_level": country["risk_level"],
            "active": random.random() > 0.3  # 70% chance of active attack
        })

    return {
        "countries": filtered_countries,
        "attack_lines": attack_lines,
        "soc_location": soc_location,
        "time_range": time_range,
        "total_threats": sum(c["threat_count"] for c in filtered_countries),
        "generated_at": datetime.now().isoformat()
    }


def _generate_synthetic_threats(count: int) -> List[Dict[str, Any]]:
    """Generate synthetic threat data for demo purposes."""
    import random
    import hashlib
    from datetime import datetime, timedelta

    malware_families = [
        "Cobalt Strike", "Emotet", "TrickBot", "QakBot", "IcedID",
        "Dridex", "Ryuk", "Conti", "LockBit", "REvil"
    ]

    threat_actors = [
        "APT29", "APT28", "Lazarus Group", "FIN7", "Wizard Spider",
        "TA505", "Sandworm", "Turla", "Kimsuky", "MuddyWater"
    ]

    countries = [
        {"code": "RU", "name": "Russia", "lat": 55.75, "lon": 37.61},
        {"code": "CN", "name": "China", "lat": 39.90, "lon": 116.40},
        {"code": "KP", "name": "North Korea", "lat": 39.03, "lon": 125.75},
        {"code": "IR", "name": "Iran", "lat": 35.69, "lon": 51.39},
        {"code": "US", "name": "United States", "lat": 38.89, "lon": -77.03},
    ]

    risk_levels = ["critical", "high", "medium", "low"]
    indicator_types = ["ip", "domain", "hash", "url"]

    threats = []
    for i in range(count):
        random.seed(i)  # Deterministic for same results

        indicator_type = random.choice(indicator_types)
        country = random.choice(countries)
        risk_level = random.choice(risk_levels)

        # Generate value based on type
        if indicator_type == "ip":
            value = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        elif indicator_type == "domain":
            domains = ["malware-c2.ru", "evil-download.cn", "phish-attack.ir", "botnet-control.kp"]
            value = f"sub{i}.{random.choice(domains)}"
        elif indicator_type == "hash":
            value = hashlib.sha256(f"malware-{i}".encode()).hexdigest()
        else:  # url
            value = f"http://evil{i}.com/malware/download.exe"

        threat = {
            "id": f"threat-{i:05d}",
            "type": indicator_type,
            "value": value,
            "risk_score": random.randint(30, 100),
            "risk_level": risk_level,
            "first_seen": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            "last_seen": datetime.now().isoformat(),
            "geo": {
                "country": country["code"],
                "country_name": country["name"],
                "latitude": country["lat"],
                "longitude": country["lon"]
            },
            "threat_intel": {
                "malware_families": random.sample(malware_families, k=random.randint(1, 3)),
                "threat_actors": random.sample(threat_actors, k=random.randint(0, 2)),
                "tags": ["malicious", "active"]
            }
        }
        threats.append(threat)

    return threats


# Handler mapping for MCP registration
threat_enrichment_handlers = {
    "enrichment_threats": handle_enrichment_threats,
    "threats_query": handle_threats_query,
    "threats_map": handle_threats_map,
}
