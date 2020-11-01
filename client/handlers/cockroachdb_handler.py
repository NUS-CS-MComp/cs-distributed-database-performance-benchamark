from decimal import Decimal
from typing import Any

from client.handlers.base import BaseSingleClientHandler


class CockroachDBSingleClientHandler(BaseSingleClientHandler):
    """
    CockroachDB client input handler
    """

    def run_pre_transaction_hook(self):
        """
        Initiate new cockroach database connection
        :return: None
        """
        from cockroachdb.modules.connection import (
            database,
            initialize_cockroach_database,
        )

        database.initialize(
            initialize_cockroach_database(
                server_idx=self.client_number % self.num_servers
            )
        )

    def run_transaction_from_input(self, transaction_type, transaction_inputs):
        """
        Method to run transaction from input
        :param transaction_type: type of transaction represented in string
        :param transaction_inputs: transaction input arguments as tuple
        :return: None
        """
        transaction = CockroachDBSingleClientHandler.init_new_transaction(
            transaction_type, transaction_inputs
        )
        transaction.run()

    @staticmethod
    def init_new_transaction(transaction_type: str, inputs: Any):
        """
        Get transaction instance with transaction type and relevant inputs
        :param transaction_type: transaction type identifier
        :param inputs: inputs as tuple for a transaction
        :return: transaction class object
        """

        from cockroachdb.modules.transactions import (
            NewOrderTransaction,
            PaymentTransaction,
            DeliveryTransaction,
            OrderStatusTransaction,
            StockLevelTransaction,
            PopularItemsTransaction,
            TopBalanceTransaction,
            RelatedCustomerTransaction,
        )

        if transaction_type == "N":
            return NewOrderTransaction(*inputs)
        elif transaction_type == "P":
            return PaymentTransaction(tuple(inputs[:3]), Decimal(inputs[-1]))
        elif transaction_type == "D":
            return DeliveryTransaction(*inputs)
        elif transaction_type == "O":
            return OrderStatusTransaction(tuple(inputs[:3]))
        elif transaction_type == "S":
            return StockLevelTransaction(*inputs)
        elif transaction_type == "I":
            return PopularItemsTransaction(*inputs)
        elif transaction_type == "R":
            return RelatedCustomerTransaction(tuple(inputs[:3]))
        elif transaction_type == "T":
            return TopBalanceTransaction()
        else:
            raise NotImplementedError(
                f"No such transaction: {transaction_type}"
            )
