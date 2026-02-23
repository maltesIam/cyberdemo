"""
Unit tests for NarrationMessage database model.

TECH-007: Tabla narration_messages para historial
REQ-003-002-002: Formato de mensaje {type, content, confidence, timestamp}

Following TDD: These tests are written FIRST, before implementation.
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4


class TestNarrationMessageModel:
    """Tests for the NarrationMessage SQLAlchemy model."""

    def test_model_import(self):
        """NarrationMessage can be imported from models."""
        from src.models.narration import NarrationMessage
        assert NarrationMessage is not None

    def test_narration_type_enum_exists(self):
        """NarrationType enum exists with required values."""
        from src.models.narration import NarrationType

        assert hasattr(NarrationType, 'THINKING')
        assert hasattr(NarrationType, 'FINDING')
        assert hasattr(NarrationType, 'DECISION')
        assert hasattr(NarrationType, 'ACTION')

    def test_narration_type_values(self):
        """NarrationType enum values are lowercase strings."""
        from src.models.narration import NarrationType

        assert NarrationType.THINKING.value == "thinking"
        assert NarrationType.FINDING.value == "finding"
        assert NarrationType.DECISION.value == "decision"
        assert NarrationType.ACTION.value == "action"

    def test_confidence_level_enum_exists(self):
        """ConfidenceLevel enum exists with required values."""
        from src.models.narration import ConfidenceLevel

        assert hasattr(ConfidenceLevel, 'LOW')
        assert hasattr(ConfidenceLevel, 'MEDIUM')
        assert hasattr(ConfidenceLevel, 'HIGH')

    def test_confidence_level_values(self):
        """ConfidenceLevel enum values are lowercase strings."""
        from src.models.narration import ConfidenceLevel

        assert ConfidenceLevel.LOW.value == "low"
        assert ConfidenceLevel.MEDIUM.value == "medium"
        assert ConfidenceLevel.HIGH.value == "high"

    def test_model_has_tablename(self):
        """Model has correct __tablename__."""
        from src.models.narration import NarrationMessage

        assert NarrationMessage.__tablename__ == "narration_messages"

    def test_model_has_required_columns(self):
        """Model has all required columns from TECH-007."""
        from src.models.narration import NarrationMessage

        # Check column existence
        columns = NarrationMessage.__table__.columns
        assert 'id' in columns
        assert 'session_id' in columns
        assert 'message_type' in columns
        assert 'content' in columns
        assert 'confidence' in columns
        assert 'confidence_score' in columns
        assert 'timestamp' in columns
        assert 'created_at' in columns

    def test_id_is_primary_key(self):
        """id column is the primary key."""
        from src.models.narration import NarrationMessage

        id_column = NarrationMessage.__table__.columns['id']
        assert id_column.primary_key is True

    def test_session_id_is_indexed(self):
        """session_id column is indexed for efficient queries."""
        from src.models.narration import NarrationMessage

        session_id_column = NarrationMessage.__table__.columns['session_id']
        assert session_id_column.index is True

    def test_message_type_uses_enum(self):
        """message_type column uses NarrationType enum."""
        from src.models.narration import NarrationMessage, NarrationType
        from sqlalchemy import Enum

        message_type_column = NarrationMessage.__table__.columns['message_type']
        assert isinstance(message_type_column.type, Enum)

    def test_confidence_uses_enum(self):
        """confidence column uses ConfidenceLevel enum."""
        from src.models.narration import NarrationMessage, ConfidenceLevel
        from sqlalchemy import Enum

        confidence_column = NarrationMessage.__table__.columns['confidence']
        assert isinstance(confidence_column.type, Enum)

    def test_confidence_score_is_float(self):
        """confidence_score column stores float values (0.0-1.0)."""
        from src.models.narration import NarrationMessage
        from sqlalchemy import Float

        score_column = NarrationMessage.__table__.columns['confidence_score']
        assert isinstance(score_column.type, Float)

    def test_content_is_text(self):
        """content column stores text for narration content."""
        from src.models.narration import NarrationMessage
        from sqlalchemy import Text

        content_column = NarrationMessage.__table__.columns['content']
        assert isinstance(content_column.type, Text)

    def test_timestamp_is_datetime(self):
        """timestamp column stores datetime values."""
        from src.models.narration import NarrationMessage
        from sqlalchemy import DateTime

        timestamp_column = NarrationMessage.__table__.columns['timestamp']
        assert isinstance(timestamp_column.type, DateTime)


class TestNarrationMessageInstance:
    """Tests for creating NarrationMessage instances."""

    def test_create_instance_with_required_fields(self):
        """Can create NarrationMessage with required fields."""
        from src.models.narration import NarrationMessage, NarrationType, ConfidenceLevel

        msg = NarrationMessage(
            session_id="session-123",
            message_type=NarrationType.THINKING,
            content="Analyzing alert data...",
            confidence=ConfidenceLevel.MEDIUM,
            confidence_score=0.55
        )

        assert msg.session_id == "session-123"
        assert msg.message_type == NarrationType.THINKING
        assert msg.content == "Analyzing alert data..."
        assert msg.confidence == ConfidenceLevel.MEDIUM
        assert msg.confidence_score == 0.55

    def test_id_has_default_uuid(self):
        """id column has a default UUID factory."""
        from src.models.narration import NarrationMessage, NarrationType, ConfidenceLevel

        msg = NarrationMessage(
            session_id="session-123",
            message_type=NarrationType.FINDING,
            content="Found suspicious process",
            confidence=ConfidenceLevel.HIGH,
            confidence_score=0.85
        )

        # ID should be generated automatically (default factory)
        # We can't check the value before insertion, but we can verify
        # the default is set up in the column definition
        id_column = NarrationMessage.__table__.columns['id']
        assert id_column.default is not None

    def test_timestamp_has_default(self):
        """timestamp column has a default value."""
        from src.models.narration import NarrationMessage

        timestamp_column = NarrationMessage.__table__.columns['timestamp']
        assert timestamp_column.default is not None

    def test_created_at_has_default(self):
        """created_at column has a default value."""
        from src.models.narration import NarrationMessage

        created_at_column = NarrationMessage.__table__.columns['created_at']
        assert created_at_column.default is not None


class TestConfidenceLevelMapping:
    """Tests for confidence level boundaries."""

    def test_low_confidence_range(self):
        """Low confidence is for scores 0.0-0.33."""
        from src.models.narration import confidence_from_score, ConfidenceLevel

        assert confidence_from_score(0.0) == ConfidenceLevel.LOW
        assert confidence_from_score(0.15) == ConfidenceLevel.LOW
        assert confidence_from_score(0.33) == ConfidenceLevel.LOW

    def test_medium_confidence_range(self):
        """Medium confidence is for scores 0.34-0.66."""
        from src.models.narration import confidence_from_score, ConfidenceLevel

        assert confidence_from_score(0.34) == ConfidenceLevel.MEDIUM
        assert confidence_from_score(0.50) == ConfidenceLevel.MEDIUM
        assert confidence_from_score(0.66) == ConfidenceLevel.MEDIUM

    def test_high_confidence_range(self):
        """High confidence is for scores 0.67-1.0."""
        from src.models.narration import confidence_from_score, ConfidenceLevel

        assert confidence_from_score(0.67) == ConfidenceLevel.HIGH
        assert confidence_from_score(0.85) == ConfidenceLevel.HIGH
        assert confidence_from_score(1.0) == ConfidenceLevel.HIGH

    def test_boundary_values(self):
        """Test exact boundary values."""
        from src.models.narration import confidence_from_score, ConfidenceLevel

        # 0.33 is still LOW
        assert confidence_from_score(0.33) == ConfidenceLevel.LOW
        # 0.34 is MEDIUM
        assert confidence_from_score(0.34) == ConfidenceLevel.MEDIUM
        # 0.66 is still MEDIUM
        assert confidence_from_score(0.66) == ConfidenceLevel.MEDIUM
        # 0.67 is HIGH
        assert confidence_from_score(0.67) == ConfidenceLevel.HIGH

    def test_invalid_negative_score_raises(self):
        """Negative confidence score raises ValueError."""
        from src.models.narration import confidence_from_score

        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            confidence_from_score(-0.1)

    def test_invalid_score_above_1_raises(self):
        """Confidence score above 1.0 raises ValueError."""
        from src.models.narration import confidence_from_score

        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            confidence_from_score(1.1)
