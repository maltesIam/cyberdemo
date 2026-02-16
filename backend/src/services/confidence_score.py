"""Confidence Score Calculator for SOC alert triage.

Calculates the confidence score for containment decisions by evaluating
multiple dimensions of threat intelligence and context.

Component Weights (default):
  - Intel (40%): VirusTotal score, threat labels, source count
  - Behavior (30%): MITRE technique risk, command line analysis
  - Context (20%): CTEM vulnerability risk, asset criticality
  - Propagation (10%): Number of affected hosts

Thresholds for Decision Making:
  - Score >= 90: HIGH confidence - Auto-containment eligible
  - Score 50-89: MEDIUM confidence - Requires human approval
  - Score < 50: LOW confidence - Likely false positive

Threat Type Weight Profiles:
  - RANSOMWARE: Behavior (40%), Intel (30%), Context (20%), Propagation (10%)
  - LATERAL_MOVEMENT: Propagation (30%), Behavior (30%), Intel (25%), Context (15%)
  - CREDENTIAL_THEFT: Behavior (35%), Intel (35%), Context (20%), Propagation (10%)
  - DEFAULT: Intel (40%), Behavior (30%), Context (20%), Propagation (10%)
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ThreatType(Enum):
    """Threat type classification for weight profile selection."""

    DEFAULT = "default"
    RANSOMWARE = "ransomware"
    LATERAL_MOVEMENT = "lateral_movement"
    CREDENTIAL_THEFT = "credential_theft"
    APT = "apt"
    MALWARE = "malware"


@dataclass
class WeightProfile:
    """Weight configuration for each scoring dimension.

    Weights must sum to 100 (representing percentage allocation).
    """

    intel: int = 40
    behavior: int = 30
    context: int = 20
    propagation: int = 10

    def __post_init__(self):
        total = self.intel + self.behavior + self.context + self.propagation
        if total != 100:
            raise ValueError(f"Weights must sum to 100, got {total}")


# Pre-configured weight profiles per threat type
WEIGHT_PROFILES: dict[ThreatType, WeightProfile] = {
    ThreatType.DEFAULT: WeightProfile(intel=40, behavior=30, context=20, propagation=10),
    ThreatType.RANSOMWARE: WeightProfile(intel=30, behavior=40, context=20, propagation=10),
    ThreatType.LATERAL_MOVEMENT: WeightProfile(intel=25, behavior=30, context=15, propagation=30),
    ThreatType.CREDENTIAL_THEFT: WeightProfile(intel=35, behavior=35, context=20, propagation=10),
    ThreatType.APT: WeightProfile(intel=35, behavior=35, context=20, propagation=10),
    ThreatType.MALWARE: WeightProfile(intel=45, behavior=25, context=20, propagation=10),
}


@dataclass
class ConfidenceComponents:
    """Breakdown of confidence score by dimension.

    Each component represents a normalized score (0-100 scale) that is then
    weighted according to the active weight profile.
    """

    intel: int = 0
    behavior: int = 0
    context: int = 0
    propagation: int = 0

    @property
    def total(self) -> int:
        """Sum of all component scores (unweighted)."""
        return self.intel + self.behavior + self.context + self.propagation


# MITRE techniques considered high-risk (credential access, lateral movement,
# execution of known attack tools, ransomware impact, privilege escalation).
HIGH_RISK_TECHNIQUES: set[str] = {
    # Credential Access
    "T1003.001",  # LSASS Memory
    "T1003.002",  # Security Account Manager
    "T1558.003",  # Kerberoasting
    # Execution (PowerShell, malicious files)
    "T1059.001",  # PowerShell
    "T1204.002",  # Malicious File
    # Lateral Movement
    "T1021.001",  # RDP
    "T1021.002",  # SMB/Admin Shares
    "T1570",  # Lateral Tool Transfer
    # Privilege Escalation
    "T1548.002",  # UAC Bypass
    "T1134.001",  # Token Impersonation
    # Defense Evasion
    "T1562.001",  # Disable or Modify Tools
    # Impact
    "T1486",  # Data Encrypted for Impact (ransomware)
    "T1490",  # Inhibit System Recovery
}

# Medium-risk techniques that warrant attention but less severe
MEDIUM_RISK_TECHNIQUES: set[str] = {
    "T1083",  # File and Directory Discovery
    "T1082",  # System Information Discovery
    "T1057",  # Process Discovery
    "T1016",  # System Network Configuration Discovery
    "T1049",  # System Network Connections Discovery
    "T1018",  # Remote System Discovery
}

# Substrings in a command line that indicate suspicious activity.
SUSPICIOUS_CMDLINE_PATTERNS: list[str] = [
    "encodedcommand",
    "mimikatz",
    "-nop -exec bypass",
    "-nop -w hidden",
    "sekurlsa",
    "invoke-mimikatz",
]

# Additional patterns for command line analysis
HIGHLY_SUSPICIOUS_CMDLINE_PATTERNS: list[str] = [
    "invoke-expression",
    "downloadstring",
    "downloadfile",
    "certutil -urlcache",
    "bitsadmin /transfer",
    "regsvr32 /s /n /u /i:",
    "mshta vbscript:",
    "rundll32.exe javascript:",
]

# Asset criticality values that earn the +5 context bonus.
HIGH_CRITICALITY_VALUES: set[str] = {"vip", "critical"}

# Decision threshold constants
THRESHOLD_HIGH_CONFIDENCE: int = 90
THRESHOLD_MEDIUM_CONFIDENCE: int = 50


def calculate_confidence_score(
    detection: dict,
    intel: dict,
    ctem: dict,
    propagation: dict,
    threat_type: Optional[ThreatType] = None,
) -> tuple[int, ConfidenceComponents, str]:
    """
    Calculate the confidence score for containment decisions.

    This is the main entry point that orchestrates all component calculations.

    Args:
        detection: Detection data containing MITRE technique and cmdline
        intel: Threat intel data with VT score, labels, and sources
        ctem: CTEM data with risk color and asset criticality
        propagation: Propagation data with affected host count

    Returns:
        Tuple of (score 0-100, component breakdown, decision recommendation)

    Example:
        >>> detection = {"mitre_technique": "T1003.001", "cmdline": "mimikatz.exe"}
        >>> intel = {"vt_score": 60, "vt_total": 74, "labels": ["trojan"], "sources": 3}
        >>> ctem = {"risk_color": "Red", "criticality": "vip"}
        >>> propagation = {"affected_hosts": 5}
        >>> score, components, decision = calculate_confidence_score(
        ...     detection, intel, ctem, propagation
        ... )
    """
    calculator = ConfidenceScoreCalculator(threat_type=threat_type)

    # Extract values with safe defaults
    vt_score = intel.get("vt_score", 0)
    vt_total = intel.get("vt_total", 74)
    malware_labels = intel.get("labels", []) or intel.get("malware_labels", [])
    source_count = intel.get("sources", 0) or intel.get("source_count", 0)

    mitre_technique = detection.get("mitre_technique", "")
    cmdline = detection.get("cmdline", "")

    ctem_risk = ctem.get("risk_color", "Green") or ctem.get("ctem_risk", "Green")
    asset_criticality = ctem.get("criticality", "low") or ctem.get("asset_criticality", "low")

    affected_hosts = propagation.get("affected_hosts", 0)

    total, components = calculator.calculate(
        vt_score=vt_score,
        vt_total=vt_total,
        malware_labels=malware_labels,
        source_count=source_count,
        mitre_technique=mitre_technique,
        cmdline=cmdline,
        ctem_risk=ctem_risk,
        asset_criticality=asset_criticality,
        affected_hosts=affected_hosts,
    )

    # Determine decision based on thresholds
    if total >= THRESHOLD_HIGH_CONFIDENCE:
        decision = "AUTO_CONTAIN"
    elif total >= THRESHOLD_MEDIUM_CONFIDENCE:
        decision = "REQUIRES_APPROVAL"
    else:
        decision = "FALSE_POSITIVE"

    return total, components, decision


def calculate_intel_component(intel: dict) -> int:
    """
    Calculate the intel component score (0-40).

    Scoring breakdown:
      - VT detections > 50: +30 points
      - At least one malware label: +10 points
      - Multiple sources (>= 3): +5 bonus (capped at max)

    Args:
        intel: Dictionary with vt_score, vt_total, labels/malware_labels, sources

    Returns:
        Intel score from 0-40
    """
    calculator = ConfidenceScoreCalculator()
    return calculator._calculate_intel(
        vt_score=intel.get("vt_score", 0),
        vt_total=intel.get("vt_total", 74),
        malware_labels=intel.get("labels", []) or intel.get("malware_labels", []),
        source_count=intel.get("sources", 0) or intel.get("source_count", 0),
    )


def calculate_behavior_component(detection: dict) -> int:
    """
    Calculate the behavior component score (0-30).

    Scoring breakdown:
      - High-risk MITRE technique: +20 points
      - Medium-risk MITRE technique: +10 points
      - Suspicious command line pattern: +10 points (max once)

    Args:
        detection: Dictionary with mitre_technique and cmdline

    Returns:
        Behavior score from 0-30
    """
    calculator = ConfidenceScoreCalculator()
    return calculator._calculate_behavior(
        mitre_technique=detection.get("mitre_technique", ""),
        cmdline=detection.get("cmdline", ""),
    )


def calculate_context_component(ctem: dict) -> int:
    """
    Calculate the context component score (0-20).

    Scoring breakdown:
      - Red CTEM risk (critical vulnerabilities): +15 points
      - VIP/Critical asset criticality: +5 points

    Args:
        ctem: Dictionary with risk_color/ctem_risk and criticality/asset_criticality

    Returns:
        Context score from 0-20
    """
    calculator = ConfidenceScoreCalculator()
    # Handle both key naming conventions
    ctem_risk = ctem.get("risk_color") or ctem.get("ctem_risk") or "Green"
    asset_criticality = ctem.get("criticality") or ctem.get("asset_criticality") or "low"
    return calculator._calculate_context(
        ctem_risk=ctem_risk,
        asset_criticality=asset_criticality,
    )


def calculate_propagation_component(propagation: dict) -> int:
    """
    Calculate the propagation component score (0-10).

    Scoring breakdown:
      - 0 hosts: 0 points
      - 1 host: +2 points
      - 2-5 hosts: +5 points
      - 6+ hosts: +10 points

    Args:
        propagation: Dictionary with affected_hosts count

    Returns:
        Propagation score from 0-10
    """
    calculator = ConfidenceScoreCalculator()
    return calculator._calculate_propagation(
        affected_hosts=propagation.get("affected_hosts", 0)
    )


class ConfidenceScoreCalculator:
    """Calculates a deterministic confidence score for SOC alert triage.

    The calculator supports configurable weight profiles per threat type,
    allowing the scoring algorithm to prioritize different dimensions
    based on the nature of the threat being evaluated.

    Attributes:
        weights: The active weight profile for score calculation
        threat_type: The threat type classification being used

    Example:
        >>> calculator = ConfidenceScoreCalculator(threat_type=ThreatType.RANSOMWARE)
        >>> total, components = calculator.calculate(
        ...     vt_score=60, vt_total=74, malware_labels=["ransomware"],
        ...     mitre_technique="T1486", cmdline="vssadmin delete shadows",
        ...     ctem_risk="Red", asset_criticality="critical",
        ...     affected_hosts=10
        ... )
    """

    def __init__(
        self,
        threat_type: Optional[ThreatType] = None,
        weights: Optional[WeightProfile] = None,
    ):
        """Initialize the calculator with a weight profile.

        Args:
            threat_type: Threat classification for automatic profile selection
            weights: Custom weight profile (overrides threat_type selection)
        """
        self.threat_type = threat_type or ThreatType.DEFAULT
        if weights is not None:
            self.weights = weights
        else:
            self.weights = WEIGHT_PROFILES.get(self.threat_type, WEIGHT_PROFILES[ThreatType.DEFAULT])

    def _calculate_intel(
        self,
        vt_score: int,
        vt_total: int,
        malware_labels: list[str],
        source_count: int = 0,
    ) -> int:
        """Score the threat-intel dimension (0-40 points).

        Thresholds:
          - VT Detection Threshold: > 50 detections out of vt_total
          - Label Presence: Any non-empty malware_labels list
          - Source Count Bonus: >= 3 distinct intel sources

        Scoring rules:
          - VT detections > 50 out of vt_total: +30
          - At least one known malware label present: +10
          - 3+ intel sources: +5 (bonus, stacks with above)

        Args:
            vt_score: Number of VirusTotal detections
            vt_total: Total number of VirusTotal engines (typically 74)
            malware_labels: List of malware family/type labels
            source_count: Number of distinct intel sources reporting this IOC

        Returns:
            Intel component score (0-40)
        """
        score = 0

        if vt_score > 50:
            score += 30

        if malware_labels:
            score += 10

        # Bonus for multiple corroborating sources
        if source_count >= 3:
            score += 5

        return min(score, 40)

    def _calculate_behavior(
        self,
        mitre_technique: str,
        cmdline: str,
    ) -> int:
        """Score the behavior dimension (0-30 points).

        Thresholds:
          - High-Risk Technique: Matches HIGH_RISK_TECHNIQUES set
          - Medium-Risk Technique: Matches MEDIUM_RISK_TECHNIQUES set
          - Suspicious Cmdline: Contains SUSPICIOUS_CMDLINE_PATTERNS substring

        Scoring rules:
          - High-risk MITRE technique: +20
          - Medium-risk MITRE technique: +10 (not cumulative with high-risk)
          - Suspicious command-line pattern (encoded PS, mimikatz, etc.): +10

        Args:
            mitre_technique: MITRE ATT&CK technique ID (e.g., "T1003.001")
            cmdline: Full command line of the suspicious process

        Returns:
            Behavior component score (0-30)
        """
        score = 0

        if mitre_technique in HIGH_RISK_TECHNIQUES:
            score += 20
        elif mitre_technique in MEDIUM_RISK_TECHNIQUES:
            score += 10

        cmdline_lower = cmdline.lower()
        for pattern in SUSPICIOUS_CMDLINE_PATTERNS:
            if pattern in cmdline_lower:
                score += 10
                break

        return min(score, 30)

    def _calculate_context(
        self,
        ctem_risk: str,
        asset_criticality: str,
    ) -> int:
        """Score the context dimension (0-20 points).

        Thresholds:
          - Critical Vulnerability: ctem_risk == "Red"
          - High Criticality Asset: asset_criticality in {"vip", "critical"}

        Scoring rules:
          - Host with critical vulnerabilities (Red CTEM risk): +15
          - Asset criticality is VIP or critical: +5
          - Green/patched host with low criticality: 0

        Args:
            ctem_risk: CTEM risk color ("Red", "Yellow", "Green")
            asset_criticality: Asset criticality level ("vip", "critical", "low", etc.)

        Returns:
            Context component score (0-20)
        """
        score = 0

        if ctem_risk == "Red":
            score += 15

        if asset_criticality in HIGH_CRITICALITY_VALUES:
            score += 5

        return min(score, 20)

    def _calculate_propagation(self, affected_hosts: int) -> int:
        """Score the propagation dimension (0-10 points).

        Thresholds:
          - Single Host: affected_hosts == 1
          - Small Cluster: 2 <= affected_hosts <= 5
          - Large Outbreak: affected_hosts >= 6

        Scoring rules:
          - 0 hosts: 0
          - 1 host: +2
          - 2-5 hosts: +5
          - 6+ hosts: +10

        Args:
            affected_hosts: Number of hosts where the IOC/behavior was detected

        Returns:
            Propagation component score (0-10)
        """
        if affected_hosts >= 6:
            return 10
        if affected_hosts >= 2:
            return 5
        if affected_hosts == 1:
            return 2
        return 0

    def calculate(
        self,
        vt_score: int,
        vt_total: int,
        malware_labels: list[str],
        mitre_technique: str,
        cmdline: str,
        ctem_risk: str,
        asset_criticality: str,
        affected_hosts: int,
        source_count: int = 0,
    ) -> tuple[int, ConfidenceComponents]:
        """Calculate the overall confidence score and per-dimension breakdown.

        This method computes individual component scores and combines them
        according to the active weight profile.

        Decision Thresholds (for reference):
          - >= 90: HIGH confidence - Suitable for auto-containment
          - 50-89: MEDIUM confidence - Requires human review
          - < 50: LOW confidence - Likely false positive

        Args:
            vt_score: Number of VirusTotal detections
            vt_total: Total VirusTotal engines (typically 74)
            malware_labels: List of malware family labels
            mitre_technique: MITRE ATT&CK technique ID
            cmdline: Process command line
            ctem_risk: CTEM vulnerability risk color
            asset_criticality: Asset criticality level
            affected_hosts: Number of affected hosts
            source_count: Number of intel sources (optional)

        Returns:
            A tuple of (total_score, components) where total_score is 0-100
            and components is a ConfidenceComponents with per-dimension values.
        """
        components = ConfidenceComponents(
            intel=self._calculate_intel(vt_score, vt_total, malware_labels, source_count),
            behavior=self._calculate_behavior(mitre_technique, cmdline),
            context=self._calculate_context(ctem_risk, asset_criticality),
            propagation=self._calculate_propagation(affected_hosts),
        )

        total = max(0, min(100, components.total))
        return total, components

    def calculate_weighted(
        self,
        vt_score: int,
        vt_total: int,
        malware_labels: list[str],
        mitre_technique: str,
        cmdline: str,
        ctem_risk: str,
        asset_criticality: str,
        affected_hosts: int,
        source_count: int = 0,
    ) -> tuple[int, ConfidenceComponents]:
        """Calculate the weighted confidence score using the active weight profile.

        Unlike calculate(), this method applies the weight profile to scale
        each component's contribution to the final score.

        Args:
            Same as calculate()

        Returns:
            A tuple of (weighted_total_score, raw_components) where the total
            reflects the weighted combination of components.
        """
        # Calculate raw component scores (normalized to 0-100)
        raw_intel = self._calculate_intel(vt_score, vt_total, malware_labels, source_count)
        raw_behavior = self._calculate_behavior(mitre_technique, cmdline)
        raw_context = self._calculate_context(ctem_risk, asset_criticality)
        raw_propagation = self._calculate_propagation(affected_hosts)

        # Normalize to percentage of max possible (intel max=40, behavior max=30, etc.)
        norm_intel = (raw_intel / 40) * 100
        norm_behavior = (raw_behavior / 30) * 100
        norm_context = (raw_context / 20) * 100
        norm_propagation = (raw_propagation / 10) * 100

        # Apply weights
        weighted_total = (
            norm_intel * (self.weights.intel / 100)
            + norm_behavior * (self.weights.behavior / 100)
            + norm_context * (self.weights.context / 100)
            + norm_propagation * (self.weights.propagation / 100)
        )

        components = ConfidenceComponents(
            intel=raw_intel,
            behavior=raw_behavior,
            context=raw_context,
            propagation=raw_propagation,
        )

        return int(max(0, min(100, weighted_total))), components
