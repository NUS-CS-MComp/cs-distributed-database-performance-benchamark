#!/usr/bin/bash

OUTPUT_FILE_DIR=$1

cat ${OUTPUT_FILE_DIR}* | sort > ${OUTPUT_FILE_DIR}clients.csv
