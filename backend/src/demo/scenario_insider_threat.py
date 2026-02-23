"""Scenario 5: Insider Threat - Privileged User Data Exfiltration.

Trigger: Privileged user exfiltrating data.
Expected behavior:
1. Detect anomalous data volume
2. Correlate with time/location anomalies
3. Require HR approval before action
4. Legal evidence preservation
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any
import uuid


# =============================================================================
# Scenario Constants
# =============================================================================

SCENARIO_ID = "INC-ANCHOR-005"
SCENARIO_NAME = "Insider Threat - Data Exfiltration"
INSIDER_USER_ID = "jdoe.admin"
INSIDER_DEVICE_ID = "WS-IT-ADMIN-042"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class DataTransferEvent:
    """Individual data transfer event."""
    event_id: str
    timestamp: datetime
    destination: str
    destination_type: str  # cloud_storage, usb, email, external_site
    data_size_mb: float
    file_count: int
    sensitive_data_detected: bool
    dlp_policy_violated: str | None


@dataclass
class LocationAnomaly:
    """Geographic location anomaly."""
    timestamp: datetime
    expected_location: str
    actual_location: str
    ip_address: str
    vpn_used: bool
    impossible_travel: bool
    distance_km: float


@dataclass
class TimeAnomaly:
    """Time-based anomaly."""
    timestamp: datetime
    activity_type: str
    normal_hours: str
    actual_time: str
    day_of_week: str
    is_holiday: bool


@dataclass
class InsiderThreatScenarioData:
    """Complete insider threat scenario data."""
    incident_id: str
    user_id: str
    user_name: str
    user_title: str
    user_department: str
    device_id: str
    risk_score: int
    data_transfers: list[DataTransferEvent]
    location_anomalies: list[LocationAnomaly]
    time_anomalies: list[TimeAnomaly]
    hr_flags: list[str]
    recent_events: list[str]  # HR events like resignation notice, PIP, etc.
    timeline_events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def total_data_transferred_mb(self) -> float:
        return sum(t.data_size_mb for t in self.data_transfers)

    @property
    def total_files_transferred(self) -> int:
        return sum(t.file_count for t in self.data_transfers)

    @property
    def dlp_violations_count(self) -> int:
        return sum(1 for t in self.data_transfers if t.dlp_policy_violated)


# =============================================================================
# Scenario Data Generator
# =============================================================================

def generate_insider_threat_scenario() -> InsiderThreatScenarioData:
    """Generate synthetic insider threat scenario data."""
    base_time = datetime.now(timezone.utc) - timedelta(hours=6)

    # Data transfer events (anomalous volume)
    data_transfers = [
        DataTransferEvent(
            event_id=f"DT-{uuid.uuid4().hex[:8].upper()}",
            timestamp=base_time,
            destination="personal-cloud.example.com",
            destination_type="cloud_storage",
            data_size_mb=1250.5,
            file_count=342,
            sensitive_data_detected=True,
            dlp_policy_violated="PII-PROTECTION",
        ),
        DataTransferEvent(
            event_id=f"DT-{uuid.uuid4().hex[:8].upper()}",
            timestamp=base_time + timedelta(hours=1),
            destination="USB-DRIVE-SANDISK-8GB",
            destination_type="usb",
            data_size_mb=7800.0,
            file_count=1523,
            sensitive_data_detected=True,
            dlp_policy_violated="SOURCE-CODE-EXFIL",
        ),
        DataTransferEvent(
            event_id=f"DT-{uuid.uuid4().hex[:8].upper()}",
            timestamp=base_time + timedelta(hours=2),
            destination="competitor-hr@rivalcorp.com",
            destination_type="email",
            data_size_mb=45.2,
            file_count=12,
            sensitive_data_detected=True,
            dlp_policy_violated="CUSTOMER-DATA-LEAK",
        ),
        DataTransferEvent(
            event_id=f"DT-{uuid.uuid4().hex[:8].upper()}",
            timestamp=base_time + timedelta(hours=3),
            destination="mega.nz",
            destination_type="cloud_storage",
            data_size_mb=3200.0,
            file_count=567,
            sensitive_data_detected=True,
            dlp_policy_violated="CONFIDENTIAL-DOCS",
        ),
    ]

    # Location anomalies
    location_anomalies = [
        LocationAnomaly(
            timestamp=base_time - timedelta(hours=2),
            expected_location="New York, NY",
            actual_location="Singapore",
            ip_address="103.45.67.89",
            vpn_used=True,
            impossible_travel=True,
            distance_km=15330.0,
        ),
        LocationAnomaly(
            timestamp=base_time + timedelta(hours=1),
            expected_location="New York, NY",
            actual_location="Toronto, Canada",
            ip_address="72.142.55.12",
            vpn_used=False,
            impossible_travel=False,
            distance_km=550.0,
        ),
    ]

    # Time anomalies
    time_anomalies = [
        TimeAnomaly(
            timestamp=base_time,
            activity_type="data_access",
            normal_hours="09:00-18:00",
            actual_time="02:30",
            day_of_week="Saturday",
            is_holiday=False,
        ),
        TimeAnomaly(
            timestamp=base_time + timedelta(hours=2),
            activity_type="bulk_download",
            normal_hours="09:00-18:00",
            actual_time="04:30",
            day_of_week="Saturday",
            is_holiday=False,
        ),
    ]

    # HR flags
    hr_flags = [
        "RESIGNATION_NOTICE_SUBMITTED",
        "COMPETITOR_OFFER_SUSPECTED",
        "BADGE_ACCESS_AFTER_HOURS",
        "UNUSUAL_PRINT_VOLUME",
    ]

    # Recent HR events
    recent_events = [
        "2 weeks ago: Submitted resignation notice",
        "3 weeks ago: Denied promotion request",
        "1 month ago: Verbal warning for policy violation",
    ]

    # Timeline events with MITRE ATT&CK mapping
    # Insider threat techniques: T1078 (Valid Accounts), T1567 (Exfil Over Web),
    # T1052 (Exfil Over Physical Medium), T1114 (Email Collection)
    timeline_events = [
        {
            "timestamp": base_time.isoformat(),
            "event": "anomaly_detected",
            "details": "Anomalous data volume detected for privileged user",
            "mitre_tactic": "TA0010",
            "tactic_id": "TA0010",
            "tactic_name": "Exfiltration",
            "mitre_technique": "T1567",
            "technique_id": "T1567",
            "technique_name": "Exfiltration Over Web Service",
        },
        {
            "timestamp": (base_time + timedelta(minutes=5)).isoformat(),
            "event": "ueba_alert",
            "details": "UEBA risk score exceeded threshold (85/100)",
            "mitre_tactic": "TA0001",
            "tactic_id": "TA0001",
            "tactic_name": "Initial Access",
            "mitre_technique": "T1078",
            "technique_id": "T1078",
            "technique_name": "Valid Accounts",
        },
        {
            "timestamp": (base_time + timedelta(minutes=10)).isoformat(),
            "event": "dlp_violations",
            "details": "Multiple DLP policy violations detected",
            "mitre_tactic": "TA0009",
            "tactic_id": "TA0009",
            "tactic_name": "Collection",
            "mitre_technique": "T1005",
            "technique_id": "T1005",
            "technique_name": "Data from Local System",
        },
        {
            "timestamp": (base_time + timedelta(minutes=15)).isoformat(),
            "event": "hr_correlation",
            "details": "Correlated with recent resignation notice",
            "mitre_tactic": None,
            "tactic_id": None,
            "mitre_technique": None,
            "technique_id": None,
        },
        {
            "timestamp": (base_time + timedelta(minutes=20)).isoformat(),
            "event": "location_anomaly",
            "details": "Impossible travel detected: NY to Singapore in 2 hours",
            "mitre_tactic": "TA0005",
            "tactic_id": "TA0005",
            "tactic_name": "Defense Evasion",
            "mitre_technique": "T1078.004",
            "technique_id": "T1078.004",
            "technique_name": "Cloud Accounts",
        },
        {
            "timestamp": (base_time + timedelta(minutes=25)).isoformat(),
            "event": "usb_exfiltration",
            "details": "USB device data transfer detected",
            "mitre_tactic": "TA0010",
            "tactic_id": "TA0010",
            "tactic_name": "Exfiltration",
            "mitre_technique": "T1052.001",
            "technique_id": "T1052.001",
            "technique_name": "Exfiltration over USB",
        },
        {
            "timestamp": (base_time + timedelta(minutes=27)).isoformat(),
            "event": "hr_approval_required",
            "details": "HR approval required before containment action",
            "mitre_tactic": None,
            "tactic_id": None,
            "mitre_technique": None,
            "technique_id": None,
        },
        {
            "timestamp": (base_time + timedelta(minutes=30)).isoformat(),
            "event": "legal_hold_initiated",
            "details": "Legal hold initiated for evidence preservation",
            "mitre_tactic": None,
            "tactic_id": None,
            "mitre_technique": None,
            "technique_id": None,
        },
    ]

    return InsiderThreatScenarioData(
        incident_id=SCENARIO_ID,
        user_id=INSIDER_USER_ID,
        user_name="John Doe",
        user_title="Senior IT Administrator",
        user_department="IT Operations",
        device_id=INSIDER_DEVICE_ID,
        risk_score=85,
        data_transfers=data_transfers,
        location_anomalies=location_anomalies,
        time_anomalies=time_anomalies,
        hr_flags=hr_flags,
        recent_events=recent_events,
        timeline_events=timeline_events,
    )


# =============================================================================
# OpenSearch Index Data
# =============================================================================

def generate_incident_document() -> dict[str, Any]:
    """Generate SIEM incident document for OpenSearch."""
    scenario = generate_insider_threat_scenario()
    return {
        "incident_id": SCENARIO_ID,
        "title": f"Insider Threat - Data Exfiltration by {scenario.user_name}",
        "severity": "Critical",
        "status": "open",
        "device_id": INSIDER_DEVICE_ID,
        "hash_sha256": "",  # No hash for insider threat
        "process_name": "explorer.exe",
        "cmdline": "",
        "mitre_technique": "T1567",  # Exfiltration Over Web Service
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tags": ["insider-threat", "data-exfiltration", "privileged-user", "hr-required"],
        "user_id": INSIDER_USER_ID,
        "risk_score": scenario.risk_score,
        "data_volume_mb": scenario.total_data_transferred_mb,
        "dlp_violations": scenario.dlp_violations_count,
    }


def generate_asset_document() -> dict[str, Any]:
    """Generate asset document for insider's workstation."""
    return {
        "asset_id": INSIDER_DEVICE_ID,
        "hostname": "ws-it-admin-042.corp.local",
        "device_type": "workstation",
        "tags": ["privileged-user", "admin-workstation", "hr-approval-required"],
        "owner": "John Doe",
        "department": "IT Operations",
        "criticality": "high",
        "admin_privileges": True,
    }


