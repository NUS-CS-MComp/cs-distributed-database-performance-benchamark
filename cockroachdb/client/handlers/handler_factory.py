from typing import Literal


class SingleClientHandlerFactory:
    COCKROACH_DB = "cockroach"

    @staticmethod
    def generate_new_client(db_name: Literal["cockroach"]):
        """
        Factory method to return a new client for
        :param db_name: DB name to generate new client
        :return: handler class object
        """
        if db_name == SingleClientHandlerFactory.COCKROACH_DB:
            from cockroachdb.client.handlers.cockroachdb_handler import (
                CockroachDBSingleClientHandler,
            )

            return CockroachDBSingleClientHandler
        else:
            raise NotImplementedError(f"No such DB: {db_name}")
