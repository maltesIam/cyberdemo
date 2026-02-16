"""
Asset Generator for CyberDemo.

Generates realistic synthetic asset data representing workstations, servers,
mobile devices, and other endpoints in an enterprise environment.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .constants import (
    ASSET_TAGS,
    ASSET_TYPE_DISTRIBUTION,
    CONTAINMENT_STATUS,
    CRITICALITY_LEVELS,
    CRITICALITY_WEIGHTS,
    CRITICALITY_WEIGHTS_SERVER,
    DEPARTMENTS,
    EDR_AGENT_VERSIONS,
    FIRST_NAMES,
    HOSTNAME_PREFIXES,
    LAST_NAMES,
    NETWORKS,
    OS_BY_TYPE,
    RISK_COLORS,
    SITES,
)


def _generate_mac_address(rng: random.Random) -> str:
    """Generate a random MAC address."""
    return ":".join([f"{rng.randint(0, 255):02x}" for _ in range(6)])


def _generate_ip_address(rng: random.Random, network: str) -> str:
    """Generate a random IP address based on network zone."""
    network_prefixes = {
        "CORP": "10.0",
        "DMZ": "172.16",
        "PROD": "10.1",
        "DEV": "10.2",
        "GUEST": "192.168.100",
        "IOT": "192.168.200",
        "MGMT": "10.255",
    }
    prefix = network_prefixes.get(network, "10.0")

    if prefix.count(".") == 1:
        return f"{prefix}.{rng.randint(1, 254)}.{rng.randint(1, 254)}"
    else:
        return f"{prefix}.{rng.randint(1, 254)}"


def _generate_hostname(
    rng: random.Random,
    asset_type: str,
    index: int
) -> str:
    """Generate a hostname based on asset type."""
    prefixes = HOSTNAME_PREFIXES[asset_type]
    prefix = rng.choice(prefixes)

    # Generate suffix based on prefix type
    if prefix in ["DESKTOP-", "MAC-"]:
        # Windows/Mac style: DESKTOP-XXXXXXX
        suffix = "".join(rng.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=7))
    elif prefix in ["IPHONE-"]:
        suffix = f"{rng.choice(FIRST_NAMES).upper()}"
    else:
        # Server style: SRV-001, WS-NYC-042
        site_code = rng.choice(["NYC", "LON", "TKY", "SYD", "LAX", "CHI"])
        suffix = f"{site_code}-{index:03d}"

    return f"{prefix}{suffix}"


def _generate_owner(rng: random.Random) -> str:
    """Generate a realistic owner name."""
    first = rng.choice(FIRST_NAMES)
    last = rng.choice(LAST_NAMES)
    return f"{first} {last}"


def _weighted_choice(rng: random.Random, weights: Dict[str, int]) -> str:
    """Make a weighted random choice from a dictionary of weights."""
    items = list(weights.keys())
    weight_values = list(weights.values())
    return rng.choices(items, weights=weight_values, k=1)[0]


def _select_asset_type(rng: random.Random) -> str:
    """Select an asset type based on distribution weights."""
    return _weighted_choice(rng, ASSET_TYPE_DISTRIBUTION)


def _select_criticality(rng: random.Random, asset_type: str) -> str:
    """Select criticality level based on asset type."""
    if asset_type == "server":
        return _weighted_choice(rng, CRITICALITY_WEIGHTS_SERVER)
    return _weighted_choice(rng, CRITICALITY_WEIGHTS)


def _generate_tags(
    rng: random.Random,
    asset_type: str,
    criticality: str,
    is_vip: bool
) -> List[str]:
    """Generate appropriate tags for an asset."""
    tags = []

    # VIP tag
    if is_vip:
        tags.append("vip")
        if rng.random() < 0.5:
            tags.append("executive")

    # Server-specific tags
    if asset_type == "server":
        tags.append("server")
        if rng.random() < 0.1:
            tags.append("domain-controller")
        if rng.random() < 0.15:
            tags.append("pci")
        if rng.random() < 0.1:
            tags.append("hipaa")
        if rng.random() < 0.05:
            tags.append("internet-facing")

    # Critical assets get more tags
    if criticality == "critical":
        if "critical-infrastructure" not in tags and rng.random() < 0.3:
            tags.append("critical-infrastructure")

    # Legacy systems
    if rng.random() < 0.05:
        tags.append("legacy")

    return list(set(tags))


def _generate_edr_data(rng: random.Random, asset_type: str) -> Dict:
    """Generate EDR agent data for an asset."""
    # Most endpoints have EDR installed
    has_edr = rng.random() < 0.95 if asset_type != "mobile" else rng.random() < 0.6

    if not has_edr:
        return {
            "agent_version": None,
            "last_seen": None,
            "containment_status": None,
        }

    # Generate last seen time (within last 30 days, most within last day)
    if rng.random() < 0.85:
        hours_ago = rng.randint(0, 24)
    else:
        hours_ago = rng.randint(24, 720)  # Up to 30 days

    last_seen = datetime.now() - timedelta(hours=hours_ago)

    # Containment status (most are normal)
    containment_weights = {
        "normal": 95,
        "contained": 2,
        "lift_pending": 2,
        "isolation_pending": 1,
    }
    containment = _weighted_choice(rng, containment_weights)

    return {
        "agent_version": rng.choice(EDR_AGENT_VERSIONS),
        "last_seen": last_seen.isoformat(),
        "containment_status": containment,
    }


def _generate_ctem_data(rng: random.Random, asset_type: str) -> Dict:
    """Generate CTEM (vulnerability) summary data for an asset."""
    # Servers tend to have more findings
    if asset_type == "server":
        finding_count = rng.randint(0, 50)
    elif asset_type == "workstation":
        finding_count = rng.randint(0, 20)
    else:
        finding_count = rng.randint(0, 10)

    # Risk color based on findings
    if finding_count == 0:
        risk_color = "Green"
    elif finding_count < 5:
        risk_color = rng.choices(["Green", "Yellow"], weights=[70, 30])[0]
    elif finding_count < 15:
        risk_color = rng.choices(["Yellow", "Red"], weights=[60, 40])[0]
    else:
        risk_color = rng.choices(["Yellow", "Red"], weights=[30, 70])[0]

    return {
        "risk_color": risk_color,
        "finding_count": finding_count,
    }


def generate_assets(
    count: int = 1000,
    seed: int = 42
) -> List[Dict]:
    """
    Generate synthetic asset data.

    Args:
        count: Number of assets to generate (default 1000)
        seed: Random seed for reproducibility (default 42)

    Returns:
        List of asset dictionaries with complete asset information

    Example:
        >>> assets = generate_assets(count=100, seed=42)
        >>> len(assets)
        100
        >>> assets[0].keys()
        dict_keys(['asset_id', 'hostname', 'ip', 'mac', 'os', ...])
    """
    rng = random.Random(seed)
    assets = []

    # Calculate VIP count (5-8% of assets)
    vip_count = int(count * rng.uniform(0.05, 0.08))
    vip_indices = set(rng.sample(range(count), vip_count))

    for i in range(count):
        # Select asset type based on distribution
        asset_type = _select_asset_type(rng)

        # Select OS based on asset type
        os_options = OS_BY_TYPE[asset_type]
        os_name, versions = rng.choice(os_options)
        os_version = rng.choice(versions)

        # Select network and site
        network = rng.choice(NETWORKS)
        site = rng.choice(SITES)
        department = rng.choice(DEPARTMENTS)

        # Generate hostname
        hostname = _generate_hostname(rng, asset_type, i)

        # Determine criticality
        criticality = _select_criticality(rng, asset_type)

        # Determine if VIP
        is_vip = i in vip_indices

        # Generate tags
        tags = _generate_tags(rng, asset_type, criticality, is_vip)

        # Generate EDR and CTEM data
        edr_data = _generate_edr_data(rng, asset_type)
        ctem_data = _generate_ctem_data(rng, asset_type)

        asset = {
            "asset_id": f"ASSET-{uuid.UUID(int=rng.getrandbits(128))}",
            "hostname": hostname,
            "ip": _generate_ip_address(rng, network),
            "mac": _generate_mac_address(rng),
            "os": os_name,
            "os_version": os_version,
            "owner": _generate_owner(rng) if asset_type != "server" else None,
            "department": department,
            "site": site,
            "network": network,
            "criticality": criticality,
            "tags": tags,
            "asset_type": asset_type,
            "edr": edr_data,
            "ctem": ctem_data,
        }

        assets.append(asset)

    return assets


def get_assets_by_type(assets: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group assets by their type.

    Args:
        assets: List of asset dictionaries

    Returns:
        Dictionary mapping asset types to lists of assets
    """
    by_type: Dict[str, List[Dict]] = {
        "workstation": [],
        "server": [],
        "mobile": [],
        "other": [],
    }

    for asset in assets:
        asset_type = asset.get("asset_type", "other")
        if asset_type in by_type:
            by_type[asset_type].append(asset)
        else:
            by_type["other"].append(asset)

    return by_type


def get_vip_assets(assets: List[Dict]) -> List[Dict]:
    """
    Get all VIP-tagged assets.

    Args:
        assets: List of asset dictionaries

    Returns:
        List of assets with VIP tag
    """
    return [a for a in assets if "vip" in a.get("tags", [])]


def get_critical_assets(assets: List[Dict]) -> List[Dict]:
    """
    Get all critical-criticality assets.

    Args:
        assets: List of asset dictionaries

    Returns:
        List of assets with critical criticality
    """
    return [a for a in assets if a.get("criticality") == "critical"]


if __name__ == "__main__":
    # Quick test
    assets = generate_assets(count=100, seed=42)
    print(f"Generated {len(assets)} assets")

    by_type = get_assets_by_type(assets)
    for asset_type, type_assets in by_type.items():
        print(f"  {asset_type}: {len(type_assets)}")

    vip_assets = get_vip_assets(assets)
    print(f"VIP assets: {len(vip_assets)} ({len(vip_assets)/len(assets)*100:.1f}%)")

    print("\nSample asset:")
    import json
    print(json.dumps(assets[0], indent=2, default=str))
