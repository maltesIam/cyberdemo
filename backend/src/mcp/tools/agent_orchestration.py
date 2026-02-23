"""
Agent Orchestration MCP Tools.

Tools for agent orchestration that allow the product to invoke
agent analysis capabilities:
- agent_analyze_alert: Analyze a security alert (REQ-001-003-001)
- agent_investigate_ioc: Investigate an indicator of compromise (REQ-001-003-002)
- agent_recommend_action: Get action recommendations (REQ-001-003-003)
- agent_generate_report: Generate an incident report (REQ-001-003-004)
- agent_explain_decision: Get the reasoning chain for a decision (REQ-001-003-005)
- agent_correlate_events: Correlate multiple events to identify patterns (REQ-001-003-006)

These tools enable the product to request analysis, recommendations, and reports
from the AI agent, supporting transparency and investigation workflows.
"""

from typing import Any, Dict, List
from datetime import datetime


# =============================================================================
# Tool Definitions
# =============================================================================

AGENT_ORCHESTRATION_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "agent_analyze_alert",
        "description": """Analyze a security alert and provide detailed assessment.

Returns analysis including severity assessment, threat intelligence,
MITRE ATT&CK mapping, and recommended actions. This enables automated
alert triage and provides context for investigation.

Use this when an alert needs to be analyzed for threat assessment.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "alert_id": {
                    "type": "string",
                    "description": "The unique identifier of the alert to analyze (e.g., ALERT-001)"
                }
            },
            "required": ["alert_id"]
        }
    },
    {
        "name": "agent_investigate_ioc",
        "description": """Investigate an indicator of compromise (IOC).

Returns reputation data, geographic information, related indicators,
and threat intelligence for the specified IOC. Supports IP addresses,
domains, file hashes, and URLs.

Use this to enrich and assess the threat level of an IOC.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ioc": {
                    "type": "string",
                    "description": "The indicator value (IP, domain, hash, or URL)"
                },
                "type": {
                    "type": "string",
                    "enum": ["ip", "domain", "hash", "url"],
                    "description": "The type of indicator"
                }
            },
            "required": ["ioc", "type"]
        }
    },
    {
        "name": "agent_recommend_action",
        "description": """Get action recommendations based on incident context.

Returns prioritized recommendations with reasoning, risk assessment,
and expected outcomes. Helps analysts decide on appropriate response
actions based on the current threat context.

Use this when you need guidance on what actions to take.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "context": {
                    "type": "object",
                    "description": "Context information including incident_id, severity, threat_type, asset_type"
                }
            },
            "required": ["context"]
        }
    },
    {
        "name": "agent_generate_report",
        "description": """Generate a comprehensive incident report.

Creates a report including executive summary, timeline, IOCs,
affected assets, and recommendations. Supports JSON and Markdown formats.

Use this to document an incident for stakeholders or compliance.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "incident_id": {
                    "type": "string",
                    "description": "The unique identifier of the incident (e.g., INC-001)"
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "markdown", "pdf"],
                    "default": "json",
                    "description": "The output format for the report"
                }
            },
            "required": ["incident_id"]
        }
    },
    {
        "name": "agent_explain_decision",
        "description": """Get detailed explanation of a decision made by the AI agent.

Returns the reasoning chain, confidence level, factors that influenced
the decision, and alternative actions that were considered. This enables
transparency and auditability of AI-driven security decisions.

Use this to understand WHY the agent made a specific recommendation or action.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "decision_id": {
                    "type": "string",
                    "description": "The unique identifier of the decision to explain (e.g., DEC-001)"
                }
            },
            "required": ["decision_id"]
        }
    },
    {
        "name": "agent_correlate_events",
        "description": """Correlate multiple security events to identify patterns and relationships.

Analyzes a list of events to find common entities, build a timeline,
identify potential attack patterns mapped to MITRE ATT&CK, and provide
investigation recommendations.

Use this when you need to understand how multiple events are related.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of event IDs to correlate (e.g., ['EVT-001', 'EVT-002'])"
                }
            },
            "required": ["event_ids"]
        }
    },
]


# =============================================================================
# Mock Alert Data Store
# =============================================================================

