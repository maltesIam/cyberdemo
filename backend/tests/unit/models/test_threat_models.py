"""
Unit tests for Threat Enrichment Pydantic models.

These tests follow TDD - they are written BEFORE the implementation.
Tests cover serialization, validation, and model constraints.
"""
import pytest
from datetime import datetime, timezone
from typing import Optional
from pydantic import ValidationError
import json


class TestGeoLocationModel:
    """Tests for GeoLocation model."""

    def test_geo_location_creation_with_all_fields(self):
        """Test creating GeoLocation with all fields."""
        from src.models.threat_enrichment_models import GeoLocation

        geo = GeoLocation(
            country="US",
            country_name="United States",
            city="New York",
            region="New York",
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York"
        )

        assert geo.country == "US"
        assert geo.country_name == "United States"
        assert geo.city == "New York"
        assert geo.region == "New York"
        assert geo.latitude == 40.7128
        assert geo.longitude == -74.0060
        assert geo.timezone == "America/New_York"

    def test_geo_location_with_optional_fields(self):
        """Test GeoLocation with only required fields."""
        from src.models.threat_enrichment_models import GeoLocation

        geo = GeoLocation(
            country="RU",
            country_name="Russia"
        )

        assert geo.country == "RU"
        assert geo.country_name == "Russia"
        assert geo.city is None
        assert geo.region is None

    def test_geo_location_serialization(self):
        """Test GeoLocation serializes to dict correctly."""
        from src.models.threat_enrichment_models import GeoLocation

        geo = GeoLocation(
            country="CN",
            country_name="China",
            city="Beijing",
            latitude=39.9042,
            longitude=116.4074
        )

        data = geo.model_dump()

        assert isinstance(data, dict)
        assert data["country"] == "CN"
        assert data["latitude"] == 39.9042

    def test_geo_location_json_serialization(self):
        """Test GeoLocation serializes to JSON."""
        from src.models.threat_enrichment_models import GeoLocation

        geo = GeoLocation(
            country="DE",
            country_name="Germany",
            city="Berlin"
        )

        json_str = geo.model_dump_json()
        assert isinstance(json_str, str)

        # Verify it can be parsed back
        parsed = json.loads(json_str)
        assert parsed["country"] == "DE"


class TestNetworkInfoModel:
    """Tests for NetworkInfo model."""

    def test_network_info_creation(self):
        """Test creating NetworkInfo with all fields."""
        from src.models.threat_enrichment_models import NetworkInfo

        network = NetworkInfo(
            asn=16276,
            asn_org="OVH SAS",
            isp="OVH Hosting",
            company="OVH",
            is_vpn=False,
            is_proxy=True,
            is_tor=False,
            is_datacenter=True,
            is_mobile=False
        )

        assert network.asn == 16276
        assert network.asn_org == "OVH SAS"
        assert network.isp == "OVH Hosting"
        assert network.is_proxy is True
        assert network.is_datacenter is True

    def test_network_info_boolean_defaults(self):
        """Test NetworkInfo has proper boolean defaults."""
        from src.models.threat_enrichment_models import NetworkInfo

        network = NetworkInfo()

        assert network.is_vpn is False
        assert network.is_proxy is False
        assert network.is_tor is False
        assert network.is_datacenter is False
        assert network.is_mobile is False

    def test_network_info_serialization(self):
        """Test NetworkInfo serializes correctly."""
        from src.models.threat_enrichment_models import NetworkInfo

        network = NetworkInfo(
            asn=13335,
            asn_org="Cloudflare, Inc.",
            is_datacenter=True
        )

        data = network.model_dump()
        assert data["asn"] == 13335
        assert data["is_datacenter"] is True


class TestServiceInfoModel:
    """Tests for ServiceInfo model."""

    def test_service_info_creation(self):
        """Test creating ServiceInfo."""
        from src.models.threat_enrichment_models import ServiceInfo

        service = ServiceInfo(
            port=22,
            protocol="tcp",
            service="ssh",
            version="OpenSSH 8.2p1",
            banner="SSH-2.0-OpenSSH_8.2p1",
            cves=["CVE-2023-51385"]
        )

        assert service.port == 22
        assert service.protocol == "tcp"
        assert service.service == "ssh"
        assert "CVE-2023-51385" in service.cves

    def test_service_info_with_empty_cves(self):
        """Test ServiceInfo with no CVEs."""
        from src.models.threat_enrichment_models import ServiceInfo

        service = ServiceInfo(
            port=443,
            protocol="tcp",
            service="https"
        )

        assert service.port == 443
        assert service.cves == []


