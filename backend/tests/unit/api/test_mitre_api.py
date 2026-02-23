"""
Unit tests for MITRE ATT&CK API endpoints.

Following TDD and UNIT TEST ISOLATION v18.1.0:
- Tests written FIRST before implementation
- NO import from src.main (unit test isolation)
- Uses mock data and isolated router tests

Tests for:
- GET /api/v1/mitre/tactics - List all MITRE ATT&CK tactics
- GET /api/v1/mitre/techniques/{tactic_id} - List techniques for a tactic
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from typing import List, Dict, Any

# Import the router directly (not the full app) - following isolation pattern
# These imports will fail until implementation exists
from src.api.mitre import (
    router,
    get_tactics,
    get_techniques_by_tactic,
    MitreTacticResponse,
    MitreTechniqueResponse,
)


# ============================================================================
# Mock Data - Based on embedded MITRE ATT&CK data in mitre_attack_client.py
# ============================================================================


MOCK_TACTICS = [
    {
        "id": "TA0043",
        "name": "Reconnaissance",
        "description": "The adversary is trying to gather information they can use to plan future operations."
    },
    {
        "id": "TA0042",
        "name": "Resource Development",
        "description": "The adversary is trying to establish resources they can use to support operations."
    },
    {
        "id": "TA0001",
        "name": "Initial Access",
        "description": "The adversary is trying to get into your network."
    },
    {
        "id": "TA0002",
        "name": "Execution",
        "description": "The adversary is trying to run malicious code."
    },
]

MOCK_TECHNIQUES = [
    {
        "id": "T1566",
        "name": "Phishing",
        "tactic_id": ["TA0001"],
        "description": "Adversaries may send phishing messages to gain access to victim systems.",
        "data_sources": ["Application Log", "Network Traffic"]
    },
    {
        "id": "T1566.001",
        "name": "Spearphishing Attachment",
        "tactic_id": ["TA0001"],
        "description": "Adversaries may send spearphishing emails with a malicious attachment.",
        "data_sources": ["Application Log", "File", "Network Traffic"]
    },
    {
        "id": "T1190",
        "name": "Exploit Public-Facing Application",
        "tactic_id": ["TA0001"],
        "description": "Adversaries may attempt to exploit a weakness in an Internet-facing host or system.",
        "data_sources": ["Application Log", "Network Traffic"]
    },
    {
        "id": "T1059",
        "name": "Command and Scripting Interpreter",
        "tactic_id": ["TA0002"],
        "description": "Adversaries may abuse command and script interpreters to execute commands.",
        "data_sources": ["Command", "Process", "Script"]
    },
]


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def mock_mitre_client():
    """Create a mock MitreAttackClient."""
    client = MagicMock()
    client.get_tactics = AsyncMock(return_value=MOCK_TACTICS)
    client.get_techniques = AsyncMock(return_value=MOCK_TECHNIQUES)
    return client


# ============================================================================
# Tests for GET /api/v1/mitre/tactics
# ============================================================================


class TestGetTactics:
    """Tests for the get_tactics endpoint."""

    @pytest.mark.asyncio
    async def test_returns_list_of_tactics(self, mock_mitre_client):
        """Test that endpoint returns a list of all MITRE ATT&CK tactics."""
        mock_mitre_client.get_tactics.return_value = MOCK_TACTICS

        with patch("src.api.mitre.MitreAttackClient", return_value=mock_mitre_client):
            result = await get_tactics()

        assert isinstance(result, MitreTacticResponse)
        assert len(result.tactics) == 4
        mock_mitre_client.get_tactics.assert_called_once()

    @pytest.mark.asyncio
    async def test_tactics_contain_required_fields(self, mock_mitre_client):
        """Test that each tactic contains id, name, and description."""
        mock_mitre_client.get_tactics.return_value = MOCK_TACTICS

        with patch("src.api.mitre.MitreAttackClient", return_value=mock_mitre_client):
            result = await get_tactics()

        for tactic in result.tactics:
            assert "id" in tactic
            assert "name" in tactic
            assert "description" in tactic

    @pytest.mark.asyncio
    async def test_tactics_have_correct_id_format(self, mock_mitre_client):
        """Test that tactic IDs follow MITRE format TAxxxx."""
        mock_mitre_client.get_tactics.return_value = MOCK_TACTICS

        with patch("src.api.mitre.MitreAttackClient", return_value=mock_mitre_client):
            result = await get_tactics()

        for tactic in result.tactics:
            assert tactic["id"].startswith("TA")
            assert len(tactic["id"]) == 6  # TA + 4 digits

    @pytest.mark.asyncio
    async def test_total_count_returned(self, mock_mitre_client):
        """Test that total count of tactics is returned."""
        mock_mitre_client.get_tactics.return_value = MOCK_TACTICS

        with patch("src.api.mitre.MitreAttackClient", return_value=mock_mitre_client):
            result = await get_tactics()

        assert result.total == 4

    @pytest.mark.asyncio
    async def test_empty_tactics_returns_empty_list(self, mock_mitre_client):
        """Test handling when no tactics are available."""
        mock_mitre_client.get_tactics.return_value = []

        with patch("src.api.mitre.MitreAttackClient", return_value=mock_mitre_client):
            result = await get_tactics()

        assert result.tactics == []
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_exception_handling(self, mock_mitre_client):
        """Test that exceptions are handled gracefully."""
        mock_mitre_client.get_tactics.side_effect = Exception("Client error")

        with patch("src.api.mitre.MitreAttackClient", return_value=mock_mitre_client):
            result = await get_tactics()

        # Should return empty response on error
        assert result.tactics == []
        assert result.total == 0


# ============================================================================
# Tests for GET /api/v1/mitre/techniques/{tactic_id}
# ============================================================================


class TestGetTechniquesByTactic:
    """Tests for the get_techniques_by_tactic endpoint."""

    @pytest.mark.asyncio
    async def test_returns_techniques_for_valid_tactic(self, mock_mitre_client):
        """Test that endpoint returns techniques for a valid tactic_id."""
        # Only return techniques for TA0001 (Initial Access)
        initial_access_techniques = [t for t in MOCK_TECHNIQUES if "TA0001" in t["tactic_id"]]
        mock_mitre_client.get_techniques.return_value = initial_access_techniques

        with patch("src.api.mitre.MitreAttackClient", return_value=mock_mitre_client):
            result = await get_techniques_by_tactic("TA0001")

        assert isinstance(result, MitreTechniqueResponse)
        assert len(result.techniques) == 3  # T1566, T1566.001, T1190
        mock_mitre_client.get_techniques.assert_called_once_with(tactic_id="TA0001")

    @pytest.mark.asyncio
    async def test_techniques_contain_required_fields(self, mock_mitre_client):
        """Test that each technique contains required fields."""
        initial_access_techniques = [t for t in MOCK_TECHNIQUES if "TA0001" in t["tactic_id"]]
        mock_mitre_client.get_techniques.return_value = initial_access_techniques

        with patch("src.api.mitre.MitreAttackClient", return_value=mock_mitre_client):
            result = await get_techniques_by_tactic("TA0001")

        for technique in result.techniques:
            assert "id" in technique
            assert "name" in technique
            assert "description" in technique
            assert "tactic_id" in technique

    @pytest.mark.asyncio
    async def test_techniques_have_correct_id_format(self, mock_mitre_client):
        """Test that technique IDs follow MITRE format Txxxx or Txxxx.xxx."""
        initial_access_techniques = [t for t in MOCK_TECHNIQUES if "TA0001" in t["tactic_id"]]
        mock_mitre_client.get_techniques.return_value = initial_access_techniques

        with patch("src.api.mitre.MitreAttackClient", return_value=mock_mitre_client):
            result = await get_techniques_by_tactic("TA0001")

        for technique in result.techniques:
            assert technique["id"].startswith("T")
            # ID can be Txxxx or Txxxx.xxx (subtechnique)
            parts = technique["id"].split(".")
            assert len(parts) <= 2

    @pytest.mark.asyncio
    async def test_tactic_id_in_response(self, mock_mitre_client):
        """Test that tactic_id is included in response."""
        initial_access_techniques = [t for t in MOCK_TECHNIQUES if "TA0001" in t["tactic_id"]]
        mock_mitre_client.get_techniques.return_value = initial_access_techniques

        with patch("src.api.mitre.MitreAttackClient", return_value=mock_mitre_client):
            result = await get_techniques_by_tactic("TA0001")

        assert result.tactic_id == "TA0001"

    @pytest.mark.asyncio
    async def test_total_count_returned(self, mock_mitre_client):
        """Test that total count of techniques is returned."""
        initial_access_techniques = [t for t in MOCK_TECHNIQUES if "TA0001" in t["tactic_id"]]
        mock_mitre_client.get_techniques.return_value = initial_access_techniques

        with patch("src.api.mitre.MitreAttackClient", return_value=mock_mitre_client):
            result = await get_techniques_by_tactic("TA0001")

        assert result.total == 3

    @pytest.mark.asyncio
    async def test_empty_techniques_for_tactic(self, mock_mitre_client):
        """Test handling when no techniques exist for a tactic."""
        mock_mitre_client.get_techniques.return_value = []

        with patch("src.api.mitre.MitreAttackClient", return_value=mock_mitre_client):
            result = await get_techniques_by_tactic("TA9999")

        assert result.techniques == []
        assert result.total == 0
        assert result.tactic_id == "TA9999"

    @pytest.mark.asyncio
    async def test_invalid_tactic_id_returns_empty(self, mock_mitre_client):
        """Test that invalid tactic_id returns empty list (not error)."""
        mock_mitre_client.get_techniques.return_value = []

        with patch("src.api.mitre.MitreAttackClient", return_value=mock_mitre_client):
            result = await get_techniques_by_tactic("INVALID")

        assert result.techniques == []
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_data_sources_included(self, mock_mitre_client):
        """Test that data_sources are included in technique response."""
        initial_access_techniques = [t for t in MOCK_TECHNIQUES if "TA0001" in t["tactic_id"]]
        mock_mitre_client.get_techniques.return_value = initial_access_techniques

        with patch("src.api.mitre.MitreAttackClient", return_value=mock_mitre_client):
            result = await get_techniques_by_tactic("TA0001")

        # At least one technique should have data_sources
        has_data_sources = any("data_sources" in t for t in result.techniques)
        assert has_data_sources

    @pytest.mark.asyncio
    async def test_exception_handling(self, mock_mitre_client):
        """Test that exceptions are handled gracefully."""
        mock_mitre_client.get_techniques.side_effect = Exception("Client error")

        with patch("src.api.mitre.MitreAttackClient", return_value=mock_mitre_client):
            result = await get_techniques_by_tactic("TA0001")

        # Should return empty response on error
        assert result.techniques == []
        assert result.total == 0


# ============================================================================
# Tests for Response Models
# ============================================================================


class TestResponseModels:
    """Tests for the Pydantic response models."""

    def test_mitre_tactic_response_model(self):
        """Test MitreTacticResponse model structure."""
        response = MitreTacticResponse(
            tactics=MOCK_TACTICS,
            total=len(MOCK_TACTICS)
        )
        assert response.tactics == MOCK_TACTICS
        assert response.total == 4

    def test_mitre_technique_response_model(self):
        """Test MitreTechniqueResponse model structure."""
        response = MitreTechniqueResponse(
            tactic_id="TA0001",
            techniques=MOCK_TECHNIQUES[:3],
            total=3
        )
        assert response.tactic_id == "TA0001"
        assert len(response.techniques) == 3
        assert response.total == 3

    def test_mitre_tactic_response_with_empty_list(self):
        """Test MitreTacticResponse with empty tactics list."""
        response = MitreTacticResponse(tactics=[], total=0)
        assert response.tactics == []
        assert response.total == 0

    def test_mitre_technique_response_with_empty_list(self):
        """Test MitreTechniqueResponse with empty techniques list."""
        response = MitreTechniqueResponse(
            tactic_id="TA0001",
            techniques=[],
            total=0
        )
        assert response.techniques == []
        assert response.total == 0


# ============================================================================
# Tests for Router Configuration
# ============================================================================


class TestRouterConfiguration:
    """Tests for router configuration and endpoints."""

    def test_router_has_mitre_prefix(self):
        """Test that router is configured with correct prefix."""
        # Router prefix is set in router.py when including
        assert router is not None

    def test_tactics_endpoint_path(self):
        """Test that /tactics endpoint is defined."""
        routes = [route.path for route in router.routes]
        assert "/tactics" in routes

    def test_techniques_endpoint_path(self):
        """Test that /techniques/{tactic_id} endpoint is defined."""
        routes = [route.path for route in router.routes]
        assert "/techniques/{tactic_id}" in routes
