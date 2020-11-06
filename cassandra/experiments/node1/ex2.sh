#!/usr/bin/bash
SCRIPT_PATH=$1
XACT_FILE_DIR=$2
OUTPUT_FILE_DIR=$3

for i in {1..20..5}
do
    python3 ${SCRIPT_PATH} ROWA < ${XACT_FILE_DIR}$i.txt | sed "s/^/2,$i,/" > ${OUTPUT_FILE_DIR}exp2-cli$i &
done
