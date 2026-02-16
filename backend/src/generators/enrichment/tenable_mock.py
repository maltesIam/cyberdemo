"""Tenable Vulnerability Priority Rating (VPR) generator (synthetic).

Simulates Tenable's VPR scoring system based on:
- CVSS score (35% weight)
- Threat intelligence (35% weight): EPSS + known exploits
- Asset criticality (20% weight)
- Product coverage (10% weight)

VPR scores range from 0.0 to 10.0.
"""

from datetime import datetime
from typing import Dict, Any


class TenableVPRMock:
    """Simulates Tenable Vulnerability Priority Rating (VPR)."""

    def calculate_vpr(
        self,
        cvss_score: float,
        epss_score: float,
        asset_criticality: str,
        known_exploited: bool,
        age_days: int,
        product_coverage: float
    ) -> Dict[str, Any]:
        """Calculate synthetic VPR score.

        VPR Score: 0.0 - 10.0

        Factors:
        - CVSS (35%): 0-10 → 0-3.5 points
        - Threat (35%): EPSS (2.5 points max) + exploit (1.0 point max) → 0-3.5 points
        - Asset criticality (20%): critical=2.0, high=1.5, medium=1.0, low=0.5
        - Product coverage (10%): 0-1 → 0-1.0 points

        Args:
            cvss_score: CVSS v3 score (0-10)
            epss_score: EPSS score (0-1)
            asset_criticality: Asset criticality level (critical, high, medium, low)
            known_exploited: Whether exploit is known
            age_days: Days since CVE published (not currently used in calculation)
            product_coverage: Percentage of assets with this product (0-1)

        Returns:
            Dictionary with VPR score, component breakdown, and metadata
        """
        # CVSS component (35% weight, max 3.5 points)
        cvss_component = (cvss_score / 10.0) * 3.5

        # Threat component (35% weight, max 3.5 points)
        # EPSS contributes up to 2.5 points
        threat_base = epss_score * 2.5
        # Known exploit adds up to 1.0 point
        threat_exploit = 1.0 if known_exploited else 0.0
        threat_component = min(3.5, threat_base + threat_exploit)

        # Asset criticality component (20% weight, max 2.0 points)
        criticality_map = {
            "critical": 2.0,
            "high": 1.5,
            "medium": 1.0,
            "low": 0.5
        }
        criticality_component = criticality_map.get(asset_criticality.lower(), 1.0)

        # Product coverage component (10% weight, max 1.0 point)
        # Higher coverage = more assets affected = higher VPR
        coverage_component = product_coverage * 1.0

        # Calculate total VPR score
        vpr_score = cvss_component + threat_component + criticality_component + coverage_component
        vpr_score = min(10.0, max(0.0, vpr_score))  # Clamp to [0.0, 10.0]

        return {
            "vpr_score": round(vpr_score, 1),
            "vpr_components": {
                "cvss": round(cvss_component, 2),
                "threat": round(threat_component, 2),
                "asset_criticality": round(criticality_component, 2),
                "product_coverage": round(coverage_component, 2)
            },
            "enrichment_source": "synthetic_tenable",
            "generated_at": datetime.utcnow().isoformat()
        }
