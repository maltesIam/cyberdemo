"""
MITRE ATT&CK Client.

MITRE ATT&CK is a globally-accessible knowledge base of adversary tactics
and techniques based on real-world observations. This client provides
access to tactics, techniques, software, and threat actor groups.

This implementation uses embedded static data for the most common/critical
MITRE ATT&CK entries to avoid external API dependencies and rate limits.
The data covers Enterprise ATT&CK v14.

For production use with full ATT&CK data, consider using:
- MITRE ATT&CK STIX data: https://github.com/mitre/cti
- MITRE ATT&CK API: https://attack.mitre.org/resources/
"""

import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


# =============================================================================
# Embedded MITRE ATT&CK Data (Enterprise ATT&CK v14 - Core subset)
# =============================================================================

# Tactics (Kill Chain Phases) - Enterprise Matrix
TACTICS = [
    {
        "id": "TA0043",
        "name": "Reconnaissance",
        "description": "The adversary is trying to gather information they can use to plan future operations."
    },
    {
        "id": "TA0042",
        "name": "Resource Development",
        "description": "The adversary is trying to establish resources they can use to support operations."
    },
    {
        "id": "TA0001",
        "name": "Initial Access",
        "description": "The adversary is trying to get into your network."
    },
    {
        "id": "TA0002",
        "name": "Execution",
        "description": "The adversary is trying to run malicious code."
    },
    {
        "id": "TA0003",
        "name": "Persistence",
        "description": "The adversary is trying to maintain their foothold."
    },
    {
        "id": "TA0004",
        "name": "Privilege Escalation",
        "description": "The adversary is trying to gain higher-level permissions."
    },
    {
        "id": "TA0005",
        "name": "Defense Evasion",
        "description": "The adversary is trying to avoid being detected."
    },
    {
        "id": "TA0006",
        "name": "Credential Access",
        "description": "The adversary is trying to steal account names and passwords."
    },
    {
        "id": "TA0007",
        "name": "Discovery",
        "description": "The adversary is trying to figure out your environment."
    },
    {
        "id": "TA0008",
        "name": "Lateral Movement",
        "description": "The adversary is trying to move through your environment."
    },
    {
        "id": "TA0009",
        "name": "Collection",
        "description": "The adversary is trying to gather data of interest to their goal."
    },
    {
        "id": "TA0011",
        "name": "Command and Control",
        "description": "The adversary is trying to communicate with compromised systems to control them."
    },
    {
        "id": "TA0010",
        "name": "Exfiltration",
        "description": "The adversary is trying to steal data."
    },
    {
        "id": "TA0040",
        "name": "Impact",
        "description": "The adversary is trying to manipulate, interrupt, or destroy your systems and data."
    },
]

