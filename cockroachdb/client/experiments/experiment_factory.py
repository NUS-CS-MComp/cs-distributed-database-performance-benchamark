from typing import Literal


class ExperimentHandlerFactory:
    COCKROACH_DB = "cockroach"

    @staticmethod
    def generate_new_experiment(db_name: Literal["cockroach"]):
        """
        Factory method to return a new handler for experiment
        :param db_name: DB name to generate new handler
        :return: handler class object
        """
        if db_name == ExperimentHandlerFactory.COCKROACH_DB:
            from cockroachdb.client.experiments.cockroachdb_experiment import (
                CockroachDBExperiment,
            )

            return CockroachDBExperiment
        else:
            raise NotImplementedError(f"No such DB: {db_name}")