MOCK_ALERTS: Dict[str, Dict[str, Any]] = {
    "ALERT-001": {
        "alert_id": "ALERT-001",
        "title": "PowerShell Encoded Command Execution",
        "description": "Suspicious PowerShell activity detected with encoded payload",
        "severity": "critical",
        "source": "EDR",
        "host": "WS-FIN-042",
        "user": "DOMAIN\\finance_user",
        "timestamp": "2026-02-14T10:30:00Z",
        "raw_data": {
            "process": "powershell.exe",
            "command_line": "powershell -enc SGVsbG8gV29ybGQ=",
            "parent_process": "explorer.exe"
        }
    },
    "ALERT-002": {
        "alert_id": "ALERT-002",
        "title": "Suspicious Network Connection to Known C2",
        "description": "Outbound connection to IP flagged in threat intelligence",
        "severity": "high",
        "source": "NDR",
        "host": "WS-FIN-042",
        "user": "DOMAIN\\finance_user",
        "timestamp": "2026-02-14T10:31:15Z",
        "raw_data": {
            "dest_ip": "185.234.72.199",
            "dest_port": 443,
            "bytes_sent": 1524
        }
    },
    "ALERT-003": {
        "alert_id": "ALERT-003",
        "title": "Ransomware Behavior Detected",
        "description": "File encryption activity detected on multiple files",
        "severity": "critical",
        "source": "EDR",
        "host": "WS-HR-015",
        "user": "DOMAIN\\hr_user",
        "timestamp": "2026-02-14T11:00:00Z",
        "raw_data": {
            "files_encrypted": 150,
            "extension_added": ".locked",
            "ransom_note": "C:\\Users\\hr_user\\Desktop\\README_DECRYPT.txt"
        }
    }
}


# =============================================================================
# Mock IOC Data Store
# =============================================================================

MOCK_IOCS: Dict[str, Dict[str, Any]] = {
    "ip:185.234.72.199": {
        "ioc": "185.234.72.199",
        "type": "ip",
        "reputation": "malicious",
        "threat_score": 95,
        "first_seen": "2025-06-15T00:00:00Z",
        "last_seen": "2026-02-14T10:31:15Z",
        "geo_info": {
            "country": "Russia",
            "country_code": "RU",
            "city": "Moscow",
            "asn": "AS12345",
            "org": "Evil Corp Hosting"
        },
        "threat_intel": {
            "apt_group": "APT29",
            "malware_family": "SUNBURST",
            "campaigns": ["SolarWinds Breach"]
        },
        "related_indicators": [
            {"type": "domain", "value": "solarwinds-update.evil.com"},
            {"type": "hash", "value": "abc123def456789abcdef123456789ab"}
        ]
    },
    "domain:malware-c2.evil.com": {
        "ioc": "malware-c2.evil.com",
        "type": "domain",
        "reputation": "malicious",
        "threat_score": 90,
        "first_seen": "2025-08-01T00:00:00Z",
        "last_seen": "2026-02-14T09:00:00Z",
        "geo_info": {
            "country": "Unknown",
            "hosting_country": "Netherlands"
        },
        "threat_intel": {
            "apt_group": "FIN7",
            "malware_family": "Carbanak"
        },
        "related_indicators": [
            {"type": "ip", "value": "185.234.72.200"},
            {"type": "ip", "value": "185.234.72.201"}
        ]
    },
    "hash:abc123def456789abcdef123456789ab": {
        "ioc": "abc123def456789abcdef123456789ab",
        "type": "hash",
        "reputation": "malicious",
        "threat_score": 98,
        "first_seen": "2026-01-15T00:00:00Z",
        "last_seen": "2026-02-14T10:32:00Z",
        "file_info": {
            "file_name": "update.ps1",
            "file_type": "PowerShell Script",
            "file_size": 4096
        },
        "threat_intel": {
            "malware_family": "SUNBURST",
            "detection_names": ["Trojan.SUNBURST", "Backdoor.APT29"]
        },
        "related_indicators": [
            {"type": "ip", "value": "185.234.72.199"},
            {"type": "domain", "value": "solarwinds-update.evil.com"}
        ],
        "geo_info": {}
    }
}


# =============================================================================
# Mock Incident Data Store
# =============================================================================

