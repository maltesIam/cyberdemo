"""
CTEM (Continuous Threat Exposure Management) Generator for CyberDemo.

Generates synthetic vulnerability findings with CVE data and calculates
aggregated risk scores per asset.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from .constants import (
    CVE_PREFIXES,
    CVE_SEVERITY_DISTRIBUTION,
    RISK_COLORS,
    VULNERABILITY_TITLES,
    VULNERABLE_PRODUCTS,
)


def _weighted_choice(rng: random.Random, weights: Dict[str, int]) -> str:
    """Make a weighted random choice from a dictionary of weights."""
    items = list(weights.keys())
    weight_values = list(weights.values())
    return rng.choices(items, weights=weight_values, k=1)[0]


def _generate_cve_id(rng: random.Random) -> str:
    """Generate a realistic CVE ID."""
    year = rng.choice(CVE_PREFIXES)
    number = rng.randint(10000, 99999)
    return f"CVE-{year}-{number}"


def _generate_cvss_score(rng: random.Random, severity: str) -> float:
    """Generate a CVSS score based on severity."""
    ranges = {
        "Critical": (9.0, 10.0),
        "High": (7.0, 8.9),
        "Medium": (4.0, 6.9),
        "Low": (0.1, 3.9),
    }

    min_score, max_score = ranges.get(severity, (4.0, 6.9))
    return round(rng.uniform(min_score, max_score), 1)


def _generate_vulnerability_title(rng: random.Random) -> Tuple[str, str]:
    """Generate a vulnerability title and affected product."""
    product = rng.choice(VULNERABLE_PRODUCTS)
    title_template = rng.choice(VULNERABILITY_TITLES)
    title = title_template.replace("{product}", product)
    return title, product


def _generate_discovery_date(rng: random.Random) -> str:
    """Generate a discovery date."""
    now = datetime.now()
    days_ago = rng.randint(1, 365)
    discovery = now - timedelta(days=days_ago)
    return discovery.isoformat()


def _generate_remediation_status(rng: random.Random, severity: str) -> str:
    """Generate remediation status based on severity."""
    statuses = ["open", "in_progress", "remediated", "accepted_risk", "false_positive"]

    # Critical findings are more likely to be addressed
    if severity == "Critical":
        weights = [30, 40, 20, 5, 5]
    elif severity == "High":
        weights = [35, 35, 20, 7, 3]
    elif severity == "Medium":
        weights = [40, 25, 20, 10, 5]
    else:  # Low
        weights = [50, 15, 15, 15, 5]

    return rng.choices(statuses, weights=weights)[0]


def _calculate_finding_count_for_asset(
    rng: random.Random,
    asset_type: str,
    criticality: str
) -> int:
    """Calculate how many findings an asset should have."""
    # Base counts by asset type
    base_counts = {
        "server": (2, 15),
        "workstation": (0, 8),
        "mobile": (0, 3),
        "other": (0, 5),
    }

    min_count, max_count = base_counts.get(asset_type, (0, 5))

    # Critical assets tend to have more findings (they're scanned more)
    if criticality in ["critical", "high"]:
        max_count = int(max_count * 1.5)

    return rng.randint(min_count, max_count)


def _calculate_asset_risk(findings: List[Dict]) -> str:
    """
    Calculate aggregated risk color for an asset based on its findings.

    Returns:
        Risk color: "Green", "Yellow", or "Red"
    """
    if not findings:
        return "Green"

    # Count open findings by severity
    open_findings = [f for f in findings if f.get("remediation_status") in ["open", "in_progress"]]

    if not open_findings:
        return "Green"

    critical_count = sum(1 for f in open_findings if f.get("severity") == "Critical")
    high_count = sum(1 for f in open_findings if f.get("severity") == "High")
    medium_count = sum(1 for f in open_findings if f.get("severity") == "Medium")

    # Risk calculation logic
    if critical_count >= 1:
        return "Red"
    elif high_count >= 3:
        return "Red"
    elif high_count >= 1:
        return "Yellow"
    elif medium_count >= 5:
        return "Yellow"
    elif medium_count >= 2:
        return "Yellow"
    else:
        return "Green"


def generate_ctem_findings(
    assets: List[Dict],
    seed: int = 42
) -> Tuple[List[Dict], List[Dict]]:
    """
    Generate CTEM vulnerability findings for assets.

    Args:
        assets: List of asset dictionaries from gen_assets
        seed: Random seed for reproducibility (default 42)

    Returns:
        Tuple of (findings, asset_risks):
        - findings: List of vulnerability finding dictionaries (~3000 total)
        - asset_risks: List of asset risk aggregation dictionaries

    Example:
        >>> from gen_assets import generate_assets
        >>> assets = generate_assets(count=100, seed=42)
        >>> findings, risks = generate_ctem_findings(assets, seed=42)
        >>> len(findings)
        ~300 (depends on asset distribution)
        >>> risks[0].keys()
        dict_keys(['asset_id', 'hostname', 'risk_color', 'finding_count', ...])
    """
    rng = random.Random(seed)
    all_findings = []
    asset_risks = []

    # Track generated CVEs to allow some reuse (same vuln on multiple assets)
    cve_cache = []

    for asset in assets:
        asset_id = asset["asset_id"]
        hostname = asset.get("hostname", "UNKNOWN")
        asset_type = asset.get("asset_type", "workstation")
        criticality = asset.get("criticality", "medium")

        # Determine finding count for this asset
        finding_count = _calculate_finding_count_for_asset(rng, asset_type, criticality)

        asset_findings = []

        for _ in range(finding_count):
            # Sometimes reuse an existing CVE (same vuln affects multiple systems)
            if cve_cache and rng.random() < 0.3:
                cached = rng.choice(cve_cache)
                cve_id = cached["cve_id"]
                title = cached["title"]
                product = cached["product"]
                severity = cached["severity"]
                cvss = cached["cvss"]
            else:
                # Generate new vulnerability
                # Servers skew toward higher severity
                if asset_type == "server":
                    severity_weights = {
                        "Critical": 15,
                        "High": 30,
                        "Medium": 35,
                        "Low": 20,
                    }
                else:
                    severity_weights = CVE_SEVERITY_DISTRIBUTION

                severity = _weighted_choice(rng, severity_weights)
                cve_id = _generate_cve_id(rng)
                title, product = _generate_vulnerability_title(rng)
                cvss = _generate_cvss_score(rng, severity)

                # Cache for potential reuse
                cve_cache.append({
                    "cve_id": cve_id,
                    "title": title,
                    "product": product,
                    "severity": severity,
                    "cvss": cvss,
                })

            finding = {
                "finding_id": f"FIND-{uuid.UUID(int=rng.getrandbits(128))}",
                "asset_id": asset_id,
                "hostname": hostname,
                "cve_id": cve_id,
                "title": title,
                "product": product,
                "severity": severity,
                "cvss_score": cvss,
                "cvss_vector": _generate_cvss_vector(rng, severity),
                "remediation_status": _generate_remediation_status(rng, severity),
                "discovered_at": _generate_discovery_date(rng),
                "exploit_available": rng.random() < 0.15,  # 15% have known exploits
                "patch_available": rng.random() < 0.85,  # 85% have patches
            }

            asset_findings.append(finding)
            all_findings.append(finding)

        # Calculate risk for this asset
        risk_color = _calculate_asset_risk(asset_findings)

        # Count by severity
        severity_counts = {
            "critical": sum(1 for f in asset_findings if f["severity"] == "Critical"),
            "high": sum(1 for f in asset_findings if f["severity"] == "High"),
            "medium": sum(1 for f in asset_findings if f["severity"] == "Medium"),
            "low": sum(1 for f in asset_findings if f["severity"] == "Low"),
        }

        asset_risk = {
            "asset_id": asset_id,
            "hostname": hostname,
            "risk_color": risk_color,
            "finding_count": len(asset_findings),
            "severity_counts": severity_counts,
            "open_findings": sum(
                1 for f in asset_findings
                if f["remediation_status"] in ["open", "in_progress"]
            ),
            "remediated_findings": sum(
                1 for f in asset_findings
                if f["remediation_status"] == "remediated"
            ),
        }

        asset_risks.append(asset_risk)

    return all_findings, asset_risks


def _generate_cvss_vector(rng: random.Random, severity: str) -> str:
    """Generate a CVSS v3.1 vector string."""
    # Attack Vector
    av = rng.choice(["N", "A", "L", "P"])  # Network, Adjacent, Local, Physical

    # Attack Complexity
    ac = rng.choice(["L", "H"])  # Low, High

    # Privileges Required
    pr = rng.choice(["N", "L", "H"])  # None, Low, High

    # User Interaction
    ui = rng.choice(["N", "R"])  # None, Required

    # Scope
    s = rng.choice(["U", "C"])  # Unchanged, Changed

    # Impact (C/I/A)
    if severity == "Critical":
        impacts = ["H", "H", "H"]
    elif severity == "High":
        impacts = rng.choices(["H", "L", "N"], k=3)
        impacts[0] = "H"  # At least one High
    else:
        impacts = rng.choices(["L", "N"], k=3)

    return f"CVSS:3.1/AV:{av}/AC:{ac}/PR:{pr}/UI:{ui}/S:{s}/C:{impacts[0]}/I:{impacts[1]}/A:{impacts[2]}"


def get_findings_by_severity(findings: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group findings by severity level.

    Args:
        findings: List of finding dictionaries

    Returns:
        Dictionary mapping severity levels to lists of findings
    """
    by_severity: Dict[str, List[Dict]] = {
        "Critical": [],
        "High": [],
        "Medium": [],
        "Low": [],
    }

    for finding in findings:
        severity = finding.get("severity", "Medium")
        if severity in by_severity:
            by_severity[severity].append(finding)

    return by_severity


