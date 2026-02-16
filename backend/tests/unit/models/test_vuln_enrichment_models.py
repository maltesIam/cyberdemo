"""
Unit tests for Vulnerability Enrichment Pydantic models.

These tests follow TDD - they are written BEFORE the implementation.
Tests cover serialization, validation, and model constraints for EnrichedCVE
and all related subentities.

Based on VULNERABILITY_ENRICHMENT_BUILD_PLAN.md Section 3.
"""
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
import json


# =============================================================================
# ExploitRef Subentity Tests
# =============================================================================

class TestExploitRefModel:
    """Tests for ExploitRef subentity model."""

    def test_exploit_ref_creation(self):
        """Test creating ExploitRef with all fields."""
        from src.models.vuln_enrichment_models import ExploitRef

        exploit = ExploitRef(
            source="exploitdb",
            exploit_id="EDB-51234",
            title="Apache Struts Remote Code Execution",
            type="remote",
            platform="linux",
            verified=True,
            url="https://www.exploit-db.com/exploits/51234",
            date_published="2024-01-15T00:00:00Z"
        )

        assert exploit.source == "exploitdb"
        assert exploit.exploit_id == "EDB-51234"
        assert exploit.title == "Apache Struts Remote Code Execution"
        assert exploit.type == "remote"
        assert exploit.platform == "linux"
        assert exploit.verified is True
        assert "exploit-db.com" in exploit.url

    def test_exploit_ref_with_datetime_object(self):
        """Test ExploitRef accepts datetime object for date_published."""
        from src.models.vuln_enrichment_models import ExploitRef

        now = datetime.now(timezone.utc)
        exploit = ExploitRef(
            source="metasploit",
            exploit_id="exploit/multi/http/struts2_content_type_ognl",
            title="Apache Struts 2 OGNL Injection",
            type="remote",
            platform="multi",
            verified=True,
            url="https://github.com/rapid7/metasploit-framework",
            date_published=now
        )

        assert exploit.date_published is not None

    def test_exploit_ref_serialization(self):
        """Test ExploitRef serializes to dict correctly."""
        from src.models.vuln_enrichment_models import ExploitRef

        exploit = ExploitRef(
            source="nuclei",
            exploit_id="CVE-2024-1234",
            title="Test Vulnerability Scanner",
            type="webapps",
            platform="any",
            verified=True,
            url="https://github.com/projectdiscovery/nuclei-templates",
            date_published="2024-02-01T00:00:00Z"
        )

        data = exploit.model_dump()

        assert isinstance(data, dict)
        assert data["source"] == "nuclei"
        assert data["verified"] is True

    def test_exploit_ref_json_serialization(self):
        """Test ExploitRef serializes to JSON string."""
        from src.models.vuln_enrichment_models import ExploitRef

        exploit = ExploitRef(
            source="github_poc",
            exploit_id="gh-12345",
            title="PoC for CVE-2024-9999",
            type="local",
            platform="windows",
            verified=False,
            url="https://github.com/user/poc-cve-2024-9999",
            date_published="2024-03-01T00:00:00Z"
        )

        json_str = exploit.model_dump_json()
        assert isinstance(json_str, str)

        parsed = json.loads(json_str)
        assert parsed["source"] == "github_poc"
        assert parsed["verified"] is False


# =============================================================================
# PackageRef Subentity Tests
# =============================================================================

class TestPackageRefModel:
    """Tests for PackageRef subentity model."""

    def test_package_ref_creation(self):
        """Test creating PackageRef with all fields."""
        from src.models.vuln_enrichment_models import PackageRef

        package = PackageRef(
            ecosystem="npm",
            package_name="lodash",
            vulnerable_versions="<4.17.21",
            patched_version="4.17.21",
            ghsa_id="GHSA-jf85-cpcp-j695"
        )

        assert package.ecosystem == "npm"
        assert package.package_name == "lodash"
        assert package.vulnerable_versions == "<4.17.21"
        assert package.patched_version == "4.17.21"
        assert package.ghsa_id == "GHSA-jf85-cpcp-j695"

    def test_package_ref_with_optional_ghsa_id(self):
        """Test PackageRef with optional ghsa_id as None."""
        from src.models.vuln_enrichment_models import PackageRef

        package = PackageRef(
            ecosystem="pip",
            package_name="django",
            vulnerable_versions="<3.2.5",
            patched_version="3.2.5"
        )

        assert package.ecosystem == "pip"
        assert package.package_name == "django"
        assert package.ghsa_id is None

    def test_package_ref_serialization(self):
        """Test PackageRef serializes to dict."""
        from src.models.vuln_enrichment_models import PackageRef

        package = PackageRef(
            ecosystem="maven",
            package_name="org.apache.struts:struts2-core",
            vulnerable_versions="<2.5.30",
            patched_version="2.5.30",
            ghsa_id="GHSA-wxyz-1234"
        )

        data = package.model_dump()
        assert data["ecosystem"] == "maven"
        assert data["package_name"] == "org.apache.struts:struts2-core"


# =============================================================================
# VendorAdvisory Subentity Tests
# =============================================================================

