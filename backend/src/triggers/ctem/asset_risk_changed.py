"""Trigger handler for asset risk level changes."""

from typing import Optional
from ..base import BaseTriggerHandler, TriggerEvent
from ..gateway_client import GatewayClient


class AssetRiskChangedTrigger(BaseTriggerHandler):
    """Trigger that fires when an asset's risk level changes to Red.

    This trigger monitors for significant risk level increases that
    indicate an asset requires immediate attention.
    """

    # Risk level that triggers action
    CRITICAL_RISK_LEVEL = "Red"

    def __init__(self, gateway_client: Optional[GatewayClient] = None):
        super().__init__(gateway_client)

    @property
    def trigger_name(self) -> str:
        return "asset_risk_changed"

    @property
    def description(self) -> str:
        return "Triggers when an asset's risk level changes to Red (critical)"

    @property
    def event_types(self) -> list[str]:
        return ["ctem.asset.risk_changed"]

    def should_trigger(self, event: TriggerEvent) -> bool:
        """Check if the new risk level is Red."""
        data = event.data

        new_risk = data.get("new_risk", "").capitalize()
        if new_risk != self.CRITICAL_RISK_LEVEL:
            return False

        return True

    def get_command(self, event: TriggerEvent) -> str:
        """Generate the /assess-vuln command for the asset."""
        asset_id = event.data.get("asset_id", "unknown")
        asset_name = event.data.get("asset_name", "unknown")
        risk_factors = event.data.get("risk_factors", [])

        factors_str = ",".join(risk_factors) if risk_factors else "unknown"
        return f"/assess-vuln asset:{asset_id} --name '{asset_name}' --factors {factors_str}"
