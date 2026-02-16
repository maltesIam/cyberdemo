"""Demo Scenario Orchestrator.

Runs the six anchor incident demonstration cases:
- INC-ANCHOR-001: Auto-containment (high confidence, non-VIP)
- INC-ANCHOR-002: VIP approval (VIP asset requiring human approval)
- INC-ANCHOR-003: False positive (low confidence, dev server)
- INC-ANCHOR-004: Ransomware multi-host (mass encryption, coordinated containment)
- INC-ANCHOR-005: Insider threat (privileged user, HR approval required)
- INC-ANCHOR-006: Supply chain attack (compromised software, organizational hunt)
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Any
import uuid

from ..services.policy_engine import PolicyEngine, ActionType, PolicyDecision
from ..services.confidence_score import ConfidenceScoreCalculator, ConfidenceComponents
from ..services.investigation_service import (
    InvestigationService,
    AlertData,
    AssetData,
    IntelData,
    CTEMData,
    PropagationData,
)
from .scenario_ransomware import (
    generate_ransomware_scenario,
    generate_incident_document as ransomware_incident,
    generate_asset_documents as ransomware_assets,
    generate_intel_document as ransomware_intel,
    generate_propagation_document as ransomware_propagation,
    get_response_playbook as ransomware_playbook,
    SCENARIO_ID as RANSOMWARE_SCENARIO_ID,
)
from .scenario_insider_threat import (
    generate_insider_threat_scenario,
    generate_incident_document as insider_incident,
    generate_asset_document as insider_asset,
    generate_ueba_document as insider_ueba,
    get_approval_requirements as insider_approvals,
    get_response_playbook as insider_playbook,
    SCENARIO_ID as INSIDER_SCENARIO_ID,
)
from .scenario_supply_chain import (
    generate_supply_chain_scenario,
    generate_incident_document as supply_chain_incident,
    generate_asset_documents as supply_chain_assets,
    generate_intel_document as supply_chain_intel,
    generate_software_verification_document,
    get_response_playbook as supply_chain_playbook,
    get_hunt_query,
    SCENARIO_ID as SUPPLY_CHAIN_SCENARIO_ID,
)


# =============================================================================
# Enums
# =============================================================================

class DemoState(str, Enum):
    """Demo execution state."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


# =============================================================================
# Result Data Class
# =============================================================================

@dataclass
class DemoResult:
    """Result from a demo scenario execution."""
    incident_id: str
    outcome: str
    action_type: ActionType
    confidence_score: int
    score_breakdown: Optional[ConfidenceComponents] = None

    # Containment
    containment_executed: bool = False
    containment_action_id: Optional[str] = None

    # Approval
    approval_required: bool = False
    approval_request: Optional[dict[str, Any]] = None

    # False positive
    false_positive_marked: bool = False
    allowlist_entry_created: bool = False

    # Artifacts
    ticket_id: Optional[str] = None
    postmortem_id: Optional[str] = None

    # Timeline
    timeline: list[dict[str, Any]] = field(default_factory=list)

    # Metadata
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    # Scenario 4: Ransomware multi-host
    affected_hosts: list[str] = field(default_factory=list)
    mass_containment: bool = False
    playbook_id: Optional[str] = None
    executive_notified: bool = False

    # Scenario 5: Insider threat
    hr_approval_required: bool = False
    legal_hold_initiated: bool = False
    evidence_preserved: bool = False
    ueba_risk_score: Optional[int] = None

    # Scenario 6: Supply chain
    hash_mismatch_detected: bool = False
    vendor_contacted: bool = False
    organizational_hunt_initiated: bool = False
    iocs_blocked: list[str] = field(default_factory=list)


# =============================================================================
# OpenSearch Client Helper
# =============================================================================

async def get_opensearch_client():
    """Get OpenSearch client instance."""
    from ..opensearch.client import get_opensearch_client as _get_client
    return await _get_client()


# =============================================================================
# Demo Runner
# =============================================================================

