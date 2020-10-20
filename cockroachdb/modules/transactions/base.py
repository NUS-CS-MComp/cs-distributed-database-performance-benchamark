from abc import ABC, abstractmethod

from cockroachdb.modules.connection import database
from common.logging import console


class BaseTransaction(ABC):
    database = database

    @database.atomic()
    def run(self, print_to_console=True, *args, **kwargs):
        outputs = self._execute(*args, **kwargs)
        if print_to_console and outputs is not None:
            BaseTransaction._print_divider()
            self._output_result(*outputs)
            BaseTransaction._print_divider()

    @abstractmethod
    def _execute(self, *args, **kwargs):
        pass

    def _output_result(self, *args, **kwargs):
        pass

    @staticmethod
    def _print_divider():
        console.print(
            "================================================================================"
        )

    @property
    @abstractmethod
    def transaction_name(self):
        pass