class TestAbuseIPDBReputationModel:
    """Tests for AbuseIPDB reputation sub-model."""

    def test_abuseipdb_reputation_creation(self):
        """Test creating AbuseIPDB reputation data."""
        from src.models.threat_enrichment_models import AbuseIPDBReputation

        rep = AbuseIPDBReputation(
            confidence_score=89,
            total_reports=234,
            last_reported="2026-02-16T10:00:00Z",
            abuse_categories=["SSH Brute Force", "Port Scan"]
        )

        assert rep.confidence_score == 89
        assert rep.total_reports == 234
        assert "SSH Brute Force" in rep.abuse_categories

    def test_abuseipdb_confidence_score_range(self):
        """Test confidence score must be 0-100."""
        from src.models.threat_enrichment_models import AbuseIPDBReputation

        # Valid scores
        rep1 = AbuseIPDBReputation(confidence_score=0)
        rep2 = AbuseIPDBReputation(confidence_score=100)

        assert rep1.confidence_score == 0
        assert rep2.confidence_score == 100


class TestGreyNoiseReputationModel:
    """Tests for GreyNoise reputation sub-model."""

    def test_greynoise_reputation_creation(self):
        """Test creating GreyNoise reputation data."""
        from src.models.threat_enrichment_models import GreyNoiseReputation

        rep = GreyNoiseReputation(
            classification="malicious",
            noise=True,
            riot=False,
            bot=True,
            vpn=False,
            actor="Unknown Scanner"
        )

        assert rep.classification == "malicious"
        assert rep.noise is True
        assert rep.riot is False
        assert rep.actor == "Unknown Scanner"

    def test_greynoise_classification_values(self):
        """Test classification must be valid value."""
        from src.models.threat_enrichment_models import GreyNoiseReputation

        # Valid classifications
        for cls in ["benign", "malicious", "unknown"]:
            rep = GreyNoiseReputation(classification=cls)
            assert rep.classification == cls


class TestVirusTotalReputationModel:
    """Tests for VirusTotal reputation sub-model."""

    def test_virustotal_reputation_creation(self):
        """Test creating VirusTotal reputation data."""
        from src.models.threat_enrichment_models import VirusTotalReputation

        rep = VirusTotalReputation(
            malicious_count=12,
            suspicious_count=3,
            harmless_count=65,
            undetected_count=9,
            community_score=-45,
            last_analysis_date="2026-02-15T14:32:00Z"
        )

        assert rep.malicious_count == 12
        assert rep.suspicious_count == 3
        assert rep.community_score == -45


class TestPulsediveReputationModel:
    """Tests for Pulsedive reputation sub-model."""

    def test_pulsedive_reputation_creation(self):
        """Test creating Pulsedive reputation data."""
        from src.models.threat_enrichment_models import PulsediveReputation

        rep = PulsediveReputation(
            risk="critical",
            risk_factors=["C2 Server", "Known Malicious"],
            feeds_count=15
        )

        assert rep.risk == "critical"
        assert "C2 Server" in rep.risk_factors
        assert rep.feeds_count == 15

    def test_pulsedive_risk_levels(self):
        """Test risk must be valid level."""
        from src.models.threat_enrichment_models import PulsediveReputation

        for level in ["critical", "high", "medium", "low", "unknown"]:
            rep = PulsediveReputation(risk=level)
            assert rep.risk == level


class TestReputationDataModel:
    """Tests for the aggregate ReputationData model."""

    def test_reputation_data_empty(self):
        """Test ReputationData with no sources."""
        from src.models.threat_enrichment_models import ReputationData

        rep = ReputationData()

        assert rep.abuseipdb is None
        assert rep.greynoise is None
        assert rep.virustotal is None
        assert rep.pulsedive is None

    def test_reputation_data_with_all_sources(self):
        """Test ReputationData with all reputation sources."""
        from src.models.threat_enrichment_models import (
            ReputationData, AbuseIPDBReputation, GreyNoiseReputation,
            VirusTotalReputation, PulsediveReputation
        )

        rep = ReputationData(
            abuseipdb=AbuseIPDBReputation(confidence_score=75),
            greynoise=GreyNoiseReputation(classification="malicious"),
            virustotal=VirusTotalReputation(malicious_count=10),
            pulsedive=PulsediveReputation(risk="high")
        )

        assert rep.abuseipdb.confidence_score == 75
        assert rep.greynoise.classification == "malicious"
        assert rep.virustotal.malicious_count == 10
        assert rep.pulsedive.risk == "high"


