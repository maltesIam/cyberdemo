"""Tests for Demo Scenario Runner.

Tests the six anchor incident demo cases:
- INC-ANCHOR-001: Auto-containment (high confidence, non-VIP)
- INC-ANCHOR-002: VIP approval (VIP asset requiring human approval)
- INC-ANCHOR-003: False positive (low confidence, dev server)
- INC-ANCHOR-004: Ransomware multi-host (mass encryption, coordinated containment)
- INC-ANCHOR-005: Insider threat (privileged user, HR approval required)
- INC-ANCHOR-006: Supply chain attack (compromised software, organizational hunt)
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from src.demo.demo_runner import DemoRunner, DemoResult, DemoState
from src.services.policy_engine import ActionType


@pytest.fixture
def demo_runner():
    """Create DemoRunner instance."""
    return DemoRunner()


@pytest.fixture
def mock_opensearch():
    """Mock OpenSearch client responses."""
    mock_client = AsyncMock()

    # Mock incident data for INC-ANCHOR-001 (auto-containment)
    anchor_001 = {
        "incident_id": "INC-ANCHOR-001",
        "title": "Credential Theft - Mimikatz Activity",
        "severity": "Critical",
        "status": "open",
        "device_id": "WS-FIN-042",
        "hash_sha256": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
        "process_name": "mimikatz.exe",
        "cmdline": "mimikatz.exe sekurlsa::logonpasswords",
        "mitre_technique": "T1003.001",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Mock incident data for INC-ANCHOR-002 (VIP approval)
    anchor_002 = {
        "incident_id": "INC-ANCHOR-002",
        "title": "Suspicious PowerShell Execution - CFO Laptop",
        "severity": "High",
        "status": "open",
        "device_id": "LAPTOP-CFO-01",
        "hash_sha256": "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1",
        "process_name": "powershell.exe",
        "cmdline": "powershell.exe -nop -exec bypass -encodedcommand SGVsbG8gV29ybGQ=",
        "mitre_technique": "T1059.001",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Mock incident data for INC-ANCHOR-003 (false positive)
    anchor_003 = {
        "incident_id": "INC-ANCHOR-003",
        "title": "Process Injection - Dev Server",
        "severity": "Medium",
        "status": "open",
        "device_id": "SRV-DEV-03",
        "hash_sha256": "c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1b2",
        "process_name": "devtool.exe",
        "cmdline": "devtool.exe --debug --inject-test",
        "mitre_technique": "T1055",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Mock asset data
    asset_001 = {
        "asset_id": "WS-FIN-042",
        "hostname": "ws-fin-042.corp.local",
        "device_type": "workstation",
        "tags": ["finance", "standard"],
        "owner": "John Smith",
        "department": "Finance",
        "criticality": "standard",
    }

    asset_002 = {
        "asset_id": "LAPTOP-CFO-01",
        "hostname": "laptop-cfo-01.corp.local",
        "device_type": "laptop",
        "tags": ["vip", "executive"],
        "owner": "Jane Doe",
        "department": "Executive",
        "criticality": "critical",
    }

    asset_003 = {
        "asset_id": "SRV-DEV-03",
        "hostname": "srv-dev-03.corp.local",
        "device_type": "server",
        "tags": ["development", "non-production"],
        "owner": "Dev Team",
        "department": "Engineering",
        "criticality": "low",
    }

    # Mock intel data (malicious for 001, suspicious for 002, benign for 003)
    intel_001 = {
        "hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
        "verdict": "malicious",
        "vt_score": 72,
        "vt_total": 75,
        "malware_labels": ["mimikatz", "credential-stealer"],
        "confidence": 95,
    }

    intel_002 = {
        "hash": "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1",
        "verdict": "malicious",
        "vt_score": 55,
        "vt_total": 75,
        "malware_labels": ["suspicious-script", "powershell-backdoor"],
        "confidence": 75,
    }

    intel_003 = {
        "hash": "c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1b2",
        "verdict": "benign",
        "vt_score": 2,
        "vt_total": 75,
        "malware_labels": [],
        "confidence": 30,
    }

    # Mock CTEM data
    ctem_001 = {
        "device_id": "WS-FIN-042",
        "cve_list": ["CVE-2023-1234", "CVE-2023-5678"],
        "risk_color": "Red",
        "vulnerability_count": 2,
    }

    ctem_002 = {
        "device_id": "LAPTOP-CFO-01",
        "cve_list": ["CVE-2023-9999"],
        "risk_color": "Yellow",
        "vulnerability_count": 1,
    }

    ctem_003 = {
        "device_id": "SRV-DEV-03",
        "cve_list": [],
        "risk_color": "Green",
        "vulnerability_count": 0,
    }

    # Mock propagation data
    propagation_001 = {
        "hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
        "affected_hosts": ["WS-FIN-042", "WS-FIN-043", "WS-FIN-044"],
        "affected_count": 3,
    }

    propagation_002 = {
        "hash": "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1",
        "affected_hosts": ["LAPTOP-CFO-01"],
        "affected_count": 1,
    }

    propagation_003 = {
        "hash": "c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1b2",
        "affected_hosts": ["SRV-DEV-03"],
        "affected_count": 1,
    }

    # Configure mock responses
    def mock_search(index, body):
        """Return appropriate mock data based on index and query."""
        query = body.get("query", {})

        # Extract incident_id from query
        term = query.get("term", {})
        incident_id = term.get("incident_id")
        asset_id = term.get("asset_id")
        hash_value = term.get("hash") or term.get("file.sha256")
        device_id = term.get("device_id")

        if "siem-incidents" in index:
            if incident_id == "INC-ANCHOR-001":
                return {"hits": {"total": {"value": 1}, "hits": [{"_source": anchor_001}]}}
            elif incident_id == "INC-ANCHOR-002":
                return {"hits": {"total": {"value": 1}, "hits": [{"_source": anchor_002}]}}
            elif incident_id == "INC-ANCHOR-003":
                return {"hits": {"total": {"value": 1}, "hits": [{"_source": anchor_003}]}}

        elif "assets-inventory" in index:
            if asset_id == "WS-FIN-042" or device_id == "WS-FIN-042":
                return {"hits": {"total": {"value": 1}, "hits": [{"_source": asset_001}]}}
            elif asset_id == "LAPTOP-CFO-01" or device_id == "LAPTOP-CFO-01":
                return {"hits": {"total": {"value": 1}, "hits": [{"_source": asset_002}]}}
            elif asset_id == "SRV-DEV-03" or device_id == "SRV-DEV-03":
                return {"hits": {"total": {"value": 1}, "hits": [{"_source": asset_003}]}}

        elif "intel-indicators" in index:
            if hash_value == anchor_001["hash_sha256"]:
                return {"hits": {"total": {"value": 1}, "hits": [{"_source": intel_001}]}}
            elif hash_value == anchor_002["hash_sha256"]:
                return {"hits": {"total": {"value": 1}, "hits": [{"_source": intel_002}]}}
            elif hash_value == anchor_003["hash_sha256"]:
                return {"hits": {"total": {"value": 1}, "hits": [{"_source": intel_003}]}}

        elif "ctem" in index:
            if device_id == "WS-FIN-042":
                return {"hits": {"total": {"value": 1}, "hits": [{"_source": ctem_001}]}}
            elif device_id == "LAPTOP-CFO-01":
                return {"hits": {"total": {"value": 1}, "hits": [{"_source": ctem_002}]}}
            elif device_id == "SRV-DEV-03":
                return {"hits": {"total": {"value": 1}, "hits": [{"_source": ctem_003}]}}

        elif "edr-detections" in index:
            if hash_value == anchor_001["hash_sha256"]:
                return {
                    "hits": {
                        "total": {"value": 3},
                        "hits": [
                            {"_source": {"asset_id": h}}
                            for h in propagation_001["affected_hosts"]
                        ]
                    }
                }
            elif hash_value == anchor_002["hash_sha256"]:
                return {
                    "hits": {
                        "total": {"value": 1},
                        "hits": [{"_source": {"asset_id": "LAPTOP-CFO-01"}}]
                    }
                }
            elif hash_value == anchor_003["hash_sha256"]:
                return {
                    "hits": {
                        "total": {"value": 1},
                        "hits": [{"_source": {"asset_id": "SRV-DEV-03"}}]
                    }
                }

        # Default empty response
        return {"hits": {"total": {"value": 0}, "hits": []}}

    mock_client.search = AsyncMock(side_effect=mock_search)
    mock_client.index = AsyncMock(return_value={"result": "created"})
    mock_client.update = AsyncMock(return_value={"result": "updated"})

    return mock_client


# =============================================================================
# Test Case 1: Auto-containment
# =============================================================================

@pytest.mark.asyncio
async def test_demo_case_1_auto_contains(demo_runner, mock_opensearch):
    """Test Case 1: High confidence + non-VIP = auto-containment."""
    with patch(
        "src.demo.demo_runner.get_opensearch_client",
        AsyncMock(return_value=mock_opensearch)
    ):
        result = await demo_runner.run_case_1_auto_containment()

        assert result.incident_id == "INC-ANCHOR-001"
        assert result.outcome == "auto_contained"
        assert result.action_type == ActionType.CONTAIN
        assert result.containment_executed is True
        assert result.confidence_score >= 90  # High confidence
        assert result.ticket_id is not None
        assert result.postmortem_id is not None
        assert result.approval_required is False


# =============================================================================
# Test Case 2: VIP approval required
# =============================================================================

@pytest.mark.asyncio
async def test_demo_case_2_requests_approval(demo_runner, mock_opensearch):
    """Test Case 2: VIP asset = requires approval."""
    with patch(
        "src.demo.demo_runner.get_opensearch_client",
        AsyncMock(return_value=mock_opensearch)
    ):
        result = await demo_runner.run_case_2_vip_approval()

        assert result.incident_id == "INC-ANCHOR-002"
        assert result.outcome == "awaiting_approval"
        assert result.action_type == ActionType.REQUEST_APPROVAL
        assert result.containment_executed is False
        assert result.approval_required is True
        assert result.approval_request is not None
        assert result.approval_request["target_id"] == "LAPTOP-CFO-01"


# =============================================================================
# Test Case 3: False positive
# =============================================================================

@pytest.mark.asyncio
async def test_demo_case_3_marks_false_positive(demo_runner, mock_opensearch):
    """Test Case 3: Low confidence + dev server = false positive."""
    with patch(
        "src.demo.demo_runner.get_opensearch_client",
        AsyncMock(return_value=mock_opensearch)
    ):
        result = await demo_runner.run_case_3_false_positive()

        assert result.incident_id == "INC-ANCHOR-003"
        assert result.outcome == "false_positive"
        assert result.action_type == ActionType.MARK_FALSE_POSITIVE
        assert result.containment_executed is False
        assert result.confidence_score < 50  # Low confidence
        assert result.false_positive_marked is True


# =============================================================================
# Test All Cases
# =============================================================================

@pytest.mark.asyncio
async def test_demo_all_runs_original_three_cases(demo_runner, mock_opensearch):
    """Test running all demo cases includes the original three cases."""
    with patch(
        "src.demo.demo_runner.get_opensearch_client",
        AsyncMock(return_value=mock_opensearch)
    ):
        results = await demo_runner.run_all_cases()

        # Now returns 6 cases total
        assert len(results) == 6

        # Verify original three cases are present
        incident_ids = [r.incident_id for r in results]
        assert "INC-ANCHOR-001" in incident_ids
        assert "INC-ANCHOR-002" in incident_ids
        assert "INC-ANCHOR-003" in incident_ids

        # Verify outcomes for original cases
        outcomes = {r.incident_id: r.outcome for r in results}
        assert outcomes["INC-ANCHOR-001"] == "auto_contained"
        assert outcomes["INC-ANCHOR-002"] == "awaiting_approval"
        assert outcomes["INC-ANCHOR-003"] == "false_positive"


# =============================================================================
# Test Demo Status
# =============================================================================

@pytest.mark.asyncio
async def test_demo_status_returns_state(demo_runner, mock_opensearch):
    """Test demo status returns current state."""
    with patch(
        "src.demo.demo_runner.get_opensearch_client",
        AsyncMock(return_value=mock_opensearch)
    ):
        # Run a case first
        await demo_runner.run_case_1_auto_containment()

        status = await demo_runner.get_status()

        assert "state" in status
        assert "cases_run" in status
        assert "last_run" in status
        assert status["cases_run"] >= 1
        assert status["state"] in [s.value for s in DemoState]


# =============================================================================
# Test Case 4: Ransomware Multi-Host
# =============================================================================

@pytest.mark.asyncio
async def test_demo_case_4_ransomware_multihost(demo_runner, mock_opensearch):
    """Test Case 4: Ransomware multi-host = mass containment."""
    with patch(
        "src.demo.demo_runner.get_opensearch_client",
        AsyncMock(return_value=mock_opensearch)
    ):
        result = await demo_runner.run_case_4_ransomware_multihost()

        assert result.incident_id == "INC-ANCHOR-004"
        assert result.outcome == "mass_contained"
        assert result.action_type == ActionType.CONTAIN
        assert result.containment_executed is True
        assert result.mass_containment is True
        assert len(result.affected_hosts) >= 5  # 5+ hosts trigger mass containment
        assert result.executive_notified is True
        assert result.playbook_id is not None
        assert result.confidence_score >= 90  # High confidence for known ransomware


@pytest.mark.asyncio
async def test_demo_case_4_ransomware_has_timeline(demo_runner, mock_opensearch):
    """Test Case 4: Ransomware has proper timeline events."""
    with patch(
        "src.demo.demo_runner.get_opensearch_client",
        AsyncMock(return_value=mock_opensearch)
    ):
        result = await demo_runner.run_case_4_ransomware_multihost()

        assert len(result.timeline) >= 4
        actions = [entry["action"] for entry in result.timeline]
        assert "initial_detection" in actions
        assert "mass_containment_initiated" in actions
        assert "executive_notification" in actions


# =============================================================================
# Test Case 5: Insider Threat
# =============================================================================

@pytest.mark.asyncio
async def test_demo_case_5_insider_threat(demo_runner, mock_opensearch):
    """Test Case 5: Insider threat = HR approval required."""
    with patch(
        "src.demo.demo_runner.get_opensearch_client",
        AsyncMock(return_value=mock_opensearch)
    ):
        result = await demo_runner.run_case_5_insider_threat()

        assert result.incident_id == "INC-ANCHOR-005"
        assert result.outcome == "awaiting_hr_approval"
        assert result.action_type == ActionType.REQUEST_APPROVAL
        assert result.containment_executed is False  # Not yet - awaiting HR
        assert result.hr_approval_required is True
        assert result.legal_hold_initiated is True
        assert result.evidence_preserved is True
        assert result.ueba_risk_score is not None
        assert result.ueba_risk_score >= 80  # High risk score


@pytest.mark.asyncio
async def test_demo_case_5_insider_has_approval_request(demo_runner, mock_opensearch):
    """Test Case 5: Insider threat has proper approval request."""
    with patch(
        "src.demo.demo_runner.get_opensearch_client",
        AsyncMock(return_value=mock_opensearch)
    ):
        result = await demo_runner.run_case_5_insider_threat()

        assert result.approval_required is True
        assert result.approval_request is not None
        assert "approval_id" in result.approval_request
        assert "card_data" in result.approval_request
        assert "hr_flags" in result.approval_request["card_data"]


# =============================================================================
# Test Case 6: Supply Chain Attack
# =============================================================================

@pytest.mark.asyncio
async def test_demo_case_6_supply_chain(demo_runner, mock_opensearch):
    """Test Case 6: Supply chain attack = organizational hunt."""
    with patch(
        "src.demo.demo_runner.get_opensearch_client",
        AsyncMock(return_value=mock_opensearch)
    ):
        result = await demo_runner.run_case_6_supply_chain()

        assert result.incident_id == "INC-ANCHOR-006"
        assert result.outcome == "supply_chain_contained"
        assert result.action_type == ActionType.CONTAIN
        assert result.containment_executed is True
        assert result.hash_mismatch_detected is True
        assert result.vendor_contacted is True
        assert result.organizational_hunt_initiated is True
        assert len(result.iocs_blocked) > 0  # Should have blocked C2 domains/IPs
        assert result.playbook_id is not None


@pytest.mark.asyncio
async def test_demo_case_6_supply_chain_has_iocs(demo_runner, mock_opensearch):
    """Test Case 6: Supply chain has blocked IOCs."""
    with patch(
        "src.demo.demo_runner.get_opensearch_client",
        AsyncMock(return_value=mock_opensearch)
    ):
        result = await demo_runner.run_case_6_supply_chain()

        # Should have both domains and IPs blocked
        domains = [ioc for ioc in result.iocs_blocked if not ioc.replace(".", "").isdigit()]
        ips = [ioc for ioc in result.iocs_blocked if ioc.replace(".", "").isdigit()]

        assert len(domains) >= 1
        assert len(ips) >= 1


# =============================================================================
# Test All Cases (Updated for 6 cases)
# =============================================================================

@pytest.mark.asyncio
async def test_demo_all_runs_six_cases(demo_runner, mock_opensearch):
    """Test running all demo cases returns six results."""
    with patch(
        "src.demo.demo_runner.get_opensearch_client",
        AsyncMock(return_value=mock_opensearch)
    ):
        results = await demo_runner.run_all_cases()

        assert len(results) == 6

        # Verify each case is present
        incident_ids = [r.incident_id for r in results]
        assert "INC-ANCHOR-001" in incident_ids
        assert "INC-ANCHOR-002" in incident_ids
        assert "INC-ANCHOR-003" in incident_ids
        assert "INC-ANCHOR-004" in incident_ids
        assert "INC-ANCHOR-005" in incident_ids
        assert "INC-ANCHOR-006" in incident_ids

        # Verify outcomes
        outcomes = {r.incident_id: r.outcome for r in results}
        assert outcomes["INC-ANCHOR-001"] == "auto_contained"
        assert outcomes["INC-ANCHOR-002"] == "awaiting_approval"
        assert outcomes["INC-ANCHOR-003"] == "false_positive"
        assert outcomes["INC-ANCHOR-004"] == "mass_contained"
        assert outcomes["INC-ANCHOR-005"] == "awaiting_hr_approval"
        assert outcomes["INC-ANCHOR-006"] == "supply_chain_contained"


# =============================================================================
# Test Scenario Data Generators
# =============================================================================

def test_ransomware_scenario_data():
    """Test ransomware scenario data generation."""
    from src.demo.scenario_ransomware import generate_ransomware_scenario

    scenario = generate_ransomware_scenario()

    assert scenario.incident_id == "INC-ANCHOR-004"
    assert scenario.ransomware_family == "LockBit 3.0"
    assert len(scenario.affected_hosts) >= 5
    assert scenario.total_encrypted_files > 0
    assert len(scenario.timeline_events) > 0


def test_insider_threat_scenario_data():
    """Test insider threat scenario data generation."""
    from src.demo.scenario_insider_threat import generate_insider_threat_scenario

    scenario = generate_insider_threat_scenario()

    assert scenario.incident_id == "INC-ANCHOR-005"
    assert scenario.user_id == "jdoe.admin"
    assert scenario.risk_score >= 80
    assert scenario.total_data_transferred_mb > 0
    assert scenario.dlp_violations_count > 0
    assert len(scenario.hr_flags) > 0
    assert len(scenario.location_anomalies) > 0
    assert len(scenario.time_anomalies) > 0


def test_supply_chain_scenario_data():
    """Test supply chain scenario data generation."""
    from src.demo.scenario_supply_chain import generate_supply_chain_scenario

    scenario = generate_supply_chain_scenario()

    assert scenario.incident_id == "INC-ANCHOR-006"
    assert scenario.software_name == "UpdateHelper.exe"
    assert scenario.vendor_name == "TrustedVendor Inc."
    assert scenario.compromised_hash != scenario.legitimate_hash
    assert len(scenario.affected_assets) >= 5
    assert len(scenario.anomalous_behaviors) > 0
    assert len(scenario.c2_domains) > 0
    assert len(scenario.c2_ips) > 0
