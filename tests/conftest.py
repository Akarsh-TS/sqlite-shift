import pytest
import os
from pathlib import Path

@pytest.fixture(scope="session")
def root_dir():
    """Fixture to return the root directory of the project."""
    return Path(__file__).parent.parent

@pytest.fixture
def test_db_path(root_dir):
    """Fixture to provide the test database path, ensuring isolation."""

    test_db = root_dir / 'tests' / 'test_db.sqlite'
    if not test_db.exists():
        open(test_db, 'w').close()  # Create an empty SQLite file

    yield test_db
    # Teardown: Remove the test database after each test session
    if test_db.exists():
        test_db.unlink()

@pytest.fixture
def migration_manager(root_dir, test_db_path):
    """Fixture to initialize MigrationManager with test configuration."""
    from sqlite_shift.manager import MigrationManager
    config_path = root_dir / 'tests' / 'migrations.ini'
    return MigrationManager("test_db", str(config_path))
