"""
Threat Intelligence Generator for CyberDemo.

Generates synthetic threat intelligence data including IOCs (Indicators of
Compromise) such as file hashes, IP addresses, and domains with associated
verdicts and metadata.
"""

import hashlib
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from .constants import (
    ANCHOR_HASHES,
    INTEL_SOURCES,
    MALWARE_LABELS,
)


def _generate_sha256(rng: random.Random) -> str:
    """Generate a random SHA256 hash."""
    return hashlib.sha256(str(rng.random()).encode()).hexdigest()


def _generate_ip_address(rng: random.Random, malicious: bool = False) -> str:
    """Generate an IP address."""
    if malicious:
        # Known bad IP ranges (fictional)
        ranges = [
            (185, rng.randint(100, 200)),
            (45, rng.randint(140, 180)),
            (91, rng.randint(200, 250)),
            (193, rng.randint(100, 150)),
            (79, rng.randint(110, 140)),
        ]
        prefix = rng.choice(ranges)
        return f"{prefix[0]}.{prefix[1]}.{rng.randint(1, 254)}.{rng.randint(1, 254)}"
    else:
        # Generic IP
        return f"{rng.randint(1, 223)}.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"


def _generate_domain(rng: random.Random, malicious: bool = False) -> str:
    """Generate a domain name."""
    if malicious:
        # DGA-like or suspicious domains
        suspicious_patterns = [
            # Random-looking
            lambda: "".join(rng.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=rng.randint(8, 16))),
            # Word + numbers
            lambda: f"{rng.choice(['update', 'secure', 'login', 'auth', 'cdn', 'api'])}{rng.randint(1, 999)}",
            # Double words
            lambda: f"{rng.choice(['cloud', 'sync', 'service'])}{rng.choice(['net', 'data', 'tech'])}",
        ]

        suspicious_tlds = ["xyz", "top", "club", "online", "site", "info", "biz", "pw"]
        domain_name = rng.choice(suspicious_patterns)()
        tld = rng.choice(suspicious_tlds)

        return f"{domain_name}.{tld}"
    else:
        # Legitimate-looking domains
        companies = ["acme", "globex", "initech", "contoso", "fabrikam", "northwind", "widgetco"]
        tlds = ["com", "net", "org", "io"]
        subdomains = ["", "www.", "api.", "cdn.", "mail.", "vpn."]

        subdomain = rng.choice(subdomains)
        company = rng.choice(companies)
        tld = rng.choice(tlds)

        return f"{subdomain}{company}.{tld}".lstrip(".")


def _generate_vt_score(rng: random.Random, verdict: str) -> str:
    """Generate a VirusTotal-style score (detections/total)."""
    total = rng.randint(70, 80)

    if verdict == "malicious":
        detections = rng.randint(35, total - 5)
    elif verdict == "suspicious":
        detections = rng.randint(5, 25)
    else:  # benign
        detections = rng.randint(0, 3)

    return f"{detections}/{total}"


def _generate_labels(rng: random.Random, verdict: str, indicator_type: str) -> List[str]:
    """Generate threat labels for an IOC."""
    if verdict == "benign":
        return []

    num_labels = rng.randint(1, 3) if verdict == "malicious" else rng.randint(1, 2)
    labels = rng.sample(MALWARE_LABELS, min(num_labels, len(MALWARE_LABELS)))

    # Add type-specific labels
    if indicator_type == "ip" and "botnet" not in labels:
        if rng.random() < 0.3:
            labels.append("c2")
    elif indicator_type == "domain":
        if rng.random() < 0.2:
            labels.append("phishing")

    return labels


def _generate_sources(rng: random.Random, verdict: str) -> List[str]:
    """Generate intelligence sources for an IOC."""
    if verdict == "benign":
        num_sources = rng.randint(1, 2)
    elif verdict == "suspicious":
        num_sources = rng.randint(2, 4)
    else:  # malicious
        num_sources = rng.randint(3, 6)

    return rng.sample(INTEL_SOURCES, min(num_sources, len(INTEL_SOURCES)))


def _generate_timestamps(rng: random.Random) -> Tuple[str, str]:
    """Generate first_seen and last_seen timestamps."""
    now = datetime.now()

    # First seen: 1-365 days ago
    first_seen_days = rng.randint(1, 365)
    first_seen = now - timedelta(days=first_seen_days)

    # Last seen: between first_seen and now
    last_seen_days = rng.randint(0, first_seen_days)
    last_seen = now - timedelta(days=last_seen_days)

    return first_seen.isoformat(), last_seen.isoformat()


def _generate_confidence(rng: random.Random, verdict: str) -> int:
    """Generate a confidence score (0-100)."""
    if verdict == "malicious":
        return rng.randint(70, 100)
    elif verdict == "suspicious":
        return rng.randint(40, 70)
    else:  # benign
        return rng.randint(80, 100)


