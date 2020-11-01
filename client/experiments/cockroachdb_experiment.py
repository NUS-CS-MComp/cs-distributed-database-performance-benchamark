from typing import Tuple

from peewee import fn

from client.experiments.base import BaseExperiment
from client.handlers import SingleClientHandlerFactory
from cockroachdb.modules.models import (
    Order,
    OrderLine,
    Customer,
    District,
    Warehouse,
    Stock,
)


class CockroachDBExperiment(BaseExperiment):
    """
    CockroachDB transaction experiment runner class
    """

    def run_pre_experiment_hook(self):
        """
        Run pre-experiment hook by initiating a database connection for state retrieval
        :return: None
        """
        from cockroachdb.modules.connection import (
            database,
            initialize_cockroach_database,
        )

        database.initialize(initialize_cockroach_database())

    @property
    def experiment_configurations(self):
        """
        CockroachDB experiment related configurations
        :return: selected configuration given experiment number
        """
        from client.config import IS_PROD

        configurations = (
            {5: (20, 4), 6: (20, 5), 7: (40, 4), 8: (40, 5)}
            if IS_PROD
            else {5: (5, 5)}
        )
        return configurations.get(self.experiment_number, (5, 5))

    def run_experiment(self):
        """
        Run multiple processes handling client transactions using client handlers
        :return: None
        """

        configurations = self.experiment_configurations
        num_of_clients, num_of_servers = configurations

        Client = SingleClientHandlerFactory.generate_new_client(
            SingleClientHandlerFactory.COCKROACH_DB
        )
        self.clients = [
            Client(
                client_number=index + 1,
                num_servers=num_of_servers,
                data_dir=self.data_dir,
            )
            for index in range(num_of_clients)
        ]

        self.process_multiple_clients(workers=num_of_clients)

    def get_database_state(self):
        """
        Get database state to be queried after an experiment finishes to get database status and store in db-state.csv
        :return: database state summary
        """
        sum_warehouse = Warehouse.select(fn.SUM(Warehouse.ytd)).scalar(
            as_tuple=True
        )

        sum_district = District.select(
            fn.SUM(District.ytd), fn.SUM(District.next_order_id)
        ).scalar(as_tuple=True)

        sum_customer = Customer.select(
            fn.SUM(Customer.balance),
            fn.SUM(Customer.ytd_payment),
            fn.SUM(Customer.payment_count),
            fn.SUM(Customer.delivery_count),
        ).scalar(as_tuple=True)

        sum_order = Order.select(
            fn.MAX(Order.id), fn.SUM(Order.order_line_count)
        ).scalar(as_tuple=True)

        sum_order_line: Tuple[..., ...] = OrderLine.select(
            fn.SUM(OrderLine.amount), fn.SUM(OrderLine.quantity)
        ).scalar(as_tuple=True)

        sum_stock = Stock.select(
            fn.SUM(Stock.quantity),
            fn.SUM(Stock.ytd),
            fn.SUM(Stock.order_count),
            fn.SUM(Stock.remote_count),
        ).scalar(as_tuple=True)

        return [
            (
                (self.experiment_number,)
                + sum_warehouse
                + sum_district
                + sum_customer
                + sum_order
                + sum_order_line
                + sum_stock
            ),
        ]
