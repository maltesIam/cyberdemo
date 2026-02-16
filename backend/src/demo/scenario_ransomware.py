"""Scenario 4: Ransomware Multi-Host Attack.

Trigger: Detection of mass encryption on 5+ hosts.
Expected behavior:
1. Detect first host
2. Hunt hash - find 5 hosts
3. Coordinated mass containment
4. Executive notification
5. Response playbook
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any
import uuid


# =============================================================================
# Scenario Constants
# =============================================================================

SCENARIO_ID = "INC-ANCHOR-004"
SCENARIO_NAME = "Ransomware Multi-Host Attack"
RANSOMWARE_HASH = "d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5"
RANSOMWARE_FAMILY = "LockBit 3.0"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class RansomwareHost:
    """Host affected by ransomware."""
    asset_id: str
    hostname: str
    department: str
    encrypted_files: int
    encryption_progress: float  # 0-100%
    first_seen: datetime
    status: str = "active"  # active, contained, recovered


@dataclass
class RansomwareScenarioData:
    """Complete ransomware scenario data."""
    incident_id: str
    ransomware_family: str
    ransom_note_text: str
    bitcoin_address: str
    ransom_amount_btc: float
    affected_hosts: list[RansomwareHost]
    initial_vector: str
    lateral_movement_technique: str
    encryption_extension: str
    kill_switch_domain: str | None
    timeline_events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def affected_count(self) -> int:
        return len(self.affected_hosts)

    @property
    def total_encrypted_files(self) -> int:
        return sum(h.encrypted_files for h in self.affected_hosts)


# =============================================================================
# Scenario Data Generator
# =============================================================================

def generate_ransomware_scenario() -> RansomwareScenarioData:
    """Generate synthetic ransomware scenario data."""
    base_time = datetime.now(timezone.utc) - timedelta(hours=1)

    # Create affected hosts (5+ hosts for mass containment trigger)
    affected_hosts = [
        RansomwareHost(
            asset_id="WS-FIN-101",
            hostname="ws-fin-101.corp.local",
            department="Finance",
            encrypted_files=1247,
            encryption_progress=78.5,
            first_seen=base_time,
            status="active",
        ),
        RansomwareHost(
            asset_id="WS-FIN-102",
            hostname="ws-fin-102.corp.local",
            department="Finance",
            encrypted_files=892,
            encryption_progress=45.2,
            first_seen=base_time + timedelta(minutes=3),
            status="active",
        ),
        RansomwareHost(
            asset_id="WS-HR-015",
            hostname="ws-hr-015.corp.local",
            department="Human Resources",
            encrypted_files=2156,
            encryption_progress=92.1,
            first_seen=base_time + timedelta(minutes=5),
            status="active",
        ),
        RansomwareHost(
            asset_id="SRV-FILE-01",
            hostname="srv-file-01.corp.local",
            department="IT",
            encrypted_files=15482,
            encryption_progress=33.7,
            first_seen=base_time + timedelta(minutes=8),
            status="active",
        ),
        RansomwareHost(
            asset_id="WS-LEGAL-003",
            hostname="ws-legal-003.corp.local",
            department="Legal",
            encrypted_files=3421,
            encryption_progress=67.9,
            first_seen=base_time + timedelta(minutes=10),
            status="active",
        ),
        RansomwareHost(
            asset_id="WS-EXEC-007",
            hostname="ws-exec-007.corp.local",
            department="Executive",
            encrypted_files=567,
            encryption_progress=12.3,
            first_seen=base_time + timedelta(minutes=12),
            status="active",
        ),
    ]

    # Create timeline events
    timeline_events = [
        {
            "timestamp": base_time.isoformat(),
            "event": "initial_detection",
            "host": "ws-fin-101.corp.local",
            "details": "Suspicious file encryption activity detected",
        },
        {
            "timestamp": (base_time + timedelta(minutes=1)).isoformat(),
            "event": "hash_hunting",
            "details": f"Hash hunt initiated for {RANSOMWARE_HASH}",
        },
        {
            "timestamp": (base_time + timedelta(minutes=2)).isoformat(),
            "event": "propagation_detected",
            "details": f"Found {len(affected_hosts)} hosts with matching hash",
        },
        {
            "timestamp": (base_time + timedelta(minutes=3)).isoformat(),
            "event": "threat_intel_match",
            "details": f"Hash identified as {RANSOMWARE_FAMILY}",
        },
        {
            "timestamp": (base_time + timedelta(minutes=4)).isoformat(),
            "event": "mass_containment_triggered",
            "details": f"Mass containment initiated for {len(affected_hosts)} hosts",
        },
        {
            "timestamp": (base_time + timedelta(minutes=5)).isoformat(),
            "event": "executive_notification",
            "details": "Executive team notified via Teams/Slack",
        },
    ]

    return RansomwareScenarioData(
        incident_id=SCENARIO_ID,
        ransomware_family=RANSOMWARE_FAMILY,
        ransom_note_text="Your files have been encrypted by LockBit 3.0. "
                         "To decrypt your files, send 2.5 BTC to the following address.",
        bitcoin_address="bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
        ransom_amount_btc=2.5,
        affected_hosts=affected_hosts,
        initial_vector="phishing_email",
        lateral_movement_technique="T1021.001 - Remote Desktop Protocol",
        encryption_extension=".lockbit3",
        kill_switch_domain=None,  # No kill switch for LockBit 3.0
        timeline_events=timeline_events,
    )


# =============================================================================
# OpenSearch Index Data
# =============================================================================

def generate_incident_document() -> dict[str, Any]:
    """Generate SIEM incident document for OpenSearch."""
    return {
        "incident_id": SCENARIO_ID,
        "title": f"Ransomware Attack - {RANSOMWARE_FAMILY} - Multi-Host Encryption",
        "severity": "Critical",
        "status": "open",
        "device_id": "WS-FIN-101",  # Initial detection host
        "hash_sha256": RANSOMWARE_HASH,
        "process_name": "lockbit3.exe",
        "cmdline": "lockbit3.exe --encrypt-all --ransom-note",
        "mitre_technique": "T1486",  # Data Encrypted for Impact
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tags": ["ransomware", "mass-encryption", "critical-incident"],
        "affected_host_count": 6,
    }


def generate_asset_documents() -> list[dict[str, Any]]:
    """Generate asset documents for all affected hosts."""
    scenario = generate_ransomware_scenario()
    assets = []

    for host in scenario.affected_hosts:
        # Determine tags based on department
        tags = ["standard"]
        if host.department == "Executive":
            tags = ["vip", "executive"]
        elif host.department == "IT" and "SRV" in host.asset_id:
            tags = ["server", "critical-infrastructure"]

        assets.append({
            "asset_id": host.asset_id,
            "hostname": host.hostname,
            "device_type": "server" if "SRV" in host.asset_id else "workstation",
            "tags": tags,
            "owner": f"{host.department} User",
            "department": host.department,
            "criticality": "critical" if "SRV" in host.asset_id or host.department == "Executive" else "standard",
        })

    return assets


def generate_intel_document() -> dict[str, Any]:
    """Generate threat intel document for ransomware hash."""
    return {
        "hash": RANSOMWARE_HASH,
        "verdict": "malicious",
        "vt_score": 74,
        "vt_total": 75,
        "malware_labels": ["ransomware", "lockbit", "extortion", "file-encryptor"],
        "confidence": 99,
        "first_seen": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
        "threat_actor": "LockBit Ransomware Group",
        "ttp_references": ["T1486", "T1490", "T1489", "T1021.001"],
    }


def generate_edr_documents() -> list[dict[str, Any]]:
    """Generate EDR detection documents for all affected hosts."""
    scenario = generate_ransomware_scenario()
    detections = []

    for host in scenario.affected_hosts:
        detections.append({
            "detection_id": f"DET-{uuid.uuid4().hex[:8].upper()}",
            "asset_id": host.asset_id,
            "hostname": host.hostname,
            "file": {
                "sha256": RANSOMWARE_HASH,
                "name": "lockbit3.exe",
                "path": "C:\\Users\\Public\\lockbit3.exe",
            },
            "process": {
                "name": "lockbit3.exe",
                "cmdline": "lockbit3.exe --encrypt-all --ransom-note",
                "parent": "explorer.exe",
            },
            "severity": "Critical",
            "mitre_technique": "T1486",
            "timestamp": host.first_seen.isoformat(),
            "encrypted_files": host.encrypted_files,
            "encryption_progress": host.encryption_progress,
        })

    return detections


def generate_propagation_document() -> dict[str, Any]:
    """Generate hash propagation document."""
    scenario = generate_ransomware_scenario()
    return {
        "hash": RANSOMWARE_HASH,
        "affected_hosts": [h.asset_id for h in scenario.affected_hosts],
        "affected_count": scenario.affected_count,
        "first_seen": scenario.affected_hosts[0].first_seen.isoformat(),
        "last_seen": scenario.affected_hosts[-1].first_seen.isoformat(),
        "spread_rate": "rapid",  # >5 hosts in <15 minutes
    }


# =============================================================================
# Playbook Actions
# =============================================================================

def get_response_playbook() -> dict[str, Any]:
    """Get the ransomware response playbook for this scenario."""
    return {
        "playbook_id": "PB-RANSOMWARE-001",
        "name": "Ransomware Mass Containment Response",
        "steps": [
            {
                "step": 1,
                "action": "mass_containment",
                "description": "Immediately contain all affected hosts",
                "automated": True,
                "priority": "critical",
            },
            {
                "step": 2,
                "action": "network_isolation",
                "description": "Isolate affected network segments",
                "automated": True,
                "priority": "critical",
            },
            {
                "step": 3,
                "action": "executive_notification",
                "description": "Notify executive team and CISO",
                "automated": True,
                "priority": "critical",
            },
            {
                "step": 4,
                "action": "hash_block",
                "description": "Block ransomware hash across all EDR agents",
                "automated": True,
                "priority": "high",
            },
            {
                "step": 5,
                "action": "backup_verification",
                "description": "Verify backup integrity and availability",
                "automated": False,
                "priority": "high",
            },
            {
                "step": 6,
                "action": "forensic_collection",
                "description": "Collect forensic evidence from affected hosts",
                "automated": False,
                "priority": "medium",
            },
            {
                "step": 7,
                "action": "law_enforcement_notification",
                "description": "Consider law enforcement notification",
                "automated": False,
                "priority": "medium",
            },
        ],
        "estimated_duration_minutes": 60,
        "requires_executive_approval": True,
    }
