"""
Unit tests for narration_logs OpenSearch index template.

INT-004: Indice narration_logs para historial de narracion
REQ-003-002-002: Formato de mensaje {type, content, confidence, timestamp}

Following TDD: These tests are written FIRST, before implementation.
"""
import pytest


class TestNarrationLogsIndexTemplate:
    """Tests for the narration-logs-v1 OpenSearch index template."""

    def test_index_exists_in_all_indices(self):
        """narration-logs-v1 index is in ALL_INDICES list."""
        from src.opensearch.templates import ALL_INDICES

        assert "narration-logs-v1" in ALL_INDICES

    def test_index_template_exists(self):
        """narration-logs-v1 has an index template definition."""
        from src.opensearch.templates import INDEX_TEMPLATES

        assert "narration-logs-v1" in INDEX_TEMPLATES

    def test_template_has_settings(self):
        """Template has settings with shards and replicas."""
        from src.opensearch.templates import INDEX_TEMPLATES

        template = INDEX_TEMPLATES["narration-logs-v1"]
        assert "settings" in template
        assert "number_of_shards" in template["settings"]
        assert "number_of_replicas" in template["settings"]

    def test_template_has_mappings(self):
        """Template has mappings with properties."""
        from src.opensearch.templates import INDEX_TEMPLATES

        template = INDEX_TEMPLATES["narration-logs-v1"]
        assert "mappings" in template
        assert "properties" in template["mappings"]


class TestNarrationLogsFieldMappings:
    """Tests for field mappings in narration-logs-v1 index."""

    @pytest.fixture
    def properties(self):
        """Get properties from the index template."""
        from src.opensearch.templates import INDEX_TEMPLATES
        return INDEX_TEMPLATES["narration-logs-v1"]["mappings"]["properties"]

    def test_has_message_id_field(self, properties):
        """Index has message_id field as keyword."""
        assert "message_id" in properties
        assert properties["message_id"]["type"] == "keyword"

    def test_has_session_id_field(self, properties):
        """Index has session_id field as keyword."""
        assert "session_id" in properties
        assert properties["session_id"]["type"] == "keyword"

    def test_has_message_type_field(self, properties):
        """Index has message_type field as keyword."""
        assert "message_type" in properties
        assert properties["message_type"]["type"] == "keyword"

    def test_has_content_field_as_text(self, properties):
        """Index has content field as text for full-text search."""
        assert "content" in properties
        assert properties["content"]["type"] == "text"

    def test_content_has_keyword_subfield(self, properties):
        """Content field has keyword subfield for exact matching."""
        assert "content" in properties
        assert "fields" in properties["content"]
        assert "keyword" in properties["content"]["fields"]
        assert properties["content"]["fields"]["keyword"]["type"] == "keyword"

    def test_has_confidence_level_field(self, properties):
        """Index has confidence_level field as keyword."""
        assert "confidence_level" in properties
        assert properties["confidence_level"]["type"] == "keyword"

    def test_has_confidence_score_field(self, properties):
        """Index has confidence_score field as float."""
        assert "confidence_score" in properties
        assert properties["confidence_score"]["type"] == "float"

    def test_has_timestamp_field(self, properties):
        """Index has timestamp field as date."""
        assert "timestamp" in properties
        assert properties["timestamp"]["type"] == "date"

    def test_has_created_at_field(self, properties):
        """Index has created_at field as date."""
        assert "created_at" in properties
        assert properties["created_at"]["type"] == "date"

    def test_has_agent_id_field(self, properties):
        """Index has agent_id field as keyword for filtering by agent."""
        assert "agent_id" in properties
        assert properties["agent_id"]["type"] == "keyword"

    def test_has_incident_id_field(self, properties):
        """Index has incident_id field as keyword for correlation."""
        assert "incident_id" in properties
        assert properties["incident_id"]["type"] == "keyword"

    def test_has_related_entities_field(self, properties):
        """Index has related_entities field as keyword array."""
        assert "related_entities" in properties
        assert properties["related_entities"]["type"] == "keyword"

    def test_has_metadata_field(self, properties):
        """Index has metadata field as object for additional data."""
        assert "metadata" in properties
        assert properties["metadata"]["type"] == "object"
        # Metadata should be stored but not indexed for search
        assert properties["metadata"]["enabled"] is False
