"""Verification tests for correlation metrics and data quality.

These tests verify that synthetic data meets quality requirements:
- Risk scores correlate highly (≥0.8) with CVSS+EPSS
- APT groups only assigned to high-risk CVEs
- Realistic behavior distributions
"""

import pytest
import statistics
from src.generators.enrichment.recorded_future_mock import RecordedFutureMock
from src.generators.enrichment.tenable_mock import TenableVPRMock
from src.generators.enrichment.crowdstrike_mock import CrowdStrikeSandboxMock


class TestCorrelationMetrics:
    """Verify synthetic data quality and correlation metrics."""

    def test_recorded_future_risk_score_correlation(self):
        """
        Verify that RecordedFuture risk scores correlate ≥0.8 with CVSS+EPSS.

        This ensures synthetic data is realistic and not random.
        """
        mock = RecordedFutureMock(seed=42)

        # Test cases covering the full range
        test_cases = [
            {"cvss": 9.8, "epss": 0.95, "exploit": True, "age": 15},
            {"cvss": 9.0, "epss": 0.80, "exploit": True, "age": 30},
            {"cvss": 8.5, "epss": 0.70, "exploit": False, "age": 45},
            {"cvss": 7.5, "epss": 0.60, "exploit": False, "age": 60},
            {"cvss": 6.5, "epss": 0.45, "exploit": False, "age": 90},
            {"cvss": 5.5, "epss": 0.30, "exploit": False, "age": 120},
            {"cvss": 4.5, "epss": 0.20, "exploit": False, "age": 180},
            {"cvss": 3.5, "epss": 0.10, "exploit": False, "age": 250},
            {"cvss": 3.0, "epss": 0.05, "exploit": False, "age": 300},
            {"cvss": 2.0, "epss": 0.01, "exploit": False, "age": 400},
        ]

        risk_scores = []
        combined_scores = []

        for tc in test_cases:
            result = mock.calculate_risk_score(
                cve_id=f"CVE-2024-TEST",
                cvss_score=tc["cvss"],
                epss_score=tc["epss"],
                known_exploited=tc["exploit"],
                age_days=tc["age"]
            )
            risk_scores.append(result["risk_score"])

            # Normalize CVSS (0-10) + EPSS (0-1) to 0-100 scale
            # Weight: CVSS 50%, EPSS 50% (simplified for comparison)
            combined = (tc["cvss"] / 10.0) * 50 + tc["epss"] * 50
            combined_scores.append(combined)

        # Calculate Pearson correlation
        correlation = self._pearson_correlation(risk_scores, combined_scores)

        print(f"\n{'='*70}")
        print(f"RecordedFuture Risk Score Correlation Analysis")
        print(f"{'='*70}")
        print(f"Correlation: {correlation:.3f}")
        print(f"Requirement: ≥0.800")
        print(f"Status: {'✓ PASS' if correlation >= 0.8 else '✗ FAIL'}")
        print(f"{'='*70}\n")

        assert correlation >= 0.8, f"Correlation {correlation:.3f} below required 0.8"

    def test_apt_group_assignment_realism(self):
        """
        Verify that APT groups are only assigned to high-risk exploited CVEs.

        This ensures synthetic threat intelligence is realistic.
        """
        mock = RecordedFutureMock(seed=42)

        # Test 100 CVEs across risk spectrum
        test_cases = []

        # High-risk exploited (should have APTs)
        for i in range(20):
            test_cases.append({
                "cvss": 9.0 + (i % 10) * 0.1,
                "epss": 0.8 + (i % 20) * 0.01,
                "exploit": True,
                "age": 10 + i,
                "expected_apts": True
            })

        # Medium-risk non-exploited (should NOT have APTs)
        for i in range(30):
            test_cases.append({
                "cvss": 5.0 + (i % 20) * 0.1,
                "epss": 0.3 + (i % 30) * 0.01,
                "exploit": False,
                "age": 60 + i,
                "expected_apts": False
            })

        # Low-risk (should NOT have APTs)
        for i in range(30):
            test_cases.append({
                "cvss": 2.0 + (i % 20) * 0.1,
                "epss": 0.01 + (i % 30) * 0.001,
                "exploit": False,
                "age": 200 + i,
                "expected_apts": False
            })

        correct_assignments = 0
        total_cases = len(test_cases)

        for tc in test_cases:
            result = mock.calculate_risk_score(
                cve_id="CVE-TEST",
                cvss_score=tc["cvss"],
                epss_score=tc["epss"],
                known_exploited=tc["exploit"],
                age_days=tc["age"]
            )

            has_apts = len(result["threat_actors"]) > 0

            if tc["expected_apts"] == has_apts:
                correct_assignments += 1

        accuracy = correct_assignments / total_cases

        print(f"\n{'='*70}")
        print(f"APT Group Assignment Realism Analysis")
        print(f"{'='*70}")
        print(f"Accuracy: {accuracy:.1%}")
        print(f"Correct: {correct_assignments}/{total_cases}")
        print(f"Requirement: ≥85%")
        print(f"Status: {'✓ PASS' if accuracy >= 0.85 else '✗ FAIL'}")
        print(f"{'='*70}\n")

        assert accuracy >= 0.85, f"APT assignment accuracy {accuracy:.1%} below 85%"

    def test_tenable_vpr_component_weights(self):
        """
        Verify that Tenable VPR components follow correct weights.

        This ensures VPR calculation is mathematically sound.
        """
        mock = TenableVPRMock()

        # Test maximum values
        result = mock.calculate_vpr(
            cvss_score=10.0,
            epss_score=1.0,
            asset_criticality="critical",
            known_exploited=True,
            age_days=1,
            product_coverage=1.0
        )

        components = result["vpr_components"]

        print(f"\n{'='*70}")
        print(f"Tenable VPR Component Weights Verification")
        print(f"{'='*70}")
        print(f"CVSS component: {components['cvss']:.2f} / 3.50 max (35%)")
        print(f"Threat component: {components['threat']:.2f} / 3.50 max (35%)")
        print(f"Asset criticality: {components['asset_criticality']:.2f} / 2.00 max (20%)")
        print(f"Product coverage: {components['product_coverage']:.2f} / 1.00 max (10%)")
        print(f"Total VPR: {result['vpr_score']:.1f} / 10.0 max")
        print(f"{'='*70}\n")

        # Verify maximums
        assert components["cvss"] <= 3.5, "CVSS component exceeds max"
        assert components["threat"] <= 3.5, "Threat component exceeds max"
        assert components["asset_criticality"] <= 2.0, "Criticality component exceeds max"
        assert components["product_coverage"] <= 1.0, "Coverage component exceeds max"
        assert result["vpr_score"] <= 10.0, "VPR score exceeds max"

    def test_crowdstrike_behavior_diversity(self):
        """
        Verify that CrowdStrike sandbox reports have diverse behaviors.

        This ensures reports are realistic and not repetitive.
        """
        mock = CrowdStrikeSandboxMock(seed=42)

        # Generate 50 malicious reports
        all_categories = []
        all_severities = []
        all_techniques = []
        all_malware_families = []

        for i in range(50):
            result = mock.generate_sandbox_report(
                file_hash=f"test_hash_{i}",
                malicious=True
            )

            all_malware_families.append(result["malware_family"])

            for behavior in result["behaviors"]:
                all_categories.append(behavior["category"])
                all_severities.append(behavior["severity"])

            all_techniques.extend(result["mitre_techniques"])

        # Count unique values
        unique_categories = len(set(all_categories))
        unique_severities = len(set(all_severities))
        unique_techniques = len(set(all_techniques))
        unique_families = len(set(all_malware_families))

        print(f"\n{'='*70}")
        print(f"CrowdStrike Behavior Diversity Analysis")
        print(f"{'='*70}")
        print(f"Unique behavior categories: {unique_categories}")
        print(f"Unique severities: {unique_severities}")
        print(f"Unique MITRE techniques: {unique_techniques}")
        print(f"Unique malware families: {unique_families}")
        print(f"Total behaviors generated: {len(all_categories)}")
        print(f"Total techniques generated: {len(all_techniques)}")
        print(f"{'='*70}\n")

        # Verify diversity
        assert unique_categories >= 4, "Insufficient behavior category diversity"
        assert unique_severities >= 3, "Insufficient severity diversity"
        assert unique_techniques >= 8, "Insufficient MITRE technique diversity"
        assert unique_families >= 10, "Insufficient malware family diversity"

    @staticmethod
    def _pearson_correlation(x: list, y: list) -> float:
        """Calculate Pearson correlation coefficient.

        Args:
            x: First data series
            y: Second data series

        Returns:
            Correlation coefficient (-1 to 1)
        """
        n = len(x)
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)

        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denominator = (
            sum((x[i] - mean_x) ** 2 for i in range(n)) *
            sum((y[i] - mean_y) ** 2 for i in range(n))
        ) ** 0.5

        return numerator / denominator if denominator != 0 else 0
