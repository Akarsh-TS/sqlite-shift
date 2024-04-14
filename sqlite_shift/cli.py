import click

from sqlite_shift.manager import MigrationManager


@click.group()
def cli():
    pass

@cli.command()
@click.argument('dbname')
@click.option('--config', help="Path to the configuration file", type=click.Path(exists=True))
def apply(dbname, config):
    """Apply all pending migrations."""
    manager = MigrationManager(dbname, config)
    manager.apply_all_migrations()

@cli.command()
@click.argument('dbname')
@click.option('--config', help="Path to the configuration file", type=click.Path(exists=True))
def revert(dbname, config):
    """Revert the last applied migration."""
    manager = MigrationManager(dbname, config)
    manager.revert_last_migration()

@cli.command()
@click.argument('dbname')
@click.option('--config', help="Path to the configuration file", type=click.Path(exists=True))
@click.option('--migration_name', required=True, help="Name of the migration file")
def create(dbname, config, migration_name):
    """Create a new migration file."""
    # Validate the migration name to ensure it contains only lowercase letters and underscores
    if not all(c.islower() or c == '_' for c in migration_name):
        raise click.BadParameter("Migration name can only have lowercase alphabets and underscore.")
    
    manager = MigrationManager(dbname, config)
    manager.create_migration(migration_name)

if __name__ == '__main__':
    cli()