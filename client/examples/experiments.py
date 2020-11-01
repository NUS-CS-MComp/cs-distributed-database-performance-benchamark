from client.config import TRANSACTION_DATA_PATH
from client.experiments import ExperimentHandlerFactory

if __name__ == "__main__":
    Experiment = ExperimentHandlerFactory.generate_new_experiment(
        ExperimentHandlerFactory.COCKROACH_DB
    )
    experiment = Experiment(
        data_dir=TRANSACTION_DATA_PATH, experiment_number=5
    )
    experiment.run()
