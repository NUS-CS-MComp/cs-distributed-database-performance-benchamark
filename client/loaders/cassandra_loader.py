from typing import Any, List

from client.loaders.csv_loader import CSVLoader


class CassandraCSVLoader(CSVLoader):
    """
    Data loader for Cassandra
    """

    def run_init_hook(self):
        pass

    def transform_row_data(self, row: List, *args, **kwargs):
        pass

    def process_batch(self, batch: Any, **kwargs):
        pass

    def get_model_constructor(self, file_name: str):
        return None

    def get_column_names(self, file_name: str):
        return None
