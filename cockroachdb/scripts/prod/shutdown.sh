#!/bin/zsh

source ./config.sh

function stop_instances {
  ssh $USER@xcnc$1.comp.nus.edu.sg "cd /$FOLDER_NAME/cockroachdb; bin/cockroach quit --certs-dir=certs --host=xcnc$1.comp.nus.edu.sg:$PORT | pkill cockroach";
}

for seq in $(seq $SERVER_SEQ_START $SERVER_SEQ_END);
  do
    stop_instances $seq
  done
