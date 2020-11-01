from client.experiments.base import BaseExperiment


class CassandraExperiment(BaseExperiment):
    """
    Cassandra transaction experiment runner class
    """

    def run_pre_experiment_hook(self):
        pass

    def run_experiment(self):
        pass

    def get_database_state(self):
        pass

    @property
    def experiment_configurations(self):
        return None
