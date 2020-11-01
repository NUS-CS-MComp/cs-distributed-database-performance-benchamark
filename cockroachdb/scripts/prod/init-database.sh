#!/bin/zsh

cockroach sql --certs-dir=certs_35 --host=xcnc35.comp.nus.edu.sg --port=26262 --user=cs4224o --database=cs5424 < "../db/init_db_schema.sql"
