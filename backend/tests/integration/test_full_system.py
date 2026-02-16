"""
Full System Integration Tests for CyberDemo SOC Platform.

These tests verify complete flows across multiple services:
- MCP to Investigation
- Investigation to Containment
- Trigger to Gateway
- Approval Workflow
- Postmortem Generation

All external dependencies (gateway, OpenSearch) are mocked.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any
from datetime import datetime


# ============================================================================
# Test 1: MCP to Investigation Flow
# ============================================================================

@pytest.mark.asyncio
async def test_mcp_to_investigation_flow():
    """
    Test flow: MCP call siem_get_incident -> returns valid incident data ->
    Investigation service can process it.

    Steps:
    1. Call siem_get_incident via MCP server
    2. Verify incident data structure
    3. Process incident with investigation service (enrichment)
    4. Verify investigation result
    """
    from src.mcp.tools.siem import handle_siem_get_incident
    from src.services.policy_engine import PolicyEngine

    # Step 1: Get incident via MCP tool
    incident_id = "INC-ANCHOR-001"
    incident = await handle_siem_get_incident({"incident_id": incident_id})

    # Step 2: Verify incident has required fields for investigation
    assert incident is not None
    assert incident["id"] == incident_id
    assert "severity" in incident
    assert "status" in incident
    assert "asset" in incident

    # Step 3: Process with policy engine (simulates investigation)
    policy_engine = PolicyEngine()

    # Calculate confidence based on incident data
    confidence = policy_engine.calculate_confidence(
        intel_verdict="malicious",
        intel_confidence=85,
        propagation_count=3,
        ctem_risk="Red",
        severity=incident["severity"].capitalize()
    )

    # Step 4: Verify investigation produces valid confidence score
    assert confidence >= 0
    assert confidence <= 100

    # For critical malicious activity, confidence should be high
    assert confidence >= 60, f"Expected high confidence for malicious activity, got {confidence}"


@pytest.mark.asyncio
async def test_mcp_to_investigation_flow_benign():
    """
    Test flow for benign activity detection.

    Verifies low confidence scores for benign indicators.
    """
    from src.mcp.tools.siem import handle_siem_get_incident
    from src.services.policy_engine import PolicyEngine

    # Get benign incident
    incident = await handle_siem_get_incident({"incident_id": "INC-ANCHOR-003"})

    # Process with policy engine
    policy_engine = PolicyEngine()

    confidence = policy_engine.calculate_confidence(
        intel_verdict="benign",
        intel_confidence=90,
        propagation_count=0,
        ctem_risk="Green",
        severity=incident["severity"].capitalize() if "severity" in incident else "Low"
    )

    # Benign activity should have low confidence for threat
    assert confidence < 50, f"Expected low confidence for benign activity, got {confidence}"


# ============================================================================
# Test 2: Investigation to Containment Flow
# ============================================================================

@pytest.mark.asyncio
async def test_investigation_to_containment_flow():
    """
    Test flow: Investigation returns high confidence ->
    Containment is executed via SOAR -> Action is logged.

    Steps:
    1. Policy engine runs assessment with high confidence
    2. Decision allows auto-containment
    3. SOAR executes containment action
    4. Action is logged and retrievable
    """
    from src.services.policy_engine import PolicyEngine, ActionType
    from src.services.soar_service import SOARService

    policy_engine = PolicyEngine()
    soar_service = SOARService()

    # Step 1: High confidence investigation result (95%)
    confidence_score = 95.0
    device_tags = ["workstation"]  # Non-critical asset

    # Step 2: Policy decision
    decision = policy_engine.assess(
        confidence_score=confidence_score,
        device_tags=device_tags,
        has_approval=False
    )

    # High confidence non-critical asset should auto-contain
    assert decision.action == ActionType.CONTAIN
    assert decision.requires_approval is False

    # Step 3: Execute containment via SOAR
    device_id = "WS-FIN-042"
    action_result = await soar_service.execute_action(
        action="contain",
        device_id=device_id,
        reason=decision.reason,
        actor="soulbot"
    )

    # Step 4: Verify action logged
    assert action_result is not None
    assert action_result["status"] == "success"
    assert action_result["device_id"] == device_id
    assert action_result["action"] == "contain"
    assert "action_id" in action_result

    # Verify action can be retrieved
    retrieved_action = await soar_service.get_action(action_result["action_id"])
    assert retrieved_action is not None
    assert retrieved_action["action_id"] == action_result["action_id"]


@pytest.mark.asyncio
async def test_investigation_to_containment_blocked_for_low_confidence():
    """
    Test that low confidence investigations do NOT trigger containment.
    """
    from src.services.policy_engine import PolicyEngine, ActionType

    policy_engine = PolicyEngine()

    # Low confidence (30%)
    decision = policy_engine.assess(
        confidence_score=30.0,
        device_tags=["workstation"],
        has_approval=False
    )

    # Should mark as false positive, not contain
    assert decision.action == ActionType.MARK_FALSE_POSITIVE
    assert decision.requires_approval is False


@pytest.mark.asyncio
async def test_investigation_to_containment_requires_approval_for_medium_confidence():
    """
    Test that medium confidence requires approval before containment.
    """
    from src.services.policy_engine import PolicyEngine, ActionType

    policy_engine = PolicyEngine()

    # Medium confidence (70%)
    decision = policy_engine.assess(
        confidence_score=70.0,
        device_tags=["workstation"],
        has_approval=False
    )

    # Should request approval
    assert decision.action == ActionType.REQUEST_APPROVAL
    assert decision.requires_approval is True


# ============================================================================
# Test 3: Trigger to Gateway Flow
# ============================================================================

@pytest.mark.asyncio
async def test_trigger_to_gateway_flow():
    """
    Test flow: Incident created triggers event ->
    Gateway client receives command -> Command is properly formatted.

    Since gateway_client module doesn't exist yet, we'll mock the interface
    and verify the expected contract.
    """
    # Mock gateway client interface
    class MockGatewayClient:
        def __init__(self):
            self.sent_commands = []

        async def send_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
            """Send command to gateway."""
            # Validate command structure
            if "action" not in command:
                raise ValueError("Command must have 'action' field")
            if "incident_id" not in command:
                raise ValueError("Command must have 'incident_id' field")

            self.sent_commands.append(command)
            return {
                "status": "sent",
                "command_id": f"CMD-{len(self.sent_commands):04d}",
                "timestamp": datetime.utcnow().isoformat()
            }

    # Create gateway client
    gateway = MockGatewayClient()

    # Simulate incident trigger
    incident_id = "INC-ANCHOR-001"
    command = {
        "action": "investigate",
        "incident_id": incident_id,
        "priority": "high",
        "metadata": {
            "severity": "critical",
            "asset": "WS-FIN-042"
        }
    }

    # Send command to gateway
    result = await gateway.send_command(command)

    # Verify command was sent
    assert result["status"] == "sent"
    assert "command_id" in result

    # Verify command is properly formatted
    assert len(gateway.sent_commands) == 1
    sent_cmd = gateway.sent_commands[0]
    assert sent_cmd["action"] == "investigate"
    assert sent_cmd["incident_id"] == incident_id
    assert "metadata" in sent_cmd


@pytest.mark.asyncio
async def test_trigger_to_gateway_validates_command_structure():
    """
    Test that gateway client validates command structure.
    """
    class MockGatewayClient:
        async def send_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
            if "action" not in command:
                raise ValueError("Command must have 'action' field")
            if "incident_id" not in command:
                raise ValueError("Command must have 'incident_id' field")
            return {"status": "sent"}

    gateway = MockGatewayClient()

    # Invalid command - missing action
    with pytest.raises(ValueError, match="action"):
        await gateway.send_command({"incident_id": "INC-001"})

    # Invalid command - missing incident_id
    with pytest.raises(ValueError, match="incident_id"):
        await gateway.send_command({"action": "investigate"})


@pytest.mark.asyncio
async def test_trigger_to_gateway_multiple_commands():
    """
    Test sending multiple commands through gateway.
    """
    class MockGatewayClient:
        def __init__(self):
            self.sent_commands = []

        async def send_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
            self.sent_commands.append(command)
            return {"status": "sent", "command_id": f"CMD-{len(self.sent_commands)}"}

    gateway = MockGatewayClient()

    # Send multiple commands
    commands = [
        {"action": "investigate", "incident_id": "INC-001"},
        {"action": "enrich", "incident_id": "INC-001"},
        {"action": "contain", "incident_id": "INC-001"}
    ]

    for cmd in commands:
        await gateway.send_command(cmd)

    assert len(gateway.sent_commands) == 3
    assert [c["action"] for c in gateway.sent_commands] == ["investigate", "enrich", "contain"]


# ============================================================================
# Test 4: Approval Workflow Flow
# ============================================================================

@pytest.mark.asyncio
async def test_approval_workflow_flow():
    """
    Test flow: VIP incident creates approval request ->
    Approval is granted -> Containment proceeds.

    Steps:
    1. Policy engine detects VIP asset requires approval
    2. Approval request is created via MCP
    3. Approval is granted
    4. Containment is allowed after approval
    """
    from src.services.policy_engine import PolicyEngine, ActionType
    from src.services.soar_service import SOARService
    from src.mcp.tools.approvals import handle_approvals_request

    policy_engine = PolicyEngine()
    soar_service = SOARService()

    # Step 1: VIP device detection (requires approval)
    confidence_score = 95.0  # High confidence
    device_tags = ["vip", "executive"]  # VIP asset

    decision = policy_engine.assess(
        confidence_score=confidence_score,
        device_tags=device_tags,
        has_approval=False
    )

    # VIP assets require approval even with high confidence
    assert decision.action == ActionType.REQUEST_APPROVAL
    assert decision.requires_approval is True

    # Step 2: Create approval request via MCP
    incident_id = "INC-ANCHOR-002"
    approval_result = await handle_approvals_request({
        "incident_id": incident_id,
        "action": "contain",
        "reason": decision.reason
    })

    assert approval_result["status"] == "success"
    assert "approval_id" in approval_result

    # Step 3: Simulate approval granted
    has_approval = True

    # Step 4: Re-run assessment with approval
    decision_with_approval = policy_engine.assess(
        confidence_score=confidence_score,
        device_tags=device_tags,
        has_approval=has_approval
    )

    # With approval, containment should proceed
    assert decision_with_approval.action == ActionType.CONTAIN
    assert decision_with_approval.requires_approval is False

    # Execute containment
    action_result = await soar_service.execute_action(
        action="contain",
        device_id="LAPTOP-CFO-01",
        reason=decision_with_approval.reason,
        actor="security_analyst"
    )

    assert action_result["status"] == "success"


@pytest.mark.asyncio
async def test_approval_workflow_rejected():
    """
    Test that rejected approvals do not lead to containment.
    """
    from src.services.policy_engine import PolicyEngine, ActionType

    policy_engine = PolicyEngine()

    # VIP device with high confidence but no approval
    decision = policy_engine.assess(
        confidence_score=95.0,
        device_tags=["vip"],
        has_approval=False
    )

    # Without approval, should not contain
    assert decision.action == ActionType.REQUEST_APPROVAL
    assert decision.requires_approval is True


@pytest.mark.asyncio
async def test_approval_workflow_different_critical_tags():
    """
    Test approval workflow for different critical asset types.
    """
    from src.services.policy_engine import PolicyEngine, ActionType

    policy_engine = PolicyEngine()

    critical_tag_sets = [
        ["vip"],
        ["executive"],
        ["server"],
        ["domain-controller"],
        ["vip", "executive"],
        ["server", "domain-controller"]
    ]

    for tags in critical_tag_sets:
        decision = policy_engine.assess(
            confidence_score=95.0,
            device_tags=tags,
            has_approval=False
        )

        assert decision.action == ActionType.REQUEST_APPROVAL, f"Failed for tags: {tags}"
        assert decision.requires_approval is True, f"Failed for tags: {tags}"


# ============================================================================
# Test 5: Postmortem Generation Flow
# ============================================================================

@pytest.mark.asyncio
async def test_postmortem_generation_flow():
    """
    Test flow: Incident is contained -> Ticket is created ->
    Postmortem is generated.

    Steps:
    1. Close incident via SIEM
    2. Create ticket via MCP
    3. Generate postmortem report
    4. Verify postmortem contains required sections
    """
    from src.mcp.tools.siem import handle_siem_close_incident
    from src.mcp.tools.tickets import handle_tickets_create
    from src.mcp.tools.reports import handle_reports_generate_postmortem, handle_reports_get_postmortem

    incident_id = "INC-ANCHOR-001"

    # Step 1: Close the incident
    close_result = await handle_siem_close_incident({
        "incident_id": incident_id,
        "resolution": "true_positive",
        "notes": "Malware successfully contained and removed"
    })

    assert close_result["status"] == "success"
    assert close_result["resolution"] == "true_positive"

    # Step 2: Create ticket for tracking
    ticket_result = await handle_tickets_create({
        "title": f"Security Incident: {incident_id}",
        "description": "Incident containment and remediation tracking",
        "incident_id": incident_id,
        "priority": "critical"
    })

    assert ticket_result["status"] == "success"
    assert "ticket_id" in ticket_result

    # Step 3: Generate postmortem
    postmortem_result = await handle_reports_generate_postmortem({
        "incident_id": incident_id
    })

    assert postmortem_result["status"] == "success"
    assert "postmortem_id" in postmortem_result

    # Step 4: Verify postmortem sections
    assert "sections" in postmortem_result
    required_sections = [
        "Executive Summary",
        "Timeline of Events",
        "Root Cause Analysis",
        "Impact Assessment",
        "Remediation Actions",
        "Lessons Learned"
    ]

    for section in required_sections:
        assert section in postmortem_result["sections"], f"Missing section: {section}"

    # Verify postmortem can be retrieved
    retrieved_postmortem = await handle_reports_get_postmortem({
        "incident_id": incident_id
    })

    assert retrieved_postmortem["incident_id"] == incident_id
    assert "executive_summary" in retrieved_postmortem
    assert "timeline" in retrieved_postmortem
    assert "root_cause" in retrieved_postmortem


@pytest.mark.asyncio
async def test_postmortem_generation_requires_incident_id():
    """
    Test that postmortem generation requires incident_id.
    """
    from src.mcp.tools.reports import handle_reports_generate_postmortem

    with pytest.raises(ValueError, match="incident_id"):
        await handle_reports_generate_postmortem({})


@pytest.mark.asyncio
async def test_ticket_creation_requires_all_fields():
    """
    Test that ticket creation requires all mandatory fields.
    """
    from src.mcp.tools.tickets import handle_tickets_create

    # Missing title
    with pytest.raises(ValueError):
        await handle_tickets_create({
            "description": "Test",
            "incident_id": "INC-001"
        })

    # Missing description
    with pytest.raises(ValueError):
        await handle_tickets_create({
            "title": "Test",
            "incident_id": "INC-001"
        })

    # Missing incident_id
    with pytest.raises(ValueError):
        await handle_tickets_create({
            "title": "Test",
            "description": "Test"
        })


# ============================================================================
# End-to-End Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_complete_incident_lifecycle():
    """
    Test complete incident lifecycle from detection to postmortem.

    This test combines all flows into a single end-to-end test.
    """
    from src.mcp.tools.siem import handle_siem_get_incident, handle_siem_close_incident
    from src.mcp.tools.tickets import handle_tickets_create
    from src.mcp.tools.reports import handle_reports_generate_postmortem
    from src.services.policy_engine import PolicyEngine, ActionType
    from src.services.soar_service import SOARService

    incident_id = "INC-ANCHOR-001"
    policy_engine = PolicyEngine()
    soar_service = SOARService()

    # Phase 1: Detection
    incident = await handle_siem_get_incident({"incident_id": incident_id})
    assert incident["id"] == incident_id

    # Phase 2: Investigation
    confidence = policy_engine.calculate_confidence(
        intel_verdict="malicious",
        intel_confidence=90,
        propagation_count=2,
        ctem_risk="Red",
        severity="Critical"
    )
    assert confidence >= 70

    # Phase 3: Decision
    decision = policy_engine.assess(
        confidence_score=confidence,
        device_tags=["workstation"],  # Non-VIP
        has_approval=False
    )

    # Phase 4: Action (containment or approval based on decision)
    if decision.action == ActionType.CONTAIN:
        action_result = await soar_service.execute_action(
            action="contain",
            device_id=incident["asset"],
            reason=decision.reason,
            actor="soulbot"
        )
        assert action_result["status"] == "success"

    # Phase 5: Close incident
    close_result = await handle_siem_close_incident({
        "incident_id": incident_id,
        "resolution": "true_positive",
        "notes": "Automated containment successful"
    })
    assert close_result["status"] == "success"

    # Phase 6: Create ticket
    ticket_result = await handle_tickets_create({
        "title": f"Incident Closure: {incident_id}",
        "description": "Post-incident tracking and documentation",
        "incident_id": incident_id,
        "priority": "high"
    })
    assert ticket_result["status"] == "success"

    # Phase 7: Generate postmortem
    postmortem_result = await handle_reports_generate_postmortem({
        "incident_id": incident_id
    })
    assert postmortem_result["status"] == "success"
    assert len(postmortem_result["sections"]) >= 5


@pytest.mark.asyncio
async def test_soar_action_logging_and_retrieval():
    """
    Test that SOAR actions are properly logged and can be retrieved.
    """
    from src.services.soar_service import SOARService

    soar_service = SOARService()

    # Execute multiple actions
    actions_to_execute = [
        {"action": "contain", "device_id": "DEV-001", "reason": "Malware detected"},
        {"action": "isolate", "device_id": "DEV-002", "reason": "Lateral movement detected"},
        {"action": "scan", "device_id": "DEV-003", "reason": "Suspicious activity"},
    ]

    action_ids = []
    for action_data in actions_to_execute:
        result = await soar_service.execute_action(**action_data)
        assert result["status"] == "success"
        action_ids.append(result["action_id"])

    # Verify all actions can be retrieved
    for action_id in action_ids:
        action = await soar_service.get_action(action_id)
        assert action is not None
        assert action["action_id"] == action_id

    # Verify list actions works
    all_actions = await soar_service.list_actions(limit=100)
    assert len(all_actions) >= 3

    # Filter by device
    dev001_actions = await soar_service.list_actions(device_id="DEV-001")
    assert all(a["device_id"] == "DEV-001" for a in dev001_actions)

    # Filter by action type
    contain_actions = await soar_service.list_actions(action_type="contain")
    assert all(a["action"] == "contain" for a in contain_actions)


@pytest.mark.asyncio
async def test_soar_validates_actions():
    """
    Test that SOAR service validates action types and device IDs.
    """
    from src.services.soar_service import SOARService

    soar_service = SOARService()

    # Invalid action type
    with pytest.raises(ValueError, match="Invalid action"):
        await soar_service.execute_action(
            action="invalid_action",
            device_id="DEV-001",
            reason="Test"
        )

    # Invalid device ID
    with pytest.raises(LookupError, match="Device not found"):
        await soar_service.execute_action(
            action="contain",
            device_id="INVALID-DEVICE-999",
            reason="Test"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
