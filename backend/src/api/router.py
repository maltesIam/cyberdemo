"""Main API router aggregating all sub-routers."""
from fastapi import APIRouter

from .health import router as health_router
from .siem import router as siem_router
from .edr import router as edr_router
from .intel import router as intel_router
from .ctem import router as ctem_router
from .assets import router as assets_router
from .approvals import router as approvals_router
from .gen import router as gen_router
from .dashboard import router as dashboard_router
from .postmortems import router as postmortems_router
from .tickets import router as tickets_router
from .timeline import router as timeline_router
from .enrichment import router as enrichment_router
from .soar import router as soar_router
from .graph import router as graph_router
from .collab import router as collab_router
from .notifications import router as notifications_router
from .playbooks import router as playbooks_router
from .config import router as config_router
from .audit import router as audit_router
from .surface import router as surface_router
from .vulnerabilities import router as vulnerabilities_router
from .vuln_visualization import router as vuln_visualization_router
from .vuln_enrichment import router as vuln_enrichment_router
from .vuln_ssvc import router as vuln_ssvc_router
from .threats import router as threats_router
from ..mcp import mcp_router
from ..mcp.data_server import router as data_mcp_router
from ..demo.demo_api import router as demo_router

api_router = APIRouter()

# Include all sub-routers
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(siem_router, prefix="/siem", tags=["siem"])
api_router.include_router(edr_router, prefix="/edr", tags=["edr"])
api_router.include_router(intel_router, prefix="/intel", tags=["intel"])
api_router.include_router(ctem_router, prefix="/ctem", tags=["ctem"])
api_router.include_router(assets_router, prefix="/assets", tags=["assets"])
api_router.include_router(approvals_router, prefix="/approvals", tags=["approvals"])
api_router.include_router(gen_router, prefix="/gen", tags=["generation"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(postmortems_router, prefix="/postmortems", tags=["postmortems"])
api_router.include_router(tickets_router, prefix="/tickets", tags=["tickets"])
api_router.include_router(timeline_router, prefix="/agent-actions", tags=["timeline"])
api_router.include_router(enrichment_router, prefix="/api", tags=["enrichment"])
api_router.include_router(soar_router, prefix="/soar", tags=["soar"])
api_router.include_router(graph_router, prefix="/graph", tags=["graph"])
api_router.include_router(collab_router, prefix="/collab", tags=["collaboration"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
api_router.include_router(playbooks_router, prefix="/playbooks", tags=["playbooks"])
api_router.include_router(config_router, prefix="/config", tags=["configuration"])
api_router.include_router(audit_router, prefix="/audit", tags=["audit"])
api_router.include_router(surface_router, prefix="/surface", tags=["surface"])
api_router.include_router(vulnerabilities_router, prefix="/vulnerabilities", tags=["vulnerabilities"])
api_router.include_router(vuln_visualization_router, prefix="/api/vulnerabilities", tags=["vulnerability-visualization"])
api_router.include_router(vuln_enrichment_router, prefix="/api", tags=["vulnerability-enrichment"])
api_router.include_router(vuln_ssvc_router, prefix="/vulnerabilities", tags=["vulnerabilities-ssvc"])
api_router.include_router(threats_router, prefix="/threats", tags=["threats"])
api_router.include_router(mcp_router, prefix="/mcp", tags=["mcp"])
api_router.include_router(data_mcp_router, prefix="/data-mcp", tags=["data-mcp"])
api_router.include_router(demo_router, prefix="/demo", tags=["demo"])