class TestThreatIntelDataModel:
    """Tests for ThreatIntelData model."""

    def test_threat_intel_data_creation(self):
        """Test creating ThreatIntelData."""
        from src.models.threat_enrichment_models import ThreatIntelData, MaliciousURL, DistributedMalware

        intel = ThreatIntelData(
            malware_families=["Emotet", "TrickBot", "Cobalt Strike"],
            threat_actors=["APT29", "Lazarus Group"],
            campaigns=["SolarWinds", "Log4Shell exploitation"],
            tags=["c2", "botnet", "phishing"],
            malicious_urls=[
                MaliciousURL(url="http://evil.com/mal.exe", threat="Trojan", date_added="2026-01-01")
            ],
            distributed_malware=[
                DistributedMalware(
                    hash="abc123def456",
                    hash_type="sha256",
                    malware_name="Emotet",
                    file_type="exe"
                )
            ]
        )

        assert "Emotet" in intel.malware_families
        assert "APT29" in intel.threat_actors
        assert len(intel.malicious_urls) == 1
        assert intel.distributed_malware[0].malware_name == "Emotet"

    def test_threat_intel_data_empty(self):
        """Test ThreatIntelData with empty lists."""
        from src.models.threat_enrichment_models import ThreatIntelData

        intel = ThreatIntelData()

        assert intel.malware_families == []
        assert intel.threat_actors == []
        assert intel.campaigns == []
        assert intel.tags == []


class TestMitreAttackDataModel:
    """Tests for MitreAttackData model."""

    def test_mitre_attack_data_creation(self):
        """Test creating MitreAttackData."""
        from src.models.threat_enrichment_models import MitreAttackData, MitreTactic, MitreTechnique, MitreSoftware

        mitre = MitreAttackData(
            tactics=[
                MitreTactic(id="TA0001", name="Initial Access")
            ],
            techniques=[
                MitreTechnique(
                    id="T1566.001",
                    name="Spearphishing Attachment",
                    data_sources=["Email Gateway", "Network Traffic"]
                )
            ],
            software=[
                MitreSoftware(id="S0154", name="Cobalt Strike")
            ]
        )

        assert mitre.tactics[0].id == "TA0001"
        assert mitre.techniques[0].name == "Spearphishing Attachment"
        assert mitre.software[0].name == "Cobalt Strike"

    def test_mitre_attack_data_serialization(self):
        """Test MitreAttackData serializes correctly."""
        from src.models.threat_enrichment_models import MitreAttackData, MitreTactic

        mitre = MitreAttackData(
            tactics=[MitreTactic(id="TA0002", name="Execution")]
        )

        data = mitre.model_dump()
        assert data["tactics"][0]["id"] == "TA0002"


class TestIntelFeedModel:
    """Tests for IntelFeed model."""

    def test_intel_feed_creation(self):
        """Test creating IntelFeed."""
        from src.models.threat_enrichment_models import IntelFeed

        feed = IntelFeed(
            source="AlienVault OTX",
            feed_name="Cobalt Strike C2 Infrastructure",
            feed_id="pulse-12345",
            description="Known Cobalt Strike C2 servers",
            created="2026-02-14T00:00:00Z",
            author="ThreatHunter42",
            tlp="amber",
            reference_urls=["https://example.com/report"]
        )

        assert feed.source == "AlienVault OTX"
        assert feed.tlp == "amber"
        assert "https://example.com/report" in feed.reference_urls

    def test_intel_feed_tlp_values(self):
        """Test TLP must be valid value."""
        from src.models.threat_enrichment_models import IntelFeed

        for tlp in ["white", "green", "amber", "red"]:
            feed = IntelFeed(
                source="test",
                feed_name="test",
                feed_id="1",
                tlp=tlp
            )
            assert feed.tlp == tlp


class TestBreachDataModel:
    """Tests for BreachData model."""

    def test_breach_data_creation(self):
        """Test creating BreachData."""
        from src.models.threat_enrichment_models import BreachData, Breach

        breach_data = BreachData(
            breached=True,
            breach_count=3,
            breaches=[
                Breach(
                    name="LinkedIn",
                    breach_date="2016-05-05",
                    pwn_count=164611595,
                    data_classes=["Email", "Password", "Phone"]
                )
            ],
            paste_count=5
        )

        assert breach_data.breached is True
        assert breach_data.breach_count == 3
        assert breach_data.breaches[0].name == "LinkedIn"
        assert "Email" in breach_data.breaches[0].data_classes

    def test_breach_data_not_breached(self):
        """Test BreachData for clean email."""
        from src.models.threat_enrichment_models import BreachData

        breach_data = BreachData(
            breached=False,
            breach_count=0,
            breaches=[],
            paste_count=0
        )

        assert breach_data.breached is False
        assert len(breach_data.breaches) == 0