class TestVendorAdvisoryModel:
    """Tests for VendorAdvisory subentity model."""

    def test_vendor_advisory_creation(self):
        """Test creating VendorAdvisory with all fields."""
        from src.models.vuln_enrichment_models import VendorAdvisory

        advisory = VendorAdvisory(
            vendor="Microsoft",
            advisory_id="MSRC-CVE-2024-1234",
            patch_url="https://msrc.microsoft.com/update-guide/vulnerability/CVE-2024-1234",
            patch_date="2024-02-13T00:00:00Z",
            workaround="Disable affected service until patch is applied",
            severity_vendor="Critical"
        )

        assert advisory.vendor == "Microsoft"
        assert advisory.advisory_id == "MSRC-CVE-2024-1234"
        assert "msrc.microsoft.com" in advisory.patch_url
        assert advisory.workaround is not None
        assert advisory.severity_vendor == "Critical"

    def test_vendor_advisory_with_optional_workaround(self):
        """Test VendorAdvisory with optional workaround as None."""
        from src.models.vuln_enrichment_models import VendorAdvisory

        advisory = VendorAdvisory(
            vendor="Apache",
            advisory_id="ASF-2024-001",
            patch_url="https://apache.org/security/advisories",
            patch_date="2024-01-20T00:00:00Z",
            severity_vendor="High"
        )

        assert advisory.vendor == "Apache"
        assert advisory.workaround is None

    def test_vendor_advisory_with_datetime_object(self):
        """Test VendorAdvisory accepts datetime object for patch_date."""
        from src.models.vuln_enrichment_models import VendorAdvisory

        now = datetime.now(timezone.utc)
        advisory = VendorAdvisory(
            vendor="Red Hat",
            advisory_id="RHSA-2024:1234",
            patch_url="https://access.redhat.com/errata/RHSA-2024:1234",
            patch_date=now,
            severity_vendor="Important"
        )

        assert advisory.patch_date is not None

    def test_vendor_advisory_serialization(self):
        """Test VendorAdvisory serializes to dict."""
        from src.models.vuln_enrichment_models import VendorAdvisory

        advisory = VendorAdvisory(
            vendor="Ubuntu",
            advisory_id="USN-5678-1",
            patch_url="https://ubuntu.com/security/notices/USN-5678-1",
            patch_date="2024-03-01T00:00:00Z",
            severity_vendor="Medium"
        )

        data = advisory.model_dump()
        assert data["vendor"] == "Ubuntu"
        assert data["advisory_id"] == "USN-5678-1"


# =============================================================================
# ThreatActorRef Subentity Tests
# =============================================================================

class TestThreatActorRefModel:
    """Tests for ThreatActorRef subentity model."""

    def test_threat_actor_ref_creation(self):
        """Test creating ThreatActorRef with all fields."""
        from src.models.vuln_enrichment_models import ThreatActorRef

        actor = ThreatActorRef(
            name="APT29",
            aliases=["Cozy Bear", "The Dukes", "YTTRIUM"],
            country="Russia",
            motivation="espionage",
            sophistication="high"
        )

        assert actor.name == "APT29"
        assert "Cozy Bear" in actor.aliases
        assert actor.country == "Russia"
        assert actor.motivation == "espionage"
        assert actor.sophistication == "high"

    def test_threat_actor_ref_with_empty_aliases(self):
        """Test ThreatActorRef with empty aliases list."""
        from src.models.vuln_enrichment_models import ThreatActorRef

        actor = ThreatActorRef(
            name="Unknown Actor",
            aliases=[],
            country="Unknown",
            motivation="unknown",
            sophistication="low"
        )

        assert actor.name == "Unknown Actor"
        assert actor.aliases == []

    def test_threat_actor_ref_serialization(self):
        """Test ThreatActorRef serializes to dict."""
        from src.models.vuln_enrichment_models import ThreatActorRef

        actor = ThreatActorRef(
            name="Lazarus Group",
            aliases=["Hidden Cobra", "Guardians of Peace"],
            country="North Korea",
            motivation="financial",
            sophistication="advanced"
        )

        data = actor.model_dump()
        assert data["name"] == "Lazarus Group"
        assert "Hidden Cobra" in data["aliases"]
        assert data["country"] == "North Korea"


# =============================================================================
# AffectedAsset Subentity Tests
# =============================================================================

class TestAffectedAssetModel:
    """Tests for AffectedAsset subentity model."""

    def test_affected_asset_creation(self):
        """Test creating AffectedAsset with all fields."""
        from src.models.vuln_enrichment_models import AffectedAsset

        asset = AffectedAsset(
            asset_id="asset-12345",
            hostname="web-server-01.company.com",
            ip="10.0.1.50",
            asset_type="server",
            criticality="high",
            department="IT Infrastructure",
            installed_version="2.5.29",
            patched=False,
            last_scanned="2024-02-15T10:30:00Z"
        )

        assert asset.asset_id == "asset-12345"
        assert asset.hostname == "web-server-01.company.com"
        assert asset.ip == "10.0.1.50"
        assert asset.asset_type == "server"
        assert asset.criticality == "high"
        assert asset.department == "IT Infrastructure"
        assert asset.installed_version == "2.5.29"
        assert asset.patched is False

    def test_affected_asset_with_datetime_object(self):
        """Test AffectedAsset accepts datetime object for last_scanned."""
        from src.models.vuln_enrichment_models import AffectedAsset

        now = datetime.now(timezone.utc)
        asset = AffectedAsset(
            asset_id="asset-67890",
            hostname="db-primary.company.com",
            ip="10.0.2.100",
            asset_type="database",
            criticality="critical",
            department="Database",
            installed_version="15.2",
            patched=True,
            last_scanned=now
        )

        assert asset.last_scanned is not None
        assert asset.patched is True

    def test_affected_asset_serialization(self):
        """Test AffectedAsset serializes to dict."""
        from src.models.vuln_enrichment_models import AffectedAsset

        asset = AffectedAsset(
            asset_id="asset-abc",
            hostname="app-server-02",
            ip="192.168.1.10",
            asset_type="application",
            criticality="medium",
            department="Development",
            installed_version="1.0.0",
            patched=False,
            last_scanned="2024-02-10T00:00:00Z"
        )

        data = asset.model_dump()
        assert data["asset_id"] == "asset-abc"
        assert data["patched"] is False


