"""
AlienVault OTX (Open Threat Exchange) API Client.

OTX provides threat intelligence including:
- Pulses (threat feeds)
- IOC reputation
- Malware families
- MITRE ATT&CK TTPs

API Documentation: https://otx.alienvault.com/api
Free tier: Unlimited requests (requires API key)
"""

import logging
from typing import Optional, Dict, List

import httpx


logger = logging.getLogger(__name__)

# Constants
OTX_API_BASE_URL = "https://otx.alienvault.com/api/v1"
MAX_ITEMS_PER_SOURCE = 100
DEFAULT_TIMEOUT = 30  # seconds


class OTXClient:
    """
    Client for AlienVault OTX API.

    Provides threat intelligence for IPs, domains, and file hashes.
    """

    def __init__(self, api_key: str, timeout: int = DEFAULT_TIMEOUT):
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def fetch_ip_reputation(self, ip: str) -> Optional[Dict]:
        """
        Fetch IP reputation from OTX.

        Returns:
            Dict with IP reputation data on success, None on failure.
            Dict structure:
            {
                "indicator_value": str,
                "indicator_type": "ip",
                "reputation_score": int,  # 0-100
                "malware_families": List[str],
                "threat_types": List[str],
                "attack_techniques": List[str],  # MITRE ATT&CK
                "pulses": List[Dict]
            }
        """
        url = f"{OTX_API_BASE_URL}/indicators/IPv4/{ip}/general"
        headers = {"X-OTX-API-KEY": self.api_key}

        try:
            response = await self.client.get(url, headers=headers)

            if response.status_code == 403:
                logger.error(f"OTX API authentication failed for IP {ip}")
                return None

            if response.status_code != 200:
                logger.error(f"OTX API error for IP {ip}: {response.status_code}")
                return None

            data = response.json()

            # Fetch additional pulse data
            pulses = await self._fetch_pulses(ip, "IPv4")

            return self._parse_ip_response(data, ip, pulses)

        except TimeoutError:
            logger.error(f"Timeout fetching OTX data for IP {ip}")
            return None

        except httpx.TimeoutException:
            logger.error(f"HTTP timeout fetching OTX data for IP {ip}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error fetching OTX data for IP {ip}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching OTX data for IP {ip}: {e}")
            return None

    async def fetch_domain_reputation(self, domain: str) -> Optional[Dict]:
        """Fetch domain reputation from OTX."""
        url = f"{OTX_API_BASE_URL}/indicators/domain/{domain}/general"
        headers = {"X-OTX-API-KEY": self.api_key}

        try:
            response = await self.client.get(url, headers=headers)

            if response.status_code != 200:
                logger.error(f"OTX API error for domain {domain}: {response.status_code}")
                return None

            data = response.json()
            pulses = await self._fetch_pulses(domain, "domain")

            return self._parse_domain_response(data, domain, pulses)

        except Exception as e:
            logger.error(f"Error fetching OTX data for domain {domain}: {e}")
            return None

    async def fetch_hash_reputation(self, file_hash: str) -> Optional[Dict]:
        """Fetch file hash reputation from OTX."""
        url = f"{OTX_API_BASE_URL}/indicators/file/{file_hash}/general"
        headers = {"X-OTX-API-KEY": self.api_key}

        try:
            response = await self.client.get(url, headers=headers)

            if response.status_code != 200:
                logger.error(f"OTX API error for hash {file_hash}: {response.status_code}")
                return None

            data = response.json()
            pulses = await self._fetch_pulses(file_hash, "file")

            return self._parse_hash_response(data, file_hash, pulses)

        except Exception as e:
            logger.error(f"Error fetching OTX data for hash {file_hash}: {e}")
            return None

    async def _fetch_pulses(self, indicator: str, indicator_type: str) -> List[Dict]:
        """Fetch pulses associated with an indicator."""
        try:
            if indicator_type == "IPv4":
                url = f"{OTX_API_BASE_URL}/indicators/IPv4/{indicator}/general"
            elif indicator_type == "domain":
                url = f"{OTX_API_BASE_URL}/indicators/domain/{indicator}/general"
            elif indicator_type == "file":
                url = f"{OTX_API_BASE_URL}/indicators/file/{indicator}/general"
            else:
                return []

            headers = {"X-OTX-API-KEY": self.api_key}
            response = await self.client.get(url, headers=headers)

            if response.status_code != 200:
                return []

            data = response.json()
            pulses = data.get("pulse_info", {}).get("pulses", [])

            return pulses[:10]  # Limit to 10 most relevant pulses

        except Exception as e:
            logger.error(f"Error fetching pulses for {indicator}: {e}")
            return []

    def _parse_ip_response(
        self,
        data: Dict,
        ip: str,
        pulses: List[Dict]
    ) -> Optional[Dict]:
        """Parse OTX IP response into internal format."""
        try:
            # Calculate reputation score based on pulses
            reputation_score = self._calculate_reputation_score(pulses)

            # Extract malware families
            malware_families = []
            threat_types = []
            attack_techniques = []

            for pulse in pulses:
                # Extract malware families from pulse tags
                tags = pulse.get("tags", [])
                for tag in tags:
                    if "malware" in tag.lower() or "trojan" in tag.lower():
                        malware_families.append(tag)

                # Extract threat types
                if pulse.get("targeted_countries"):
                    threat_types.append("targeted_attack")

                # Extract MITRE ATT&CK techniques
                attack_ids = pulse.get("attack_ids", [])
                for attack in attack_ids:
                    technique_id = attack.get("id", "")
                    if technique_id:
                        attack_techniques.append(technique_id)

            # Remove duplicates
            malware_families = list(set(malware_families))
            threat_types = list(set(threat_types))
            attack_techniques = list(set(attack_techniques))

            # Format pulse data
            pulse_summaries = [
                {
                    "pulse_id": pulse.get("id"),
                    "pulse_name": pulse.get("name"),
                    "created": pulse.get("created"),
                    "author": pulse.get("author_name")
                }
                for pulse in pulses[:5]  # Top 5 pulses
            ]

            return {
                "indicator_value": ip,
                "indicator_type": "ip",
                "reputation_score": reputation_score,
                "malware_families": malware_families,
                "threat_types": threat_types,
                "attack_techniques": attack_techniques,
                "pulses": pulse_summaries
            }

        except Exception as e:
            logger.error(f"Error parsing OTX IP response for {ip}: {e}")
            return None

    def _parse_domain_response(
        self,
        data: Dict,
        domain: str,
        pulses: List[Dict]
    ) -> Optional[Dict]:
        """Parse OTX domain response."""
        try:
            reputation_score = self._calculate_reputation_score(pulses)

            return {
                "indicator_value": domain,
                "indicator_type": "domain",
                "reputation_score": reputation_score,
                "malware_families": [],
                "threat_types": [],
                "attack_techniques": [],
                "pulses": [
                    {
                        "pulse_id": pulse.get("id"),
                        "pulse_name": pulse.get("name"),
                        "created": pulse.get("created")
                    }
                    for pulse in pulses[:5]
                ]
            }

        except Exception as e:
            logger.error(f"Error parsing OTX domain response for {domain}: {e}")
            return None

    def _parse_hash_response(
        self,
        data: Dict,
        file_hash: str,
        pulses: List[Dict]
    ) -> Optional[Dict]:
        """Parse OTX file hash response."""
        try:
            reputation_score = self._calculate_reputation_score(pulses)

            malware_families = []
            for pulse in pulses:
                tags = pulse.get("tags", [])
                malware_families.extend([
                    tag for tag in tags
                    if any(keyword in tag.lower() for keyword in ["malware", "trojan", "ransomware"])
                ])

            malware_families = list(set(malware_families))

            return {
                "indicator_value": file_hash,
                "indicator_type": "hash",
                "reputation_score": reputation_score,
                "malware_families": malware_families,
                "threat_types": ["malware"],
                "attack_techniques": [],
                "pulses": [
                    {
                        "pulse_id": pulse.get("id"),
                        "pulse_name": pulse.get("name")
                    }
                    for pulse in pulses[:5]
                ]
            }

        except Exception as e:
            logger.error(f"Error parsing OTX hash response for {file_hash}: {e}")
            return None

    def _calculate_reputation_score(self, pulses: List[Dict]) -> int:
        """
        Calculate reputation score (0-100) based on pulses.

        More pulses = higher malicious score.
        """
        if not pulses:
            return 0  # Clean

        # Base score on number of pulses
        num_pulses = len(pulses)

        if num_pulses >= 10:
            return 100  # Definitely malicious
        elif num_pulses >= 5:
            return 80
        elif num_pulses >= 3:
            return 60
        elif num_pulses >= 1:
            return 40
        else:
            return 0

    async def fetch_indicators(
        self,
        indicators: List[Dict]
    ) -> List[Optional[Dict]]:
        """
        Fetch reputation for multiple indicators.

        Respects MAX_ITEMS_PER_SOURCE limit (100).

        Args:
            indicators: List of dicts with "type" and "value" keys
        """
        # Limit to MAX_ITEMS_PER_SOURCE
        if len(indicators) > MAX_ITEMS_PER_SOURCE:
            logger.warning(
                f"Limiting OTX fetch from {len(indicators)} to {MAX_ITEMS_PER_SOURCE}"
            )
            indicators = indicators[:MAX_ITEMS_PER_SOURCE]

        results = []

        for indicator in indicators:
            indicator_type = indicator.get("type")
            indicator_value = indicator.get("value")

            if indicator_type == "ip":
                result = await self.fetch_ip_reputation(indicator_value)
            elif indicator_type == "domain":
                result = await self.fetch_domain_reputation(indicator_value)
            elif indicator_type == "hash":
                result = await self.fetch_hash_reputation(indicator_value)
            else:
                logger.warning(f"Unknown indicator type: {indicator_type}")
                result = None

            results.append(result)

        return results