# Techniques - Most commonly observed techniques
TECHNIQUES = [
    # Initial Access
    {
        "id": "T1566",
        "name": "Phishing",
        "tactic_id": ["TA0001"],
        "description": "Adversaries may send phishing messages to gain access to victim systems.",
        "data_sources": ["Application Log", "Network Traffic"]
    },
    {
        "id": "T1566.001",
        "name": "Spearphishing Attachment",
        "tactic_id": ["TA0001"],
        "description": "Adversaries may send spearphishing emails with a malicious attachment.",
        "data_sources": ["Application Log", "File", "Network Traffic"]
    },
    {
        "id": "T1566.002",
        "name": "Spearphishing Link",
        "tactic_id": ["TA0001"],
        "description": "Adversaries may send spearphishing emails with a malicious link.",
        "data_sources": ["Application Log", "Network Traffic"]
    },
    {
        "id": "T1190",
        "name": "Exploit Public-Facing Application",
        "tactic_id": ["TA0001"],
        "description": "Adversaries may attempt to exploit a weakness in an Internet-facing host or system.",
        "data_sources": ["Application Log", "Network Traffic"]
    },
    {
        "id": "T1133",
        "name": "External Remote Services",
        "tactic_id": ["TA0001", "TA0003"],
        "description": "Adversaries may leverage external-facing remote services to initially access and/or persist.",
        "data_sources": ["Logon Session", "Network Traffic"]
    },
    {
        "id": "T1078",
        "name": "Valid Accounts",
        "tactic_id": ["TA0001", "TA0003", "TA0004", "TA0005"],
        "description": "Adversaries may obtain and abuse credentials of existing accounts.",
        "data_sources": ["Logon Session", "User Account"]
    },
    # Execution
    {
        "id": "T1059",
        "name": "Command and Scripting Interpreter",
        "tactic_id": ["TA0002"],
        "description": "Adversaries may abuse command and script interpreters to execute commands.",
        "data_sources": ["Command", "Process", "Script"]
    },
    {
        "id": "T1059.001",
        "name": "PowerShell",
        "tactic_id": ["TA0002"],
        "description": "Adversaries may abuse PowerShell commands and scripts for execution.",
        "data_sources": ["Command", "Module", "Process", "Script"]
    },
    {
        "id": "T1059.003",
        "name": "Windows Command Shell",
        "tactic_id": ["TA0002"],
        "description": "Adversaries may abuse the Windows command shell for execution.",
        "data_sources": ["Command", "Process"]
    },
    {
        "id": "T1204",
        "name": "User Execution",
        "tactic_id": ["TA0002"],
        "description": "An adversary may rely upon specific actions by a user in order to gain execution.",
        "data_sources": ["File", "Network Traffic", "Process"]
    },
    {
        "id": "T1053",
        "name": "Scheduled Task/Job",
        "tactic_id": ["TA0002", "TA0003", "TA0004"],
        "description": "Adversaries may abuse task scheduling functionality to facilitate execution.",
        "data_sources": ["Command", "File", "Process", "Scheduled Job"]
    },
    # Persistence
    {
        "id": "T1547",
        "name": "Boot or Logon Autostart Execution",
        "tactic_id": ["TA0003", "TA0004"],
        "description": "Adversaries may configure system settings to automatically execute a program during boot.",
        "data_sources": ["Command", "Driver", "File", "Process", "Windows Registry"]
    },
    {
        "id": "T1547.001",
        "name": "Registry Run Keys / Startup Folder",
        "tactic_id": ["TA0003", "TA0004"],
        "description": "Adversaries may achieve persistence by adding a program to a startup folder or registry run key.",
        "data_sources": ["Command", "File", "Process", "Windows Registry"]
    },
    {
        "id": "T1543",
        "name": "Create or Modify System Process",
        "tactic_id": ["TA0003", "TA0004"],
        "description": "Adversaries may create or modify system-level processes for persistence.",
        "data_sources": ["Command", "Driver", "File", "Process", "Service", "Windows Registry"]
    },
    # Privilege Escalation
    {
        "id": "T1068",
        "name": "Exploitation for Privilege Escalation",
        "tactic_id": ["TA0004"],
        "description": "Adversaries may exploit software vulnerabilities to elevate privileges.",
        "data_sources": ["Process"]
    },
    # Defense Evasion
    {
        "id": "T1070",
        "name": "Indicator Removal",
        "tactic_id": ["TA0005"],
        "description": "Adversaries may delete or modify artifacts generated within systems to remove evidence.",
        "data_sources": ["Command", "File", "Network Traffic", "Process", "Windows Registry"]
    },
    {
        "id": "T1027",
        "name": "Obfuscated Files or Information",
        "tactic_id": ["TA0005"],
        "description": "Adversaries may attempt to make an executable or file difficult to discover or analyze.",
        "data_sources": ["Command", "File", "Process", "Script"]
    },
    {
        "id": "T1562",
        "name": "Impair Defenses",
        "tactic_id": ["TA0005"],
        "description": "Adversaries may maliciously modify components of a victim environment to hinder defenses.",
        "data_sources": ["Cloud Service", "Command", "Process", "Sensor Health", "Service", "Windows Registry"]
    },
    # Credential Access
    {
        "id": "T1003",
        "name": "OS Credential Dumping",
        "tactic_id": ["TA0006"],
        "description": "Adversaries may attempt to dump credentials to obtain account login information.",
        "data_sources": ["Active Directory", "Command", "File", "Process", "Windows Registry"]
    },
    {
        "id": "T1003.001",
        "name": "LSASS Memory",
        "tactic_id": ["TA0006"],
        "description": "Adversaries may attempt to access credential material stored in LSASS process memory.",
        "data_sources": ["Process"]
    },
    {
        "id": "T1110",
        "name": "Brute Force",
        "tactic_id": ["TA0006"],
        "description": "Adversaries may use brute force techniques to gain access to accounts.",
        "data_sources": ["Application Log", "User Account"]
    },
    # Discovery
    {
        "id": "T1083",
        "name": "File and Directory Discovery",
        "tactic_id": ["TA0007"],
        "description": "Adversaries may enumerate files and directories to find specific information.",
        "data_sources": ["Command", "Process"]
    },
    {
        "id": "T1057",
        "name": "Process Discovery",
        "tactic_id": ["TA0007"],
        "description": "Adversaries may attempt to get information about running processes.",
        "data_sources": ["Command", "Process"]
    },
    {
        "id": "T1082",
        "name": "System Information Discovery",
        "tactic_id": ["TA0007"],
        "description": "An adversary may attempt to get detailed information about the operating system.",
        "data_sources": ["Command", "Process"]
    },
    # Lateral Movement
    {
        "id": "T1021",
        "name": "Remote Services",
        "tactic_id": ["TA0008"],
        "description": "Adversaries may use remote services to move laterally within an environment.",
        "data_sources": ["Logon Session", "Network Traffic", "Process"]
    },
    {
        "id": "T1021.001",
        "name": "Remote Desktop Protocol",
        "tactic_id": ["TA0008"],
        "description": "Adversaries may use RDP to connect to a remote host for lateral movement.",
        "data_sources": ["Logon Session", "Network Traffic", "Process"]
    },
    # Collection
    {
        "id": "T1005",
        "name": "Data from Local System",
        "tactic_id": ["TA0009"],
        "description": "Adversaries may search local system sources to find files of interest.",
        "data_sources": ["Command", "File", "Process"]
    },
    {
        "id": "T1074",
        "name": "Data Staged",
        "tactic_id": ["TA0009"],
        "description": "Adversaries may stage collected data in a central location prior to Exfiltration.",
        "data_sources": ["Command", "File", "Process"]
    },
    # Command and Control
    {
        "id": "T1071",
        "name": "Application Layer Protocol",
        "tactic_id": ["TA0011"],
        "description": "Adversaries may communicate using application layer protocols.",
        "data_sources": ["Network Traffic"]
    },
    {
        "id": "T1071.001",
        "name": "Web Protocols",
        "tactic_id": ["TA0011"],
        "description": "Adversaries may communicate using web protocols (HTTP/HTTPS).",
        "data_sources": ["Network Traffic"]
    },
    {
        "id": "T1105",
        "name": "Ingress Tool Transfer",
        "tactic_id": ["TA0011"],
        "description": "Adversaries may transfer tools from an external system into a compromised environment.",
        "data_sources": ["File", "Network Traffic"]
    },
    {
        "id": "T1219",
        "name": "Remote Access Software",
        "tactic_id": ["TA0011"],
        "description": "An adversary may use legitimate remote access software to control a victim system.",
        "data_sources": ["Network Traffic", "Process"]
    },
    # Exfiltration
    {
        "id": "T1041",
        "name": "Exfiltration Over C2 Channel",
        "tactic_id": ["TA0010"],
        "description": "Adversaries may steal data by exfiltrating it over an existing C2 channel.",
        "data_sources": ["Command", "File", "Network Traffic"]
    },
    {
        "id": "T1048",
        "name": "Exfiltration Over Alternative Protocol",
        "tactic_id": ["TA0010"],
        "description": "Adversaries may steal data by exfiltrating over a different protocol than the existing C2.",
        "data_sources": ["Cloud Storage", "Command", "File", "Network Traffic"]
    },
    # Impact
    {
        "id": "T1486",
        "name": "Data Encrypted for Impact",
        "tactic_id": ["TA0040"],
        "description": "Adversaries may encrypt data on target systems to interrupt availability.",
        "data_sources": ["Cloud Storage", "File", "Process"]
    },
    {
        "id": "T1490",
        "name": "Inhibit System Recovery",
        "tactic_id": ["TA0040"],
        "description": "Adversaries may delete or remove built-in OS data and turn off automatic repair.",
        "data_sources": ["Cloud Storage", "Command", "File", "Process", "Service", "Windows Registry"]
    },
    {
        "id": "T1489",
        "name": "Service Stop",
        "tactic_id": ["TA0040"],
        "description": "Adversaries may stop or disable services to render them unavailable to legitimate users.",
        "data_sources": ["Command", "Process", "Service", "Windows Registry"]
    },
]

