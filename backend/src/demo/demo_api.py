"""Demo API Endpoints.

Provides REST endpoints to trigger and monitor demo scenarios.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

from .demo_runner import get_demo_runner, DemoResult, DemoState

router = APIRouter(tags=["Demo"])


# =============================================================================
# Response Models
# =============================================================================

class ScoreBreakdownModel(BaseModel):
    """Confidence score breakdown."""
    intel: int
    behavior: int
    context: int
    propagation: int


class TimelineEntryModel(BaseModel):
    """Timeline entry for demo result."""
    action: str
    timestamp: str
    details: dict[str, Any]
    actor: str


class ApprovalRequestModel(BaseModel):
    """Approval request details."""
    approval_id: str
    incident_id: str
    action_type: str
    target_id: str
    reason: str
    card_data: dict[str, Any]
    status: str


class DemoResultResponse(BaseModel):
    """Response model for demo case execution."""
    incident_id: str
    outcome: str
    action_type: str
    confidence_score: int
    score_breakdown: Optional[ScoreBreakdownModel] = None

    # Containment
    containment_executed: bool = False
    containment_action_id: Optional[str] = None

    # Approval
    approval_required: bool = False
    approval_request: Optional[ApprovalRequestModel] = None

    # False positive
    false_positive_marked: bool = False
    allowlist_entry_created: bool = False

    # Artifacts
    ticket_id: Optional[str] = None
    postmortem_id: Optional[str] = None

    # Timeline
    timeline: list[TimelineEntryModel] = []

    # Metadata
    started_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None


class RansomwareFieldsModel(BaseModel):
    """Ransomware scenario specific fields."""
    affected_hosts: list[str] = []
    mass_containment: bool = False
    playbook_id: Optional[str] = None
    executive_notified: bool = False


class InsiderThreatFieldsModel(BaseModel):
    """Insider threat scenario specific fields."""
    hr_approval_required: bool = False
    legal_hold_initiated: bool = False
    evidence_preserved: bool = False
    ueba_risk_score: Optional[int] = None


class SupplyChainFieldsModel(BaseModel):
    """Supply chain scenario specific fields."""
    hash_mismatch_detected: bool = False
    vendor_contacted: bool = False
    organizational_hunt_initiated: bool = False
    iocs_blocked: list[str] = []


class AllCasesResponse(BaseModel):
    """Response model for running all demo cases."""
    cases: list[DemoResultResponse]
    total_cases: int
    successful_cases: int
    failed_cases: int


class DemoStatusResponse(BaseModel):
    """Response model for demo status."""
    state: str
    cases_run: int
    last_run: Optional[str] = None
    results: list[dict[str, Any]] = []


# =============================================================================
# Helper Functions
# =============================================================================

def _convert_result_to_response(result: DemoResult) -> DemoResultResponse:
    """Convert DemoResult to API response model."""
    score_breakdown = None
    if result.score_breakdown:
        score_breakdown = ScoreBreakdownModel(
            intel=result.score_breakdown.intel,
            behavior=result.score_breakdown.behavior,
            context=result.score_breakdown.context,
            propagation=result.score_breakdown.propagation,
        )

    approval_request = None
    if result.approval_request:
        approval_request = ApprovalRequestModel(
            approval_id=result.approval_request["approval_id"],
            incident_id=result.approval_request["incident_id"],
            action_type=result.approval_request["action_type"],
            target_id=result.approval_request["target_id"],
            reason=result.approval_request["reason"],
            card_data=result.approval_request["card_data"],
            status=result.approval_request["status"],
        )

    timeline = [
        TimelineEntryModel(
            action=entry["action"],
            timestamp=entry["timestamp"],
            details=entry["details"],
            actor=entry["actor"],
        )
        for entry in result.timeline
    ]

    return DemoResultResponse(
        incident_id=result.incident_id,
        outcome=result.outcome,
        action_type=result.action_type.value,
        confidence_score=result.confidence_score,
        score_breakdown=score_breakdown,
        containment_executed=result.containment_executed,
        containment_action_id=result.containment_action_id,
        approval_required=result.approval_required,
        approval_request=approval_request,
        false_positive_marked=result.false_positive_marked,
        allowlist_entry_created=result.allowlist_entry_created,
        ticket_id=result.ticket_id,
        postmortem_id=result.postmortem_id,
        timeline=timeline,
        started_at=result.started_at.isoformat(),
        completed_at=result.completed_at.isoformat() if result.completed_at else None,
        error=result.error,
    )


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/case/1", response_model=DemoResultResponse)
async def run_case_1():
    """Run Demo Case 1: Auto-containment scenario.

    Scenario: High confidence + non-VIP asset = auto-containment.
    - Incident: INC-ANCHOR-001 - Mimikatz credential theft
    - Asset: WS-FIN-042 (Finance workstation, standard criticality)
    - Expected: Auto-contain, create ticket, create postmortem
    """
    try:
        runner = get_demo_runner()
        result = await runner.run_case_1_auto_containment()
        return _convert_result_to_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/case/2", response_model=DemoResultResponse)
async def run_case_2():
    """Run Demo Case 2: VIP approval scenario.

    Scenario: VIP asset requires human approval.
    - Incident: INC-ANCHOR-002 - Suspicious PowerShell on CFO laptop
    - Asset: LAPTOP-CFO-01 (Executive laptop, VIP tag)
    - Expected: Request approval, do NOT auto-contain
    """
    try:
        runner = get_demo_runner()
        result = await runner.run_case_2_vip_approval()
        return _convert_result_to_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/case/3", response_model=DemoResultResponse)
async def run_case_3():
    """Run Demo Case 3: False positive scenario.

    Scenario: Low confidence + dev server = mark as false positive.
    - Incident: INC-ANCHOR-003 - Process injection on dev server
    - Asset: SRV-DEV-03 (Development server, non-production)
    - Expected: Mark as false positive, do NOT contain
    """
    try:
        runner = get_demo_runner()
        result = await runner.run_case_3_false_positive()
        return _convert_result_to_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/case/4", response_model=DemoResultResponse)
async def run_case_4():
    """Run Demo Case 4: Ransomware multi-host scenario.

    Scenario: Mass encryption detected on 5+ hosts.
    - Incident: INC-ANCHOR-004 - LockBit 3.0 ransomware attack
    - Assets: 6 hosts across Finance, HR, Legal, IT, Executive
    - Expected: Mass containment, executive notification, response playbook
    """
    try:
        runner = get_demo_runner()
        result = await runner.run_case_4_ransomware_multihost()
        return _convert_result_to_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/case/5", response_model=DemoResultResponse)
async def run_case_5():
    """Run Demo Case 5: Insider threat scenario.

    Scenario: Privileged user exfiltrating data.
    - Incident: INC-ANCHOR-005 - Senior IT Admin data exfiltration
    - Asset: WS-IT-ADMIN-042 (privileged workstation)
    - Expected: HR approval required, legal hold, evidence preservation
    """
    try:
        runner = get_demo_runner()
        result = await runner.run_case_5_insider_threat()
        return _convert_result_to_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/case/6", response_model=DemoResultResponse)
async def run_case_6():
    """Run Demo Case 6: Supply chain attack scenario.

    Scenario: Compromised legitimate software.
    - Incident: INC-ANCHOR-006 - Trojanized UpdateHelper.exe
    - Assets: 5 hosts with compromised software
    - Expected: Hash verification, organizational hunt, IOC blocking
    """
    try:
        runner = get_demo_runner()
        result = await runner.run_case_6_supply_chain()
        return _convert_result_to_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/all", response_model=AllCasesResponse)
async def run_all_cases():
    """Run all six demo cases sequentially.

    Runs:
    - Case 1: Auto-containment
    - Case 2: VIP approval
    - Case 3: False positive
    - Case 4: Ransomware multi-host
    - Case 5: Insider threat
    - Case 6: Supply chain attack

    Returns results for all cases.
    """
    try:
        runner = get_demo_runner()
        results = await runner.run_all_cases()

        responses = [_convert_result_to_response(r) for r in results]
        successful = sum(1 for r in results if r.error is None)
        failed = len(results) - successful

        return AllCasesResponse(
            cases=responses,
            total_cases=len(results),
            successful_cases=successful,
            failed_cases=failed,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=DemoStatusResponse)
async def get_demo_status():
    """Get current demo runner status.

    Returns:
    - state: Current state (idle, running, completed, error)
    - cases_run: Number of cases executed
    - last_run: Timestamp of last execution
    - results: Summary of previous results
    """
    try:
        runner = get_demo_runner()
        status = await runner.get_status()

        return DemoStatusResponse(
            state=status["state"],
            cases_run=status["cases_run"],
            last_run=status["last_run"],
            results=status["results"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
