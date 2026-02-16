"""Recorded Future vulnerability risk score generator (synthetic).

Simulates Recorded Future's vulnerability risk scoring based on:
- CVSS scores (40% weight)
- EPSS scores (30% weight)
- Known exploitation (20% weight)
- Vulnerability age (10% weight)

The risk scores correlate highly with real CVSS+EPSS data for realistic demos.
"""

import random
from datetime import datetime
from typing import Dict, List, Any


class RecordedFutureVulnMock:
    """Simulates Recorded Future vulnerability risk scoring for CVE enrichment."""

    def __init__(self, seed: int = None):
        """Initialize the mock generator.

        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)

    def calculate_risk_score(
        self,
        cve_id: str,
        cvss_score: float,
        epss_score: float,
        known_exploited: bool,
        age_days: int
    ) -> Dict[str, Any]:
        """Calculate synthetic risk score based on multiple factors.

        Risk Score: 0-100 where 100 is highest risk

        Factors:
        - CVSS score (40% weight): 0-10 -> 0-40 points
        - EPSS score (30% weight): 0-1 -> 0-30 points
        - Known exploited (20% weight): True -> +20 points
        - Age/freshness (10% weight): Recent = higher risk
          - 0-30 days: 10 points
          - 31-90 days: 7 points
          - 91-365 days: 4 points
          - >365 days: 2 points

        Args:
            cve_id: CVE identifier
            cvss_score: CVSS v3 score (0-10)
            epss_score: EPSS score (0-1)
            known_exploited: Whether exploit is known
            age_days: Days since CVE published

        Returns:
            Dictionary with risk score, category, threat actors, campaigns, and vector breakdown
        """
        # CVSS component (40% weight)
        cvss_component = (cvss_score / 10.0) * 40

        # EPSS component (30% weight)
        epss_component = epss_score * 30

        # Known exploited component (20% weight)
        exploit_component = 20 if known_exploited else 0

        # Age component (10% weight) - newer is riskier
        if age_days <= 30:
            age_component = 10
        elif age_days <= 90:
            age_component = 7
        elif age_days <= 365:
            age_component = 4
        else:
            age_component = 2

        # Calculate total risk score
        risk_score = int(cvss_component + epss_component + exploit_component + age_component)
        risk_score = min(100, max(0, risk_score))  # Clamp to [0, 100]

        # Determine risk category
        if risk_score >= 90:
            risk_category = "Critical"
        elif risk_score >= 70:
            risk_category = "High"
        elif risk_score >= 50:
            risk_category = "Medium"
        else:
            risk_category = "Low"

        # Generate threat actors (only for high-risk exploited CVEs)
        threat_actors = self._generate_threat_actors(risk_score, known_exploited)

        # Generate campaigns (only for recent high-risk CVEs)
        campaigns = self._generate_campaigns(risk_score, age_days)

        return {
            "risk_score": risk_score,
            "risk_category": risk_category,
            "threat_actors": threat_actors,
            "campaigns": campaigns,
            "risk_vector": {
                "cvss_component": round(cvss_component, 2),
                "epss_component": round(epss_component, 2),
                "exploit_component": exploit_component,
                "age_component": age_component
            },
            "enrichment_source": "synthetic_recorded_future_vuln",
            "generated_at": datetime.utcnow().isoformat()
        }

    def _generate_threat_actors(self, risk_score: int, known_exploited: bool) -> List[str]:
        """Generate synthetic threat actors based on risk score.

        APT groups are only assigned to high-risk vulnerabilities (score >=80)
        with known exploits to ensure realistic synthetic data.

        Args:
            risk_score: Calculated risk score (0-100)
            known_exploited: Whether vulnerability has known exploits

        Returns:
            List of threat actor names
        """
        # High sophistication APT groups (publicly known)
        high_sophistication_apts = [
            "APT28", "APT29", "APT41", "Lazarus Group", "FIN7", "Carbanak",
            "OilRig", "Turla", "Equation Group", "DarkHotel"
        ]

        # Only assign APTs to high-risk exploited vulnerabilities
        if risk_score >= 80 and known_exploited:
            return random.sample(high_sophistication_apts, random.randint(1, 3))

        return []

    def _generate_campaigns(self, risk_score: int, age_days: int) -> List[str]:
        """Generate synthetic campaigns based on risk score and age.

        Campaigns are only generated for recent (<=90 days) high-risk (>=70) CVEs
        to simulate active exploitation campaigns.

        Args:
            risk_score: Calculated risk score (0-100)
            age_days: Days since CVE published

        Returns:
            List of campaign names
        """
        campaign_templates = [
            "Operation {adjective} {noun}",
            "{adjective} {animal} Campaign",
            "Project {noun}",
            "{adjective} {weather} Operation"
        ]

        adjectives = [
            "Silent", "Dark", "Hidden", "Persistent", "Advanced", "Covert",
            "Stealthy", "Sophisticated", "Complex", "Targeted"
        ]
        nouns = [
            "Phoenix", "Dragon", "Eagle", "Wolf", "Serpent", "Hawk", "Tiger",
            "Storm", "Thunder", "Lightning"
        ]
        animals = ["Panda", "Bear", "Cat", "Elephant", "Monkey", "Spider"]
        weather = ["Storm", "Thunder", "Lightning", "Blizzard", "Hurricane"]

        campaigns = []

        # Only generate campaigns for recent high-risk vulnerabilities
        if age_days <= 90 and risk_score >= 70:
            num_campaigns = random.randint(1, 2)
            for _ in range(num_campaigns):
                template = random.choice(campaign_templates)
                campaign_name = template.format(
                    adjective=random.choice(adjectives),
                    noun=random.choice(nouns),
                    animal=random.choice(animals),
                    weather=random.choice(weather)
                )
                campaigns.append(campaign_name)

        return campaigns
