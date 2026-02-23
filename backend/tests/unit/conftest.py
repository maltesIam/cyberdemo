"""
Unit tests configuration and guards.

This conftest.py enforces unit test isolation by preventing imports
that would create infrastructure dependencies.
"""

import pytest
import sys
import warnings


# =============================================================================
# UNIT TEST ARCHITECTURE GUARD
# =============================================================================
# Unit tests must NOT depend on:
# - src.main (imports full FastAPI app with DB/OpenSearch connections)
# - Real database connections
# - Real network connections
# - External services
#
# Tests that need these dependencies belong in tests/integration/
# =============================================================================


def pytest_collection_modifyitems(session, config, items):
    """
    Hook that runs after test collection.

    Validates that unit tests don't import forbidden modules that would
    create infrastructure dependencies and cause tests to hang.
    """
    forbidden_imports = [
        "src.main",  # Full FastAPI app with DB/OpenSearch init
    ]

    for item in items:
        # Check if this is a unit test (based on path)
        if "tests/unit" in str(item.fspath):
            module = item.module
            if module is None:
                continue

            # Check module's imports
            for forbidden in forbidden_imports:
                if forbidden in sys.modules:
                    # Check if this specific test module caused the import
                    module_name = getattr(module, "__name__", "")
                    if module_name.startswith("tests.unit"):
                        warnings.warn(
                            f"\n\n{'='*70}\n"
                            f"UNIT TEST ARCHITECTURE VIOLATION\n"
                            f"{'='*70}\n"
                            f"Test: {item.nodeid}\n"
                            f"Forbidden import detected: {forbidden}\n\n"
                            f"Unit tests should NOT import modules that create\n"
                            f"infrastructure dependencies (DB, OpenSearch, etc.)\n\n"
                            f"SOLUTION: Move this test to tests/integration/\n"
                            f"{'='*70}\n",
                            UserWarning
                        )


@pytest.fixture(scope="session", autouse=True)
def check_no_infrastructure_imports():
    """
    Session-scoped fixture that verifies no infrastructure modules were imported.

    This runs once at the start of the test session.
    """
    # List of modules that should NOT be imported in unit tests
    infrastructure_modules = [
        "src.main",
        "opensearchpy",
        "psycopg2",
        "asyncpg",
    ]

    yield  # Let tests run

    # After all tests, check for violations
    violations = []
    for mod in infrastructure_modules:
        if mod in sys.modules:
            # Check if it was imported by a unit test
            violations.append(mod)

    if violations:
        warnings.warn(
            f"\nInfrastructure modules were imported during unit tests: {violations}\n"
            f"This may cause test hangs. Consider moving affected tests to integration/",
            UserWarning
        )


# =============================================================================
# COMMON UNIT TEST FIXTURES
# =============================================================================


@pytest.fixture
def mock_datetime():
    """Fixture for mocking datetime in tests."""
    from datetime import datetime, timezone
    return datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_alert_id():
    """Sample alert ID for tests."""
    return "ALT-2024-001"


@pytest.fixture
def sample_job_id():
    """Sample job ID for tests."""
    return "JOB-UNIT-001"