# Software (Malware and Tools)
SOFTWARE = [
    # Malware
    {
        "id": "S0154",
        "name": "Cobalt Strike",
        "type": "tool",
        "description": "Cobalt Strike is a commercial adversary simulation tool."
    },
    {
        "id": "S0002",
        "name": "Mimikatz",
        "type": "tool",
        "description": "Mimikatz is a credential dumper capable of obtaining plaintext passwords."
    },
    {
        "id": "S0029",
        "name": "PsExec",
        "type": "tool",
        "description": "PsExec is a free Microsoft tool that can be used to execute programs on remote systems."
    },
    {
        "id": "S0650",
        "name": "QakBot",
        "type": "malware",
        "description": "QakBot is a modular banking trojan."
    },
    {
        "id": "S0367",
        "name": "Emotet",
        "type": "malware",
        "description": "Emotet is a modular malware variant used as a dropper and loader."
    },
    {
        "id": "S0446",
        "name": "Ryuk",
        "type": "malware",
        "description": "Ryuk is a ransomware that has been used against multiple industries."
    },
    {
        "id": "S0483",
        "name": "TrickBot",
        "type": "malware",
        "description": "TrickBot is a banking Trojan that has evolved into a modular malware framework."
    },
    {
        "id": "S0357",
        "name": "Impacket",
        "type": "tool",
        "description": "Impacket is an open source collection of modules for working with network protocols."
    },
    {
        "id": "S0552",
        "name": "AdFind",
        "type": "tool",
        "description": "AdFind is a free command-line query tool for gathering Active Directory information."
    },
    {
        "id": "S0266",
        "name": "TinyTurla",
        "type": "malware",
        "description": "TinyTurla is a backdoor used by the Turla APT group."
    },
    {
        "id": "S0534",
        "name": "Bazar",
        "type": "malware",
        "description": "Bazar is a backdoor with loader capabilities associated with TrickBot."
    },
    {
        "id": "S0386",
        "name": "Ursnif",
        "type": "malware",
        "description": "Ursnif is a banking Trojan and variant of Gozi."
    },
    {
        "id": "S0606",
        "name": "SUNBURST",
        "type": "malware",
        "description": "SUNBURST is a trojanized update to the SolarWinds Orion software."
    },
    {
        "id": "S0359",
        "name": "Nltest",
        "type": "tool",
        "description": "Nltest is a Windows command-line utility for domain and trust information."
    },
    {
        "id": "S0378",
        "name": "PoshC2",
        "type": "tool",
        "description": "PoshC2 is an open source remote administration and post-exploitation framework."
    },
]

