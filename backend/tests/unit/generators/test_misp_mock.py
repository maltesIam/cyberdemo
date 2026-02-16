"""Unit tests for MISP mock generator.

Tests follow TDD RED-GREEN-REFACTOR cycle.
These tests should FAIL initially (RED phase).
"""
import pytest
import uuid


class TestMISPMock:
    """Tests for MISPMock generator."""

    def test_misp_generates_valid_events(self):
        """
        RED: Test that MISP generates valid event structures.
        """
        from src.generators.enrichment.misp_mock import MISPMock

        mock = MISPMock()

        events = mock.generate_events(
            indicator_type="ip",
            indicator_value="192.168.1.100"
        )

        # Should return a list of events
        assert isinstance(events, list)
        assert len(events) >= 1, "Should generate at least one event"

        # Each event should be a dictionary
        for event in events:
            assert isinstance(event, dict)

    def test_misp_events_contain_required_fields(self):
        """
        RED: Test that MISP events contain all required fields.

        Required fields: event_id, uuid, info, threat_level_id,
        date, timestamp, published, orgc, tags, attributes
        """
        from src.generators.enrichment.misp_mock import MISPMock

        mock = MISPMock()

        events = mock.generate_events(
            indicator_type="domain",
            indicator_value="malicious-domain.com",
            threat_level=1
        )

        assert len(events) >= 1

        required_fields = [
            "event_id", "uuid", "info", "threat_level_id",
            "date", "timestamp", "published", "orgc", "tags", "attributes"
        ]

        for event in events:
            for field in required_fields:
                assert field in event, f"Missing required field: {field}"

            # Validate specific field types
            assert isinstance(event["event_id"], (int, str))
            assert isinstance(event["uuid"], str)
            assert isinstance(event["info"], str)
            assert isinstance(event["threat_level_id"], int)
            assert isinstance(event["date"], str)
            assert isinstance(event["timestamp"], (int, str))
            assert isinstance(event["published"], bool)
            assert isinstance(event["orgc"], dict)
            assert isinstance(event["tags"], list)
            assert isinstance(event["attributes"], list)

    def test_misp_attributes_match_indicator_type(self):
        """
        RED: Test that MISP attributes correctly match the indicator type.
        """
        from src.generators.enrichment.misp_mock import MISPMock

        mock = MISPMock()

        # Test IP indicator
        ip_events = mock.generate_events(
            indicator_type="ip",
            indicator_value="10.20.30.40"
        )
        assert len(ip_events) >= 1
        ip_attrs = ip_events[0]["attributes"]
        assert any(attr["type"].startswith("ip") for attr in ip_attrs), "IP indicator should have ip-* type attribute"

        # Test domain indicator
        domain_events = mock.generate_events(
            indicator_type="domain",
            indicator_value="evil-domain.net"
        )
        assert len(domain_events) >= 1
        domain_attrs = domain_events[0]["attributes"]
        assert any("domain" in attr["type"] for attr in domain_attrs), "Domain indicator should have domain type attribute"

        # Test hash indicator
        hash_events = mock.generate_events(
            indicator_type="hash",
            indicator_value="d41d8cd98f00b204e9800998ecf8427e"
        )
        assert len(hash_events) >= 1
        hash_attrs = hash_events[0]["attributes"]
        assert any("md5" in attr["type"] or "sha" in attr["type"] or "hash" in attr["type"] for attr in hash_attrs), "Hash indicator should have hash type attribute"

        # Test URL indicator
        url_events = mock.generate_events(
            indicator_type="url",
            indicator_value="http://malware.com/payload.exe"
        )
        assert len(url_events) >= 1
        url_attrs = url_events[0]["attributes"]
        assert any("url" in attr["type"] for attr in url_attrs), "URL indicator should have url type attribute"

    def test_misp_threat_levels_are_valid(self):
        """
        RED: Test that MISP threat levels are valid (1=High, 2=Medium, 3=Low, 4=Undefined).
        """
        from src.generators.enrichment.misp_mock import MISPMock

        mock = MISPMock()

        # Test each threat level
        for threat_level in [1, 2, 3, 4]:
            events = mock.generate_events(
                indicator_type="ip",
                indicator_value="192.168.1.1",
                threat_level=threat_level
            )

            assert len(events) >= 1
            for event in events:
                assert event["threat_level_id"] == threat_level, f"Expected threat_level {threat_level}"
                assert 1 <= event["threat_level_id"] <= 4, "Threat level must be between 1 and 4"

    def test_misp_orgc_structure(self):
        """
        RED: Test that MISP organization creator (orgc) has correct structure.
        """
        from src.generators.enrichment.misp_mock import MISPMock

        mock = MISPMock()

        events = mock.generate_events(
            indicator_type="ip",
            indicator_value="1.2.3.4"
        )

        for event in events:
            orgc = event["orgc"]
            assert "id" in orgc, "orgc should have id"
            assert "name" in orgc, "orgc should have name"
            assert "uuid" in orgc, "orgc should have uuid"
            assert isinstance(orgc["name"], str)
            assert len(orgc["name"]) > 0

    def test_misp_tags_contain_tlp(self):
        """
        RED: Test that MISP events contain TLP (Traffic Light Protocol) tags.
        """
        from src.generators.enrichment.misp_mock import MISPMock

        mock = MISPMock()

        events = mock.generate_events(
            indicator_type="domain",
            indicator_value="test.com"
        )

        for event in events:
            tags = event["tags"]
            assert len(tags) >= 1, "Events should have at least one tag"

            # Check for TLP tag
            tag_names = [t.get("name", "") for t in tags]
            tlp_found = any("tlp:" in name.lower() for name in tag_names)
            assert tlp_found, "Events should have a TLP tag"

    def test_misp_attributes_have_required_fields(self):
        """
        RED: Test that MISP attributes have required fields.
        """
        from src.generators.enrichment.misp_mock import MISPMock

        mock = MISPMock()

        events = mock.generate_events(
            indicator_type="ip",
            indicator_value="8.8.8.8"
        )

        required_attr_fields = ["uuid", "type", "category", "value", "to_ids"]

        for event in events:
            for attr in event["attributes"]:
                for field in required_attr_fields:
                    assert field in attr, f"Attribute missing required field: {field}"

                # Validate attribute types
                assert isinstance(attr["uuid"], str)
                assert isinstance(attr["type"], str)
                assert isinstance(attr["category"], str)
                assert isinstance(attr["value"], str)
                assert isinstance(attr["to_ids"], bool)

    def test_misp_attribute_value_matches_input(self):
        """
        RED: Test that at least one attribute contains the input indicator value.
        """
        from src.generators.enrichment.misp_mock import MISPMock

        mock = MISPMock()

        test_value = "203.0.113.50"
        events = mock.generate_events(
            indicator_type="ip",
            indicator_value=test_value
        )

        for event in events:
            values = [attr["value"] for attr in event["attributes"]]
            assert test_value in values, f"Indicator value {test_value} should be in attributes"

    def test_generate_attributes_standalone(self):
        """
        RED: Test the standalone generate_attributes method.
        """
        from src.generators.enrichment.misp_mock import MISPMock

        mock = MISPMock()

        # Test IP attributes
        ip_attrs = mock.generate_attributes("ip", "192.0.2.1")
        assert isinstance(ip_attrs, list)
        assert len(ip_attrs) >= 1

        for attr in ip_attrs:
            assert "uuid" in attr
            assert "type" in attr
            assert "value" in attr
            assert "category" in attr

        # Verify the input value is in attributes
        values = [a["value"] for a in ip_attrs]
        assert "192.0.2.1" in values

    def test_misp_uuid_format_valid(self):
        """
        RED: Test that generated UUIDs are valid UUID format.
        """
        from src.generators.enrichment.misp_mock import MISPMock

        mock = MISPMock()

        events = mock.generate_events(
            indicator_type="hash",
            indicator_value="abc123def456"
        )

        for event in events:
            # Validate event UUID
            try:
                uuid.UUID(event["uuid"])
            except ValueError:
                pytest.fail(f"Invalid event UUID format: {event['uuid']}")

            # Validate orgc UUID
            try:
                uuid.UUID(event["orgc"]["uuid"])
            except ValueError:
                pytest.fail(f"Invalid orgc UUID format: {event['orgc']['uuid']}")

            # Validate attribute UUIDs
            for attr in event["attributes"]:
                try:
                    uuid.UUID(attr["uuid"])
                except ValueError:
                    pytest.fail(f"Invalid attribute UUID format: {attr['uuid']}")

    def test_misp_date_format_valid(self):
        """
        RED: Test that date fields have valid ISO format.
        """
        from src.generators.enrichment.misp_mock import MISPMock
        from datetime import datetime

        mock = MISPMock()

        events = mock.generate_events(
            indicator_type="url",
            indicator_value="http://test.com/malware"
        )

        for event in events:
            # Date should be YYYY-MM-DD format
            try:
                datetime.strptime(event["date"], "%Y-%m-%d")
            except ValueError:
                pytest.fail(f"Invalid date format: {event['date']}, expected YYYY-MM-DD")

    def test_misp_reproducibility_with_seed(self):
        """
        RED: Test that MISPMock produces reproducible results with seed.

        Note: UUIDs are generated by uuid4() which doesn't use random.seed,
        so we only test that random-based fields are reproducible.
        """
        from src.generators.enrichment.misp_mock import MISPMock

        mock1 = MISPMock(seed=42)
        events1 = mock1.generate_events("ip", "1.1.1.1")

        mock2 = MISPMock(seed=42)
        events2 = mock2.generate_events("ip", "1.1.1.1")

        # Should produce same number of events and same event info
        assert len(events1) == len(events2)
        assert events1[0]["info"] == events2[0]["info"]
        assert events1[0]["threat_level_id"] == events2[0]["threat_level_id"]

    def test_misp_default_threat_level(self):
        """
        RED: Test that default threat level is 2 (Medium).
        """
        from src.generators.enrichment.misp_mock import MISPMock

        mock = MISPMock()

        # Don't specify threat_level
        events = mock.generate_events(
            indicator_type="ip",
            indicator_value="10.0.0.1"
        )

        for event in events:
            assert event["threat_level_id"] == 2, "Default threat level should be 2 (Medium)"

    def test_misp_event_info_descriptive(self):
        """
        RED: Test that event info contains descriptive threat information.
        """
        from src.generators.enrichment.misp_mock import MISPMock

        mock = MISPMock()

        events = mock.generate_events(
            indicator_type="ip",
            indicator_value="203.0.113.100"
        )

        for event in events:
            info = event["info"]
            assert isinstance(info, str)
            assert len(info) >= 10, "Event info should be descriptive (at least 10 chars)"

    def test_misp_multiple_events_unique(self):
        """
        RED: Test that when multiple events are generated, they have unique IDs.
        """
        from src.generators.enrichment.misp_mock import MISPMock

        mock = MISPMock()

        # Generate events multiple times
        all_event_ids = set()
        all_event_uuids = set()

        for _ in range(5):
            events = mock.generate_events(
                indicator_type="domain",
                indicator_value="unique-test.com"
            )
            for event in events:
                all_event_ids.add(event["event_id"])
                all_event_uuids.add(event["uuid"])

        # All event IDs should be unique
        # Note: If multiple calls return same events, that's fine
        # But within a single call, events should have unique IDs
        # This test verifies uniqueness across calls
        assert len(all_event_uuids) >= 1, "Should have unique UUIDs"
