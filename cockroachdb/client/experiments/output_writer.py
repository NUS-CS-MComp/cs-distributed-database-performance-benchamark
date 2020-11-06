import csv
import pathlib
from typing import Literal, Tuple, Any, List


class ExperimentOutputWriter:
    CLIENT_PERFORMANCE = "clients.csv"
    THROUGHPUT = "throughput.csv"
    DATABASE_STATE = "db-state.csv"
    LIST_FILES = [CLIENT_PERFORMANCE, THROUGHPUT, DATABASE_STATE]
    FILE_HEADER_MAPPING = {
        # 'Experiment Number', 'Client Number',
        # 'Transactions', 'Total Execution Time', 'Throughput',
        # 'Latency (Average)', 'Latency (Median)', 'Latency (95th Percentile)', 'Latency (99th Percentile)'
        CLIENT_PERFORMANCE: (
            "experiment_number",
            "client_number",
            "measurement_a",
            "measurement_b",
            "measurement_c",
            "measurement_d",
            "measurement_e",
            "measurement_f",
            "measurement_g",
        ),
        # 'Experiment Number', 'Throughput (Min)', 'Throughput (Average)', 'Throughput (Max)'
        THROUGHPUT: (
            "experiment_number",
            "min_throughput",
            "avg_throughput",
            "max_throughput",
        ),
        # Database aggregation results
        DATABASE_STATE: (
            "experiment_number",
            "statistics_1",
            "statistics_2",
            "statistics_3",
            "statistics_4",
            "statistics_5",
            "statistics_6",
            "statistics_7",
            "statistics_8",
            "statistics_9",
            "statistics_10",
            "statistics_11",
            "statistics_12",
            "statistics_13",
            "statistics_14",
            "statistics_15",
        ),
    }

    def __init__(
        self,
        output_path: pathlib.Path = pathlib.Path(__file__).parent / "outputs",
    ):
        """
        Initiate a CSV writer class for experiment results
        :param output_path: output path
        """
        self.output_path = output_path
        ExperimentOutputWriter.init_files(output_path)

    def append_rows(
        self,
        rows: List[Tuple[Any, ...]],
        output_type: Literal[
            "client_performance", "throughput", "database_state"
        ],
    ):
        """
        Append rows to output files given output type
        :param rows: row data to append
        :param output_type: one of the expected output file type
        """
        file = None
        if output_type == "client_performance":
            file = ExperimentOutputWriter.CLIENT_PERFORMANCE
        elif output_type == "throughput":
            file = ExperimentOutputWriter.THROUGHPUT
        elif output_type == "database_state":
            file = ExperimentOutputWriter.DATABASE_STATE
        else:
            raise NotImplementedError(f"No such output type: {output_type}")
        file_path = self.output_path / file
        with open(file_path, "a") as output_file:
            writer = csv.writer(output_file)
            for row in rows:
                writer.writerow(row)

    @staticmethod
    def init_files(output_path: pathlib.Path):
        """
        Initiate files if they do not exist
        :param output_path: output path
        :return: None
        """
        if not output_path.exists():
            output_path.mkdir(parents=True)
        for file in ExperimentOutputWriter.LIST_FILES:
            file_path = output_path / file
            if not file_path.exists():
                with open(file_path, "w") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        ExperimentOutputWriter.FILE_HEADER_MAPPING[file]
                    )
