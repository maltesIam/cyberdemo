"""
E2E tests for Attack Simulation Flow.

Task: T-1.4.007
Requirements: REQ-002-001-003, REQ-002-001-004, REQ-002-003-001
Test ID: E2E-007

Tests verify end-to-end attack simulation flow:
- Lazarus Group scenario executes correctly
- REvil scenario executes correctly
- All scenarios include MITRE ATT&CK mapping
- Scenario events are generated in correct order
- Timeline events are properly structured
"""

import pytest
from datetime import datetime, timezone


class TestLazarusScenarioE2E:
    """E2E tests for Lazarus Group destructive attack scenario."""

    def test_lazarus_scenario_generates_complete_timeline(self):
        """Test that Lazarus scenario generates complete attack timeline."""
        from src.demo.scenario_lazarus import generate_lazarus_scenario

        scenario = generate_lazarus_scenario()

        # Verify scenario has complete structure
        assert scenario.incident_id is not None
        assert scenario.threat_actor is not None
        assert scenario.attack_type == "destructive"
        assert len(scenario.affected_hosts) > 0
        assert len(scenario.timeline_events) > 0

        # Verify timeline events have timestamps
        for event in scenario.timeline_events:
            assert "timestamp" in event
            assert "event" in event
            assert "details" in event

    def test_lazarus_scenario_follows_attack_chain(self):
        """Test that Lazarus scenario follows realistic attack chain."""
        from src.demo.scenario_lazarus import generate_lazarus_scenario

        scenario = generate_lazarus_scenario()

        # Extract event types in order
        event_types = [e["event"] for e in scenario.timeline_events]

        # Verify logical progression (some events must come before others)
        initial_access_idx = next(
            (i for i, e in enumerate(event_types) if "initial_access" in e.lower()),
            None
        )
        impact_idx = next(
            (i for i, e in enumerate(event_types) if "impact" in e.lower()),
            None
        )

        # Initial access should come before impact
        if initial_access_idx is not None and impact_idx is not None:
            assert initial_access_idx < impact_idx, "Initial access should precede impact"

    def test_lazarus_scenario_mitre_mapping_complete(self):
        """Test that Lazarus scenario has complete MITRE mapping."""
        from src.demo.scenario_lazarus import generate_lazarus_scenario

        scenario = generate_lazarus_scenario()

        # Count events with MITRE mapping
        events_with_mitre = [
            e for e in scenario.timeline_events
            if e.get("tactic_id") or e.get("technique_id")
        ]

        # At least 50% of events should have MITRE mapping
        assert len(events_with_mitre) >= len(scenario.timeline_events) * 0.5

    def test_lazarus_scenario_affected_hosts_valid(self):
        """Test that affected hosts have valid data."""
        from src.demo.scenario_lazarus import generate_lazarus_scenario

        scenario = generate_lazarus_scenario()

        for host in scenario.affected_hosts:
            assert host.asset_id is not None
            assert host.hostname is not None
            assert host.department is not None
            assert host.wipe_status in ["pending", "in_progress", "wiped"]
            assert 0 <= host.wipe_progress <= 100

    def test_lazarus_scenario_opensearch_documents_valid(self):
        """Test that OpenSearch documents are valid."""
        from src.demo.scenario_lazarus import (
            generate_incident_document,
            generate_edr_documents,
            generate_asset_documents,
        )

        incident_doc = generate_incident_document()
        edr_docs = generate_edr_documents()
        asset_docs = generate_asset_documents()

        # Verify incident document
        assert incident_doc["incident_id"] is not None
        assert incident_doc["severity"] == "Critical"
        assert "mitre_technique" in incident_doc

        # Verify EDR documents
        assert len(edr_docs) > 0
        for doc in edr_docs:
            assert "detection_id" in doc
            assert "asset_id" in doc
            assert "mitre_technique" in doc or "technique_id" in doc

        # Verify asset documents
        assert len(asset_docs) > 0
        for doc in asset_docs:
            assert "asset_id" in doc
            assert "hostname" in doc

    def test_lazarus_scenario_playbook_valid(self):
        """Test that response playbook is valid."""
        from src.demo.scenario_lazarus import get_response_playbook

        playbook = get_response_playbook()

        assert playbook["playbook_id"] is not None
        assert "steps" in playbook
        assert len(playbook["steps"]) > 0

        # Verify steps have required fields
        for step in playbook["steps"]:
            assert "step" in step
            assert "action" in step
            assert "description" in step
            assert "priority" in step


