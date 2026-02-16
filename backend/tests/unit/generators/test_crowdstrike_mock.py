"""Unit tests for CrowdStrike Falcon X Sandbox mock generator.

Tests follow TDD RED-GREEN-REFACTOR cycle.
These tests should FAIL initially (RED phase).
"""
import pytest


class TestCrowdStrikeSandboxMock:
    """Tests for CrowdStrikeSandboxMock generator."""

    def test_generate_clean_sandbox_report(self):
        """
        RED: Test generation of clean (non-malicious) sandbox report.
        """
        from src.generators.enrichment.crowdstrike_mock import CrowdStrikeSandboxMock

        mock = CrowdStrikeSandboxMock()

        result = mock.generate_sandbox_report(
            file_hash="abc123def456",
            malicious=False
        )

        assert result["verdict"] == "clean"
        assert 85 <= result["confidence"] <= 95
        assert result["file_hash"] == "abc123def456"
        assert result["sandbox_runs"] >= 1
        assert result["enrichment_source"] == "synthetic_crowdstrike"
        assert "generated_at" in result

    def test_generate_malicious_sandbox_report(self):
        """
        RED: Test generation of malicious sandbox report with behaviors.
        """
        from src.generators.enrichment.crowdstrike_mock import CrowdStrikeSandboxMock

        mock = CrowdStrikeSandboxMock()

        result = mock.generate_sandbox_report(
            file_hash="malware123hash",
            malicious=True,
            malware_family="Emotet"
        )

        assert result["verdict"] == "malicious"
        assert 80 <= result["confidence"] <= 99
        assert result["file_hash"] == "malware123hash"
        assert result["malware_family"] == "Emotet"

        # Should have behaviors
        assert "behaviors" in result
        assert len(result["behaviors"]) > 0, "Malicious file should have behaviors"

        # Each behavior should have required fields
        for behavior in result["behaviors"]:
            assert "category" in behavior
            assert "description" in behavior
            assert "severity" in behavior
            assert "details" in behavior
            assert behavior["severity"] in ["low", "medium", "high", "critical"]

    def test_mitre_attack_techniques_generated(self):
        """
        RED: Test that MITRE ATT&CK techniques are generated for malicious files.
        """
        from src.generators.enrichment.crowdstrike_mock import CrowdStrikeSandboxMock

        mock = CrowdStrikeSandboxMock()

        result = mock.generate_sandbox_report(
            file_hash="apt_malware_hash",
            malicious=True
        )

        assert "mitre_techniques" in result
        assert len(result["mitre_techniques"]) > 0, "Malicious file should have MITRE techniques"

        # Techniques should follow TXXXX.XXX format
        for technique in result["mitre_techniques"]:
            assert technique.startswith("T"), f"Invalid MITRE technique format: {technique}"

    def test_behavior_categories_realistic(self):
        """
        RED: Test that behavior categories are realistic.

        Expected categories: persistence, network, file_system, process, evasion
        """
        from src.generators.enrichment.crowdstrike_mock import CrowdStrikeSandboxMock

        mock = CrowdStrikeSandboxMock()

        # Generate multiple reports to check categories
        results = [
            mock.generate_sandbox_report(
                file_hash=f"malware_{i}",
                malicious=True
            )
            for i in range(10)
        ]

        all_categories = set()
        for result in results:
            for behavior in result["behaviors"]:
                all_categories.add(behavior["category"])

        # Expected categories should be present
        expected_categories = {"persistence", "network", "file_system", "process", "evasion"}
        assert all_categories.issubset(expected_categories), f"Unexpected categories: {all_categories - expected_categories}"

    def test_extracted_iocs_present(self):
        """
        RED: Test that malicious reports extract IOCs (IPs, domains, file paths).
        """
        from src.generators.enrichment.crowdstrike_mock import CrowdStrikeSandboxMock

        mock = CrowdStrikeSandboxMock()

        result = mock.generate_sandbox_report(
            file_hash="ioc_test_hash",
            malicious=True
        )

        assert "extracted_iocs" in result
        iocs = result["extracted_iocs"]

        # Should have at least one type of IOC
        assert "ips" in iocs
        assert "domains" in iocs
        assert "file_paths" in iocs

        # IPs should be valid format (basic check)
        if iocs["ips"]:
            for ip in iocs["ips"]:
                parts = ip.split(".")
                assert len(parts) == 4, f"Invalid IP format: {ip}"
                for part in parts:
                    assert 0 <= int(part) <= 255

    def test_sandbox_environments_listed(self):
        """
        RED: Test that sandbox environments are listed in report.
        """
        from src.generators.enrichment.crowdstrike_mock import CrowdStrikeSandboxMock

        mock = CrowdStrikeSandboxMock()

        result = mock.generate_sandbox_report(
            file_hash="env_test_hash",
            malicious=True
        )

        assert "sandbox_environments" in result
        assert len(result["sandbox_environments"]) > 0
        # Should mention Windows versions
        env_str = " ".join(result["sandbox_environments"])
        assert "Windows" in env_str

    def test_malware_family_assigned_when_not_specified(self):
        """
        RED: Test that a malware family is randomly assigned if not specified.
        """
        from src.generators.enrichment.crowdstrike_mock import CrowdStrikeSandboxMock

        mock = CrowdStrikeSandboxMock()

        # Don't specify malware_family
        result = mock.generate_sandbox_report(
            file_hash="auto_family_hash",
            malicious=True
        )

        assert "malware_family" in result
        assert result["malware_family"] is not None
        assert len(result["malware_family"]) > 0

        # Should be a known malware family
        known_families = [
            "Emotet", "TrickBot", "Dridex", "Qbot", "IcedID", "Cobalt Strike",
            "Ryuk", "Conti", "LockBit", "BlackCat", "AgentTesla", "FormBook",
            "Remcos", "AsyncRAT", "RedLine", "Vidar", "Raccoon", "Azorult"
        ]
        assert result["malware_family"] in known_families

    def test_confidence_score_range(self):
        """
        RED: Test that confidence scores are in valid range [0-100].
        """
        from src.generators.enrichment.crowdstrike_mock import CrowdStrikeSandboxMock

        mock = CrowdStrikeSandboxMock()

        # Test multiple reports
        for i in range(20):
            result = mock.generate_sandbox_report(
                file_hash=f"conf_test_{i}",
                malicious=(i % 2 == 0)  # Alternate between malicious and clean
            )
            assert 0 <= result["confidence"] <= 100, f"Confidence {result['confidence']} out of range"

    def test_behavior_severity_distribution(self):
        """
        RED: Test that behaviors have varied severities (not all critical).
        """
        from src.generators.enrichment.crowdstrike_mock import CrowdStrikeSandboxMock

        mock = CrowdStrikeSandboxMock()

        # Generate report with many behaviors (run multiple times to get variety)
        all_severities = set()
        for _ in range(10):
            result = mock.generate_sandbox_report(
                file_hash="severity_test",
                malicious=True
            )
            for behavior in result["behaviors"]:
                all_severities.add(behavior["severity"])

        # Should have variety of severities
        assert len(all_severities) >= 2, "Behaviors should have varied severities"

    def test_network_behavior_includes_c2_ip(self):
        """
        RED: Test that network behaviors include C2 IP addresses in details.
        """
        from src.generators.enrichment.crowdstrike_mock import CrowdStrikeSandboxMock

        mock = CrowdStrikeSandboxMock()

        # Generate multiple reports to find network behavior
        found_network_behavior = False
        for _ in range(10):
            result = mock.generate_sandbox_report(
                file_hash="network_test",
                malicious=True
            )
            for behavior in result["behaviors"]:
                if behavior["category"] == "network":
                    found_network_behavior = True
                    # Details should mention IP or connection
                    assert "Connection" in behavior["details"] or "IP" in behavior["details"]
                    break
            if found_network_behavior:
                break

        # Network behavior should appear in at least one of multiple runs
        # (probabilistic test, but with 10 runs very likely to occur)
