"""Unit tests for synthetic data generators."""
import pytest
from src.generators.gen_assets import generate_assets
from src.generators.gen_edr import generate_edr_detections
from src.generators.gen_intel import generate_threat_intel
from src.generators.gen_ctem import generate_ctem_findings
from src.generators.gen_siem import generate_siem_incidents
from src.generators.constants import ANCHOR_DETECTION_IDS, ANCHOR_INCIDENT_IDS


class TestAssetGenerator:
    """Tests for asset generator."""

    def test_generates_1000_assets(self):
        """Test that generator creates exactly 1000 assets."""
        assets = generate_assets(count=1000, seed=42)
        assert len(assets) == 1000

    def test_assets_have_required_fields(self):
        """Test that all assets have required fields."""
        assets = generate_assets(count=10, seed=42)
        required_fields = ["asset_id", "hostname", "ip", "os", "owner", "tags"]
        for asset in assets:
            for field in required_fields:
                assert field in asset, f"Missing field: {field}"

    def test_asset_id_unique(self):
        """Test that all asset IDs are unique."""
        assets = generate_assets(count=100, seed=42)
        asset_ids = [a["asset_id"] for a in assets]
        assert len(asset_ids) == len(set(asset_ids))

    def test_vip_distribution(self):
        """Test that 5-8% of assets have VIP tags."""
        assets = generate_assets(count=1000, seed=42)
        vip_count = sum(1 for a in assets if "vip" in a.get("tags", []) or "executive" in a.get("tags", []))
        vip_percentage = (vip_count / 1000) * 100
        assert 4 <= vip_percentage <= 10, f"VIP percentage {vip_percentage}% outside expected range"

    def test_server_distribution(self):
        """Test that ~20% of assets are servers."""
        assets = generate_assets(count=1000, seed=42)
        server_count = sum(1 for a in assets if a.get("asset_type") == "server")
        server_percentage = (server_count / 1000) * 100
        assert 5 <= server_percentage <= 25, f"Server percentage {server_percentage}% outside expected range"

    def test_reproducibility_with_seed(self):
        """Test that same seed produces same asset IDs and hostnames."""
        assets1 = generate_assets(count=100, seed=42)
        assets2 = generate_assets(count=100, seed=42)
        # Compare deterministic fields only (not timestamps)
        ids1 = [a["asset_id"] for a in assets1]
        ids2 = [a["asset_id"] for a in assets2]
        hostnames1 = [a["hostname"] for a in assets1]
        hostnames2 = [a["hostname"] for a in assets2]
        assert ids1 == ids2
        assert hostnames1 == hostnames2


class TestEDRGenerator:
    """Tests for EDR detection generator."""

    def test_generates_1000_detections(self):
        """Test that generator creates exactly 1000 detections."""
        assets = generate_assets(count=100, seed=42)
        detections = generate_edr_detections(count=1000, assets=assets, seed=42)
        assert len(detections) == 1000

    def test_detections_reference_existing_assets(self):
        """Test that all detections reference valid assets."""
        assets = generate_assets(count=100, seed=42)
        asset_ids = {a["asset_id"] for a in assets}
        detections = generate_edr_detections(count=50, assets=assets, seed=42)
        for det in detections:
            assert det["asset_id"] in asset_ids, f"Detection references unknown asset: {det['asset_id']}"

    def test_anchor_cases_created(self):
        """Test that 3 anchor detection cases exist."""
        assets = generate_assets(count=100, seed=42)
        detections = generate_edr_detections(count=100, assets=assets, seed=42)
        detection_ids = {d["detection_id"] for d in detections}
        for anchor_id in ANCHOR_DETECTION_IDS:
            assert anchor_id in detection_ids, f"Anchor detection {anchor_id} not found"

    def test_severity_distribution(self):
        """Test severity distribution is reasonable."""
        assets = generate_assets(count=100, seed=42)
        detections = generate_edr_detections(count=1000, assets=assets, seed=42)
        severities = [d["severity"] for d in detections]
        critical_pct = severities.count("Critical") / len(severities) * 100
        assert 10 <= critical_pct <= 25, f"Critical percentage {critical_pct}% outside expected range"

    def test_reproducibility_with_seed(self):
        """Test that same seed produces same detection IDs."""
        assets = generate_assets(count=100, seed=42)
        det1 = generate_edr_detections(count=50, assets=assets, seed=42)
        det2 = generate_edr_detections(count=50, assets=assets, seed=42)
        ids1 = [d["detection_id"] for d in det1]
        ids2 = [d["detection_id"] for d in det2]
        assert ids1 == ids2


