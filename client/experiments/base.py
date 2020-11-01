import pathlib
from abc import ABC, abstractmethod
from statistics import mean
from typing import List, Optional, Any, Tuple

from client.experiments.output_writer import ExperimentOutputWriter
from client.handlers.base import BaseSingleClientHandler


class BaseExperiment(ABC):
    """
    Client transaction experiment runner class
    """

    def __init__(
        self,
        experiment_number: int,
        data_dir: pathlib.Path,
        writer: Optional[ExperimentOutputWriter] = ExperimentOutputWriter(),
    ):
        """
        Initiate a new experiment handler
        :param experiment_number: experiment number for retrieving experiment configurations
        :param data_dir: input data directory
        """
        self.experiment_number = experiment_number
        self.clients: List[BaseSingleClientHandler] = []
        self.result = []
        self.data_dir = data_dir
        self.writer = writer

    def run(self):
        """
        Trigger experiment runner from initialization, processing to final output
        :return: None
        """
        self.run_pre_experiment_hook()
        self.run_experiment()
        client_results = self.consolidate_results()
        throughput_summary = self.consolidate_throughput()
        database_state = self.get_database_state()
        if self.writer is not None:
            self.writer.append_rows(client_results, "client_performance")
            self.writer.append_rows(throughput_summary, "throughput")
            self.writer.append_rows(database_state, "database_state")

    def process_multiple_clients(self, workers: int):
        """
        Trigger multiprocessing for parallel transactions
        :param workers: number of workers
        :return: None
        """
        import multiprocessing
        from client.experiments.client_handler_consumer import (
            ClientHandlerConsumer,
        )

        handler_queue: multiprocessing.JoinableQueue[
            Optional[BaseSingleClientHandler]
        ] = multiprocessing.JoinableQueue()
        result_queue: multiprocessing.Queue[
            Optional[BaseSingleClientHandler]
        ] = multiprocessing.Queue()

        consumers = [
            ClientHandlerConsumer(handler_queue, result_queue)
            for _ in range(workers)
        ]
        for consumer in consumers:
            consumer.start()

        for client in self.clients:
            handler_queue.put(client)

        for _ in range(workers):
            handler_queue.put(None)

        handler_queue.join()

        processed_clients: List[BaseSingleClientHandler] = []
        for _ in range(workers):
            processed_handler = result_queue.get()
            processed_clients.append(processed_handler)

        self.clients = processed_clients

    def consolidate_results(self) -> List[Tuple[Any, ...]]:
        """
        Get transaction details for all clients in the experiment to be stored in clients.csv
        :return: concatenated transaction results
        """
        for client in self.clients:
            self.result.append(
                (self.experiment_number,) + client.client_transaction_summary
            )
        return self.result

    def consolidate_throughput(self) -> List[Tuple[Any, ...]]:
        """
        Get minimum, average and maximum transaction throughput among all clients in the experiment
        to be stored in throughput.csv
        :return: consolidated throughput statistics
        """
        throughput = [client.throughput for client in self.clients]
        return [
            (
                self.experiment_number,
                min(throughput),
                mean(throughput),
                max(throughput),
            ),
        ]

    @property
    @abstractmethod
    def experiment_configurations(self):
        """
        Abstract experiment configuration property
        """
        pass

    @abstractmethod
    def run_pre_experiment_hook(self):
        """
        Abstract method to run preparation work before running experiments
        :return: NotImplemented object
        """
        return NotImplemented

    @abstractmethod
    def run_experiment(self):
        """
        Perform experiment using specifications
        :return: NotImplemented object
        """
        return NotImplemented

    @abstractmethod
    def get_database_state(self) -> List[Tuple[Any, ...]]:
        """
        Abstract method to get consequent database state
        """
        pass