class TestEnrichmentMetaModel:
    """Tests for EnrichmentMeta model."""

    def test_enrichment_meta_creation(self):
        """Test creating EnrichmentMeta."""
        from src.models.threat_enrichment_models import EnrichmentMeta

        meta = EnrichmentMeta(
            enriched_at="2026-02-16T10:45:32Z",
            sources_queried=["otx", "abuseipdb", "greynoise", "virustotal"],
            sources_successful=["otx", "abuseipdb", "greynoise"],
            sources_failed=["virustotal"],
            total_sources=4,
            successful_sources=3,
            cache_hit=False,
            processing_time_ms=2300
        )

        assert meta.total_sources == 4
        assert meta.successful_sources == 3
        assert meta.cache_hit is False
        assert meta.processing_time_ms == 2300

    def test_enrichment_meta_with_datetime(self):
        """Test EnrichmentMeta accepts datetime object."""
        from src.models.threat_enrichment_models import EnrichmentMeta

        now = datetime.now(timezone.utc)
        meta = EnrichmentMeta(
            enriched_at=now,
            sources_queried=[],
            sources_successful=[],
            sources_failed=[],
            total_sources=0,
            successful_sources=0
        )

        assert meta.enriched_at is not None


class TestRelationshipDataModel:
    """Tests for RelationshipData model."""

    def test_relationship_data_creation(self):
        """Test creating RelationshipData."""
        from src.models.threat_enrichment_models import RelationshipData, PassiveDNS, SSLCertificate

        relationships = RelationshipData(
            related_ips=["192.168.1.1", "10.0.0.1"],
            related_domains=["evil.com", "malware.net"],
            related_urls=["http://evil.com/payload.exe"],
            related_hashes=["abc123", "def456"],
            passive_dns=[
                PassiveDNS(
                    domain="evil.com",
                    ip="45.33.32.156",
                    first_seen="2026-01-01",
                    last_seen="2026-02-16"
                )
            ],
            ssl_certificates=[
                SSLCertificate(
                    sha256="a1b2c3d4e5f6",
                    issuer="Let's Encrypt",
                    subject="*.evil.com",
                    not_before="2025-01-01",
                    not_after="2026-01-01"
                )
            ]
        )

        assert "evil.com" in relationships.related_domains
        assert len(relationships.passive_dns) == 1
        assert relationships.ssl_certificates[0].issuer == "Let's Encrypt"