# Threat Actor Groups
GROUPS = [
    {
        "id": "G0007",
        "name": "APT28",
        "aliases": ["Fancy Bear", "Sofacy", "Pawn Storm", "STRONTIUM"],
        "description": "APT28 is a Russian threat group attributed to Russian intelligence services."
    },
    {
        "id": "G0016",
        "name": "APT29",
        "aliases": ["Cozy Bear", "The Dukes", "NOBELIUM"],
        "description": "APT29 is a Russian threat group attributed to Russian Foreign Intelligence Service."
    },
    {
        "id": "G0010",
        "name": "Turla",
        "aliases": ["Snake", "Venomous Bear", "KRYPTON"],
        "description": "Turla is a Russian-based threat group that has infected victims in over 45 countries."
    },
    {
        "id": "G0032",
        "name": "Lazarus Group",
        "aliases": ["Hidden Cobra", "ZINC", "Labyrinth Chollima"],
        "description": "Lazarus Group is a North Korean state-sponsored threat group."
    },
    {
        "id": "G0082",
        "name": "APT38",
        "aliases": ["Bluenoroff", "Stardust Chollima"],
        "description": "APT38 is a North Korean state-sponsored threat group focusing on financial institutions."
    },
    {
        "id": "G0045",
        "name": "menuPass",
        "aliases": ["APT10", "Stone Panda", "POTASSIUM"],
        "description": "menuPass is a Chinese threat group known for targeting multiple industries."
    },
    {
        "id": "G0050",
        "name": "APT32",
        "aliases": ["OceanLotus", "SeaLotus"],
        "description": "APT32 is a Vietnamese threat group that has targeted multiple industries."
    },
    {
        "id": "G0059",
        "name": "Magic Hound",
        "aliases": ["APT35", "Charming Kitten", "Phosphorus"],
        "description": "Magic Hound is an Iranian threat group conducting cyber espionage."
    },
    {
        "id": "G0027",
        "name": "Threat Group-3390",
        "aliases": ["TG-3390", "Emissary Panda", "APT27"],
        "description": "Threat Group-3390 is a Chinese threat group targeting multiple industries."
    },
    {
        "id": "G0096",
        "name": "APT41",
        "aliases": ["Wicked Panda", "BARIUM", "Winnti"],
        "description": "APT41 is a Chinese state-sponsored espionage group conducting financially motivated operations."
    },
]


