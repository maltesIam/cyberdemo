"""
E2E Tests for Scenario 1: Auto-Containment (INC-ANCHOR-001)

Asset: WS-FIN-042 (standard-user, finance)
Intel: Malicious QakBot hash with 58/72 VT detections
Expected: Confidence >= 90%, auto-contain, create ticket and postmortem

This scenario validates that high-confidence malware on a standard workstation
triggers automatic containment without requiring human approval.
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


class TestScenario1AutoContainment:
    """E2E tests for auto-containment on standard workstation."""

    # =========================================================================
    # Test 1: Investigation Initialization
    # =========================================================================

    @pytest.mark.asyncio
    async def test_investigation_initializes_correctly(
        self,
        investigation_service,
        scenario1_alert: AlertData,
        scenario1_asset: AssetData,
    ):
        """Test that investigation initializes with correct data."""
        # Act
        investigation = await investigation_service.create_investigation(
            incident_id=scenario1_alert.incident_id,
            alert=scenario1_alert,
            asset=scenario1_asset,
        )

        # Assert
        assert investigation is not None
        assert investigation.incident_id == "INC-ANCHOR-001"
        assert investigation.state == InvestigationState.INITIALIZED
        assert investigation.asset.device_id == "WS-FIN-042"
        assert "standard-user" in investigation.asset.tags

    # =========================================================================
    # Test 2: Enrichment with Intel, CTEM, Propagation
    # =========================================================================

    @pytest.mark.asyncio
    async def test_enrichment_aggregates_all_sources(
        self,
        investigation_service,
        scenario1_alert: AlertData,
        scenario1_asset: AssetData,
        scenario1_intel: IntelData,
        scenario1_ctem: CTEMData,
        scenario1_propagation: PropagationData,
    ):
        """Test that enrichment gathers data from intel, CTEM, and propagation."""
        # Arrange
        investigation = await investigation_service.create_investigation(
            incident_id=scenario1_alert.incident_id,
            alert=scenario1_alert,
            asset=scenario1_asset,
        )

        # Act
        enriched = await investigation_service.enrich(
            investigation=investigation,
            intel=scenario1_intel,
            ctem=scenario1_ctem,
            propagation=scenario1_propagation,
        )

        # Assert
        assert enriched.state == InvestigationState.ENRICHING
        assert enriched.intel.verdict == "malicious"
        assert enriched.intel.vt_score == 58
        assert enriched.ctem.risk_color == "Red"
        assert enriched.propagation.affected_count == 3

    # =========================================================================
    # Test 3: Confidence Score Calculation
    # =========================================================================

    @pytest.mark.asyncio
    async def test_confidence_score_exceeds_90(
        self,
        investigation_service,
        scenario1_alert: AlertData,
        scenario1_asset: AssetData,
        scenario1_intel: IntelData,
        scenario1_ctem: CTEMData,
        scenario1_propagation: PropagationData,
    ):
        """Test that confidence score is >= 90% for this scenario."""
        # Arrange
        investigation = await investigation_service.create_investigation(
            incident_id=scenario1_alert.incident_id,
            alert=scenario1_alert,
            asset=scenario1_asset,
        )
        enriched = await investigation_service.enrich(
            investigation=investigation,
            intel=scenario1_intel,
            ctem=scenario1_ctem,
            propagation=scenario1_propagation,
        )

        # Act
        scored = await investigation_service.calculate_confidence(enriched)

        # Assert
        assert scored.state == InvestigationState.SCORING
        assert scored.confidence_score >= 90, (
            f"Expected confidence >= 90, got {scored.confidence_score}"
        )
        # Verify score breakdown exists
        assert scored.score_breakdown is not None
        assert scored.score_breakdown.intel > 0
        assert scored.score_breakdown.behavior > 0

    # =========================================================================
    # Test 4: Policy Evaluation Results in Auto-Contain
    # =========================================================================

    @pytest.mark.asyncio
    async def test_policy_decision_is_auto_contain(
        self,
        investigation_service,
        scenario1_alert: AlertData,
        scenario1_asset: AssetData,
        scenario1_intel: IntelData,
        scenario1_ctem: CTEMData,
        scenario1_propagation: PropagationData,
    ):
        """Test that policy engine decides to auto-contain for high confidence."""
        # Arrange
        investigation = await investigation_service.create_investigation(
            incident_id=scenario1_alert.incident_id,
            alert=scenario1_alert,
            asset=scenario1_asset,
        )
        enriched = await investigation_service.enrich(
            investigation=investigation,
            intel=scenario1_intel,
            ctem=scenario1_ctem,
            propagation=scenario1_propagation,
        )
        scored = await investigation_service.calculate_confidence(enriched)

        # Act
        evaluated = await investigation_service.evaluate_policy(scored)

        # Assert
        assert evaluated.state == InvestigationState.POLICY_EVALUATED
        assert evaluated.policy_decision.action.value == "contain"
        assert evaluated.policy_decision.requires_approval is False
        assert "auto" in evaluated.policy_decision.reason.lower() or "high" in evaluated.policy_decision.reason.lower()

    # =========================================================================
    # Test 5: Full Workflow Executes Containment and Creates Artifacts
    # =========================================================================

    @pytest.mark.asyncio
    async def test_full_workflow_auto_contains_and_creates_artifacts(
        self,
        investigation_service,
        scenario1_alert: AlertData,
        scenario1_asset: AssetData,
        scenario1_intel: IntelData,
        scenario1_ctem: CTEMData,
        scenario1_propagation: PropagationData,
    ):
        """Test complete workflow: enrich -> score -> policy -> contain -> artifacts."""
        # Act: Run full investigation workflow
        result = await investigation_service.run_investigation(
            incident_id=scenario1_alert.incident_id,
            alert=scenario1_alert,
            asset=scenario1_asset,
            intel=scenario1_intel,
            ctem=scenario1_ctem,
            propagation=scenario1_propagation,
        )

        # Assert: Final state and outcome
        assert result.state == InvestigationState.COMPLETED
        assert result.outcome == ActionOutcome.AUTO_CONTAINED

        # Assert: Containment was executed
        assert result.containment_executed is True
        assert result.containment_action_id is not None

        # Assert: Ticket was created
        assert result.ticket_id is not None
        assert result.ticket_id.startswith("TKT-")

        # Assert: Postmortem was generated
        assert result.postmortem_id is not None
        assert result.postmortem_id.startswith("PM-")

        # Assert: Timeline has all steps
        assert len(result.timeline) >= 4
        timeline_actions = [t.action for t in result.timeline]
        assert "enrichment" in timeline_actions
        assert "scoring" in timeline_actions
        assert "policy_evaluation" in timeline_actions
        assert "containment" in timeline_actions


class TestScenario1EdgeCases:
    """Edge case tests for auto-containment scenario."""

    @pytest.mark.asyncio
    async def test_medium_confidence_requests_approval(
        self,
        investigation_service,
        scenario1_asset: AssetData,
    ):
        """Test that medium confidence (50-89%) on standard asset requests approval."""
        # Arrange: Create a clean alert without suspicious cmdline patterns
        # to get medium confidence (50-89 range)
        clean_alert = AlertData(
            alert_id="ALT-MEDIUM-001",
            incident_id="INC-MEDIUM-001",
            hash_sha256="d4e5f678901234567890123456789012345678901234567890123456789012ab",
            process_name="normal_app.exe",
            cmdline="C:\\Program Files\\App\\normal_app.exe --start",  # No suspicious patterns
            mitre_technique="T1059.001",  # Still PowerShell technique (+20)
            severity="High"
        )

        investigation = await investigation_service.create_investigation(
            incident_id=clean_alert.incident_id,
            alert=clean_alert,
            asset=scenario1_asset,
        )

        # Intel: 55 VT detections (+30) + malware label (+10) = 40 intel
        # Behavior: T1059.001 (+20), no suspicious cmdline = 20 behavior
        # Context: Red CTEM (+15), standard asset = 15 context
        # Propagation: 2 hosts (+5) = 5
        # Total: 40 + 20 + 15 + 5 = 80 (medium range, should request approval)
        medium_intel = IntelData(
            hash_sha256=clean_alert.hash_sha256,
            verdict="malicious",
            vt_score=55,  # >50 triggers +30
            vt_total=72,
            malware_labels=["Trojan.Generic"],  # +10
            confidence=80,
        )
        medium_ctem = CTEMData(
            device_id="WS-FIN-042",
            cve_list=["CVE-2024-1234"],
            risk_color="Red",  # +15
            vulnerability_count=1,
        )
        medium_propagation = PropagationData(
            hash_sha256=clean_alert.hash_sha256,
            affected_hosts=["WS-FIN-042", "WS-FIN-043"],
            affected_count=2,  # +5
        )

        enriched = await investigation_service.enrich(
            investigation=investigation,
            intel=medium_intel,
            ctem=medium_ctem,
            propagation=medium_propagation,
        )
        scored = await investigation_service.calculate_confidence(enriched)

        # Act
        evaluated = await investigation_service.evaluate_policy(scored)

        # Assert: Should be in medium range (50-89) and request approval
        assert 50 <= scored.confidence_score < 90, f"Got {scored.confidence_score}, expected 50-89"
        assert evaluated.policy_decision.action.value == "request_approval"
        assert evaluated.policy_decision.requires_approval is True
