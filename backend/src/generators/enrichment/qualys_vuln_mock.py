"""Qualys Detection Score (QDS) generator (synthetic).

Simulates Qualys QDS scoring system based on:
- CVSS score (40% weight)
- EPSS score (20% weight)
- Known exploitation (10% weight)
- Threat indicators (30% weight): malware association + real-time threats

QDS scores range from 0 to 100.
"""

from datetime import datetime
from typing import Dict, Any


class QualysQDSMock:
    """Simulates Qualys Detection Score (QDS) for CVE enrichment."""

    def calculate_qds(
        self,
        cvss_score: float,
        epss_score: float,
        known_exploited: bool,
        malware_associated: bool,
        real_time_threat: bool
    ) -> Dict[str, Any]:
        """Calculate synthetic QDS score.

        QDS Score: 0 - 100

        Factors:
        - CVSS (40%): 0-10 -> 0-40 points
        - EPSS (20%): 0-1 -> 0-20 points
        - Exploit bonus (10%): 10 if known_exploited else 0
        - Threat indicators (30%): 15 if malware_associated + 15 if real_time_threat

        Args:
            cvss_score: CVSS v3 score (0-10)
            epss_score: EPSS score (0-1)
            known_exploited: Whether exploit is known
            malware_associated: Whether malware is associated with this CVE
            real_time_threat: Whether there is real-time threat activity

        Returns:
            Dictionary with QDS score, severity, component breakdown, and metadata
        """
        # CVSS component (40% weight, max 40 points)
        cvss_component = (cvss_score / 10.0) * 40

        # EPSS component (20% weight, max 20 points)
        epss_component = epss_score * 20

        # Exploit bonus (10% weight, 10 points if exploited)
        exploit_bonus = 10 if known_exploited else 0

        # Threat indicators (30% weight, 15 points each)
        threat_indicators = 0
        if malware_associated:
            threat_indicators += 15
        if real_time_threat:
            threat_indicators += 15

        # Calculate total QDS score
        qds_score = int(cvss_component + epss_component + exploit_bonus + threat_indicators)
        qds_score = min(100, max(0, qds_score))  # Clamp to [0, 100]

        # Determine QDS severity
        if qds_score >= 90:
            qds_severity = "Critical"
        elif qds_score >= 70:
            qds_severity = "High"
        elif qds_score >= 40:
            qds_severity = "Medium"
        else:
            qds_severity = "Low"

        return {
            "qds_score": qds_score,
            "qds_severity": qds_severity,
            "qds_components": {
                "cvss_component": round(cvss_component, 2),
                "epss_component": round(epss_component, 2),
                "exploit_bonus": exploit_bonus,
                "threat_indicators": threat_indicators
            },
            "enrichment_source": "synthetic_qualys_qds",
            "generated_at": datetime.utcnow().isoformat()
        }
