import csv
import pathlib
from abc import ABC, abstractmethod
from typing import TextIO, List, Callable, Any

from common.logging import logger

# File names
FILE_NAMES = [
    "warehouse.csv",
    "district.csv",
    "customer.csv",
    "order.csv",
    "item.csv",
    "order-line.csv",
    "stock.csv",
]  # Order is important


def csv_data_generator(
    csv_file: TextIO,
    delimiter: str,
    model_constructor: Callable = None,
    column_names: List[str] = None,
    batch_size: int = 100,
):
    """
    Generate csv data generator
    :param csv_file: csv file object
    :param delimiter: delimiter for csv data
    :param model_constructor: model object constructor, default as None
    :param column_names: column name mapping to be used together with model constructor
    :param batch_size: batch size
    :return: data generator
    """

    def normalize_row(row_data: List[str]):
        """
        Helper function to normalize read row data
        :param row_data: row data parsed from csv
        :return: normalized row data
        """
        return map(lambda value: None if value == "null" else value, row_data)

    if model_constructor is not None:
        assert column_names is not None

    data_name = (
        csv_file.name
        if model_constructor is None
        else model_constructor.__name__
    )

    csv_reader = csv.reader(csv_file, delimiter=delimiter)
    csv_rows = []
    total_size = 0
    for csv_row in csv_reader:
        csv_rows.append(
            normalize_row(csv_row)
            if model_constructor is None
            else model_constructor(
                **dict(zip(column_names, normalize_row(csv_row)))
            )
        )
        total_size += 1
        if len(csv_rows) == batch_size:
            batch = total_size // batch_size
            if total_size % batch_size == 0:
                logger.info(
                    f"Loading batch {batch} of {data_name} data (size: {total_size})"
                )
            yield csv_rows
            csv_rows = []
    logger.info(
        f"Loading final batch of {data_name} data (size: {total_size})"
    )
    yield csv_rows


class CSVLoader(ABC):
    """
    Loader for converting raw csv to database object
    """

    def __init__(
        self,
        data_dir: pathlib.Path,
        file_names: List[str],
        workers=4,
        batch_size=999,
        print_interval=10000,
    ):
        """
        Initiate a new csv loader class with multiprocessing specifications
        :param data_dir: data directory
        :param file_names: file names to parse as csv object
        :param workers: number of CPU workers
        :param batch_size: batch size
        :param print_interval: logging interval
        """
        self.files = [data_dir / file_name for file_name in file_names]
        self.workers = workers
        self.batch_size = batch_size
        self.print_interval = print_interval

    def run(self):
        """
        Run multiprocessing on data loading
        :return: None
        """
        import multiprocessing

        for file in self.files:
            process_queue = multiprocessing.Queue(maxsize=self.workers)
            process_pool = multiprocessing.Pool(
                self.workers,
                initializer=self.process_input_data,
                initargs=(process_queue,),
            )
            with open(file, "r") as f:
                model = self.get_model_constructor(file.stem)
                columns = self.get_column_names(file.stem)
                generator = csv_data_generator(
                    csv_file=f,
                    delimiter=",",
                    model_constructor=model,
                    column_names=columns,
                    batch_size=self.batch_size,
                )
                for data in generator:
                    process_queue.put(
                        self.transform_row_data(
                            data, model=model, columns=columns
                        )
                    )
                for _ in range(self.workers):
                    process_queue.put(None)
                process_pool.close()
                process_pool.join()

    def process_input_data(self, queue):
        """
        Multiprocess thunk
        :param queue: multiprocess queue
        :return: None
        """
        hook_output = self.run_init_hook()
        while True:
            row_data = queue.get()
            if row_data is None:
                break
            if type(hook_output) == dict:
                self.process_batch(row_data, **hook_output)
            else:
                self.process_batch(row_data)

    @abstractmethod
    def run_init_hook(self):
        """
        Abstract method to run initialization hook before processing row data
        :return: Empty argument map
        """
        return dict()

    @abstractmethod
    def transform_row_data(self, row: List, *args, **kwargs):
        """
        Abstract method to process row data as pickles for multiprocess
        :param row: row data in tuple form
        :return: NotImplemented object
        """
        return NotImplemented

    @abstractmethod
    def process_batch(self, batch: Any, **kwargs):
        """
        Abstract method to process batch data loaded from process queue
        :param batch: batch data as returned from processed row data
        :return: NotImplemented object
        """
        return NotImplemented

    @abstractmethod
    def get_model_constructor(self, file_name: str):
        """
        Abstract method to infer model constructor from current file name
        :param file_name: file name
        :return: NotImplemented object
        """
        return NotImplemented

    @abstractmethod
    def get_column_names(self, file_name: str):
        """
        Abstract method to infer column names from current file name
        :param file_name: file name
        :return: NotImplemented object
        """
        return NotImplemented
