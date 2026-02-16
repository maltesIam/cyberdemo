"""Data generation endpoints for CyberDemo synthetic data."""

import logging
import random
import uuid
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..opensearch.client import OpenSearchClient
from ..opensearch.templates import ALL_INDICES

logger = logging.getLogger(__name__)
router = APIRouter()


class ResetResponse(BaseModel):
    """Response model for reset operation."""
    status: str
    deleted: dict[str, bool]
    created: dict[str, bool]


class GenerateResponse(BaseModel):
    """Response model for data generation."""
    status: str
    counts: dict[str, int]


class HealthResponse(BaseModel):
    """Response model for generation health check."""
    status: str
    indices: dict[str, int]
    total_documents: int


class GenerationStatusResponse(BaseModel):
    """Response model for generation status (document counts)."""
    assets: int = 0
    incidents: int = 0
    detections: int = 0
    postmortems: int = 0
    tickets: int = 0
    agent_actions: int = 0


# Synthetic data generators
class SyntheticDataGenerator:
    """Generator for synthetic security data."""

    # Common data pools
    HOSTNAMES = [
        "ws-dev-001", "ws-dev-002", "ws-dev-003", "ws-finance-001", "ws-finance-002",
        "ws-hr-001", "srv-dc-001", "srv-dc-002", "srv-web-001", "srv-web-002",
        "srv-db-001", "srv-db-002", "srv-app-001", "srv-app-002", "srv-file-001",
        "laptop-exec-001", "laptop-exec-002", "laptop-sales-001", "laptop-sales-002",
        "srv-mail-001", "srv-backup-001", "ws-it-001", "ws-it-002", "ws-legal-001",
    ]

    USERS = [
        "admin", "jsmith", "jdoe", "asmith", "bwilson", "cjohnson", "dlee",
        "ewilliams", "fbrown", "gjones", "hgarcia", "imiller", "jmartinez",
        "krobinson", "lclark", "mrodriguez", "nlewis", "owalker", "phall",
        "qallen", "ryoung", "sking", "twright", "uscott", "vgreen",
    ]

    DEPARTMENTS = ["IT", "Finance", "HR", "Engineering", "Sales", "Legal", "Executive", "Marketing"]
    LOCATIONS = ["NYC-HQ", "SF-OFFICE", "CHI-BRANCH", "LON-EU", "TYO-APAC", "REMOTE"]
    OS_TYPES = ["Windows 11", "Windows 10", "Windows Server 2022", "macOS 14", "Ubuntu 22.04"]

    MITRE_TECHNIQUES = [
        ("T1059.001", "PowerShell", "Execution"),
        ("T1059.003", "Windows Command Shell", "Execution"),
        ("T1053.005", "Scheduled Task", "Persistence"),
        ("T1547.001", "Registry Run Keys", "Persistence"),
        ("T1003.001", "LSASS Memory", "Credential Access"),
        ("T1566.001", "Spearphishing Attachment", "Initial Access"),
        ("T1071.001", "Web Protocols", "Command and Control"),
        ("T1105", "Ingress Tool Transfer", "Command and Control"),
        ("T1486", "Data Encrypted for Impact", "Impact"),
        ("T1021.001", "Remote Desktop Protocol", "Lateral Movement"),
    ]

    MALWARE_FAMILIES = ["Emotet", "Cobalt Strike", "Mimikatz", "BloodHound", "TrickBot", "Ryuk"]
    THREAT_TYPES = ["malware", "phishing", "c2", "exploit", "ransomware", "cryptominer"]

    CVE_LIST = [
        ("CVE-2024-0001", 9.8, "Critical RCE in Web Framework"),
        ("CVE-2024-0002", 8.1, "SQL Injection in Database Driver"),
        ("CVE-2024-0003", 7.5, "Authentication Bypass"),
        ("CVE-2024-0004", 6.5, "Information Disclosure"),
        ("CVE-2024-0005", 5.3, "Cross-Site Scripting"),
        ("CVE-2023-9999", 9.1, "Privilege Escalation in Kernel"),
        ("CVE-2023-8888", 8.5, "Buffer Overflow in Service"),
    ]

    def __init__(self):
        self.now = datetime.utcnow()

    def _random_datetime(self, days_back: int = 30) -> str:
        """Generate a random datetime within the last N days."""
        delta = timedelta(
            days=random.randint(0, days_back),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        return (self.now - delta).isoformat() + "Z"

    def _generate_ip(self) -> str:
        """Generate a random internal IP address."""
        return f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

    def _generate_mac(self) -> str:
        """Generate a random MAC address."""
        return ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))

    def generate_assets(self, count: int = 50) -> list[dict[str, Any]]:
        """Generate synthetic asset inventory data."""
        assets = []
        for i in range(count):
            hostname = random.choice(self.HOSTNAMES) if i < len(self.HOSTNAMES) else f"host-{i:03d}"
            is_critical = "srv-dc" in hostname or "exec" in hostname

            assets.append({
                "asset_id": str(uuid.uuid4()),
                "hostname": hostname,
                "ip_address": self._generate_ip(),
                "mac_address": self._generate_mac(),
                "os": random.choice(self.OS_TYPES),
                "os_version": f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(1000, 9999)}",
                "asset_type": "server" if "srv" in hostname else "workstation" if "ws" in hostname else "laptop",
                "department": random.choice(self.DEPARTMENTS),
                "owner": random.choice(self.USERS),
                "location": random.choice(self.LOCATIONS),
                "criticality": "critical" if is_critical else random.choice(["high", "medium", "low"]),
                "tags": random.sample(["vip", "pci", "hipaa", "production", "development"], k=random.randint(0, 3)),
                "last_seen": self._random_datetime(1),
                "first_seen": self._random_datetime(365),
                "status": random.choice(["active", "active", "active", "inactive", "maintenance"]),
                "agent_version": f"7.{random.randint(0, 9)}.{random.randint(0, 99)}",
                "created_at": self._random_datetime(365),
                "updated_at": self._random_datetime(7),
            })
        return assets

    def generate_edr_detections(self, count: int = 100) -> list[dict[str, Any]]:
        """Generate synthetic EDR detection data."""
        detections = []
        for _ in range(count):
            technique = random.choice(self.MITRE_TECHNIQUES)
            severity = random.choice(["critical", "high", "medium", "low"])

            detections.append({
                "detection_id": str(uuid.uuid4()),
                "asset_id": str(uuid.uuid4()),
                "hostname": random.choice(self.HOSTNAMES),
                "detection_type": random.choice(["behavioral", "signature", "heuristic", "ml"]),
                "severity": severity,
                "confidence": round(random.uniform(0.5, 1.0), 2),
                "technique_id": technique[0],
                "technique_name": technique[1],
                "tactic": technique[2],
                "description": f"Detected suspicious {technique[1]} activity",
                "process_name": random.choice(["powershell.exe", "cmd.exe", "rundll32.exe", "regsvr32.exe", "mshta.exe"]),
                "process_path": f"C:\\Windows\\System32\\{random.choice(['powershell.exe', 'cmd.exe', 'rundll32.exe'])}",
                "process_hash": uuid.uuid4().hex,
                "parent_process": random.choice(["explorer.exe", "svchost.exe", "winword.exe", "outlook.exe"]),
                "command_line": f"-nop -w hidden -encodedcommand {uuid.uuid4().hex[:32]}",
                "user": random.choice(self.USERS),
                "status": random.choice(["new", "investigating", "resolved", "false_positive"]),
                "assigned_to": random.choice(self.USERS + [None, None]),
                "detected_at": self._random_datetime(7),
                "resolved_at": None if random.random() > 0.3 else self._random_datetime(3),
                "created_at": self._random_datetime(7),
            })
        return detections

    def generate_process_trees(self, count: int = 30) -> list[dict[str, Any]]:
        """Generate synthetic process tree data."""
        trees = []
        for _ in range(count):
            root_pid = str(random.randint(1000, 9999))
            processes = []

            # Generate parent process
            processes.append({
                "process_id": root_pid,
                "parent_id": "4",
                "name": random.choice(["explorer.exe", "services.exe", "winlogon.exe"]),
                "path": "C:\\Windows\\System32\\explorer.exe",
                "command_line": "C:\\Windows\\explorer.exe",
                "user": "SYSTEM",
                "start_time": self._random_datetime(1),
                "end_time": None,
                "hash_sha256": uuid.uuid4().hex + uuid.uuid4().hex[:32],
            })

            # Generate child processes
            for j in range(random.randint(1, 5)):
                child_pid = str(random.randint(10000, 99999))
                processes.append({
                    "process_id": child_pid,
                    "parent_id": root_pid,
                    "name": random.choice(["powershell.exe", "cmd.exe", "conhost.exe"]),
                    "path": f"C:\\Windows\\System32\\{random.choice(['powershell.exe', 'cmd.exe'])}",
                    "command_line": f"-nop -exec bypass -file script{j}.ps1",
                    "user": random.choice(self.USERS),
                    "start_time": self._random_datetime(1),
                    "end_time": self._random_datetime(1) if random.random() > 0.5 else None,
                    "hash_sha256": uuid.uuid4().hex + uuid.uuid4().hex[:32],
                })

            trees.append({
                "tree_id": str(uuid.uuid4()),
                "detection_id": str(uuid.uuid4()),
                "asset_id": str(uuid.uuid4()),
                "root_process_id": root_pid,
                "processes": processes,
                "created_at": self._random_datetime(7),
            })
        return trees

    def generate_hunt_results(self, count: int = 10) -> list[dict[str, Any]]:
        """Generate synthetic threat hunt results."""
        hunts = []
        for i in range(count):
            hosts_scanned = random.randint(50, 500)
            hosts_matched = random.randint(0, min(10, hosts_scanned))

            matches = []
            for _ in range(hosts_matched):
                matches.append({
                    "asset_id": str(uuid.uuid4()),
                    "hostname": random.choice(self.HOSTNAMES),
                    "match_details": f"Found suspicious artifact in registry/file/memory",
                    "matched_at": self._random_datetime(3),
                })

            hunts.append({
                "hunt_id": str(uuid.uuid4()),
                "hunt_name": f"Hunt for {random.choice(self.MALWARE_FAMILIES)} indicators",
                "query": f"process.name:powershell.exe AND command_line:*-encoded*",
                "status": random.choice(["completed", "completed", "running", "failed"]),
                "started_by": random.choice(self.USERS),
                "started_at": self._random_datetime(7),
                "completed_at": self._random_datetime(3),
                "total_hosts_scanned": hosts_scanned,
                "hosts_with_matches": hosts_matched,
                "matches": matches,
                "created_at": self._random_datetime(7),
            })
        return hunts

    def generate_host_actions(self, count: int = 50) -> list[dict[str, Any]]:
        """Generate synthetic host action data."""
        actions = []
        for _ in range(count):
            action_type = random.choice(["isolate", "unisolate", "scan", "collect", "kill_process", "quarantine"])
            status = random.choice(["completed", "completed", "pending", "in_progress", "failed"])

            actions.append({
                "action_id": str(uuid.uuid4()),
                "asset_id": str(uuid.uuid4()),
                "hostname": random.choice(self.HOSTNAMES),
                "action_type": action_type,
                "status": status,
                "initiated_by": random.choice(self.USERS + ["soc-agent"]),
                "reason": f"Automated response to detection",
                "detection_id": str(uuid.uuid4()) if random.random() > 0.3 else None,
                "parameters": {"force": True, "timeout": 300},
                "result": {"success": status == "completed", "message": "Action completed"} if status == "completed" else None,
                "started_at": self._random_datetime(3),
                "completed_at": self._random_datetime(1) if status == "completed" else None,
                "created_at": self._random_datetime(3),
            })
        return actions

    def generate_siem_incidents(self, count: int = 50) -> list[dict[str, Any]]:
        """Generate synthetic SIEM incident data."""
        incidents = []
        # Use timestamp to ensure unique IDs across multiple generations
        batch_ts = int(datetime.now().timestamp() * 1000)
        for i in range(count):
            severity = random.choice(["critical", "high", "medium", "low"])
            status = random.choice(["new", "triaging", "investigating", "contained", "resolved", "closed"])

            incidents.append({
                "incident_id": f"INC-{datetime.now().year}-{batch_ts}-{i+1:04d}",
                "title": f"{random.choice(['Suspicious', 'Malicious', 'Anomalous'])} {random.choice(['PowerShell', 'Network', 'Login', 'File'])} activity detected",
                "description": "Multiple related alerts correlated into single incident for investigation",
                "severity": severity,
                "status": status,
                "priority": "P1" if severity == "critical" else "P2" if severity == "high" else "P3",
                "category": random.choice(["malware", "intrusion", "data_exfil", "insider_threat", "policy_violation"]),
                "source": random.choice(["EDR", "SIEM", "NDR", "User Report", "Threat Intel"]),
                "assigned_to": random.choice(self.USERS) if status not in ["new"] else None,
                "detection_ids": [str(uuid.uuid4()) for _ in range(random.randint(1, 5))],
                "asset_ids": [str(uuid.uuid4()) for _ in range(random.randint(1, 3))],
                "entity_ids": [str(uuid.uuid4()) for _ in range(random.randint(1, 4))],
                "tags": random.sample(["apt", "ransomware", "phishing", "lateral_movement", "persistence"], k=random.randint(0, 3)),
                "ttd_minutes": random.randint(5, 120) if status != "new" else None,
                "ttr_minutes": random.randint(30, 480) if status in ["resolved", "closed"] else None,
                "created_at": self._random_datetime(14),
                "updated_at": self._random_datetime(3),
                "resolved_at": self._random_datetime(1) if status in ["resolved", "closed"] else None,
                "closed_at": self._random_datetime(1) if status == "closed" else None,
            })
        return incidents

    def generate_siem_entities(self, count: int = 100) -> list[dict[str, Any]]:
        """Generate synthetic SIEM entity data."""
        entities = []
        entity_types = ["user", "host", "ip", "domain", "file_hash", "url"]

        for _ in range(count):
            entity_type = random.choice(entity_types)

            if entity_type == "user":
                value = random.choice(self.USERS)
            elif entity_type == "host":
                value = random.choice(self.HOSTNAMES)
            elif entity_type == "ip":
                value = self._generate_ip()
            elif entity_type == "domain":
                value = f"{uuid.uuid4().hex[:8]}.{random.choice(['com', 'net', 'org', 'io'])}"
            elif entity_type == "file_hash":
                value = uuid.uuid4().hex + uuid.uuid4().hex[:32]
            else:
                value = f"https://{uuid.uuid4().hex[:8]}.com/path"

            entities.append({
                "entity_id": str(uuid.uuid4()),
                "entity_type": entity_type,
                "entity_value": value,
                "risk_score": round(random.uniform(0, 100), 1),
                "first_seen": self._random_datetime(90),
                "last_seen": self._random_datetime(7),
                "incident_ids": [f"INC-2024-{random.randint(1, 50):04d}" for _ in range(random.randint(0, 3))],
                "detection_ids": [str(uuid.uuid4()) for _ in range(random.randint(0, 5))],
                "tags": random.sample(["suspicious", "known_bad", "under_investigation", "cleared"], k=random.randint(0, 2)),
                "enrichment": {"geo": "US", "asn": f"AS{random.randint(1000, 9999)}"} if entity_type == "ip" else {},
                "created_at": self._random_datetime(90),
                "updated_at": self._random_datetime(3),
            })
        return entities

    def generate_siem_comments(self, count: int = 200) -> list[dict[str, Any]]:
        """Generate synthetic SIEM comment data."""
        comments = []
        comment_templates = [
            "Initial triage completed. Escalating for further analysis.",
            "Confirmed malicious activity. Initiating containment.",
            "False positive. Closing ticket.",
            "Contacted asset owner for verification.",
            "Running memory analysis on affected host.",
            "IOCs extracted and shared with threat intel team.",
            "Containment actions completed. Monitoring for re-infection.",
            "Root cause identified: phishing email from external sender.",
        ]

        for _ in range(count):
            comments.append({
                "comment_id": str(uuid.uuid4()),
                "incident_id": f"INC-2024-{random.randint(1, 50):04d}",
                "author": random.choice(self.USERS + ["soc-agent"]),
                "author_type": "agent" if random.random() > 0.7 else "human",
                "content": random.choice(comment_templates),
                "attachments": [],
                "created_at": self._random_datetime(14),
                "updated_at": self._random_datetime(7),
            })
        return comments

    def generate_ctem_findings(self, count: int = 150) -> list[dict[str, Any]]:
        """Generate synthetic CTEM vulnerability findings."""
        findings = []
        for _ in range(count):
            cve = random.choice(self.CVE_LIST)

            findings.append({
                "finding_id": str(uuid.uuid4()),
                "asset_id": str(uuid.uuid4()),
                "hostname": random.choice(self.HOSTNAMES),
                "finding_type": random.choice(["vulnerability", "misconfiguration", "exposure"]),
                "cve_id": cve[0],
                "cvss_score": cve[1],
                "severity": "critical" if cve[1] >= 9.0 else "high" if cve[1] >= 7.0 else "medium" if cve[1] >= 4.0 else "low",
                "title": cve[2],
                "description": f"Vulnerability found: {cve[2]}. Immediate patching recommended.",
                "remediation": "Apply vendor security patch or implement compensating controls.",
                "status": random.choice(["open", "open", "in_progress", "remediated", "accepted"]),
                "exploitable": random.random() > 0.5,
                "exploit_available": random.random() > 0.7,
                "discovered_at": self._random_datetime(30),
                "remediated_at": self._random_datetime(7) if random.random() > 0.6 else None,
                "created_at": self._random_datetime(30),
                "updated_at": self._random_datetime(7),
            })
        return findings

    def generate_ctem_asset_risk(self, count: int = 50) -> list[dict[str, Any]]:
        """Generate synthetic CTEM asset risk scores."""
        risks = []
        for hostname in self.HOSTNAMES[:count]:
            vuln_counts = {
                "critical": random.randint(0, 5),
                "high": random.randint(0, 10),
                "medium": random.randint(0, 20),
                "low": random.randint(0, 30),
            }
            total_vulns = sum(vuln_counts.values())
            risk_score = min(100, vuln_counts["critical"] * 25 + vuln_counts["high"] * 10 + vuln_counts["medium"] * 3 + vuln_counts["low"])

            risks.append({
                "risk_id": str(uuid.uuid4()),
                "asset_id": str(uuid.uuid4()),
                "hostname": hostname,
                "risk_score": float(risk_score),
                "risk_level": "critical" if risk_score >= 80 else "high" if risk_score >= 60 else "medium" if risk_score >= 30 else "low",
                "vulnerability_count": total_vulns,
                "critical_count": vuln_counts["critical"],
                "high_count": vuln_counts["high"],
                "medium_count": vuln_counts["medium"],
                "low_count": vuln_counts["low"],
                "exposure_score": round(random.uniform(0, 100), 1),
                "attack_surface_score": round(random.uniform(0, 100), 1),
                "compliance_score": round(random.uniform(50, 100), 1),
                "calculated_at": self._random_datetime(1),
                "created_at": self._random_datetime(30),
            })
        return risks

    def generate_threat_intel(self, count: int = 200) -> list[dict[str, Any]]:
        """Generate synthetic threat intelligence indicators."""
        intel = []
        indicator_types = ["ip", "domain", "hash_sha256", "url", "email"]

        for _ in range(count):
            ind_type = random.choice(indicator_types)

            if ind_type == "ip":
                value = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            elif ind_type == "domain":
                value = f"{uuid.uuid4().hex[:10]}.{random.choice(['com', 'net', 'ru', 'cn', 'xyz'])}"
            elif ind_type == "hash_sha256":
                value = uuid.uuid4().hex + uuid.uuid4().hex[:32]
            elif ind_type == "url":
                value = f"http://{uuid.uuid4().hex[:8]}.com/{uuid.uuid4().hex[:8]}"
            else:
                value = f"{uuid.uuid4().hex[:8]}@{uuid.uuid4().hex[:6]}.com"

            intel.append({
                "intel_id": str(uuid.uuid4()),
                "indicator_type": ind_type,
                "indicator_value": value,
                "threat_type": random.choice(self.THREAT_TYPES),
                "malware_family": random.choice(self.MALWARE_FAMILIES) if random.random() > 0.5 else None,
                "confidence": round(random.uniform(0.5, 1.0), 2),
                "severity": random.choice(["critical", "high", "medium", "low"]),
                "source": random.choice(["OSINT", "Commercial Feed", "Internal", "ISAC", "Government"]),
                "description": f"Known malicious {ind_type} associated with threat activity",
                "tags": random.sample(["apt", "crimeware", "c2", "phishing", "malware"], k=random.randint(1, 3)),
                "ttl_days": random.choice([7, 30, 90, 365]),
                "first_seen": self._random_datetime(180),
                "last_seen": self._random_datetime(30),
                "expires_at": (self.now + timedelta(days=random.randint(7, 365))).isoformat() + "Z",
                "created_at": self._random_datetime(180),
            })
        return intel

    def generate_collab_messages(self, count: int = 100) -> list[dict[str, Any]]:
        """Generate synthetic collaboration messages."""
        messages = []
        channels = ["#soc-alerts", "#incident-response", "#threat-intel", "#general"]
        message_templates = [
            "New critical alert on {host}. Anyone available to investigate?",
            "Confirmed containment complete for INC-2024-{num}.",
            "Sharing IOCs from recent investigation: {hash}",
            "Need approval for host isolation on {host}.",
            "Threat hunt complete. Found {n} suspicious hosts.",
            "Escalating to Tier 2 for malware analysis.",
            "All clear on {host}. Resuming normal operations.",
        ]

        for _ in range(count):
            msg = random.choice(message_templates).format(
                host=random.choice(self.HOSTNAMES),
                num=random.randint(1, 50),
                hash=uuid.uuid4().hex[:16],
                n=random.randint(0, 10),
            )

            messages.append({
                "message_id": str(uuid.uuid4()),
                "channel": random.choice(channels),
                "channel_id": str(uuid.uuid4()),
                "thread_id": str(uuid.uuid4()) if random.random() > 0.7 else None,
                "author": random.choice(self.USERS + ["soc-agent"]),
                "author_type": "agent" if "agent" in msg.lower() or random.random() > 0.8 else "human",
                "content": msg,
                "mentions": random.sample(self.USERS, k=random.randint(0, 2)),
                "incident_ids": [f"INC-2024-{random.randint(1, 50):04d}"] if random.random() > 0.5 else [],
                "attachments": [],
                "reactions": {"thumbsup": random.randint(0, 5)} if random.random() > 0.7 else {},
                "created_at": self._random_datetime(7),
                "updated_at": self._random_datetime(3),
            })
        return messages

    def generate_approvals(self, count: int = 30) -> list[dict[str, Any]]:
        """Generate synthetic approval requests."""
        approvals = []
        request_types = ["host_isolation", "account_disable", "firewall_block", "malware_quarantine"]

        for _ in range(count):
            status = random.choice(["pending", "approved", "denied", "expired"])

            approvals.append({
                "approval_id": str(uuid.uuid4()),
                "request_type": random.choice(request_types),
                "requestor": random.choice(self.USERS + ["soc-agent"]),
                "approvers": random.sample(self.USERS, k=random.randint(1, 3)),
                "status": status,
                "incident_id": f"INC-2024-{random.randint(1, 50):04d}",
                "asset_id": str(uuid.uuid4()),
                "action_type": random.choice(["isolate", "disable", "block", "quarantine"]),
                "reason": "Automated response to high-confidence threat detection",
                "decision": status if status in ["approved", "denied"] else None,
                "decided_by": random.choice(self.USERS) if status in ["approved", "denied"] else None,
                "decision_reason": "Approved based on threat severity" if status == "approved" else "Insufficient evidence" if status == "denied" else None,
                "requested_at": self._random_datetime(7),
                "decided_at": self._random_datetime(3) if status in ["approved", "denied"] else None,
                "expires_at": (self.now + timedelta(hours=random.randint(1, 24))).isoformat() + "Z",
                "created_at": self._random_datetime(7),
            })
        return approvals

    def generate_soar_actions(self, count: int = 80) -> list[dict[str, Any]]:
        """Generate synthetic SOAR playbook action data."""
        actions = []
        playbooks = [
            ("pb-001", "Malware Containment"),
            ("pb-002", "Phishing Response"),
            ("pb-003", "Ransomware IR"),
            ("pb-004", "Account Compromise"),
            ("pb-005", "Data Exfiltration"),
        ]
        action_types = ["enrich", "contain", "notify", "ticket", "scan", "block"]

        for _ in range(count):
            playbook = random.choice(playbooks)
            status = random.choice(["completed", "completed", "running", "failed", "skipped"])

            actions.append({
                "action_id": str(uuid.uuid4()),
                "playbook_id": playbook[0],
                "playbook_name": playbook[1],
                "action_type": random.choice(action_types),
                "status": status,
                "incident_id": f"INC-2024-{random.randint(1, 50):04d}",
                "detection_id": str(uuid.uuid4()),
                "asset_id": str(uuid.uuid4()),
                "input_params": {"target": random.choice(self.HOSTNAMES), "force": True},
                "output_result": {"success": True, "data": {}} if status == "completed" else None,
                "error_message": "Connection timeout" if status == "failed" else None,
                "triggered_by": random.choice(["automation", "manual"]),
                "started_at": self._random_datetime(7),
                "completed_at": self._random_datetime(3) if status in ["completed", "failed"] else None,
                "created_at": self._random_datetime(7),
            })
        return actions

    def generate_tickets_sync(self, count: int = 40) -> list[dict[str, Any]]:
        """Generate synthetic ticket synchronization data."""
        tickets = []
        systems = ["jira", "servicenow", "zendesk"]

        for i in range(count):
            system = random.choice(systems)
            status = random.choice(["synced", "synced", "pending", "error"])

            tickets.append({
                "sync_id": str(uuid.uuid4()),
                "ticket_system": system,
                "ticket_id": str(random.randint(10000, 99999)),
                "ticket_key": f"{'JIRA' if system == 'jira' else 'INC'}-{random.randint(1000, 9999)}",
                "incident_id": f"INC-2024-{random.randint(1, 50):04d}",
                "status": status,
                "ticket_status": random.choice(["open", "in_progress", "resolved", "closed"]),
                "sync_direction": random.choice(["bidirectional", "push", "pull"]),
                "last_sync_at": self._random_datetime(1),
                "error_message": "API rate limit exceeded" if status == "error" else None,
                "created_at": self._random_datetime(14),
                "updated_at": self._random_datetime(1),
            })
        return tickets

    def generate_agent_events(self, count: int = 500) -> list[dict[str, Any]]:
        """Generate synthetic AI agent event logs."""
        events = []
        event_types = ["analysis", "decision", "action", "recommendation", "escalation"]
        action_names = ["triage_alert", "enrich_entity", "contain_host", "create_ticket", "notify_analyst", "run_playbook"]

        for _ in range(count):
            event_type = random.choice(event_types)
            status = random.choice(["completed", "completed", "completed", "failed", "pending"])

            events.append({
                "event_id": str(uuid.uuid4()),
                "agent_id": "soc-agent-001",
                "event_type": event_type,
                "action": random.choice(action_names),
                "status": status,
                "incident_id": f"INC-2024-{random.randint(1, 50):04d}" if random.random() > 0.3 else None,
                "detection_id": str(uuid.uuid4()) if random.random() > 0.3 else None,
                "asset_id": str(uuid.uuid4()) if random.random() > 0.5 else None,
                "input_summary": "Received alert for analysis",
                "output_summary": "Determined severity and recommended containment" if status == "completed" else None,
                "reasoning": "High confidence malware detection on critical asset. Automated containment triggered.",
                "confidence": round(random.uniform(0.7, 1.0), 2),
                "duration_ms": random.randint(100, 5000),
                "tokens_used": random.randint(500, 4000),
                "error_message": "Model timeout" if status == "failed" else None,
                "created_at": self._random_datetime(7),
            })
        return events

    def generate_postmortems(self, count: int = 10) -> list[dict[str, Any]]:
        """Generate synthetic incident postmortem data."""
        postmortems = []

        for i in range(count):
            timeline = []
            for j in range(random.randint(3, 8)):
                timeline.append({
                    "timestamp": self._random_datetime(14),
                    "event": random.choice([
                        "Initial alert triggered",
                        "Analyst began investigation",
                        "Malware sample collected",
                        "Containment initiated",
                        "Root cause identified",
                        "Remediation completed",
                        "Systems restored",
                    ]),
                    "actor": random.choice(self.USERS + ["soc-agent", "automation"]),
                })

            action_items = []
            for k in range(random.randint(2, 5)):
                action_items.append({
                    "item_id": str(uuid.uuid4()),
                    "description": random.choice([
                        "Implement additional email filtering rules",
                        "Update EDR detection signatures",
                        "Conduct security awareness training",
                        "Review and update incident response playbook",
                        "Deploy additional network monitoring",
                    ]),
                    "owner": random.choice(self.USERS),
                    "due_date": (self.now + timedelta(days=random.randint(7, 30))).isoformat() + "Z",
                    "status": random.choice(["open", "in_progress", "completed"]),
                })

            postmortems.append({
                "postmortem_id": str(uuid.uuid4()),
                "incident_id": f"INC-2024-{i+1:04d}",
                "title": f"Post-Incident Review: {random.choice(['Ransomware', 'Phishing', 'Malware', 'Data Breach'])} Incident",
                "summary": "Comprehensive review of incident response and lessons learned.",
                "impact": f"Affected {random.randint(1, 50)} systems. Estimated downtime: {random.randint(1, 48)} hours.",
                "root_cause": random.choice([
                    "Phishing email bypassed email security controls",
                    "Unpatched vulnerability exploited",
                    "Compromised credentials from third-party breach",
                    "Insider threat - malicious employee action",
                ]),
                "timeline": timeline,
                "lessons_learned": "Need to improve detection capabilities and reduce response time.",
                "action_items": action_items,
                "participants": random.sample(self.USERS, k=random.randint(3, 6)),
                "status": random.choice(["draft", "in_review", "published"]),
                "created_by": random.choice(self.USERS),
                "created_at": self._random_datetime(30),
                "updated_at": self._random_datetime(7),
                "published_at": self._random_datetime(3) if random.random() > 0.5 else None,
            })
        return postmortems


