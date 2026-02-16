"""
Pydantic models for Vulnerability Enrichment system.

These models represent the enriched CVE data structure, including
CVSS/EPSS scoring, KEV status, SSVC decision framework, exploit
intelligence, package/vendor information, threat intel, and more.

Based on VULNERABILITY_ENRICHMENT_BUILD_PLAN.md Section 3.
"""
from datetime import datetime
from typing import Optional, List, Literal, Union
from pydantic import BaseModel, Field


# =============================================================================
# ExploitRef Subentity
# =============================================================================

class ExploitRef(BaseModel):
    """
    Reference to an exploit associated with a CVE.

    Contains information about exploit sources like ExploitDB,
    Metasploit, GitHub PoCs, and Nuclei templates.
    """
    source: str = Field(
        ...,
        description="Exploit source: exploitdb, metasploit, github_poc, nuclei"
    )
    exploit_id: str = Field(..., description="Unique exploit identifier")
    title: str = Field(..., description="Exploit title/name")
    type: str = Field(
        ...,
        description="Exploit type: remote, local, webapps, dos"
    )
    platform: str = Field(..., description="Target platform (linux, windows, multi, any)")
    verified: bool = Field(..., description="Whether the exploit is verified/working")
    url: str = Field(..., description="URL to the exploit")
    date_published: Union[str, datetime] = Field(
        ...,
        description="Date the exploit was published (ISO 8601)"
    )


# =============================================================================
# PackageRef Subentity
# =============================================================================

class PackageRef(BaseModel):
    """
    Reference to an affected software package.

    Contains package ecosystem, name, version ranges, and GHSA ID
    for open source vulnerability tracking.
    """
    ecosystem: str = Field(
        ...,
        description="Package ecosystem: npm, pip, maven, go, cargo"
    )
    package_name: str = Field(..., description="Package name")
    vulnerable_versions: str = Field(
        ...,
        description="Vulnerable version range (e.g., '<4.17.21')"
    )
    patched_version: str = Field(..., description="First patched version")
    ghsa_id: Optional[str] = Field(
        default=None,
        description="GitHub Security Advisory ID (e.g., 'GHSA-jf85-cpcp-j695')"
    )


# =============================================================================
# VendorAdvisory Subentity
# =============================================================================

class VendorAdvisory(BaseModel):
    """
    Vendor security advisory information.

    Contains vendor name, advisory ID, patch URLs, and workaround info.
    """
    vendor: str = Field(..., description="Vendor name (e.g., 'Microsoft', 'Apache')")
    advisory_id: str = Field(..., description="Vendor advisory ID")
    patch_url: str = Field(..., description="URL to the patch/advisory")
    patch_date: Union[str, datetime] = Field(
        ...,
        description="Date the patch was released (ISO 8601)"
    )
    workaround: Optional[str] = Field(
        default=None,
        description="Workaround instructions if available"
    )
    severity_vendor: str = Field(
        ...,
        description="Vendor-assigned severity (e.g., 'Critical', 'Important')"
    )


# =============================================================================
# ThreatActorRef Subentity
# =============================================================================

class ThreatActorRef(BaseModel):
    """
    Reference to a threat actor associated with CVE exploitation.

    Contains actor name, aliases, attribution, and sophistication level.
    """
    name: str = Field(..., description="Primary threat actor name (e.g., 'APT29')")
    aliases: List[str] = Field(
        default_factory=list,
        description="Known aliases (e.g., ['Cozy Bear', 'The Dukes'])"
    )
    country: str = Field(..., description="Attribution country")
    motivation: str = Field(
        ...,
        description="Primary motivation (e.g., 'espionage', 'financial')"
    )
    sophistication: str = Field(
        ...,
        description="Sophistication level (e.g., 'low', 'medium', 'high', 'advanced')"
    )


# =============================================================================
# AffectedAsset Subentity
# =============================================================================

class AffectedAsset(BaseModel):
    """
    An asset affected by a vulnerability.

    Contains asset identification, criticality, and patch status.
    """
    asset_id: str = Field(..., description="Unique asset identifier")
    hostname: str = Field(..., description="Asset hostname")
    ip: str = Field(..., description="Asset IP address")
    asset_type: str = Field(
        ...,
        description="Asset type (e.g., 'server', 'database', 'application')"
    )
    criticality: str = Field(
        ...,
        description="Asset criticality (e.g., 'critical', 'high', 'medium', 'low')"
    )
    department: str = Field(..., description="Owning department")
    installed_version: str = Field(..., description="Installed vulnerable version")
    patched: bool = Field(..., description="Whether the asset has been patched")
    last_scanned: Union[str, datetime] = Field(
        ...,
        description="Last vulnerability scan timestamp (ISO 8601)"
    )