def generate_ueba_document() -> dict[str, Any]:
    """Generate UEBA (User Entity Behavior Analytics) document."""
    scenario = generate_insider_threat_scenario()
    return {
        "user_id": INSIDER_USER_ID,
        "risk_score": scenario.risk_score,
        "baseline_deviation": 4.2,  # Standard deviations from normal
        "anomalies_detected": [
            "data_volume_spike",
            "off_hours_activity",
            "impossible_travel",
            "usb_usage",
            "cloud_upload",
        ],
        "risk_factors": {
            "data_volume": 95,
            "time_anomaly": 78,
            "location_anomaly": 88,
            "dlp_violations": 100,
            "hr_risk_indicators": 75,
        },
        "peer_comparison": "12x average data transfer compared to peer group",
        "historical_risk": [
            {"date": "2025-01-15", "score": 25},
            {"date": "2025-01-22", "score": 35},
            {"date": "2025-01-29", "score": 45},
            {"date": "2025-02-05", "score": 65},
            {"date": "2025-02-12", "score": 85},
        ],
    }


def generate_dlp_documents() -> list[dict[str, Any]]:
    """Generate DLP violation documents."""
    scenario = generate_insider_threat_scenario()
    dlp_docs = []

    for transfer in scenario.data_transfers:
        if transfer.dlp_policy_violated:
            dlp_docs.append({
                "dlp_id": f"DLP-{uuid.uuid4().hex[:8].upper()}",
                "user_id": INSIDER_USER_ID,
                "device_id": INSIDER_DEVICE_ID,
                "policy_violated": transfer.dlp_policy_violated,
                "destination": transfer.destination,
                "destination_type": transfer.destination_type,
                "data_size_mb": transfer.data_size_mb,
                "file_count": transfer.file_count,
                "sensitive_categories": ["PII", "source_code", "customer_data"],
                "timestamp": transfer.timestamp.isoformat(),
                "action_taken": "logged",  # logged, blocked, quarantined
                "severity": "critical",
            })

    return dlp_docs


