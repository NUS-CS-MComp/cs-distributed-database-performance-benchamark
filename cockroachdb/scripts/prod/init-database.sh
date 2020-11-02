#!/bin/zsh

source ./config.sh

cockroach sql --certs-dir=certs_35 --host=xcnc35.comp.nus.edu.sg --port=$PORT --user=$USER --database=cs5424 < "../db/init_db_schema.sql"