# =============================================================================
# EnrichedCVE Main Entity
# =============================================================================

class EnrichedCVE(BaseModel):
    """
    Main enriched CVE model with 50+ fields.

    This is the complete representation of a CVE enriched with data
    from multiple intelligence sources including NVD, EPSS, KEV,
    ExploitDB, Shodan, MITRE ATT&CK, and threat intelligence.

    Contains:
    - Core (NVD): cve_id, title, description, dates
    - Scoring: CVSS, EPSS, risk_score
    - Classification: severity, CWE, CPE
    - KEV (CISA): is_kev, dates, ransomware_use
    - Exploit Intelligence: count, sources, maturity
    - SSVC Decision: decision, exploitation, automatable, impact
    - Open Source Context: packages, versions, ecosystems
    - Internet Exposure (Shodan): exposed_count, countries, ports
    - Vendor Patches: advisories, patch_available, workaround
    - ATT&CK Context: techniques, tactics, actors
    - Threat Intel: actors, malware, campaigns, trending
    - Asset Impact: counts, departments
    - Lifecycle: status, assigned_to, SLA
    - Enrichment Metadata: level, sources, last_enriched
    """

    # =========================================================================
    # Core (NVD)
    # =========================================================================
    cve_id: str = Field(..., description="CVE identifier (e.g., 'CVE-2024-1234')")
    title: str = Field(..., description="CVE title/summary")
    description: str = Field(..., description="Full CVE description")
    published_date: Union[str, datetime] = Field(
        ...,
        description="Date CVE was published (ISO 8601)"
    )
    last_modified_date: Union[str, datetime] = Field(
        ...,
        description="Date CVE was last modified (ISO 8601)"
    )

    # =========================================================================
    # Scoring
    # =========================================================================
    cvss_v3_score: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        description="CVSS v3.x base score (0.0-10.0)"
    )
    cvss_v3_vector: str = Field(
        ...,
        description="CVSS v3.x vector string"
    )
    cvss_v2_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=10.0,
        description="CVSS v2.0 base score (0.0-10.0)"
    )
    epss_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="EPSS probability score (0.0-1.0)"
    )
    epss_percentile: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="EPSS percentile (0.0-1.0)"
    )
    risk_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Composite risk score (0.0-100.0)"
    )

    # =========================================================================
    # Classification
    # =========================================================================
    severity: Literal["Critical", "High", "Medium", "Low"] = Field(
        ...,
        description="Severity classification"
    )
    cwe_ids: List[str] = Field(
        default_factory=list,
        description="Associated CWE IDs (e.g., ['CWE-89', 'CWE-20'])"
    )
    cwe_names: List[str] = Field(
        default_factory=list,
        description="CWE names (e.g., ['SQL Injection'])"
    )
    cpe_uris: List[str] = Field(
        default_factory=list,
        description="Affected CPE URIs"
    )

    # =========================================================================
    # KEV (CISA Known Exploited Vulnerabilities)
    # =========================================================================
    is_kev: bool = Field(..., description="Whether CVE is in CISA KEV catalog")
    kev_date_added: Optional[Union[str, datetime]] = Field(
        default=None,
        description="Date added to KEV catalog (ISO 8601)"
    )
    kev_due_date: Optional[Union[str, datetime]] = Field(
        default=None,
        description="KEV remediation due date (ISO 8601)"
    )
    kev_required_action: Optional[str] = Field(
        default=None,
        description="Required remediation action from CISA"
    )
    kev_ransomware_use: bool = Field(
        default=False,
        description="Whether CVE is known to be used in ransomware"
    )

    # =========================================================================
    # Exploit Intelligence
    # =========================================================================
    exploit_count: int = Field(
        default=0,
        ge=0,
        description="Number of known exploits"
    )
    exploit_sources: List[ExploitRef] = Field(
        default_factory=list,
        description="List of exploit references"
    )
    exploit_maturity: Optional[Literal["weaponized", "poc", "unproven", "none"]] = Field(
        default=None,
        description="Exploit maturity level"
    )
    has_nuclei_template: bool = Field(
        default=False,
        description="Whether a Nuclei detection template exists"
    )
    nuclei_template_id: Optional[str] = Field(
        default=None,
        description="Nuclei template ID if available"
    )

    # =========================================================================
    # SSVC Decision Framework
    # =========================================================================
    ssvc_decision: Literal["Act", "Attend", "Track*", "Track"] = Field(
        ...,
        description="SSVC prioritization decision"
    )
    ssvc_exploitation: Optional[Literal["active", "poc", "none"]] = Field(
        default=None,
        description="SSVC exploitation status"
    )
    ssvc_automatable: bool = Field(
        default=False,
        description="Whether exploitation is automatable"
    )
    ssvc_technical_impact: Optional[Literal["total", "partial"]] = Field(
        default=None,
        description="SSVC technical impact"
    )
    ssvc_mission_prevalence: Optional[Literal["essential", "supportive", "minimal"]] = Field(
        default=None,
        description="SSVC mission prevalence"
    )

    # =========================================================================
    # Open Source Context
    # =========================================================================
    affected_packages: List[PackageRef] = Field(
        default_factory=list,
        description="Affected open source packages"
    )
    patched_versions: List[str] = Field(
        default_factory=list,
        description="Patched version strings"
    )
    vulnerable_ranges: List[str] = Field(
        default_factory=list,
        description="Vulnerable version ranges"
    )
    ecosystems: List[str] = Field(
        default_factory=list,
        description="Affected ecosystems (npm, pip, maven, etc.)"
    )

    # =========================================================================
    # Internet Exposure (Shodan)
    # =========================================================================
    shodan_exposed_count: int = Field(
        default=0,
        ge=0,
        description="Number of internet-exposed instances"
    )
    shodan_countries: List[str] = Field(
        default_factory=list,
        description="Countries with exposed instances"
    )
    shodan_top_ports: List[int] = Field(
        default_factory=list,
        description="Top exposed ports"
    )

    # =========================================================================
    # Vendor Patches
    # =========================================================================
    vendor_advisories: List[VendorAdvisory] = Field(
        default_factory=list,
        description="Vendor security advisories"
    )
    patch_available: bool = Field(
        default=False,
        description="Whether an official patch is available"
    )
    patch_url: Optional[str] = Field(
        default=None,
        description="URL to the official patch"
    )
    workaround_available: bool = Field(
        default=False,
        description="Whether a workaround is available"
    )
    product_eol: bool = Field(
        default=False,
        description="Whether the affected product is end-of-life"
    )

    # =========================================================================
    # ATT&CK Context
    # =========================================================================
    mitre_techniques: List[str] = Field(
        default_factory=list,
        description="MITRE ATT&CK technique IDs (e.g., ['T1190', 'T1133'])"
    )
    mitre_tactics: List[str] = Field(
        default_factory=list,
        description="MITRE ATT&CK tactic IDs (e.g., ['TA0001', 'TA0006'])"
    )
    typical_actors: List[str] = Field(
        default_factory=list,
        description="Threat actors known to exploit this CVE"
    )

    # =========================================================================
    # Threat Intel
    # =========================================================================
    threat_actors: List[ThreatActorRef] = Field(
        default_factory=list,
        description="Detailed threat actor references"
    )
    malware_families: List[str] = Field(
        default_factory=list,
        description="Malware families exploiting this CVE"
    )
    campaigns: List[str] = Field(
        default_factory=list,
        description="Campaigns exploiting this CVE"
    )
    exploitation_activity: Optional[Literal["none", "low", "medium", "high", "critical"]] = Field(
        default=None,
        description="Current exploitation activity level"
    )
    trending: bool = Field(
        default=False,
        description="Whether CVE is currently trending"
    )

    # =========================================================================
    # Asset Impact (local)
    # =========================================================================
    affected_asset_count: int = Field(
        default=0,
        ge=0,
        description="Number of affected assets"
    )
    affected_critical_assets: int = Field(
        default=0,
        ge=0,
        description="Number of affected critical assets"
    )
    affected_departments: List[str] = Field(
        default_factory=list,
        description="Departments with affected assets"
    )

    # =========================================================================
    # Lifecycle
    # =========================================================================
    remediation_status: Optional[Literal[
        "open", "in_progress", "remediated", "accepted_risk", "false_positive"
    ]] = Field(
        default=None,
        description="Current remediation status"
    )
    assigned_to: Optional[str] = Field(
        default=None,
        description="Assigned owner/team"
    )
    sla_due_date: Optional[Union[str, datetime]] = Field(
        default=None,
        description="SLA due date (ISO 8601)"
    )
    sla_status: Optional[Literal["on_track", "at_risk", "overdue"]] = Field(
        default=None,
        description="Current SLA status"
    )
    ticket_id: Optional[str] = Field(
        default=None,
        description="Associated ticket ID (e.g., 'JIRA-SEC-1234')"
    )

    # =========================================================================
    # Enrichment Metadata
    # =========================================================================
    enrichment_level: Optional[Literal["basic", "partial", "rich", "full"]] = Field(
        default=None,
        description="Current enrichment level"
    )
    enrichment_sources: List[str] = Field(
        default_factory=list,
        description="Sources used for enrichment"
    )
    last_enriched_at: Optional[Union[str, datetime]] = Field(
        default=None,
        description="Last enrichment timestamp (ISO 8601)"
    )