# =============================================================================
# EnrichedCVE Main Entity Tests
# =============================================================================

class TestEnrichedCVEModel:
    """Tests for the main EnrichedCVE model."""

    def test_enriched_cve_creation(self):
        """Test creating EnrichedCVE with all required fields."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        cve = EnrichedCVE(
            cve_id="CVE-2024-1234",
            title="Remote Code Execution in Apache Struts",
            description="A vulnerability in Apache Struts allows remote code execution.",
            published_date="2024-01-15T00:00:00Z",
            last_modified_date="2024-02-10T00:00:00Z",
            cvss_v3_score=9.8,
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
            epss_score=0.972,
            epss_percentile=0.997,
            risk_score=95.5,
            severity="Critical",
            is_kev=True,
            ssvc_decision="Act"
        )

        assert cve.cve_id == "CVE-2024-1234"
        assert cve.title == "Remote Code Execution in Apache Struts"
        assert cve.cvss_v3_score == 9.8
        assert cve.epss_score == 0.972
        assert cve.risk_score == 95.5
        assert cve.severity == "Critical"
        assert cve.is_kev is True
        assert cve.ssvc_decision == "Act"

    def test_enriched_cve_with_all_fields(self):
        """Test creating EnrichedCVE with ALL 50+ fields."""
        from src.models.vuln_enrichment_models import (
            EnrichedCVE, ExploitRef, PackageRef, VendorAdvisory,
            ThreatActorRef, AffectedAsset
        )

        cve = EnrichedCVE(
            # Core (NVD)
            cve_id="CVE-2024-5678",
            title="SQL Injection in Product X",
            description="SQL injection vulnerability allows data exfiltration.",
            published_date="2024-02-01T00:00:00Z",
            last_modified_date="2024-02-15T00:00:00Z",

            # Scoring
            cvss_v3_score=8.8,
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H",
            cvss_v2_score=7.5,
            epss_score=0.456,
            epss_percentile=0.89,
            risk_score=78.3,

            # Classification
            severity="High",
            cwe_ids=["CWE-89", "CWE-20"],
            cwe_names=["SQL Injection", "Improper Input Validation"],
            cpe_uris=["cpe:2.3:a:vendor:product:1.0:*:*:*:*:*:*:*"],

            # KEV (CISA)
            is_kev=True,
            kev_date_added="2024-02-10T00:00:00Z",
            kev_due_date="2024-03-01T00:00:00Z",
            kev_required_action="Apply vendor patch immediately",
            kev_ransomware_use=True,

            # Exploit Intelligence
            exploit_count=5,
            exploit_sources=[
                ExploitRef(
                    source="exploitdb",
                    exploit_id="EDB-99999",
                    title="Product X SQLi Exploit",
                    type="webapps",
                    platform="any",
                    verified=True,
                    url="https://www.exploit-db.com/exploits/99999",
                    date_published="2024-02-05T00:00:00Z"
                )
            ],
            exploit_maturity="weaponized",
            has_nuclei_template=True,
            nuclei_template_id="CVE-2024-5678",

            # SSVC Decision
            ssvc_decision="Act",
            ssvc_exploitation="active",
            ssvc_automatable=True,
            ssvc_technical_impact="total",
            ssvc_mission_prevalence="essential",

            # Open Source Context
            affected_packages=[
                PackageRef(
                    ecosystem="npm",
                    package_name="affected-lib",
                    vulnerable_versions="<2.0.0",
                    patched_version="2.0.0",
                    ghsa_id="GHSA-1234-5678"
                )
            ],
            patched_versions=["2.0.0", "2.0.1"],
            vulnerable_ranges=["<2.0.0"],
            ecosystems=["npm", "pip"],

            # Internet Exposure (Shodan)
            shodan_exposed_count=15000,
            shodan_countries=["US", "CN", "DE", "RU", "BR"],
            shodan_top_ports=[80, 443, 8080, 8443],

            # Vendor Patches
            vendor_advisories=[
                VendorAdvisory(
                    vendor="Product Vendor",
                    advisory_id="VENDOR-2024-001",
                    patch_url="https://vendor.com/security/advisories/2024-001",
                    patch_date="2024-02-12T00:00:00Z",
                    workaround="Disable module X",
                    severity_vendor="Critical"
                )
            ],
            patch_available=True,
            patch_url="https://vendor.com/downloads/patch-2.0.0",
            workaround_available=True,
            product_eol=False,

            # ATT&CK Context
            mitre_techniques=["T1190", "T1133"],
            mitre_tactics=["TA0001", "TA0006"],
            typical_actors=["APT28", "FIN7"],

            # Threat Intel
            threat_actors=[
                ThreatActorRef(
                    name="APT28",
                    aliases=["Fancy Bear", "Sofacy"],
                    country="Russia",
                    motivation="espionage",
                    sophistication="advanced"
                )
            ],
            malware_families=["Cobalt Strike", "Mimikatz"],
            campaigns=["Operation Silent Wolf"],
            exploitation_activity="high",
            trending=True,

            # Asset Impact (local)
            affected_asset_count=125,
            affected_critical_assets=15,
            affected_departments=["IT", "Finance", "HR"],

            # Lifecycle
            remediation_status="in_progress",
            assigned_to="security-team@company.com",
            sla_due_date="2024-02-28T23:59:59Z",
            sla_status="at_risk",
            ticket_id="JIRA-SEC-1234",

            # Enrichment Metadata
            enrichment_level="full",
            enrichment_sources=["nvd", "epss", "kev", "exploitdb", "shodan", "mitre"],
            last_enriched_at="2024-02-16T10:45:32Z"
        )

        # Verify core fields
        assert cve.cve_id == "CVE-2024-5678"
        assert cve.cvss_v3_score == 8.8
        assert cve.cvss_v2_score == 7.5

        # Verify KEV fields
        assert cve.is_kev is True
        assert cve.kev_ransomware_use is True

        # Verify exploit fields
        assert cve.exploit_count == 5
        assert len(cve.exploit_sources) == 1
        assert cve.exploit_maturity == "weaponized"

        # Verify SSVC fields
        assert cve.ssvc_decision == "Act"
        assert cve.ssvc_automatable is True

        # Verify package fields
        assert len(cve.affected_packages) == 1
        assert "npm" in cve.ecosystems

        # Verify Shodan fields
        assert cve.shodan_exposed_count == 15000
        assert "US" in cve.shodan_countries

        # Verify vendor fields
        assert len(cve.vendor_advisories) == 1
        assert cve.patch_available is True

        # Verify threat intel fields
        assert len(cve.threat_actors) == 1
        assert cve.trending is True

        # Verify lifecycle fields
        assert cve.remediation_status == "in_progress"
        assert cve.sla_status == "at_risk"

        # Verify enrichment fields
        assert cve.enrichment_level == "full"
        assert "nvd" in cve.enrichment_sources

    def test_enriched_cve_serialization(self):
        """Test EnrichedCVE serializes to dict correctly."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        cve = EnrichedCVE(
            cve_id="CVE-2024-0001",
            title="Test Vulnerability",
            description="Test description",
            published_date="2024-01-01T00:00:00Z",
            last_modified_date="2024-01-15T00:00:00Z",
            cvss_v3_score=7.5,
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
            epss_score=0.123,
            epss_percentile=0.456,
            risk_score=65.0,
            severity="High",
            is_kev=False,
            ssvc_decision="Track*"
        )

        data = cve.model_dump()

        assert isinstance(data, dict)
        assert data["cve_id"] == "CVE-2024-0001"
        assert data["cvss_v3_score"] == 7.5
        assert data["is_kev"] is False
        assert data["ssvc_decision"] == "Track*"

    def test_enriched_cve_json_conversion(self):
        """Test EnrichedCVE serializes to JSON string."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        cve = EnrichedCVE(
            cve_id="CVE-2024-0002",
            title="JSON Test Vulnerability",
            description="Testing JSON serialization",
            published_date="2024-02-01T00:00:00Z",
            last_modified_date="2024-02-15T00:00:00Z",
            cvss_v3_score=5.5,
            cvss_v3_vector="CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N",
            epss_score=0.05,
            epss_percentile=0.30,
            risk_score=45.0,
            severity="Medium",
            is_kev=False,
            ssvc_decision="Track"
        )

        json_str = cve.model_dump_json()

        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["cve_id"] == "CVE-2024-0002"
        assert parsed["severity"] == "Medium"
        assert parsed["ssvc_decision"] == "Track"


# =============================================================================
# Validation Tests
# =============================================================================

class TestSeverityValidation:
    """Tests for severity field validation."""

    def test_severity_validation_valid_values(self):
        """Test severity accepts only Critical/High/Medium/Low."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        for severity in ["Critical", "High", "Medium", "Low"]:
            cve = EnrichedCVE(
                cve_id="CVE-2024-TEST",
                title="Test",
                description="Test",
                published_date="2024-01-01T00:00:00Z",
                last_modified_date="2024-01-15T00:00:00Z",
                cvss_v3_score=5.0,
                cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L",
                epss_score=0.01,
                epss_percentile=0.10,
                risk_score=50.0,
                severity=severity,
                is_kev=False,
                ssvc_decision="Track"
            )
            assert cve.severity == severity

    def test_severity_validation_invalid_value(self):
        """Test severity rejects invalid values."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        with pytest.raises(ValidationError):
            EnrichedCVE(
                cve_id="CVE-2024-TEST",
                title="Test",
                description="Test",
                published_date="2024-01-01T00:00:00Z",
                last_modified_date="2024-01-15T00:00:00Z",
                cvss_v3_score=5.0,
                cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L",
                epss_score=0.01,
                epss_percentile=0.10,
                risk_score=50.0,
                severity="invalid_severity",  # Invalid
                is_kev=False,
                ssvc_decision="Track"
            )


class TestSSVCDecisionValidation:
    """Tests for SSVC decision field validation."""

    def test_ssvc_decision_validation_valid_values(self):
        """Test ssvc_decision accepts only Act/Attend/Track*/Track."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        for decision in ["Act", "Attend", "Track*", "Track"]:
            cve = EnrichedCVE(
                cve_id="CVE-2024-SSVC",
                title="Test",
                description="Test",
                published_date="2024-01-01T00:00:00Z",
                last_modified_date="2024-01-15T00:00:00Z",
                cvss_v3_score=5.0,
                cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L",
                epss_score=0.01,
                epss_percentile=0.10,
                risk_score=50.0,
                severity="Medium",
                is_kev=False,
                ssvc_decision=decision
            )
            assert cve.ssvc_decision == decision

    def test_ssvc_decision_validation_invalid_value(self):
        """Test ssvc_decision rejects invalid values."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        with pytest.raises(ValidationError):
            EnrichedCVE(
                cve_id="CVE-2024-SSVC",
                title="Test",
                description="Test",
                published_date="2024-01-01T00:00:00Z",
                last_modified_date="2024-01-15T00:00:00Z",
                cvss_v3_score=5.0,
                cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L",
                epss_score=0.01,
                epss_percentile=0.10,
                risk_score=50.0,
                severity="Medium",
                is_kev=False,
                ssvc_decision="Invalid"  # Invalid SSVC decision
            )


class TestExploitMaturityValidation:
    """Tests for exploit_maturity field validation."""

    def test_exploit_maturity_validation_valid_values(self):
        """Test exploit_maturity accepts only weaponized/poc/unproven/none."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        for maturity in ["weaponized", "poc", "unproven", "none"]:
            cve = EnrichedCVE(
                cve_id="CVE-2024-EXPLOIT",
                title="Test",
                description="Test",
                published_date="2024-01-01T00:00:00Z",
                last_modified_date="2024-01-15T00:00:00Z",
                cvss_v3_score=7.0,
                cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                epss_score=0.50,
                epss_percentile=0.85,
                risk_score=70.0,
                severity="High",
                is_kev=False,
                ssvc_decision="Attend",
                exploit_maturity=maturity
            )
            assert cve.exploit_maturity == maturity

    def test_exploit_maturity_validation_invalid_value(self):
        """Test exploit_maturity rejects invalid values."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        with pytest.raises(ValidationError):
            EnrichedCVE(
                cve_id="CVE-2024-EXPLOIT",
                title="Test",
                description="Test",
                published_date="2024-01-01T00:00:00Z",
                last_modified_date="2024-01-15T00:00:00Z",
                cvss_v3_score=7.0,
                cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                epss_score=0.50,
                epss_percentile=0.85,
                risk_score=70.0,
                severity="High",
                is_kev=False,
                ssvc_decision="Attend",
                exploit_maturity="invalid_maturity"  # Invalid
            )


class TestSSVCExploitationValidation:
    """Tests for ssvc_exploitation field validation."""

    def test_ssvc_exploitation_valid_values(self):
        """Test ssvc_exploitation accepts only active/poc/none."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        for exploitation in ["active", "poc", "none"]:
            cve = EnrichedCVE(
                cve_id="CVE-2024-SSVC-EXP",
                title="Test",
                description="Test",
                published_date="2024-01-01T00:00:00Z",
                last_modified_date="2024-01-15T00:00:00Z",
                cvss_v3_score=7.0,
                cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                epss_score=0.50,
                epss_percentile=0.85,
                risk_score=70.0,
                severity="High",
                is_kev=False,
                ssvc_decision="Attend",
                ssvc_exploitation=exploitation
            )
            assert cve.ssvc_exploitation == exploitation


