import os

from playhouse.cockroachdb import CockroachDatabase

DB_NAME = os.getenv("DB_NAME", "cs5424")
HOST = os.getenv("HOST", "localhost")
PORT = os.getenv("POST", 26257)
USERNAME = os.getenv("USERNAME", "test")
PASSWORD = os.getenv("PASSWORD", "test")

database = CockroachDatabase(
    DB_NAME, user=USERNAME, password=PASSWORD, host=HOST, port=PORT
)

database.connect()
