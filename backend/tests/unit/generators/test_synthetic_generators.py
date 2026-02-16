"""
Combined unit tests for all synthetic generators.

This file consolidates tests for the enrichment plan section 8.2:
- test_risk_score_calculation_high_cvss_high_epss
- test_risk_score_calculation_low_cvss_low_epss
- test_vpr_score_calculation
- test_sandbox_report_generation

Each generator (RecordedFutureMock, TenableVPRMock, CrowdStrikeSandboxMock)
is tested for correct behavior and realistic data generation.
"""
import pytest
import statistics


class TestRecordedFutureRiskScore:
    """Tests for RecordedFutureMock risk score calculation."""

    def test_risk_score_calculation_high_cvss_high_epss(self):
        """
        Test risk score for critical vulnerability:
        - High CVSS (9.8) + High EPSS (0.95) + Known exploit + Recent = Critical risk

        Expected calculation:
        - CVSS component: (9.8/10) * 40 = 39.2 points
        - EPSS component: 0.95 * 30 = 28.5 points
        - Exploit component: 20 points (known_exploited=True)
        - Age component: 10 points (age_days=15, within 0-30 range)
        - Total: ~97-98 points = Critical risk
        """
        from src.generators.enrichment.recorded_future_mock import RecordedFutureMock

        mock = RecordedFutureMock(seed=42)  # Fixed seed for reproducibility

        result = mock.calculate_risk_score(
            cve_id="CVE-2024-0001",
            cvss_score=9.8,
            epss_score=0.95,
            known_exploited=True,
            age_days=15
        )

        # High risk score expected (90+)
        assert result["risk_score"] >= 90
        assert result["risk_category"] == "Critical"

        # Threat actors should be assigned for critical exploited CVEs
        assert len(result["threat_actors"]) >= 1

        # Risk vector breakdown should be present
        assert "risk_vector" in result
        assert result["risk_vector"]["cvss_component"] >= 38  # ~40% of 9.8
        assert result["risk_vector"]["epss_component"] >= 28  # ~30% of 0.95
        assert result["risk_vector"]["exploit_component"] == 20
        assert result["risk_vector"]["age_component"] == 10  # 0-30 days

        # Metadata
        assert result["enrichment_source"] == "synthetic_recorded_future"
        assert "generated_at" in result

    def test_risk_score_calculation_low_cvss_low_epss(self):
        """
        Test risk score for low-risk vulnerability:
        - Low CVSS (3.2) + Low EPSS (0.01) + No exploit + Old = Low risk

        Expected calculation:
        - CVSS component: (3.2/10) * 40 = 12.8 points
        - EPSS component: 0.01 * 30 = 0.3 points
        - Exploit component: 0 points (not exploited)
        - Age component: 2 points (age_days=400, >365)
        - Total: ~15 points = Low risk
        """
        from src.generators.enrichment.recorded_future_mock import RecordedFutureMock

        mock = RecordedFutureMock(seed=42)

        result = mock.calculate_risk_score(
            cve_id="CVE-2024-9999",
            cvss_score=3.2,
            epss_score=0.01,
            known_exploited=False,
            age_days=400
        )

        # Low risk score expected (<=40)
        assert result["risk_score"] <= 40
        assert result["risk_category"] in ["Low", "Medium"]

        # No threat actors for low-risk non-exploited CVEs
        assert len(result["threat_actors"]) == 0

        # No active campaigns for old CVEs
        assert len(result["campaigns"]) == 0

        # Age component should be 2 (>365 days)
        assert result["risk_vector"]["age_component"] == 2

    def test_risk_score_clamped_to_valid_range(self):
        """Test that risk scores are always in [0, 100] range."""
        from src.generators.enrichment.recorded_future_mock import RecordedFutureMock

        mock = RecordedFutureMock(seed=42)

        # Maximum possible inputs
        result_max = mock.calculate_risk_score(
            cve_id="CVE-MAX",
            cvss_score=10.0,
            epss_score=1.0,
            known_exploited=True,
            age_days=1
        )
        assert 0 <= result_max["risk_score"] <= 100

        # Minimum possible inputs
        result_min = mock.calculate_risk_score(
            cve_id="CVE-MIN",
            cvss_score=0.0,
            epss_score=0.0,
            known_exploited=False,
            age_days=1000
        )
        assert 0 <= result_min["risk_score"] <= 100