@router.post("/reset", response_model=ResetResponse)
async def reset_indices() -> ResetResponse:
    """
    Delete all indices and recreate them with templates.
    WARNING: This will delete all existing data!
    """
    try:
        client = await OpenSearchClient.create()
        results = await client.reset_all_indices()

        return ResetResponse(
            status="success",
            deleted=results["deleted"],
            created=results["created"],
        )
    except Exception as e:
        logger.error(f"Error resetting indices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/all", response_model=GenerateResponse)
async def generate_all_data() -> GenerateResponse:
    """
    Generate synthetic data for all indices.
    This populates the entire demo environment with realistic data.
    """
    try:
        client = await OpenSearchClient.create()
        generator = SyntheticDataGenerator()
        counts: dict[str, int] = {}

        # Generate and index data for each index
        data_generators = [
            ("assets-inventory-v1", generator.generate_assets(50), "asset_id"),
            ("edr-detections-v1", generator.generate_edr_detections(100), "detection_id"),
            ("edr-process-trees-v1", generator.generate_process_trees(30), "tree_id"),
            ("edr-hunt-results-v1", generator.generate_hunt_results(10), "hunt_id"),
            ("edr-host-actions-v1", generator.generate_host_actions(50), "action_id"),
            ("siem-incidents-v1", generator.generate_siem_incidents(50), "incident_id"),
            ("siem-entities-v1", generator.generate_siem_entities(100), "entity_id"),
            ("siem-comments-v1", generator.generate_siem_comments(200), "comment_id"),
            ("ctem-findings-v1", generator.generate_ctem_findings(150), "finding_id"),
            ("ctem-asset-risk-v1", generator.generate_ctem_asset_risk(50), "risk_id"),
            ("threat-intel-v1", generator.generate_threat_intel(200), "intel_id"),
            ("collab-messages-v1", generator.generate_collab_messages(100), "message_id"),
            ("approvals-v1", generator.generate_approvals(30), "approval_id"),
            ("soar-actions-v1", generator.generate_soar_actions(80), "action_id"),
            ("tickets-sync-v1", generator.generate_tickets_sync(40), "sync_id"),
            ("agent-events-v1", generator.generate_agent_events(500), "event_id"),
            ("postmortems-v1", generator.generate_postmortems(10), "postmortem_id"),
        ]

        for index_name, documents, id_field in data_generators:
            # Ensure index exists
            await client.create_index(index_name)

            # Bulk index documents
            result = await client.bulk_index(index_name, documents, id_field=id_field)
            counts[index_name] = result.get("indexed", 0)

            if not result.get("success"):
                logger.warning(f"Errors indexing {index_name}: {result.get('errors')}")

        return GenerateResponse(status="success", counts=counts)

    except Exception as e:
        logger.error(f"Error generating data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assets", response_model=GenerateResponse)
