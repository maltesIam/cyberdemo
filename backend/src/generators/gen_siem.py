"""
SIEM Incident Generator for CyberDemo.

Generates synthetic SIEM (Security Information and Event Management) incidents
by correlating EDR detections with threat intelligence and CTEM data.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

from .constants import (
    ANCHOR_DETECTION_IDS,
    ANCHOR_HASHES,
    ANCHOR_INCIDENT_IDS,
    INCIDENT_SEVERITY_DISTRIBUTION,
    INCIDENT_STATUS,
    INCIDENT_STATUS_WEIGHTS,
    INCIDENT_TITLE_TEMPLATES,
)


def _weighted_choice(rng: random.Random, weights: Dict[str, int]) -> str:
    """Make a weighted random choice from a dictionary of weights."""
    items = list(weights.keys())
    weight_values = list(weights.values())
    return rng.choices(items, weights=weight_values, k=1)[0]


def _generate_incident_title(rng: random.Random, detections: List[Dict]) -> str:
    """Generate an incident title based on related detections."""
    if not detections:
        return "Security Incident Detected"

    # Get hostname from first detection
    first_detection = detections[0]
    hostname = first_detection.get("device_id", "UNKNOWN")

    # Choose template based on detection characteristics
    template = rng.choice(INCIDENT_TITLE_TEMPLATES)
    return template.replace("{hostname}", hostname)


def _generate_incident_description(
    rng: random.Random,
    detections: List[Dict],
    intel_matches: List[Dict],
    ctem_risk: Optional[str]
) -> str:
    """Generate a detailed incident description."""
    parts = []

    if len(detections) == 1:
        parts.append(f"Single detection triggered this incident.")
    else:
        parts.append(f"This incident correlates {len(detections)} related detections.")

    # Add detection info
    techniques = set()
    for det in detections:
        behavior = det.get("behavior", {})
        technique = behavior.get("technique_id")
        if technique:
            techniques.add(technique)

    if techniques:
        parts.append(f"MITRE techniques observed: {', '.join(sorted(techniques))}.")

    # Add intel context
    if intel_matches:
        malicious_count = sum(1 for i in intel_matches if i.get("verdict") == "malicious")
        if malicious_count > 0:
            parts.append(f"Threat intelligence identified {malicious_count} malicious indicators.")

    # Add CTEM context
    if ctem_risk:
        if ctem_risk == "Red":
            parts.append("Affected assets have high vulnerability exposure.")
        elif ctem_risk == "Yellow":
            parts.append("Affected assets have moderate vulnerability exposure.")

    return " ".join(parts)


def _calculate_incident_severity(
    detections: List[Dict],
    intel_matches: List[Dict],
    ctem_risk: Optional[str]
) -> str:
    """Calculate incident severity based on enrichment data."""
    # Start with highest detection severity
    severity_order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    max_severity = 1

    for det in detections:
        det_severity = severity_order.get(det.get("severity", "Low"), 1)
        max_severity = max(max_severity, det_severity)

    # Boost severity for malicious intel matches
    malicious_intel = sum(1 for i in intel_matches if i.get("verdict") == "malicious")
    if malicious_intel > 0:
        max_severity = min(4, max_severity + 1)

    # Boost severity for high-risk assets
    if ctem_risk == "Red":
        max_severity = min(4, max_severity + 1)

    # Convert back to string
    reverse_order = {4: "Critical", 3: "High", 2: "Medium", 1: "Low"}
    return reverse_order.get(max_severity, "Medium")


def _generate_timestamp(rng: random.Random, base_time: Optional[datetime] = None) -> str:
    """Generate an incident creation timestamp."""
    if base_time is None:
        base_time = datetime.now()

    # Incident created within 30 days
    seconds_back = rng.randint(0, 30 * 24 * 3600)
    timestamp = base_time - timedelta(seconds=seconds_back)
    return timestamp.isoformat()


def _correlate_detections(
    detections: List[Dict],
    rng: random.Random
) -> List[List[Dict]]:
    """
    Group detections into correlated incident groups.

    Correlation rules:
    - Same asset within 1 hour
    - Same technique across assets within 15 minutes
    - Some detections remain standalone
    """
    if not detections:
        return []

    # Sort by timestamp
    sorted_detections = sorted(
        detections,
        key=lambda d: d.get("timestamp", "")
    )

    groups: List[List[Dict]] = []
    used_detection_ids: Set[str] = set()

    for detection in sorted_detections:
        det_id = detection["detection_id"]

        if det_id in used_detection_ids:
            continue

        # Start a new group with this detection
        group = [detection]
        used_detection_ids.add(det_id)

        # Find related detections
        for other in sorted_detections:
            other_id = other["detection_id"]

            if other_id in used_detection_ids:
                continue

            # Same asset correlation
            if detection.get("asset_id") == other.get("asset_id"):
                if rng.random() < 0.7:  # 70% chance to correlate
                    group.append(other)
                    used_detection_ids.add(other_id)
                    continue

            # Same technique correlation
            det_technique = detection.get("behavior", {}).get("technique_id")
            other_technique = other.get("behavior", {}).get("technique_id")

            if det_technique and det_technique == other_technique:
                if rng.random() < 0.3:  # 30% chance to correlate
                    group.append(other)
                    used_detection_ids.add(other_id)

            # Limit group size
            if len(group) >= 5:
                break

        groups.append(group)

    return groups


def _enrich_with_intel(
    detections: List[Dict],
    intel: List[Dict]
) -> List[Dict]:
    """Find threat intel matches for detection file hashes."""
    matches = []

    # Build hash lookup
    intel_by_hash = {
        i["indicator_value"]: i
        for i in intel
        if i.get("indicator_type") == "filehash"
    }

    for detection in detections:
        file_info = detection.get("file", {})
        sha256 = file_info.get("sha256")

        if sha256 and sha256 in intel_by_hash:
            matches.append(intel_by_hash[sha256])

    return matches


def _enrich_with_ctem(
    detections: List[Dict],
    asset_risks: List[Dict]
) -> Optional[str]:
    """Get the worst CTEM risk color for affected assets."""
    # Build asset risk lookup
    risk_by_asset = {r["asset_id"]: r["risk_color"] for r in asset_risks}

    risk_order = {"Red": 3, "Yellow": 2, "Green": 1}
    worst_risk = 0

    for detection in detections:
        asset_id = detection.get("asset_id")
        if asset_id and asset_id in risk_by_asset:
            risk_color = risk_by_asset[asset_id]
            risk_value = risk_order.get(risk_color, 0)
            worst_risk = max(worst_risk, risk_value)

    reverse_order = {3: "Red", 2: "Yellow", 1: "Green"}
    return reverse_order.get(worst_risk)


def _get_unique_assets(detections: List[Dict]) -> List[str]:
    """Get unique asset IDs from detections."""
    return list(set(d.get("asset_id") for d in detections if d.get("asset_id")))


def generate_siem_incidents(
    detections: List[Dict],
    intel: Optional[List[Dict]] = None,
    ctem: Optional[List[Dict]] = None,
    seed: int = 42
) -> List[Dict]:
    """
    Generate SIEM incidents by correlating EDR detections.

    Args:
        detections: List of detection dictionaries from gen_edr
        intel: Optional list of threat intel IOCs from gen_intel
        ctem: Optional list of asset risk dictionaries from gen_ctem
        seed: Random seed for reproducibility (default 42)

    Returns:
        List of incident dictionaries (~650 from 1000 detections)

    Example:
        >>> from gen_edr import generate_edr_detections
        >>> detections = generate_edr_detections(count=1000, seed=42)
        >>> incidents = generate_siem_incidents(detections, seed=42)
        >>> len(incidents)
        ~650
    """
    rng = random.Random(seed)
    incidents = []

    intel = intel or []
    ctem = ctem or []

    # First, create anchor incidents with anchor detections
    anchor_detections = [
        d for d in detections
        if d["detection_id"] in ANCHOR_DETECTION_IDS
    ]

    for i, anchor_id in enumerate(ANCHOR_INCIDENT_IDS):
        if i < len(anchor_detections):
            anchor_det = [anchor_detections[i]]

            # Enrich
            intel_matches = _enrich_with_intel(anchor_det, intel)
            ctem_risk = _enrich_with_ctem(anchor_det, ctem)

            incident = {
                "incident_id": anchor_id,
                "title": _generate_incident_title(rng, anchor_det),
                "description": _generate_incident_description(
                    rng, anchor_det, intel_matches, ctem_risk
                ),
                "severity": "Critical",  # Anchor incidents are critical
                "status": rng.choice(["new", "investigating"]),
                "created_at": _generate_timestamp(rng),
                "related_detections": [d["detection_id"] for d in anchor_det],
                "related_assets": _get_unique_assets(anchor_det),
                "enrichment": {
                    "ctem_risk": ctem_risk,
                    "intel_verdict": "malicious" if intel_matches else None,
                    "org_scope": "single_asset",
                },
            }
            incidents.append(incident)

    # Filter out anchor detections for remaining processing
    remaining_detections = [
        d for d in detections
        if d["detection_id"] not in ANCHOR_DETECTION_IDS
    ]

    # Correlate remaining detections into groups
    groups = _correlate_detections(remaining_detections, rng)

    for group in groups:
        # Enrich
        intel_matches = _enrich_with_intel(group, intel)
        ctem_risk = _enrich_with_ctem(group, ctem)

        # Calculate severity
        severity = _calculate_incident_severity(group, intel_matches, ctem_risk)

        # Determine org scope
        unique_assets = _get_unique_assets(group)
        if len(unique_assets) == 1:
            org_scope = "single_asset"
        elif len(unique_assets) <= 3:
            org_scope = "limited"
        else:
            org_scope = "widespread"

        # Determine status
        status = _weighted_choice(rng, INCIDENT_STATUS_WEIGHTS)

        incident = {
            "incident_id": f"INC-{uuid.UUID(int=rng.getrandbits(128))}",
            "title": _generate_incident_title(rng, group),
            "description": _generate_incident_description(
                rng, group, intel_matches, ctem_risk
            ),
            "severity": severity,
            "status": status,
            "created_at": _generate_timestamp(rng),
            "related_detections": [d["detection_id"] for d in group],
            "related_assets": unique_assets,
            "enrichment": {
                "ctem_risk": ctem_risk,
                "intel_verdict": "malicious" if any(
                    i.get("verdict") == "malicious" for i in intel_matches
                ) else ("suspicious" if intel_matches else None),
                "org_scope": org_scope,
            },
        }

        incidents.append(incident)

    return incidents


def get_incidents_by_severity(incidents: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group incidents by severity level.

    Args:
        incidents: List of incident dictionaries

    Returns:
        Dictionary mapping severity levels to lists of incidents
    """
    by_severity: Dict[str, List[Dict]] = {
        "Critical": [],
        "High": [],
        "Medium": [],
        "Low": [],
    }

    for incident in incidents:
        severity = incident.get("severity", "Medium")
        if severity in by_severity:
            by_severity[severity].append(incident)

    return by_severity


