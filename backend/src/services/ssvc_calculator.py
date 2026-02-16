"""
SSVC (Stakeholder-Specific Vulnerability Categorization) Calculator.

Implements the SSVC decision tree for vulnerability prioritization:
- Exploitation Status: "active" | "poc" | "none"
- Automatable: True | False
- Technical Impact: "total" | "partial"
- Decision: "Act" | "Attend" | "Track*" | "Track"

Reference: https://www.cisa.gov/ssvc
"""
from typing import Dict, Optional


class SSVCCalculator:
    """
    Calculator for SSVC vulnerability prioritization decisions.

    SSVC Decision Tree:
    1. If exploitation is "active":
       - If automatable: "Act"
       - Else: "Attend"
    2. If exploitation is "poc":
       - If technical_impact is "total": "Attend"
       - Else: "Track*"
    3. If exploitation is "none": "Track"
    """

    # Exploitation status thresholds
    EPSS_ACTIVE_THRESHOLD = 0.70  # EPSS > 0.70 = active exploitation

    # Technical impact thresholds
    CVSS_TOTAL_THRESHOLD = 9.0  # CVSS >= 9.0 = total impact

    def calculate_ssvc_decision(
        self,
        is_kev: bool,
        epss_score: float,
        exploit_count: int,
        cvss_v3_score: float,
        cvss_v3_vector: Optional[str]
    ) -> Dict:
        """
        Calculate SSVC decision for a vulnerability.

        Args:
            is_kev: Whether CVE is in CISA KEV catalog
            epss_score: EPSS probability score (0.0 - 1.0)
            exploit_count: Number of known exploits
            cvss_v3_score: CVSS v3 base score (0.0 - 10.0)
            cvss_v3_vector: CVSS v3 vector string (e.g., "CVSS:3.1/AV:N/...")

        Returns:
            Dictionary with:
            - decision: "Act" | "Attend" | "Track*" | "Track"
            - exploitation: "active" | "poc" | "none"
            - automatable: bool
            - technical_impact: "total" | "partial"
            - mission_prevalence: "essential" | "supportive" | "minimal"
        """
        # Determine exploitation status
        exploitation = self._determine_exploitation_status(
            is_kev=is_kev,
            epss_score=epss_score,
            exploit_count=exploit_count
        )

        # Determine if automatable
        automatable = self._is_automatable(cvss_v3_vector)

        # Determine technical impact
        technical_impact = self._determine_technical_impact(
            cvss_v3_score=cvss_v3_score,
            cvss_v3_vector=cvss_v3_vector
        )

        # Apply decision matrix
        decision = self._apply_decision_matrix(
            exploitation=exploitation,
            automatable=automatable,
            technical_impact=technical_impact
        )

        return {
            "decision": decision,
            "exploitation": exploitation,
            "automatable": automatable,
            "technical_impact": technical_impact,
            "mission_prevalence": "essential"  # Placeholder for now
        }

    def _determine_exploitation_status(
        self,
        is_kev: bool,
        epss_score: float,
        exploit_count: int
    ) -> str:
        """
        Determine exploitation status.

        Logic:
        - "active" if: is_kev=True OR epss_score > 0.70
        - "poc" if: exploit_count > 0
        - "none" otherwise

        Args:
            is_kev: Whether CVE is in CISA KEV catalog
            epss_score: EPSS probability score (0.0 - 1.0)
            exploit_count: Number of known exploits

        Returns:
            "active" | "poc" | "none"
        """
        # Active exploitation takes priority
        if is_kev or epss_score > self.EPSS_ACTIVE_THRESHOLD:
            return "active"

        # POC if there are exploits
        if exploit_count > 0:
            return "poc"

        # No exploitation evidence
        return "none"

    def _is_automatable(self, cvss_v3_vector: Optional[str]) -> bool:
        """
        Determine if vulnerability is automatable.

        Automatable if CVSS vector has:
        - AV:N (Network attack vector)
        - AC:L (Low attack complexity)
        - PR:N (No privileges required)

        Args:
            cvss_v3_vector: CVSS v3 vector string

        Returns:
            True if automatable, False otherwise
        """
        if not cvss_v3_vector:
            return False

        parsed = self._parse_cvss_vector(cvss_v3_vector)
        if not parsed:
            return False

        # Must be Network, Low complexity, No privileges
        is_network = parsed.get("AV") == "N"
        is_low_complexity = parsed.get("AC") == "L"
        is_no_privileges = parsed.get("PR") == "N"

        return is_network and is_low_complexity and is_no_privileges

    def _determine_technical_impact(
        self,
        cvss_v3_score: float,
        cvss_v3_vector: Optional[str]
    ) -> str:
        """
        Determine technical impact.

        Logic:
        - "total" if: CVSS >= 9.0 OR (C:H AND I:H in vector)
        - "partial" otherwise

        Args:
            cvss_v3_score: CVSS v3 base score (0.0 - 10.0)
            cvss_v3_vector: CVSS v3 vector string

        Returns:
            "total" | "partial"
        """
        # High CVSS score = total impact
        if cvss_v3_score >= self.CVSS_TOTAL_THRESHOLD:
            return "total"

        # Check for high confidentiality AND high integrity
        if cvss_v3_vector:
            parsed = self._parse_cvss_vector(cvss_v3_vector)
            if parsed.get("C") == "H" and parsed.get("I") == "H":
                return "total"

        return "partial"

    def _parse_cvss_vector(self, vector: Optional[str]) -> Dict[str, str]:
        """
        Parse a CVSS v3 vector string into a dictionary.

        Example:
            "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
            ->
            {"AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "U", "C": "H", "I": "H", "A": "H"}

        Args:
            vector: CVSS v3 vector string

        Returns:
            Dictionary of metric -> value mappings, empty dict if invalid
        """
        if not vector:
            return {}

        # Check for CVSS prefix
        if not vector.startswith("CVSS:"):
            return {}

        result = {}

        try:
            # Split by / and skip the version prefix
            parts = vector.split("/")
            for part in parts[1:]:  # Skip "CVSS:3.1"
                if ":" in part:
                    metric, value = part.split(":", 1)
                    result[metric] = value
        except Exception:
            return {}

        return result

    def _apply_decision_matrix(
        self,
        exploitation: str,
        automatable: bool,
        technical_impact: str
    ) -> str:
        """
        Apply the SSVC decision matrix.

        Decision Matrix:
        - exploitation="active" AND automatable=True -> "Act"
        - exploitation="active" AND automatable=False -> "Attend"
        - exploitation="poc" AND technical_impact="total" -> "Attend"
        - exploitation="poc" AND technical_impact="partial" -> "Track*"
        - exploitation="none" -> "Track"

        Args:
            exploitation: "active" | "poc" | "none"
            automatable: True | False
            technical_impact: "total" | "partial"

        Returns:
            "Act" | "Attend" | "Track*" | "Track"
        """
        if exploitation == "active":
            if automatable:
                return "Act"
            return "Attend"

        if exploitation == "poc":
            if technical_impact == "total":
                return "Attend"
            return "Track*"

        # exploitation == "none"
        return "Track"
