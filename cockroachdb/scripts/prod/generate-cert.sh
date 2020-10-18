#!/bin/zsh

source ./config.sh

function create_certs {
  cockroach cert create-node localhost xcnc$1.comp.nus.edu.sg --certs-dir=certs --ca-key=keys/ca.key
  cockroach cert create-client root --certs-dir=certs --ca-key=keys/ca.key
  cockroach cert create-client $USER --certs-dir=certs --ca-key=keys/ca.key
  cp certs/* certs_$1/
  rm certs/node.crt certs/node.key certs/client*
}

function upload_certs {
  ssh $USER@xcnc$1.comp.nus.edu.sg "mkdir -p $FOLDER_NAME/cockroachdb/certs"
  scp certs_$1/* $USER@xcnc$1.comp.nus.edu.sg:$FOLDER_NAME/cockroachdb/certs
}

if [ ! -f certs/ca.crt ]; then
  cockroach cert create-ca --certs-dir=certs --ca-key=keys/ca.key --allow-ca-key-reuse
  for seq in $(seq $SERVER_SEQ_START $SERVER_SEQ_END);
    do
      create_certs $seq;
    done
fi

for seq in $(seq $SERVER_SEQ_START $SERVER_SEQ_END); do upload_certs $seq; done
