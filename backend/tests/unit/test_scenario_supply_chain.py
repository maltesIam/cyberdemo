"""
Unit tests for Supply Chain Attack scenario.

Task: T-1.3.007
Requirement: REQ-002-001-005 - Escenario Supply Chain - Compromised Software
Test ID: UT-015

Tests verify:
- SupplyChainScenario class exists
- Scenario generates correct events
- Events follow MITRE ATT&CK framework
- Scenario data matches supply chain TTPs
- Hash verification and vendor notification flow
"""

import pytest
from datetime import datetime, timezone


class TestSupplyChainScenarioExists:
    """Tests for Supply Chain scenario module existence."""

    def test_supply_chain_scenario_module_exists(self):
        """Test that scenario_supply_chain module exists."""
        from src.demo import scenario_supply_chain
        assert scenario_supply_chain is not None

    def test_scenario_constants_exist(self):
        """Test that scenario constants are defined."""
        from src.demo.scenario_supply_chain import SCENARIO_ID, SCENARIO_NAME

        assert SCENARIO_ID is not None
        assert "006" in SCENARIO_ID or "ANCHOR" in SCENARIO_ID
        assert SCENARIO_NAME is not None
        assert "Supply Chain" in SCENARIO_NAME

    def test_legitimate_software_constant_exists(self):
        """Test that legitimate software constant exists."""
        from src.demo.scenario_supply_chain import LEGITIMATE_SOFTWARE

        assert LEGITIMATE_SOFTWARE is not None
        assert len(LEGITIMATE_SOFTWARE) > 0

    def test_vendor_name_constant_exists(self):
        """Test that vendor name constant exists."""
        from src.demo.scenario_supply_chain import VENDOR_NAME

        assert VENDOR_NAME is not None

    def test_compromised_hash_constant_exists(self):
        """Test that compromised hash constant exists."""
        from src.demo.scenario_supply_chain import COMPROMISED_HASH

        assert COMPROMISED_HASH is not None
        assert len(COMPROMISED_HASH) == 64  # SHA256 hash length

    def test_legitimate_hash_constant_exists(self):
        """Test that legitimate hash constant exists."""
        from src.demo.scenario_supply_chain import LEGITIMATE_HASH

        assert LEGITIMATE_HASH is not None
        assert len(LEGITIMATE_HASH) == 64  # SHA256 hash length

    def test_hashes_are_different(self):
        """Test that compromised and legitimate hashes are different."""
        from src.demo.scenario_supply_chain import COMPROMISED_HASH, LEGITIMATE_HASH

        assert COMPROMISED_HASH != LEGITIMATE_HASH

    def test_software_version_dataclass_exists(self):
        """Test that SoftwareVersion dataclass exists."""
        from src.demo.scenario_supply_chain import SoftwareVersion

        assert SoftwareVersion is not None

    def test_anomalous_behavior_dataclass_exists(self):
        """Test that AnomalousBehavior dataclass exists."""
        from src.demo.scenario_supply_chain import AnomalousBehavior

        assert AnomalousBehavior is not None

    def test_affected_asset_dataclass_exists(self):
        """Test that AffectedAsset dataclass exists."""
        from src.demo.scenario_supply_chain import AffectedAsset

        assert AffectedAsset is not None

    def test_supply_chain_scenario_data_dataclass_exists(self):
        """Test that SupplyChainScenarioData dataclass exists."""
        from src.demo.scenario_supply_chain import SupplyChainScenarioData

        assert SupplyChainScenarioData is not None


