"""
Unit tests for PlaybookService.

Following TDD: Tests for playbook loading, execution, and variable interpolation.
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import tempfile
import yaml

from src.services.playbook_service import (
    PlaybookService,
    Playbook,
    PlaybookStep,
    PlaybookRun,
    PlaybookRunStatus,
    StepResult,
    StepStatus,
    PlaybookError,
    PlaybookNotFoundError,
    PlaybookExecutionError,
    interpolate_variables,
)


class TestPlaybookModels:
    """Tests for Playbook data models."""

    def test_playbook_step_creation(self):
        """PlaybookStep should store action, params, timeout, and on_error."""
        step = PlaybookStep(
            action="edr.contain_host",
            params={"reason": "Test containment"},
            timeout=60,
            on_error="notify_human"
        )
        assert step.action == "edr.contain_host"
        assert step.params == {"reason": "Test containment"}
        assert step.timeout == 60
        assert step.on_error == "notify_human"

    def test_playbook_step_defaults(self):
        """PlaybookStep should have sensible defaults."""
        step = PlaybookStep(action="edr.scan")
        assert step.action == "edr.scan"
        assert step.params == {}
        assert step.timeout == 120  # Default 2 minutes
        assert step.on_error == "fail"  # Default behavior

    def test_playbook_creation(self):
        """Playbook should store name, description, triggers, and steps."""
        step = PlaybookStep(action="edr.scan")
        playbook = Playbook(
            id="pb-001",
            name="test_playbook",
            description="A test playbook",
            triggers=["high_confidence_malware"],
            steps=[step]
        )
        assert playbook.id == "pb-001"
        assert playbook.name == "test_playbook"
        assert playbook.description == "A test playbook"
        assert playbook.triggers == ["high_confidence_malware"]
        assert len(playbook.steps) == 1

    def test_playbook_run_creation(self):
        """PlaybookRun should track execution state."""
        run = PlaybookRun(
            id="run-001",
            playbook_id="pb-001",
            playbook_name="test_playbook",
            status=PlaybookRunStatus.RUNNING,
            context={"incident_id": "INC-123"}
        )
        assert run.id == "run-001"
        assert run.playbook_id == "pb-001"
        assert run.status == PlaybookRunStatus.RUNNING
        assert run.context == {"incident_id": "INC-123"}
        assert run.step_results == []

    def test_step_result_creation(self):
        """StepResult should capture step execution outcome."""
        result = StepResult(
            step_index=0,
            action="edr.contain_host",
            status=StepStatus.SUCCESS,
            result={"device_id": "DEV-001", "status": "contained"},
            duration_ms=1500
        )
        assert result.step_index == 0
        assert result.action == "edr.contain_host"
        assert result.status == StepStatus.SUCCESS
        assert result.result == {"device_id": "DEV-001", "status": "contained"}
        assert result.duration_ms == 1500


class TestVariableInterpolation:
    """Tests for variable interpolation in playbook parameters."""

    def test_simple_variable_interpolation(self):
        """Should interpolate ${variable} patterns."""
        template = "Containment reason: ${incident.title}"
        context = {"incident": {"title": "Ransomware detected"}}
        result = interpolate_variables(template, context)
        assert result == "Containment reason: Ransomware detected"

    def test_nested_variable_interpolation(self):
        """Should interpolate nested variable paths."""
        template = "User: ${alert.user.name}, Host: ${alert.host.hostname}"
        context = {
            "alert": {
                "user": {"name": "jsmith"},
                "host": {"hostname": "WS-FIN-042"}
            }
        }
        result = interpolate_variables(template, context)
        assert result == "User: jsmith, Host: WS-FIN-042"

    def test_previous_result_interpolation(self):
        """Should interpolate ${previous.result} patterns."""
        template = "${previous.result}"
        context = {"previous": {"result": {"artifacts": ["mem.dmp", "reg.hive"]}}}
        result = interpolate_variables(template, context)
        assert result == {"artifacts": ["mem.dmp", "reg.hive"]}

    def test_missing_variable_returns_empty(self):
        """Missing variables should return empty string."""
        template = "Value: ${missing.variable}"
        context = {}
        result = interpolate_variables(template, context)
        assert result == "Value: "

    def test_interpolate_dict_values(self):
        """Should interpolate all string values in a dict."""
        params = {
            "reason": "${incident.title}",
            "device_id": "${host.device_id}",
            "static": "unchanged"
        }
        context = {
            "incident": {"title": "Malware detected"},
            "host": {"device_id": "DEV-001"}
        }
        result = interpolate_variables(params, context)
        assert result == {
            "reason": "Malware detected",
            "device_id": "DEV-001",
            "static": "unchanged"
        }

    def test_interpolate_list_values(self):
        """Should interpolate values in lists."""
        params = ["${item1}", "static", "${item2}"]
        context = {"item1": "first", "item2": "second"}
        result = interpolate_variables(params, context)
        assert result == ["first", "static", "second"]


class TestPlaybookServiceLoading:
    """Tests for loading playbooks from YAML files."""

    @pytest.fixture
    def temp_playbook_dir(self):
        """Create a temporary directory with playbook files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a valid playbook file
            playbook_yaml = {
                "name": "contain_and_investigate",
                "description": "Auto-containment followed by investigation",
                "triggers": ["high_confidence_malware", "ransomware_detected"],
                "steps": [
                    {
                        "action": "edr.contain_host",
                        "params": {"reason": "${incident.title}"},
                        "on_error": "notify_human"
                    },
                    {
                        "action": "edr.collect_artifacts",
                        "params": {"types": ["memory_dump", "registry"]},
                        "timeout": 300
                    }
                ]
            }
            with open(Path(tmpdir) / "contain_and_investigate.yaml", "w") as f:
                yaml.dump(playbook_yaml, f)

            # Create another playbook
            vip_yaml = {
                "name": "vip_escalation",
                "description": "Escalation for VIP users",
                "triggers": ["vip_alert"],
                "steps": [
                    {"action": "notify.escalate", "params": {"priority": "high"}}
                ]
            }
            with open(Path(tmpdir) / "vip_escalation.yaml", "w") as f:
                yaml.dump(vip_yaml, f)

            yield tmpdir

    def test_load_playbooks_from_directory(self, temp_playbook_dir):
        """Service should load all playbooks from directory."""
        service = PlaybookService(playbook_dir=temp_playbook_dir)
        playbooks = service.list_playbooks()

        assert len(playbooks) == 2
        names = [p.name for p in playbooks]
        assert "contain_and_investigate" in names
        assert "vip_escalation" in names

    def test_get_playbook_by_name(self, temp_playbook_dir):
        """Service should retrieve playbook by name."""
        service = PlaybookService(playbook_dir=temp_playbook_dir)
        playbook = service.get_playbook("contain_and_investigate")

        assert playbook is not None
        assert playbook.name == "contain_and_investigate"
        assert len(playbook.steps) == 2
        assert playbook.steps[0].action == "edr.contain_host"

    def test_get_playbook_by_id(self, temp_playbook_dir):
        """Service should retrieve playbook by ID."""
        service = PlaybookService(playbook_dir=temp_playbook_dir)
        playbooks = service.list_playbooks()
        playbook_id = playbooks[0].id

        playbook = service.get_playbook_by_id(playbook_id)
        assert playbook is not None
        assert playbook.id == playbook_id

    def test_get_nonexistent_playbook_raises(self, temp_playbook_dir):
        """Getting a nonexistent playbook should raise error."""
        service = PlaybookService(playbook_dir=temp_playbook_dir)

        with pytest.raises(PlaybookNotFoundError):
            service.get_playbook("nonexistent_playbook")

    def test_get_playbooks_by_trigger(self, temp_playbook_dir):
        """Service should filter playbooks by trigger."""
        service = PlaybookService(playbook_dir=temp_playbook_dir)
        playbooks = service.get_playbooks_by_trigger("ransomware_detected")

        assert len(playbooks) == 1
        assert playbooks[0].name == "contain_and_investigate"

    def test_invalid_playbook_yaml_skipped(self, temp_playbook_dir):
        """Invalid YAML files should be skipped with warning."""
        # Create an invalid playbook file (missing required fields)
        with open(Path(temp_playbook_dir) / "invalid.yaml", "w") as f:
            f.write("name: incomplete\n")  # Missing steps

        service = PlaybookService(playbook_dir=temp_playbook_dir)
        playbooks = service.list_playbooks()

        # Should still load valid playbooks
        assert len(playbooks) == 2


