#!/bin/zsh

source ./config.sh

function start_instances {
  node_addresses=()
  for seq in $(seq $SERVER_SEQ_START $SERVER_SEQ_END);
    do
      if [ $seq -ne $1 ]; then
        node_addresses+=xcnc$seq.comp.nus.edu.sg:$PORT
      fi
    done
  join_address=$(printf ",%s" "${node_addresses[@]}")
  join_address=${join_address:1}
  ssh $USER@xcnc$1.comp.nus.edu.sg "cd /$FOLDER_NAME/cockroachdb; bin/cockroach start --certs-dir=certs --listen-addr=xcnc$1.comp.nus.edu.sg:$PORT --advertise-addr=xcnc$1.comp.nus.edu.sg:$PORT --http-addr=xcnc$1.comp.nus.edu.sg:$HTTP_PORT --join=$join_address --cache=.25 --max-sql-memory=.25 --background";
}

for seq in $(seq $SERVER_SEQ_START $SERVER_SEQ_END);
  do
    start_instances $seq
  done
