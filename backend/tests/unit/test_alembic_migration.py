"""
Unit tests for Alembic migration for analysis_jobs and webhook_configs tables.

Task: T-1.1.003
Agent: build-1
Requirements: TECH-004, TECH-005
TDD Phase: Tests for migration file structure.
"""
import pytest
from pathlib import Path


class TestAlembicMigrationExists:
    """Tests to verify Alembic migration file exists."""

    def test_alembic_directory_exists(self):
        """Test that alembic directory exists."""
        alembic_dir = Path("/home/oscar/NewProjects/SoulInTheBot/cyberdemo/backend/alembic")
        assert alembic_dir.exists()

    def test_alembic_versions_directory_exists(self):
        """Test that versions directory exists."""
        versions_dir = Path("/home/oscar/NewProjects/SoulInTheBot/cyberdemo/backend/alembic/versions")
        assert versions_dir.exists()

    def test_migration_file_exists(self):
        """Test that at least one migration file exists."""
        versions_dir = Path("/home/oscar/NewProjects/SoulInTheBot/cyberdemo/backend/alembic/versions")
        migration_files = list(versions_dir.glob("*.py"))
        assert len(migration_files) >= 1, "No migration files found"

    def test_migration_has_analysis_jobs_table(self):
        """Test that migration includes analysis_jobs table creation."""
        versions_dir = Path("/home/oscar/NewProjects/SoulInTheBot/cyberdemo/backend/alembic/versions")
        migration_files = list(versions_dir.glob("*.py"))
        assert len(migration_files) >= 1

        # Read the first migration file
        migration_content = migration_files[0].read_text()
        assert "analysis_jobs" in migration_content, "analysis_jobs table not in migration"

    def test_migration_has_webhook_configs_table(self):
        """Test that migration includes webhook_configs table creation."""
        versions_dir = Path("/home/oscar/NewProjects/SoulInTheBot/cyberdemo/backend/alembic/versions")
        migration_files = list(versions_dir.glob("*.py"))
        assert len(migration_files) >= 1

        # Read the first migration file
        migration_content = migration_files[0].read_text()
        assert "webhook_configs" in migration_content, "webhook_configs table not in migration"


class TestMigrationContent:
    """Tests for migration content structure."""

    @pytest.fixture
    def migration_content(self):
        """Load the migration file content."""
        versions_dir = Path("/home/oscar/NewProjects/SoulInTheBot/cyberdemo/backend/alembic/versions")
        migration_files = list(versions_dir.glob("*.py"))
        if not migration_files:
            pytest.skip("No migration files found")
        return migration_files[0].read_text()

    def test_migration_has_upgrade_function(self, migration_content):
        """Test that migration has upgrade function."""
        assert "def upgrade()" in migration_content

    def test_migration_has_downgrade_function(self, migration_content):
        """Test that migration has downgrade function."""
        assert "def downgrade()" in migration_content

    def test_analysis_jobs_has_required_columns(self, migration_content):
        """Test that analysis_jobs table has required columns."""
        required_columns = [
            "id",
            "job_type",
            "status",
            "payload",
            "result",
            "created_at",
            "updated_at",
        ]
        for col in required_columns:
            assert col in migration_content, f"Column {col} not found in migration"

    def test_webhook_configs_has_required_columns(self, migration_content):
        """Test that webhook_configs table has required columns."""
        required_columns = [
            "name",
            "url",
            "event_types",
            "timeout_seconds",
            "max_retries",
        ]
        for col in required_columns:
            assert col in migration_content, f"Column {col} not found in migration"

    def test_migration_creates_indexes(self, migration_content):
        """Test that migration creates necessary indexes."""
        # Check for index creation
        assert "create_index" in migration_content or "Index" in migration_content or "index=True" in migration_content

    def test_downgrade_drops_tables(self, migration_content):
        """Test that downgrade drops the created tables."""
        assert "drop_table" in migration_content or "op.drop_table" in migration_content