class TestSSVCTechnicalImpactValidation:
    """Tests for ssvc_technical_impact field validation."""

    def test_ssvc_technical_impact_valid_values(self):
        """Test ssvc_technical_impact accepts only total/partial."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        for impact in ["total", "partial"]:
            cve = EnrichedCVE(
                cve_id="CVE-2024-SSVC-TI",
                title="Test",
                description="Test",
                published_date="2024-01-01T00:00:00Z",
                last_modified_date="2024-01-15T00:00:00Z",
                cvss_v3_score=7.0,
                cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                epss_score=0.50,
                epss_percentile=0.85,
                risk_score=70.0,
                severity="High",
                is_kev=False,
                ssvc_decision="Attend",
                ssvc_technical_impact=impact
            )
            assert cve.ssvc_technical_impact == impact


class TestSSVCMissionPrevalenceValidation:
    """Tests for ssvc_mission_prevalence field validation."""

    def test_ssvc_mission_prevalence_valid_values(self):
        """Test ssvc_mission_prevalence accepts only essential/supportive/minimal."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        for prevalence in ["essential", "supportive", "minimal"]:
            cve = EnrichedCVE(
                cve_id="CVE-2024-SSVC-MP",
                title="Test",
                description="Test",
                published_date="2024-01-01T00:00:00Z",
                last_modified_date="2024-01-15T00:00:00Z",
                cvss_v3_score=7.0,
                cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                epss_score=0.50,
                epss_percentile=0.85,
                risk_score=70.0,
                severity="High",
                is_kev=False,
                ssvc_decision="Attend",
                ssvc_mission_prevalence=prevalence
            )
            assert cve.ssvc_mission_prevalence == prevalence