def get_findings_by_asset(findings: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group findings by asset ID.

    Args:
        findings: List of finding dictionaries

    Returns:
        Dictionary mapping asset IDs to lists of findings
    """
    by_asset: Dict[str, List[Dict]] = {}

    for finding in findings:
        asset_id = finding.get("asset_id", "unknown")
        if asset_id not in by_asset:
            by_asset[asset_id] = []
        by_asset[asset_id].append(finding)

    return by_asset


def get_exploitable_findings(findings: List[Dict]) -> List[Dict]:
    """
    Get findings with known exploits available.

    Args:
        findings: List of finding dictionaries

    Returns:
        List of findings with exploit_available=True
    """
    return [f for f in findings if f.get("exploit_available")]


def get_unpatched_findings(findings: List[Dict]) -> List[Dict]:
    """
    Get findings without patches available.

    Args:
        findings: List of finding dictionaries

    Returns:
        List of findings with patch_available=False
    """
    return [f for f in findings if not f.get("patch_available")]


def get_high_risk_assets(asset_risks: List[Dict]) -> List[Dict]:
    """
    Get assets with Red risk color.

    Args:
        asset_risks: List of asset risk dictionaries

    Returns:
        List of high-risk assets
    """
    return [a for a in asset_risks if a.get("risk_color") == "Red"]


def get_ctem_stats(findings: List[Dict], asset_risks: List[Dict]) -> Dict:
    """
    Get statistics about CTEM data.

    Args:
        findings: List of finding dictionaries
        asset_risks: List of asset risk dictionaries

    Returns:
        Dictionary with CTEM statistics
    """
    by_severity = get_findings_by_severity(findings)

    risk_distribution = {
        "Green": sum(1 for a in asset_risks if a["risk_color"] == "Green"),
        "Yellow": sum(1 for a in asset_risks if a["risk_color"] == "Yellow"),
        "Red": sum(1 for a in asset_risks if a["risk_color"] == "Red"),
    }

    return {
        "total_findings": len(findings),
        "total_assets": len(asset_risks),
        "by_severity": {k: len(v) for k, v in by_severity.items()},
        "risk_distribution": risk_distribution,
        "exploitable_count": len(get_exploitable_findings(findings)),
        "unpatched_count": len(get_unpatched_findings(findings)),
        "avg_findings_per_asset": len(findings) / len(asset_risks) if asset_risks else 0,
    }


if __name__ == "__main__":
    # Quick test
    import json
    from .gen_assets import generate_assets

    assets = generate_assets(count=100, seed=42)
    findings, asset_risks = generate_ctem_findings(assets, seed=42)

    print(f"Generated {len(findings)} findings for {len(asset_risks)} assets")

    stats = get_ctem_stats(findings, asset_risks)
    print(f"\nStatistics:")
    print(f"  By severity: {stats['by_severity']}")
    print(f"  Risk distribution: {stats['risk_distribution']}")
    print(f"  Exploitable: {stats['exploitable_count']}")
    print(f"  Avg per asset: {stats['avg_findings_per_asset']:.2f}")

    high_risk = get_high_risk_assets(asset_risks)
    print(f"\nHigh risk assets: {len(high_risk)}")

    print("\nSample finding:")
    print(json.dumps(findings[0], indent=2, default=str))

    print("\nSample asset risk:")
    print(json.dumps(asset_risks[0], indent=2, default=str))
