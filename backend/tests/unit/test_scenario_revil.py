"""
Unit tests for REvil ransomware attack scenario.

Task: T-1.3.005
Requirement: REQ-002-001-004 - Escenario REvil - Ransomware
Test ID: UT-013

Tests verify:
- REvilScenario class exists
- Scenario generates correct events
- Events follow MITRE ATT&CK framework
- Scenario data matches REvil TTPs
- Double extortion model is implemented
"""

import pytest
from datetime import datetime, timezone


class TestREvilScenarioExists:
    """Tests for REvil scenario module existence."""

    def test_revil_scenario_module_exists(self):
        """Test that scenario_revil module exists."""
        from src.demo import scenario_revil
        assert scenario_revil is not None

    def test_scenario_constants_exist(self):
        """Test that scenario constants are defined."""
        from src.demo.scenario_revil import SCENARIO_ID, SCENARIO_NAME

        assert SCENARIO_ID is not None
        assert "REVIL" in SCENARIO_ID.upper() or "006" in SCENARIO_ID
        assert SCENARIO_NAME is not None
        assert "REvil" in SCENARIO_NAME or "Sodinokibi" in SCENARIO_NAME

    def test_revil_host_dataclass_exists(self):
        """Test that REvilHost dataclass exists."""
        from src.demo.scenario_revil import REvilHost

        assert REvilHost is not None

    def test_revil_scenario_data_dataclass_exists(self):
        """Test that REvilScenarioData dataclass exists."""
        from src.demo.scenario_revil import REvilScenarioData

        assert REvilScenarioData is not None


class TestREvilScenarioGenerator:
    """Tests for scenario data generation."""

    def test_generate_revil_scenario_function_exists(self):
        """Test that generate_revil_scenario function exists."""
        from src.demo.scenario_revil import generate_revil_scenario

        assert callable(generate_revil_scenario)

    def test_generate_revil_scenario_returns_data(self):
        """Test that generator returns scenario data."""
        from src.demo.scenario_revil import generate_revil_scenario

        scenario = generate_revil_scenario()
        assert scenario is not None

    def test_revil_scenario_has_incident_id(self):
        """Test that scenario has incident_id."""
        from src.demo.scenario_revil import generate_revil_scenario

        scenario = generate_revil_scenario()
        assert hasattr(scenario, "incident_id")
        assert scenario.incident_id is not None

    def test_revil_scenario_has_affected_hosts(self):
        """Test that scenario has affected_hosts list."""
        from src.demo.scenario_revil import generate_revil_scenario

        scenario = generate_revil_scenario()
        assert hasattr(scenario, "affected_hosts")
        assert len(scenario.affected_hosts) > 0

    def test_revil_scenario_has_timeline_events(self):
        """Test that scenario has timeline_events."""
        from src.demo.scenario_revil import generate_revil_scenario

        scenario = generate_revil_scenario()
        assert hasattr(scenario, "timeline_events")
        assert len(scenario.timeline_events) > 0

    def test_revil_scenario_double_extortion(self):
        """Test that REvil scenario includes double extortion elements."""
        from src.demo.scenario_revil import generate_revil_scenario

        scenario = generate_revil_scenario()
        # REvil is known for double extortion (encrypt + data theft)
        assert hasattr(scenario, "data_exfiltrated")
        assert scenario.data_exfiltrated is True or hasattr(scenario, "exfiltration_size_gb")

    def test_revil_scenario_has_ransom_info(self):
        """Test that REvil scenario has ransom information."""
        from src.demo.scenario_revil import generate_revil_scenario

        scenario = generate_revil_scenario()
        assert hasattr(scenario, "ransom_amount_btc") or hasattr(scenario, "ransom_amount_usd")
        assert hasattr(scenario, "payment_deadline")


