#!/usr/bin/bash
SCRIPT_PATH=$1
XACT_FILE_DIR=$2
OUTPUT_FILE_DIR=$3

for i in {1..20..5}
do
    python3 ${SCRIPT_PATH} QUORUM < ${XACT_FILE_DIR}$i.txt | sed "s/^/1,$i,/" > ${OUTPUT_FILE_DIR}exp1-cli$i &
done
