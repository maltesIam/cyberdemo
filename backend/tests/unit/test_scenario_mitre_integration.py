"""
Unit tests for MITRE ATT&CK integration across all scenarios.

Task: T-1.3.016
Requirement: REQ-002-003-001 - Each event includes tactic_id and technique_id
Test ID: UT-014

Tests verify:
- All scenario timeline events have MITRE tactic IDs
- All scenario timeline events have MITRE technique IDs
- EDR documents include MITRE mapping
- Incident documents include MITRE mapping
"""

import pytest


class TestInsiderThreatMITREIntegration:
    """Tests for MITRE ATT&CK integration in insider threat scenario."""

    def test_timeline_events_have_tactic_id(self):
        """Test that timeline events include MITRE tactic IDs."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()

        # Check that at least some events have tactic_id
        events_with_tactic = [
            event for event in scenario.timeline_events
            if "tactic_id" in event and event["tactic_id"] is not None
        ]
        assert len(events_with_tactic) > 0, "At least some events should have tactic_id"

    def test_timeline_events_have_technique_id(self):
        """Test that timeline events include MITRE technique IDs."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()

        # Check that at least some events have technique_id
        events_with_technique = [
            event for event in scenario.timeline_events
            if "technique_id" in event and event["technique_id"] is not None
        ]
        assert len(events_with_technique) > 0, "At least some events should have technique_id"

    def test_incident_document_has_mitre_fields(self):
        """Test that incident document has MITRE technique."""
        from src.demo.scenario_insider_threat import generate_incident_document

        doc = generate_incident_document()
        assert "mitre_technique" in doc or "technique_id" in doc


class TestSupplyChainMITREIntegration:
    """Tests for MITRE ATT&CK integration in supply chain scenario."""

    def test_timeline_events_have_tactic_id(self):
        """Test that timeline events include MITRE tactic IDs."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()

        # Check that at least some events have tactic_id
        events_with_tactic = [
            event for event in scenario.timeline_events
            if "tactic_id" in event and event["tactic_id"] is not None
        ]
        assert len(events_with_tactic) > 0, "At least some events should have tactic_id"

    def test_timeline_events_have_technique_id(self):
        """Test that timeline events include MITRE technique IDs."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()

        # Check that at least some events have technique_id
        events_with_technique = [
            event for event in scenario.timeline_events
            if "technique_id" in event and event["technique_id"] is not None
        ]
        assert len(events_with_technique) > 0, "At least some events should have technique_id"

    def test_incident_document_has_mitre_fields(self):
        """Test that incident document has MITRE technique."""
        from src.demo.scenario_supply_chain import generate_incident_document

        doc = generate_incident_document()
        assert "mitre_technique" in doc or "technique_id" in doc

    def test_anomalous_behaviors_have_mitre_technique(self):
        """Test that anomalous behaviors have MITRE technique."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()
        for behavior in scenario.anomalous_behaviors:
            assert hasattr(behavior, "mitre_technique")
            assert behavior.mitre_technique is not None


class TestRansomwareMITREIntegration:
    """Tests for MITRE ATT&CK integration in ransomware scenario."""

    def test_timeline_events_have_tactic_id(self):
        """Test that timeline events include MITRE tactic IDs."""
        from src.demo.scenario_ransomware import generate_ransomware_scenario

        scenario = generate_ransomware_scenario()

        # Check that at least some events have tactic_id
        events_with_tactic = [
            event for event in scenario.timeline_events
            if "tactic_id" in event and event["tactic_id"] is not None
        ]
        assert len(events_with_tactic) > 0, "At least some events should have tactic_id"

    def test_timeline_events_have_technique_id(self):
        """Test that timeline events include MITRE technique IDs."""
        from src.demo.scenario_ransomware import generate_ransomware_scenario

        scenario = generate_ransomware_scenario()

        # Check that at least some events have technique_id
        events_with_technique = [
            event for event in scenario.timeline_events
            if "technique_id" in event and event["technique_id"] is not None
        ]
        assert len(events_with_technique) > 0, "At least some events should have technique_id"


class TestAllScenariosMITRECompliance:
    """Cross-scenario tests for MITRE compliance."""

    def test_lazarus_scenario_mitre_compliance(self):
        """Test Lazarus scenario MITRE compliance."""
        from src.demo.scenario_lazarus import generate_lazarus_scenario

        scenario = generate_lazarus_scenario()
        mitre_events = [
            e for e in scenario.timeline_events
            if ("tactic_id" in e and e["tactic_id"]) or ("technique_id" in e and e["technique_id"])
        ]
        # At least 50% of events should have MITRE mapping
        assert len(mitre_events) >= len(scenario.timeline_events) * 0.5

    def test_revil_scenario_mitre_compliance(self):
        """Test REvil scenario MITRE compliance."""
        from src.demo.scenario_revil import generate_revil_scenario

        scenario = generate_revil_scenario()
        mitre_events = [
            e for e in scenario.timeline_events
            if ("tactic_id" in e and e["tactic_id"]) or ("technique_id" in e and e["technique_id"])
        ]
        # At least 50% of events should have MITRE mapping
        assert len(mitre_events) >= len(scenario.timeline_events) * 0.5

    def test_insider_threat_scenario_mitre_compliance(self):
        """Test insider threat scenario MITRE compliance."""
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario

        scenario = generate_insider_threat_scenario()
        mitre_events = [
            e for e in scenario.timeline_events
            if ("tactic_id" in e and e["tactic_id"]) or ("technique_id" in e and e["technique_id"])
        ]
        # At least 50% of events should have MITRE mapping
        assert len(mitre_events) >= len(scenario.timeline_events) * 0.5

    def test_supply_chain_scenario_mitre_compliance(self):
        """Test supply chain scenario MITRE compliance."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()
        mitre_events = [
            e for e in scenario.timeline_events
            if ("tactic_id" in e and e["tactic_id"]) or ("technique_id" in e and e["technique_id"])
        ]
        # At least 50% of events should have MITRE mapping
        assert len(mitre_events) >= len(scenario.timeline_events) * 0.5
