"""
Scenario data types for the Dynamic Scenario Data Engine.

DATA-001: PhaseEvents structure (incidents, detections, iocs per phase)
DATA-002: ScenarioState cumulative structure
DATA-006: Agent mutation format
TECH-010: PhaseEvents data structure with SIEM, EDR, Intel event lists
"""

from pydantic import BaseModel, Field
from typing import Any


class SiemIncident(BaseModel):
    """A SIEM incident event within a scenario phase."""

    id: str
    title: str
    severity: str  # low, medium, high, critical
    source: str  # sentinel, crowdstrike, etc.
    mitre_tactic: str
    mitre_technique: str
    description: str = ""
    host_id: str = ""
    timestamp: str = ""
    status: str = "new"


class EdrDetection(BaseModel):
    """An EDR detection event within a scenario phase."""

    id: str
    host_id: str
    process_name: str
    action: str  # detected, blocked, quarantined
    severity: str
    mitre_technique: str
    process_path: str = ""
    parent_process: str = ""
    command_line: str = ""
    sha256: str = ""
    timestamp: str = ""


class IntelIOC(BaseModel):
    """A Threat Intel IOC within a scenario phase."""

    id: str
    type: str  # ip, domain, hash, url
    value: str
    threat_actor: str
    source: str  # recorded-future, mandiant, etc.
    confidence: float = 0.0
    first_seen: str = ""
    last_seen: str = ""
    tags: list[str] = Field(default_factory=list)


class AgentComment(BaseModel):
    """A comment added by the agent during investigation."""

    id: str
    incident_id: str
    content: str
    author: str = "vega-agent"
    timestamp: str = ""


class PhaseEvents(BaseModel):
    """Events that occur during a single scenario phase.

    DATA-001: Contains SIEM incidents, EDR detections, and Intel IOCs per phase.
    """

    phase_number: int
    phase_name: str
    incidents: list[SiemIncident] = Field(default_factory=list)
    detections: list[EdrDetection] = Field(default_factory=list)
    iocs: list[IntelIOC] = Field(default_factory=list)
    mitre_tactic: str = ""
    description: str = ""


class ScenarioState(BaseModel):
    """Cumulative state of an active scenario.

    DATA-002: Holds all accumulated data from phase 1 through current phase,
    plus any agent mutations (containments, closures, comments).
    """

    scenario_id: str
    scenario_name: str
    current_phase: int = 0
    total_phases: int = 0

    # Cumulative event data (grows as phases advance)
    incidents: list[SiemIncident] = Field(default_factory=list)
    detections: list[EdrDetection] = Field(default_factory=list)
    iocs: list[IntelIOC] = Field(default_factory=list)

    # Agent mutations (DATA-006)
    contained_hosts: set[str] = Field(default_factory=set)
    closed_incidents: set[str] = Field(default_factory=set)
    comments: list[AgentComment] = Field(default_factory=list)

    class Config:
        """Pydantic config for ScenarioState."""

        arbitrary_types_allowed = True