class TestEnrichedThreatIndicatorModel:
    """Tests for the main EnrichedThreatIndicator model."""

    def test_enriched_threat_indicator_ip_creation(self):
        """Test creating EnrichedThreatIndicator for IP."""
        from src.models.threat_enrichment_models import (
            EnrichedThreatIndicator, GeoLocation, NetworkInfo,
            ReputationData, ThreatIntelData, MitreAttackData,
            EnrichmentMeta, RelationshipData
        )

        indicator = EnrichedThreatIndicator(
            id="550e8400-e29b-41d4-a716-446655440000",
            type="ip",
            value="45.33.32.156",
            first_seen="2026-01-01T00:00:00Z",
            last_seen="2026-02-16T00:00:00Z",
            risk_score=92,
            risk_level="critical",
            confidence=85,
            geo=GeoLocation(country="RU", country_name="Russia", city="Moscow"),
            network=NetworkInfo(asn=16276, asn_org="OVH SAS"),
            reputation=ReputationData(),
            threat_intel=ThreatIntelData(malware_families=["Cobalt Strike"]),
            mitre_attack=MitreAttackData(),
            intel_feeds=[],
            enrichment_meta=EnrichmentMeta(
                enriched_at="2026-02-16T10:45:32Z",
                sources_queried=["otx"],
                sources_successful=["otx"],
                sources_failed=[],
                total_sources=1,
                successful_sources=1
            ),
            relationships=RelationshipData()
        )

        assert indicator.id == "550e8400-e29b-41d4-a716-446655440000"
        assert indicator.type == "ip"
        assert indicator.value == "45.33.32.156"
        assert indicator.risk_score == 92
        assert indicator.risk_level == "critical"
        assert indicator.geo.country == "RU"

    def test_enriched_threat_indicator_domain_creation(self):
        """Test creating EnrichedThreatIndicator for domain."""
        from src.models.threat_enrichment_models import (
            EnrichedThreatIndicator, ReputationData, ThreatIntelData,
            MitreAttackData, EnrichmentMeta, RelationshipData
        )

        indicator = EnrichedThreatIndicator(
            id="550e8400-e29b-41d4-a716-446655440001",
            type="domain",
            value="evil-malware.com",
            first_seen="2026-01-15T00:00:00Z",
            last_seen="2026-02-16T00:00:00Z",
            risk_score=78,
            risk_level="high",
            confidence=70,
            reputation=ReputationData(),
            threat_intel=ThreatIntelData(tags=["phishing", "malware"]),
            mitre_attack=MitreAttackData(),
            intel_feeds=[],
            enrichment_meta=EnrichmentMeta(
                enriched_at="2026-02-16T00:00:00Z",
                sources_queried=[],
                sources_successful=[],
                sources_failed=[],
                total_sources=0,
                successful_sources=0
            ),
            relationships=RelationshipData()
        )

        assert indicator.type == "domain"
        assert indicator.value == "evil-malware.com"
        assert indicator.risk_level == "high"

    def test_enriched_threat_indicator_hash_creation(self):
        """Test creating EnrichedThreatIndicator for hash."""
        from src.models.threat_enrichment_models import (
            EnrichedThreatIndicator, ReputationData, ThreatIntelData,
            MitreAttackData, EnrichmentMeta, RelationshipData
        )

        indicator = EnrichedThreatIndicator(
            id="550e8400-e29b-41d4-a716-446655440002",
            type="hash",
            value="d41d8cd98f00b204e9800998ecf8427e",
            first_seen="2026-02-01T00:00:00Z",
            last_seen="2026-02-16T00:00:00Z",
            risk_score=65,
            risk_level="high",
            confidence=80,
            reputation=ReputationData(),
            threat_intel=ThreatIntelData(malware_families=["Emotet"]),
            mitre_attack=MitreAttackData(),
            intel_feeds=[],
            enrichment_meta=EnrichmentMeta(
                enriched_at="2026-02-16T00:00:00Z",
                sources_queried=[],
                sources_successful=[],
                sources_failed=[],
                total_sources=0,
                successful_sources=0
            ),
            relationships=RelationshipData()
        )

        assert indicator.type == "hash"
        assert "Emotet" in indicator.threat_intel.malware_families

    def test_enriched_threat_indicator_type_validation(self):
        """Test that type must be one of the allowed values."""
        from src.models.threat_enrichment_models import (
            EnrichedThreatIndicator, ReputationData, ThreatIntelData,
            MitreAttackData, EnrichmentMeta, RelationshipData
        )

        # Valid types
        for ioc_type in ["ip", "domain", "url", "hash", "email", "cve"]:
            indicator = EnrichedThreatIndicator(
                id="test-id",
                type=ioc_type,
                value="test-value",
                first_seen="2026-01-01T00:00:00Z",
                last_seen="2026-02-16T00:00:00Z",
                risk_score=50,
                risk_level="medium",
                confidence=50,
                reputation=ReputationData(),
                threat_intel=ThreatIntelData(),
                mitre_attack=MitreAttackData(),
                intel_feeds=[],
                enrichment_meta=EnrichmentMeta(
                    enriched_at="2026-02-16T00:00:00Z",
                    sources_queried=[],
                    sources_successful=[],
                    sources_failed=[],
                    total_sources=0,
                    successful_sources=0
                ),
                relationships=RelationshipData()
            )
            assert indicator.type == ioc_type

    def test_enriched_threat_indicator_risk_level_validation(self):
        """Test that risk_level must be one of allowed values."""
        from src.models.threat_enrichment_models import (
            EnrichedThreatIndicator, ReputationData, ThreatIntelData,
            MitreAttackData, EnrichmentMeta, RelationshipData
        )

        # Valid risk levels
        for level in ["critical", "high", "medium", "low", "unknown"]:
            indicator = EnrichedThreatIndicator(
                id="test-id",
                type="ip",
                value="1.2.3.4",
                first_seen="2026-01-01T00:00:00Z",
                last_seen="2026-02-16T00:00:00Z",
                risk_score=50,
                risk_level=level,
                confidence=50,
                reputation=ReputationData(),
                threat_intel=ThreatIntelData(),
                mitre_attack=MitreAttackData(),
                intel_feeds=[],
                enrichment_meta=EnrichmentMeta(
                    enriched_at="2026-02-16T00:00:00Z",
                    sources_queried=[],
                    sources_successful=[],
                    sources_failed=[],
                    total_sources=0,
                    successful_sources=0
                ),
                relationships=RelationshipData()
            )
            assert indicator.risk_level == level

    def test_enriched_threat_indicator_serialization(self):
        """Test EnrichedThreatIndicator serializes to dict."""
        from src.models.threat_enrichment_models import (
            EnrichedThreatIndicator, GeoLocation, NetworkInfo,
            ReputationData, AbuseIPDBReputation, ThreatIntelData,
            MitreAttackData, MitreTactic, EnrichmentMeta, RelationshipData,
            IntelFeed
        )

        indicator = EnrichedThreatIndicator(
            id="test-serialize",
            type="ip",
            value="192.168.1.1",
            first_seen="2026-01-01T00:00:00Z",
            last_seen="2026-02-16T00:00:00Z",
            risk_score=85,
            risk_level="high",
            confidence=90,
            geo=GeoLocation(country="US", country_name="United States"),
            network=NetworkInfo(asn=12345, is_datacenter=True),
            reputation=ReputationData(
                abuseipdb=AbuseIPDBReputation(confidence_score=80)
            ),
            threat_intel=ThreatIntelData(malware_families=["TrickBot"]),
            mitre_attack=MitreAttackData(
                tactics=[MitreTactic(id="TA0001", name="Initial Access")]
            ),
            intel_feeds=[
                IntelFeed(
                    source="OTX",
                    feed_name="Test Feed",
                    feed_id="123",
                    tlp="green"
                )
            ],
            enrichment_meta=EnrichmentMeta(
                enriched_at="2026-02-16T00:00:00Z",
                sources_queried=["otx", "abuseipdb"],
                sources_successful=["otx", "abuseipdb"],
                sources_failed=[],
                total_sources=2,
                successful_sources=2,
                cache_hit=False,
                processing_time_ms=1500
            ),
            relationships=RelationshipData(
                related_ips=["10.0.0.1"],
                related_domains=["test.com"]
            )
        )

        data = indicator.model_dump()

        assert isinstance(data, dict)
        assert data["id"] == "test-serialize"
        assert data["type"] == "ip"
        assert data["risk_score"] == 85
        assert data["geo"]["country"] == "US"
        assert data["network"]["is_datacenter"] is True
        assert data["reputation"]["abuseipdb"]["confidence_score"] == 80
        assert "TrickBot" in data["threat_intel"]["malware_families"]
        assert data["mitre_attack"]["tactics"][0]["id"] == "TA0001"
        assert data["enrichment_meta"]["processing_time_ms"] == 1500

    def test_enriched_threat_indicator_json_serialization(self):
        """Test EnrichedThreatIndicator serializes to JSON string."""
        from src.models.threat_enrichment_models import (
            EnrichedThreatIndicator, ReputationData, ThreatIntelData,
            MitreAttackData, EnrichmentMeta, RelationshipData
        )

        indicator = EnrichedThreatIndicator(
            id="test-json",
            type="domain",
            value="test.com",
            first_seen="2026-01-01T00:00:00Z",
            last_seen="2026-02-16T00:00:00Z",
            risk_score=30,
            risk_level="low",
            confidence=60,
            reputation=ReputationData(),
            threat_intel=ThreatIntelData(),
            mitre_attack=MitreAttackData(),
            intel_feeds=[],
            enrichment_meta=EnrichmentMeta(
                enriched_at="2026-02-16T00:00:00Z",
                sources_queried=[],
                sources_successful=[],
                sources_failed=[],
                total_sources=0,
                successful_sources=0
            ),
            relationships=RelationshipData()
        )

        json_str = indicator.model_dump_json()

        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["value"] == "test.com"
        assert parsed["risk_level"] == "low"

    def test_enriched_threat_indicator_with_services(self):
        """Test EnrichedThreatIndicator with services field."""
        from src.models.threat_enrichment_models import (
            EnrichedThreatIndicator, ServiceInfo, ReputationData,
            ThreatIntelData, MitreAttackData, EnrichmentMeta, RelationshipData
        )

        indicator = EnrichedThreatIndicator(
            id="test-services",
            type="ip",
            value="10.0.0.1",
            first_seen="2026-01-01T00:00:00Z",
            last_seen="2026-02-16T00:00:00Z",
            risk_score=50,
            risk_level="medium",
            confidence=50,
            services=[
                ServiceInfo(port=22, protocol="tcp", service="ssh"),
                ServiceInfo(port=443, protocol="tcp", service="https", cves=["CVE-2024-1234"])
            ],
            reputation=ReputationData(),
            threat_intel=ThreatIntelData(),
            mitre_attack=MitreAttackData(),
            intel_feeds=[],
            enrichment_meta=EnrichmentMeta(
                enriched_at="2026-02-16T00:00:00Z",
                sources_queried=[],
                sources_successful=[],
                sources_failed=[],
                total_sources=0,
                successful_sources=0
            ),
            relationships=RelationshipData()
        )

        assert len(indicator.services) == 2
        assert indicator.services[0].port == 22
        assert "CVE-2024-1234" in indicator.services[1].cves

    def test_enriched_threat_indicator_with_breach_data(self):
        """Test EnrichedThreatIndicator with breach data for email type."""
        from src.models.threat_enrichment_models import (
            EnrichedThreatIndicator, ReputationData, ThreatIntelData,
            MitreAttackData, EnrichmentMeta, RelationshipData,
            BreachData, Breach
        )

        indicator = EnrichedThreatIndicator(
            id="test-breach",
            type="email",
            value="user@example.com",
            first_seen="2026-01-01T00:00:00Z",
            last_seen="2026-02-16T00:00:00Z",
            risk_score=40,
            risk_level="medium",
            confidence=70,
            breach_data=BreachData(
                breached=True,
                breach_count=2,
                breaches=[
                    Breach(name="LinkedIn", breach_date="2016-05-05", pwn_count=1000000)
                ],
                paste_count=3
            ),
            reputation=ReputationData(),
            threat_intel=ThreatIntelData(),
            mitre_attack=MitreAttackData(),
            intel_feeds=[],
            enrichment_meta=EnrichmentMeta(
                enriched_at="2026-02-16T00:00:00Z",
                sources_queried=["hibp"],
                sources_successful=["hibp"],
                sources_failed=[],
                total_sources=1,
                successful_sources=1
            ),
            relationships=RelationshipData()
        )

        assert indicator.type == "email"
        assert indicator.breach_data is not None
        assert indicator.breach_data.breached is True
        assert indicator.breach_data.breaches[0].name == "LinkedIn"

    def test_enriched_threat_indicator_risk_score_validation(self):
        """Test risk_score must be within 0-100."""
        from src.models.threat_enrichment_models import (
            EnrichedThreatIndicator, ReputationData, ThreatIntelData,
            MitreAttackData, EnrichmentMeta, RelationshipData
        )

        # Valid scores at boundaries
        for score in [0, 50, 100]:
            indicator = EnrichedThreatIndicator(
                id="test-score",
                type="ip",
                value="1.2.3.4",
                first_seen="2026-01-01T00:00:00Z",
                last_seen="2026-02-16T00:00:00Z",
                risk_score=score,
                risk_level="medium",
                confidence=50,
                reputation=ReputationData(),
                threat_intel=ThreatIntelData(),
                mitre_attack=MitreAttackData(),
                intel_feeds=[],
                enrichment_meta=EnrichmentMeta(
                    enriched_at="2026-02-16T00:00:00Z",
                    sources_queried=[],
                    sources_successful=[],
                    sources_failed=[],
                    total_sources=0,
                    successful_sources=0
                ),
                relationships=RelationshipData()
            )
            assert indicator.risk_score == score

    def test_enriched_threat_indicator_confidence_validation(self):
        """Test confidence must be within 0-100."""
        from src.models.threat_enrichment_models import (
            EnrichedThreatIndicator, ReputationData, ThreatIntelData,
            MitreAttackData, EnrichmentMeta, RelationshipData
        )

        # Valid confidence at boundaries
        for conf in [0, 50, 100]:
            indicator = EnrichedThreatIndicator(
                id="test-conf",
                type="ip",
                value="1.2.3.4",
                first_seen="2026-01-01T00:00:00Z",
                last_seen="2026-02-16T00:00:00Z",
                risk_score=50,
                risk_level="medium",
                confidence=conf,
                reputation=ReputationData(),
                threat_intel=ThreatIntelData(),
                mitre_attack=MitreAttackData(),
                intel_feeds=[],
                enrichment_meta=EnrichmentMeta(
                    enriched_at="2026-02-16T00:00:00Z",
                    sources_queried=[],
                    sources_successful=[],
                    sources_failed=[],
                    total_sources=0,
                    successful_sources=0
                ),
                relationships=RelationshipData()
            )
            assert indicator.confidence == conf


