# sqlite-shift

## Description
`sqlite-shift` is a streamlined framework for managing SQLite database migrations, inspired by Django's methodology, offering an intuitive approach to schema evolution.

## Table of Contents
1. [Installation](#Installation)
2. [Features](#Features)
3. [Usage](#Usage)
4. [Examples](#Examples)
5. [Contribution](#Contribution)
6. [License](#License)

## Installation
You can install SQLite-Shift via pip:
```
pip install sqlite-shift
```
## Features & Usage
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
    Refer to [Migration Structure](###MigrationStructure) on how to implement a migration file.

 5. Apply a Migration
    ```
    sqlite-shift apply test_db
    ```
 6. Revert a Migration
    ```
    sqlite-shift revert test_db
    ```
    


## Migration Structure

hi
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


## Examples
## Contribution
## License
Licensed under the **Apache License 2.0**.