class TestExploitationActivityValidation:
    """Tests for exploitation_activity field validation."""

    def test_exploitation_activity_valid_values(self):
        """Test exploitation_activity accepts only none/low/medium/high/critical."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        for activity in ["none", "low", "medium", "high", "critical"]:
            cve = EnrichedCVE(
                cve_id="CVE-2024-EA",
                title="Test",
                description="Test",
                published_date="2024-01-01T00:00:00Z",
                last_modified_date="2024-01-15T00:00:00Z",
                cvss_v3_score=7.0,
                cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                epss_score=0.50,
                epss_percentile=0.85,
                risk_score=70.0,
                severity="High",
                is_kev=False,
                ssvc_decision="Attend",
                exploitation_activity=activity
            )
            assert cve.exploitation_activity == activity


class TestRemediationStatusValidation:
    """Tests for remediation_status field validation."""

    def test_remediation_status_valid_values(self):
        """Test remediation_status accepts valid values."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        for status in ["open", "in_progress", "remediated", "accepted_risk", "false_positive"]:
            cve = EnrichedCVE(
                cve_id="CVE-2024-RS",
                title="Test",
                description="Test",
                published_date="2024-01-01T00:00:00Z",
                last_modified_date="2024-01-15T00:00:00Z",
                cvss_v3_score=7.0,
                cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                epss_score=0.50,
                epss_percentile=0.85,
                risk_score=70.0,
                severity="High",
                is_kev=False,
                ssvc_decision="Attend",
                remediation_status=status
            )
            assert cve.remediation_status == status


