#!/bin/zsh

source ./config.sh

function stop_instances {
  cockroach quit --certs-dir=certs --host=localhost:$(($PORT+$1-1)) || pkill cockroach
}

for seq in $(seq 1 $NUM_NODES);
  do
    stop_instances $seq
  done
