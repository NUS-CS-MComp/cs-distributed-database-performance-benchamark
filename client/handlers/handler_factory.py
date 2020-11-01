from typing import Literal


class SingleClientHandlerFactory:
    COCKROACH_DB = "cockroach"
    CASSANDRA = "cassandra"

    @staticmethod
    def generate_new_client(db_name: Literal["cockroach", "cassandra"]):
        """
        Factory method to return a new client for
        :param db_name: DB name to generate new client
        :return: handler class object
        """
        if db_name == SingleClientHandlerFactory.COCKROACH_DB:
            from client.handlers.cockroachdb_handler import (
                CockroachDBSingleClientHandler,
            )

            return CockroachDBSingleClientHandler
        elif db_name == SingleClientHandlerFactory.CASSANDRA:
            from client.handlers.cassandra_handler import (
                CassandraDBSingleClientHandler,
            )

            return CassandraDBSingleClientHandler
        else:
            raise NotImplementedError(f"No such DB: {db_name}")
