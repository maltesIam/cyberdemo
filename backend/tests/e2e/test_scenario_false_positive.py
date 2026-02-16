"""
E2E Tests for Scenario 3: False Positive (INC-ANCHOR-003)

Asset: SRV-DEV-03 (standard, development)
Intel: Benign hash with 0/72 VT detections
Expected: Confidence < 50%, mark as false positive, no containment

This scenario validates that low-confidence detections on benign files
are correctly identified as false positives and do not trigger containment.
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


class TestScenario3FalsePositive:
    """E2E tests for false positive detection workflow."""

    # =========================================================================
    # Test 1: Investigation Initialization for Dev Server
    # =========================================================================

    @pytest.mark.asyncio
    async def test_investigation_initializes_for_dev_server(
        self,
        investigation_service,
        scenario3_alert: AlertData,
        scenario3_asset: AssetData,
    ):
        """Test that investigation initializes correctly for development server."""
        # Act
        investigation = await investigation_service.create_investigation(
            incident_id=scenario3_alert.incident_id,
            alert=scenario3_alert,
            asset=scenario3_asset,
        )

        # Assert
        assert investigation is not None
        assert investigation.incident_id == "INC-ANCHOR-003"
        assert investigation.asset.device_id == "SRV-DEV-03"
        assert investigation.alert.severity == "Medium"
        assert "standard" in investigation.asset.tags
        assert "development" in investigation.asset.tags

    # =========================================================================
    # Test 2: Benign Intel Recognized
    # =========================================================================

    @pytest.mark.asyncio
    async def test_benign_intel_correctly_enriched(
        self,
        investigation_service,
        scenario3_alert: AlertData,
        scenario3_asset: AssetData,
        scenario3_intel: IntelData,
        scenario3_ctem: CTEMData,
        scenario3_propagation: PropagationData,
    ):
        """Test that benign intel is correctly recognized and enriched."""
        # Arrange
        investigation = await investigation_service.create_investigation(
            incident_id=scenario3_alert.incident_id,
            alert=scenario3_alert,
            asset=scenario3_asset,
        )

        # Act
        enriched = await investigation_service.enrich(
            investigation=investigation,
            intel=scenario3_intel,
            ctem=scenario3_ctem,
            propagation=scenario3_propagation,
        )

        # Assert
        assert enriched.state == InvestigationState.ENRICHING
        assert enriched.intel.verdict == "benign"
        assert enriched.intel.vt_score == 0
        assert len(enriched.intel.malware_labels) == 0
        assert enriched.ctem.risk_color == "Green"
        assert enriched.propagation.affected_count == 1

    # =========================================================================
    # Test 3: Confidence Score Below Threshold
    # =========================================================================

    @pytest.mark.asyncio
    async def test_confidence_score_below_50(
        self,
        investigation_service,
        scenario3_alert: AlertData,
        scenario3_asset: AssetData,
        scenario3_intel: IntelData,
        scenario3_ctem: CTEMData,
        scenario3_propagation: PropagationData,
    ):
        """Test that confidence score is < 50% for benign file."""
        # Arrange
        investigation = await investigation_service.create_investigation(
            incident_id=scenario3_alert.incident_id,
            alert=scenario3_alert,
            asset=scenario3_asset,
        )
        enriched = await investigation_service.enrich(
            investigation=investigation,
            intel=scenario3_intel,
            ctem=scenario3_ctem,
            propagation=scenario3_propagation,
        )

        # Act
        scored = await investigation_service.calculate_confidence(enriched)

        # Assert
        assert scored.state == InvestigationState.SCORING
        assert scored.confidence_score < 50, (
            f"Expected confidence < 50, got {scored.confidence_score}"
        )

        # Verify score breakdown shows low values
        assert scored.score_breakdown is not None
        assert scored.score_breakdown.intel == 0  # Benign = 0 intel points

    # =========================================================================
    # Test 4: Policy Decision is Mark False Positive
    # =========================================================================

    @pytest.mark.asyncio
    async def test_policy_decision_is_false_positive(
        self,
        investigation_service,
        scenario3_alert: AlertData,
        scenario3_asset: AssetData,
        scenario3_intel: IntelData,
        scenario3_ctem: CTEMData,
        scenario3_propagation: PropagationData,
    ):
        """Test that policy engine decides to mark as false positive."""
        # Arrange
        investigation = await investigation_service.create_investigation(
            incident_id=scenario3_alert.incident_id,
            alert=scenario3_alert,
            asset=scenario3_asset,
        )
        enriched = await investigation_service.enrich(
            investigation=investigation,
            intel=scenario3_intel,
            ctem=scenario3_ctem,
            propagation=scenario3_propagation,
        )
        scored = await investigation_service.calculate_confidence(enriched)

        # Act
        evaluated = await investigation_service.evaluate_policy(scored)

        # Assert
        assert evaluated.state == InvestigationState.POLICY_EVALUATED
        assert evaluated.policy_decision.action.value == "mark_false_positive"
        assert evaluated.policy_decision.requires_approval is False
        assert "below" in evaluated.policy_decision.reason.lower() or "threshold" in evaluated.policy_decision.reason.lower()

    # =========================================================================
    # Test 5: Full Workflow Marks as False Positive Without Containment
    # =========================================================================

    @pytest.mark.asyncio
    async def test_full_workflow_marks_false_positive(
        self,
        investigation_service,
        scenario3_alert: AlertData,
        scenario3_asset: AssetData,
        scenario3_intel: IntelData,
        scenario3_ctem: CTEMData,
        scenario3_propagation: PropagationData,
    ):
        """Test complete workflow marks as false positive without any containment."""
        # Act: Run full investigation workflow
        result = await investigation_service.run_investigation(
            incident_id=scenario3_alert.incident_id,
            alert=scenario3_alert,
            asset=scenario3_asset,
            intel=scenario3_intel,
            ctem=scenario3_ctem,
            propagation=scenario3_propagation,
        )

        # Assert: Final state and outcome
        assert result.state == InvestigationState.COMPLETED
        assert result.outcome == ActionOutcome.FALSE_POSITIVE

        # Assert: NO containment was executed
        assert result.containment_executed is False
        assert result.containment_action_id is None

        # Assert: Alert marked as false positive
        assert result.false_positive_marked is True

        # Assert: No ticket created for false positive (or minimal ticket)
        # False positives typically don't need escalation tickets
        # But may have a tracking ticket depending on policy
        # Here we assert no containment-type ticket
        if result.ticket_id:
            assert result.ticket_type == "informational"

        # Assert: Timeline shows false positive marking
        timeline_actions = [t.action for t in result.timeline]
        assert "enrichment" in timeline_actions
        assert "scoring" in timeline_actions
        assert "policy_evaluation" in timeline_actions
        assert "false_positive_marked" in timeline_actions
        assert "containment" not in timeline_actions


class TestScenario3EdgeCases:
    """Edge case tests for false positive scenario."""

    @pytest.mark.asyncio
    async def test_boundary_confidence_at_50_requests_approval(
        self,
        investigation_service,
    ):
        """Test that confidence >= 50 (boundary) requests approval, not FP."""
        # Arrange: Create alert that will produce exactly 50 confidence
        # Use high-risk MITRE technique and enough factors to hit 50+
        boundary_alert = AlertData(
            alert_id="ALT-BOUNDARY-001",
            incident_id="INC-BOUNDARY-001",
            hash_sha256="e5f6789012345678901234567890123456789012345678901234567890123456",
            process_name="suspicious_script.ps1",
            cmdline="powershell.exe -File suspicious_script.ps1",  # No encodedcommand
            mitre_technique="T1059.001",  # PowerShell (+20 behavior)
            severity="Medium"
        )
        boundary_asset = AssetData(
            device_id="WS-TEST-01",
            hostname="WS-TEST-01.corp.acme.com",
            device_type="workstation",
            tags=["standard"],
            owner="test@acme.com",
            department="Testing",
            criticality="standard",
        )

        investigation = await investigation_service.create_investigation(
            incident_id=boundary_alert.incident_id,
            alert=boundary_alert,
            asset=boundary_asset,
        )

        # Build to get exactly 50:
        # Intel: VT > 50 (+30) + malware label (+10) = 40
        # Behavior: T1059.001 (+20), no cmdline pattern = 20
        # Context: Red CTEM (+15), standard = 15
        # Propagation: 1 host (+2) = 2
        # But we want ~50, so:
        # Intel: VT < 50 (0) + no labels (0) = 0
        # Behavior: T1059.001 (+20), no pattern = 20
        # Context: Red CTEM (+15) = 15
        # Propagation: 6+ hosts (+10) = 10
        # But that gives 45... Let's add propagation:
        # Actually: T1059.001 (+20) + Red CTEM (+15) + 6+ hosts (+10) + malware label (+10) = 55

        moderate_intel = IntelData(
            hash_sha256=boundary_alert.hash_sha256,
            verdict="suspicious",
            vt_score=30,  # Not >50, so no +30
            vt_total=72,
            malware_labels=["PUP.Generic"],  # +10
            confidence=50,
        )
        moderate_ctem = CTEMData(
            device_id="WS-TEST-01",
            cve_list=["CVE-2024-9999"],
            risk_color="Red",  # +15
            vulnerability_count=1,
        )
        moderate_propagation = PropagationData(
            hash_sha256=boundary_alert.hash_sha256,
            affected_hosts=["WS-TEST-01", "WS-TEST-02", "WS-TEST-03", "WS-TEST-04", "WS-TEST-05", "WS-TEST-06"],
            affected_count=6,  # +10
        )
        # Total: 10 (intel) + 20 (behavior) + 15 (context) + 10 (propagation) = 55

        enriched = await investigation_service.enrich(
            investigation=investigation,
            intel=moderate_intel,
            ctem=moderate_ctem,
            propagation=moderate_propagation,
        )
        scored = await investigation_service.calculate_confidence(enriched)

        # Act
        evaluated = await investigation_service.evaluate_policy(scored)

        # Assert: At 50+ confidence, should request approval (not mark FP)
        assert scored.confidence_score >= 50, f"Got {scored.confidence_score}, expected >= 50"
        assert evaluated.policy_decision.action.value == "request_approval"
        assert evaluated.policy_decision.requires_approval is True

    @pytest.mark.asyncio
    async def test_unknown_verdict_treated_conservatively(
        self,
        investigation_service,
        scenario3_alert: AlertData,
        scenario3_asset: AssetData,
    ):
        """Test that unknown intel verdict is handled conservatively."""
        # Arrange
        investigation = await investigation_service.create_investigation(
            incident_id=scenario3_alert.incident_id,
            alert=scenario3_alert,
            asset=scenario3_asset,
        )

        # Unknown verdict - never seen before
        unknown_intel = IntelData(
            hash_sha256=scenario3_alert.hash_sha256,
            verdict="unknown",
            vt_score=0,
            vt_total=72,
            malware_labels=[],
            confidence=0,
        )
        clean_ctem = CTEMData(
            device_id="SRV-DEV-03",
            cve_list=[],
            risk_color="Green",
            vulnerability_count=0,
        )
        single_propagation = PropagationData(
            hash_sha256=scenario3_alert.hash_sha256,
            affected_hosts=["SRV-DEV-03"],
            affected_count=1,
        )

        enriched = await investigation_service.enrich(
            investigation=investigation,
            intel=unknown_intel,
            ctem=clean_ctem,
            propagation=single_propagation,
        )
        scored = await investigation_service.calculate_confidence(enriched)

        # Act
        evaluated = await investigation_service.evaluate_policy(scored)

        # Assert: Unknown should result in low confidence (< 50)
        assert scored.confidence_score < 50
        assert evaluated.policy_decision.action.value == "mark_false_positive"

    @pytest.mark.asyncio
    async def test_false_positive_adds_to_allowlist_optionally(
        self,
        investigation_service,
        scenario3_alert: AlertData,
        scenario3_asset: AssetData,
        scenario3_intel: IntelData,
        scenario3_ctem: CTEMData,
        scenario3_propagation: PropagationData,
    ):
        """Test that false positive can optionally add hash to allowlist."""
        # Act: Run investigation with allowlist option
        result = await investigation_service.run_investigation(
            incident_id=scenario3_alert.incident_id,
            alert=scenario3_alert,
            asset=scenario3_asset,
            intel=scenario3_intel,
            ctem=scenario3_ctem,
            propagation=scenario3_propagation,
            options={"add_to_allowlist": True},
        )

        # Assert
        assert result.outcome == ActionOutcome.FALSE_POSITIVE
        assert result.allowlist_entry_created is True
        assert result.allowlist_hash == scenario3_alert.hash_sha256

    @pytest.mark.asyncio
    async def test_repeated_false_positive_suggests_tuning(
        self,
        investigation_service,
        scenario3_alert: AlertData,
        scenario3_asset: AssetData,
        scenario3_intel: IntelData,
        scenario3_ctem: CTEMData,
        scenario3_propagation: PropagationData,
    ):
        """Test that repeated false positives suggest detection tuning."""
        # Arrange: Simulate this being the 3rd false positive for same detection
        # Act
        result = await investigation_service.run_investigation(
            incident_id=scenario3_alert.incident_id,
            alert=scenario3_alert,
            asset=scenario3_asset,
            intel=scenario3_intel,
            ctem=scenario3_ctem,
            propagation=scenario3_propagation,
            context={"previous_fp_count": 2},
        )

        # Assert
        assert result.outcome == ActionOutcome.FALSE_POSITIVE
        assert result.tuning_recommendation is not None
        assert "detection" in result.tuning_recommendation.lower() or "rule" in result.tuning_recommendation.lower()
