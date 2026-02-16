"""CrowdStrike Falcon X Sandbox report generator (synthetic).

Simulates CrowdStrike sandbox analysis reports including:
- Verdict (clean/malicious)
- Malware behaviors (persistence, network, file operations, etc.)
- MITRE ATT&CK techniques
- Extracted IOCs (IPs, domains, file paths)
- Malware family identification
"""

import random
from datetime import datetime
from typing import Dict, List, Any, Optional


class CrowdStrikeSandboxMock:
    """Simulates CrowdStrike Falcon X sandbox reports."""

    def __init__(self, seed: int = None):
        """Initialize the mock generator.

        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)

    def generate_sandbox_report(
        self,
        file_hash: str,
        malicious: bool,
        malware_family: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate synthetic sandbox report.

        Args:
            file_hash: File hash (SHA256)
            malicious: Whether file is malicious
            malware_family: Optional malware family name

        Returns:
            Dictionary with sandbox analysis results
        """
        if not malicious:
            return self._generate_clean_report(file_hash)

        return self._generate_malicious_report(file_hash, malware_family)

    def _generate_clean_report(self, file_hash: str) -> Dict[str, Any]:
        """Generate clean (non-malicious) sandbox report.

        Args:
            file_hash: File hash

        Returns:
            Clean verdict report
        """
        return {
            "verdict": "clean",
            "confidence": random.randint(85, 95),
            "file_hash": file_hash,
            "sandbox_runs": 3,
            "enrichment_source": "synthetic_crowdstrike",
            "generated_at": datetime.utcnow().isoformat()
        }

    def _generate_malicious_report(
        self,
        file_hash: str,
        malware_family: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate malicious sandbox report with behaviors.

        Args:
            file_hash: File hash
            malware_family: Optional malware family name

        Returns:
            Malicious verdict report with behaviors and IOCs
        """
        # Assign malware family
        if not malware_family:
            malware_family = self._random_malware_family()

        # Generate behaviors
        behaviors = self._generate_behaviors()

        # Extract MITRE ATT&CK techniques from behaviors
        techniques = self._extract_mitre_techniques(behaviors)

        # Generate extracted IOCs
        extracted_iocs = self._generate_iocs()

        return {
            "verdict": "malicious",
            "confidence": random.randint(80, 99),
            "file_hash": file_hash,
            "malware_family": malware_family,
            "behaviors": behaviors,
            "mitre_techniques": techniques,
            "sandbox_runs": 5,
            "sandbox_environments": ["Windows 10 x64", "Windows 11 x64"],
            "extracted_iocs": extracted_iocs,
            "enrichment_source": "synthetic_crowdstrike",
            "generated_at": datetime.utcnow().isoformat()
        }

    def _generate_behaviors(self) -> List[Dict[str, str]]:
        """Generate malware behaviors.

        Returns:
            List of behavior dictionaries
        """
        behaviors = []

        # Persistence (70% chance)
        if random.random() > 0.3:
            behaviors.append({
                "category": "persistence",
                "description": "Registry modification for autostart",
                "severity": "high",
                "details": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            })

        # Network communication (80% chance)
        if random.random() > 0.2:
            c2_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            behaviors.append({
                "category": "network",
                "description": "Outbound connection to suspicious IP",
                "severity": "critical",
                "details": f"Connection to {c2_ip}:443"
            })

        # File operations (60% chance)
        if random.random() > 0.4:
            behaviors.append({
                "category": "file_system",
                "description": "Suspicious file creation",
                "severity": "medium",
                "details": "Created executable in %TEMP% directory"
            })

        # Process injection (50% chance)
        if random.random() > 0.5:
            behaviors.append({
                "category": "process",
                "description": "Process injection detected",
                "severity": "high",
                "details": "Injected into svchost.exe"
            })

        # Anti-analysis / Evasion (40% chance)
        if random.random() > 0.6:
            behaviors.append({
                "category": "evasion",
                "description": "VM detection attempted",
                "severity": "medium",
                "details": "Checked for VMware and VirtualBox artifacts"
            })

        return behaviors

    def _extract_mitre_techniques(self, behaviors: List[Dict[str, str]]) -> List[str]:
        """Extract MITRE ATT&CK techniques from behaviors.

        Args:
            behaviors: List of behavior dictionaries

        Returns:
            List of MITRE technique IDs
        """
        # Map behavior categories to MITRE techniques
        technique_map = {
            "persistence": ["T1547.001", "T1053"],
            "network": ["T1071.001", "T1095"],
            "file_system": ["T1027", "T1105"],
            "process": ["T1055", "T1106"],
            "evasion": ["T1497", "T1562"]
        }

        techniques = []
        for behavior in behaviors:
            category = behavior["category"]
            if category in technique_map:
                # Pick one random technique for this category
                techniques.extend(random.sample(technique_map[category], 1))

        # Return unique techniques
        return list(set(techniques))

    def _generate_iocs(self) -> Dict[str, List[str]]:
        """Generate extracted IOCs.

        Returns:
            Dictionary with IPs, domains, and file paths
        """
        # Generate IPs
        num_ips = random.randint(1, 3)
        ips = [
            f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            for _ in range(num_ips)
        ]

        # Generate domains
        num_domains = random.randint(0, 2)
        domain_prefixes = ["evil", "bad", "malicious", "c2", "command", "control"]
        domain_tlds = ["com", "net", "org", "ru", "cn"]
        domains = [
            f"{random.choice(domain_prefixes)}{random.randint(1,99)}.{random.choice(domain_tlds)}"
            for _ in range(num_domains)
        ]

        # Generate file paths
        file_names = ["temp", "data", "cache", "update", "system"]
        file_paths = [
            f"C:\\Users\\Public\\{random.choice(file_names)}{random.randint(1,999)}.exe"
        ]

        return {
            "ips": ips,
            "domains": domains,
            "file_paths": file_paths
        }

    def _random_malware_family(self) -> str:
        """Select random malware family.

        Returns:
            Malware family name
        """
        families = [
            "Emotet", "TrickBot", "Dridex", "Qbot", "IcedID", "Cobalt Strike",
            "Ryuk", "Conti", "LockBit", "BlackCat", "AgentTesla", "FormBook",
            "Remcos", "AsyncRAT", "RedLine", "Vidar", "Raccoon", "Azorult"
        ]
        return random.choice(families)
