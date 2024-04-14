import configparser
import os
import importlib.util
import re
import sqlite3
import time

ROOT_DIR = os.getcwd()


class MigrationManager:
    def __init__(self, db_name, config_file_path=None):
        self.config_file = os.path.join(ROOT_DIR, config_file_path if config_file_path else "migrations.ini")
        self.db_name = db_name
        self._read_config()
        self._validate_paths()
        self._ensure_migration_tracking_table()
        self._check_missing_migrations()

    def _read_config(self):
        if not os.path.isfile(self.config_file):
            raise FileNotFoundError(
                f"Configuration file 'migrations.ini' not found in the root directory. {self.config_file}"
            )

        config = configparser.ConfigParser()
        config.read(self.config_file)

        if self.db_name not in config:
            raise ValueError(
                f"Database '{self.db_name}' not found in the configuration file."
            )

        section = config[self.db_name]
        self.db_path = os.path.join(ROOT_DIR,section.get("DB_PATH"))
        self.migrations_path = os.path.join(ROOT_DIR,section.get("DB_MIGRATIONS_PATH"))

    def _validate_paths(self):
        # Validate the database path
        if not os.path.isfile(self.db_path):
            raise FileNotFoundError(
                f"The database file was not found at {self.db_path}."
            )

        # Validate the migrations directory exists
        if not os.path.isdir(self.migrations_path):
            raise FileNotFoundError(
                f"The migrations directory was not found at {self.migrations_path}."
            )

        # Ensure the migrations directory is named 'schema_migrations'
        dir_name = os.path.basename(os.path.normpath(self.migrations_path))
        
        
        if dir_name != "schema_migrations":
            raise ValueError(
                f"The migrations directory must be named 'schema_migrations', but was named '{dir_name}'."
            )
  
        if os.path.exists(os.path.join(self.migrations_path, '__init__.py')) is False:
            raise ValueError(
                f"The migrations directory '{self.migrations_path}' is not a valid Python module."
            )

        # Check if the migrations directory contains __init__.py
        init_py_file = os.path.join(self.migrations_path, "__init__.py")
        if not os.path.isfile(init_py_file):
            raise ValueError(
                f"The migrations directory '{self.migrations_path}' does not contain an __init__.py file."
            )

    def _ensure_migration_tracking_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT NOT NULL UNIQUE,
                    db_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            )
            conn.commit()

    def _get_applied_migrations(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Order by 'id' to ensure the migrations are returned in the order they were applied
            cursor.execute(
                "SELECT version FROM schema_migrations WHERE db_name = ? ORDER BY id ASC;",
                (self.db_name,),
            )
            return [row[0] for row in cursor.fetchall()]

    def _check_missing_migrations(self):
        applied_migrations = self._get_applied_migrations()
        migration_files = sorted(
            f[:-3]
            for f in os.listdir(self.migrations_path)
            if f.endswith(".py") and f != "__init__.py"
        )
        missing_migrations = [
            migration
            for migration in applied_migrations
            if migration not in migration_files
        ]
        if missing_migrations:
            print(
                "Warning: Some applied migrations are missing from the versions directory."
            )
            print(
                "Please ensure all migration files are present or revert the missing migrations manually."
            )
            print("Missing migrations:", ",".join(missing_migrations))
            raise RuntimeError(
                "Some applied migrations are missing from the versions directory. "
                "Please ensure all migration files are present or revert the missing migrations manually."
            )
        return missing_migrations

    def _record_migration_as_applied(self, version, conn: sqlite3.Connection):
        conn.execute(
            "INSERT INTO schema_migrations (version,db_name) VALUES (?,?) ;",
            (
                version,
                self.db_name,
            ),
        )

    def _remove_migration_record(self, version, conn: sqlite3.Connection):
        conn.execute(
            "DELETE FROM schema_migrations WHERE version = ? and db_name = ? ;",
            (
                version,
                self.db_name,
            ),
        )

    def _load_migration_module(self, migration_name: str):
        migration_path = os.path.join(self.migrations_path, migration_name + ".py")

        # Validate the migration file name format if necessary
        # E.g., ensuring it starts with a digit and follows a specific naming convention
        if not migration_name:
            raise ValueError(
                f"Migration file '{migration_name}' does not follow the required naming convention (e.g., '001_initial')."
            )

        # Dynamically load the migration module
        spec = importlib.util.spec_from_file_location(
            "migration_module", migration_path
        )
        migration_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration_module)

        # Validate that the migration module contains a Migration class
        if not hasattr(migration_module, "Migration"):
            raise AttributeError(
                f"Migration file '{migration_name}' does not contain a 'Migration' class."
            )

        # validate that the Migration class has 'upgrade' and 'downgrade' methods
        if not all(
            hasattr(migration_module.Migration, method)
            for method in ["upgrade", "downgrade"]
        ):
            raise NotImplementedError(
                f"Migration class in '{migration_name}' must implement 'upgrade' and 'downgrade' methods."
            )

        # Check if the migration module contains transactional operations
        with open(migration_path, "r") as file:
            migration_content = file.read()
            if (
                re.search(r"\bBEGIN TRANSACTION\b", migration_content)
                or re.search(r"\bCOMMIT\b", migration_content)
                or re.search(r"\bROLLBACK\b", migration_content)
            ):
                raise ValueError(
                    f"Migration file '{migration_name}' contains manual transaction operations. "
                    f"Please ensure transactions are managed by the MigrationManager."
                )

        return migration_module

    def _apply_migration(self, migration_name):
        migration_module = self._load_migration_module(migration_name)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("BEGIN")
            migration_module.Migration().upgrade(conn)
            self._record_migration_as_applied(migration_name, conn)
            conn.commit()

    def _revert_migration(self, migration_name):
        migration_module = self._load_migration_module(migration_name)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("BEGIN")
            migration_module.Migration().downgrade(conn)
            self._remove_migration_record(migration_name, conn)
            conn.commit()

    def _get_last_migration(self):
        # Get a list of migration files in the migrations directory
        migration_files = os.listdir(self.migrations_path)

        # Filter out non-migration files
        migration_files = [
            file
            for file in migration_files
            if file.endswith(".py") and file != "__init__.py"
        ]

        # Sort the migration files by timestamp in descending order
        migration_files.sort(reverse=True)

        # Extract the details of the last applied migration from the file name
        if migration_files:
            last_migration_file = migration_files[0]
            return last_migration_file[:-3]

        return None

    # Public Methods
    def apply_all_migrations(self):
        applied_migrations = self._get_applied_migrations()
        migration_files = sorted(
            f[:-3]
            for f in os.listdir(self.migrations_path)
            if f.endswith(".py") and f != "__init__.py"
        )
        for migration_name in migration_files:
            if migration_name not in applied_migrations:
                self._apply_migration(migration_name)
                print(f"Applied migration {migration_name}")

    def revert_last_migration(self):
        applied_migrations = self._get_applied_migrations()
        if applied_migrations:
            last_migration = applied_migrations[-1]
            self._revert_migration(last_migration)
            print(f"Reverted migration {last_migration}")
        else:
            print("No migrations have been applied.")

    def create_migration(self, migration_name: str):
        # Create a new migration file with a timestamp and the provided name

        timestamp = int(time.time())
        migration_file_name = f"{timestamp}_{migration_name}.py"

        migration_file_path = os.path.join(self.migrations_path, migration_file_name)
        previous_migration = self._get_last_migration()

        # Write the migration template to the new file
        with open(migration_file_path, "w") as f:
            f.write(
                f"""
from sqlite3 import Connection
from sqlite_shift.core.base_migration import BaseMigration

class Migration(BaseMigration):
    db_name = "{self.db_name}"
    previous_migration = "{previous_migration}"

    def upgrade(cls, conn:Connection):
        # To be implemented
        pass

    def downgrade(cls, conn:Connection):
        # To be implemented
        pass
"""
            )

        print(f"Created migration: {migration_file_name}")
