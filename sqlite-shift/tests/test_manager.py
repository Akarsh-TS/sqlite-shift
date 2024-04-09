import unittest
import os
import sqlite3
from core.manager import MigrationManager


class TestMigrationManager(unittest.TestCase):
    def setUp(self):
        self.create_test_database()

        # Initialize MigrationManager instance with test configuration
        self.manager = MigrationManager("test_db", "tests/resources/migrations.ini")

    def tearDown(self):
        # Delete sample test database
        self.delete_test_database()

    def create_test_database(self):
        # Create an empty test database file
        open("tests/resources/test_db.sqlite", "w").close()

    def delete_test_database(self):
        # Delete the test database
        os.remove("tests/resources/test_db.sqlite")

    def test_apply_and_revert_migrations(self):
        # Test applying and reverting migrations
        # Apply all migrations
        self.manager.apply_all_migrations()

        # Verify the changes in the database after applying migrations
        with sqlite3.connect("tests/resources/test_db.sqlite") as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT version FROM schema_migrations order by id asc;")
            values = cursor.fetchall()
            self.assertEqual(len(values), 2)
            versions = [v[0] for v in values]

            self.assertListEqual(["001_initial", "002_add_foriegn_key"], versions)

            # Check if the 'users' table exists and has the 'age' column
            cursor.execute("PRAGMA table_info(users);")
            users_table_info = cursor.fetchall()
            self.assertTrue(
                any(col[1] == "age" for col in users_table_info),
                "Column 'age' was not added to 'users' table",
            )

        # Revert last migration
        self.manager.revert_last_migration()

        # Verify the changes in the database after reverting last migration
        with sqlite3.connect("tests/resources/test_db.sqlite") as conn:
            cursor = conn.cursor()
            # Check if the 'users' table exists and does not have the 'age' column
            cursor.execute("PRAGMA table_info(users);")
            users_table_info = cursor.fetchall()
            self.assertFalse(
                any(col[1] == "age" for col in users_table_info),
                "Column 'age' was not removed from 'users' table",
            )

            cursor.execute("SELECT version FROM schema_migrations order by id asc;")
            values = cursor.fetchall()
            versions = [v[0] for v in values]
            self.assertEqual(len(values), 1)
            self.assertListEqual(["001_initial"], versions)


if __name__ == "__main__":
    unittest.main()