MOCK_INCIDENTS: Dict[str, Dict[str, Any]] = {
    "INC-001": {
        "incident_id": "INC-001",
        "title": "APT29 Intrusion via Supply Chain",
        "description": "Multi-stage attack detected involving PowerShell execution, C2 communication, and data collection",
        "severity": "critical",
        "status": "investigating",
        "created_at": "2026-02-14T10:30:00Z",
        "updated_at": "2026-02-14T12:00:00Z",
        "affected_assets": ["WS-FIN-042"],
        "timeline": [
            {"timestamp": "2026-02-14T10:30:00Z", "event": "PowerShell encoded command executed", "event_id": "EVT-001"},
            {"timestamp": "2026-02-14T10:31:15Z", "event": "C2 connection established", "event_id": "EVT-002"},
            {"timestamp": "2026-02-14T10:32:00Z", "event": "Malicious script dropped", "event_id": "EVT-003"},
            {"timestamp": "2026-02-14T10:33:30Z", "event": "Persistence mechanism installed", "event_id": "EVT-004"},
            {"timestamp": "2026-02-14T10:35:00Z", "event": "Sensitive data accessed", "event_id": "EVT-005"}
        ],
        "indicators_of_compromise": [
            {"type": "ip", "value": "185.234.72.199", "context": "C2 server"},
            {"type": "hash", "value": "abc123def456789abcdef123456789ab", "context": "Malicious script"},
            {"type": "domain", "value": "solarwinds-update.evil.com", "context": "Payload delivery"}
        ],
        "mitre_mapping": [
            {"tactic_id": "TA0002", "tactic_name": "Execution", "technique_id": "T1059.001", "technique_name": "PowerShell"},
            {"tactic_id": "TA0011", "tactic_name": "Command and Control", "technique_id": "T1071.001", "technique_name": "Web Protocols"},
            {"tactic_id": "TA0003", "tactic_name": "Persistence", "technique_id": "T1547.001", "technique_name": "Registry Run Keys"},
            {"tactic_id": "TA0009", "tactic_name": "Collection", "technique_id": "T1039", "technique_name": "Data from Network Shared Drive"}
        ],
        "recommendations": [
            "Contain affected host WS-FIN-042 immediately",
            "Block C2 IP 185.234.72.199 at perimeter firewall",
            "Search for lateral movement indicators",
            "Notify data owners about potential data exposure",
            "Preserve forensic evidence for analysis"
        ]
    },
    "INC-002": {
        "incident_id": "INC-002",
        "title": "Ransomware Attack on HR Systems",
        "description": "Ransomware encryption detected on HR workstation",
        "severity": "critical",
        "status": "contained",
        "created_at": "2026-02-14T11:00:00Z",
        "updated_at": "2026-02-14T11:30:00Z",
        "affected_assets": ["WS-HR-015"],
        "timeline": [
            {"timestamp": "2026-02-14T11:00:00Z", "event": "Ransomware activity detected", "event_id": "EVT-006"},
            {"timestamp": "2026-02-14T11:05:00Z", "event": "Host isolated", "event_id": "EVT-007"}
        ],
        "indicators_of_compromise": [
            {"type": "hash", "value": "def456789abc123def456789abc123de", "context": "Ransomware binary"},
            {"type": "ip", "value": "192.168.100.50", "context": "Internal propagation source"}
        ],
        "mitre_mapping": [
            {"tactic_id": "TA0040", "tactic_name": "Impact", "technique_id": "T1486", "technique_name": "Data Encrypted for Impact"}
        ],
        "recommendations": [
            "Keep host isolated",
            "Check backups for affected files",
            "Scan other HR systems for ransomware indicators"
        ]
    }
}


# =============================================================================
# Mock Decision Data Store
# =============================================================================

MOCK_DECISIONS: Dict[str, Dict[str, Any]] = {
    "DEC-001": {
        "decision_id": "DEC-001",
        "type": "containment_recommendation",
        "incident_id": "INC-ANCHOR-001",
        "action": "contain_host",
        "target": "WS-FIN-042",
        "reasoning_chain": [
            {
                "step": 1,
                "thought": "Detected PowerShell encoded command execution",
                "evidence": "Event log shows base64 encoded payload"
            },
            {
                "step": 2,
                "thought": "Pattern matches known APT29 technique T1059.001",
                "evidence": "Encoded command structure matches threat intel signatures"
            },
            {
                "step": 3,
                "thought": "Host is in Finance network segment with access to sensitive data",
                "evidence": "Asset context shows critical business value"
            },
            {
                "step": 4,
                "thought": "Recommend immediate containment to prevent lateral movement",
                "evidence": "No legitimate business justification found for PowerShell usage"
            }
        ],
        "confidence": "high",
        "confidence_score": 0.92,
        "factors": [
            {
                "name": "threat_intel_match",
                "weight": 0.35,
                "description": "Strong correlation with known APT29 TTPs"
            },
            {
                "name": "asset_criticality",
                "weight": 0.25,
                "description": "Target is a critical finance workstation"
            },
            {
                "name": "behavior_anomaly",
                "weight": 0.25,
                "description": "PowerShell usage is anomalous for this user"
            },
            {
                "name": "network_context",
                "weight": 0.15,
                "description": "Host has network access to sensitive segments"
            }
        ],
        "alternatives_considered": [
            {
                "action": "monitor_only",
                "reason_rejected": "Risk too high given asset criticality and threat match",
                "risk_score": 0.85
            },
            {
                "action": "partial_isolation",
                "reason_rejected": "Would not prevent data exfiltration already in progress",
                "risk_score": 0.65
            }
        ],
        "decision_timestamp": "2026-02-14T10:35:00Z"
    },
    "DEC-002": {
        "decision_id": "DEC-002",
        "type": "false_positive_determination",
        "incident_id": "INC-ANCHOR-003",
        "action": "close_as_benign",
        "target": "SRV-DEV-03",
        "reasoning_chain": [
            {
                "step": 1,
                "thought": "Script execution detected on development server",
                "evidence": "PowerShell script running automated tests"
            },
            {
                "step": 2,
                "thought": "User is authorized developer with valid justification",
                "evidence": "User profile shows DevOps role with script permissions"
            },
            {
                "step": 3,
                "thought": "Script behavior matches legitimate CI/CD patterns",
                "evidence": "Execution timing aligns with scheduled build jobs"
            }
        ],
        "confidence": "high",
        "confidence_score": 0.88,
        "factors": [
            {
                "name": "user_context",
                "weight": 0.40,
                "description": "User is authorized for this type of activity"
            },
            {
                "name": "timing_pattern",
                "weight": 0.30,
                "description": "Activity matches expected CI/CD schedule"
            },
            {
                "name": "asset_context",
                "weight": 0.30,
                "description": "Development server where such activity is normal"
            }
        ],
        "alternatives_considered": [
            {
                "action": "investigate_further",
                "reason_rejected": "Evidence strongly supports legitimate use",
                "risk_score": 0.15
            }
        ],
        "decision_timestamp": "2026-02-14T09:15:00Z"
    }
}


