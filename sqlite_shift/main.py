import argparse
import os

from sqlite_shift.manager import MigrationManager


def main():
    parser = argparse.ArgumentParser(
        description="sqlite-shift: SQLite Migrations Manager"
    )
    parser.add_argument(
        "command",
        choices=["apply", "revert", "create"],
        help="Command to execute (apply, revert, check)",
    )
    parser.add_argument("dbname", help="Name of the database")
    parser.add_argument("--config", help="Path to the configuration file")
    parser.add_argument(
        "--migration_name",
        required=False,
        help="Name of the migration file, required for 'create' command",
    )

    args = parser.parse_args()

    if args.config is not None and os.path.isfile(args.config) is False:
        parser.error(f"Configuration file '{args.config}' not found.")

    manager = MigrationManager(args.dbname, args.config)

    if args.command == "apply":
        manager.apply_all_migrations()
    elif args.command == "revert":
        manager.revert_last_migration()
    elif args.command == "create":
        if args.migration_name is None:
            parser.error(
                f"Migration name not found, please provide a name for the migration using the --migration_name argument"
            )
        manager.create_migration(args.migration_name)


if __name__ == "__main__":
    main()
