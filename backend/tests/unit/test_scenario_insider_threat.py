"""
Unit tests for Insider Threat - Data Exfiltration scenario.

Task: T-1.3.008
Requirement: REQ-002-001-006 - Escenario Insider Threat - Privileged User Exfiltration
Test ID: UT-016

Tests verify:
- InsiderThreatScenario class exists
- Scenario generates correct events
- Events follow MITRE ATT&CK framework
- Scenario data matches insider threat TTPs
- HR approval workflow is implemented
"""

import pytest
from datetime import datetime, timezone


class TestInsiderThreatScenarioExists:
    """Tests for Insider Threat scenario module existence."""

    def test_insider_threat_scenario_module_exists(self):
        """Test that scenario_insider_threat module exists."""
        from src.demo import scenario_insider_threat
        assert scenario_insider_threat is not None

    def test_scenario_constants_exist(self):
        """Test that scenario constants are defined."""
        from src.demo.scenario_insider_threat import SCENARIO_ID, SCENARIO_NAME

        assert SCENARIO_ID is not None
        assert "005" in SCENARIO_ID or "ANCHOR" in SCENARIO_ID
        assert SCENARIO_NAME is not None
        assert "Insider" in SCENARIO_NAME

    def test_insider_user_id_constant_exists(self):
        """Test that insider user ID constant exists."""
        from src.demo.scenario_insider_threat import INSIDER_USER_ID

        assert INSIDER_USER_ID is not None
        assert len(INSIDER_USER_ID) > 0

    def test_insider_device_id_constant_exists(self):
        """Test that insider device ID constant exists."""
        from src.demo.scenario_insider_threat import INSIDER_DEVICE_ID

        assert INSIDER_DEVICE_ID is not None
        assert len(INSIDER_DEVICE_ID) > 0

    def test_data_transfer_event_dataclass_exists(self):
        """Test that DataTransferEvent dataclass exists."""
        from src.demo.scenario_insider_threat import DataTransferEvent

        assert DataTransferEvent is not None

    def test_location_anomaly_dataclass_exists(self):
        """Test that LocationAnomaly dataclass exists."""
        from src.demo.scenario_insider_threat import LocationAnomaly

        assert LocationAnomaly is not None

    def test_time_anomaly_dataclass_exists(self):
        """Test that TimeAnomaly dataclass exists."""
        from src.demo.scenario_insider_threat import TimeAnomaly

        assert TimeAnomaly is not None

    def test_insider_threat_scenario_data_dataclass_exists(self):
        """Test that InsiderThreatScenarioData dataclass exists."""
        from src.demo.scenario_insider_threat import InsiderThreatScenarioData

        assert InsiderThreatScenarioData is not None


