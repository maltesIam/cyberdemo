"""CTEM-related trigger handlers."""

from .critical_vulnerability import CriticalVulnerabilityTrigger
from .asset_risk_changed import AssetRiskChangedTrigger
from .vip_asset_vulnerability import VIPAssetVulnerabilityTrigger
from .exploit_available import ExploitAvailableTrigger

__all__ = [
    "CriticalVulnerabilityTrigger",
    "AssetRiskChangedTrigger",
    "VIPAssetVulnerabilityTrigger",
    "ExploitAvailableTrigger",
]
