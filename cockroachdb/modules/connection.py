import os
import pathlib
from random import choice, randint
from typing import List

from playhouse.cockroachdb import CockroachDatabase, DatabaseProxy

# Basic database configuration
IS_PROD = os.getenv("ENV", "dev") == "prod"
DATABASE = os.getenv("DATABASE", "cs5424")
HOST = os.getenv("HOST", "localhost")
USER = os.getenv("USER", "cs4224o")
ASSIGNED_PORTS = os.getenv("PORTS", "26257,26258,26259,26260,26261").split(",")

# Connection options
CONNECTION_KWARGS = {"host": HOST, "database": DATABASE, "user": USER}
SCRIPTS_PATH = pathlib.Path(__file__).parent.parent / "scripts"


# Helper functions
def initialize_cockroach_database(
    hosts: List[str] = None, host_index: int = None, port: int = None
):
    """
    Initialize
    :param hosts: list of hosts, only for production
    :param host_index: server index to connect to, only for production
    :param port: database port number, only for production
    :return: Pooled CockroachDB instance
    """
    if IS_PROD:
        if host_index is None:
            host = hosts[randint(0, len(hosts) - 1)]
        else:
            host = hosts[host_index]
        CONNECTION_KWARGS.update(
            host=host,
            sslmode="verify-full",
            sslrootcert=SCRIPTS_PATH / "prod/certs/ca.crt",
            sslcert=SCRIPTS_PATH
            / f"prod/server_certs/{host}/client.{USER}.crt",
            sslkey=SCRIPTS_PATH
            / f"prod/server_certs/{host}/client.{USER}.key",
        )
        return CockroachDatabase(
            port=port,
            **CONNECTION_KWARGS,
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