# =============================================================================
# Approval Workflow
# =============================================================================

def get_approval_requirements() -> dict[str, Any]:
    """Get required approvals for insider threat response."""
    return {
        "required_approvals": [
            {
                "role": "HR Manager",
                "reason": "Employee privacy and labor law compliance",
                "sla_minutes": 30,
                "escalation_path": "CHRO",
            },
            {
                "role": "Legal Counsel",
                "reason": "Evidence preservation and legal hold",
                "sla_minutes": 60,
                "escalation_path": "General Counsel",
            },
        ],
        "optional_approvals": [
            {
                "role": "IT Security Manager",
                "reason": "Technical containment approach review",
            },
        ],
        "evidence_preservation": {
            "required": True,
            "chain_of_custody": True,
            "forensic_image": True,
            "legal_hold": True,
        },
    }


def get_response_playbook() -> dict[str, Any]:
    """Get the insider threat response playbook for this scenario."""
    return {
        "playbook_id": "PB-INSIDER-001",
        "name": "Insider Threat Investigation Response",
        "steps": [
            {
                "step": 1,
                "action": "evidence_preservation",
                "description": "Initiate legal hold and preserve evidence",
                "automated": True,
                "priority": "critical",
            },
            {
                "step": 2,
                "action": "hr_notification",
                "description": "Notify HR for approval and guidance",
                "automated": True,
                "priority": "critical",
            },
            {
                "step": 3,
                "action": "legal_notification",
                "description": "Notify legal team for chain of custody",
                "automated": True,
                "priority": "critical",
            },
            {
                "step": 4,
                "action": "await_hr_approval",
                "description": "Wait for HR approval before containment",
                "automated": False,
                "priority": "critical",
                "sla_minutes": 30,
            },
            {
                "step": 5,
                "action": "account_disable",
                "description": "Disable user account (requires HR approval)",
                "automated": False,
                "priority": "high",
                "requires_approval": True,
            },
            {
                "step": 6,
                "action": "badge_revocation",
                "description": "Revoke physical access badges",
                "automated": False,
                "priority": "high",
            },
            {
                "step": 7,
                "action": "forensic_collection",
                "description": "Collect forensic image of user's device",
                "automated": False,
                "priority": "high",
            },
            {
                "step": 8,
                "action": "data_recovery",
                "description": "Attempt to recover exfiltrated data",
                "automated": False,
                "priority": "medium",
            },
        ],
        "estimated_duration_minutes": 120,
        "requires_hr_approval": True,
        "requires_legal_approval": True,
    }
