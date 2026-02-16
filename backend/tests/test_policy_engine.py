"""Unit tests for Policy Engine."""
import pytest
from src.services.policy_engine import PolicyEngine, ActionType


class TestPolicyEngine:
    """Tests for the deterministic Policy Engine."""

    @pytest.fixture
    def engine(self):
        return PolicyEngine()

    def test_low_confidence_marks_false_positive(self, engine):
        """Test: confidence < 50% → mark as false positive."""
        decision = engine.evaluate(
            confidence_score=22,
            device_tags=[],
            has_approval=False
        )
        assert decision.action == ActionType.MARK_FALSE_POSITIVE
        assert decision.requires_approval is False

    def test_high_confidence_auto_contain(self, engine):
        """Test: confidence >= 90% on non-critical asset → auto-contain."""
        decision = engine.evaluate(
            confidence_score=95,
            device_tags=["standard-user"],
            has_approval=False
        )
        assert decision.action == ActionType.CONTAIN
        assert decision.requires_approval is False

    def test_vip_requires_approval(self, engine):
        """Test: VIP tag without approval → request approval."""
        decision = engine.evaluate(
            confidence_score=95,
            device_tags=["vip", "executive"],
            has_approval=False
        )
        assert decision.action == ActionType.REQUEST_APPROVAL
        assert decision.requires_approval is True

    def test_vip_with_approval_contains(self, engine):
        """Test: VIP tag with approval → contain."""
        decision = engine.evaluate(
            confidence_score=95,
            device_tags=["vip", "executive"],
            has_approval=True
        )
        assert decision.action == ActionType.CONTAIN
        assert decision.requires_approval is False

    def test_server_requires_approval(self, engine):
        """Test: server tag without approval → request approval."""
        decision = engine.evaluate(
            confidence_score=95,
            device_tags=["server"],
            has_approval=False
        )
        assert decision.action == ActionType.REQUEST_APPROVAL
        assert decision.requires_approval is True

    def test_domain_controller_requires_approval(self, engine):
        """Test: domain-controller tag without approval → request approval."""
        decision = engine.evaluate(
            confidence_score=95,
            device_tags=["domain-controller"],
            has_approval=False
        )
        assert decision.action == ActionType.REQUEST_APPROVAL
        assert decision.requires_approval is True

    def test_medium_confidence_requests_approval(self, engine):
        """Test: 50% <= confidence < 90% on non-critical → request approval."""
        decision = engine.evaluate(
            confidence_score=70,
            device_tags=[],
            has_approval=False
        )
        assert decision.action == ActionType.REQUEST_APPROVAL
        assert decision.requires_approval is True

    def test_calculate_confidence_malicious_intel(self, engine):
        """Test confidence calculation with malicious intel."""
        confidence = engine.calculate_confidence(
            intel_verdict="malicious",
            intel_confidence=90,
            propagation_count=3,
            ctem_risk="Red",
            severity="High"
        )
        # Should be high confidence: 36 (intel) + 15 (propagation) + 20 (ctem) + 15 (severity) = 86
        assert confidence >= 80

    def test_calculate_confidence_benign_intel(self, engine):
        """Test confidence calculation with benign intel."""
        confidence = engine.calculate_confidence(
            intel_verdict="benign",
            intel_confidence=90,
            propagation_count=0,
            ctem_risk="Green",
            severity="Low"
        )
        # Should be low confidence: -30 (benign) + 0 + 0 + 5 = -25 → 0
        assert confidence < 20

    # Scenario tests for anchor cases

    def test_scenario_1_auto_containment(self, engine):
        """Scenario 1: Malware on standard workstation → Auto-containment."""
        # WS-FIN-042, standard-user, malicious hash, 95% confidence
        decision = engine.evaluate(
            confidence_score=95,
            device_tags=["standard-user"],
            has_approval=False
        )
        assert decision.action == ActionType.CONTAIN
        assert decision.requires_approval is False

    def test_scenario_2_vip_requires_approval(self, engine):
        """Scenario 2: Malware on VIP laptop → Requires approval."""
        # LAPTOP-CFO-01, vip/executive, malicious hash, 95% confidence
        decision = engine.evaluate(
            confidence_score=95,
            device_tags=["vip", "executive"],
            has_approval=False
        )
        assert decision.action == ActionType.REQUEST_APPROVAL
        assert decision.requires_approval is True

    def test_scenario_3_false_positive(self, engine):
        """Scenario 3: Benign script → False Positive."""
        # SRV-DEV-03, standard, benign hash, 22% confidence
        decision = engine.evaluate(
            confidence_score=22,
            device_tags=["standard"],
            has_approval=False
        )
        assert decision.action == ActionType.MARK_FALSE_POSITIVE
        assert decision.requires_approval is False
