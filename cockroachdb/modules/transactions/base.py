from cockroachdb.modules.connection import database


class BaseTransaction:
    @database.atomic()
    def execute(self):
        raise NotImplementedError(
            f"{self.__class__.__name__} should implement execute() method"
        )