async def generate_assets_only() -> GenerateResponse:
    """Generate synthetic asset inventory data only."""
    try:
        client = await OpenSearchClient.create()
        generator = SyntheticDataGenerator()

        # Ensure index exists
        await client.create_index("assets-inventory-v1")

        # Generate and index assets
        documents = generator.generate_assets(50)
        result = await client.bulk_index("assets-inventory-v1", documents, id_field="asset_id")

        return GenerateResponse(
            status="success",
            counts={"assets-inventory-v1": result.get("indexed", 0)},
        )
    except Exception as e:
        logger.error(f"Error generating assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/edr", response_model=GenerateResponse)
async def generate_edr_only(count: int = 100) -> GenerateResponse:
    """Generate synthetic EDR detection data only."""
    try:
        client = await OpenSearchClient.create()
        generator = SyntheticDataGenerator()

        # Ensure index exists
        await client.create_index("edr-detections-v1")

        # Generate and index EDR detections
        documents = generator.generate_edr_detections(count)
        result = await client.bulk_index("edr-detections-v1", documents, id_field="detection_id")

        return GenerateResponse(
            status="success",
            counts={"edr-detections-v1": result.get("indexed", 0)},
        )
    except Exception as e:
        logger.error(f"Error generating EDR detections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/incidents", response_model=GenerateResponse)
