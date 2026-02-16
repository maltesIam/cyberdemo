"""
MCP Data Generation Tools.

Provides tools for generating synthetic cybersecurity data:
- data_generate_assets: Generate synthetic assets
- data_generate_edr_detections: Generate EDR detections
- data_generate_siem_incidents: Generate SIEM incidents
- data_generate_threat_intel: Generate threat intelligence IOCs
- data_generate_ctem_findings: Generate CTEM vulnerability findings
- data_generate_all: Generate all data types with cross-references
- data_reset: Clear all generated data
- data_get_health: Get data generation status
"""

from typing import Any, Dict

from ...generators import (
    generate_assets,
    generate_edr_detections,
    generate_siem_incidents,
    generate_threat_intel,
    generate_ctem_findings,
    generate_all_data,
    get_data_summary,
)


# =============================================================================
# In-Memory Data Store
# =============================================================================

_generated_data: Dict[str, Any] = {
    "assets": [],
    "detections": [],
    "process_trees": [],
    "intel": [],
    "ctem_findings": [],
    "asset_risks": [],
    "incidents": [],
}


def _clear_data() -> None:
    """Clear all generated data."""
    global _generated_data
    _generated_data = {
        "assets": [],
        "detections": [],
        "process_trees": [],
        "intel": [],
        "ctem_findings": [],
        "asset_risks": [],
        "incidents": [],
    }


def _get_data_counts() -> Dict[str, int]:
    """Get counts of all generated data."""
    return {key: len(value) for key, value in _generated_data.items()}


# =============================================================================
# Tool Definitions
# =============================================================================

DATA_TOOLS = [
    {
        "name": "data_generate_assets",
        "description": "Generate synthetic assets (workstations, servers, mobile devices, IoT). Returns asset list with IDs, types, and metadata.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "description": "Number of assets to generate (default: 100)",
                    "default": 100
                },
                "seed": {
                    "type": "integer",
                    "description": "Random seed for reproducibility (default: 42)",
                    "default": 42
                }
            }
        }
    },
    {
        "name": "data_generate_edr_detections",
        "description": "Generate synthetic EDR detections with MITRE techniques, severity levels, and process information.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "description": "Number of detections to generate (default: 100)",
                    "default": 100
                },
                "seed": {
                    "type": "integer",
                    "description": "Random seed for reproducibility (default: 42)",
                    "default": 42
                }
            }
        }
    },
    {
        "name": "data_generate_siem_incidents",
        "description": "Generate synthetic SIEM incidents with correlation to detections, intel, and asset risks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "seed": {
                    "type": "integer",
                    "description": "Random seed for reproducibility (default: 42)",
                    "default": 42
                }
            }
        }
    },
    {
        "name": "data_generate_threat_intel",
        "description": "Generate synthetic threat intelligence IOCs (hashes, IPs, domains) with verdicts and attribution.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "description": "Number of IOCs to generate (default: 200)",
                    "default": 200
                },
                "seed": {
                    "type": "integer",
                    "description": "Random seed for reproducibility (default: 42)",
                    "default": 42
                }
            }
        }
    },
    {
        "name": "data_generate_ctem_findings",
        "description": "Generate synthetic CTEM vulnerability findings with CVEs, severity, and exploitability data.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "seed": {
                    "type": "integer",
                    "description": "Random seed for reproducibility (default: 42)",
                    "default": 42
                }
            }
        }
    },
    {
        "name": "data_generate_all",
        "description": "Generate all data types (assets, detections, incidents, intel, findings) with proper cross-references.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "asset_count": {
                    "type": "integer",
                    "description": "Number of assets to generate (default: 1000)",
                    "default": 1000
                },
                "detection_count": {
                    "type": "integer",
                    "description": "Number of detections to generate (default: 1000)",
                    "default": 1000
                },
                "intel_count": {
                    "type": "integer",
                    "description": "Number of threat intel IOCs to generate (default: 200)",
                    "default": 200
                },
                "seed": {
                    "type": "integer",
                    "description": "Random seed for reproducibility (default: 42)",
                    "default": 42
                }
            }
        }
    },
    {
        "name": "data_reset",
        "description": "Clear all generated synthetic data from memory.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "data_get_health",
        "description": "Get current data generation status and counts.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
]


# =============================================================================
# Tool Handlers
# =============================================================================

