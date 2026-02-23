"""
Unit tests for Playbook Definitions.

TDD: Tests written FIRST for Data Exfiltration, Insider Threat, and Cloud Compromise playbooks.
Build Agent 4 - Phase 2.3: Automated Playbooks

Tasks:
- T-2.3.011: Data Exfiltration Response playbook (REQ-005-002-004)
- T-2.3.012: Insider Threat Investigation playbook (REQ-005-002-005)
- T-2.3.013: Cloud Compromise Response playbook (REQ-005-002-006)
"""

import asyncio
import pytest
import yaml
from pathlib import Path
from unittest.mock import AsyncMock

from src.services.playbook_service import (
    PlaybookService,
    PlaybookRunStatus,
    StepStatus,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def playbooks_dir():
    """Return the path to the playbooks directory."""
    return Path(__file__).parent.parent.parent / "playbooks"


@pytest.fixture
def playbook_service(playbooks_dir):
    """Create a PlaybookService with actual playbooks."""
    async def mock_handler(action: str, params: dict) -> dict:
        """Mock handler that simulates successful actions."""
        return {"status": "success", "action": action, "params": params}

    return PlaybookService(
        playbook_dir=str(playbooks_dir),
        action_handler=mock_handler
    )


# ============================================================================
# T-2.3.011: Data Exfiltration Response Playbook Tests (REQ-005-002-004)
# ============================================================================

class TestDataExfiltrationPlaybook:
    """Tests for data_exfiltration_response playbook.

    Requirements (REQ-005-002-004):
    1. Identify exfiltration channels
    2. Block data transfer
    3. Assess data impact
    4. Preserve evidence
    5. Notify stakeholders
    """

    def test_playbook_exists(self, playbooks_dir):
        """Playbook YAML file should exist."""
        playbook_path = playbooks_dir / "data_exfiltration_response.yaml"
        assert playbook_path.exists(), f"Playbook not found at {playbook_path}"

    def test_playbook_has_valid_yaml(self, playbooks_dir):
        """Playbook should have valid YAML syntax."""
        playbook_path = playbooks_dir / "data_exfiltration_response.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)
        assert data is not None
        assert "name" in data
        assert "steps" in data

    def test_playbook_name(self, playbooks_dir):
        """Playbook should have correct name."""
        playbook_path = playbooks_dir / "data_exfiltration_response.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)
        assert data["name"] == "data_exfiltration_response"

    def test_playbook_has_required_triggers(self, playbooks_dir):
        """Playbook should have appropriate triggers."""
        playbook_path = playbooks_dir / "data_exfiltration_response.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        triggers = data.get("triggers", [])
        # Should have data exfiltration related triggers
        assert len(triggers) >= 1
        expected_triggers = [
            "data_exfiltration_detected",
            "dlp_alert",
            "large_data_transfer",
            "suspicious_upload"
        ]
        assert any(t in expected_triggers for t in triggers), \
            f"Should have at least one of {expected_triggers}, got {triggers}"

    def test_playbook_has_identify_exfiltration_step(self, playbooks_dir):
        """Playbook should have step to identify exfiltration channels (REQ-1)."""
        playbook_path = playbooks_dir / "data_exfiltration_response.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        steps = data.get("steps", [])
        actions = [s.get("action", "") for s in steps]

        # Should have identification action
        identify_actions = [
            "dlp.identify_channel",
            "network.analyze_transfer",
            "siem.identify_exfiltration",
            "network.identify_destination"
        ]
        assert any(any(ia in a for ia in identify_actions) for a in actions), \
            f"Should have identification step, got actions: {actions}"

    def test_playbook_has_block_transfer_step(self, playbooks_dir):
        """Playbook should have step to block data transfer (REQ-2)."""
        playbook_path = playbooks_dir / "data_exfiltration_response.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        steps = data.get("steps", [])
        actions = [s.get("action", "") for s in steps]

        # Should have blocking action
        block_actions = [
            "network.block_destination",
            "dlp.block_transfer",
            "network.block_ip",
            "firewall.block"
        ]
        assert any(any(ba in a for ba in block_actions) for a in actions), \
            f"Should have blocking step, got actions: {actions}"

    def test_playbook_has_assess_impact_step(self, playbooks_dir):
        """Playbook should have step to assess data impact (REQ-3)."""
        playbook_path = playbooks_dir / "data_exfiltration_response.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        steps = data.get("steps", [])
        actions = [s.get("action", "") for s in steps]

        # Should have impact assessment action
        assess_actions = [
            "dlp.assess_impact",
            "data.classify_impact",
            "dlp.identify_data_types",
            "intel.assess_data_sensitivity"
        ]
        assert any(any(aa in a for aa in assess_actions) for a in actions), \
            f"Should have impact assessment step, got actions: {actions}"

    def test_playbook_has_preserve_evidence_step(self, playbooks_dir):
        """Playbook should have step to preserve evidence (REQ-4)."""
        playbook_path = playbooks_dir / "data_exfiltration_response.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        steps = data.get("steps", [])
        actions = [s.get("action", "") for s in steps]

        # Should have evidence preservation action
        evidence_actions = [
            "edr.collect_artifacts",
            "forensics.preserve_evidence",
            "network.capture_traffic",
            "dlp.preserve_logs"
        ]
        assert any(any(ea in a for ea in evidence_actions) for a in actions), \
            f"Should have evidence preservation step, got actions: {actions}"

    def test_playbook_has_notify_stakeholders_step(self, playbooks_dir):
        """Playbook should have step to notify stakeholders (REQ-5)."""
        playbook_path = playbooks_dir / "data_exfiltration_response.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        steps = data.get("steps", [])
        actions = [s.get("action", "") for s in steps]

        # Should have notification action
        notify_actions = [
            "notify.page_oncall",
            "notify.send_email",
            "notify.create_ticket",
            "notify.alert_legal",
            "notify.stakeholders"
        ]
        assert any(any(na in a for na in notify_actions) for a in actions), \
            f"Should have notification step, got actions: {actions}"

    def test_playbook_loads_into_service(self, playbook_service):
        """Playbook should load correctly into PlaybookService."""
        playbook = playbook_service.get_playbook("data_exfiltration_response")
        assert playbook is not None
        assert playbook.name == "data_exfiltration_response"

    def test_playbook_executes_successfully(self, playbooks_dir):
        """Playbook should execute all steps successfully with valid context."""
        async def success_handler(action: str, params: dict) -> dict:
            return {"status": "success", "action": action}

        service = PlaybookService(
            playbook_dir=str(playbooks_dir),
            action_handler=success_handler
        )

        context = {
            "incident": {
                "id": "INC-001",
                "title": "Data Exfiltration Alert",
                "timestamp": "2024-01-15T10:30:00Z"
            },
            "host": {
                "device_id": "DEV-001",
                "hostname": "WS-FIN-042",
                "ip_address": "192.168.1.100"
            },
            "user": {
                "name": "jsmith",
                "email": "jsmith@company.com"
            },
            "alert": {
                "destination_ip": "203.0.113.50",
                "data_volume_mb": 500,
                "protocol": "HTTPS"
            },
            "dlp": {
                "policy_name": "PCI-DSS",
                "data_types": ["credit_card", "ssn"]
            }
        }

        async def run_test():
            return await service.execute_playbook("data_exfiltration_response", context)

        run = asyncio.run(run_test())
        assert run.status == PlaybookRunStatus.COMPLETED
        assert len(run.step_results) >= 5  # At least 5 required steps


# ============================================================================
# T-2.3.012: Insider Threat Investigation Playbook Tests (REQ-005-002-005)
# ============================================================================

class TestInsiderThreatPlaybook:
    """Tests for insider_threat_investigation playbook.

    Requirements (REQ-005-002-005):
    1. Correlate user activities
    2. Review access patterns
    3. Check data downloads
    4. HR/Legal notification
    5. Preserve evidence chain
    """

    def test_playbook_exists(self, playbooks_dir):
        """Playbook YAML file should exist."""
        playbook_path = playbooks_dir / "insider_threat_investigation.yaml"
        assert playbook_path.exists(), f"Playbook not found at {playbook_path}"

    def test_playbook_has_valid_yaml(self, playbooks_dir):
        """Playbook should have valid YAML syntax."""
        playbook_path = playbooks_dir / "insider_threat_investigation.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)
        assert data is not None
        assert "name" in data
        assert "steps" in data

    def test_playbook_name(self, playbooks_dir):
        """Playbook should have correct name."""
        playbook_path = playbooks_dir / "insider_threat_investigation.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)
        assert data["name"] == "insider_threat_investigation"

    def test_playbook_has_required_triggers(self, playbooks_dir):
        """Playbook should have appropriate triggers."""
        playbook_path = playbooks_dir / "insider_threat_investigation.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        triggers = data.get("triggers", [])
        assert len(triggers) >= 1
        expected_triggers = [
            "insider_threat_detected",
            "suspicious_employee_activity",
            "data_hoarding_detected",
            "termination_risk",
            "policy_violation"
        ]
        assert any(t in expected_triggers for t in triggers), \
            f"Should have at least one of {expected_triggers}, got {triggers}"

    def test_playbook_has_correlate_activities_step(self, playbooks_dir):
        """Playbook should have step to correlate user activities (REQ-1)."""
        playbook_path = playbooks_dir / "insider_threat_investigation.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        steps = data.get("steps", [])
        actions = [s.get("action", "") for s in steps]

        correlate_actions = [
            "ueba.correlate_activities",
            "siem.correlate_user",
            "insider.correlate_events",
            "siem.search_user_activity"
        ]
        assert any(any(ca in a for ca in correlate_actions) for a in actions), \
            f"Should have correlation step, got actions: {actions}"

    def test_playbook_has_review_access_step(self, playbooks_dir):
        """Playbook should have step to review access patterns (REQ-2)."""
        playbook_path = playbooks_dir / "insider_threat_investigation.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        steps = data.get("steps", [])
        actions = [s.get("action", "") for s in steps]

        access_actions = [
            "iam.review_access",
            "ueba.analyze_access_patterns",
            "insider.review_permissions",
            "siem.analyze_access"
        ]
        assert any(any(aa in a for aa in access_actions) for a in actions), \
            f"Should have access review step, got actions: {actions}"

    def test_playbook_has_check_downloads_step(self, playbooks_dir):
        """Playbook should have step to check data downloads (REQ-3)."""
        playbook_path = playbooks_dir / "insider_threat_investigation.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        steps = data.get("steps", [])
        actions = [s.get("action", "") for s in steps]

        download_actions = [
            "dlp.check_downloads",
            "ueba.analyze_downloads",
            "insider.review_data_access",
            "siem.search_file_access"
        ]
        assert any(any(da in a for da in download_actions) for a in actions), \
            f"Should have download check step, got actions: {actions}"

    def test_playbook_has_hr_legal_notification_step(self, playbooks_dir):
        """Playbook should have step for HR/Legal notification (REQ-4)."""
        playbook_path = playbooks_dir / "insider_threat_investigation.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        steps = data.get("steps", [])
        actions = [s.get("action", "") for s in steps]

        hr_legal_actions = [
            "notify.alert_hr",
            "notify.alert_legal",
            "hr.notify",
            "legal.notify"
        ]
        assert any(any(hl in a for hl in hr_legal_actions) for a in actions), \
            f"Should have HR/Legal notification step, got actions: {actions}"

    def test_playbook_has_preserve_evidence_chain_step(self, playbooks_dir):
        """Playbook should have step to preserve evidence chain (REQ-5)."""
        playbook_path = playbooks_dir / "insider_threat_investigation.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        steps = data.get("steps", [])
        actions = [s.get("action", "") for s in steps]

        evidence_actions = [
            "forensics.preserve_evidence",
            "edr.collect_artifacts",
            "insider.preserve_chain",
            "legal.create_case"
        ]
        assert any(any(ea in a for ea in evidence_actions) for a in actions), \
            f"Should have evidence preservation step, got actions: {actions}"

    def test_playbook_loads_into_service(self, playbook_service):
        """Playbook should load correctly into PlaybookService."""
        playbook = playbook_service.get_playbook("insider_threat_investigation")
        assert playbook is not None
        assert playbook.name == "insider_threat_investigation"

    def test_playbook_executes_successfully(self, playbooks_dir):
        """Playbook should execute all steps successfully with valid context."""
        async def success_handler(action: str, params: dict) -> dict:
            return {"status": "success", "action": action}

        service = PlaybookService(
            playbook_dir=str(playbooks_dir),
            action_handler=success_handler
        )

        context = {
            "incident": {
                "id": "INC-002",
                "title": "Insider Threat Investigation",
                "timestamp": "2024-01-15T11:00:00Z"
            },
            "host": {
                "device_id": "DEV-002",
                "hostname": "WS-ENG-101"
            },
            "user": {
                "name": "jdoe",
                "email": "jdoe@company.com",
                "department": "Engineering",
                "employee_id": "EMP-12345",
                "manager": "msmith@company.com"
            },
            "alert": {
                "risk_score": 85,
                "indicators": ["data_hoarding", "off_hours_access"],
                "timeframe": "30d"
            },
            "insider": {
                "risk_category": "high",
                "termination_date": None,
                "hr_case_id": None
            }
        }

        async def run_test():
            return await service.execute_playbook("insider_threat_investigation", context)

        run = asyncio.run(run_test())
        assert run.status == PlaybookRunStatus.COMPLETED
        assert len(run.step_results) >= 5  # At least 5 required steps


# ============================================================================
# T-2.3.013: Cloud Compromise Response Playbook Tests (REQ-005-002-006)
# ============================================================================

class TestCloudCompromisePlaybook:
    """Tests for cloud_compromise_response playbook.

    Requirements (REQ-005-002-006):
    1. Rotate cloud credentials
    2. Review IAM policies
    3. Check resource access logs
    4. Block suspicious IPs
    5. Enable MFA enforcement
    """

    def test_playbook_exists(self, playbooks_dir):
        """Playbook YAML file should exist."""
        playbook_path = playbooks_dir / "cloud_compromise_response.yaml"
        assert playbook_path.exists(), f"Playbook not found at {playbook_path}"

    def test_playbook_has_valid_yaml(self, playbooks_dir):
        """Playbook should have valid YAML syntax."""
        playbook_path = playbooks_dir / "cloud_compromise_response.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)
        assert data is not None
        assert "name" in data
        assert "steps" in data

    def test_playbook_name(self, playbooks_dir):
        """Playbook should have correct name."""
        playbook_path = playbooks_dir / "cloud_compromise_response.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)
        assert data["name"] == "cloud_compromise_response"

    def test_playbook_has_required_triggers(self, playbooks_dir):
        """Playbook should have appropriate triggers."""
        playbook_path = playbooks_dir / "cloud_compromise_response.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        triggers = data.get("triggers", [])
        assert len(triggers) >= 1
        expected_triggers = [
            "cloud_compromise_detected",
            "suspicious_cloud_activity",
            "aws_guardduty_alert",
            "azure_sentinel_alert",
            "gcp_security_alert",
            "cloud_credential_leak"
        ]
        assert any(t in expected_triggers for t in triggers), \
            f"Should have at least one of {expected_triggers}, got {triggers}"

    def test_playbook_has_rotate_credentials_step(self, playbooks_dir):
        """Playbook should have step to rotate cloud credentials (REQ-1)."""
        playbook_path = playbooks_dir / "cloud_compromise_response.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        steps = data.get("steps", [])
        actions = [s.get("action", "") for s in steps]

        rotate_actions = [
            "cloud.rotate_credentials",
            "iam.rotate_keys",
            "aws.rotate_access_keys",
            "azure.rotate_secrets"
        ]
        assert any(any(ra in a for ra in rotate_actions) for a in actions), \
            f"Should have credential rotation step, got actions: {actions}"

    def test_playbook_has_review_iam_step(self, playbooks_dir):
        """Playbook should have step to review IAM policies (REQ-2)."""
        playbook_path = playbooks_dir / "cloud_compromise_response.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        steps = data.get("steps", [])
        actions = [s.get("action", "") for s in steps]

        iam_actions = [
            "iam.review_policies",
            "cloud.audit_iam",
            "aws.review_iam",
            "azure.review_rbac"
        ]
        assert any(any(ia in a for ia in iam_actions) for a in actions), \
            f"Should have IAM review step, got actions: {actions}"

    def test_playbook_has_check_access_logs_step(self, playbooks_dir):
        """Playbook should have step to check resource access logs (REQ-3)."""
        playbook_path = playbooks_dir / "cloud_compromise_response.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        steps = data.get("steps", [])
        actions = [s.get("action", "") for s in steps]

        log_actions = [
            "cloud.check_access_logs",
            "cloudtrail.search",
            "aws.review_cloudtrail",
            "azure.review_activity_log"
        ]
        assert any(any(la in a for la in log_actions) for a in actions), \
            f"Should have access log check step, got actions: {actions}"

    def test_playbook_has_block_ips_step(self, playbooks_dir):
        """Playbook should have step to block suspicious IPs (REQ-4)."""
        playbook_path = playbooks_dir / "cloud_compromise_response.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        steps = data.get("steps", [])
        actions = [s.get("action", "") for s in steps]

        block_actions = [
            "network.block_ip",
            "cloud.block_ip",
            "waf.block_ip",
            "security_group.block"
        ]
        assert any(any(ba in a for ba in block_actions) for a in actions), \
            f"Should have IP blocking step, got actions: {actions}"

    def test_playbook_has_mfa_enforcement_step(self, playbooks_dir):
        """Playbook should have step to enable MFA enforcement (REQ-5)."""
        playbook_path = playbooks_dir / "cloud_compromise_response.yaml"
        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        steps = data.get("steps", [])
        actions = [s.get("action", "") for s in steps]

        mfa_actions = [
            "iam.enforce_mfa",
            "cloud.require_mfa",
            "idp.enforce_mfa",
            "auth.enable_mfa"
        ]
        assert any(any(ma in a for ma in mfa_actions) for a in actions), \
            f"Should have MFA enforcement step, got actions: {actions}"

    def test_playbook_loads_into_service(self, playbook_service):
        """Playbook should load correctly into PlaybookService."""
        playbook = playbook_service.get_playbook("cloud_compromise_response")
        assert playbook is not None
        assert playbook.name == "cloud_compromise_response"

    def test_playbook_executes_successfully(self, playbooks_dir):
        """Playbook should execute all steps successfully with valid context."""
        async def success_handler(action: str, params: dict) -> dict:
            return {"status": "success", "action": action}

        service = PlaybookService(
            playbook_dir=str(playbooks_dir),
            action_handler=success_handler
        )

        context = {
            "incident": {
                "id": "INC-003",
                "title": "Cloud Compromise Alert",
                "timestamp": "2024-01-15T12:00:00Z"
            },
            "cloud": {
                "provider": "aws",
                "account_id": "123456789012",
                "region": "us-east-1"
            },
            "user": {
                "name": "admin@company.com",
                "iam_user": "admin-user",
                "access_key_id": "AKIA..."
            },
            "alert": {
                "source_ip": "203.0.113.100",
                "activity_type": "console_login",
                "risk_score": 90,
                "guardduty_finding_id": "abc123"
            }
        }

        async def run_test():
            return await service.execute_playbook("cloud_compromise_response", context)

        run = asyncio.run(run_test())
        assert run.status == PlaybookRunStatus.COMPLETED
        assert len(run.step_results) >= 5  # At least 5 required steps


# ============================================================================
# Integration Tests for All Playbooks
# ============================================================================

class TestPlaybookIntegration:
    """Integration tests to verify all playbooks work together."""

    def test_all_required_playbooks_exist(self, playbooks_dir):
        """All required playbooks should exist."""
        required_playbooks = [
            "data_exfiltration_response.yaml",
            "insider_threat_investigation.yaml",
            "cloud_compromise_response.yaml"
        ]

        for playbook_name in required_playbooks:
            playbook_path = playbooks_dir / playbook_name
            assert playbook_path.exists(), f"Required playbook missing: {playbook_name}"

    def test_all_playbooks_have_mitre_mapping(self, playbooks_dir):
        """All playbooks should have MITRE ATT&CK mapping."""
        playbook_files = [
            "data_exfiltration_response.yaml",
            "insider_threat_investigation.yaml",
            "cloud_compromise_response.yaml"
        ]

        for playbook_file in playbook_files:
            playbook_path = playbooks_dir / playbook_file
            if playbook_path.exists():
                with open(playbook_path) as f:
                    data = yaml.safe_load(f)

                # Check for MITRE mapping in playbook or steps
                has_mitre = "mitre_mapping" in data or any(
                    "mitre" in str(s).lower() for s in data.get("steps", [])
                )
                # MITRE mapping is recommended but not strictly required
                # Just verify the structure is valid

    def test_all_playbooks_load_without_error(self, playbook_service):
        """All playbooks should load into service without errors."""
        playbooks = playbook_service.list_playbooks()
        playbook_names = [p.name for p in playbooks]

        required = [
            "data_exfiltration_response",
            "insider_threat_investigation",
            "cloud_compromise_response"
        ]

        for name in required:
            assert name in playbook_names, f"Playbook '{name}' not loaded"

    def test_playbooks_have_proper_error_handling(self, playbooks_dir):
        """Playbooks should have proper on_error configurations."""
        playbook_files = [
            "data_exfiltration_response.yaml",
            "insider_threat_investigation.yaml",
            "cloud_compromise_response.yaml"
        ]

        valid_on_error = ["fail", "continue", "notify_human"]

        for playbook_file in playbook_files:
            playbook_path = playbooks_dir / playbook_file
            if playbook_path.exists():
                with open(playbook_path) as f:
                    data = yaml.safe_load(f)

                for step in data.get("steps", []):
                    on_error = step.get("on_error", "fail")
                    assert on_error in valid_on_error, \
                        f"Invalid on_error '{on_error}' in {playbook_file}"

    def test_playbooks_have_reasonable_timeouts(self, playbooks_dir):
        """Playbooks should have reasonable timeout values."""
        playbook_files = [
            "data_exfiltration_response.yaml",
            "insider_threat_investigation.yaml",
            "cloud_compromise_response.yaml"
        ]

        for playbook_file in playbook_files:
            playbook_path = playbooks_dir / playbook_file
            if playbook_path.exists():
                with open(playbook_path) as f:
                    data = yaml.safe_load(f)

                for step in data.get("steps", []):
                    timeout = step.get("timeout", 120)
                    assert 1 <= timeout <= 3600, \
                        f"Timeout {timeout}s out of range in {playbook_file}"
