from abc import ABC, abstractmethod

from cockroachdb.modules.connection import database


class BaseTransaction(ABC):
    database = database

    @database.atomic()
    def run(self, *args, **kwargs):
        self._execute(*args, **kwargs)

    @abstractmethod
    def _execute(self, *args, **kwargs):
        pass

    @property
    @abstractmethod
    def transaction_name(self):
        pass
