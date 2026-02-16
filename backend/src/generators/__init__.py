"""
CyberDemo Synthetic Data Generators.

This package provides generators for creating realistic cybersecurity synthetic
data for demonstration and testing purposes. All generators use seeded random
number generators for reproducibility.

Modules:
    constants: Shared constants (MITRE techniques, templates, anchor IDs)
    gen_assets: Asset generation (workstations, servers, mobile, IoT)
    gen_edr: EDR detection generation
    gen_process_trees: Process tree generation for detections
    gen_intel: Threat intelligence IOC generation
    gen_ctem: CTEM vulnerability finding generation
    gen_siem: SIEM incident generation with correlation

Example usage:
    >>> from generators import (
    ...     generate_assets,
    ...     generate_edr_detections,
    ...     generate_process_trees,
    ...     generate_threat_intel,
    ...     generate_ctem_findings,
    ...     generate_siem_incidents,
    ... )
    >>>
    >>> # Generate all data with consistent seed
    >>> seed = 42
    >>> assets = generate_assets(count=1000, seed=seed)
    >>> detections = generate_edr_detections(count=1000, assets=assets, seed=seed)
    >>> trees = generate_process_trees(detections, seed=seed)
    >>> intel = generate_threat_intel(count=200, seed=seed)
    >>> findings, asset_risks = generate_ctem_findings(assets, seed=seed)
    >>> incidents = generate_siem_incidents(detections, intel, asset_risks, seed=seed)
"""

# Generator functions
from .gen_assets import (
    generate_assets,
    get_assets_by_type,
    get_critical_assets,
    get_vip_assets,
)
from .gen_ctem import (
    generate_ctem_findings,
    get_ctem_stats,
    get_exploitable_findings,
    get_findings_by_asset,
    get_findings_by_severity,
    get_high_risk_assets,
    get_unpatched_findings,
)
from .gen_edr import (
    generate_edr_detections,
    get_anchor_detections,
    get_critical_detections,
    get_detections_by_severity,
    get_detections_by_technique,
)
from .gen_intel import (
    generate_threat_intel,
    get_intel_by_type,
    get_intel_by_verdict,
    get_intel_stats,
    get_malicious_hashes,
    lookup_domain,
    lookup_hash,
    lookup_ip,
)
from .gen_process_trees import (
    flatten_tree,
    generate_process_trees,
    get_deep_trees,
    get_tree_for_detection,
    get_tree_stats,
)
from .gen_siem import (
    generate_siem_incidents,
    get_anchor_incidents,
    get_enriched_incidents,
    get_incident_stats,
    get_incidents_by_severity,
    get_incidents_by_status,
    get_open_incidents,
    get_widespread_incidents,
)

# Constants
from .constants import (
    ANCHOR_DETECTION_IDS,
    ANCHOR_HASHES,
    ANCHOR_INCIDENT_IDS,
    MITRE_TECHNIQUES,
)

__all__ = [
    # Asset generation
    "generate_assets",
    "get_assets_by_type",
    "get_vip_assets",
    "get_critical_assets",
    # EDR detection generation
    "generate_edr_detections",
    "get_detections_by_severity",
    "get_detections_by_technique",
    "get_anchor_detections",
    "get_critical_detections",
    # Process tree generation
    "generate_process_trees",
    "get_tree_for_detection",
    "get_deep_trees",
    "get_tree_stats",
    "flatten_tree",
    # Threat intel generation
    "generate_threat_intel",
    "get_intel_by_verdict",
    "get_intel_by_type",
    "lookup_hash",
    "lookup_ip",
    "lookup_domain",
    "get_malicious_hashes",
    "get_intel_stats",
    # CTEM generation
    "generate_ctem_findings",
    "get_findings_by_severity",
    "get_findings_by_asset",
    "get_exploitable_findings",
    "get_unpatched_findings",
    "get_high_risk_assets",
    "get_ctem_stats",
    # SIEM incident generation
    "generate_siem_incidents",
    "get_incidents_by_severity",
    "get_incidents_by_status",
    "get_anchor_incidents",
    "get_open_incidents",
    "get_enriched_incidents",
    "get_widespread_incidents",
    "get_incident_stats",
    # Constants
    "ANCHOR_DETECTION_IDS",
    "ANCHOR_INCIDENT_IDS",
    "ANCHOR_HASHES",
    "MITRE_TECHNIQUES",
]


def generate_all_data(
    asset_count: int = 1000,
    detection_count: int = 1000,
    intel_count: int = 200,
    seed: int = 42
) -> dict:
    """
    Generate a complete synthetic dataset with all data types.

    This is a convenience function that generates all data types in the
    correct order with proper cross-references.

    Args:
        asset_count: Number of assets to generate (default 1000)
        detection_count: Number of EDR detections to generate (default 1000)
        intel_count: Number of threat intel IOCs to generate (default 200)
        seed: Random seed for reproducibility (default 42)

    Returns:
        Dictionary containing all generated data:
        - assets: List of asset dictionaries
        - detections: List of EDR detection dictionaries
        - process_trees: List of process tree dictionaries
        - intel: List of threat intel IOC dictionaries
        - ctem_findings: List of vulnerability finding dictionaries
        - asset_risks: List of asset risk aggregation dictionaries
        - incidents: List of SIEM incident dictionaries

    Example:
        >>> data = generate_all_data(seed=42)
        >>> print(f"Assets: {len(data['assets'])}")
        >>> print(f"Detections: {len(data['detections'])}")
        >>> print(f"Incidents: {len(data['incidents'])}")
    """
    # Generate assets first
    assets = generate_assets(count=asset_count, seed=seed)

    # Generate EDR detections referencing assets
    detections = generate_edr_detections(
        count=detection_count,
        assets=assets,
        seed=seed
    )

    # Generate process trees for detections
    process_trees = generate_process_trees(detections, seed=seed)

    # Generate threat intel
    intel = generate_threat_intel(count=intel_count, seed=seed)

    # Generate CTEM findings and asset risks
    ctem_findings, asset_risks = generate_ctem_findings(assets, seed=seed)

    # Generate SIEM incidents with enrichment
    incidents = generate_siem_incidents(
        detections=detections,
        intel=intel,
        ctem=asset_risks,
        seed=seed
    )

    return {
        "assets": assets,
        "detections": detections,
        "process_trees": process_trees,
        "intel": intel,
        "ctem_findings": ctem_findings,
        "asset_risks": asset_risks,
        "incidents": incidents,
    }


def get_data_summary(data: dict) -> dict:
    """
    Get a summary of generated data.

    Args:
        data: Dictionary from generate_all_data()

    Returns:
        Dictionary with counts and statistics for each data type
    """
    summary = {
        "counts": {
            "assets": len(data.get("assets", [])),
            "detections": len(data.get("detections", [])),
            "process_trees": len(data.get("process_trees", [])),
            "intel": len(data.get("intel", [])),
            "ctem_findings": len(data.get("ctem_findings", [])),
            "asset_risks": len(data.get("asset_risks", [])),
            "incidents": len(data.get("incidents", [])),
        }
    }

    # Add detailed stats if data exists
    if data.get("assets"):
        by_type = get_assets_by_type(data["assets"])
        summary["asset_distribution"] = {k: len(v) for k, v in by_type.items()}

    if data.get("detections"):
        by_severity = get_detections_by_severity(data["detections"])
        summary["detection_severity"] = {k: len(v) for k, v in by_severity.items()}

    if data.get("intel"):
        summary["intel_stats"] = get_intel_stats(data["intel"])

    if data.get("incidents"):
        summary["incident_stats"] = get_incident_stats(data["incidents"])

    return summary
