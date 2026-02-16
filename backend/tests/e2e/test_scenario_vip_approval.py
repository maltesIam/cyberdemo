"""
E2E Tests for Scenario 2: VIP Human-in-the-Loop (INC-ANCHOR-002)

Asset: LAPTOP-CFO-01 (vip, executive)
Intel: Same malicious QakBot hash as scenario 1
Expected: Request approval, wait for human decision, then execute based on decision

This scenario validates that VIP/executive devices always require human approval
regardless of confidence score, and properly handles approval/rejection workflows.
"""

import pytest
from datetime import datetime, timezone

from src.services.investigation_service import (
    InvestigationState,
    ActionOutcome,
    AssetData,
    AlertData,
    IntelData,
    CTEMData,
    PropagationData,
)


class TestScenario2VIPApproval:
    """E2E tests for VIP human-in-the-loop approval workflow."""

    # =========================================================================
    # Test 1: VIP Asset Detection
    # =========================================================================

    @pytest.mark.asyncio
    async def test_vip_asset_correctly_identified(
        self,
        investigation_service,
        scenario2_alert: AlertData,
        scenario2_asset: AssetData,
    ):
        """Test that VIP tags are correctly detected on the asset."""
        # Act
        investigation = await investigation_service.create_investigation(
            incident_id=scenario2_alert.incident_id,
            alert=scenario2_alert,
            asset=scenario2_asset,
        )

        # Assert
        assert investigation is not None
        assert investigation.incident_id == "INC-ANCHOR-002"
        assert investigation.asset.device_id == "LAPTOP-CFO-01"
        assert "vip" in investigation.asset.tags
        assert "executive" in investigation.asset.tags
        assert investigation.asset.criticality == "vip"

    # =========================================================================
    # Test 2: High Confidence but VIP Still Requires Approval
    # =========================================================================

    @pytest.mark.asyncio
    async def test_high_confidence_vip_still_requires_approval(
        self,
        investigation_service,
        scenario2_alert: AlertData,
        scenario2_asset: AssetData,
        scenario2_intel: IntelData,
        scenario2_propagation: PropagationData,
    ):
        """Test that even with high confidence, VIP devices require approval."""
        # Arrange: Use Red CTEM to ensure maximum confidence score
        high_risk_ctem = CTEMData(
            device_id="LAPTOP-CFO-01",
            cve_list=["CVE-2024-1111", "CVE-2024-2222"],
            risk_color="Red",  # +15 instead of Green's 0
            vulnerability_count=2,
        )

        investigation = await investigation_service.create_investigation(
            incident_id=scenario2_alert.incident_id,
            alert=scenario2_alert,
            asset=scenario2_asset,
        )
        enriched = await investigation_service.enrich(
            investigation=investigation,
            intel=scenario2_intel,
            ctem=high_risk_ctem,  # Use Red CTEM for higher confidence
            propagation=scenario2_propagation,
        )
        scored = await investigation_service.calculate_confidence(enriched)

        # Verify confidence is high (>= 90)
        # Intel: 58/72 VT (+30) + 2 malware labels (+10) = 40
        # Behavior: T1059.001 (+20) + encodedcommand (+10) = 30
        # Context: Red CTEM (+15) + VIP (+5) = 20
        # Propagation: 3 hosts (+5) = 5
        # Total: 40 + 30 + 20 + 5 = 95
        assert scored.confidence_score >= 90, f"Expected >= 90, got {scored.confidence_score}"

        # Act
        evaluated = await investigation_service.evaluate_policy(scored)

        # Assert: Despite high confidence, VIP requires approval
        assert evaluated.state == InvestigationState.POLICY_EVALUATED
        assert evaluated.policy_decision.action.value == "request_approval"
        assert evaluated.policy_decision.requires_approval is True
        assert "vip" in evaluated.policy_decision.reason.lower() or "executive" in evaluated.policy_decision.reason.lower() or "critical" in evaluated.policy_decision.reason.lower()

    # =========================================================================
    # Test 3: Approval Request Created Correctly
    # =========================================================================

    @pytest.mark.asyncio
    async def test_approval_request_created_with_card_data(
        self,
        investigation_service,
        scenario2_alert: AlertData,
        scenario2_asset: AssetData,
        scenario2_intel: IntelData,
        scenario2_ctem: CTEMData,
        scenario2_propagation: PropagationData,
    ):
        """Test that approval request is created with rich card data for Teams/Slack."""
        # Arrange: Run investigation until approval is needed
        result = await investigation_service.run_investigation(
            incident_id=scenario2_alert.incident_id,
            alert=scenario2_alert,
            asset=scenario2_asset,
            intel=scenario2_intel,
            ctem=scenario2_ctem,
            propagation=scenario2_propagation,
        )

        # Assert: Investigation paused awaiting approval
        assert result.state == InvestigationState.AWAITING_APPROVAL
        assert result.outcome == ActionOutcome.AWAITING_APPROVAL

        # Assert: Approval request exists with proper data
        assert result.approval_request is not None
        assert result.approval_request.incident_id == "INC-ANCHOR-002"
        assert result.approval_request.action_type == "contain"
        assert result.approval_request.target_id == "LAPTOP-CFO-01"

        # Assert: Card data for adaptive card
        assert result.approval_request.card_data is not None
        card = result.approval_request.card_data
        assert "device_id" in card
        assert "confidence_score" in card
        assert "malware_labels" in card or "threat_name" in card

    # =========================================================================
    # Test 4: Approval Granted Leads to Containment
    # =========================================================================

    @pytest.mark.asyncio
    async def test_approval_granted_executes_containment(
        self,
        investigation_service,
        scenario2_alert: AlertData,
        scenario2_asset: AssetData,
        scenario2_intel: IntelData,
        scenario2_ctem: CTEMData,
        scenario2_propagation: PropagationData,
    ):
        """Test that granting approval leads to containment execution."""
        # Arrange: Run investigation until awaiting approval
        investigation = await investigation_service.run_investigation(
            incident_id=scenario2_alert.incident_id,
            alert=scenario2_alert,
            asset=scenario2_asset,
            intel=scenario2_intel,
            ctem=scenario2_ctem,
            propagation=scenario2_propagation,
        )

        assert investigation.state == InvestigationState.AWAITING_APPROVAL

        # Act: Grant approval
        result = await investigation_service.process_approval(
            incident_id=scenario2_alert.incident_id,
            decision="approved",
            decided_by="security_analyst@acme.com",
            notes="Verified with CFO - proceed with containment",
        )

        # Assert: Containment executed after approval
        assert result.state == InvestigationState.COMPLETED
        assert result.outcome == ActionOutcome.CONTAINED_AFTER_APPROVAL

        # Assert: Containment was executed
        assert result.containment_executed is True
        assert result.containment_action_id is not None

        # Assert: Approval recorded in timeline
        timeline_actions = [t.action for t in result.timeline]
        assert "approval_granted" in timeline_actions
        assert "containment" in timeline_actions

        # Assert: Ticket and postmortem created
        assert result.ticket_id is not None
        assert result.postmortem_id is not None

    # =========================================================================
    # Test 5: Approval Denied Does Not Contain
    # =========================================================================

    @pytest.mark.asyncio
    async def test_approval_denied_does_not_contain(
        self,
        investigation_service,
        scenario2_alert: AlertData,
        scenario2_asset: AssetData,
        scenario2_intel: IntelData,
        scenario2_ctem: CTEMData,
        scenario2_propagation: PropagationData,
    ):
        """Test that denying approval does not execute containment."""
        # Arrange: Run investigation until awaiting approval
        investigation = await investigation_service.run_investigation(
            incident_id=scenario2_alert.incident_id,
            alert=scenario2_alert,
            asset=scenario2_asset,
            intel=scenario2_intel,
            ctem=scenario2_ctem,
            propagation=scenario2_propagation,
        )

        assert investigation.state == InvestigationState.AWAITING_APPROVAL

        # Act: Deny approval
        result = await investigation_service.process_approval(
            incident_id=scenario2_alert.incident_id,
            decision="rejected",
            decided_by="security_analyst@acme.com",
            notes="CFO confirmed this is authorized software for financial reporting",
        )

        # Assert: Investigation completed without containment
        assert result.state == InvestigationState.COMPLETED
        assert result.outcome == ActionOutcome.APPROVAL_DENIED

        # Assert: Containment was NOT executed
        assert result.containment_executed is False
        assert result.containment_action_id is None

        # Assert: Denial recorded in timeline
        timeline_actions = [t.action for t in result.timeline]
        assert "approval_denied" in timeline_actions
        assert "containment" not in timeline_actions

        # Assert: Still creates a ticket for tracking
        assert result.ticket_id is not None