class TestSLAStatusValidation:
    """Tests for sla_status field validation."""

    def test_sla_status_valid_values(self):
        """Test sla_status accepts only on_track/at_risk/overdue."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        for sla in ["on_track", "at_risk", "overdue"]:
            cve = EnrichedCVE(
                cve_id="CVE-2024-SLA",
                title="Test",
                description="Test",
                published_date="2024-01-01T00:00:00Z",
                last_modified_date="2024-01-15T00:00:00Z",
                cvss_v3_score=7.0,
                cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                epss_score=0.50,
                epss_percentile=0.85,
                risk_score=70.0,
                severity="High",
                is_kev=False,
                ssvc_decision="Attend",
                sla_status=sla
            )
            assert cve.sla_status == sla


class TestEnrichmentLevelValidation:
    """Tests for enrichment_level field validation."""

    def test_enrichment_level_valid_values(self):
        """Test enrichment_level accepts only basic/partial/rich/full."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        for level in ["basic", "partial", "rich", "full"]:
            cve = EnrichedCVE(
                cve_id="CVE-2024-EL",
                title="Test",
                description="Test",
                published_date="2024-01-01T00:00:00Z",
                last_modified_date="2024-01-15T00:00:00Z",
                cvss_v3_score=7.0,
                cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                epss_score=0.50,
                epss_percentile=0.85,
                risk_score=70.0,
                severity="High",
                is_kev=False,
                ssvc_decision="Attend",
                enrichment_level=level
            )
            assert cve.enrichment_level == level


# =============================================================================
# Optional Fields and Defaults Tests
# =============================================================================

class TestOptionalFieldsDefaultNone:
    """Tests for optional fields defaulting to None."""

    def test_optional_fields_default_none(self):
        """Test that optional fields default to None."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        cve = EnrichedCVE(
            cve_id="CVE-2024-OPT",
            title="Test",
            description="Test",
            published_date="2024-01-01T00:00:00Z",
            last_modified_date="2024-01-15T00:00:00Z",
            cvss_v3_score=7.0,
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
            epss_score=0.50,
            epss_percentile=0.85,
            risk_score=70.0,
            severity="High",
            is_kev=False,
            ssvc_decision="Attend"
        )

        # Optional datetime fields
        assert cve.kev_date_added is None
        assert cve.kev_due_date is None
        assert cve.sla_due_date is None

        # Optional string fields
        assert cve.cvss_v2_score is None
        assert cve.kev_required_action is None
        assert cve.nuclei_template_id is None
        assert cve.patch_url is None
        assert cve.assigned_to is None
        assert cve.ticket_id is None


class TestListFieldsDefaultEmpty:
    """Tests for list fields defaulting to empty lists."""

    def test_list_fields_default_empty(self):
        """Test that list fields default to empty lists."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        cve = EnrichedCVE(
            cve_id="CVE-2024-LIST",
            title="Test",
            description="Test",
            published_date="2024-01-01T00:00:00Z",
            last_modified_date="2024-01-15T00:00:00Z",
            cvss_v3_score=7.0,
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
            epss_score=0.50,
            epss_percentile=0.85,
            risk_score=70.0,
            severity="High",
            is_kev=False,
            ssvc_decision="Attend"
        )

        # Classification lists
        assert cve.cwe_ids == []
        assert cve.cwe_names == []
        assert cve.cpe_uris == []

        # Exploit lists
        assert cve.exploit_sources == []

        # Package lists
        assert cve.affected_packages == []
        assert cve.patched_versions == []
        assert cve.vulnerable_ranges == []
        assert cve.ecosystems == []

        # Shodan lists
        assert cve.shodan_countries == []
        assert cve.shodan_top_ports == []

        # Vendor lists
        assert cve.vendor_advisories == []

        # MITRE lists
        assert cve.mitre_techniques == []
        assert cve.mitre_tactics == []
        assert cve.typical_actors == []

        # Threat intel lists
        assert cve.threat_actors == []
        assert cve.malware_families == []
        assert cve.campaigns == []

        # Asset lists
        assert cve.affected_departments == []

        # Enrichment lists
        assert cve.enrichment_sources == []