class TestTenableVPRScore:
    """Tests for TenableVPRMock VPR score calculation."""

    def test_vpr_score_calculation(self):
        """
        Test VPR score for high-risk vulnerability:
        - CVSS 9.8, EPSS 0.89, critical asset, known exploit, 80% coverage

        Expected calculation:
        - CVSS component: (9.8/10) * 3.5 = 3.43 points
        - Threat component: min(3.5, 0.89*2.5 + 1.0) = min(3.5, 3.225) = 3.225 points
        - Asset criticality: critical = 2.0 points
        - Product coverage: 0.8 * 1.0 = 0.8 points
        - Total: ~9.45 points = Very high VPR
        """
        from src.generators.enrichment.tenable_mock import TenableVPRMock

        mock = TenableVPRMock()

        result = mock.calculate_vpr(
            cvss_score=9.8,
            epss_score=0.89,
            asset_criticality="critical",
            known_exploited=True,
            age_days=20,
            product_coverage=0.8
        )

        # VPR should be high (8.0+)
        assert result["vpr_score"] >= 8.0
        assert result["vpr_score"] <= 10.0

        # Components should be present and within ranges
        assert "vpr_components" in result
        assert result["vpr_components"]["cvss"] <= 3.5
        assert result["vpr_components"]["threat"] <= 3.5
        assert result["vpr_components"]["asset_criticality"] == 2.0
        assert result["vpr_components"]["product_coverage"] <= 1.0

        # Metadata
        assert result["enrichment_source"] == "synthetic_tenable"
        assert "generated_at" in result

    def test_vpr_asset_criticality_levels(self):
        """Test that asset criticality maps correctly to points."""
        from src.generators.enrichment.tenable_mock import TenableVPRMock

        mock = TenableVPRMock()

        base_params = {
            "cvss_score": 7.0,
            "epss_score": 0.5,
            "known_exploited": False,
            "age_days": 100,
            "product_coverage": 0.5
        }

        # Test each criticality level
        result_critical = mock.calculate_vpr(**base_params, asset_criticality="critical")
        result_high = mock.calculate_vpr(**base_params, asset_criticality="high")
        result_medium = mock.calculate_vpr(**base_params, asset_criticality="medium")
        result_low = mock.calculate_vpr(**base_params, asset_criticality="low")

        # Check criticality component values
        assert result_critical["vpr_components"]["asset_criticality"] == 2.0
        assert result_high["vpr_components"]["asset_criticality"] == 1.5
        assert result_medium["vpr_components"]["asset_criticality"] == 1.0
        assert result_low["vpr_components"]["asset_criticality"] == 0.5

        # VPR should decrease with criticality
        assert result_critical["vpr_score"] > result_high["vpr_score"]
        assert result_high["vpr_score"] > result_medium["vpr_score"]
        assert result_medium["vpr_score"] > result_low["vpr_score"]

    def test_vpr_threat_component_capped(self):
        """Test that threat component is capped at 3.5 points."""
        from src.generators.enrichment.tenable_mock import TenableVPRMock

        mock = TenableVPRMock()

        # Maximum threat scenario: EPSS=1.0 + exploit
        result = mock.calculate_vpr(
            cvss_score=5.0,
            epss_score=1.0,  # Max EPSS
            asset_criticality="medium",
            known_exploited=True,  # +1.0 exploit
            age_days=10,
            product_coverage=0.5
        )

        # Threat = min(3.5, 1.0*2.5 + 1.0) = min(3.5, 3.5) = 3.5
        assert result["vpr_components"]["threat"] <= 3.5

    def test_vpr_score_range(self):
        """Test that VPR scores are always in [0.0, 10.0] range."""
        from src.generators.enrichment.tenable_mock import TenableVPRMock

        mock = TenableVPRMock()

        # Minimum values
        result_min = mock.calculate_vpr(
            cvss_score=0.0,
            epss_score=0.0,
            asset_criticality="low",
            known_exploited=False,
            age_days=1000,
            product_coverage=0.0
        )
        assert 0.0 <= result_min["vpr_score"] <= 10.0

        # Maximum values
        result_max = mock.calculate_vpr(
            cvss_score=10.0,
            epss_score=1.0,
            asset_criticality="critical",
            known_exploited=True,
            age_days=1,
            product_coverage=1.0
        )
        assert 0.0 <= result_max["vpr_score"] <= 10.0


