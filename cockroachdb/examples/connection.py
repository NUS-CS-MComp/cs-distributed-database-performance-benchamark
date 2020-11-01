from cockroachdb.modules.connection import (
    initialize_cockroach_database,
    database,
)
from common.logging import console

if __name__ == "__main__":
    cockroach_db = initialize_cockroach_database()
    database.initialize(cockroach_db)
    with database.atomic():
        result = cockroach_db.execute_sql("SHOW USERS;")
        console.log("Connection is successfully established")
        console.log(result.fetchall())
