"""
Pydantic models for Threat Enrichment system.

These models represent the enriched threat indicator data structure,
including geolocation, network info, reputation data from multiple
sources, threat intelligence, MITRE ATT&CK mappings, and relationships.

Based on THREAT_ENRICHMENT_DESIGN.md specification.
"""
from datetime import datetime
from typing import Optional, List, Literal, Union
from pydantic import BaseModel, Field


# =============================================================================
# Geolocation Models
# =============================================================================

class GeoLocation(BaseModel):
    """
    Geolocation information for IP addresses.

    Contains country, city, coordinates, and timezone data
    typically sourced from IPinfo or similar services.
    """
    country: str = Field(..., description="ISO country code (e.g., 'US', 'RU')")
    country_name: str = Field(..., description="Full country name (e.g., 'United States')")
    city: Optional[str] = Field(default=None, description="City name")
    region: Optional[str] = Field(default=None, description="Region/state name")
    latitude: Optional[float] = Field(default=None, description="Latitude coordinate")
    longitude: Optional[float] = Field(default=None, description="Longitude coordinate")
    timezone: Optional[str] = Field(default=None, description="Timezone (e.g., 'America/New_York')")


# =============================================================================
# Network Information Models
# =============================================================================

class NetworkInfo(BaseModel):
    """
    Network information for IP addresses.

    Contains ASN, ISP, company info, and network type flags
    (VPN, proxy, Tor, datacenter, mobile).
    """
    asn: Optional[int] = Field(default=None, description="Autonomous System Number")
    asn_org: Optional[str] = Field(default=None, description="ASN organization name (e.g., 'Google LLC')")
    isp: Optional[str] = Field(default=None, description="Internet Service Provider")
    company: Optional[str] = Field(default=None, description="Company owning the IP")
    is_vpn: bool = Field(default=False, description="Is this a known VPN endpoint?")
    is_proxy: bool = Field(default=False, description="Is this a known proxy?")
    is_tor: bool = Field(default=False, description="Is this a Tor exit node?")
    is_datacenter: bool = Field(default=False, description="Is this a datacenter IP?")
    is_mobile: bool = Field(default=False, description="Is this a mobile network IP?")


# =============================================================================
# Service Information Models (Shodan/Censys)
# =============================================================================

class ServiceInfo(BaseModel):
    """
    Information about services exposed on an IP.

    Contains port, protocol, service name, version, banner,
    and associated CVEs. Typically from Shodan or Censys.
    """
    port: int = Field(..., description="Port number")
    protocol: Optional[str] = Field(default=None, description="Protocol (tcp/udp)")
    service: Optional[str] = Field(default=None, description="Service name (e.g., 'ssh', 'http')")
    version: Optional[str] = Field(default=None, description="Service version")
    banner: Optional[str] = Field(default=None, description="Service banner")
    cves: List[str] = Field(default_factory=list, description="Associated CVE IDs")


# =============================================================================
# Reputation Sub-Models (Per Source)
# =============================================================================

class AbuseIPDBReputation(BaseModel):
    """
    Reputation data from AbuseIPDB.

    Contains confidence score, abuse reports, and categories.
    """
    confidence_score: int = Field(default=0, ge=0, le=100, description="Confidence score 0-100")
    total_reports: Optional[int] = Field(default=None, description="Total abuse reports")
    last_reported: Optional[str] = Field(default=None, description="Last report timestamp (ISO 8601)")
    abuse_categories: List[str] = Field(default_factory=list, description="Abuse categories (e.g., 'SSH Brute Force')")


class GreyNoiseReputation(BaseModel):
    """
    Reputation data from GreyNoise.

    Contains classification, noise status, and actor info.
    """
    classification: Literal["benign", "malicious", "unknown"] = Field(
        ..., description="Classification: benign, malicious, or unknown"
    )
    noise: bool = Field(default=False, description="Is this a known internet scanner?")
    riot: bool = Field(default=False, description="Is this legitimate infrastructure (RIOT)?")
    bot: bool = Field(default=False, description="Is this a bot?")
    vpn: bool = Field(default=False, description="Is this a VPN endpoint?")
    actor: Optional[str] = Field(default=None, description="Actor name (e.g., 'Shodan', 'Censys')")


