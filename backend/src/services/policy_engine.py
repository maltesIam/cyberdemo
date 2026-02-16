"""Policy Engine - Deterministic decision making for containment actions.

This engine does NOT depend on LLM decisions. It uses hard-coded rules
based on confidence scores and asset criticality tags.
"""
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class ActionType(str, Enum):
    CONTAIN = "contain"
    MARK_FALSE_POSITIVE = "mark_false_positive"
    REQUEST_APPROVAL = "request_approval"


@dataclass
class PolicyDecision:
    action: ActionType
    requires_approval: bool
    reason: str


class PolicyEngine:
    """Deterministic policy engine for SOC containment decisions.

    Rules:
    1. If confidence < 50% → mark as false positive
    2. If asset has critical tags (vip, executive, server, domain-controller) AND no approval → request approval
    3. If asset has critical tags AND has approval → contain
    4. If confidence >= 90% → auto-contain
    5. Otherwise → request approval
    """

    CONFIDENCE_HIGH = 90
    CONFIDENCE_MEDIUM = 50
    CRITICAL_TAGS = {"vip", "executive", "server", "domain-controller"}

    def evaluate(
        self,
        confidence_score: float,
        device_tags: list[str],
        has_approval: bool = False
    ) -> PolicyDecision:
        """Evaluate policy and return decision.

        Args:
            confidence_score: Confidence score from 0-100
            device_tags: Tags associated with the asset
            has_approval: Whether human approval has been granted

        Returns:
            PolicyDecision with action, requires_approval flag, and reason
        """
        device_tags_set = set(device_tags) if device_tags else set()
        is_critical = bool(device_tags_set & self.CRITICAL_TAGS)

        # Rule 1: Low confidence → False Positive
        if confidence_score < self.CONFIDENCE_MEDIUM:
            return PolicyDecision(
                action=ActionType.MARK_FALSE_POSITIVE,
                requires_approval=False,
                reason=f"Confidence score {confidence_score}% is below threshold {self.CONFIDENCE_MEDIUM}%"
            )

        # Rule 2 & 3: Critical asset handling
        if is_critical:
            matched_tags = device_tags_set & self.CRITICAL_TAGS
            if has_approval:
                return PolicyDecision(
                    action=ActionType.CONTAIN,
                    requires_approval=False,
                    reason=f"Critical asset ({matched_tags}) with approval granted"
                )
            return PolicyDecision(
                action=ActionType.REQUEST_APPROVAL,
                requires_approval=True,
                reason=f"Critical asset ({matched_tags}) requires human approval"
            )

        # Rule 4: High confidence → Auto-contain
        if confidence_score >= self.CONFIDENCE_HIGH:
            return PolicyDecision(
                action=ActionType.CONTAIN,
                requires_approval=False,
                reason=f"High confidence {confidence_score}% allows auto-containment"
            )

        # Rule 5: Medium confidence → Request approval
        return PolicyDecision(
            action=ActionType.REQUEST_APPROVAL,
            requires_approval=True,
            reason=f"Medium confidence {confidence_score}% requires human review"
        )

    # Alias for evaluate - used in integration tests for clarity
    def assess(
        self,
        confidence_score: float,
        device_tags: list[str],
        has_approval: bool = False
    ) -> PolicyDecision:
        """Alias for evaluate method - assesses policy and returns decision."""
        return self.evaluate(confidence_score, device_tags, has_approval)

    def calculate_confidence(
        self,
        intel_verdict: str,
        intel_confidence: int,
        propagation_count: int,
        ctem_risk: str,
        severity: str
    ) -> float:
        """Calculate overall confidence score based on enrichment data.

        Args:
            intel_verdict: Threat intel verdict (malicious, suspicious, benign, unknown)
            intel_confidence: Intel source confidence 0-100
            propagation_count: Number of hosts with same hash
            ctem_risk: CTEM risk color (Red, Yellow, Green)
            severity: Detection severity (Critical, High, Medium, Low)

        Returns:
            Confidence score 0-100
        """
        score = 0.0

        # Intel verdict weight (40 points max)
        if intel_verdict == "malicious":
            score += 40 * (intel_confidence / 100)
        elif intel_verdict == "suspicious":
            score += 20 * (intel_confidence / 100)
        elif intel_verdict == "benign":
            score -= 30
        # unknown adds 0

        # Propagation weight (20 points max)
        if propagation_count >= 5:
            score += 20
        elif propagation_count >= 3:
            score += 15
        elif propagation_count >= 1:
            score += 10

        # CTEM risk weight (20 points max)
        if ctem_risk == "Red":
            score += 20
        elif ctem_risk == "Yellow":
            score += 10
        # Green adds 0

        # Severity weight (20 points max)
        severity_weights = {
            "Critical": 20,
            "High": 15,
            "Medium": 10,
            "Low": 5
        }
        score += severity_weights.get(severity, 0)

        # Normalize to 0-100
        return max(0, min(100, score))


# Singleton instance
_policy_engine: Optional[PolicyEngine] = None


def get_policy_engine() -> PolicyEngine:
    """Get or create the policy engine singleton."""
    global _policy_engine
    if _policy_engine is None:
        _policy_engine = PolicyEngine()
    return _policy_engine