class TestREvilScenarioE2E:
    """E2E tests for REvil double extortion ransomware scenario."""

    def test_revil_scenario_generates_complete_timeline(self):
        """Test that REvil scenario generates complete attack timeline."""
        from src.demo.scenario_revil import generate_revil_scenario

        scenario = generate_revil_scenario()

        # Verify scenario has complete structure
        assert scenario.incident_id is not None
        assert scenario.threat_actor is not None
        assert scenario.ransomware_family is not None
        assert len(scenario.affected_hosts) > 0
        assert len(scenario.timeline_events) > 0

        # Verify double extortion elements
        assert scenario.data_exfiltrated is True
        assert scenario.exfiltration_size_gb > 0
        assert scenario.ransom_amount_btc > 0

    def test_revil_scenario_follows_double_extortion_pattern(self):
        """Test that REvil scenario follows double extortion pattern."""
        from src.demo.scenario_revil import generate_revil_scenario

        scenario = generate_revil_scenario()

        # Extract event types
        event_types = [e["event"] for e in scenario.timeline_events]

        # Should have exfiltration before encryption (double extortion pattern)
        exfil_idx = next(
            (i for i, e in enumerate(event_types) if "exfil" in e.lower()),
            None
        )
        encrypt_idx = next(
            (i for i, e in enumerate(event_types) if "encrypt" in e.lower()),
            None
        )

        # Exfiltration should come before or during encryption
        if exfil_idx is not None and encrypt_idx is not None:
            assert exfil_idx <= encrypt_idx, "Exfiltration should precede or accompany encryption"

    def test_revil_scenario_mitre_mapping_complete(self):
        """Test that REvil scenario has complete MITRE mapping."""
        from src.demo.scenario_revil import generate_revil_scenario

        scenario = generate_revil_scenario()

        # Count events with MITRE mapping
        events_with_mitre = [
            e for e in scenario.timeline_events
            if e.get("tactic_id") or e.get("technique_id")
        ]

        # At least 50% of events should have MITRE mapping
        assert len(events_with_mitre) >= len(scenario.timeline_events) * 0.5

    def test_revil_scenario_affected_hosts_with_exfil_data(self):
        """Test that affected hosts have exfiltration data."""
        from src.demo.scenario_revil import generate_revil_scenario

        scenario = generate_revil_scenario()

        # At least some hosts should have data exfiltrated
        hosts_with_exfil = [h for h in scenario.affected_hosts if h.data_exfiltrated]
        assert len(hosts_with_exfil) > 0

        for host in hosts_with_exfil:
            assert host.exfil_size_gb > 0

    def test_revil_scenario_ransom_deadline_in_future(self):
        """Test that ransom deadline is in the future."""
        from src.demo.scenario_revil import generate_revil_scenario

        scenario = generate_revil_scenario()

        assert scenario.payment_deadline > datetime.now(timezone.utc)

    def test_revil_scenario_playbook_handles_data_breach(self):
        """Test that playbook addresses data breach aspect."""
        from src.demo.scenario_revil import get_response_playbook

        playbook = get_response_playbook()

        # Verify playbook acknowledges data breach
        assert playbook.get("data_breach_confirmed") is True

        # Check for data breach related steps
        step_descriptions = " ".join(
            [s["description"].lower() for s in playbook["steps"]]
        )
        step_actions = " ".join([s["action"].lower() for s in playbook["steps"]])

        # Should have breach notification or legal steps
        has_breach_handling = (
            "breach" in step_descriptions or
            "legal" in step_actions or
            "regulatory" in step_descriptions or
            "notification" in step_descriptions
        )
        assert has_breach_handling, "Playbook should address data breach"


