import csv
import pathlib
from typing import TextIO, List, Callable

from cockroachdb.modules.models import (
    Warehouse,
    District,
    Customer,
    Order,
    OrderLine,
    Item,
    Stock,
)
from common.logging import logger

# Data file path
DATA_PATH = (
    pathlib.Path(__file__).parent.parent.parent.parent / "data/data-files"
)

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

# File name to model and column name mapping
MODEL_MAPPING = {
    "warehouse": {
        "model": Warehouse,
        "columns": [
            "id",
            "name",
            "street_1",
            "street_2",
            "city",
            "state",
            "zip",
            "tax",
            "ytd",
        ],
    },
    "district": {
        "model": District,
        "columns": [
            "warehouse_id",
            "id",
            "name",
            "street_1",
            "street_2",
            "city",
            "state",
            "zip",
            "tax",
            "ytd",
            "next_order_id",
        ],
    },
    "customer": {
        "model": Customer,
        "columns": [
            "warehouse_id",
            "district_id",
            "id",
            "first_name",
            "middle_name",
            "last_name",
            "street_1",
            "street_2",
            "city",
            "state",
            "zip",
            "phone_number",
            "since",
            "credit",
            "credit_limit",
            "discount",
            "balance",
            "ytd_payment",
            "payment_count",
            "delivery_count",
            "data",
        ],
    },
    "order": {
        "model": Order,
        "columns": [
            "warehouse_id",
            "district_id",
            "id",
            "customer_id",
            "carrier_id",
            "order_line_count",
            "all_local",
            "entry_date",
        ],
    },
    "item": {
        "model": Item,
        "columns": ["id", "name", "price", "image_id", "data"],
    },
    "order-line": {
        "model": OrderLine,
        "columns": [
            "warehouse_id",
            "district_id",
            "order_id",
            "number",
            "item_id",
            "delivery_date",
            "amount",
            "supplying_warehouse_id",
            "quantity",
            "dist_info",
        ],
    },
    "stock": {
        "model": Stock,
        "columns": [
            "warehouse_id",
            "item_id",
            "quantity",
            "ytd",
            "order_count",
            "remote_count",
            "dist_info_01",
            "dist_info_02",
            "dist_info_03",
            "dist_info_04",
            "dist_info_05",
            "dist_info_06",
            "dist_info_07",
            "dist_info_08",
            "dist_info_09",
            "dist_info_10",
            "data",
        ],
    },
}


def csv_data_generator(
    csv_file: TextIO,
    delimiter: str,
    model_constructor: Callable,
    column_names: List[str],
    batch_size: int = 100,
):
    """
    Generate csv data generator
    :param csv_file: csv file object
    :param delimiter: delimiter for csv data
    :param model_constructor: model object constructor
    :param column_names: column name mapping
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

    csv_reader = csv.reader(csv_file, delimiter=delimiter)
    csv_rows = []
    total_size = 0
    for csv_row in csv_reader:
        csv_rows.append(
            model_constructor(
                **dict(zip(column_names, normalize_row(csv_row)))
            )
        )
        total_size += 1
        if len(csv_rows) == batch_size:
            batch = total_size // batch_size
            if total_size % batch_size == 0:
                logger.info(
                    f"Loading batch {batch} of {model_constructor.__name__} data (size: {total_size})"
                )
            yield csv_rows
            csv_rows = []
    logger.info(
        f"Loading final batch of {model_constructor.__name__} data (size: {total_size})"
    )
    yield csv_rows


def process_input_data(queue):
    """
    Multiprocess thunk
    :param queue: multiprocess queue
    :return: None
    """
    from cockroachdb.modules.connection import (
        database,
        initialize_cockroach_database,
    )

    database.initialize(initialize_cockroach_database())

    while True:
        raw_data = queue.get()
        if raw_data is None:
            break
        model_object, batch_data = raw_data

        def bulk_create(_db):
            """
            Bulk data creation thunk
            :param _db: database reference
            :return: None
            """
            return model_object.bulk_create(batch_data)

        database.run_transaction(bulk_create, max_attempts=50)


if __name__ == "__main__":
    import multiprocessing

    WORKER = 4
    BATCH_SIZE = 999
    PRINT_INTERVAL = 10000

    for file_name in FILE_NAMES:
        file = DATA_PATH / file_name
        name = file.stem

        process_queue = multiprocessing.Queue(maxsize=WORKER)
        process_pool = multiprocessing.Pool(
            WORKER, initializer=process_input_data, initargs=(process_queue,)
        )

        with open(file, "r") as f:
            Model, columns = MODEL_MAPPING.get(name).values()
            generator = csv_data_generator(
                csv_file=f,
                delimiter=",",
                model_constructor=Model,
                column_names=columns,
                batch_size=BATCH_SIZE,
            )
            for data in generator:
                process_queue.put((Model, data))
            for _ in range(WORKER):
                process_queue.put(None)
            process_pool.close()
            process_pool.join()
