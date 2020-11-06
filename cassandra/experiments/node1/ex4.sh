#!/usr/bin/bash
SCRIPT_PATH=$1
XACT_FILE_DIR=$2
OUTPUT_FILE_DIR=$3

for i in {1..40..5}
do
    python3 ${SCRIPT_PATH} ROWA < ${XACT_FILE_DIR}$i.txt | sed "s/^/4,$i,/" > ${OUTPUT_FILE_DIR}exp4-cli$i &
done