class TestSupplyChainScenarioGenerator:
    """Tests for scenario data generation."""

    def test_generate_supply_chain_scenario_function_exists(self):
        """Test that generate_supply_chain_scenario function exists."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        assert callable(generate_supply_chain_scenario)

    def test_generate_supply_chain_scenario_returns_data(self):
        """Test that generator returns scenario data."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()
        assert scenario is not None

    def test_supply_chain_scenario_has_incident_id(self):
        """Test that scenario has incident_id."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()
        assert hasattr(scenario, "incident_id")
        assert scenario.incident_id is not None

    def test_supply_chain_scenario_has_affected_assets(self):
        """Test that scenario has affected_assets list."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()
        assert hasattr(scenario, "affected_assets")
        assert len(scenario.affected_assets) > 0

    def test_supply_chain_scenario_has_timeline_events(self):
        """Test that scenario has timeline_events."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()
        assert hasattr(scenario, "timeline_events")
        assert len(scenario.timeline_events) > 0

    def test_supply_chain_scenario_has_software_info(self):
        """Test that scenario has software information."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()
        assert hasattr(scenario, "software_name")
        assert hasattr(scenario, "vendor_name")
        assert hasattr(scenario, "compromised_version")
        assert hasattr(scenario, "legitimate_version")

    def test_supply_chain_scenario_has_hash_info(self):
        """Test that scenario has hash information."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()
        assert hasattr(scenario, "compromised_hash")
        assert hasattr(scenario, "legitimate_hash")
        assert scenario.compromised_hash != scenario.legitimate_hash

    def test_supply_chain_scenario_has_c2_infrastructure(self):
        """Test that scenario has C2 infrastructure details."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()
        assert hasattr(scenario, "c2_domains")
        assert hasattr(scenario, "c2_ips")
        assert len(scenario.c2_domains) > 0
        assert len(scenario.c2_ips) > 0

    def test_supply_chain_scenario_has_backdoor_capabilities(self):
        """Test that scenario has backdoor capabilities list."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()
        assert hasattr(scenario, "backdoor_capabilities")
        assert len(scenario.backdoor_capabilities) > 0

    def test_supply_chain_scenario_has_anomalous_behaviors(self):
        """Test that scenario has anomalous behaviors list."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()
        assert hasattr(scenario, "anomalous_behaviors")
        assert len(scenario.anomalous_behaviors) > 0

    def test_supply_chain_scenario_has_affected_count_property(self):
        """Test that scenario has affected_count computed property."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()
        assert hasattr(scenario, "affected_count")
        assert scenario.affected_count == len(scenario.affected_assets)

    def test_supply_chain_scenario_has_vendor_contacted_flag(self):
        """Test that scenario has vendor_contacted flag."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()
        assert hasattr(scenario, "vendor_contacted")
        assert isinstance(scenario.vendor_contacted, bool)