class TestPlaybookServiceExecution:
    """Tests for playbook execution."""

    @pytest.fixture
    def mock_action_handler(self):
        """Create a mock action handler."""
        async def handler(action: str, params: dict) -> dict:
            return {"status": "success", "action": action, "params": params}
        return AsyncMock(side_effect=handler)

    @pytest.fixture
    def temp_playbook_dir(self):
        """Create temporary directory with test playbooks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            playbook_yaml = {
                "name": "test_playbook",
                "description": "Test",
                "triggers": ["test"],
                "steps": [
                    {"action": "edr.contain_host", "params": {"reason": "${incident.title}"}},
                    {"action": "edr.scan", "params": {"artifacts": "${previous.result}"}}
                ]
            }
            with open(Path(tmpdir) / "test_playbook.yaml", "w") as f:
                yaml.dump(playbook_yaml, f)
            yield tmpdir

    @pytest.mark.asyncio
    async def test_execute_playbook_success(self, temp_playbook_dir, mock_action_handler):
        """Successful playbook execution should complete all steps."""
        service = PlaybookService(
            playbook_dir=temp_playbook_dir,
            action_handler=mock_action_handler
        )

        context = {"incident": {"title": "Malware detected", "id": "INC-123"}}
        run = await service.execute_playbook("test_playbook", context)

        assert run.status == PlaybookRunStatus.COMPLETED
        assert len(run.step_results) == 2
        assert all(r.status == StepStatus.SUCCESS for r in run.step_results)

    @pytest.mark.asyncio
    async def test_execute_playbook_passes_context(self, temp_playbook_dir, mock_action_handler):
        """Playbook execution should interpolate context into params."""
        service = PlaybookService(
            playbook_dir=temp_playbook_dir,
            action_handler=mock_action_handler
        )

        context = {"incident": {"title": "Ransomware Alert"}}
        await service.execute_playbook("test_playbook", context)

        # Check first call had interpolated params
        first_call = mock_action_handler.call_args_list[0]
        assert first_call[0][1]["reason"] == "Ransomware Alert"

    @pytest.mark.asyncio
    async def test_execute_playbook_chains_results(self, temp_playbook_dir):
        """Previous step results should be available to next step."""
        call_order = []

        async def tracking_handler(action: str, params: dict) -> dict:
            call_order.append((action, params))
            if action == "edr.contain_host":
                return {"device_id": "DEV-001", "status": "contained"}
            return {"status": "success"}

        service = PlaybookService(
            playbook_dir=temp_playbook_dir,
            action_handler=tracking_handler
        )

        context = {"incident": {"title": "Test"}}
        await service.execute_playbook("test_playbook", context)

        # Second step should receive first step's result
        assert len(call_order) == 2
        second_params = call_order[1][1]
        assert second_params["artifacts"] == {"device_id": "DEV-001", "status": "contained"}

    @pytest.mark.asyncio
    async def test_execute_playbook_step_failure_default(self, temp_playbook_dir):
        """By default, step failure should stop execution."""
        async def failing_handler(action: str, params: dict) -> dict:
            if action == "edr.contain_host":
                raise Exception("Containment failed")
            return {"status": "success"}

        service = PlaybookService(
            playbook_dir=temp_playbook_dir,
            action_handler=failing_handler
        )

        context = {"incident": {"title": "Test"}}
        run = await service.execute_playbook("test_playbook", context)

        assert run.status == PlaybookRunStatus.FAILED
        assert len(run.step_results) == 1
        assert run.step_results[0].status == StepStatus.FAILED

    @pytest.mark.asyncio
    async def test_execute_playbook_on_error_continue(self):
        """on_error: continue should proceed to next step."""
        with tempfile.TemporaryDirectory() as tmpdir:
            playbook_yaml = {
                "name": "continue_on_error",
                "description": "Test continue behavior",
                "triggers": ["test"],
                "steps": [
                    {"action": "edr.risky_action", "params": {}, "on_error": "continue"},
                    {"action": "edr.safe_action", "params": {}}
                ]
            }
            with open(Path(tmpdir) / "continue_on_error.yaml", "w") as f:
                yaml.dump(playbook_yaml, f)

            call_count = 0
            async def handler(action: str, params: dict) -> dict:
                nonlocal call_count
                call_count += 1
                if action == "edr.risky_action":
                    raise Exception("Expected failure")
                return {"status": "success"}

            service = PlaybookService(playbook_dir=tmpdir, action_handler=handler)
            run = await service.execute_playbook("continue_on_error", {})

            assert run.status == PlaybookRunStatus.COMPLETED
            assert call_count == 2  # Both steps were called
            assert run.step_results[0].status == StepStatus.FAILED
            assert run.step_results[1].status == StepStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_execute_playbook_on_error_notify_human(self):
        """on_error: notify_human should mark as needs_review."""
        with tempfile.TemporaryDirectory() as tmpdir:
            playbook_yaml = {
                "name": "notify_on_error",
                "description": "Test notify behavior",
                "triggers": ["test"],
                "steps": [
                    {"action": "edr.action", "params": {}, "on_error": "notify_human"}
                ]
            }
            with open(Path(tmpdir) / "notify_on_error.yaml", "w") as f:
                yaml.dump(playbook_yaml, f)

            async def handler(action: str, params: dict) -> dict:
                raise Exception("Needs human review")

            service = PlaybookService(playbook_dir=tmpdir, action_handler=handler)
            run = await service.execute_playbook("notify_on_error", {})

            assert run.status == PlaybookRunStatus.NEEDS_REVIEW
            assert run.step_results[0].status == StepStatus.FAILED

    @pytest.mark.asyncio
    async def test_execute_playbook_timeout(self):
        """Steps should respect timeout configuration."""
        import asyncio

        with tempfile.TemporaryDirectory() as tmpdir:
            playbook_yaml = {
                "name": "timeout_test",
                "description": "Test timeout",
                "triggers": ["test"],
                "steps": [
                    {"action": "edr.slow_action", "params": {}, "timeout": 1}  # 1 second
                ]
            }
            with open(Path(tmpdir) / "timeout_test.yaml", "w") as f:
                yaml.dump(playbook_yaml, f)

            async def slow_handler(action: str, params: dict) -> dict:
                await asyncio.sleep(5)  # Takes 5 seconds
                return {"status": "success"}

            service = PlaybookService(playbook_dir=tmpdir, action_handler=slow_handler)
            run = await service.execute_playbook("timeout_test", {})

            assert run.status == PlaybookRunStatus.FAILED
            assert run.step_results[0].status == StepStatus.TIMEOUT

    @pytest.mark.asyncio
    async def test_execute_nonexistent_playbook_raises(self, temp_playbook_dir, mock_action_handler):
        """Executing a nonexistent playbook should raise error."""
        service = PlaybookService(
            playbook_dir=temp_playbook_dir,
            action_handler=mock_action_handler
        )

        with pytest.raises(PlaybookNotFoundError):
            await service.execute_playbook("nonexistent", {})


class TestPlaybookRunHistory:
    """Tests for playbook run history tracking."""

    @pytest.fixture
    def temp_playbook_dir(self):
        """Create temporary directory with test playbook."""
        with tempfile.TemporaryDirectory() as tmpdir:
            playbook_yaml = {
                "name": "simple_playbook",
                "description": "Simple test",
                "triggers": ["test"],
                "steps": [{"action": "test.action", "params": {}}]
            }
            with open(Path(tmpdir) / "simple_playbook.yaml", "w") as f:
                yaml.dump(playbook_yaml, f)
            yield tmpdir

    @pytest.mark.asyncio
    async def test_run_is_stored(self, temp_playbook_dir):
        """Completed runs should be stored in history."""
        async def handler(action: str, params: dict) -> dict:
            return {"status": "success"}

        service = PlaybookService(playbook_dir=temp_playbook_dir, action_handler=handler)
        run = await service.execute_playbook("simple_playbook", {})

        stored_run = service.get_run(run.id)
        assert stored_run is not None
        assert stored_run.id == run.id

    @pytest.mark.asyncio
    async def test_list_runs_for_playbook(self, temp_playbook_dir):
        """Should list all runs for a specific playbook."""
        async def handler(action: str, params: dict) -> dict:
            return {"status": "success"}

        service = PlaybookService(playbook_dir=temp_playbook_dir, action_handler=handler)

        # Execute multiple runs
        await service.execute_playbook("simple_playbook", {"run": 1})
        await service.execute_playbook("simple_playbook", {"run": 2})

        playbook = service.get_playbook("simple_playbook")
        runs = service.list_runs(playbook.id)

        assert len(runs) == 2

    @pytest.mark.asyncio
    async def test_runs_have_timestamps(self, temp_playbook_dir):
        """Runs should have start and end timestamps."""
        async def handler(action: str, params: dict) -> dict:
            return {"status": "success"}

        service = PlaybookService(playbook_dir=temp_playbook_dir, action_handler=handler)

        before = datetime.utcnow()
        run = await service.execute_playbook("simple_playbook", {})
        after = datetime.utcnow()

        assert run.started_at is not None
        assert run.completed_at is not None
        assert before <= run.started_at <= run.completed_at <= after


class TestPlaybookCreation:
    """Tests for creating new playbooks programmatically."""

    @pytest.fixture
    def temp_playbook_dir(self):
        """Create empty temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_create_playbook(self, temp_playbook_dir):
        """Should create and save a new playbook."""
        service = PlaybookService(playbook_dir=temp_playbook_dir)

        playbook = service.create_playbook(
            name="new_playbook",
            description="A newly created playbook",
            triggers=["new_trigger"],
            steps=[
                {"action": "test.action", "params": {"key": "value"}}
            ]
        )

        assert playbook.name == "new_playbook"
        assert playbook.description == "A newly created playbook"

        # Should be retrievable
        retrieved = service.get_playbook("new_playbook")
        assert retrieved is not None
        assert retrieved.id == playbook.id

    def test_create_playbook_persists_to_yaml(self, temp_playbook_dir):
        """Created playbooks should be saved as YAML files."""
        service = PlaybookService(playbook_dir=temp_playbook_dir)

        service.create_playbook(
            name="persistent_playbook",
            description="Should persist",
            triggers=["test"],
            steps=[{"action": "test.action", "params": {}}]
        )

        # Check file exists
        yaml_path = Path(temp_playbook_dir) / "persistent_playbook.yaml"
        assert yaml_path.exists()

        # Verify content
        with open(yaml_path) as f:
            content = yaml.safe_load(f)
        assert content["name"] == "persistent_playbook"
        assert content["description"] == "Should persist"

    def test_create_playbook_duplicate_name_raises(self, temp_playbook_dir):
        """Creating a playbook with existing name should raise error."""
        service = PlaybookService(playbook_dir=temp_playbook_dir)

        service.create_playbook(
            name="duplicate",
            description="First",
            triggers=["test"],
            steps=[{"action": "test", "params": {}}]
        )

        with pytest.raises(PlaybookError, match="already exists"):
            service.create_playbook(
                name="duplicate",
                description="Second",
                triggers=["test"],
                steps=[{"action": "test", "params": {}}]
            )