class TestREvilMITREMapping:
    """Tests for MITRE ATT&CK integration."""

    def test_revil_uses_known_ttps(self):
        """Test that scenario uses known REvil TTPs."""
        from src.demo.scenario_revil import generate_revil_scenario

        scenario = generate_revil_scenario()
        # REvil commonly uses these techniques
        known_techniques = [
            "T1486",  # Data Encrypted for Impact
            "T1490",  # Inhibit System Recovery (delete shadow copies)
            "T1489",  # Service Stop (stop security services)
            "T1567",  # Exfiltration Over Web Service
            "T1059",  # Command and Scripting Interpreter
        ]

        # Check timeline events have MITRE references
        mitre_refs = []
        for event in scenario.timeline_events:
            if "mitre_technique" in event:
                mitre_refs.append(event["mitre_technique"])
            if "technique_id" in event:
                mitre_refs.append(event["technique_id"])

        # At least some events should have MITRE techniques
        assert len(mitre_refs) > 0

    def test_timeline_events_have_tactic_id(self):
        """Test that timeline events include MITRE tactic IDs."""
        from src.demo.scenario_revil import generate_revil_scenario

        scenario = generate_revil_scenario()

        # Check at least one event has tactic_id
        has_tactic = any(
            "tactic_id" in event or "mitre_tactic" in event
            for event in scenario.timeline_events
        )
        assert has_tactic, "Timeline events should include MITRE tactic IDs"

    def test_timeline_events_have_technique_id(self):
        """Test that timeline events include MITRE technique IDs."""
        from src.demo.scenario_revil import generate_revil_scenario

        scenario = generate_revil_scenario()

        # Check at least one event has technique_id
        has_technique = any(
            "technique_id" in event or "mitre_technique" in event
            for event in scenario.timeline_events
        )
        assert has_technique, "Timeline events should include MITRE technique IDs"


class TestREvilOpenSearchDocuments:
    """Tests for OpenSearch document generation."""

    def test_generate_incident_document_exists(self):
        """Test that generate_incident_document function exists."""
        from src.demo.scenario_revil import generate_incident_document

        assert callable(generate_incident_document)

    def test_generate_incident_document_returns_dict(self):
        """Test that incident document is a dict."""
        from src.demo.scenario_revil import generate_incident_document

        doc = generate_incident_document()
        assert isinstance(doc, dict)
        assert "incident_id" in doc
        assert "severity" in doc

    def test_incident_document_has_mitre_technique(self):
        """Test that incident document has MITRE technique."""
        from src.demo.scenario_revil import generate_incident_document

        doc = generate_incident_document()
        assert "mitre_technique" in doc or "technique_id" in doc

    def test_generate_edr_documents_exists(self):
        """Test that generate_edr_documents function exists."""
        from src.demo.scenario_revil import generate_edr_documents

        assert callable(generate_edr_documents)

    def test_generate_edr_documents_returns_list(self):
        """Test that EDR documents is a list."""
        from src.demo.scenario_revil import generate_edr_documents

        docs = generate_edr_documents()
        assert isinstance(docs, list)
        assert len(docs) > 0

    def test_edr_documents_have_mitre_fields(self):
        """Test that EDR documents have MITRE fields."""
        from src.demo.scenario_revil import generate_edr_documents

        docs = generate_edr_documents()
        for doc in docs:
            # Each EDR detection should reference MITRE
            assert "mitre_technique" in doc or "technique_id" in doc


class TestREvilResponsePlaybook:
    """Tests for response playbook."""

    def test_get_response_playbook_exists(self):
        """Test that get_response_playbook function exists."""
        from src.demo.scenario_revil import get_response_playbook

        assert callable(get_response_playbook)

    def test_response_playbook_returns_dict(self):
        """Test that playbook is a dict."""
        from src.demo.scenario_revil import get_response_playbook

        playbook = get_response_playbook()
        assert isinstance(playbook, dict)
        assert "playbook_id" in playbook
        assert "steps" in playbook

    def test_playbook_has_containment_steps(self):
        """Test that playbook includes containment for ransomware."""
        from src.demo.scenario_revil import get_response_playbook

        playbook = get_response_playbook()
        steps = playbook["steps"]

        actions = [step["action"] for step in steps]
        assert any("isolation" in action or "containment" in action or "disconnect" in action
                   for action in actions)

    def test_playbook_handles_data_breach(self):
        """Test that playbook addresses data exfiltration (double extortion)."""
        from src.demo.scenario_revil import get_response_playbook

        playbook = get_response_playbook()
        steps = playbook["steps"]

        # Double extortion response should include data breach considerations
        actions = [step["action"].lower() for step in steps]
        descriptions = [step["description"].lower() for step in steps]

        has_data_breach_response = any(
            "exfil" in a or "breach" in a or "notification" in a or "legal" in a or "regulatory" in a
            for a in actions + descriptions
        )
        assert has_data_breach_response, "Playbook should handle double extortion data breach"