class TestCrowdStrikeSandboxReport:
    """Tests for CrowdStrikeSandboxMock report generation."""

    def test_sandbox_report_generation_clean(self):
        """Test sandbox report for clean (non-malicious) file."""
        from src.generators.enrichment.crowdstrike_mock import CrowdStrikeSandboxMock

        mock = CrowdStrikeSandboxMock(seed=42)

        result = mock.generate_sandbox_report(
            file_hash="abc123def456",
            malicious=False
        )

        # Clean verdict
        assert result["verdict"] == "clean"
        assert 85 <= result["confidence"] <= 95
        assert result["file_hash"] == "abc123def456"

        # Clean files don't have behaviors, IOCs, or malware family
        assert "behaviors" not in result or len(result.get("behaviors", [])) == 0
        assert "mitre_techniques" not in result
        assert "malware_family" not in result

        # Metadata
        assert result["enrichment_source"] == "synthetic_crowdstrike"
        assert "generated_at" in result

    def test_sandbox_report_generation_malicious(self):
        """Test sandbox report for malicious file with specified family."""
        from src.generators.enrichment.crowdstrike_mock import CrowdStrikeSandboxMock

        mock = CrowdStrikeSandboxMock(seed=42)

        result = mock.generate_sandbox_report(
            file_hash="malware123hash",
            malicious=True,
            malware_family="Emotet"
        )

        # Malicious verdict
        assert result["verdict"] == "malicious"
        assert 80 <= result["confidence"] <= 99
        assert result["file_hash"] == "malware123hash"
        assert result["malware_family"] == "Emotet"

        # Should have behaviors
        assert "behaviors" in result
        assert len(result["behaviors"]) > 0

        # Each behavior should have required fields
        for behavior in result["behaviors"]:
            assert "category" in behavior
            assert "description" in behavior
            assert "severity" in behavior
            assert "details" in behavior
            assert behavior["severity"] in ["low", "medium", "high", "critical"]

        # Should have MITRE techniques
        assert "mitre_techniques" in result
        assert len(result["mitre_techniques"]) > 0

        # Should have extracted IOCs
        assert "extracted_iocs" in result
        assert "ips" in result["extracted_iocs"]
        assert "domains" in result["extracted_iocs"]
        assert "file_paths" in result["extracted_iocs"]

    def test_sandbox_report_auto_assigns_malware_family(self):
        """Test that malware family is auto-assigned if not specified."""
        from src.generators.enrichment.crowdstrike_mock import CrowdStrikeSandboxMock

        mock = CrowdStrikeSandboxMock(seed=42)

        result = mock.generate_sandbox_report(
            file_hash="unknown_malware",
            malicious=True
            # malware_family not specified
        )

        # Should have an auto-assigned malware family
        assert "malware_family" in result
        assert result["malware_family"] is not None
        assert len(result["malware_family"]) > 0

        # Should be from the known families list
        known_families = [
            "Emotet", "TrickBot", "Dridex", "Qbot", "IcedID", "Cobalt Strike",
            "Ryuk", "Conti", "LockBit", "BlackCat", "AgentTesla", "FormBook",
            "Remcos", "AsyncRAT", "RedLine", "Vidar", "Raccoon", "Azorult"
        ]
        assert result["malware_family"] in known_families

    def test_sandbox_report_mitre_techniques_valid(self):
        """Test that MITRE ATT&CK techniques have valid format."""
        from src.generators.enrichment.crowdstrike_mock import CrowdStrikeSandboxMock

        mock = CrowdStrikeSandboxMock(seed=42)

        result = mock.generate_sandbox_report(
            file_hash="mitre_test",
            malicious=True
        )

        # All techniques should start with T (MITRE format)
        for technique in result["mitre_techniques"]:
            assert technique.startswith("T")
            # Format: T1234 or T1234.001
            parts = technique.split(".")
            assert len(parts[0]) >= 5  # T followed by 4+ digits

    def test_sandbox_report_ioc_ips_valid(self):
        """Test that extracted IOC IPs are valid format."""
        from src.generators.enrichment.crowdstrike_mock import CrowdStrikeSandboxMock

        mock = CrowdStrikeSandboxMock(seed=42)

        result = mock.generate_sandbox_report(
            file_hash="ioc_ip_test",
            malicious=True
        )

        # IPs should be valid IPv4 format
        for ip in result["extracted_iocs"]["ips"]:
            parts = ip.split(".")
            assert len(parts) == 4
            for part in parts:
                assert 0 <= int(part) <= 255