class MitreAttackClient:
    """
    Client for MITRE ATT&CK data.

    Provides access to tactics, techniques, software, and threat groups
    from the MITRE ATT&CK framework. Uses embedded static data for
    reliability and performance.
    """

    def __init__(self):
        """Initialize the MITRE ATT&CK client."""
        self._tactics = {t["id"]: t for t in TACTICS}
        self._techniques = {t["id"]: t for t in TECHNIQUES}
        self._software = {s["id"]: s for s in SOFTWARE}
        self._groups = {g["id"]: g for g in GROUPS}

    async def close(self):
        """Close the client (no-op for static data client)."""
        pass

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def get_tactics(self) -> List[Dict[str, Any]]:
        """
        Get all MITRE ATT&CK tactics.

        Returns:
            List of tactics with id, name, description.
        """
        return TACTICS.copy()

    async def get_techniques(
        self,
        tactic_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get MITRE ATT&CK techniques.

        Args:
            tactic_id: Optional tactic ID to filter techniques by.

        Returns:
            List of techniques with id, name, tactic_id, description, data_sources.
        """
        techniques = TECHNIQUES.copy()

        if tactic_id:
            techniques = [
                t for t in techniques
                if tactic_id in t["tactic_id"]
            ]

        return techniques

    async def get_technique(self, technique_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific technique.

        Args:
            technique_id: The technique ID (e.g., "T1566", "T1566.001").

        Returns:
            Technique details or None if not found.
        """
        return self._techniques.get(technique_id)

    async def get_software(
        self,
        software_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get MITRE ATT&CK software (malware and tools).

        Args:
            software_type: Optional type filter ("malware" or "tool").

        Returns:
            List of software with id, name, type, description.
        """
        software = SOFTWARE.copy()

        if software_type:
            software = [
                s for s in software
                if s["type"] == software_type
            ]

        return software

    async def get_groups(self) -> List[Dict[str, Any]]:
        """
        Get MITRE ATT&CK threat actor groups.

        Returns:
            List of groups with id, name, aliases, description.
        """
        return GROUPS.copy()

    async def map_technique_to_tactic(
        self,
        technique_id: str
    ) -> List[Dict[str, Any]]:
        """
        Map a technique ID to its associated tactics.

        Args:
            technique_id: The technique ID to map.

        Returns:
            List of tactics associated with the technique.
        """
        technique = self._techniques.get(technique_id)

        if not technique:
            return []

        tactic_ids = technique["tactic_id"]
        return [
            self._tactics[tid]
            for tid in tactic_ids
            if tid in self._tactics
        ]

    async def search_techniques(self, query: str) -> List[Dict[str, Any]]:
        """
        Search techniques by name (case-insensitive substring match).

        Args:
            query: Search query string.

        Returns:
            List of matching techniques.
        """
        query_lower = query.lower()
        return [
            t for t in TECHNIQUES
            if query_lower in t["name"].lower()
        ]

    async def build_attack_data(
        self,
        technique_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Build a MitreAttackData compatible structure for given techniques.

        Args:
            technique_ids: List of technique IDs to include.

        Returns:
            Dict with tactics, techniques, software lists matching MitreAttackData model.
        """
        if not technique_ids:
            return {
                "tactics": [],
                "techniques": [],
                "software": []
            }

        # Collect techniques
        techniques = []
        tactic_ids_set = set()

        for tid in technique_ids:
            technique = self._techniques.get(tid)
            if technique:
                techniques.append({
                    "id": technique["id"],
                    "name": technique["name"],
                    "tactic_id": technique["tactic_id"],
                    "data_sources": technique.get("data_sources", [])
                })
                # Collect associated tactic IDs
                for tactic_id in technique["tactic_id"]:
                    tactic_ids_set.add(tactic_id)

        # Collect tactics
        tactics = []
        for tactic_id in tactic_ids_set:
            tactic = self._tactics.get(tactic_id)
            if tactic:
                tactics.append({
                    "id": tactic["id"],
                    "name": tactic["name"]
                })

        # Return empty software for now (would require technique-to-software mapping)
        return {
            "tactics": tactics,
            "techniques": techniques,
            "software": []
        }
