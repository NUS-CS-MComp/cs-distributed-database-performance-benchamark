#!/bin/zsh

source ./config.sh

cockroach sql --certs-dir=certs --host=localhost --port=$PORT --database=cs5424 < "../db/init_db_schema.sql"
