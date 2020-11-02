import os
import pathlib
from random import choice, randint

from playhouse.cockroachdb import CockroachDatabase, DatabaseProxy

# Basic database configuration
IS_PROD = os.getenv("ENV", "dev") == "prod"
DATABASE = os.getenv("DATABASE", "cs5424")
HOST = os.getenv("HOST", "localhost")
USER = os.getenv("USERNAME", "root")
ASSIGNED_PORTS = os.getenv("PORTS", "26257,26258,26259,26260,26261").split(",")
SERVER_START_INDEX = 35
NUM_SERVERS = int(os.getenv("NUM_SERVERS", 5))

# Connection options
CONNECTION_KWARGS = {"database": DATABASE, "host": HOST, "user": USER}
SCRIPTS_PATH = pathlib.Path(__file__).parent.parent / "scripts"


# Helper functions
def initialize_cockroach_database(server_idx: int = None):
    """
    Initialize
    :param server_idx: server index to connect, only for production
    :return: Pooled CockroachDB instance
    """
    if IS_PROD:
        if server_idx is None:
            SERVER = SERVER_START_INDEX + randint(0, NUM_SERVERS - 1)
        else:
            SERVER = SERVER_START_INDEX + server_idx
        CONNECTION_KWARGS.update(
            host=f"xcnc{SERVER}.comp.nus.edu.sg",
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
    return CockroachDatabase(
        port=choice(ASSIGNED_PORTS),
        **CONNECTION_KWARGS,
    )


# Proxy database instance to be initialized later
database = DatabaseProxy()
