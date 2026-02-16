"""
Unit tests for MITRE ATT&CK Client.

MITRE ATT&CK is a knowledge base of adversary tactics, techniques, and common
knowledge (TTPs) based on real-world observations. This client provides access
to tactics, techniques, software, and threat groups.

These tests are written FIRST following TDD.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

# Import will fail until we implement the module (RED phase)
try:
    from src.clients.mitre_attack_client import MitreAttackClient
except ImportError:
    pass


# =============================================================================
# Test: Get Tactics
# =============================================================================

@pytest.mark.asyncio
async def test_get_tactics_returns_list():
    """
    RED: Test that get_tactics returns a list of MITRE ATT&CK tactics.

    Expected behavior:
    - Return list of tactics with id, name, description
    - Each tactic should have TA#### format ID
    """
    client = MitreAttackClient()

    result = await client.get_tactics()

    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0

    # Verify tactic structure
    tactic = result[0]
    assert "id" in tactic
    assert "name" in tactic
    assert "description" in tactic

    # Verify ID format (TA####)
    assert tactic["id"].startswith("TA")

    await client.close()


@pytest.mark.asyncio
async def test_get_tactics_contains_known_tactics():
    """
    RED: Test that get_tactics includes well-known MITRE ATT&CK tactics.

    Expected behavior:
    - Should include Initial Access (TA0001)
    - Should include Execution (TA0002)
    - Should include Persistence (TA0003)
    """
    client = MitreAttackClient()

    result = await client.get_tactics()

    tactic_ids = [t["id"] for t in result]

    # Verify key tactics are present
    assert "TA0001" in tactic_ids  # Initial Access
    assert "TA0002" in tactic_ids  # Execution
    assert "TA0003" in tactic_ids  # Persistence
    assert "TA0040" in tactic_ids  # Impact

    await client.close()


# =============================================================================
# Test: Get Techniques
# =============================================================================

@pytest.mark.asyncio
async def test_get_techniques_returns_list():
    """
    RED: Test that get_techniques returns a list of techniques.

    Expected behavior:
    - Return list of techniques
    - Each technique has id, name, tactic_id
    """
    client = MitreAttackClient()

    result = await client.get_techniques()

    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0

    # Verify technique structure
    technique = result[0]
    assert "id" in technique
    assert "name" in technique
    assert "tactic_id" in technique

    # Verify ID format (T####)
    assert technique["id"].startswith("T")

    await client.close()


@pytest.mark.asyncio
async def test_get_techniques_by_tactic():
    """
    RED: Test filtering techniques by tactic ID.

    Expected behavior:
    - Return only techniques associated with the specified tactic
    """
    client = MitreAttackClient()

    # Get techniques for Initial Access (TA0001)
    result = await client.get_techniques(tactic_id="TA0001")

    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0

    # All returned techniques should be for Initial Access
    for technique in result:
        assert "TA0001" in technique["tactic_id"]

    await client.close()


@pytest.mark.asyncio
async def test_get_techniques_contains_known_techniques():
    """
    RED: Test that get_techniques includes well-known techniques.

    Expected behavior:
    - Should include Phishing (T1566)
    - Should include Command and Scripting Interpreter (T1059)
    """
    client = MitreAttackClient()

    result = await client.get_techniques()

    technique_ids = [t["id"] for t in result]

    # Verify key techniques are present
    assert "T1566" in technique_ids  # Phishing
    assert "T1059" in technique_ids  # Command and Scripting Interpreter

    await client.close()


# =============================================================================
# Test: Get Single Technique Details
# =============================================================================

@pytest.mark.asyncio
async def test_get_technique_returns_details():
    """
    RED: Test getting details for a specific technique.

    Expected behavior:
    - Return detailed technique info including data_sources
    """
    client = MitreAttackClient()

    # Get details for Phishing (T1566)
    result = await client.get_technique("T1566")

    assert result is not None
    assert result["id"] == "T1566"
    assert result["name"] == "Phishing"
    assert "description" in result
    assert "data_sources" in result
    assert "tactic_id" in result

    await client.close()


@pytest.mark.asyncio
async def test_get_technique_not_found():
    """
    RED: Test that get_technique returns None for unknown technique.
    """
    client = MitreAttackClient()

    result = await client.get_technique("T9999")

    assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_get_technique_with_subtechnique():
    """
    RED: Test getting a subtechnique (e.g., T1566.001).

    Expected behavior:
    - Return subtechnique details
    - Subtechnique ID format is T####.###
    """
    client = MitreAttackClient()

    # Get Spearphishing Attachment (T1566.001)
    result = await client.get_technique("T1566.001")

    assert result is not None
    assert result["id"] == "T1566.001"
    assert result["name"] == "Spearphishing Attachment"

    await client.close()


# =============================================================================
# Test: Get Software
# =============================================================================

@pytest.mark.asyncio
async def test_get_software_returns_list():
    """
    RED: Test that get_software returns a list of malware/tools.

    Expected behavior:
    - Return list of software with id, name, type
    """
    client = MitreAttackClient()

    result = await client.get_software()

    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0

    # Verify software structure
    software = result[0]
    assert "id" in software
    assert "name" in software
    assert "type" in software  # 'malware' or 'tool'

    # Verify ID format (S####)
    assert software["id"].startswith("S")

    await client.close()


@pytest.mark.asyncio
async def test_get_software_contains_known_software():
    """
    RED: Test that get_software includes well-known malware/tools.

    Expected behavior:
    - Should include Cobalt Strike (S0154)
    - Should include Mimikatz (S0002)
    """
    client = MitreAttackClient()

    result = await client.get_software()

    software_ids = [s["id"] for s in result]

    # Verify key software is present
    assert "S0154" in software_ids  # Cobalt Strike
    assert "S0002" in software_ids  # Mimikatz

    await client.close()


@pytest.mark.asyncio
async def test_get_software_by_type():
    """
    RED: Test filtering software by type (malware or tool).
    """
    client = MitreAttackClient()

    # Get only tools
    result = await client.get_software(software_type="tool")

    assert result is not None
    assert len(result) > 0

    # All returned software should be tools
    for software in result:
        assert software["type"] == "tool"

    await client.close()


# =============================================================================
# Test: Get Groups (Threat Actors)
# =============================================================================

@pytest.mark.asyncio
async def test_get_groups_returns_list():
    """
    RED: Test that get_groups returns a list of threat actor groups.

    Expected behavior:
    - Return list of groups with id, name, aliases
    """
    client = MitreAttackClient()

    result = await client.get_groups()

    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0

    # Verify group structure
    group = result[0]
    assert "id" in group
    assert "name" in group
    assert "aliases" in group

    # Verify ID format (G####)
    assert group["id"].startswith("G")

    await client.close()


@pytest.mark.asyncio
async def test_get_groups_contains_known_groups():
    """
    RED: Test that get_groups includes well-known threat actors.

    Expected behavior:
    - Should include APT28 (G0007)
    - Should include APT29 (G0016)
    """
    client = MitreAttackClient()

    result = await client.get_groups()

    group_ids = [g["id"] for g in result]

    # Verify key groups are present
    assert "G0007" in group_ids  # APT28
    assert "G0016" in group_ids  # APT29

    await client.close()


# =============================================================================
# Test: Map Technique to Tactic
# =============================================================================

@pytest.mark.asyncio
async def test_map_technique_to_tactic():
    """
    RED: Test mapping a technique ID to its associated tactic(s).

    Expected behavior:
    - Given a technique ID, return associated tactics
    """
    client = MitreAttackClient()

    # Map Phishing (T1566) to its tactic
    result = await client.map_technique_to_tactic("T1566")

    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0

    # Phishing maps to Initial Access
    tactic_ids = [t["id"] for t in result]
    assert "TA0001" in tactic_ids

    await client.close()


@pytest.mark.asyncio
async def test_map_technique_to_tactic_multiple_tactics():
    """
    RED: Test technique that maps to multiple tactics.

    Some techniques can belong to multiple tactics (kill chain phases).
    """
    client = MitreAttackClient()

    # Scheduled Task/Job (T1053) maps to multiple tactics
    result = await client.map_technique_to_tactic("T1053")

    assert result is not None
    assert isinstance(result, list)
    # T1053 maps to Execution, Persistence, and Privilege Escalation
    assert len(result) >= 2

    await client.close()


@pytest.mark.asyncio
async def test_map_technique_to_tactic_not_found():
    """
    RED: Test mapping unknown technique returns empty list.
    """
    client = MitreAttackClient()

    result = await client.map_technique_to_tactic("T9999")

    assert result is not None
    assert result == []

    await client.close()


# =============================================================================
# Test: Build MitreAttackData for Enrichment
# =============================================================================

@pytest.mark.asyncio
async def test_build_mitre_attack_data():
    """
    RED: Test building MitreAttackData compatible structure.

    Expected behavior:
    - Return dict with tactics, techniques, software lists
    - Structure matches MitreAttackData model
    """
    client = MitreAttackClient()

    # Build MITRE ATT&CK data for specific technique IDs
    technique_ids = ["T1566", "T1059"]
    result = await client.build_attack_data(technique_ids)

    assert result is not None
    assert "tactics" in result
    assert "techniques" in result
    assert "software" in result

    # Verify structure matches MitreAttackData model
    assert isinstance(result["tactics"], list)
    assert isinstance(result["techniques"], list)
    assert isinstance(result["software"], list)

    # Verify tactics have correct structure
    if result["tactics"]:
        tactic = result["tactics"][0]
        assert "id" in tactic
        assert "name" in tactic

    # Verify techniques have correct structure
    if result["techniques"]:
        technique = result["techniques"][0]
        assert "id" in technique
        assert "name" in technique
        assert "tactic_id" in technique

    await client.close()


@pytest.mark.asyncio
async def test_build_mitre_attack_data_empty_input():
    """
    RED: Test building MitreAttackData with empty technique list.
    """
    client = MitreAttackClient()

    result = await client.build_attack_data([])

    assert result is not None
    assert result["tactics"] == []
    assert result["techniques"] == []
    assert result["software"] == []

    await client.close()


# =============================================================================
# Test: Search Techniques by Name
# =============================================================================

@pytest.mark.asyncio
async def test_search_techniques_by_name():
    """
    RED: Test searching techniques by name substring.

    Expected behavior:
    - Search for techniques containing a keyword
    - Return matching techniques
    """
    client = MitreAttackClient()

    result = await client.search_techniques("phishing")

    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0

    # All results should contain "phishing" (case-insensitive)
    for technique in result:
        assert "phishing" in technique["name"].lower()

    await client.close()


@pytest.mark.asyncio
async def test_search_techniques_no_match():
    """
    RED: Test searching techniques with no matches.
    """
    client = MitreAttackClient()

    result = await client.search_techniques("xyznonexistent123")

    assert result is not None
    assert result == []

    await client.close()


# =============================================================================
# Test: Client Lifecycle
# =============================================================================

@pytest.mark.asyncio
async def test_client_close():
    """
    RED: Test that client can be properly closed.
    """
    client = MitreAttackClient()

    # Should not raise any exceptions
    await client.close()


@pytest.mark.asyncio
async def test_client_context_manager():
    """
    RED: Test that client can be used as async context manager.
    """
    async with MitreAttackClient() as client:
        tactics = await client.get_tactics()
        assert tactics is not None
        assert len(tactics) > 0


# =============================================================================
# Test: Data Integrity
# =============================================================================

@pytest.mark.asyncio
async def test_tactics_have_unique_ids():
    """
    RED: Test that all tactics have unique IDs.
    """
    client = MitreAttackClient()

    tactics = await client.get_tactics()

    ids = [t["id"] for t in tactics]
    assert len(ids) == len(set(ids))  # No duplicates

    await client.close()


@pytest.mark.asyncio
async def test_techniques_have_valid_tactic_references():
    """
    RED: Test that techniques reference valid tactics.
    """
    client = MitreAttackClient()

    tactics = await client.get_tactics()
    valid_tactic_ids = {t["id"] for t in tactics}

    techniques = await client.get_techniques()

    # All technique tactic_ids should reference valid tactics
    for technique in techniques:
        tactic_ids = technique["tactic_id"]
        if isinstance(tactic_ids, str):
            tactic_ids = [tactic_ids]
        for tid in tactic_ids:
            assert tid in valid_tactic_ids, f"Technique {technique['id']} references invalid tactic {tid}"

    await client.close()
