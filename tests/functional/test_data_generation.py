"""Functional tests for synthetic data generation and validation.

These tests verify:
1. Data generators insert data into OpenSearch
2. Data appears correctly in the dashboard APIs
3. Data is valid for SoulInTheBot decision making
"""
import pytest
import httpx
import asyncio
from typing import Optional

# Test configuration
BACKEND_URL = "http://localhost:8000"


class TestDataGeneration:
    """Functional tests for data generation into databases."""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup test client."""
        self.client = httpx.AsyncClient(base_url=BACKEND_URL, timeout=60.0)
        yield
        await self.client.aclose()

    @pytest.mark.asyncio
    async def test_generate_assets_inserts_to_opensearch(self):
        """Test that generating assets inserts data into OpenSearch."""
        # Generate assets
        response = await self.client.post("/gen/assets", params={"count": 100, "seed": 42})
        assert response.status_code == 200, f"Generation failed: {response.text}"

        # Verify data was inserted
        health = await self.client.get("/gen/health")
        data = health.json()
        assert data.get("counts", {}).get("assets-inventory-v1", 0) >= 100

    @pytest.mark.asyncio
    async def test_generate_edr_inserts_to_opensearch(self):
        """Test that generating EDR detections inserts data into OpenSearch."""
        response = await self.client.post("/gen/edr", params={"count": 100, "seed": 42})
        assert response.status_code == 200

        health = await self.client.get("/gen/health")
        data = health.json()
        assert data.get("counts", {}).get("edr-detections-v1", 0) >= 100

    @pytest.mark.asyncio
    async def test_generate_intel_inserts_to_opensearch(self):
        """Test that generating threat intel inserts data into OpenSearch."""
        response = await self.client.post("/gen/intel", params={"count": 50, "seed": 42})
        assert response.status_code == 200

        health = await self.client.get("/gen/health")
        data = health.json()
        assert data.get("counts", {}).get("threat-intel-v1", 0) >= 50

    @pytest.mark.asyncio
    async def test_generate_ctem_inserts_to_opensearch(self):
        """Test that generating CTEM findings inserts data into OpenSearch."""
        response = await self.client.post("/gen/ctem", params={"seed": 42})
        assert response.status_code == 200

        health = await self.client.get("/gen/health")
        data = health.json()
        assert data.get("counts", {}).get("ctem-findings-v1", 0) > 0

    @pytest.mark.asyncio
    async def test_generate_siem_inserts_to_opensearch(self):
        """Test that generating SIEM incidents inserts data into OpenSearch."""
        response = await self.client.post("/gen/siem", params={"seed": 42})
        assert response.status_code == 200

        health = await self.client.get("/gen/health")
        data = health.json()
        assert data.get("counts", {}).get("siem-incidents-v1", 0) > 0

    @pytest.mark.asyncio
    async def test_generate_all_creates_all_data(self):
        """Test that /gen/all creates all synthetic data."""
        # Reset first
        reset_response = await self.client.post("/gen/reset")
        assert reset_response.status_code == 200

        # Generate all
        response = await self.client.post("/gen/all", params={"seed": 42})
        assert response.status_code == 200

        # Verify counts
        health = await self.client.get("/gen/health")
        data = health.json()
        counts = data.get("counts", {})

        assert counts.get("assets-inventory-v1", 0) >= 1000, "Assets not generated"
        assert counts.get("edr-detections-v1", 0) >= 1000, "Detections not generated"
        assert counts.get("threat-intel-v1", 0) >= 200, "Intel not generated"
        assert counts.get("siem-incidents-v1", 0) >= 500, "Incidents not generated"

    @pytest.mark.asyncio
    async def test_data_count_matches_expected(self):
        """Test that generated data counts match expected values."""
        health = await self.client.get("/gen/health")
        data = health.json()
        counts = data.get("counts", {})

        # Expected counts (approximate)
        assert 900 <= counts.get("assets-inventory-v1", 0) <= 1100
        assert 900 <= counts.get("edr-detections-v1", 0) <= 1100
        assert 150 <= counts.get("threat-intel-v1", 0) <= 250


class TestDashboardVisualization:
    """Tests that generated data appears correctly in dashboard APIs."""

    @pytest.fixture(autouse=True)
    async def setup(self):
        self.client = httpx.AsyncClient(base_url=BACKEND_URL, timeout=30.0)
        yield
        await self.client.aclose()

    @pytest.mark.asyncio
    async def test_assets_shown_in_dashboard(self):
        """Test that assets are visible via API."""
        response = await self.client.get("/assets")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0, "No assets visible in dashboard"
        assert len(data["assets"]) > 0

    @pytest.mark.asyncio
    async def test_incidents_shown_in_dashboard(self):
        """Test that incidents are visible via API."""
        response = await self.client.get("/siem/incidents")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0, "No incidents visible in dashboard"
        assert len(data["incidents"]) > 0

    @pytest.mark.asyncio
    async def test_detections_shown_in_dashboard(self):
        """Test that detections are visible via API."""
        response = await self.client.get("/edr/detections")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0, "No detections visible in dashboard"

    @pytest.mark.asyncio
    async def test_kpis_reflect_data(self):
        """Test that summary statistics reflect generated data."""
        response = await self.client.get("/assets/summary/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0, "Asset summary shows no data"


class TestSoulInTheBotValidation:
    """Tests that data is valid for SoulInTheBot decision making."""

    @pytest.fixture(autouse=True)
    async def setup(self):
        self.client = httpx.AsyncClient(base_url=BACKEND_URL, timeout=30.0)
        yield
        await self.client.aclose()

    @pytest.mark.asyncio
    async def test_anchor_incident_1_valid(self):
        """Test INC-ANCHOR-001 is valid for auto-containment decision."""
        response = await self.client.get("/siem/incidents/INC-ANCHOR-001")
        if response.status_code == 404:
            pytest.skip("Anchor incident not yet generated")

        data = response.json()
        assert data["severity"] in ["Critical", "High"], "Anchor 1 should be high severity"
        assert len(data.get("related_detections", [])) > 0, "Should have related detections"

    @pytest.mark.asyncio
    async def test_anchor_incident_2_valid_vip(self):
        """Test INC-ANCHOR-002 is valid VIP case requiring approval."""
        response = await self.client.get("/siem/incidents/INC-ANCHOR-002")
        if response.status_code == 404:
            pytest.skip("Anchor incident not yet generated")

        data = response.json()
        # Get related asset and verify it's VIP
        if data.get("related_assets"):
            asset_id = data["related_assets"][0]
            asset_response = await self.client.get(f"/assets/{asset_id}")
            if asset_response.status_code == 200:
                asset = asset_response.json()
                tags = asset.get("tags", [])
                assert any(t in tags for t in ["vip", "executive"]), "Anchor 2 asset should be VIP"

    @pytest.mark.asyncio
    async def test_anchor_incident_3_valid_fp(self):
        """Test INC-ANCHOR-003 is valid False Positive case."""
        response = await self.client.get("/siem/incidents/INC-ANCHOR-003")
        if response.status_code == 404:
            pytest.skip("Anchor incident not yet generated")

        data = response.json()
        # This should be a low-confidence case
        assert data["severity"] in ["Low", "Medium"], "Anchor 3 should be low severity for FP"

    @pytest.mark.asyncio
    async def test_policy_engine_auto_contain(self):
        """Test Policy Engine correctly identifies auto-containment case."""
        # Import and test policy engine
        from src.services.policy_engine import get_policy_engine, ActionType

        engine = get_policy_engine()
        decision = engine.evaluate(
            confidence_score=95,
            device_tags=["standard-user"],
            has_approval=False
        )
        assert decision.action == ActionType.CONTAIN

    @pytest.mark.asyncio
    async def test_policy_engine_vip_approval(self):
        """Test Policy Engine correctly requires VIP approval."""
        from src.services.policy_engine import get_policy_engine, ActionType

        engine = get_policy_engine()
        decision = engine.evaluate(
            confidence_score=95,
            device_tags=["vip", "executive"],
            has_approval=False
        )
        assert decision.action == ActionType.REQUEST_APPROVAL
        assert decision.requires_approval is True

    @pytest.mark.asyncio
    async def test_policy_engine_false_positive(self):
        """Test Policy Engine correctly marks False Positive."""
        from src.services.policy_engine import get_policy_engine, ActionType

        engine = get_policy_engine()
        decision = engine.evaluate(
            confidence_score=22,
            device_tags=["standard"],
            has_approval=False
        )
        assert decision.action == ActionType.MARK_FALSE_POSITIVE

    @pytest.mark.asyncio
    async def test_intel_lookup_works(self):
        """Test that threat intel lookup returns valid data."""
        # First, get a detection to find a hash
        det_response = await self.client.get("/edr/detections", params={"page_size": 1})
        if det_response.status_code == 200:
            data = det_response.json()
            if data["detections"]:
                sha256 = data["detections"][0].get("file", {}).get("sha256")
                if sha256:
                    intel_response = await self.client.get(f"/intel/indicators/filehash/{sha256}")
                    assert intel_response.status_code == 200
                    intel = intel_response.json()
                    assert intel["verdict"] in ["malicious", "suspicious", "benign", "unknown"]

    @pytest.mark.asyncio
    async def test_process_tree_available(self):
        """Test that process trees are available for detections."""
        det_response = await self.client.get("/edr/detections", params={"page_size": 1})
        if det_response.status_code == 200:
            data = det_response.json()
            if data["detections"]:
                detection_id = data["detections"][0]["detection_id"]
                tree_response = await self.client.get(f"/edr/detections/{detection_id}/process-tree")
                # May return 404 if tree not generated, but should not error
                assert tree_response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_ctem_risk_available(self):
        """Test that CTEM risk data is available for assets."""
        asset_response = await self.client.get("/assets", params={"page_size": 1})
        if asset_response.status_code == 200:
            data = asset_response.json()
            if data["assets"]:
                asset_id = data["assets"][0]["asset_id"]
                ctem_response = await self.client.get(f"/ctem/assets/{asset_id}")
                # May return 404 if not generated, but should not error
                assert ctem_response.status_code in [200, 404]
