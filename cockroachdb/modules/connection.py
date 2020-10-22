import os
import pathlib
from random import choice

from playhouse.cockroachdb import PooledCockroachDatabase, DatabaseProxy

# Basic database configuration
IS_PROD = os.getenv("ENV", "dev") == "prod"
DATABASE = os.getenv("DATABASE", "cs5424")
HOST = os.getenv("HOST", "localhost")
USER = os.getenv("USERNAME", "root")
ASSIGNED_PORTS = os.getenv("PORTS", "26257,26258,26259,26260,26261").split(",")
SERVER_START_INDEX = 35

# Connection options
CONNECTION_KWARGS = {"database": DATABASE, "host": HOST, "user": USER}
SCRIPTS_PATH = pathlib.Path(__file__).parent.parent / "scripts"


# Helper functions
def initialize_cockroach_database(
    pooling_size: int = None, stale_timeout: int = 600, timeout: int = 30
):
    """
    Initialize
    :param pooling_size: connection pooling size
    :param stale_timeout: time to keep connection alive
    :param timeout: time to block connection
    :return: Pooled CockroachDB instance
    """
    random_port = choice(ASSIGNED_PORTS)
    if IS_PROD:
        SERVER = SERVER_START_INDEX + int(random_port) - 26257
        CONNECTION_KWARGS.update(
            sslmode="verify-full",
            sslrootcert=SCRIPTS_PATH / "prod/certs/ca.crt",
            sslcert=SCRIPTS_PATH / f"prod/certs_{SERVER}/client.{USER}.crt",
            sslkey=SCRIPTS_PATH / f"prod/certs_{SERVER}/client.{USER}.key",
        )
    else:
        CONNECTION_KWARGS.update(
            sslmode="verify-full",
            sslrootcert=SCRIPTS_PATH / "dev/certs/ca.crt",
            sslcert=SCRIPTS_PATH / "dev/certs/client.root.crt",
            sslkey=SCRIPTS_PATH / "dev/certs/client.root.key",
        )
    return PooledCockroachDatabase(
        port=random_port,
        max_connections=pooling_size,
        timeout=timeout,
        stale_timeout=stale_timeout,
        **CONNECTION_KWARGS,
    )


# Proxy database instance to be initialized later
database = DatabaseProxy()
