from abc import ABC, abstractmethod
from statistics import mean
from typing import List

from client.handlers.base import BaseSingleClientHandler


class BaseExperiment(ABC):
    """
    Client transaction experiment runner class
    """

    def __init__(
        self,
        experiment_number: int,
    ):
        self.experiment_number = experiment_number
        self.clients: List[BaseSingleClientHandler] = []
        self.result = []

    def consolidate_results(self):
        """
        Get transaction details for all clients in the experiment to be stored in clients.csv
        :return: concatenated transaction results
        """
        for client in self.clients:
            self.result.append(
                (self.experiment_number,) + client.client_transaction_summary
            )
        return self.result

    def consolidate_throughput(self):
        """
        Get minimum, average and maximum transaction throughput among all clients in the experiment
        to be stored in throughput.csv
        :return: consolidated throughput statistics
        """
        throughput = [client.throughput for client in self.clients]
        return (
            self.experiment_number,
            min(throughput),
            mean(throughput),
            max(throughput),
        )

    @abstractmethod
    @property
    def experiment_configurations(self):
        """
        Abstract experiment configuration property
        """
        pass

    @abstractmethod
    def perform_experiment(self):
        """
        Abstract method to perform experiment
        """
        pass

    @abstractmethod
    def get_database_state(self):
        """
        Abstract method to get consequent database state
        """
        pass
