from typing import Literal


class ExperimentHandlerFactory:
    COCKROACH_DB = "cockroach"
    CASSANDRA = "cassandra"

    @staticmethod
    def generate_new_experiment(db_name: Literal["cockroach", "cassandra"]):
        """
        Factory method to return a new handler for experiment
        :param db_name: DB name to generate new handler
        :return: handler class object
        """
        if db_name == ExperimentHandlerFactory.COCKROACH_DB:
            from client.experiments.cockroachdb_experiment import (
                CockroachDBExperiment,
            )

            return CockroachDBExperiment
        elif db_name == ExperimentHandlerFactory.CASSANDRA:
            from client.experiments.cassandra_experiment import (
                CassandraExperiment,
            )

            return CassandraExperiment
        else:
            raise NotImplementedError(f"No such DB: {db_name}")
