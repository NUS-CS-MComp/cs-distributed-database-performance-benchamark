from abc import ABC, abstractmethod
from typing import List, Any

from cockroachdb.modules.connection import (
    database,
)
from common.logging import (
    console,
    create_table,
    logger,
    TableColumnInput,
    OUTPUT_DIVIDER,
)


class BaseTransaction(ABC):
    MAX_ATTEMPTS = 10

    def __init__(self):
        """
        Abstract base transaction class to be inherited
        """
        self._output_queue: List[Any] = []

    def run(self, print_to_console=True, *args, **kwargs):
        def execute_transaction(_database):
            """
            Thunk to execute actual transaction
            :param _database: database reference
            :return: execution result
            """
            return self._execute(*args, **kwargs)

        outputs = database.run_transaction(
            execute_transaction, max_attempts=BaseTransaction.MAX_ATTEMPTS
        )

        try:
            if print_to_console and outputs is not None:
                self._output_result(*outputs)
                self.flush_output()
        except Exception as e:
            transaction_name = self.__class__.__name__
            logger.exception(e)
            logger.error(
                f"Error occurred while printing output to console, but {transaction_name} was executed successfully."
            )

    def print(self, print_string: str, is_heading: bool = False):
        """
        Add new string to be printed to output queue
        :param print_string: string to be printed
        :param is_heading: boolean flag to convert to upper case letters
        :return: None
        """
        self._output_queue.append(
            print_string if not is_heading else print_string.upper()
        )

    def print_table(
        self, columns: List[TableColumnInput], rows: List[List[str]]
    ):
        """
        Helper function to print data in table format
        :param columns: column inputs
        :param rows: row data
        :return: None
        """
        if len(rows) > 0:
            for row in rows:
                assert len(row) == len(columns)
        table = create_table(columns)
        for row in rows:
            table.add_row(*row)
        self._output_queue.append(table)

    def flush_output(self):
        """
        Helper function to flush output to console
        :return: None
        """
        self._output_queue.insert(0, OUTPUT_DIVIDER)
        self._output_queue.append(OUTPUT_DIVIDER)
        console.print(*self._output_queue, sep="\n")
        self._output_queue.clear()

    def _output_result(self, *args, **kwargs):
        pass

    @abstractmethod
    def _execute(self, *args, **kwargs):
        pass

    @property
    @abstractmethod
    def transaction_name(self):
        pass
