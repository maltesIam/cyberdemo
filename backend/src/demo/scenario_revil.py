"""Scenario 6: REvil (Sodinokibi) Ransomware Attack.

Trigger: Detection of file encryption combined with data exfiltration.
Expected behavior:
1. Detect initial compromise via RDP brute force or phishing
2. Identify lateral movement and privilege escalation
3. Detect data staging and exfiltration (double extortion)
4. Detect ransomware deployment and encryption
5. Mass containment and executive notification
6. Data breach response procedures

MITRE ATT&CK Mapping (REvil/Sodinokibi - S0496):
- Initial Access: T1133 (External Remote Services), T1566 (Phishing)
- Execution: T1059.001 (PowerShell), T1047 (WMI)
- Persistence: T1547.001 (Registry Run Keys)
- Privilege Escalation: T1055 (Process Injection)
- Defense Evasion: T1562.001 (Disable Security Tools)
- Credential Access: T1003 (Credential Dumping)
- Discovery: T1083 (File and Directory Discovery)
- Collection: T1005 (Data from Local System), T1560 (Archive Collected Data)
- Exfiltration: T1567 (Exfiltration Over Web Service)
- Impact: T1486 (Data Encrypted for Impact), T1490 (Inhibit System Recovery)

Task: T-1.3.005
Requirement: REQ-002-001-004 - Escenario REvil - Ransomware
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any
import uuid


# =============================================================================
# Scenario Constants
# =============================================================================

SCENARIO_ID = "INC-REVIL-006"
SCENARIO_NAME = "REvil (Sodinokibi) Double Extortion Attack"
THREAT_ACTOR = "REvil Ransomware Group (Gold Southfield)"
RANSOMWARE_HASH = "e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6"
RANSOMWARE_FAMILY = "REvil/Sodinokibi"
EXFIL_DOMAIN = "exfil-7h2x9.revil-leaks.onion"


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
    "TA0009": "Collection",
    "TA0010": "Exfiltration",
    "TA0040": "Impact",
}

REVIL_TECHNIQUES = {
    "T1133": {"name": "External Remote Services", "tactic": "TA0001"},
    "T1566.001": {"name": "Spear-Phishing Attachment", "tactic": "TA0001"},
    "T1059.001": {"name": "PowerShell", "tactic": "TA0002"},
    "T1047": {"name": "Windows Management Instrumentation", "tactic": "TA0002"},
    "T1547.001": {"name": "Registry Run Keys", "tactic": "TA0003"},
    "T1055": {"name": "Process Injection", "tactic": "TA0004"},
    "T1562.001": {"name": "Disable or Modify Tools", "tactic": "TA0005"},
    "T1003.001": {"name": "LSASS Memory", "tactic": "TA0006"},
    "T1083": {"name": "File and Directory Discovery", "tactic": "TA0007"},
    "T1005": {"name": "Data from Local System", "tactic": "TA0009"},
    "T1560.001": {"name": "Archive via Utility", "tactic": "TA0009"},
    "T1567.002": {"name": "Exfiltration to Cloud Storage", "tactic": "TA0010"},
    "T1486": {"name": "Data Encrypted for Impact", "tactic": "TA0040"},
    "T1490": {"name": "Inhibit System Recovery", "tactic": "TA0040"},
    "T1489": {"name": "Service Stop", "tactic": "TA0040"},
}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class REvilHost:
    """Host affected by REvil ransomware attack."""
    asset_id: str
    hostname: str
    department: str
    encryption_status: str  # pending, in_progress, encrypted
    encryption_progress: float  # 0-100%
    data_exfiltrated: bool
    exfil_size_gb: float
    first_seen: datetime
    status: str = "compromised"  # compromised, contained, recovered


@dataclass
class REvilScenarioData:
    """Complete REvil ransomware attack scenario data."""
    incident_id: str
    threat_actor: str
    ransomware_family: str
    ransomware_hash: str
    initial_vector: str
    affected_hosts: list[REvilHost]
    data_exfiltrated: bool
    exfiltration_size_gb: float
    exfil_destination: str
    ransom_amount_btc: float
    ransom_amount_usd: int
    payment_deadline: datetime
    leak_site_url: str
    encryption_extension: str
    timeline_events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def affected_count(self) -> int:
        return len(self.affected_hosts)

    @property
    def encrypted_count(self) -> int:
        return sum(1 for h in self.affected_hosts if h.encryption_status == "encrypted")

    @property
    def total_exfil_size(self) -> float:
        return sum(h.exfil_size_gb for h in self.affected_hosts if h.data_exfiltrated)


# =============================================================================
# Scenario Data Generator
# =============================================================================

def generate_revil_scenario() -> REvilScenarioData:
    """Generate synthetic REvil ransomware attack scenario data."""
    base_time = datetime.now(timezone.utc) - timedelta(hours=6)

    # Create affected hosts (REvil targets valuable data)
    affected_hosts = [
        REvilHost(
            asset_id="SRV-DC-01",
            hostname="srv-dc-01.corp.local",
            department="IT Infrastructure",
            encryption_status="encrypted",
            encryption_progress=100.0,
            data_exfiltrated=True,
            exfil_size_gb=45.2,
            first_seen=base_time + timedelta(hours=5),
            status="compromised",
        ),
        REvilHost(
            asset_id="SRV-FILE-01",
            hostname="srv-file-01.corp.local",
            department="IT Infrastructure",
            encryption_status="encrypted",
            encryption_progress=100.0,
            data_exfiltrated=True,
            exfil_size_gb=128.7,
            first_seen=base_time + timedelta(hours=5, minutes=5),
            status="compromised",
        ),
        REvilHost(
            asset_id="SRV-SQL-PROD",
            hostname="srv-sql-prod.corp.local",
            department="Database",
            encryption_status="in_progress",
            encryption_progress=67.3,
            data_exfiltrated=True,
            exfil_size_gb=256.4,
            first_seen=base_time + timedelta(hours=5, minutes=10),
            status="compromised",
        ),
        REvilHost(
            asset_id="WS-CEO-001",
            hostname="ws-ceo-001.corp.local",
            department="Executive",
            encryption_status="encrypted",
            encryption_progress=100.0,
            data_exfiltrated=True,
            exfil_size_gb=12.8,
            first_seen=base_time + timedelta(hours=5, minutes=15),
            status="compromised",
        ),
        REvilHost(
            asset_id="WS-CFO-001",
            hostname="ws-cfo-001.corp.local",
            department="Executive",
            encryption_status="in_progress",
            encryption_progress=45.2,
            data_exfiltrated=True,
            exfil_size_gb=8.3,
            first_seen=base_time + timedelta(hours=5, minutes=18),
            status="compromised",
        ),
        REvilHost(
            asset_id="SRV-EXCHANGE",
            hostname="srv-exchange.corp.local",
            department="IT Infrastructure",
            encryption_status="pending",
            encryption_progress=0.0,
            data_exfiltrated=False,
            exfil_size_gb=0.0,
            first_seen=base_time + timedelta(hours=5, minutes=20),
            status="compromised",
        ),
    ]

    payment_deadline = datetime.now(timezone.utc) + timedelta(days=7)

    # Create timeline events with MITRE ATT&CK mapping
    timeline_events = [
        {
            "timestamp": base_time.isoformat(),
            "event": "initial_access",
            "details": "RDP brute force attack succeeded on exposed server",
            "host": "srv-dc-01.corp.local",
            "mitre_tactic": "TA0001",
            "tactic_id": "TA0001",
            "tactic_name": "Initial Access",
            "mitre_technique": "T1133",
            "technique_id": "T1133",
            "technique_name": "External Remote Services",
        },
        {
            "timestamp": (base_time + timedelta(minutes=15)).isoformat(),
            "event": "execution",
            "details": "PowerShell payload executed - Cobalt Strike beacon deployed",
            "host": "srv-dc-01.corp.local",
            "mitre_tactic": "TA0002",
            "tactic_id": "TA0002",
            "tactic_name": "Execution",
            "mitre_technique": "T1059.001",
            "technique_id": "T1059.001",
            "technique_name": "PowerShell",
        },
        {
            "timestamp": (base_time + timedelta(minutes=30)).isoformat(),
            "event": "credential_access",
            "details": "Mimikatz executed - domain admin credentials obtained",
            "host": "srv-dc-01.corp.local",
            "mitre_tactic": "TA0006",
            "tactic_id": "TA0006",
            "tactic_name": "Credential Access",
            "mitre_technique": "T1003.001",
            "technique_id": "T1003.001",
            "technique_name": "LSASS Memory",
        },
        {
            "timestamp": (base_time + timedelta(hours=1)).isoformat(),
            "event": "discovery",
            "details": "File and directory enumeration across network shares",
            "host": "srv-dc-01.corp.local",
            "mitre_tactic": "TA0007",
            "tactic_id": "TA0007",
            "tactic_name": "Discovery",
            "mitre_technique": "T1083",
            "technique_id": "T1083",
            "technique_name": "File and Directory Discovery",
        },
        {
            "timestamp": (base_time + timedelta(hours=2)).isoformat(),
            "event": "defense_evasion",
            "details": "Security tools disabled - Windows Defender and AV stopped",
            "host": "srv-dc-01.corp.local",
            "mitre_tactic": "TA0005",
            "tactic_id": "TA0005",
            "tactic_name": "Defense Evasion",
            "mitre_technique": "T1562.001",
            "technique_id": "T1562.001",
            "technique_name": "Disable or Modify Tools",
        },
        {
            "timestamp": (base_time + timedelta(hours=3)).isoformat(),
            "event": "collection",
            "details": "Data staging - sensitive files archived for exfiltration",
            "host": "srv-file-01.corp.local",
            "mitre_tactic": "TA0009",
            "tactic_id": "TA0009",
            "tactic_name": "Collection",
            "mitre_technique": "T1560.001",
            "technique_id": "T1560.001",
            "technique_name": "Archive via Utility",
        },
        {
            "timestamp": (base_time + timedelta(hours=4)).isoformat(),
            "event": "exfiltration",
            "details": f"Data exfiltration to {EXFIL_DOMAIN} - 450+ GB transferred",
            "host": "srv-file-01.corp.local",
            "exfil_destination": EXFIL_DOMAIN,
            "exfil_size_gb": 451.4,
            "mitre_tactic": "TA0010",
            "tactic_id": "TA0010",
            "tactic_name": "Exfiltration",
            "mitre_technique": "T1567.002",
            "technique_id": "T1567.002",
            "technique_name": "Exfiltration to Cloud Storage",
        },
        {
            "timestamp": (base_time + timedelta(hours=4, minutes=30)).isoformat(),
            "event": "impact_recovery_inhibit",
            "details": "Shadow copies deleted - vssadmin delete shadows /all /quiet",
            "host": "srv-dc-01.corp.local",
            "mitre_tactic": "TA0040",
            "tactic_id": "TA0040",
            "tactic_name": "Impact",
            "mitre_technique": "T1490",
            "technique_id": "T1490",
            "technique_name": "Inhibit System Recovery",
        },
        {
            "timestamp": (base_time + timedelta(hours=4, minutes=45)).isoformat(),
            "event": "impact_service_stop",
            "details": "Critical services stopped - SQL Server, Exchange, backup agents",
            "host": "srv-sql-prod.corp.local",
            "mitre_tactic": "TA0040",
            "tactic_id": "TA0040",
            "tactic_name": "Impact",
            "mitre_technique": "T1489",
            "technique_id": "T1489",
            "technique_name": "Service Stop",
        },
        {
            "timestamp": (base_time + timedelta(hours=5)).isoformat(),
            "event": "impact_encryption",
            "details": "Ransomware deployed - mass file encryption initiated",
            "host": "srv-dc-01.corp.local",
            "mitre_tactic": "TA0040",
            "tactic_id": "TA0040",
            "tactic_name": "Impact",
            "mitre_technique": "T1486",
            "technique_id": "T1486",
            "technique_name": "Data Encrypted for Impact",
        },
        {
            "timestamp": (base_time + timedelta(hours=5, minutes=30)).isoformat(),
            "event": "ransom_note",
            "details": f"Ransom note dropped - demanding 50 BTC ($2.3M USD) by {payment_deadline.strftime('%Y-%m-%d')}",
            "ransom_btc": 50.0,
            "ransom_usd": 2300000,
            "mitre_tactic": "TA0040",
            "tactic_id": "TA0040",
            "mitre_technique": "T1486",
            "technique_id": "T1486",
        },
        {
            "timestamp": (base_time + timedelta(hours=5, minutes=45)).isoformat(),
            "event": "threat_intel_match",
            "details": f"Hash identified as {RANSOMWARE_FAMILY} - double extortion attack confirmed",
            "mitre_tactic": None,
            "tactic_id": None,
            "mitre_technique": None,
            "technique_id": None,
        },
        {
            "timestamp": (base_time + timedelta(hours=6)).isoformat(),
            "event": "executive_notification",
            "details": "Ransomware + data breach detected - escalating to executive leadership and legal",
            "mitre_tactic": None,
            "tactic_id": None,
            "mitre_technique": None,
            "technique_id": None,
        },
    ]

    return REvilScenarioData(
        incident_id=SCENARIO_ID,
        threat_actor=THREAT_ACTOR,
        ransomware_family=RANSOMWARE_FAMILY,
        ransomware_hash=RANSOMWARE_HASH,
        initial_vector="rdp_brute_force",
        affected_hosts=affected_hosts,
        data_exfiltrated=True,
        exfiltration_size_gb=451.4,
        exfil_destination=EXFIL_DOMAIN,
        ransom_amount_btc=50.0,
        ransom_amount_usd=2300000,
        payment_deadline=payment_deadline,
        leak_site_url=f"http://{EXFIL_DOMAIN}/leaks/corp-inc",
        encryption_extension=".revil",
        timeline_events=timeline_events,
    )


# =============================================================================
# OpenSearch Index Data
# =============================================================================

def generate_incident_document() -> dict[str, Any]:
    """Generate SIEM incident document for OpenSearch."""
    return {
        "incident_id": SCENARIO_ID,
        "title": f"Ransomware Attack - {RANSOMWARE_FAMILY} - Double Extortion",
        "severity": "Critical",
        "status": "open",
        "device_id": "SRV-DC-01",  # First compromised host
        "hash_sha256": RANSOMWARE_HASH,
        "process_name": "sodinokibi.exe",
        "cmdline": "sodinokibi.exe --encrypt --network --delete-shadows",
        "mitre_technique": "T1486",  # Data Encrypted for Impact
        "technique_id": "T1486",
        "tactic_id": "TA0040",
        "threat_actor": THREAT_ACTOR,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tags": ["ransomware", "double-extortion", "data-breach", "revil", "sodinokibi", "critical-incident"],
        "affected_host_count": 6,
        "data_exfiltrated": True,
        "exfil_size_gb": 451.4,
        "ransom_btc": 50.0,
    }


def generate_asset_documents() -> list[dict[str, Any]]:
    """Generate asset documents for all affected hosts."""
    scenario = generate_revil_scenario()
    assets = []

    for host in scenario.affected_hosts:
        # Determine criticality based on type
        if "DC" in host.asset_id or "SQL" in host.asset_id:
            criticality = "critical"
            tags = ["domain-controller" if "DC" in host.asset_id else "database", "production"]
        elif "EXCHANGE" in host.asset_id:
            criticality = "critical"
            tags = ["email", "production"]
        elif "CEO" in host.asset_id or "CFO" in host.asset_id:
            criticality = "high"
            tags = ["vip", "executive"]
        elif "FILE" in host.asset_id:
            criticality = "high"
            tags = ["file-server", "production"]
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
            "encryption_status": host.encryption_status,
            "data_exfiltrated": host.data_exfiltrated,
        })

    return assets


def generate_intel_document() -> dict[str, Any]:
    """Generate threat intel document for ransomware hash."""
    return {
        "hash": RANSOMWARE_HASH,
        "verdict": "malicious",
        "vt_score": 72,
        "vt_total": 73,
        "malware_labels": ["ransomware", "revil", "sodinokibi", "double-extortion", "raas"],
        "confidence": 99,
        "first_seen": (datetime.now(timezone.utc) - timedelta(days=14)).isoformat(),
        "threat_actor": THREAT_ACTOR,
        "ransomware_family": RANSOMWARE_FAMILY,
        "ttp_references": ["T1486", "T1490", "T1489", "T1567.002", "T1133"],
        "ioc_type": "file_hash",
        "affiliate_id": "aff-7x92",  # REvil uses affiliate model
    }


def generate_edr_documents() -> list[dict[str, Any]]:
    """Generate EDR detection documents for all affected hosts."""
    scenario = generate_revil_scenario()
    detections = []

    for host in scenario.affected_hosts:
        # Primary detection - ransomware
        detections.append({
            "detection_id": f"DET-{uuid.uuid4().hex[:8].upper()}",
            "asset_id": host.asset_id,
            "hostname": host.hostname,
            "file": {
                "sha256": RANSOMWARE_HASH,
                "name": "sodinokibi.exe",
                "path": "C:\\ProgramData\\sodinokibi.exe",
            },
            "process": {
                "name": "sodinokibi.exe",
                "cmdline": "sodinokibi.exe --encrypt --network --delete-shadows",
                "parent": "powershell.exe",
            },
            "severity": "Critical",
            "mitre_technique": "T1486",
            "technique_id": "T1486",
            "tactic_id": "TA0040",
            "timestamp": host.first_seen.isoformat(),
            "encryption_status": host.encryption_status,
            "encryption_progress": host.encryption_progress,
            "data_exfiltrated": host.data_exfiltrated,
            "threat_actor": THREAT_ACTOR,
        })

    return detections


def generate_exfil_document() -> dict[str, Any]:
    """Generate data exfiltration document."""
    scenario = generate_revil_scenario()
    return {
        "exfil_id": f"EXFIL-{uuid.uuid4().hex[:8].upper()}",
        "destination": EXFIL_DOMAIN,
        "total_size_gb": scenario.exfiltration_size_gb,
        "files_exfiltrated": 15247,  # Estimated file count
        "sensitive_data_types": [
            "financial_records",
            "employee_pii",
            "customer_data",
            "intellectual_property",
            "executive_communications",
        ],
        "first_seen": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
        "last_seen": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
        "source_hosts": [h.asset_id for h in scenario.affected_hosts if h.data_exfiltrated],
    }


# =============================================================================
# Playbook Actions
# =============================================================================

def get_response_playbook() -> dict[str, Any]:
    """Get the double extortion ransomware response playbook."""
    return {
        "playbook_id": "PB-DOUBLE-EXTORT-001",
        "name": "REvil Double Extortion Response",
        "steps": [
            {
                "step": 1,
                "action": "network_isolation",
                "description": "Immediately isolate all affected systems from network",
                "automated": True,
                "priority": "critical",
            },
            {
                "step": 2,
                "action": "mass_containment",
                "description": "Contain all systems with ransomware indicators",
                "automated": True,
                "priority": "critical",
            },
            {
                "step": 3,
                "action": "executive_notification",
                "description": "Notify C-suite - ransomware + data breach confirmed",
                "automated": True,
                "priority": "critical",
            },
            {
                "step": 4,
                "action": "legal_notification",
                "description": "Engage legal counsel for data breach response",
                "automated": False,
                "priority": "critical",
            },
            {
                "step": 5,
                "action": "regulatory_assessment",
                "description": "Assess regulatory notification requirements (GDPR, HIPAA, etc.)",
                "automated": False,
                "priority": "high",
            },
            {
                "step": 6,
                "action": "forensic_collection",
                "description": "Collect forensic evidence from affected systems",
                "automated": False,
                "priority": "high",
            },
            {
                "step": 7,
                "action": "exfiltration_analysis",
                "description": "Analyze what data was exfiltrated for breach notification",
                "automated": False,
                "priority": "high",
            },
            {
                "step": 8,
                "action": "backup_verification",
                "description": "Verify backup integrity - ensure not encrypted",
                "automated": False,
                "priority": "high",
            },
            {
                "step": 9,
                "action": "threat_intel_sharing",
                "description": "Share IOCs with ISAC and law enforcement",
                "automated": False,
                "priority": "medium",
            },
            {
                "step": 10,
                "action": "law_enforcement_contact",
                "description": "Contact FBI IC3 for ransomware incident reporting",
                "automated": False,
                "priority": "medium",
            },
            {
                "step": 11,
                "action": "data_breach_notification",
                "description": "Prepare customer/employee breach notifications as required",
                "automated": False,
                "priority": "medium",
            },
            {
                "step": 12,
                "action": "recovery_planning",
                "description": "Develop clean recovery plan from verified backups",
                "automated": False,
                "priority": "medium",
            },
        ],
        "estimated_duration_minutes": 720,  # 12 hours minimum
        "requires_executive_approval": True,
        "requires_legal_review": True,
        "data_breach_confirmed": True,
        "external_notifications": ["FBI IC3", "State AG", "Industry ISAC", "Cyber Insurance"],
    }