# =============================================================================
# Mock Event Data Store
# =============================================================================

MOCK_EVENTS: Dict[str, Dict[str, Any]] = {
    "EVT-001": {
        "event_id": "EVT-001",
        "type": "process_execution",
        "timestamp": "2026-02-14T10:30:00Z",
        "host": "WS-FIN-042",
        "user": "DOMAIN\\finance_user",
        "process": "powershell.exe",
        "command_line": "powershell -enc SGVsbG8gV29ybGQ=",
        "parent_process": "explorer.exe",
        "ip_addresses": ["192.168.1.42"],
        "mitre_tactic": "TA0002",  # Execution
        "mitre_technique": "T1059.001"  # PowerShell
    },
    "EVT-002": {
        "event_id": "EVT-002",
        "type": "network_connection",
        "timestamp": "2026-02-14T10:31:15Z",
        "host": "WS-FIN-042",
        "user": "DOMAIN\\finance_user",
        "source_ip": "192.168.1.42",
        "dest_ip": "185.234.72.199",
        "dest_port": 443,
        "protocol": "HTTPS",
        "bytes_sent": 1524,
        "mitre_tactic": "TA0011",  # Command and Control
        "mitre_technique": "T1071.001"  # Application Layer Protocol: Web
    },
    "EVT-003": {
        "event_id": "EVT-003",
        "type": "file_creation",
        "timestamp": "2026-02-14T10:32:00Z",
        "host": "WS-FIN-042",
        "user": "DOMAIN\\finance_user",
        "file_path": "C:\\Users\\finance_user\\AppData\\Local\\Temp\\update.ps1",
        "file_hash": "abc123def456789",
        "ip_addresses": ["192.168.1.42"],
        "mitre_tactic": "TA0005",  # Defense Evasion
        "mitre_technique": "T1027"  # Obfuscated Files
    },
    "EVT-004": {
        "event_id": "EVT-004",
        "type": "registry_modification",
        "timestamp": "2026-02-14T10:33:30Z",
        "host": "WS-FIN-042",
        "user": "DOMAIN\\finance_user",
        "registry_key": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        "registry_value": "UpdateService",
        "ip_addresses": ["192.168.1.42"],
        "mitre_tactic": "TA0003",  # Persistence
        "mitre_technique": "T1547.001"  # Registry Run Keys
    },
    "EVT-005": {
        "event_id": "EVT-005",
        "type": "data_access",
        "timestamp": "2026-02-14T10:35:00Z",
        "host": "WS-FIN-042",
        "user": "DOMAIN\\finance_user",
        "resource": "\\\\FILESERVER\\Finance\\Q4_Reports",
        "action": "read",
        "files_accessed": 47,
        "ip_addresses": ["192.168.1.42", "192.168.1.10"],
        "mitre_tactic": "TA0009",  # Collection
        "mitre_technique": "T1039"  # Data from Network Shared Drive
    }
}


# =============================================================================
# Tool Handlers
# =============================================================================