class TestBooleanFieldsDefaults:
    """Tests for boolean fields having correct defaults."""

    def test_boolean_fields_defaults(self):
        """Test that boolean fields have correct default values."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        cve = EnrichedCVE(
            cve_id="CVE-2024-BOOL",
            title="Test",
            description="Test",
            published_date="2024-01-01T00:00:00Z",
            last_modified_date="2024-01-15T00:00:00Z",
            cvss_v3_score=7.0,
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
            epss_score=0.50,
            epss_percentile=0.85,
            risk_score=70.0,
            severity="High",
            is_kev=False,
            ssvc_decision="Attend"
        )

        # KEV booleans
        assert cve.kev_ransomware_use is False

        # Exploit booleans
        assert cve.has_nuclei_template is False

        # SSVC booleans
        assert cve.ssvc_automatable is False

        # Vendor booleans
        assert cve.patch_available is False
        assert cve.workaround_available is False
        assert cve.product_eol is False

        # Threat intel booleans
        assert cve.trending is False


class TestIntegerFieldsDefaults:
    """Tests for integer fields having correct defaults."""

    def test_integer_fields_defaults(self):
        """Test that integer fields have correct default values."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        cve = EnrichedCVE(
            cve_id="CVE-2024-INT",
            title="Test",
            description="Test",
            published_date="2024-01-01T00:00:00Z",
            last_modified_date="2024-01-15T00:00:00Z",
            cvss_v3_score=7.0,
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
            epss_score=0.50,
            epss_percentile=0.85,
            risk_score=70.0,
            severity="High",
            is_kev=False,
            ssvc_decision="Attend"
        )

        # Exploit integers
        assert cve.exploit_count == 0

        # Shodan integers
        assert cve.shodan_exposed_count == 0

        # Asset integers
        assert cve.affected_asset_count == 0
        assert cve.affected_critical_assets == 0


# =============================================================================
# Edge Cases and Complex Scenarios
# =============================================================================

class TestEnrichedCVEWithDatetimeObjects:
    """Tests for EnrichedCVE with datetime objects."""

    def test_enriched_cve_with_datetime_objects(self):
        """Test EnrichedCVE accepts datetime objects for date fields."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        now = datetime.now(timezone.utc)
        cve = EnrichedCVE(
            cve_id="CVE-2024-DT",
            title="Test",
            description="Test",
            published_date=now,
            last_modified_date=now,
            cvss_v3_score=7.0,
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
            epss_score=0.50,
            epss_percentile=0.85,
            risk_score=70.0,
            severity="High",
            is_kev=True,
            kev_date_added=now,
            kev_due_date=now,
            ssvc_decision="Act",
            sla_due_date=now,
            last_enriched_at=now
        )

        assert cve.published_date is not None
        assert cve.last_modified_date is not None
        assert cve.kev_date_added is not None


class TestEnrichedCVEMinimalCreation:
    """Tests for creating EnrichedCVE with minimal required fields."""

    def test_enriched_cve_minimal_creation(self):
        """Test creating EnrichedCVE with only required fields."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        cve = EnrichedCVE(
            cve_id="CVE-2024-MIN",
            title="Minimal CVE",
            description="Minimal description",
            published_date="2024-01-01T00:00:00Z",
            last_modified_date="2024-01-15T00:00:00Z",
            cvss_v3_score=5.0,
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L",
            epss_score=0.01,
            epss_percentile=0.10,
            risk_score=30.0,
            severity="Medium",
            is_kev=False,
            ssvc_decision="Track"
        )

        assert cve.cve_id == "CVE-2024-MIN"
        # All optional fields should be at their defaults
        assert cve.exploit_count == 0
        assert cve.cwe_ids == []


class TestSubentityIndependentCreation:
    """Tests for creating subentities independently."""

    def test_exploit_ref_independent(self):
        """Test ExploitRef can be created independently."""
        from src.models.vuln_enrichment_models import ExploitRef

        exploit = ExploitRef(
            source="metasploit",
            exploit_id="exploit/linux/http/apache_struts2_ognl",
            title="Apache Struts 2 OGNL Injection",
            type="remote",
            platform="linux",
            verified=True,
            url="https://github.com/rapid7/metasploit-framework",
            date_published="2024-01-01T00:00:00Z"
        )

        data = exploit.model_dump()
        json_str = exploit.model_dump_json()

        assert data["source"] == "metasploit"
        assert isinstance(json_str, str)

    def test_package_ref_independent(self):
        """Test PackageRef can be created independently."""
        from src.models.vuln_enrichment_models import PackageRef

        package = PackageRef(
            ecosystem="go",
            package_name="github.com/vulnerable/package",
            vulnerable_versions="<1.0.0",
            patched_version="1.0.0"
        )

        data = package.model_dump()
        assert data["ecosystem"] == "go"

    def test_vendor_advisory_independent(self):
        """Test VendorAdvisory can be created independently."""
        from src.models.vuln_enrichment_models import VendorAdvisory

        advisory = VendorAdvisory(
            vendor="Cisco",
            advisory_id="cisco-sa-20240215-struts",
            patch_url="https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory",
            patch_date="2024-02-15T00:00:00Z",
            severity_vendor="High"
        )

        data = advisory.model_dump()
        assert data["vendor"] == "Cisco"

    def test_threat_actor_ref_independent(self):
        """Test ThreatActorRef can be created independently."""
        from src.models.vuln_enrichment_models import ThreatActorRef

        actor = ThreatActorRef(
            name="FIN7",
            aliases=["Carbanak", "Navigator Group"],
            country="Russia",
            motivation="financial",
            sophistication="advanced"
        )

        data = actor.model_dump()
        assert data["name"] == "FIN7"

    def test_affected_asset_independent(self):
        """Test AffectedAsset can be created independently."""
        from src.models.vuln_enrichment_models import AffectedAsset

        asset = AffectedAsset(
            asset_id="asset-xyz",
            hostname="server-01",
            ip="10.0.0.1",
            asset_type="server",
            criticality="high",
            department="Production",
            installed_version="1.0.0",
            patched=False,
            last_scanned="2024-02-16T00:00:00Z"
        )

        data = asset.model_dump()
        assert data["asset_id"] == "asset-xyz"
        assert data["patched"] is False


# =============================================================================
# Nested Subentities in EnrichedCVE Tests
# =============================================================================

