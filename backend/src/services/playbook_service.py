"""
Playbook Service.

Handles loading, validation, execution, and management of SOAR playbooks.
Supports YAML-based playbook definitions with variable interpolation
and configurable error handling.
"""

import asyncio
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union
from uuid import uuid4

import yaml

from ..models.playbook import (
    Playbook,
    PlaybookRun,
    PlaybookRunStatus,
    PlaybookStep,
    StepResult,
    StepStatus,
)


logger = logging.getLogger(__name__)


# ============================================================================
# Exceptions
# ============================================================================

class PlaybookError(Exception):
    """Base exception for playbook-related errors."""
    pass


class PlaybookNotFoundError(PlaybookError):
    """Raised when a playbook cannot be found."""
    pass


class PlaybookExecutionError(PlaybookError):
    """Raised when playbook execution fails."""
    pass


class PlaybookValidationError(PlaybookError):
    """Raised when playbook definition is invalid."""
    pass


# ============================================================================
# Variable Interpolation
# ============================================================================

# Pattern to match ${variable.path} expressions
VARIABLE_PATTERN = re.compile(r'\$\{([^}]+)\}')


def _get_nested_value(obj: Dict[str, Any], path: str) -> Any:
    """Get a nested value from a dictionary using dot notation.

    Args:
        obj: The dictionary to search
        path: Dot-separated path (e.g., "incident.title")

    Returns:
        The value at the path, or empty string if not found
    """
    parts = path.split(".")
    current = obj

    for part in parts:
        if not isinstance(current, dict):
            return ""
        current = current.get(part, "")
        if current == "":
            return ""

    return current


def interpolate_variables(
    template: Union[str, Dict, List, Any],
    context: Dict[str, Any]
) -> Any:
    """Interpolate ${variable} patterns in templates.

    Supports:
    - Simple strings: "Hello ${name}" -> "Hello World"
    - Nested paths: "${incident.title}" -> "Malware Alert"
    - Full replacement: "${previous.result}" -> actual dict/list value
    - Nested structures: Recursively processes dicts and lists

    Args:
        template: The template to interpolate (string, dict, list, or other)
        context: Dictionary of values for variable substitution

    Returns:
        The interpolated result
    """
    if isinstance(template, str):
        # Check if the entire string is a single variable reference
        match = VARIABLE_PATTERN.fullmatch(template)
        if match:
            # Return the actual value (could be dict, list, etc.)
            return _get_nested_value(context, match.group(1))

        # Otherwise, do string substitution
        def replace_match(m: re.Match) -> str:
            value = _get_nested_value(context, m.group(1))
            return str(value) if value != "" else ""

        return VARIABLE_PATTERN.sub(replace_match, template)

    elif isinstance(template, dict):
        return {k: interpolate_variables(v, context) for k, v in template.items()}

    elif isinstance(template, list):
        return [interpolate_variables(item, context) for item in template]

    else:
        return template


# ============================================================================
# Action Handler Type
# ============================================================================

# Type for action handler functions
ActionHandler = Callable[[str, Dict[str, Any]], Coroutine[Any, Any, Dict[str, Any]]]


