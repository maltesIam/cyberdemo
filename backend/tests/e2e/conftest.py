"""
Shared fixtures for E2E Demo Scenario tests.

Provides pre-configured assets, alerts, and intel data for the three anchor scenarios.
"""

import pytest
from datetime import datetime, timezone
from typing import Optional

# Import from the investigation service module
from src.services.investigation_service import (
    InvestigationState,
    ActionOutcome,
    AssetData,
    AlertData,
    IntelData,
    CTEMData,
    PropagationData,
)


# ============================================================================
# Scenario 1: Auto-Containment (INC-ANCHOR-001)
# ============================================================================

@pytest.fixture
def scenario1_asset() -> AssetData:
    """WS-FIN-042: Standard finance workstation."""
    return AssetData(
        device_id="WS-FIN-042",
        hostname="WS-FIN-042.corp.acme.com",
        device_type="workstation",
        tags=["standard-user", "finance"],
        owner="john.doe@acme.com",
        department="Finance",
        criticality="standard"
    )


@pytest.fixture
def scenario1_alert() -> AlertData:
    """Alert for malicious QakBot hash on standard workstation."""
    return AlertData(
        alert_id="ALT-ANCHOR-001",
        incident_id="INC-ANCHOR-001",
        hash_sha256="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
        process_name="update_service.exe",
        cmdline="C:\\Windows\\Temp\\update_service.exe -nop -exec bypass -encodedcommand JABz...",
        mitre_technique="T1059.001",  # PowerShell
        severity="Critical"
    )


@pytest.fixture
def scenario1_intel() -> IntelData:
    """Intel showing malicious QakBot hash."""
    return IntelData(
        hash_sha256="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
        verdict="malicious",
        vt_score=58,
        vt_total=72,
        malware_labels=["QakBot", "Trojan.GenericKD"],
        confidence=95
    )


@pytest.fixture
def scenario1_ctem() -> CTEMData:
    """CTEM data for WS-FIN-042 - has vulnerabilities."""
    return CTEMData(
        device_id="WS-FIN-042",
        cve_list=["CVE-2024-1234", "CVE-2024-5678"],
        risk_color="Red",
        vulnerability_count=2
    )


@pytest.fixture
def scenario1_propagation() -> PropagationData:
    """Propagation data - hash found on 3 hosts."""
    return PropagationData(
        hash_sha256="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
        affected_hosts=["WS-FIN-042", "WS-FIN-043", "WS-FIN-044"],
        affected_count=3
    )


# ============================================================================
# Scenario 2: VIP Human-in-the-Loop (INC-ANCHOR-002)
# ============================================================================

@pytest.fixture
def scenario2_asset() -> AssetData:
    """LAPTOP-CFO-01: Executive VIP laptop."""
    return AssetData(
        device_id="LAPTOP-CFO-01",
        hostname="LAPTOP-CFO-01.corp.acme.com",
        device_type="laptop",
        tags=["vip", "executive"],
        owner="cfo@acme.com",
        department="Executive",
        criticality="vip"
    )


@pytest.fixture
def scenario2_alert() -> AlertData:
    """Alert for same malicious hash on VIP device."""
    return AlertData(
        alert_id="ALT-ANCHOR-002",
        incident_id="INC-ANCHOR-002",
        hash_sha256="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
        process_name="update_service.exe",
        cmdline="C:\\Windows\\Temp\\update_service.exe -nop -exec bypass -encodedcommand JABz...",
        mitre_technique="T1059.001",
        severity="Critical"
    )


@pytest.fixture
def scenario2_intel() -> IntelData:
    """Same malicious intel as scenario 1."""
    return IntelData(
        hash_sha256="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
        verdict="malicious",
        vt_score=58,
        vt_total=72,
        malware_labels=["QakBot", "Trojan.GenericKD"],
        confidence=95
    )


@pytest.fixture
def scenario2_ctem() -> CTEMData:
    """CTEM data for LAPTOP-CFO-01 - fully patched."""
    return CTEMData(
        device_id="LAPTOP-CFO-01",
        cve_list=[],
        risk_color="Green",
        vulnerability_count=0
    )


@pytest.fixture
def scenario2_propagation() -> PropagationData:
    """Propagation data - hash found on 3 hosts."""
    return PropagationData(
        hash_sha256="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
        affected_hosts=["WS-FIN-042", "WS-FIN-043", "LAPTOP-CFO-01"],
        affected_count=3
    )


# ============================================================================
# Scenario 3: False Positive (INC-ANCHOR-003)
# ============================================================================

@pytest.fixture
def scenario3_asset() -> AssetData:
    """SRV-DEV-03: Standard development server."""
    return AssetData(
        device_id="SRV-DEV-03",
        hostname="SRV-DEV-03.corp.acme.com",
        device_type="server",
        tags=["standard", "development"],
        owner="devops@acme.com",
        department="Engineering",
        criticality="standard"
    )


@pytest.fixture
def scenario3_alert() -> AlertData:
    """Alert for benign admin script falsely flagged."""
    return AlertData(
        alert_id="ALT-ANCHOR-003",
        incident_id="INC-ANCHOR-003",
        hash_sha256="b2c3d4e5f678901234567890123456789012345678901234567890123456abcd",
        process_name="deploy_script.ps1",
        cmdline="powershell.exe -File C:\\Scripts\\deploy_script.ps1 -Environment staging",
        mitre_technique="T1059.001",
        severity="Medium"
    )


@pytest.fixture
def scenario3_intel() -> IntelData:
    """Intel showing benign hash."""
    return IntelData(
        hash_sha256="b2c3d4e5f678901234567890123456789012345678901234567890123456abcd",
        verdict="benign",
        vt_score=0,
        vt_total=72,
        malware_labels=[],
        confidence=10
    )


@pytest.fixture
def scenario3_ctem() -> CTEMData:
    """CTEM data for SRV-DEV-03 - fully patched dev server."""
    return CTEMData(
        device_id="SRV-DEV-03",
        cve_list=[],
        risk_color="Green",
        vulnerability_count=0
    )


@pytest.fixture
def scenario3_propagation() -> PropagationData:
    """Propagation data - hash only on this server (normal for deploy script)."""
    return PropagationData(
        hash_sha256="b2c3d4e5f678901234567890123456789012345678901234567890123456abcd",
        affected_hosts=["SRV-DEV-03"],
        affected_count=1
    )


# ============================================================================
# Shared Services
# ============================================================================

@pytest.fixture
def mock_opensearch_client():
    """Mock OpenSearch client for E2E tests."""
    from unittest.mock import AsyncMock, MagicMock

    client = MagicMock()
    client.index = AsyncMock()
    client.search = AsyncMock(return_value={"hits": {"total": {"value": 0}, "hits": []}})
    client.get = AsyncMock()
    client.update = AsyncMock()

    return client


@pytest.fixture
def investigation_service():
    """Create an InvestigationService instance for testing."""
    from src.services.investigation_service import InvestigationService
    return InvestigationService()