class VirusTotalReputation(BaseModel):
    """
    Reputation data from VirusTotal.

    Contains AV detection counts and community score.
    """
    malicious_count: int = Field(default=0, description="Number of AV engines flagging as malicious")
    suspicious_count: int = Field(default=0, description="Number of AV engines flagging as suspicious")
    harmless_count: int = Field(default=0, description="Number of AV engines flagging as harmless")
    undetected_count: int = Field(default=0, description="Number of AV engines with no detection")
    community_score: Optional[int] = Field(default=None, description="Community score (-100 to +100)")
    last_analysis_date: Optional[str] = Field(default=None, description="Last analysis timestamp (ISO 8601)")


class PulsediveReputation(BaseModel):
    """
    Reputation data from Pulsedive.

    Contains risk level and risk factors.
    """
    risk: Literal["critical", "high", "medium", "low", "unknown"] = Field(
        ..., description="Risk level"
    )
    risk_factors: List[str] = Field(default_factory=list, description="Risk factor descriptions")
    feeds_count: int = Field(default=0, description="Number of feeds containing this indicator")


class ReputationData(BaseModel):
    """
    Aggregated reputation data from multiple sources.

    Contains optional reputation data from AbuseIPDB, GreyNoise,
    VirusTotal, and Pulsedive.
    """
    abuseipdb: Optional[AbuseIPDBReputation] = Field(default=None, description="AbuseIPDB reputation data")
    greynoise: Optional[GreyNoiseReputation] = Field(default=None, description="GreyNoise reputation data")
    virustotal: Optional[VirusTotalReputation] = Field(default=None, description="VirusTotal reputation data")
    pulsedive: Optional[PulsediveReputation] = Field(default=None, description="Pulsedive reputation data")


# =============================================================================
# Threat Intelligence Models
# =============================================================================

class MaliciousURL(BaseModel):
    """
    Information about a malicious URL associated with an indicator.
    """
    url: str = Field(..., description="The malicious URL")
    threat: Optional[str] = Field(default=None, description="Threat type/name")
    date_added: Optional[str] = Field(default=None, description="Date added (ISO 8601)")


class DistributedMalware(BaseModel):
    """
    Information about malware distributed by an indicator.
    """
    hash: str = Field(..., description="File hash")
    hash_type: Literal["md5", "sha1", "sha256"] = Field(..., description="Hash algorithm")
    malware_name: Optional[str] = Field(default=None, description="Malware family/name")
    file_type: Optional[str] = Field(default=None, description="File type (e.g., 'exe', 'dll')")


class ThreatIntelData(BaseModel):
    """
    Threat intelligence data for an indicator.

    Contains malware families, threat actors, campaigns, tags,
    associated malicious URLs, and distributed malware info.
    """
    malware_families: List[str] = Field(default_factory=list, description="Associated malware families")
    threat_actors: List[str] = Field(default_factory=list, description="Associated threat actors/APT groups")
    campaigns: List[str] = Field(default_factory=list, description="Associated campaigns")
    tags: List[str] = Field(default_factory=list, description="Community tags (e.g., 'c2', 'botnet')")
    malicious_urls: List[MaliciousURL] = Field(default_factory=list, description="Associated malicious URLs")
    distributed_malware: List[DistributedMalware] = Field(default_factory=list, description="Distributed malware samples")


# =============================================================================
# MITRE ATT&CK Models
# =============================================================================

class MitreTactic(BaseModel):
    """
    MITRE ATT&CK Tactic.
    """
    id: str = Field(..., description="Tactic ID (e.g., 'TA0001')")
    name: str = Field(..., description="Tactic name (e.g., 'Initial Access')")


