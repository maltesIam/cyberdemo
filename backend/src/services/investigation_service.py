"""
Investigation Service - Orchestrates the complete SOC investigation workflow.

This service coordinates:
1. Investigation initialization
2. Enrichment (Intel, CTEM, Propagation)
3. Confidence scoring
4. Policy evaluation
5. Action execution (containment, approval, false positive)
6. Artifact creation (tickets, postmortems)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Any
import uuid

from .policy_engine import PolicyEngine, PolicyDecision, ActionType
from .confidence_score import ConfidenceScoreCalculator, ConfidenceComponents


# ============================================================================
# Enums and Types
# ============================================================================

class InvestigationState(str, Enum):
    """Investigation workflow states."""
    INITIALIZED = "initialized"
    ENRICHING = "enriching"
    SCORING = "scoring"
    POLICY_EVALUATED = "policy_evaluated"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    COMPLETED = "completed"


class ActionOutcome(str, Enum):
    """Possible outcomes of an investigation."""
    AUTO_CONTAINED = "auto_contained"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"
    CONTAINED_AFTER_APPROVAL = "contained_after_approval"
    FALSE_POSITIVE = "false_positive"
    ESCALATED = "escalated"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class AssetData:
    """Asset information for investigations."""
    device_id: str
    hostname: str
    device_type: str
    tags: list[str]
    owner: str
    department: str
    criticality: str = "standard"


@dataclass
class AlertData:
    """Alert information from EDR/SIEM."""
    alert_id: str
    incident_id: str
    hash_sha256: str
    process_name: str
    cmdline: str
    mitre_technique: str
    severity: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class IntelData:
    """Threat intelligence enrichment data."""
    hash_sha256: str
    verdict: str
    vt_score: int
    vt_total: int
    malware_labels: list[str]
    confidence: int


@dataclass
class CTEMData:
    """Continuous Threat Exposure Management data."""
    device_id: str
    cve_list: list[str]
    risk_color: str
    vulnerability_count: int


@dataclass
class PropagationData:
    """Hash propagation across the environment."""
    hash_sha256: str
    affected_hosts: list[str]
    affected_count: int


@dataclass
class ApprovalRequest:
    """Approval request for human-in-the-loop."""
    approval_id: str
    incident_id: str
    action_type: str
    target_id: str
    reason: str
    card_data: dict[str, Any]
    status: str = "pending"
    decided_by: Optional[str] = None
    decision_notes: Optional[str] = None


@dataclass
class TimelineEntry:
    """Entry in the investigation timeline."""
    action: str
    timestamp: datetime
    details: dict[str, Any]
    actor: str = "system"


@dataclass
class Investigation:
    """Complete investigation state."""
    incident_id: str
    state: InvestigationState
    alert: AlertData
    asset: AssetData

    # Enrichment data
    intel: Optional[IntelData] = None
    ctem: Optional[CTEMData] = None
    propagation: Optional[PropagationData] = None

    # Scoring
    confidence_score: int = 0
    score_breakdown: Optional[ConfidenceComponents] = None

    # Policy
    policy_decision: Optional[PolicyDecision] = None

    # Outcome
    outcome: Optional[ActionOutcome] = None

    # Containment
    containment_executed: bool = False
    containment_action_id: Optional[str] = None

    # Approval
    approval_request: Optional[ApprovalRequest] = None

    # False positive
    false_positive_marked: bool = False
    allowlist_entry_created: bool = False
    allowlist_hash: Optional[str] = None

    # Artifacts
    ticket_id: Optional[str] = None
    ticket_type: Optional[str] = None
    postmortem_id: Optional[str] = None

    # Recommendations
    tuning_recommendation: Optional[str] = None

    # Timeline
    timeline: list[TimelineEntry] = field(default_factory=list)

    def add_timeline_entry(self, action: str, details: dict[str, Any], actor: str = "system"):
        """Add an entry to the investigation timeline."""
        self.timeline.append(TimelineEntry(
            action=action,
            timestamp=datetime.now(timezone.utc),
            details=details,
            actor=actor,
        ))


# ============================================================================
# Investigation Service
# ============================================================================

class InvestigationService:
    """Orchestrates the complete SOC investigation workflow."""

    def __init__(self):
        self._policy_engine = PolicyEngine()
        self._confidence_calculator = ConfidenceScoreCalculator()
        self._investigations: dict[str, Investigation] = {}

    async def create_investigation(
        self,
        incident_id: str,
        alert: AlertData,
        asset: AssetData,
    ) -> Investigation:
        """Create a new investigation."""
        investigation = Investigation(
            incident_id=incident_id,
            state=InvestigationState.INITIALIZED,
            alert=alert,
            asset=asset,
        )

        investigation.add_timeline_entry(
            action="investigation_created",
            details={
                "incident_id": incident_id,
                "device_id": asset.device_id,
                "alert_id": alert.alert_id,
            },
        )

        self._investigations[incident_id] = investigation
        return investigation

    async def enrich(
        self,
        investigation: Investigation,
        intel: IntelData,
        ctem: CTEMData,
        propagation: PropagationData,
    ) -> Investigation:
        """Enrich investigation with threat intel, CTEM, and propagation data."""
        investigation.intel = intel
        investigation.ctem = ctem
        investigation.propagation = propagation
        investigation.state = InvestigationState.ENRICHING

        investigation.add_timeline_entry(
            action="enrichment",
            details={
                "intel_verdict": intel.verdict,
                "vt_score": f"{intel.vt_score}/{intel.vt_total}",
                "ctem_risk": ctem.risk_color,
                "propagation_count": propagation.affected_count,
            },
        )

        return investigation

    async def calculate_confidence(self, investigation: Investigation) -> Investigation:
        """Calculate confidence score based on enrichment data."""
        if not investigation.intel or not investigation.ctem or not investigation.propagation:
            raise ValueError("Investigation must be enriched before calculating confidence")

        # Use the confidence score calculator
        total, components = self._confidence_calculator.calculate(
            vt_score=investigation.intel.vt_score,
            vt_total=investigation.intel.vt_total,
            malware_labels=investigation.intel.malware_labels,
            mitre_technique=investigation.alert.mitre_technique,
            cmdline=investigation.alert.cmdline,
            ctem_risk=investigation.ctem.risk_color,
            asset_criticality=investigation.asset.criticality,
            affected_hosts=investigation.propagation.affected_count,
        )

        investigation.confidence_score = total
        investigation.score_breakdown = components
        investigation.state = InvestigationState.SCORING

        investigation.add_timeline_entry(
            action="scoring",
            details={
                "confidence_score": total,
                "intel_score": components.intel,
                "behavior_score": components.behavior,
                "context_score": components.context,
                "propagation_score": components.propagation,
            },
        )

        return investigation

    async def evaluate_policy(self, investigation: Investigation) -> Investigation:
        """Evaluate policy engine to determine action."""
        decision = self._policy_engine.evaluate(
            confidence_score=investigation.confidence_score,
            device_tags=investigation.asset.tags,
            has_approval=False,
        )

        investigation.policy_decision = decision
        investigation.state = InvestigationState.POLICY_EVALUATED

        investigation.add_timeline_entry(
            action="policy_evaluation",
            details={
                "action": decision.action.value,
                "requires_approval": decision.requires_approval,
                "reason": decision.reason,
            },
        )

        return investigation

    async def run_investigation(
        self,
        incident_id: str,
        alert: AlertData,
        asset: AssetData,
        intel: IntelData,
        ctem: CTEMData,
        propagation: PropagationData,
        options: Optional[dict[str, Any]] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> Investigation:
        """Run the complete investigation workflow."""
        options = options or {}
        context = context or {}

        # Step 1: Create investigation
        investigation = await self.create_investigation(incident_id, alert, asset)

        # Step 2: Enrich
        investigation = await self.enrich(investigation, intel, ctem, propagation)

        # Step 3: Calculate confidence
        investigation = await self.calculate_confidence(investigation)

        # Step 4: Evaluate policy
        investigation = await self.evaluate_policy(investigation)

        # Step 5: Execute based on policy decision
        if investigation.policy_decision.action == ActionType.MARK_FALSE_POSITIVE:
            investigation = await self._handle_false_positive(investigation, options, context)

        elif investigation.policy_decision.action == ActionType.CONTAIN:
            investigation = await self._handle_auto_containment(investigation)

        elif investigation.policy_decision.action == ActionType.REQUEST_APPROVAL:
            investigation = await self._handle_approval_request(investigation)

        return investigation

    async def _handle_false_positive(
        self,
        investigation: Investigation,
        options: dict[str, Any],
        context: dict[str, Any],
    ) -> Investigation:
        """Handle false positive workflow."""
        investigation.false_positive_marked = True
        investigation.outcome = ActionOutcome.FALSE_POSITIVE
        investigation.state = InvestigationState.COMPLETED
        investigation.containment_executed = False

        investigation.add_timeline_entry(
            action="false_positive_marked",
            details={
                "confidence_score": investigation.confidence_score,
                "reason": investigation.policy_decision.reason,
            },
        )

        # Optional: Add to allowlist
        if options.get("add_to_allowlist"):
            investigation.allowlist_entry_created = True
            investigation.allowlist_hash = investigation.alert.hash_sha256
            investigation.add_timeline_entry(
                action="allowlist_entry_created",
                details={"hash": investigation.alert.hash_sha256},
            )

        # Check for repeated false positives
        previous_fp_count = context.get("previous_fp_count", 0)
        if previous_fp_count >= 2:
            investigation.tuning_recommendation = (
                f"This detection has triggered {previous_fp_count + 1} false positives. "
                "Consider tuning the detection rule or adding exceptions."
            )

        return investigation

    async def _handle_auto_containment(self, investigation: Investigation) -> Investigation:
        """Handle auto-containment workflow."""
        # Execute containment
        action_id = f"action-{uuid.uuid4().hex[:8]}"
        investigation.containment_executed = True
        investigation.containment_action_id = action_id
        investigation.outcome = ActionOutcome.AUTO_CONTAINED
        investigation.state = InvestigationState.COMPLETED

        investigation.add_timeline_entry(
            action="containment",
            details={
                "action_id": action_id,
                "device_id": investigation.asset.device_id,
                "type": "auto_containment",
            },
        )

        # Create ticket
        investigation.ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        investigation.ticket_type = "incident"
        investigation.add_timeline_entry(
            action="ticket_created",
            details={"ticket_id": investigation.ticket_id},
        )

        # Create postmortem
        investigation.postmortem_id = f"PM-{uuid.uuid4().hex[:8].upper()}"
        investigation.add_timeline_entry(
            action="postmortem_created",
            details={"postmortem_id": investigation.postmortem_id},
        )

        return investigation

    async def _handle_approval_request(self, investigation: Investigation) -> Investigation:
        """Handle approval request workflow."""
        approval_id = f"APR-{uuid.uuid4().hex[:8].upper()}"

        # Build card data for Teams/Slack adaptive card
        card_data = {
            "device_id": investigation.asset.device_id,
            "hostname": investigation.asset.hostname,
            "owner": investigation.asset.owner,
            "department": investigation.asset.department,
            "confidence_score": investigation.confidence_score,
            "threat_name": investigation.intel.malware_labels[0] if investigation.intel.malware_labels else "Unknown",
            "malware_labels": investigation.intel.malware_labels,
            "vt_score": f"{investigation.intel.vt_score}/{investigation.intel.vt_total}",
            "process_name": investigation.alert.process_name,
            "mitre_technique": investigation.alert.mitre_technique,
            "affected_hosts": investigation.propagation.affected_count,
        }

        investigation.approval_request = ApprovalRequest(
            approval_id=approval_id,
            incident_id=investigation.incident_id,
            action_type="contain",
            target_id=investigation.asset.device_id,
            reason=investigation.policy_decision.reason,
            card_data=card_data,
        )

        investigation.outcome = ActionOutcome.AWAITING_APPROVAL
        investigation.state = InvestigationState.AWAITING_APPROVAL

        investigation.add_timeline_entry(
            action="approval_requested",
            details={
                "approval_id": approval_id,
                "target_id": investigation.asset.device_id,
                "reason": investigation.policy_decision.reason,
            },
        )

        return investigation

    async def process_approval(
        self,
        incident_id: str,
        decision: str,
        decided_by: str,
        notes: Optional[str] = None,
    ) -> Investigation:
        """Process an approval decision."""
        investigation = self._investigations.get(incident_id)
        if not investigation:
            raise ValueError(f"Investigation not found: {incident_id}")

        if investigation.state != InvestigationState.AWAITING_APPROVAL:
            raise ValueError(f"Investigation not awaiting approval: {incident_id}")

        if decision == "approved":
            return await self._handle_approval_granted(investigation, decided_by, notes)
        else:
            return await self._handle_approval_denied(investigation, decided_by, notes)

    async def _handle_approval_granted(
        self,
        investigation: Investigation,
        decided_by: str,
        notes: Optional[str],
    ) -> Investigation:
        """Handle approved decision."""
        investigation.add_timeline_entry(
            action="approval_granted",
            details={
                "decided_by": decided_by,
                "notes": notes,
            },
            actor=decided_by,
        )

        # Execute containment
        action_id = f"action-{uuid.uuid4().hex[:8]}"
        investigation.containment_executed = True
        investigation.containment_action_id = action_id
        investigation.outcome = ActionOutcome.CONTAINED_AFTER_APPROVAL
        investigation.state = InvestigationState.COMPLETED

        investigation.add_timeline_entry(
            action="containment",
            details={
                "action_id": action_id,
                "device_id": investigation.asset.device_id,
                "type": "approved_containment",
            },
        )

        # Create ticket
        investigation.ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        investigation.ticket_type = "incident"
        investigation.add_timeline_entry(
            action="ticket_created",
            details={"ticket_id": investigation.ticket_id},
        )

        # Create postmortem
        investigation.postmortem_id = f"PM-{uuid.uuid4().hex[:8].upper()}"
        investigation.add_timeline_entry(
            action="postmortem_created",
            details={"postmortem_id": investigation.postmortem_id},
        )

        return investigation

    async def _handle_approval_denied(
        self,
        investigation: Investigation,
        decided_by: str,
        notes: Optional[str],
    ) -> Investigation:
        """Handle denied decision."""
        investigation.add_timeline_entry(
            action="approval_denied",
            details={
                "decided_by": decided_by,
                "notes": notes,
            },
            actor=decided_by,
        )

        investigation.containment_executed = False
        investigation.outcome = ActionOutcome.APPROVAL_DENIED
        investigation.state = InvestigationState.COMPLETED

        # Still create a ticket for tracking
        investigation.ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        investigation.ticket_type = "informational"
        investigation.add_timeline_entry(
            action="ticket_created",
            details={
                "ticket_id": investigation.ticket_id,
                "type": "informational",
            },
        )

        return investigation

    async def handle_approval_timeout(
        self,
        incident_id: str,
        timeout_minutes: int,
    ) -> Investigation:
        """Handle approval timeout - escalate."""
        investigation = self._investigations.get(incident_id)
        if not investigation:
            raise ValueError(f"Investigation not found: {incident_id}")

        investigation.add_timeline_entry(
            action="escalation",
            details={
                "reason": f"Approval timeout after {timeout_minutes} minutes",
                "escalation_level": "L2",
            },
        )

        investigation.outcome = ActionOutcome.ESCALATED
        investigation.state = InvestigationState.COMPLETED

        return investigation
