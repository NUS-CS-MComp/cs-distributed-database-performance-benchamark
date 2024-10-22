#!/usr/bin/bash
SCRIPT_PATH="/home/stuproj/cs4224o/cs5424-distributed-database-group-project/cassandra/src/main.py"
XACT_FILE_DIR="/home/stuproj/cs4224o/cs5424-distributed-database-group-project/cassandra/project-files/xact-files/"
OUTPUT_FILE_DIR="/home/stuproj/cs4224o/cs5424-distributed-database-group-project/cassandra/project-files/output-files/"

for i in {1..20..5}
do
    python3 ${SCRIPT_PATH} QUORUM < ${XACT_FILE_DIR}zach.txt | sed "s/^/Z,$i,/" > ${OUTPUT_FILE_DIR}expZ-cli$i &
done