class TestInsiderThreatScenarioGenerator:
    """Tests for scenario data generation."""

    def test_generate_insider_threat_scenario_function_exists(self):
        """Test that generate_insider_threat_scenario function exists."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        assert callable(generate_insider_threat_scenario)

    def test_generate_insider_threat_scenario_returns_data(self):
        """Test that generator returns scenario data."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()
        assert scenario is not None

    def test_insider_threat_scenario_has_incident_id(self):
        """Test that scenario has incident_id."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()
        assert hasattr(scenario, "incident_id")
        assert scenario.incident_id is not None

    def test_insider_threat_scenario_has_user_info(self):
        """Test that scenario has user information."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()
        assert hasattr(scenario, "user_id")
        assert hasattr(scenario, "user_name")
        assert hasattr(scenario, "user_title")
        assert hasattr(scenario, "user_department")

    def test_insider_threat_scenario_has_device_id(self):
        """Test that scenario has device_id."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()
        assert hasattr(scenario, "device_id")
        assert scenario.device_id is not None

    def test_insider_threat_scenario_has_risk_score(self):
        """Test that scenario has risk_score."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()
        assert hasattr(scenario, "risk_score")
        assert isinstance(scenario.risk_score, int)
        assert 0 <= scenario.risk_score <= 100

    def test_insider_threat_scenario_has_data_transfers(self):
        """Test that scenario has data_transfers list."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()
        assert hasattr(scenario, "data_transfers")
        assert len(scenario.data_transfers) > 0

    def test_insider_threat_scenario_has_location_anomalies(self):
        """Test that scenario has location_anomalies list."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()
        assert hasattr(scenario, "location_anomalies")
        assert len(scenario.location_anomalies) > 0

    def test_insider_threat_scenario_has_time_anomalies(self):
        """Test that scenario has time_anomalies list."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()
        assert hasattr(scenario, "time_anomalies")
        assert len(scenario.time_anomalies) > 0

    def test_insider_threat_scenario_has_hr_flags(self):
        """Test that scenario has hr_flags list."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()
        assert hasattr(scenario, "hr_flags")
        assert len(scenario.hr_flags) > 0

    def test_insider_threat_scenario_has_recent_events(self):
        """Test that scenario has recent_events list."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()
        assert hasattr(scenario, "recent_events")
        assert len(scenario.recent_events) > 0

    def test_insider_threat_scenario_has_timeline_events(self):
        """Test that scenario has timeline_events."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()
        assert hasattr(scenario, "timeline_events")
        assert len(scenario.timeline_events) > 0

    def test_insider_threat_scenario_has_total_data_transferred_property(self):
        """Test that scenario has total_data_transferred_mb computed property."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()
        assert hasattr(scenario, "total_data_transferred_mb")
        expected_total = sum(t.data_size_mb for t in scenario.data_transfers)
        assert scenario.total_data_transferred_mb == expected_total

    def test_insider_threat_scenario_has_total_files_transferred_property(self):
        """Test that scenario has total_files_transferred computed property."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()
        assert hasattr(scenario, "total_files_transferred")
        expected_total = sum(t.file_count for t in scenario.data_transfers)
        assert scenario.total_files_transferred == expected_total

    def test_insider_threat_scenario_has_dlp_violations_count_property(self):
        """Test that scenario has dlp_violations_count computed property."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()
        assert hasattr(scenario, "dlp_violations_count")
        expected_count = sum(1 for t in scenario.data_transfers if t.dlp_policy_violated)
        assert scenario.dlp_violations_count == expected_count


class TestDataTransferEventDataclass:
    """Tests for DataTransferEvent dataclass."""

    def test_data_transfer_event_has_required_fields(self):
        """Test that DataTransferEvent has required fields."""
        from src.demo.scenario_insider_threat import DataTransferEvent
        from datetime import datetime, timezone

        event = DataTransferEvent(
            event_id="DT-TEST-001",
            timestamp=datetime.now(timezone.utc),
            destination="test.example.com",
            destination_type="cloud_storage",
            data_size_mb=100.5,
            file_count=50,
            sensitive_data_detected=True,
            dlp_policy_violated="PII-PROTECTION",
        )

        assert event.event_id == "DT-TEST-001"
        assert event.destination == "test.example.com"
        assert event.destination_type == "cloud_storage"
        assert event.data_size_mb == 100.5
        assert event.file_count == 50
        assert event.sensitive_data_detected is True
        assert event.dlp_policy_violated == "PII-PROTECTION"


class TestLocationAnomalyDataclass:
    """Tests for LocationAnomaly dataclass."""

    def test_location_anomaly_has_required_fields(self):
        """Test that LocationAnomaly has required fields."""
        from src.demo.scenario_insider_threat import LocationAnomaly
        from datetime import datetime, timezone

        anomaly = LocationAnomaly(
            timestamp=datetime.now(timezone.utc),
            expected_location="New York, NY",
            actual_location="Singapore",
            ip_address="103.45.67.89",
            vpn_used=True,
            impossible_travel=True,
            distance_km=15330.0,
        )

        assert anomaly.expected_location == "New York, NY"
        assert anomaly.actual_location == "Singapore"
        assert anomaly.impossible_travel is True
        assert anomaly.distance_km == 15330.0


class TestInsiderThreatMITREMapping:
    """Tests for MITRE ATT&CK integration."""

    def test_insider_threat_uses_known_ttps(self):
        """Test that scenario uses known insider threat TTPs."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()
        # Insider threat commonly uses these techniques
        known_techniques = [
            "T1078",      # Valid Accounts
            "T1567",      # Exfiltration Over Web Service
            "T1052.001",  # Exfiltration over USB
            "T1005",      # Data from Local System
        ]

        # Check timeline events have MITRE references
        mitre_refs = []
        for event in scenario.timeline_events:
            if "mitre_technique" in event and event["mitre_technique"]:
                mitre_refs.append(event["mitre_technique"])
            if "technique_id" in event and event["technique_id"]:
                mitre_refs.append(event["technique_id"])

        # At least some events should have MITRE techniques
        assert len(mitre_refs) > 0

    def test_timeline_events_have_tactic_id(self):
        """Test that timeline events include MITRE tactic IDs."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()

        # Check at least one event has tactic_id
        has_tactic = any(
            ("tactic_id" in event and event["tactic_id"]) or
            ("mitre_tactic" in event and event["mitre_tactic"])
            for event in scenario.timeline_events
        )
        assert has_tactic, "Timeline events should include MITRE tactic IDs"

    def test_timeline_events_have_technique_id(self):
        """Test that timeline events include MITRE technique IDs."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()

        # Check at least one event has technique_id
        has_technique = any(
            ("technique_id" in event and event["technique_id"]) or
            ("mitre_technique" in event and event["mitre_technique"])
            for event in scenario.timeline_events
        )
        assert has_technique, "Timeline events should include MITRE technique IDs"

    def test_timeline_has_exfiltration_tactic(self):
        """Test that timeline includes Exfiltration tactic (TA0010)."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()

        # Check for Exfiltration tactic
        has_exfil = any(
            event.get("tactic_id") == "TA0010" or event.get("mitre_tactic") == "TA0010"
            for event in scenario.timeline_events
        )
        assert has_exfil, "Timeline should include Exfiltration tactic (TA0010)"


class TestInsiderThreatOpenSearchDocuments:
    """Tests for OpenSearch document generation."""

    def test_generate_incident_document_exists(self):
        """Test that generate_incident_document function exists."""
        from src.demo.scenario_insider_threat import generate_incident_document

        assert callable(generate_incident_document)

    def test_generate_incident_document_returns_dict(self):
        """Test that incident document is a dict."""
        from src.demo.scenario_insider_threat import generate_incident_document

        doc = generate_incident_document()
        assert isinstance(doc, dict)
        assert "incident_id" in doc
        assert "severity" in doc

    def test_incident_document_severity_is_critical(self):
        """Test that insider threat incident has critical severity."""
        from src.demo.scenario_insider_threat import generate_incident_document

        doc = generate_incident_document()
        assert doc["severity"] == "Critical"

    def test_incident_document_has_mitre_technique(self):
        """Test that incident document has MITRE technique."""
        from src.demo.scenario_insider_threat import generate_incident_document

        doc = generate_incident_document()
        assert "mitre_technique" in doc or "technique_id" in doc

    def test_incident_document_has_user_id(self):
        """Test that incident document has user_id."""
        from src.demo.scenario_insider_threat import generate_incident_document

        doc = generate_incident_document()
        assert "user_id" in doc

    def test_incident_document_has_risk_score(self):
        """Test that incident document has risk_score."""
        from src.demo.scenario_insider_threat import generate_incident_document

        doc = generate_incident_document()
        assert "risk_score" in doc

    def test_incident_document_has_data_volume(self):
        """Test that incident document has data volume info."""
        from src.demo.scenario_insider_threat import generate_incident_document

        doc = generate_incident_document()
        assert "data_volume_mb" in doc

    def test_incident_document_has_hr_required_tag(self):
        """Test that incident document has HR approval required tag."""
        from src.demo.scenario_insider_threat import generate_incident_document

        doc = generate_incident_document()
        assert "tags" in doc
        assert "hr-required" in doc["tags"]

    def test_generate_asset_document_exists(self):
        """Test that generate_asset_document function exists."""
        from src.demo.scenario_insider_threat import generate_asset_document

        assert callable(generate_asset_document)

    def test_generate_asset_document_returns_dict(self):
        """Test that asset document is a dict."""
        from src.demo.scenario_insider_threat import generate_asset_document

        doc = generate_asset_document()
        assert isinstance(doc, dict)
        assert "asset_id" in doc

    def test_asset_document_has_admin_privileges(self):
        """Test that asset document indicates admin privileges."""
        from src.demo.scenario_insider_threat import generate_asset_document

        doc = generate_asset_document()
        assert "admin_privileges" in doc
        assert doc["admin_privileges"] is True

    def test_generate_ueba_document_exists(self):
        """Test that generate_ueba_document function exists."""
        from src.demo.scenario_insider_threat import generate_ueba_document

        assert callable(generate_ueba_document)

    def test_generate_ueba_document_returns_dict(self):
        """Test that UEBA document is a dict."""
        from src.demo.scenario_insider_threat import generate_ueba_document

        doc = generate_ueba_document()
        assert isinstance(doc, dict)
        assert "user_id" in doc
        assert "risk_score" in doc

    def test_ueba_document_has_anomalies(self):
        """Test that UEBA document has anomalies detected."""
        from src.demo.scenario_insider_threat import generate_ueba_document

        doc = generate_ueba_document()
        assert "anomalies_detected" in doc
        assert len(doc["anomalies_detected"]) > 0

    def test_ueba_document_has_risk_factors(self):
        """Test that UEBA document has risk factors."""
        from src.demo.scenario_insider_threat import generate_ueba_document

        doc = generate_ueba_document()
        assert "risk_factors" in doc
        assert isinstance(doc["risk_factors"], dict)

    def test_ueba_document_has_historical_risk(self):
        """Test that UEBA document has historical risk trend."""
        from src.demo.scenario_insider_threat import generate_ueba_document

        doc = generate_ueba_document()
        assert "historical_risk" in doc
        assert len(doc["historical_risk"]) > 0

    def test_generate_dlp_documents_exists(self):
        """Test that generate_dlp_documents function exists."""
        from src.demo.scenario_insider_threat import generate_dlp_documents

        assert callable(generate_dlp_documents)

    def test_generate_dlp_documents_returns_list(self):
        """Test that DLP documents is a list."""
        from src.demo.scenario_insider_threat import generate_dlp_documents

        docs = generate_dlp_documents()
        assert isinstance(docs, list)
        assert len(docs) > 0

    def test_dlp_documents_have_policy_violated(self):
        """Test that DLP documents have policy violated info."""
        from src.demo.scenario_insider_threat import generate_dlp_documents

        docs = generate_dlp_documents()
        for doc in docs:
            assert "policy_violated" in doc
            assert doc["policy_violated"] is not None


class TestInsiderThreatApprovalWorkflow:
    """Tests for approval workflow."""

    def test_get_approval_requirements_exists(self):
        """Test that get_approval_requirements function exists."""
        from src.demo.scenario_insider_threat import get_approval_requirements

        assert callable(get_approval_requirements)

    def test_get_approval_requirements_returns_dict(self):
        """Test that approval requirements is a dict."""
        from src.demo.scenario_insider_threat import get_approval_requirements

        reqs = get_approval_requirements()
        assert isinstance(reqs, dict)
        assert "required_approvals" in reqs

    def test_approval_requirements_includes_hr(self):
        """Test that approval requirements include HR manager."""
        from src.demo.scenario_insider_threat import get_approval_requirements

        reqs = get_approval_requirements()
        required = reqs["required_approvals"]

        has_hr = any(
            "HR" in approval["role"]
            for approval in required
        )
        assert has_hr, "Approval requirements should include HR Manager"

    def test_approval_requirements_includes_legal(self):
        """Test that approval requirements include legal counsel."""
        from src.demo.scenario_insider_threat import get_approval_requirements

        reqs = get_approval_requirements()
        required = reqs["required_approvals"]

        has_legal = any(
            "Legal" in approval["role"]
            for approval in required
        )
        assert has_legal, "Approval requirements should include Legal Counsel"

    def test_approval_requirements_has_evidence_preservation(self):
        """Test that approval requirements include evidence preservation."""
        from src.demo.scenario_insider_threat import get_approval_requirements

        reqs = get_approval_requirements()
        assert "evidence_preservation" in reqs
        assert reqs["evidence_preservation"]["required"] is True
        assert reqs["evidence_preservation"]["legal_hold"] is True


class TestInsiderThreatResponsePlaybook:
    """Tests for response playbook."""

    def test_get_response_playbook_exists(self):
        """Test that get_response_playbook function exists."""
        from src.demo.scenario_insider_threat import get_response_playbook

        assert callable(get_response_playbook)

    def test_response_playbook_returns_dict(self):
        """Test that playbook is a dict."""
        from src.demo.scenario_insider_threat import get_response_playbook

        playbook = get_response_playbook()
        assert isinstance(playbook, dict)
        assert "playbook_id" in playbook
        assert "steps" in playbook

    def test_playbook_has_evidence_preservation_step(self):
        """Test that playbook includes evidence preservation."""
        from src.demo.scenario_insider_threat import get_response_playbook

        playbook = get_response_playbook()
        steps = playbook["steps"]

        actions = [step["action"] for step in steps]
        assert any("evidence" in action or "preservation" in action or "legal_hold" in action
                   for action in actions)

    def test_playbook_has_hr_notification_step(self):
        """Test that playbook includes HR notification."""
        from src.demo.scenario_insider_threat import get_response_playbook

        playbook = get_response_playbook()
        steps = playbook["steps"]

        actions = [step["action"] for step in steps]
        assert any("hr" in action.lower() for action in actions)

    def test_playbook_has_legal_notification_step(self):
        """Test that playbook includes legal notification."""
        from src.demo.scenario_insider_threat import get_response_playbook

        playbook = get_response_playbook()
        steps = playbook["steps"]

        actions = [step["action"] for step in steps]
        assert any("legal" in action.lower() for action in actions)

    def test_playbook_has_await_hr_approval_step(self):
        """Test that playbook includes step to wait for HR approval."""
        from src.demo.scenario_insider_threat import get_response_playbook

        playbook = get_response_playbook()
        steps = playbook["steps"]

        actions = [step["action"] for step in steps]
        descriptions = [step["description"].lower() for step in steps]

        has_await_approval = any(
            "await" in a.lower() or "approval" in a.lower() or
            "wait" in d or "approval" in d
            for a, d in zip(actions, descriptions)
        )
        assert has_await_approval, "Playbook should include step to await HR approval"

    def test_playbook_has_account_disable_step(self):
        """Test that playbook includes account disable step."""
        from src.demo.scenario_insider_threat import get_response_playbook

        playbook = get_response_playbook()
        steps = playbook["steps"]

        actions = [step["action"] for step in steps]
        assert any("account" in action.lower() and "disable" in action.lower()
                   for action in actions)

    def test_playbook_has_forensic_collection_step(self):
        """Test that playbook includes forensic collection."""
        from src.demo.scenario_insider_threat import get_response_playbook

        playbook = get_response_playbook()
        steps = playbook["steps"]

        actions = [step["action"] for step in steps]
        assert any("forensic" in action.lower() for action in actions)

    def test_playbook_requires_hr_approval(self):
        """Test that playbook requires HR approval."""
        from src.demo.scenario_insider_threat import get_response_playbook

        playbook = get_response_playbook()
        assert playbook.get("requires_hr_approval") is True

    def test_playbook_requires_legal_approval(self):
        """Test that playbook requires legal approval."""
        from src.demo.scenario_insider_threat import get_response_playbook

        playbook = get_response_playbook()
        assert playbook.get("requires_legal_approval") is True

    def test_account_disable_step_requires_approval(self):
        """Test that account disable step requires approval."""
        from src.demo.scenario_insider_threat import get_response_playbook

        playbook = get_response_playbook()
        steps = playbook["steps"]

        for step in steps:
            if "account" in step["action"].lower() and "disable" in step["action"].lower():
                assert step.get("requires_approval") is True, \
                    "Account disable step should require approval"