def generate_threat_intel(
    count: int = 200,
    seed: int = 42
) -> List[Dict]:
    """
    Generate synthetic threat intelligence IOCs.

    Args:
        count: Number of IOCs to generate (default 200)
        seed: Random seed for reproducibility (default 42)

    Returns:
        List of IOC dictionaries with threat intelligence data

    Example:
        >>> intel = generate_threat_intel(count=50, seed=42)
        >>> len(intel)
        50
        >>> intel[0].keys()
        dict_keys(['indicator_type', 'indicator_value', 'verdict', ...])
    """
    rng = random.Random(seed)
    indicators = []

    # First, generate anchor hashes as malicious
    for anchor_hash in ANCHOR_HASHES:
        first_seen, last_seen = _generate_timestamps(rng)

        indicator = {
            "indicator_type": "filehash",
            "indicator_value": anchor_hash,
            "verdict": "malicious",
            "confidence": rng.randint(90, 100),
            "vt_score": _generate_vt_score(rng, "malicious"),
            "labels": _generate_labels(rng, "malicious", "filehash"),
            "sources": _generate_sources(rng, "malicious"),
            "first_seen": first_seen,
            "last_seen": last_seen,
        }
        indicators.append(indicator)

    # Calculate remaining counts
    remaining = count - len(ANCHOR_HASHES)

    # Distribution: 20% malicious, 10% suspicious, 70% benign
    # Subtract anchor hashes from malicious count
    malicious_count = int(count * 0.20) - len(ANCHOR_HASHES)
    suspicious_count = int(count * 0.10)
    benign_count = remaining - malicious_count - suspicious_count

    # Ensure we don't have negative counts
    malicious_count = max(0, malicious_count)

    # Type distribution: ~50% hashes, ~25% IPs, ~25% domains
    type_distribution = {
        "filehash": 0.50,
        "ip": 0.25,
        "domain": 0.25,
    }

    # Generate malicious indicators
    for _ in range(malicious_count):
        indicator_type = rng.choices(
            list(type_distribution.keys()),
            weights=list(type_distribution.values())
        )[0]

        if indicator_type == "filehash":
            value = _generate_sha256(rng)
        elif indicator_type == "ip":
            value = _generate_ip_address(rng, malicious=True)
        else:
            value = _generate_domain(rng, malicious=True)

        first_seen, last_seen = _generate_timestamps(rng)

        indicator = {
            "indicator_type": indicator_type,
            "indicator_value": value,
            "verdict": "malicious",
            "confidence": _generate_confidence(rng, "malicious"),
            "vt_score": _generate_vt_score(rng, "malicious"),
            "labels": _generate_labels(rng, "malicious", indicator_type),
            "sources": _generate_sources(rng, "malicious"),
            "first_seen": first_seen,
            "last_seen": last_seen,
        }
        indicators.append(indicator)

    # Generate suspicious indicators
    for _ in range(suspicious_count):
        indicator_type = rng.choices(
            list(type_distribution.keys()),
            weights=list(type_distribution.values())
        )[0]

        if indicator_type == "filehash":
            value = _generate_sha256(rng)
        elif indicator_type == "ip":
            # 50/50 malicious-looking or generic
            value = _generate_ip_address(rng, malicious=rng.random() < 0.5)
        else:
            value = _generate_domain(rng, malicious=rng.random() < 0.5)

        first_seen, last_seen = _generate_timestamps(rng)

        indicator = {
            "indicator_type": indicator_type,
            "indicator_value": value,
            "verdict": "suspicious",
            "confidence": _generate_confidence(rng, "suspicious"),
            "vt_score": _generate_vt_score(rng, "suspicious"),
            "labels": _generate_labels(rng, "suspicious", indicator_type),
            "sources": _generate_sources(rng, "suspicious"),
            "first_seen": first_seen,
            "last_seen": last_seen,
        }
        indicators.append(indicator)

    # Generate benign indicators
    for _ in range(benign_count):
        indicator_type = rng.choices(
            list(type_distribution.keys()),
            weights=list(type_distribution.values())
        )[0]

        if indicator_type == "filehash":
            value = _generate_sha256(rng)
        elif indicator_type == "ip":
            value = _generate_ip_address(rng, malicious=False)
        else:
            value = _generate_domain(rng, malicious=False)

        first_seen, last_seen = _generate_timestamps(rng)

        indicator = {
            "indicator_type": indicator_type,
            "indicator_value": value,
            "verdict": "benign",
            "confidence": _generate_confidence(rng, "benign"),
            "vt_score": _generate_vt_score(rng, "benign"),
            "labels": [],
            "sources": _generate_sources(rng, "benign"),
            "first_seen": first_seen,
            "last_seen": last_seen,
        }
        indicators.append(indicator)

    # Shuffle to mix verdicts
    rng.shuffle(indicators)

    return indicators