def get_incidents_by_status(incidents: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group incidents by status.

    Args:
        incidents: List of incident dictionaries

    Returns:
        Dictionary mapping statuses to lists of incidents
    """
    by_status: Dict[str, List[Dict]] = {}

    for incident in incidents:
        status = incident.get("status", "new")
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(incident)

    return by_status


def get_anchor_incidents(incidents: List[Dict]) -> List[Dict]:
    """
    Get anchor incidents (fixed test case IDs).

    Args:
        incidents: List of incident dictionaries

    Returns:
        List of anchor incidents
    """
    return [i for i in incidents if i["incident_id"] in ANCHOR_INCIDENT_IDS]


def get_open_incidents(incidents: List[Dict]) -> List[Dict]:
    """
    Get incidents that are new or investigating.

    Args:
        incidents: List of incident dictionaries

    Returns:
        List of open incidents
    """
    open_statuses = {"new", "investigating"}
    return [i for i in incidents if i.get("status") in open_statuses]


def get_enriched_incidents(incidents: List[Dict]) -> List[Dict]:
    """
    Get incidents with threat intel enrichment.

    Args:
        incidents: List of incident dictionaries

    Returns:
        List of incidents with intel verdicts
    """
    return [
        i for i in incidents
        if i.get("enrichment", {}).get("intel_verdict") is not None
    ]


def get_widespread_incidents(incidents: List[Dict]) -> List[Dict]:
    """
    Get incidents affecting multiple assets.

    Args:
        incidents: List of incident dictionaries

    Returns:
        List of widespread incidents
    """
    return [
        i for i in incidents
        if i.get("enrichment", {}).get("org_scope") == "widespread"
    ]


def get_incident_stats(incidents: List[Dict]) -> Dict:
    """
    Get statistics about SIEM incidents.

    Args:
        incidents: List of incident dictionaries

    Returns:
        Dictionary with incident statistics
    """
    by_severity = get_incidents_by_severity(incidents)
    by_status = get_incidents_by_status(incidents)

    # Calculate detection correlation ratio
    total_detections = sum(
        len(i.get("related_detections", []))
        for i in incidents
    )

    return {
        "total_incidents": len(incidents),
        "total_related_detections": total_detections,
        "correlation_ratio": total_detections / len(incidents) if incidents else 0,
        "by_severity": {k: len(v) for k, v in by_severity.items()},
        "by_status": {k: len(v) for k, v in by_status.items()},
        "open_count": len(get_open_incidents(incidents)),
        "enriched_count": len(get_enriched_incidents(incidents)),
        "widespread_count": len(get_widespread_incidents(incidents)),
        "anchor_incidents": len(get_anchor_incidents(incidents)),
    }


if __name__ == "__main__":
    # Quick test
    import json

    # Create mock data
    mock_detections = [
        {
            "detection_id": f"DET-{i:04d}",
            "asset_id": f"ASSET-{i % 100:04d}",
            "device_id": f"DESKTOP-{i:04d}",
            "timestamp": datetime.now().isoformat(),
            "severity": ["Critical", "High", "Medium", "Low"][i % 4],
            "behavior": {"technique_id": f"T{1000 + i % 10}"},
            "file": {"sha256": f"{'0' * 64}"},
        }
        for i in range(100)
    ]

    # Add anchor detections
    for i, anchor_id in enumerate(ANCHOR_DETECTION_IDS):
        mock_detections.append({
            "detection_id": anchor_id,
            "asset_id": f"ASSET-ANCHOR-{i}",
            "device_id": f"DESKTOP-ANCHOR-{i}",
            "timestamp": datetime.now().isoformat(),
            "severity": "Critical",
            "behavior": {"technique_id": "T1059.001"},
            "file": {"sha256": ANCHOR_HASHES[i] if i < len(ANCHOR_HASHES) else "0" * 64},
        })

    incidents = generate_siem_incidents(mock_detections, seed=42)

    print(f"Generated {len(incidents)} incidents from {len(mock_detections)} detections")

    stats = get_incident_stats(incidents)
    print(f"\nStatistics:")
    print(f"  By severity: {stats['by_severity']}")
    print(f"  By status: {stats['by_status']}")
    print(f"  Correlation ratio: {stats['correlation_ratio']:.2f}")
    print(f"  Anchor incidents: {stats['anchor_incidents']}")

    print("\nAnchor incidents:")
    for inc in get_anchor_incidents(incidents):
        print(f"  {inc['incident_id']}: {inc['title']}")

    print("\nSample incident:")
    print(json.dumps(incidents[0], indent=2, default=str))