class TestModelValidationErrors:
    """Tests for validation error handling."""

    def test_invalid_type_raises_validation_error(self):
        """Test that invalid IOC type raises ValidationError."""
        from src.models.threat_enrichment_models import (
            EnrichedThreatIndicator, ReputationData, ThreatIntelData,
            MitreAttackData, EnrichmentMeta, RelationshipData
        )

        with pytest.raises(ValidationError):
            EnrichedThreatIndicator(
                id="test-invalid",
                type="invalid_type",  # Invalid type
                value="test",
                first_seen="2026-01-01T00:00:00Z",
                last_seen="2026-02-16T00:00:00Z",
                risk_score=50,
                risk_level="medium",
                confidence=50,
                reputation=ReputationData(),
                threat_intel=ThreatIntelData(),
                mitre_attack=MitreAttackData(),
                intel_feeds=[],
                enrichment_meta=EnrichmentMeta(
                    enriched_at="2026-02-16T00:00:00Z",
                    sources_queried=[],
                    sources_successful=[],
                    sources_failed=[],
                    total_sources=0,
                    successful_sources=0
                ),
                relationships=RelationshipData()
            )

    def test_invalid_risk_level_raises_validation_error(self):
        """Test that invalid risk level raises ValidationError."""
        from src.models.threat_enrichment_models import (
            EnrichedThreatIndicator, ReputationData, ThreatIntelData,
            MitreAttackData, EnrichmentMeta, RelationshipData
        )

        with pytest.raises(ValidationError):
            EnrichedThreatIndicator(
                id="test-invalid-risk",
                type="ip",
                value="1.2.3.4",
                first_seen="2026-01-01T00:00:00Z",
                last_seen="2026-02-16T00:00:00Z",
                risk_score=50,
                risk_level="invalid_level",  # Invalid risk level
                confidence=50,
                reputation=ReputationData(),
                threat_intel=ThreatIntelData(),
                mitre_attack=MitreAttackData(),
                intel_feeds=[],
                enrichment_meta=EnrichmentMeta(
                    enriched_at="2026-02-16T00:00:00Z",
                    sources_queried=[],
                    sources_successful=[],
                    sources_failed=[],
                    total_sources=0,
                    successful_sources=0
                ),
                relationships=RelationshipData()
            )

    def test_invalid_greynoise_classification_raises_error(self):
        """Test that invalid GreyNoise classification raises ValidationError."""
        from src.models.threat_enrichment_models import GreyNoiseReputation

        with pytest.raises(ValidationError):
            GreyNoiseReputation(classification="invalid_class")

    def test_invalid_tlp_raises_error(self):
        """Test that invalid TLP raises ValidationError."""
        from src.models.threat_enrichment_models import IntelFeed

        with pytest.raises(ValidationError):
            IntelFeed(
                source="test",
                feed_name="test",
                feed_id="1",
                tlp="invalid_tlp"  # Invalid TLP
            )

    def test_invalid_pulsedive_risk_raises_error(self):
        """Test that invalid Pulsedive risk raises ValidationError."""
        from src.models.threat_enrichment_models import PulsediveReputation

        with pytest.raises(ValidationError):
            PulsediveReputation(risk="invalid_risk")

    def test_negative_risk_score_raises_error(self):
        """Test that negative risk score raises ValidationError."""
        from src.models.threat_enrichment_models import (
            EnrichedThreatIndicator, ReputationData, ThreatIntelData,
            MitreAttackData, EnrichmentMeta, RelationshipData
        )

        with pytest.raises(ValidationError):
            EnrichedThreatIndicator(
                id="test-negative",
                type="ip",
                value="1.2.3.4",
                first_seen="2026-01-01T00:00:00Z",
                last_seen="2026-02-16T00:00:00Z",
                risk_score=-10,  # Invalid - negative
                risk_level="medium",
                confidence=50,
                reputation=ReputationData(),
                threat_intel=ThreatIntelData(),
                mitre_attack=MitreAttackData(),
                intel_feeds=[],
                enrichment_meta=EnrichmentMeta(
                    enriched_at="2026-02-16T00:00:00Z",
                    sources_queried=[],
                    sources_successful=[],
                    sources_failed=[],
                    total_sources=0,
                    successful_sources=0
                ),
                relationships=RelationshipData()
            )

    def test_risk_score_over_100_raises_error(self):
        """Test that risk score over 100 raises ValidationError."""
        from src.models.threat_enrichment_models import (
            EnrichedThreatIndicator, ReputationData, ThreatIntelData,
            MitreAttackData, EnrichmentMeta, RelationshipData
        )

        with pytest.raises(ValidationError):
            EnrichedThreatIndicator(
                id="test-over100",
                type="ip",
                value="1.2.3.4",
                first_seen="2026-01-01T00:00:00Z",
                last_seen="2026-02-16T00:00:00Z",
                risk_score=150,  # Invalid - over 100
                risk_level="medium",
                confidence=50,
                reputation=ReputationData(),
                threat_intel=ThreatIntelData(),
                mitre_attack=MitreAttackData(),
                intel_feeds=[],
                enrichment_meta=EnrichmentMeta(
                    enriched_at="2026-02-16T00:00:00Z",
                    sources_queried=[],
                    sources_successful=[],
                    sources_failed=[],
                    total_sources=0,
                    successful_sources=0
                ),
                relationships=RelationshipData()
            )