async def handle_generate_assets(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Generate synthetic assets."""
    count = arguments.get("count", 100)
    seed = arguments.get("seed", 42)

    assets = generate_assets(count=count, seed=seed)
    _generated_data["assets"] = assets

    return {
        "status": "success",
        "count": len(assets),
        "assets": assets[:10],  # Return first 10 as sample
        "message": f"Generated {len(assets)} assets"
    }


async def handle_generate_edr_detections(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Generate synthetic EDR detections."""
    count = arguments.get("count", 100)
    seed = arguments.get("seed", 42)

    # Use existing assets or generate minimal set
    assets = _generated_data.get("assets") or generate_assets(count=50, seed=seed)
    if not _generated_data.get("assets"):
        _generated_data["assets"] = assets

    detections = generate_edr_detections(count=count, assets=assets, seed=seed)
    _generated_data["detections"] = detections

    return {
        "status": "success",
        "count": len(detections),
        "detections": detections[:5],  # Return first 5 as sample
        "message": f"Generated {len(detections)} EDR detections"
    }


async def handle_generate_siem_incidents(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Generate synthetic SIEM incidents."""
    seed = arguments.get("seed", 42)

    # Ensure we have required data
    if not _generated_data.get("detections"):
        assets = _generated_data.get("assets") or generate_assets(count=50, seed=seed)
        _generated_data["assets"] = assets
        detections = generate_edr_detections(count=50, assets=assets, seed=seed)
        _generated_data["detections"] = detections

    intel = _generated_data.get("intel") or generate_threat_intel(count=50, seed=seed)
    if not _generated_data.get("intel"):
        _generated_data["intel"] = intel

    # Generate CTEM if needed
    if not _generated_data.get("asset_risks"):
        findings, asset_risks = generate_ctem_findings(_generated_data["assets"], seed=seed)
        _generated_data["ctem_findings"] = findings
        _generated_data["asset_risks"] = asset_risks

    incidents = generate_siem_incidents(
        detections=_generated_data["detections"],
        intel=intel,
        ctem=_generated_data["asset_risks"],
        seed=seed
    )
    _generated_data["incidents"] = incidents

    return {
        "status": "success",
        "count": len(incidents),
        "incidents": incidents[:5],  # Return first 5 as sample
        "message": f"Generated {len(incidents)} SIEM incidents"
    }


async def handle_generate_threat_intel(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Generate synthetic threat intelligence IOCs."""
    count = arguments.get("count", 200)
    seed = arguments.get("seed", 42)

    intel = generate_threat_intel(count=count, seed=seed)
    _generated_data["intel"] = intel

    return {
        "status": "success",
        "count": len(intel),
        "intel": intel[:10],  # Return first 10 as sample
        "message": f"Generated {len(intel)} threat intel IOCs"
    }


async def handle_generate_ctem_findings(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Generate synthetic CTEM vulnerability findings."""
    seed = arguments.get("seed", 42)

    # Ensure we have assets
    if not _generated_data.get("assets"):
        assets = generate_assets(count=100, seed=seed)
        _generated_data["assets"] = assets

    findings, asset_risks = generate_ctem_findings(_generated_data["assets"], seed=seed)
    _generated_data["ctem_findings"] = findings
    _generated_data["asset_risks"] = asset_risks

    return {
        "status": "success",
        "findings_count": len(findings),
        "asset_risks_count": len(asset_risks),
        "findings": findings[:5],  # Return first 5 as sample
        "message": f"Generated {len(findings)} CTEM findings for {len(asset_risks)} assets"
    }


async def handle_generate_all(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Generate all data types with proper cross-references."""
    global _generated_data

    asset_count = arguments.get("asset_count", 1000)
    detection_count = arguments.get("detection_count", 1000)
    intel_count = arguments.get("intel_count", 200)
    seed = arguments.get("seed", 42)

    data = generate_all_data(
        asset_count=asset_count,
        detection_count=detection_count,
        intel_count=intel_count,
        seed=seed
    )

    _generated_data = data
    summary = get_data_summary(data)

    return {
        "status": "success",
        "summary": summary["counts"],
        "message": "Generated all synthetic data with cross-references"
    }


async def handle_data_reset(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Clear all generated data."""
    _clear_data()

    return {
        "status": "success",
        "message": "All generated data has been cleared"
    }


async def handle_data_get_health(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get current data generation status."""
    counts = _get_data_counts()

    return {
        "status": "healthy",
        "data_counts": counts,
        "total_records": sum(counts.values())
    }


# =============================================================================
# Handler Registry
# =============================================================================

data_handlers = {
    "data_generate_assets": handle_generate_assets,
    "data_generate_edr_detections": handle_generate_edr_detections,
    "data_generate_siem_incidents": handle_generate_siem_incidents,
    "data_generate_threat_intel": handle_generate_threat_intel,
    "data_generate_ctem_findings": handle_generate_ctem_findings,
    "data_generate_all": handle_generate_all,
    "data_reset": handle_data_reset,
    "data_get_health": handle_data_get_health,
}
