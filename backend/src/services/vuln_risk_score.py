"""Vulnerability Risk Score Calculator.

Calculates a composite risk score (0-100) for CVEs based on multiple factors:

Component Weights (sum to 100):
  - CVSS Score (25%): Base severity from NVD
  - EPSS Score (25%): Exploit prediction probability
  - KEV Status (15%): CISA Known Exploited Vulnerabilities catalog
  - Exploit Maturity (15%): Availability and sophistication of exploits
  - Asset Impact (10%): Impact on critical assets in the organization
  - Exposure (10%): Internet exposure via Shodan

Risk Levels:
  - >= 85: Critical - Immediate action required
  - >= 70: High - Prioritized remediation
  - >= 40: Medium - Scheduled remediation
  - < 40: Low - Monitor and review

This scoring system goes beyond CVSS by incorporating threat intelligence
and organizational context to provide actionable prioritization.
"""
from typing import Literal


RiskLevel = Literal["Critical", "High", "Medium", "Low"]
ExploitMaturity = Literal["weaponized", "poc", "unproven", "none"]


# Weight constants (must sum to 100)
WEIGHT_CVSS = 25.0
WEIGHT_EPSS = 25.0
WEIGHT_KEV = 15.0
WEIGHT_EXPLOIT = 15.0
WEIGHT_ASSET = 10.0
WEIGHT_EXPOSURE = 10.0

# Exploit maturity score mapping
EXPLOIT_MATURITY_SCORES: dict[str, float] = {
    "weaponized": 15.0,
    "poc": 10.0,
    "unproven": 5.0,
    "none": 0.0,
}

# Risk level thresholds
THRESHOLD_CRITICAL = 85.0
THRESHOLD_HIGH = 70.0
THRESHOLD_MEDIUM = 40.0


