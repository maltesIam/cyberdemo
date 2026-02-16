"""Demo module for SOC Analyst scenario demonstrations."""
from .demo_runner import DemoRunner, DemoResult, DemoState
from .scenario_ransomware import (
    RansomwareScenarioData,
    RansomwareHost,
    generate_ransomware_scenario,
    get_response_playbook as get_ransomware_playbook,
)
from .scenario_insider_threat import (
    InsiderThreatScenarioData,
    DataTransferEvent,
    LocationAnomaly,
    TimeAnomaly,
    generate_insider_threat_scenario,
    get_approval_requirements as get_insider_approvals,
    get_response_playbook as get_insider_playbook,
)
from .scenario_supply_chain import (
    SupplyChainScenarioData,
    AnomalousBehavior,
    AffectedAsset,
    generate_supply_chain_scenario,
    get_response_playbook as get_supply_chain_playbook,
    get_hunt_query,
)

__all__ = [
    # Core demo classes
    "DemoRunner",
    "DemoResult",
    "DemoState",
    # Ransomware scenario
    "RansomwareScenarioData",
    "RansomwareHost",
    "generate_ransomware_scenario",
    "get_ransomware_playbook",
    # Insider threat scenario
    "InsiderThreatScenarioData",
    "DataTransferEvent",
    "LocationAnomaly",
    "TimeAnomaly",
    "generate_insider_threat_scenario",
    "get_insider_approvals",
    "get_insider_playbook",
    # Supply chain scenario
    "SupplyChainScenarioData",
    "AnomalousBehavior",
    "AffectedAsset",
    "generate_supply_chain_scenario",
    "get_supply_chain_playbook",
    "get_hunt_query",
]