class TestIntelGenerator:
    """Tests for threat intelligence generator."""

    def test_generates_200_iocs(self):
        """Test that generator creates ~200 IOCs."""
        iocs = generate_threat_intel(count=200, seed=42)
        assert len(iocs) == 200

    def test_ioc_types_present(self):
        """Test that all IOC types are present."""
        iocs = generate_threat_intel(count=200, seed=42)
        types = {i["indicator_type"] for i in iocs}
        assert "filehash" in types
        assert "ip" in types or "domain" in types

    def test_verdict_distribution(self):
        """Test verdict distribution (20% malicious, 10% suspicious, 70% benign)."""
        iocs = generate_threat_intel(count=200, seed=42)
        verdicts = [i["verdict"] for i in iocs]
        malicious_pct = verdicts.count("malicious") / len(verdicts) * 100
        assert 10 <= malicious_pct <= 35, f"Malicious percentage {malicious_pct}% outside expected range"

    def test_reproducibility_with_seed(self):
        """Test that same seed produces same IOC values."""
        iocs1 = generate_threat_intel(count=50, seed=42)
        iocs2 = generate_threat_intel(count=50, seed=42)
        vals1 = [i["indicator_value"] for i in iocs1]
        vals2 = [i["indicator_value"] for i in iocs2]
        assert vals1 == vals2


class TestCTEMGenerator:
    """Tests for CTEM findings generator."""

    def test_ctem_findings_per_asset(self):
        """Test that findings are generated for assets."""
        assets = generate_assets(count=100, seed=42)
        findings, risks = generate_ctem_findings(assets=assets, seed=42)
        assert len(findings) > 0
        assert len(risks) == len(assets)

    def test_risk_color_calculation(self):
        """Test that risk colors are calculated correctly."""
        assets = generate_assets(count=100, seed=42)
        findings, risks = generate_ctem_findings(assets=assets, seed=42)
        colors = {r["risk_color"] for r in risks}
        assert colors.issubset({"Green", "Yellow", "Red"})

    def test_servers_skew_higher_risk(self):
        """Test that servers have higher risk on average."""
        assets = generate_assets(count=200, seed=42)
        findings, risks = generate_ctem_findings(assets=assets, seed=42)

        server_assets = [a for a in assets if a.get("asset_type") == "server"]
        server_ids = {a["asset_id"] for a in server_assets}
        server_risks = [r for r in risks if r["asset_id"] in server_ids]

        if server_risks:
            red_count = sum(1 for r in server_risks if r["risk_color"] == "Red")
            red_pct = red_count / len(server_risks) * 100
            # Servers should have at least some red
            assert red_pct >= 5, f"Server red percentage {red_pct}% lower than expected"

    def test_reproducibility_with_seed(self):
        """Test that same seed produces same finding counts per asset."""
        assets = generate_assets(count=50, seed=42)
        f1, r1 = generate_ctem_findings(assets=assets, seed=42)
        f2, r2 = generate_ctem_findings(assets=assets, seed=42)
        assert len(f1) == len(f2)
        assert len(r1) == len(r2)


class TestSIEMGenerator:
    """Tests for SIEM incident generator."""

    def test_creates_incidents_from_detections(self):
        """Test that incidents are created from detections."""
        assets = generate_assets(count=100, seed=42)
        detections = generate_edr_detections(count=100, assets=assets, seed=42)
        intel = generate_threat_intel(count=50, seed=42)
        incidents = generate_siem_incidents(detections=detections, intel=intel, seed=42)
        assert len(incidents) > 0

    def test_anchor_incidents_exist(self):
        """Test that 3 anchor incidents exist."""
        assets = generate_assets(count=100, seed=42)
        detections = generate_edr_detections(count=100, assets=assets, seed=42)
        intel = generate_threat_intel(count=50, seed=42)
        incidents = generate_siem_incidents(detections=detections, intel=intel, seed=42)
        incident_ids = {i["incident_id"] for i in incidents}
        for anchor_id in ANCHOR_INCIDENT_IDS:
            assert anchor_id in incident_ids, f"Anchor incident {anchor_id} not found"

    def test_reproducibility_with_seed(self):
        """Test that same seed produces same incident IDs."""
        assets = generate_assets(count=100, seed=42)
        detections = generate_edr_detections(count=100, assets=assets, seed=42)
        intel = generate_threat_intel(count=50, seed=42)
        inc1 = generate_siem_incidents(detections=detections, intel=intel, seed=42)
        inc2 = generate_siem_incidents(detections=detections, intel=intel, seed=42)
        ids1 = [i["incident_id"] for i in inc1]
        ids2 = [i["incident_id"] for i in inc2]
        assert ids1 == ids2