class MitreTechnique(BaseModel):
    """
    MITRE ATT&CK Technique.
    """
    id: str = Field(..., description="Technique ID (e.g., 'T1566.001')")
    name: str = Field(..., description="Technique name (e.g., 'Spearphishing Attachment')")
    data_sources: List[str] = Field(default_factory=list, description="Data sources for detection")


class MitreSoftware(BaseModel):
    """
    MITRE ATT&CK Software.
    """
    id: str = Field(..., description="Software ID (e.g., 'S0154')")
    name: str = Field(..., description="Software name (e.g., 'Cobalt Strike')")


class MitreAttackData(BaseModel):
    """
    MITRE ATT&CK TTP mapping for an indicator.

    Contains associated tactics, techniques, and software.
    """
    tactics: List[MitreTactic] = Field(default_factory=list, description="Associated tactics")
    techniques: List[MitreTechnique] = Field(default_factory=list, description="Associated techniques")
    software: List[MitreSoftware] = Field(default_factory=list, description="Associated software/tools")


# =============================================================================
# Intel Feed Models
# =============================================================================

class IntelFeed(BaseModel):
    """
    Intelligence feed/pulse information.

    Contains feed metadata, source, author, and TLP classification.
    """
    source: str = Field(..., description="Feed source (e.g., 'AlienVault OTX')")
    feed_name: str = Field(..., description="Feed/pulse name")
    feed_id: str = Field(..., description="Feed/pulse ID")
    description: Optional[str] = Field(default=None, description="Feed description")
    created: Optional[str] = Field(default=None, description="Creation timestamp (ISO 8601)")
    author: Optional[str] = Field(default=None, description="Feed author")
    tlp: Literal["white", "green", "amber", "red"] = Field(
        ..., description="Traffic Light Protocol classification"
    )
    reference_urls: List[str] = Field(default_factory=list, description="Reference URLs")


# =============================================================================
# Breach Data Models (for Email IOCs)
# =============================================================================

class Breach(BaseModel):
    """
    Individual breach information.
    """
    name: str = Field(..., description="Breach name (e.g., 'LinkedIn')")
    breach_date: Optional[str] = Field(default=None, description="Breach date")
    pwn_count: int = Field(default=0, description="Number of accounts affected")
    data_classes: List[str] = Field(default_factory=list, description="Data types exposed (e.g., 'Email', 'Password')")


class BreachData(BaseModel):
    """
    Breach exposure data for email IOCs.

    Contains breach status, count, and detailed breach information.
    """
    breached: bool = Field(..., description="Whether the email was found in breaches")
    breach_count: int = Field(..., description="Number of breaches")
    breaches: List[Breach] = Field(default_factory=list, description="List of breaches")
    paste_count: int = Field(default=0, description="Number of paste appearances")


# =============================================================================
# Enrichment Metadata Models
# =============================================================================

class EnrichmentMeta(BaseModel):
    """
    Metadata about the enrichment process.

    Contains timing, source query results, and cache status.
    """
    enriched_at: Union[str, datetime] = Field(..., description="Enrichment timestamp (ISO 8601)")
    sources_queried: List[str] = Field(..., description="List of sources queried")
    sources_successful: List[str] = Field(..., description="List of sources that responded successfully")
    sources_failed: List[str] = Field(..., description="List of sources that failed")
    total_sources: int = Field(..., description="Total number of sources queried")
    successful_sources: int = Field(..., description="Number of successful source responses")
    cache_hit: bool = Field(default=False, description="Whether data was retrieved from cache")
    processing_time_ms: int = Field(default=0, description="Processing time in milliseconds")


# =============================================================================
# Relationship Models
# =============================================================================

class PassiveDNS(BaseModel):
    """
    Passive DNS record.
    """
    domain: str = Field(..., description="Domain name")
    ip: str = Field(..., description="Resolved IP address")
    first_seen: Optional[str] = Field(default=None, description="First observation date")
    last_seen: Optional[str] = Field(default=None, description="Last observation date")