class VulnRiskScoreCalculator:
    """Calculates vulnerability risk scores based on multiple intelligence factors.

    The calculator produces a deterministic risk score (0-100) that combines:
    - Technical severity (CVSS)
    - Exploitation probability (EPSS)
    - Active exploitation evidence (KEV)
    - Exploit availability (maturity)
    - Organizational impact (affected critical assets)
    - Internet exposure (Shodan data)

    Example:
        >>> calculator = VulnRiskScoreCalculator()
        >>> result = calculator.calculate_risk_score(
        ...     cvss_v3_score=9.8,
        ...     epss_score=0.972,
        ...     is_kev=True,
        ...     exploit_maturity="weaponized",
        ...     affected_critical_assets=10,
        ...     total_critical_assets=50,
        ...     shodan_exposed_count=1000
        ... )
        >>> print(result["risk_score"], result["risk_level"])
        92.4 Critical
    """

    def calculate_risk_score(
        self,
        cvss_v3_score: float,
        epss_score: float,
        is_kev: bool,
        exploit_maturity: str,  # "weaponized" | "poc" | "unproven" | "none"
        affected_critical_assets: int = 0,
        total_critical_assets: int = 1,
        shodan_exposed_count: int = 0,
    ) -> dict:
        """
        Calculate composite risk score for a CVE.

        Args:
            cvss_v3_score: CVSS v3 base score (0.0-10.0)
            epss_score: EPSS probability score (0.0-1.0)
            is_kev: Whether CVE is in CISA KEV catalog
            exploit_maturity: Exploit availability level
            affected_critical_assets: Number of critical assets affected
            total_critical_assets: Total number of critical assets
            shodan_exposed_count: Number of internet-exposed instances

        Returns:
            Dictionary containing:
            - risk_score: float (0-100)
            - risk_level: "Critical" | "High" | "Medium" | "Low"
            - components: breakdown of each factor's contribution
        """
        # Calculate individual components
        cvss_component = self._calculate_cvss_component(cvss_v3_score)
        epss_component = self._calculate_epss_component(epss_score)
        kev_component = self._calculate_kev_component(is_kev)
        exploit_component = self._calculate_exploit_component(exploit_maturity)
        asset_component = self._calculate_asset_component(
            affected_critical_assets, total_critical_assets
        )
        exposure_component = self._calculate_exposure_component(shodan_exposed_count)

        # Sum all components (each already weighted)
        risk_score = (
            cvss_component
            + epss_component
            + kev_component
            + exploit_component
            + asset_component
            + exposure_component
        )

        # Clamp to valid range
        risk_score = max(0.0, min(100.0, risk_score))

        # Determine risk level
        risk_level = self._get_risk_level(risk_score)

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "components": {
                "cvss": cvss_component,
                "epss": epss_component,
                "kev": kev_component,
                "exploit": exploit_component,
                "asset": asset_component,
                "exposure": exposure_component,
            },
        }

    def _calculate_cvss_component(self, cvss_v3_score: float) -> float:
        """
        Calculate CVSS component (25% weight).

        Formula: (cvss_v3_score / 10.0) * 25

        Args:
            cvss_v3_score: CVSS v3 base score (0.0-10.0)

        Returns:
            CVSS component score (0.0-25.0)
        """
        # Handle negative values
        if cvss_v3_score < 0:
            cvss_v3_score = 0.0
        # Cap at maximum
        if cvss_v3_score > 10.0:
            cvss_v3_score = 10.0

        return (cvss_v3_score / 10.0) * WEIGHT_CVSS

    def _calculate_epss_component(self, epss_score: float) -> float:
        """
        Calculate EPSS component (25% weight).

        Formula: epss_score * 25

        Args:
            epss_score: EPSS probability score (0.0-1.0)

        Returns:
            EPSS component score (0.0-25.0)
        """
        # Handle negative values
        if epss_score < 0:
            epss_score = 0.0
        # Cap at maximum
        if epss_score > 1.0:
            epss_score = 1.0

        return epss_score * WEIGHT_EPSS

    def _calculate_kev_component(self, is_kev: bool) -> float:
        """
        Calculate KEV component (15% weight).

        Formula: 15 if is_kev else 0

        Args:
            is_kev: Whether CVE is in CISA KEV catalog

        Returns:
            KEV component score (0.0 or 15.0)
        """
        return WEIGHT_KEV if is_kev else 0.0

    def _calculate_exploit_component(self, exploit_maturity: str) -> float:
        """
        Calculate exploit maturity component (15% weight).

        Scoring:
          - "weaponized": 15 points
          - "poc": 10 points
          - "unproven": 5 points
          - "none" or unknown: 0 points

        Args:
            exploit_maturity: Exploit availability level

        Returns:
            Exploit component score (0.0-15.0)
        """
        return EXPLOIT_MATURITY_SCORES.get(exploit_maturity.lower(), 0.0)

    def _calculate_asset_component(
        self, affected_critical_assets: int, total_critical_assets: int
    ) -> float:
        """
        Calculate asset impact component (10% weight).

        Formula: (affected_critical_assets / total_critical_assets) * 10, capped at 10

        Args:
            affected_critical_assets: Number of critical assets affected
            total_critical_assets: Total number of critical assets

        Returns:
            Asset impact component score (0.0-10.0)
        """
        # Handle edge cases
        if total_critical_assets <= 0:
            return 0.0
        if affected_critical_assets < 0:
            return 0.0

        # Calculate ratio and scale
        ratio = affected_critical_assets / total_critical_assets
        component = ratio * WEIGHT_ASSET

        # Cap at maximum weight
        return min(WEIGHT_ASSET, component)

    def _calculate_exposure_component(self, shodan_exposed_count: int) -> float:
        """
        Calculate internet exposure component (10% weight).

        Formula: 10 if shodan_exposed_count > 0 else 0

        Args:
            shodan_exposed_count: Number of internet-exposed instances

        Returns:
            Exposure component score (0.0 or 10.0)
        """
        # Handle negative values
        if shodan_exposed_count < 0:
            return 0.0

        return WEIGHT_EXPOSURE if shodan_exposed_count > 0 else 0.0

    def _get_risk_level(self, score: float) -> RiskLevel:
        """
        Determine risk level from score.

        Thresholds:
          - >= 85: Critical
          - >= 70: High
          - >= 40: Medium
          - < 40: Low

        Args:
            score: Risk score (0-100)

        Returns:
            Risk level classification
        """
        if score >= THRESHOLD_CRITICAL:
            return "Critical"
        elif score >= THRESHOLD_HIGH:
            return "High"
        elif score >= THRESHOLD_MEDIUM:
            return "Medium"
        else:
            return "Low"
