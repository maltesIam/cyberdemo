"""Scenario 6: Supply Chain Attack - Compromised Legitimate Software.

Trigger: Compromised legitimate software with anomalous behavior.
Expected behavior:
1. Detect anomalous behavior in known app
2. Verify hash vs vendor's published hash
3. Supply chain alert to security team
4. Organizational hunting for affected systems
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any
import uuid


# =============================================================================
# Scenario Constants
# =============================================================================

SCENARIO_ID = "INC-ANCHOR-006"
SCENARIO_NAME = "Supply Chain Attack - Compromised Software"
LEGITIMATE_SOFTWARE = "UpdateHelper.exe"
VENDOR_NAME = "TrustedVendor Inc."
COMPROMISED_HASH = "f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6"
LEGITIMATE_HASH = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class SoftwareVersion:
    """Software version information."""
    version: str
    hash_sha256: str
    release_date: datetime
    is_compromised: bool
    vendor_verified: bool


@dataclass
class AnomalousBehavior:
    """Anomalous behavior detected from compromised software."""
    behavior_id: str
    timestamp: datetime
    behavior_type: str
    description: str
    ioc_type: str
    ioc_value: str
    mitre_technique: str


@dataclass
class AffectedAsset:
    """Asset affected by supply chain attack."""
    asset_id: str
    hostname: str
    department: str
    software_version: str
    install_date: datetime
    last_execution: datetime
    network_traffic_suspicious: bool


@dataclass
class SupplyChainScenarioData:
    """Complete supply chain attack scenario data."""
    incident_id: str
    software_name: str
    vendor_name: str
    compromised_version: str
    legitimate_version: str
    compromised_hash: str
    legitimate_hash: str
    affected_assets: list[AffectedAsset]
    anomalous_behaviors: list[AnomalousBehavior]
    c2_domains: list[str]
    c2_ips: list[str]
    backdoor_capabilities: list[str]
    supply_chain_vector: str
    first_compromise_date: datetime
    vendor_contacted: bool
    cve_assigned: str | None
    timeline_events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def affected_count(self) -> int:
        return len(self.affected_assets)


# =============================================================================
# Scenario Data Generator
# =============================================================================

def generate_supply_chain_scenario() -> SupplyChainScenarioData:
    """Generate synthetic supply chain attack scenario data."""
    base_time = datetime.now(timezone.utc) - timedelta(hours=3)

    # Affected assets across organization
    affected_assets = [
        AffectedAsset(
            asset_id="WS-DEV-001",
            hostname="ws-dev-001.corp.local",
            department="Engineering",
            software_version="2.4.1",
            install_date=base_time - timedelta(days=14),
            last_execution=base_time - timedelta(hours=1),
            network_traffic_suspicious=True,
        ),
        AffectedAsset(
            asset_id="WS-DEV-015",
            hostname="ws-dev-015.corp.local",
            department="Engineering",
            software_version="2.4.1",
            install_date=base_time - timedelta(days=12),
            last_execution=base_time - timedelta(hours=2),
            network_traffic_suspicious=True,
        ),
        AffectedAsset(
            asset_id="WS-QA-003",
            hostname="ws-qa-003.corp.local",
            department="QA",
            software_version="2.4.1",
            install_date=base_time - timedelta(days=10),
            last_execution=base_time - timedelta(hours=4),
            network_traffic_suspicious=False,
        ),
        AffectedAsset(
            asset_id="SRV-BUILD-01",
            hostname="srv-build-01.corp.local",
            department="DevOps",
            software_version="2.4.1",
            install_date=base_time - timedelta(days=14),
            last_execution=base_time - timedelta(minutes=30),
            network_traffic_suspicious=True,
        ),
        AffectedAsset(
            asset_id="WS-DEV-022",
            hostname="ws-dev-022.corp.local",
            department="Engineering",
            software_version="2.4.1",
            install_date=base_time - timedelta(days=8),
            last_execution=base_time - timedelta(hours=3),
            network_traffic_suspicious=True,
        ),
    ]

    # Anomalous behaviors detected
    anomalous_behaviors = [
        AnomalousBehavior(
            behavior_id=f"BEH-{uuid.uuid4().hex[:8].upper()}",
            timestamp=base_time,
            behavior_type="network_beacon",
            description="Periodic beacon to unknown external domain",
            ioc_type="domain",
            ioc_value="update-cdn.malicious-actor.com",
            mitre_technique="T1071.001",
        ),
        AnomalousBehavior(
            behavior_id=f"BEH-{uuid.uuid4().hex[:8].upper()}",
            timestamp=base_time + timedelta(minutes=5),
            behavior_type="process_injection",
            description="Injected code into legitimate browser process",
            ioc_type="technique",
            ioc_value="CreateRemoteThread",
            mitre_technique="T1055.001",
        ),
        AnomalousBehavior(
            behavior_id=f"BEH-{uuid.uuid4().hex[:8].upper()}",
            timestamp=base_time + timedelta(minutes=10),
            behavior_type="credential_access",
            description="Attempted to read credential storage",
            ioc_type="file_path",
            ioc_value=r"C:\Users\*\AppData\Local\Google\Chrome\User Data\Default\Login Data",
            mitre_technique="T1555.003",
        ),
        AnomalousBehavior(
            behavior_id=f"BEH-{uuid.uuid4().hex[:8].upper()}",
            timestamp=base_time + timedelta(minutes=15),
            behavior_type="persistence",
            description="Created scheduled task for persistence",
            ioc_type="scheduled_task",
            ioc_value="UpdateHelperMaintenance",
            mitre_technique="T1053.005",
        ),
        AnomalousBehavior(
            behavior_id=f"BEH-{uuid.uuid4().hex[:8].upper()}",
            timestamp=base_time + timedelta(minutes=20),
            behavior_type="data_staging",
            description="Compressed and staged files in temp directory",
            ioc_type="file_path",
            ioc_value=r"C:\Windows\Temp\upd_cache.zip",
            mitre_technique="T1074.001",
        ),
    ]

    # C2 infrastructure
    c2_domains = [
        "update-cdn.malicious-actor.com",
        "api.trusted-updates.net",
        "cdn.software-patch.org",
    ]

    c2_ips = [
        "185.234.72.15",
        "91.219.28.44",
        "45.88.67.123",
    ]

    # Backdoor capabilities
    backdoor_capabilities = [
        "remote_shell",
        "file_exfiltration",
        "credential_harvesting",
        "screenshot_capture",
        "keylogging",
        "process_enumeration",
        "lateral_movement_tools",
    ]

    # Timeline events
    timeline_events = [
        {
            "timestamp": base_time.isoformat(),
            "event": "behavioral_anomaly_detected",
            "details": f"Anomalous network behavior from {LEGITIMATE_SOFTWARE}",
        },
        {
            "timestamp": (base_time + timedelta(minutes=5)).isoformat(),
            "event": "hash_verification_failed",
            "details": f"Software hash does not match vendor's published hash",
        },
        {
            "timestamp": (base_time + timedelta(minutes=10)).isoformat(),
            "event": "supply_chain_alert",
            "details": "Supply chain compromise suspected",
        },
        {
            "timestamp": (base_time + timedelta(minutes=15)).isoformat(),
            "event": "organization_hunt_initiated",
            "details": f"Hunting for all instances of {LEGITIMATE_SOFTWARE} v2.4.1",
        },
        {
            "timestamp": (base_time + timedelta(minutes=20)).isoformat(),
            "event": "affected_assets_identified",
            "details": f"Found {len(affected_assets)} assets with compromised version",
        },
        {
            "timestamp": (base_time + timedelta(minutes=25)).isoformat(),
            "event": "vendor_notification",
            "details": f"Contacted {VENDOR_NAME} security team",
        },
        {
            "timestamp": (base_time + timedelta(minutes=30)).isoformat(),
            "event": "ioc_block_deployed",
            "details": "Blocked C2 domains and IPs across network",
        },
    ]

    return SupplyChainScenarioData(
        incident_id=SCENARIO_ID,
        software_name=LEGITIMATE_SOFTWARE,
        vendor_name=VENDOR_NAME,
        compromised_version="2.4.1",
        legitimate_version="2.4.0",
        compromised_hash=COMPROMISED_HASH,
        legitimate_hash=LEGITIMATE_HASH,
        affected_assets=affected_assets,
        anomalous_behaviors=anomalous_behaviors,
        c2_domains=c2_domains,
        c2_ips=c2_ips,
        backdoor_capabilities=backdoor_capabilities,
        supply_chain_vector="compromised_update_server",
        first_compromise_date=base_time - timedelta(days=14),
        vendor_contacted=True,
        cve_assigned="CVE-2025-XXXX",  # Pending assignment
        timeline_events=timeline_events,
    )


# =============================================================================
# OpenSearch Index Data
# =============================================================================

def generate_incident_document() -> dict[str, Any]:
    """Generate SIEM incident document for OpenSearch."""
    scenario = generate_supply_chain_scenario()
    return {
        "incident_id": SCENARIO_ID,
        "title": f"Supply Chain Attack - Compromised {LEGITIMATE_SOFTWARE}",
        "severity": "Critical",
        "status": "open",
        "device_id": "WS-DEV-001",  # Initial detection host
        "hash_sha256": COMPROMISED_HASH,
        "process_name": LEGITIMATE_SOFTWARE,
        "cmdline": f"{LEGITIMATE_SOFTWARE} --update-check --silent",
        "mitre_technique": "T1195.002",  # Supply Chain Compromise: Compromise Software Supply Chain
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tags": ["supply-chain", "backdoor", "apt", "critical-incident"],
        "vendor_name": VENDOR_NAME,
        "compromised_version": scenario.compromised_version,
        "affected_host_count": scenario.affected_count,
    }


def generate_asset_documents() -> list[dict[str, Any]]:
    """Generate asset documents for all affected hosts."""
    scenario = generate_supply_chain_scenario()
    assets = []

    for asset in scenario.affected_assets:
        # Determine tags based on type
        tags = ["standard"]
        if "SRV" in asset.asset_id:
            tags = ["server", "build-infrastructure"]
        elif "DEV" in asset.asset_id:
            tags = ["developer-workstation"]

        assets.append({
            "asset_id": asset.asset_id,
            "hostname": asset.hostname,
            "device_type": "server" if "SRV" in asset.asset_id else "workstation",
            "tags": tags,
            "owner": f"{asset.department} Team",
            "department": asset.department,
            "criticality": "critical" if "SRV" in asset.asset_id else "high",
            "installed_software": {
                "name": LEGITIMATE_SOFTWARE,
                "version": asset.software_version,
                "hash": COMPROMISED_HASH,
            },
        })

    return assets


def generate_intel_document() -> dict[str, Any]:
    """Generate threat intel document for compromised software hash."""
    return {
        "hash": COMPROMISED_HASH,
        "verdict": "malicious",
        "vt_score": 45,
        "vt_total": 75,
        "malware_labels": ["trojan", "backdoor", "supply-chain", "apt"],
        "confidence": 88,
        "first_seen": (datetime.now(timezone.utc) - timedelta(days=14)).isoformat(),
        "threat_actor": "UNC4523",  # Threat actor designation
        "campaign": "Operation UpdateStorm",
        "ttp_references": ["T1195.002", "T1071.001", "T1055.001", "T1555.003"],
        "legitimate_software_trojanized": True,
        "vendor_name": VENDOR_NAME,
    }


def generate_software_verification_document() -> dict[str, Any]:
    """Generate software verification document comparing hashes."""
    return {
        "software_name": LEGITIMATE_SOFTWARE,
        "vendor_name": VENDOR_NAME,
        "verification_status": "MISMATCH",
        "versions": [
            {
                "version": "2.4.0",
                "vendor_hash": LEGITIMATE_HASH,
                "observed_hash": LEGITIMATE_HASH,
                "match": True,
                "status": "verified",
            },
            {
                "version": "2.4.1",
                "vendor_hash": "e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3",
                "observed_hash": COMPROMISED_HASH,
                "match": False,
                "status": "compromised",
            },
        ],
        "vendor_advisory_url": "https://trustedvendor.com/security/advisory-2025-001",
        "vendor_contacted": True,
        "vendor_response_received": False,
    }


def generate_ioc_documents() -> list[dict[str, Any]]:
    """Generate IOC documents for the supply chain attack."""
    scenario = generate_supply_chain_scenario()
    iocs = []

    # Add C2 domains
    for domain in scenario.c2_domains:
        iocs.append({
            "ioc_id": f"IOC-{uuid.uuid4().hex[:8].upper()}",
            "type": "domain",
            "value": domain,
            "threat_type": "c2",
            "campaign": "Operation UpdateStorm",
            "confidence": 95,
            "first_seen": datetime.now(timezone.utc).isoformat(),
            "blocked": True,
        })

    # Add C2 IPs
    for ip in scenario.c2_ips:
        iocs.append({
            "ioc_id": f"IOC-{uuid.uuid4().hex[:8].upper()}",
            "type": "ip",
            "value": ip,
            "threat_type": "c2",
            "campaign": "Operation UpdateStorm",
            "confidence": 90,
            "first_seen": datetime.now(timezone.utc).isoformat(),
            "blocked": True,
        })

    # Add file hash
    iocs.append({
        "ioc_id": f"IOC-{uuid.uuid4().hex[:8].upper()}",
        "type": "sha256",
        "value": COMPROMISED_HASH,
        "threat_type": "trojanized_software",
        "campaign": "Operation UpdateStorm",
        "confidence": 100,
        "first_seen": datetime.now(timezone.utc).isoformat(),
        "blocked": True,
    })

    return iocs


# =============================================================================
# Response Actions
# =============================================================================

def get_response_playbook() -> dict[str, Any]:
    """Get the supply chain attack response playbook for this scenario."""
    return {
        "playbook_id": "PB-SUPPLYCHAIN-001",
        "name": "Supply Chain Compromise Response",
        "steps": [
            {
                "step": 1,
                "action": "hash_verification",
                "description": "Verify software hash against vendor's published hash",
                "automated": True,
                "priority": "critical",
            },
            {
                "step": 2,
                "action": "organizational_hunt",
                "description": "Hunt for all instances of compromised software version",
                "automated": True,
                "priority": "critical",
            },
            {
                "step": 3,
                "action": "network_block",
                "description": "Block C2 domains and IPs at network perimeter",
                "automated": True,
                "priority": "critical",
            },
            {
                "step": 4,
                "action": "hash_block",
                "description": "Block compromised hash across all EDR agents",
                "automated": True,
                "priority": "critical",
            },
            {
                "step": 5,
                "action": "affected_isolation",
                "description": "Isolate affected hosts for analysis",
                "automated": True,
                "priority": "high",
            },
            {
                "step": 6,
                "action": "vendor_notification",
                "description": "Contact vendor security team",
                "automated": False,
                "priority": "high",
            },
            {
                "step": 7,
                "action": "forensic_analysis",
                "description": "Perform forensic analysis on affected hosts",
                "automated": False,
                "priority": "high",
            },
            {
                "step": 8,
                "action": "credential_reset",
                "description": "Reset credentials on affected systems",
                "automated": False,
                "priority": "high",
            },
            {
                "step": 9,
                "action": "software_rollback",
                "description": "Rollback to known-good software version",
                "automated": False,
                "priority": "medium",
            },
            {
                "step": 10,
                "action": "threat_intelligence_share",
                "description": "Share IOCs with threat intelligence community",
                "automated": False,
                "priority": "medium",
            },
        ],
        "estimated_duration_minutes": 180,
        "requires_vendor_coordination": True,
    }


def get_hunt_query() -> dict[str, Any]:
    """Get the organizational hunt query for this scenario."""
    return {
        "query_type": "edr_hunt",
        "name": f"Hunt for {LEGITIMATE_SOFTWARE} v2.4.1",
        "description": "Find all hosts with compromised software version",
        "filters": [
            {
                "field": "file.sha256",
                "operator": "equals",
                "value": COMPROMISED_HASH,
            },
            {
                "field": "process.name",
                "operator": "equals",
                "value": LEGITIMATE_SOFTWARE,
            },
        ],
        "network_indicators": {
            "domains": ["update-cdn.malicious-actor.com", "api.trusted-updates.net"],
            "ips": ["185.234.72.15", "91.219.28.44"],
        },
        "behavioral_indicators": [
            "process_injection",
            "credential_access",
            "scheduled_task_creation",
            "data_staging",
        ],
    }
