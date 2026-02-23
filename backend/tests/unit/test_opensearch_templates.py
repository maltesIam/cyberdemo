"""
Unit tests for OpenSearch index templates, specifically attack_simulations.

Task: T-1.1.005
Requirement: INT-003 - OpenSearch Index attack_simulations for scenario events
Test ID: Part of UT-018 to UT-030 infrastructure

Tests verify:
- attack_simulations index template exists
- Template has correct mappings for simulation events
- Template includes MITRE ATT&CK fields
- Template includes scenario metadata fields
"""

import pytest


class TestAttackSimulationsIndexTemplate:
    """Tests for the attack_simulations OpenSearch index template."""

    def test_attack_simulations_in_all_indices(self):
        """Test attack_simulations is included in ALL_INDICES."""
        from src.opensearch.templates import ALL_INDICES

        assert "attack-simulations-v1" in ALL_INDICES

    def test_attack_simulations_template_exists(self):
        """Test attack_simulations template is defined."""
        from src.opensearch.templates import INDEX_TEMPLATES

        assert "attack-simulations-v1" in INDEX_TEMPLATES

    def test_attack_simulations_has_settings(self):
        """Test attack_simulations template has proper settings."""
        from src.opensearch.templates import INDEX_TEMPLATES

        template = INDEX_TEMPLATES["attack-simulations-v1"]

        assert "settings" in template
        assert template["settings"]["number_of_shards"] >= 1
        assert template["settings"]["number_of_replicas"] >= 0

    def test_attack_simulations_has_mappings(self):
        """Test attack_simulations template has mappings."""
        from src.opensearch.templates import INDEX_TEMPLATES

        template = INDEX_TEMPLATES["attack-simulations-v1"]

        assert "mappings" in template
        assert "properties" in template["mappings"]

    def test_attack_simulations_required_fields(self):
        """Test attack_simulations has all required fields."""
        from src.opensearch.templates import INDEX_TEMPLATES

        template = INDEX_TEMPLATES["attack-simulations-v1"]
        properties = template["mappings"]["properties"]

        required_fields = [
            "event_id",
            "simulation_id",
            "scenario_name",
            "scenario_type",
            "stage_number",
            "stage_name",
            "event_type",
            "timestamp",
            "created_at",
        ]

        for field in required_fields:
            assert field in properties, f"Required field '{field}' missing"

    def test_attack_simulations_mitre_fields(self):
        """Test attack_simulations has MITRE ATT&CK fields (REQ-002-003-001)."""
        from src.opensearch.templates import INDEX_TEMPLATES

        template = INDEX_TEMPLATES["attack-simulations-v1"]
        properties = template["mappings"]["properties"]

        # MITRE fields required by REQ-002-003-001
        mitre_fields = [
            "tactic_id",
            "tactic_name",
            "technique_id",
            "technique_name",
            "sub_technique_id",
        ]

        for field in mitre_fields:
            assert field in properties, f"MITRE field '{field}' missing"

    def test_attack_simulations_event_data_fields(self):
        """Test attack_simulations has event data fields."""
        from src.opensearch.templates import INDEX_TEMPLATES

        template = INDEX_TEMPLATES["attack-simulations-v1"]
        properties = template["mappings"]["properties"]

        event_fields = [
            "description",
            "severity",
            "host_id",
            "hostname",
            "ip_address",
            "user",
            "process_name",
            "command_line",
            "indicators",
        ]

        for field in event_fields:
            assert field in properties, f"Event field '{field}' missing"

    def test_attack_simulations_field_types(self):
        """Test attack_simulations field types are correct."""
        from src.opensearch.templates import INDEX_TEMPLATES

        template = INDEX_TEMPLATES["attack-simulations-v1"]
        properties = template["mappings"]["properties"]

        # Check specific field types
        assert properties["event_id"]["type"] == "keyword"
        assert properties["simulation_id"]["type"] == "keyword"
        assert properties["scenario_name"]["type"] == "keyword"
        assert properties["timestamp"]["type"] == "date"
        assert properties["created_at"]["type"] == "date"
        assert properties["tactic_id"]["type"] == "keyword"
        assert properties["technique_id"]["type"] == "keyword"
        assert properties["severity"]["type"] == "keyword"
        assert properties["description"]["type"] == "text"

    def test_attack_simulations_ip_address_type(self):
        """Test ip_address field uses IP type."""
        from src.opensearch.templates import INDEX_TEMPLATES

        template = INDEX_TEMPLATES["attack-simulations-v1"]
        properties = template["mappings"]["properties"]

        assert properties["ip_address"]["type"] == "ip"

    def test_attack_simulations_indicators_nested(self):
        """Test indicators field is properly structured for IOCs."""
        from src.opensearch.templates import INDEX_TEMPLATES

        template = INDEX_TEMPLATES["attack-simulations-v1"]
        properties = template["mappings"]["properties"]

        # indicators should support IOC data (nested or object)
        assert "indicators" in properties

    def test_attack_simulations_simulation_control_fields(self):
        """Test simulation control fields exist (for pause/resume)."""
        from src.opensearch.templates import INDEX_TEMPLATES

        template = INDEX_TEMPLATES["attack-simulations-v1"]
        properties = template["mappings"]["properties"]

        control_fields = [
            "speed_multiplier",
            "is_paused",
            "seed",
        ]

        for field in control_fields:
            assert field in properties, f"Control field '{field}' missing"
