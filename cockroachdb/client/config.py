import os

from common.path import WORKSPACE_PATH

IS_PROD = os.getenv("ENV", "dev") == "prod"
DATA_PATH = WORKSPACE_PATH / "data"
INIT_DATA_PATH = DATA_PATH / "data-files"
TRANSACTION_DATA_PATH = DATA_PATH / (
    "xact-files" if IS_PROD else "test-xact-files"
)
