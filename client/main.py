import argparse
import pathlib
from typing import Literal, Optional

import client.config as config


def main():
    """
    Main entry point to the benchmark application
    :return: None
    """
    parser = argparse.ArgumentParser()
    db_group = parser.add_mutually_exclusive_group()

    parser.add_argument(
        "-l", "--load", help="Load data into database", action="store_true"
    )

    parser.add_argument(
        "-e", "--experiment", help="Run experiment", action="store_true"
    )
    db_group.add_argument(
        "--cockroachdb",
        help="Run experiment in CockroachDB",
        action="store_true",
    )
    db_group.add_argument(
        "--cassandra", help="Run experiment in Cassandra", action="store_true"
    )

    parser.add_argument(
        "-n", "--experiment-number", help="Experiment number", type=int
    )
    parser.add_argument(
        "-dl",
        "--load-data-path",
        help="Path to read initial data",
        type=str,
        default=config.INIT_DATA_PATH,
    )
    parser.add_argument(
        "-dt",
        "--transaction-data-path",
        help="Path to read transaction data",
        type=str,
        default=config.TRANSACTION_DATA_PATH,
    )

    args = parser.parse_args()

    database: Optional[Literal["cassandra", "cockroachdb"]] = None
    if args.cassandra:
        database = "cassandra"
    elif args.cockroachdb:
        database = "cockroachdb"
    if database is None:
        return

    if args.load:
        load_data(database, args.load_data_path)
    elif args.experiment:
        run_experiment(
            database, args.experiment_number, args.transaction_data_path
        )


def load_data(
    database: Literal["cassandra", "cockroachdb"], data_path: pathlib.Path
):
    """
    Load data into database
    :param database: database name
    :param data_path: data path to read
    :return: None
    """
    if database == "cockroachdb":
        from client.config import INIT_DATA_PATH
        from client.loaders.cockroachdb_loader import CockroachDBCSVLoader
        from client.loaders.csv_loader import FILE_NAMES

        loader = CockroachDBCSVLoader(
            data_dir=INIT_DATA_PATH if data_path is None else data_path,
            file_names=FILE_NAMES,
        )
        loader.run()


def run_experiment(
    database: Literal["cassandra", "cockroachdb"],
    experiment_number: int,
    transaction_data_path: pathlib.Path,
):
    """
    Run experiment given database and experiment number
    :param database: database name
    :param experiment_number: experiment number
    :param transaction_data_path: transaction data path to read
    :return: None
    """
    from client.config import TRANSACTION_DATA_PATH
    from client.experiments import ExperimentHandlerFactory

    factory = None
    if database == "cassandra":
        factory = ExperimentHandlerFactory.CASSANDRA
    elif database == "cockroachdb":
        factory = ExperimentHandlerFactory.COCKROACH_DB

    Experiment = ExperimentHandlerFactory.generate_new_experiment(factory)
    experiment = Experiment(
        data_dir=TRANSACTION_DATA_PATH
        if transaction_data_path is None
        else transaction_data_path,
        experiment_number=experiment_number,
    )
    experiment.run()


if __name__ == "__main__":
    main()