async def handle_agent_analyze_alert(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle agent_analyze_alert tool call (REQ-001-003-001).

    Analyzes a security alert and returns detailed assessment including
    severity assessment, threat intelligence, MITRE ATT&CK mapping,
    and recommended actions.

    Args:
        args: Dictionary with alert_id

    Returns:
        Dictionary with analysis results

    Raises:
        ValueError: If alert_id is not provided
    """
    alert_id = args.get("alert_id")

    if not alert_id:
        raise ValueError("alert_id is required")

    # Look up the alert
    if alert_id not in MOCK_ALERTS:
        return {
            "status": "not_found",
            "alert_id": alert_id,
            "message": f"Alert {alert_id} not found in the system"
        }

    alert = MOCK_ALERTS[alert_id]

    # Generate analysis based on alert data
    analysis = {
        "alert_id": alert_id,
        "analysis": {
            "summary": f"Analysis of {alert['title']}",
            "threat_assessment": "This activity matches known attack patterns",
            "impact_assessment": "Potential data compromise and persistence"
        },
        "severity_assessment": {
            "original_severity": alert["severity"],
            "assessed_severity": alert["severity"],
            "factors": [
                "Matches known APT TTPs",
                "Targets critical business asset",
                "Evidence of data access"
            ]
        },
        "confidence_score": 0.89,
        "threat_intel": {
            "apt_group_match": "APT29",
            "malware_family": "SUNBURST",
            "threat_actor_confidence": "high"
        },
        "mitre_mapping": [
            {
                "tactic_id": "TA0002",
                "tactic_name": "Execution",
                "technique_id": "T1059.001",
                "technique_name": "PowerShell"
            },
            {
                "tactic_id": "TA0011",
                "tactic_name": "Command and Control",
                "technique_id": "T1071.001",
                "technique_name": "Web Protocols"
            }
        ],
        "recommendations": [
            "Isolate affected host immediately",
            "Block identified C2 IP addresses",
            "Search for lateral movement indicators",
            "Preserve forensic evidence"
        ],
        "related_alerts": ["ALERT-002"],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    return analysis


async def handle_agent_investigate_ioc(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle agent_investigate_ioc tool call (REQ-001-003-002).

    Investigates an indicator of compromise and returns reputation data,
    geographic information, related indicators, and threat intelligence.

    Args:
        args: Dictionary with ioc and type

    Returns:
        Dictionary with IOC investigation results

    Raises:
        ValueError: If ioc or type is not provided
    """
    ioc = args.get("ioc")
    ioc_type = args.get("type")

    if not ioc:
        raise ValueError("ioc is required")
    if not ioc_type:
        raise ValueError("type is required")

    # Build lookup key
    lookup_key = f"{ioc_type}:{ioc}"

    # Look up the IOC
    if lookup_key in MOCK_IOCS:
        return MOCK_IOCS[lookup_key]

    # Return generic response for unknown IOCs
    return {
        "ioc": ioc,
        "type": ioc_type,
        "reputation": "unknown",
        "threat_score": 0,
        "first_seen": None,
        "last_seen": None,
        "geo_info": {
            "country": "Unknown",
            "country_code": "XX"
        },
        "threat_intel": {},
        "related_indicators": [],
        "message": f"No threat intelligence available for this {ioc_type}"
    }


async def handle_agent_recommend_action(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle agent_recommend_action tool call (REQ-001-003-003).

    Returns prioritized action recommendations based on the incident context
    with reasoning, risk assessment, and expected outcomes.

    Args:
        args: Dictionary with context object

    Returns:
        Dictionary with action recommendations

    Raises:
        ValueError: If context is not provided
    """
    context = args.get("context")

    if not context:
        raise ValueError("context is required")

    incident_id = context.get("incident_id", "UNKNOWN")
    severity = context.get("severity", "medium")
    threat_type = context.get("threat_type", "unknown")
    asset_type = context.get("asset_type", "workstation")

    # Generate recommendations based on context
    recommendations = []

    # Ransomware-specific recommendations
    if threat_type == "ransomware":
        recommendations.extend([
            {
                "action": "Isolate affected host immediately",
                "priority": "critical",
                "reasoning": "Stop ransomware spread to other systems",
                "expected_outcome": "Contain the attack to single host",
                "requires_approval": False
            },
            {
                "action": "Disable network shares",
                "priority": "high",
                "reasoning": "Prevent encryption of shared files",
                "expected_outcome": "Protect shared data from encryption",
                "requires_approval": True
            },
            {
                "action": "Restore from backup",
                "priority": "medium",
                "reasoning": "Recover encrypted files without paying ransom",
                "expected_outcome": "Data recovery without attacker engagement",
                "requires_approval": True
            }
        ])
    # Critical severity recommendations
    elif severity == "critical":
        recommendations.extend([
            {
                "action": "Contain affected host",
                "priority": "critical",
                "reasoning": "Prevent lateral movement and data exfiltration",
                "expected_outcome": "Isolate threat to single system",
                "requires_approval": False
            },
            {
                "action": "Block identified IOCs at perimeter",
                "priority": "high",
                "reasoning": "Prevent C2 communication and additional downloads",
                "expected_outcome": "Cut off attacker access",
                "requires_approval": False
            },
            {
                "action": "Collect forensic evidence",
                "priority": "high",
                "reasoning": "Preserve evidence for investigation and legal action",
                "expected_outcome": "Complete incident timeline and attribution",
                "requires_approval": False
            }
        ])
    else:
        # Default recommendations
        recommendations.extend([
            {
                "action": "Monitor for additional indicators",
                "priority": "medium",
                "reasoning": "Gather more context before taking disruptive action",
                "expected_outcome": "Better understanding of threat scope",
                "requires_approval": False
            },
            {
                "action": "Review affected asset logs",
                "priority": "medium",
                "reasoning": "Identify timeline and scope of activity",
                "expected_outcome": "Complete activity timeline",
                "requires_approval": False
            }
        ])

    # Calculate risk
    risk_scores = {
        "critical": 95,
        "high": 75,
        "medium": 50,
        "low": 25
    }
    current_risk = risk_scores.get(severity, 50)

    return {
        "incident_id": incident_id,
        "recommendations": recommendations,
        "risk_assessment": {
            "current_risk": current_risk,
            "risk_level": severity,
            "risk_factors": [
                "Active threat indicators detected",
                f"Asset type: {asset_type}",
                f"Threat type: {threat_type}"
            ],
            "mitigated_risk_estimate": max(current_risk - 40, 10) if recommendations else current_risk
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


async def handle_agent_generate_report(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle agent_generate_report tool call (REQ-001-003-004).

    Generates a comprehensive incident report including executive summary,
    timeline, IOCs, affected assets, and recommendations.

    Args:
        args: Dictionary with incident_id and format

    Returns:
        Dictionary with report in specified format

    Raises:
        ValueError: If incident_id is not provided
    """
    incident_id = args.get("incident_id")
    report_format = args.get("format", "json")

    if not incident_id:
        raise ValueError("incident_id is required")

    # Look up the incident
    if incident_id not in MOCK_INCIDENTS:
        return {
            "status": "not_found",
            "incident_id": incident_id,
            "message": f"Incident {incident_id} not found in the system",
            "format": report_format,
            "report": {}
        }

    incident = MOCK_INCIDENTS[incident_id]

    # Build report structure
    report_data = {
        "incident_id": incident_id,
        "title": incident["title"],
        "executive_summary": f"""
This report documents {incident['title']}. The incident was classified as {incident['severity']} severity
and is currently {incident['status']}. The attack affected {len(incident['affected_assets'])} asset(s)
and involved {len(incident.get('mitre_mapping', []))} MITRE ATT&CK techniques.

Key findings indicate sophisticated threat actor activity consistent with known APT TTPs.
Immediate containment and remediation actions are recommended.
        """.strip(),
        "severity": incident["severity"],
        "status": incident["status"],
        "timeline": incident["timeline"],
        "affected_assets": incident["affected_assets"],
        "indicators_of_compromise": incident.get("indicators_of_compromise", []),
        "mitre_mapping": incident.get("mitre_mapping", []),
        "recommendations": incident.get("recommendations", []),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "report_version": "1.0"
    }

    # Convert to requested format
    if report_format == "markdown":
        markdown_report = _generate_markdown_report(report_data)
        return {
            "incident_id": incident_id,
            "format": "markdown",
            "report": markdown_report
        }
    else:
        # Default to JSON
        return {
            "incident_id": incident_id,
            "format": "json",
            "report": report_data
        }


def _generate_markdown_report(report_data: Dict[str, Any]) -> str:
    """Generate a markdown formatted incident report."""
    lines = []

    lines.append(f"# Incident Report: {report_data['incident_id']}")
    lines.append("")
    lines.append(f"## {report_data['title']}")
    lines.append("")
    lines.append(f"**Severity:** {report_data['severity'].upper()}")
    lines.append(f"**Status:** {report_data['status']}")
    lines.append(f"**Generated:** {report_data['generated_at']}")
    lines.append("")

    lines.append("## Executive Summary")
    lines.append("")
    lines.append(report_data['executive_summary'])
    lines.append("")

    lines.append("## Timeline")
    lines.append("")
    for event in report_data['timeline']:
        lines.append(f"- **{event['timestamp']}**: {event['event']}")
    lines.append("")

    lines.append("## Affected Assets")
    lines.append("")
    for asset in report_data['affected_assets']:
        lines.append(f"- {asset}")
    lines.append("")

    lines.append("## Indicators of Compromise")
    lines.append("")
    lines.append("| Type | Value | Context |")
    lines.append("|------|-------|---------|")
    for ioc in report_data['indicators_of_compromise']:
        lines.append(f"| {ioc['type']} | {ioc['value']} | {ioc.get('context', '')} |")
    lines.append("")

    lines.append("## MITRE ATT&CK Mapping")
    lines.append("")
    for mapping in report_data.get('mitre_mapping', []):
        lines.append(f"- **{mapping['tactic_name']}** ({mapping['tactic_id']}): {mapping['technique_name']} ({mapping['technique_id']})")
    lines.append("")

    lines.append("## Recommendations")
    lines.append("")
    for i, rec in enumerate(report_data['recommendations'], 1):
        lines.append(f"{i}. {rec}")
    lines.append("")

    return "\n".join(lines)


async def handle_agent_explain_decision(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle agent_explain_decision tool call.

    Returns the reasoning chain and factors behind a decision made by the agent.

    Args:
        args: Dictionary with decision_id

    Returns:
        Dictionary with decision explanation including reasoning chain,
        confidence, factors, and alternatives considered.

    Raises:
        ValueError: If decision_id is not provided
    """
    decision_id = args.get("decision_id")

    if not decision_id:
        raise ValueError("decision_id is required")

    # Look up the decision
    if decision_id not in MOCK_DECISIONS:
        return {
            "status": "not_found",
            "decision_id": decision_id,
            "message": f"Decision {decision_id} not found in the system"
        }

    decision = MOCK_DECISIONS[decision_id]
    return decision


async def handle_agent_correlate_events(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle agent_correlate_events tool call.

    Correlates multiple events to identify patterns, common entities,
    and potential attack chains.

    Args:
        args: Dictionary with event_ids array

    Returns:
        Dictionary with correlation results including common entities,
        timeline, attack patterns, and recommendations.

    Raises:
        ValueError: If event_ids is not provided or empty
    """
    event_ids = args.get("event_ids")

    if event_ids is None:
        raise ValueError("event_ids is required")

    if len(event_ids) == 0:
        raise ValueError("at least one event_id is required")

    # Gather events
    events = []
    for event_id in event_ids:
        if event_id in MOCK_EVENTS:
            events.append(MOCK_EVENTS[event_id])

    # Handle single event case - no correlations possible
    if len(events) <= 1:
        return {
            "correlations": [],
            "correlation_score": 0,
            "common_entities": [],
            "timeline": [events[0]] if events else [],
            "attack_patterns": [],
            "recommendations": ["Add more events for meaningful correlation analysis"]
        }

    # Find common entities across events
    common_entities = _find_common_entities(events)

    # Build chronological timeline
    timeline = sorted(events, key=lambda e: e["timestamp"])

    # Identify attack patterns from MITRE mappings
    attack_patterns = _identify_attack_patterns(events)

    # Calculate correlation score
    correlation_score = _calculate_correlation_score(events, common_entities)

    # Generate correlations between event pairs
    correlations = _generate_correlations(events, common_entities)

    # Generate recommendations
    recommendations = _generate_recommendations(events, attack_patterns)

    return {
        "correlations": correlations,
        "correlation_score": correlation_score,
        "common_entities": common_entities,
        "timeline": timeline,
        "attack_patterns": attack_patterns,
        "recommendations": recommendations
    }


# =============================================================================
# Helper Functions
# =============================================================================

def _find_common_entities(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find entities that appear in multiple events."""
    entity_counts: Dict[str, Dict[str, Any]] = {}

    for event in events:
        # Extract entity types
        entities = []

        if "host" in event:
            entities.append(("host", event["host"]))
        if "user" in event:
            entities.append(("user", event["user"]))
        if "source_ip" in event:
            entities.append(("ip", event["source_ip"]))
        if "dest_ip" in event:
            entities.append(("ip", event["dest_ip"]))
        if "ip_addresses" in event:
            for ip in event["ip_addresses"]:
                entities.append(("ip", ip))
        if "process" in event:
            entities.append(("process", event["process"]))
        if "file_hash" in event:
            entities.append(("hash", event["file_hash"]))

        # Count occurrences
        for entity_type, entity_value in entities:
            key = f"{entity_type}:{entity_value}"
            if key not in entity_counts:
                entity_counts[key] = {
                    "type": entity_type,
                    "value": entity_value,
                    "count": 0,
                    "event_ids": []
                }
            entity_counts[key]["count"] += 1
            entity_counts[key]["event_ids"].append(event["event_id"])

    # Return entities that appear in multiple events
    common = [e for e in entity_counts.values() if e["count"] > 1]
    return sorted(common, key=lambda x: x["count"], reverse=True)


def _identify_attack_patterns(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify MITRE ATT&CK patterns from event sequences."""
    patterns = []

    # Map tactics to readable names
    tactic_names = {
        "TA0001": "Initial Access",
        "TA0002": "Execution",
        "TA0003": "Persistence",
        "TA0004": "Privilege Escalation",
        "TA0005": "Defense Evasion",
        "TA0006": "Credential Access",
        "TA0007": "Discovery",
        "TA0008": "Lateral Movement",
        "TA0009": "Collection",
        "TA0010": "Exfiltration",
        "TA0011": "Command and Control"
    }

    # Collect unique tactics and techniques
    seen_patterns = set()
    for event in events:
        tactic_id = event.get("mitre_tactic")
        technique_id = event.get("mitre_technique")

        if tactic_id and technique_id:
            pattern_key = f"{tactic_id}:{technique_id}"
            if pattern_key not in seen_patterns:
                seen_patterns.add(pattern_key)
                patterns.append({
                    "tactic_id": tactic_id,
                    "tactic_name": tactic_names.get(tactic_id, "Unknown"),
                    "technique_id": technique_id,
                    "event_ids": [e["event_id"] for e in events
                                 if e.get("mitre_tactic") == tactic_id
                                 and e.get("mitre_technique") == technique_id]
                })

    # Sort by tactic ID to show attack chain progression
    patterns.sort(key=lambda x: x["tactic_id"])

    return patterns


def _calculate_correlation_score(events: List[Dict[str, Any]],
                                  common_entities: List[Dict[str, Any]]) -> float:
    """Calculate a correlation score between 0 and 1."""
    if len(events) <= 1:
        return 0.0

    # Factors for scoring
    entity_factor = min(len(common_entities) / 5, 1.0) * 0.4  # Up to 40%

    # Time proximity factor (events close in time score higher)
    timestamps = [datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00"))
                  for e in events]
    time_span = (max(timestamps) - min(timestamps)).total_seconds()
    time_factor = max(0, 1 - (time_span / 3600)) * 0.3  # Up to 30%, penalize > 1 hour

    # Attack chain factor (multiple tactics = likely coordinated)
    unique_tactics = len(set(e.get("mitre_tactic") for e in events if e.get("mitre_tactic")))
    tactic_factor = min(unique_tactics / 4, 1.0) * 0.3  # Up to 30%

    score = entity_factor + time_factor + tactic_factor
    return round(min(score, 1.0), 2)


def _generate_correlations(events: List[Dict[str, Any]],
                           common_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate correlation descriptions between events."""
    correlations = []

    # Create correlations based on common entities
    for entity in common_entities:
        if len(entity["event_ids"]) >= 2:
            correlations.append({
                "type": "shared_entity",
                "entity_type": entity["type"],
                "entity_value": entity["value"],
                "event_ids": entity["event_ids"],
                "description": f"Events share common {entity['type']}: {entity['value']}"
            })

    # Check for temporal proximity correlations
    sorted_events = sorted(events, key=lambda e: e["timestamp"])
    for i in range(len(sorted_events) - 1):
        t1 = datetime.fromisoformat(sorted_events[i]["timestamp"].replace("Z", "+00:00"))
        t2 = datetime.fromisoformat(sorted_events[i+1]["timestamp"].replace("Z", "+00:00"))
        time_diff = (t2 - t1).total_seconds()

        if time_diff < 120:  # Within 2 minutes
            correlations.append({
                "type": "temporal_proximity",
                "event_ids": [sorted_events[i]["event_id"], sorted_events[i+1]["event_id"]],
                "time_diff_seconds": time_diff,
                "description": f"Events occurred within {int(time_diff)} seconds of each other"
            })

    return correlations


def _generate_recommendations(events: List[Dict[str, Any]],
                              attack_patterns: List[Dict[str, Any]]) -> List[str]:
    """Generate investigation recommendations based on findings."""
    recommendations = []

    # Check for C2 activity
    if any(p["tactic_id"] == "TA0011" for p in attack_patterns):
        recommendations.append("Block identified C2 IP addresses at the firewall")
        recommendations.append("Search for additional hosts communicating with the same C2")

    # Check for persistence
    if any(p["tactic_id"] == "TA0003" for p in attack_patterns):
        recommendations.append("Inspect registry keys and scheduled tasks on affected hosts")
        recommendations.append("Consider host reimaging if persistence is confirmed")

    # Check for data collection/exfiltration
    if any(p["tactic_id"] in ["TA0009", "TA0010"] for p in attack_patterns):
        recommendations.append("Review file access logs for sensitive data exposure")
        recommendations.append("Notify data owners about potential breach")

    # General recommendations based on pattern count
    if len(attack_patterns) >= 3:
        recommendations.append("Evidence suggests multi-stage attack - escalate to Tier 2")
        recommendations.append("Consider full incident declaration and containment")

    if not recommendations:
        recommendations.append("Continue monitoring for additional related activity")

    return recommendations


# =============================================================================
# Handler Mapping
# =============================================================================

agent_orchestration_handlers = {
    "agent_analyze_alert": handle_agent_analyze_alert,
    "agent_investigate_ioc": handle_agent_investigate_ioc,
    "agent_recommend_action": handle_agent_recommend_action,
    "agent_generate_report": handle_agent_generate_report,
    "agent_explain_decision": handle_agent_explain_decision,
    "agent_correlate_events": handle_agent_correlate_events,
}
