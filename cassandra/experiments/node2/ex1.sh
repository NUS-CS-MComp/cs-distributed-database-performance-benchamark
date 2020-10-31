#!/usr/bin/bash
SCRIPT_PATH="/home/stuproj/cs4224o/cs5424-distributed-database-group-project/cassandra/src/main.py"
XACT_FILE_DIR="/home/stuproj/cs4224o/cs5424-distributed-database-group-project/cassandra/project-files/xact-files/"

for i in {2..20..5}
do
    python3 ${SCRIPT_PATH} < ${XACT_FILE_DIR}$i.txt &
done