async def default_action_handler(action: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Default action handler that logs actions without executing them.

    In production, this would dispatch to actual EDR/SIEM/notification systems.
    """
    logger.info(f"Executing action: {action} with params: {params}")
    return {"status": "success", "action": action, "simulated": True}


# ============================================================================
# Playbook Service
# ============================================================================

class PlaybookService:
    """Service for managing and executing SOAR playbooks.

    Handles:
    - Loading playbooks from YAML files
    - Variable interpolation in playbook steps
    - Sequential step execution with error handling
    - Run history tracking
    - Creating new playbooks programmatically
    """

    def __init__(
        self,
        playbook_dir: Optional[str] = None,
        action_handler: Optional[ActionHandler] = None
    ):
        """Initialize the playbook service.

        Args:
            playbook_dir: Directory containing playbook YAML files
            action_handler: Async function to execute actions
        """
        self._playbook_dir = Path(playbook_dir) if playbook_dir else None
        self._action_handler = action_handler or default_action_handler
        self._playbooks: Dict[str, Playbook] = {}
        self._runs: Dict[str, PlaybookRun] = {}

        # Load playbooks from directory if provided
        if self._playbook_dir and self._playbook_dir.exists():
            self._load_playbooks()

    def _load_playbooks(self) -> None:
        """Load all playbook YAML files from the playbook directory."""
        if not self._playbook_dir:
            return

        for yaml_file in self._playbook_dir.glob("*.yaml"):
            try:
                self._load_playbook_file(yaml_file)
            except Exception as e:
                logger.warning(f"Failed to load playbook {yaml_file}: {e}")

        for yml_file in self._playbook_dir.glob("*.yml"):
            try:
                self._load_playbook_file(yml_file)
            except Exception as e:
                logger.warning(f"Failed to load playbook {yml_file}: {e}")

    def _load_playbook_file(self, file_path: Path) -> Playbook:
        """Load a single playbook from a YAML file.

        Args:
            file_path: Path to the YAML file

        Returns:
            The loaded Playbook

        Raises:
            PlaybookValidationError: If the playbook is invalid
        """
        with open(file_path) as f:
            data = yaml.safe_load(f)

        # Validate required fields
        if not data.get("name"):
            raise PlaybookValidationError(f"Playbook missing 'name': {file_path}")
        if not data.get("steps"):
            raise PlaybookValidationError(f"Playbook missing 'steps': {file_path}")

        # Generate ID based on filename
        playbook_id = f"pb-{file_path.stem}-{uuid4().hex[:4]}"

        playbook = Playbook.from_dict(data, playbook_id)
        self._playbooks[playbook.name] = playbook

        logger.info(f"Loaded playbook: {playbook.name} ({playbook.id})")
        return playbook

    # ========================================================================
    # Playbook Retrieval
    # ========================================================================

    def list_playbooks(self) -> List[Playbook]:
        """Get all loaded playbooks.

        Returns:
            List of all playbooks
        """
        return list(self._playbooks.values())

    def get_playbook(self, name: str) -> Playbook:
        """Get a playbook by name.

        Args:
            name: The playbook name

        Returns:
            The playbook

        Raises:
            PlaybookNotFoundError: If playbook not found
        """
        if name not in self._playbooks:
            raise PlaybookNotFoundError(f"Playbook not found: {name}")
        return self._playbooks[name]

    def get_playbook_by_id(self, playbook_id: str) -> Playbook:
        """Get a playbook by ID.

        Args:
            playbook_id: The playbook ID

        Returns:
            The playbook

        Raises:
            PlaybookNotFoundError: If playbook not found
        """
        for playbook in self._playbooks.values():
            if playbook.id == playbook_id:
                return playbook
        raise PlaybookNotFoundError(f"Playbook not found: {playbook_id}")

    def get_playbooks_by_trigger(self, trigger: str) -> List[Playbook]:
        """Get all playbooks that can be triggered by an event.

        Args:
            trigger: The trigger event name

        Returns:
            List of playbooks with matching trigger
        """
        return [
            pb for pb in self._playbooks.values()
            if trigger in pb.triggers
        ]

    # ========================================================================
    # Playbook Execution
    # ========================================================================

    async def execute_playbook(
        self,
        name: str,
        context: Dict[str, Any],
        triggered_by: Optional[str] = None
    ) -> PlaybookRun:
        """Execute a playbook with the given context.

        Args:
            name: Name of the playbook to execute
            context: Input context for variable interpolation
            triggered_by: What triggered this execution

        Returns:
            PlaybookRun with execution results

        Raises:
            PlaybookNotFoundError: If playbook not found
        """
        playbook = self.get_playbook(name)
        return await self._execute(playbook, context, triggered_by)

    async def execute_playbook_by_id(
        self,
        playbook_id: str,
        context: Dict[str, Any],
        triggered_by: Optional[str] = None
    ) -> PlaybookRun:
        """Execute a playbook by ID with the given context.

        Args:
            playbook_id: ID of the playbook to execute
            context: Input context for variable interpolation
            triggered_by: What triggered this execution

        Returns:
            PlaybookRun with execution results
        """
        playbook = self.get_playbook_by_id(playbook_id)
        return await self._execute(playbook, context, triggered_by)

    async def _execute(
        self,
        playbook: Playbook,
        context: Dict[str, Any],
        triggered_by: Optional[str] = None
    ) -> PlaybookRun:
        """Internal execution logic.

        Args:
            playbook: The playbook to execute
            context: Input context
            triggered_by: Trigger source

        Returns:
            PlaybookRun with results
        """
        # Create run record
        run = PlaybookRun.create(playbook, context, triggered_by)
        run.status = PlaybookRunStatus.RUNNING
        self._runs[run.id] = run

        logger.info(f"Starting playbook run: {run.id} for {playbook.name}")

        # Build execution context (includes previous step results)
        exec_context = dict(context)

        try:
            for idx, step in enumerate(playbook.steps):
                step_result = await self._execute_step(
                    step, idx, exec_context
                )
                run.step_results.append(step_result)

                # Handle step failure
                if step_result.status in (StepStatus.FAILED, StepStatus.TIMEOUT):
                    if step.on_error == "fail":
                        run.status = PlaybookRunStatus.FAILED
                        run.error = step_result.error
                        break
                    elif step.on_error == "notify_human":
                        run.status = PlaybookRunStatus.NEEDS_REVIEW
                        run.error = step_result.error
                        break
                    # on_error == "continue" - proceed to next step

                # Make result available for next step
                if step_result.result:
                    exec_context["previous"] = {"result": step_result.result}

            # If we completed all steps without failure
            if run.status == PlaybookRunStatus.RUNNING:
                run.status = PlaybookRunStatus.COMPLETED

        except Exception as e:
            logger.exception(f"Playbook execution failed: {e}")
            run.status = PlaybookRunStatus.FAILED
            run.error = str(e)

        run.completed_at = datetime.utcnow()
        logger.info(
            f"Playbook run {run.id} completed with status: {run.status.value}"
        )

        return run

    async def _execute_step(
        self,
        step: PlaybookStep,
        index: int,
        context: Dict[str, Any]
    ) -> StepResult:
        """Execute a single playbook step.

        Args:
            step: The step to execute
            index: Step index in the playbook
            context: Current execution context

        Returns:
            StepResult with execution outcome
        """
        started_at = datetime.utcnow()

        # Interpolate variables in params
        params = interpolate_variables(step.params, context)

        logger.debug(f"Executing step {index}: {step.action}")

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self._action_handler(step.action, params),
                timeout=step.timeout
            )

            completed_at = datetime.utcnow()
            duration_ms = int((completed_at - started_at).total_seconds() * 1000)

            return StepResult(
                step_index=index,
                action=step.action,
                status=StepStatus.SUCCESS,
                result=result,
                duration_ms=duration_ms,
                started_at=started_at,
                completed_at=completed_at
            )

        except asyncio.TimeoutError:
            completed_at = datetime.utcnow()
            duration_ms = int((completed_at - started_at).total_seconds() * 1000)

            return StepResult(
                step_index=index,
                action=step.action,
                status=StepStatus.TIMEOUT,
                error=f"Step timed out after {step.timeout}s",
                duration_ms=duration_ms,
                started_at=started_at,
                completed_at=completed_at
            )

        except Exception as e:
            completed_at = datetime.utcnow()
            duration_ms = int((completed_at - started_at).total_seconds() * 1000)

            return StepResult(
                step_index=index,
                action=step.action,
                status=StepStatus.FAILED,
                error=str(e),
                duration_ms=duration_ms,
                started_at=started_at,
                completed_at=completed_at
            )

    # ========================================================================
    # Run History
    # ========================================================================

    def get_run(self, run_id: str) -> Optional[PlaybookRun]:
        """Get a specific run by ID.

        Args:
            run_id: The run ID

        Returns:
            PlaybookRun or None if not found
        """
        return self._runs.get(run_id)

    def list_runs(
        self,
        playbook_id: Optional[str] = None,
        limit: int = 100
    ) -> List[PlaybookRun]:
        """List playbook runs with optional filtering.

        Args:
            playbook_id: Filter by playbook ID
            limit: Maximum results to return

        Returns:
            List of playbook runs
        """
        runs = list(self._runs.values())

        if playbook_id:
            runs = [r for r in runs if r.playbook_id == playbook_id]

        # Sort by start time descending
        runs.sort(key=lambda r: r.started_at or datetime.min, reverse=True)

        return runs[:limit]

    # ========================================================================
    # Playbook Management
    # ========================================================================

    def create_playbook(
        self,
        name: str,
        description: str,
        triggers: List[str],
        steps: List[Dict[str, Any]],
        enabled: bool = True
    ) -> Playbook:
        """Create a new playbook.

        Args:
            name: Playbook name
            description: Description of the playbook
            triggers: List of trigger events
            steps: List of step definitions
            enabled: Whether the playbook is active

        Returns:
            The created playbook

        Raises:
            PlaybookError: If playbook with name already exists
        """
        if name in self._playbooks:
            raise PlaybookError(f"Playbook already exists: {name}")

        playbook_id = f"pb-{uuid4().hex[:8]}"

        playbook_data = {
            "name": name,
            "description": description,
            "triggers": triggers,
            "steps": steps,
            "enabled": enabled
        }

        playbook = Playbook.from_dict(playbook_data, playbook_id)
        self._playbooks[name] = playbook

        # Persist to YAML if directory is configured
        if self._playbook_dir:
            self._save_playbook(playbook)

        logger.info(f"Created playbook: {name} ({playbook_id})")
        return playbook

    def _save_playbook(self, playbook: Playbook) -> None:
        """Save a playbook to a YAML file.

        Args:
            playbook: The playbook to save
        """
        if not self._playbook_dir:
            return

        self._playbook_dir.mkdir(parents=True, exist_ok=True)
        file_path = self._playbook_dir / f"{playbook.name}.yaml"

        with open(file_path, "w") as f:
            yaml.dump(playbook.to_dict(), f, default_flow_style=False)

        logger.info(f"Saved playbook to {file_path}")


# ============================================================================
# Singleton Instance
# ============================================================================

_service_instance: Optional[PlaybookService] = None


def get_playbook_service(
    playbook_dir: Optional[str] = None,
    action_handler: Optional[ActionHandler] = None
) -> PlaybookService:
    """Get or create the playbook service singleton.

    Args:
        playbook_dir: Directory containing playbook YAML files
        action_handler: Optional custom action handler

    Returns:
        PlaybookService instance
    """
    global _service_instance
    if _service_instance is None:
        # Default to playbooks directory relative to this file
        if playbook_dir is None:
            default_dir = Path(__file__).parent.parent.parent / "playbooks"
            playbook_dir = str(default_dir)

        _service_instance = PlaybookService(
            playbook_dir=playbook_dir,
            action_handler=action_handler
        )
    return _service_instance


def reset_playbook_service() -> None:
    """Reset the singleton instance (for testing)."""
    global _service_instance
    _service_instance = None
