#!/bin/zsh

source ./config.sh

function create_group_folder {
  if [ ! -e $FOLDER_NAME ]; then
    mkdir $FOLDER_NAME
  fi
  if [ ! -e $FOLDER_NAME/cockroachdb ]; then
    mkdir $FOLDER_NAME/cockroachdb
  fi
}

function install_cockroachdb {
  if [ ! -e $FOLDER_NAME/cockroachdb/bin/ ]; then
    cd $FOLDER_NAME/cockroachdb
    wget -qO- https://binaries.cockroachdb.com/cockroach-v19.2.9.linux-amd64.tgz | tar xvz
    mv cockroach-v19.2.9.linux-amd64/ bin/
  fi
}

for seq in $(seq $SERVER_SEQ_START $SERVER_SEQ_END);
  do
    ssh $USER@xcnc$seq.comp.nus.edu.sg "$(typeset -f create_group_folder); $(typeset -f install_cockroachdb); FOLDER_NAME=$FOLDER_NAME; create_group_folder && install_cockroachdb";
  done
