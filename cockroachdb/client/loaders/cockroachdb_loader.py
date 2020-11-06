import pathlib
from typing import TypedDict, List, Dict

from peewee import Model

from cockroachdb.client.loaders.csv_loader import CSVLoader
from cockroachdb.modules.models import (
    Warehouse,
    District,
    Customer,
    Order,
    OrderLine,
    Item,
    Stock,
)


class ModelMapping(TypedDict):
    """
    Model mapping dict type
    """

    model: Model
    columns: List[str]


class CockroachDBCSVLoader(CSVLoader):
    """
    Data loader for CockroachDB
    """

    def __init__(
        self,
        data_dir: pathlib.Path,
        file_names: List[str],
        file_name_model_mapping: Dict[str, ModelMapping] = None,
        **kwargs,
    ):
        """
        Initiate a new csv loader class for Cockroach DB
        :param data_dir: data directory
        :param file_names: file names to parse as csv object
        :param file_name_model_mapping: file name to model mapping
        """
        super().__init__(data_dir=data_dir, file_names=file_names, **kwargs)
        if file_name_model_mapping is None:
            file_name_model_mapping = CockroachDBCSVLoader.MODEL_MAPPING
        self.file_name_model_mapping = file_name_model_mapping

    def run_init_hook(self):
        """
        Run initialization hook before processing row data
        :return: database reference
        """
        from cockroachdb.modules.connection import (
            database,
            initialize_cockroach_database,
        )

        database.initialize(
            initialize_cockroach_database(
                hosts=self.db_hosts, port=self.db_port
            )
        )
        return dict(database=database)

    def transform_row_data(self, row, **kwargs):
        """
        Transform row data to be enqueued in processes
        :param row: row data
        :return: model constructor with row data
        """
        ModelConstructor = kwargs.get("model")
        return ModelConstructor, row

    def process_batch(self, batch, *args, **kwargs):
        """
        Batch processing of processed row data
        :param batch: batch data as specified during transformation
        :return: None
        """
        model_object, batch_data = batch
        database = kwargs.get("database")

        def bulk_create(_db):
            """
            Bulk data creation thunk
            :param _db: database reference
            :return: None
            """
            return model_object.bulk_create(batch_data)

        database.run_transaction(bulk_create, max_attempts=50)

    def get_model_constructor(self, file_name):
        """
        Get model constructor from file name using model mapping
        :param file_name: file name
        :return: model constructor
        """
        model_mapping = self.file_name_model_mapping.get(file_name).values()
        CustomModel, columns = model_mapping
        return CustomModel

    def get_column_names(self, file_name):
        """
        Get model constructor from file name using model mapping
        :param file_name: file name
        :return: list of column names
        """
        model_mapping = self.file_name_model_mapping.get(file_name).values()
        CustomModel, columns = model_mapping
        return columns

    # File name to model and column name mapping
    MODEL_MAPPING: Dict[str, ModelMapping] = {
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
