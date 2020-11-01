from typing import Any

from client.handlers.base import BaseSingleClientHandler


class CassandraDBSingleClientHandler(BaseSingleClientHandler):
    """
    Cassandra client input handler
    """

    def run_pre_transaction_hook(self):
        pass

    def run_transaction_from_input(
        self, transaction_type: str, transaction_inputs: Any
    ):
        pass