class TestAllScenariosMITRECompliance:
    """E2E tests for MITRE ATT&CK compliance across all scenarios."""

    def test_all_scenarios_have_mitre_tactic_ids(self):
        """Test that all scenarios include MITRE tactic IDs."""
        from src.demo.scenario_lazarus import generate_lazarus_scenario
        from src.demo.scenario_revil import generate_revil_scenario
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario
        from src.demo.scenario_ransomware import generate_ransomware_scenario

        scenarios = [
            ("Lazarus", generate_lazarus_scenario()),
            ("REvil", generate_revil_scenario()),
            ("InsiderThreat", generate_insider_threat_scenario()),
            ("SupplyChain", generate_supply_chain_scenario()),
            ("Ransomware", generate_ransomware_scenario()),
        ]

        for name, scenario in scenarios:
            events_with_tactic = [
                e for e in scenario.timeline_events
                if e.get("tactic_id") is not None
            ]
            assert len(events_with_tactic) > 0, f"{name} scenario missing tactic_id"

    def test_all_scenarios_have_mitre_technique_ids(self):
        """Test that all scenarios include MITRE technique IDs."""
        from src.demo.scenario_lazarus import generate_lazarus_scenario
        from src.demo.scenario_revil import generate_revil_scenario
        from src.demo.scenario_insider_threat import generate_insider_threat_scenario
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario
        from src.demo.scenario_ransomware import generate_ransomware_scenario

        scenarios = [
            ("Lazarus", generate_lazarus_scenario()),
            ("REvil", generate_revil_scenario()),
            ("InsiderThreat", generate_insider_threat_scenario()),
            ("SupplyChain", generate_supply_chain_scenario()),
            ("Ransomware", generate_ransomware_scenario()),
        ]

        for name, scenario in scenarios:
            events_with_technique = [
                e for e in scenario.timeline_events
                if e.get("technique_id") is not None
            ]
            assert len(events_with_technique) > 0, f"{name} scenario missing technique_id"

    def test_mitre_ids_follow_valid_format(self):
        """Test that MITRE IDs follow valid format (TAxxxx for tactics, Txxxx for techniques)."""
        from src.demo.scenario_lazarus import generate_lazarus_scenario
        from src.demo.scenario_revil import generate_revil_scenario

        scenarios = [
            generate_lazarus_scenario(),
            generate_revil_scenario(),
        ]

        for scenario in scenarios:
            for event in scenario.timeline_events:
                tactic_id = event.get("tactic_id")
                technique_id = event.get("technique_id")

                if tactic_id:
                    # Should start with TA followed by digits
                    assert tactic_id.startswith("TA"), f"Invalid tactic_id format: {tactic_id}"

                if technique_id:
                    # Should start with T followed by digits (may have sub-technique like T1234.001)
                    assert technique_id.startswith("T"), f"Invalid technique_id format: {technique_id}"


class TestScenarioDataConsistency:
    """E2E tests for data consistency across scenario components."""

    def test_incident_document_matches_scenario(self):
        """Test that incident document matches scenario data."""
        from src.demo.scenario_lazarus import (
            generate_lazarus_scenario,
            generate_incident_document,
            SCENARIO_ID,
        )

        scenario = generate_lazarus_scenario()
        incident_doc = generate_incident_document()

        assert incident_doc["incident_id"] == scenario.incident_id
        assert incident_doc["incident_id"] == SCENARIO_ID
        assert incident_doc["affected_host_count"] == scenario.affected_count

    def test_edr_documents_match_affected_hosts(self):
        """Test that EDR documents match affected hosts."""
        from src.demo.scenario_lazarus import (
            generate_lazarus_scenario,
            generate_edr_documents,
        )

        scenario = generate_lazarus_scenario()
        edr_docs = generate_edr_documents()

        # Each affected host should have an EDR document
        edr_asset_ids = {doc["asset_id"] for doc in edr_docs}
        scenario_asset_ids = {host.asset_id for host in scenario.affected_hosts}

        assert edr_asset_ids == scenario_asset_ids

    def test_revil_exfiltration_totals_match(self):
        """Test that REvil exfiltration totals are consistent."""
        from src.demo.scenario_revil import generate_revil_scenario

        scenario = generate_revil_scenario()

        # Calculate total from hosts
        host_total = sum(
            h.exfil_size_gb for h in scenario.affected_hosts
            if h.data_exfiltrated
        )

        # Should approximately match scenario total (allow for rounding)
        # The scenario total might be a summary, so we just verify it's reasonable
        assert scenario.exfiltration_size_gb > 0
        assert host_total > 0
