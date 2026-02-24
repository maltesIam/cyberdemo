"""Agent API - Proxies requests to the OpenClaw gateway agent (Vega)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from ..triggers.gateway_client import get_gateway_client, AgentResponse

logger = logging.getLogger(__name__)

router = APIRouter()

SOC_SYSTEM_PROMPT = (
    "You are Vega, a cybersecurity SOC analyst AI assistant integrated into a Security Operations Center demo platform. "
    "You analyze security alerts, investigate IOCs, recommend containment actions, and explain attack techniques. "
    "Keep responses concise (2-4 sentences). Use technical cybersecurity terminology. "
    "Reference MITRE ATT&CK techniques when relevant. Respond in the same language as the user's message."
)


class AgentChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
    system_prompt: Optional[str] = None
    max_tokens: int = 500


class AgentChatResponse(BaseModel):
    content: str
    agent_id: str = "main"
    model: str = ""


class AgentAnalyzeRequest(BaseModel):
    alert_type: str
    description: str
    mitre_tactic: Optional[str] = None
    mitre_technique: Optional[str] = None
    severity: Optional[str] = None
    stage: Optional[int] = None
    scenario: Optional[str] = None


class AgentAnalyzeResponse(BaseModel):
    analysis: str
    agent_id: str = "main"


class AgentStatusResponse(BaseModel):
    connected: bool
    agent_name: str = ""
    gateway_url: str = ""
    error: Optional[str] = None


@router.get("/status")
async def agent_status() -> AgentStatusResponse:
    """Check if the OpenClaw gateway agent is reachable."""
    client = get_gateway_client()
    try:
        response = await client.chat(
            message="Respond with exactly: OK",
            max_tokens=10
        )
        return AgentStatusResponse(
            connected=True,
            agent_name="Vega",
            gateway_url=client.gateway_url,
        )
    except Exception as e:
        return AgentStatusResponse(
            connected=False,
            gateway_url=client.gateway_url,
            error=str(e),
        )


@router.post("/chat")
async def agent_chat(req: AgentChatRequest) -> AgentChatResponse:
    """Send a chat message to the agent and get a response."""
    client = get_gateway_client()
    try:
        prompt = req.system_prompt or SOC_SYSTEM_PROMPT
        message = req.message
        if req.context:
            message = f"{req.message}\n\nContext:\n{req.context}"

        response = await client.chat(
            message=message,
            system_prompt=prompt,
            max_tokens=req.max_tokens,
        )
        return AgentChatResponse(
            content=response.content,
            agent_id=response.agent_id,
            model=response.model,
        )
    except Exception as e:
        logger.error(f"Agent chat error: {e}")
        raise HTTPException(status_code=502, detail=f"Agent unavailable: {e}")


@router.post("/analyze")
async def agent_analyze(req: AgentAnalyzeRequest) -> AgentAnalyzeResponse:
    """Ask the agent to analyze a security event from the simulation."""
    client = get_gateway_client()

    parts = [f"Analyze this security event: {req.description}"]
    if req.alert_type:
        parts.append(f"Alert type: {req.alert_type}")
    if req.mitre_tactic:
        parts.append(f"MITRE ATT&CK Tactic: {req.mitre_tactic}")
    if req.mitre_technique:
        parts.append(f"MITRE ATT&CK Technique: {req.mitre_technique}")
    if req.severity:
        parts.append(f"Severity: {req.severity}")
    if req.scenario:
        parts.append(f"Attack scenario: {req.scenario}")
    if req.stage is not None:
        parts.append(f"Simulation stage: {req.stage}")

    message = "\n".join(parts)

    try:
        response = await client.chat(
            message=message,
            system_prompt=SOC_SYSTEM_PROMPT,
            max_tokens=300,
        )
        return AgentAnalyzeResponse(
            analysis=response.content,
            agent_id=response.agent_id,
        )
    except Exception as e:
        logger.error(f"Agent analyze error: {e}")
        raise HTTPException(status_code=502, detail=f"Agent unavailable: {e}")