class TestSupplyChainMITREMapping:
    """Tests for MITRE ATT&CK integration."""

    def test_supply_chain_uses_known_ttps(self):
        """Test that scenario uses known supply chain TTPs."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()
        # Supply chain attacks commonly use these techniques
        known_techniques = [
            "T1195.002",  # Compromise Software Supply Chain
            "T1071.001",  # Web Protocols
            "T1055.001",  # Process Injection
            "T1555.003",  # Credentials from Web Browsers
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
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()

        # Check at least one event has tactic_id
        has_tactic = any(
            ("tactic_id" in event and event["tactic_id"]) or
            ("mitre_tactic" in event and event["mitre_tactic"])
            for event in scenario.timeline_events
        )
        assert has_tactic, "Timeline events should include MITRE tactic IDs"

    def test_timeline_events_have_technique_id(self):
        """Test that timeline events include MITRE technique IDs."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()

        # Check at least one event has technique_id
        has_technique = any(
            ("technique_id" in event and event["technique_id"]) or
            ("mitre_technique" in event and event["mitre_technique"])
            for event in scenario.timeline_events
        )
        assert has_technique, "Timeline events should include MITRE technique IDs"

    def test_timeline_has_supply_chain_technique(self):
        """Test that timeline includes Supply Chain technique (T1195.002)."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()

        # Check for Supply Chain technique
        has_supply_chain = any(
            event.get("technique_id") == "T1195.002" or
            event.get("mitre_technique") == "T1195.002"
            for event in scenario.timeline_events
        )
        assert has_supply_chain, "Timeline should include Supply Chain technique (T1195.002)"

    def test_anomalous_behaviors_have_mitre_technique(self):
        """Test that anomalous behaviors have MITRE techniques."""
        from src.demo.scenario_supply_chain import generate_supply_chain_scenario

        scenario = generate_supply_chain_scenario()

        for behavior in scenario.anomalous_behaviors:
            assert hasattr(behavior, "mitre_technique")
            assert behavior.mitre_technique is not None


class TestSupplyChainOpenSearchDocuments:
    """Tests for OpenSearch document generation."""

    def test_generate_incident_document_exists(self):
        """Test that generate_incident_document function exists."""
        from src.demo.scenario_supply_chain import generate_incident_document

        assert callable(generate_incident_document)

    def test_generate_incident_document_returns_dict(self):
        """Test that incident document is a dict."""
        from src.demo.scenario_supply_chain import generate_incident_document

        doc = generate_incident_document()
        assert isinstance(doc, dict)
        assert "incident_id" in doc
        assert "severity" in doc

    def test_incident_document_severity_is_critical(self):
        """Test that supply chain incident has critical severity."""
        from src.demo.scenario_supply_chain import generate_incident_document

        doc = generate_incident_document()
        assert doc["severity"] == "Critical"

    def test_incident_document_has_mitre_technique(self):
        """Test that incident document has MITRE technique."""
        from src.demo.scenario_supply_chain import generate_incident_document

        doc = generate_incident_document()
        assert "mitre_technique" in doc or "technique_id" in doc
        # Should be supply chain technique
        assert doc.get("mitre_technique") == "T1195.002"

    def test_incident_document_has_vendor_info(self):
        """Test that incident document has vendor information."""
        from src.demo.scenario_supply_chain import generate_incident_document

        doc = generate_incident_document()
        assert "vendor_name" in doc

    def test_generate_asset_documents_exists(self):
        """Test that generate_asset_documents function exists."""
        from src.demo.scenario_supply_chain import generate_asset_documents

        assert callable(generate_asset_documents)

    def test_generate_asset_documents_returns_list(self):
        """Test that asset documents is a list."""
        from src.demo.scenario_supply_chain import generate_asset_documents

        docs = generate_asset_documents()
        assert isinstance(docs, list)
        assert len(docs) > 0

    def test_asset_documents_have_installed_software(self):
        """Test that asset documents have installed software info."""
        from src.demo.scenario_supply_chain import generate_asset_documents

        docs = generate_asset_documents()
        for doc in docs:
            assert "installed_software" in doc
            assert "version" in doc["installed_software"]

    def test_generate_intel_document_exists(self):
        """Test that generate_intel_document function exists."""
        from src.demo.scenario_supply_chain import generate_intel_document

        assert callable(generate_intel_document)

    def test_generate_intel_document_returns_dict(self):
        """Test that intel document is a dict."""
        from src.demo.scenario_supply_chain import generate_intel_document

        doc = generate_intel_document()
        assert isinstance(doc, dict)
        assert "hash" in doc
        assert "verdict" in doc
        assert doc["verdict"] == "malicious"

    def test_intel_document_has_trojanized_flag(self):
        """Test that intel document has trojanized software flag."""
        from src.demo.scenario_supply_chain import generate_intel_document

        doc = generate_intel_document()
        assert "legitimate_software_trojanized" in doc
        assert doc["legitimate_software_trojanized"] is True

    def test_generate_software_verification_document_exists(self):
        """Test that generate_software_verification_document function exists."""
        from src.demo.scenario_supply_chain import generate_software_verification_document

        assert callable(generate_software_verification_document)

    def test_software_verification_document_shows_mismatch(self):
        """Test that software verification document shows hash mismatch."""
        from src.demo.scenario_supply_chain import generate_software_verification_document

        doc = generate_software_verification_document()
        assert isinstance(doc, dict)
        assert "verification_status" in doc
        assert doc["verification_status"] == "MISMATCH"

    def test_generate_ioc_documents_exists(self):
        """Test that generate_ioc_documents function exists."""
        from src.demo.scenario_supply_chain import generate_ioc_documents

        assert callable(generate_ioc_documents)

    def test_generate_ioc_documents_returns_list(self):
        """Test that IOC documents is a list."""
        from src.demo.scenario_supply_chain import generate_ioc_documents

        docs = generate_ioc_documents()
        assert isinstance(docs, list)
        assert len(docs) > 0

    def test_ioc_documents_have_c2_indicators(self):
        """Test that IOC documents include C2 indicators."""
        from src.demo.scenario_supply_chain import generate_ioc_documents

        docs = generate_ioc_documents()

        has_domain = any(doc["type"] == "domain" for doc in docs)
        has_ip = any(doc["type"] == "ip" for doc in docs)

        assert has_domain, "IOC documents should include C2 domains"
        assert has_ip, "IOC documents should include C2 IPs"


class TestSupplyChainResponsePlaybook:
    """Tests for response playbook."""

    def test_get_response_playbook_exists(self):
        """Test that get_response_playbook function exists."""
        from src.demo.scenario_supply_chain import get_response_playbook

        assert callable(get_response_playbook)

    def test_response_playbook_returns_dict(self):
        """Test that playbook is a dict."""
        from src.demo.scenario_supply_chain import get_response_playbook

        playbook = get_response_playbook()
        assert isinstance(playbook, dict)
        assert "playbook_id" in playbook
        assert "steps" in playbook

    def test_playbook_has_hash_verification_step(self):
        """Test that playbook includes hash verification."""
        from src.demo.scenario_supply_chain import get_response_playbook

        playbook = get_response_playbook()
        steps = playbook["steps"]

        actions = [step["action"] for step in steps]
        assert any("hash" in action or "verification" in action
                   for action in actions)

    def test_playbook_has_vendor_notification_step(self):
        """Test that playbook includes vendor notification."""
        from src.demo.scenario_supply_chain import get_response_playbook

        playbook = get_response_playbook()
        steps = playbook["steps"]

        actions = [step["action"] for step in steps]
        descriptions = [step["description"].lower() for step in steps]

        has_vendor_notification = any(
            "vendor" in a.lower() or "vendor" in d
            for a, d in zip(actions, descriptions)
        )
        assert has_vendor_notification, "Playbook should include vendor notification"

    def test_playbook_has_organizational_hunt_step(self):
        """Test that playbook includes organizational hunt."""
        from src.demo.scenario_supply_chain import get_response_playbook

        playbook = get_response_playbook()
        steps = playbook["steps"]

        actions = [step["action"] for step in steps]
        descriptions = [step["description"].lower() for step in steps]

        has_hunt = any(
            "hunt" in a.lower() or "hunt" in d
            for a, d in zip(actions, descriptions)
        )
        assert has_hunt, "Playbook should include organizational hunt"

    def test_playbook_has_network_block_step(self):
        """Test that playbook includes network blocking for C2."""
        from src.demo.scenario_supply_chain import get_response_playbook

        playbook = get_response_playbook()
        steps = playbook["steps"]

        actions = [step["action"] for step in steps]
        descriptions = [step["description"].lower() for step in steps]

        has_block = any(
            "block" in a.lower() or "block" in d
            for a, d in zip(actions, descriptions)
        )
        assert has_block, "Playbook should include network blocking"

    def test_playbook_has_forensic_analysis_step(self):
        """Test that playbook includes forensic analysis."""
        from src.demo.scenario_supply_chain import get_response_playbook

        playbook = get_response_playbook()
        steps = playbook["steps"]

        actions = [step["action"] for step in steps]
        assert any("forensic" in action.lower() for action in actions)

    def test_playbook_requires_vendor_coordination(self):
        """Test that playbook requires vendor coordination."""
        from src.demo.scenario_supply_chain import get_response_playbook

        playbook = get_response_playbook()
        assert playbook.get("requires_vendor_coordination") is True


class TestSupplyChainHuntQuery:
    """Tests for hunt query generation."""

    def test_get_hunt_query_exists(self):
        """Test that get_hunt_query function exists."""
        from src.demo.scenario_supply_chain import get_hunt_query

        assert callable(get_hunt_query)

    def test_get_hunt_query_returns_dict(self):
        """Test that hunt query is a dict."""
        from src.demo.scenario_supply_chain import get_hunt_query

        query = get_hunt_query()
        assert isinstance(query, dict)
        assert "query_type" in query
        assert "filters" in query

    def test_hunt_query_has_hash_filter(self):
        """Test that hunt query includes hash filter."""
        from src.demo.scenario_supply_chain import get_hunt_query

        query = get_hunt_query()
        filters = query["filters"]

        has_hash_filter = any(
            f["field"] == "file.sha256"
            for f in filters
        )
        assert has_hash_filter, "Hunt query should include hash filter"

    def test_hunt_query_has_network_indicators(self):
        """Test that hunt query includes network indicators."""
        from src.demo.scenario_supply_chain import get_hunt_query

        query = get_hunt_query()
        assert "network_indicators" in query
        assert "domains" in query["network_indicators"]
        assert "ips" in query["network_indicators"]
