# sqlite-shift

## Description
`sqlite-shift` is a streamlined framework for managing SQLite database migrations, inspired by Django's methodology, offering an intuitive approach to schema evolution.

## Table of Contents
1. [Installation](#installation)
2. [Features](#features)
3. [Basic Usage](#basic-usage)
4. [Migration Structure](#migration-structure)
5. [Migration Manager](#migration-manager)
6. [Contribution](#Contribution)
7. [License](#License)

## Installation
You can install SQLite-Shift via pip:
```
pip install sqlite-shift
```
## Features
* **Automatic Dependency Tracking**: Automatically track and manage migration dependencies based on the order of execution.
* **Configuration Options**: Customize migration paths, database connections, and other settings via a configuration file.
* **CLI Support**: Command-line interface for convenient migration management.
* **Structured**: A systematic and developer friendly way to write and maintain migrations.

## Basic Usage

### 1. Create a configuration file
SQLite-Shift utilizes a configuration file to manage settings such as database connection details and migration paths. To create a configuration file:
1. Create a new file named migrations.ini in your project directory.
2. Add the following configuration options:
   ```
    [test_db] # Database name  
    db_path = /path/to/database.db # Database path
    migrations_path = /path/to/migrations # The directory path where migration files are to be stored for this database.
   ```
 3. Generate a Migration
    Use the create_migration command from the SQLite-Shift CLI
    ```
    sqlite-shift create test_db --migration_name add_users_table
    ```
    Refer to [Migration Structure](#migration-structure) on how to implement a migration file.

 5. Apply a Migration
    ```
    sqlite-shift apply test_db
    ```
 6. Revert a Migration
    ```
    sqlite-shift revert test_db
    ```
    


## Migration Structure
* To apply a migration, **sqlite-shift** uses the `upgrade` method defined in each migration file. When `apply_all_migrations` is called, S **sqlite-shift** iterates through all migration files in the specified directory and applies them in the correct order based on their dependencies.
* To revert a migration, **sqlite-shift** uses the `downgrade` method defined in each migration file. When `revert_last_migration` is called,  **sqlite-shift** reverts the last applied migration by executing the downgrade method of the corresponding migration file.
* All migrations will be executed within a **transaction**

```
from sqlite_shift.core.base_migration import BaseMigration

class Migration(BaseMigration):  # All migration classes should extend "BaseMigration" class
    def upgrade(self, conn): # class method that will be used while applying a migration
        # Add 'users' table to the database schema
        conn.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT NOT NULL
            );
        """)

    def downgrade(self, conn): # class method that will be used while revertinf a migration
        # Remove 'users' table from the database schema
        conn.execute("DROP TABLE users;")

```

## Migration Manager
The Migration Manager class in **sqlite-shift** provides a set of methods to manage database migrations.

### Initialisation
```
from sqlite_shift import MigrationManager

# Initialize Migration Manager
manager = MigrationManager(db_name="example_db", config_file_path="migrations.ini")
```
Accepts the following parameters on initialisation
1. **db_name**: The database to be used
2. **config_file_path**: The path for the configuration file. By default, it tries to find the config file in the project root directory.

### Methods

```
manager.apply_all_migrations()  # Applies all unapplied migrations in the specified migrations directory to the database.
manager.revert_last_migration() # Reverts the last applied migration from the database.
```

## Contribution
## License
Licensed under the **Apache License 2.0**.
