from client.experiments.base import BaseExperiment

if __name__ == "__main__":
    experiment = BaseExperiment(5)
    experiment.perform_experiment()
    clients = experiment.consolidate_results()
    db_state = experiment.get_database_state()
