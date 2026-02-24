"""
Unit tests for asyncio Lock thread safety - UT-023
Requirement: REQ-002-001-004
Description: Add asyncio.Lock to all ScenarioStateManager state mutations
to ensure thread-safe concurrent access.

BR-016: The ScenarioStateManager must be thread-safe (asyncio Lock).
"""
import pytest
import asyncio


def _make_simple_phases():
    """Create minimal phases for concurrency testing."""
    from src.models.scenario_types import PhaseEvents, SiemIncident

    return {
        1: PhaseEvents(
            phase_number=1,
            phase_name="Phase 1",
            incidents=[
                SiemIncident(
                    id="INC-001",
                    title="Incident 1",
                    severity="high",
                    source="sentinel",
                    mitre_tactic="initial-access",
                    mitre_technique="T1566",
                ),
            ],
            detections=[],
            iocs=[],
        ),
        2: PhaseEvents(
            phase_number=2,
            phase_name="Phase 2",
            incidents=[
                SiemIncident(
                    id="INC-002",
                    title="Incident 2",
                    severity="critical",
                    source="sentinel",
                    mitre_tactic="execution",
                    mitre_technique="T1059",
                ),
            ],
            detections=[],
            iocs=[],
        ),
    }


class TestAsyncioLockPresence:
    """Test that the ScenarioStateManager uses asyncio.Lock."""

    def test_manager_has_lock_attribute(self):
        """ScenarioStateManager has an asyncio.Lock instance."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        assert hasattr(mgr, "_lock")
        assert isinstance(mgr._lock, asyncio.Lock)


class TestConcurrentStateAccess:
    """Test that concurrent operations don't corrupt state."""

    @pytest.mark.asyncio
    async def test_concurrent_advance_and_read(self):
        """Concurrent advance_to_phase and get_current_state don't corrupt data."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_simple_phases()
        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(1)

        errors = []

        async def advance_repeatedly():
            for _ in range(50):
                try:
                    await mgr.advance_to_phase(1)
                    await mgr.advance_to_phase(2)
                except Exception as e:
                    errors.append(str(e))

        async def read_repeatedly():
            for _ in range(100):
                try:
                    state = await mgr.get_current_state()
                    if state is not None:
                        # State should always be consistent
                        assert state.current_phase in (1, 2)
                except Exception as e:
                    errors.append(str(e))

        # Run advance and read concurrently
        await asyncio.gather(
            advance_repeatedly(),
            read_repeatedly(),
            read_repeatedly(),
        )

        assert errors == [], f"Concurrent access errors: {errors}"

    @pytest.mark.asyncio
    async def test_concurrent_mutations_no_data_loss(self):
        """Concurrent contain_host calls all persist correctly."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_simple_phases()
        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(1)

        host_count = 20

        async def contain_hosts(start: int, count: int):
            for i in range(start, start + count):
                await mgr.contain_host(f"HOST-{i:03d}")

        # Run 4 concurrent batches of containments
        await asyncio.gather(
            contain_hosts(0, host_count),
            contain_hosts(host_count, host_count),
            contain_hosts(host_count * 2, host_count),
            contain_hosts(host_count * 3, host_count),
        )

        state = await mgr.get_current_state()
        expected_total = host_count * 4
        assert len(state.contained_hosts) == expected_total, (
            f"Expected {expected_total} contained hosts, got {len(state.contained_hosts)}"
        )

    @pytest.mark.asyncio
    async def test_concurrent_comments_no_data_loss(self):
        """Concurrent add_comment calls all persist correctly."""
        from src.services.scenario_state_manager import ScenarioStateManager
        from src.models.scenario_types import AgentComment

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_simple_phases()
        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(1)

        comment_count = 20

        async def add_comments(prefix: str, count: int):
            for i in range(count):
                comment = AgentComment(
                    id=f"{prefix}-{i:03d}",
                    incident_id="INC-001",
                    content=f"Comment {prefix}-{i}",
                )
                await mgr.add_comment(comment)

        await asyncio.gather(
            add_comments("A", comment_count),
            add_comments("B", comment_count),
            add_comments("C", comment_count),
        )

        state = await mgr.get_current_state()
        expected_total = comment_count * 3
        assert len(state.comments) == expected_total, (
            f"Expected {expected_total} comments, got {len(state.comments)}"
        )

    @pytest.mark.asyncio
    async def test_concurrent_start_and_advance_safe(self):
        """Concurrent start_scenario and advance_to_phase don't crash."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_simple_phases()
        errors = []

        async def restart_scenario():
            for _ in range(10):
                try:
                    await mgr.start_scenario("test", "Test", phases)
                except Exception as e:
                    errors.append(str(e))

        async def advance_phase():
            for _ in range(10):
                try:
                    state = await mgr.get_current_state()
                    if state is not None and state.total_phases >= 1:
                        await mgr.advance_to_phase(1)
                except Exception as e:
                    errors.append(str(e))

        await asyncio.gather(
            restart_scenario(),
            advance_phase(),
        )

        assert errors == [], f"Concurrent access errors: {errors}"
