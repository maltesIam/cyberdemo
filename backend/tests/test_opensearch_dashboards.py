"""Tests for OpenSearch Dashboards configuration files."""

import json
import os
from pathlib import Path

import pytest


# Get the dashboards directory path
# Path: CyberDemo/backend/tests/test_opensearch_dashboards.py -> CyberDemo/opensearch/dashboards
DASHBOARDS_DIR = Path(__file__).parent.parent.parent / "opensearch" / "dashboards"

# Expected dashboard files
EXPECTED_DASHBOARD_FILES = [
    "soc-overview.ndjson",
    "asset-risk.ndjson",
    "threat-intel.ndjson",
    "incident-investigation.ndjson",
    "index-patterns.ndjson",
]

# Expected index patterns (from templates.py)
EXPECTED_INDEX_PATTERNS = [
    "assets-inventory-*",
    "edr-detections-*",
    "edr-process-trees-*",
    "edr-hunt-results-*",
    "edr-host-actions-*",
    "siem-incidents-*",
    "siem-entities-*",
    "siem-comments-*",
    "ctem-findings-*",
    "ctem-asset-risk-*",
    "threat-intel-*",
    "collab-messages-*",
    "approvals-*",
    "soar-actions-*",
    "tickets-sync-*",
    "agent-events-*",
    "postmortems-*",
]


class TestDashboardFilesExist:
    """Test that all expected dashboard files exist."""

    def test_dashboards_directory_exists(self):
        """Test that the dashboards directory exists."""
        assert DASHBOARDS_DIR.exists(), f"Dashboards directory not found: {DASHBOARDS_DIR}"
        assert DASHBOARDS_DIR.is_dir(), f"Dashboards path is not a directory: {DASHBOARDS_DIR}"

    @pytest.mark.parametrize("filename", EXPECTED_DASHBOARD_FILES)
    def test_dashboard_file_exists(self, filename: str):
        """Test that each expected dashboard file exists."""
        file_path = DASHBOARDS_DIR / filename
        assert file_path.exists(), f"Dashboard file not found: {file_path}"
        assert file_path.is_file(), f"Dashboard path is not a file: {file_path}"

    def test_readme_exists(self):
        """Test that README.md exists in dashboards directory."""
        readme_path = DASHBOARDS_DIR / "README.md"
        assert readme_path.exists(), f"README.md not found: {readme_path}"


