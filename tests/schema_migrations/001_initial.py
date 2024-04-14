from sqlite3 import Connection

from sqlite_shift.base_migration import BaseMigration



class Migration(BaseMigration):
    db_name = "test_db"
    previous_migration = "None"

    def upgrade(cls, conn: Connection):
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT NOT NULL
            );
        """
        )
        conn.commit()

    def downgrade(cls, conn):
        cursor = conn.cursor()
        cursor.execute("DROP TABLE users;")
        conn.commit()
