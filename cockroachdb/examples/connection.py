from cockroachdb.modules.connection import (
    initialize_cockroach_database,
    database,
)

if __name__ == "__main__":
    cockroach_db = initialize_cockroach_database()
    database.initialize(cockroach_db)
    with database.atomic():
        result = cockroach_db.execute_sql("SHOW USERS;")
