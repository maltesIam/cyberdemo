"""
MITRE ATT&CK API endpoints.

Provides REST API access to MITRE ATT&CK framework data:
- GET /api/v1/mitre/tactics - List all tactics
- GET /api/v1/mitre/techniques/{tactic_id} - List techniques for a tactic

REQ-002-003-002: Implement GET /api/v1/mitre/tactics
REQ-002-003-003: Implement GET /api/v1/mitre/techniques/{tactic_id}
"""
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Path
from pydantic import BaseModel, Field

from src.clients.mitre_attack_client import MitreAttackClient

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Response Models
# ============================================================================


class MitreTacticResponse(BaseModel):
    """Response model for listing MITRE ATT&CK tactics."""

    tactics: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of MITRE ATT&CK tactics with id, name, and description"
    )
    total: int = Field(
        default=0,
        description="Total number of tactics"
    )


class MitreTechniqueResponse(BaseModel):
    """Response model for listing MITRE ATT&CK techniques for a tactic."""

    tactic_id: str = Field(
        description="The MITRE ATT&CK tactic ID (e.g., TA0001)"
    )
    techniques: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of techniques with id, name, description, tactic_id, data_sources"
    )
    total: int = Field(
        default=0,
        description="Total number of techniques for this tactic"
    )


# ============================================================================
# API Endpoints
# ============================================================================


@router.get(
    "/tactics",
    response_model=MitreTacticResponse,
    summary="List all MITRE ATT&CK tactics",
    description="Returns a list of all MITRE ATT&CK tactics with their IDs and names."
)
async def get_tactics() -> MitreTacticResponse:
    """
    Get all MITRE ATT&CK tactics.

    Returns:
        MitreTacticResponse: List of tactics with total count.
    """
    try:
        client = MitreAttackClient()
        tactics = await client.get_tactics()
        return MitreTacticResponse(
            tactics=tactics,
            total=len(tactics)
        )
    except Exception as e:
        logger.error(f"Error fetching MITRE tactics: {e}")
        return MitreTacticResponse(tactics=[], total=0)


@router.get(
    "/techniques/{tactic_id}",
    response_model=MitreTechniqueResponse,
    summary="List techniques for a tactic",
    description="Returns a list of MITRE ATT&CK techniques associated with a specific tactic."
)
async def get_techniques_by_tactic(
    tactic_id: str = Path(
        ...,
        description="The MITRE ATT&CK tactic ID (e.g., TA0001 for Initial Access)",
        examples=["TA0001", "TA0002", "TA0003"]
    )
) -> MitreTechniqueResponse:
    """
    Get techniques for a specific MITRE ATT&CK tactic.

    Args:
        tactic_id: The tactic ID (e.g., TA0001 for Initial Access).

    Returns:
        MitreTechniqueResponse: List of techniques with total count.
    """
    try:
        client = MitreAttackClient()
        techniques = await client.get_techniques(tactic_id=tactic_id)
        return MitreTechniqueResponse(
            tactic_id=tactic_id,
            techniques=techniques,
            total=len(techniques)
        )
    except Exception as e:
        logger.error(f"Error fetching techniques for tactic {tactic_id}: {e}")
        return MitreTechniqueResponse(
            tactic_id=tactic_id,
            techniques=[],
            total=0
        )
