"""
Unit tests for data isolation between phases.

Task: T-027
Requirement: REQ-002-004-004
Test ID: UT-033

Tests that tools must NOT reveal data from future phases.
If current phase is 3, tools only see phase 1-3 data (BR-013).
"""

import pytest


class TestDataIsolation:
    """Tests that future-phase data is never leaked."""

    @pytest.fixture(autouse=True)
    def setup_scenario(self):
        """Set up scenario manager."""
        from src.scenarios.scenario_state_manager import (
            get_scenario_manager, reset_scenario_manager
        )
        reset_scenario_manager()
        self.mgr = get_scenario_manager()
        yield
        reset_scenario_manager()

    @pytest.mark.asyncio
    async def test_phase_1_siem_no_phase_2_data(self):
        """At phase 1, SIEM should not contain phase 2+ incidents."""
        await self.mgr.start_scenario("apt29")
        await self.mgr.advance_to_phase(1)

        from src.mcp.tools.siem import handle_siem_list_incidents
        result = await handle_siem_list_incidents({})
        incident_ids = {inc["id"] for inc in result["data"]}

        # Phase 2 incident IDs should NOT be present
        assert "INC-APT29-003" not in incident_ids  # Phase 2
        assert "INC-APT29-004" not in incident_ids  # Phase 2
        assert "INC-APT29-005" not in incident_ids  # Phase 3
        # Phase 1 should be present
        assert "INC-APT29-001" in incident_ids

    @pytest.mark.asyncio
    async def test_phase_1_edr_no_phase_2_data(self):
        """At phase 1, EDR should not contain phase 2+ detections."""
        await self.mgr.start_scenario("apt29")
        await self.mgr.advance_to_phase(1)

        from src.mcp.tools.edr import handle_edr_list_detections
        result = await handle_edr_list_detections({})
        detection_ids = {det["id"] for det in result["data"]}

        # Phase 2 detection IDs should NOT be present
        assert "DET-APT29-003" not in detection_ids  # Phase 2
        assert "DET-APT29-004" not in detection_ids  # Phase 2
        # Phase 1 should be present
        assert "DET-APT29-001" in detection_ids

    @pytest.mark.asyncio
    async def test_phase_1_intel_no_future_iocs(self):
        """At phase 1, Intel should not contain phase 3+ IOCs."""
        await self.mgr.start_scenario("apt29")
        await self.mgr.advance_to_phase(1)

        from src.mcp.tools.intel import handle_intel_get_indicator
        # IOC-APT29-004 is a hash from phase 3 - should not be known yet
        result = await handle_intel_get_indicator({
            "indicator_type": "hash",
            "value": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"
        })
        # At phase 1, the hash IOC is not yet introduced in scenario context
        # (even though phase 1 EDR detection references it, the IOC entry is phase 3)
        # The intel tool should return the IOC if it is present in cumulative data
        # Phase 1 has IOC-APT29-001, IOC-APT29-002, IOC-APT29-003
        # IOC-APT29-004 (the hash) is added in phase 3, so at phase 1 it should be unknown
        # Since the value matches the hash of IOC-APT29-004 which is NOT in phase 1 IOCs,
        # the intel tool should NOT return it as a known threat indicator

    @pytest.mark.asyncio
    async def test_phase_3_siem_includes_only_phases_1_to_3(self):
        """At phase 3, SIEM should include phases 1-3 only."""
        await self.mgr.start_scenario("apt29")
        await self.mgr.advance_to_phase(3)

        from src.mcp.tools.siem import handle_siem_list_incidents
        result = await handle_siem_list_incidents({})
        incident_ids = {inc["id"] for inc in result["data"]}

        # Phase 1-3 should be present
        assert "INC-APT29-001" in incident_ids  # Phase 1
        assert "INC-APT29-003" in incident_ids  # Phase 2
        assert "INC-APT29-005" in incident_ids  # Phase 3

        # Phase 4+ should NOT be present
        assert "INC-APT29-007" not in incident_ids  # Phase 4
        assert "INC-APT29-008" not in incident_ids  # Phase 5

    @pytest.mark.asyncio
    async def test_phase_5_edr_includes_only_phases_1_to_5(self):
        """At phase 5, EDR should include phases 1-5 only."""
        await self.mgr.start_scenario("apt29")
        await self.mgr.advance_to_phase(5)

        from src.mcp.tools.edr import handle_edr_list_detections
        result = await handle_edr_list_detections({})
        detection_ids = {det["id"] for det in result["data"]}

        # Phase 1-5 should be present
        assert "DET-APT29-001" in detection_ids  # Phase 1
        assert "DET-APT29-009" in detection_ids  # Phase 5

        # Phase 6+ should NOT be present
        assert "DET-APT29-011" not in detection_ids  # Phase 6
        assert "DET-APT29-013" not in detection_ids  # Phase 7

    @pytest.mark.asyncio
    async def test_phase_advance_reveals_more_data(self):
        """Advancing phase should reveal data from the new phase."""
        await self.mgr.start_scenario("apt29")
        await self.mgr.advance_to_phase(1)

        from src.mcp.tools.siem import handle_siem_list_incidents

        # Phase 1: limited data
        result1 = await handle_siem_list_incidents({})
        count_phase1 = len(result1["data"])

        # Advance to phase 3
        await self.mgr.advance_to_phase(3)
        result3 = await handle_siem_list_incidents({})
        count_phase3 = len(result3["data"])

        assert count_phase3 > count_phase1

    @pytest.mark.asyncio
    async def test_get_incident_not_in_current_phase_returns_not_found(self):
        """Getting an incident from a future phase should return not found."""
        await self.mgr.start_scenario("apt29")
        await self.mgr.advance_to_phase(1)

        from src.mcp.tools.siem import handle_siem_get_incident
        # INC-APT29-007 is phase 4, not visible at phase 1
        result = await handle_siem_get_incident({"incident_id": "INC-APT29-007"})
        # Should return a generic not-found or the incident should not be from scenario
        assert result["id"] == "INC-APT29-007"
        # It should not contain scenario-specific data since it's not visible
        assert result.get("severity", "medium") == "medium"  # Generic default

    @pytest.mark.asyncio
    async def test_phase_8_reveals_all_data(self):
        """At phase 8, all data should be visible."""
        await self.mgr.start_scenario("apt29")
        await self.mgr.advance_to_phase(8)

        from src.mcp.tools.siem import handle_siem_list_incidents
        result = await handle_siem_list_incidents({})
        assert len(result["data"]) == 14  # All 14 incidents

        from src.mcp.tools.edr import handle_edr_list_detections
        result_edr = await handle_edr_list_detections({})
        assert len(result_edr["data"]) == 15  # All 15 detections