async def generate_incidents_only(count: int = 50) -> GenerateResponse:
    """Generate synthetic SIEM incident data only."""
    try:
        client = await OpenSearchClient.create()
        generator = SyntheticDataGenerator()

        # Ensure index exists
        await client.create_index("siem-incidents-v1")

        # Generate and index incidents
        documents = generator.generate_siem_incidents(count)
        result = await client.bulk_index("siem-incidents-v1", documents, id_field="incident_id")

        return GenerateResponse(
            status="success",
            counts={"siem-incidents-v1": result.get("indexed", 0)},
        )
    except Exception as e:
        logger.error(f"Error generating incidents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/postmortems", response_model=GenerateResponse)
async def generate_postmortems_only(count: int = 10) -> GenerateResponse:
    """Generate synthetic postmortem data only."""
    try:
        client = await OpenSearchClient.create()
        generator = SyntheticDataGenerator()

        # Ensure index exists
        await client.create_index("postmortems-v1")

        # Generate and index postmortems
        documents = generator.generate_postmortems(count)
        result = await client.bulk_index("postmortems-v1", documents, id_field="postmortem_id")

        return GenerateResponse(
            status="success",
            counts={"postmortems-v1": result.get("indexed", 0)},
        )
    except Exception as e:
        logger.error(f"Error generating postmortems: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tickets", response_model=GenerateResponse)
