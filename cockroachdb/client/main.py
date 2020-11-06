import argparse
import pathlib
from typing import Literal, Optional, List

import cockroachdb.client.config as config


def main():
    """
    Main entry point to the benchmark application
    :return: None
    """
    parser = argparse.ArgumentParser()
    db_group = parser.add_mutually_exclusive_group()

    parser.add_argument(
        "--hosts",
        help="List of hosts to resolve",
        type=str,
        default="xcnc35.comp.nus.edu.sg,xcnc36.comp.nus.edu.sg,xcnc37.comp.nus.edu.sg,xcnc38.comp.nus.edu.sg,"
        "xcnc39.comp.nus.edu.sg",
    )
    parser.add_argument(
        "--port", help="Database port number", type=int, default=26257
    )

    parser.add_argument(
        "-l", "--load", help="Load data into database", action="store_true"
    )
    parser.add_argument(
        "-w",
        "--workers",
        help="Number of processes to load data",
        type=int,
        default=4,
    )
    parser.add_argument(
        "--batch-size",
        help="Batch size of loading data",
        type=int,
        default=999,
    )

    parser.add_argument(
        "-e", "--experiment", help="Run experiment", action="store_true"
    )
    db_group.add_argument(
        "--cockroachdb",
        help="Run experiment in CockroachDB",
        action="store_true",
    )

    parser.add_argument(
        "-en", "--experiment-number", help="Experiment number", type=int
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

    database: Optional[Literal["cockroachdb"]] = None
    if args.cockroachdb:
        database = "cockroachdb"
    if database is None:
        return

    if args.load:
        load_data(
            database,
            args.load_data_path,
            args.workers,
            args.batch_size,
            args.hosts.split(","),
            args.port,
        )
    elif args.experiment:
        run_experiment(
            database,
            args.experiment_number,
            args.transaction_data_path,
            args.hosts.split(","),
            args.port,
        )


def load_data(
    database: Literal["cockroachdb"],
    data_path: pathlib.Path,
    workers: int,
    batch_size: int,
    hosts: List[str],
    port: int,
):
    """
    Load data into database
    :param database: database name
    :param data_path: data path to read
    :param workers: number of workers for loading
    :param batch_size: batch loading size
    :param hosts: list of hosts
    :param port: database port number
    :return: None
    """
    if database == "cockroachdb":
        from cockroachdb.client.config import INIT_DATA_PATH
        from cockroachdb.client.loaders.cockroachdb_loader import (
            CockroachDBCSVLoader,
        )
        from cockroachdb.client.loaders.csv_loader import FILE_NAMES

        loader = CockroachDBCSVLoader(
            data_dir=INIT_DATA_PATH if data_path is None else data_path,
            file_names=FILE_NAMES,
            workers=workers,
            batch_size=batch_size,
            db_hosts=hosts,
            db_port=port,
        )
        loader.run()


def run_experiment(
    database: Literal["cockroachdb"],
    experiment_number: int,
    transaction_data_path: pathlib.Path,
    hosts: List[str],
    port: int,
):
    """
    Run experiment given database and experiment number
    :param database: database name
    :param experiment_number: experiment number
    :param transaction_data_path: transaction data path to read
    :param hosts: list of hosts
    :param port: database port number
    :return: None
    """
    from cockroachdb.client.config import TRANSACTION_DATA_PATH
    from cockroachdb.client.experiments import ExperimentHandlerFactory

    factory = None
    if database == "cockroachdb":
        factory = ExperimentHandlerFactory.COCKROACH_DB
    else:
        raise NotImplementedError(f"No such DB: {database}")

    Experiment = ExperimentHandlerFactory.generate_new_experiment(factory)
    experiment = Experiment(
        data_dir=TRANSACTION_DATA_PATH
        if transaction_data_path is None
        else transaction_data_path,
        experiment_number=experiment_number,
        db_hosts=hosts,
        db_port=port,
    )
    experiment.run()


if __name__ == "__main__":
    main()