def get_intel_by_verdict(intel: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group IOCs by verdict.

    Args:
        intel: List of IOC dictionaries

    Returns:
        Dictionary mapping verdicts to lists of IOCs
    """
    by_verdict: Dict[str, List[Dict]] = {
        "malicious": [],
        "suspicious": [],
        "benign": [],
    }

    for ioc in intel:
        verdict = ioc.get("verdict", "benign")
        if verdict in by_verdict:
            by_verdict[verdict].append(ioc)

    return by_verdict


def get_intel_by_type(intel: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group IOCs by indicator type.

    Args:
        intel: List of IOC dictionaries

    Returns:
        Dictionary mapping types to lists of IOCs
    """
    by_type: Dict[str, List[Dict]] = {
        "filehash": [],
        "ip": [],
        "domain": [],
    }

    for ioc in intel:
        ioc_type = ioc.get("indicator_type", "filehash")
        if ioc_type in by_type:
            by_type[ioc_type].append(ioc)
        else:
            by_type[ioc_type] = [ioc]

    return by_type


def lookup_hash(intel: List[Dict], sha256: str) -> Dict:
    """
    Look up threat intel for a specific hash.

    Args:
        intel: List of IOC dictionaries
        sha256: The SHA256 hash to look up

    Returns:
        IOC data if found, or a default "unknown" response
    """
    for ioc in intel:
        if ioc.get("indicator_type") == "filehash" and ioc.get("indicator_value") == sha256:
            return ioc

    return {
        "indicator_type": "filehash",
        "indicator_value": sha256,
        "verdict": "unknown",
        "confidence": 0,
        "vt_score": "0/0",
        "labels": [],
        "sources": [],
        "first_seen": None,
        "last_seen": None,
    }


def lookup_ip(intel: List[Dict], ip: str) -> Dict:
    """
    Look up threat intel for a specific IP.

    Args:
        intel: List of IOC dictionaries
        ip: The IP address to look up

    Returns:
        IOC data if found, or a default "unknown" response
    """
    for ioc in intel:
        if ioc.get("indicator_type") == "ip" and ioc.get("indicator_value") == ip:
            return ioc

    return {
        "indicator_type": "ip",
        "indicator_value": ip,
        "verdict": "unknown",
        "confidence": 0,
        "vt_score": "0/0",
        "labels": [],
        "sources": [],
        "first_seen": None,
        "last_seen": None,
    }


def lookup_domain(intel: List[Dict], domain: str) -> Dict:
    """
    Look up threat intel for a specific domain.

    Args:
        intel: List of IOC dictionaries
        domain: The domain to look up

    Returns:
        IOC data if found, or a default "unknown" response
    """
    for ioc in intel:
        if ioc.get("indicator_type") == "domain" and ioc.get("indicator_value") == domain:
            return ioc

    return {
        "indicator_type": "domain",
        "indicator_value": domain,
        "verdict": "unknown",
        "confidence": 0,
        "vt_score": "0/0",
        "labels": [],
        "sources": [],
        "first_seen": None,
        "last_seen": None,
    }


def get_malicious_hashes(intel: List[Dict]) -> List[str]:
    """
    Get all malicious file hashes.

    Args:
        intel: List of IOC dictionaries

    Returns:
        List of malicious SHA256 hashes
    """
    return [
        ioc["indicator_value"]
        for ioc in intel
        if ioc.get("indicator_type") == "filehash" and ioc.get("verdict") == "malicious"
    ]


def get_intel_stats(intel: List[Dict]) -> Dict:
    """
    Get statistics about the threat intelligence data.

    Args:
        intel: List of IOC dictionaries

    Returns:
        Dictionary with intel statistics
    """
    by_verdict = get_intel_by_verdict(intel)
    by_type = get_intel_by_type(intel)

    return {
        "total": len(intel),
        "by_verdict": {k: len(v) for k, v in by_verdict.items()},
        "by_type": {k: len(v) for k, v in by_type.items()},
        "anchor_hashes_included": sum(
            1 for ioc in intel
            if ioc.get("indicator_value") in ANCHOR_HASHES
        ),
    }


if __name__ == "__main__":
    # Quick test
    import json

    intel = generate_threat_intel(count=200, seed=42)

    print(f"Generated {len(intel)} IOCs")

    stats = get_intel_stats(intel)
    print(f"\nStatistics:")
    print(f"  By verdict: {stats['by_verdict']}")
    print(f"  By type: {stats['by_type']}")
    print(f"  Anchor hashes: {stats['anchor_hashes_included']}")

    # Check anchor hashes
    print("\nAnchor hash lookups:")
    for anchor in ANCHOR_HASHES[:2]:
        result = lookup_hash(intel, anchor)
        print(f"  {anchor[:16]}...: {result['verdict']}")

    print("\nSample IOC:")
    print(json.dumps(intel[0], indent=2, default=str))
