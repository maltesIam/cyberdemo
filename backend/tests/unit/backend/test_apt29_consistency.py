"""
Unit tests for APT29 cross-reference consistency.

Task: T-021
Requirement: REQ-002-002-005
Test ID: UT-029

Tests that cross-references between SIEM incidents, EDR detections,
and Intel IOCs are consistent within the APT29 scenario.
"""

import pytest


class TestAPT29CrossReferenceConsistency:
    """Tests for cross-reference consistency between data types."""

    def test_siem_incident_ips_match_iocs(self):
        """IP addresses referenced in SIEM incidents must have matching IOC entries."""
        from src.scenarios.apt29 import APT29_PHASES
        # Collect all IOC IP values
        ioc_ips = set()
        for phase in APT29_PHASES.values():
            for ioc in phase["intel_iocs"]:
                if ioc["type"] == "ip":
                    ioc_ips.add(ioc["value"])

        # Check SIEM incidents that reference IPs
        for phase in APT29_PHASES.values():
            for inc in phase["siem_incidents"]:
                if "source_ip" in inc:
                    # The source_ip in an incident should match an IOC if it's malicious
                    if inc.get("is_malicious_ip", False):
                        assert inc["source_ip"] in ioc_ips, (
                            f"Incident {inc['id']} references malicious IP "
                            f"{inc['source_ip']} not in IOCs"
                        )

    def test_edr_detections_reference_valid_hosts(self):
        """EDR detection hosts must be from the scenario's target environment."""
        from src.scenarios.apt29 import APT29_PHASES, APT29_METADATA
        valid_hosts = set(APT29_METADATA.get("target_hosts", []))
        # If no target_hosts defined, skip
        if not valid_hosts:
            pytest.skip("No target_hosts defined in metadata")

        for phase in APT29_PHASES.values():
            for det in phase["edr_detections"]:
                assert det["host"] in valid_hosts, (
                    f"Detection {det['id']} references unknown host {det['host']}"
                )

    def test_siem_detection_ids_match_edr(self):
        """SIEM incidents with detection_ids must reference existing EDR detections."""
        from src.scenarios.apt29 import APT29_PHASES
        # Collect all EDR detection IDs
        all_edr_ids = set()
        for phase in APT29_PHASES.values():
            for det in phase["edr_detections"]:
                all_edr_ids.add(det["id"])

        # Check SIEM incidents that reference detection IDs
        for phase in APT29_PHASES.values():
            for inc in phase["siem_incidents"]:
                if "detection_ids" in inc:
                    for det_id in inc["detection_ids"]:
                        assert det_id in all_edr_ids, (
                            f"Incident {inc['id']} references non-existent "
                            f"detection {det_id}"
                        )

    def test_mitre_tactics_consistent_with_phase(self):
        """Incident and detection MITRE tactics must match their phase's tactic."""
        from src.scenarios.apt29 import APT29_PHASES
        for phase_num, phase in APT29_PHASES.items():
            phase_tactic = phase["mitre_tactic"]
            for inc in phase["siem_incidents"]:
                assert inc["mitre_tactic"] == phase_tactic, (
                    f"Phase {phase_num} incident {inc['id']} tactic "
                    f"{inc['mitre_tactic']} != phase tactic {phase_tactic}"
                )

    def test_edr_hash_iocs_consistent(self):
        """File hashes in EDR detections must match hash IOCs when referenced."""
        from src.scenarios.apt29 import APT29_PHASES
        # Collect all hash IOCs
        ioc_hashes = set()
        for phase in APT29_PHASES.values():
            for ioc in phase["intel_iocs"]:
                if ioc["type"] == "hash":
                    ioc_hashes.add(ioc["value"])

        # Check EDR detections with file hashes
        for phase in APT29_PHASES.values():
            for det in phase["edr_detections"]:
                if "file_hash" in det and det.get("is_malicious_hash", False):
                    assert det["file_hash"] in ioc_hashes, (
                        f"Detection {det['id']} references malicious hash "
                        f"{det['file_hash']} not in IOCs"
                    )

    def test_domain_iocs_referenced_in_network_incidents(self):
        """Domain IOCs should be referenced in at least one incident or detection."""
        from src.scenarios.apt29 import APT29_PHASES
        # Collect domain IOC values
        domain_iocs = set()
        for phase in APT29_PHASES.values():
            for ioc in phase["intel_iocs"]:
                if ioc["type"] == "domain":
                    domain_iocs.add(ioc["value"])

        if not domain_iocs:
            pytest.skip("No domain IOCs defined")

        # Collect all domains referenced in incidents and detections
        referenced_domains = set()
        for phase in APT29_PHASES.values():
            for inc in phase["siem_incidents"]:
                if "c2_domain" in inc:
                    referenced_domains.add(inc["c2_domain"])
            for det in phase["edr_detections"]:
                if "c2_domain" in det:
                    referenced_domains.add(det["c2_domain"])

        # At least one domain IOC must be referenced somewhere
        overlap = domain_iocs & referenced_domains
        assert len(overlap) >= 1, (
            f"No domain IOCs are referenced in incidents/detections. "
            f"IOCs: {domain_iocs}, Referenced: {referenced_domains}"
        )

    def test_no_orphan_cross_references(self):
        """All cross-references in the scenario must resolve to existing entities."""
        from src.scenarios.apt29 import APT29_PHASES
        all_incident_ids = set()
        all_detection_ids = set()
        all_ioc_ids = set()

        for phase in APT29_PHASES.values():
            for inc in phase["siem_incidents"]:
                all_incident_ids.add(inc["id"])
            for det in phase["edr_detections"]:
                all_detection_ids.add(det["id"])
            for ioc in phase["intel_iocs"]:
                all_ioc_ids.add(ioc["id"])

        # Check incident -> detection references
        for phase in APT29_PHASES.values():
            for inc in phase["siem_incidents"]:
                for ref in inc.get("detection_ids", []):
                    assert ref in all_detection_ids, (
                        f"Incident {inc['id']} references missing detection {ref}"
                    )
                for ref in inc.get("ioc_ids", []):
                    assert ref in all_ioc_ids, (
                        f"Incident {inc['id']} references missing IOC {ref}"
                    )
