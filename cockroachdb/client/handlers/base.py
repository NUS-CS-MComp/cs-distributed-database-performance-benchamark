import pathlib
from abc import ABC, abstractmethod
from functools import wraps
from statistics import mean
from typing import Any, TextIO, List

from common.logging_tool import error_console, logger
from common.stats import time_execution, median, percentile


class BaseSingleClientHandler(ABC):
    """
    Single client transactions handler that reads transactions for a client from input file,
    process transactions and output database and transaction measurements
    """

    def __init__(
        self,
        client_number: int,
        data_dir: pathlib.Path,
        db_hosts: List[str],
        db_port: int,
    ):
        """
        Initiate a new client handler
        :param client_number: number of clients for running transactions
        :param data_dir: input data directory
        :param db_hosts: list of hosts
        :param db_port: database port number
        """
        self.client_number = client_number
        self.client_input_file = data_dir / f"{self.client_number}.txt"
        self.db_hosts = db_hosts
        self.db_port = db_port
        self.num_of_transactions = 0
        self.elapsed_time = 0
        self.individual_execution_time = []
        self.throughput = float("inf")
        self.avg_latency = float("inf")
        self.median_latency = float("inf")
        self.latency_95_pct = float("inf")
        self.latency_99_pct = float("inf")

    @abstractmethod
    def run_transaction_from_input(
        self, transaction_type: str, transaction_inputs: Any
    ):
        """
        Abstract method to run transaction from input
        :param transaction_type: type of transaction represented in string
        :param transaction_inputs: transaction input arguments as tuple
        :return: NotImplemented object
        """
        return NotImplemented

    @abstractmethod
    def run_pre_transaction_hook(self):
        """
        Abstract method to run preparation work before running transactions
        :return: NotImplemented object
        """
        return NotImplemented

    def process_client_transactions(self):
        """
        Process client transactions
        """
        self.run_pre_transaction_hook()
        _output, self.elapsed_time = time_execution(
            self._read_and_execute_transactions
        )()
        self.throughput = self.num_of_transactions / self.elapsed_time
        self.avg_latency = mean(self.individual_execution_time) * 1000
        self.median_latency = median(self.individual_execution_time) * 1000
        self.latency_95_pct = (
            percentile(self.individual_execution_time, percent=0.95) * 1000
        )
        self.latency_99_pct = (
            percentile(self.individual_execution_time, percent=0.98) * 1000
        )
        self.print_measurements()

    def print_measurements(self):
        """
        Output performance measurements for transactions
        :return: None
        """

        def format_float(value: float):
            """
            Helper function to format float value
            :param value: float value to format
            :return: formatted string representation
            """
            return "{:.2f}".format(value)

        print_lines: List[str] = [
            f"Total number of transactions processed: {self.num_of_transactions}",
            f"Total elapsed time: {format_float(self.elapsed_time)}s",
            f"Transaction throughput: {format_float(self.throughput)}",
            f"Average transaction latency: {format_float(self.avg_latency)}ms",
            f"Median transaction latency: {format_float(self.median_latency)}ms",
            f"95th percentile transaction latency: {format_float(self.latency_95_pct)}ms",
            f"99th percentile transaction latency: {format_float(self.latency_99_pct)}ms",
        ]
        error_console.print("\n".join(print_lines))

    def _read_and_execute_transactions(self):
        """
        Read file input and execute transactions
        :return: None
        """
        with open(self.client_input_file, "r") as input_file_ref:
            while True:
                try:
                    line = input_file_ref.readline()
                    if not line:
                        break
                    line = line.strip()
                    transaction_type = line[0]
                    if transaction_type not in ["N"]:
                        transaction_inputs = line.split(",")[1:]
                        parsed_inputs = []
                        for transaction_input in transaction_inputs:
                            try:
                                parsed_integer = int(transaction_input)
                                parsed_inputs.append(parsed_integer)
                            except ValueError:
                                parsed_inputs.append(transaction_input)
                    else:
                        transaction_inputs = (
                            BaseSingleClientHandler.parse_new_order_input(
                                line, input_file_ref
                            )
                        )
                    execute_transaction = self._time_and_aggregate_transaction(
                        self.run_transaction_from_input
                    )
                    execute_transaction(
                        transaction_type=transaction_type,
                        transaction_inputs=transaction_inputs,
                    )
                except Exception as e:
                    logger.exception(e)
                    logger.error(e)

    def _time_and_aggregate_transaction(self, transaction_func):
        """
        Helper function to time a function
        :param transaction_func: transaction execution function to wrap
        :return: wrapped function layer
        """

        @wraps(transaction_func)
        def time_and_execute(*args, **kwargs):
            """
            Time and execute a function
            :return: output and execution time
            """
            _output, execution_time = time_execution(transaction_func)(
                *args, **kwargs
            )
            self.num_of_transactions += 1
            self.individual_execution_time.append(execution_time)

        return time_and_execute

    @property
    def client_transaction_summary(self):
        """
        Get summary for transactions for a client
        To be used together with experiment information and stored in clients.csv
        :return: transaction performance metrics
        """
        return (
            self.client_number,
            self.num_of_transactions,
            self.elapsed_time,
            self.throughput,
            self.avg_latency,
            self.median_latency,
            self.latency_95_pct,
            self.latency_99_pct,
        )

    @staticmethod
    def parse_new_order_input(current_line: str, file_ref: TextIO):
        """
        Helper function to parse new order item details in input file lines
        :param current_line: current line string
        :param file_ref: file object reference
        :return: order input ready to be consumed by transaction
        """
        split_line = current_line.split(",")
        num_of_items = int(split_line[-1])
        item_number_list = []
        supplier_warehouse_list = []
        quantity_list = []
        for item in range(num_of_items):
            detail = file_ref.readline().split(",")
            item_number_list.append(int(detail[0]))
            supplier_warehouse_list.append(int(detail[1]))
            quantity_list.append(int(detail[2]))
        customer_identifier = (
            int(split_line[2]),
            int(split_line[3]),
            int(split_line[1]),
        )
        transaction_inputs = [
            customer_identifier,
            num_of_items,
            item_number_list,
            supplier_warehouse_list,
            quantity_list,
        ]
        return transaction_inputs
