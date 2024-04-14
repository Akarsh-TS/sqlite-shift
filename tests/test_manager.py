import pytest
import sqlite3

@pytest.mark.usefixtures("migration_manager")
class TestMigrationManager:
    def test_apply_and_revert_migrations(self, migration_manager, test_db_path):
        """Test applying and reverting migrations."""
        # Apply all migrations
        migration_manager.apply_all_migrations()

        # Verify the changes in the database
        conn = sqlite3.connect(str(test_db_path))
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT version FROM schema_migrations_sqlite_shift ORDER BY id ASC;")
            versions = [row[0] for row in cursor.fetchall()]
            print("versions",versions)
            assert len(versions) == 2, "Two migrations should be applied."
            assert versions == ["001_initial", "002_add_foriegn_key"], "Migrations should match expected versions."

            # Revert last migration
            migration_manager.revert_last_migration()

            # Check state after revert
            cursor.execute("SELECT version FROM schema_migrations_sqlite_shift ORDER BY id ASC;")
            versions = [row[0] for row in cursor.fetchall()]
            assert len(versions) == 1, "Only one migration should remain after revert."
            assert versions == ["001_initial"], "Remaining migration should be the initial one."
        finally:
            conn.close()