class TestScenario2EdgeCases:
    """Edge case tests for VIP approval scenario."""

    @pytest.mark.asyncio
    async def test_server_tag_also_requires_approval(
        self,
        investigation_service,
        scenario2_alert: AlertData,
        scenario2_intel: IntelData,
    ):
        """Test that 'server' tag also requires human approval."""
        # Arrange: Asset with server tag
        server_asset = AssetData(
            device_id="SRV-PROD-01",
            hostname="SRV-PROD-01.corp.acme.com",
            device_type="server",
            tags=["server", "production"],
            owner="infra@acme.com",
            department="Infrastructure",
            criticality="critical",
        )

        investigation = await investigation_service.create_investigation(
            incident_id="INC-SERVER-001",
            alert=scenario2_alert,
            asset=server_asset,
        )
        enriched = await investigation_service.enrich(
            investigation=investigation,
            intel=scenario2_intel,
            ctem=CTEMData(
                device_id="SRV-PROD-01",
                cve_list=[],
                risk_color="Green",
                vulnerability_count=0,
            ),
            propagation=PropagationData(
                hash_sha256=scenario2_alert.hash_sha256,
                affected_hosts=["SRV-PROD-01"],
                affected_count=1,
            ),
        )
        scored = await investigation_service.calculate_confidence(enriched)
        evaluated = await investigation_service.evaluate_policy(scored)

        # Assert: Server requires approval
        assert evaluated.policy_decision.action.value == "request_approval"
        assert evaluated.policy_decision.requires_approval is True

    @pytest.mark.asyncio
    async def test_domain_controller_requires_approval(
        self,
        investigation_service,
        scenario2_alert: AlertData,
        scenario2_intel: IntelData,
    ):
        """Test that domain-controller tag requires human approval."""
        # Arrange: Asset with domain-controller tag
        dc_asset = AssetData(
            device_id="DC-CORP-01",
            hostname="DC-CORP-01.corp.acme.com",
            device_type="server",
            tags=["domain-controller", "infrastructure"],
            owner="ad-admins@acme.com",
            department="IT",
            criticality="critical",
        )

        investigation = await investigation_service.create_investigation(
            incident_id="INC-DC-001",
            alert=scenario2_alert,
            asset=dc_asset,
        )
        enriched = await investigation_service.enrich(
            investigation=investigation,
            intel=scenario2_intel,
            ctem=CTEMData(
                device_id="DC-CORP-01",
                cve_list=[],
                risk_color="Green",
                vulnerability_count=0,
            ),
            propagation=PropagationData(
                hash_sha256=scenario2_alert.hash_sha256,
                affected_hosts=["DC-CORP-01"],
                affected_count=1,
            ),
        )
        scored = await investigation_service.calculate_confidence(enriched)
        evaluated = await investigation_service.evaluate_policy(scored)

        # Assert: Domain controller requires approval
        assert evaluated.policy_decision.action.value == "request_approval"
        assert evaluated.policy_decision.requires_approval is True

    @pytest.mark.asyncio
    async def test_approval_timeout_escalates(
        self,
        investigation_service,
        scenario2_alert: AlertData,
        scenario2_asset: AssetData,
        scenario2_intel: IntelData,
        scenario2_ctem: CTEMData,
        scenario2_propagation: PropagationData,
    ):
        """Test that approval timeout leads to escalation."""
        # Arrange: Run investigation until awaiting approval
        investigation = await investigation_service.run_investigation(
            incident_id=scenario2_alert.incident_id,
            alert=scenario2_alert,
            asset=scenario2_asset,
            intel=scenario2_intel,
            ctem=scenario2_ctem,
            propagation=scenario2_propagation,
        )

        assert investigation.state == InvestigationState.AWAITING_APPROVAL

        # Act: Simulate timeout
        result = await investigation_service.handle_approval_timeout(
            incident_id=scenario2_alert.incident_id,
            timeout_minutes=30,
        )

        # Assert: Investigation escalated
        assert result.state == InvestigationState.COMPLETED
        assert result.outcome == ActionOutcome.ESCALATED

        # Assert: Escalation recorded
        timeline_actions = [t.action for t in result.timeline]
        assert "escalation" in timeline_actions
