from client.config import INIT_DATA_PATH
from client.loaders.cockroachdb_loader import CockroachDBCSVLoader
from client.loaders.csv_loader import FILE_NAMES

if __name__ == "__main__":
    loader = CockroachDBCSVLoader(
        data_dir=INIT_DATA_PATH, file_names=FILE_NAMES
    )
    loader.run()
