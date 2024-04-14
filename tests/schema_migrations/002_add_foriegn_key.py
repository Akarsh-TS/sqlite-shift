from sqlite_shift.base_migration import BaseMigration


class Migration(BaseMigration):
    db_name = "test_db"

    def upgrade(cls, conn):
        cursor = conn.cursor()
        cursor.execute(
            """
            ALTER TABLE users
            ADD COLUMN age INTEGER;
        """
        )

    def downgrade(cls, conn):
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE users DROP COLUMN age;")
        conn.commit()