class TestSyntheticGeneratorCorrelation:
    """Tests for correlation between synthetic data and real metrics."""

    def test_risk_score_correlation_with_cvss_epss(self):
        """
        Test that risk scores correlate highly with CVSS + EPSS.
        Correlation should be >= 0.8 for realistic synthetic data.
        """
        from src.generators.enrichment.recorded_future_mock import RecordedFutureMock

        mock = RecordedFutureMock(seed=42)

        # Test cases spanning the risk spectrum
        test_cases = [
            {"cvss": 9.8, "epss": 0.95, "exploit": True, "age": 15},
            {"cvss": 9.0, "epss": 0.80, "exploit": True, "age": 30},
            {"cvss": 7.5, "epss": 0.60, "exploit": False, "age": 60},
            {"cvss": 5.0, "epss": 0.30, "exploit": False, "age": 120},
            {"cvss": 3.0, "epss": 0.05, "exploit": False, "age": 300},
        ]

        risk_scores = []
        combined_scores = []  # CVSS + EPSS normalized to 0-100

        for tc in test_cases:
            result = mock.calculate_risk_score(
                cve_id="CVE-CORR-TEST",
                cvss_score=tc["cvss"],
                epss_score=tc["epss"],
                known_exploited=tc["exploit"],
                age_days=tc["age"]
            )
            risk_scores.append(result["risk_score"])
            # Normalize: CVSS (0-10) * 5 + EPSS (0-1) * 50 = 0-100 scale
            combined = (tc["cvss"] / 10.0) * 50 + tc["epss"] * 50
            combined_scores.append(combined)

        # Calculate Pearson correlation coefficient
        def pearson_correlation(x, y):
            n = len(x)
            if n == 0:
                return 0
            mean_x = statistics.mean(x)
            mean_y = statistics.mean(y)
            numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
            denominator = (
                sum((x[i] - mean_x) ** 2 for i in range(n)) *
                sum((y[i] - mean_y) ** 2 for i in range(n))
            ) ** 0.5
            return numerator / denominator if denominator != 0 else 0

        correlation = pearson_correlation(risk_scores, combined_scores)
        assert correlation >= 0.8, f"Correlation {correlation:.2f} below required 0.8"

    def test_vpr_correlation_with_cvss(self):
        """Test that VPR scores correlate with CVSS scores."""
        from src.generators.enrichment.tenable_mock import TenableVPRMock

        mock = TenableVPRMock()

        # Fixed parameters, varying CVSS
        fixed_params = {
            "epss_score": 0.5,
            "asset_criticality": "medium",
            "known_exploited": False,
            "age_days": 100,
            "product_coverage": 0.5
        }

        cvss_values = [2.0, 4.0, 6.0, 8.0, 10.0]
        vpr_scores = []

        for cvss in cvss_values:
            result = mock.calculate_vpr(cvss_score=cvss, **fixed_params)
            vpr_scores.append(result["vpr_score"])

        # VPR should increase monotonically with CVSS
        for i in range(len(vpr_scores) - 1):
            assert vpr_scores[i] < vpr_scores[i + 1], \
                f"VPR should increase with CVSS: {vpr_scores}"


class TestSyntheticGeneratorReproducibility:
    """Tests for reproducibility with random seeds."""

    def test_recorded_future_reproducible_with_seed(self):
        """Test that RecordedFutureMock produces same output with same seed."""
        from src.generators.enrichment.recorded_future_mock import RecordedFutureMock

        # Same seed, same inputs
        mock1 = RecordedFutureMock(seed=42)
        mock2 = RecordedFutureMock(seed=42)

        params = {
            "cve_id": "CVE-SEED-TEST",
            "cvss_score": 8.5,
            "epss_score": 0.75,
            "known_exploited": True,
            "age_days": 45
        }

        result1 = mock1.calculate_risk_score(**params)
        result2 = mock2.calculate_risk_score(**params)

        # Deterministic parts should match
        assert result1["risk_score"] == result2["risk_score"]
        assert result1["risk_category"] == result2["risk_category"]
        assert result1["risk_vector"] == result2["risk_vector"]

    def test_crowdstrike_reproducible_with_seed(self):
        """Test that CrowdStrikeSandboxMock produces same output with same seed."""
        from src.generators.enrichment.crowdstrike_mock import CrowdStrikeSandboxMock

        mock1 = CrowdStrikeSandboxMock(seed=42)
        mock2 = CrowdStrikeSandboxMock(seed=42)

        params = {
            "file_hash": "test_hash",
            "malicious": True,
            "malware_family": "Emotet"
        }

        result1 = mock1.generate_sandbox_report(**params)
        result2 = mock2.generate_sandbox_report(**params)

        # Deterministic parts should match
        assert result1["verdict"] == result2["verdict"]
        assert result1["malware_family"] == result2["malware_family"]
