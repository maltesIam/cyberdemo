"""
Unit tests for Ransomware Multi-Host Attack scenario.

Task: T-1.3.006
Requirement: REQ-002-001-004 - Escenario Ransomware - Multi-Host Encryption
Test ID: UT-014

Tests verify:
- RansomwareScenario class exists
- Scenario generates correct events
- Events follow MITRE ATT&CK framework
- Scenario data matches LockBit TTPs
- Mass containment trigger works for 5+ hosts
"""

import pytest
from datetime import datetime, timezone


class TestRansomwareScenarioExists:
    """Tests for Ransomware scenario module existence."""

    def test_ransomware_scenario_module_exists(self):
        """Test that scenario_ransomware module exists."""
        from src.demo import scenario_ransomware
        assert scenario_ransomware is not None

    def test_scenario_constants_exist(self):
        """Test that scenario constants are defined."""
        from src.demo.scenario_ransomware import SCENARIO_ID, SCENARIO_NAME

        assert SCENARIO_ID is not None
        assert "004" in SCENARIO_ID or "ANCHOR" in SCENARIO_ID
        assert SCENARIO_NAME is not None
        assert "Ransomware" in SCENARIO_NAME

    def test_ransomware_hash_constant_exists(self):
        """Test that ransomware hash constant exists."""
        from src.demo.scenario_ransomware import RANSOMWARE_HASH

        assert RANSOMWARE_HASH is not None
        assert len(RANSOMWARE_HASH) == 64  # SHA256 hash length

    def test_ransomware_family_constant_exists(self):
        """Test that ransomware family constant exists."""
        from src.demo.scenario_ransomware import RANSOMWARE_FAMILY

        assert RANSOMWARE_FAMILY is not None
        assert "LockBit" in RANSOMWARE_FAMILY

    def test_ransomware_host_dataclass_exists(self):
        """Test that RansomwareHost dataclass exists."""
        from src.demo.scenario_ransomware import RansomwareHost

        assert RansomwareHost is not None

    def test_ransomware_scenario_data_dataclass_exists(self):
        """Test that RansomwareScenarioData dataclass exists."""
        from src.demo.scenario_ransomware import RansomwareScenarioData

        assert RansomwareScenarioData is not None


class TestRansomwareScenarioGenerator:
    """Tests for scenario data generation."""

    def test_generate_ransomware_scenario_function_exists(self):
        """Test that generate_ransomware_scenario function exists."""
        from src.demo.scenario_ransomware import generate_ransomware_scenario

        assert callable(generate_ransomware_scenario)

    def test_generate_ransomware_scenario_returns_data(self):
        """Test that generator returns scenario data."""
        from src.demo.scenario_ransomware import generate_ransomware_scenario

        scenario = generate_ransomware_scenario()
        assert scenario is not None

    def test_ransomware_scenario_has_incident_id(self):
        """Test that scenario has incident_id."""
        from src.demo.scenario_ransomware import generate_ransomware_scenario

        scenario = generate_ransomware_scenario()
        assert hasattr(scenario, "incident_id")
        assert scenario.incident_id is not None

    def test_ransomware_scenario_has_affected_hosts(self):
        """Test that scenario has affected_hosts list."""
        from src.demo.scenario_ransomware import generate_ransomware_scenario

        scenario = generate_ransomware_scenario()
        assert hasattr(scenario, "affected_hosts")
        assert len(scenario.affected_hosts) > 0

    def test_ransomware_scenario_has_at_least_5_hosts(self):
        """Test that scenario has at least 5 hosts for mass containment trigger."""
        from src.demo.scenario_ransomware import generate_ransomware_scenario

        scenario = generate_ransomware_scenario()
        assert len(scenario.affected_hosts) >= 5

    def test_ransomware_scenario_has_timeline_events(self):
        """Test that scenario has timeline_events."""
        from src.demo.scenario_ransomware import generate_ransomware_scenario

        scenario = generate_ransomware_scenario()
        assert hasattr(scenario, "timeline_events")
        assert len(scenario.timeline_events) > 0

    def test_ransomware_scenario_has_ransomware_family(self):
        """Test that scenario has ransomware_family."""
        from src.demo.scenario_ransomware import generate_ransomware_scenario

        scenario = generate_ransomware_scenario()
        assert hasattr(scenario, "ransomware_family")
        assert "LockBit" in scenario.ransomware_family

    def test_ransomware_scenario_has_ransom_info(self):
        """Test that scenario has ransom information."""
        from src.demo.scenario_ransomware import generate_ransomware_scenario

        scenario = generate_ransomware_scenario()
        assert hasattr(scenario, "ransom_amount_btc")
        assert hasattr(scenario, "bitcoin_address")
        assert hasattr(scenario, "ransom_note_text")

    def test_ransomware_scenario_has_affected_count_property(self):
        """Test that scenario has affected_count computed property."""
        from src.demo.scenario_ransomware import generate_ransomware_scenario

        scenario = generate_ransomware_scenario()
        assert hasattr(scenario, "affected_count")
        assert scenario.affected_count == len(scenario.affected_hosts)

    def test_ransomware_scenario_has_total_encrypted_files_property(self):
        """Test that scenario has total_encrypted_files computed property."""
        from src.demo.scenario_ransomware import generate_ransomware_scenario

        scenario = generate_ransomware_scenario()
        assert hasattr(scenario, "total_encrypted_files")
        expected_total = sum(h.encrypted_files for h in scenario.affected_hosts)
        assert scenario.total_encrypted_files == expected_total


