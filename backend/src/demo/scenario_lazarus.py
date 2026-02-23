"""Scenario 5: Lazarus Group Destructive Attack.

Trigger: Detection of data wiping activity across multiple systems.
Expected behavior:
1. Detect initial compromise via spear-phishing
2. Identify lateral movement using stolen credentials
3. Detect deployment of wiper malware
4. Mass containment of affected systems
5. Executive notification - nation-state actor attribution
6. Forensic evidence collection

MITRE ATT&CK Mapping (Lazarus Group - G0032):
- Initial Access: T1566.001 (Spear-Phishing Attachment)
- Execution: T1059.001 (PowerShell), T1059.003 (Windows Command Shell)
- Persistence: T1547.001 (Registry Run Keys)
- Defense Evasion: T1027 (Obfuscated Files), T1070.004 (File Deletion)
- Credential Access: T1003.001 (LSASS Memory)
- Lateral Movement: T1021.001 (Remote Desktop Protocol)
- Impact: T1485 (Data Destruction), T1561.001 (Disk Content Wipe)

Task: T-1.3.004
Requirement: REQ-002-001-003 - Escenario Lazarus Group - Ataque destructivo
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any
import uuid


# =============================================================================
# Scenario Constants
# =============================================================================

SCENARIO_ID = "INC-LAZARUS-005"
SCENARIO_NAME = "Lazarus Group Destructive Attack"
THREAT_ACTOR = "Lazarus Group (APT38 / HIDDEN COBRA)"
WIPER_HASH = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"
WIPER_FAMILY = "DUSTMAN Wiper"


# =============================================================================
# MITRE ATT&CK Mapping
# =============================================================================

MITRE_TACTICS = {
    "TA0001": "Initial Access",
    "TA0002": "Execution",
    "TA0003": "Persistence",
    "TA0004": "Privilege Escalation",
    "TA0005": "Defense Evasion",
    "TA0006": "Credential Access",
    "TA0007": "Discovery",
    "TA0008": "Lateral Movement",
    "TA0040": "Impact",
}

LAZARUS_TECHNIQUES = {
    "T1566.001": {"name": "Spear-Phishing Attachment", "tactic": "TA0001"},
    "T1059.001": {"name": "PowerShell", "tactic": "TA0002"},
    "T1059.003": {"name": "Windows Command Shell", "tactic": "TA0002"},
    "T1547.001": {"name": "Registry Run Keys", "tactic": "TA0003"},
    "T1027": {"name": "Obfuscated Files or Information", "tactic": "TA0005"},
    "T1070.004": {"name": "File Deletion", "tactic": "TA0005"},
    "T1003.001": {"name": "LSASS Memory", "tactic": "TA0006"},
    "T1082": {"name": "System Information Discovery", "tactic": "TA0007"},
    "T1021.001": {"name": "Remote Desktop Protocol", "tactic": "TA0008"},
    "T1485": {"name": "Data Destruction", "tactic": "TA0040"},
    "T1561.001": {"name": "Disk Content Wipe", "tactic": "TA0040"},
    "T1561.002": {"name": "Disk Structure Wipe", "tactic": "TA0040"},
}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class LazarusHost:
    """Host affected by Lazarus wiper attack."""
    asset_id: str
    hostname: str
    department: str
    wipe_status: str  # pending, in_progress, wiped
    wipe_progress: float  # 0-100%
    first_seen: datetime
    status: str = "compromised"  # compromised, contained, recovered


@dataclass
class LazarusScenarioData:
    """Complete Lazarus Group attack scenario data."""
    incident_id: str
    threat_actor: str
    attack_type: str  # destructive, wiper, data_destruction
    initial_vector: str
    wiper_family: str
    wiper_hash: str
    affected_hosts: list[LazarusHost]
    lateral_movement_technique: str
    target_sector: str
    estimated_impact: str
    timeline_events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def affected_count(self) -> int:
        return len(self.affected_hosts)

    @property
    def wiped_count(self) -> int:
        return sum(1 for h in self.affected_hosts if h.wipe_status == "wiped")


# =============================================================================
# Scenario Data Generator
# =============================================================================

def generate_lazarus_scenario() -> LazarusScenarioData:
    """Generate synthetic Lazarus Group attack scenario data."""
    base_time = datetime.now(timezone.utc) - timedelta(hours=4)

    # Create affected hosts (nation-state attack hits critical systems)
    affected_hosts = [
        LazarusHost(
            asset_id="SRV-DB-PROD-01",
            hostname="srv-db-prod-01.corp.local",
            department="IT Infrastructure",
            wipe_status="wiped",
            wipe_progress=100.0,
            first_seen=base_time + timedelta(hours=3, minutes=30),
            status="compromised",
        ),
        LazarusHost(
            asset_id="SRV-BACKUP-01",
            hostname="srv-backup-01.corp.local",
            department="IT Infrastructure",
            wipe_status="wiped",
            wipe_progress=100.0,
            first_seen=base_time + timedelta(hours=3, minutes=32),
            status="compromised",
        ),
        LazarusHost(
            asset_id="WS-EXEC-001",
            hostname="ws-exec-001.corp.local",
            department="Executive",
            wipe_status="in_progress",
            wipe_progress=67.3,
            first_seen=base_time + timedelta(hours=3, minutes=35),
            status="compromised",
        ),
        LazarusHost(
            asset_id="SRV-FILE-01",
            hostname="srv-file-01.corp.local",
            department="IT Infrastructure",
            wipe_status="in_progress",
            wipe_progress=45.8,
            first_seen=base_time + timedelta(hours=3, minutes=38),
            status="compromised",
        ),
        LazarusHost(
            asset_id="WS-FINANCE-042",
            hostname="ws-finance-042.corp.local",
            department="Finance",
            wipe_status="pending",
            wipe_progress=0.0,
            first_seen=base_time + timedelta(hours=3, minutes=40),
            status="compromised",
        ),
        LazarusHost(
            asset_id="SRV-SCADA-01",
            hostname="srv-scada-01.ot.corp.local",
            department="Operations Technology",
            wipe_status="pending",
            wipe_progress=0.0,
            first_seen=base_time + timedelta(hours=3, minutes=42),
            status="compromised",
        ),
    ]

    # Create timeline events with MITRE ATT&CK mapping
    timeline_events = [
        {
            "timestamp": base_time.isoformat(),
            "event": "initial_access",
            "details": "Spear-phishing email with malicious Word document received",
            "host": "ws-finance-042.corp.local",
            "mitre_tactic": "TA0001",
            "tactic_id": "TA0001",
            "tactic_name": "Initial Access",
            "mitre_technique": "T1566.001",
            "technique_id": "T1566.001",
            "technique_name": "Spear-Phishing Attachment",
        },
        {
            "timestamp": (base_time + timedelta(minutes=2)).isoformat(),
            "event": "execution",
            "details": "Macro executed, PowerShell payload downloaded",
            "host": "ws-finance-042.corp.local",
            "mitre_tactic": "TA0002",
            "tactic_id": "TA0002",
            "tactic_name": "Execution",
            "mitre_technique": "T1059.001",
            "technique_id": "T1059.001",
            "technique_name": "PowerShell",
        },
        {
            "timestamp": (base_time + timedelta(minutes=5)).isoformat(),
            "event": "persistence",
            "details": "Registry run key created for persistence",
            "host": "ws-finance-042.corp.local",
            "mitre_tactic": "TA0003",
            "tactic_id": "TA0003",
            "tactic_name": "Persistence",
            "mitre_technique": "T1547.001",
            "technique_id": "T1547.001",
            "technique_name": "Registry Run Keys",
        },
        {
            "timestamp": (base_time + timedelta(hours=1)).isoformat(),
            "event": "credential_access",
            "details": "Mimikatz detected - LSASS memory dump",
            "host": "ws-finance-042.corp.local",
            "mitre_tactic": "TA0006",
            "tactic_id": "TA0006",
            "tactic_name": "Credential Access",
            "mitre_technique": "T1003.001",
            "technique_id": "T1003.001",
            "technique_name": "LSASS Memory",
        },
        {
            "timestamp": (base_time + timedelta(hours=2)).isoformat(),
            "event": "discovery",
            "details": "Network enumeration and system information gathering",
            "host": "ws-finance-042.corp.local",
            "mitre_tactic": "TA0007",
            "tactic_id": "TA0007",
            "tactic_name": "Discovery",
            "mitre_technique": "T1082",
            "technique_id": "T1082",
            "technique_name": "System Information Discovery",
        },
        {
            "timestamp": (base_time + timedelta(hours=2, minutes=30)).isoformat(),
            "event": "lateral_movement",
            "details": "RDP connection to database server using stolen credentials",
            "host": "srv-db-prod-01.corp.local",
            "source_host": "ws-finance-042.corp.local",
            "mitre_tactic": "TA0008",
            "tactic_id": "TA0008",
            "tactic_name": "Lateral Movement",
            "mitre_technique": "T1021.001",
            "technique_id": "T1021.001",
            "technique_name": "Remote Desktop Protocol",
        },
        {
            "timestamp": (base_time + timedelta(hours=3)).isoformat(),
            "event": "defense_evasion",
            "details": "Obfuscated wiper malware deployed",
            "host": "srv-db-prod-01.corp.local",
            "mitre_tactic": "TA0005",
            "tactic_id": "TA0005",
            "tactic_name": "Defense Evasion",
            "mitre_technique": "T1027",
            "technique_id": "T1027",
            "technique_name": "Obfuscated Files or Information",
        },
        {
            "timestamp": (base_time + timedelta(hours=3, minutes=30)).isoformat(),
            "event": "impact_data_destruction",
            "details": "Data destruction initiated - MBR and critical files being wiped",
            "host": "srv-db-prod-01.corp.local",
            "mitre_tactic": "TA0040",
            "tactic_id": "TA0040",
            "tactic_name": "Impact",
            "mitre_technique": "T1485",
            "technique_id": "T1485",
            "technique_name": "Data Destruction",
        },
        {
            "timestamp": (base_time + timedelta(hours=3, minutes=31)).isoformat(),
            "event": "impact_disk_wipe",
            "details": "Disk content wipe detected on backup server",
            "host": "srv-backup-01.corp.local",
            "mitre_tactic": "TA0040",
            "tactic_id": "TA0040",
            "tactic_name": "Impact",
            "mitre_technique": "T1561.001",
            "technique_id": "T1561.001",
            "technique_name": "Disk Content Wipe",
        },
        {
            "timestamp": (base_time + timedelta(hours=3, minutes=45)).isoformat(),
            "event": "threat_intel_match",
            "details": f"Hash identified as {WIPER_FAMILY} - attributed to {THREAT_ACTOR}",
            "mitre_tactic": None,
            "tactic_id": None,
            "mitre_technique": None,
            "technique_id": None,
        },
        {
            "timestamp": (base_time + timedelta(hours=3, minutes=50)).isoformat(),
            "event": "executive_notification",
            "details": "Nation-state attribution - escalating to executive leadership and legal",
            "mitre_tactic": None,
            "tactic_id": None,
            "mitre_technique": None,
            "technique_id": None,
        },
    ]

    return LazarusScenarioData(
        incident_id=SCENARIO_ID,
        threat_actor=THREAT_ACTOR,
        attack_type="destructive",
        initial_vector="spear_phishing",
        wiper_family=WIPER_FAMILY,
        wiper_hash=WIPER_HASH,
        affected_hosts=affected_hosts,
        lateral_movement_technique="T1021.001 - Remote Desktop Protocol",
        target_sector="Critical Infrastructure / Energy",
        estimated_impact="Catastrophic - Complete data loss on critical systems",
        timeline_events=timeline_events,
    )


# =============================================================================
# OpenSearch Index Data
# =============================================================================

def generate_incident_document() -> dict[str, Any]:
    """Generate SIEM incident document for OpenSearch."""
    return {
        "incident_id": SCENARIO_ID,
        "title": f"APT Attack - {THREAT_ACTOR} - Destructive Wiper Deployed",
        "severity": "Critical",
        "status": "open",
        "device_id": "SRV-DB-PROD-01",  # First wiped host
        "hash_sha256": WIPER_HASH,
        "process_name": "dustman.exe",
        "cmdline": "dustman.exe --wipe-all --overwrite=3",
        "mitre_technique": "T1485",  # Data Destruction
        "technique_id": "T1485",
        "tactic_id": "TA0040",
        "threat_actor": THREAT_ACTOR,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tags": ["apt", "nation-state", "destructive", "wiper", "lazarus", "critical-incident"],
        "affected_host_count": 6,
        "attribution_confidence": "high",
    }


def generate_asset_documents() -> list[dict[str, Any]]:
    """Generate asset documents for all affected hosts."""
    scenario = generate_lazarus_scenario()
    assets = []

    for host in scenario.affected_hosts:
        # Determine criticality based on type
        if "SCADA" in host.asset_id or "DB-PROD" in host.asset_id:
            criticality = "critical"
            tags = ["critical-infrastructure", "production"]
        elif "BACKUP" in host.asset_id:
            criticality = "critical"
            tags = ["backup", "dr-critical"]
        elif "EXEC" in host.asset_id:
            criticality = "high"
            tags = ["vip", "executive"]
        else:
            criticality = "standard"
            tags = ["standard"]

        assets.append({
            "asset_id": host.asset_id,
            "hostname": host.hostname,
            "device_type": "server" if "SRV" in host.asset_id else "workstation",
            "tags": tags,
            "owner": f"{host.department} Team",
            "department": host.department,
            "criticality": criticality,
            "wipe_status": host.wipe_status,
        })

    return assets


def generate_intel_document() -> dict[str, Any]:
    """Generate threat intel document for wiper hash."""
    return {
        "hash": WIPER_HASH,
        "verdict": "malicious",
        "vt_score": 71,
        "vt_total": 72,
        "malware_labels": ["wiper", "destructive", "apt", "lazarus", "nation-state"],
        "confidence": 98,
        "first_seen": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
        "threat_actor": THREAT_ACTOR,
        "campaign": "Operation Sharpshooter",
        "ttp_references": ["T1485", "T1561.001", "T1561.002", "T1059.001", "T1003.001"],
        "geo_targets": ["US", "UK", "KR", "JP"],
        "ioc_type": "file_hash",
    }


def generate_edr_documents() -> list[dict[str, Any]]:
    """Generate EDR detection documents for all affected hosts."""
    scenario = generate_lazarus_scenario()
    detections = []

    for host in scenario.affected_hosts:
        # Primary detection - wiper
        detections.append({
            "detection_id": f"DET-{uuid.uuid4().hex[:8].upper()}",
            "asset_id": host.asset_id,
            "hostname": host.hostname,
            "file": {
                "sha256": WIPER_HASH,
                "name": "dustman.exe",
                "path": "C:\\Windows\\Temp\\dustman.exe",
            },
            "process": {
                "name": "dustman.exe",
                "cmdline": "dustman.exe --wipe-all --overwrite=3",
                "parent": "cmd.exe",
            },
            "severity": "Critical",
            "mitre_technique": "T1485",
            "technique_id": "T1485",
            "tactic_id": "TA0040",
            "timestamp": host.first_seen.isoformat(),
            "wipe_status": host.wipe_status,
            "wipe_progress": host.wipe_progress,
            "threat_actor": THREAT_ACTOR,
        })

    return detections


def generate_propagation_document() -> dict[str, Any]:
    """Generate wiper propagation document."""
    scenario = generate_lazarus_scenario()
    return {
        "hash": WIPER_HASH,
        "affected_hosts": [h.asset_id for h in scenario.affected_hosts],
        "affected_count": scenario.affected_count,
        "wiped_count": scenario.wiped_count,
        "first_seen": scenario.affected_hosts[0].first_seen.isoformat(),
        "last_seen": scenario.affected_hosts[-1].first_seen.isoformat(),
        "spread_rate": "coordinated",  # All at once - not worm-like
        "attack_type": "destructive",
    }


# =============================================================================
# Playbook Actions
# =============================================================================

def get_response_playbook() -> dict[str, Any]:
    """Get the destructive attack response playbook for this scenario."""
    return {
        "playbook_id": "PB-DESTRUCT-001",
        "name": "Nation-State Destructive Attack Response",
        "steps": [
            {
                "step": 1,
                "action": "network_isolation",
                "description": "Immediately disconnect all affected segments from network",
                "automated": True,
                "priority": "critical",
            },
            {
                "step": 2,
                "action": "mass_containment",
                "description": "Contain all systems with wiper indicators",
                "automated": True,
                "priority": "critical",
            },
            {
                "step": 3,
                "action": "power_preservation",
                "description": "Keep affected systems powered on for forensic evidence",
                "automated": False,
                "priority": "critical",
            },
            {
                "step": 4,
                "action": "executive_notification",
                "description": "Notify C-suite, Legal, and Board - potential nation-state attack",
                "automated": True,
                "priority": "critical",
            },
            {
                "step": 5,
                "action": "forensic_collection",
                "description": "Collect forensic images from all affected systems",
                "automated": False,
                "priority": "high",
            },
            {
                "step": 6,
                "action": "memory_acquisition",
                "description": "Capture volatile memory before any reboot",
                "automated": False,
                "priority": "high",
            },
            {
                "step": 7,
                "action": "backup_verification",
                "description": "Verify backup integrity - ensure not compromised",
                "automated": False,
                "priority": "high",
            },
            {
                "step": 8,
                "action": "threat_intel_sharing",
                "description": "Share IOCs with ISAC and government agencies",
                "automated": False,
                "priority": "medium",
            },
            {
                "step": 9,
                "action": "law_enforcement_contact",
                "description": "Contact FBI Cyber Division for nation-state attribution",
                "automated": False,
                "priority": "medium",
            },
            {
                "step": 10,
                "action": "recovery_planning",
                "description": "Develop clean recovery plan from known-good backups",
                "automated": False,
                "priority": "medium",
            },
        ],
        "estimated_duration_minutes": 480,  # 8 hours minimum for nation-state incident
        "requires_executive_approval": True,
        "requires_legal_review": True,
        "external_notifications": ["FBI", "CISA", "Industry ISAC"],
    }
