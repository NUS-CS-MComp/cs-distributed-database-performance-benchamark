#!/usr/bin/bash
SCRIPT_PATH="/home/stuproj/cs4224o/cs5424-distributed-database-group-project/cassandra/src/main.py"
XACT_FILE_DIR="/home/stuproj/cs4224o/cs5424-distributed-database-group-project/cassandra/project-files/xact-files/"
OUTPUT_FILE_DIR="/home/stuproj/cs4224o/cs5424-distributed-database-group-project/cassandra/project-files/output-files/"

for i in {2..40..5}
do
    python3 ${SCRIPT_PATH} ROWA < ${XACT_FILE_DIR}$i.txt | sed "s/^/4,$i,/" > ${OUTPUT_FILE_DIR}exp4-cli$i &
done