class DemoRunner:
    """Orchestrator for demo scenario execution."""

    def __init__(self):
        """Initialize the demo runner."""
        self._state = DemoState.IDLE
        self._results: list[DemoResult] = []
        self._last_run: Optional[datetime] = None
        self._cases_run = 0

        # Services
        self._policy_engine = PolicyEngine()
        self._confidence_calculator = ConfidenceScoreCalculator()
        self._investigation_service = InvestigationService()

    # -------------------------------------------------------------------------
    # Case 1: Auto-containment (INC-ANCHOR-001)
    # -------------------------------------------------------------------------

    async def run_case_1_auto_containment(self) -> DemoResult:
        """Run Case 1: Auto-containment scenario.

        Scenario: High confidence + non-VIP asset = auto-containment.
        - Incident: INC-ANCHOR-001 - Mimikatz credential theft
        - Asset: WS-FIN-042 (Finance workstation, standard criticality)
        - Expected: Auto-contain, create ticket, create postmortem
        """
        self._state = DemoState.RUNNING
        incident_id = "INC-ANCHOR-001"

        try:
            # Fetch incident data
            incident = await self._fetch_incident(incident_id)
            asset = await self._fetch_asset(incident["device_id"])

            # Build data objects
            alert = AlertData(
                alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
                incident_id=incident_id,
                hash_sha256=incident["hash_sha256"],
                process_name=incident["process_name"],
                cmdline=incident["cmdline"],
                mitre_technique=incident["mitre_technique"],
                severity=incident["severity"],
            )

            asset_data = AssetData(
                device_id=asset["asset_id"],
                hostname=asset["hostname"],
                device_type=asset["device_type"],
                tags=asset.get("tags", []),
                owner=asset.get("owner", "Unknown"),
                department=asset.get("department", "Unknown"),
                criticality=asset.get("criticality", "standard"),
            )

            # Fetch enrichment data
            intel = await self._fetch_intel(incident["hash_sha256"])
            ctem = await self._fetch_ctem(asset["asset_id"])
            propagation = await self._fetch_propagation(incident["hash_sha256"])

            intel_data = IntelData(
                hash_sha256=intel["hash"],
                verdict=intel["verdict"],
                vt_score=intel["vt_score"],
                vt_total=intel["vt_total"],
                malware_labels=intel.get("malware_labels", []),
                confidence=intel["confidence"],
            )

            ctem_data = CTEMData(
                device_id=ctem["device_id"],
                cve_list=ctem.get("cve_list", []),
                risk_color=ctem["risk_color"],
                vulnerability_count=ctem["vulnerability_count"],
            )

            propagation_data = PropagationData(
                hash_sha256=propagation["hash"],
                affected_hosts=propagation["affected_hosts"],
                affected_count=propagation["affected_count"],
            )

            # Run investigation
            investigation = await self._investigation_service.run_investigation(
                incident_id=incident_id,
                alert=alert,
                asset=asset_data,
                intel=intel_data,
                ctem=ctem_data,
                propagation=propagation_data,
            )

            # Build result
            result = DemoResult(
                incident_id=incident_id,
                outcome=investigation.outcome.value if investigation.outcome else "unknown",
                action_type=investigation.policy_decision.action,
                confidence_score=investigation.confidence_score,
                score_breakdown=investigation.score_breakdown,
                containment_executed=investigation.containment_executed,
                containment_action_id=investigation.containment_action_id,
                approval_required=investigation.policy_decision.requires_approval if investigation.policy_decision else False,
                ticket_id=investigation.ticket_id,
                postmortem_id=investigation.postmortem_id,
                timeline=[
                    {
                        "action": entry.action,
                        "timestamp": entry.timestamp.isoformat(),
                        "details": entry.details,
                        "actor": entry.actor,
                    }
                    for entry in investigation.timeline
                ],
                completed_at=datetime.now(timezone.utc),
            )

            # Persist artifacts to OpenSearch
            await self._persist_demo_artifacts(result, investigation)

            self._results.append(result)
            self._cases_run += 1
            self._last_run = datetime.now(timezone.utc)
            self._state = DemoState.COMPLETED

            return result

        except Exception as e:
            self._state = DemoState.ERROR
            return DemoResult(
                incident_id=incident_id,
                outcome="error",
                action_type=ActionType.REQUEST_APPROVAL,
                confidence_score=0,
                error=str(e),
            )

    # -------------------------------------------------------------------------
    # Case 2: VIP Approval (INC-ANCHOR-002)
    # -------------------------------------------------------------------------

    async def run_case_2_vip_approval(self) -> DemoResult:
        """Run Case 2: VIP approval scenario.

        Scenario: VIP asset requires human approval.
        - Incident: INC-ANCHOR-002 - Suspicious PowerShell on CFO laptop
        - Asset: LAPTOP-CFO-01 (Executive laptop, VIP tag)
        - Expected: Request approval, do NOT auto-contain
        """
        self._state = DemoState.RUNNING
        incident_id = "INC-ANCHOR-002"

        try:
            # Fetch incident data
            incident = await self._fetch_incident(incident_id)
            asset = await self._fetch_asset(incident["device_id"])

            # Build data objects
            alert = AlertData(
                alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
                incident_id=incident_id,
                hash_sha256=incident["hash_sha256"],
                process_name=incident["process_name"],
                cmdline=incident["cmdline"],
                mitre_technique=incident["mitre_technique"],
                severity=incident["severity"],
            )

            asset_data = AssetData(
                device_id=asset["asset_id"],
                hostname=asset["hostname"],
                device_type=asset["device_type"],
                tags=asset.get("tags", []),
                owner=asset.get("owner", "Unknown"),
                department=asset.get("department", "Unknown"),
                criticality=asset.get("criticality", "standard"),
            )

            # Fetch enrichment data
            intel = await self._fetch_intel(incident["hash_sha256"])
            ctem = await self._fetch_ctem(asset["asset_id"])
            propagation = await self._fetch_propagation(incident["hash_sha256"])

            intel_data = IntelData(
                hash_sha256=intel["hash"],
                verdict=intel["verdict"],
                vt_score=intel["vt_score"],
                vt_total=intel["vt_total"],
                malware_labels=intel.get("malware_labels", []),
                confidence=intel["confidence"],
            )

            ctem_data = CTEMData(
                device_id=ctem["device_id"],
                cve_list=ctem.get("cve_list", []),
                risk_color=ctem["risk_color"],
                vulnerability_count=ctem["vulnerability_count"],
            )

            propagation_data = PropagationData(
                hash_sha256=propagation["hash"],
                affected_hosts=propagation["affected_hosts"],
                affected_count=propagation["affected_count"],
            )

            # Run investigation
            investigation = await self._investigation_service.run_investigation(
                incident_id=incident_id,
                alert=alert,
                asset=asset_data,
                intel=intel_data,
                ctem=ctem_data,
                propagation=propagation_data,
            )

            # Build approval request data
            approval_request = None
            if investigation.approval_request:
                approval_request = {
                    "approval_id": investigation.approval_request.approval_id,
                    "incident_id": investigation.approval_request.incident_id,
                    "action_type": investigation.approval_request.action_type,
                    "target_id": investigation.approval_request.target_id,
                    "reason": investigation.approval_request.reason,
                    "card_data": investigation.approval_request.card_data,
                    "status": investigation.approval_request.status,
                }

            # Build result
            result = DemoResult(
                incident_id=incident_id,
                outcome=investigation.outcome.value if investigation.outcome else "unknown",
                action_type=investigation.policy_decision.action,
                confidence_score=investigation.confidence_score,
                score_breakdown=investigation.score_breakdown,
                containment_executed=investigation.containment_executed,
                approval_required=investigation.policy_decision.requires_approval if investigation.policy_decision else True,
                approval_request=approval_request,
                timeline=[
                    {
                        "action": entry.action,
                        "timestamp": entry.timestamp.isoformat(),
                        "details": entry.details,
                        "actor": entry.actor,
                    }
                    for entry in investigation.timeline
                ],
                completed_at=datetime.now(timezone.utc),
            )

            # Persist artifacts to OpenSearch
            await self._persist_demo_artifacts(result, investigation)

            self._results.append(result)
            self._cases_run += 1
            self._last_run = datetime.now(timezone.utc)
            self._state = DemoState.COMPLETED

            return result

        except Exception as e:
            self._state = DemoState.ERROR
            return DemoResult(
                incident_id=incident_id,
                outcome="error",
                action_type=ActionType.REQUEST_APPROVAL,
                confidence_score=0,
                error=str(e),
            )

    # -------------------------------------------------------------------------
    # Case 3: False Positive (INC-ANCHOR-003)
    # -------------------------------------------------------------------------

    async def run_case_3_false_positive(self) -> DemoResult:
        """Run Case 3: False positive scenario.

        Scenario: Low confidence + dev server = mark as false positive.
        - Incident: INC-ANCHOR-003 - Process injection on dev server
        - Asset: SRV-DEV-03 (Development server, non-production)
        - Expected: Mark as false positive, do NOT contain
        """
        self._state = DemoState.RUNNING
        incident_id = "INC-ANCHOR-003"

        try:
            # Fetch incident data
            incident = await self._fetch_incident(incident_id)
            asset = await self._fetch_asset(incident["device_id"])

            # Build data objects
            alert = AlertData(
                alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
                incident_id=incident_id,
                hash_sha256=incident["hash_sha256"],
                process_name=incident["process_name"],
                cmdline=incident["cmdline"],
                mitre_technique=incident["mitre_technique"],
                severity=incident["severity"],
            )

            asset_data = AssetData(
                device_id=asset["asset_id"],
                hostname=asset["hostname"],
                device_type=asset["device_type"],
                tags=asset.get("tags", []),
                owner=asset.get("owner", "Unknown"),
                department=asset.get("department", "Unknown"),
                criticality=asset.get("criticality", "low"),
            )

            # Fetch enrichment data - for false positive, we get benign intel
            intel = await self._fetch_intel(incident["hash_sha256"])
            ctem = await self._fetch_ctem(asset["asset_id"])
            propagation = await self._fetch_propagation(incident["hash_sha256"])

            intel_data = IntelData(
                hash_sha256=intel["hash"],
                verdict=intel["verdict"],
                vt_score=intel["vt_score"],
                vt_total=intel["vt_total"],
                malware_labels=intel.get("malware_labels", []),
                confidence=intel["confidence"],
            )

            ctem_data = CTEMData(
                device_id=ctem["device_id"],
                cve_list=ctem.get("cve_list", []),
                risk_color=ctem["risk_color"],
                vulnerability_count=ctem["vulnerability_count"],
            )

            propagation_data = PropagationData(
                hash_sha256=propagation["hash"],
                affected_hosts=propagation["affected_hosts"],
                affected_count=propagation["affected_count"],
            )

            # Run investigation
            investigation = await self._investigation_service.run_investigation(
                incident_id=incident_id,
                alert=alert,
                asset=asset_data,
                intel=intel_data,
                ctem=ctem_data,
                propagation=propagation_data,
            )

            # Build result
            result = DemoResult(
                incident_id=incident_id,
                outcome=investigation.outcome.value if investigation.outcome else "unknown",
                action_type=investigation.policy_decision.action,
                confidence_score=investigation.confidence_score,
                score_breakdown=investigation.score_breakdown,
                containment_executed=investigation.containment_executed,
                false_positive_marked=investigation.false_positive_marked,
                allowlist_entry_created=investigation.allowlist_entry_created,
                timeline=[
                    {
                        "action": entry.action,
                        "timestamp": entry.timestamp.isoformat(),
                        "details": entry.details,
                        "actor": entry.actor,
                    }
                    for entry in investigation.timeline
                ],
                completed_at=datetime.now(timezone.utc),
            )

            # Persist artifacts to OpenSearch
            await self._persist_demo_artifacts(result, investigation)

            self._results.append(result)
            self._cases_run += 1
            self._last_run = datetime.now(timezone.utc)
            self._state = DemoState.COMPLETED

            return result

        except Exception as e:
            self._state = DemoState.ERROR
            return DemoResult(
                incident_id=incident_id,
                outcome="error",
                action_type=ActionType.MARK_FALSE_POSITIVE,
                confidence_score=0,
                error=str(e),
            )

    # -------------------------------------------------------------------------
    # Case 4: Ransomware Multi-Host (INC-ANCHOR-004)
    # -------------------------------------------------------------------------

    async def run_case_4_ransomware_multihost(self) -> DemoResult:
        """Run Case 4: Ransomware multi-host scenario.

        Scenario: Mass encryption detected on 5+ hosts.
        - Incident: INC-ANCHOR-004 - LockBit 3.0 ransomware attack
        - Assets: 6 hosts across Finance, HR, Legal, IT, Executive
        - Expected: Mass containment, executive notification, response playbook
        """
        self._state = DemoState.RUNNING
        incident_id = RANSOMWARE_SCENARIO_ID

        try:
            # Generate scenario data
            scenario = generate_ransomware_scenario()
            incident = ransomware_incident()
            assets = ransomware_assets()
            intel = ransomware_intel()
            propagation = ransomware_propagation()
            playbook = ransomware_playbook()

            # Build timeline
            timeline = [
                {
                    "action": "initial_detection",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {"host": scenario.affected_hosts[0].hostname},
                    "actor": "system",
                },
                {
                    "action": "hash_hunting",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {"hash": scenario.ransomware_family},
                    "actor": "system",
                },
                {
                    "action": "propagation_detected",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {"affected_count": scenario.affected_count},
                    "actor": "system",
                },
                {
                    "action": "mass_containment_initiated",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {"hosts": [h.asset_id for h in scenario.affected_hosts]},
                    "actor": "system",
                },
                {
                    "action": "executive_notification",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {"channel": "Teams/Slack"},
                    "actor": "system",
                },
                {
                    "action": "playbook_activated",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {"playbook_id": playbook["playbook_id"]},
                    "actor": "system",
                },
            ]

            # Build result
            result = DemoResult(
                incident_id=incident_id,
                outcome="mass_contained",
                action_type=ActionType.CONTAIN,
                confidence_score=99,  # High confidence for known ransomware
                containment_executed=True,
                containment_action_id=f"action-mass-{uuid.uuid4().hex[:8]}",
                ticket_id=f"TKT-{uuid.uuid4().hex[:8].upper()}",
                postmortem_id=f"PM-{uuid.uuid4().hex[:8].upper()}",
                timeline=timeline,
                completed_at=datetime.now(timezone.utc),
                # Ransomware-specific fields
                affected_hosts=[h.asset_id for h in scenario.affected_hosts],
                mass_containment=True,
                playbook_id=playbook["playbook_id"],
                executive_notified=True,
            )

            # Persist artifacts
            await self._persist_ransomware_artifacts(result, scenario, playbook)

            self._results.append(result)
            self._cases_run += 1
            self._last_run = datetime.now(timezone.utc)
            self._state = DemoState.COMPLETED

            return result

        except Exception as e:
            self._state = DemoState.ERROR
            return DemoResult(
                incident_id=incident_id,
                outcome="error",
                action_type=ActionType.CONTAIN,
                confidence_score=0,
                error=str(e),
            )

    # -------------------------------------------------------------------------
    # Case 5: Insider Threat (INC-ANCHOR-005)
    # -------------------------------------------------------------------------

    async def run_case_5_insider_threat(self) -> DemoResult:
        """Run Case 5: Insider threat scenario.

        Scenario: Privileged user exfiltrating data.
        - Incident: INC-ANCHOR-005 - Senior IT Admin data exfiltration
        - Asset: WS-IT-ADMIN-042 (privileged workstation)
        - Expected: HR approval required, legal hold, evidence preservation
        """
        self._state = DemoState.RUNNING
        incident_id = INSIDER_SCENARIO_ID

        try:
            # Generate scenario data
            scenario = generate_insider_threat_scenario()
            incident = insider_incident()
            asset = insider_asset()
            ueba = insider_ueba()
            approvals = insider_approvals()
            playbook = insider_playbook()

            # Build timeline
            timeline = [
                {
                    "action": "anomaly_detected",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {"data_volume_mb": scenario.total_data_transferred_mb},
                    "actor": "system",
                },
                {
                    "action": "ueba_alert",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {"risk_score": scenario.risk_score},
                    "actor": "system",
                },
                {
                    "action": "dlp_violations_detected",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {"violation_count": scenario.dlp_violations_count},
                    "actor": "system",
                },
                {
                    "action": "hr_correlation",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {"flags": scenario.hr_flags},
                    "actor": "system",
                },
                {
                    "action": "hr_approval_requested",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {"required_approvals": [a["role"] for a in approvals["required_approvals"]]},
                    "actor": "system",
                },
                {
                    "action": "legal_hold_initiated",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {"chain_of_custody": True},
                    "actor": "system",
                },
            ]

            # Build approval request
            approval_request = {
                "approval_id": f"APR-{uuid.uuid4().hex[:8].upper()}",
                "incident_id": incident_id,
                "action_type": "account_disable",
                "target_id": scenario.user_id,
                "reason": "Insider threat - data exfiltration detected",
                "card_data": {
                    "user_name": scenario.user_name,
                    "user_title": scenario.user_title,
                    "department": scenario.user_department,
                    "risk_score": scenario.risk_score,
                    "data_transferred_mb": scenario.total_data_transferred_mb,
                    "dlp_violations": scenario.dlp_violations_count,
                    "hr_flags": scenario.hr_flags,
                },
                "status": "pending",
            }

            # Build result
            result = DemoResult(
                incident_id=incident_id,
                outcome="awaiting_hr_approval",
                action_type=ActionType.REQUEST_APPROVAL,
                confidence_score=scenario.risk_score,
                containment_executed=False,  # Not yet - awaiting HR
                approval_required=True,
                approval_request=approval_request,
                timeline=timeline,
                completed_at=datetime.now(timezone.utc),
                # Insider threat-specific fields
                hr_approval_required=True,
                legal_hold_initiated=True,
                evidence_preserved=True,
                ueba_risk_score=scenario.risk_score,
            )

            # Persist artifacts
            await self._persist_insider_threat_artifacts(result, scenario, ueba)

            self._results.append(result)
            self._cases_run += 1
            self._last_run = datetime.now(timezone.utc)
            self._state = DemoState.COMPLETED

            return result

        except Exception as e:
            self._state = DemoState.ERROR
            return DemoResult(
                incident_id=incident_id,
                outcome="error",
                action_type=ActionType.REQUEST_APPROVAL,
                confidence_score=0,
                error=str(e),
            )

    # -------------------------------------------------------------------------
    # Case 6: Supply Chain Attack (INC-ANCHOR-006)
    # -------------------------------------------------------------------------

    async def run_case_6_supply_chain(self) -> DemoResult:
        """Run Case 6: Supply chain attack scenario.

        Scenario: Compromised legitimate software.
        - Incident: INC-ANCHOR-006 - Trojanized UpdateHelper.exe
        - Assets: 5 hosts with compromised software
        - Expected: Hash verification, organizational hunt, IOC blocking
        """
        self._state = DemoState.RUNNING
        incident_id = SUPPLY_CHAIN_SCENARIO_ID

        try:
            # Generate scenario data
            scenario = generate_supply_chain_scenario()
            incident = supply_chain_incident()
            assets = supply_chain_assets()
            intel = supply_chain_intel()
            verification = generate_software_verification_document()
            playbook = supply_chain_playbook()
            hunt = get_hunt_query()

            # Build timeline
            timeline = [
                {
                    "action": "behavioral_anomaly_detected",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {"software": scenario.software_name},
                    "actor": "system",
                },
                {
                    "action": "hash_verification_failed",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {
                        "observed_hash": scenario.compromised_hash,
                        "expected_hash": scenario.legitimate_hash,
                    },
                    "actor": "system",
                },
                {
                    "action": "supply_chain_alert",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {"vendor": scenario.vendor_name},
                    "actor": "system",
                },
                {
                    "action": "organizational_hunt_initiated",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {"hunt_query": hunt["name"]},
                    "actor": "system",
                },
                {
                    "action": "affected_assets_identified",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {"count": scenario.affected_count},
                    "actor": "system",
                },
                {
                    "action": "iocs_blocked",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {
                        "domains": scenario.c2_domains,
                        "ips": scenario.c2_ips,
                    },
                    "actor": "system",
                },
                {
                    "action": "vendor_notified",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {"vendor": scenario.vendor_name},
                    "actor": "system",
                },
            ]

            # Build result
            result = DemoResult(
                incident_id=incident_id,
                outcome="supply_chain_contained",
                action_type=ActionType.CONTAIN,
                confidence_score=88,
                containment_executed=True,
                containment_action_id=f"action-sc-{uuid.uuid4().hex[:8]}",
                ticket_id=f"TKT-{uuid.uuid4().hex[:8].upper()}",
                postmortem_id=f"PM-{uuid.uuid4().hex[:8].upper()}",
                timeline=timeline,
                completed_at=datetime.now(timezone.utc),
                # Supply chain-specific fields
                affected_hosts=[a.asset_id for a in scenario.affected_assets],
                playbook_id=playbook["playbook_id"],
                hash_mismatch_detected=True,
                vendor_contacted=True,
                organizational_hunt_initiated=True,
                iocs_blocked=scenario.c2_domains + scenario.c2_ips,
            )

            # Persist artifacts
            await self._persist_supply_chain_artifacts(result, scenario, verification)

            self._results.append(result)
            self._cases_run += 1
            self._last_run = datetime.now(timezone.utc)
            self._state = DemoState.COMPLETED

            return result

        except Exception as e:
            self._state = DemoState.ERROR
            return DemoResult(
                incident_id=incident_id,
                outcome="error",
                action_type=ActionType.CONTAIN,
                confidence_score=0,
                error=str(e),
            )

    # -------------------------------------------------------------------------
    # Run All Cases
    # -------------------------------------------------------------------------

    async def run_all_cases(self) -> list[DemoResult]:
        """Run all six demo cases sequentially.

        Returns:
            List of DemoResult objects for each case.
        """
        results = []

        # Case 1: Auto-containment
        result_1 = await self.run_case_1_auto_containment()
        results.append(result_1)

        # Case 2: VIP approval
        result_2 = await self.run_case_2_vip_approval()
        results.append(result_2)

        # Case 3: False positive
        result_3 = await self.run_case_3_false_positive()
        results.append(result_3)

        # Case 4: Ransomware multi-host
        result_4 = await self.run_case_4_ransomware_multihost()
        results.append(result_4)

        # Case 5: Insider threat
        result_5 = await self.run_case_5_insider_threat()
        results.append(result_5)

        # Case 6: Supply chain attack
        result_6 = await self.run_case_6_supply_chain()
        results.append(result_6)

        return results

    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    async def get_status(self) -> dict[str, Any]:
        """Get current demo runner status.

        Returns:
            Dictionary with state, cases_run, last_run, and results.
        """
        return {
            "state": self._state.value,
            "cases_run": self._cases_run,
            "last_run": self._last_run.isoformat() if self._last_run else None,
            "results": [
                {
                    "incident_id": r.incident_id,
                    "outcome": r.outcome,
                    "confidence_score": r.confidence_score,
                    "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                }
                for r in self._results
            ],
        }

    # -------------------------------------------------------------------------
    # Data Fetching Helpers
    # -------------------------------------------------------------------------

    async def _fetch_incident(self, incident_id: str) -> dict[str, Any]:
        """Fetch incident data from OpenSearch."""
        client = await get_opensearch_client()

        response = await client.search(
            index="siem-incidents-v1",
            body={"query": {"term": {"incident_id": incident_id}}}
        )

        if response["hits"]["total"]["value"] == 0:
            raise ValueError(f"Incident not found: {incident_id}")

        return response["hits"]["hits"][0]["_source"]

    async def _fetch_asset(self, asset_id: str) -> dict[str, Any]:
        """Fetch asset data from OpenSearch."""
        client = await get_opensearch_client()

        response = await client.search(
            index="assets-inventory-v1",
            body={"query": {"term": {"asset_id": asset_id}}}
        )

        if response["hits"]["total"]["value"] == 0:
            raise ValueError(f"Asset not found: {asset_id}")

        return response["hits"]["hits"][0]["_source"]

    async def _fetch_intel(self, hash_sha256: str) -> dict[str, Any]:
        """Fetch threat intel data from OpenSearch."""
        client = await get_opensearch_client()

        response = await client.search(
            index="intel-indicators-v1",
            body={"query": {"term": {"hash": hash_sha256}}}
        )

        if response["hits"]["total"]["value"] == 0:
            # Return unknown verdict for missing intel
            return {
                "hash": hash_sha256,
                "verdict": "unknown",
                "vt_score": 0,
                "vt_total": 75,
                "malware_labels": [],
                "confidence": 0,
            }

        return response["hits"]["hits"][0]["_source"]

    async def _fetch_ctem(self, device_id: str) -> dict[str, Any]:
        """Fetch CTEM data from OpenSearch."""
        client = await get_opensearch_client()

        response = await client.search(
            index="ctem-exposure-v1",
            body={"query": {"term": {"device_id": device_id}}}
        )

        if response["hits"]["total"]["value"] == 0:
            # Return green risk for missing CTEM data
            return {
                "device_id": device_id,
                "cve_list": [],
                "risk_color": "Green",
                "vulnerability_count": 0,
            }

        return response["hits"]["hits"][0]["_source"]

    async def _fetch_propagation(self, hash_sha256: str) -> dict[str, Any]:
        """Fetch hash propagation data from OpenSearch."""
        client = await get_opensearch_client()

        response = await client.search(
            index="edr-detections-v1",
            body={"query": {"term": {"file.sha256": hash_sha256}}, "size": 100}
        )

        hosts = list(set(
            hit["_source"].get("asset_id")
            for hit in response["hits"]["hits"]
            if hit["_source"].get("asset_id")
        ))

        return {
            "hash": hash_sha256,
            "affected_hosts": hosts,
            "affected_count": len(hosts),
        }

    # -------------------------------------------------------------------------
    # Artifact Persistence
    # -------------------------------------------------------------------------

    async def _persist_demo_artifacts(
        self,
        result: DemoResult,
        investigation: Any,
    ) -> None:
        """Persist demo artifacts to OpenSearch."""
        client = await get_opensearch_client()

        # Persist ticket if created
        if result.ticket_id:
            ticket_doc = {
                "ticket_id": result.ticket_id,
                "incident_id": result.incident_id,
                "title": f"Investigation - {result.incident_id}",
                "priority": "High" if result.outcome == "auto_contained" else "Medium",
                "status": "open",
                "system": "JIRA",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "outcome": result.outcome,
                "confidence_score": result.confidence_score,
            }
            try:
                await client.index(
                    index="tickets-v1",
                    body=ticket_doc,
                    refresh=True
                )
            except Exception:
                pass  # Non-critical

        # Persist postmortem if created
        if result.postmortem_id:
            postmortem_doc = {
                "postmortem_id": result.postmortem_id,
                "incident_id": result.incident_id,
                "title": f"Postmortem - {result.incident_id}",
                "summary": f"Investigation completed with outcome: {result.outcome}",
                "confidence_score": result.confidence_score,
                "action_taken": result.outcome,
                "containment_executed": result.containment_executed,
                "timeline": result.timeline,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            try:
                await client.index(
                    index="postmortems-v1",
                    body=postmortem_doc,
                    refresh=True
                )
            except Exception:
                pass  # Non-critical

        # Persist approval request if created
        if result.approval_request:
            approval_doc = {
                "approval_id": result.approval_request["approval_id"],
                "incident_id": result.incident_id,
                "action_type": result.approval_request["action_type"],
                "target_id": result.approval_request["target_id"],
                "reason": result.approval_request["reason"],
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            try:
                await client.index(
                    index="approvals-v1",
                    body=approval_doc,
                    refresh=True
                )
            except Exception:
                pass  # Non-critical

    async def _persist_ransomware_artifacts(
        self,
        result: DemoResult,
        scenario: Any,
        playbook: dict[str, Any],
    ) -> None:
        """Persist ransomware scenario artifacts to OpenSearch."""
        client = await get_opensearch_client()

        # Persist incident
        incident_doc = {
            "incident_id": result.incident_id,
            "title": f"Ransomware Attack - {scenario.ransomware_family}",
            "severity": "Critical",
            "status": "contained",
            "affected_host_count": len(result.affected_hosts),
            "ransomware_family": scenario.ransomware_family,
            "encrypted_files": scenario.total_encrypted_files,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            await client.index(
                index="siem-incidents-v1",
                body=incident_doc,
                id=result.incident_id,
                refresh=True
            )
        except Exception:
            pass

        # Persist playbook execution
        playbook_doc = {
            "playbook_id": playbook["playbook_id"],
            "incident_id": result.incident_id,
            "name": playbook["name"],
            "status": "executed",
            "steps_completed": len(playbook["steps"]),
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            await client.index(
                index="playbooks-v1",
                body=playbook_doc,
                refresh=True
            )
        except Exception:
            pass

        # Persist mass containment actions
        for host_id in result.affected_hosts:
            action_doc = {
                "action_id": f"action-{uuid.uuid4().hex[:8]}",
                "incident_id": result.incident_id,
                "action_type": "containment",
                "target_id": host_id,
                "status": "completed",
                "mass_action": True,
                "executed_at": datetime.now(timezone.utc).isoformat(),
            }
            try:
                await client.index(
                    index="actions-v1",
                    body=action_doc,
                    refresh=True
                )
            except Exception:
                pass

    async def _persist_insider_threat_artifacts(
        self,
        result: DemoResult,
        scenario: Any,
        ueba: dict[str, Any],
    ) -> None:
        """Persist insider threat scenario artifacts to OpenSearch."""
        client = await get_opensearch_client()

        # Persist incident
        incident_doc = {
            "incident_id": result.incident_id,
            "title": f"Insider Threat - {scenario.user_name}",
            "severity": "Critical",
            "status": "awaiting_approval",
            "user_id": scenario.user_id,
            "risk_score": scenario.risk_score,
            "data_transferred_mb": scenario.total_data_transferred_mb,
            "dlp_violations": scenario.dlp_violations_count,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            await client.index(
                index="siem-incidents-v1",
                body=incident_doc,
                id=result.incident_id,
                refresh=True
            )
        except Exception:
            pass

        # Persist UEBA data
        ueba_doc = {
            "user_id": scenario.user_id,
            "incident_id": result.incident_id,
            **ueba,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            await client.index(
                index="ueba-v1",
                body=ueba_doc,
                refresh=True
            )
        except Exception:
            pass

        # Persist legal hold
        if result.legal_hold_initiated:
            legal_hold_doc = {
                "hold_id": f"LH-{uuid.uuid4().hex[:8].upper()}",
                "incident_id": result.incident_id,
                "user_id": scenario.user_id,
                "status": "active",
                "chain_of_custody": True,
                "initiated_at": datetime.now(timezone.utc).isoformat(),
            }
            try:
                await client.index(
                    index="legal-holds-v1",
                    body=legal_hold_doc,
                    refresh=True
                )
            except Exception:
                pass

    async def _persist_supply_chain_artifacts(
        self,
        result: DemoResult,
        scenario: Any,
        verification: dict[str, Any],
    ) -> None:
        """Persist supply chain scenario artifacts to OpenSearch."""
        client = await get_opensearch_client()

        # Persist incident
        incident_doc = {
            "incident_id": result.incident_id,
            "title": f"Supply Chain Attack - {scenario.software_name}",
            "severity": "Critical",
            "status": "contained",
            "vendor_name": scenario.vendor_name,
            "compromised_version": scenario.compromised_version,
            "affected_host_count": scenario.affected_count,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            await client.index(
                index="siem-incidents-v1",
                body=incident_doc,
                id=result.incident_id,
                refresh=True
            )
        except Exception:
            pass

        # Persist software verification
        verification_doc = {
            "verification_id": f"VER-{uuid.uuid4().hex[:8].upper()}",
            "incident_id": result.incident_id,
            **verification,
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            await client.index(
                index="software-verification-v1",
                body=verification_doc,
                refresh=True
            )
        except Exception:
            pass

        # Persist blocked IOCs
        for ioc in result.iocs_blocked:
            ioc_doc = {
                "ioc_id": f"IOC-{uuid.uuid4().hex[:8].upper()}",
                "incident_id": result.incident_id,
                "value": ioc,
                "type": "domain" if "." in ioc and not ioc.replace(".", "").isdigit() else "ip",
                "status": "blocked",
                "blocked_at": datetime.now(timezone.utc).isoformat(),
            }
            try:
                await client.index(
                    index="iocs-blocked-v1",
                    body=ioc_doc,
                    refresh=True
                )
            except Exception:
                pass


# =============================================================================
# Singleton Instance
# =============================================================================

_demo_runner_instance: Optional[DemoRunner] = None


def get_demo_runner() -> DemoRunner:
    """Get or create the DemoRunner singleton."""
    global _demo_runner_instance
    if _demo_runner_instance is None:
        _demo_runner_instance = DemoRunner()
    return _demo_runner_instance