class TestEnrichedCVEWithNestedSubentities:
    """Tests for EnrichedCVE with nested subentity lists."""

    def test_enriched_cve_with_multiple_exploit_refs(self):
        """Test EnrichedCVE with multiple ExploitRef objects."""
        from src.models.vuln_enrichment_models import EnrichedCVE, ExploitRef

        cve = EnrichedCVE(
            cve_id="CVE-2024-MULTI-EXP",
            title="Test Multiple Exploits",
            description="Test",
            published_date="2024-01-01T00:00:00Z",
            last_modified_date="2024-01-15T00:00:00Z",
            cvss_v3_score=9.8,
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
            epss_score=0.95,
            epss_percentile=0.99,
            risk_score=95.0,
            severity="Critical",
            is_kev=True,
            ssvc_decision="Act",
            exploit_count=3,
            exploit_sources=[
                ExploitRef(
                    source="exploitdb",
                    exploit_id="EDB-1",
                    title="Exploit 1",
                    type="remote",
                    platform="linux",
                    verified=True,
                    url="https://exploit-db.com/1",
                    date_published="2024-01-01T00:00:00Z"
                ),
                ExploitRef(
                    source="metasploit",
                    exploit_id="MSF-1",
                    title="Exploit 2",
                    type="remote",
                    platform="multi",
                    verified=True,
                    url="https://github.com/rapid7",
                    date_published="2024-01-05T00:00:00Z"
                ),
                ExploitRef(
                    source="nuclei",
                    exploit_id="CVE-2024-MULTI-EXP",
                    title="Nuclei Template",
                    type="webapps",
                    platform="any",
                    verified=True,
                    url="https://github.com/projectdiscovery",
                    date_published="2024-01-10T00:00:00Z"
                )
            ]
        )

        assert cve.exploit_count == 3
        assert len(cve.exploit_sources) == 3
        assert cve.exploit_sources[0].source == "exploitdb"
        assert cve.exploit_sources[1].source == "metasploit"
        assert cve.exploit_sources[2].source == "nuclei"

    def test_enriched_cve_with_multiple_packages(self):
        """Test EnrichedCVE with multiple PackageRef objects."""
        from src.models.vuln_enrichment_models import EnrichedCVE, PackageRef

        cve = EnrichedCVE(
            cve_id="CVE-2024-MULTI-PKG",
            title="Test Multiple Packages",
            description="Test",
            published_date="2024-01-01T00:00:00Z",
            last_modified_date="2024-01-15T00:00:00Z",
            cvss_v3_score=7.5,
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
            epss_score=0.50,
            epss_percentile=0.85,
            risk_score=70.0,
            severity="High",
            is_kev=False,
            ssvc_decision="Attend",
            affected_packages=[
                PackageRef(
                    ecosystem="npm",
                    package_name="vulnerable-pkg-1",
                    vulnerable_versions="<1.0.0",
                    patched_version="1.0.0"
                ),
                PackageRef(
                    ecosystem="pip",
                    package_name="vulnerable-pkg-2",
                    vulnerable_versions="<2.0.0",
                    patched_version="2.0.0",
                    ghsa_id="GHSA-1234"
                )
            ],
            ecosystems=["npm", "pip"]
        )

        assert len(cve.affected_packages) == 2
        assert cve.affected_packages[0].ecosystem == "npm"
        assert cve.affected_packages[1].ecosystem == "pip"
        assert len(cve.ecosystems) == 2


# =============================================================================
# Score Range Validation Tests
# =============================================================================

class TestScoreRangeValidation:
    """Tests for score field range validation."""

    def test_cvss_v3_score_range(self):
        """Test cvss_v3_score must be within 0.0-10.0."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        # Valid scores
        for score in [0.0, 5.0, 10.0]:
            cve = EnrichedCVE(
                cve_id="CVE-2024-CVSS",
                title="Test",
                description="Test",
                published_date="2024-01-01T00:00:00Z",
                last_modified_date="2024-01-15T00:00:00Z",
                cvss_v3_score=score,
                cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                epss_score=0.50,
                epss_percentile=0.85,
                risk_score=70.0,
                severity="High",
                is_kev=False,
                ssvc_decision="Attend"
            )
            assert cve.cvss_v3_score == score

    def test_epss_score_range(self):
        """Test epss_score must be within 0.0-1.0."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        # Valid scores
        for score in [0.0, 0.5, 1.0]:
            cve = EnrichedCVE(
                cve_id="CVE-2024-EPSS",
                title="Test",
                description="Test",
                published_date="2024-01-01T00:00:00Z",
                last_modified_date="2024-01-15T00:00:00Z",
                cvss_v3_score=7.0,
                cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                epss_score=score,
                epss_percentile=score,
                risk_score=70.0,
                severity="High",
                is_kev=False,
                ssvc_decision="Attend"
            )
            assert cve.epss_score == score

    def test_risk_score_range(self):
        """Test risk_score must be within 0.0-100.0."""
        from src.models.vuln_enrichment_models import EnrichedCVE

        # Valid scores
        for score in [0.0, 50.0, 100.0]:
            cve = EnrichedCVE(
                cve_id="CVE-2024-RISK",
                title="Test",
                description="Test",
                published_date="2024-01-01T00:00:00Z",
                last_modified_date="2024-01-15T00:00:00Z",
                cvss_v3_score=7.0,
                cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                epss_score=0.50,
                epss_percentile=0.85,
                risk_score=score,
                severity="High",
                is_kev=False,
                ssvc_decision="Attend"
            )
            assert cve.risk_score == score
