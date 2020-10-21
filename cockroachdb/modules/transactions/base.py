from abc import ABC, abstractmethod

from cockroachdb.modules.connection import database
from common.logging import console, logger


class BaseTransaction(ABC):
    database = database

    def run(self, print_to_console=True, *args, **kwargs):
        with database.atomic():
            outputs = self._execute(*args, **kwargs)
        try:
            if print_to_console and outputs is not None:
                BaseTransaction._print_divider()
                self._output_result(*outputs)
        except Exception as e:
            transaction_name = self.__class__.__name__
            logger.exception(e)
            logger.error(
                f"Error occurred while printing output to console, but {transaction_name} was executed successfully."
            )

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