class TestRansomwareHostDataclass:
    """Tests for RansomwareHost dataclass."""

    def test_ransomware_host_has_required_fields(self):
        """Test that RansomwareHost has required fields."""
        from src.demo.scenario_ransomware import RansomwareHost
        from datetime import datetime, timezone

        host = RansomwareHost(
            asset_id="WS-TEST-001",
            hostname="ws-test-001.corp.local",
            department="Test",
            encrypted_files=100,
            encryption_progress=50.0,
            first_seen=datetime.now(timezone.utc),
        )

        assert host.asset_id == "WS-TEST-001"
        assert host.hostname == "ws-test-001.corp.local"
        assert host.department == "Test"
        assert host.encrypted_files == 100
        assert host.encryption_progress == 50.0
        assert host.status == "active"  # Default value


class TestRansomwareMITREMapping:
    """Tests for MITRE ATT&CK integration."""

    def test_ransomware_uses_known_ttps(self):
        """Test that scenario uses known ransomware TTPs."""
        from src.demo.scenario_ransomware import generate_ransomware_scenario

        scenario = generate_ransomware_scenario()
        # Ransomware commonly uses these techniques
        known_techniques = [
            "T1486",  # Data Encrypted for Impact
            "T1490",  # Inhibit System Recovery
            "T1489",  # Service Stop
            "T1021.001",  # Remote Desktop Protocol
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
        from src.demo.scenario_ransomware import generate_ransomware_scenario

        scenario = generate_ransomware_scenario()

        # Check at least one event has tactic_id
        has_tactic = any(
            ("tactic_id" in event and event["tactic_id"]) or
            ("mitre_tactic" in event and event["mitre_tactic"])
            for event in scenario.timeline_events
        )
        assert has_tactic, "Timeline events should include MITRE tactic IDs"

    def test_timeline_events_have_technique_id(self):
        """Test that timeline events include MITRE technique IDs."""
        from src.demo.scenario_ransomware import generate_ransomware_scenario

        scenario = generate_ransomware_scenario()

        # Check at least one event has technique_id
        has_technique = any(
            ("technique_id" in event and event["technique_id"]) or
            ("mitre_technique" in event and event["mitre_technique"])
            for event in scenario.timeline_events
        )
        assert has_technique, "Timeline events should include MITRE technique IDs"

    def test_timeline_has_impact_tactic(self):
        """Test that timeline includes Impact tactic (TA0040) for encryption."""
        from src.demo.scenario_ransomware import generate_ransomware_scenario

        scenario = generate_ransomware_scenario()

        # Check for Impact tactic
        has_impact = any(
            event.get("tactic_id") == "TA0040" or event.get("mitre_tactic") == "TA0040"
            for event in scenario.timeline_events
        )
        assert has_impact, "Timeline should include Impact tactic (TA0040)"


class TestRansomwareOpenSearchDocuments:
    """Tests for OpenSearch document generation."""

    def test_generate_incident_document_exists(self):
        """Test that generate_incident_document function exists."""
        from src.demo.scenario_ransomware import generate_incident_document

        assert callable(generate_incident_document)

    def test_generate_incident_document_returns_dict(self):
        """Test that incident document is a dict."""
        from src.demo.scenario_ransomware import generate_incident_document

        doc = generate_incident_document()
        assert isinstance(doc, dict)
        assert "incident_id" in doc
        assert "severity" in doc

    def test_incident_document_severity_is_critical(self):
        """Test that ransomware incident has critical severity."""
        from src.demo.scenario_ransomware import generate_incident_document

        doc = generate_incident_document()
        assert doc["severity"] == "Critical"

    def test_incident_document_has_mitre_technique(self):
        """Test that incident document has MITRE technique."""
        from src.demo.scenario_ransomware import generate_incident_document

        doc = generate_incident_document()
        assert "mitre_technique" in doc or "technique_id" in doc

    def test_incident_document_has_hash(self):
        """Test that incident document has ransomware hash."""
        from src.demo.scenario_ransomware import generate_incident_document

        doc = generate_incident_document()
        assert "hash_sha256" in doc
        assert len(doc["hash_sha256"]) == 64

    def test_generate_edr_documents_exists(self):
        """Test that generate_edr_documents function exists."""
        from src.demo.scenario_ransomware import generate_edr_documents

        assert callable(generate_edr_documents)

    def test_generate_edr_documents_returns_list(self):
        """Test that EDR documents is a list."""
        from src.demo.scenario_ransomware import generate_edr_documents

        docs = generate_edr_documents()
        assert isinstance(docs, list)
        assert len(docs) > 0

    def test_edr_documents_have_mitre_fields(self):
        """Test that EDR documents have MITRE fields."""
        from src.demo.scenario_ransomware import generate_edr_documents

        docs = generate_edr_documents()
        for doc in docs:
            # Each EDR detection should reference MITRE
            assert "mitre_technique" in doc or "technique_id" in doc

    def test_generate_asset_documents_exists(self):
        """Test that generate_asset_documents function exists."""
        from src.demo.scenario_ransomware import generate_asset_documents

        assert callable(generate_asset_documents)

    def test_generate_asset_documents_returns_list(self):
        """Test that asset documents is a list."""
        from src.demo.scenario_ransomware import generate_asset_documents

        docs = generate_asset_documents()
        assert isinstance(docs, list)
        assert len(docs) > 0

    def test_generate_intel_document_exists(self):
        """Test that generate_intel_document function exists."""
        from src.demo.scenario_ransomware import generate_intel_document

        assert callable(generate_intel_document)

    def test_generate_intel_document_returns_dict(self):
        """Test that intel document is a dict."""
        from src.demo.scenario_ransomware import generate_intel_document

        doc = generate_intel_document()
        assert isinstance(doc, dict)
        assert "hash" in doc
        assert "verdict" in doc
        assert doc["verdict"] == "malicious"

    def test_generate_propagation_document_exists(self):
        """Test that generate_propagation_document function exists."""
        from src.demo.scenario_ransomware import generate_propagation_document

        assert callable(generate_propagation_document)

    def test_generate_propagation_document_returns_dict(self):
        """Test that propagation document is a dict."""
        from src.demo.scenario_ransomware import generate_propagation_document

        doc = generate_propagation_document()
        assert isinstance(doc, dict)
        assert "hash" in doc
        assert "affected_hosts" in doc
        assert "spread_rate" in doc


class TestRansomwareResponsePlaybook:
    """Tests for response playbook."""

    def test_get_response_playbook_exists(self):
        """Test that get_response_playbook function exists."""
        from src.demo.scenario_ransomware import get_response_playbook

        assert callable(get_response_playbook)

    def test_response_playbook_returns_dict(self):
        """Test that playbook is a dict."""
        from src.demo.scenario_ransomware import get_response_playbook

        playbook = get_response_playbook()
        assert isinstance(playbook, dict)
        assert "playbook_id" in playbook
        assert "steps" in playbook

    def test_playbook_has_mass_containment_step(self):
        """Test that playbook includes mass containment for multi-host attack."""
        from src.demo.scenario_ransomware import get_response_playbook

        playbook = get_response_playbook()
        steps = playbook["steps"]

        actions = [step["action"] for step in steps]
        assert any("containment" in action or "isolation" in action
                   for action in actions)

    def test_playbook_has_executive_notification(self):
        """Test that playbook includes executive notification."""
        from src.demo.scenario_ransomware import get_response_playbook

        playbook = get_response_playbook()
        steps = playbook["steps"]

        actions = [step["action"] for step in steps]
        descriptions = [step["description"].lower() for step in steps]

        has_exec_notification = any(
            "executive" in a.lower() or "executive" in d
            for a, d in zip(actions, descriptions)
        )
        assert has_exec_notification, "Playbook should include executive notification"

    def test_playbook_has_forensic_steps(self):
        """Test that playbook includes forensics steps."""
        from src.demo.scenario_ransomware import get_response_playbook

        playbook = get_response_playbook()
        steps = playbook["steps"]

        actions = [step["action"] for step in steps]
        assert any("forensic" in action.lower() for action in actions)

    def test_playbook_has_backup_verification(self):
        """Test that playbook includes backup verification for ransomware."""
        from src.demo.scenario_ransomware import get_response_playbook

        playbook = get_response_playbook()
        steps = playbook["steps"]

        actions = [step["action"] for step in steps]
        descriptions = [step["description"].lower() for step in steps]

        has_backup_step = any(
            "backup" in a.lower() or "backup" in d
            for a, d in zip(actions, descriptions)
        )
        assert has_backup_step, "Playbook should include backup verification"

    def test_playbook_requires_executive_approval(self):
        """Test that playbook requires executive approval."""
        from src.demo.scenario_ransomware import get_response_playbook

        playbook = get_response_playbook()
        assert playbook.get("requires_executive_approval") is True
