import os

from playhouse.cockroachdb import CockroachDatabase

DATABASE = os.getenv("DATABASE", "cs5424")
HOST = os.getenv("HOST", "localhost")
PORT = os.getenv("POST", 26257)
USERNAME = os.getenv("USERNAME", "test")
PASSWORD = os.getenv("PASSWORD", "test")

database = CockroachDatabase(
    DATABASE, user=USERNAME, password=PASSWORD, host=HOST, port=PORT
)
