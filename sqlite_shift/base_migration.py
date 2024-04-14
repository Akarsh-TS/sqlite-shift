from abc import abstractmethod


class BaseMigration:
    db_name = None
    previous_migration = None
    description = ""

    @abstractmethod
    def upgrade(self, conn):
        pass
        # raise NotImplementedError(
        #     "The 'upgrade' method must be implemented by the subclass."
        # )

    @abstractmethod
    def downgrade(self, conn):
        pass
        # raise NotImplementedError(
        #     "The 'downgrade' method must be implemented by the subclass."
        # )
