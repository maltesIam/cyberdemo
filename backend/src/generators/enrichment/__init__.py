"""Enrichment data generators for premium API simulation.

This module contains synthetic data generators that simulate responses
from premium cybersecurity APIs (Recorded Future, Tenable, CrowdStrike, Mandiant, etc.)
for demo purposes.

Generators are organized by type:
- Threat enrichment: For IPs, domains, URLs, hashes (RecordedFutureMock, CrowdStrikeSandboxMock, etc.)
- Vulnerability enrichment: For CVEs (RecordedFutureVulnMock, TenableVPRMock, QualysQDSMock)
"""

# Threat enrichment generators
from .recorded_future_mock import RecordedFutureMock
from .tenable_mock import TenableVPRMock
from .crowdstrike_mock import CrowdStrikeSandboxMock
from .mandiant_mock import MandiantMock
from .threatquotient_mock import ThreatQuotientMock
from .misp_mock import MISPMock

# Vulnerability enrichment generators
from .recorded_future_vuln_mock import RecordedFutureVulnMock
from .tenable_vuln_mock import TenableVPRMock as TenableVulnMock
from .qualys_vuln_mock import QualysQDSMock

__all__ = [
    # Threat enrichment
    "RecordedFutureMock",
    "TenableVPRMock",
    "CrowdStrikeSandboxMock",
    "MandiantMock",
    "ThreatQuotientMock",
    "MISPMock",
    # Vulnerability enrichment
    "RecordedFutureVulnMock",
    "TenableVulnMock",
    "QualysQDSMock",
]
