#!/bin/zsh

source ./config.sh

function start_instances {
  node_addresses=()
  for seq in $(seq 1 $NUM_NODES);
    do
      if [ $seq -ne $1 ]; then
        node_addresses+=localhost:$(($PORT+seq-1))
      fi
    done
  join_address=$(printf ",%s" "${node_addresses[@]}")
  join_address=${join_address:1}
  cockroach start --certs-dir=certs --store=node$1 --listen-addr=localhost:$(($PORT+$1-1)) --http-addr=localhost:$((8080+$1-1)) --join=$join_address --background
}

for seq in $(seq 1 $NUM_NODES);
  do
    start_instances $seq
  done

cockroach init --certs-dir=certs --host=localhost:$PORT ||