class SSLCertificate(BaseModel):
    """
    SSL certificate information.
    """
    sha256: str = Field(..., description="Certificate SHA256 fingerprint")
    issuer: Optional[str] = Field(default=None, description="Certificate issuer")
    subject: Optional[str] = Field(default=None, description="Certificate subject")
    not_before: Optional[str] = Field(default=None, description="Valid from date")
    not_after: Optional[str] = Field(default=None, description="Valid until date")


class RelationshipData(BaseModel):
    """
    Relationship data for an indicator.

    Contains related IOCs, passive DNS records, and SSL certificates.
    """
    related_ips: List[str] = Field(default_factory=list, description="Related IP addresses")
    related_domains: List[str] = Field(default_factory=list, description="Related domains")
    related_urls: List[str] = Field(default_factory=list, description="Related URLs")
    related_hashes: List[str] = Field(default_factory=list, description="Related file hashes")
    passive_dns: List[PassiveDNS] = Field(default_factory=list, description="Passive DNS records")
    ssl_certificates: List[SSLCertificate] = Field(default_factory=list, description="SSL certificates")


# =============================================================================
# Main EnrichedThreatIndicator Model
# =============================================================================

class EnrichedThreatIndicator(BaseModel):
    """
    Main enriched threat indicator model.

    This is the complete representation of an IOC (Indicator of Compromise)
    enriched with data from multiple threat intelligence sources.

    Supports 6 IOC types: ip, domain, url, hash, email, cve

    Contains:
    - Identification (id, type, value, timestamps)
    - Risk scoring (0-100 score, risk level, confidence)
    - Geolocation (for IPs)
    - Network info (for IPs)
    - Services (from Shodan/Censys)
    - Reputation data (from multiple sources)
    - Threat intelligence (malware, actors, campaigns)
    - MITRE ATT&CK TTPs
    - Intel feeds/pulses
    - Breach data (for emails)
    - Enrichment metadata
    - Relationships
    """
    # Identification
    id: str = Field(..., description="Unique identifier (UUID)")
    type: Literal["ip", "domain", "url", "hash", "email", "cve"] = Field(
        ..., description="IOC type"
    )
    value: str = Field(..., description="The IOC value")
    first_seen: Union[str, datetime] = Field(..., description="First observation timestamp (ISO 8601)")
    last_seen: Union[str, datetime] = Field(..., description="Last observation timestamp (ISO 8601)")

    # Risk Scoring
    risk_score: int = Field(..., ge=0, le=100, description="Aggregated risk score 0-100")
    risk_level: Literal["critical", "high", "medium", "low", "unknown"] = Field(
        ..., description="Risk level classification"
    )
    confidence: int = Field(..., ge=0, le=100, description="Confidence level 0-100")

    # Geolocation (for IPs)
    geo: Optional[GeoLocation] = Field(default=None, description="Geolocation data (for IPs)")

    # Network Info (for IPs)
    network: Optional[NetworkInfo] = Field(default=None, description="Network information (for IPs)")

    # Services (from Shodan/Censys)
    services: Optional[List[ServiceInfo]] = Field(default=None, description="Exposed services (for IPs)")

    # Reputation Data
    reputation: ReputationData = Field(..., description="Reputation data from multiple sources")

    # Threat Intelligence
    threat_intel: ThreatIntelData = Field(..., description="Threat intelligence data")

    # MITRE ATT&CK
    mitre_attack: MitreAttackData = Field(..., description="MITRE ATT&CK TTP mapping")

    # Intel Feeds
    intel_feeds: List[IntelFeed] = Field(default_factory=list, description="Associated intel feeds/pulses")

    # Breach Data (for Emails)
    breach_data: Optional[BreachData] = Field(default=None, description="Breach data (for emails)")

    # CVE Data (for CVEs) - using dict for flexibility
    cve_data: Optional[dict] = Field(default=None, description="CVE data (for CVE type)")

    # Enrichment Metadata
    enrichment_meta: EnrichmentMeta = Field(..., description="Enrichment process metadata")

    # Relationships
    relationships: RelationshipData = Field(..., description="Related indicators and data")