async def generate_tickets_only(count: int = 40) -> GenerateResponse:
    """Generate synthetic tickets sync data only."""
    try:
        client = await OpenSearchClient.create()
        generator = SyntheticDataGenerator()

        # Ensure index exists
        await client.create_index("tickets-sync-v1")

        # Generate and index tickets
        documents = generator.generate_tickets_sync(count)
        result = await client.bulk_index("tickets-sync-v1", documents, id_field="sync_id")

        return GenerateResponse(
            status="success",
            counts={"tickets-sync-v1": result.get("indexed", 0)},
        )
    except Exception as e:
        logger.error(f"Error generating tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent-actions", response_model=GenerateResponse)
async def generate_agent_actions_only(count: int = 500) -> GenerateResponse:
    """Generate synthetic agent events data only."""
    try:
        client = await OpenSearchClient.create()
        generator = SyntheticDataGenerator()

        # Ensure index exists
        await client.create_index("agent-events-v1")

        # Generate and index agent events
        documents = generator.generate_agent_events(count)
        result = await client.bulk_index("agent-events-v1", documents, id_field="event_id")

        return GenerateResponse(
            status="success",
            counts={"agent-events-v1": result.get("indexed", 0)},
        )
    except Exception as e:
        logger.error(f"Error generating agent actions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=GenerationStatusResponse)
async def generation_status() -> GenerationStatusResponse:
    """
    Get document counts for the main data types.
    Used by the frontend to display current data status.
    """
    try:
        client = await OpenSearchClient.create()
        counts = await client.get_all_counts()

        return GenerationStatusResponse(
            assets=counts.get("assets-inventory-v1", 0),
            incidents=counts.get("siem-incidents-v1", 0),
            detections=counts.get("edr-detections-v1", 0),
            postmortems=counts.get("postmortems-v1", 0),
            tickets=counts.get("tickets-sync-v1", 0),
            agent_actions=counts.get("agent-events-v1", 0),
        )
    except Exception as e:
        logger.error(f"Error getting generation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def generation_health() -> HealthResponse:
    """
    Get document counts for all indices.
    Useful for verifying data generation status.
    """
    try:
        client = await OpenSearchClient.create()
        counts = await client.get_all_counts()
        total = sum(counts.values())

        return HealthResponse(
            status="healthy",
            indices=counts,
            total_documents=total,
        )
    except Exception as e:
        logger.error(f"Error getting generation health: {e}")
        raise HTTPException(status_code=500, detail=str(e))
