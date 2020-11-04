#!/usr/bin/bash

OUTPUT_FILE_DIR="/home/stuproj/cs4224o/cs5424-distributed-database-group-project/cassandra/project-files/output-files/"

cat ${OUTPUT_FILE_DIR}* | sort > ${OUTPUT_FILE_DIR}final_result.csv