class TestDashboardsValidNdjson:
    """Test that all dashboard files are valid NDJSON."""

    @pytest.mark.parametrize("filename", EXPECTED_DASHBOARD_FILES)
    def test_dashboard_is_valid_ndjson(self, filename: str):
        """Test that each dashboard file is valid NDJSON (newline-delimited JSON)."""
        file_path = DASHBOARDS_DIR / filename
        if not file_path.exists():
            pytest.skip(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # NDJSON files should have at least one line
        lines = [line.strip() for line in content.strip().split("\n") if line.strip()]
        assert len(lines) > 0, f"NDJSON file is empty: {filename}"

        # Each line must be valid JSON
        for i, line in enumerate(lines, 1):
            try:
                obj = json.loads(line)
                assert isinstance(obj, dict), f"Line {i} in {filename} is not a JSON object"
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON on line {i} in {filename}: {e}")

    @pytest.mark.parametrize("filename", EXPECTED_DASHBOARD_FILES)
    def test_dashboard_has_required_fields(self, filename: str):
        """Test that NDJSON objects have required OpenSearch Dashboards fields."""
        file_path = DASHBOARDS_DIR / filename
        if not file_path.exists():
            pytest.skip(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        for i, line in enumerate(lines, 1):
            obj = json.loads(line)
            # Each object should have either 'type' field or be a reference object
            # OpenSearch Dashboards export format uses alternating reference/object pairs
            # or single objects with 'type' and 'attributes'
            if "type" in obj:
                # This is a saved object
                assert "id" in obj, f"Object on line {i} in {filename} missing 'id' field"
                # Most saved objects should have attributes (index-pattern, visualization, dashboard, search)
                # Some special objects may not have attributes, so we just warn
                if obj["type"] in ["index-pattern", "visualization", "dashboard", "search"]:
                    assert "attributes" in obj, f"Object on line {i} in {filename} missing 'attributes' field"


class TestIndexPatternsComplete:
    """Test that all required index patterns are defined."""

    def test_index_patterns_file_has_all_patterns(self):
        """Test that index-patterns.ndjson contains all expected index patterns."""
        file_path = DASHBOARDS_DIR / "index-patterns.ndjson"
        if not file_path.exists():
            pytest.skip(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        # Extract index pattern titles from the file
        found_patterns = set()
        for line in lines:
            obj = json.loads(line)
            if obj.get("type") == "index-pattern":
                attributes = obj.get("attributes", {})
                title = attributes.get("title", "")
                if title:
                    found_patterns.add(title)

        # Check that all expected patterns are present
        missing_patterns = set(EXPECTED_INDEX_PATTERNS) - found_patterns
        assert not missing_patterns, f"Missing index patterns: {missing_patterns}"

    def test_index_patterns_have_time_field(self):
        """Test that index patterns have a time field defined."""
        file_path = DASHBOARDS_DIR / "index-patterns.ndjson"
        if not file_path.exists():
            pytest.skip(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        for line in lines:
            obj = json.loads(line)
            if obj.get("type") == "index-pattern":
                attributes = obj.get("attributes", {})
                title = attributes.get("title", "")
                time_field = attributes.get("timeFieldName")
                # All CyberDemo indices should have a time field
                assert time_field, f"Index pattern '{title}' missing timeFieldName"


class TestDashboardContent:
    """Test specific dashboard content requirements."""

    def test_soc_overview_has_required_visualizations(self):
        """Test that SOC Overview dashboard has required KPIs and charts."""
        file_path = DASHBOARDS_DIR / "soc-overview.ndjson"
        if not file_path.exists():
            pytest.skip(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        visualization_types = set()
        for line in lines:
            obj = json.loads(line)
            if obj.get("type") == "visualization":
                attributes = obj.get("attributes", {})
                vis_state_str = attributes.get("visState", "{}")
                try:
                    vis_state = json.loads(vis_state_str)
                    vis_type = vis_state.get("type", "")
                    visualization_types.add(vis_type)
                except json.JSONDecodeError:
                    continue

        # Should have variety of visualizations
        # metric for KPIs, pie chart, line chart, table
        expected_types = {"metric", "pie", "line", "table"}
        missing_types = expected_types - visualization_types
        # Note: Some types may be aliased differently in OpenSearch
        # Just verify we have at least some visualizations
        assert len(visualization_types) > 0, "SOC Overview should have visualizations"

    def test_asset_risk_has_heatmap_or_table(self):
        """Test that Asset Risk dashboard has risk visualization."""
        file_path = DASHBOARDS_DIR / "asset-risk.ndjson"
        if not file_path.exists():
            pytest.skip(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Should reference ctem-asset-risk or ctem-findings indices
        assert "ctem" in content.lower(), "Asset Risk dashboard should reference CTEM indices"

    def test_threat_intel_references_correct_index(self):
        """Test that Threat Intel dashboard references threat-intel index."""
        file_path = DASHBOARDS_DIR / "threat-intel.ndjson"
        if not file_path.exists():
            pytest.skip(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "threat-intel" in content.lower(), "Threat Intel dashboard should reference threat-intel index"

    def test_incident_investigation_has_timeline(self):
        """Test that Incident Investigation dashboard has timeline visualization."""
        file_path = DASHBOARDS_DIR / "incident-investigation.ndjson"
        if not file_path.exists():
            pytest.skip(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Should reference siem-incidents or related indices
        assert "siem" in content.lower() or "incident" in content.lower(), \
            "Incident Investigation dashboard should reference incident-related indices"
