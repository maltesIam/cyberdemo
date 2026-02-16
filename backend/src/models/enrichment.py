"""
Database models for enrichment system.

These models store enrichment jobs, vulnerability enrichment data,
threat intelligence enrichment data, and API response cache.
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ARRAY, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from ..core.database import Base


class EnrichmentJob(Base):
    """
    Tracks enrichment jobs (background tasks).

    Stores metadata about enrichment operations, progress tracking,
    and completion status.
    """
    __tablename__ = "enrichment_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(50), nullable=False)  # 'vulnerability' | 'threat'
    status = Column(String(50), nullable=False, default="pending")  # 'pending' | 'running' | 'completed' | 'failed'
    total_items = Column(Integer, nullable=False)
    processed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    job_metadata = Column(JSON, nullable=True)  # Additional job metadata (renamed to avoid SQLAlchemy conflict)

    __table_args__ = (
        Index('idx_enrichment_jobs_status', 'status'),
        Index('idx_enrichment_jobs_type', 'type'),
    )


class VulnerabilityEnrichment(Base):
    """
    Enrichment data for CVEs.

    Stores data from multiple sources:
    - NVD: CVSS scores, CWE, CPE
    - EPSS: Exploit prediction scores
    - GitHub Advisory: Security advisories
    - Synthetic: Risk scores, threat actors (simulated premium data)
    """
    __tablename__ = "vulnerability_enrichment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cve_id = Column(String(50), nullable=False, unique=True, index=True)

    # CVSS scores (from NVD)
    cvss_v3_score = Column(Float, nullable=True)
    cvss_v3_vector = Column(String(100), nullable=True)
    cvss_v2_score = Column(Float, nullable=True)

    # EPSS scores (from EPSS API)
    epss_score = Column(Float, nullable=True)  # 0.0-1.0
    epss_percentile = Column(Float, nullable=True)  # 0.0-1.0

    # Weakness and platform info (from NVD)
    cwe_ids = Column(ARRAY(Text), nullable=True)  # Common Weakness Enumeration
    cpe_uris = Column(ARRAY(Text), nullable=True)  # Common Platform Enumeration

    # Exploit info
    known_exploited = Column(Boolean, default=False)  # CISA KEV
    exploit_available = Column(Boolean, default=False)
    patch_available = Column(Boolean, default=False)
    vendor_advisory_url = Column(String(500), nullable=True)

    # References and affected products
    references = Column(JSON, nullable=True)  # [{url, source, tags}]
    affected_products = Column(JSON, nullable=True)  # [{vendor, product, versions}]

    # Attack characteristics
    attack_complexity = Column(String(50), nullable=True)
    privileges_required = Column(String(50), nullable=True)
    user_interaction = Column(String(50), nullable=True)

    # Synthetic premium fields (simulated Recorded Future, Tenable, etc.)
    risk_score = Column(Integer, nullable=True)  # 0-100 (synthetic)
    threat_actors = Column(ARRAY(Text), nullable=True)  # Associated APT groups (synthetic)
    campaigns = Column(ARRAY(Text), nullable=True)  # Associated campaigns (synthetic)
    vpr_score = Column(Float, nullable=True)  # Vulnerability Priority Rating (synthetic Tenable)
    qds_score = Column(Integer, nullable=True)  # Qualys Detection Score (synthetic)

    # Metadata
    enriched_at = Column(DateTime(timezone=True), default=func.now())
    enrichment_sources = Column(JSON, nullable=True)  # Which APIs were used

    __table_args__ = (
        Index('idx_vuln_enrichment_cve', 'cve_id'),
        Index('idx_vuln_enrichment_risk_score', 'risk_score'),
        Index('idx_vuln_enrichment_known_exploited', 'known_exploited'),
    )


class ThreatEnrichment(Base):
    """
    Enrichment data for threat intelligence indicators (IOCs).

    Stores data from multiple sources:
    - AlienVault OTX: Pulses, threat actors, malware families
    - AbuseIPDB: IP reputation, abuse confidence
    - GreyNoise: IP classification, tags
    - VirusTotal: Detections, malicious count
    - Shodan: Open ports, vulnerabilities
    - Synthetic: Sandbox reports (simulated CrowdStrike)
    """
    __tablename__ = "threat_enrichment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    indicator_type = Column(String(50), nullable=False)  # 'ip' | 'domain' | 'url' | 'hash'
    indicator_value = Column(String(500), nullable=False)

    # General threat info
    reputation_score = Column(Integer, nullable=True)  # 0-100 (0=clean, 100=malicious)
    malicious = Column(Boolean, default=False)
    confidence = Column(Integer, nullable=True)  # 0-100
    first_seen = Column(DateTime(timezone=True), nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)

    # IP specific (geolocation)
    country = Column(String(10), nullable=True)
    city = Column(String(100), nullable=True)
    asn = Column(Integer, nullable=True)
    asn_owner = Column(String(200), nullable=True)

    # Threat context
    malware_families = Column(ARRAY(Text), nullable=True)
    threat_types = Column(ARRAY(Text), nullable=True)  # ['botnet', 'c2', 'phishing', 'malware']
    attack_techniques = Column(ARRAY(Text), nullable=True)  # MITRE ATT&CK techniques
    threat_actors = Column(ARRAY(Text), nullable=True)  # APT groups
    campaigns = Column(ARRAY(Text), nullable=True)

    # AlienVault OTX specific
    otx_pulses = Column(JSON, nullable=True)  # [{pulse_id, pulse_name, created, author}]

    # AbuseIPDB specific
    abuse_confidence_score = Column(Integer, nullable=True)
    total_reports = Column(Integer, nullable=True)

    # GreyNoise specific
    greynoise_classification = Column(String(50), nullable=True)  # 'benign' | 'malicious' | 'unknown'
    greynoise_tags = Column(ARRAY(Text), nullable=True)

    # VirusTotal specific
    vt_detections = Column(Integer, nullable=True)
    vt_total_engines = Column(Integer, nullable=True)
    vt_malicious_count = Column(Integer, nullable=True)

    # Shodan specific
    open_ports = Column(ARRAY(Integer), nullable=True)
    vulnerabilities = Column(ARRAY(Text), nullable=True)

    # Synthetic premium fields (simulated CrowdStrike, ThreatQuotient)
    risk_score = Column(Integer, nullable=True)  # 0-100 (synthetic)
    sandbox_report = Column(JSON, nullable=True)  # Synthetic CrowdStrike style
    context_description = Column(Text, nullable=True)  # Synthetic ThreatQuotient style

    # Metadata
    enriched_at = Column(DateTime(timezone=True), default=func.now())
    enrichment_sources = Column(JSON, nullable=True)  # Which APIs were used

    __table_args__ = (
        Index('idx_threat_enrichment_indicator', 'indicator_type', 'indicator_value'),
        Index('idx_threat_enrichment_malicious', 'malicious'),
        Index('idx_threat_enrichment_reputation', 'reputation_score'),
    )


class EnrichmentCache(Base):
    """
    Cache for API responses to avoid rate limiting.

    Stores responses from external APIs with expiration times.
    Used to reduce API calls and improve performance.
    """
    __tablename__ = "enrichment_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cache_key = Column(String(500), nullable=False, unique=True)
    api_source = Column(String(100), nullable=False)
    response_data = Column(JSON, nullable=False)
    cached_at = Column(DateTime(timezone=True), default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    hit_count = Column(Integer, default=0)

    __table_args__ = (
        Index('idx_enrichment_cache_key', 'cache_key'),
        Index('idx_enrichment_cache_expires', 'expires_at'),
        Index('idx_enrichment_cache_source', 'api_source'),
    )
